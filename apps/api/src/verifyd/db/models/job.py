from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Job(Base, TimestampedUUIDMixin):
    __tablename__ = "jobs"

    submission_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("submissions.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="queued",
        nullable=False
    )  # 'queued' | 'running' | 'succeeded' | 'failed' | 'retrying'
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    error_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    submission: Mapped[Optional["Submission"]] = relationship("Submission", back_populates="jobs")
