from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from verifyd.schemas.report import ComplianceReportResponse


class SubmissionCreate(BaseModel):
    contract_id: str
    kind: str = "final"  # 'preflight' | 'final'
    video_file_key: str
    caption_text: Optional[str] = None
    duration_seconds: Optional[float] = None
    platform_url: Optional[str] = None


class SubmissionStatusResponse(BaseModel):
    submission_id: str
    status: str
    progress: int  # 0 to 100
    stage: str  # 'Uploading' | 'Extracting audio' | 'Transcribing' | 'Analysing video' | 'Matching clauses' | 'Building report' | 'Complete' | 'Failed'
    error_message: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: str
    contract_id: str
    contract_version: int
    creator_id: str
    kind: str
    video_file_key: str
    duration_seconds: Optional[float] = None
    caption_text: Optional[str] = None
    platform_url: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None
    attempt_number: int
    created_at: datetime
    updated_at: datetime
    campaign_name: Optional[str] = None
    creator_name: Optional[str] = None
    creator_handle: Optional[str] = None
    product_name: Optional[str] = None
    report: Optional[ComplianceReportResponse] = None

    model_config = ConfigDict(from_attributes=True)
