import asyncio
import time
from datetime import datetime, timezone
from verifyd.workers.celery_app import celery_app
from verifyd.db.session import SyncSessionLocal
from verifyd.db.models.submission import Submission
from verifyd.db.models.contract import Contract
from verifyd.db.models.clause import Clause
from verifyd.db.models.analysis_artifact import AnalysisArtifact
from verifyd.db.models.compliance_report import ComplianceReport
from verifyd.db.models.clause_verdict import ClauseVerdict
from verifyd.db.models.evidence_item import EvidenceItem
from verifyd.db.models.job import Job
from verifyd.ai.gemini import GeminiClient
from verifyd.services.scoring_service import (
    compute_deterministic_post_checks,
    calculate_overall_compliance,
)
from verifyd.core.logging import get_logger

logger = get_logger("worker.score_submission")


async def run_score_submission_async(submission_id: str, job_id: str = None):
    db = SyncSessionLocal()
    gemini = GeminiClient()
    start_time = time.time()

    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error("Submission not found", submission_id=submission_id)
            return

        submission.status = "processing"
        job = None
        if job_id:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
        db.commit()

        # Load clauses from contract
        clauses = (
            db.query(Clause)
            .filter(Clause.contract_id == submission.contract_id)
            .order_by(Clause.ordinal)
            .all()
        )
        clauses_data = [
            {
                "id": c.id,
                "clause_ref": c.clause_ref,
                "source_text": c.source_text,
                "requirement": c.requirement,
                "clause_type": c.clause_type,
                "params": c.params,
                "modality": c.modality,
                "severity": c.severity,
            }
            for c in clauses
        ]

        # Load artifacts
        transcript_artifact = (
            db.query(AnalysisArtifact)
            .filter(AnalysisArtifact.submission_id == submission_id, AnalysisArtifact.kind == "transcript")
            .first()
        )
        visual_artifact = (
            db.query(AnalysisArtifact)
            .filter(AnalysisArtifact.submission_id == submission_id, AnalysisArtifact.kind == "visual")
            .first()
        )

        transcript_payload = transcript_artifact.payload if transcript_artifact else {}
        visual_payload = visual_artifact.payload if visual_artifact else {}

        duration = submission.duration_seconds or 30.0

        # AI Scoring pass
        raw_score_output, meta = await gemini.score_submission(
            clauses_data=clauses_data,
            transcript_data=transcript_payload,
            visual_data=visual_payload,
            caption_text=submission.caption_text or "",
            duration_seconds=duration,
        )

        # Deterministic post-checks in code (code arithmetic overrides model)
        finalized_verdicts_data = compute_deterministic_post_checks(
            clauses=clauses_data,
            raw_verdicts=[v.model_dump() for v in raw_score_output.verdicts],
            transcript_segments=transcript_payload.get("segments", []),
            visual_events=visual_payload.get("visual_events", []),
            on_screen_text=visual_payload.get("on_screen_text", []),
            caption_text=submission.caption_text or "",
            duration_seconds=duration,
        )

        overall_score, overall_verdict, total_c, pass_c, fail_c, flag_c = calculate_overall_compliance(
            finalized_verdicts_data
        )

        processing_ms = int((time.time() - start_time) * 1000)
        total_cost = (
            (transcript_artifact.cost_estimate_usd if transcript_artifact else 0.0)
            + (visual_artifact.cost_estimate_usd if visual_artifact else 0.0)
            + meta.get("cost_estimate_usd", 0.0)
        )

        # Single transaction write for report + verdicts + evidence items
        # Remove any previous report for this submission
        db.query(ComplianceReport).filter(ComplianceReport.submission_id == submission_id).delete()

        report = ComplianceReport(
            submission_id=submission_id,
            overall_score=overall_score,
            verdict=overall_verdict,
            clauses_total=total_c,
            clauses_passed=pass_c,
            clauses_failed=fail_c,
            clauses_flagged=flag_c,
            model_version="gemini-2.0-flash",
            prompt_version="v1.0.0",
            processing_ms=processing_ms,
            cost_estimate_usd=round(total_cost, 6),
        )
        db.add(report)
        db.flush()

        for vd in finalized_verdicts_data:
            clause_verdict = ClauseVerdict(
                report_id=report.id,
                clause_id=vd["clause_id"],
                clause_ref=vd["clause_ref"],
                verdict=vd["verdict"],
                confidence=vd["confidence"],
                rationale=vd["rationale"],
                measured_value=vd["measured_value"],
                required_value=vd["required_value"],
                is_overridden=False,
            )
            db.add(clause_verdict)
            db.flush()

            for ev in vd.get("evidence", []):
                evidence_item = EvidenceItem(
                    clause_verdict_id=clause_verdict.id,
                    type=ev.get("type", "transcript_span"),
                    start_ms=ev.get("start_ms", 0),
                    end_ms=ev.get("end_ms", 0),
                    payload=ev.get("payload", {}),
                    thumbnail_key=ev.get("thumbnail_key"),
                )
                db.add(evidence_item)

        submission.status = "report_ready"
        if job:
            job.status = "succeeded"
            job.finished_at = datetime.now(timezone.utc)
        db.commit()
        logger.info("Compliance report generated successfully", submission_id=submission_id, score=overall_score, verdict=overall_verdict)
    except Exception as e:
        db.rollback()
        logger.error("Submission scoring failed", submission_id=submission_id, error=str(e))
        if submission:
            submission.status = "failed"
        if job:
            job.status = "failed"
            job.error_class = type(e).__name__
            job.error_message = str(e)
            job.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def score_submission_task(self, submission_id: str, job_id: str = None):
    asyncio.run(run_score_submission_async(submission_id, job_id))


async def run_full_submission_pipeline_async(submission_id: str):
    """Orchestrates full submission pipeline: transcribe + analyse -> score."""
    from verifyd.workers.tasks.transcribe import run_transcribe_async
    from verifyd.workers.tasks.analyse_video import run_analyse_video_async

    # Step 1: Run transcribe & analyse in parallel
    await asyncio.gather(
        run_transcribe_async(submission_id),
        run_analyse_video_async(submission_id),
    )

    # Step 2: Score submission
    await run_score_submission_async(submission_id)
