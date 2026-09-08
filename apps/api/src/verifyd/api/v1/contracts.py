from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.api.deps import assert_can_access, get_current_user, require
from verifyd.core.errors import DomainStateError, NotFoundError, ValidationError
from verifyd.db.models.campaign import Campaign
from verifyd.db.models.contract import Contract
from verifyd.db.models.clause import Clause
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.models.job import Job
from verifyd.db.models.pdf_extraction import PDFExtraction
from verifyd.db.models.user import User
from verifyd.db.session import get_db
from verifyd.ingestion.pdf import ExtractedPage
from verifyd.schemas.contract import (
    ContractCreate,
    ContractDiffResponse,
    ContractResponse,
    ContractUpdate,
    DocumentSummaryResponse,
)
from verifyd.schemas.clause import ClauseCreate, ClauseResponse, ClauseUpdate
from verifyd.services.clause_service import compute_clause_diff
from verifyd.workers.tasks.extract_clauses import run_extract_clauses_async

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("", response_model=ContractResponse)
async def create_contract(
    req: ContractCreate,
    current_user: User = Depends(require("upload_contract")),
    db: AsyncSession = Depends(get_db),
):
    c_query = select(Campaign).where(Campaign.id == req.campaign_id, Campaign.deleted_at.is_(None))
    c_res = await db.execute(c_query)
    campaign = c_res.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    assert_can_access(current_user, campaign)

    contract = Contract(
        campaign_id=req.campaign_id,
        creator_id=req.creator_id,
        version=1,
        raw_document_key=req.raw_document_key,
        raw_document_filename=req.raw_document_filename,
        status="draft",
        fee_amount=req.fee_amount,
        fee_currency=req.fee_currency,
        notes=req.notes,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return ContractResponse.model_validate(contract)


@router.get("/{id}", response_model=ContractResponse)
async def get_contract(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Contract, Campaign, CreatorProfile)
        .join(Campaign, Contract.campaign_id == Campaign.id)
        .outerjoin(CreatorProfile, Contract.creator_id == CreatorProfile.id)
        .where(Contract.id == id, Contract.deleted_at.is_(None))
    )
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign, creator = row
    assert_can_access(current_user, campaign)

    cl_query = select(Clause).where(Clause.contract_id == id, Clause.deleted_at.is_(None)).order_by(Clause.ordinal, Clause.id)
    cl_res = await db.execute(cl_query)
    clauses = cl_res.scalars().all()

    resp = ContractResponse.model_validate(contract)
    resp.creator_handle = creator.handle if creator else None
    resp.clauses = [ClauseResponse.model_validate(c) for c in clauses]
    return resp


@router.get("/{id}/document", response_model=DocumentSummaryResponse)
async def get_contract_document(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the parsed document text and metadata without the heavy word-level bounding box payload."""
    query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign = row
    assert_can_access(current_user, campaign)

    if not contract.source_content_hash:
        raise NotFoundError("No parsed document text found for this contract")

    ext_query = select(PDFExtraction).where(PDFExtraction.content_hash == contract.source_content_hash)
    ext_res = await db.execute(ext_query)
    doc_ext = ext_res.scalar_one_or_none()
    if not doc_ext:
        raise NotFoundError("Document extraction record not found")

    return DocumentSummaryResponse(
        page_count=doc_ext.page_count,
        full_text=doc_ext.full_text,
        is_scanned=doc_ext.is_scanned,
        extraction_method=doc_ext.extraction_method,
        content_hash=doc_ext.content_hash,
        char_count=doc_ext.char_count,
    )


@router.get("/{id}/document/pages/{page}", response_model=ExtractedPage)
async def get_contract_document_page(
    id: str,
    page: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns single page coordinates including word-level bounding boxes for frontend highlighting."""
    query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign = row
    assert_can_access(current_user, campaign)

    if not contract.source_content_hash:
        raise NotFoundError("No parsed document found")

    ext_query = select(PDFExtraction).where(PDFExtraction.content_hash == contract.source_content_hash)
    ext_res = await db.execute(ext_query)
    doc_ext = ext_res.scalar_one_or_none()
    if not doc_ext:
        raise NotFoundError("Document extraction record not found")

    for p in doc_ext.pages:
        if p.get("page") == page:
            return ExtractedPage.model_validate(p)

    raise NotFoundError(f"Page {page} not found in document extraction (document has {doc_ext.page_count} pages)")


@router.get("/{id}/clauses", response_model=List[ClauseResponse])
async def list_contract_clauses(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign = row
    assert_can_access(current_user, campaign)

    cl_query = select(Clause).where(Clause.contract_id == id, Clause.deleted_at.is_(None)).order_by(Clause.ordinal, Clause.id)
    cl_res = await db.execute(cl_query)
    clauses = cl_res.scalars().all()
    return [ClauseResponse.model_validate(c) for c in clauses]


@router.post("/{id}/extract")
async def extract_contract_clauses(
    id: str,
    current_user: User = Depends(require("upload_contract")),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign = row
    assert_can_access(current_user, campaign)

    job = Job(
        task_name="extract_clauses",
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    await run_extract_clauses_async(contract_id=id, job_id=job.id)
    return {"status": "queued", "job_id": job.id}


@router.patch("/{id}/clauses/{clause_id}", response_model=ClauseResponse)
async def update_contract_clause(
    id: str,
    clause_id: str,
    req: ClauseUpdate,
    current_user: User = Depends(require("edit_clauses")),
    db: AsyncSession = Depends(get_db),
):
    cl_query = select(Clause).where(Clause.id == clause_id, Clause.contract_id == id, Clause.deleted_at.is_(None))
    cl_res = await db.execute(cl_query)
    clause = cl_res.scalar_one_or_none()
    if not clause:
        raise NotFoundError("Clause not found")

    if req.clause_ref is not None:
        clause.clause_ref = req.clause_ref
    if req.source_text is not None:
        clause.source_text = req.source_text
    if req.requirement is not None:
        clause.requirement = req.requirement
    if req.clause_type is not None:
        clause.clause_type = req.clause_type
    if req.params is not None:
        clause.params = req.params
    if req.modality is not None:
        clause.modality = req.modality
    if req.severity is not None:
        clause.severity = req.severity
    if req.is_auto_checkable is not None:
        clause.is_auto_checkable = req.is_auto_checkable
    if req.confidence is not None:
        clause.confidence = req.confidence
    if req.review_status is not None:
        clause.review_status = req.review_status
    if req.source_page is not None:
        clause.source_page = req.source_page
    if req.source_bbox is not None:
        clause.source_bbox = req.source_bbox

    clause.edited_by = current_user.id
    clause.edited_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(clause)
    return ClauseResponse.model_validate(clause)


@router.post("/{id}/confirm", response_model=ContractResponse)
async def confirm_contract(
    id: str,
    current_user: User = Depends(require("confirm_checklist")),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    res = await db.execute(query)
    row = res.first()
    if not row:
        raise NotFoundError("Contract not found")

    contract, campaign = row
    assert_can_access(current_user, campaign)

    # Check unreviewed clauses
    cl_query = select(Clause).where(Clause.contract_id == id, Clause.review_status == "unreviewed", Clause.deleted_at.is_(None))
    cl_res = await db.execute(cl_query)
    unreviewed = cl_res.scalars().all()
    if unreviewed:
        raise ValidationError(
            message=f"Cannot send agreement: {len(unreviewed)} clauses have not been reviewed.",
            code="UNREVIEWED_CLAUSES",
            details={"unreviewed_count": len(unreviewed)},
        )

    contract.status = "sent_for_signature"
    await db.commit()
    await db.refresh(contract)
    return ContractResponse.model_validate(contract)


@router.get("/{id}/diff/{other_id}", response_model=ContractDiffResponse)
async def diff_contracts(
    id: str,
    other_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c1_query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == id, Contract.deleted_at.is_(None))
    c2_query = select(Contract, Campaign).join(Campaign, Contract.campaign_id == Campaign.id).where(Contract.id == other_id, Contract.deleted_at.is_(None))
    c1_res = await db.execute(c1_query)
    c2_res = await db.execute(c2_query)
    r1 = c1_res.first()
    r2 = c2_res.first()
    if not r1 or not r2:
        raise NotFoundError("One or both contracts not found for comparison")

    ct1, camp1 = r1
    ct2, camp2 = r2
    assert_can_access(current_user, camp1)
    assert_can_access(current_user, camp2)

    cl1_q = select(Clause).where(Clause.contract_id == id, Clause.deleted_at.is_(None)).order_by(Clause.ordinal, Clause.id)
    cl2_q = select(Clause).where(Clause.contract_id == other_id, Clause.deleted_at.is_(None)).order_by(Clause.ordinal, Clause.id)
    cl1_res = await db.execute(cl1_q)
    cl2_res = await db.execute(cl2_q)
    clauses1 = cl1_res.scalars().all()
    clauses2 = cl2_res.scalars().all()

    return compute_clause_diff(
        base_clauses=clauses1,
        target_clauses=clauses2,
        base_contract_id=ct1.id,
        base_version=ct1.version,
        target_contract_id=ct2.id,
        target_version=ct2.version,
    )
