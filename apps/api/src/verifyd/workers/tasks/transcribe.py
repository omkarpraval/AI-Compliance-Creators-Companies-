import asyncio
from datetime import datetime, timezone
from verifyd.workers.celery_app import celery_app
from verifyd.db.session import SyncSessionLocal
from verifyd.db.models.submission import Submission
from verifyd.db.models.analysis_artifact import AnalysisArtifact
from verifyd.db.models.job import Job
from verifyd.ai.groq import GroqClient
from verifyd.ai.bhashini import BhashiniClient
from verifyd.core.logging import get_logger

logger = get_logger("worker.transcribe")


async def run_transcribe_async(submission_id: str):
    db = SyncSessionLocal()
    groq = GroqClient()
    bhashini = BhashiniClient()

    try:
        # Check idempotency: if transcript artifact already exists, skip
        existing = db.query(AnalysisArtifact).filter(
            AnalysisArtifact.submission_id == submission_id,
            AnalysisArtifact.kind == "transcript"
        ).first()
        if existing:
            logger.info("Transcript artifact already exists, skipping transcribe task", submission_id=submission_id)
            return

        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return

        duration = submission.duration_seconds or 30.0
        payload, meta = await groq.transcribe(submission.video_file_key, duration_seconds=duration)

        artifact = AnalysisArtifact(
            submission_id=submission_id,
            kind="transcript",
            provider=meta.get("provider", "groq"),
            model=meta.get("model", "whisper-large-v3"),
            payload=payload,
            token_usage=meta.get("token_usage", {}),
            latency_ms=meta.get("latency_ms", 0),
            cost_estimate_usd=meta.get("cost_estimate_usd", 0.0),
        )
        db.add(artifact)

        # Non-English translation check
        lang = payload.get("language", "en")
        if lang != "en":
            t_payload, t_meta = await bhashini.translate(payload.get("text", ""), source_language=lang)
            trans_artifact = AnalysisArtifact(
                submission_id=submission_id,
                kind="translation",
                provider="bhashini",
                model="bhashini-nmt",
                payload=t_payload,
                token_usage=t_meta.get("token_usage", {}),
                latency_ms=t_meta.get("latency_ms", 0),
                cost_estimate_usd=t_meta.get("cost_estimate_usd", 0.0),
            )
            db.add(trans_artifact)

        db.commit()
        logger.info("Transcribe task completed", submission_id=submission_id)
    except Exception as e:
        db.rollback()
        logger.error("Transcribe task error", submission_id=submission_id, error=str(e))
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def transcribe_task(self, submission_id: str):
    asyncio.run(run_transcribe_async(submission_id))
