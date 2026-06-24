"""Normalize Result Population artifacts for deterministic replay comparison.

This module is intentionally read-only. It does not run strategies, write
canonical evidence, or call runtime/paper/live paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_VERSION = "result_population_replay_normalization_contract_v1"
HASH_ALGORITHM = "sha256"
METRIC_KEYS = (
    "pnl",
    "return_pct",
    "drawdown",
    "trade_count",
    "win_rate",
    "sharpe",
    "fees",
    "funding",
    "slippage",
    "exposure",
)


class ReplayNormalizationError(ValueError):
    """Raised when a Result Population cannot be normalized safely."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_prefixed_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def sha256_prefixed_json(value: Any) -> str:
    return sha256_prefixed_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    return sha256_prefixed_bytes(path.read_bytes())


def load_result_population(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReplayNormalizationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReplayNormalizationError(f"{path}: Result Population must be a JSON object")
    return payload


def _repo_relative_path(path: Path, repo_root: Path) -> str | None:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None


def _normalize_portable_path(value: Any, repo_root: Path) -> Any:
    if not isinstance(value, str) or not value:
        return value

    normalized = value.replace("\\", "/")
    candidate = Path(value)
    if candidate.is_absolute():
        relative = _repo_relative_path(candidate, repo_root)
        if relative is None:
            raise ReplayNormalizationError(
                "absolute path is outside repo root and cannot be normalized safely: "
                f"{value}"
            )
        return relative

    repo_prefix = repo_root.as_posix().rstrip("/") + "/"
    if normalized.startswith(repo_prefix):
        return normalized[len(repo_prefix) :]
    return normalized


def _artifact_ref(parent: Mapping[str, Any], ref_key: str, repo_root: Path) -> Any:
    return _normalize_portable_path(parent.get(ref_key), repo_root)


def _required_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ReplayNormalizationError(f"missing object: {key}")
    return value


def _required_list(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ReplayNormalizationError(f"missing array: {key}")
    return value


def _row_projection(row: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    lineage = row.get("lineage")
    if not isinstance(lineage, Mapping):
        lineage = {}
    metrics = row.get("metrics")
    if not isinstance(metrics, Mapping):
        metrics = {}
    return {
        "row_id": row.get("row_id"),
        "variant_id": row.get("variant_id"),
        "row_identity_hash": row.get("row_identity_hash"),
        "assignment_hash": row.get("assignment_hash"),
        "assignment_ref": _normalize_portable_path(row.get("assignment_ref"), repo_root),
        "outcome_category": row.get("outcome_category"),
        "attempted": row.get("attempted"),
        "metrics": {key: metrics.get(key) for key in METRIC_KEYS},
        "non_success": row.get("non_success"),
        "error": row.get("error"),
        "data_coverage": row.get("data_coverage"),
        "backtest_assumption_ref": _normalize_portable_path(
            row.get("backtest_assumption_ref"),
            repo_root,
        ),
        "lineage": {
            "parent_variant_id": lineage.get("parent_variant_id"),
            "parent_variant_assignment_hash": lineage.get("parent_variant_assignment_hash"),
            "parent_variant_assignment_ref": _normalize_portable_path(
                lineage.get("parent_variant_assignment_ref"),
                repo_root,
            ),
            "parent_sweep_plan_id": lineage.get("parent_sweep_plan_id"),
            "parent_manifest_id": lineage.get("parent_manifest_id"),
        },
    }


def normalized_payload(
    payload: Mapping[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    runner_command: str | None = None,
) -> dict[str, Any]:
    """Return the stable semantic replay payload.

    Excluded by design: raw file hash, audit envelope timestamps, validation
    timestamps, append-only event timestamps, local absolute path spellings, and
    operator notes. Included by design: metrics, rows, variant IDs, outcome
    counts, denominator counts, parent hashes, data identity, and runner identity.
    """

    parent_strategy_spec = _required_mapping(payload, "parent_strategy_spec")
    parent_variant_manifest = _required_mapping(payload, "parent_variant_manifest")
    parent_sweep_plan = _required_mapping(payload, "parent_sweep_plan")
    execution_context = _required_mapping(payload, "execution_context")
    data_coverage_summary = _required_mapping(payload, "data_coverage_summary")
    committed_denominator_snapshot = _required_mapping(payload, "committed_denominator_snapshot")
    outcome_category_counts = _required_mapping(payload, "outcome_category_counts")
    input_identity_hash = _required_mapping(payload, "input_identity_hash")
    result_population_identity_hash = _required_mapping(payload, "result_population_identity_hash")
    validation_summary = _required_mapping(payload, "validation_summary")
    rows = _required_list(payload, "variant_result_rows")

    row_projections = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ReplayNormalizationError(
                f"variant_result_rows[{index}] must be an object"
            )
        row_projections.append(_row_projection(row, repo_root))
    variant_ids = [row.get("variant_id") for row in row_projections]
    metric_set = sorted(
        key
        for key in METRIC_KEYS
        if any(row.get("metrics", {}).get(key) is not None for row in row_projections)
    )

    artifact_refs = {
        "strategy_spec_ref": _artifact_ref(parent_strategy_spec, "strategy_spec_ref", repo_root),
        "variant_manifest_ref": _artifact_ref(parent_variant_manifest, "manifest_ref", repo_root),
        "sweep_plan_ref": _artifact_ref(parent_sweep_plan, "sweep_plan_ref", repo_root),
    }

    return {
        "contract_version": CONTRACT_VERSION,
        "artifact_type": "result_population_replay_normalization",
        "result_population_id": payload.get("result_population_id"),
        "status": payload.get("status"),
        "parent_identities": {
            "strategy_spec_id": parent_strategy_spec.get("strategy_spec_id"),
            "strategy_spec_hash": parent_strategy_spec.get("strategy_spec_hash"),
            "variant_manifest_id": parent_variant_manifest.get("variant_manifest_id"),
            "variant_manifest_hash": parent_variant_manifest.get("manifest_hash"),
            "sweep_plan_id": parent_sweep_plan.get("sweep_plan_id"),
            "sweep_plan_identity_hash": parent_sweep_plan.get("sweep_plan_identity_hash"),
            "artifact_refs": artifact_refs,
        },
        "runner_identity": {
            "repo_commit": execution_context.get("repo_commit"),
            "runner_code_ref": execution_context.get("runner_code_ref"),
            "runner_version": execution_context.get("runner_version"),
            "runner_command": runner_command,
            "determinism_seed": execution_context.get("determinism_seed"),
            "execution_mode": execution_context.get("execution_mode"),
            "offline_only": execution_context.get("offline_only"),
            "no_runtime_contact": execution_context.get("no_runtime_contact"),
            "no_paper_live_contact": execution_context.get("no_paper_live_contact"),
            "no_broker_exchange_order_contact": execution_context.get(
                "no_broker_exchange_order_contact"
            ),
            "no_protected_path_contact": execution_context.get("no_protected_path_contact"),
            "environment_summary": execution_context.get("environment_summary"),
            "dependency_summary": execution_context.get("dependency_summary"),
        },
        "data_identity": {
            "data_catalog_ref": _normalize_portable_path(
                data_coverage_summary.get("data_catalog_ref"),
                repo_root,
            ),
            "data_slice_identity": data_coverage_summary.get("data_slice_identity"),
            "timeframe": data_coverage_summary.get("timeframe"),
            "data_stream": data_coverage_summary.get("data_stream"),
            "data_availability_claim": payload.get("data_availability_claim"),
        },
        "declared_identity_hashes": {
            "input_identity_hash": input_identity_hash.get("hash"),
            "input_identity_hash_scope": input_identity_hash.get("hash_scope"),
            "result_population_identity_hash": result_population_identity_hash.get("hash"),
            "result_population_identity_hash_scope": result_population_identity_hash.get(
                "hash_scope"
            ),
        },
        "trial_count": len(row_projections),
        "variant_ids": variant_ids,
        "metric_set": metric_set,
        "status_counts": outcome_category_counts,
        "denominator_counts": committed_denominator_snapshot,
        "sizing_metadata": payload.get("sizing_metadata"),
        "backtest_assumption_summary": payload.get("backtest_assumption_summary"),
        "validation_identity": {
            "validator_identity": validation_summary.get("validator_identity"),
            "validator_version": validation_summary.get("validator_version"),
            "schema_validation_status": validation_summary.get("schema_validation_status"),
            "validator_status": validation_summary.get("validator_status"),
        },
        "variant_result_rows": row_projections,
    }


def normalized_stable_hash(
    payload: Mapping[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    runner_command: str | None = None,
) -> str:
    return sha256_prefixed_json(
        normalized_payload(payload, repo_root=repo_root, runner_command=runner_command)
    )


def build_contract_summary(
    payload_or_path: Mapping[str, Any] | Path | str,
    *,
    repo_root: Path = REPO_ROOT,
    runner_command: str | None = None,
) -> dict[str, Any]:
    path: Path | None = None
    if isinstance(payload_or_path, (str, Path)):
        path = Path(payload_or_path)
        payload = load_result_population(path)
    else:
        payload = dict(payload_or_path)

    normalized = normalized_payload(payload, repo_root=repo_root, runner_command=runner_command)
    source = {
        "path": _repo_relative_path(path, repo_root) if path is not None else None,
        "raw_sha256": sha256_file(path) if path is not None else None,
        "result_population_id": payload.get("result_population_id"),
    }
    return {
        "contract_version": CONTRACT_VERSION,
        "hash_algorithm": HASH_ALGORITHM,
        "source": source,
        "normalized_stable_hash": sha256_prefixed_json(normalized),
        "normalized_payload": normalized,
    }


def compare_result_populations(
    left: Mapping[str, Any] | Path | str,
    right: Mapping[str, Any] | Path | str,
    *,
    repo_root: Path = REPO_ROOT,
    runner_command: str | None = None,
) -> dict[str, Any]:
    left_summary = build_contract_summary(
        left,
        repo_root=repo_root,
        runner_command=runner_command,
    )
    right_summary = build_contract_summary(
        right,
        repo_root=repo_root,
        runner_command=runner_command,
    )
    left_payload = left_summary["normalized_payload"]
    right_payload = right_summary["normalized_payload"]
    return {
        "contract_version": CONTRACT_VERSION,
        "normalized_stable_hash_match": (
            left_summary["normalized_stable_hash"]
            == right_summary["normalized_stable_hash"]
        ),
        "left": {
            "source": left_summary["source"],
            "normalized_stable_hash": left_summary["normalized_stable_hash"],
        },
        "right": {
            "source": right_summary["source"],
            "normalized_stable_hash": right_summary["normalized_stable_hash"],
        },
        "matched_fields": {
            "trial_count": left_payload["trial_count"] == right_payload["trial_count"],
            "variant_ids": left_payload["variant_ids"] == right_payload["variant_ids"],
            "status_counts": left_payload["status_counts"] == right_payload["status_counts"],
            "denominator_counts": (
                left_payload["denominator_counts"] == right_payload["denominator_counts"]
            ),
            "metric_set": left_payload["metric_set"] == right_payload["metric_set"],
            "parent_identities": (
                left_payload["parent_identities"] == right_payload["parent_identities"]
            ),
            "runner_identity": (
                left_payload["runner_identity"] == right_payload["runner_identity"]
            ),
            "data_identity": left_payload["data_identity"] == right_payload["data_identity"],
            "variant_result_rows": (
                left_payload["variant_result_rows"] == right_payload["variant_result_rows"]
            ),
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_population", type=Path)
    parser.add_argument("--compare-to", type=Path)
    parser.add_argument("--runner-command")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.compare_to is not None:
            result = compare_result_populations(
                args.result_population,
                args.compare_to,
                repo_root=args.repo_root,
                runner_command=args.runner_command,
            )
        else:
            result = build_contract_summary(
                args.result_population,
                repo_root=args.repo_root,
                runner_command=args.runner_command,
            )
    except ReplayNormalizationError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
