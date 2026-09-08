from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import get_current_user
from verifyd.core.errors import ConflictError, PermissionDeniedError, ValidationError
from verifyd.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from verifyd.db.models.organization import Organization
from verifyd.db.models.user import User
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.session import get_async_db
from verifyd.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, response: Response, db: AsyncSession = Depends(get_async_db)):
    # Check if user already exists
    stmt = select(User).where(User.email == req.email.lower())
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise ConflictError(f"User with email '{req.email}' already exists")

    org_id = None
    if req.role in ("company_admin", "company_member"):
        # Create or find organization
        org_name = req.org_name or f"{req.full_name}'s Organization"
        org = Organization(name=org_name, type="brand")
        db.add(org)
        await db.flush()
        org_id = org.id

    user = User(
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        org_id=org_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    handle = None
    if req.role == "creator":
        creator_handle = (req.handle or req.email.split("@")[0]).lower()
        profile = CreatorProfile(
            user_id=user.id,
            handle=creator_handle,
            primary_language="en",
            niches=["Lifestyle", "Beauty"],
            is_verified=False,
            public_id_enabled=True,
        )
        db.add(profile)
        await db.flush()
        handle = creator_handle

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": user.id, "role": user.role, "org_id": user.org_id})
    refresh_token = create_refresh_token({"sub": user.id})

    # Set httpOnly cookie for refresh
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    user_resp = UserResponse(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        handle=handle,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_async_db)):
    stmt = select(User).where(User.email == req.email.lower())
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    handle = None
    if user.role == "creator":
        p_stmt = select(CreatorProfile).where(CreatorProfile.user_id == user.id)
        p_res = await db.execute(p_stmt)
        profile = p_res.scalar_one_or_none()
        if profile:
            handle = profile.handle

    access_token = create_access_token({"sub": user.id, "role": user.role, "org_id": user.org_id})
    refresh_token = create_refresh_token({"sub": user.id})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    user_resp = UserResponse(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        handle=handle,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, response: Response, db: AsyncSession = Depends(get_async_db)):
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise PermissionDeniedError("Invalid token type")

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise PermissionDeniedError("User not found or inactive")

    access_token = create_access_token({"sub": user.id, "role": user.role, "org_id": user.org_id})
    new_refresh_token = create_refresh_token({"sub": user.id})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    handle = None
    if user.role == "creator":
        p_stmt = select(CreatorProfile).where(CreatorProfile.user_id == user.id)
        p_res = await db.execute(p_stmt)
        profile = p_res.scalar_one_or_none()
        if profile:
            handle = profile.handle

    user_resp = UserResponse(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        handle=handle,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=user_resp,
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    handle = None
    if current_user.role == "creator":
        p_stmt = select(CreatorProfile).where(CreatorProfile.user_id == current_user.id)
        p_res = await db.execute(p_stmt)
        profile = p_res.scalar_one_or_none()
        if profile:
            handle = profile.handle

    return UserResponse(
        id=current_user.id,
        org_id=current_user.org_id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_active=current_user.is_active,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        handle=handle,
    )
