"""Run a scratch-only purged/embargoed fold construction pilot.

The pilot writes advisory scratch artifacts only. It does not create or mutate
canonical walk-forward manifests, Result Populations, runner behavior, or any
runtime/paper/live path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / "WP-PILOT-PURGEDCV-01"
DEFAULT_CREATED_AT_UTC = "2026-06-20T12:00:00Z"
PILOT_ID = "WP-PILOT-PURGEDCV-01"
TOOL_CANDIDATE = "purgedcv"
NON_AUTHORITY_FLAGS = [
    "scratch_only",
    "non_canonical",
    "not_walkforward_contract",
    "not_canonical_evidence",
    "not_runner_change",
    "not_promotion",
    "not_readiness",
    "not_paper_live",
]


class PurgedCvPilotError(RuntimeError):
    """Raised when the scratch-only pilot cannot run safely."""


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")


def _sha256_text(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _source_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _assert_scratch_output_dir(path: Path) -> Path:
    resolved = path.resolve()
    scratch_root = (REPO_ROOT / "scratch").resolve()
    if resolved != scratch_root and scratch_root not in resolved.parents:
        raise PurgedCvPilotError(f"output must remain under {scratch_root}: {resolved}")
    return resolved


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise PurgedCvPilotError("created_at_utc must be UTC")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _dependency_status() -> dict[str, Any]:
    status: dict[str, Any] = {
        "package": TOOL_CANDIDATE,
        "import_attempted": True,
        "available": False,
        "version": None,
        "used_for_fold_construction": False,
        "probe_result": "unavailable",
        "notes": [],
    }
    try:
        module = importlib.import_module(TOOL_CANDIDATE)
    except Exception as exc:  # pragma: no cover - environment dependent
        status["error_type"] = exc.__class__.__name__
        status["error"] = str(exc)
        status["notes"].append(
            "Dependency import failed in the current environment; pilot uses a transparent repo-owned sketch."
        )
        return status

    status["available"] = True
    status["probe_result"] = "available_not_used_for_authority"
    status["module_file"] = getattr(module, "__file__", None)
    status["version"] = getattr(module, "__version__", None)
    if status["version"] is None:
        try:
            status["version"] = importlib.metadata.version(TOOL_CANDIDATE)
        except importlib.metadata.PackageNotFoundError:
            status["version"] = "unknown"
    status["notes"].append(
        "Dependency import succeeded, but this pilot still uses a transparent repo-owned sketch to avoid granting dependency authority."
    )
    return status


def _fixture_timestamps() -> list[datetime]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [start + timedelta(minutes=15 * index) for index in range(20 * 24 * 4)]


def _window_ref(timestamps: list[datetime], start_pos: int, end_pos: int) -> dict[str, Any]:
    if start_pos < 0 or end_pos > len(timestamps) or start_pos >= end_pos:
        raise PurgedCvPilotError(f"invalid window positions: {start_pos}, {end_pos}")
    end_exclusive = (
        timestamps[end_pos]
        if end_pos < len(timestamps)
        else timestamps[-1] + (timestamps[-1] - timestamps[-2])
    )
    return {
        "start_pos": start_pos,
        "end_pos_exclusive": end_pos,
        "start_utc": _iso(timestamps[start_pos]),
        "end_utc_exclusive": _iso(end_exclusive),
        "bar_count": end_pos - start_pos,
    }


def _build_naive_folds(
    timestamps: list[datetime],
    *,
    selection_bars: int,
    evaluation_bars: int,
    max_folds: int,
) -> list[dict[str, Any]]:
    step = selection_bars + evaluation_bars
    folds: list[dict[str, Any]] = []
    for fold_index in range(max_folds):
        selection_start = fold_index * step
        selection_end = selection_start + selection_bars
        evaluation_end = selection_end + evaluation_bars
        if evaluation_end > len(timestamps):
            break
        folds.append(
            {
                "fold_id": f"FOLD-{fold_index + 1:03d}",
                "fold_order": fold_index + 1,
                "construction": "naive_adjacent_walkforward",
                "selection_window": _window_ref(timestamps, selection_start, selection_end),
                "evaluation_window": _window_ref(timestamps, selection_end, evaluation_end),
                "gap_between_selection_and_evaluation_bars": 0,
                "purge": {"mode": "none", "bars": 0},
                "embargo": {"mode": "none", "bars": 0},
            }
        )
    return folds


def _build_purged_embargoed_folds(
    timestamps: list[datetime],
    naive_folds: list[dict[str, Any]],
    *,
    purge_bars: int,
    embargo_bars: int,
) -> list[dict[str, Any]]:
    folds: list[dict[str, Any]] = []
    previous_evaluation_end_pos: int | None = None
    for naive in naive_folds:
        nominal_selection = naive["selection_window"]
        evaluation = naive["evaluation_window"]
        selection_start = int(nominal_selection["start_pos"])
        if previous_evaluation_end_pos is not None:
            selection_start = max(selection_start, previous_evaluation_end_pos + embargo_bars)
        selection_end = int(evaluation["start_pos"]) - purge_bars
        if selection_start >= selection_end:
            raise PurgedCvPilotError(
                f"{naive['fold_id']} purge/embargo leaves no valid selection window"
            )
        purge_start = selection_end
        purge_end = int(evaluation["start_pos"])
        embargo_start = int(evaluation["end_pos_exclusive"])
        embargo_end = min(embargo_start + embargo_bars, len(timestamps))
        folds.append(
            {
                "fold_id": naive["fold_id"],
                "fold_order": naive["fold_order"],
                "construction": "repo_native_purged_embargoed_sketch",
                "selection_window": _window_ref(timestamps, selection_start, selection_end),
                "evaluation_window": {
                    "start_pos": evaluation["start_pos"],
                    "end_pos_exclusive": evaluation["end_pos_exclusive"],
                    "start_utc": evaluation["start_utc"],
                    "end_utc_exclusive": evaluation["end_utc_exclusive"],
                    "bar_count": evaluation["bar_count"],
                },
                "gap_between_selection_and_evaluation_bars": purge_bars,
                "purge": {
                    "mode": "bars",
                    "bars": purge_bars,
                    "window": _window_ref(timestamps, purge_start, purge_end),
                    "reason": "remove training labels/features whose horizon can overlap the evaluation boundary",
                },
                "embargo": {
                    "mode": "bars",
                    "bars": embargo_bars,
                    "window_after_evaluation": (
                        _window_ref(timestamps, embargo_start, embargo_end)
                        if embargo_end > embargo_start
                        else None
                    ),
                    "reason": "exclude immediate post-evaluation rows from later selection windows",
                },
                "selection_bars_removed_vs_naive": int(nominal_selection["bar_count"])
                - (selection_end - selection_start),
            }
        )
        previous_evaluation_end_pos = int(evaluation["end_pos_exclusive"])
    return folds


def _comparison_summary(
    naive_folds: list[dict[str, Any]],
    purged_folds: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = []
    for naive, purged in zip(naive_folds, purged_folds, strict=True):
        rows.append(
            {
                "fold_id": naive["fold_id"],
                "naive_selection_start_utc": naive["selection_window"]["start_utc"],
                "purged_selection_start_utc": purged["selection_window"]["start_utc"],
                "naive_selection_end_utc": naive["selection_window"]["end_utc_exclusive"],
                "purged_selection_end_utc": purged["selection_window"]["end_utc_exclusive"],
                "evaluation_start_utc": naive["evaluation_window"]["start_utc"],
                "naive_selection_bars": naive["selection_window"]["bar_count"],
                "purged_selection_bars": purged["selection_window"]["bar_count"],
                "selection_bars_removed": purged["selection_bars_removed_vs_naive"],
                "purge_gap_bars": purged["purge"]["bars"],
                "embargo_bars_after_evaluation": purged["embargo"]["bars"],
            }
        )
    return {
        "fold_count": len(rows),
        "rows": rows,
        "total_selection_bars_naive": sum(row["naive_selection_bars"] for row in rows),
        "total_selection_bars_purged_embargoed": sum(
            row["purged_selection_bars"] for row in rows
        ),
        "total_selection_bars_removed": sum(row["selection_bars_removed"] for row in rows),
        "folds_with_boundary_gap": sum(row["purge_gap_bars"] > 0 for row in rows),
        "folds_with_embargo_shifted_selection_start": sum(
            row["naive_selection_start_utc"] != row["purged_selection_start_utc"]
            for row in rows
        ),
        "material_difference_observed": any(row["selection_bars_removed"] > 0 for row in rows),
    }


def _repo_fit_assessment(dependency: dict[str, Any]) -> dict[str, Any]:
    return {
        "can_improve_fold_rigor": True,
        "should_borrow_repo_native": True,
        "keep_purgedcv_as_dependency_or_sidecar": False,
        "smallest_future_integration_surface": (
            "a pure fold-boundary helper that emits explicit purge/embargo fields for "
            "walkforward_fold_manifest instances, plus validator checks that evaluation "
            "starts after selection end plus required purge"
        ),
        "future_wp": (
            "WP-WALKFORWARD-PURGE-EMBARGO-HELPER-01: implement a repo-native helper "
            "and focused validator strengthening without changing runner/backtester semantics"
        ),
        "dependency_fit": (
            "Preserve as a reference only unless a later package proves packaging, API stability, "
            "and fold semantics are better than the small repo-native helper."
            if dependency["available"]
            else "Import unavailable in this environment; dependency adoption cannot be justified by this pilot."
        ),
        "unknowns": [
            "whether purgedcv's exact API and maintenance posture match the repo's explicit manifest grammar",
            "the correct purge horizon for each future label/feature family",
            "whether multi-timeframe or overlapping-label candidates require fold-level or sample-level purging",
            "how validator checks should encode purge/embargo without changing existing zero-instance compatibility",
            "whether any future canonical runner path should consume manifest purge/embargo fields directly",
        ],
    }


def build_report(created_at_utc: str = DEFAULT_CREATED_AT_UTC) -> dict[str, Any]:
    _parse_utc(created_at_utc)
    timestamps = _fixture_timestamps()
    selection_bars = 4 * 24 * 4
    evaluation_bars = 24 * 4
    purge_bars = 12
    embargo_bars = 8
    naive = _build_naive_folds(
        timestamps,
        selection_bars=selection_bars,
        evaluation_bars=evaluation_bars,
        max_folds=4,
    )
    purged = _build_purged_embargoed_folds(
        timestamps,
        naive,
        purge_bars=purge_bars,
        embargo_bars=embargo_bars,
    )
    dependency = _dependency_status()
    assessment = _repo_fit_assessment(dependency)
    return {
        "schema_version": "v1",
        "created_at_utc": created_at_utc,
        "source_commit": _source_commit(),
        "pilot_id": PILOT_ID,
        "tool_candidate": TOOL_CANDIDATE,
        "dependency_status": dependency,
        "input_fixture_description": {
            "kind": "deterministic_15m_like_timestamp_fixture",
            "symbol_context": "BTCUSDT Binance USDT-M perpetual research posture only",
            "timeframe": "15m",
            "start_utc": _iso(timestamps[0]),
            "end_utc_exclusive": _iso(timestamps[-1] + timedelta(minutes=15)),
            "bar_count": len(timestamps),
            "selection_bars_per_nominal_fold": selection_bars,
            "evaluation_bars_per_fold": evaluation_bars,
            "purge_bars": purge_bars,
            "embargo_bars": embargo_bars,
            "boundary_semantics": "start_inclusive_end_exclusive",
            "no_market_data_or_private_api_used": True,
        },
        "naive_folds": naive,
        "purged_embargoed_folds": purged,
        "comparison_summary": _comparison_summary(naive, purged),
        "leakage_risks_addressed": [
            "adjacent training labels with horizons that overlap the first evaluation bars",
            "feature warmup or rolling-stat lookback contamination at the IS/OOS boundary",
            "post-test bleed where rows immediately after an evaluation window enter the next selection window",
            "implicit zero-gap assumptions that are hard to audit once fold boundaries are materialized",
        ],
        "repo_fit_assessment": assessment,
        "recommendation": "borrow",
        "recommendation_rationale": (
            "Borrow the purged/embargoed approach into a small repo-native helper. Do not adopt "
            "purgedcv as a required dependency or canonical sidecar from this pilot alone."
        ),
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
    }


def _markdown_report(report: dict[str, Any]) -> str:
    summary = report["comparison_summary"]
    assessment = report["repo_fit_assessment"]
    lines = [
        f"# {PILOT_ID} Fold Comparison Report",
        "",
        f"Recommendation: `{report['recommendation']}`",
        f"Dependency available: `{report['dependency_status']['available']}`",
        f"Material fold difference observed: `{summary['material_difference_observed']}`",
        "",
        "## Conclusion",
        "",
        f"- Can this improve fold rigor? `{assessment['can_improve_fold_rigor']}`.",
        f"- Borrow repo-native? `{assessment['should_borrow_repo_native']}`.",
        f"- Keep purgedcv as dependency/sidecar? `{assessment['keep_purgedcv_as_dependency_or_sidecar']}`.",
        f"- Future WP: `{assessment['future_wp']}`.",
        f"- Smallest surface: {assessment['smallest_future_integration_surface']}.",
        "",
        "## Boundary Difference",
        "",
        "| fold | naive selection | purged/embargoed selection | eval start | bars removed |",
        "|---|---|---|---|---:|",
    ]
    for row in summary["rows"]:
        lines.append(
            "| {fold_id} | {naive_selection_start_utc} to {naive_selection_end_utc} | "
            "{purged_selection_start_utc} to {purged_selection_end_utc} | "
            "{evaluation_start_utc} | {selection_bars_removed} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Leakage Risks Addressed",
            "",
            *[f"- {item}" for item in report["leakage_risks_addressed"]],
            "",
            "## Unknowns",
            "",
            *[f"- {item}" for item in assessment["unknowns"]],
            "",
            "## Non-Authority",
            "",
            *[f"- {flag}" for flag in report["non_authority_flags"]],
            "",
        ]
    )
    return "\n".join(lines)


def _readme() -> str:
    return "\n".join(
        [
            f"# {PILOT_ID}",
            "",
            "Scratch-only purged/embargoed fold construction pilot.",
            "",
            "Artifacts in this directory are non-canonical and advisory. They are not a",
            "walk-forward contract, not canonical evidence, not a runner change, not a",
            "promotion/readiness signal, and not paper/live authority.",
            "",
            "Regenerate with:",
            "",
            "```powershell",
            "python -m tools.pilots.purgedcv_pilot.run_purgedcv_pilot --output-dir scratch/WP-PILOT-PURGEDCV-01",
            "```",
            "",
        ]
    )


def _requirements_poc() -> str:
    return "\n".join(
        [
            "# Scratch-only probe candidate; do not promote into repo dependency files from this pilot.",
            "purgedcv",
            "",
        ]
    )


def _provenance(
    *,
    output_dir: Path,
    report_path: Path,
    markdown_path: Path,
    readme_path: Path,
    dependency_probe_path: Path,
    requirements_path: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "pilot_id": PILOT_ID,
        "created_at_utc": report["created_at_utc"],
        "source_commit": report["source_commit"],
        "output_dir": output_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix(),
        "generated_files": {
            report_path.name: _sha256_file(report_path),
            markdown_path.name: _sha256_file(markdown_path),
            readme_path.name: _sha256_file(readme_path),
            dependency_probe_path.name: _sha256_file(dependency_probe_path),
            requirements_path.name: _sha256_file(requirements_path),
        },
        "report_payload_sha256": _sha256_text(
            json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
        ),
        "canonical_write_paths": [],
        "non_authority_flags": list(NON_AUTHORITY_FLAGS),
    }


def run_pilot(output_dir: Path = DEFAULT_OUTPUT_DIR, created_at_utc: str = DEFAULT_CREATED_AT_UTC) -> dict[str, Any]:
    resolved_output = _assert_scratch_output_dir(output_dir)
    report = build_report(created_at_utc=created_at_utc)
    report_path = resolved_output / "fold_comparison_report.json"
    markdown_path = resolved_output / "fold_comparison_report.md"
    readme_path = resolved_output / "README.md"
    dependency_probe_path = resolved_output / "dependency_probe.json"
    requirements_path = resolved_output / "requirements.poc.txt"
    provenance_path = resolved_output / "provenance.json"

    _write_json(report_path, report)
    _write_text(markdown_path, _markdown_report(report))
    _write_text(readme_path, _readme())
    _write_json(dependency_probe_path, report["dependency_status"])
    _write_text(requirements_path, _requirements_poc())
    provenance = _provenance(
        output_dir=resolved_output,
        report_path=report_path,
        markdown_path=markdown_path,
        readme_path=readme_path,
        dependency_probe_path=dependency_probe_path,
        requirements_path=requirements_path,
        report=report,
    )
    _write_json(provenance_path, provenance)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--created-at-utc", default=DEFAULT_CREATED_AT_UTC)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = run_pilot(output_dir=args.output_dir, created_at_utc=args.created_at_utc)
    except (PurgedCvPilotError, OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        json.dumps(
            {
                "pilot_id": report["pilot_id"],
                "recommendation": report["recommendation"],
                "dependency_available": report["dependency_status"]["available"],
                "material_difference_observed": report["comparison_summary"][
                    "material_difference_observed"
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
