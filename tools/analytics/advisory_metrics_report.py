"""Generate a repo-native advisory analytics report over committed fixture evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-INTEG-ANALYTICS-METRICS-01"
DEFAULT_RP_FIXTURE = REPO_ROOT / "research/result_populations/RP-7134.result_population.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DECISION_LABEL = "FORMULA_ADAPT_REPO_NATIVE"

ADVISORY_LABELS = [
    "ADVISORY ANALYTICS OUTPUT",
    "NOT A SCREEN GATE",
    "NOT CANDIDATE READINESS",
    "NOT PROMOTION AUTHORITY",
    "NOT RUNTIME/PAPER/LIVE AUTHORITY",
]

PATH_METRICS = [
    "total_return",
    "max_drawdown",
    "drawdown_episodes",
    "underwater_curve",
    "rolling_return",
    "rolling_volatility",
    "rolling_drawdown",
    "calmar_style",
    "worst_period",
    "period_downside_summary",
]


class AdvisoryReportError(RuntimeError):
    """Raised when the advisory report fixture is invalid."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _sha256_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return "external:" + path.name


def _load_fixture(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AdvisoryReportError(f"input file does not exist: {_repo_relative(path)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdvisoryReportError(f"input is not readable JSON: {_repo_relative(path)}") from exc
    required = {"result_population_id", "lineage", "data_coverage_summary", "variant_result_rows"}
    missing = sorted(required - set(payload))
    if missing:
        raise AdvisoryReportError(f"missing required Result Population fields: {missing}")
    return payload


def _successful_attempted_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in payload["variant_result_rows"]
        if row.get("attempted") is True and row.get("outcome_category") == "successful"
    ]
    if not rows:
        raise AdvisoryReportError("Result Population has no successful attempted rows")
    return rows


def _finite_metric(rows: list[dict[str, Any]], metric: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get("metrics", {}).get(metric)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            values.append(float(value))
    return values


def _cross_sectional_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    returns = _finite_metric(rows, "return_pct")
    drawdowns = _finite_metric(rows, "drawdown")
    downside = [value for value in returns if value < 0.0]
    return {
        "basis": "successful attempted Result Population rows; aggregate variants, not periods",
        "row_count": len(rows),
        "return_pct": {
            "available_row_count": len(returns),
            "minimum": min(returns) if returns else None,
            "maximum": max(returns) if returns else None,
            "mean": sum(returns) / len(returns) if returns else None,
            "negative_row_count": len(downside),
            "negative_row_frequency": len(downside) / len(returns) if returns else None,
            "mean_negative_row_return": sum(downside) / len(downside) if downside else None,
        },
        "drawdown": {
            "available_row_count": len(drawdowns),
            "minimum": min(drawdowns) if drawdowns else None,
            "maximum": max(drawdowns) if drawdowns else None,
            "mean": sum(drawdowns) / len(drawdowns) if drawdowns else None,
        },
    }


def build_report(*, result_population_path: Path = DEFAULT_RP_FIXTURE) -> dict[str, Any]:
    """Build an advisory report without treating aggregate rows as a time series."""

    payload = _load_fixture(result_population_path)
    rows = _successful_attempted_rows(payload)
    lineage = payload["lineage"]
    coverage = payload["data_coverage_summary"]
    unavailable_reason = (
        "The committed Result Population exposes aggregate per-variant metrics, not a "
        "chronological equity or return series. No variant ordering, return path, period "
        "frequency, rolling window, or annualization assumption is invented."
    )
    report: dict[str, Any] = {
        "package_id": PACKAGE_ID,
        "decision_label": DECISION_LABEL,
        "labels": ADVISORY_LABELS,
        "fixture": {
            "path": _repo_relative(result_population_path),
            "sha256": _sha256_file(result_population_path),
            "result_population_id": payload["result_population_id"],
            "strategy_spec_id": lineage.get("strategy_spec_id"),
            "variant_manifest_id": lineage.get("variant_manifest_id"),
            "sweep_plan_id": lineage.get("sweep_plan_id"),
            "data_slice_identity": coverage.get("data_slice_identity"),
            "timeframe": coverage.get("timeframe"),
            "successful_attempted_rows": len(rows),
        },
        "input_classification": {
            "chronological_equity_available": False,
            "chronological_returns_available": False,
            "aggregate_variant_metrics_available": True,
            "periods_per_year_available": False,
        },
        "path_metrics": {
            metric: {"available": False, "value": None, "reason": unavailable_reason}
            for metric in PATH_METRICS
        },
        "cross_sectional_variant_summary": _cross_sectional_summary(rows),
        "formula_surface": {
            "module": "tools.analytics.advisory_metrics",
            "requires_real_chronological_input": True,
            "supported": [
                "equity_and_return_normalization",
                "maximum_drawdown_and_episode_decomposition",
                "underwater_curve",
                "rolling_return_volatility_drawdown",
                "calmar_style",
                "worst_period_and_downside_tail_summary",
            ],
        },
        "provenance": {
            "source_type": "committed_result_population_fixture",
            "network_required": False,
            "external_dependency_required": False,
            "canonical_write": False,
            "report_scope": "advisory_only",
        },
    }
    report["report_checksum"] = _sha256_payload(report)
    return report


def _markdown(report: dict[str, Any]) -> str:
    summary = report["cross_sectional_variant_summary"]
    lines = [
        f"# {PACKAGE_ID} Advisory Analytics Report",
        "",
        *[f"- {label}" for label in ADVISORY_LABELS],
        "",
        f"Decision label: `{report['decision_label']}`",
        f"Report checksum: `{report['report_checksum']}`",
        "",
        "## Provenance",
        "",
        f"- Fixture: `{report['fixture']['path']}`",
        f"- Fixture SHA256: `{report['fixture']['sha256']}`",
        f"- Result Population: `{report['fixture']['result_population_id']}`",
        f"- Successful attempted rows: `{report['fixture']['successful_attempted_rows']}`",
        "",
        "## Metric Availability",
        "",
        "All path-dependent metrics are unavailable for this fixture. The committed Result "
        "Population contains aggregate variant rows, not a chronological equity or return series. "
        "No return path or annualization assumption is fabricated.",
        "",
        "Unavailable: " + ", ".join(f"`{name}`" for name in PATH_METRICS) + ".",
        "",
        "## Cross-sectional Variant Summary",
        "",
        "This is a descriptive aggregate across successful attempted variants. It is not a "
        "period-return tail analysis, ranking, screen gate, readiness decision, or promotion signal.",
        "",
        f"- Return rows: `{summary['return_pct']['available_row_count']}`",
        f"- Minimum row return: `{summary['return_pct']['minimum']}`",
        f"- Negative row count: `{summary['return_pct']['negative_row_count']}`",
        f"- Drawdown rows: `{summary['drawdown']['available_row_count']}`",
        f"- Maximum row drawdown: `{summary['drawdown']['maximum']}`",
        "",
    ]
    return "\n".join(lines)


def run(
    *,
    result_population_path: Path = DEFAULT_RP_FIXTURE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    report = build_report(result_population_path=result_population_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "advisory_analytics_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "advisory_analytics_report.md").write_text(
        _markdown(report), encoding="utf-8"
    )
    (output_dir / "advisory_analytics_report.sha256").write_text(
        report["report_checksum"] + "\n", encoding="utf-8"
    )
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-population", type=Path, default=DEFAULT_RP_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = run(
            result_population_path=args.result_population,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "decision_label": report["decision_label"],
                "fixture": report["fixture"]["result_population_id"],
                "path_metrics_available": False,
                "report_checksum": report["report_checksum"],
                "output_dir": _repo_relative(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
