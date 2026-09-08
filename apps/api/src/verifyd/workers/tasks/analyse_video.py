import asyncio
from datetime import datetime, timezone
from verifyd.workers.celery_app import celery_app
from verifyd.db.session import SyncSessionLocal
from verifyd.db.models.submission import Submission
from verifyd.db.models.analysis_artifact import AnalysisArtifact
from verifyd.ai.gemini import GeminiClient
from verifyd.core.logging import get_logger

logger = get_logger("worker.analyse_video")


async def run_analyse_video_async(submission_id: str):
    db = SyncSessionLocal()
    gemini = GeminiClient()

    try:
        # Idempotency check
        existing = db.query(AnalysisArtifact).filter(
            AnalysisArtifact.submission_id == submission_id,
            AnalysisArtifact.kind == "visual"
        ).first()
        if existing:
            logger.info("Visual artifact already exists, skipping analyse_video", submission_id=submission_id)
            return

        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return

        duration = submission.duration_seconds or 30.0
        output, meta = await gemini.analyse_video(submission.video_file_key, duration_seconds=duration)

        artifact = AnalysisArtifact(
            submission_id=submission_id,
            kind="visual",
            provider="gemini",
            model="gemini-2.0-flash-multimodal",
            payload=output.model_dump(),
            token_usage=meta.get("token_usage", {}),
            latency_ms=meta.get("latency_ms", 0),
            cost_estimate_usd=meta.get("cost_estimate_usd", 0.0),
        )
        db.add(artifact)
        db.commit()
        logger.info("Video analysis task completed", submission_id=submission_id)
    except Exception as e:
        db.rollback()
        logger.error("Video analysis task error", submission_id=submission_id, error=str(e))
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def analyse_video_task(self, submission_id: str):
    asyncio.run(run_analyse_video_async(submission_id))
