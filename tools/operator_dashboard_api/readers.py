"""Read-only artifact readers for the local operator dashboard API."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from tools.dashboard.collector import collect_dashboard_data
from tools.lab_cockpit.model import (
    build_cockpit_data,
    build_product_candidate_funnel,
    build_product_pipeline_runs,
)
from tools.lab_pipeline.queue_status import build_queue_status
from tools.lab_reporting.report_model import build_report_data
from tools.lab_state.resolver import REPO_ROOT
from tools.operator_dashboard_api.models import (
    DERIVED_PROJECTION_WARNING,
    READ_ONLY_AUTHORITY,
    ApiEnvelope,
    ProvenanceRef,
)


RESULT_POPULATIONS_DIR = REPO_ROOT / "research" / "result_populations"
STRATEGY_SPECS_DIR = REPO_ROOT / "research" / "strategy_specs"
CANDIDATE_REGISTRY_PATH = REPO_ROOT / "research" / "candidate_registry.jsonl"
WFO_REPORT_PATHS = (
    REPO_ROOT / "scratch" / "WP-LAB-WALKFORWARD-RUN-01" / "walkforward_run_report.json",
    REPO_ROOT
    / "scratch"
    / "WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01"
    / "purged_walkforward_run_report.json",
)
MONTE_CARLO_REPORT_PATHS = (
    REPO_ROOT
    / "scratch"
    / "EXT-INTEG-ROBUSTNESS-MC-01"
    / "seeded_advisory_mc_report.json",
)


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return rows
    for line in lines:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _provenance(path: Path | str, role: str, note: str | None = None) -> ProvenanceRef:
    path_obj = REPO_ROOT / path if isinstance(path, str) else path
    return ProvenanceRef(
        path=_repo_relative(path_obj),
        role=role,
        note=note,
        sha256=_sha256(path_obj),
    )


def _envelope(
    *,
    source: str,
    data: Any,
    provenance: list[ProvenanceRef],
    warnings: list[str] | None = None,
    withheld: dict[str, Any] | None = None,
    unavailable: dict[str, Any] | None = None,
) -> ApiEnvelope:
    return ApiEnvelope(
        source=source,
        provenance=provenance,
        authority=dict(READ_ONLY_AUTHORITY),
        warnings=[DERIVED_PROJECTION_WARNING, *(warnings or [])],
        withheld=withheld or {},
        unavailable=unavailable or {},
        data=data,
    )


def _result_population_summary(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    lineage = payload.get("lineage") or {}
    denominator = payload.get("committed_denominator_snapshot") or {}
    outcome_counts = payload.get("outcome_category_counts") or {}
    execution = payload.get("execution_context") or {}
    validation = payload.get("validation_summary") or {}
    identity = payload.get("result_population_identity_hash") or {}
    input_identity = payload.get("input_identity_hash") or {}
    result_id = payload.get("result_population_id") or path.name.split(".", 1)[0]
    return {
        "result_population_id": result_id,
        "path": _repo_relative(path),
        "parent_strategy_spec_id": lineage.get("strategy_spec_id"),
        "variant_manifest_id": lineage.get("variant_manifest_id"),
        "sweep_plan_id": lineage.get("sweep_plan_id"),
        "committed_denominator": denominator.get("committed_denominator"),
        "result_row_count": denominator.get("result_row_count"),
        "outcome_counts": outcome_counts,
        "result_population_identity_hash": identity.get("hash"),
        "input_identity_hash": input_identity.get("hash"),
        "execution_mode": execution.get("execution_mode"),
        "offline_only": execution.get("offline_only"),
        "no_runtime_contact": execution.get("no_runtime_contact"),
        "no_paper_live_contact": execution.get("no_paper_live_contact"),
        "validator_status": validation.get("validator_status"),
        "review_status": (payload.get("review") or {}).get("review_status"),
    }


def _variant_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("variant_result_rows") or []
    if not isinstance(rows, list):
        return []
    projected = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        projected.append(
            {
                "variant_id": row.get("variant_id"),
                "row_id": row.get("row_id"),
                "outcome_category": row.get("outcome_category"),
                "attempted": row.get("attempted"),
                "metrics": row.get("metrics") or {},
                "non_success": row.get("non_success") or {},
                "error": row.get("error") or {},
            }
        )
    return projected


def _result_population_files() -> list[Path]:
    if not RESULT_POPULATIONS_DIR.is_dir():
        return []
    return sorted(RESULT_POPULATIONS_DIR.glob("*.result_population.json"))


def read_dashboard_summary() -> ApiEnvelope:
    result_populations = read_result_populations().data["items"]
    strategies = read_strategies().data["items"]
    candidates = _read_jsonl(CANDIDATE_REGISTRY_PATH)
    queue = build_queue_status(repo_root=REPO_ROOT)
    product_runs = build_product_pipeline_runs(repo_root=REPO_ROOT)
    cockpit = build_cockpit_data(repo_root=REPO_ROOT)
    data = {
        "status": "available",
        "system_posture": "research_only",
        "counts": {
            "result_populations": len(result_populations),
            "strategies": len(strategies),
            "registered_candidates": len(candidates),
            "queue_runs": queue["summary"]["run_count"],
            "product_runs": product_runs["totals"]["run_count"],
            "candidates_admitted": cockpit["product_candidate_funnel"].get(
                "candidate_admitted_count", 0
            ),
        },
        "queue_summary": queue["summary"],
        "product_run_summary": product_runs["totals"],
        "paper_trading": {
            "status": "unavailable",
            "reason": "No authorized read-only paper telemetry snapshot exists for this API package.",
            "capability_built": False,
        },
        "live_trading": {
            "status": "unavailable",
            "reason": "No authorized read-only live telemetry snapshot exists for this API package.",
            "capability_built": False,
        },
    }
    return _envelope(
        source="committed repo artifacts plus static cockpit and queue readers",
        data=data,
        provenance=[
            _provenance("tools/lab_cockpit/model.py", "static_reader"),
            _provenance("tools/lab_pipeline/queue_status.py", "static_reader"),
            _provenance(CANDIDATE_REGISTRY_PATH, "candidate_registry"),
            _provenance(RESULT_POPULATIONS_DIR, "result_population_directory"),
            _provenance(STRATEGY_SPECS_DIR, "strategy_spec_directory"),
        ],
        unavailable={
            "paper_live_telemetry": "No paper/live read-only snapshot is authorized or present.",
            "control_actions": "No control actions are implemented by this API.",
        },
    )


def read_research_jobs() -> ApiEnvelope:
    data = build_queue_status(repo_root=REPO_ROOT)
    return _envelope(
        source="tools.lab_pipeline.queue_status.build_queue_status",
        data=data,
        provenance=[
            _provenance("tools/lab_pipeline/queue_status.py", "reader"),
            _provenance(data["artifact_roots"]["pipeline_runs_root"], "artifact_root"),
            _provenance(data["artifact_roots"]["runner_results_root"], "artifact_root"),
            _provenance(data["artifact_roots"]["gates_results_root"], "artifact_root"),
        ],
        withheld={"notifications": "Notification fields are dry-run preview metadata only."},
    )


def read_result_populations() -> ApiEnvelope:
    items: list[dict[str, Any]] = []
    malformed: list[str] = []
    for path in _result_population_files():
        payload = _read_json(path)
        if payload is None:
            malformed.append(_repo_relative(path))
            continue
        items.append(_result_population_summary(path, payload))
    return _envelope(
        source="committed research/result_populations artifacts",
        data={"status": "available", "count": len(items), "items": items},
        provenance=[
            _provenance(RESULT_POPULATIONS_DIR, "result_population_directory"),
            _provenance("tools/research_query/query_layer.py", "available_read_only_query_surface"),
        ],
        warnings=[f"Malformed result population files skipped: {malformed}"] if malformed else [],
        withheld={
            "per_trade_distributions": "Only fields committed in each result population artifact are projected.",
        },
    )


def read_result_population(result_population_id: str) -> ApiEnvelope:
    path = RESULT_POPULATIONS_DIR / f"{result_population_id}.result_population.json"
    payload = _read_json(path)
    if payload is None:
        return _envelope(
            source="committed research/result_populations artifacts",
            data={"status": "unavailable", "result_population_id": result_population_id},
            provenance=[_provenance(RESULT_POPULATIONS_DIR, "result_population_directory")],
            unavailable={
                "result_population": f"{result_population_id} is not present as a committed artifact."
            },
        )
    summary = _result_population_summary(path, payload)
    summary.update(
        {
            "status": "available",
            "data_coverage_summary": payload.get("data_coverage_summary") or {},
            "backtest_assumption_summary": payload.get("backtest_assumption_summary") or {},
            "error_summary": payload.get("error_summary") or {},
            "append_only_ledger": payload.get("append_only_ledger") or {},
            "non_authority_declaration": payload.get("non_authority_declaration") or {},
            "review": payload.get("review") or {},
            "variant_result_rows": _variant_rows(payload),
        }
    )
    return _envelope(
        source=f"committed artifact {path.name}",
        data=summary,
        provenance=[_provenance(path, "result_population_artifact")],
        withheld={
            "uncommitted_runner_outputs": "Not read. This endpoint projects committed artifacts only."
        },
    )


def _lineage_matches_result_population(
    artifact: dict[str, Any], result_population: dict[str, Any]
) -> bool:
    lineage = result_population.get("lineage") or {}
    fields = (
        ("strategy_spec_id", "strategy_spec_id"),
        ("variant_manifest_id", "variant_manifest_id"),
        ("sweep_plan_id", "sweep_plan_id"),
    )
    return all(
        isinstance(artifact.get(field), str)
        and bool(artifact[field])
        and artifact[field] == lineage.get(lineage_field)
        for field, lineage_field in fields
    )


def _artifact_source(
    *,
    artifact_kind: str,
    path: Path,
    source_field: str,
    data: Any,
    row_count: int,
    fold_count: int | None = None,
    sample_count: int | None = None,
    linkage: str,
) -> dict[str, Any]:
    return {
        "artifact_kind": artifact_kind,
        "data_available": True,
        "source_path": _repo_relative(path),
        "source_sha256": _sha256(path),
        "source_field": source_field,
        "row_count": row_count,
        "fold_count": fold_count,
        "path_count": 1,
        "sample_count": sample_count,
        "linkage": linkage,
        "data": data,
    }


def _inventory_item(
    artifact_kind: str,
    sources: list[dict[str, Any]],
    unavailable_reason: str,
) -> dict[str, Any]:
    if sources:
        return {
            "artifact_kind": artifact_kind,
            "data_available": True,
            "source_path": sources[0]["source_path"] if len(sources) == 1 else None,
            "source_sha256": sources[0]["source_sha256"] if len(sources) == 1 else None,
            "path_count": len(sources),
            "row_count": sum(source["row_count"] for source in sources),
            "fold_count": sum(source["fold_count"] or 0 for source in sources),
            "withheld_reason": None,
            "unavailable_reason": None,
        }
    return {
        "artifact_kind": artifact_kind,
        "data_available": False,
        "source_path": None,
        "source_sha256": None,
        "path_count": 0,
        "row_count": 0,
        "fold_count": 0,
        "withheld_reason": unavailable_reason,
        "unavailable_reason": unavailable_reason,
    }


def read_result_population_artifact_projections(
    result_population_id: str,
) -> ApiEnvelope:
    """Project only committed diagnostic arrays linked to one result population."""

    result_path = RESULT_POPULATIONS_DIR / f"{result_population_id}.result_population.json"
    result_population = _read_json(result_path)
    if result_population is None:
        return _envelope(
            source="committed diagnostic artifact inventory",
            data={"status": "unavailable", "result_population_id": result_population_id},
            provenance=[_provenance(RESULT_POPULATIONS_DIR, "result_population_directory")],
            unavailable={
                "artifact_projections": (
                    f"{result_population_id} is not present as a committed result population."
                )
            },
        )

    projections: list[dict[str, Any]] = []
    by_kind: dict[str, list[dict[str, Any]]] = {
        "equity_curve": [],
        "drawdown_time_series": [],
        "wfo_folds": [],
        "monte_carlo_robustness_summary": [],
        "monte_carlo_sample_distribution": [],
        "per_trade_return_distribution": [],
        "trade_list": [],
        "summarized_trade_diagnostics": [],
    }

    variant_rows = result_population.get("variant_result_rows")
    if isinstance(variant_rows, list):
        projection = _artifact_source(
            artifact_kind="summarized_trade_diagnostics",
            path=result_path,
            source_field="variant_result_rows",
            data=variant_rows,
            row_count=len(variant_rows),
            linkage="direct_result_population_id",
        )
        projections.append(projection)
        by_kind[projection["artifact_kind"]].append(projection)

    for path in WFO_REPORT_PATHS:
        payload = _read_json(path)
        if payload is None or not _lineage_matches_result_population(payload, result_population):
            continue
        folds = payload.get("fold_results")
        if not isinstance(folds, list):
            continue
        projection = _artifact_source(
            artifact_kind="wfo_folds",
            path=path,
            source_field="fold_results",
            data=folds,
            row_count=len(folds),
            fold_count=len(folds),
            linkage="exact_strategy_spec_variant_manifest_sweep_plan_lineage_match",
        )
        projections.append(projection)
        by_kind[projection["artifact_kind"]].append(projection)

    for path in MONTE_CARLO_REPORT_PATHS:
        payload = _read_json(path)
        fixture = (payload or {}).get("fixture") or {}
        bootstrap_ci = (payload or {}).get("bootstrap_ci")
        if fixture.get("result_population_id") != result_population_id:
            continue
        if not isinstance(bootstrap_ci, dict):
            continue
        projection = _artifact_source(
            artifact_kind="monte_carlo_robustness_summary",
            path=path,
            source_field="bootstrap_ci",
            data=bootstrap_ci,
            row_count=len(bootstrap_ci),
            sample_count=payload.get("bootstrap_sample_count"),
            linkage="direct_fixture_result_population_id",
        )
        projections.append(projection)
        by_kind[projection["artifact_kind"]].append(projection)

    absence_reasons = {
        "equity_curve": (
            "No committed equity-curve point series is linked to this result population."
        ),
        "drawdown_time_series": (
            "Committed artifacts expose aggregate drawdown metrics, not drawdown "
            "time-series points."
        ),
        "wfo_folds": "No committed WFO fold report has exact lineage to this result population.",
        "monte_carlo_robustness_summary": (
            "No committed Monte Carlo confidence-summary artifact directly names this "
            "result population."
        ),
        "monte_carlo_sample_distribution": (
            "Monte Carlo reports commit confidence summaries and a sample checksum, not "
            "the raw bootstrap sample distribution."
        ),
        "per_trade_return_distribution": (
            "Committed result populations expose aggregate per-variant metrics only; no "
            "real per-trade returns are present."
        ),
        "trade_list": (
            "No committed trade-list rows are linked to this result population; "
            "aggregate trade counts are not expanded into trades."
        ),
        "summarized_trade_diagnostics": (
            "No committed variant_result_rows array is present for summarized trade diagnostics."
        ),
    }
    inventory = [
        _inventory_item(kind, by_kind[kind], absence_reasons[kind]) for kind in by_kind
    ]
    available_count = sum(item["data_available"] for item in inventory)
    data = {
        "status": "available" if available_count == len(inventory) else "partially_available",
        "result_population_id": result_population_id,
        "artifact_class_count": len(inventory),
        "available_artifact_class_count": available_count,
        "projection_count": len(projections),
        "artifact_inventory": inventory,
        "projections": projections,
    }
    unavailable = {
        item["artifact_kind"]: item["unavailable_reason"]
        for item in inventory
        if not item["data_available"]
    }
    source_paths = [result_path, *WFO_REPORT_PATHS, *MONTE_CARLO_REPORT_PATHS]
    projected_paths = {projection["source_path"] for projection in projections}
    return _envelope(
        source="committed result population and diagnostic artifacts",
        data=data,
        provenance=[
            _provenance(path, "projected_diagnostic_artifact")
            for path in source_paths
            if _repo_relative(path) in projected_paths
        ],
        withheld=unavailable,
        unavailable=unavailable,
    )


def _strategy_summary(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    timeframe = payload.get("timeframe_and_data") or {}
    instruments = payload.get("instruments") or {}
    free_parameters = payload.get("free_parameters") or {}
    review = payload.get("review") or {}
    strategy_id = payload.get("strategy_spec_id") or path.name.split(".", 1)[0]
    return {
        "strategy_id": strategy_id,
        "strategy_spec_id": strategy_id,
        "path": _repo_relative(path),
        "title": payload.get("title"),
        "short_name": payload.get("short_name"),
        "status": payload.get("status"),
        "source_type": (payload.get("provenance") or {}).get("source_type"),
        "instrument_family": instruments.get("instrument_family"),
        "market_type": instruments.get("market_type"),
        "primary_timeframe": timeframe.get("primary_timeframe"),
        "direction": (payload.get("entry_logic") or {}).get("direction"),
        "free_parameter_count": free_parameters.get("count"),
        "max_free_parameters": free_parameters.get("max_free_parameters"),
        "approval_scope": review.get("review_scope"),
        "not_executable": (payload.get("non_execution_declaration") or {}).get(
            "not_executable"
        ),
    }


def _strategy_files() -> list[Path]:
    if not STRATEGY_SPECS_DIR.is_dir():
        return []
    return sorted(STRATEGY_SPECS_DIR.glob("*.strategy_spec.json"))


def read_strategies() -> ApiEnvelope:
    items: list[dict[str, Any]] = []
    malformed: list[str] = []
    for path in _strategy_files():
        payload = _read_json(path)
        if payload is None:
            malformed.append(_repo_relative(path))
            continue
        items.append(_strategy_summary(path, payload))
    return _envelope(
        source="committed research/strategy_specs artifacts",
        data={"status": "available", "count": len(items), "items": items},
        provenance=[
            _provenance(STRATEGY_SPECS_DIR, "strategy_spec_directory"),
            _provenance("tools/research_query/query_layer.py", "available_read_only_query_surface"),
        ],
        warnings=[f"Malformed strategy spec files skipped: {malformed}"] if malformed else [],
    )


def read_strategy(strategy_id: str) -> ApiEnvelope:
    path = STRATEGY_SPECS_DIR / f"{strategy_id}.strategy_spec.json"
    payload = _read_json(path)
    if payload is None:
        return _envelope(
            source="committed research/strategy_specs artifacts",
            data={"status": "unavailable", "strategy_id": strategy_id},
            provenance=[_provenance(STRATEGY_SPECS_DIR, "strategy_spec_directory")],
            unavailable={"strategy": f"{strategy_id} is not present as a committed artifact."},
        )
    summary = _strategy_summary(path, payload)
    summary.update(
        {
            "status": "available",
            "provenance": payload.get("provenance") or {},
            "non_execution_declaration": payload.get("non_execution_declaration") or {},
            "timeframe_and_data": payload.get("timeframe_and_data") or {},
            "entry_logic": payload.get("entry_logic") or {},
            "exit_logic": payload.get("exit_logic") or {},
            "filters": payload.get("filters") or {},
            "free_parameters": payload.get("free_parameters") or {},
            "review": payload.get("review") or {},
        }
    )
    return _envelope(
        source=f"committed artifact {path.name}",
        data=summary,
        provenance=[_provenance(path, "strategy_spec_artifact")],
        withheld={
            "execution_results": "Strategy specs are planning artifacts; result populations are exposed separately."
        },
    )


def read_candidate_funnel() -> ApiEnvelope:
    candidates = _read_jsonl(CANDIDATE_REGISTRY_PATH)
    by_status: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    for candidate in candidates:
        by_status[str(candidate.get("status", "unknown"))] = (
            by_status.get(str(candidate.get("status", "unknown")), 0) + 1
        )
        by_verdict[str(candidate.get("overall_verdict", "unknown"))] = (
            by_verdict.get(str(candidate.get("overall_verdict", "unknown")), 0) + 1
        )
    product_runs = build_product_pipeline_runs(repo_root=REPO_ROOT)
    product_funnel = build_product_candidate_funnel(product_runs)
    data = {
        "status": "available",
        "candidate_registry": {
            "registered_count": len(candidates),
            "by_status": by_status,
            "by_overall_verdict": by_verdict,
            "admitted_candidate_count": 0,
            "paper_live_built": False,
        },
        "product_candidate_funnel": product_funnel,
        "note": (
            "Candidate funnel is read-only. GO-like review routing, when present, "
            "is advisory review routing only and admits no candidate."
        ),
    }
    return _envelope(
        source="candidate registry plus static product cockpit funnel",
        data=data,
        provenance=[
            _provenance(CANDIDATE_REGISTRY_PATH, "candidate_registry"),
            _provenance("tools/lab_cockpit/model.py", "static_reader"),
        ],
        withheld={
            "candidate_admission": "No committed candidate admission is created or implied by this endpoint."
        },
        unavailable={
            "paper_live_capability": "No paper/live capability is built by this dashboard API package."
        },
    )


def read_daily_report() -> ApiEnvelope:
    data = build_report_data(as_of="unspecified", period="unspecified", repo_root=REPO_ROOT)
    return _envelope(
        source="tools.lab_reporting.report_model.build_report_data",
        data={"status": "available", "report_kind": "daily_brief", "report": data},
        provenance=[
            _provenance("tools/lab_reporting/report_model.py", "static_reader"),
            _provenance("docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md", "report_surface_doc"),
        ],
        withheld={"charting": data.get("charting", {})},
    )


def read_weekly_report() -> ApiEnvelope:
    data = build_report_data(as_of="unspecified", period="unspecified", repo_root=REPO_ROOT)
    return _envelope(
        source="tools.lab_reporting.report_model.build_report_data",
        data={"status": "available", "report_kind": "weekly_report", "report": data},
        provenance=[
            _provenance("tools/lab_reporting/report_model.py", "static_reader"),
            _provenance("docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md", "report_surface_doc"),
        ],
        withheld={"charting": data.get("charting", {})},
    )


def read_data_health() -> ApiEnvelope:
    dashboard = collect_dashboard_data(REPO_ROOT)
    pages = dashboard.get("pages") or {}
    data_provenance = pages.get("data_provenance") or {}
    overview = pages.get("overview") or {}
    data = {
        "status": data_provenance.get("status", "unavailable"),
        "system_posture": dashboard.get("system_posture"),
        "data_provenance": data_provenance,
        "latest_data_slice": overview.get("latest_data_slice"),
        "latest_validation": overview.get("latest_validation"),
        "paper_runtime": overview.get("paper_runtime_empty_state"),
        "live_mode": overview.get("live_mode_empty_state"),
        "warnings": dashboard.get("warnings") or [],
    }
    unavailable = {}
    if data["status"] in {"NOT_AVAILABLE", "unavailable"}:
        unavailable["data_health"] = "Committed dashboard data artifacts are missing or unavailable."
    return _envelope(
        source="tools.dashboard.collector.collect_dashboard_data",
        data=data,
        provenance=[
            _provenance("tools/dashboard/collector.py", "static_reader"),
            _provenance("docs/dashboard/README.md", "dashboard_doc"),
        ],
        unavailable=unavailable,
    )


def read_agent_intake_schema() -> ApiEnvelope:
    data = {
        "status": "unavailable",
        "schema_status": "future_placeholder_only",
        "draft_endpoint_available": False,
        "post_endpoint_created": False,
        "agent_inbox_write_created": False,
        "allowed_methods": ["GET"],
        "future_intake_fields_preview": [
            "source_label",
            "source_type",
            "idea_text",
            "claimed_edge",
            "timeframe_hint",
            "data_requirements",
            "operator_notes",
        ],
        "reason": (
            "Agent Inbox writes belong to a later isolated package. This endpoint "
            "only displays the boundary and does not accept or persist drafts."
        ),
    }
    return _envelope(
        source="operator dashboard architecture lock",
        data=data,
        provenance=[
            _provenance(
                "docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md",
                "architecture_lock",
            )
        ],
        unavailable={
            "agent_inbox_write": "POST /api/agent/intake-draft is intentionally not implemented."
        },
    )
