from typing import Any, Dict, Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Review(Base, TimestampedUUIDMixin):
    __tablename__ = "reviews"

    submission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    reviewer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    decision: Mapped[str] = mapped_column(String(50), nullable=False)  # 'approved' | 'rejected' | 'changes_requested'
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flags: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User")
