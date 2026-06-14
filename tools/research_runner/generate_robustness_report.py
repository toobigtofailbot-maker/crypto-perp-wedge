"""Generate derived, non-authoritative robustness diagnostics for result populations."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_FIELDS = (
    "result_population_id",
    "lineage",
    "data_coverage_summary",
    "committed_denominator_snapshot",
    "outcome_category_counts",
    "variant_result_rows",
)

METRIC_KEYS = (
    "sharpe",
    "return_pct",
    "pnl",
    "drawdown",
    "trade_count",
    "win_rate",
    "fees",
    "funding",
    "slippage",
    "exposure",
)

MISSING_INPUTS = (
    "per-bar or per-period return series",
    "number of observations / effective sample length",
    "skewness",
    "kurtosis",
    "benchmark Sharpe",
    "annualization convention",
    "selection rule",
    "effective number of independent trials",
)

OOS_IS_EFFICIENCY_MISSING_INPUTS = (
    "walk-forward window rows",
    "in-sample Sharpe",
    "out-of-sample Sharpe",
    "positive finite in-sample Sharpe denominator",
)

TRIAL_LOG_REQUIRED_FIELDS = (
    "trial_id",
    "utc",
    "hypothesis_id",
    "config_sha256",
    "dataset_sha256",
    "params",
    "in_sample_sharpe",
    "oos_sharpe",
    "max_drawdown",
    "n_obs",
)

OUTCOME_KEYS = (
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
    "not_attempted",
    "counts_sum",
)


class RobustnessReportError(RuntimeError):
    """Raised when a result-population input cannot support a derived report."""


def _repo_relative_default_trial_log(input_path: Path) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    try:
        input_path.resolve().relative_to(repo_root)
    except ValueError:
        return Path("research/trial_log.jsonl")
    return repo_root / "research" / "trial_log.jsonl"


def _load_result_population(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RobustnessReportError(f"result_population file does not exist: {path}")
    if not path.is_file():
        raise RobustnessReportError(f"result_population path is not a file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RobustnessReportError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RobustnessReportError("result_population JSON must be an object")
    _validate_required_structure(payload)
    return payload


def _validate_required_structure(payload: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in payload]
    if missing:
        raise RobustnessReportError(f"missing required result_population fields: {', '.join(missing)}")

    if not isinstance(payload["lineage"], dict):
        raise RobustnessReportError("lineage must be an object")
    if not isinstance(payload["data_coverage_summary"], dict):
        raise RobustnessReportError("data_coverage_summary must be an object")
    if not isinstance(payload["committed_denominator_snapshot"], dict):
        raise RobustnessReportError("committed_denominator_snapshot must be an object")
    if not isinstance(payload["outcome_category_counts"], dict):
        raise RobustnessReportError("outcome_category_counts must be an object")
    if not isinstance(payload["variant_result_rows"], list):
        raise RobustnessReportError("variant_result_rows must be an array")

    denominator = payload["committed_denominator_snapshot"].get("committed_denominator")
    if not isinstance(denominator, int):
        raise RobustnessReportError(
            "committed_denominator_snapshot.committed_denominator must be an integer"
        )
    counts_sum = payload["outcome_category_counts"].get("counts_sum")
    if not isinstance(counts_sum, int):
        raise RobustnessReportError("outcome_category_counts.counts_sum must be an integer")


def _format_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        return f"{value:.12g}"
    if isinstance(value, (str, int, bool)):
        return str(value)
    return json.dumps(value, sort_keys=True)


def compute_oos_is_efficiency(in_sample_sharpe: Any, out_of_sample_sharpe: Any) -> dict[str, Any]:
    """Return descriptive OOS/IS Sharpe efficiency or missing-input warnings."""
    warnings: list[str] = []
    if not isinstance(in_sample_sharpe, (int, float)) or isinstance(in_sample_sharpe, bool):
        warnings.append("in_sample_sharpe_missing_or_non_numeric")
    if not isinstance(out_of_sample_sharpe, (int, float)) or isinstance(out_of_sample_sharpe, bool):
        warnings.append("out_of_sample_sharpe_missing_or_non_numeric")
    if warnings:
        return {"status": "missing_inputs", "value": None, "missing_input_warnings": warnings}

    is_value = float(in_sample_sharpe)
    oos_value = float(out_of_sample_sharpe)
    if not math.isfinite(is_value):
        warnings.append("in_sample_sharpe_non_finite")
    if not math.isfinite(oos_value):
        warnings.append("out_of_sample_sharpe_non_finite")
    if math.isfinite(is_value) and is_value <= 0.0:
        warnings.append("in_sample_sharpe_not_positive")
    if warnings:
        return {"status": "missing_inputs", "value": None, "missing_input_warnings": warnings}

    return {
        "status": "computed",
        "value": oos_value / is_value,
        "missing_input_warnings": [],
    }


def summarize_oos_is_efficiency(window_rows: list[Any] | None) -> dict[str, Any]:
    """Summarize descriptive OOS/IS efficiency from supplied walk-forward rows."""
    if not window_rows:
        return {
            "status": "withheld_missing_window_inputs",
            "metric": "out_of_sample_sharpe / in_sample_sharpe",
            "computed_count": 0,
            "values": [],
            "mean": None,
            "missing_input_warnings": list(OOS_IS_EFFICIENCY_MISSING_INPUTS),
            "authority": "descriptive_only_not_ranking_not_promotion",
        }

    values: list[float] = []
    warnings: list[str] = []
    for row in window_rows:
        if not isinstance(row, dict):
            warnings.append("window_row_not_object")
            continue
        if "oos_is_sharpe_efficiency" in row:
            value = row.get("oos_is_sharpe_efficiency")
            if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
                values.append(float(value))
            else:
                warnings.extend(row.get("missing_input_warnings", []) or ["oos_is_sharpe_efficiency_missing"])
            continue
        is_metrics = row.get("in_sample_metrics")
        oos_metrics = row.get("out_of_sample_metrics")
        if not isinstance(is_metrics, dict) or not isinstance(oos_metrics, dict):
            warnings.append("is_or_oos_metrics_missing")
            continue
        computed = compute_oos_is_efficiency(is_metrics.get("sharpe"), oos_metrics.get("sharpe"))
        if computed["status"] == "computed":
            values.append(float(computed["value"]))
        else:
            warnings.extend(computed["missing_input_warnings"])

    return {
        "status": "computed" if values else "withheld_missing_inputs",
        "metric": "out_of_sample_sharpe / in_sample_sharpe",
        "computed_count": len(values),
        "values": values,
        "mean": sum(values) / len(values) if values else None,
        "missing_input_warnings": sorted(set(warnings)),
        "authority": "descriptive_only_not_ranking_not_promotion",
    }


def _metric_summary(rows: list[Any]) -> list[str]:
    lines: list[str] = []
    lines.append("| variant_id | outcome | attempted | sharpe | return_pct | pnl | drawdown | trade_count |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _format_value(row.get("variant_id")),
                    _format_value(row.get("outcome_category")),
                    _format_value(row.get("attempted")),
                    _format_value(row.get("sharpe")),
                    _format_value(row.get("return_pct")),
                    _format_value(row.get("pnl")),
                    _format_value(row.get("drawdown")),
                    _format_value(row.get("trade_count")),
                ]
            )
            + " |"
        )
    return lines


def _available_metric_keys(rows: list[Any]) -> list[str]:
    available: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            continue
        for key in METRIC_KEYS:
            if key in metrics:
                available.add(key)
    return sorted(available)


def _load_trial_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "trial_log_path": path.as_posix(),
            "state": "missing",
            "trial_count_source": "missing_trial_log_file",
            "countable_trial_denominator": None,
            "valid_trial_rows": 0,
            "invalid_trial_rows": 0,
            "unique_trial_ids": 0,
            "duplicate_trial_ids": [],
            "hypothesis_counts": {},
            "n_obs_min": None,
            "n_obs_max": None,
            "missing_required_field_counts": {},
            "posture_notes": [
                "No trial-log denominator is available from the configured path.",
                "DSR and multiple-testing correction inputs remain incomplete.",
            ],
        }
    if not path.is_file():
        raise RobustnessReportError(f"trial_log path is not a file: {path}")

    valid_rows: list[dict[str, Any]] = []
    invalid_rows = 0
    missing_required_field_counts: dict[str, int] = {}
    seen_trial_ids: set[str] = set()
    duplicate_trial_ids: list[str] = []
    hypothesis_counts: dict[str, int] = {}
    n_obs_values: list[int] = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RobustnessReportError(
                f"invalid JSON in trial_log {path} line {line_number}: {exc}"
            ) from exc
        if not isinstance(row, dict):
            invalid_rows += 1
            continue

        missing = [field for field in TRIAL_LOG_REQUIRED_FIELDS if field not in row]
        if missing:
            invalid_rows += 1
            for field in missing:
                missing_required_field_counts[field] = (
                    missing_required_field_counts.get(field, 0) + 1
                )
            continue

        valid_rows.append(row)
        trial_id = row.get("trial_id")
        if isinstance(trial_id, str):
            if trial_id in seen_trial_ids:
                duplicate_trial_ids.append(trial_id)
            seen_trial_ids.add(trial_id)
        hypothesis_id = row.get("hypothesis_id")
        if isinstance(hypothesis_id, str):
            hypothesis_counts[hypothesis_id] = hypothesis_counts.get(hypothesis_id, 0) + 1
        n_obs = row.get("n_obs")
        if isinstance(n_obs, int):
            n_obs_values.append(n_obs)

    if not valid_rows and invalid_rows == 0:
        state = "present_empty"
    elif invalid_rows:
        state = "present_with_invalid_rows"
    else:
        state = "present"

    return {
        "trial_log_path": path.as_posix(),
        "state": state,
        "trial_count_source": "valid_rows_in_committed_trial_log_jsonl",
        "countable_trial_denominator": len(valid_rows),
        "valid_trial_rows": len(valid_rows),
        "invalid_trial_rows": invalid_rows,
        "unique_trial_ids": len(seen_trial_ids),
        "duplicate_trial_ids": duplicate_trial_ids,
        "hypothesis_counts": dict(sorted(hypothesis_counts.items())),
        "n_obs_min": min(n_obs_values) if n_obs_values else None,
        "n_obs_max": max(n_obs_values) if n_obs_values else None,
        "missing_required_field_counts": dict(sorted(missing_required_field_counts.items())),
        "posture_notes": [
            "The denominator is the full count of valid trial-log rows, not a winner-only or successful-only subset.",
            "The trial log does not expose failed, unavailable, aborted, or unlogged attempted trials beyond rows that exist in the JSONL file.",
            "Duplicate trial_id values, if present, are surfaced as diagnostics rather than silently removed from the denominator.",
        ],
    }


def _is_fixture_data(data: dict[str, Any]) -> bool:
    values: list[str] = []
    for key in ("data_catalog_ref", "data_slice_identity"):
        value = data.get(key)
        if isinstance(value, str):
            values.append(value)
    notes = data.get("data_coverage_notes")
    if isinstance(notes, list):
        values.extend(note for note in notes if isinstance(note, str))
    return any("fixture" in value.lower() or "not production data" in value.lower() for value in values)


def _data_posture(data: dict[str, Any]) -> str:
    if _is_fixture_data(data):
        return "fixture_only_pipeline_evidence"
    return "committed_offline_result_population_data_posture"


def _provenance_caveat(result_population_id: str, data: dict[str, Any]) -> str:
    if _is_fixture_data(data):
        return (
            f"{result_population_id} is fixture-based pipeline evidence, "
            "not strategy-quality evidence."
        )
    return (
        f"{result_population_id} is a committed offline result population; "
        "this derived diagnostic is descriptive only and does not claim strategy edge."
    )


def _extract_observed_summary(rows: list[Any]) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
        observed.append(
            {
                "variant_id": row.get("variant_id"),
                "outcome_category": row.get("outcome_category"),
                "attempted": row.get("attempted"),
                "sharpe": metrics.get("sharpe"),
                "return_pct": metrics.get("return_pct"),
                "pnl": metrics.get("pnl"),
                "drawdown": metrics.get("drawdown"),
                "trade_count": metrics.get("trade_count"),
            }
        )
    return observed


def build_diagnostic(payload: dict[str, Any], input_path: Path) -> dict[str, Any]:
    trial_log_path = _repo_relative_default_trial_log(input_path)
    return build_diagnostic_with_trial_log(payload, input_path, trial_log_path)


def build_diagnostic_with_trial_log(
    payload: dict[str, Any], input_path: Path, trial_log_path: Path
) -> dict[str, Any]:
    result_population_id = payload["result_population_id"]
    lineage = payload["lineage"]
    data = payload["data_coverage_summary"]
    denominator = payload["committed_denominator_snapshot"]
    counts = payload["outcome_category_counts"]
    rows = payload["variant_result_rows"]
    trial_log = _load_trial_log(trial_log_path)

    return {
        "report_identity": {
            "input_result_population_id": result_population_id,
            "input_path": input_path.as_posix(),
            "report_scope": "derived_non_authoritative_item6_robustness_reporting",
            "psr_status": "withheld_missing_inputs",
            "dsr_status": "withheld_missing_inputs",
            "min_trl_status": "withheld_missing_inputs",
        },
        "parent_lineage": {
            "strategy_spec_id": lineage.get("strategy_spec_id"),
            "variant_manifest_id": lineage.get("variant_manifest_id"),
            "sweep_plan_id": lineage.get("sweep_plan_id"),
            "result_population_id": lineage.get("result_population_id"),
            "complete_population_lineage_preserved": lineage.get(
                "complete_population_lineage_preserved"
            ),
        },
        "data_provenance": {
            "data_catalog_ref": data.get("data_catalog_ref"),
            "data_slice_identity": data.get("data_slice_identity"),
            "timeframe": data.get("timeframe"),
            "data_stream": data.get("data_stream"),
            "missing_data_policy": data.get("missing_data_policy"),
            "irreparable_gap_count": data.get("irreparable_gap_count"),
            "data_unavailable_count": data.get("data_unavailable_count"),
            "data_posture": _data_posture(data),
            "provenance_caveat": _provenance_caveat(result_population_id, data),
        },
        "committed_denominator_snapshot": {
            "committed_denominator": denominator.get("committed_denominator"),
            "outcome_counts_sum": denominator.get("outcome_counts_sum"),
            "result_row_count": denominator.get("result_row_count"),
            "denominator_basis": denominator.get("denominator_basis"),
            "denominator_policy": [
                "DSR and multiple-testing-aware metrics must use the committed denominator, not only successful variants.",
                "Failed, errored, invalid, excluded, filtered, data_unavailable, not_attempted, and aborted variants remain denominator members in future populations.",
                "No winner-only denominator.",
                "No executed-only denominator.",
            ],
        },
        "outcome_distribution": {key: counts.get(key) for key in OUTCOME_KEYS},
        "trial_accounting": trial_log,
        "available_metric_fields": _available_metric_keys(rows),
        "observed_summary": _extract_observed_summary(rows),
        "robustness_readiness_assessment": {
            "PSR": "withheld_missing_inputs; rigorous numeric PSR cannot be computed from the available result-population fields.",
            "DSR": "withheld_missing_inputs; rigorous numeric DSR cannot be computed from the available result-population fields.",
            "MinTRL": "withheld_missing_inputs; rigorous numeric MinTRL cannot be computed from the available result-population fields.",
            "numeric_values_emitted": False,
            "multiple_testing_inputs_present": {
                "committed_result_population_denominator": denominator.get("committed_denominator") is not None,
                "trial_log_denominator": trial_log["countable_trial_denominator"] is not None,
                "effective_independent_trial_count": False,
                "return_distribution_moments": False,
                "declared_selection_rule": False,
            },
        },
        "oos_is_efficiency": summarize_oos_is_efficiency(None),
        "missing_input_warnings": {item: "absent" for item in MISSING_INPUTS},
        "anti_overfit_threshold_definitions": {
            "committed_population_denominator": "Definition only: use the committed pre-registered population count recorded in the result population; do not shrink to convenient subsets.",
            "trial_log_denominator": "Definition only: use the full valid trial-log row count available at evaluation time when trial-log DSR posture is inspected.",
            "effective_independent_trials": "Definition only: required for rigorous DSR or multiple-testing correction, but not derivable from current result-population or trial-log fields alone.",
            "benchmark_sharpe": "Definition only: must be explicit before PSR, DSR, or MinTRL numeric computation.",
            "minimum_track_record_length": "Definition only: requires observation count, benchmark Sharpe, target confidence, frequency, and distribution assumptions before computation.",
        },
        "non_authority_declaration": [
            "derived report only",
            "derived diagnostic only",
            "not ranking authority",
            "not readiness authority",
            "not recommendation authority",
            "not promotion authority",
            "not transition authority",
            "not paper/live/runtime authority",
            "not gate authority",
            "not result-population mutation",
        ],
        "implementation_assumptions": [
            "The input result_population JSON is read-only and is not mutated.",
            "Existing committed result-population fields are used as descriptive facts only.",
            "Missing formula-critical inputs require withholding rigorous numeric PSR / DSR / MinTRL values.",
            "No schema, query-layer, validator, ranking, readiness, recommendation, promotion, transition, paper/live, or runtime authority is created.",
        ],
    }


def format_markdown(diagnostic: dict[str, Any]) -> str:
    identity = diagnostic["report_identity"]
    lineage = diagnostic["parent_lineage"]
    data = diagnostic["data_provenance"]
    denominator = diagnostic["committed_denominator_snapshot"]
    counts = diagnostic["outcome_distribution"]
    trial_log = diagnostic["trial_accounting"]
    rows = diagnostic["observed_summary"]
    missing = diagnostic["missing_input_warnings"]
    assessment = diagnostic["robustness_readiness_assessment"]
    oos_is_efficiency = diagnostic["oos_is_efficiency"]
    threshold_definitions = diagnostic["anti_overfit_threshold_definitions"]

    result_population_id = identity["input_result_population_id"]

    report_lines: list[str] = [
        f"# Item 6 Robustness Report - {result_population_id}",
        "",
        "Derived non-authoritative robustness diagnostic.",
        "",
        "## Report Identity",
        "",
        f"- input_result_population_id: {identity['input_result_population_id']}",
        f"- input_path: {identity['input_path']}",
        f"- report_scope: {identity['report_scope']}",
        f"- psr_status: {identity['psr_status']}",
        f"- dsr_status: {identity['dsr_status']}",
        f"- min_trl_status: {identity['min_trl_status']}",
        "",
        "## Parent Lineage",
        "",
        f"- strategy_spec_id: {_format_value(lineage.get('strategy_spec_id'))}",
        f"- variant_manifest_id: {_format_value(lineage.get('variant_manifest_id'))}",
        f"- sweep_plan_id: {_format_value(lineage.get('sweep_plan_id'))}",
        f"- result_population_id: {_format_value(lineage.get('result_population_id'))}",
        f"- complete_population_lineage_preserved: {_format_value(lineage.get('complete_population_lineage_preserved'))}",
        "",
        "## Data Provenance",
        "",
        f"- data_catalog_ref: {_format_value(data.get('data_catalog_ref'))}",
        f"- data_slice_identity: {_format_value(data.get('data_slice_identity'))}",
        f"- timeframe: {_format_value(data.get('timeframe'))}",
        f"- data_stream: {_format_value(data.get('data_stream'))}",
        f"- missing_data_policy: {_format_value(data.get('missing_data_policy'))}",
        f"- irreparable_gap_count: {_format_value(data.get('irreparable_gap_count'))}",
        f"- data_unavailable_count: {_format_value(data.get('data_unavailable_count'))}",
        f"- data_posture: {_format_value(data.get('data_posture'))}",
        f"- provenance_caveat: {_format_value(data.get('provenance_caveat'))}",
        "",
        "## Committed Denominator Snapshot",
        "",
        f"- committed_denominator: {_format_value(denominator.get('committed_denominator'))}",
        f"- outcome_counts_sum: {_format_value(denominator.get('outcome_counts_sum'))}",
        f"- result_row_count: {_format_value(denominator.get('result_row_count'))}",
        f"- denominator_basis: {_format_value(denominator.get('denominator_basis'))}",
        *(f"- {item}" for item in denominator["denominator_policy"]),
        "",
        "## Outcome Distribution",
        "",
    ]

    for key in OUTCOME_KEYS:
        report_lines.append(f"- {key}: {_format_value(counts.get(key))}")

    report_lines.extend(
        [
            "",
            "## Trial Accounting",
            "",
            f"- trial_log_path: {_format_value(trial_log.get('trial_log_path'))}",
            f"- trial_log_state: {_format_value(trial_log.get('state'))}",
            f"- trial_count_source: {_format_value(trial_log.get('trial_count_source'))}",
            f"- countable_trial_denominator: {_format_value(trial_log.get('countable_trial_denominator'))}",
            f"- valid_trial_rows: {_format_value(trial_log.get('valid_trial_rows'))}",
            f"- invalid_trial_rows: {_format_value(trial_log.get('invalid_trial_rows'))}",
            f"- unique_trial_ids: {_format_value(trial_log.get('unique_trial_ids'))}",
            f"- duplicate_trial_ids: {_format_value(trial_log.get('duplicate_trial_ids'))}",
            f"- hypothesis_counts: {_format_value(trial_log.get('hypothesis_counts'))}",
            f"- n_obs_min: {_format_value(trial_log.get('n_obs_min'))}",
            f"- n_obs_max: {_format_value(trial_log.get('n_obs_max'))}",
            f"- missing_required_field_counts: {_format_value(trial_log.get('missing_required_field_counts'))}",
            *(f"- {item}" for item in trial_log["posture_notes"]),
            "",
            "## Available Metric Summary",
            "",
            f"- available_metric_fields: {', '.join(diagnostic['available_metric_fields'])}",
            "",
            *_metric_summary(rows),
            "",
            "## PSR / DSR / MinTRL Readiness Assessment",
            "",
            f"- PSR: {assessment['PSR']}",
            f"- DSR: {assessment['DSR']}",
            f"- MinTRL: {assessment['MinTRL']}",
            f"- multiple_testing_inputs_present: {_format_value(assessment['multiple_testing_inputs_present'])}",
            "- No fabricated PSR, DSR, or MinTRL numeric values are emitted.",
            "",
            "## OOS / IS Efficiency",
            "",
            f"- status: {_format_value(oos_is_efficiency.get('status'))}",
            f"- metric: {_format_value(oos_is_efficiency.get('metric'))}",
            f"- computed_count: {_format_value(oos_is_efficiency.get('computed_count'))}",
            f"- mean: {_format_value(oos_is_efficiency.get('mean'))}",
            f"- missing_input_warnings: {_format_value(oos_is_efficiency.get('missing_input_warnings'))}",
            f"- authority: {_format_value(oos_is_efficiency.get('authority'))}",
            "",
            "## Missing Inputs",
            "",
        ]
    )

    report_lines.extend(f"- {item}: {status}" for item, status in missing.items())
    report_lines.extend(
        [
            "",
            "## Anti-Overfit Threshold Definitions",
            "",
            *(f"- {key}: {value}" for key, value in threshold_definitions.items()),
            "",
            "## Non-Authority Declaration",
            "",
            *(f"- {item}" for item in diagnostic["non_authority_declaration"]),
            f"- {data['provenance_caveat']}",
            "",
            "## Implementation Assumptions",
            "",
            *(f"- {item}" for item in diagnostic["implementation_assumptions"]),
            "",
        ]
    )
    return "\n".join(report_lines)


def generate_report(payload: dict[str, Any], input_path: Path) -> str:
    return format_markdown(build_diagnostic(payload, input_path))


def write_report(report: str, output_path: Path | None) -> None:
    if output_path is None:
        print(report, end="")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-population", type=Path, required=True)
    parser.add_argument("--trial-log", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)

    try:
        payload = _load_result_population(args.result_population)
        trial_log_path = args.trial_log or _repo_relative_default_trial_log(
            args.result_population
        )
        diagnostic = build_diagnostic_with_trial_log(
            payload, args.result_population, trial_log_path
        )
        if args.format == "json":
            report = json.dumps(diagnostic, indent=2, sort_keys=True) + "\n"
        else:
            report = format_markdown(diagnostic)
        write_report(report, args.output)
    except RobustnessReportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
