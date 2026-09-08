from typing import Any, Dict, Optional
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class EvidenceItem(Base, TimestampedUUIDMixin):
    __tablename__ = "evidence_items"

    verdict_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("clause_verdicts.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'transcript_span' | 'visual_detection' | 'ocr_text' | 'metadata_match'
    start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    thumbnail_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    verdict: Mapped["ClauseVerdict"] = relationship("ClauseVerdict", back_populates="evidence_items")
