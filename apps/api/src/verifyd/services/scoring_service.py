import re
from typing import Any, Dict, List, Tuple
from verifyd.core.logging import get_logger

logger = get_logger("services.scoring")

SEVERITY_WEIGHTS = {
    "critical": 3,
    "standard": 2,
    "advisory": 1,
}


def compute_deterministic_post_checks(
    clauses: List[Dict[str, Any]],
    raw_verdicts: List[Dict[str, Any]],
    transcript_segments: List[Dict[str, Any]],
    visual_events: List[Dict[str, Any]],
    on_screen_text: List[Dict[str, Any]],
    caption_text: str = "",
    duration_seconds: float = 30.0,
) -> List[Dict[str, Any]]:
    """
    Deterministic post-checks in code.
    The model finds and localises evidence; arithmetic over that evidence is never delegated to it.
    If code arithmetic disagrees with model verdict, code wins and marks verdict as flagged with explanation.
    """
    final_verdicts = []
    verdict_by_ref = {v.get("clause_ref"): v for v in raw_verdicts}

    for clause in clauses:
        ref = clause.get("clause_ref", "")
        c_type = clause.get("clause_type", "manual_only")
        params = clause.get("params", {})
        severity = clause.get("severity", "standard")
        model_v = verdict_by_ref.get(ref, {})

        model_verdict = model_v.get("verdict", "flagged")
        model_confidence = model_v.get("confidence", 0.8)
        evidence = model_v.get("evidence", [])
        measured = model_v.get("measured_value", {}).copy()
        required = model_v.get("required_value", {}).copy()
        rationale = model_v.get("rationale", "")

        # Rule: Pass/Fail must have evidence. If no evidence, downgrade to flagged.
        valid_evidence = []
        for ev in evidence:
            s_ms = ev.get("start_ms", 0)
            e_ms = ev.get("end_ms", 0)
            # Timestamp validity check against video duration
            if s_ms <= duration_seconds * 1000 and e_ms <= (duration_seconds + 1.0) * 1000:
                valid_evidence.append(ev)

        if model_verdict in ("pass", "fail") and not valid_evidence:
            model_verdict = "flagged"
            rationale = "Verdict downgraded to flagged: no verifiable timestamped evidence anchors provided."

        code_verdict = model_verdict
        arithmetic_override = False

        # 1. min_spoken_duration check
        if c_type == "min_spoken_duration":
            target_sec = float(params.get("seconds", 30))
            # Calculate total duration from valid transcript spans in evidence
            total_spoken = 0.0
            for ev in valid_evidence:
                if ev.get("type") == "transcript_span":
                    dur = (ev.get("end_ms", 0) - ev.get("start_ms", 0)) / 1000.0
                    total_spoken += max(0.0, dur)

            measured["spoken_seconds"] = round(total_spoken, 1)
            required["seconds"] = target_sec

            if total_spoken >= target_sec:
                code_verdict = "pass"
            else:
                code_verdict = "fail"

            if code_verdict != model_verdict:
                arithmetic_override = True
                rationale = f"Deterministic check measured {total_spoken:.1f}s of speech against {target_sec}s required. Disagreement with AI model flagged for review."
                code_verdict = "flagged"

        # 2. required_phrase check
        elif c_type == "required_phrase":
            phrases = params.get("phrases", [])
            min_occurrences = int(params.get("min_occurrences", 1))
            total_occurrences = 0

            # Count occurrences in transcript segments
            full_transcript = " ".join([s.get("text", "") for s in transcript_segments]).lower()
            for phrase in phrases:
                pattern = re.escape(phrase.lower())
                matches = re.findall(pattern, full_transcript)
                total_occurrences += len(matches)

            measured["occurrences"] = total_occurrences
            required["min_occurrences"] = min_occurrences

            code_verdict = "pass" if total_occurrences >= min_occurrences else "fail"
            if code_verdict != model_verdict:
                arithmetic_override = True
                rationale = f"Code found {total_occurrences} occurrence(s) of required phrase(s) against {min_occurrences} required. Flagged for reviewer review."
                code_verdict = "flagged"

        # 3. visual_presence check
        elif c_type == "visual_presence":
            min_sec = float(params.get("min_seconds", 5))
            total_vis_sec = 0.0
            for ev in valid_evidence:
                if ev.get("type") == "visual_detection":
                    dur = (ev.get("end_ms", 0) - ev.get("start_ms", 0)) / 1000.0
                    total_vis_sec += max(0.0, dur)

            measured["visible_seconds"] = round(total_vis_sec, 1)
            required["min_seconds"] = min_sec

            code_verdict = "pass" if total_vis_sec >= min_sec else "fail"
            if code_verdict != model_verdict:
                arithmetic_override = True
                rationale = f"Visual evidence totaled {total_vis_sec:.1f}s against {min_sec}s required. Disagreement flagged."
                code_verdict = "flagged"

        # 4. visual_timing check
        elif c_type == "visual_timing":
            within_sec = float(params.get("within_seconds", 10))
            first_ms = 9999999
            for ev in valid_evidence:
                if ev.get("type") == "visual_detection":
                    first_ms = min(first_ms, ev.get("start_ms", 9999999))

            first_sec = first_ms / 1000.0 if first_ms != 9999999 else 999.0
            measured["first_appearance_seconds"] = round(first_sec, 1)
            required["within_seconds"] = within_sec

            code_verdict = "pass" if first_sec <= within_sec else "fail"
            if code_verdict != model_verdict:
                arithmetic_override = True
                rationale = f"First visual appearance detected at {first_sec:.1f}s against {within_sec}s deadline. Flagged for review."
                code_verdict = "flagged"

        # 5. disclosure_tag check
        elif c_type == "disclosure_tag":
            accepted = [t.lower() for t in params.get("accepted", ["#ad", "paid partnership"])]
            tag_found_caption = any(t in caption_text.lower() for t in accepted) if caption_text else False
            tag_found_ocr = False
            earliest_ocr_sec = 999.0

            for ocr in on_screen_text:
                text = ocr.get("text", "").lower()
                if any(t in text for t in accepted):
                    tag_found_ocr = True
                    earliest_ocr_sec = min(earliest_ocr_sec, ocr.get("start_ms", 0) / 1000.0)

            measured["caption_tag_found"] = tag_found_caption
            measured["on_screen_tag_found"] = tag_found_ocr
            within_sec = float(params.get("within_seconds", 5))

            if tag_found_caption or (tag_found_ocr and earliest_ocr_sec <= within_sec):
                code_verdict = "pass"
            else:
                code_verdict = "fail"

        # Construct finalized verdict dict
        final_verdicts.append({
            "clause_id": clause.get("id"),
            "clause_ref": ref,
            "verdict": code_verdict,
            "confidence": model_confidence,
            "rationale": rationale or f"Clause {ref} evaluated.",
            "measured_value": measured,
            "required_value": required,
            "evidence": valid_evidence,
            "severity": severity,
        })

    return final_verdicts


def calculate_overall_compliance(verdicts: List[Dict[str, Any]]) -> Tuple[int, str, int, int, int, int]:
    """
    Computes weighted score and overall submission verdict.
    overall_score = weighted percentage of clauses passed:
      critical = 3, standard = 2, advisory = 1
    Verdict = 'fail' if any critical failed, 'needs_review' if any flagged, otherwise 'pass'.
    """
    total_clauses = len(verdicts)
    if total_clauses == 0:
        return 100, "pass", 0, 0, 0, 0

    passed_count = 0
    failed_count = 0
    flagged_count = 0

    weighted_points = 0.0
    max_possible_points = 0.0

    critical_failed = False
    any_flagged = False

    for v in verdicts:
        verdict = v.get("verdict", "flagged")
        # Check for overrides
        if v.get("is_overridden") and v.get("override_verdict"):
            verdict = v.get("override_verdict")

        severity = v.get("severity", "standard")
        weight = SEVERITY_WEIGHTS.get(severity, 2)
        max_possible_points += weight

        if verdict == "pass":
            passed_count += 1
            weighted_points += weight
        elif verdict == "fail":
            failed_count += 1
            if severity == "critical":
                critical_failed = True
        else:  # flagged
            flagged_count += 1
            any_flagged = True
            weighted_points += weight * 0.5  # partial credit for calculation

    if max_possible_points > 0:
        overall_score = int(round((weighted_points / max_possible_points) * 100))
    else:
        overall_score = 100

    overall_score = max(0, min(100, overall_score))

    if critical_failed:
        submission_verdict = "fail"
    elif any_flagged:
        submission_verdict = "needs_review"
    else:
        submission_verdict = "pass"

    return overall_score, submission_verdict, total_clauses, passed_count, failed_count, flagged_count
