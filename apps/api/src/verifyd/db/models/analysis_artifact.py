from typing import Any, Dict, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class AnalysisArtifact(Base, TimestampedUUIDMixin):
    __tablename__ = "analysis_artifacts"

    submission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    artifact_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'transcript' | 'keyframes' | 'audio_features' | 'visual_events' | 'ocr_events'
    storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="artifacts")
