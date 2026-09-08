from typing import Any, Dict, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from verifyd.db.base import Base, TimestampedUUIDMixin


class AuditEvent(Base, TimestampedUUIDMixin):
    __tablename__ = "audit_events"

    actor_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    actor_type: Mapped[str] = mapped_column(String(50), default="user", nullable=False)  # 'user' | 'system' | 'api_key'
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'contract' | 'clause' | 'submission' | 'verdict'
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # 'created' | 'updated' | 'overridden' | 'reviewed'
    before: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    after: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    actor: Mapped[Optional["User"]] = relationship("User")
