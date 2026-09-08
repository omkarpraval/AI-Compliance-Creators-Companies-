from typing import Any, Dict, List
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class Organization(Base, TimestampedUUIDMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'brand' | 'agency'
    settings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="organization", cascade="all, delete-orphan")
