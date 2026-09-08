from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class ClauseVerdict(Base, TimestampedUUIDMixin):
    __tablename__ = "clause_verdicts"

    report_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("compliance_reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    clause_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("clauses.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    clause_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # 'pass' | 'fail' | 'flagged'
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    measured_value: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    required_value: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_overridden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    override_verdict: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    overridden_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    overridden_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    report: Mapped["ComplianceReport"] = relationship("ComplianceReport", back_populates="verdicts")
    clause: Mapped["Clause"] = relationship("Clause", back_populates="verdicts")
    evidence_items: Mapped[List["EvidenceItem"]] = relationship("EvidenceItem", back_populates="verdict", cascade="all, delete-orphan")
