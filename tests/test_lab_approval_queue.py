"""Tests for the read-only lab approval / gate queue surface.

The queue is a deterministic projection of the merged coordinator state model
(``tools/lab_state``) and the committed artifacts it references. These tests
assert it surfaces operator-gate-pending / blocked-validation / NO-GO items,
exposes ``no_candidate_review_packet_reason`` and ``blocked_review_reason``
verbatim, shows ``candidate_review_packet_created`` True only when committed
evidence records it, carries the non-authority boundary, renders no executable
control, and is byte-deterministic.
"""

from __future__ import annotations

from tools.lab_approval_queue import queue_model
from tools.lab_approval_queue.queue_model import (
    QUEUE_STATUSES,
    build_queue_data,
    build_queue_entry,
)
from tools.lab_approval_queue.render import render_html, render_markdown
from tools.lab_state.resolver import REPO_ROOT
from tools.lab_state.run import SUBJECTS


def _entry(data: dict, subject_id: str) -> dict:
    return next(e for e in data["entries"] if e["subject_id"] == subject_id)


def test_queue_data_schema_and_subjects() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    assert data["schema_version"] == queue_model.SCHEMA_VERSION
    assert data["surface_kind"] == "read_only_operator_gate_queue"
    ids = {e["subject_id"] for e in data["entries"]}
    assert "H-FUNDING-RATE-POSITIONING-FADE-01" in ids
    assert "OOS-GATE-FIXTURE-RP-2592" in ids
    assert "WP-RESEARCH-FUNDING-CARRY-02" in ids
    assert "HISTORICAL-CANONICAL-EVIDENCE" in ids


def test_summary_lists_every_queue_status_including_zero_buckets() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    summary = data["queue_summary"]
    assert summary["subject_count"] == len(SUBJECTS)
    # Every queue status appears (including zero buckets) so blocked / NO-GO
    # lanes are never hidden behind an empty actionable lane.
    assert set(summary["by_queue_status"]) == set(QUEUE_STATUSES)


def test_honest_current_state_is_nothing_candidate_ready() -> None:
    """The committed evidence is NO-GO / blocked only; the queue must say so."""
    data = build_queue_data(repo_root=REPO_ROOT)
    summary = data["queue_summary"]
    assert summary["operator_gate_pending_count"] == 0
    assert summary["candidate_review_packet_created_count"] == 0
    assert summary["nothing_candidate_ready"] is True
    assert "honest current state" in summary["honest_state_note"]
    # NO-GO and blocked items are present as first-class queue contents.
    assert summary["no_go_count"] >= 1
    assert summary["blocked_validation_count"] >= 1


def test_no_go_entry_exposes_no_candidate_review_packet_reason() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    entry = _entry(data, "H-FUNDING-RATE-POSITIONING-FADE-01")
    assert entry["queue_status"] == "no_go"
    assert entry["actionable_by_operator"] is False
    assert entry["candidate_review_packet_created"] is False
    reason = entry["no_candidate_review_packet_reason"]
    assert reason is not None
    assert reason["code"] == "NO_GO_PRIMARY_RISK_SCREEN_FAILED"
    assert "drawdown" in reason["detail"]
    # Nothing produced => no human decision surface.
    assert entry["human_decision"] is None


def test_legacy_no_go_entries_do_not_create_gate_pending() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    for subject_id in (
        "WP-RESEARCH-FUNDING-CARRY-01",
        "WP-RESEARCH-FUNDING-CARRY-02",
    ):
        entry = _entry(data, subject_id)
        assert entry["queue_status"] == "no_go"
        assert entry["candidate_review_packet_created"] is False
        assert entry["human_decision_pending"] is False
        assert entry["no_candidate_review_packet_reason"] is not None


def test_blocked_entry_exposes_blocked_review_reason_and_blockers() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    entry = _entry(data, "OOS-GATE-FIXTURE-RP-2592")
    assert entry["queue_status"] == "blocked_validation"
    reason = entry["blocked_review_reason"]
    assert reason is not None
    assert reason["code"] == "BLOCKED_OOS_GATE_UNAVAILABLE"
    # OOS gate failure and candidate-review block are both surfaced as blockers.
    kinds = {b["blocker_kind"] for b in entry["blockers"]}
    assert "oos_gate_blocker" in kinds
    assert "candidate_review_blocker" in kinds


def test_legacy_blocked_entries_surface_blocked_review_reason() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    for subject_id in (
        "WP-RESEARCH-EDGE-SMA-FAMILY-01",
        "WP-RESEARCH-ORB-EXIT-RESPEC-01",
    ):
        entry = _entry(data, subject_id)
        assert entry["queue_status"] == "blocked_validation"
        assert entry["blocked_review_reason"] is not None
        assert entry["blocked_review_reason"]["code"] == (
            "BLOCKED_RESULT_POPULATION_UNAVAILABLE"
        )


def test_candidate_ready_path_only_when_evidence_records_it() -> None:
    """A packet-created review (committed contract example) surfaces a held gate.

    Bound directly via ``build_queue_entry`` so the default queue stays honestly
    empty of candidate-ready items; this exercises the evidence-backed path over
    the already-committed generic review contract.
    """
    subject = {
        "subject_id": "SMA-PACKET-SHAPE",
        "subject_label": "sma_crossover_packet_shape",
        "review_example_id": "sma_review_packet_shape",
        "artifacts": {
            "candidate_review_reach": (
                "scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/"
                "generic_review_contract.json"
            ),
        },
    }
    entry = build_queue_entry(subject, REPO_ROOT)
    assert entry["candidate_review_packet_created"] is True
    assert entry["queue_status"] == "operator_gate_pending"
    assert entry["actionable_by_operator"] is True
    # The human decision is surfaced as pending but explicitly not executable here.
    hd = entry["human_decision"]
    assert hd is not None
    assert hd["pending"] is True
    assert hd["executable_here"] is False


def test_non_authority_declares_no_gate_execution() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    decl = data["non_authority_declaration"]
    for flag in (
        "executes_approval",
        "writes_approval",
        "fires_notification",
        "executes_canonical_crossing",
        "executes_promotion",
        "declares_readiness",
        "has_approve_button",
        "has_reject_button",
        "has_promote_button",
        "writes_candidate_lifecycle",
        "renders_executable_control",
    ):
        assert decl[flag] is False
    assert decl["read_only"] is True
    assert decl["authorizes_edge_search"] is False
    assert "No further edge-search is authorized" in data["edge_search_hold"]


def test_rendered_html_has_no_controls_or_scripts() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    html_out = render_html(data)
    lowered = html_out.lower()
    for forbidden in (
        "<script",
        "<button",
        "<form",
        "<input",
        "onclick",
        'http-equiv="refresh"',
    ):
        assert forbidden not in lowered
    assert "Queue summary" in html_out
    assert "does not execute them" in html_out


def test_markdown_lists_full_status_population() -> None:
    data = build_queue_data(repo_root=REPO_ROOT)
    md = render_markdown(data)
    assert "Queue summary" in md
    for status in QUEUE_STATUSES:
        assert f"`{status}`" in md


def test_render_is_deterministic_across_two_builds() -> None:
    first = build_queue_data(repo_root=REPO_ROOT)
    second = build_queue_data(repo_root=REPO_ROOT)
    assert first == second
    assert render_html(first) == render_html(second)
    assert render_markdown(first) == render_markdown(second)


def test_artifact_refs_dedup_sorted_and_flagged() -> None:
    entry = build_queue_entry(
        SUBJECTS["funding_positioning_fade_no_go"], REPO_ROOT
    )
    paths = [ref["path"] for ref in entry["artifact_refs"]]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths))
    assert all("present" in ref for ref in entry["artifact_refs"])
