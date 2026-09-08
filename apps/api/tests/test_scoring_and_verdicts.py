import pytest
from verifyd.services.scoring_service import (
    calculate_overall_compliance,
    compute_deterministic_post_checks,
)
from verifyd.services.clause_service import compute_clause_diff
from verifyd.db.models.clause import Clause

def test_scoring_arithmetic_all_pass():
    verdicts = [
        {
            "verdict": "pass",
            "severity": "standard",
            "confidence": 0.95,
        },
        {
            "verdict": "pass",
            "severity": "standard",
            "confidence": 0.98,
        },
    ]

    score, submission_verdict, total, passed, failed, flagged = calculate_overall_compliance(verdicts)
    assert score == 100
    assert submission_verdict == "pass"
    assert passed == 2
    assert failed == 0
    assert flagged == 0

def test_scoring_arithmetic_critical_fail():
    verdicts = [
        {
            "verdict": "pass",
            "severity": "standard",
            "confidence": 0.95,
        },
        {
            "verdict": "fail",
            "severity": "critical",
            "confidence": 0.92,
        },
    ]

    score, submission_verdict, total, passed, failed, flagged = calculate_overall_compliance(verdicts)
    assert submission_verdict == "fail"
    assert failed == 1
    assert score < 50

def test_deterministic_post_checks_spoken_duration_override():
    clauses = [
        {
            "clause_ref": "C-01",
            "clause_type": "min_spoken_duration",
            "params": {"seconds": 30.0},
            "severity": "critical",
        }
    ]
    raw_verdicts = [
        {
            "clause_ref": "C-01",
            "verdict": "pass", # Model hallucinated pass
            "confidence": 0.9,
            "evidence": [
                {
                    "type": "transcript_span",
                    "start_ms": 1000,
                    "end_ms": 23000, # 22 seconds measured < 30s required -> Code arithmetic must catch and flag!
                    "payload": {"text": "Lumen serum"},
                }
            ],
            "measured_value": {"spoken_seconds": 22.0},
            "required_value": {"seconds": 30.0},
        }
    ]

    checked = compute_deterministic_post_checks(
        clauses=clauses,
        raw_verdicts=raw_verdicts,
        transcript_segments=[],
        visual_events=[],
        on_screen_text=[],
        duration_seconds=30.0,
    )

    assert len(checked) == 1
    # Code arithmetic wins and marks disagreement as flagged for human adjudication!
    assert checked[0]["verdict"] == "flagged"
    assert "Disagreement with AI model flagged" in checked[0]["rationale"]

def test_clause_diff_computation():
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    base_clauses = [
        Clause(
            id="c1",
            contract_id="ct1",
            ordinal=1,
            clause_ref="C-01",
            requirement="Must feature Lumen Serum for 30s",
            source_text="Feature serum for 30s",
            clause_type="min_spoken_duration",
            params={"seconds": 30},
            modality="audio",
            severity="critical",
            is_auto_checkable=True,
            review_status="confirmed",
            confidence=0.95,
            created_at=now,
            updated_at=now,
        ),
        Clause(
            id="c2",
            contract_id="ct1",
            ordinal=2,
            clause_ref="C-02",
            requirement="Must include discount code LUMEN20 in caption",
            source_text="Include LUMEN20 in caption",
            clause_type="disclosure_tag",
            params={"tag": "LUMEN20"},
            modality="text_overlay",
            severity="standard",
            is_auto_checkable=True,
            review_status="confirmed",
            confidence=0.9,
            created_at=now,
            updated_at=now,
        ),
    ]

    target_clauses = [
        Clause(
            id="c3",
            contract_id="ct2",
            ordinal=1,
            clause_ref="C-01",
            requirement="Must feature Lumen Serum for 45s", # Modified duration
            source_text="Feature serum for 45s",
            clause_type="min_spoken_duration",
            params={"seconds": 45},
            modality="audio",
            severity="critical",
            is_auto_checkable=True,
            review_status="confirmed",
            confidence=0.95,
            created_at=now,
            updated_at=now,
        ),
        Clause(
            id="c4",
            contract_id="ct2",
            ordinal=2,
            clause_ref="C-03", # New added clause
            requirement="Must display product in first 5 seconds",
            source_text="Show in first 5s",
            clause_type="visual_timing",
            params={"max_start_sec": 5},
            modality="visual",
            severity="standard",
            is_auto_checkable=True,
            review_status="confirmed",
            confidence=0.9,
            created_at=now,
            updated_at=now,
        ),
    ]

    diff = compute_clause_diff(
        base_clauses=base_clauses,
        target_clauses=target_clauses,
        base_contract_id="ct1",
        base_version=1,
        target_contract_id="ct2",
        target_version=2,
    )

    assert diff.base_version == 1
    assert diff.target_version == 2
    assert len(diff.diff_items) == 3

    types = {item.clause_ref: item.change_type for item in diff.diff_items}
    assert types["C-01"] == "modified"
    assert types["C-02"] == "removed"
    assert types["C-03"] == "added"
