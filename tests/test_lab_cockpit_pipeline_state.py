"""Tests for the read-only pipeline run-state cockpit panels.

These extend the static lab product cockpit with a deterministic, read-only
projection of committed ``tools/lab_pipeline`` run packets. The panel must show
run cards, stage timelines, awaiting-approval and blocked states, and honest
``runner_invoked=false`` spine-only labeling; fail closed on missing/malformed
packets; render no executable control; and track the *real* orchestrator output
shape (a contract test drives the actual orchestrator into a temp dir).
"""

from __future__ import annotations

import json

from tools.lab_cockpit import model as cockpit_model
from tools.lab_cockpit.model import build_cockpit_data, build_pipeline_state
from tools.lab_cockpit.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT


def _run_by_status(ps: dict, display_status: str) -> dict:
    return next(r for r in ps["runs"] if r["display_status"] == display_status)


# ---------------------------------------------------------------------------
# Committed fixtures project into the expected honest run states.
# ---------------------------------------------------------------------------
def test_committed_fixtures_present_and_projected() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    assert ps["available"] is True
    assert ps["status"] == "present"
    statuses = {r["display_status"] for r in ps["runs"]}
    assert "awaiting_prereg_approval" in statuses
    assert "blocked_or_invalid" in statuses
    assert "complete_spine_only" in statuses
    totals = ps["totals"]
    assert totals["run_count"] == len(ps["runs"]) >= 3
    assert totals["awaiting_approval"] >= 1
    assert totals["blocked_or_invalid"] >= 1
    assert totals["complete_spine_only"] >= 1
    # No committed run ever invoked a real runner.
    assert totals["complete_real"] == 0


def test_runs_are_ordered_deterministically() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    ids = [r["pipeline_run_id"] for r in ps["runs"]]
    assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# Awaiting approval is shown clearly with the approval requirement.
# ---------------------------------------------------------------------------
def test_awaiting_approval_state_shown() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    run = _run_by_status(ps, "awaiting_prereg_approval")
    assert run["awaiting_approval"] is True
    assert run["current_stage"] == "awaiting_prereg_approval"
    assert run["approval"]["required"] is True
    assert run["approval"]["approval_scope"] == (
        "noncanonical_offline_research_execution_only"
    )
    assert str(run["approval"]["preregistration_packet_sha256"]).startswith("sha256:")


def test_awaiting_approval_rendered_in_html() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    lowered = render_html(data).lower()
    assert "awaiting prereg approval" in lowered
    assert "halted until" in lowered


# ---------------------------------------------------------------------------
# Blocked state shows the blocker reason.
# ---------------------------------------------------------------------------
def test_blocked_state_shows_reason() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    run = _run_by_status(ps, "blocked_or_invalid")
    assert run["blocked_reasons"]
    assert any("availability_blocked" in r for r in run["blocked_reasons"])


def test_blocked_reason_rendered_in_html() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    html = render_html(data)
    assert "availability_blocked:unsupported_timeframe" in html


# ---------------------------------------------------------------------------
# runner_invoked=false is displayed honestly, never as a real run.
# ---------------------------------------------------------------------------
def test_spine_only_runner_invoked_false_displayed() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    run = _run_by_status(ps, "complete_spine_only")
    assert run["runner_invoked"] is False
    assert run["spine_only"] is True
    assert run["execution_kind"] == "deterministic_spine_proof"


def test_spine_only_honest_label_present() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    ps = data["pipeline_state"]
    assert ps["spine_only"] is True
    expected = (
        "State spine / prereg approval contract only; real agent/runner adapter "
        "flow not yet complete."
    )
    assert ps["spine_only_label"] == expected
    html = render_html(data)
    assert expected in html
    assert "runner_invoked" in html
    # The spine proof is never presented as a real completed hypothesis run.
    lowered = html.lower()
    assert "complete · spine only" in lowered or "spine only" in lowered


# ---------------------------------------------------------------------------
# Fail-closed: missing directory, empty directory, malformed state.
# ---------------------------------------------------------------------------
def test_missing_pipeline_dir_fails_closed(tmp_path) -> None:
    ps = build_pipeline_state(repo_root=tmp_path, runs_root="does_not_exist")
    assert ps["available"] is False
    assert ps["status"] == "unavailable"
    assert ps["runs"] == []
    assert ps["totals"]["run_count"] == 0
    # The honest spine-only label is still available for the unavailable panel.
    assert "not yet complete" in ps["spine_only_label"]


def test_empty_pipeline_dir_fails_closed(tmp_path) -> None:
    (tmp_path / "runs").mkdir()
    ps = build_pipeline_state(repo_root=tmp_path, runs_root="runs")
    assert ps["available"] is False
    assert ps["status"] == "unavailable"


def test_malformed_state_is_blocked_or_invalid(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "LPIPE-badbadbadbadbad0"
    run_dir.mkdir(parents=True)
    (run_dir / "pipeline_state.json").write_text("{ not valid json", encoding="utf-8")
    ps = build_pipeline_state(repo_root=tmp_path, runs_root="runs")
    assert ps["available"] is True
    run = ps["runs"][0]
    assert run["available"] is False
    assert run["display_status"] == "blocked_or_invalid"
    assert "malformed" in run["invalid_reason"].lower()
    # A malformed run still renders (fail-closed) without crashing.
    data = build_cockpit_data(repo_root=REPO_ROOT)
    data["pipeline_state"] = ps
    html = render_html(data)
    assert "fail-closed" in html.lower()


def test_unavailable_panel_renders(tmp_path) -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    data["pipeline_state"] = build_pipeline_state(
        repo_root=tmp_path, runs_root="missing"
    )
    html = render_html(data)
    lowered = html.lower()
    assert "no committed pipeline run packets" in lowered
    assert "fails closed" in lowered


# ---------------------------------------------------------------------------
# Contract: the projection tracks the REAL orchestrator output shape.
# ---------------------------------------------------------------------------
def test_projection_matches_real_orchestrator_complete_run(tmp_path) -> None:
    from tools.lab_pipeline.orchestrator import (
        approval_template_for,
        run_pipeline,
    )
    from tools.lab_pipeline.state import write_json

    out = tmp_path / "out"
    req = tmp_path / "req.json"
    req.write_text(
        json.dumps(
            {
                "source_idea": "Contract-test idea on BTCUSDT 15m",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "requested_by": "Karl",
            }
        ),
        encoding="utf-8",
    )
    first = run_pipeline(request_path=req, output_root=out)
    template = approval_template_for(first.output_dir / "preregistration_packet.json")
    approval = tmp_path / "approval.json"
    write_json(approval, template)
    run_pipeline(request_path=req, approval_path=approval, output_root=out)

    ps = build_pipeline_state(repo_root=tmp_path, runs_root="out")
    assert ps["available"] is True
    run = ps["runs"][0]
    assert run["display_status"] == "complete_spine_only"
    assert run["runner_invoked"] is False
    assert run["current_stage"] == "complete"
    # Even from raw orchestrator output, no absolute path leaks into the surface.
    for artifact in run["artifacts"]:
        assert not artifact["path"].startswith("/")
        assert ":" not in artifact["path"]
        assert artifact["path"].startswith("out/")


def test_projection_matches_real_orchestrator_awaiting_and_blocked(tmp_path) -> None:
    from tools.lab_pipeline.orchestrator import run_pipeline

    out = tmp_path / "out"
    awaiting_req = tmp_path / "await.json"
    awaiting_req.write_text(
        json.dumps(
            {
                "source_idea": "Awaiting idea on BTCUSDT 1h",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "requested_by": "Karl",
            }
        ),
        encoding="utf-8",
    )
    blocked_req = tmp_path / "block.json"
    blocked_req.write_text(
        json.dumps(
            {
                "source_idea": "Blocked idea on unsupported timeframe",
                "symbol": "BTCUSDT",
                "timeframe": "3m",
                "requested_by": "Karl",
            }
        ),
        encoding="utf-8",
    )
    run_pipeline(request_path=awaiting_req, output_root=out)
    run_pipeline(request_path=blocked_req, output_root=out)

    ps = build_pipeline_state(repo_root=tmp_path, runs_root="out")
    statuses = {r["display_status"] for r in ps["runs"]}
    assert "awaiting_prereg_approval" in statuses
    assert "blocked_or_invalid" in statuses


# ---------------------------------------------------------------------------
# No executable control / no forbidden tokens introduced by the panel.
# ---------------------------------------------------------------------------
def test_pipeline_panel_has_no_controls_or_network() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    lowered = render_html(data).lower()
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


def test_no_pipeline_run_or_approve_controls_declared() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    decl = data["non_authority_declaration"]
    assert decl["reads_pipeline_state_only"] is True
    for control in (
        "invokes_pipeline_runner",
        "has_pipeline_run_button",
        "has_pipeline_approve_button",
        "has_pipeline_retry_button",
        "writes_prereg_approval_marker",
    ):
        assert decl[control] is False, control


def test_no_absolute_paths_in_pipeline_artifacts() -> None:
    ps = build_pipeline_state(repo_root=REPO_ROOT)
    for run in ps["runs"]:
        for artifact in run.get("artifacts", []):
            path = artifact["path"]
            assert not path.startswith("/")
            assert ":" not in path
            assert ".." not in path
            assert path.startswith("scratch/")


# ---------------------------------------------------------------------------
# Determinism + existing panels still render.
# ---------------------------------------------------------------------------
def test_pipeline_panel_is_deterministic() -> None:
    first = build_pipeline_state(repo_root=REPO_ROOT)
    second = build_pipeline_state(repo_root=REPO_ROOT)
    assert first == second


def test_render_with_pipeline_panel_is_deterministic() -> None:
    a = build_cockpit_data(repo_root=REPO_ROOT)
    b = build_cockpit_data(repo_root=REPO_ROOT)
    assert render_html(a) == render_html(b)
    assert render_markdown(a) == render_markdown(b)


def test_existing_static_panels_still_render() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    lowered = render_html(data).lower()
    # Pre-existing panels remain present alongside the new pipeline panel.
    for panel in (
        "lab overview",
        "pipeline runs",
        "candidate funnel",
        "strategy / hypothesis explorer",
        "coordinator state",
        "artifact drilldown",
    ):
        assert panel in lowered, panel
    # The SVG result charts are still emitted.
    assert render_html(data).count("<svg") >= 3


def test_markdown_has_pipeline_section() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    assert "## Pipeline runs / run-state" in md
    assert "runner_invoked" in md
    assert cockpit_model.PIPELINE_SPINE_ONLY_LABEL in md
