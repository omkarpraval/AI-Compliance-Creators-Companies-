from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ReviewCreate(BaseModel):
    decision: str  # 'approved' | 'rejected' | 'changes_requested'
    note: Optional[str] = None
    failed_clause_ids: Optional[List[str]] = None  # for requested changes


class ReviewResponse(BaseModel):
    id: str
    submission_id: str
    reviewer_id: str
    decision: str
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
