"""Pure denominator and result-comparison semantics for CPW research."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence

from .contracts import TRIAL_STATUSES

_RUNNER_OUTCOME_TO_TRIAL_STATUS = {
    "successful": "completed",
    "failed": "failed",
    "invalid": "invalid",
    "excluded": "pruned",
    "filtered": "pruned",
    "errored": "blocked",
    "aborted": "blocked",
    "data_unavailable": "blocked",
    "not_attempted": "blocked",
}

_BRIDGE_NON_AUTHORITY_FLAGS = (
    "not canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not paper/live readiness",
    "human review required",
)


def _sha256(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def validate_declared_trials(trials: Sequence[Mapping[str, Any]]) -> None:
    if not trials:
        raise ValueError("at least one trial is required")
    trial_ids: list[str] = []
    for trial in trials:
        for key in ("strategy_family", "variant_id", "trial_id", "params"):
            if key not in trial:
                raise ValueError(f"trial is missing {key}")
        if not isinstance(trial["params"], Mapping):
            raise ValueError("trial params must be an object")
        trial_ids.append(str(trial["trial_id"]))
    if len(trial_ids) != len(set(trial_ids)):
        raise ValueError("trial_id values must be unique")


def validate_trial_denominator(
    ledger: Sequence[Mapping[str, Any]], expected_trial_ids: Sequence[str] | set[str]
) -> None:
    expected = {str(item) for item in expected_trial_ids}
    actual = {str(row.get("trial_id")) for row in ledger}
    if actual != expected or len(ledger) != len(expected):
        raise ValueError("denominator ledger does not preserve every declared trial")
    invalid = [
        row.get("trial_status") for row in ledger if row.get("trial_status") not in TRIAL_STATUSES
    ]
    if invalid:
        raise ValueError(f"denominator ledger has unsupported statuses: {invalid}")


def build_bridge_ledger_rows(
    *,
    run_id: str,
    runner_invocation_id: str,
    formalizer_run_id: str,
    formalizer_path: str,
    approval_scope: str,
    input_paths: Mapping[str, str],
    manifest: Mapping[str, Any],
    runner_result: Mapping[str, Any] | None,
    runner_artifact_path: str | None,
    blockers: Sequence[str],
    funding_cost_mode: str,
    timestamp_utc: str,
    strategy_family: str = "sma_stddev_mean_reversion_v1",
) -> list[dict[str, Any]]:
    variants = {row["variant_id"]: row for row in manifest["variant_assignments"]}
    if runner_result is None:
        source_rows = [
            {
                "variant_id": variant_id,
                "outcome_category": "not_attempted",
                "non_success": {"reason": "; ".join(blockers)},
                "metrics": None,
                "row_identity_hash": None,
            }
            for variant_id in sorted(variants)
        ]
    else:
        source_rows = runner_result["result_population"]["variant_result_rows"]
    rows: list[dict[str, Any]] = []
    for index, runner_row in enumerate(source_rows, start=1):
        variant = variants[runner_row["variant_id"]]
        outcome = runner_row["outcome_category"]
        if outcome not in _RUNNER_OUTCOME_TO_TRIAL_STATUS:
            raise ValueError(f"unsupported runner outcome category: {outcome}")
        trial_status = _RUNNER_OUTCOME_TO_TRIAL_STATUS[outcome]
        metrics = runner_row.get("metrics") if trial_status == "completed" else None
        reason = runner_row.get("non_success", {}).get("reason") or f"runner {outcome}"
        rows.append(
            {
                "run_id": run_id,
                "source_formalizer_run_id": formalizer_run_id,
                "source_formalizer_artifact_path": formalizer_path,
                "approval_scope": approval_scope,
                "bridge_input_paths": dict(input_paths),
                "runner_invocation_id": runner_invocation_id,
                "strategy_family": strategy_family,
                "variant_id": runner_row["variant_id"],
                "trial_id": f"{run_id}-TRIAL-{index:03d}",
                "trial_status": trial_status,
                "status_reason": reason,
                "runner_outcome_category": outcome,
                "params": copy.deepcopy(variant["parameter_values"]),
                "funding_cost_mode": funding_cost_mode,
                "input_hash": _sha256(variant),
                "output_hash": runner_row.get("row_identity_hash"),
                "metrics_summary": metrics,
                "runner_artifact_path": runner_artifact_path,
                "started_at_utc": timestamp_utc,
                "finished_at_utc": timestamp_utc,
                "non_authority_flags": list(_BRIDGE_NON_AUTHORITY_FLAGS),
            }
        )
    return rows


def validate_variant_denominator(
    rows: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]
) -> None:
    expected = {row["variant_id"] for row in manifest["variant_assignments"]}
    actual = {row.get("variant_id") for row in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError("denominator ledger does not preserve every declared variant")
    if any(row.get("trial_status") not in TRIAL_STATUSES for row in rows):
        raise ValueError("denominator ledger contains an unsupported status")


def compare_result_populations(
    bridged: Mapping[str, Any], direct: Mapping[str, Any]
) -> dict[str, Any]:
    bridged_rows = bridged["result_population"]["variant_result_rows"]
    direct_rows = direct["result_population"]["variant_result_rows"]
    comparisons = {
        "trial_count": len(bridged_rows) == len(direct_rows),
        "variant_ids": [row["variant_id"] for row in bridged_rows]
        == [row["variant_id"] for row in direct_rows],
        "outcomes": [row["outcome_category"] for row in bridged_rows]
        == [row["outcome_category"] for row in direct_rows],
        "core_metrics": [row["metrics"] for row in bridged_rows]
        == [row["metrics"] for row in direct_rows],
        "status_counts": bridged["outcome_category_counts"] == direct["outcome_category_counts"],
        "committed_denominator": bridged["committed_denominator"]
        == direct["committed_denominator"],
        "result_identity": bridged["result_population"]["result_population_identity_hash"]
        == direct["result_population"]["result_population_identity_hash"],
    }
    return {"passed": all(comparisons.values()), "comparisons": comparisons}
