"""Seeded non-canonical robustness diagnostics over Result Population rows."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-ROBUSTNESS-MC-PILOT-01"
DEFAULT_RP_FIXTURE = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_SEED = 20260618
DEFAULT_BOOTSTRAP_SAMPLES = 1000
DEFAULT_CONFIDENCE_LEVEL = 0.95

NON_CANONICAL_LABELS = [
    "NON-CANONICAL ROBUSTNESS / MONTE CARLO PILOT OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT SCREEN-GATE AUTHORITY",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT CANDIDATE EVIDENCE AUTHORITY",
    "NOT PROMOTION / READINESS AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    "PER-TRADE MONTE CARLO USES ONLY REAL PER-TRADE DATA IF AVAILABLE",
    "MISSING PER-TRADE DATA MUST BE REPORTED, NOT FABRICATED",
]

METRICS_TO_ATTEMPT = (
    "return_pct",
    "drawdown",
    "sharpe",
    "trade_count",
    "win_rate",
    "fees",
    "funding",
    "slippage",
)


class RobustnessMCPilotError(RuntimeError):
    """Raised when the pilot cannot run safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RobustnessMCPilotError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RobustnessMCPilotError(f"JSON root must be an object: {path}")
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


def _portable_report_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def _successful_rows(result_population: dict[str, Any]) -> list[dict[str, Any]]:
    rows = result_population.get("variant_result_rows")
    if not isinstance(rows, list):
        raise RobustnessMCPilotError("Result Population lacks variant_result_rows array")
    successful = [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("attempted") is True
        and row.get("outcome_category") == "successful"
    ]
    if not successful:
        raise RobustnessMCPilotError("Result Population fixture has no successful attempted rows")
    return sorted(successful, key=lambda row: str(row.get("variant_id", "")))


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values))


def _percentile(sorted_values: list[float], quantile: float) -> float:
    if not sorted_values:
        raise RobustnessMCPilotError("cannot compute percentile over empty values")
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[int(position)])
    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]
    return float(lower_value + (upper_value - lower_value) * (position - lower))


def _metric_values(rows: list[dict[str, Any]], metric_name: str) -> tuple[list[float], list[str]]:
    values: list[float] = []
    skipped_rows: list[str] = []
    for row in rows:
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            skipped_rows.append(str(row.get("row_id", row.get("variant_id", "<unknown>"))))
            continue
        number = _finite_number(metrics.get(metric_name))
        if number is None:
            skipped_rows.append(str(row.get("row_id", row.get("variant_id", "<unknown>"))))
            continue
        values.append(number)
    return values, skipped_rows


def _bootstrap_metric(
    *,
    metric_name: str,
    values: list[float],
    rng: random.Random,
    sample_count: int,
    confidence_level: float,
) -> tuple[dict[str, Any], list[float]]:
    samples: list[float] = []
    row_count = len(values)
    for _ in range(sample_count):
        sample = [values[rng.randrange(row_count)] for _ in range(row_count)]
        samples.append(_mean(sample))
    ordered = sorted(samples)
    alpha = 1.0 - confidence_level
    return (
        {
            "metric": metric_name,
            "row_count": row_count,
            "sample_count": sample_count,
            "observed_mean": _mean(values),
            "bootstrap_mean": _mean(samples),
            "ci_lower": _percentile(ordered, alpha / 2.0),
            "ci_upper": _percentile(ordered, 1.0 - alpha / 2.0),
            "confidence_level": confidence_level,
        },
        samples,
    )


def _bootstrap_diagnostics(
    *,
    rows: list[dict[str, Any]],
    seed: int,
    sample_count: int,
    confidence_level: float,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, list[float]]]:
    rng = random.Random(seed)
    diagnostics: dict[str, Any] = {}
    skipped: list[dict[str, Any]] = []
    all_samples: dict[str, list[float]] = {}
    for metric_name in METRICS_TO_ATTEMPT:
        values, skipped_rows = _metric_values(rows, metric_name)
        if not values:
            skipped.append(
                {
                    "metric": metric_name,
                    "reason": "no_finite_numeric_values",
                    "skipped_rows": skipped_rows,
                }
            )
            continue
        diagnostic, samples = _bootstrap_metric(
            metric_name=metric_name,
            values=values,
            rng=rng,
            sample_count=sample_count,
            confidence_level=confidence_level,
        )
        diagnostics[metric_name] = diagnostic
        all_samples[metric_name] = samples
        if skipped_rows:
            skipped.append(
                {
                    "metric": metric_name,
                    "reason": "some_rows_missing_or_non_finite",
                    "skipped_rows": skipped_rows,
                }
            )
    if not diagnostics:
        raise RobustnessMCPilotError("No finite RP row metrics are available for bootstrap")
    return diagnostics, skipped, all_samples


def _variant_manifest_path(result_population: dict[str, Any]) -> Path | None:
    manifest_id = result_population.get("lineage", {}).get("variant_manifest_id")
    if not isinstance(manifest_id, str):
        return None
    path = REPO_ROOT / "research" / "variant_manifests" / f"{manifest_id}.variant_manifest.json"
    return path if path.exists() else None


def _load_parameter_mapping(
    result_population: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[Path | None, dict[str, dict[str, Any]], str | None]:
    path = _variant_manifest_path(result_population)
    if path is None:
        return None, {}, "variant_manifest_not_found_from_rp_lineage"
    manifest = _load_json(path)
    assignments = manifest.get("variant_assignments")
    if not isinstance(assignments, list):
        return path, {}, "variant_manifest_lacks_variant_assignments"
    mapping: dict[str, dict[str, Any]] = {}
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        variant_id = assignment.get("variant_id")
        params = assignment.get("parameter_values")
        if isinstance(variant_id, str) and isinstance(params, dict):
            mapping[variant_id] = params
    missing = [str(row.get("variant_id")) for row in rows if row.get("variant_id") not in mapping]
    if missing:
        return path, {}, "missing_parameter_mapping_for_variants:" + ",".join(missing)
    return path, mapping, None


def _parameter_sensitivity(
    result_population: dict[str, Any],
    rows: list[dict[str, Any]],
    metrics_used: list[str],
) -> dict[str, Any]:
    path, mapping, unavailable_reason = _load_parameter_mapping(result_population, rows)
    if unavailable_reason is not None:
        return {
            "status": "insufficient_mapping",
            "source_path": _portable_report_path(path) if path else None,
            "reason": unavailable_reason,
            "authority": "advisory_only_not_ranking_not_gate",
        }

    parameter_names = sorted({name for params in mapping.values() for name in params})
    parameters: list[dict[str, Any]] = []
    for parameter_name in parameter_names:
        groups: dict[str, dict[str, Any]] = {}
        for row in rows:
            variant_id = str(row["variant_id"])
            value_key = str(mapping[variant_id][parameter_name])
            groups.setdefault(value_key, {"variant_ids": [], "metrics": {}})
            groups[value_key]["variant_ids"].append(variant_id)
            for metric_name in metrics_used:
                number = _finite_number(row.get("metrics", {}).get(metric_name))
                if number is None:
                    continue
                groups[value_key]["metrics"].setdefault(metric_name, []).append(number)
        value_summaries = []
        for value_key in sorted(groups):
            metric_summary = {
                metric_name: {
                    "mean": _mean(values),
                    "count": len(values),
                }
                for metric_name, values in sorted(groups[value_key]["metrics"].items())
                if values
            }
            value_summaries.append(
                {
                    "parameter_value": value_key,
                    "variant_ids": sorted(groups[value_key]["variant_ids"]),
                    "metrics": metric_summary,
                }
            )
        parameters.append(
            {
                "parameter_name": parameter_name,
                "value_count": len(value_summaries),
                "values": value_summaries,
            }
        )

    return {
        "status": "performed",
        "source_path": _portable_report_path(path) if path else None,
        "parameter_count": len(parameters),
        "parameters": parameters,
        "authority": "advisory_only_not_ranking_not_gate",
    }


def _trade_order_resampling() -> dict[str, Any]:
    return {
        "status": "PER_TRADE_DATA_MISSING",
        "performed": False,
        "source_path": None,
        "source_checksum": None,
        "finding": "PER_TRADE_DATA_MISSING",
        "reason": (
            "Committed Result Population rows expose aggregate per-variant metrics only; "
            "no real per-trade rows were found or supplied for this pilot."
        ),
        "fabricated_per_trade_data": False,
    }


def _empyrical_status() -> dict[str, Any]:
    try:
        module = importlib.import_module("empyrical")
    except Exception:
        return {
            "status": "unavailable",
            "available": False,
            "version": None,
            "mode": "repo_native_formula_mode",
            "note": "empyrical unavailable; repo-native formula mode used",
        }
    return {
        "status": "available_not_used_for_row_bootstrap",
        "available": True,
        "version": getattr(module, "__version__", "unknown"),
        "mode": "repo_native_formula_mode",
        "note": (
            "empyrical is available, but this pilot bootstraps aggregate RP row metrics; "
            "no chronological return-series comparison is semantically claimed."
        ),
    }


def _fixture_summary(path: Path, result_population: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    lineage = result_population.get("lineage", {})
    data = result_population.get("data_coverage_summary", {})
    return {
        "result_population_id": result_population.get("result_population_id"),
        "path": _portable_report_path(path),
        "checksum": _sha256_file(path),
        "row_count": len(rows),
        "strategy_spec_id": lineage.get("strategy_spec_id"),
        "variant_manifest_id": lineage.get("variant_manifest_id"),
        "sweep_plan_id": lineage.get("sweep_plan_id"),
        "data_slice_identity": data.get("data_slice_identity"),
        "timeframe": data.get("timeframe"),
        "source_fields_used": [
            "variant_result_rows[].variant_id",
            *[f"variant_result_rows[].metrics.{name}" for name in METRICS_TO_ATTEMPT],
        ],
    }


def build_report(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    seed: int = DEFAULT_SEED,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
) -> tuple[dict[str, Any], dict[str, list[float]]]:
    if bootstrap_samples <= 0:
        raise RobustnessMCPilotError("bootstrap_samples must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise RobustnessMCPilotError("confidence_level must be between 0 and 1")
    result_population = _load_json(rp_fixture_path)
    rows = _successful_rows(result_population)
    bootstrap_ci, skipped, samples = _bootstrap_diagnostics(
        rows=rows,
        seed=seed,
        sample_count=bootstrap_samples,
        confidence_level=confidence_level,
    )
    metrics_used = sorted(bootstrap_ci)
    samples_checksum = _sha256_payload(samples)
    report: dict[str, Any] = {
        "labels": NON_CANONICAL_LABELS,
        "package_id": PACKAGE_ID,
        "fixture": _fixture_summary(rp_fixture_path, result_population, rows),
        "input_checksum": _sha256_file(rp_fixture_path),
        "input_row_count": len(rows),
        "seed": seed,
        "bootstrap_sample_count": bootstrap_samples,
        "confidence_level": confidence_level,
        "metrics_used": metrics_used,
        "metrics_skipped": skipped,
        "bootstrap_ci": bootstrap_ci,
        "bootstrap_samples_checksum": samples_checksum,
        "trade_order_resampling": _trade_order_resampling(),
        "parameter_sensitivity": _parameter_sensitivity(result_population, rows, metrics_used),
        "optional_empyrical": _empyrical_status(),
        "jesse_concept_inspection": {
            "status": "not_inspected",
            "reason": "Jesse was not locally available or needed for this repo-native pilot.",
        },
        "decision_recommendation": "ADOPT_AS_ROBUSTNESS_LAYER",
        "next_gated_wp_suggestion": (
            "Narrow scratch-only per-trade distribution instrumentation design for committed RP lineage, "
            "without runner/backtester mutation unless separately authorized."
        ),
        "boundary_statement": {
            "canonical_result_population_write": False,
            "strategy_spec_vm_sweep_write": False,
            "runtime_paper_live_touched": False,
            "runner_backtester_touched": False,
            "screen_gate_authority_created": False,
            "promotion_readiness_authority_created": False,
            "candidate_evidence_authority_created": False,
            "fabricated_per_trade_data": False,
        },
    }
    report["output_checksum"] = _sha256_payload(report)
    return report, samples


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Scratch Robustness Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Recommendation: `{report['decision_recommendation']}`",
        f"Seed: `{report['seed']}`",
        f"Bootstrap samples: `{report['bootstrap_sample_count']}`",
        f"Confidence level: `{report['confidence_level']}`",
        f"Output checksum: `{report['output_checksum']}`",
        "",
        "## Fixture",
        "",
        f"- Result Population: `{report['fixture']['result_population_id']}`",
        f"- Path: `{report['fixture']['path']}`",
        f"- Checksum: `{report['fixture']['checksum']}`",
        f"- Rows used: `{report['fixture']['row_count']}`",
        f"- VM: `{report['fixture']['variant_manifest_id']}`",
        f"- Sweep: `{report['fixture']['sweep_plan_id']}`",
        "",
        "## Bootstrap Confidence Intervals",
        "",
        "| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric_name in report["metrics_used"]:
        row = report["bootstrap_ci"][metric_name]
        lines.append(
            "| {metric} | {observed_mean} | {bootstrap_mean} | {ci_lower} | {ci_upper} | {row_count} |".format(
                metric=metric_name,
                observed_mean=row["observed_mean"],
                bootstrap_mean=row["bootstrap_mean"],
                ci_lower=row["ci_lower"],
                ci_upper=row["ci_upper"],
                row_count=row["row_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Missing / Skipped Inputs",
            "",
            f"- Metrics skipped: `{report['metrics_skipped']}`",
            f"- Trade-order resampling: `{report['trade_order_resampling']['status']}`",
            f"- Parameter sensitivity: `{report['parameter_sensitivity']['status']}`",
            f"- Empyrical: `{report['optional_empyrical']['status']}`",
            f"- Jesse concept inspection: `{report['jesse_concept_inspection']['status']}`",
            "",
            "## Boundary",
            "",
            "- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.",
            "- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.",
            "",
        ]
    )
    return "\n".join(lines)


def run_pilot(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    seed: int = DEFAULT_SEED,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
) -> dict[str, Any]:
    report, _samples = build_report(
        rp_fixture_path=rp_fixture_path,
        seed=seed,
        bootstrap_samples=bootstrap_samples,
        confidence_level=confidence_level,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "robustness_report.json", report)
    (output_dir / "robustness_report.md").write_text(_markdown_report(report), encoding="utf-8")
    (output_dir / "bootstrap_samples.sha256").write_text(
        report["bootstrap_samples_checksum"] + "\n", encoding="utf-8"
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rp-fixture", type=Path, default=DEFAULT_RP_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--confidence-level", type=float, default=DEFAULT_CONFIDENCE_LEVEL)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_pilot(
            rp_fixture_path=args.rp_fixture,
            output_dir=args.output_dir,
            seed=args.seed,
            bootstrap_samples=args.bootstrap_samples,
            confidence_level=args.confidence_level,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "fixture": report["fixture"]["result_population_id"],
                "seed": report["seed"],
                "bootstrap_samples": report["bootstrap_sample_count"],
                "metrics_used": report["metrics_used"],
                "trade_order_resampling": report["trade_order_resampling"]["status"],
                "parameter_sensitivity": report["parameter_sensitivity"]["status"],
                "recommendation": report["decision_recommendation"],
                "output_checksum": report["output_checksum"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
