"""Non-canonical analytics metrics pilot over a committed Result Population fixture."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RP_FIXTURE = REPO_ROOT / "research/result_populations/RP-7134.result_population.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch/EXT-ANALYTICS-PILOT-01"

NON_CANONICAL_LABELS = [
    "NON-CANONICAL EXTERNAL ANALYTICS PILOT OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT SCREEN-GATE AUTHORITY",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT CANDIDATE EVIDENCE",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
]

UNSUPPORTED_ANNUALIZATION_NOTE = (
    "Unsupported for this pilot fixture: committed Result Population rows expose "
    "per-variant metrics, not a chronological strategy return series. The pilot "
    "does not invent an annualization or period assumption for row-level fixture data."
)


class AnalyticsPilotError(RuntimeError):
    """Raised when the non-canonical analytics pilot cannot run safely."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_payload(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_empyrical() -> Any | None:
    try:
        return importlib.import_module("empyrical")
    except Exception:
        return None


def _successful_rows(result_population: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in result_population.get("variant_result_rows", [])
        if row.get("outcome_category") == "successful" and row.get("attempted") is True
    ]
    if not rows:
        raise AnalyticsPilotError("Result Population fixture has no successful attempted rows")
    return sorted(rows, key=lambda row: row["variant_id"])


def _return_series_from_rows(rows: list[dict[str, Any]]) -> pd.Series:
    values = []
    index = []
    for row in rows:
        value = row.get("metrics", {}).get("return_pct")
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise AnalyticsPilotError(
                f"Row {row.get('row_id', '<unknown>')} lacks finite metrics.return_pct"
            )
        if float(value) <= -1.0:
            raise AnalyticsPilotError(
                f"Row {row.get('row_id', '<unknown>')} return_pct <= -1.0; "
                "row-level cumulative product would be degenerate"
            )
        values.append(float(value))
        index.append(row["variant_id"])
    return pd.Series(values, index=index, name="rp_variant_return_pct")


def _equity_from_returns(returns: pd.Series) -> pd.Series:
    values = [1.0]
    index = ["initial"]
    current = 1.0
    for label, value in returns.items():
        current *= 1.0 + float(value)
        values.append(current)
        index.append(str(label))
    return pd.Series(values, index=index, name="synthetic_variant_path_equity")


def _formula_cumulative_return(returns: pd.Series) -> float:
    return float((1.0 + returns.astype(float)).prod() - 1.0)


def _formula_max_drawdown_from_returns(returns: pd.Series) -> float:
    equity = _equity_from_returns(returns)
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return float(-drawdown.min())


def _formula_tail_ratio(returns: pd.Series) -> float | None:
    lower = float(returns.quantile(0.05))
    upper = float(returns.quantile(0.95))
    if lower == 0.0:
        return None
    return float(abs(upper / lower))


def _underwater_periods(returns: pd.Series) -> dict[str, Any]:
    equity = _equity_from_returns(returns)
    drawdown = (equity - equity.cummax()) / equity.cummax()
    runs = []
    current_start = None
    current_length = 0
    for label, value in drawdown.items():
        if float(value) < 0.0:
            if current_start is None:
                current_start = str(label)
            current_length += 1
        elif current_start is not None:
            runs.append(
                {
                    "start": current_start,
                    "end": str(label),
                    "length_observations": current_length,
                }
            )
            current_start = None
            current_length = 0
    if current_start is not None:
        runs.append(
            {
                "start": current_start,
                "end": str(drawdown.index[-1]),
                "length_observations": current_length,
            }
        )
    longest = max((run["length_observations"] for run in runs), default=0)
    return {
        "basis": "synthetic_variant_path_from_sorted_result_population_rows",
        "period_count": len(runs),
        "longest_period_observations": longest,
        "periods": runs,
    }


def _external_metrics(returns: pd.Series, empyrical_module: Any | None) -> dict[str, Any]:
    if empyrical_module is None:
        return {
            "engine": "empyrical",
            "available": False,
            "version": None,
            "metrics": {},
            "unavailable_reason": (
                "empyrical is not installed in the current repo environment and the repo has no "
                "non-runtime dependency group for this pilot; dependency files are unchanged."
            ),
        }
    metrics = {
        "cumulative_return": float(empyrical_module.cum_returns_final(returns)),
        "max_drawdown": abs(float(empyrical_module.max_drawdown(returns))),
    }
    if hasattr(empyrical_module, "tail_ratio"):
        tail_ratio = empyrical_module.tail_ratio(returns)
        metrics["tail_ratio"] = None if pd.isna(tail_ratio) else float(tail_ratio)
    return {
        "engine": "empyrical",
        "available": True,
        "version": getattr(empyrical_module, "__version__", "unknown"),
        "metrics": metrics,
        "unavailable_reason": None,
    }


def _comparison_rows(
    *,
    formula_metrics: dict[str, float | None],
    external: dict[str, Any],
    tolerance: float,
) -> list[dict[str, Any]]:
    rows = []
    external_metrics = external["metrics"]
    for metric_name in ("cumulative_return", "max_drawdown", "tail_ratio"):
        formula_value = formula_metrics.get(metric_name)
        external_value = external_metrics.get(metric_name)
        if not external["available"]:
            status = "external_unavailable"
            delta = None
        elif formula_value is None or external_value is None:
            status = "unsupported"
            delta = None
        else:
            delta = float(external_value) - float(formula_value)
            status = "matched" if abs(delta) <= tolerance else "mismatch"
        rows.append(
            {
                "metric_name": metric_name,
                "fixture_formula_value": formula_value,
                "external_value": external_value,
                "delta": delta,
                "tolerance": tolerance,
                "status": status,
                "notes": [],
            }
        )
    for metric_name in ("annualized_sharpe", "sortino", "calmar"):
        rows.append(
            {
                "metric_name": metric_name,
                "fixture_formula_value": None,
                "external_value": None,
                "delta": None,
                "tolerance": tolerance,
                "status": "unsupported",
                "notes": [UNSUPPORTED_ANNUALIZATION_NOTE],
            }
        )
    return rows


def _fixture_summary(
    result_population: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    metrics = [row["metrics"] for row in rows]
    return {
        "result_population_id": result_population["result_population_id"],
        "strategy_spec_id": result_population["lineage"]["strategy_spec_id"],
        "variant_manifest_id": result_population["lineage"]["variant_manifest_id"],
        "sweep_plan_id": result_population["lineage"]["sweep_plan_id"],
        "data_slice_identity": result_population["data_coverage_summary"]["data_slice_identity"],
        "timeframe": result_population["data_coverage_summary"]["timeframe"],
        "successful_attempted_rows": len(rows),
        "source_fields_used": [
            "variant_result_rows[].variant_id",
            "variant_result_rows[].metrics.return_pct",
            "variant_result_rows[].metrics.drawdown",
            "variant_result_rows[].metrics.sharpe",
            "variant_result_rows[].metrics.trade_count",
            "variant_result_rows[].metrics.win_rate",
            "variant_result_rows[].metrics.fees",
            "variant_result_rows[].metrics.funding",
            "variant_result_rows[].metrics.slippage",
        ],
        "row_metric_summary": {
            "mean_return_pct": float(pd.Series([item["return_pct"] for item in metrics]).mean()),
            "worst_row_drawdown": max(float(item["drawdown"]) for item in metrics),
            "mean_row_sharpe": float(pd.Series([item["sharpe"] for item in metrics]).mean()),
            "total_trade_count": int(sum(int(item["trade_count"]) for item in metrics)),
            "total_fees": float(sum(float(item["fees"]) for item in metrics)),
            "total_funding": float(sum(float(item["funding"]) for item in metrics)),
            "total_slippage": float(sum(float(item["slippage"]) for item in metrics)),
        },
    }


def _recommendation(external: dict[str, Any], comparisons: list[dict[str, Any]]) -> str:
    if not external["available"]:
        return "FORMULA_ADAPT_ONLY"
    mismatches = [row for row in comparisons if row["status"] == "mismatch"]
    if mismatches:
        return "EXPLORATION_ONLY"
    return "FORMULA_ADAPT_ONLY"


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# EXT-ANALYTICS-PILOT-01 Scratch Analytics Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Recommendation: `{report['recommendation']}`",
        f"Dependency mode: `{report['dependency_mode']}`",
        f"External engine available: `{report['external_engine']['available']}`",
        "",
        "## Fixture",
        "",
        f"- Result Population: `{report['fixture']['result_population_id']}`",
        f"- Strategy: `{report['fixture']['strategy_spec_id']}`",
        f"- VM: `{report['fixture']['variant_manifest_id']}`",
        f"- Sweep: `{report['fixture']['sweep_plan_id']}`",
        f"- Data slice: `{report['fixture']['data_slice_identity']}`",
        f"- Rows used: `{report['fixture']['successful_attempted_rows']}`",
        "",
        "## Metric Comparison",
        "",
        "| metric | formula value | external value | delta | status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["metric_comparison"]:
        lines.append(
            "| {metric_name} | {formula} | {external} | {delta} | {status} |".format(
                metric_name=row["metric_name"],
                formula=row["fixture_formula_value"],
                external=row["external_value"],
                delta=row["delta"],
                status=row["status"],
            )
        )
    lines.extend(
        [
            "",
            "## Unsupported Metrics",
            "",
            "- Annualized Sharpe, Sortino, and Calmar are not claimed for this fixture.",
            "- The committed RP fixture exposes per-variant result rows, not a "
            "chronological return series.",
            "- No canonical Result Population, Strategy Spec, Variant Manifest, "
            "Sweep Plan, or runtime artifact is written.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "metric_name",
        "fixture_formula_value",
        "external_value",
        "delta",
        "tolerance",
        "status",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["notes"] = "; ".join(row["notes"])
            writer.writerow(csv_row)


def build_report(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    empyrical_module: Any | None = None,
    load_external: bool = True,
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    result_population = _load_json(rp_fixture_path)
    rows = _successful_rows(result_population)
    returns = _return_series_from_rows(rows)
    formula_metrics = {
        "cumulative_return": _formula_cumulative_return(returns),
        "max_drawdown": _formula_max_drawdown_from_returns(returns),
        "tail_ratio": _formula_tail_ratio(returns),
    }
    if load_external and empyrical_module is None:
        empyrical_module = _load_empyrical()
    external = _external_metrics(returns, empyrical_module)
    comparisons = _comparison_rows(
        formula_metrics=formula_metrics,
        external=external,
        tolerance=tolerance,
    )
    dependency_mode = (
        "optional_empyrical_import"
        if external["available"]
        else "formula_adapter_only_no_repo_dependency_change"
    )
    report = {
        "labels": NON_CANONICAL_LABELS,
        "package": "EXT-ANALYTICS-PILOT-01",
        "dependency_mode": dependency_mode,
        "fixture": _fixture_summary(result_population, rows),
        "return_series_basis": (
            "successful Result Population rows sorted by variant_id; this is a deterministic "
            "fixture series for analytics formula comparison, not a chronological strategy "
            "return series"
        ),
        "external_engine": external,
        "formula_metrics": formula_metrics,
        "underwater_periods": _underwater_periods(returns),
        "metric_comparison": comparisons,
        "unsupported_metrics": [
            {
                "metric_name": "annualized_sharpe",
                "reason": UNSUPPORTED_ANNUALIZATION_NOTE,
            },
            {"metric_name": "sortino", "reason": UNSUPPORTED_ANNUALIZATION_NOTE},
            {"metric_name": "calmar", "reason": UNSUPPORTED_ANNUALIZATION_NOTE},
        ],
        "canonical_write": False,
        "runtime_paper_live_contact": False,
        "network_required": False,
        "recommendation": _recommendation(external, comparisons),
    }
    report["determinism_hash"] = _sha256_payload(report)
    return report


def run_pilot(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    empyrical_module: Any | None = None,
    load_external: bool = True,
) -> dict[str, Any]:
    report = build_report(
        rp_fixture_path=rp_fixture_path,
        empyrical_module=empyrical_module,
        load_external=load_external,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "analytics_report.json", report)
    (output_dir / "analytics_report.md").write_text(_markdown_report(report), encoding="utf-8")
    _write_csv(output_dir / "metric_comparison.csv", report["metric_comparison"])
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rp-fixture", type=Path, default=DEFAULT_RP_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--formula-only",
        action="store_true",
        help="Skip optional empyrical import and emit formula-adapter-only output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_pilot(
            rp_fixture_path=args.rp_fixture,
            output_dir=args.output_dir,
            load_external=not args.formula_only,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "labels": NON_CANONICAL_LABELS,
                "recommendation": report["recommendation"],
                "dependency_mode": report["dependency_mode"],
                "fixture": report["fixture"]["result_population_id"],
                "matched_metrics": [
                    row["metric_name"]
                    for row in report["metric_comparison"]
                    if row["status"] == "matched"
                ],
                "external_unavailable_metrics": [
                    row["metric_name"]
                    for row in report["metric_comparison"]
                    if row["status"] == "external_unavailable"
                ],
                "unsupported_metrics": [
                    row["metric_name"]
                    for row in report["metric_comparison"]
                    if row["status"] == "unsupported"
                ],
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
