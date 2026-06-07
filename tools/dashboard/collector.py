"""Collect repo facts into dashboard_data.v1.

The collector is the only dashboard component that reads repo artifacts. The
renderer consumes the validated contract output produced here.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


D4A_DIR = Path("research/data_slices/binance_usdtm_btcusdt_15m")
D4A_CATALOG = D4A_DIR / "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
D4A_VALIDATION = D4A_DIR / "binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json"
D4A_IMPORT = D4A_DIR / "binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json"


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


def _source_commit(repo_root: Path) -> str:
    try:
        return _run_git(repo_root, "rev-parse", "--short", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _source_branch(repo_root: Path) -> str:
    try:
        return _run_git(repo_root, "branch", "--show-current") or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _dirty_state(repo_root: Path) -> str:
    try:
        return "dirty" if _run_git(repo_root, "status", "--short") else "clean"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(repo_root: Path, path: Path) -> dict[str, Any] | None:
    full_path = repo_root / path
    if not full_path.exists():
        return None
    return json.loads(full_path.read_text(encoding="utf-8"))


def _hash_or_none(repo_root: Path, path: Path) -> str | None:
    full_path = repo_root / path
    if not full_path.exists():
        return None
    return _sha256_file(full_path)


def _source_ref(
    ref_id: str,
    ref_type: str,
    path: str,
    sha256: str | None,
    description: str,
) -> dict[str, Any]:
    return {
        "ref_id": ref_id,
        "ref_type": ref_type,
        "path": path,
        "sha256": sha256,
        "description": description,
    }


def _fresh(reason: str) -> dict[str, Any]:
    return {
        "staleness_status": "FRESH",
        "staleness_reason": reason,
        "source_artifact_mtime_utc": None,
    }


def _counts_by_status(gates: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in ["PASS", "WARN", "FAIL", "BLOCKED", "UNKNOWN", "NOT_AVAILABLE"]}
    for gate in gates:
        counts[gate["status"]] += 1
    return counts


def _d4_status(catalog: dict[str, Any] | None, validation: dict[str, Any] | None) -> str:
    if catalog is None or validation is None:
        return "NOT_AVAILABLE"
    if catalog.get("catalog_status") == "valid_offline_validated_slice" and (
        validation.get("validation", {}).get("status") == "PASS" or validation.get("ok") is True
    ):
        return "PASS"
    return "WARN"


def _build_missing_data(repo_root: Path) -> dict[str, Any]:
    source_refs = [
        _source_ref("project-status", "doc", "docs/project_status.md", None, "Current project status anchor."),
        _source_ref("status-wp-f2", "status_entry", "docs/status_entries/WP-F2.md", None, "F2 status fragment."),
    ]
    empty_freshness = {
        "staleness_status": "UNKNOWN",
        "staleness_reason": "D4A source artifacts were not found in the current repo checkout.",
        "source_artifact_mtime_utc": None,
    }
    gates = _gate_entries()
    return {
        "schema_version": "dashboard_data.v1",
        "generated_at_utc": _utc_now(),
        "source_commit": _source_commit(repo_root),
        "source_branch": _source_branch(repo_root),
        "dirty_state": _dirty_state(repo_root),
        "system_posture": "research_only",
        "non_authority_declaration": _non_authority_declaration(),
        "pages": {
            "overview": {
                "status": "WARN",
                "source_refs": ["project-status"],
                "status_cards": [
                    {
                        "card_id": "d4a-data-slice",
                        "title": "Latest D4A data slice",
                        "status": "NOT_AVAILABLE",
                        "summary": "D4A data slice artifacts were not found.",
                        "source_refs": ["project-status"],
                    }
                ],
                "warnings": [
                    {
                        "warning_id": "d4a-missing",
                        "status": "WARN",
                        "message": "D4A catalog, validation, or import artifacts are missing.",
                        "source_refs": ["project-status"],
                    }
                ],
                "latest_data_slice": {
                    "status": "NOT_AVAILABLE",
                    "d4_catalog_ref": None,
                    "d4_slice_identity": None,
                    "freshness": empty_freshness,
                    "source_refs": ["project-status"],
                },
                "latest_validation": {
                    "status": "NOT_AVAILABLE",
                    "validation_report_ref": None,
                    "validation_report_sha256": None,
                    "freshness": empty_freshness,
                    "source_refs": ["project-status"],
                },
                "latest_result_population_empty_state": _empty_state(
                    "No D5 result population yet.", "project-status"
                ),
                "paper_runtime_empty_state": _empty_state("No paper runtime yet.", "project-status"),
                "live_mode_empty_state": _empty_state("No live mode.", "project-status"),
                "open_gates_summary": {
                    "status": "BLOCKED",
                    "total_gates": len(gates),
                    "counts_by_status": _counts_by_status(gates),
                    "source_refs": ["project-status", "status-wp-f2"],
                },
            },
            "data_provenance": _empty_data_provenance(),
            "gates": {"status": "BLOCKED", "source_refs": ["project-status", "status-wp-f2"], "gates": gates},
        },
        "warnings": [
            {
                "warning_id": "d4a-missing",
                "status": "WARN",
                "message": "D4A source artifacts are missing from this checkout.",
                "source_refs": ["project-status"],
            }
        ],
        "source_refs": source_refs,
    }


def _empty_state(message: str, ref_id: str) -> dict[str, Any]:
    return {"status": "NOT_AVAILABLE", "message": message, "source_refs": [ref_id]}


def _empty_data_provenance() -> dict[str, Any]:
    return {
        "status": "NOT_AVAILABLE",
        "source_refs": ["project-status"],
        "d4_slice": {
            "status": "NOT_AVAILABLE",
            "catalog_ref": None,
            "data_slice_identity": None,
            "catalog_artifact_sha256": None,
            "dataset_id": None,
            "venue": None,
            "symbol": None,
            "market_type": None,
            "stream": None,
            "timeframe": None,
            "row_count": None,
            "expected_row_count": None,
            "timestamp_range": {"start_utc": None, "end_utc": None},
            "gap_facts": {"gap_count": None, "missing_bar_count": None, "gaps": [], "policy": None},
            "duplicate_facts": {
                "duplicate_group_count": None,
                "duplicate_row_count": None,
                "duplicates": [],
                "policy": None,
            },
            "raw_source_sha256": None,
            "normalized_sha256": None,
            "source_refs": ["project-status"],
        },
        "d3_validation_report": {
            "status": "NOT_AVAILABLE",
            "path": None,
            "sha256": None,
            "source_refs": ["project-status"],
        },
        "d2_import_report": {
            "status": "NOT_AVAILABLE",
            "path": None,
            "sha256": None,
            "source_refs": ["project-status"],
        },
        "artifact_paths": [],
        "freshness": {
            "staleness_status": "UNKNOWN",
            "staleness_reason": "D4A source artifacts were not found.",
            "source_artifact_mtime_utc": None,
        },
    }


def _non_authority_declaration() -> dict[str, bool]:
    return {
        "read_only_mirror": True,
        "renderer_must_not_invent_facts": True,
        "not_executable": True,
        "not_runtime_authority": True,
        "not_paper_live_authority": True,
        "not_order_authority": True,
        "not_broker_exchange_authority": True,
        "not_ranking_authority": True,
        "not_recommendation_authority": True,
        "not_readiness_authority": True,
        "not_promotion_authority": True,
        "not_transition_authority": True,
        "not_gate_authority": True,
    }


def _gate_entries() -> list[dict[str, Any]]:
    note = "Display-only gate fact. The dashboard cannot satisfy or alter this gate."
    return [
        {
            "gate_id": "D5A_RUNNER_PROVENANCE_ALIGNMENT",
            "title": "D5A runner provenance alignment",
            "status": "PASS",
            "why_it_matters": "D5A is merged and the offline runner can record D4 catalog and slice provenance.",
            "required_human_action": "Inspect the merged WP-D5A status fragment when preparing later D5 work.",
            "source_refs": ["status-wp-d5a"],
            "non_authority_note": note,
        },
        {
            "gate_id": "D5_KARL_GATE",
            "title": "D5 Karl gate",
            "status": "BLOCKED",
            "why_it_matters": "A first real-data result population remains gated after D5A.",
            "required_human_action": "Record the Karl decision through a later approved package path.",
            "source_refs": ["status-wp-d5a"],
            "non_authority_note": note,
        },
        {
            "gate_id": "F2_REPORT_BACK_BEFORE_F3",
            "title": "F2 report-back before F3",
            "status": "PASS",
            "why_it_matters": "F3 is authorized after the dashboard_data contract and validator are merged.",
            "required_human_action": "Use only contract-valid dashboard_data as renderer input.",
            "source_refs": ["status-wp-f2"],
            "non_authority_note": note,
        },
        {
            "gate_id": "F5_RESULTS_PAGE_GATED_UNTIL_D5",
            "title": "F5 Results page waits for D5",
            "status": "BLOCKED",
            "why_it_matters": "Results content waits for a later D5 result population.",
            "required_human_action": "Keep Results page work out of F3.",
            "source_refs": ["status-wp-d5a"],
            "non_authority_note": note,
        },
        {
            "gate_id": "F6_PAPER_PAGE_GATED_UNTIL_PAPER_RUNTIME",
            "title": "F6 Paper page waits for paper runtime",
            "status": "BLOCKED",
            "why_it_matters": "Paper views wait for separately authorized paper runtime and read-only snapshots.",
            "required_human_action": "Keep paper views out of F3.",
            "source_refs": ["project-status"],
            "non_authority_note": note,
        },
        {
            "gate_id": "LIVE_GATE_PAPER_TO_LIVE_KARL_GATE",
            "title": "Live gate / paper-to-live Karl gate",
            "status": "BLOCKED",
            "why_it_matters": "Live mode remains outside dashboard authority and future human gates are required.",
            "required_human_action": "Keep live mode disabled unless future repo truth changes through approved work.",
            "source_refs": ["project-status"],
            "non_authority_note": note,
        },
    ]


def collect_dashboard_data(repo_root: Path | str = ".") -> dict[str, Any]:
    """Return dashboard_data.v1 collected from the current repo checkout."""

    root = Path(repo_root).resolve()
    catalog = _load_json(root, D4A_CATALOG)
    validation = _load_json(root, D4A_VALIDATION)
    import_report = _load_json(root, D4A_IMPORT)
    if catalog is None or validation is None or import_report is None:
        return _build_missing_data(root)

    catalog_sha = _hash_or_none(root, D4A_CATALOG)
    validation_sha = _hash_or_none(root, D4A_VALIDATION)
    import_sha = _hash_or_none(root, D4A_IMPORT)
    validation_report_sha = validation_sha
    catalog_status = _d4_status(catalog, validation)
    gates = _gate_entries()
    gate_counts = _counts_by_status(gates)
    overall_status = "BLOCKED" if gate_counts["BLOCKED"] else "WARN"

    source_refs = [
        _source_ref("project-status", "doc", "docs/project_status.md", None, "Current project status anchor."),
        _source_ref("status-wp-f1", "status_entry", "docs/status_entries/WP-F1.md", None, "F1 dashboard design status fragment."),
        _source_ref("status-wp-f2", "status_entry", "docs/status_entries/WP-F2.md", None, "F2 contract status fragment."),
        _source_ref("status-wp-d4a", "status_entry", "docs/status_entries/WP-D4A.md", None, "D4A catalog slice status fragment."),
        _source_ref("status-wp-d5a", "status_entry", "docs/status_entries/WP-D5A.md", None, "D5A runner provenance status fragment."),
        _source_ref("d4a-catalog", "catalog_slice", D4A_CATALOG.as_posix(), catalog_sha, "D4A catalog/slice JSON."),
        _source_ref("d4a-validation", "validation_report", D4A_VALIDATION.as_posix(), validation_sha, "D3 PASS validation report."),
        _source_ref("d4a-import", "import_report", D4A_IMPORT.as_posix(), import_sha, "D2 import/provenance report."),
    ]

    range_facts = catalog["range"]
    gap_facts = catalog["gap_summary"]
    duplicate_facts = catalog["duplicate_summary"]
    normalized = catalog["normalized"]
    source = catalog["source"]
    validation_ref = catalog["validation_report"]

    return {
        "schema_version": "dashboard_data.v1",
        "generated_at_utc": _utc_now(),
        "source_commit": _source_commit(root),
        "source_branch": _source_branch(root),
        "dirty_state": _dirty_state(root),
        "system_posture": "research_only",
        "non_authority_declaration": _non_authority_declaration(),
        "pages": {
            "overview": {
                "status": overall_status,
                "source_refs": ["project-status", "status-wp-f1", "status-wp-f2"],
                "status_cards": [
                    {
                        "card_id": "system-posture",
                        "title": "System posture",
                        "status": "WARN",
                        "summary": "Research-only; paper disabled; live disabled.",
                        "source_refs": ["project-status"],
                    },
                    {
                        "card_id": "d4a-data-slice",
                        "title": "Latest D4A data slice",
                        "status": catalog_status,
                        "summary": f"{catalog['symbol']} {catalog['timeframe']} slice has {range_facts['row_count']} rows.",
                        "source_refs": ["d4a-catalog", "status-wp-d4a"],
                    },
                    {
                        "card_id": "d3-validation",
                        "title": "Latest validation",
                        "status": "PASS" if validation.get("validation", {}).get("status") == "PASS" else "WARN",
                        "summary": "D3 validation report is present for the D4A 15m slice.",
                        "source_refs": ["d4a-validation"],
                    },
                    {
                        "card_id": "d5-gate",
                        "title": "D5 gate",
                        "status": "BLOCKED",
                        "summary": "D5 remains Karl-gated after D5A.",
                        "source_refs": ["status-wp-d5a"],
                    },
                    {
                        "card_id": "dashboard-data-validation",
                        "title": "Dashboard data validation",
                        "status": "PASS",
                        "summary": "Generator validates dashboard_data.v1 before rendering.",
                        "source_refs": ["status-wp-f2"],
                    },
                ],
                "warnings": [
                    {
                        "warning_id": "no-d5-results",
                        "status": "WARN",
                        "message": "F3 renders no Results page because D5 result population is not present.",
                        "source_refs": ["status-wp-d5a"],
                    }
                ],
                "latest_data_slice": {
                    "status": catalog_status,
                    "d4_catalog_ref": catalog["catalog_ref"],
                    "d4_slice_identity": catalog["slice_identity"]["data_slice_identity"],
                    "freshness": _fresh("Committed D4A catalog slice artifact is present on the source commit."),
                    "source_refs": ["d4a-catalog"],
                },
                "latest_validation": {
                    "status": "PASS" if validation.get("validation", {}).get("status") == "PASS" else "WARN",
                    "validation_report_ref": D4A_VALIDATION.as_posix(),
                    "validation_report_sha256": validation_report_sha,
                    "freshness": _fresh("Validation report is present as a committed D4A source artifact."),
                    "source_refs": ["d4a-validation"],
                },
                "latest_result_population_empty_state": _empty_state(
                    "No D5 result population yet.", "status-wp-d5a"
                ),
                "paper_runtime_empty_state": _empty_state("No paper runtime yet.", "project-status"),
                "live_mode_empty_state": _empty_state("No live mode.", "project-status"),
                "open_gates_summary": {
                    "status": "BLOCKED",
                    "total_gates": len(gates),
                    "counts_by_status": gate_counts,
                    "source_refs": ["status-wp-d5a", "status-wp-f2"],
                },
            },
            "data_provenance": {
                "status": catalog_status,
                "source_refs": ["d4a-catalog", "d4a-validation", "d4a-import"],
                "d4_slice": {
                    "status": catalog_status,
                    "catalog_ref": catalog["catalog_ref"],
                    "data_slice_identity": catalog["slice_identity"]["data_slice_identity"],
                    "catalog_artifact_sha256": catalog_sha,
                    "dataset_id": catalog["dataset_id"],
                    "venue": catalog["venue"],
                    "symbol": catalog["symbol"],
                    "market_type": catalog["market_type"],
                    "stream": catalog["stream"],
                    "timeframe": catalog["timeframe"],
                    "row_count": range_facts["row_count"],
                    "expected_row_count": range_facts["expected_row_count"],
                    "timestamp_range": {
                        "start_utc": range_facts["start_utc"],
                        "end_utc": range_facts["end_utc"],
                    },
                    "gap_facts": {
                        "gap_count": gap_facts["gap_count"],
                        "missing_bar_count": gap_facts["missing_bar_count"],
                        "gaps": gap_facts["gaps"],
                        "policy": gap_facts["policy"],
                    },
                    "duplicate_facts": {
                        "duplicate_group_count": duplicate_facts["duplicate_group_count"],
                        "duplicate_row_count": duplicate_facts["duplicate_row_count"],
                        "duplicates": duplicate_facts["duplicates"],
                        "policy": duplicate_facts["policy"],
                    },
                    "raw_source_sha256": source["raw_source_sha256"],
                    "normalized_sha256": normalized["sha256"],
                    "source_refs": ["d4a-catalog"],
                },
                "d3_validation_report": {
                    "status": "PASS" if validation_ref["status"] == "PASS" else "WARN",
                    "path": D4A_VALIDATION.as_posix(),
                    "sha256": validation_report_sha,
                    "source_refs": ["d4a-validation"],
                },
                "d2_import_report": {
                    "status": "PASS" if import_report.get("validation", {}).get("status") == "PASS" else "WARN",
                    "path": D4A_IMPORT.as_posix(),
                    "sha256": import_sha,
                    "source_refs": ["d4a-import"],
                },
                "artifact_paths": [
                    {
                        "artifact_id": "D4A-CATALOG",
                        "artifact_type": "catalog_slice",
                        "path": D4A_CATALOG.as_posix(),
                        "sha256": catalog_sha,
                        "source_refs": ["d4a-catalog"],
                    },
                    {
                        "artifact_id": "D3-VALIDATION",
                        "artifact_type": "validation_report",
                        "path": D4A_VALIDATION.as_posix(),
                        "sha256": validation_sha,
                        "source_refs": ["d4a-validation"],
                    },
                    {
                        "artifact_id": "D2-IMPORT",
                        "artifact_type": "import_report",
                        "path": D4A_IMPORT.as_posix(),
                        "sha256": import_sha,
                        "source_refs": ["d4a-import"],
                    },
                    {
                        "artifact_id": "D4A-NORMALIZED-DATA",
                        "artifact_type": "normalized_data",
                        "path": normalized["path"],
                        "sha256": normalized["sha256"],
                        "source_refs": ["d4a-catalog"],
                    },
                    {
                        "artifact_id": "D4A-RAW-SOURCE",
                        "artifact_type": "raw_source",
                        "path": import_report["source"]["path"],
                        "sha256": source["raw_source_sha256"],
                        "source_refs": ["d4a-import"],
                    },
                ],
                "freshness": _fresh("D4A artifacts are committed under the current source commit."),
            },
            "gates": {
                "status": "BLOCKED",
                "source_refs": ["project-status", "status-wp-f2", "status-wp-d5a"],
                "gates": gates,
            },
        },
        "warnings": [
            {
                "warning_id": "display-only-gates",
                "status": "WARN",
                "message": "Dashboard displays gates; dashboard does not satisfy gates.",
                "source_refs": ["status-wp-f1", "status-wp-f2"],
            }
        ],
        "source_refs": source_refs,
    }
