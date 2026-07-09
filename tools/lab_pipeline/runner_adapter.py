"""Product runner adapter over bridge prepare-only artifacts.

This module is package-local productization glue. It validates a separate
execute approval, invokes the existing offline runner, writes only product
scratch Result Population artifacts, and reconciles adapter-vs-direct runner
output without changing runner semantics.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from tools.agent_sandbox import MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import RUN_NONCANONICAL_OFFLINE_SWEEP
from tools.lab_pipeline.state import file_sha256, read_json, sha256_payload, write_json
from tools.research_replay.normalization import compare_result_populations
from tools.research_runner.run_offline_sweep import run_offline_sweep


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "scratch" / WP_ID / "outputs"
RUNNER_ADAPTER_STAGE_IDENTITY = "noncanonical_offline_runner_execution"
EXECUTE_APPROVAL_SCHEMA_VERSION = "product_runner_execute_approval_v1"
EXECUTE_APPROVAL_SCOPE = "noncanonical_product_runner_execution_only"
EXECUTE_APPROVAL_STATEMENT = (
    "Authorizes only non-canonical product runner execution for the exact "
    "bridge-prepared Strategy Spec, Variant Manifest, and Sweep Plan artifacts."
)
RUNNER_CODE_REF = "tools.research_runner.run_offline_sweep.run_offline_sweep"

FALSE_AUTHORITY_FLAGS = (
    "authorizes_canonical_write",
    "authorizes_candidate_lifecycle",
    "authorizes_wfo_oos_execution",
    "authorizes_robustness_execution",
    "authorizes_candidate_review_execution",
    "authorizes_paper_live_runtime",
    "authorizes_scheduler_autonomy",
    "authorizes_notification",
    "authorizes_provider_api_credential",
    "authorizes_dependency_config_data_acquisition",
    "authorizes_protected_path_touch",
)

RUNNER_OUTCOME_TO_STATUS = {
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
ALLOWED_DENOMINATOR_STATUSES = ("completed", "failed", "invalid", "blocked", "pruned")


class RunnerAdapterError(ValueError):
    """Raised when the product runner adapter must fail closed."""


@dataclass(frozen=True)
class RunnerAdapterResult:
    runner_adapter_run_id: str
    adapter_status: str
    output_dir: Path
    artifact_paths: dict[str, str]
    denominator_counts: dict[str, int]
    reconciliation: dict[str, Any]
    audit_records: tuple[dict[str, Any], ...]


def _fixed_clock() -> datetime:
    return datetime(2026, 7, 8, 0, 0, 0, tzinfo=timezone.utc)


def _safe_repo_relative(path: Path | str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(REPO_ROOT.resolve())
        except ValueError as exc:
            raise RunnerAdapterError(f"path is outside repo root: {path}") from exc
    normalized = candidate.as_posix()
    pure = PurePosixPath(normalized.replace("\\", "/"))
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise RunnerAdapterError(f"path must be safe repo-relative: {path}")
    if pure.parts and pure.parts[0].endswith(":"):
        raise RunnerAdapterError(f"path must be safe repo-relative: {path}")
    return pure.as_posix()


def _repo_path(path: Path | str) -> Path:
    return REPO_ROOT / _safe_repo_relative(path)


def _validate_product_output_root(output_root: Path) -> str:
    resolved = output_root.resolve()
    allowed = DEFAULT_OUTPUT_ROOT.resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise RunnerAdapterError(
            "product runner output_root must be under "
            f"{allowed.as_posix()}; got {resolved.as_posix()}"
        ) from exc
    return _safe_repo_relative(resolved)


def _parse_utc_like_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RunnerAdapterError("execute approval timestamp is required")
    timestamp = value.strip()
    if not timestamp.endswith("Z"):
        raise RunnerAdapterError("execute approval timestamp must be UTC-like ISO-8601 with Z")
    try:
        datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as exc:
        raise RunnerAdapterError("execute approval timestamp is malformed") from exc


def _file_hash(path: Path | str) -> str:
    target = _repo_path(path)
    if not target.is_file():
        raise RunnerAdapterError(f"prepared artifact does not exist: {_safe_repo_relative(path)}")
    return file_sha256(target)


def approval_template(
    *,
    prepared_strategy_spec_path: Path | str,
    prepared_variant_manifest_path: Path | str,
    prepared_sweep_plan_path: Path | str,
    bridge_preparation_run_id: str,
    product_pipeline_run_id: str,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    approval_timestamp_utc: str = "2026-07-08T00:00:00Z",
) -> dict[str, Any]:
    """Return an exact-content execute approval marker template."""

    output_root_rel = _validate_product_output_root(Path(output_root))
    return {
        "schema_version": EXECUTE_APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": EXECUTE_APPROVAL_SCOPE,
        "approval_statement": EXECUTE_APPROVAL_STATEMENT,
        "approval_timestamp_utc": approval_timestamp_utc,
        "prepared_strategy_spec_path": _safe_repo_relative(prepared_strategy_spec_path),
        "prepared_strategy_spec_sha256": _file_hash(prepared_strategy_spec_path),
        "prepared_variant_manifest_path": _safe_repo_relative(prepared_variant_manifest_path),
        "prepared_variant_manifest_sha256": _file_hash(prepared_variant_manifest_path),
        "prepared_sweep_plan_path": _safe_repo_relative(prepared_sweep_plan_path),
        "prepared_sweep_plan_sha256": _file_hash(prepared_sweep_plan_path),
        "bridge_preparation_run_id": bridge_preparation_run_id,
        "product_pipeline_run_id": product_pipeline_run_id,
        "runner_adapter_stage_identity": RUNNER_ADAPTER_STAGE_IDENTITY,
        "product_output_root": output_root_rel,
        "authorizes_runner_execution": True,
        **{field: False for field in FALSE_AUTHORITY_FLAGS},
    }


def _require_execute_approval(
    *,
    approval_path: Path,
    prepared_strategy_spec_path: str,
    prepared_variant_manifest_path: str,
    prepared_sweep_plan_path: str,
    bridge_preparation_run_id: str,
    product_pipeline_run_id: str,
    output_root: str,
) -> tuple[dict[str, Any], str]:
    approval = read_json(approval_path)
    approval_hash = file_sha256(approval_path)
    errors: list[str] = []

    expected = {
        "schema_version": EXECUTE_APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": EXECUTE_APPROVAL_SCOPE,
        "approval_statement": EXECUTE_APPROVAL_STATEMENT,
        "prepared_strategy_spec_path": prepared_strategy_spec_path,
        "prepared_strategy_spec_sha256": _file_hash(prepared_strategy_spec_path),
        "prepared_variant_manifest_path": prepared_variant_manifest_path,
        "prepared_variant_manifest_sha256": _file_hash(prepared_variant_manifest_path),
        "prepared_sweep_plan_path": prepared_sweep_plan_path,
        "prepared_sweep_plan_sha256": _file_hash(prepared_sweep_plan_path),
        "bridge_preparation_run_id": bridge_preparation_run_id,
        "product_pipeline_run_id": product_pipeline_run_id,
        "runner_adapter_stage_identity": RUNNER_ADAPTER_STAGE_IDENTITY,
        "product_output_root": output_root,
        "authorizes_runner_execution": True,
    }
    for field, expected_value in expected.items():
        if approval.get(field) != expected_value:
            errors.append(f"execute_approval_mismatch:{field}")
    try:
        _parse_utc_like_timestamp(approval.get("approval_timestamp_utc"))
    except RunnerAdapterError as exc:
        errors.append(str(exc))
    for field in FALSE_AUTHORITY_FLAGS:
        if approval.get(field) is not False:
            errors.append(f"execute_approval_unauthorized_authority:{field}")
    if errors:
        raise RunnerAdapterError("; ".join(errors))
    return approval, approval_hash


def _runner_adapter_run_id(bindings: Mapping[str, Any]) -> str:
    return "LRUN-" + sha256_payload(
        {"runner_adapter": "product_runner_adapter_v1", "bindings": dict(bindings)}
    ).split(":", 1)[1][:16]


def _status_counts(result_population: Mapping[str, Any]) -> dict[str, int]:
    counts = Counter()
    rows = result_population.get("variant_result_rows")
    if not isinstance(rows, list):
        raise RunnerAdapterError("runner result population has no variant_result_rows")
    for row in rows:
        if not isinstance(row, Mapping):
            raise RunnerAdapterError("runner result row must be an object")
        outcome = row.get("outcome_category")
        if outcome not in RUNNER_OUTCOME_TO_STATUS:
            raise RunnerAdapterError(f"unsupported runner outcome category: {outcome}")
        counts[RUNNER_OUTCOME_TO_STATUS[outcome]] += 1
    return {status: counts.get(status, 0) for status in ALLOWED_DENOMINATOR_STATUSES}


def _invoke_existing_runner(
    *,
    output_dir: Path,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    deterministic_seed: int,
) -> dict[str, Any]:
    return run_offline_sweep(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
        output_dir=output_dir,
        write_result_population=True,
        deterministic_seed=deterministic_seed,
    )


def _reconcile_outputs(adapter_path: Path, direct_path: Path) -> dict[str, Any]:
    adapter_hash = file_sha256(adapter_path)
    direct_hash = file_sha256(direct_path)
    raw_match = adapter_hash == direct_hash
    normalized = None
    normalized_match = raw_match
    if not raw_match:
        normalized = compare_result_populations(adapter_path, direct_path)
        normalized_match = bool(normalized["normalized_stable_hash_match"])
    if not normalized_match:
        raise RunnerAdapterError("adapter-vs-direct runner reconciliation failed")
    return {
        "schema_version": "product_runner_adapter_reconciliation_v1",
        "adapter_result_population_path": _safe_repo_relative(adapter_path),
        "adapter_result_population_sha256": adapter_hash,
        "direct_result_population_path": _safe_repo_relative(direct_path),
        "direct_result_population_sha256": direct_hash,
        "raw_byte_hash_match": raw_match,
        "normalized_comparison_used": normalized is not None,
        "normalized_stable_hash_match": normalized_match,
        "normalized_comparison": normalized,
        "verdict": "passed",
    }


def run_product_runner_adapter(
    *,
    prepared_strategy_spec_path: Path | str,
    prepared_variant_manifest_path: Path | str,
    prepared_sweep_plan_path: Path | str,
    bridge_preparation_run_id: str,
    product_pipeline_run_id: str,
    execute_approval_path: Path | str,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    deterministic_seed: int = 0,
    tool_context: ToolContext | None = None,
) -> RunnerAdapterResult:
    """Execute the product runner adapter over bridge prepare-only outputs."""

    output_root_path = Path(output_root)
    output_root_rel = _validate_product_output_root(output_root_path)
    strategy_rel = _safe_repo_relative(prepared_strategy_spec_path)
    manifest_rel = _safe_repo_relative(prepared_variant_manifest_path)
    sweep_rel = _safe_repo_relative(prepared_sweep_plan_path)
    approval_rel = _safe_repo_relative(execute_approval_path)
    approval, approval_hash = _require_execute_approval(
        approval_path=_repo_path(approval_rel),
        prepared_strategy_spec_path=strategy_rel,
        prepared_variant_manifest_path=manifest_rel,
        prepared_sweep_plan_path=sweep_rel,
        bridge_preparation_run_id=bridge_preparation_run_id,
        product_pipeline_run_id=product_pipeline_run_id,
        output_root=output_root_rel,
    )
    bindings = {
        "prepared_strategy_spec_path": strategy_rel,
        "prepared_strategy_spec_sha256": approval["prepared_strategy_spec_sha256"],
        "prepared_variant_manifest_path": manifest_rel,
        "prepared_variant_manifest_sha256": approval["prepared_variant_manifest_sha256"],
        "prepared_sweep_plan_path": sweep_rel,
        "prepared_sweep_plan_sha256": approval["prepared_sweep_plan_sha256"],
        "execute_approval_path": approval_rel,
        "execute_approval_sha256": approval_hash,
        "bridge_preparation_run_id": bridge_preparation_run_id,
        "product_pipeline_run_id": product_pipeline_run_id,
        "runner_adapter_stage_identity": RUNNER_ADAPTER_STAGE_IDENTITY,
        "product_output_root": output_root_rel,
        "deterministic_seed": deterministic_seed,
    }
    run_id = _runner_adapter_run_id(bindings)
    run_dir = output_root_path / run_id

    sink = None
    if tool_context is None:
        sink = MemoryAuditSink()
        tool_context = ToolContext(
            wp_id=WP_ID,
            role="formalizer_runner_bridge",
            audit_sink=sink,
            clock=_fixed_clock,
        )
    adapter_target = _safe_repo_relative(run_dir / "runner_artifacts" / "adapter")
    tool_context.require_allowed(
        ToolAction(
            RUN_NONCANONICAL_OFFLINE_SWEEP,
            adapter_target,
            metadata={"runner_adapter_run_id": run_id},
        )
    )
    direct_target = _safe_repo_relative(run_dir / "runner_artifacts" / "direct")
    tool_context.require_allowed(
        ToolAction(
            RUN_NONCANONICAL_OFFLINE_SWEEP,
            direct_target,
            metadata={"runner_adapter_run_id": run_id, "reconciliation": "direct_runner"},
        )
    )

    adapter_result = _invoke_existing_runner(
        output_dir=run_dir / "runner_artifacts" / "adapter",
        strategy_spec_path=_repo_path(strategy_rel),
        variant_manifest_path=_repo_path(manifest_rel),
        sweep_plan_path=_repo_path(sweep_rel),
        deterministic_seed=deterministic_seed,
    )
    direct_result = _invoke_existing_runner(
        output_dir=run_dir / "runner_artifacts" / "direct",
        strategy_spec_path=_repo_path(strategy_rel),
        variant_manifest_path=_repo_path(manifest_rel),
        sweep_plan_path=_repo_path(sweep_rel),
        deterministic_seed=deterministic_seed,
    )
    adapter_output_path = Path(str(adapter_result["output_path"]))
    direct_output_path = Path(str(direct_result["output_path"]))
    reconciliation = _reconcile_outputs(adapter_output_path, direct_output_path)
    adapter_counts = _status_counts(adapter_result["result_population"])
    direct_counts = _status_counts(direct_result["result_population"])
    if adapter_counts != direct_counts:
        raise RunnerAdapterError("adapter-vs-direct denominator counts mismatch")

    metadata = {
        "schema_version": "product_runner_adapter_result_v1",
        "runner_adapter_run_id": run_id,
        "adapter_status": "completed",
        "noncanonical_status": "noncanonical_product_scratch_only",
        "runner_code_ref": RUNNER_CODE_REF,
        "runner_reimplemented": False,
        "source_bindings": bindings,
        "execute_approval": {
            "path": approval_rel,
            "sha256": approval_hash,
            "approved_by": approval["approved_by"],
            "approval_scope": approval["approval_scope"],
        },
        "runner_outputs": {
            "adapter_result_population_path": reconciliation["adapter_result_population_path"],
            "adapter_result_population_sha256": reconciliation["adapter_result_population_sha256"],
            "direct_result_population_path": reconciliation["direct_result_population_path"],
            "direct_result_population_sha256": reconciliation["direct_result_population_sha256"],
        },
        "denominator_counts": adapter_counts,
        "runner_outcome_category_counts": adapter_result["outcome_category_counts"],
        "full_denominator_preserved": True,
        "winner_narrowing": False,
        "direct_runner_reconciliation": reconciliation,
        "non_authority_assertions": {
            "canonical_evidence_written": False,
            "candidate_lifecycle_written": False,
            "wfo_oos_execution": False,
            "robustness_execution": False,
            "candidate_review_execution": False,
            "paper_live_runtime_contact": False,
            "scheduler_autonomous_dispatch": False,
            "notification_firing": False,
            "provider_api_credential_use": False,
            "dependency_config_data_acquisition": False,
            "protected_path_touch": False,
        },
    }
    artifact_paths = {
        "runner_adapter_result": write_json(run_dir / "runner_adapter_result.json", metadata),
        "adapter_result_population": reconciliation["adapter_result_population_path"],
        "direct_result_population": reconciliation["direct_result_population_path"],
        "execute_approval": approval_rel,
    }
    audit_records = tuple(record.to_dict() for record in sink.records) if sink is not None else ()
    return RunnerAdapterResult(
        runner_adapter_run_id=run_id,
        adapter_status="completed",
        output_dir=run_dir,
        artifact_paths=artifact_paths,
        denominator_counts=adapter_counts,
        reconciliation=reconciliation,
        audit_records=audit_records,
    )
