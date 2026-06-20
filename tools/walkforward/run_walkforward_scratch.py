"""Execute explicit walk-forward folds through the existing offline runner path.

This module writes scratch reports only. It does not write Result Populations,
trial-log rows, canonical fold manifests, or any runtime/paper/live artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from tools.registry.validate_walkforward_fold_manifest import (
    validate_walkforward_fold_manifests,
)
from tools.registry.validate_walkforward_run_report import validate_walkforward_run_reports
from tools.research_runner import run_offline_sweep as runner


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_SPEC = REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0004.strategy_spec.json"
DEFAULT_VARIANT_MANIFEST = REPO_ROOT / "research" / "variant_manifests" / "VM-0004.variant_manifest.json"
DEFAULT_SWEEP_PLAN = REPO_ROOT / "research" / "sweep_plans" / "SWEEP-PLAN-0004.sweep_plan.json"
DEFAULT_D4_CATALOG = REPO_ROOT / "research" / "data_slices" / "binance_usdtm_btcusdt_15m" / "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
DEFAULT_D2_IMPORT = REPO_ROOT / "research" / "data_slices" / "binance_usdtm_btcusdt_15m" / "binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / "WP-LAB-WALKFORWARD-RUN-01"
NON_AUTHORITY_FLAGS = [
    "not canonical evidence",
    "not promotion evidence",
    "not ranking authority",
    "not readiness authority",
    "not paper/live authority",
    "not candidate registration",
]
METRIC_NAMES = (
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


class WalkForwardScratchError(RuntimeError):
    """Raised when a scratch walk-forward run cannot safely proceed."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _source_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _parse_utc(value: str, label: str) -> pd.Timestamp:
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is None or str(parsed.tzinfo) not in ("UTC", "UTC+00:00"):
        raise WalkForwardScratchError(f"{label} must be UTC")
    return parsed.tz_convert("UTC")


def _assert_scratch_path(path: Path) -> Path:
    resolved = path.resolve()
    scratch_root = (REPO_ROOT / "scratch").resolve()
    if resolved != scratch_root and scratch_root not in resolved.parents:
        raise WalkForwardScratchError(f"output must remain under {scratch_root}: {resolved}")
    return resolved


def _validate_manifest(path: Path) -> dict[str, Any]:
    errors = validate_walkforward_fold_manifests(explicit_paths=[path])
    if errors:
        raise WalkForwardScratchError("invalid walk-forward fold manifest: " + "; ".join(errors))
    return _load_json(path)


def _validate_lineage(
    fold_manifest: dict[str, Any],
    strategy_spec: dict[str, Any],
    variant_manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
) -> None:
    expected = {
        "strategy_spec_id": strategy_spec.get("strategy_spec_id"),
        "variant_manifest_id": variant_manifest.get("variant_manifest_id"),
        "sweep_plan_id": sweep_plan.get("sweep_plan_id"),
    }
    mismatches = [
        f"{key}: manifest={fold_manifest.get(key)!r}, parent={value!r}"
        for key, value in expected.items()
        if fold_manifest.get(key) != value
    ]
    if mismatches:
        raise WalkForwardScratchError("walk-forward lineage mismatch: " + "; ".join(mismatches))


def _load_execution_input(
    ohlcv_input_path: Path,
    d4_catalog_slice_path: Path | None,
    d2_import_report_path: Path | None,
) -> Any:
    if (d4_catalog_slice_path is None) != (d2_import_report_path is None):
        raise WalkForwardScratchError("D4 catalog and D2 import paths must be supplied together")
    if d4_catalog_slice_path is not None and d2_import_report_path is not None:
        return runner._d4_catalog_execution_input(  # noqa: SLF001 - existing read-only runner loader
            ohlcv_input_path,
            d4_catalog_slice_path,
            d2_import_report_path,
        )
    return runner._canonical_15m_execution_input(ohlcv_input_path)  # noqa: SLF001


def _finite_number(value: Any) -> float | int | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    numeric = float(value)
    if not math.isfinite(numeric):
        return None
    if isinstance(value, int):
        return value
    return numeric


def _clean_metrics(metrics: dict[str, Any] | None) -> dict[str, float | int | None] | None:
    if metrics is None:
        return None
    return {name: _finite_number(metrics.get(name)) for name in METRIC_NAMES}


def _metric_summary(rows: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    metric_rows = [row[key] for row in rows if row["status"] == "successful" and row[key] is not None]
    if not metric_rows:
        return None
    summary: dict[str, Any] = {"successful_variant_count": len(metric_rows), "metrics": {}}
    for name in METRIC_NAMES:
        values = [float(row[name]) for row in metric_rows if row.get(name) is not None]
        summary["metrics"][name] = (
            {
                "mean": sum(values) / len(values),
                "minimum": min(values),
                "maximum": max(values),
            }
            if values
            else None
        )
    return summary


def _degradation_summary(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    comparable = [
        row
        for row in rows
        if row["status"] == "successful"
        and row["is_metrics"] is not None
        and row["oos_metrics"] is not None
    ]
    if not comparable:
        return None

    def mean_delta(metric: str) -> float | None:
        values = [
            float(row["oos_metrics"][metric]) - float(row["is_metrics"][metric])
            for row in comparable
            if row["is_metrics"].get(metric) is not None
            and row["oos_metrics"].get(metric) is not None
        ]
        return sum(values) / len(values) if values else None

    efficiencies = [
        float(row["sharpe_efficiency"])
        for row in comparable
        if row["sharpe_efficiency"] is not None
    ]
    return {
        "comparable_variant_count": len(comparable),
        "mean_sharpe_delta": mean_delta("sharpe"),
        "mean_return_pct_delta": mean_delta("return_pct"),
        "mean_drawdown_delta": mean_delta("drawdown"),
        "mean_trade_count_delta": mean_delta("trade_count"),
        "sharpe_efficiency_available_count": len(efficiencies),
        "mean_sharpe_efficiency": sum(efficiencies) / len(efficiencies) if efficiencies else None,
    }


def _execute_fold(
    fold: dict[str, Any],
    strategy_spec: dict[str, Any],
    variants: list[dict[str, Any]],
    execution_input: Any,
    sizing_mode: str,
    target_leverage: float,
) -> dict[str, Any]:
    selection_start = _parse_utc(fold["selection_window_start_utc"], "selection start")
    selection_end = _parse_utc(fold["selection_window_end_utc"], "selection end")
    evaluation_start = _parse_utc(fold["evaluation_window_start_utc"], "evaluation start")
    evaluation_end = _parse_utc(fold["evaluation_window_end_utc"], "evaluation end")
    windows = {
        "selection_window": {"start_utc": fold["selection_window_start_utc"], "end_utc": fold["selection_window_end_utc"]},
        "evaluation_window": {"start_utc": fold["evaluation_window_start_utc"], "end_utc": fold["evaluation_window_end_utc"]},
    }
    warnings: list[str] = []
    try:
        is_input = runner._slice_execution_input(  # noqa: SLF001 - explicit manifest boundary adapter
            execution_input,
            start=selection_start,
            end=selection_end,
            window_label=f"{fold['fold_id']}:selection",
        )
        oos_input = runner._slice_execution_input(  # noqa: SLF001
            execution_input,
            start=evaluation_start,
            end=evaluation_end,
            window_label=f"{fold['fold_id']}:evaluation",
        )
    except Exception as exc:
        warning = f"fold_data_unavailable:{exc.__class__.__name__}:{exc}"
        return {
            "fold_id": fold["fold_id"],
            "fold_order": fold["fold_order"],
            **windows,
            "is_metrics": None,
            "oos_metrics": None,
            "degradation_metrics": None,
            "variant_count_posture": {
                "declared": fold["declared_variant_count"],
                "attempted": 0,
                "successful": 0,
                "errored": 0,
                "data_unavailable": fold["declared_variant_count"],
                "not_attempted": fold["declared_variant_count"],
                "denominator_preserved": fold["declared_variant_count"] == len(variants),
            },
            "result_population_ref_or_null": fold.get("result_population_ref"),
            "status": "data_unavailable",
            "warnings": [warning],
            "variant_results": [],
        }

    variant_results: list[dict[str, Any]] = []
    for variant in variants:
        row_warnings: list[str] = []
        try:
            is_metrics = _clean_metrics(
                runner._run_window_variant_backtest(  # noqa: SLF001 - existing runner semantics
                    strategy_spec, variant, is_input, sizing_mode, target_leverage
                )
            )
            oos_metrics = _clean_metrics(
                runner._run_window_variant_backtest(  # noqa: SLF001
                    strategy_spec, variant, oos_input, sizing_mode, target_leverage
                )
            )
            efficiency = runner._efficiency_ratio(  # noqa: SLF001
                is_metrics.get("sharpe") if is_metrics else None,
                oos_metrics.get("sharpe") if oos_metrics else None,
            )
            if efficiency is None:
                row_warnings.append("sharpe_efficiency_unavailable_non_positive_or_missing_is_sharpe")
            status = "successful"
        except Exception as exc:
            is_metrics = None
            oos_metrics = None
            efficiency = None
            status = "errored"
            row_warnings.append(f"variant_error:{exc.__class__.__name__}:{exc}")
        warnings.extend(row_warnings)
        variant_results.append(
            {
                "variant_id": variant["variant_id"],
                "status": status,
                "is_metrics": is_metrics,
                "oos_metrics": oos_metrics,
                "sharpe_efficiency": _finite_number(efficiency),
                "warnings": row_warnings,
            }
        )

    successful = sum(row["status"] == "successful" for row in variant_results)
    errored = len(variant_results) - successful
    denominator_preserved = fold["declared_variant_count"] == len(variants)
    if not denominator_preserved:
        warnings.append("declared_variant_count_does_not_match_included_variant_count")
    status = "successful" if successful == len(variants) and denominator_preserved else "partial"
    if successful == 0:
        status = "errored"
    return {
        "fold_id": fold["fold_id"],
        "fold_order": fold["fold_order"],
        **windows,
        "is_metrics": _metric_summary(variant_results, "is_metrics"),
        "oos_metrics": _metric_summary(variant_results, "oos_metrics"),
        "degradation_metrics": _degradation_summary(variant_results),
        "variant_count_posture": {
            "declared": fold["declared_variant_count"],
            "attempted": len(variant_results),
            "successful": successful,
            "errored": errored,
            "data_unavailable": 0,
            "not_attempted": 0,
            "denominator_preserved": denominator_preserved,
        },
        "result_population_ref_or_null": fold.get("result_population_ref"),
        "status": status,
        "warnings": sorted(set(warnings)),
        "variant_results": variant_results,
    }


def _aggregate(fold_results: list[dict[str, Any]]) -> dict[str, Any]:
    comparable = [fold["degradation_metrics"] for fold in fold_results if fold["degradation_metrics"]]

    def weighted_mean(name: str, weight_name: str = "comparable_variant_count") -> float | None:
        pairs = [
            (float(item[name]), int(item[weight_name]))
            for item in comparable
            if item.get(name) is not None and int(item[weight_name]) > 0
        ]
        total_weight = sum(weight for _, weight in pairs)
        return sum(value * weight for value, weight in pairs) / total_weight if total_weight else None

    return {
        "fold_count": len(fold_results),
        "successful_fold_count": sum(fold["status"] == "successful" for fold in fold_results),
        "partial_fold_count": sum(fold["status"] == "partial" for fold in fold_results),
        "unavailable_or_errored_fold_count": sum(
            fold["status"] in {"data_unavailable", "errored"} for fold in fold_results
        ),
        "comparable_variant_pairs": sum(item["comparable_variant_count"] for item in comparable),
        "mean_sharpe_delta": weighted_mean("mean_sharpe_delta"),
        "mean_return_pct_delta": weighted_mean("mean_return_pct_delta"),
        "mean_drawdown_delta": weighted_mean("mean_drawdown_delta"),
        "mean_sharpe_efficiency": weighted_mean(
            "mean_sharpe_efficiency", "sharpe_efficiency_available_count"
        ),
    }


def _dashboard_fragment(report: dict[str, Any], report_ref: str) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "source_report_ref": report_ref,
        "run_id": report["run_id"],
        "created_at_utc": report["created_at_utc"],
        "canonical_authority": False,
        "scratch_only": True,
        "strategy_spec_id": report["strategy_spec_id"],
        "variant_manifest_id": report["variant_manifest_id"],
        "sweep_plan_id": report["sweep_plan_id"],
        "fold_statuses": [
            {
                "fold_id": fold["fold_id"],
                "fold_order": fold["fold_order"],
                "status": fold["status"],
                "degradation_metrics": fold["degradation_metrics"],
                "warnings": fold["warnings"],
            }
            for fold in report["fold_results"]
        ],
        "aggregate_degradation": report["aggregate_degradation"],
        "warnings": report["warnings"],
        "blockers": report["blockers"],
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
    }


def run_walkforward_scratch(
    *,
    walkforward_manifest_path: Path,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    ohlcv_input_path: Path,
    output_dir: Path,
    created_at_utc: str,
    d4_catalog_slice_path: Path | None = None,
    d2_import_report_path: Path | None = None,
    sizing_mode: str = runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
    target_leverage: float = 1.0,
) -> tuple[Path, Path]:
    """Run explicit folds and write a validated report plus display-only fragment."""
    output_dir = _assert_scratch_path(output_dir)
    _parse_utc(created_at_utc, "created_at_utc")
    fold_manifest = _validate_manifest(walkforward_manifest_path)
    strategy_spec, variant_manifest, sweep_plan = runner._validate_parent_inputs(  # noqa: SLF001
        strategy_spec_path, variant_manifest_path, sweep_plan_path
    )
    _validate_lineage(fold_manifest, strategy_spec, variant_manifest, sweep_plan)
    execution_input = _load_execution_input(
        ohlcv_input_path, d4_catalog_slice_path, d2_import_report_path
    )
    if execution_input.timeframe != fold_manifest["timeframe"]:
        raise WalkForwardScratchError(
            f"timeframe mismatch: manifest={fold_manifest['timeframe']}, data={execution_input.timeframe}"
        )
    if execution_input.data_slice_identity != fold_manifest["data_slice_id"]:
        raise WalkForwardScratchError(
            "data slice mismatch: "
            f"manifest={fold_manifest['data_slice_id']}, data={execution_input.data_slice_identity}"
        )

    variants = [
        variant
        for variant in sorted(variant_manifest["variant_assignments"], key=lambda item: item["variant_id"])
        if variant["assignment_status"] == "included"
    ]
    fold_results = [
        _execute_fold(
            fold,
            strategy_spec,
            variants,
            execution_input,
            sizing_mode,
            target_leverage,
        )
        for fold in sorted(fold_manifest["folds"], key=lambda item: item["fold_order"])
    ]
    source_commit = _source_commit()
    identity = {
        "source_commit": source_commit,
        "walkforward_manifest": fold_manifest,
        "strategy_spec_id": fold_manifest["strategy_spec_id"],
        "variant_manifest_id": fold_manifest["variant_manifest_id"],
        "sweep_plan_id": fold_manifest["sweep_plan_id"],
        "data_slice_id": fold_manifest["data_slice_id"],
        "sizing_mode": sizing_mode,
        "target_leverage": target_leverage,
    }
    manifest_ref = walkforward_manifest_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    report = {
        "schema_version": "v1",
        "run_id": f"WF-RUN-{_canonical_hash(identity)[:16].upper()}",
        "created_at_utc": created_at_utc,
        "source_commit": source_commit,
        "canonical_authority": False,
        "scratch_only": True,
        "strategy_spec_id": fold_manifest["strategy_spec_id"],
        "variant_manifest_id": fold_manifest["variant_manifest_id"],
        "sweep_plan_id": fold_manifest["sweep_plan_id"],
        "walkforward_manifest_ref": manifest_ref,
        "data_slice": {
            "data_slice_id": fold_manifest["data_slice_id"],
            "data_catalog_ref": execution_input.data_catalog_ref,
            "timeframe": execution_input.timeframe,
            "boundary_semantics": fold_manifest["boundary_semantics"],
        },
        "assumptions": {
            "runner_path": "tools.research_runner.run_offline_sweep._run_window_variant_backtest",
            "funding": "existing runner input posture; D4 OHLCV loader supplies zero funding",
            "sizing_mode": sizing_mode,
            "target_leverage": target_leverage,
            "selection_behavior": "carry all included variants; no winner selection",
            "output_posture": "scratch-only; no canonical or trial-log write",
        },
        "fold_results": fold_results,
        "aggregate_degradation": _aggregate(fold_results),
        "warnings": sorted({warning for fold in fold_results for warning in fold["warnings"]}),
        "blockers": [],
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
    }
    report_path = output_dir / "walkforward_run_report.json"
    fragment_path = output_dir / "walkforward_dashboard_fragment.json"
    report_tmp = output_dir / ".walkforward_run_report.tmp.json"
    fragment_tmp = output_dir / ".walkforward_dashboard_fragment.tmp.json"
    _write_json(report_tmp, report)
    errors = validate_walkforward_run_reports(explicit_paths=[report_tmp])
    if errors:
        report_tmp.unlink(missing_ok=True)
        raise WalkForwardScratchError("generated report failed validation: " + "; ".join(errors))
    report_tmp.replace(report_path)
    report_ref = report_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    _write_json(fragment_tmp, _dashboard_fragment(report, report_ref))
    fragment_tmp.replace(fragment_path)
    return report_path, fragment_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--walkforward-manifest", required=True, type=Path)
    parser.add_argument("--ohlcv-input", required=True, type=Path)
    parser.add_argument("--strategy-spec", type=Path, default=DEFAULT_STRATEGY_SPEC)
    parser.add_argument("--variant-manifest", type=Path, default=DEFAULT_VARIANT_MANIFEST)
    parser.add_argument("--sweep-plan", type=Path, default=DEFAULT_SWEEP_PLAN)
    parser.add_argument("--d4-catalog-slice", type=Path, default=DEFAULT_D4_CATALOG)
    parser.add_argument("--d2-import-report", type=Path, default=DEFAULT_D2_IMPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--created-at-utc", required=True)
    parser.add_argument(
        "--sizing-mode",
        choices=runner.SIZING_MODES,
        default=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
    )
    parser.add_argument("--target-leverage", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report_path, fragment_path = run_walkforward_scratch(
            walkforward_manifest_path=args.walkforward_manifest,
            strategy_spec_path=args.strategy_spec,
            variant_manifest_path=args.variant_manifest,
            sweep_plan_path=args.sweep_plan,
            ohlcv_input_path=args.ohlcv_input,
            d4_catalog_slice_path=args.d4_catalog_slice,
            d2_import_report_path=args.d2_import_report,
            output_dir=args.output_dir,
            created_at_utc=args.created_at_utc,
            sizing_mode=args.sizing_mode,
            target_leverage=args.target_leverage,
        )
    except (WalkForwardScratchError, runner.OfflineSweepError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"OK: scratch walk-forward report written: {report_path}")
    print(f"OK: dashboard fragment written: {fragment_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
