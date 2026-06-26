"""Tests for the unified read-only operator-surface index.

The index is a deterministic *composition* of the already-merged read-only
surfaces (coordinator state model, results dashboard, operator brief / weekly
report, approval / gate queue, inert scheduler shell). These tests assert it
links to every surface, re-states each surface's honest summary verbatim,
introduces no new state vocabulary, carries the non-authority boundary and the
edge-search hold, renders no executable control, surfaces the honest
"nothing candidate-ready" current state, and is byte-deterministic.
"""

from __future__ import annotations

from tools.lab_approval_queue.queue_model import build_queue_data
from tools.lab_dashboard.data_model import build_dashboard_data
from tools.lab_operator_surface import index_model
from tools.lab_operator_surface.index_model import build_index_data
from tools.lab_operator_surface.render import render_html, render_markdown
from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT


def _tile(data: dict, key: str) -> dict:
    return next(t for t in data["surfaces"] if t["key"] == key)


def test_index_schema_and_surface_kind() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    assert data["schema_version"] == index_model.SCHEMA_VERSION
    assert data["surface_kind"] == "read_only_operator_surface_index"


def test_index_links_every_required_surface() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    keys = {t["key"] for t in data["surfaces"]}
    assert keys == {
        "coordinator_state",
        "results_dashboard",
        "daily_brief",
        "weekly_report",
        "approval_queue",
        "scheduler_shell",
    }
    # Each surface links to a real module path and a research doc.
    for tile in data["surfaces"]:
        assert tile["module"].startswith("tools/")
        assert tile["doc"].startswith("docs/research/")
        assert tile["cli"].startswith("python -m tools.")


def test_related_docs_present_on_disk() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    roles = {ref["role"] for ref in data["related_docs"]}
    assert {
        "state_model",
        "dashboard",
        "brief_report",
        "approval_queue",
        "scheduler_shell",
    } <= roles
    # The five dependency docs are committed and must resolve as present.
    for ref in data["related_docs"]:
        if ref["role"] != "integration":
            assert ref["present"] is True, ref["path"]


def test_batch_boundary_matches_dashboard_denominator() -> None:
    """State / denominator are taken verbatim from the dashboard; never re-derived."""
    data = build_index_data(repo_root=REPO_ROOT)
    dashboard = build_dashboard_data(repo_root=REPO_ROOT)
    summary = dashboard["denominator_summary"]
    batch = data["batch_boundary"]
    assert batch["subject_count"] == summary["subject_count"]
    assert batch["by_overall_state"] == summary["by_overall_state"]
    assert batch["no_go_count"] == summary["no_go_count"]
    # No new state vocabulary: every batch state key is in the canonical model.
    assert set(batch["by_overall_state"]).issubset(set(model.OVERALL_STATES))


def test_honest_state_taken_verbatim_from_approval_queue() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    queue = build_queue_data(repo_root=REPO_ROOT)
    qsum = queue["queue_summary"]
    honest = data["honest_state"]
    assert honest["nothing_candidate_ready"] == qsum["nothing_candidate_ready"]
    assert honest["note"] == qsum["honest_state_note"]
    # Committed evidence is NO-GO / blocked only: nothing candidate-ready.
    assert honest["nothing_candidate_ready"] is True
    assert honest["candidate_ready_count"] == 0
    assert honest["operator_gate_pending_count"] == 0


def test_batch_boundary_reflects_coverage_gap_closure() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    batch = data["batch_boundary"]
    assert batch["subject_count"] == 8
    assert batch["no_go_count"] == 3
    assert batch["blocked_count"] == 2
    assert batch["candidate_ready_count"] == 0
    assert batch["operator_gate_pending_count"] == 0


def test_scheduler_tile_is_inert_and_default_off() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    sched = _tile(data, "scheduler_shell")["summary"]
    assert sched["all_default_off"] is True
    assert sched["enabled_flags"] == []
    assert sched["dry_run_all_actions_noop"] is True
    assert sched["dry_run_executed_any_action"] is False


def test_non_authority_declares_no_execution_control() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    decl = data["non_authority_declaration"]
    for flag in (
        "renders_executable_control",
        "has_run_button",
        "has_approve_button",
        "has_reject_button",
        "has_promote_button",
        "has_retry_button",
        "has_scheduler_toggle",
        "fetches_live_data",
        "auto_refreshes",
        "ranks_or_recommends",
        "introduces_new_state_vocabulary",
        "enables_autonomous_behavior",
        "executes_transition",
        "writes_candidate_lifecycle",
    ):
        assert decl[flag] is False
    assert decl["read_only"] is True
    assert "No further edge-search is authorized" in data["edge_search_hold"]


def test_labels_are_descriptive_only() -> None:
    data = build_index_data(as_of="2026-06-25", period="2026-W26", repo_root=REPO_ROOT)
    assert data["as_of"] == "2026-06-25"
    assert data["period"] == "2026-W26"
    # Default labels fall back to "unspecified" (no clock read).
    default = build_index_data(repo_root=REPO_ROOT)
    assert default["as_of"] == "unspecified"
    assert default["period"] == "unspecified"


def test_rendered_html_has_no_controls_or_scripts() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    lowered = html_out.lower()
    for forbidden in (
        "<script",
        "<button",
        "<form",
        "<input",
        "onclick",
        'http-equiv="refresh"',
        "meta refresh",
    ):
        assert forbidden not in lowered
    assert "Unified Index" in html_out
    assert "not a control panel" in html_out


def test_markdown_lists_surfaces_and_honest_state() -> None:
    data = build_index_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    assert "Unified Index" in md
    assert "Honest current state" in md
    assert "Batch boundary" in md
    for tile in data["surfaces"]:
        assert tile["title"] in md


def test_render_is_deterministic_across_two_builds() -> None:
    first = build_index_data(as_of="D", period="P", repo_root=REPO_ROOT)
    second = build_index_data(as_of="D", period="P", repo_root=REPO_ROOT)
    assert first == second
    assert render_html(first) == render_html(second)
    assert render_markdown(first) == render_markdown(second)
