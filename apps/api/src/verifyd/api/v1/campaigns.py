from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import assert_can_access, get_current_user, require
from verifyd.core.errors import NotFoundError
from verifyd.core.pagination import PaginatedResponse, decode_cursor, encode_cursor
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.contract import Contract
from verifyd.db.models.submission import Submission
from verifyd.db.models.user import User
from verifyd.db.session import get_async_db
from verifyd.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from verifyd.schemas.contract import ContractResponse

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=PaginatedResponse[CampaignResponse])
async def list_campaigns(
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(require("view_org_submissions")),
    db: AsyncSession = Depends(get_async_db),
):
    offset = decode_cursor(cursor)
    query = select(Campaign).where(Campaign.deleted_at.is_(None))

    if current_user.role != "platform_admin":
        query = query.where(Campaign.org_id == current_user.org_id)

    if status:
        query = query.where(Campaign.status == status)

    query = query.order_by(Campaign.created_at.desc(), Campaign.id.desc()).offset(offset).limit(limit + 1)
    res = await db.execute(query)
    campaigns = res.scalars().all()

    items = []
    for c in campaigns[:limit]:
        # Count contracts & submissions
        contract_count_query = select(func.count(Contract.id)).where(Contract.campaign_id == c.id, Contract.deleted_at.is_(None))
        sub_count_query = (
            select(func.count(Submission.id))
            .join(Contract, Submission.contract_id == Contract.id)
            .where(Contract.campaign_id == c.id, Submission.deleted_at.is_(None))
        )
        cc_res = await db.execute(contract_count_query)
        sc_res = await db.execute(sub_count_query)

        items.append(
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
                contract_count=cc_res.scalar() or 0,
                submission_count=sc_res.scalar() or 0,
            )
        )

    next_cursor = encode_cursor(offset + limit) if len(campaigns) > limit else None
    return PaginatedResponse(items=items, next_cursor=next_cursor)


@router.post("", response_model=CampaignResponse)
async def create_campaign(
    req: CampaignCreate,
    current_user: User = Depends(require("create_campaign")),
    db: AsyncSession = Depends(get_async_db),
):
    campaign = Campaign(
        org_id=current_user.org_id,
        name=req.name,
        product_name=req.product_name,
        description=req.description,
        starts_on=req.starts_on,
        ends_on=req.ends_on,
        status="active",
        created_by=current_user.id,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        name=campaign.name,
        product_name=campaign.product_name,
        description=campaign.description,
        starts_on=campaign.starts_on,
        ends_on=campaign.ends_on,
        status=campaign.status,
        created_by=campaign.created_by,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        contract_count=0,
        submission_count=0,
    )


@router.get("/{id}", response_model=CampaignResponse)
async def get_campaign(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Campaign).where(Campaign.id == id, Campaign.deleted_at.is_(None))
    res = await db.execute(query)
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    assert_can_access(current_user, campaign)

    contract_count_query = select(func.count(Contract.id)).where(Contract.campaign_id == campaign.id, Contract.deleted_at.is_(None))
    sub_count_query = (
        select(func.count(Submission.id))
        .join(Contract, Submission.contract_id == Contract.id)
        .where(Contract.campaign_id == campaign.id, Submission.deleted_at.is_(None))
    )
    cc_res = await db.execute(contract_count_query)
    sc_res = await db.execute(sub_count_query)

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        name=campaign.name,
        product_name=campaign.product_name,
        description=campaign.description,
        starts_on=campaign.starts_on,
        ends_on=campaign.ends_on,
        status=campaign.status,
        created_by=campaign.created_by,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        contract_count=cc_res.scalar() or 0,
        submission_count=sc_res.scalar() or 0,
    )


@router.patch("/{id}", response_model=CampaignResponse)
async def update_campaign(
    id: str,
    req: CampaignUpdate,
    current_user: User = Depends(require("create_campaign")),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Campaign).where(Campaign.id == id, Campaign.deleted_at.is_(None))
    res = await db.execute(query)
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    assert_can_access(current_user, campaign)

    if req.name is not None:
        campaign.name = req.name
    if req.product_name is not None:
        campaign.product_name = req.product_name
    if req.description is not None:
        campaign.description = req.description
    if req.starts_on is not None:
        campaign.starts_on = req.starts_on
    if req.ends_on is not None:
        campaign.ends_on = req.ends_on
    if req.status is not None:
        campaign.status = req.status

    await db.commit()
    await db.refresh(campaign)

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        name=campaign.name,
        product_name=campaign.product_name,
        description=campaign.description,
        starts_on=campaign.starts_on,
        ends_on=campaign.ends_on,
        status=campaign.status,
        created_by=campaign.created_by,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


@router.post("/{id}/close", response_model=CampaignResponse)
async def close_campaign(
    id: str,
    current_user: User = Depends(require("create_campaign")),
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Campaign).where(Campaign.id == id, Campaign.deleted_at.is_(None))
    res = await db.execute(query)
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    assert_can_access(current_user, campaign)
    campaign.status = "closed"
    await db.commit()
    await db.refresh(campaign)

    return CampaignResponse(
        id=campaign.id,
        org_id=campaign.org_id,
        name=campaign.name,
        product_name=campaign.product_name,
        description=campaign.description,
        starts_on=campaign.starts_on,
        ends_on=campaign.ends_on,
        status=campaign.status,
        created_by=campaign.created_by,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


@router.get("/{id}/contracts", response_model=PaginatedResponse[ContractResponse])
async def list_campaign_contracts(
    id: str,
    cursor: Optional[str] = None,
    limit: int = Query(default=25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    c_query = select(Campaign).where(Campaign.id == id, Campaign.deleted_at.is_(None))
    c_res = await db.execute(c_query)
    campaign = c_res.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    assert_can_access(current_user, campaign)

    offset = decode_cursor(cursor)
    query = (
        select(Contract)
        .where(Contract.campaign_id == id, Contract.deleted_at.is_(None))
        .order_by(Contract.version.desc())
        .offset(offset)
        .limit(limit + 1)
    )
    res = await db.execute(query)
    contracts = res.scalars().all()

    items = [
        ContractResponse(
            id=ct.id,
            campaign_id=ct.campaign_id,
            creator_id=ct.creator_id,
            version=ct.version,
            parent_contract_id=ct.parent_contract_id,
            source_file_key=ct.source_file_key,
            status=ct.status,
            esign_envelope_id=ct.esign_envelope_id,
            signed_at=ct.signed_at,
            fee_amount=float(ct.fee_amount) if ct.fee_amount else None,
            fee_currency=ct.fee_currency,
            created_at=ct.created_at,
            updated_at=ct.updated_at,
            campaign_name=campaign.name,
        )
        for ct in contracts[:limit]
    ]

    next_cursor = encode_cursor(offset + limit) if len(contracts) > limit else None
    return PaginatedResponse(items=items, next_cursor=next_cursor)
