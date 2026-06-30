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


# ---------------------------------------------------------------------------
# WP-LAB-DASHBOARD-GAP-COMPLETE-01: new panel tests
# ---------------------------------------------------------------------------

def test_schema_version_bumped_to_v2() -> None:
    """Dashboard schema version updated to reflect new panel additions."""
    assert data_model.SCHEMA_VERSION == "lab_results_dashboard_v2"
    result = build_dashboard_data(repo_root=REPO_ROOT)
    assert result["schema_version"] == "lab_results_dashboard_v2"


def test_baseline_proof_panel_present_and_non_authoritative() -> None:
    """Baseline proof panel exists and carries non-authority label."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    assert "baseline_proof_panel" in data
    panel = data["baseline_proof_panel"]
    assert panel["panel_kind"] == "baseline_fixture_proof"
    assert "non_authority_note" in panel
    assert "not ranking" in panel["non_authority_note"].lower() or \
           "not readiness" in panel["non_authority_note"].lower() or \
           "non-promotable" in panel["non_authority_note"].lower()


def test_baseline_proof_panel_payloads_populated() -> None:
    """Baseline payload catalog (PR #583) is surfaced: 3 non-promotable baselines."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    bp = data["baseline_proof_panel"]["baseline_payloads"]
    assert bp["available"] is True
    assert bp["baseline_count"] == 3
    assert bp["contract_only_route_used"] is True
    assert len(bp["baselines"]) == 3
    for b in bp["baselines"]:
        assert b["non_promotable"] is True
        assert b["construction_payload"] is True
        assert b["candidate_eligible"] is False
        # All baselines expect crossing rejection by construction.
        assert b["expected_crossing_result"] == "reject_by_construction"


def test_baseline_proof_panel_gate_posture_no_fabrication() -> None:
    """Gate expectations (PR #584) surfaced; no numeric override or fabrication."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    ge = data["baseline_proof_panel"]["gate_expectations"]
    assert ge["available"] is True
    gr = ge["global_rule"]
    assert gr.get("numeric_override_allowed") is False
    assert gr.get("fabricated_metrics_allowed") is False
    # WFO/OOS and MC/robustness posture per baseline (withheld/insufficient language).
    assert len(ge["per_baseline"]) == 3
    for b in ge["per_baseline"]:
        assert b["numeric_override_allowed"] is False
        assert b["retuning_allowed"] is False
        # Every baseline expects construction-rejection at crossing.
        assert b["crossing_expected"] == "reject_by_construction"


def test_baseline_proof_panel_guard_hardened() -> None:
    """Non-promotable crossing guard (PR #585) is confirmed hardened."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    gv = data["baseline_proof_panel"]["guard_validation"]
    assert gv["available"] is True
    assert gv["guard_implemented"] is True
    assert gv["non_promotable_crossing_guard_hardened"] is True
    assert gv["lab_declared_finished"] is False
    assert gv["test_result"] == "passed"


def test_baseline_proof_panel_agent_loop_no_candidate() -> None:
    """Agent loop exercise (PR #586): fixture-only, no candidate, crossing rejected."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    al = data["baseline_proof_panel"]["agent_loop_exercise"]
    assert al["available"] is True
    assert al["fixture_only"] is True
    assert al["non_promotable"] is True
    assert al["candidate_eligible"] is False
    assert al["canonical_result_population_written"] is False
    assert al["candidate_registry_written"] is False
    # No-candidate result.
    nc = al["no_candidate_result"]
    assert nc["status"] == "no_candidate"
    assert nc["missing_or_unavailable_metrics_fabricated"] is False
    # Crossing rejection.
    cr = al["crossing_rejection"]
    assert cr["status"] == "rejected"
    assert cr["reason_code"] == "reject_by_construction"
    assert cr["crossing_action_authorized"] is False
    assert cr["first_real_crossing_remains_karl_gated"] is True
    # Agent did not recommend rescue, retuning, or ranking.
    beh = al["agent_loop_behavior"]
    for flag in (
        "recommended_rescue",
        "recommended_retuning",
        "ranked_as_edge",
        "proposed_promotion",
        "proposed_readiness",
        "proposed_paper_live",
        "proposed_real_crossing",
    ):
        assert beh[flag] is False, f"agent_loop_behavior.{flag} must be False"


def test_baseline_proof_panel_provenance_trace_not_finished() -> None:
    """Provenance trace (PR #587) shows what was proven and what was NOT proven."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    pv = data["baseline_proof_panel"]["provenance_trace"]
    assert pv["available"] is True
    assert pv["core_pipe_fixture_proven"] is True
    assert pv["no_candidate_result_observed"] is True
    assert pv["crossing_rejection_observed"] is True
    # These are explicitly NOT proven (fixture/plumbing only).
    assert pv["real_candidate_crossing_completed"] is False
    assert pv["full_always_on_factory_completed"] is False
    assert pv["lab_declared_finished_without_qualification"] is False
    # No authorization granted.
    assert pv["edge_search_authorized_here"] is False
    assert pv["canonical_writes_authorized_here"] is False
    assert pv["paper_live_runtime_go_gated"] is True
    assert pv["held_b_requires_real_edge_search_or_candidate_flow"] is True
    assert len(pv["baseline_sequence_prs"]) == 4


def test_held_boundary_panel_present_and_non_authoritative() -> None:
    """Held-boundary panel exists, carries non-authority label, is available."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    assert "held_boundary_panel" in data
    hb = data["held_boundary_panel"]
    assert hb["panel_kind"] == "held_boundary_deferred_b"
    assert hb["available"] is True
    assert "not authorized" in hb["non_authority_note"].lower()


def test_held_boundary_panel_content() -> None:
    """Held-boundary panel surfaces deferred-B, GO-candidate, and GO-gated items."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    hb = data["held_boundary_panel"]
    # Deferred-B items.
    assert len(hb["held_b_until_real_research_flow"]) > 0
    # GO-candidate items.
    assert len(hb["requires_real_go_candidate"]) > 0
    # GO-gated protected paths.
    assert len(hb["go_gated_protected"]) > 0
    # GO-gated items include paper/live/runtime.
    go_gated_text = " ".join(hb["go_gated_protected"]).lower()
    assert any(
        kw in go_gated_text
        for kw in ("paper", "live", "runtime", "oms", "broker", "exchange")
    )


def test_rendered_html_includes_baseline_proof_sections() -> None:
    """HTML render includes baseline proof and held-boundary panels."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    lowered = html_out.lower()
    assert "baseline fixture proof" in lowered
    assert "non-promotable" in lowered
    assert "held-boundary" in lowered or "held_boundary" in lowered or "deferred-b" in lowered
    # Still no executable controls.
    for forbidden in ("<script", "<button", "<form", "<input", "onclick"):
        assert forbidden not in lowered


def test_rendered_markdown_includes_baseline_proof_sections() -> None:
    """Markdown render includes baseline proof and held-boundary panels."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    assert "Baseline fixture proof" in md
    assert "Gate posture" in md
    assert "Agent/baseline loop activity" in md
    assert "Data/provenance trace" in md
    assert "Held-boundary" in md


def test_baseline_proof_artifact_refs_all_present() -> None:
    """All PR #583-#587 scratch artifacts referenced in the panel are present."""
    data = build_dashboard_data(repo_root=REPO_ROOT)
    refs = data["baseline_proof_panel"]["artifact_refs"]
    for key, ref in refs.items():
        assert ref["present"] is True, (
            f"Expected artifact '{key}' at '{ref['path']}' to be present on main"
        )
    # Also check the held_boundary artifact directly.
    hb = data["held_boundary_panel"]
    assert hb["artifact_ref"]["present"] is True
