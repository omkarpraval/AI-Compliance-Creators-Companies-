from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class User(Base, TimestampedUUIDMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(CITEXT, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'company_admin' | 'company_member' | 'agency_admin' | 'agency_member' | 'creator' | 'platform_admin'
    org_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    creator_profile: Mapped[Optional["CreatorProfile"]] = relationship("CreatorProfile", back_populates="user", uselist=False)

    @property
    def password_hash(self) -> str:
        return self.hashed_password

    @password_hash.setter
    def password_hash(self, value: str) -> None:
        self.hashed_password = value

