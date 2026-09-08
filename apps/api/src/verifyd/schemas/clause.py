from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ClauseCreate(BaseModel):
    ordinal: int = 0
    clause_ref: str
    source_text: str
    requirement: str
    clause_type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    modality: str = "mixed"
    severity: str = "standard"
    is_auto_checkable: bool = True
    confidence: float = 1.0
    source_page: Optional[int] = None
    source_bbox: Optional[Dict[str, Any]] = None


class ClauseUpdate(BaseModel):
    clause_ref: Optional[str] = None
    source_text: Optional[str] = None
    requirement: Optional[str] = None
    clause_type: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    modality: Optional[str] = None
    severity: Optional[str] = None
    is_auto_checkable: Optional[bool] = None
    confidence: Optional[float] = None
    review_status: Optional[str] = None
    source_page: Optional[int] = None
    source_bbox: Optional[Dict[str, Any]] = None


class ClauseResponse(BaseModel):
    id: str
    contract_id: str
    ordinal: int
    clause_ref: str
    source_text: str
    requirement: str
    clause_type: str
    params: Dict[str, Any]
    modality: str
    severity: str
    is_auto_checkable: bool
    confidence: float
    review_status: str
    source_page: Optional[int] = None
    source_bbox: Optional[Dict[str, Any]] = None
    edited_by: Optional[str] = None
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
