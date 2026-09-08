from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import assert_can_access, get_current_user, require
from verifyd.core.errors import NotFoundError, ValidationError
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.contract import Contract
from verifyd.db.models.submission import Submission
from verifyd.db.models.clause_verdict import ClauseVerdict
from verifyd.db.models.review import Review
from verifyd.db.models.user import User
from verifyd.db.session import get_async_db
from verifyd.schemas.review import ReviewCreate, ReviewResponse
from verifyd.schemas.report import ClauseVerdictResponse, VerdictOverrideRequest
from verifyd.services.audit_service import record_audit_event
from verifyd.services.scoring_service import calculate_overall_compliance

router = APIRouter(tags=["Reviews"])


@router.post("/submissions/{id}/review", response_model=ReviewResponse)
async def review_submission(
    id: str,
    req: ReviewCreate,
    current_user: User = Depends(require("review_submission")),
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(Submission, Contract, Campaign)
        .join(Contract, Submission.contract_id == Contract.id)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .where(Submission.id == id, Submission.deleted_at.is_(None))
    )
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Submission not found")

    sub, contract, campaign = row
    assert_can_access(current_user, sub)

    # State transition
    sub.status = req.decision

    review = Review(
        submission_id=id,
        reviewer_id=current_user.id,
        decision=req.decision,
        note=req.note,
    )
    db.add(review)

    await record_audit_event(
        session=db,
        entity_type="submission",
        entity_id=id,
        action=f"review_{req.decision}",
        actor_id=current_user.id,
        after={"decision": req.decision, "note": req.note},
    )

    await db.commit()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        submission_id=review.submission_id,
        reviewer_id=review.reviewer_id,
        decision=review.decision,
        note=review.note,
        created_at=review.created_at,
    )


@router.patch("/verdicts/{id}/override", response_model=ClauseVerdictResponse)
async def override_verdict(
    id: str,
    req: VerdictOverrideRequest,
    current_user: User = Depends(require("override_verdict")),
    db: AsyncSession = Depends(get_async_db),
):
    if len(req.reason.strip()) < 20:
        raise ValidationError("Override reason must be at least 20 characters explaining the rationale.")

    query = (
        select(ClauseVerdict)
        .options(selectinload(ClauseVerdict.evidence_items), selectinload(ClauseVerdict.report))
        .where(ClauseVerdict.id == id)
    )
    res = await db.execute(query)
    verdict = res.scalar_one_or_none()
    if not verdict:
        raise NotFoundError("Clause verdict not found")

    before_state = {
        "verdict": verdict.verdict,
        "is_overridden": verdict.is_overridden,
        "override_verdict": verdict.override_verdict,
    }

    verdict.is_overridden = True
    verdict.override_verdict = req.verdict
    verdict.override_reason = req.reason
    verdict.overridden_by = current_user.id
    verdict.overridden_at = datetime.now(timezone.utc)

    # Recompute compliance report score
    rep_query = (
        select(ClauseVerdict)
        .where(ClauseVerdict.report_id == verdict.report_id)
    )
    rep_res = await db.execute(rep_query)
    all_verdicts = rep_res.scalars().all()

    verdicts_data = [
        {
            "verdict": v.override_verdict if v.is_overridden else v.verdict,
            "severity": "standard",  # standard weight fallback
        }
        for v in all_verdicts
    ]
    new_score, new_v, tot, pas, fai, flg = calculate_overall_compliance(verdicts_data)

    if verdict.report:
        verdict.report.overall_score = new_score
        verdict.report.verdict = new_v
        verdict.report.clauses_passed = pas
        verdict.report.clauses_failed = fai
        verdict.report.clauses_flagged = flg

    await record_audit_event(
        session=db,
        entity_type="clause_verdict",
        entity_id=id,
        action="override_verdict",
        actor_id=current_user.id,
        before=before_state,
        after={"override_verdict": req.verdict, "override_reason": req.reason},
    )

    await db.commit()
    await db.refresh(verdict)

    from verifyd.schemas.report import EvidenceItemResponse
    return ClauseVerdictResponse(
        id=verdict.id,
        report_id=verdict.report_id,
        clause_id=verdict.clause_id,
        clause_ref=verdict.clause_ref,
        verdict=verdict.verdict,
        confidence=verdict.confidence,
        rationale=verdict.rationale,
        measured_value=verdict.measured_value,
        required_value=verdict.required_value,
        is_overridden=verdict.is_overridden,
        override_verdict=verdict.override_verdict,
        override_reason=verdict.override_reason,
        overridden_by=verdict.overridden_by,
        overridden_at=verdict.overridden_at,
        evidence_items=[EvidenceItemResponse.model_validate(e) for e in verdict.evidence_items],
    )
