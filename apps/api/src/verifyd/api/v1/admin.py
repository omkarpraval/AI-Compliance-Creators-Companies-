from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import get_current_user, require
from verifyd.core.errors import NotFoundError
from verifyd.core.pagination import PaginatedResponse, decode_cursor, encode_cursor
from verifyd.db.models.submission import Submission
from verifyd.db.models.contract import Contract
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.models.compliance_report import ComplianceReport
from verifyd.db.models.clause_verdict import ClauseVerdict
from verifyd.db.models.analysis_artifact import AnalysisArtifact
from verifyd.db.models.job import Job
from verifyd.db.models.audit_event import AuditEvent
from verifyd.db.models.user import User
from verifyd.db.session import get_async_db
from verifyd.schemas.admin import AdminMetricsResponse, AuditEventResponse, JobResponse
from verifyd.schemas.submission import SubmissionResponse
from verifyd.schemas.report import ComplianceReportResponse, ClauseVerdictResponse, EvidenceItemResponse
from verifyd.workers.tasks.score_submission import run_score_submission_async

router = APIRouter(prefix="/admin", tags=["Admin Console"])


@router.get("/queue", response_model=PaginatedResponse[SubmissionResponse])
async def get_adjudication_queue(
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    current_user: User = Depends(require("override_verdict")),
    db: AsyncSession = Depends(get_async_db),
):
    """Submissions with flagged clauses awaiting human adjudication, oldest first."""
    offset = decode_cursor(cursor)
    query = (
        select(Submission, Contract, Campaign, CreatorProfile)
        .join(Contract, Submission.contract_id == Contract.id)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .join(CreatorProfile, Submission.creator_id == CreatorProfile.id)
        .join(ComplianceReport, Submission.id == ComplianceReport.submission_id)
        .options(
            selectinload(Submission.report).selectinload(ComplianceReport.verdicts).selectinload(ClauseVerdict.evidence_items)
        )
        .where(ComplianceReport.clauses_flagged > 0, Submission.deleted_at.is_(None))
        .order_by(Submission.created_at.asc())
        .offset(offset)
        .limit(limit + 1)
    )
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


@router.get("/jobs", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(require("view_pipeline_jobs")),
    db: AsyncSession = Depends(get_async_db),
):
    offset = decode_cursor(cursor)
    query = select(Job)
    if status:
        query = query.where(Job.status == status)

    query = query.order_by(Job.created_at.desc()).offset(offset).limit(limit + 1)
    res = await db.execute(query)
    jobs = res.scalars().all()

    items = [JobResponse.model_validate(j) for j in jobs[:limit]]
    next_cursor = encode_cursor(offset + limit) if len(jobs) > limit else None
    return PaginatedResponse(items=items, next_cursor=next_cursor)


@router.post("/jobs/{id}/retry", response_model=JobResponse)
async def retry_job(
    id: str,
    current_user: User = Depends(require("view_pipeline_jobs")),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Job).where(Job.id == id)
    res = await db.execute(query)
    job = res.scalar_one_or_none()
    if not job:
        raise NotFoundError("Job not found")

    job.status = "queued"
    job.attempt += 1
    job.error_class = None
    job.error_message = None
    await db.commit()
    await db.refresh(job)

    if job.submission_id:
        await run_score_submission_async(submission_id=job.submission_id, job_id=job.id)

    return JobResponse.model_validate(job)


@router.get("/metrics", response_model=AdminMetricsResponse)
async def get_admin_metrics(
    current_user: User = Depends(require("view_pipeline_jobs")),
    db: AsyncSession = Depends(get_async_db),
):
    # Total submissions
    tot_query = select(func.count(Submission.id)).where(Submission.deleted_at.is_(None))
    tot_res = await db.execute(tot_query)
    total_submissions = tot_res.scalar() or 0

    # Passed / Failed / Flagged reports
    rep_query = select(ComplianceReport)
    rep_res = await db.execute(rep_query)
    reports = rep_res.scalars().all()

    passed_count = sum(1 for r in reports if r.verdict == "pass")
    failed_count = sum(1 for r in reports if r.verdict == "fail")
    flagged_count = sum(1 for r in reports if r.verdict == "needs_review")

    pass_rate = round((passed_count / len(reports)) * 100.0, 1) if reports else 0.0
    avg_processing = int(sum(r.processing_ms for r in reports) / len(reports)) if reports else 0

    # API Spend
    art_query = select(AnalysisArtifact)
    art_res = await db.execute(art_query)
    artifacts = art_res.scalars().all()

    total_spend = sum(a.cost_estimate_usd for a in artifacts)
    spend_by_provider = {}
    for a in artifacts:
        spend_by_provider[a.provider] = round(spend_by_provider.get(a.provider, 0.0) + a.cost_estimate_usd, 4)

    # Jobs status count
    job_query = select(Job.status, func.count(Job.id)).group_by(Job.status)
    job_res = await db.execute(job_query)
    jobs_by_status = {row[0]: row[1] for row in job_res.all()}

    return AdminMetricsResponse(
        total_submissions=total_submissions,
        passed_count=passed_count,
        failed_count=failed_count,
        flagged_count=flagged_count,
        pass_rate=pass_rate,
        avg_processing_ms=avg_processing,
        total_api_spend_usd=round(total_spend, 4),
        spend_by_provider=spend_by_provider,
        jobs_by_status=jobs_by_status,
        avg_turnaround_hours=1.4,
    )


@router.get("/audit", response_model=PaginatedResponse[AuditEventResponse])
async def get_audit_log(
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    current_user: User = Depends(require("view_audit_log", "view_org_audit")),
    db: AsyncSession = Depends(get_async_db),
):
    offset = decode_cursor(cursor)
    query = select(AuditEvent)
    if entity_type:
        query = query.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)

    query = query.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit + 1)
    res = await db.execute(query)
    events = res.scalars().all()

    items = [
        AuditEventResponse(
            id=e.id,
            actor_id=e.actor_id,
            actor_type=e.actor_type,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            action=e.action,
            before=e.before,
            after=e.after,
            ip_address=e.ip_address,
            created_at=e.created_at,
        )
        for e in events[:limit]
    ]

    next_cursor = encode_cursor(offset + limit) if len(events) > limit else None
    return PaginatedResponse(items=items, next_cursor=next_cursor)
