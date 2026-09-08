from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class EvidenceItemResponse(BaseModel):
    id: str
    clause_verdict_id: str
    type: str  # 'transcript_span' | 'visual_detection' | 'ocr_text' | 'caption_span'
    start_ms: int
    end_ms: int
    payload: Dict[str, Any]
    thumbnail_key: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClauseVerdictResponse(BaseModel):
    id: str
    report_id: str
    clause_id: str
    clause_ref: str
    verdict: str  # 'pass' | 'fail' | 'flagged'
    confidence: float
    rationale: str
    measured_value: Dict[str, Any]
    required_value: Dict[str, Any]
    is_overridden: bool
    override_verdict: Optional[str] = None
    override_reason: Optional[str] = None
    overridden_by: Optional[str] = None
    overridden_at: Optional[datetime] = None
    evidence_items: List[EvidenceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ComplianceReportResponse(BaseModel):
    id: str
    submission_id: str
    overall_score: int
    verdict: str  # 'pass' | 'fail' | 'needs_review'
    clauses_total: int
    clauses_passed: int
    clauses_failed: int
    clauses_flagged: int
    model_version: str
    prompt_version: str
    generated_at: datetime
    processing_ms: int
    cost_estimate_usd: float
    verdicts: List[ClauseVerdictResponse] = []

    model_config = ConfigDict(from_attributes=True)


class VerdictOverrideRequest(BaseModel):
    verdict: str  # 'pass' | 'fail' | 'flagged'
    reason: str  # min 20 chars
