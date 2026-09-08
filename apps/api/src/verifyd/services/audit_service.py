from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.db.models.audit_event import AuditEvent


async def record_audit_event(
    session: AsyncSession,
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: Optional[str] = None,
    actor_type: str = "user",
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditEvent:
    """Records an immutable append-only audit event."""
    event = AuditEvent(
        actor_id=actor_id,
        actor_type=actor_type,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before=before,
        after=after,
        ip_address=ip_address,
    )
    session.add(event)
    await session.flush()
    return event
