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
import stat
from typing import Any, Mapping

from tools.agent_sandbox import MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import RUN_NONCANONICAL_OFFLINE_SWEEP
from tools.lab_pipeline.state import file_sha256, read_json, sha256_payload, write_json
from tools.research_replay.normalization import compare_result_populations
from tools.research_runner.run_offline_sweep import run_offline_sweep
from tools.research_runner import run_offline_sweep as offline_runner


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "scratch" / WP_ID / "outputs"
RUNNER_ADAPTER_STAGE_IDENTITY = "noncanonical_offline_runner_execution"
EXECUTE_APPROVAL_SCHEMA_VERSION = "product_runner_execute_approval_v1"
REAL_EXECUTE_APPROVAL_SCHEMA_VERSION = "product_runner_execute_approval_v2"
EXECUTE_APPROVAL_SCOPE = "noncanonical_product_runner_execution_only"
EXECUTE_APPROVAL_STATEMENT = (
    "Authorizes only non-canonical product runner execution for the exact "
    "bridge-prepared Strategy Spec, Variant Manifest, and Sweep Plan artifacts."
)
SWEEP_BUDGET_SCHEMA_VERSION = "product_runner_approved_sweep_budget_v1"
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


def _ordinary_input(path: Path | str) -> Path:
    """Reject indirection before resolving any real-data or approval input."""
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    try:
        parts = candidate.absolute().relative_to(REPO_ROOT.absolute()).parts
    except ValueError as exc:
        raise RunnerAdapterError("input outside repository") from exc
    if any(part in {".", ".."} for part in parts):
        raise RunnerAdapterError("unsafe input path")
    cursor = REPO_ROOT
    for part in parts:
        cursor /= part
        attrs = cursor.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
            raise RunnerAdapterError("input indirection denied")
    if not cursor.is_file():
        raise RunnerAdapterError("ordinary input file required")
    return cursor


def _execution_binding(
    *,
    canonical_15m=False,
    ohlcv_input_path=None,
    d4_catalog_slice_path=None,
    d2_import_report_path=None,
    deterministic_seed=0,
) -> dict[str, Any] | None:
    if type(canonical_15m) is not bool or type(deterministic_seed) is not int:
        raise RunnerAdapterError("explicit boolean mode and integer seed required")
    paths = (ohlcv_input_path, d4_catalog_slice_path, d2_import_report_path)
    if not canonical_15m:
        if any(path is not None for path in paths):
            raise RunnerAdapterError("real input requires explicit 15m D4 route")
        return None
    if any(path is None for path in paths):
        raise RunnerAdapterError("15m D4 route requires OHLCV, catalog and import report")
    files = [_ordinary_input(path) for path in paths]
    binding = {
        "mode": "canonical_15m_d4_provenance",
        "canonical_15m": True,
        "deterministic_seed": deterministic_seed,
        "funding_cost_mode": "off",
        "sizing_mode": offline_runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        "target_leverage": 1.0,
    }
    for name, path in zip(("ohlcv_input", "d4_catalog_slice", "d2_import_report"), files):
        binding[name + "_path"] = _safe_repo_relative(path)
        binding[name + "_sha256"] = file_sha256(path)
    catalog = read_json(files[1])
    binding.update(
        timeframe="15m",
        data_catalog_ref=catalog.get("catalog_ref"),
        data_slice_identity=catalog.get("slice_identity", {}).get("data_slice_identity"),
    )
    if not binding["data_catalog_ref"] or not binding["data_slice_identity"]:
        raise RunnerAdapterError("D4 catalog identities required")
    return binding


def _validate_real_execution(binding: Mapping[str, Any]) -> None:
    paths = [
        _ordinary_input(binding[name + "_path"])
        for name in ("ohlcv_input", "d4_catalog_slice", "d2_import_report")
    ]
    before = [file_sha256(path) for path in paths]
    for name, digest in zip(("ohlcv_input", "d4_catalog_slice", "d2_import_report"), before):
        if binding[name + "_sha256"] != digest:
            raise RunnerAdapterError("real execution bytes changed")
    catalog = read_json(paths[1])
    if catalog.get("normalized", {}).get("sha256") != before[0].removeprefix("sha256:"):
        raise RunnerAdapterError("D4 normalized bytes hash mismatch")
    try:
        execution = offline_runner._d4_catalog_execution_input(*paths)
    except (OSError, ValueError, RuntimeError) as exc:
        raise RunnerAdapterError(f"invalid real D4 execution input: {exc}") from exc
    if (
        execution.timeframe != "15m"
        or execution.execution_provenance_class != "canonical_real_data"
        or execution.data_catalog_ref != binding["data_catalog_ref"]
        or execution.data_slice_identity != binding["data_slice_identity"]
    ):
        raise RunnerAdapterError("real 15m provenance required")
    coverage = catalog["range"]
    import pandas as pd

    if (
        len(execution.ohlcv) != coverage["row_count"]
        or execution.ohlcv.index[0] != pd.Timestamp(coverage["start_utc"])
        or execution.ohlcv.index[-1] != pd.Timestamp(coverage["end_utc"])
    ):
        raise RunnerAdapterError("D4 physical coverage mismatch")
    if before != [file_sha256(path) for path in paths]:
        raise RunnerAdapterError("real input changed during validation")


@dataclass(frozen=True)
class RunnerAdapterResult:
    runner_adapter_run_id: str
    adapter_status: str
    output_dir: Path
    artifact_paths: dict[str, str]
    denominator_counts: dict[str, int]
    approved_sweep_budget: dict[str, Any]
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


def _require_int(payload: Mapping[str, Any], dotted_path: str) -> int:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise RunnerAdapterError(f"sweep budget missing {dotted_path}")
        current = current[part]
    if not isinstance(current, int) or isinstance(current, bool):
        raise RunnerAdapterError(f"sweep budget {dotted_path} must be an integer")
    return current


def _require_positive_budget(value: int | None) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RunnerAdapterError("approved max_variant_count must be a positive integer")
    return value


def _selected_variant_ids(sweep_plan: Mapping[str, Any]) -> list[str]:
    selected = sweep_plan.get("test_selection", {}).get("selected_variant_ids")
    if not isinstance(selected, list) or not all(isinstance(item, str) and item for item in selected):
        raise RunnerAdapterError("sweep budget selected_variant_ids must be non-empty strings")
    if len(selected) != len(set(selected)):
        raise RunnerAdapterError("sweep budget selected_variant_ids must be unique")
    return selected


def _manifest_variant_ids(manifest: Mapping[str, Any]) -> list[str]:
    assignments = manifest.get("variant_assignments")
    if not isinstance(assignments, list):
        raise RunnerAdapterError("sweep budget variant_assignments must be a list")
    ids: list[str] = []
    for row in assignments:
        if not isinstance(row, Mapping) or not isinstance(row.get("variant_id"), str):
            raise RunnerAdapterError("sweep budget variant_assignments require variant_id")
        ids.append(row["variant_id"])
    if len(ids) != len(set(ids)):
        raise RunnerAdapterError("sweep budget variant_assignments must have unique ids")
    return ids


def _sweep_budget_contract(
    *,
    prepared_strategy_spec_path: str,
    prepared_variant_manifest_path: str,
    prepared_sweep_plan_path: str,
    max_variant_count: int,
) -> dict[str, Any]:
    max_variant_count = _require_positive_budget(max_variant_count)
    manifest = read_json(_repo_path(prepared_variant_manifest_path))
    sweep_plan = read_json(_repo_path(prepared_sweep_plan_path))
    manifest_ids = _manifest_variant_ids(manifest)
    selected_ids = _selected_variant_ids(sweep_plan)
    committed = _require_int(
        manifest, "population_governance.declared_population.committed_population_count"
    )
    declared = _require_int(
        manifest, "population_governance.declared_population.declared_variant_count"
    )
    trial_denominator = _require_int(
        manifest, "population_governance.trial_budget.trial_budget_denominator"
    )
    denominator_count = _require_int(
        manifest, "population_governance.trial_budget.denominator_count"
    )
    manifest_cap = _require_int(manifest, "population_governance.population_cap.max_variants")
    sweep_committed = _require_int(sweep_plan, "trial_accounting.committed_population_count")
    sweep_selected = _require_int(sweep_plan, "trial_accounting.selected_variant_count")
    parent_committed = _require_int(
        sweep_plan, "parent_variant_manifest.manifest_committed_population_count"
    )
    selection_mode = sweep_plan.get("test_selection", {}).get("selection_mode")
    if selection_mode != "all_manifest_variants":
        raise RunnerAdapterError("approved bounded sweeps require all_manifest_variants selection")
    if set(selected_ids) != set(manifest_ids):
        raise RunnerAdapterError("approved bounded sweep must select every manifest variant")
    counts = {
        "committed_population_count": committed,
        "declared_variant_count": declared,
        "trial_budget_denominator": trial_denominator,
        "denominator_count": denominator_count,
        "sweep_committed_population_count": sweep_committed,
        "sweep_selected_variant_count": sweep_selected,
        "parent_manifest_committed_population_count": parent_committed,
        "variant_assignment_count": len(manifest_ids),
        "selected_variant_id_count": len(selected_ids),
    }
    if len(set(counts.values())) != 1:
        raise RunnerAdapterError(f"sweep budget count mismatch: {counts}")
    if committed > max_variant_count:
        raise RunnerAdapterError(
            "sweep budget exceeded: "
            f"committed_population_count {committed} > max_variant_count {max_variant_count}"
        )
    return {
        "schema_version": SWEEP_BUDGET_SCHEMA_VERSION,
        "approval_binding": "karl_exact_content_runner_execute_approval",
        "scope": "prepared_strategy_spec_variant_manifest_sweep_plan_only",
        "prepared_strategy_spec_path": prepared_strategy_spec_path,
        "prepared_variant_manifest_path": prepared_variant_manifest_path,
        "prepared_sweep_plan_path": prepared_sweep_plan_path,
        "variant_manifest_id": manifest.get("variant_manifest_id"),
        "sweep_plan_id": sweep_plan.get("sweep_plan_id"),
        "selection_mode": selection_mode,
        "max_variant_count": max_variant_count,
        "committed_population_count": committed,
        "declared_variant_count": declared,
        "selected_variant_count": sweep_selected,
        "variant_assignment_count": len(manifest_ids),
        "manifest_population_cap": manifest_cap,
        "selected_variant_ids_sha256": sha256_payload({"selected_variant_ids": selected_ids}),
        "within_approved_budget": True,
        "full_denominator_required": True,
        "winner_narrowing_forbidden": True,
        "canonical_writes_allowed": False,
        "candidate_lifecycle_allowed": False,
        "noncanonical_product_scratch_only": True,
        "allowed_denominator_statuses": list(ALLOWED_DENOMINATOR_STATUSES),
        "runner_outcome_categories_preserved": list(RUNNER_OUTCOME_TO_STATUS),
    }


def _expected_variant_ids_from_sweep(prepared_sweep_plan_path: str) -> set[str]:
    return set(_selected_variant_ids(read_json(_repo_path(prepared_sweep_plan_path))))


def approval_template(
    *,
    prepared_strategy_spec_path: Path | str,
    prepared_variant_manifest_path: Path | str,
    prepared_sweep_plan_path: Path | str,
    bridge_preparation_run_id: str,
    product_pipeline_run_id: str,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    approval_timestamp_utc: str = "2026-07-08T00:00:00Z",
    max_variant_count: int | None = None,
    canonical_15m: bool = False,
    ohlcv_input_path: Path | str | None = None,
    d4_catalog_slice_path: Path | str | None = None,
    d2_import_report_path: Path | str | None = None,
    deterministic_seed: int = 0,
) -> dict[str, Any]:
    """Return an exact-content execute approval marker template."""

    output_root_rel = _validate_product_output_root(Path(output_root))
    strategy_rel = _safe_repo_relative(prepared_strategy_spec_path)
    manifest_rel = _safe_repo_relative(prepared_variant_manifest_path)
    sweep_rel = _safe_repo_relative(prepared_sweep_plan_path)
    manifest = read_json(_repo_path(manifest_rel))
    committed = _require_int(
        manifest, "population_governance.declared_population.committed_population_count"
    )
    approved_budget = _sweep_budget_contract(
        prepared_strategy_spec_path=strategy_rel,
        prepared_variant_manifest_path=manifest_rel,
        prepared_sweep_plan_path=sweep_rel,
        max_variant_count=max_variant_count if max_variant_count is not None else committed,
    )
    execution = _execution_binding(
        canonical_15m=canonical_15m,
        ohlcv_input_path=ohlcv_input_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        deterministic_seed=deterministic_seed,
    )
    return {
        **({"execution": execution} if execution else {}),
        "schema_version": REAL_EXECUTE_APPROVAL_SCHEMA_VERSION
        if execution
        else EXECUTE_APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": EXECUTE_APPROVAL_SCOPE,
        "approval_statement": EXECUTE_APPROVAL_STATEMENT,
        "approval_timestamp_utc": approval_timestamp_utc,
        "prepared_strategy_spec_path": strategy_rel,
        "prepared_strategy_spec_sha256": _file_hash(prepared_strategy_spec_path),
        "prepared_variant_manifest_path": manifest_rel,
        "prepared_variant_manifest_sha256": _file_hash(prepared_variant_manifest_path),
        "prepared_sweep_plan_path": sweep_rel,
        "prepared_sweep_plan_sha256": _file_hash(prepared_sweep_plan_path),
        "bridge_preparation_run_id": bridge_preparation_run_id,
        "product_pipeline_run_id": product_pipeline_run_id,
        "runner_adapter_stage_identity": RUNNER_ADAPTER_STAGE_IDENTITY,
        "product_output_root": output_root_rel,
        "approved_sweep_budget": approved_budget,
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
    execution: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    if execution:
        _ordinary_input(approval_path)
        for path in (
            prepared_strategy_spec_path,
            prepared_variant_manifest_path,
            prepared_sweep_plan_path,
        ):
            _ordinary_input(path)
    approval = read_json(approval_path)
    approval_hash = file_sha256(approval_path)
    errors: list[str] = []

    expected = {
        "schema_version": REAL_EXECUTE_APPROVAL_SCHEMA_VERSION
        if execution
        else EXECUTE_APPROVAL_SCHEMA_VERSION,
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
    if execution:
        expected["execution"] = dict(execution)
    elif "execution" in approval:
        errors.append("v1 approval cannot contain real execution settings")
    for field, expected_value in expected.items():
        matches = (
            (sha256_payload(approval.get(field)) == sha256_payload(expected_value))
            if execution
            else (approval.get(field) == expected_value)
        )
        if not matches:
            errors.append(f"execute_approval_mismatch:{field}")
    approved_budget = approval.get("approved_sweep_budget")
    if not isinstance(approved_budget, Mapping):
        errors.append("execute_approval_missing:approved_sweep_budget")
    else:
        try:
            expected_budget = _sweep_budget_contract(
                prepared_strategy_spec_path=prepared_strategy_spec_path,
                prepared_variant_manifest_path=prepared_variant_manifest_path,
                prepared_sweep_plan_path=prepared_sweep_plan_path,
                max_variant_count=approved_budget.get("max_variant_count"),
            )
            budget_matches = (
                (sha256_payload(dict(approved_budget)) == sha256_payload(expected_budget))
                if execution
                else (dict(approved_budget) == expected_budget)
            )
            if not budget_matches:
                errors.append("execute_approval_mismatch:approved_sweep_budget")
        except RunnerAdapterError as exc:
            errors.append(f"approved_sweep_budget_invalid:{exc}")
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


def _assert_result_population_preserves_budget(
    *,
    result_population: Mapping[str, Any],
    approved_budget: Mapping[str, Any],
    expected_variant_ids: set[str],
) -> None:
    rows = result_population.get("variant_result_rows")
    if not isinstance(rows, list):
        raise RunnerAdapterError("runner result population has no variant_result_rows")
    row_ids = [
        row.get("variant_id")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("variant_id"), str)
    ]
    committed = approved_budget["committed_population_count"]
    if len(rows) != committed:
        raise RunnerAdapterError(
            f"runner result row count {len(rows)} does not equal approved denominator {committed}"
        )
    if len(row_ids) != len(rows) or set(row_ids) != expected_variant_ids:
        raise RunnerAdapterError("runner result rows do not match approved sweep variant ids")
    counts = _status_counts(result_population)
    if sum(counts.values()) != committed:
        raise RunnerAdapterError("runner denominator status counts do not sum to approved denominator")


def _invoke_existing_runner(
    *,
    output_dir: Path,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    deterministic_seed: int,
    execution: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = {}
    if execution:
        _validate_real_execution(execution)
        settings = {
            "canonical_15m": True,
            "ohlcv_input_path": _repo_path(execution["ohlcv_input_path"]),
            "d4_catalog_slice_path": _repo_path(execution["d4_catalog_slice_path"]),
            "d2_import_report_path": _repo_path(execution["d2_import_report_path"]),
            "funding_cost_mode": execution["funding_cost_mode"],
            "sizing_mode": execution["sizing_mode"],
            "target_leverage": execution["target_leverage"],
        }
    return run_offline_sweep(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
        output_dir=output_dir,
        write_result_population=True,
        deterministic_seed=deterministic_seed,
        **settings,
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


def _assert_real_population_inputs(
    population: Mapping[str, Any], execution: Mapping[str, Any]
) -> None:
    """Reject synthetic fallback and substituted provenance on either invocation."""
    coverage = [population.get("data_coverage_summary", {})]
    coverage.extend(row.get("data_coverage", {}) for row in population["variant_result_rows"])
    for item in coverage:
        if any(
            item.get(key) != execution[key]
            for key in ("timeframe", "data_catalog_ref", "data_slice_identity")
        ):
            raise RunnerAdapterError("real D4 output provenance mismatch; investigate before rerun")
    notes = population["data_coverage_summary"].get("data_coverage_notes", [])
    if offline_runner.D4_PROVENANCE_MODE_NOTE not in notes:
        raise RunnerAdapterError("real D4 execution provenance missing")


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
    canonical_15m: bool = False,
    ohlcv_input_path: Path | str | None = None,
    d4_catalog_slice_path: Path | str | None = None,
    d2_import_report_path: Path | str | None = None,
) -> RunnerAdapterResult:
    """Execute the product runner adapter over bridge prepare-only outputs."""

    if canonical_15m:
        for source in (
            prepared_strategy_spec_path,
            prepared_variant_manifest_path,
            prepared_sweep_plan_path,
            execute_approval_path,
        ):
            _ordinary_input(source)
        destination = Path(output_root)
        if not destination.is_absolute():
            destination = REPO_ROOT / destination
        try:
            parts = destination.absolute().relative_to(REPO_ROOT.absolute()).parts
        except ValueError as exc:
            raise RunnerAdapterError("output outside repository") from exc
        cursor = REPO_ROOT
        for part in parts:
            if part in {".", ".."}:
                raise RunnerAdapterError("unsafe output path")
            cursor /= part
            if cursor.exists() or cursor.is_symlink():
                attrs = cursor.lstat()
                if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
                    raise RunnerAdapterError("output indirection denied")
    output_root_path = Path(output_root)
    output_root_rel = _validate_product_output_root(output_root_path)
    strategy_rel = _safe_repo_relative(prepared_strategy_spec_path)
    manifest_rel = _safe_repo_relative(prepared_variant_manifest_path)
    sweep_rel = _safe_repo_relative(prepared_sweep_plan_path)
    approval_rel = _safe_repo_relative(execute_approval_path)
    execution = _execution_binding(
        canonical_15m=canonical_15m,
        ohlcv_input_path=ohlcv_input_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        deterministic_seed=deterministic_seed,
    )
    approval, approval_hash = _require_execute_approval(
        approval_path=_repo_path(approval_rel),
        prepared_strategy_spec_path=strategy_rel,
        prepared_variant_manifest_path=manifest_rel,
        prepared_sweep_plan_path=sweep_rel,
        bridge_preparation_run_id=bridge_preparation_run_id,
        product_pipeline_run_id=product_pipeline_run_id,
        output_root=output_root_rel,
        execution=execution,
    )
    if execution:
        _validate_real_execution(execution)
    approved_budget = dict(approval["approved_sweep_budget"])
    expected_variant_ids = _expected_variant_ids_from_sweep(sweep_rel)
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
        "approved_sweep_budget": approved_budget,
    }
    if execution:
        bindings["execution"] = execution
    run_id = _runner_adapter_run_id(bindings)
    run_dir = output_root_path / run_id

    if execution and run_dir.exists():
        raise RunnerAdapterError("possible prior physical execution: reconcile before rerun")
    if execution:
        cursor = REPO_ROOT
        for part in Path(_safe_repo_relative(run_dir)).parts:
            cursor /= part
            if cursor.exists() or cursor.is_symlink():
                attrs = cursor.lstat()
                if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
                    raise RunnerAdapterError("output indirection denied")

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

    if execution:
        # Atomic reservation survives failure and prevents two callers from
        # starting the same approved physical run concurrently.
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise RunnerAdapterError(
                "possible prior physical execution: reconcile before rerun"
            ) from exc
    adapter_result = _invoke_existing_runner(
        output_dir=run_dir / "runner_artifacts" / "adapter",
        strategy_spec_path=_repo_path(strategy_rel),
        variant_manifest_path=_repo_path(manifest_rel),
        sweep_plan_path=_repo_path(sweep_rel),
        deterministic_seed=deterministic_seed,
        **({"execution": execution} if execution else {}),
    )
    if execution:
        _assert_real_population_inputs(adapter_result["result_population"], execution)
        adapter_approval, current_hash = _require_execute_approval(
            approval_path=_repo_path(approval_rel),
            prepared_strategy_spec_path=strategy_rel,
            prepared_variant_manifest_path=manifest_rel,
            prepared_sweep_plan_path=sweep_rel,
            bridge_preparation_run_id=bridge_preparation_run_id,
            product_pipeline_run_id=product_pipeline_run_id,
            output_root=output_root_rel,
            execution=execution,
        )
        if current_hash != approval_hash:
            raise RunnerAdapterError(
                "approval changed after possible physical execution; investigate"
            )
    direct_result = _invoke_existing_runner(
        output_dir=run_dir / "runner_artifacts" / "direct",
        strategy_spec_path=_repo_path(strategy_rel),
        variant_manifest_path=_repo_path(manifest_rel),
        sweep_plan_path=_repo_path(sweep_rel),
        deterministic_seed=deterministic_seed,
        **({"execution": execution} if execution else {}),
    )
    if execution:
        _assert_real_population_inputs(direct_result["result_population"], execution)
        _validate_real_execution(execution)
        if file_sha256(_repo_path(approval_rel)) != approval_hash:
            raise RunnerAdapterError("approval bytes changed during execution")
    adapter_output_path = Path(str(adapter_result["output_path"]))
    direct_output_path = Path(str(direct_result["output_path"]))
    reconciliation = _reconcile_outputs(adapter_output_path, direct_output_path)
    if execution:
        reconciliation["execution_binding"] = dict(execution)
    _assert_result_population_preserves_budget(
        result_population=adapter_result["result_population"],
        approved_budget=approved_budget,
        expected_variant_ids=expected_variant_ids,
    )
    _assert_result_population_preserves_budget(
        result_population=direct_result["result_population"],
        approved_budget=approved_budget,
        expected_variant_ids=expected_variant_ids,
    )
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
        "approved_sweep_budget": approved_budget,
        "largest_tested_denominator": approved_budget["committed_population_count"],
        "budget_exceeded": False,
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
        approved_sweep_budget=approved_budget,
        reconciliation=reconciliation,
        audit_records=audit_records,
    )
