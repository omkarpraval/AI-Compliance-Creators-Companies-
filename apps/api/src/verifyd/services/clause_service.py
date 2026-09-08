from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.db.models.contract import Contract
from verifyd.db.models.clause import Clause
from verifyd.schemas.contract import ClauseDiffItem, ContractDiffResponse
from verifyd.schemas.clause import ClauseResponse


def compute_clause_diff(
    base_clauses: List[Clause],
    target_clauses: List[Clause],
    base_contract_id: str,
    base_version: int,
    target_contract_id: str,
    target_version: int,
) -> ContractDiffResponse:
    """
    Computes a clause-by-clause diff between two versions of a contract.
    Identifies 'added', 'removed', 'modified', and 'unchanged' clauses.
    """
    base_map = {c.clause_ref: c for c in base_clauses}
    target_map = {c.clause_ref: c for c in target_clauses}

    all_refs = sorted(list(set(base_map.keys()).union(set(target_map.keys()))))
    diff_items: List[ClauseDiffItem] = []

    added_count = 0
    removed_count = 0
    modified_count = 0

    for ref in all_refs:
        base_c = base_map.get(ref)
        target_c = target_map.get(ref)

        if base_c and not target_c:
            # Removed in target
            removed_count += 1
            diff_items.append(
                ClauseDiffItem(
                    change_type="removed",
                    clause_ref=ref,
                    previous_clause=ClauseResponse.model_validate(base_c),
                    current_clause=None,
                )
            )
        elif not base_c and target_c:
            # Added in target
            added_count += 1
            diff_items.append(
                ClauseDiffItem(
                    change_type="added",
                    clause_ref=ref,
                    previous_clause=None,
                    current_clause=ClauseResponse.model_validate(target_c),
                )
            )
        else:
            # Check for modifications
            diff_fields = []
            if base_c.source_text != target_c.source_text:
                diff_fields.append("source_text")
            if base_c.requirement != target_c.requirement:
                diff_fields.append("requirement")
            if base_c.clause_type != target_c.clause_type:
                diff_fields.append("clause_type")
            if base_c.params != target_c.params:
                diff_fields.append("params")
            if base_c.severity != target_c.severity:
                diff_fields.append("severity")

            if diff_fields:
                modified_count += 1
                diff_items.append(
                    ClauseDiffItem(
                        change_type="modified",
                        clause_ref=ref,
                        previous_clause=ClauseResponse.model_validate(base_c),
                        current_clause=ClauseResponse.model_validate(target_c),
                        diff_fields=diff_fields,
                    )
                )
            else:
                diff_items.append(
                    ClauseDiffItem(
                        change_type="unchanged",
                        clause_ref=ref,
                        previous_clause=ClauseResponse.model_validate(base_c),
                        current_clause=ClauseResponse.model_validate(target_c),
                    )
                )

    summary_parts = []
    if added_count:
        summary_parts.append(f"{added_count} added")
    if removed_count:
        summary_parts.append(f"{removed_count} removed")
    if modified_count:
        summary_parts.append(f"{modified_count} changed")

    summary_text = ", ".join(summary_parts) if summary_parts else "No changes between versions."
    summary = f"{summary_text} Submissions already scored against v{base_version} keep their original verdicts."

    return ContractDiffResponse(
        base_contract_id=base_contract_id,
        base_version=base_version,
        target_contract_id=target_contract_id,
        target_version=target_version,
        summary=summary,
        diff_items=diff_items,
    )
