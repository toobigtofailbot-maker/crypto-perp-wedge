"""Advisory robustness-depth stress diagnostics over Result Population-style rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-LAB-ROBUSTNESS-DEPTH-01"
DEFAULT_RESULT_POPULATION = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_SEED = 1729

NON_AUTHORITY_FLAGS = [
    "advisory_only",
    "scratch_only",
    "non_canonical",
    "not_screen_gate",
    "not_promotion",
    "not_readiness",
    "not_candidate_evidence",
    "not_paper_live",
    "missing_inputs_not_fabricated",
]

STRESS_CONFIG = {
    "cost_fee_multipliers": [1.0, 1.25, 1.5, 2.0],
    "funding_multipliers": [1.0, 1.5, 2.0],
    "slippage_multipliers": [1.0, 1.25, 1.5, 2.0],
    "per_trade_bootstrap_samples": 250,
    "regime_label_fields": ["regime", "regime_label", "market_regime"],
    "stress_output_posture": "advisory_only_does_not_mutate_canonical_metrics",
}


class RobustnessDepthError(RuntimeError):
    """Raised when robustness-depth diagnostics cannot run safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RobustnessDepthError(f"input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RobustnessDepthError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RobustnessDepthError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_payload(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _sha256_bytes(data)


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_relative(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _run_git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def _percentile(sorted_values: list[float], quantile: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[int(position)])
    return float(sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (position - lower))


def _created_at(payload: dict[str, Any]) -> str:
    candidates = [
        payload.get("created_at_utc"),
        payload.get("created_at"),
        payload.get("audit_envelope", {}).get("created_at") if isinstance(payload.get("audit_envelope"), dict) else None,
        payload.get("validation_summary", {}).get("validation_timestamp")
        if isinstance(payload.get("validation_summary"), dict)
        else None,
    ]
    for value in candidates:
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _validate_result_population_shape(payload: dict[str, Any]) -> list[str]:
    required = ("result_population_id", "lineage", "data_coverage_summary", "variant_result_rows")
    missing = [field for field in required if field not in payload]
    if missing:
        raise RobustnessDepthError(f"missing required Result Population fields: {', '.join(missing)}")
    if not isinstance(payload["lineage"], dict):
        raise RobustnessDepthError("lineage must be an object")
    if not isinstance(payload["data_coverage_summary"], dict):
        raise RobustnessDepthError("data_coverage_summary must be an object")
    if not isinstance(payload["variant_result_rows"], list):
        raise RobustnessDepthError("variant_result_rows must be an array")
    warnings: list[str] = []
    denominator = payload.get("committed_denominator_snapshot")
    if isinstance(denominator, dict):
        committed = denominator.get("committed_denominator")
        row_count = denominator.get("result_row_count")
        if isinstance(committed, int) and committed != len(payload["variant_result_rows"]):
            warnings.append("committed_denominator_differs_from_variant_result_rows_count")
        if isinstance(row_count, int) and row_count != len(payload["variant_result_rows"]):
            warnings.append("result_row_count_differs_from_variant_result_rows_count")
    else:
        warnings.append("committed_denominator_snapshot_missing")
    return warnings


def _successful_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in payload["variant_result_rows"]
        if isinstance(row, dict)
        and row.get("attempted") is True
        and row.get("outcome_category") == "successful"
    ]
    if not rows:
        raise RobustnessDepthError("Result Population has no successful attempted rows")
    return sorted(rows, key=lambda row: str(row.get("variant_id", row.get("row_id", ""))))


def _row_ref(row: dict[str, Any]) -> str:
    return str(row.get("row_id", row.get("variant_id", "<unknown>")))


def _metric(row: dict[str, Any], metric_name: str) -> float | None:
    metrics = row.get("metrics")
    if not isinstance(metrics, dict):
        return None
    return _finite_number(metrics.get(metric_name))


def _implied_equity(row: dict[str, Any]) -> float | None:
    pnl = _metric(row, "pnl")
    return_pct = _metric(row, "return_pct")
    if pnl is None or return_pct is None or return_pct == 0.0:
        return None
    equity = pnl / return_pct
    return equity if math.isfinite(equity) and equity > 0 else None


def _summarize_stressed_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pnl_values = [_finite_number(row.get("stressed_pnl")) for row in rows]
    return_values = [_finite_number(row.get("stressed_return_pct")) for row in rows]
    pnl_values = [value for value in pnl_values if value is not None]
    return_values = [value for value in return_values if value is not None]
    return {
        "row_count": len(rows),
        "rows_with_stressed_pnl": len(pnl_values),
        "rows_with_stressed_return_pct": len(return_values),
        "mean_stressed_pnl": _mean(pnl_values),
        "mean_stressed_return_pct": _mean(return_values),
        "min_stressed_return_pct": min(return_values) if return_values else None,
        "max_stressed_return_pct": max(return_values) if return_values else None,
    }


def _stress_dimension(rows: list[dict[str, Any]], metric_name: str, multipliers: list[float]) -> tuple[dict[str, Any], list[str]]:
    missing_rows = [_row_ref(row) for row in rows if _metric(row, metric_name) is None]
    if len(missing_rows) == len(rows):
        return (
            {
                "status": "blocked_input_gap",
                "dimension": metric_name,
                "reason": f"no finite metrics.{metric_name} values available",
                "authority": "advisory_only_not_gate_not_canonical_mutation",
            },
            [f"variant_result_rows[].metrics.{metric_name}"],
        )

    scenarios: list[dict[str, Any]] = []
    for multiplier in multipliers:
        stressed_rows: list[dict[str, Any]] = []
        for row in rows:
            baseline_pnl = _metric(row, "pnl")
            baseline_return = _metric(row, "return_pct")
            observed_cost = _metric(row, metric_name)
            if baseline_pnl is None or observed_cost is None:
                continue
            additional_cost = abs(observed_cost) * (multiplier - 1.0)
            equity = _implied_equity(row)
            stressed_rows.append(
                {
                    "row_id": _row_ref(row),
                    "variant_id": row.get("variant_id"),
                    "observed_metric": observed_cost,
                    "additional_cost_native": additional_cost,
                    "baseline_pnl": baseline_pnl,
                    "stressed_pnl": baseline_pnl - additional_cost,
                    "baseline_return_pct": baseline_return,
                    "stressed_return_pct": None if equity is None or baseline_return is None else baseline_return - additional_cost / equity,
                }
            )
        scenarios.append(
            {
                "multiplier": multiplier,
                "summary": _summarize_stressed_rows(stressed_rows),
                "rows": stressed_rows,
            }
        )

    warnings = []
    if missing_rows:
        warnings.append({"reason": f"some_rows_missing_metrics.{metric_name}", "rows": missing_rows})
    finite_values = [_metric(row, metric_name) for row in rows if _metric(row, metric_name) is not None]
    if finite_values and all(value == 0.0 for value in finite_values):
        warnings.append({"reason": f"all_metrics.{metric_name}_values_are_zero", "rows": []})
    return (
        {
            "status": "exercised",
            "dimension": metric_name,
            "input_metric": f"variant_result_rows[].metrics.{metric_name}",
            "baseline_metrics_preserved": True,
            "stress_method": "subtract_additional_absolute_observed_cost_from_aggregate_pnl",
            "scenarios": scenarios,
            "warnings": warnings,
            "authority": "advisory_only_not_gate_not_canonical_mutation",
        },
        [],
    )


def _regime_label(row: dict[str, Any]) -> str | None:
    for field in STRESS_CONFIG["regime_label_fields"]:
        value = row.get(field)
        if isinstance(value, str) and value:
            return value
    data_coverage = row.get("data_coverage")
    if isinstance(data_coverage, dict):
        value = data_coverage.get("regime")
        if isinstance(value, str) and value:
            return value
    return None


def _regime_stress(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    labeled = [(row, _regime_label(row)) for row in rows]
    if not any(label for _row, label in labeled):
        return (
            {
                "status": "blocked_input_gap",
                "reason": "no real regime labels found on variant rows",
                "labels_checked": [*STRESS_CONFIG["regime_label_fields"], "data_coverage.regime"],
                "stress_method": "not_exercised_missing_regime_labels",
                "authority": "advisory_only_not_gate_not_canonical_mutation",
            },
            ["variant_result_rows[].regime_label_or_equivalent"],
        )

    groups: dict[str, list[dict[str, Any]]] = {}
    unlabeled_rows = []
    for row, label in labeled:
        if label is None:
            unlabeled_rows.append(_row_ref(row))
            continue
        groups.setdefault(label, []).append(row)

    summaries = []
    for label, group_rows in sorted(groups.items()):
        return_values = [_metric(row, "return_pct") for row in group_rows]
        drawdown_values = [_metric(row, "drawdown") for row in group_rows]
        return_values = [value for value in return_values if value is not None]
        drawdown_values = [value for value in drawdown_values if value is not None]
        summaries.append(
            {
                "regime": label,
                "row_count": len(group_rows),
                "variant_ids": [row.get("variant_id") for row in group_rows],
                "mean_return_pct": _mean(return_values),
                "min_return_pct": min(return_values) if return_values else None,
                "max_drawdown": max(drawdown_values) if drawdown_values else None,
            }
        )
    ordered_by_return = sorted(
        [item for item in summaries if item["mean_return_pct"] is not None],
        key=lambda item: float(item["mean_return_pct"]),
    )
    return (
        {
            "status": "exercised",
            "stress_method": "summarize_existing_rows_by_real_regime_label_only",
            "regime_count": len(summaries),
            "regime_summaries": summaries,
            "lowest_mean_return_regime": ordered_by_return[0]["regime"] if ordered_by_return else None,
            "unlabeled_rows": unlabeled_rows,
            "warnings": [] if not unlabeled_rows else [{"reason": "some_rows_missing_regime_labels", "rows": unlabeled_rows}],
            "authority": "advisory_only_not_gate_not_canonical_mutation",
        },
        [],
    )


def _trade_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    for field in ("per_trade_rows", "trade_rows", "trades"):
        value = payload.get(field)
        if isinstance(value, list):
            rows = [row for row in value if isinstance(row, dict)]
            return rows, field
    return [], None


def _trade_pnl(row: dict[str, Any]) -> float | None:
    for field in ("pnl", "realized_pnl", "net_pnl", "return_pct"):
        value = _finite_number(row.get(field))
        if value is not None:
            return value
    return None


def _per_trade_resampling(payload: dict[str, Any], seed: int) -> tuple[dict[str, Any], list[str]]:
    rows, source_field = _trade_rows(payload)
    if source_field is None:
        return (
            {
                "status": "unavailable_missing_per_trade_rows",
                "performed": False,
                "reason": "per-trade resampling not exercised",
                "future_input_schema_requirement": "provide real per_trade_rows/trade_rows/trades with finite pnl, realized_pnl, net_pnl, or return_pct",
                "fabricated_per_trade_data": False,
                "no_fabricated_trade_rows": True,
                "authority": "advisory_only_not_gate_not_canonical_mutation",
            },
            ["per_trade_rows"],
        )
    trade_values = [_trade_pnl(row) for row in rows]
    trade_values = [value for value in trade_values if value is not None]
    if not trade_values:
        return (
            {
                "status": "blocked_input_gap",
                "performed": False,
                "source_field": source_field,
                "reason": "per-trade rows exist but no finite trade pnl/return field was found",
                "future_input_schema_requirement": "provide finite pnl, realized_pnl, net_pnl, or return_pct per trade row",
                "fabricated_per_trade_data": False,
                "no_fabricated_trade_rows": True,
                "authority": "advisory_only_not_gate_not_canonical_mutation",
            },
            [f"{source_field}[].pnl_or_equivalent"],
        )

    rng = random.Random(seed)
    sample_count = int(STRESS_CONFIG["per_trade_bootstrap_samples"])
    samples = []
    for _ in range(sample_count):
        sample = [trade_values[rng.randrange(len(trade_values))] for _ in range(len(trade_values))]
        samples.append(sum(sample))
    ordered = sorted(samples)
    return (
        {
            "status": "available_and_exercised",
            "performed": True,
            "source_field": source_field,
            "trade_count": len(trade_values),
            "sample_count": sample_count,
            "observed_total": sum(trade_values),
            "bootstrap_total_mean": _mean(samples),
            "bootstrap_total_p05": _percentile(ordered, 0.05),
            "bootstrap_total_p50": _percentile(ordered, 0.50),
            "bootstrap_total_p95": _percentile(ordered, 0.95),
            "fabricated_per_trade_data": False,
            "no_fabricated_trade_rows": True,
            "authority": "advisory_only_not_gate_not_canonical_mutation",
        },
        [],
    )


def _input_refs(input_path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    lineage = payload.get("lineage", {}) if isinstance(payload.get("lineage"), dict) else {}
    return [
        {
            "ref_id": "result_population_or_fixture",
            "path": _repo_relative(input_path),
            "sha256": _sha256_file(input_path),
            "result_population_id": payload.get("result_population_id"),
        },
        {
            "ref_id": "lineage",
            "path": None,
            "strategy_spec_id": lineage.get("strategy_spec_id"),
            "variant_manifest_id": lineage.get("variant_manifest_id"),
            "sweep_plan_id": lineage.get("sweep_plan_id"),
        },
    ]


def build_report(
    *,
    result_population_path: Path = DEFAULT_RESULT_POPULATION,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    payload = _load_json(result_population_path)
    warnings = _validate_result_population_shape(payload)
    rows = _successful_rows(payload)
    cost_stress_results, cost_missing = _stress_dimension(rows, "fees", STRESS_CONFIG["cost_fee_multipliers"])
    funding_stress_results, funding_missing = _stress_dimension(rows, "funding", STRESS_CONFIG["funding_multipliers"])
    slippage_stress_results, slippage_missing = _stress_dimension(
        rows,
        "slippage",
        STRESS_CONFIG["slippage_multipliers"],
    )
    regime_stress_results, regime_missing = _regime_stress(rows)
    per_trade_resampling_status, per_trade_missing = _per_trade_resampling(payload, seed)

    missing_inputs = sorted(set(cost_missing + funding_missing + slippage_missing + regime_missing + per_trade_missing))
    exercised = [
        name
        for name, result in [
            ("cost", cost_stress_results),
            ("funding", funding_stress_results),
            ("slippage", slippage_stress_results),
            ("regime", regime_stress_results),
            ("per_trade_resampling", per_trade_resampling_status),
        ]
        if result.get("status") in {"exercised", "available_and_exercised"}
    ]
    report: dict[str, Any] = {
        "schema_version": "robustness_depth.v1",
        "package_id": PACKAGE_ID,
        "created_at_utc": _created_at(payload),
        "source_commit": _run_git("rev-parse", "HEAD"),
        "seed": seed,
        "input_refs": _input_refs(result_population_path, payload),
        "stress_config": STRESS_CONFIG,
        "dimensions_exercised": exercised,
        "cost_stress_results": cost_stress_results,
        "funding_stress_results": funding_stress_results,
        "slippage_stress_results": slippage_stress_results,
        "regime_stress_results": regime_stress_results,
        "per_trade_resampling_status": per_trade_resampling_status,
        "missing_inputs": missing_inputs,
        "warnings": warnings,
        "blockers": [],
        "non_authority_flags": NON_AUTHORITY_FLAGS,
        "recommendation_scope": "diagnostic_advisory_only_no_strategy_decision_no_gate_no_readiness_no_canonical_mutation",
        "canonical_artifact_mutation": False,
        "gate_or_readiness_authority_created": False,
    }
    report["output_checksum"] = _sha256_payload(report)
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    per_trade = report["per_trade_resampling_status"]
    lines = [
        f"# {PACKAGE_ID} Advisory Robustness Depth Report",
        "",
        "## Boundary",
        "",
        "- Advisory only; scratch only; non-canonical.",
        "- No screen-gate, promotion, readiness, candidate-evidence, paper/live, or runtime authority is created.",
        "- Missing inputs are reported and not fabricated.",
        "",
        "## Inputs",
        "",
        f"- Source commit: `{report['source_commit']}`",
        f"- Seed: `{report['seed']}`",
        f"- Input: `{report['input_refs'][0]['path']}`",
        f"- Input checksum: `{report['input_refs'][0]['sha256']}`",
        "",
        "## Stress Dimensions",
        "",
        f"- Exercised: `{', '.join(report['dimensions_exercised']) if report['dimensions_exercised'] else 'none'}`",
        f"- Cost stress: `{report['cost_stress_results']['status']}`",
        f"- Funding stress: `{report['funding_stress_results']['status']}`",
        f"- Slippage stress: `{report['slippage_stress_results']['status']}`",
        f"- Regime stress: `{report['regime_stress_results']['status']}`",
        f"- Per-trade resampling: `{per_trade['status']}`",
        "",
        "## Missing Inputs",
        "",
        f"- Missing inputs: `{report['missing_inputs']}`",
        f"- Per-trade note: `{per_trade.get('reason')}`",
        f"- Future per-trade requirement: `{per_trade.get('future_input_schema_requirement')}`",
        f"- No fabricated trade rows: `{per_trade.get('no_fabricated_trade_rows')}`",
        "",
        "## Conclusion",
        "",
        f"- Canonical artifact mutated: `{report['canonical_artifact_mutation']}`",
        f"- Gate/readiness authority created: `{report['gate_or_readiness_authority_created']}`",
        f"- Output checksum: `{report['output_checksum']}`",
        "",
    ]
    return "\n".join(lines)


def _provenance(report: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    return {
        "package_id": PACKAGE_ID,
        "source_commit": report["source_commit"],
        "source_branch": _run_git("branch", "--show-current"),
        "output_dir": _repo_relative(output_dir),
        "report_json": _repo_relative(output_dir / "robustness_depth_report.json"),
        "report_markdown": _repo_relative(output_dir / "robustness_depth_report.md"),
        "report_checksum": report["output_checksum"],
        "canonical_artifact_mutation": False,
        "runtime_paper_live_touched": False,
        "runner_backtester_touched": False,
        "dependency_files_touched": False,
    }


def run(
    *,
    result_population_path: Path = DEFAULT_RESULT_POPULATION,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    report = build_report(result_population_path=result_population_path, seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "robustness_depth_report.json", report)
    (output_dir / "robustness_depth_report.md").write_text(_markdown_report(report), encoding="utf-8")
    _write_json(output_dir / "provenance.json", _provenance(report, output_dir))
    (output_dir / "README.md").write_text(
        "\n".join(
            [
                f"# {PACKAGE_ID}",
                "",
                "Scratch-only advisory robustness-depth outputs.",
                "",
                "These files are non-canonical diagnostics. They create no screen-gate, promotion, readiness, candidate-evidence, paper/live, or runtime authority.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-population", type=Path, default=DEFAULT_RESULT_POPULATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run(
            result_population_path=args.result_population,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "result_population_id": report["input_refs"][0]["result_population_id"],
                "seed": report["seed"],
                "dimensions_exercised": report["dimensions_exercised"],
                "per_trade_resampling_status": report["per_trade_resampling_status"]["status"],
                "missing_inputs": report["missing_inputs"],
                "output_checksum": report["output_checksum"],
                "output_dir": _repo_relative(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
