"""Tests for the static read-only lab product cockpit.

The cockpit is a deterministic projection of committed lab evidence: the merged
coordinator state model (``tools/lab_state`` via ``tools/lab_dashboard``) and the
concluded real-traffic four-hypothesis batch. These tests assert it shows the
full denominator, never fabricates a candidate-ready state, surfaces withheld
statistics honestly, shows real-traffic metrics only from committed evidence,
keeps artifact paths repo-relative, carries the non-authority boundary, renders
no executable control, and is byte-deterministic.
"""

from __future__ import annotations

import re

from tools.lab_cockpit import model as cockpit_model
from tools.lab_cockpit.model import build_cockpit_data
from tools.lab_cockpit.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT


def _hyp(data: dict, hypothesis_id: str) -> dict:
    return next(
        h
        for h in data["real_traffic_batch"]["hypotheses"]
        if h["hypothesis_id"] == hypothesis_id
    )


# ---------------------------------------------------------------------------
# Determinism.
# ---------------------------------------------------------------------------
def test_data_model_is_deterministic() -> None:
    first = build_cockpit_data(repo_root=REPO_ROOT)
    second = build_cockpit_data(repo_root=REPO_ROOT)
    assert first == second


def test_render_is_deterministic_across_two_builds() -> None:
    first = build_cockpit_data(repo_root=REPO_ROOT)
    second = build_cockpit_data(repo_root=REPO_ROOT)
    assert render_html(first) == render_html(second)
    assert render_markdown(first) == render_markdown(second)


def test_schema_and_surface_kind() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    assert data["schema_version"] == cockpit_model.SCHEMA_VERSION
    assert data["schema_version"] == "lab_product_cockpit_v1"
    assert data["surface_kind"] == "read_only_operator_cockpit"


# ---------------------------------------------------------------------------
# Full denominator, no winner-only view.
# ---------------------------------------------------------------------------
def test_full_denominator_visible() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    batch = data["real_traffic_batch"]
    assert batch["available"] is True
    assert batch["frozen_denominator_rows"] == 32
    assert batch["preserved_rows"] == 32
    assert batch["dropped_rows"] == 0
    assert batch["blocked_rows"] == 0
    # All four frozen hypotheses are present (full population, not winners).
    ids = {h["hypothesis_id"] for h in batch["hypotheses"]}
    assert ids == {
        "LAB-RT-HYP-001",
        "LAB-RT-HYP-002R",
        "LAB-RT-HYP-003R",
        "LAB-RT-HYP-004R",
    }
    # Every hypothesis keeps its full 8-row denominator.
    for h in batch["hypotheses"]:
        assert h["denominator"] == 8


def test_funnel_is_full_denominator_not_winner_only() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    funnel = data["candidate_funnel"]
    assert funnel["winner_only_view"] is False
    stages = {s["stage"]: s["count"] for s in funnel["stages"]}
    assert stages["frozen_hypotheses"] == 4
    assert stages["executed"] == 4


# ---------------------------------------------------------------------------
# No fabricated candidate-ready / GO-like state.
# ---------------------------------------------------------------------------
def test_no_candidate_ready_state_fabricated() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    batch = data["real_traffic_batch"]
    assert batch["go_like_evidence"] is False
    assert batch["totals"]["go_like_hypotheses"] == 0
    assert batch["totals"]["candidate_worthy_hypotheses"] == 0
    assert data["candidate_funnel"]["candidate_ready_count"] == 0
    stages = {s["stage"]: s["count"] for s in data["candidate_funnel"]["stages"]}
    assert stages["go_like_evidence"] == 0
    assert stages["candidate_ready"] == 0
    assert data["overview"]["candidate_state"]["candidate_ready_count"] == 0
    assert data["overview"]["candidate_state"]["candidate_admitted"] is False


def test_no_canonical_result_population_claimed() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    assert (
        data["real_traffic_batch"]["canonical_result_population_written"] is False
    )
    for h in data["real_traffic_batch"]["hypotheses"]:
        assert h["canonical_write"] is False


# ---------------------------------------------------------------------------
# Real-traffic metrics come only from committed source evidence.
# ---------------------------------------------------------------------------
def test_real_traffic_metrics_from_committed_evidence() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    h1 = _hyp(data, "LAB-RT-HYP-001")
    assert h1["positive_pnl_rows"] == 6
    assert round(h1["max_drawdown"], 6) == 0.770882
    assert h1["status"] == "non_promoting"

    h2 = _hyp(data, "LAB-RT-HYP-002R")
    assert h2["positive_pnl_rows"] == 8
    assert round(h2["median_pnl"], 3) == 56170.006
    assert h2["result_population_id"] == "RP-1413"
    assert h2["status"] == "non_promoting"

    h3 = _hyp(data, "LAB-RT-HYP-003R")
    assert h3["positive_pnl_rows"] == 0
    assert h3["median_pnl"] < 0
    # Clean NO-GO: no positive rows and a negative median.
    assert h3["status"] == "no_go"

    h4 = _hyp(data, "LAB-RT-HYP-004R")
    assert h4["positive_pnl_rows"] == 8
    assert h4["status"] == "non_promoting"


def test_hypothesis_names_and_readings_present() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    h2 = _hyp(data, "LAB-RT-HYP-002R")
    assert "RVOL" in (h2["name"] or "")
    # HYP-002R reading is the completion-package reading, not the earlier
    # "blocked before execution" batch-execute reading.
    assert h2["reading"]
    assert "blocked" not in h2["reading"].lower()


def test_pass_with_caution_context_preserved() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    h3 = _hyp(data, "LAB-RT-HYP-003R")
    h4 = _hyp(data, "LAB-RT-HYP-004R")
    assert any("caution" in f.lower() for f in h3["result_context_flags"])
    assert any("caution" in f.lower() for f in h4["result_context_flags"])


# ---------------------------------------------------------------------------
# Withheld statistics shown when source data is missing.
# ---------------------------------------------------------------------------
def test_withheld_statistics_displayed() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    rob = data["robustness"]
    assert rob["monte_carlo_run"] is False
    for stat in ("MonteCarlo", "Bootstrap", "PSR", "DSR", "MinTRL"):
        assert stat in rob["withheld_statistics"]
    assert data["wfo_oos"]["rigorous_oos_gate_pass"] is False


def test_withheld_statistics_rendered_in_html() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    assert "withheld" in html_out.lower()
    assert "not a rigorous oos gate pass" in html_out.lower()


# ---------------------------------------------------------------------------
# Artifact drilldown paths are repo-relative and non-secret.
# ---------------------------------------------------------------------------
def test_artifact_drilldown_paths_repo_relative() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    drill = data["artifact_drilldown"]
    assert len(drill) > 0
    for ref in drill:
        path = ref["path"]
        assert not path.startswith("/")
        assert ":" not in path  # no drive letters / absolute Windows paths
        assert ".." not in path
        assert path.startswith(("scratch/", "docs/"))
        assert "present" in ref
        assert "category" in ref
    # The authoritative rollup and synthesis are present.
    present = {ref["key"] for ref in drill if ref["present"]}
    assert "final_rollup" in present
    assert "batch_synthesis" in present


# ---------------------------------------------------------------------------
# Non-authority declaration + no executable controls.
# ---------------------------------------------------------------------------
def test_non_authority_declaration_present() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    decl = data["non_authority_declaration"]
    assert decl["read_only"] is True
    assert decl["static_only"] is True
    for control in (
        "renders_executable_control",
        "has_run_button",
        "has_approve_button",
        "has_promote_button",
        "has_retry_button",
        "has_candidate_control",
        "has_scheduler_toggle",
        "fetches_live_data",
        "auto_refreshes",
        "submits_forms",
        "contacts_runtime",
        "writes_canonical_result_population",
        "creates_candidate",
    ):
        assert decl[control] is False, control
    assert decl["authorizes_paper_live_runtime"] is False
    assert "No further edge-search is authorized" in data["edge_search_hold"]


def test_boundary_assertions_from_committed_evidence() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    boundary = data["boundary"]
    assert boundary["available"] is True
    a = boundary["assertions"]
    assert a["candidate_admitted"] is False
    assert a["canonical_crossing_performed"] is False
    assert a["promotion_readiness_created"] is False
    assert a["paper_live_authority_created"] is False
    assert a["runtime_contact_performed"] is False
    assert a["winner_only_pruning_performed"] is False


def test_rendered_html_has_no_controls_scripts_or_network() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    lowered = html_out.lower()
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
    ):
        assert forbidden not in lowered, forbidden
    # Core panels are present.
    assert "lab product cockpit" in lowered
    assert "candidate funnel" in lowered
    assert "strategy / hypothesis explorer" in lowered
    assert "read-only" in lowered


def test_rendered_html_is_richer_than_plain_tables() -> None:
    """The cockpit must be visually richer: it uses inline SVG chart panels."""
    data = build_cockpit_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    # Multiple inline SVG chart visualizations are present.
    assert html_out.count("<svg") >= 3
    # Chart primitives (bars) are emitted, not just tables.
    assert "<rect" in html_out


def test_rendered_markdown_covers_all_panels() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    for heading in (
        "# Lab Product Cockpit",
        "## Lab overview",
        "## Candidate funnel",
        "## Strategy / hypothesis explorer",
        "## Robustness / WFO / OOS",
        "## Activity / evidence timeline",
        "## Artifact drilldown",
        "## Boundary / non-authority",
    ):
        assert heading in md


# ---------------------------------------------------------------------------
# Timeline from committed metadata only.
# ---------------------------------------------------------------------------
def test_timeline_from_committed_pr_sequence() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    refs = [ev["ref"] for ev in data["timeline"]]
    assert refs == ["PR #600", "PR #606", "PR #608", "PR #609"]
    # Every timeline event points at a present committed source artifact.
    for ev in data["timeline"]:
        assert (REPO_ROOT / ev["source"]).exists()


# ---------------------------------------------------------------------------
# Coordinator projection stays consistent with the dashboard state model.
# ---------------------------------------------------------------------------
def test_coordinator_projection_reuses_state_model() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    coord = data["coordinator"]
    summary = coord["denominator_summary"]
    # Candidate-ready and operator-gate-pending remain zero lab-wide.
    assert summary["candidate_ready_count"] == 0
    assert summary["operator_gate_pending_count"] == 0
    assert summary["no_go_count"] >= 1
    assert coord["held_boundary_panel"]["available"] is True


# ---------------------------------------------------------------------------
# Fail-closed behaviour when the authoritative rollup is unavailable.
# ---------------------------------------------------------------------------
def test_batch_fails_closed_without_rollup(tmp_path) -> None:
    """With no committed rollup under the repo root, the batch is unavailable
    rather than fabricating hypotheses or metrics."""
    batch = cockpit_model.build_real_traffic_batch(repo_root=tmp_path)
    assert batch["available"] is False
    assert batch["hypotheses"] == []
    funnel = cockpit_model.build_candidate_funnel(batch)
    assert funnel["candidate_ready_count"] == 0


def test_no_absolute_or_secret_paths_in_html() -> None:
    data = build_cockpit_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    # No Windows drive-letter absolute paths leak into the rendered surface.
    assert not re.search(r"[A-Za-z]:\\\\", html_out)
    assert "C:/" not in html_out
