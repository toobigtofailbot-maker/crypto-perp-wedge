"""Tests for the local-first read-only operator dashboard API."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from tools.operator_dashboard_api.app import app
from tools.lab_state.resolver import REPO_ROOT


REQUIRED_GET_ROUTES = {
    "/api/dashboard/summary",
    "/api/research/jobs",
    "/api/research/result-populations",
    "/api/research/result-populations/{id}",
    "/api/research/result-populations/{id}/artifact-projections",
    "/api/strategies",
    "/api/strategies/{id}",
    "/api/candidates/funnel",
    "/api/reports/daily",
    "/api/reports/weekly",
    "/api/system/data-health",
    "/api/agent/intake-schema",
}


def _client() -> TestClient:
    return TestClient(app)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_envelope(payload: dict) -> None:
    assert payload["schema_version"] == "operator_dashboard_api_v1"
    assert payload["source"]
    assert payload["provenance"]
    assert payload["authority"]["read_only"] is True
    assert payload["authority"]["control_surface"] == "none"
    assert isinstance(payload["warnings"], list)
    assert isinstance(payload["withheld"], dict)
    assert isinstance(payload["unavailable"], dict)
    assert "data" in payload


def test_app_imports_and_route_subset_present() -> None:
    routes = {route.path for route in app.routes}
    assert REQUIRED_GET_ROUTES <= routes


def test_all_dashboard_api_routes_are_get_only() -> None:
    for route in app.routes:
        if not route.path.startswith("/api/"):
            continue
        assert route.methods == {"GET"}


def test_no_agent_inbox_write_or_control_routes() -> None:
    paths = {route.path.lower() for route in app.routes if route.path.startswith("/api/")}
    assert "/api/agent/intake-draft" not in paths
    forbidden_segments = (
        "approve",
        "execute",
        "promote",
        "cross",
        "trade",
        "go_live",
        "paper_start",
        "notify_send",
    )
    for path in paths:
        assert not any(segment in path for segment in forbidden_segments), path


def test_required_routes_return_json_envelopes() -> None:
    client = _client()
    concrete_paths = [
        "/api/dashboard/summary",
        "/api/research/jobs",
        "/api/research/result-populations",
        "/api/research/result-populations/RP-7134",
        "/api/research/result-populations/RP-2592/artifact-projections",
        "/api/strategies",
        "/api/strategies/STRAT-SPEC-0003",
        "/api/candidates/funnel",
        "/api/reports/daily",
        "/api/reports/weekly",
        "/api/system/data-health",
        "/api/agent/intake-schema",
    ]
    for path in concrete_paths:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["content-type"].startswith("application/json")
        _assert_envelope(response.json())


def test_result_populations_expose_provenance_and_withheld_fields() -> None:
    payload = _client().get("/api/research/result-populations").json()
    _assert_envelope(payload)
    assert payload["data"]["count"] >= 1
    assert payload["withheld"]
    item = next(i for i in payload["data"]["items"] if i["result_population_id"] == "RP-7134")
    assert item["path"] == "research/result_populations/RP-7134.result_population.json"
    assert item["offline_only"] is True
    assert item["no_runtime_contact"] is True
    assert item["no_paper_live_contact"] is True


def test_result_population_detail_is_read_only_and_denominator_visible() -> None:
    payload = _client().get("/api/research/result-populations/RP-7134").json()
    data = payload["data"]
    assert data["status"] == "available"
    assert data["committed_denominator"] == data["result_row_count"]
    assert data["variant_result_rows"]
    non_authority = data["non_authority_declaration"]
    assert non_authority["not_executable"] is True
    assert non_authority["not_runtime_authority"] is True
    assert non_authority["not_paper_live_authority"] is True


def test_real_artifact_projections_trace_exact_committed_content() -> None:
    payload = _client().get(
        "/api/research/result-populations/RP-2592/artifact-projections"
    ).json()
    _assert_envelope(payload)
    data = payload["data"]
    assert data["status"] == "partially_available"

    projections = data["projections"]
    for projection in projections:
        source = REPO_ROOT / projection["source_path"]
        assert projection["source_sha256"] == f"sha256:{_sha(source)}"
        assert projection["path_count"] == 1

    trade_diagnostics = next(
        item for item in projections if item["artifact_kind"] == "summarized_trade_diagnostics"
    )
    result_population = json.loads(
        (REPO_ROOT / trade_diagnostics["source_path"]).read_text(encoding="utf-8")
    )
    assert trade_diagnostics["source_field"] == "variant_result_rows"
    assert trade_diagnostics["data"] == result_population["variant_result_rows"]
    assert trade_diagnostics["row_count"] == len(result_population["variant_result_rows"])

    wfo = [item for item in projections if item["artifact_kind"] == "wfo_folds"]
    assert len(wfo) == 2
    for projection in wfo:
        source_payload = json.loads(
            (REPO_ROOT / projection["source_path"]).read_text(encoding="utf-8")
        )
        assert projection["data"] == source_payload["fold_results"]
        assert projection["fold_count"] == len(source_payload["fold_results"])

    monte_carlo = next(
        item
        for item in projections
        if item["artifact_kind"] == "monte_carlo_robustness_summary"
    )
    mc_payload = json.loads(
        (REPO_ROOT / monte_carlo["source_path"]).read_text(encoding="utf-8")
    )
    assert monte_carlo["data"] == mc_payload["bootstrap_ci"]
    assert monte_carlo["sample_count"] == mc_payload["bootstrap_sample_count"]


def test_absent_artifact_classes_have_reasons_and_no_fake_data_arrays() -> None:
    payload = _client().get(
        "/api/research/result-populations/RP-7134/artifact-projections"
    ).json()
    inventory = {item["artifact_kind"]: item for item in payload["data"]["artifact_inventory"]}
    for kind in (
        "equity_curve",
        "drawdown_time_series",
        "wfo_folds",
        "monte_carlo_robustness_summary",
        "monte_carlo_sample_distribution",
        "per_trade_return_distribution",
        "trade_list",
    ):
        item = inventory[kind]
        assert item["data_available"] is False
        assert item["withheld_reason"]
        assert item["unavailable_reason"]
        assert "data" not in item
        assert kind in payload["unavailable"]


def test_unknown_result_population_artifact_projection_is_unavailable() -> None:
    payload = _client().get(
        "/api/research/result-populations/RP-NOT-PRESENT/artifact-projections"
    ).json()
    assert payload["data"] == {
        "status": "unavailable",
        "result_population_id": "RP-NOT-PRESENT",
    }
    assert payload["unavailable"]["artifact_projections"]


def test_strategy_detail_does_not_imply_execution_authority() -> None:
    payload = _client().get("/api/strategies/STRAT-SPEC-0003").json()
    data = payload["data"]
    assert data["status"] == "available"
    assert data["strategy_spec_id"] == "STRAT-SPEC-0003"
    assert data["non_execution_declaration"]["not_executable"] is True
    assert data["non_execution_declaration"]["not_runtime_authority"] is True
    assert payload["withheld"]["execution_results"]


def test_candidate_funnel_admits_no_candidate_and_no_paper_live() -> None:
    payload = _client().get("/api/candidates/funnel").json()
    data = payload["data"]
    assert data["candidate_registry"]["admitted_candidate_count"] == 0
    assert data["candidate_registry"]["paper_live_built"] is False
    assert data["product_candidate_funnel"]["candidate_admitted_count"] == 0
    assert data["product_candidate_funnel"]["winner_only_view"] is False
    assert "paper_live_capability" in payload["unavailable"]


def test_reports_are_existing_read_only_report_projection() -> None:
    client = _client()
    daily = client.get("/api/reports/daily").json()
    weekly = client.get("/api/reports/weekly").json()
    assert daily["data"]["report_kind"] == "daily_brief"
    assert weekly["data"]["report_kind"] == "weekly_report"
    for payload in (daily, weekly):
        report = payload["data"]["report"]
        assert report["non_authority_declaration"]["descriptive_only"] is True
        assert report["non_authority_declaration"]["fires_notifications"] is False
        assert payload["withheld"]["charting"]["enabled"] is False


def test_agent_intake_schema_is_placeholder_only() -> None:
    payload = _client().get("/api/agent/intake-schema").json()
    data = payload["data"]
    assert data["status"] == "unavailable"
    assert data["draft_endpoint_available"] is False
    assert data["post_endpoint_created"] is False
    assert data["agent_inbox_write_created"] is False
    assert data["allowed_methods"] == ["GET"]
    assert "agent_inbox_write" in payload["unavailable"]


def test_requests_do_not_mutate_source_artifacts() -> None:
    paths = [
        REPO_ROOT / "research" / "result_populations" / "RP-7134.result_population.json",
        REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0003.strategy_spec.json",
        REPO_ROOT / "research" / "candidate_registry.jsonl",
        REPO_ROOT / "scratch" / "WP-LABPROD-COCKPIT-REALRUN-REFRESH-08" / "product_runs" / "LGATE-ad8b6d62f772e9d8" / "run_index.json",
    ]
    before = {path: _sha(path) for path in paths}
    client = _client()
    for route in (
        "/api/dashboard/summary",
        "/api/research/jobs",
        "/api/research/result-populations/RP-7134",
        "/api/strategies/STRAT-SPEC-0003",
        "/api/candidates/funnel",
        "/api/reports/daily",
        "/api/system/data-health",
        "/api/agent/intake-schema",
    ):
        assert client.get(route).status_code == 200
    after = {path: _sha(path) for path in paths}
    assert after == before
