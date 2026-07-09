"""Tests for the read-only product real-run cockpit panel.

These extend the static lab product cockpit with a deterministic, read-only
projection of committed *real* product-pipeline output (product bridge prepare
-> product runner adapter -> product gates adapters -> advisory review packet).

The panel must:

- distinguish the honest run states (no run / awaiting approval / prepared /
  executed / advisory packet ready / blocked-failed);
- back every real-run number with an actual committed advisory packet;
- show missing WFO/OOS/robustness statistics as withheld/missing, never zero;
- keep the candidate funnel honest (no candidate admitted / no GO promotion);
- render no executable control and fail closed on missing/malformed fixtures.
"""

from __future__ import annotations

import json

import pytest

from tools.lab_cockpit import model as cockpit_model
from tools.lab_cockpit.model import (
    PRODUCT_RUN_STATE_VOCABULARY,
    build_cockpit_data,
    build_product_candidate_funnel,
    build_product_pipeline_runs,
)
from tools.lab_cockpit.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT


def _only_run(pr: dict) -> dict:
    assert pr["runs"], "expected at least one committed product run"
    return pr["runs"][0]


# ---------------------------------------------------------------------------
# Committed real-run fixtures project into the expected honest states.
# ---------------------------------------------------------------------------
def test_committed_product_run_present_and_real() -> None:
    pr = build_product_pipeline_runs(repo_root=REPO_ROOT)
    assert pr["available"] is True
    assert pr["status"] == "present"
    totals = pr["totals"]
    assert totals["run_count"] >= 1
    assert totals["advisory_packet_ready"] >= 1
    # The run is a *real* runner invocation, not a spine-only proof.
    assert totals["real_runner_runs"] >= 1
    assert totals["blocked_or_failed"] == 0
    run = _only_run(pr)
    assert run["real_run"] is True
    assert run["runner_invoked"] is True
    assert run["display_state"] == "advisory_packet_ready"


def test_state_vocabulary_distinguishes_all_required_states() -> None:
    pr = build_product_pipeline_runs(repo_root=REPO_ROOT)
    states = {v["state"] for v in pr["state_vocabulary"]}
    for required in (
        "no_run",
        "awaiting_approval",
        "prepared",
        "executed",
        "advisory_packet_ready",
        "blocked_or_failed",
    ):
        assert required in states, required


def test_stage_ladder_reaches_advisory_packet() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    reached = run["reached_states"]
    for stage in (
        "idea_formalized",
        "bridge_prepared",
        "execute_approval_consumed",
        "runner_executed",
        "advisory_packet_ready",
    ):
        assert stage in reached, stage


def test_denominator_preserved_and_backed_by_artifact() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    counts = run["denominator_counts"]
    assert set(counts) == {"completed", "failed", "invalid", "blocked", "pruned"}
    assert counts["completed"] >= 1
    assert run["full_denominator_preserved"] is True
    # The advisory packet artifact backing the run is committed and present.
    advisory = next(
        a for a in run["artifacts"] if a["filename"] == "advisory_review_packet.json"
    )
    assert advisory["present"] is True
    assert str(advisory["sha256"]).startswith("sha256:")


# ---------------------------------------------------------------------------
# Missing WFO/OOS/robustness statistics show as withheld/missing, never zero.
# ---------------------------------------------------------------------------
def test_withheld_statistics_shown_missing_not_zero() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    wh = run["withheld_statistics"]
    assert wh["fabricated_any"] is False
    # The WFO/OOS gate is honestly blocked with withheld inputs, not a zero pass.
    assert wh["wfo_oos_gate_status"] == "blocked"
    assert wh["wfo_oos_withheld_status"] == "withheld_missing_walkforward_oos_inputs"
    assert wh["wfo_oos_statistics"], "expected named withheld WFO/OOS statistics"
    keys = {s["key"] for s in wh["sections"]}
    assert {"wfo_oos", "oos_walkforward", "per_trade"} <= keys
    for section in wh["sections"]:
        assert section["fabricated"] is False
        assert section["status"], section["key"]


def test_robustness_diagnostics_completed_and_skipped_shown() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    rob = run["robustness"]
    assert rob["existing_agent_invoked"] is True
    assert rob["diagnostics_completed"], "expected completed robustness diagnostics"
    # Skipped diagnostics carry honest reasons, not fabricated results.
    assert rob["diagnostics_skipped"]
    for skipped in rob["diagnostics_skipped"]:
        assert skipped["diagnostic"]
        assert skipped["reason"]


def test_candidate_review_is_advisory_and_non_promoting() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    cr = run["candidate_review"]
    assert cr["existing_agent_invoked"] is True
    assert cr["status"] == "completed"
    # Evidence gaps are surfaced; no promotion recommendation is fabricated.
    assert cr["evidence_gaps"]
    assert cr["recommendation"] in (None, "")


# ---------------------------------------------------------------------------
# Candidate funnel must not imply admission; GO-like stays review-needed.
# ---------------------------------------------------------------------------
def test_product_funnel_admits_no_candidate() -> None:
    pr = build_product_pipeline_runs(repo_root=REPO_ROOT)
    funnel = build_product_candidate_funnel(pr)
    assert funnel["available"] is True
    assert funnel["candidate_admitted_count"] == 0
    assert funnel["winner_only_view"] is False
    admitted = next(s for s in funnel["stages"] if s["stage"] == "candidate_admitted")
    assert admitted["count"] == 0


def test_surface_routing_carries_no_admission_or_promotion_authority() -> None:
    run = _only_run(build_product_pipeline_runs(repo_root=REPO_ROOT))
    assert run["candidate_lifecycle_written"] is False
    assert run["go_auto_admission"] is False
    assert run["go_auto_crossing"] is False
    assert run["go_auto_promotion"] is False
    posture = run["non_promotion_posture"]
    for key in (
        "not_candidate_admission",
        "not_candidate_lifecycle",
        "not_crossing",
        "not_promotion_or_readiness",
        "not_paper_live_runtime_authority",
    ):
        assert posture.get(key) is True, key


# ---------------------------------------------------------------------------
# Fail-closed: missing directory, empty directory, malformed run index.
# ---------------------------------------------------------------------------
def test_missing_product_dir_fails_closed_to_no_run(tmp_path) -> None:
    pr = build_product_pipeline_runs(repo_root=tmp_path, runs_root="does_not_exist")
    assert pr["available"] is False
    assert pr["status"] == "unavailable"
    assert pr["panel_state"] == "no_run"
    assert pr["runs"] == []
    # The state vocabulary is still surfaced for the no-run panel.
    assert {v["state"] for v in pr["state_vocabulary"]} >= {"no_run", "advisory_packet_ready"}


def test_empty_product_dir_fails_closed(tmp_path) -> None:
    (tmp_path / "runs").mkdir()
    pr = build_product_pipeline_runs(repo_root=tmp_path, runs_root="runs")
    assert pr["available"] is False
    assert pr["panel_state"] == "no_run"


def test_malformed_run_index_is_blocked_or_failed(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "LGATE-badbadbadbad0000"
    run_dir.mkdir(parents=True)
    (run_dir / "run_index.json").write_text("{ not valid json", encoding="utf-8")
    pr = build_product_pipeline_runs(repo_root=tmp_path, runs_root="runs")
    assert pr["available"] is True
    run = pr["runs"][0]
    assert run["available"] is False
    assert run["display_state"] == "blocked_or_failed"
    assert "run_index" in run["invalid_reason"]


def test_unavailable_product_panel_renders(tmp_path) -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    data["product_runs"] = build_product_pipeline_runs(
        repo_root=tmp_path, runs_root="missing"
    )
    data["product_candidate_funnel"] = build_product_candidate_funnel(
        data["product_runs"]
    )
    lowered = render_html(data).lower()
    assert "no committed product-pipeline run fixtures" in lowered
    assert "fails closed" in lowered
    assert "no-run" in lowered


# ---------------------------------------------------------------------------
# No absolute paths / no controls / no network in the product panel.
# ---------------------------------------------------------------------------
def test_no_absolute_paths_in_product_artifacts() -> None:
    pr = build_product_pipeline_runs(repo_root=REPO_ROOT)
    for run in pr["runs"]:
        for artifact in run.get("artifacts", []):
            path = artifact["path"]
            assert not path.startswith("/")
            assert ":" not in path
            assert ".." not in path
            assert path.startswith("scratch/")


def test_product_panel_has_no_controls_or_network() -> None:
    lowered = render_html(build_cockpit_data(repo_root=REPO_ROOT)).lower()
    for forbidden in (
        "<script",
        "<button",
        "<form",
        "<input",
        "onclick",
        'http-equiv="refresh"',
        "http://",
        "https://",
        "fetch(",
        "xmlhttprequest",
        "ws://",
        "setinterval",
        "settimeout",
    ):
        assert forbidden not in lowered, forbidden


def test_no_product_run_or_execute_controls_declared() -> None:
    decl = build_cockpit_data(repo_root=REPO_ROOT)["non_authority_declaration"]
    assert decl["reads_product_run_state_only"] is True
    for control in (
        "invokes_product_runner_adapter",
        "invokes_product_gates_adapter",
        "writes_advisory_review_packet",
        "records_candidate_surface_decision",
        "admits_candidate",
    ):
        assert decl[control] is False, control


# ---------------------------------------------------------------------------
# Render integration + determinism.
# ---------------------------------------------------------------------------
def test_product_panel_rendered_in_html() -> None:
    lowered = render_html(build_cockpit_data(repo_root=REPO_ROOT)).lower()
    assert "product pipeline" in lowered
    assert "advisory packet ready" in lowered
    assert "real runner executed" in lowered
    assert "withheld / missing statistics" in lowered
    assert "no candidate is" in lowered


def test_product_panel_in_markdown() -> None:
    md = render_markdown(build_cockpit_data(repo_root=REPO_ROOT))
    assert "## Product pipeline / real runs" in md
    assert "## Product candidate funnel (no candidate admitted)" in md
    assert "States distinguished:" in md


def test_spine_only_panel_notes_real_run_supersession() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    assert data["pipeline_state"]["real_run_evidence_available"] is True
    note = data["pipeline_state"]["real_run_supersedes_note"]
    assert note == cockpit_model.PIPELINE_REAL_RUN_SUPERSEDES_NOTE
    html = render_html(data)
    assert cockpit_model.PIPELINE_REAL_RUN_SUPERSEDES_NOTE in html


def test_product_panels_are_deterministic() -> None:
    a = build_cockpit_data(repo_root=REPO_ROOT)
    b = build_cockpit_data(repo_root=REPO_ROOT)
    assert a["product_runs"] == b["product_runs"]
    assert a["product_candidate_funnel"] == b["product_candidate_funnel"]
    assert render_html(a) == render_html(b)
    assert render_markdown(a) == render_markdown(b)


def test_existing_panels_still_render_alongside_product_panel() -> None:
    lowered = render_html(build_cockpit_data(repo_root=REPO_ROOT)).lower()
    for panel in (
        "lab overview",
        "pipeline runs",
        "product pipeline",
        "candidate funnel",
        "strategy / hypothesis explorer",
        "coordinator state",
    ):
        assert panel in lowered, panel


# ---------------------------------------------------------------------------
# Contract: the projection tracks the REAL product advisory-packet output shape.
# ---------------------------------------------------------------------------
def test_projection_matches_real_advisory_packet_shape(tmp_path) -> None:
    pytest.importorskip("pandas")
    from tools.lab_pipeline import gates_adapter, runner_adapter
    from tools.lab_pipeline.gates_adapter import run_product_gates_adapters
    from tools.lab_pipeline.state import read_json
    from tools.research_agents.candidate_review_packet_agent import (
        CandidateReviewPacketConfig,
    )
    from tools.research_agents.robustness_diagnostician_agent import (
        RobustnessDiagnosticianConfig,
    )
    from tests.test_agent_formalizer_runner_bridge import _run_product
    from tests.test_lab_pipeline_runner_adapter import (
        _run_valid_adapter,
        _write_execute_approval,
    )

    runner_output_root = tmp_path / "scratch" / runner_adapter.WP_ID / "outputs"
    gates_output_root = tmp_path / "scratch" / gates_adapter.WP_ID / "outputs"
    source_repo = gates_adapter.SOURCE_REPO_ROOT
    runner_adapter.REPO_ROOT = tmp_path
    runner_adapter.DEFAULT_OUTPUT_ROOT = runner_output_root
    gates_adapter.REPO_ROOT = tmp_path
    gates_adapter.DEFAULT_SCRATCH_ROOT = tmp_path / "scratch" / gates_adapter.WP_ID
    gates_adapter.DEFAULT_OUTPUT_ROOT = gates_output_root
    try:
        bridge_result, _ = _run_product(tmp_path)
        bridge_review = read_json(
            tmp_path / bridge_result["artifact_paths"]["human_review_packet"]
        )
        approval_path = _write_execute_approval(
            tmp_path, runner_output_root, bridge_result, bridge_review
        )
        runner_result = _run_valid_adapter(
            tmp_path, runner_output_root, bridge_result, bridge_review, approval_path
        )
        gates = run_product_gates_adapters(
            runner_adapter_result_path=runner_result.artifact_paths[
                "runner_adapter_result"
            ],
            output_root=gates_output_root,
            robustness_config=RobustnessDiagnosticianConfig(bootstrap_samples=50),
            candidate_review_config=CandidateReviewPacketConfig(
                timestamp_utc="2026-07-08T00:00:00Z"
            ),
        )
        advisory = read_json(tmp_path / gates.artifact_paths["advisory_review_packet"])
    finally:
        runner_adapter.REPO_ROOT = source_repo
        gates_adapter.REPO_ROOT = source_repo

    # The read-only projection helpers extract exactly the fields the cockpit renders.
    withheld = cockpit_model._product_withheld_view(advisory)
    assert withheld["fabricated_any"] is False
    assert withheld["wfo_oos_gate_status"] == "blocked"
    assert {s["key"] for s in withheld["sections"]} >= {"wfo_oos", "per_trade"}

    rob = cockpit_model._product_robustness_view(advisory)
    assert rob["existing_agent_invoked"] is True
    assert rob["diagnostics_completed"]

    review = cockpit_model._product_candidate_review_view(advisory)
    assert review["status"] == "completed"

    routing = advisory["candidate_surface_routing"]
    assert routing["go_auto_admission"] is False
    assert routing["candidate_lifecycle_written"] is False
