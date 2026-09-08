from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIClauseItem(BaseModel):
    clause_ref: str
    source_text: str
    requirement: str
    clause_type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    modality: str = "mixed"
    severity: str = "standard"
    is_auto_checkable: bool = True
    confidence: float = 1.0
    source_page: Optional[int] = 1


class AIExtractClausesOutput(BaseModel):
    clauses: List[AIClauseItem]
    unparsed_sections: List[str] = []


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class AIVisualEvent(BaseModel):
    target: str  # 'logo' | 'product' | 'packaging' | 'person'
    label: str
    start_ms: int
    end_ms: int
    bbox: Optional[BoundingBox] = None
    confidence: float = 1.0


class AIOnScreenText(BaseModel):
    text: str
    start_ms: int
    end_ms: int
    position: Optional[str] = "bottom"
    confidence: float = 1.0


class AIEvidenceItem(BaseModel):
    type: str
    start_ms: int
    end_ms: int
    confidence: float = 1.0
    payload: Dict[str, Any] = Field(default_factory=dict)


class AIClauseVerdict(BaseModel):
    clause_ref: str
    verdict: str  # 'pass' | 'fail' | 'flagged'
    confidence: float
    rationale: str
    measured_value: Dict[str, Any] = Field(default_factory=dict)
    required_value: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[AIEvidenceItem] = Field(default_factory=list)


class AIVideoAnalysisOutput(BaseModel):
    visual_events: List[AIVisualEvent] = []
    on_screen_text: List[AIOnScreenText] = []
    duration_seconds: float = 30.0


class AIScoreSubmissionOutput(BaseModel):
    verdicts: List[AIClauseVerdict]
    summary: str = ""
