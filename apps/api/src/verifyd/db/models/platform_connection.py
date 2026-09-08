from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class PlatformConnection(Base, TimestampedUUIDMixin):
    __tablename__ = "platform_connections"

    creator_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # 'youtube' | 'instagram' | 'tiktok'
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_handle: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    creator_profile: Mapped["CreatorProfile"] = relationship("CreatorProfile", back_populates="platform_connections")
