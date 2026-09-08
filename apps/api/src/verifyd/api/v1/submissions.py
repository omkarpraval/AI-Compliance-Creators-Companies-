from datetime import datetime, timezone
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import assert_can_access, get_current_user, require
from verifyd.core.errors import DomainStateError, NotFoundError, ValidationError
from verifyd.core.pagination import PaginatedResponse, decode_cursor, encode_cursor
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.contract import Contract
from verifyd.db.models.submission import Submission
from verifyd.db.models.compliance_report import ComplianceReport
from verifyd.db.models.clause_verdict import ClauseVerdict
from verifyd.db.models.evidence_item import EvidenceItem
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.models.user import User
from verifyd.db.session import get_async_db
from verifyd.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionStatusResponse,
)
from verifyd.schemas.report import (
    ComplianceReportResponse,
    ClauseVerdictResponse,
    EvidenceItemResponse,
)
from verifyd.workers.tasks.score_submission import run_full_submission_pipeline_async

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get("", response_model=PaginatedResponse[SubmissionResponse])
async def list_submissions(
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    status: Optional[str] = None,
    campaign_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    offset = decode_cursor(cursor)
    query = (
        select(Submission, Contract, Campaign, CreatorProfile)
        .join(Contract, Submission.contract_id == Contract.id)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .join(CreatorProfile, Submission.creator_id == CreatorProfile.id)
        .options(
            selectinload(Submission.report).selectinload(ComplianceReport.verdicts).selectinload(ClauseVerdict.evidence_items)
        )
        .where(Submission.deleted_at.is_(None))
    )

    if current_user.role == "creator":
        query = query.where(Submission.creator_id == current_user.creator_profile.id)
    elif current_user.role in ("company_admin", "company_member"):
        query = query.where(Campaign.org_id == current_user.org_id)

    if status:
        query = query.where(Submission.status == status)
    if campaign_id:
        query = query.where(Contract.campaign_id == campaign_id)

    query = query.order_by(Submission.created_at.desc(), Submission.id.desc()).offset(offset).limit(limit + 1)
    res = await db.execute(query)
    rows = res.all()

    items = []
    for row in rows[:limit]:
        sub, contract, campaign, creator = row
        rep_resp = None
        if sub.report:
            verdicts_resp = []
            for v in sub.report.verdicts:
                ev_items = [EvidenceItemResponse.model_validate(e) for e in v.evidence_items]
                verdicts_resp.append(
                    ClauseVerdictResponse(
                        id=v.id,
                        report_id=v.report_id,
                        clause_id=v.clause_id,
                        clause_ref=v.clause_ref,
                        verdict=v.verdict,
                        confidence=v.confidence,
                        rationale=v.rationale,
                        measured_value=v.measured_value,
                        required_value=v.required_value,
                        is_overridden=v.is_overridden,
                        override_verdict=v.override_verdict,
                        override_reason=v.override_reason,
                        overridden_by=v.overridden_by,
                        overridden_at=v.overridden_at,
                        evidence_items=ev_items,
                    )
                )
            rep_resp = ComplianceReportResponse(
                id=sub.report.id,
                submission_id=sub.report.submission_id,
                overall_score=sub.report.overall_score,
                verdict=sub.report.verdict,
                clauses_total=sub.report.clauses_total,
                clauses_passed=sub.report.clauses_passed,
                clauses_failed=sub.report.clauses_failed,
                clauses_flagged=sub.report.clauses_flagged,
                model_version=sub.report.model_version,
                prompt_version=sub.report.prompt_version,
                generated_at=sub.report.generated_at,
                processing_ms=sub.report.processing_ms,
                cost_estimate_usd=sub.report.cost_estimate_usd,
                verdicts=verdicts_resp,
            )

        items.append(
            SubmissionResponse(
                id=sub.id,
                contract_id=sub.contract_id,
                contract_version=sub.contract_version,
                creator_id=sub.creator_id,
                kind=sub.kind,
                video_file_key=sub.video_file_key,
                duration_seconds=sub.duration_seconds,
                caption_text=sub.caption_text,
                platform_url=sub.platform_url,
                status=sub.status,
                submitted_at=sub.submitted_at,
                attempt_number=sub.attempt_number,
                created_at=sub.created_at,
                updated_at=sub.updated_at,
                campaign_name=campaign.name,
                creator_handle=creator.handle,
                product_name=campaign.product_name,
                report=rep_resp,
            )
        )

    next_cursor = encode_cursor(offset + limit) if len(rows) > limit else None
    return PaginatedResponse(items=items, next_cursor=next_cursor)


@router.post("", response_model=SubmissionResponse)
async def create_submission(
    req: SubmissionCreate,
    current_user: User = Depends(require("submit_video", "run_preflight")),
    db: AsyncSession = Depends(get_async_db),
):
    c_query = (
        select(Contract, Campaign)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .where(Contract.id == req.contract_id, Contract.deleted_at.is_(None))
    )
    c_res = await db.execute(c_query)
    c_row = c_res.first()
    if not c_row:
        raise NotFoundError("Contract not found")

    contract, campaign = c_row

    creator_id = current_user.creator_profile.id if current_user.creator_profile else contract.creator_id

    # Check previous attempts
    att_query = select(Submission).where(
        Submission.contract_id == req.contract_id,
        Submission.kind == req.kind,
        Submission.deleted_at.is_(None),
    )
    att_res = await db.execute(att_query)
    prev_submissions = att_res.scalars().all()
    attempt_num = len(prev_submissions) + 1

    submission = Submission(
        contract_id=req.contract_id,
        contract_version=contract.version,  # Denormalised deliberately
        creator_id=creator_id,
        kind=req.kind,
        video_file_key=req.video_file_key,
        duration_seconds=req.duration_seconds or 30.0,
        caption_text=req.caption_text,
        platform_url=req.platform_url,
        status="processing",
        submitted_at=datetime.now(timezone.utc),
        attempt_number=attempt_num,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # Run AI pipeline async
    await run_full_submission_pipeline_async(submission_id=submission.id)

    # Reload submission with report
    return await get_submission(submission.id, current_user, db)


@router.get("/{id}", response_model=SubmissionResponse)
async def get_submission(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(Submission, Contract, Campaign, CreatorProfile)
        .join(Contract, Submission.contract_id == Contract.id)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .join(CreatorProfile, Submission.creator_id == CreatorProfile.id)
        .options(
            selectinload(Submission.report).selectinload(ComplianceReport.verdicts).selectinload(ClauseVerdict.evidence_items)
        )
        .where(Submission.id == id, Submission.deleted_at.is_(None))
    )
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Submission not found")

    sub, contract, campaign, creator = row
    assert_can_access(current_user, sub)

    rep_resp = None
    if sub.report:
        verdicts_resp = []
        for v in sub.report.verdicts:
            ev_items = [EvidenceItemResponse.model_validate(e) for e in v.evidence_items]
            verdicts_resp.append(
                ClauseVerdictResponse(
                    id=v.id,
                    report_id=v.report_id,
                    clause_id=v.clause_id,
                    clause_ref=v.clause_ref,
                    verdict=v.verdict,
                    confidence=v.confidence,
                    rationale=v.rationale,
                    measured_value=v.measured_value,
                    required_value=v.required_value,
                    is_overridden=v.is_overridden,
                    override_verdict=v.override_verdict,
                    override_reason=v.override_reason,
                    overridden_by=v.overridden_by,
                    overridden_at=v.overridden_at,
                    evidence_items=ev_items,
                )
            )
        rep_resp = ComplianceReportResponse(
            id=sub.report.id,
            submission_id=sub.report.submission_id,
            overall_score=sub.report.overall_score,
            verdict=sub.report.verdict,
            clauses_total=sub.report.clauses_total,
            clauses_passed=sub.report.clauses_passed,
            clauses_failed=sub.report.clauses_failed,
            clauses_flagged=sub.report.clauses_flagged,
            model_version=sub.report.model_version,
            prompt_version=sub.report.prompt_version,
            generated_at=sub.report.generated_at,
            processing_ms=sub.report.processing_ms,
            cost_estimate_usd=sub.report.cost_estimate_usd,
            verdicts=verdicts_resp,
        )

    return SubmissionResponse(
        id=sub.id,
        contract_id=sub.contract_id,
        contract_version=sub.contract_version,
        creator_id=sub.creator_id,
        kind=sub.kind,
        video_file_key=sub.video_file_key,
        duration_seconds=sub.duration_seconds,
        caption_text=sub.caption_text,
        platform_url=sub.platform_url,
        status=sub.status,
        submitted_at=sub.submitted_at,
        attempt_number=sub.attempt_number,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
        campaign_name=campaign.name,
        creator_handle=creator.handle,
        product_name=campaign.product_name,
        report=rep_resp,
    )


@router.get("/{id}/status", response_model=SubmissionStatusResponse)
async def get_submission_status(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Submission).where(Submission.id == id, Submission.deleted_at.is_(None))
    res = await db.execute(query)
    sub = res.scalar_one_or_none()
    if not sub:
        raise NotFoundError("Submission not found")

    assert_can_access(current_user, sub)

    # Calculate status and stage
    if sub.status == "report_ready" or sub.status in ("approved", "rejected", "changes_requested"):
        return SubmissionStatusResponse(
            submission_id=sub.id,
            status=sub.status,
            progress=100,
            stage="Complete",
        )
    elif sub.status == "processing":
        return SubmissionStatusResponse(
            submission_id=sub.id,
            status="processing",
            progress=75,
            stage="Matching clauses",
        )
    elif sub.status == "failed":
        return SubmissionStatusResponse(
            submission_id=sub.id,
            status="failed",
            progress=100,
            stage="Failed",
            error_message="AI pipeline processing failed",
        )
    else:
        return SubmissionStatusResponse(
            submission_id=sub.id,
            status=sub.status,
            progress=25,
            stage="Uploading",
        )


@router.get("/{id}/report", response_model=ComplianceReportResponse)
async def get_submission_report(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(ComplianceReport)
        .options(selectinload(ComplianceReport.verdicts).selectinload(ClauseVerdict.evidence_items))
        .where(ComplianceReport.submission_id == id)
    )
    res = await db.execute(query)
    rep = res.scalar_one_or_none()
    if not rep:
        raise NotFoundError("Compliance report not found for this submission")

    verdicts_resp = []
    for v in rep.verdicts:
        ev_items = [EvidenceItemResponse.model_validate(e) for e in v.evidence_items]
        verdicts_resp.append(
            ClauseVerdictResponse(
                id=v.id,
                report_id=v.report_id,
                clause_id=v.clause_id,
                clause_ref=v.clause_ref,
                verdict=v.verdict,
                confidence=v.confidence,
                rationale=v.rationale,
                measured_value=v.measured_value,
                required_value=v.required_value,
                is_overridden=v.is_overridden,
                override_verdict=v.override_verdict,
                override_reason=v.override_reason,
                overridden_by=v.overridden_by,
                overridden_at=v.overridden_at,
                evidence_items=ev_items,
            )
        )

    return ComplianceReportResponse(
        id=rep.id,
        submission_id=rep.submission_id,
        overall_score=rep.overall_score,
        verdict=rep.verdict,
        clauses_total=rep.clauses_total,
        clauses_passed=rep.clauses_passed,
        clauses_failed=rep.clauses_failed,
        clauses_flagged=rep.clauses_flagged,
        model_version=rep.model_version,
        prompt_version=rep.prompt_version,
        generated_at=rep.generated_at,
        processing_ms=rep.processing_ms,
        cost_estimate_usd=rep.cost_estimate_usd,
        verdicts=verdicts_resp,
    )


@router.get("/{id}/report/export")
async def export_submission_report_pdf(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    rep_query = (
        select(ComplianceReport, Submission, Contract, Campaign)
        .join(Submission, ComplianceReport.submission_id == Submission.id)
        .join(Contract, Submission.contract_id == Contract.id)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .options(selectinload(ComplianceReport.verdicts).selectinload(ClauseVerdict.evidence_items))
        .where(ComplianceReport.submission_id == id)
    )
    res = await db.execute(rep_query)
    row = res.first()
    if not row:
        raise NotFoundError("Report not found")

    rep, sub, contract, campaign = row
    assert_can_access(current_user, sub)

    # Generate PDF using ReportLab
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors

    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    p.setTitle(f"Verifyd_Report_{sub.id[:8]}.pdf")

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, 750, "VERIFYD COMPLIANCE AUDIT REPORT")
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#566579"))
    p.drawString(50, 735, f"Campaign: {campaign.name} | Product: {campaign.product_name} | Contract v{sub.contract_version}")
    p.drawString(50, 720, f"Generated: {rep.generated_at.strftime('%Y-%m-%d %H:%M UTC')} | Model: {rep.model_version}")

    # Score Box
    p.setFillColor(colors.HexColor("#101620"))
    p.rect(50, 640, 512, 65, fill=1, stroke=0)
    p.setFillColor(colors.HexColor("#E8EDF5"))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(65, 680, f"OVERALL VERDICT: {rep.verdict.upper()}")
    p.drawString(65, 660, f"Compliance Score: {rep.overall_score}%  (Passed: {rep.clauses_passed} | Failed: {rep.clauses_failed} | Flagged: {rep.clauses_flagged})")

    # Clause list
    y = 610
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.HexColor("#131B27"))
    p.drawString(50, y, "CLAUSE-BY-CLAUSE AUDIT EVIDENCE")
    y -= 20

    for v in rep.verdicts:
        if y < 80:
            p.showPage()
            y = 750

        # Verdict color badge
        if v.verdict == "pass":
            p.setFillColor(colors.HexColor("#1E9E63"))
        elif v.verdict == "fail":
            p.setFillColor(colors.HexColor("#D93838"))
        else:
            p.setFillColor(colors.HexColor("#D08700"))

        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, f"[{v.clause_ref}]  {v.verdict.upper()}")

        p.setFillColor(colors.HexColor("#131B27"))
        p.setFont("Helvetica", 9)
        p.drawString(130, y, f"{v.rationale[:85]}...")
        y -= 18

    p.save()
    pdf_data = buf.getvalue()
    buf.close()

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Verifyd_Report_{sub.id[:8]}.pdf"'},
    )
