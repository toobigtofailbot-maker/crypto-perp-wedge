"""Generate repo-native purged/embargoed walk-forward fold manifests.

This helper writes scratch/non-canonical manifest artifacts only. It does not
change the walk-forward schema, validators, runner semantics, result
populations, trial log, or any runtime/paper/live path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.registry.validate_walkforward_fold_manifest import (
    validate_walkforward_fold_manifests,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "scratch" / "WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01" / "purged_fold_manifest.json"
DEFAULT_CREATED_AT_UTC = "2026-06-20T12:00:00Z"
DEFAULT_TIMEFRAME = "15m"
DEFAULT_START_UTC = "2022-01-01T00:00:00Z"
DEFAULT_SELECTION_BARS = 35_040
DEFAULT_EVALUATION_BARS = 8_640
DEFAULT_PURGE_BARS = 96
DEFAULT_EMBARGO_BARS = 32
DEFAULT_FOLD_COUNT = 2
DEFAULT_DECLARED_VARIANT_COUNT = 8
NON_AUTHORITY_DECLARATION = {
    "not_executable": True,
    "not_runner_authority": True,
    "not_result_population_write_authority": True,
    "not_canonical_result_population": True,
    "not_candidate_approval": True,
    "not_ranking_authority": True,
    "not_recommendation_authority": True,
    "not_readiness_authority": True,
    "not_promotion_authority": True,
    "not_gate_authority": True,
    "not_runtime_authority": True,
    "not_paper_live_authority": True,
    "not_broker_exchange_order_authority": True,
}


class PurgedFoldError(ValueError):
    """Raised when purged/embargo fold construction is invalid."""


@dataclass(frozen=True)
class PurgedFoldConfig:
    manifest_id: str
    created_at_utc: str
    strategy_spec_id: str
    variant_manifest_id: str
    sweep_plan_id: str
    data_slice_id: str
    timeframe: str
    start_utc: str
    selection_bars: int
    evaluation_bars: int
    purge_bars: int
    embargo_bars: int
    fold_count: int
    declared_variant_count: int


def _parse_utc(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PurgedFoldError(f"{label} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise PurgedFoldError(f"{label} must be UTC")
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _bar_delta(timeframe: str) -> timedelta:
    mapping = {
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
    }
    try:
        return mapping[timeframe]
    except KeyError as exc:
        raise PurgedFoldError(f"unsupported timeframe: {timeframe}") from exc


def _require_non_negative_int(value: int, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PurgedFoldError(f"{label} must be a non-negative integer")


def _require_positive_int(value: int, label: str) -> None:
    _require_non_negative_int(value, label)
    if value == 0:
        raise PurgedFoldError(f"{label} must be greater than zero")


def _source_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _hash_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _lineage_refs() -> list[dict[str, str]]:
    return [
        {
            "ref_id": "spec",
            "ref_type": "strategy_spec",
            "ref": "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json",
        },
        {
            "ref_id": "vm",
            "ref_type": "variant_manifest",
            "ref": "research/variant_manifests/VM-0004.variant_manifest.json",
        },
        {
            "ref_id": "sweep",
            "ref_type": "sweep_plan",
            "ref": "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json",
        },
        {
            "ref_id": "rp-comparator",
            "ref_type": "result_population",
            "ref": "research/result_populations/RP-2592.result_population.json",
        },
    ]


def _gap_posture() -> dict[str, Any]:
    return {
        "missing_data_policy": "mark_data_unavailable",
        "irreparable_gap_policy": "consult_irreparable_gaps_manifest",
        "silent_interpolation_forbidden": True,
    }


def _validate_config(config: PurgedFoldConfig) -> None:
    _parse_utc(config.created_at_utc, "created_at_utc")
    _parse_utc(config.start_utc, "start_utc")
    _bar_delta(config.timeframe)
    _require_positive_int(config.selection_bars, "selection_bars")
    _require_positive_int(config.evaluation_bars, "evaluation_bars")
    _require_non_negative_int(config.purge_bars, "purge_bars")
    _require_non_negative_int(config.embargo_bars, "embargo_bars")
    _require_positive_int(config.fold_count, "fold_count")
    _require_positive_int(config.declared_variant_count, "declared_variant_count")
    if config.selection_bars <= config.purge_bars:
        raise PurgedFoldError("selection_bars must be greater than purge_bars")


def build_purged_manifest_and_comparison(
    config: PurgedFoldConfig,
    *,
    source_commit: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a schema-compatible fold manifest and naive-vs-purged comparison."""
    _validate_config(config)
    commit = source_commit or _source_commit()
    bar = _bar_delta(config.timeframe)
    start = _parse_utc(config.start_utc, "start_utc")

    folds: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    previous_evaluation_end: datetime | None = None
    block_start = start

    for index in range(config.fold_count):
        fold_order = index + 1
        fold_id = f"FOLD-{fold_order:03d}"
        naive_selection_start = block_start
        naive_selection_end = naive_selection_start + bar * config.selection_bars
        evaluation_start = naive_selection_end
        evaluation_end = evaluation_start + bar * config.evaluation_bars

        min_selection_start = naive_selection_start
        if previous_evaluation_end is not None:
            min_selection_start = max(
                min_selection_start,
                previous_evaluation_end + bar * config.embargo_bars,
            )
        selection_start = min_selection_start
        selection_end = evaluation_start - bar * config.purge_bars
        if selection_start >= selection_end:
            raise PurgedFoldError(
                f"{fold_id} invalid purged selection window: "
                f"{_format_utc(selection_start)} >= {_format_utc(selection_end)}"
            )

        purged_selection_bars = int((selection_end - selection_start) / bar)
        selection_bars_removed = config.selection_bars - purged_selection_bars
        folds.append(
            {
                "fold_id": fold_id,
                "fold_order": fold_order,
                "selection_window_start_utc": _format_utc(selection_start),
                "selection_window_end_utc": _format_utc(selection_end),
                "evaluation_window_start_utc": _format_utc(evaluation_start),
                "evaluation_window_end_utc": _format_utc(evaluation_end),
                "warmup_window_start_utc": None,
                "warmup_window_end_utc": None,
                "purge": {"mode": "bars", "bars": config.purge_bars, "duration": None},
                "embargo": {"mode": "bars", "bars": config.embargo_bars, "duration": None},
                "result_population_ref": None,
                "planned_result_population_ref": f"scratch:not-created:{config.manifest_id}:{fold_id}",
                "declared_variant_count": config.declared_variant_count,
                "successful_count": None,
                "failed_count": None,
                "errored_count": None,
                "invalid_count": None,
                "data_unavailable_count": None,
                "not_attempted_count": None,
                "gap_posture": _gap_posture(),
                "lineage_refs": _lineage_refs(),
            }
        )
        comparison_rows.append(
            {
                "fold_id": fold_id,
                "fold_order": fold_order,
                "naive_selection_start_utc": _format_utc(naive_selection_start),
                "naive_selection_end_utc": _format_utc(naive_selection_end),
                "purged_selection_start_utc": _format_utc(selection_start),
                "purged_selection_end_utc": _format_utc(selection_end),
                "evaluation_start_utc": _format_utc(evaluation_start),
                "evaluation_end_utc": _format_utc(evaluation_end),
                "naive_selection_bars": config.selection_bars,
                "purged_selection_bars": purged_selection_bars,
                "selection_bars_removed": selection_bars_removed,
                "purge_gap_bars": config.purge_bars,
                "embargo_bars_after_previous_evaluation": (
                    0 if previous_evaluation_end is None else config.embargo_bars
                ),
            }
        )
        previous_evaluation_end = evaluation_end
        block_start = evaluation_end

    manifest = {
        "schema_version": "v1",
        "manifest_id": config.manifest_id,
        "created_at_utc": config.created_at_utc,
        "source_commit": commit,
        "non_authority_declaration": dict(NON_AUTHORITY_DECLARATION),
        "strategy_spec_id": config.strategy_spec_id,
        "variant_manifest_id": config.variant_manifest_id,
        "sweep_plan_id": config.sweep_plan_id,
        "data_slice_id": config.data_slice_id,
        "timeframe": config.timeframe,
        "timezone": "UTC",
        "boundary_semantics": "start_inclusive_end_exclusive",
        "window_policy": {
            "policy_id": (
                f"purged_embargoed_explicit_{config.timeframe}_"
                f"sel{config.selection_bars}_eval{config.evaluation_bars}_"
                f"purge{config.purge_bars}_embargo{config.embargo_bars}"
            ),
            "window_type": "custom_explicit",
            "fold_construction": "explicit_manifest_boundaries",
            "overlap_policy": "selection_evaluation_overlap_forbidden",
            "declared_before_evaluation": True,
        },
        "selection_rule": {
            "rule_id": "carry_full_population",
            "rule_type": "carry_full_population",
            "description": (
                "Carry all included variants through each purged/embargoed "
                "scratch IS/OOS fold without winner selection."
            ),
            "declared_before_evaluation": True,
            "winner_only_selection_forbidden": True,
            "denominator_preservation": "all_declared_variants_remain_visible",
        },
        "folds": folds,
    }
    total_naive = sum(row["naive_selection_bars"] for row in comparison_rows)
    total_purged = sum(row["purged_selection_bars"] for row in comparison_rows)
    comparison = {
        "schema_version": "v1",
        "comparison_id": "WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01",
        "created_at_utc": config.created_at_utc,
        "source_commit": commit,
        "manifest_id": config.manifest_id,
        "timeframe": config.timeframe,
        "fold_parameters": {
            "start_utc": config.start_utc,
            "selection_bars": config.selection_bars,
            "evaluation_bars": config.evaluation_bars,
            "purge_bars": config.purge_bars,
            "embargo_bars": config.embargo_bars,
            "fold_count": config.fold_count,
            "boundary_semantics": "start_inclusive_end_exclusive",
        },
        "comparison_summary": {
            "fold_count": len(comparison_rows),
            "folds_with_boundary_gap": sum(row["purge_gap_bars"] > 0 for row in comparison_rows),
            "folds_with_embargo_shifted_selection_start": sum(
                row["embargo_bars_after_previous_evaluation"] > 0 for row in comparison_rows
            ),
            "total_selection_bars_naive": total_naive,
            "total_selection_bars_purged_embargoed": total_purged,
            "total_selection_bars_removed": total_naive - total_purged,
            "material_difference_observed": total_naive != total_purged,
        },
        "rows": comparison_rows,
        "leakage_risks_addressed": [
            "adjacent training labels with horizons that overlap first evaluation bars",
            "rolling feature or warmup contamination at the IS/OOS boundary",
            "post-evaluation bleed where rows immediately after one OOS window enter a later selection window",
            "implicit zero-gap fold assumptions that are hard to audit after materialization",
        ],
        "non_authority_flags": [
            "scratch_only",
            "non_canonical",
            "not_canonical_evidence",
            "not_runner_change",
            "not_backtester_change",
            "not_promotion",
            "not_readiness",
            "not_paper_live",
        ],
    }
    return manifest, comparison


def write_purged_fold_artifacts(
    *,
    output_path: Path,
    comparison_output_path: Path,
    provenance_output_path: Path,
    config: PurgedFoldConfig,
) -> tuple[Path, Path, Path]:
    """Write and validate scratch purged-fold artifacts."""
    manifest, comparison = build_purged_manifest_and_comparison(config)
    _write_json(output_path, manifest)
    errors = validate_walkforward_fold_manifests(explicit_paths=[output_path])
    if errors:
        raise PurgedFoldError("generated manifest failed validation: " + "; ".join(errors))
    _write_json(comparison_output_path, comparison)
    provenance = {
        "schema_version": "v1",
        "wp_id": "WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01",
        "created_at_utc": config.created_at_utc,
        "source_commit": manifest["source_commit"],
        "generated_files": {
            "purged_fold_manifest": output_path.as_posix(),
            "purged_fold_comparison_report": comparison_output_path.as_posix(),
        },
        "artifact_hashes": {
            "purged_fold_manifest": _hash_json(manifest),
            "purged_fold_comparison_report": _hash_json(comparison),
        },
        "generation_tool": "tools.walkforward.purged_folds",
        "dependency_posture": "repo-native; no purgedcv dependency used",
        "contract_validation": {
            "validator": "tools.registry.validate_walkforward_fold_manifest",
            "passed": True,
        },
        "non_authority_flags": comparison["non_authority_flags"],
    }
    _write_json(provenance_output_path, provenance)
    return output_path, comparison_output_path, provenance_output_path


def _default_comparison_path(output: Path) -> Path:
    return output.with_name("purged_fold_comparison_report.json")


def _default_provenance_path(output: Path) -> Path:
    return output.with_name("provenance.json")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--comparison-output", type=Path)
    parser.add_argument("--provenance-output", type=Path)
    parser.add_argument("--manifest-id", default="WFM-9002")
    parser.add_argument("--created-at-utc", default=DEFAULT_CREATED_AT_UTC)
    parser.add_argument("--strategy-spec-id", default="STRAT-SPEC-0004")
    parser.add_argument("--variant-manifest-id", default="VM-0004")
    parser.add_argument("--sweep-plan-id", default="SWEEP-PLAN-0004")
    parser.add_argument(
        "--data-slice-id",
        default=(
            "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
            "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
        ),
    )
    parser.add_argument("--timeframe", default=DEFAULT_TIMEFRAME)
    parser.add_argument("--start-utc", default=DEFAULT_START_UTC)
    parser.add_argument("--selection-bars", type=int, default=DEFAULT_SELECTION_BARS)
    parser.add_argument("--evaluation-bars", type=int, default=DEFAULT_EVALUATION_BARS)
    parser.add_argument("--purge-bars", type=int, default=DEFAULT_PURGE_BARS)
    parser.add_argument("--embargo-bars", type=int, default=DEFAULT_EMBARGO_BARS)
    parser.add_argument("--fold-count", type=int, default=DEFAULT_FOLD_COUNT)
    parser.add_argument("--declared-variant-count", type=int, default=DEFAULT_DECLARED_VARIANT_COUNT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = PurgedFoldConfig(
        manifest_id=args.manifest_id,
        created_at_utc=args.created_at_utc,
        strategy_spec_id=args.strategy_spec_id,
        variant_manifest_id=args.variant_manifest_id,
        sweep_plan_id=args.sweep_plan_id,
        data_slice_id=args.data_slice_id,
        timeframe=args.timeframe,
        start_utc=args.start_utc,
        selection_bars=args.selection_bars,
        evaluation_bars=args.evaluation_bars,
        purge_bars=args.purge_bars,
        embargo_bars=args.embargo_bars,
        fold_count=args.fold_count,
        declared_variant_count=args.declared_variant_count,
    )
    comparison_output = args.comparison_output or _default_comparison_path(args.output)
    provenance_output = args.provenance_output or _default_provenance_path(args.output)
    try:
        manifest_path, comparison_path, provenance_path = write_purged_fold_artifacts(
            output_path=args.output,
            comparison_output_path=comparison_output,
            provenance_output_path=provenance_output,
            config=config,
        )
    except (OSError, PurgedFoldError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"OK: purged fold manifest written: {manifest_path}")
    print(f"OK: comparison report written: {comparison_path}")
    print(f"OK: provenance written: {provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
