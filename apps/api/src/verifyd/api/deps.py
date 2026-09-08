from typing import Any, Callable, List, Optional
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.core.errors import NotFoundError, PermissionDeniedError
from verifyd.core.security import decode_token
from verifyd.db.models.user import User
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.session import get_async_db

security = HTTPBearer(auto_error=False)

# Capability Matrix definition
ROLE_CAPABILITIES = {
    "company_admin": {
        "create_campaign",
        "upload_contract",
        "edit_clauses",
        "view_org_submissions",
        "review_submission",
        "view_org_audit",
        "manage_users",
    },
    "company_member": {
        "create_campaign",
        "upload_contract",
        "edit_clauses",
        "view_org_submissions",
        "review_submission",
    },
    "creator": {
        "submit_video",
        "run_preflight",
        "view_own_reports",
        "manage_creatorid",
    },
    "platform_admin": {
        "create_campaign",
        "upload_contract",
        "edit_clauses",
        "view_org_submissions",
        "review_submission",
        "override_verdict",
        "view_pipeline_jobs",
        "view_audit_log",
        "manage_users",
    },
}


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # Check cookie
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    stmt = select(User).where(User.id == user_id, User.is_active == True)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


def require(*required_capabilities: str) -> Callable:
    async def capability_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role
        user_caps = ROLE_CAPABILITIES.get(user_role, set())

        for cap in required_capabilities:
            if cap not in user_caps:
                raise PermissionDeniedError(
                    f"User role '{user_role}' lacks required capability '{cap}'",
                    details={"required": list(required_capabilities), "role": user_role},
                )
        return current_user

    return capability_checker


def assert_can_access(user: User, obj: Any) -> None:
    """
    Object-level access validation.
    Enforces that wrong-org access returns 404 (NotFoundError) rather than 403.
    """
    if user.role == "platform_admin":
        return

    # Organization-scoped entities (Campaigns, etc.)
    if hasattr(obj, "org_id") and obj.org_id:
        if user.org_id != obj.org_id:
            raise NotFoundError("Resource not found")

    # Creator-scoped entities (Submissions, CreatorProfile, etc.)
    if hasattr(obj, "creator_id") and obj.creator_id:
        if user.role == "creator":
            if user.creator_profile and obj.creator_id != user.creator_profile.id:
                raise NotFoundError("Resource not found")
        elif user.role in ("company_admin", "company_member"):
            # If checking a submission or contract, verify campaign org
            if hasattr(obj, "campaign") and obj.campaign and obj.campaign.org_id != user.org_id:
                raise NotFoundError("Resource not found")

    # Direct User match
    if hasattr(obj, "user_id") and obj.user_id:
        if user.role == "creator" and obj.user_id != user.id:
            raise NotFoundError("Resource not found")
