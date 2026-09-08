from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from verifyd.schemas.clause import ClauseResponse
from verifyd.ingestion.pdf import ExtractedDocument, ExtractedPage


class ContractCreate(BaseModel):
    campaign_id: str
    creator_id: Optional[str] = None
    raw_document_key: Optional[str] = None
    raw_document_filename: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    fee_currency: str = "INR"
    notes: Optional[str] = None


class ContractUpdate(BaseModel):
    status: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    fee_currency: Optional[str] = None
    notes: Optional[str] = None


class ContractResponse(BaseModel):
    id: str
    campaign_id: str
    creator_id: Optional[str] = None
    version: int
    parent_contract_id: Optional[str] = None
    status: str
    raw_document_key: Optional[str] = None
    raw_document_filename: Optional[str] = None
    source_content_hash: Optional[str] = None
    parsed_at: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    fee_currency: str
    notes: Optional[str] = None
    creator_handle: Optional[str] = None
    clauses: Optional[List[ClauseResponse]] = None

    model_config = ConfigDict(from_attributes=True)


class ClauseDiffItem(BaseModel):
    change_type: str  # 'added' | 'removed' | 'modified' | 'unchanged'
    clause_ref: str
    current_clause: Optional[ClauseResponse] = None
    previous_clause: Optional[ClauseResponse] = None
    diff_fields: Optional[List[str]] = None


class ContractDiffResponse(BaseModel):
    base_contract_id: str
    base_version: int
    target_contract_id: str
    target_version: int
    summary: str
    diff_items: List[ClauseDiffItem]


class DocumentSummaryResponse(BaseModel):
    page_count: int
    full_text: str
    is_scanned: bool
    extraction_method: str
    content_hash: str
    char_count: int
