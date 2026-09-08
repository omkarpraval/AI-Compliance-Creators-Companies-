from celery import Celery
from verifyd.config import get_settings

settings = get_settings()

celery_app = Celery(
    "verifyd_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "verifyd.workers.tasks.extract_clauses",
        "verifyd.workers.tasks.transcribe",
        "verifyd.workers.tasks.analyse_video",
        "verifyd.workers.tasks.score_submission",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_soft_time_limit=600,
    task_time_limit=720,
)
