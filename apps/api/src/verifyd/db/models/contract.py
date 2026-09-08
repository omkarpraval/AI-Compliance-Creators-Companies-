from decimal import Decimal
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Contract(Base, TimestampedUUIDMixin):
    __tablename__ = "contracts"

    campaign_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    creator_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("creator_profiles.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False
    )  # 'draft' | 'needs_review' | 'sent_for_signature' | 'signed' | 'superseded' | 'cancelled'
    raw_document_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    raw_document_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_content_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    parsed_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fee_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    fee_currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="contracts")
    creator: Mapped[Optional["CreatorProfile"]] = relationship("CreatorProfile")
    parent_contract: Mapped[Optional["Contract"]] = relationship("Contract", remote_side="Contract.id")
    clauses: Mapped[List["Clause"]] = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")
    submissions: Mapped[List["Submission"]] = relationship("Submission", back_populates="contract")
