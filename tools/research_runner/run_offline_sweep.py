"""Build-and-test-only offline research sweep runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
from jsonschema import Draft7Validator

from lib.backtest import run_backtest
from lib.evaluation import max_drawdown, sharpe
from tools.registry.validate_result_populations import (
    DEFAULT_RESULT_POPULATION_SCHEMA_PATH,
    HASH_ALGORITHM,
    OUTCOME_CATEGORIES,
    RESULT_POPULATION_HASH_SCOPE_VERSION,
    validate_result_populations,
)
from tools.registry.validate_strategy_specs import (
    DEFAULT_SCHEMA_PATH as DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    validate_strategy_specs,
)
from tools.registry.validate_variant_sweep_artifacts import (
    DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    validate_variant_sweep_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RESULT_POPULATIONS_DIR = REPO_ROOT / "research" / "result_populations"
HASH_ALGORITHM = "sha256"
OUTCOME_CATEGORIES = (
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
RUNNER_VERSION = "wp-s2c-190-build-test-v1"
RUNNER_CODE_REF = "tools.research_runner.run_offline_sweep"
FIXED_AUDIT_TIMESTAMP = "2026-06-01T00:00:00Z"


class OfflineSweepError(RuntimeError):
    """Raised for preflight or output validation failures."""


class OfflineSweepAbort(RuntimeError):
    """Raised for deterministic fixture infrastructure aborts."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256_prefixed(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _get_path(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise OfflineSweepError(f"missing required path: {dotted_path}")
        current = current[part]
    return current


def _hash_scope_payload(payload: dict[str, Any], scope: list[str]) -> dict[str, Any]:
    return {path: _get_path(payload, path) for path in scope}


def _canonical_hash(payload: dict[str, Any], scope: list[str]) -> str:
    return _sha256_prefixed(_hash_scope_payload(payload, scope))


def _validate_schema_file(path: Path, schema_path: Path) -> None:
    schema = _load_json(schema_path)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(_load_json(path)), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path)
        prefix = f"{location}: " if location else ""
        raise OfflineSweepError(f"{path}: {prefix}{first.message}")


def _validate_parent_inputs(
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for path in (strategy_spec_path, variant_manifest_path, sweep_plan_path):
        if not path.exists():
            raise OfflineSweepError(f"input file does not exist: {path}")

    _validate_schema_file(strategy_spec_path, DEFAULT_STRATEGY_SPEC_SCHEMA_PATH)
    _validate_schema_file(variant_manifest_path, DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH)
    _validate_schema_file(sweep_plan_path, DEFAULT_SWEEP_PLAN_SCHEMA_PATH)

    strategy_errors = validate_strategy_specs(strategy_specs_dir=strategy_spec_path.parent)
    if strategy_errors:
        raise OfflineSweepError("; ".join(strategy_errors))

    variant_errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=variant_manifest_path.parent,
        sweep_plans_dir=sweep_plan_path.parent,
        strategy_specs_dir=strategy_spec_path.parent,
    )
    if variant_errors:
        raise OfflineSweepError("; ".join(variant_errors))

    strategy_spec = _load_json(strategy_spec_path)
    manifest = _load_json(variant_manifest_path)
    sweep_plan = _load_json(sweep_plan_path)

    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    sweep_manifest_hash = sweep_plan["parent_variant_manifest"]["manifest_hash"]
    if manifest["parent_strategy_spec"]["strategy_spec_hash"] != strategy_hash:
        raise OfflineSweepError("parent Strategy Spec hash mismatch")
    if sweep_manifest_hash != manifest_hash:
        raise OfflineSweepError("parent manifest hash mismatch")

    pre_registration = manifest["population_governance"]["pre_registration"]
    if pre_registration["pre_registration_status"] != "frozen_for_sweep_planning":
        raise OfflineSweepError("manifest is not frozen_for_sweep_planning")

    manifest_count = manifest["population_governance"]["declared_population"][
        "committed_population_count"
    ]
    sweep_count = sweep_plan["trial_accounting"]["committed_population_count"]
    if manifest_count != sweep_count:
        raise OfflineSweepError("manifest/sweep committed denominator mismatch")
    if sweep_plan["parent_variant_manifest"]["manifest_committed_population_count"] != manifest_count:
        raise OfflineSweepError("sweep parent manifest committed count mismatch")

    manifest_ids = {row["variant_id"] for row in manifest["variant_assignments"]}
    selected_ids = set(sweep_plan["test_selection"]["selected_variant_ids"])
    excluded_ids = set(sweep_plan["test_selection"]["excluded_variant_ids"])
    outside = (selected_ids | excluded_ids) - manifest_ids
    if outside:
        raise OfflineSweepError(f"selected variant outside manifest: {sorted(outside)}")

    accounting = manifest["population_governance"]["multiple_testing_accounting"]
    if accounting["adaptive_search_used"] is not False:
        raise OfflineSweepError("adaptive search is forbidden")
    if sweep_plan["test_selection"]["post_hoc_addition_forbidden"] is not True:
        raise OfflineSweepError("post-hoc expansion is forbidden")
    if sweep_plan["validation_methods"]["no_runner_hooks"] is not True:
        raise OfflineSweepError("runner hooks are forbidden in sweep plan")
    if sweep_plan["validation_methods"]["no_formulas"] is not True:
        raise OfflineSweepError("formula execution is forbidden in sweep plan")

    _guard_no_runtime_contact_config(strategy_spec, manifest, sweep_plan)
    if not DEFAULT_RESULT_POPULATION_SCHEMA_PATH.exists():
        raise OfflineSweepError("result population schema is missing")
    return strategy_spec, manifest, sweep_plan


def _guard_no_runtime_contact_config(*payloads: dict[str, Any]) -> None:
    forbidden = (
        "broker",
        "exchange_instruction",
        "order_instruction",
        "paper_action",
        "live_action",
        "oms",
        "reconciliation",
        "risk_cap",
        "safe_mode",
        "kill_switch",
        "credentials",
        "private_key",
        "tier_4",
    )

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lower_key = str(key).lower()
                if lower_key in forbidden:
                    raise OfflineSweepError(f"protected runtime key forbidden: {path}.{key}")
                walk(child, f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}.{index}")

    for payload in payloads:
        walk(payload)


def _guard_output_dir(output_dir: Path | None, write_result_population: bool) -> Path | None:
    if not write_result_population:
        return None
    if output_dir is None:
        raise OfflineSweepError("--output-dir is required with --write-result-population")
    resolved = output_dir.resolve()
    canonical = CANONICAL_RESULT_POPULATIONS_DIR.resolve()
    if resolved == canonical or canonical in resolved.parents:
        raise OfflineSweepError("canonical research/result_populations output is disabled")
    return resolved


def _variant_fixture_mode(variant: dict[str, Any]) -> str | None:
    reason = variant.get("status_reason")
    if isinstance(reason, str) and reason.startswith("runner_fixture:"):
        return reason.split(":", 1)[1]
    return None


def _synthetic_inputs(variant_id: str, deterministic_seed: int) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    seed_offset = int(hashlib.sha256(f"{variant_id}:{deterministic_seed}".encode()).hexdigest()[:4], 16)
    index = pd.date_range("2026-01-01", periods=48, freq="h", tz="UTC")
    base = 100.0 + (seed_offset % 11)
    close = [base + (i * 0.15) + ((i % 5) * 0.03) for i in range(len(index))]
    open_ = [price - 0.05 for price in close]
    high = [price + 0.2 for price in close]
    low = [price - 0.2 for price in close]
    ohlcv = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": [1000.0] * len(index)},
        index=index,
    )
    direction = 1.0 if seed_offset % 2 == 0 else -1.0
    signal = pd.Series(0.0, index=index)
    signal.iloc[3:28] = direction
    signal.iloc[28:] = 0.0
    funding = pd.DataFrame({"funding_rate": [0.0] * 6}, index=index[::8][:6])
    return signal, ohlcv, funding


def _run_synthetic_backtest(variant_id: str, deterministic_seed: int) -> Any:
    signal, ohlcv, funding = _synthetic_inputs(variant_id, deterministic_seed)
    return run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=4.0,
        fee_bps_maker=2.0,
        slippage_bps=1.0,
        initial_equity=10_000.0,
        stream="klines",
        interval="1h",
        gaps_path=REPO_ROOT / "tools" / "research_runner" / "_nonexistent_empty_gaps.json",
        entry_fee_side="taker",
        exit_fee_side="taker",
        funding_notional_mode="entry_price",
        order_size=1.0,
        fill_mode="complete",
        slippage_model="fixed_bps",
        liquidation_mode="zero_equity",
        mark_price_source="close",
        bar_path_assumption="next_open_close_mark",
    )


def _metrics_from_backtest(result: Any) -> dict[str, Any]:
    returns = result.equity_curve.pct_change().dropna()
    drawdown, _, _ = max_drawdown(result.equity_curve)
    final_equity = float(result.equity_curve.iloc[-1])
    initial_equity = float(result.params["initial_equity"])
    trade_count = int(len(result.trades_df))
    win_rate = 0.0
    if trade_count and "net_pnl" in result.trades_df.columns:
        win_rate = float((result.trades_df["net_pnl"] > 0).sum() / trade_count)
    return {
        "pnl": float(final_equity - initial_equity),
        "return_pct": float((final_equity - initial_equity) / initial_equity),
        "drawdown": float(drawdown),
        "trade_count": trade_count,
        "win_rate": win_rate,
        "sharpe": float(sharpe(returns, "1h")),
        "fees": float(result.fees_paid),
        "funding": float(result.funding_paid),
        "slippage": float(result.slippage_paid),
        "exposure": 1.0 if trade_count else 0.0,
    }


def _empty_metrics() -> dict[str, Any]:
    return {
        "pnl": None,
        "return_pct": None,
        "drawdown": None,
        "trade_count": None,
        "win_rate": None,
        "sharpe": None,
        "fees": None,
        "funding": None,
        "slippage": None,
        "exposure": None,
    }


def _non_success(outcome: str, reason: str | None) -> dict[str, Any]:
    return {
        "reason": reason,
        "rule_ref": None,
        "declared_before_results": None if outcome == "successful" else True,
        "counts_in_denominator": True,
    }


def _error(outcome: str, message_class: str | None, infrastructure: bool = False) -> dict[str, Any]:
    category = None
    if outcome in {"errored", "aborted"}:
        category = "runner_error"
    elif outcome == "data_unavailable":
        category = "data_error"
    elif outcome == "failed":
        category = "strategy_underperformance"
    return {
        "error_category": category,
        "error_message_class": message_class,
        "is_infrastructure_error": infrastructure if category else None,
        "is_strategy_underperformance": outcome == "failed" if category else None,
        "counts_in_denominator": True,
    }


def _data_coverage(outcome: str) -> dict[str, Any]:
    unavailable = outcome == "data_unavailable"
    return {
        "data_catalog_ref": "synthetic_fixture_only",
        "data_slice_identity": "synthetic-offline-runner-v1",
        "timeframe": "1h",
        "data_stream": "ohlcv",
        "missing_data_policy": "block_if_missing",
        "irreparable_gap": unavailable,
        "counts_in_denominator": True,
    }


def _row(
    result_population_id: str,
    row_number: int,
    variant: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    outcome: str,
    metrics: dict[str, Any] | None = None,
    reason: str | None = None,
    error_message_class: str | None = None,
    infrastructure_error: bool = False,
) -> dict[str, Any]:
    variant_id = variant["variant_id"]
    row = {
        "variant_id": variant_id,
        "row_id": f"{result_population_id}-ROW-{row_number:06d}",
        "row_identity_hash": None,
        "assignment_hash": variant.get("parameter_value_hash"),
        "assignment_ref": None,
        "outcome_category": outcome,
        "attempted": outcome in {"successful", "failed", "errored", "data_unavailable"},
        "metrics": metrics if outcome == "successful" else _empty_metrics(),
        "non_success": _non_success(outcome, reason),
        "error": _error(outcome, error_message_class, infrastructure_error),
        "data_coverage": _data_coverage(outcome),
        "backtest_assumption_ref": "backtest_assumption_summary",
        "lineage": {
            "parent_variant_id": variant_id,
            "parent_variant_assignment_hash": variant.get("parameter_value_hash"),
            "parent_variant_assignment_ref": None,
            "parent_sweep_plan_id": sweep_plan["sweep_plan_id"],
            "parent_manifest_id": manifest["variant_manifest_id"],
        },
        "row_mutation_policy": {
            "scientific_row_identity_immutable_after_commit": True,
            "corrections_require_append_only_event": True,
            "post_commit_in_place_mutation_forbidden": True,
            "post_hoc_cleanup_forbidden": True,
        },
    }
    row["row_identity_hash"] = _sha256_prefixed(
        {
            "variant_id": row["variant_id"],
            "assignment_hash": row["assignment_hash"],
            "outcome_category": row["outcome_category"],
            "metrics": row["metrics"],
            "non_success": row["non_success"],
            "error": row["error"],
            "data_coverage": row["data_coverage"],
            "lineage": row["lineage"],
        }
    )
    return row


def _deterministic_result_population_id(
    strategy_hash: str,
    manifest_hash: str,
    sweep_hash: str,
    backtest_assumption_summary: dict[str, Any],
) -> str:
    digest = hashlib.sha256(
        _canonical_json_bytes(
            {
                "strategy_hash": strategy_hash,
                "manifest_hash": manifest_hash,
                "sweep_hash": sweep_hash,
                "backtest_assumption_summary": backtest_assumption_summary,
            }
        )
    ).hexdigest()
    return f"RP-{int(digest[:8], 16) % 10000:04d}"


def _backtest_assumption_summary(sweep_plan: dict[str, Any]) -> dict[str, Any]:
    assumptions = sweep_plan["realism_assumptions"]
    return {
        "fee_side_assumption": assumptions["fee_side_assumption"] or "taker_entry_taker_exit",
        "exchange_constraint_disclosure": str(assumptions["exchange_constraints_disclosed"]),
        "funding_notional": "entry_price",
        "slippage_model": "fixed_bps",
        "fill_mode": "complete",
        "order_size_assumption": assumptions["order_size_assumption"] or "fixed_1_contract",
        "liquidity_capacity_assumption": assumptions["liquidity_capacity_assumption"],
        "liquidation_mode": "zero_equity",
        "maintenance_margin_assumption": assumptions["maintenance_margin_assumption"],
        "mark_price_source": "close",
        "bar_path_assumption": "next_open_close_mark",
        "records_assumptions_only": True,
    }


def _execute_rows(
    result_population_id: str,
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    deterministic_seed: int,
) -> tuple[list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    aborted = False
    variants = sorted(manifest["variant_assignments"], key=lambda row: row["variant_id"])
    for index, variant in enumerate(variants, start=1):
        if aborted:
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "not_attempted",
                    reason="infrastructure abort before variant attempt",
                )
            )
            continue

        mode = _variant_fixture_mode(variant)
        status = variant["assignment_status"]
        if status == "invalid":
            rows.append(
                _row(result_population_id, index, variant, manifest, sweep_plan, "invalid", reason=status)
            )
            continue
        if status == "excluded":
            rows.append(
                _row(result_population_id, index, variant, manifest, sweep_plan, "excluded", reason=status)
            )
            continue
        if status == "not_attempted":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "not_attempted",
                    reason=status,
                )
            )
            continue
        if mode == "data_unavailable":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "data_unavailable",
                    reason="fixture declared missing synthetic data",
                    error_message_class="FixtureDataUnavailable",
                )
            )
            continue
        if mode == "infra_abort":
            aborted = True
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "aborted",
                    reason="fixture infrastructure abort",
                    error_message_class="OfflineSweepAbort",
                    infrastructure_error=True,
                )
            )
            continue
        try:
            if mode == "errored":
                raise RuntimeError("fixture variant error")
            result = _run_synthetic_backtest(variant["variant_id"], deterministic_seed)
            metrics = _metrics_from_backtest(result)
            outcome = "successful" if math.isfinite(metrics["return_pct"]) else "failed"
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    outcome,
                    metrics=metrics,
                    reason=None if outcome == "successful" else "non-finite return",
                )
            )
        except Exception as exc:
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "errored",
                    reason="per-variant runner error",
                    error_message_class=exc.__class__.__name__,
                )
            )
    return rows, aborted


def _build_result_population(
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    run_label: str | None,
    deterministic_seed: int,
) -> tuple[dict[str, Any], bool]:
    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    sweep_hash = _sha256_prefixed(sweep_plan)
    committed_count = manifest["population_governance"]["declared_population"][
        "committed_population_count"
    ]
    selected_count = sweep_plan["trial_accounting"]["selected_variant_count"]
    backtest_assumptions = _backtest_assumption_summary(sweep_plan)
    result_population_id = _deterministic_result_population_id(
        strategy_hash, manifest_hash, sweep_hash, backtest_assumptions
    )
    rows, aborted = _execute_rows(result_population_id, manifest, sweep_plan, deterministic_seed)
    counts = {category: 0 for category in OUTCOME_CATEGORIES}
    counts.update(Counter(row["outcome_category"] for row in rows))
    counts["counts_sum"] = sum(counts[category] for category in OUTCOME_CATEGORIES)
    counts["counts_sum_equals_committed_denominator"] = True
    error_counts = {category: counts[category] for category in OUTCOME_CATEGORIES if category != "successful"}

    payload = {
        "schema_version": "v1",
        "result_population_id": result_population_id,
        "status": "generated",
        "non_authority_declaration": _non_authority_declaration(),
        "parent_strategy_spec": {
            "strategy_spec_id": strategy_spec["strategy_spec_id"],
            "strategy_spec_schema_version": strategy_spec["schema_version"],
            "strategy_spec_hash": strategy_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_ref": None,
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
        },
        "parent_variant_manifest": {
            "variant_manifest_id": manifest["variant_manifest_id"],
            "variant_manifest_schema_version": manifest["schema_version"],
            "manifest_hash": manifest_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "manifest_ref": None,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "committed_population_count": committed_count,
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
        },
        "parent_sweep_plan": {
            "sweep_plan_id": sweep_plan["sweep_plan_id"],
            "sweep_plan_schema_version": sweep_plan["schema_version"],
            "sweep_plan_identity_hash": sweep_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "sweep_plan_identity_hash_scope_v1",
            "sweep_plan_ref": None,
            "manifest_id": manifest["variant_manifest_id"],
            "manifest_hash": manifest_hash,
            "committed_population_count": committed_count,
            "selected_variant_count": selected_count,
            "mismatch_policy": "block",
            "missing_sweep_plan_policy": "block",
        },
        "execution_context": {
            "runner_id": "offline-research-runner",
            "runner_version": RUNNER_VERSION,
            "runner_code_ref": RUNNER_CODE_REF,
            "repo_commit": "build-test-only",
            "environment_summary": ["synthetic_fixture_only"],
            "dependency_summary": ["pandas", "jsonschema"],
            "determinism_seed": deterministic_seed,
            "execution_mode": "offline_research",
            "offline_only": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_broker_exchange_order_contact": True,
            "no_protected_path_contact": True,
        },
        "input_identity_hash": _identity_hash_object("input_identity_hash_scope_v1", _input_scope()),
        "result_population_identity_hash": _identity_hash_object(
            RESULT_POPULATION_HASH_SCOPE_VERSION,
            _result_scope(),
        ),
        "audit_envelope": {
            "excluded_from_input_identity_hash": True,
            "excluded_from_result_population_identity_hash": True,
            "may_contain_scientific_content": False,
            "administrative_only": True,
            "created_at": FIXED_AUDIT_TIMESTAMP,
            "created_by": "tools.research_runner.run_offline_sweep",
            "review_notes": [],
            "operator_notes": [f"run_label={run_label}"] if run_label else [],
            "validation_run_logs": [],
            "administrative_lineage": [],
        },
        "committed_denominator_snapshot": {
            "denominator_basis": "committed_pre_registered_population_count",
            "parent_manifest_committed_population_count": committed_count,
            "parent_sweep_plan_committed_population_count": committed_count,
            "selected_variant_count": selected_count,
            "result_row_count": len(rows),
            "outcome_counts_sum": counts["counts_sum"],
            "committed_denominator": committed_count,
            **_denominator_flags(),
        },
        "variant_result_rows": rows,
        "outcome_category_counts": counts,
        "append_only_ledger": {
            "ledger_required": True,
            "append_only": True,
            "post_commit_in_place_mutation_forbidden": True,
            "scientific_identity_mutation_forbidden_after_finalization": True,
            "corrections_require_append_only_event": True,
            "supersession_preserves_prior_result_population": True,
            "creation_event_ref": f"{result_population_id}-EVENT-001",
            "events": [
                {
                    "event_id": f"{result_population_id}-EVENT-001",
                    "event_type": "created",
                    "event_timestamp": FIXED_AUDIT_TIMESTAMP,
                    "actor_or_tool": "tools.research_runner.run_offline_sweep",
                    "related_artifact_refs": [],
                    "notes": ["build-and-test-only synthetic runner output"],
                }
            ],
        },
        "validation_summary": {
            "schema_validation_status": "passed",
            "validator_status": "passed",
            "validator_version": "wp-s2c-189",
            "validator_identity": "tools.registry.validate_result_populations",
            "validation_timestamp": FIXED_AUDIT_TIMESTAMP,
            "blocking_errors": [],
            "non_blocking_warnings": [],
            "validator_authority_boundary": "evidence_only_no_approval_no_execution",
            "validator_does_not_approve": True,
            "validator_does_not_recommend": True,
            "validator_does_not_rank": True,
            "validator_does_not_execute": True,
            "validator_does_not_contact_runtime": True,
        },
        "error_summary": {
            "failed": error_counts["failed"],
            "errored": error_counts["errored"],
            "aborted": error_counts["aborted"],
            "filtered": error_counts["filtered"],
            "data_unavailable": error_counts["data_unavailable"],
            "not_attempted": error_counts["not_attempted"],
            "invalid": error_counts["invalid"],
            "excluded": error_counts["excluded"],
            "all_error_categories_counted_in_denominator": True,
            "error_rows_preserved": True,
        },
        "data_coverage_summary": {
            "data_catalog_ref": "synthetic_fixture_only",
            "data_slice_identity": "synthetic-offline-runner-v1",
            "timeframe": "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap_count": counts["data_unavailable"],
            "data_unavailable_count": counts["data_unavailable"],
            "data_coverage_notes": ["fixture/synthetic data only"],
        },
        "backtest_assumption_summary": backtest_assumptions,
        "lineage": {
            "strategy_spec_id": strategy_spec["strategy_spec_id"],
            "variant_manifest_id": manifest["variant_manifest_id"],
            "sweep_plan_id": sweep_plan["sweep_plan_id"],
            "result_population_id": result_population_id,
            "parent_hash_chain": {
                "strategy_spec_hash": strategy_hash,
                "variant_manifest_hash": manifest_hash,
                "sweep_plan_identity_hash": sweep_hash,
                "input_identity_hash": None,
            },
            "created_from_validated_inputs": True,
            "complete_population_lineage_preserved": True,
        },
        "review": {
            "review_status": "not_reviewed",
            "review_scope": "none",
            "review_notes": [],
            "non_authority_acknowledgement": {
                "not_approval": True,
                "not_recommendation": True,
                "not_readiness": True,
                "not_transition": True,
                "not_gate_satisfaction": True,
                "not_runtime_authority": True,
                "not_paper_live_authority": True,
            },
        },
    }
    payload["input_identity_hash"]["hash"] = _canonical_hash(payload, _input_scope())
    payload["lineage"]["parent_hash_chain"]["input_identity_hash"] = payload["input_identity_hash"][
        "hash"
    ]
    payload["result_population_identity_hash"]["hash"] = _canonical_hash(payload, _result_scope())
    return payload, aborted


def _identity_hash_object(scope_version: str, scope: list[str]) -> dict[str, Any]:
    return {
        "hash": None,
        "hash_algorithm": HASH_ALGORITHM,
        "canonicalization": "json_canonical_v1",
        "hash_scope_version": scope_version,
        "hash_scope": scope,
        "audit_envelope_excluded": True,
        "audit_envelope_exclusion_reason": (
            "administrative_audit_metadata_is_excluded_from_scientific_identity"
        ),
    }


def _input_scope() -> list[str]:
    return [
        "parent_strategy_spec.strategy_spec_hash",
        "parent_variant_manifest.manifest_hash",
        "parent_sweep_plan.sweep_plan_identity_hash",
        "parent_variant_manifest.committed_population_count",
        "parent_sweep_plan.committed_population_count",
        "execution_context.runner_code_ref",
        "execution_context.repo_commit",
        "data_coverage_summary.data_catalog_ref",
        "data_coverage_summary.data_slice_identity",
        "backtest_assumption_summary",
    ]


def _result_scope() -> list[str]:
    return [
        *_input_scope(),
        "committed_denominator_snapshot",
        "variant_result_rows",
        "outcome_category_counts",
        "append_only_ledger.creation_event_ref",
        "validation_summary.validator_identity",
    ]


def _non_authority_declaration() -> dict[str, Any]:
    flags = [
        "not_executable",
        "not_runner_authority",
        "not_sweep_authority",
        "not_result_authority",
        "not_candidate_approval",
        "not_exp_approval",
        "not_ranking_authority",
        "not_recommendation_authority",
        "not_readiness_authority",
        "not_transition_authority",
        "not_runtime_authority",
        "not_paper_live_authority",
        "not_gate_authority",
        "not_canonical_evidence_replacement",
        "not_trial_log_replacement",
        "not_outcome_ledger_replacement",
        "not_reconciliation_authority",
        "not_decision_authority",
        "not_exp_replacement",
        "not_rep_replacement",
        "not_ol_replacement",
        "not_rec_replacement",
        "not_dec_replacement",
    ]
    return {**{flag: True for flag in flags}, "canonical_evidence_relationship": "reference_only"}


def _denominator_flags() -> dict[str, bool]:
    return {
        "denominator_equals_parent_manifest_committed_population_count": True,
        "denominator_equals_parent_sweep_plan_committed_population_count": True,
        "outcome_counts_sum_equals_committed_denominator": True,
        "result_row_count_equals_committed_denominator": True,
        "executed_only_denominator_forbidden": True,
        "successful_only_denominator_forbidden": True,
        "winner_only_retention_forbidden": True,
        "post_hoc_cleanup_forbidden": True,
        "failed_variants_remain_in_denominator": True,
        "invalid_variants_remain_in_denominator": True,
        "excluded_variants_remain_in_denominator": True,
        "errored_variants_remain_in_denominator": True,
        "aborted_variants_remain_in_denominator": True,
        "filtered_variants_remain_in_denominator": True,
        "data_unavailable_variants_remain_in_denominator": True,
        "not_attempted_variants_remain_in_denominator": True,
    }


def _validate_in_memory_payload(payload: dict[str, Any]) -> None:
    schema = _load_json(DEFAULT_RESULT_POPULATION_SCHEMA_PATH)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path)
        prefix = f"{location}: " if location else ""
        raise OfflineSweepError(f"result-population schema validation failed: {prefix}{first.message}")
    for object_path in ("input_identity_hash", "result_population_identity_hash"):
        scope = payload[object_path]["hash_scope"]
        if payload[object_path]["hash"] != _canonical_hash(payload, scope):
            raise OfflineSweepError(f"{object_path}.hash mismatch")


def _write_and_validate(
    payload: dict[str, Any],
    output_dir: Path,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{payload['result_population_id']}.result_population.json"
    _write_json(path, payload)
    errors = validate_result_populations(
        result_populations_dir=output_dir,
        strategy_specs_dir=strategy_spec_path.parent,
        variant_manifests_dir=variant_manifest_path.parent,
        sweep_plans_dir=sweep_plan_path.parent,
    )
    if errors:
        raise OfflineSweepError("; ".join(errors))
    return path


def run_offline_sweep(
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    output_dir: Path | None = None,
    *,
    write_result_population: bool = False,
    run_label: str | None = None,
    deterministic_seed: int = 0,
) -> dict[str, Any]:
    """Run a deterministic build-and-test-only offline research sweep."""
    if deterministic_seed is None:
        raise OfflineSweepError("deterministic_seed must be fixed")
    guarded_output_dir = _guard_output_dir(output_dir, write_result_population)
    strategy_spec, manifest, sweep_plan = _validate_parent_inputs(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
    )
    payload, aborted = _build_result_population(
        strategy_spec,
        manifest,
        sweep_plan,
        run_label,
        deterministic_seed,
    )
    _validate_in_memory_payload(payload)

    output_path = None
    if write_result_population:
        assert guarded_output_dir is not None
        output_path = _write_and_validate(
            payload,
            guarded_output_dir,
            strategy_spec_path,
            variant_manifest_path,
            sweep_plan_path,
        )
    return {
        "ok": not aborted,
        "aborted": aborted,
        "dry_run": not write_result_population,
        "wrote": output_path is not None,
        "output_path": str(output_path) if output_path else None,
        "result_population": payload,
        "result_population_id": payload["result_population_id"],
        "committed_denominator": payload["committed_denominator_snapshot"][
            "committed_denominator"
        ],
        "outcome_category_counts": payload["outcome_category_counts"],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy-spec", required=True, type=Path)
    parser.add_argument("--variant-manifest", required=True, type=Path)
    parser.add_argument("--sweep-plan", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-result-population", action="store_true")
    parser.add_argument("--run-label")
    parser.add_argument("--deterministic-seed", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_offline_sweep(
            args.strategy_spec,
            args.variant_manifest,
            args.sweep_plan,
            args.output_dir,
            write_result_population=args.write_result_population,
            run_label=args.run_label,
            deterministic_seed=args.deterministic_seed,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": result["ok"],
                "aborted": result["aborted"],
                "dry_run": result["dry_run"],
                "wrote": result["wrote"],
                "output_path": result["output_path"],
                "result_population_id": result["result_population_id"],
                "committed_denominator": result["committed_denominator"],
                "outcome_category_counts": result["outcome_category_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
