from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Clause(Base, TimestampedUUIDMixin):
    __tablename__ = "clauses"

    contract_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    ordinal: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clause_ref: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. 'C-01'
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    requirement: Mapped[str] = mapped_column(Text, nullable=False)
    clause_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'min_spoken_duration' | 'required_phrase' | 'prohibited_mention' | 'visual_presence' | 'visual_timing' | 'disclosure_tag' | 'tone_requirement' | 'manual_only'
    params: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    modality: Mapped[str] = mapped_column(
        String(50),
        default="mixed",
        nullable=False
    )  # 'audio' | 'visual' | 'text_overlay' | 'metadata' | 'mixed'
    severity: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False
    )  # 'critical' | 'standard' | 'advisory'
    is_auto_checkable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(50),
        default="unreviewed",
        nullable=False
    )  # 'unreviewed' | 'confirmed' | 'edited' | 'rejected'
    source_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_bbox: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    edited_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="clauses")
    verdicts: Mapped[List["ClauseVerdict"]] = relationship("ClauseVerdict", back_populates="clause")
