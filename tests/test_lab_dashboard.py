"""Tests for the read-only lab results dashboard surface.

The dashboard is a deterministic projection of the merged coordinator state
model (``tools/lab_state``) and the committed artifacts it references. These
tests assert it shows the full denominator, surfaces failed/blocked/NO-GO
states and withheld statistics, carries the non-authority boundary, renders no
executable control, and is byte-deterministic.
"""

from __future__ import annotations

from tools.lab_dashboard import data_model
from tools.lab_dashboard.data_model import build_dashboard_data, build_subject_view
from tools.lab_dashboard.render import render_html, render_markdown
from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT
from tools.lab_state.run import SUBJECTS


def _subject(data: dict, subject_id: str) -> dict:
    return next(s for s in data["subjects"] if s["subject_id"] == subject_id)


def test_dashboard_data_schema_and_subjects() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    assert data["schema_version"] == data_model.SCHEMA_VERSION
    assert data["surface_kind"] == "read_only_operator_visibility"
    # The committed coordinator-state subjects plus historical evidence bundles
    # are projected.
    ids = {s["subject_id"] for s in data["subjects"]}
    assert "H-FUNDING-RATE-POSITIONING-FADE-01" in ids
    assert "H-FUNDING-FADE-RISKMANAGED-01" in ids
    assert "OOS-GATE-FIXTURE-RP-2592" in ids
    assert "WP-RESEARCH-FUNDING-CARRY-02" in ids
    assert "HISTORICAL-CANONICAL-EVIDENCE" in ids


def test_denominator_summary_shows_full_population_not_winners_only() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    summary = data["denominator_summary"]
    assert summary["subject_count"] == len(SUBJECTS)
    # Every overall state appears (including zero buckets) so failed/blocked
    # counts are never hidden behind winners.
    assert set(summary["by_overall_state"]) == set(model.OVERALL_STATES)
    # NO-GO subject is counted as such.
    assert summary["no_go_count"] >= 1
    # Distinct Result Population sets are de-duplicated, not double counted.
    trials = summary["trial_denominator_over_distinct_sets"]
    assert trials["planned"] == 36
    assert trials["complete"] == 36
    assert trials["failed"] == 0


def test_funding_subject_surfaces_no_go_caveats_and_withheld_stats() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    view = _subject(data, "H-FUNDING-RATE-POSITIONING-FADE-01")
    assert view["overall_state"] == "no_go"
    assert view["evidence_class"] == "non_canonical"
    # Withheld statistics are shown explicitly, never fabricated.
    assert view["withheld_statistics"] == ["PSR", "DSR", "MinTRL"]
    assert view["robustness_status"]["withheld_statistics"] == ["PSR", "DSR", "MinTRL"]
    # NO-GO caveats are derived from the conclusion's primary failure.
    assert any("drawdown" in c for c in view["no_go_caveats"])
    # Dry-run-only OOS is surfaced as blocked, not a pass.
    assert view["oos_gate_status"]["state"] == "oos_gate_blocked"
    assert view["oos_gate_status"]["oos_evidence_status"] == "completed_dry_run_only"
    # Full denominator breakdown present.
    assert view["denominator"]["preserved"] is True
    assert view["denominator"]["planned"] == 36
    # Result Populations enumerated for drill-down.
    rp_ids = {rp["result_population_id"] for rp in view["result_populations"]}
    assert rp_ids == {"RP-2009", "RP-7592"}


def test_riskmanaged_funding_subject_is_operator_visible_without_readiness() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    view = _subject(data, "H-FUNDING-FADE-RISKMANAGED-01")
    assert view["overall_state"] == "no_go"
    assert view["evidence_class"] == "non_canonical"
    assert view["denominator"]["preserved"] is True
    assert view["denominator"]["planned"] == 108
    assert view["denominator"]["complete"] == 108
    assert view["result_populations"] == []
    assert view["candidate_review_status"]["state"] == "candidate_review_not_created"
    assert view["operator_gate_status"]["state"] == "not_started"
    assert any("Stage-1" in c or "funding" in c for c in view["no_go_caveats"])


def test_oos_fail_subject_surfaces_failed_gate() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    view = _subject(data, "OOS-GATE-FIXTURE-RP-2592")
    assert view["oos_gate_status"]["state"] == "oos_gate_fail"
    assert view["oos_gate_status"]["reason_code"] == "OOS_GATE_FAIL"
    assert view["overall_state"] == "oos_gate_fail"


def test_historical_gap_subjects_are_visible_without_candidate_readiness() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    funding_retry = _subject(data, "WP-RESEARCH-FUNDING-CARRY-02")
    assert funding_retry["overall_state"] == "no_go"
    assert funding_retry["denominator"]["planned"] == 36
    assert funding_retry["denominator"]["complete"] == 36
    rp_ids = {rp["result_population_id"] for rp in funding_retry["result_populations"]}
    assert {"RP-2009", "RP-7592"} <= rp_ids

    canonical = _subject(data, "HISTORICAL-CANONICAL-EVIDENCE")
    assert canonical["overall_state"] == "experiment_complete"
    paths = {ref["path"] for ref in canonical["artifact_drilldown"]}
    assert "research/candidate_registry.jsonl" in paths
    assert "research/result_populations/RP-7520.result_population.json" in paths

    summary = data["denominator_summary"]
    assert summary["candidate_ready_count"] == 0
    assert summary["operator_gate_pending_count"] == 0


def test_artifact_drilldown_dedups_and_flags_presence() -> None:
    view = build_subject_view(SUBJECTS["funding_positioning_fade_no_go"], REPO_ROOT)
    paths = [ref["path"] for ref in view["artifact_drilldown"]]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert all("present" in ref for ref in view["artifact_drilldown"])


def test_non_authority_declares_no_executable_controls() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    decl = data["non_authority_declaration"]
    assert decl["renders_executable_control"] is False
    for control in (
        "has_run_button",
        "has_approve_button",
        "has_promote_button",
        "has_retry_button",
        "has_scheduler_toggle",
        "fetches_live_data",
        "auto_refreshes_from_network",
    ):
        assert decl[control] is False
    assert decl["authorizes_edge_search"] is False
    assert "No further edge-search is authorized" in data["edge_search_hold"]


def test_rendered_html_has_no_controls_or_scripts() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    lowered = html_out.lower()
    for forbidden in ("<script", "<button", "<form", "<input", "onclick", "http-equiv=\"refresh\""):
        assert forbidden not in lowered
    # Surfaces the denominator and a NO-GO caveat banner.
    assert "Denominator summary" in html_out
    assert "NO-GO caveats" in html_out


def test_render_is_deterministic_across_two_builds() -> None:
    first = build_dashboard_data(repo_root=REPO_ROOT)
    second = build_dashboard_data(repo_root=REPO_ROOT)
    assert first == second
    assert render_html(first) == render_html(second)
    assert render_markdown(first) == render_markdown(second)


def test_markdown_lists_full_state_population() -> None:
    data = build_dashboard_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    assert "Denominator summary" in md
    # Every overall state is listed, so blocked/failed buckets are visible.
    for state in model.OVERALL_STATES:
        assert f"`{state}`" in md
