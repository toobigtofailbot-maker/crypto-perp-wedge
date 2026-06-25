"""Resolver tests over committed funding NO-GO / replay / OOS / robustness artifacts."""

from __future__ import annotations

from tools.lab_state import model
from tools.lab_state import resolver
from tools.lab_state.resolver import REPO_ROOT, build_snapshot
from tools.lab_state.run import SUBJECTS


def _stage(snapshot: dict, stage: str) -> dict:
    return next(s for s in snapshot["stages"] if s["stage"] == stage)


def test_funding_subject_resolves_to_no_go_end_to_end() -> None:
    snapshot = build_snapshot(SUBJECTS["funding_positioning_fade_no_go"], REPO_ROOT)
    assert snapshot["schema_version"] == model.SCHEMA_VERSION
    assert snapshot["subject_id"] == "H-FUNDING-RATE-POSITIONING-FADE-01"
    assert snapshot["overall_state"] == "no_go"

    assert _stage(snapshot, "formalization")["state"] == "formalized"
    assert _stage(snapshot, "experiment_run")["state"] == "experiment_complete"
    assert _stage(snapshot, "replay_normalization")["state"] == "replay_checked"
    # Dry-run-only OOS is not a rigorous pass.
    assert _stage(snapshot, "walkforward_oos_gate")["state"] == "oos_gate_blocked"
    assert _stage(snapshot, "robustness")["state"] == "robustness_advisory"
    review = _stage(snapshot, "candidate_review_reach")
    assert review["state"] == "candidate_review_not_created"
    assert review["reason_code"] == "NO_GO_PRIMARY_RISK_SCREEN_FAILED"
    assert _stage(snapshot, "reporting")["state"] == "reported"
    # No candidate produced => operator gate is not pending.
    assert _stage(snapshot, "operator_gate")["state"] == "not_started"


def test_oos_gate_fail_demo_surfaces_failed_gate() -> None:
    snapshot = build_snapshot(SUBJECTS["oos_gate_fail_demo"], REPO_ROOT)
    assert _stage(snapshot, "walkforward_oos_gate")["state"] == "oos_gate_fail"
    assert _stage(snapshot, "walkforward_oos_gate")["reason_code"] == "OOS_GATE_FAIL"
    assert snapshot["overall_state"] == "oos_gate_fail"


def test_snapshot_carries_non_authority_and_edge_search_hold() -> None:
    snapshot = build_snapshot(SUBJECTS["funding_positioning_fade_no_go"], REPO_ROOT)
    decl = snapshot["non_authority_declaration"]
    assert decl["executes_transition"] is False
    assert decl["authorizes_edge_search"] is False
    assert "No further edge-search is authorized" in snapshot["edge_search_hold"]


def test_packet_created_maps_to_human_review_and_operator_gate_pending() -> None:
    review = resolver.resolve_candidate_review_reach(
        review={
            "candidate_review_packet_created": True,
            "no_candidate_review_packet_reason": None,
            "blocked_review_reason": None,
        },
        refs=[],
    )
    assert review.state == "candidate_ready_for_human_review"
    gate = resolver.resolve_operator_gate(candidate_review_state=review.state)
    assert gate.state == "operator_gate_pending"


def test_blocked_review_maps_to_candidate_review_blocked() -> None:
    review = resolver.resolve_candidate_review_reach(
        review={
            "candidate_review_packet_created": False,
            "no_candidate_review_packet_reason": None,
            "blocked_review_reason": {
                "code": "BLOCKED_OOS_GATE_UNAVAILABLE",
                "detail": "OOS evidence unavailable.",
            },
        },
        refs=[],
    )
    assert review.state == "candidate_review_blocked"
    assert review.reason_code == "BLOCKED_OOS_GATE_UNAVAILABLE"


def test_missing_artifacts_fail_closed_not_fabricated() -> None:
    experiment = resolver.resolve_experiment_run(conclusion=None, refs=[])
    assert experiment.state == "not_started"
    assert experiment.reason_code == "STATE_ARTIFACT_MISSING"

    replay = resolver.resolve_replay_normalization(replay_summary=None, refs=[])
    assert replay.state == "not_started"


def test_resolver_rejects_state_outside_stage_vocabulary() -> None:
    import pytest

    with pytest.raises(resolver.LabStateResolverError):
        resolver._check(
            resolver.StageState(stage="reporting", state="oos_gate_pass")
        )


def test_overall_precedence_no_go_outranks_oos_blocked() -> None:
    stages = [
        resolver.StageState(stage="walkforward_oos_gate", state="oos_gate_blocked"),
        resolver.StageState(
            stage="candidate_review_reach",
            state="candidate_review_not_created",
            reason_code="NO_GO_PRIMARY_RISK_SCREEN_FAILED",
        ),
    ]
    assert resolver.overall_state(stages) == "no_go"


def test_candidate_review_blocked_can_be_overall_state() -> None:
    # A subject whose only non-routine outcome is a blocked candidate review must
    # surface candidate_review_blocked as the overall state (and it must be a
    # declared OVERALL_STATES value).
    stages = [
        resolver.StageState(stage="idea_intake", state="formalized"),
        resolver.StageState(stage="formalization", state="formalized"),
        resolver.StageState(stage="experiment_run", state="experiment_complete"),
        resolver.StageState(stage="replay_normalization", state="replay_checked"),
        resolver.StageState(stage="walkforward_oos_gate", state="oos_gate_pass"),
        resolver.StageState(stage="robustness", state="robustness_advisory"),
        resolver.StageState(
            stage="candidate_review_reach",
            state="candidate_review_blocked",
            reason_code="BLOCKED_OOS_GATE_UNAVAILABLE",
        ),
        resolver.StageState(stage="reporting", state="reported"),
        resolver.StageState(stage="operator_gate", state="not_started"),
    ]
    overall = resolver.overall_state(stages)
    assert overall == "candidate_review_blocked"
    assert overall in model.OVERALL_STATES


def test_unreadable_configured_artifact_blocks_not_not_started(tmp_path) -> None:
    # An existing-but-malformed JSON artifact must fail closed to blocked /
    # STATE_ARTIFACT_UNREADABLE, never be mistaken for "not reached".
    bad = tmp_path / "scratch" / "bad_replay.json"
    bad.parent.mkdir(parents=True)
    bad.write_text("{ this is : not valid json", encoding="utf-8")

    subject = {
        "subject_id": "UNREADABLE-DEMO",
        "subject_label": "unreadable_demo",
        "artifacts": {"replay_normalization": "scratch/bad_replay.json"},
    }
    snapshot = build_snapshot(subject, tmp_path)
    replay = _stage(snapshot, "replay_normalization")
    assert replay["state"] != "not_started"
    assert replay["state"] == "blocked"
    assert replay["reason_code"] == "STATE_ARTIFACT_UNREADABLE"


def test_unreadable_helper_distinguishes_missing_from_malformed(tmp_path) -> None:
    missing = resolver._read_json(tmp_path / "does_not_exist.json")
    assert missing.payload is None and missing.unreadable is False

    bad = tmp_path / "bad.json"
    bad.write_text("not json at all", encoding="utf-8")
    load = resolver._read_json(bad)
    assert load.payload is None and load.unreadable is True and load.error
