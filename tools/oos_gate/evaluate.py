"""Validate and evaluate non-canonical walk-forward/OOS gate artifacts.

The helpers in this module are read-only. They do not write candidate lifecycle
records, result populations, trial-log rows, or runtime artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


GATE_DECISIONS = {"pass", "fail", "blocked", "advisory_only"}
CANONICAL_STATUSES = {"non_canonical", "separately_crossed"}
NON_AUTHORITY_FLAGS = {
    "not_candidate_approval",
    "not_promotion_authority",
    "not_readiness_authority",
    "not_ranking_authority",
    "not_recommendation_authority",
    "not_runtime_authority",
    "not_paper_live_authority",
    "not_result_population_write_authority",
    "not_candidate_lifecycle_write_authority",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _require_object(payload: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _validate_period(period: Any, label: str, errors: list[str]) -> None:
    if not isinstance(period, dict):
        errors.append(f"{label} must be an object")
        return
    for key in ("start_utc", "end_utc"):
        if not isinstance(period.get(key), str) or not period[key]:
            errors.append(f"{label}.{key} must be a non-empty UTC timestamp string")


def _validate_purge_embargo(payload: dict[str, Any], label: str, errors: list[str]) -> None:
    value = payload.get(label)
    if not isinstance(value, dict):
        errors.append(f"split.{label} must be an object")
        return
    if value.get("mode") != "bars":
        errors.append(f"split.{label}.mode must be bars")
    bars = value.get("bars")
    if not isinstance(bars, int) or isinstance(bars, bool) or bars < 0:
        errors.append(f"split.{label}.bars must be a non-negative integer")


def validate_oos_gate_artifact(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for one OOS gate artifact."""
    errors: list[str] = []
    if payload.get("schema_version") != "oos_gate_contract.v1":
        errors.append("schema_version must be oos_gate_contract.v1")
    if not isinstance(payload.get("gate_id"), str) or not payload["gate_id"]:
        errors.append("gate_id must be a non-empty string")
    decision = payload.get("gate_decision")
    if decision not in GATE_DECISIONS:
        errors.append(f"gate_decision must be one of {sorted(GATE_DECISIONS)}")
    if payload.get("canonical_status") not in CANONICAL_STATUSES:
        errors.append(f"canonical_status must be one of {sorted(CANONICAL_STATUSES)}")
    if payload.get("canonical_status") == "separately_crossed":
        errors.append("separately_crossed is not allowed for this package artifact")

    source_rp = _require_object(payload, "source_result_population", errors)
    if source_rp:
        if not isinstance(source_rp.get("result_population_id"), str) or not source_rp["result_population_id"]:
            errors.append("source_result_population.result_population_id must be non-empty")
        if not isinstance(source_rp.get("result_population_ref"), str) or not source_rp["result_population_ref"]:
            errors.append("source_result_population.result_population_ref must be non-empty")

    source_wf = _require_object(payload, "source_walkforward_run", errors)
    if source_wf:
        if not isinstance(source_wf.get("run_id"), str) or not source_wf["run_id"]:
            errors.append("source_walkforward_run.run_id must be non-empty")
        if not isinstance(source_wf.get("report_ref"), str) or not source_wf["report_ref"]:
            errors.append("source_walkforward_run.report_ref must be non-empty")

    split = _require_object(payload, "split", errors)
    if split:
        if not isinstance(split.get("method"), str) or not split["method"]:
            errors.append("split.method must be non-empty")
        _validate_period(split.get("in_sample_period"), "split.in_sample_period", errors)
        _validate_period(split.get("out_of_sample_period"), "split.out_of_sample_period", errors)
        _validate_purge_embargo(split, "purge", errors)
        _validate_purge_embargo(split, "embargo", errors)
        for key in ("window_count", "minimum_required_windows"):
            value = split.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"split.{key} must be a positive integer")
        if (
            isinstance(split.get("window_count"), int)
            and isinstance(split.get("minimum_required_windows"), int)
            and split["window_count"] < split["minimum_required_windows"]
        ):
            errors.append("split.window_count must be >= split.minimum_required_windows")

    metrics = _require_object(payload, "oos_metrics", errors)
    if metrics:
        for key in ("mean_oos_sharpe", "minimum_oos_sharpe", "maximum_oos_drawdown"):
            if not _is_finite_number(metrics.get(key)):
                errors.append(f"oos_metrics.{key} must be finite numeric")

    mapping = _require_object(payload, "row_variant_mapping", errors)
    if mapping:
        if mapping.get("denominator_preserved") is not True:
            errors.append("row_variant_mapping.denominator_preserved must be true")
        for key in ("declared_variant_count", "per_window_variant_rows"):
            value = mapping.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"row_variant_mapping.{key} must be a positive integer")

    reason_codes = payload.get("reason_codes")
    if not isinstance(reason_codes, list) or not all(isinstance(item, str) and item for item in reason_codes):
        errors.append("reason_codes must be a non-empty string array")
    if decision in {"fail", "blocked", "advisory_only"} and not reason_codes:
        errors.append("non-pass gate decisions require reason_codes")

    flags = _require_object(payload, "non_authority_declaration", errors)
    if flags:
        for flag in sorted(NON_AUTHORITY_FLAGS):
            if flags.get(flag) is not True:
                errors.append(f"non_authority_declaration.{flag} must be true")
    return errors


def evaluate_candidate_review_gate(
    candidate_payload: dict[str, Any],
    gate_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate candidate-review readiness against a read-only OOS gate input."""
    gate_errors = validate_oos_gate_artifact(gate_artifact) if gate_artifact is not None else []
    candidate_results: list[dict[str, Any]] = []
    candidates = candidate_payload.get("candidates", [])
    if not isinstance(candidates, list):
        candidates = []

    for candidate in candidates:
        candidate_id = candidate.get("candidate_id") if isinstance(candidate, dict) else None
        evidence = candidate.get("evidence_refs", {}) if isinstance(candidate, dict) else {}
        if not isinstance(evidence, dict):
            evidence = {}
        blockers: list[str] = []
        if gate_artifact is None:
            blockers.append("missing_oos_gate_evidence")
        elif gate_errors:
            blockers.append("invalid_oos_gate_artifact")
        else:
            gate_ref = evidence.get("oos_gate_ref")
            if not gate_ref:
                blockers.append("missing_oos_gate_ref")
            result_population_ref = evidence.get("result_population_ref")
            expected_rp = gate_artifact["source_result_population"]["result_population_id"]
            if result_population_ref != expected_rp:
                blockers.append("oos_gate_result_population_mismatch")
            walkforward_ref = evidence.get("walkforward_run_ref")
            expected_wf = gate_artifact["source_walkforward_run"]["report_ref"]
            if walkforward_ref != expected_wf:
                blockers.append("oos_gate_walkforward_run_mismatch")
            gate_decision = gate_artifact["gate_decision"]
            if gate_decision in {"fail", "blocked", "advisory_only"}:
                blockers.append(f"oos_gate_decision_{gate_decision}")

        candidate_results.append(
            {
                "candidate_id": candidate_id,
                "candidate_review_gate_status": "blocked" if blockers else "pass",
                "blockers": blockers,
                "gate_decision": None if gate_artifact is None else gate_artifact.get("gate_decision"),
                "canonical_writes": 0,
                "candidate_lifecycle_writes": 0,
                "runtime_actions": 0,
            }
        )

    return {
        "schema_version": "oos_candidate_gate_evaluation.v1",
        "candidate_count": len(candidate_results),
        "gate_artifact_valid": gate_artifact is not None and not gate_errors,
        "gate_artifact_errors": gate_errors,
        "candidate_results": candidate_results,
        "aggregate": {
            "blocked_count": sum(1 for item in candidate_results if item["candidate_review_gate_status"] == "blocked"),
            "pass_count": sum(1 for item in candidate_results if item["candidate_review_gate_status"] == "pass"),
            "canonical_writes": 0,
            "candidate_lifecycle_writes": 0,
            "runtime_actions": 0,
        },
        "non_authority_flags": sorted(NON_AUTHORITY_FLAGS),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-artifact", type=Path, required=True)
    parser.add_argument("--candidate-input", type=Path)
    args = parser.parse_args(argv)

    gate_artifact = load_json(args.gate_artifact)
    errors = validate_oos_gate_artifact(gate_artifact)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.candidate_input:
        print(
            json.dumps(
                evaluate_candidate_review_gate(load_json(args.candidate_input), gate_artifact),
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print("OK: OOS gate artifact validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
