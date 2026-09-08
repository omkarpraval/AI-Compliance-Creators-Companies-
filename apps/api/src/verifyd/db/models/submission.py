from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Submission(Base, TimestampedUUIDMixin):
    __tablename__ = "submissions"

    contract_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    contract_version: Mapped[int] = mapped_column(Integer, nullable=False)
    creator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    kind: Mapped[str] = mapped_column(String(50), default="final", nullable=False)  # 'preflight' | 'final'
    video_file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    caption_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    platform_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False
    )  # 'draft' | 'uploaded' | 'queued' | 'processing' | 'report_ready' | 'in_review' | 'approved' | 'rejected' | 'changes_requested' | 'failed'
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="submissions")
    creator: Mapped["CreatorProfile"] = relationship("CreatorProfile")
    artifacts: Mapped[List["AnalysisArtifact"]] = relationship("AnalysisArtifact", back_populates="submission", cascade="all, delete-orphan")
    compliance_report: Mapped[Optional["ComplianceReport"]] = relationship("ComplianceReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="submission", cascade="all, delete-orphan")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="submission", cascade="all, delete-orphan")
