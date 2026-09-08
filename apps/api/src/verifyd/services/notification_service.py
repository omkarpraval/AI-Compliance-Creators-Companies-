from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.db.models.notification import Notification


async def create_notification(
    session: AsyncSession,
    user_id: str,
    template: str,
    payload: Dict[str, Any],
    channel: str = "in_app",
) -> Notification:
    """Dispatches a new user notification."""
    notif = Notification(
        user_id=user_id,
        template=template,
        payload=payload,
        channel=channel,
        status="unread",
    )
    session.add(notif)
    await session.flush()
    return notif
