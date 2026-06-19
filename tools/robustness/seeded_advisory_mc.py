"""Seeded advisory robustness diagnostics over Result Population rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-INTEG-ROBUSTNESS-MC-01"
DEFAULT_RESULT_POPULATION = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_SEED = 20260619
DEFAULT_BOOTSTRAP_SAMPLES = 1000
DEFAULT_CONFIDENCE_LEVEL = 0.95

ADVISORY_LABELS = [
    "ADVISORY ROBUSTNESS / SEEDED MONTE CARLO OUTPUT",
    "NON-CANONICAL REPORT",
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
    "pnl",
    "drawdown",
    "sharpe",
    "trade_count",
    "win_rate",
    "fees",
    "funding",
    "slippage",
    "exposure",
)


class SeededAdvisoryMCError(RuntimeError):
    """Raised when advisory MC diagnostics cannot run safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SeededAdvisoryMCError(f"input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SeededAdvisoryMCError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SeededAdvisoryMCError(f"JSON root must be an object: {path}")
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


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def _mean(values: list[float]) -> float:
    if not values:
        raise SeededAdvisoryMCError("cannot compute mean over empty values")
    return float(sum(values) / len(values))


def _percentile(sorted_values: list[float], quantile: float) -> float:
    if not sorted_values:
        raise SeededAdvisoryMCError("cannot compute percentile over empty values")
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


def _validate_fixture(payload: dict[str, Any], input_path: Path) -> dict[str, Any]:
    required = ("result_population_id", "lineage", "data_coverage_summary", "variant_result_rows")
    missing = [field for field in required if field not in payload]
    if missing:
        raise SeededAdvisoryMCError(f"missing required Result Population fields: {', '.join(missing)}")
    if not isinstance(payload["lineage"], dict):
        raise SeededAdvisoryMCError("lineage must be an object")
    if not isinstance(payload["data_coverage_summary"], dict):
        raise SeededAdvisoryMCError("data_coverage_summary must be an object")
    if not isinstance(payload["variant_result_rows"], list):
        raise SeededAdvisoryMCError("variant_result_rows must be an array")

    rows = payload["variant_result_rows"]
    warnings: list[str] = []
    denominator = payload.get("committed_denominator_snapshot")
    if isinstance(denominator, dict):
        committed = denominator.get("committed_denominator")
        result_row_count = denominator.get("result_row_count")
        if isinstance(committed, int) and committed != len(rows):
            warnings.append("committed_denominator_differs_from_variant_result_rows_count")
        if isinstance(result_row_count, int) and result_row_count != len(rows):
            warnings.append("result_row_count_differs_from_variant_result_rows_count")
    else:
        warnings.append("committed_denominator_snapshot_missing")

    return {
        "status": "passed",
        "input_path": _repo_relative(input_path),
        "input_checksum": _sha256_file(input_path),
        "result_population_id": payload.get("result_population_id"),
        "row_count": len(rows),
        "warnings": warnings,
        "validation_scope": "advisory_fixture_shape_only",
    }


def _successful_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in payload["variant_result_rows"]
        if isinstance(row, dict)
        and row.get("attempted") is True
        and row.get("outcome_category") == "successful"
    ]
    if not rows:
        raise SeededAdvisoryMCError("Result Population has no successful attempted rows")
    return sorted(rows, key=lambda row: str(row.get("variant_id", row.get("row_id", ""))))


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
            "authority": "advisory_only_not_gate_not_ranking",
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
        raise SeededAdvisoryMCError("no finite Result Population row metrics are available")
    return diagnostics, skipped, all_samples


def _variant_manifest_path(payload: dict[str, Any]) -> Path | None:
    manifest_id = payload.get("lineage", {}).get("variant_manifest_id")
    if not isinstance(manifest_id, str):
        return None
    path = REPO_ROOT / "research" / "variant_manifests" / f"{manifest_id}.variant_manifest.json"
    return path if path.exists() else None


def _row_parameter_mapping(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for row in rows:
        variant_id = row.get("variant_id")
        params = row.get("parameter_values") or row.get("parameters")
        if isinstance(variant_id, str) and isinstance(params, dict):
            mapping[variant_id] = params
    return mapping


def _manifest_parameter_mapping(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[Path | None, dict[str, dict[str, Any]], str | None]:
    path = _variant_manifest_path(payload)
    if path is None:
        return None, {}, "variant_manifest_not_found_from_result_population_lineage"
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


def _load_parameter_mapping(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[str, Path | None, dict[str, dict[str, Any]], str | None]:
    row_mapping = _row_parameter_mapping(rows)
    if row_mapping and all(row.get("variant_id") in row_mapping for row in rows):
        return "variant_result_rows", None, row_mapping, None
    path, mapping, reason = _manifest_parameter_mapping(payload, rows)
    return "variant_manifest", path, mapping, reason


def _parameter_sensitivity(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
    metrics_used: list[str],
) -> dict[str, Any]:
    source_type, path, mapping, unavailable_reason = _load_parameter_mapping(payload, rows)
    if unavailable_reason is not None:
        return {
            "status": "insufficient_mapping",
            "source_type": source_type,
            "source_path": _repo_relative(path),
            "reason": unavailable_reason,
            "authority": "advisory_only_not_ranking_not_gate",
        }

    parameter_names = sorted({name for params in mapping.values() for name in params})
    parameters: list[dict[str, Any]] = []
    for parameter_name in parameter_names:
        groups: dict[str, dict[str, Any]] = {}
        for row in rows:
            variant_id = str(row["variant_id"])
            if parameter_name not in mapping[variant_id]:
                continue
            value_key = str(mapping[variant_id][parameter_name])
            groups.setdefault(value_key, {"variant_ids": [], "metrics": {}})
            groups[value_key]["variant_ids"].append(variant_id)
            metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
            for metric_name in metrics_used:
                number = _finite_number(metrics.get(metric_name))
                if number is not None:
                    groups[value_key]["metrics"].setdefault(metric_name, []).append(number)
        values: list[dict[str, Any]] = []
        for value_key in sorted(groups):
            metric_summary = {
                metric_name: {"mean": _mean(metric_values), "count": len(metric_values)}
                for metric_name, metric_values in sorted(groups[value_key]["metrics"].items())
                if metric_values
            }
            values.append(
                {
                    "parameter_value": value_key,
                    "variant_ids": sorted(groups[value_key]["variant_ids"]),
                    "metrics": metric_summary,
                }
            )
        parameters.append(
            {
                "parameter_name": parameter_name,
                "value_count": len(values),
                "values": values,
            }
        )

    return {
        "status": "performed",
        "source_type": source_type,
        "source_path": _repo_relative(path),
        "parameter_count": len(parameters),
        "parameters": parameters,
        "authority": "advisory_only_not_ranking_not_gate",
    }


def _per_trade_diagnostic() -> dict[str, Any]:
    return {
        "status": "QUEUE_PER_TRADE_INSTRUMENTATION",
        "performed": False,
        "source_path": None,
        "source_checksum": None,
        "finding": "PER_TRADE_DATA_MISSING",
        "reason": (
            "Committed Result Population rows expose aggregate per-variant metrics only; "
            "no real per-trade rows were found or supplied."
        ),
        "fabricated_per_trade_data": False,
        "follow_up_label": "QUEUE_PER_TRADE_INSTRUMENTATION",
    }


def _fixture_summary(input_path: Path, payload: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    lineage = payload.get("lineage", {})
    data = payload.get("data_coverage_summary", {})
    return {
        "result_population_id": payload.get("result_population_id"),
        "path": _repo_relative(input_path),
        "checksum": _sha256_file(input_path),
        "row_filter": "attempted_true_and_outcome_category_successful",
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
    result_population_path: Path = DEFAULT_RESULT_POPULATION,
    seed: int = DEFAULT_SEED,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
) -> tuple[dict[str, Any], dict[str, list[float]]]:
    if bootstrap_samples <= 0:
        raise SeededAdvisoryMCError("bootstrap_samples must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise SeededAdvisoryMCError("confidence_level must be between 0 and 1")

    payload = _load_json(result_population_path)
    fixture_validation = _validate_fixture(payload, result_population_path)
    rows = _successful_rows(payload)
    bootstrap_ci, metrics_skipped, samples = _bootstrap_diagnostics(
        rows=rows,
        seed=seed,
        sample_count=bootstrap_samples,
        confidence_level=confidence_level,
    )
    metrics_used = sorted(bootstrap_ci)
    report: dict[str, Any] = {
        "labels": ADVISORY_LABELS,
        "package_id": PACKAGE_ID,
        "report_type": "seeded_advisory_robustness_mc",
        "decision_label": "ADOPT_AS_ROBUSTNESS_LAYER",
        "fixture_validation": fixture_validation,
        "fixture": _fixture_summary(result_population_path, payload, rows),
        "seed": seed,
        "bootstrap_sample_count": bootstrap_samples,
        "confidence_level": confidence_level,
        "metrics_used": metrics_used,
        "metrics_skipped": metrics_skipped,
        "bootstrap_ci": bootstrap_ci,
        "bootstrap_samples_checksum": _sha256_payload(samples),
        "per_trade_monte_carlo": _per_trade_diagnostic(),
        "parameter_sensitivity": _parameter_sensitivity(payload, rows, metrics_used),
        "missing_data_notes": [
            "Only finite numeric values from existing Result Population row metrics are bootstrapped.",
            "Per-trade rows are not present in committed Result Populations and were not fabricated.",
            "The report is advisory and non-canonical; it is not a screen gate or promotion input by itself.",
        ],
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
        f"# {PACKAGE_ID} Seeded Advisory Robustness Report",
        "",
        *[f"- {label}" for label in ADVISORY_LABELS],
        "",
        f"Decision label: `{report['decision_label']}`",
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
        f"- Row filter: `{report['fixture']['row_filter']}`",
        f"- Variant Manifest: `{report['fixture']['variant_manifest_id']}`",
        f"- Sweep Plan: `{report['fixture']['sweep_plan_id']}`",
        f"- Fixture validation: `{report['fixture_validation']['status']}`",
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
            "## Missing / Queued Inputs",
            "",
            f"- Metrics skipped: `{report['metrics_skipped']}`",
            f"- Per-trade Monte Carlo: `{report['per_trade_monte_carlo']['status']}`",
            f"- Parameter sensitivity: `{report['parameter_sensitivity']['status']}`",
            "",
            "## Boundary",
            "",
            "- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.",
            "- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.",
            "- No per-trade data is fabricated.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    *,
    result_population_path: Path = DEFAULT_RESULT_POPULATION,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    seed: int = DEFAULT_SEED,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
) -> dict[str, Any]:
    report, _samples = build_report(
        result_population_path=result_population_path,
        seed=seed,
        bootstrap_samples=bootstrap_samples,
        confidence_level=confidence_level,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "seeded_advisory_mc_report.json", report)
    (output_dir / "seeded_advisory_mc_report.md").write_text(
        _markdown_report(report), encoding="utf-8"
    )
    (output_dir / "bootstrap_samples.sha256").write_text(
        report["bootstrap_samples_checksum"] + "\n", encoding="utf-8"
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-population", type=Path, default=DEFAULT_RESULT_POPULATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--confidence-level", type=float, default=DEFAULT_CONFIDENCE_LEVEL)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run(
            result_population_path=args.result_population,
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
                "result_population_id": report["fixture"]["result_population_id"],
                "seed": report["seed"],
                "bootstrap_samples": report["bootstrap_sample_count"],
                "metrics_used": report["metrics_used"],
                "per_trade_monte_carlo": report["per_trade_monte_carlo"]["status"],
                "parameter_sensitivity": report["parameter_sensitivity"]["status"],
                "decision_label": report["decision_label"],
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
