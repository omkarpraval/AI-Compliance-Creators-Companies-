from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class ComplianceReport(Base, TimestampedUUIDMixin):
    __tablename__ = "compliance_reports"

    submission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # 'pass' | 'fail' | 'needs_review'
    clauses_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clauses_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clauses_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clauses_flagged: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), default="gemini-2.0-flash", nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v2", nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processing_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_estimate_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0.0"), nullable=False)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="compliance_report")
    verdicts: Mapped[List["ClauseVerdict"]] = relationship("ClauseVerdict", back_populates="report", cascade="all, delete-orphan")
