"""Tests for the read-only operator brief / weekly report surface.

The surface is a deterministic shaping of the read-only lab dashboard
projection (``tools/lab_dashboard``), itself a projection of the merged
coordinator state model (``tools/lab_state``). These tests assert it surfaces
completed / blocked / NO-GO runs and open decision surfaces, reports validation
status and withheld statistics, surfaces candidate-review readiness only when
evidence exists, carries the descriptive-only non-authority boundary, renders no
executable control / recommendation / auto-send, and is byte-deterministic.
"""

from __future__ import annotations

from tools.lab_reporting import report_model
from tools.lab_reporting.report_model import build_report_data
from tools.lab_reporting.render import (
    render_daily_brief_markdown,
    render_weekly_report_html,
    render_weekly_report_markdown,
)
from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT


def _data():
    return build_report_data(as_of="2026-06-25", period="2026-W26", repo_root=REPO_ROOT)


def _line(lines, subject_id):
    return next((line for line in lines if line["subject_id"] == subject_id), None)


def test_report_schema_and_labels() -> None:
    data = _data()
    assert data["schema_version"] == report_model.SCHEMA_VERSION
    assert data["surface_kind"] == "read_only_operator_brief_report"
    assert data["as_of"] == "2026-06-25"
    assert data["period"] == "2026-W26"


def test_unspecified_labels_default() -> None:
    data = build_report_data(repo_root=REPO_ROOT)
    assert data["as_of"] == report_model.UNSPECIFIED_LABEL
    assert data["period"] == report_model.UNSPECIFIED_LABEL


def test_no_go_subject_is_categorized_and_carries_caveats() -> None:
    data = _data()
    nogo = _line(data["no_gos"], "H-FUNDING-RATE-POSITIONING-FADE-01")
    assert nogo is not None
    assert nogo["overall_state"] == "no_go"
    assert nogo["evidence_class"] == "non_canonical"
    # NO-GO caveats are carried verbatim from the projection (not fabricated).
    assert any("drawdown" in c for c in nogo["no_go_caveats"])
    # A NO-GO is a conclusion, not a block.
    assert _line(data["blocked_runs"], "H-FUNDING-RATE-POSITIONING-FADE-01") is None


def test_completed_runs_include_reached_experiments() -> None:
    data = _data()
    ids = {line["subject_id"] for line in data["completed_runs"]}
    # Both committed subjects reached at least experiment_complete.
    assert "H-FUNDING-RATE-POSITIONING-FADE-01" in ids
    assert "OOS-GATE-FIXTURE-RP-2592" in ids


def test_validation_status_surfaces_oos_and_withheld() -> None:
    data = _data()
    funding = _line(data["validation_status"], "H-FUNDING-RATE-POSITIONING-FADE-01")
    assert funding["oos_gate_state"] == "oos_gate_blocked"
    assert funding["oos_evidence_status"] == "completed_dry_run_only"
    assert funding["withheld_statistics"] == ["PSR", "DSR", "MinTRL"]
    oos_fail = _line(data["validation_status"], "OOS-GATE-FIXTURE-RP-2592")
    assert oos_fail["oos_gate_state"] == "oos_gate_fail"


def test_withheld_statistics_aggregated_and_explicit() -> None:
    data = _data()
    # Withheld statistics are shown explicitly rather than fabricated.
    assert data["withheld_statistics"] == ["DSR", "MinTRL", "PSR"]


def test_candidate_review_readiness_only_when_evidence_exists() -> None:
    data = _data()
    # No committed subject has a candidate-review packet, so none is surfaced as
    # ready; each is recorded descriptively as having no evidence.
    assert data["counts"]["candidate_review_evidence"] == 0
    for c in data["candidate_review_readiness"]:
        assert c["has_candidate_review_evidence"] is False
        assert "No candidate-review packet evidence" in c["detail"]


def test_counts_use_full_population_by_overall_state() -> None:
    data = _data()
    by_state = data["counts"]["by_overall_state"]
    # Every overall state appears (including zero buckets): failed/blocked/NO-GO
    # are never hidden behind winners.
    assert set(by_state) == set(model.OVERALL_STATES)
    assert data["counts"]["no_gos"] >= 1


def test_non_authority_is_descriptive_only() -> None:
    data = _data()
    decl = data["non_authority_declaration"]
    assert decl["descriptive_only"] is True
    for guarantee in (
        "emits_recommendations",
        "ranks_as_authority",
        "applies_promotion_labels",
        "applies_decision_labels",
        "declares_readiness_verdict",
        "auto_sends",
        "fires_notifications",
        "integrates_scheduler",
        "suggests_edge_search",
    ):
        assert decl[guarantee] is False
    assert data["non_authority_declaration"]["authorizes_edge_search"] is False
    assert "No further edge-search is authorized" in data["edge_search_hold"]


def test_charting_is_deferred_table_based() -> None:
    data = _data()
    assert data["charting"]["enabled"] is False
    assert "deferred" in data["charting"]["note"].lower()


def test_rendered_outputs_have_no_controls_or_scripts() -> None:
    data = _data()
    for render in (
        render_daily_brief_markdown(data),
        render_weekly_report_markdown(data),
        render_weekly_report_html(data),
    ):
        lowered = render.lower()
        for forbidden in (
            "<script",
            "<button",
            "<form",
            "<input",
            "onclick",
            'http-equiv="refresh"',
        ):
            assert forbidden not in lowered


def test_rendered_outputs_are_descriptive_not_directive() -> None:
    data = _data()
    brief = render_daily_brief_markdown(data)
    weekly = render_weekly_report_markdown(data)
    # Descriptive banner present; no recommendation/promotion verbs emitted.
    for render in (brief, weekly):
        assert "Descriptive only" in render
        lowered = render.lower()
        # Directive phrasings must not appear (the non-authority disclaimer
        # legitimately contains the word "recommendation").
        for forbidden in ("we recommend", "we suggest", "promote to", "should run"):
            assert forbidden not in lowered


def test_daily_brief_lists_core_sections() -> None:
    data = _data()
    brief = render_daily_brief_markdown(data)
    for heading in (
        "## Completed runs",
        "## Blocked runs",
        "## NO-GOs",
        "## Open decision surfaces",
        "## Validation status",
        "## Candidate-review readiness",
        "## Withheld statistics and caveats",
    ):
        assert heading in brief


def test_weekly_report_lists_full_state_population() -> None:
    data = _data()
    weekly = render_weekly_report_markdown(data)
    for state in model.OVERALL_STATES:
        assert f"`{state}`" in weekly


def test_render_is_deterministic_across_two_builds() -> None:
    first = _data()
    second = _data()
    assert first == second
    assert render_daily_brief_markdown(first) == render_daily_brief_markdown(second)
    assert render_weekly_report_markdown(first) == render_weekly_report_markdown(second)
    assert render_weekly_report_html(first) == render_weekly_report_html(second)
