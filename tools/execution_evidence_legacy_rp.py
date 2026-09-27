"""Read-only Result Population v1 projection into CANON-01 contracts."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

from tools.execution_evidence_contract import build_result_envelope, build_run_request
from tools.research_replay.normalization import (
    CONTRACT_VERSION as REPLAY_NORMALIZATION_CONTRACT_VERSION,
    REPO_ROOT,
    build_contract_summary,
    load_result_population,
)


LEGACY_ADAPTER_VERSION = "cpw_result_population_v1_to_execution_evidence_v1"


def _load_source(
    payload_or_path: Mapping[str, Any] | Path | str,
) -> tuple[dict[str, Any], Path | None]:
    if isinstance(payload_or_path, (str, Path)):
        path = Path(payload_or_path)
        return load_result_population(path), path
    if not isinstance(payload_or_path, Mapping):
        raise ValueError("Result Population source must be an object or path")
    return copy.deepcopy(dict(payload_or_path)), None


def project_result_population_v1(
    payload_or_path: Mapping[str, Any] | Path | str,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Project RP v1 content without mutation, execution, or persistence."""

    payload, path = _load_source(payload_or_path)
    summary = build_contract_summary(path or payload, repo_root=repo_root)
    normalized = summary["normalized_payload"]
    parents = normalized["parent_identities"]
    data = normalized["data_identity"]

    request = build_run_request(
        parent_identities={
            "strategy_spec": {
                "id": parents["strategy_spec_id"],
                "content_sha256": parents["strategy_spec_hash"],
            },
            "variant_manifest": {
                "id": parents["variant_manifest_id"],
                "content_sha256": parents["variant_manifest_hash"],
            },
            "sweep_plan": {
                "id": parents["sweep_plan_id"],
                "content_sha256": parents["sweep_plan_identity_hash"],
            },
        },
        declared_variant_ids=copy.deepcopy(normalized["variant_ids"]),
        committed_denominator=normalized["denominator_counts"]["committed_denominator"],
        data_identity={
            "catalog_ref": data["data_catalog_ref"],
            "slice_identity": data["data_slice_identity"],
            "timeframe": data["timeframe"],
            "stream": data["data_stream"],
        },
        determinism={"seed": normalized["runner_identity"]["determinism_seed"]},
        scientific_assumptions={
            "backtest_assumption_summary": copy.deepcopy(
                normalized["backtest_assumption_summary"]
            ),
            "sizing_metadata": copy.deepcopy(normalized["sizing_metadata"]),
            "data_availability_claim": copy.deepcopy(data["data_availability_claim"]),
        },
    )

    rows = [
        {
            "variant_id": row["variant_id"],
            "assignment_hash": row["assignment_hash"],
            "outcome_category": row["outcome_category"],
            "attempted": row["attempted"],
            "metrics": copy.deepcopy(row["metrics"]),
            "non_success": copy.deepcopy(row["non_success"]),
            "error": copy.deepcopy(row["error"]),
            "data_coverage": copy.deepcopy(row["data_coverage"]),
            "lineage": copy.deepcopy(row["lineage"]),
        }
        for row in normalized["variant_result_rows"]
    ]
    outcome_counts = {
        category: normalized["status_counts"][category]
        for category in (
            "successful",
            "failed",
            "invalid",
            "excluded",
            "errored",
            "aborted",
            "filtered",
            "data_unavailable",
            "not_attempted",
        )
    }

    runner = normalized["runner_identity"]
    envelope = build_result_envelope(
        request_content_sha256=request["request_content_sha256"],
        committed_denominator=normalized["denominator_counts"]["committed_denominator"],
        outcome_category_counts=outcome_counts,
        variant_result_rows=rows,
        execution_provenance={
            "engine_id": payload["execution_context"].get("runner_id")
            or "legacy_rp_v1_engine",
            "engine_version": runner["runner_version"],
            "adapter_id": LEGACY_ADAPTER_VERSION,
            "repo_commit": runner["repo_commit"],
            "environment_summary": copy.deepcopy(runner["environment_summary"]),
            "dependency_summary": copy.deepcopy(runner["dependency_summary"]),
            "source_ref": summary["source"]["path"],
            "source_raw_sha256": summary["source"]["raw_sha256"],
        },
        compatibility_evidence={
            "result_population_id": payload["result_population_id"],
            "input_identity_hash": copy.deepcopy(payload["input_identity_hash"]),
            "result_population_identity_hash": copy.deepcopy(
                payload["result_population_identity_hash"]
            ),
            "replay_normalization_contract_version": REPLAY_NORMALIZATION_CONTRACT_VERSION,
            "replay_normalized_stable_hash": summary["normalized_stable_hash"],
        },
    )
    return request, envelope
