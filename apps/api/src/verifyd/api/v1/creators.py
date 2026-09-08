from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import get_current_user, require
from verifyd.core.errors import NotFoundError, PermissionDeniedError
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.contract import Contract
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.models.user import User
from verifyd.db.session import get_async_db
from verifyd.schemas.campaign import CampaignResponse
from verifyd.schemas.creator import (
    CreatorIDResponse,
    CreatorProfileResponse,
    CreatorProfileUpdate,
    CreatorVisibilityUpdate,
)
from verifyd.services.creatorid_service import compute_creator_metrics

router = APIRouter(tags=["Creators"])


@router.get("/creators/me", response_model=CreatorProfileResponse)
async def get_my_creator_profile(
    current_user: User = Depends(require("manage_creatorid")),
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(CreatorProfile)
        .options(selectinload(CreatorProfile.user))
        .where(CreatorProfile.user_id == current_user.id)
    )
    res = await db.execute(query)
    profile = res.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Creator profile not found")

    return CreatorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        handle=profile.handle,
        bio=profile.bio,
        primary_language=profile.primary_language,
        niches=profile.niches or [],
        is_verified=profile.is_verified,
        public_id_enabled=profile.public_id_enabled,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
    )


@router.patch("/creators/me", response_model=CreatorProfileResponse)
async def update_my_creator_profile(
    req: CreatorProfileUpdate,
    current_user: User = Depends(require("manage_creatorid")),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(CreatorProfile).where(CreatorProfile.user_id == current_user.id)
    res = await db.execute(query)
    profile = res.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Creator profile not found")

    if req.bio is not None:
        profile.bio = req.bio
    if req.primary_language is not None:
        profile.primary_language = req.primary_language
    if req.niches is not None:
        profile.niches = req.niches
    if req.public_id_enabled is not None:
        profile.public_id_enabled = req.public_id_enabled

    await db.commit()
    await db.refresh(profile)

    return CreatorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        handle=profile.handle,
        bio=profile.bio,
        primary_language=profile.primary_language,
        niches=profile.niches or [],
        is_verified=profile.is_verified,
        public_id_enabled=profile.public_id_enabled,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
    )


@router.get("/creators/me/campaigns", response_model=List[CampaignResponse])
async def list_my_campaigns(
    current_user: User = Depends(require("manage_creatorid")),
    db: AsyncSession = Depends(get_async_db),
):
    profile_query = select(CreatorProfile).where(CreatorProfile.user_id == current_user.id)
    p_res = await db.execute(profile_query)
    profile = p_res.scalar_one_or_none()
    if not profile:
        return []

    query = (
        select(Campaign)
        .join(Contract, Contract.campaign_id == Campaign.id)
        .where(Contract.creator_id == profile.id, Campaign.deleted_at.is_(None))
        .distinct()
    )
    res = await db.execute(query)
    campaigns = res.scalars().all()

    return [
        CampaignResponse(
            id=c.id,
            org_id=c.org_id,
            name=c.name,
            product_name=c.product_name,
            description=c.description,
            starts_on=c.starts_on,
            ends_on=c.ends_on,
            status=c.status,
            created_by=c.created_by,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in campaigns
    ]


@router.get("/creators/me/creatorid", response_model=CreatorIDResponse)
async def get_my_creatorid(
    current_user: User = Depends(require("manage_creatorid")),
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(CreatorProfile)
        .options(selectinload(CreatorProfile.user))
        .where(CreatorProfile.user_id == current_user.id)
    )
    res = await db.execute(query)
    profile = res.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Creator profile not found")

    return await compute_creator_metrics(db, profile)


@router.post("/creators/me/creatorid/visibility", response_model=CreatorProfileResponse)
async def update_creatorid_visibility(
    req: CreatorVisibilityUpdate,
    current_user: User = Depends(require("manage_creatorid")),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(CreatorProfile).where(CreatorProfile.user_id == current_user.id)
    res = await db.execute(query)
    profile = res.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Creator profile not found")

    profile.public_id_enabled = req.enabled
    await db.commit()
    await db.refresh(profile)

    return CreatorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        handle=profile.handle,
        bio=profile.bio,
        primary_language=profile.primary_language,
        niches=profile.niches or [],
        is_verified=profile.is_verified,
        public_id_enabled=profile.public_id_enabled,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
    )


@router.get("/public/creatorid/{handle}", response_model=CreatorIDResponse)
async def get_public_creatorid(
    handle: str,
    db: AsyncSession = Depends(get_async_db),
):
    query = (
        select(CreatorProfile)
        .options(selectinload(CreatorProfile.user))
        .where(CreatorProfile.handle == handle.lower())
    )
    res = await db.execute(query)
    profile = res.scalar_one_or_none()
    if not profile or not profile.public_id_enabled:
        raise NotFoundError("Creator profile not found or is set to private")

    return await compute_creator_metrics(db, profile)
