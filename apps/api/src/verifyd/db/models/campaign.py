from datetime import date
from typing import List, Optional
from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Campaign(Base, TimestampedUUIDMixin):
    __tablename__ = "campaigns"

    org_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # 'draft' | 'active' | 'paused' | 'completed' | 'archived'
    starts_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ends_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="campaigns")
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="campaign", cascade="all, delete-orphan")
