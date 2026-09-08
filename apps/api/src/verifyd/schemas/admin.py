from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from verifyd.schemas.submission import SubmissionResponse


class JobResponse(BaseModel):
    id: str
    submission_id: Optional[str] = None
    task_name: str
    celery_task_id: Optional[str] = None
    status: str
    attempt: int
    max_attempts: int
    error_class: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminMetricsResponse(BaseModel):
    total_submissions: int
    passed_count: int
    failed_count: int
    flagged_count: int
    pass_rate: float
    avg_processing_ms: int
    total_api_spend_usd: float
    spend_by_provider: Dict[str, float]
    jobs_by_status: Dict[str, int]
    avg_turnaround_hours: float


class AuditEventResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    actor_type: str
    entity_type: str
    entity_id: str
    action: str
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
    actor_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
