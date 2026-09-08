from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class CreatorProfile(Base, TimestampedUUIDMixin):
    __tablename__ = "creator_profiles"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    handle: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_language: Mapped[str] = mapped_column(String(50), default="en", nullable=False)
    niches: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    public_id_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="creator_profile")
    platform_connections: Mapped[List["PlatformConnection"]] = relationship("PlatformConnection", back_populates="creator_profile", cascade="all, delete-orphan")
