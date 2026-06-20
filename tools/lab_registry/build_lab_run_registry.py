"""Build a read-only lab run/result registry from committed repo artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RESULT_POPULATIONS_DIR = Path("research/result_populations")
ANALYTICS_REPORT = Path("scratch/EXT-INTEG-ANALYTICS-METRICS-01/advisory_analytics_report.json")
ROBUSTNESS_REPORT = Path("scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.json")
TRIAGE_REPORT = Path("scratch/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01/vectorbt_triage_report.json")
STATUS_VOCAB = {"PASS", "WARN", "FAIL", "BLOCKED", "UNKNOWN", "NOT_AVAILABLE"}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _git_value(repo_root: Path, *args: str) -> str:
    try:
        return _run_git(repo_root, *args)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_path(path: Path) -> str:
    return path.as_posix()


def _metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metric_names = ["return_pct", "pnl", "drawdown", "sharpe", "trade_count", "win_rate", "fees", "slippage", "funding"]
    summary: dict[str, Any] = {}
    for metric in metric_names:
        values = [
            float(row.get("metrics", {}).get(metric))
            for row in rows
            if isinstance(row.get("metrics", {}).get(metric), (int, float))
        ]
        summary[metric] = {
            "available": bool(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": sum(values) / len(values) if values else None,
        }
    return summary


def _result_record(
    repo_root: Path,
    path: Path,
    payload: dict[str, Any],
    source_commit: str,
    source_branch: str,
) -> dict[str, Any]:
    rows = sorted(payload.get("variant_result_rows", []), key=lambda row: row.get("variant_id", ""))
    lineage = payload.get("lineage", {})
    denominator = payload.get("committed_denominator_snapshot", {})
    coverage = payload.get("data_coverage_summary", {})
    assumptions = payload.get("backtest_assumption_summary", {})
    sizing = payload.get("sizing_metadata")
    row_count = len(rows)
    outcome_counts: dict[str, int] = {}
    for row in rows:
        outcome = str(row.get("outcome_category", "UNKNOWN"))
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    committed_denominator = denominator.get("committed_denominator")
    status = "PASS" if committed_denominator == row_count and row_count > 0 else "WARN"
    warnings = []
    if committed_denominator != row_count:
        warnings.append("Committed denominator does not match variant row count.")
    if not rows:
        warnings.append("No variant result rows are present.")

    return {
        "run_id": payload.get("result_population_id", path.stem),
        "run_type": "canonical_result_population",
        "source_commit": source_commit,
        "source_branch": source_branch,
        "created_at_utc": payload.get("created_at_utc") or _utc_now(),
        "status": status,
        "strategy_spec_id": lineage.get("strategy_spec_id"),
        "strategy_spec_path": lineage.get("strategy_spec_path"),
        "variant_manifest_id": lineage.get("variant_manifest_id"),
        "variant_manifest_path": lineage.get("variant_manifest_path"),
        "sweep_plan_id": lineage.get("sweep_plan_id"),
        "sweep_plan_path": lineage.get("sweep_plan_path"),
        "result_population_id": payload.get("result_population_id"),
        "result_population_path": _repo_path(path),
        "dashboard_data_ref": None,
        "analytics_report_ref": None,
        "robustness_report_ref": None,
        "triage_sidecar_report_ref": None,
        "walkforward_manifest_ref": None,
        "data_slice_refs": [
            {
                "ref_id": "data_slice_identity",
                "path": coverage.get("data_slice_path"),
                "identity": coverage.get("data_slice_identity"),
            }
        ],
        "validation_refs": [
            {
                "ref_id": "result_population_identity_hash",
                "path": _repo_path(path),
                "sha256": payload.get("result_population_identity_hash", {}).get("hash") or _sha256_file(repo_root / path),
            },
            {
                "ref_id": "input_identity_hash",
                "path": _repo_path(path),
                "sha256": payload.get("input_identity_hash", {}).get("hash"),
            },
        ],
        "lineage_refs": [
            {"ref_id": "strategy_spec", "path": lineage.get("strategy_spec_path"), "artifact_id": lineage.get("strategy_spec_id")},
            {"ref_id": "variant_manifest", "path": lineage.get("variant_manifest_path"), "artifact_id": lineage.get("variant_manifest_id")},
            {"ref_id": "sweep_plan", "path": lineage.get("sweep_plan_path"), "artifact_id": lineage.get("sweep_plan_id")},
        ],
        "warnings": warnings,
        "non_authority_flags": {
            "display_only": True,
            "not_ranking_authority": True,
            "not_recommendation": True,
            "not_readiness": True,
            "not_promotion": True,
            "not_approval": True,
            "not_execution": True,
            "not_paper_live": True,
        },
        "result_summary": {
            "committed_denominator": committed_denominator,
            "result_row_count": row_count,
            "outcome_counts": outcome_counts,
            "variant_order_policy": "variant_id_ascending_only_not_quality_order",
            "variant_ids": [row.get("variant_id") for row in rows],
            "metric_summary": _metric_summary(rows),
            "backtest_assumptions": {
                "fill_mode": assumptions.get("fill_mode"),
                "fee_side_assumption": assumptions.get("fee_side_assumption"),
                "slippage_model": assumptions.get("slippage_model"),
                "liquidation_mode": assumptions.get("liquidation_mode"),
                "order_size_assumption": assumptions.get("order_size_assumption"),
                "sizing_metadata_mode": sizing.get("mode") if isinstance(sizing, dict) else None,
            },
        },
    }


def _attach_adopted_reports(repo_root: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {record["result_population_id"]: record for record in records if record.get("result_population_id")}
    report_specs = [
        (ANALYTICS_REPORT, "analytics_report_ref", "fixture.result_population_id"),
        (ROBUSTNESS_REPORT, "robustness_report_ref", "fixture.result_population_id"),
        (TRIAGE_REPORT, "triage_sidecar_report_ref", None),
    ]
    for rel_path, field, id_path in report_specs:
        payload = _load_json(repo_root / rel_path)
        if payload is None:
            continue
        result_population_id = None
        if id_path == "fixture.result_population_id":
            result_population_id = payload.get("fixture", {}).get("result_population_id")
        elif field == "triage_sidecar_report_ref":
            # The triage sidecar is not a Result Population; attach by matching strategy/VM/sweep lineage.
            fixture = payload.get("fixture", {})
            for record in records:
                if (
                    record.get("strategy_spec_id") == fixture.get("strategy_spec_id")
                    and record.get("variant_manifest_id") == fixture.get("variant_manifest_id")
                    and record.get("sweep_plan_id") == fixture.get("sweep_plan_id")
                ):
                    result_population_id = record.get("result_population_id")
                    break
        if result_population_id in by_id:
            by_id[result_population_id][field] = {
                "path": _repo_path(rel_path),
                "sha256": _sha256_file(repo_root / rel_path),
                "status": "PASS",
                "authority": "advisory_display_only_not_gate_not_ranking",
            }
    return records


def build_lab_run_registry(repo_root: Path | str = ".") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    rp_dir = root / RESULT_POPULATIONS_DIR
    source_commit = _git_value(root, "rev-parse", "--short", "HEAD")
    source_branch = _git_value(root, "branch", "--show-current") or "unknown"
    records = [
        _result_record(root, path.relative_to(root), _load_json(path) or {}, source_commit, source_branch)
        for path in sorted(rp_dir.glob("*.result_population.json"))
    ]
    records = _attach_adopted_reports(root, records)
    return {
        "schema_version": "lab_run_registry.v1",
        "generated_at_utc": _utc_now(),
        "source_commit": source_commit,
        "source_branch": source_branch,
        "status": "PASS" if records else "NOT_AVAILABLE",
        "registry_posture": {
            "read_only_over_canonical_evidence": True,
            "append_only_posture": True,
            "display_only": True,
            "not_ranking_authority": True,
            "not_recommendation": True,
            "not_readiness": True,
            "not_promotion": True,
            "not_approval": True,
            "not_execution": True,
            "not_paper_live": True,
        },
        "records": records,
        "warnings": [] if records else ["No committed result populations found."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    registry = build_lab_run_registry(args.repo_root)
    text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"lab_run_registry: {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
