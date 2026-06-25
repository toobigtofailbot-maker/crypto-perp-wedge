"""Vocabulary-integrity tests for the lab coordinator state model."""

from __future__ import annotations

from tools.lab_state import model


def test_states_match_package_vocabulary() -> None:
    expected = {
        "not_started",
        "formalized",
        "experiment_complete",
        "blocked",
        "no_go",
        "replay_checked",
        "oos_gate_pass",
        "oos_gate_fail",
        "oos_gate_blocked",
        "robustness_advisory",
        "candidate_review_blocked",
        "candidate_review_not_created",
        "candidate_ready_for_human_review",
        "reported",
        "operator_gate_pending",
    }
    assert set(model.STATES) == expected
    # No accidental duplicates in the ordered vocabulary.
    assert len(model.STATES) == len(set(model.STATES))


def test_stages_are_ordered_pipeline() -> None:
    assert model.STAGES == (
        "idea_intake",
        "formalization",
        "experiment_run",
        "replay_normalization",
        "walkforward_oos_gate",
        "robustness",
        "candidate_review_reach",
        "reporting",
        "operator_gate",
    )


def test_every_stage_has_allowed_states_from_vocabulary() -> None:
    for stage in model.STAGES:
        allowed = model.STAGE_ALLOWED_STATES[stage]
        assert allowed, f"stage {stage} has no allowed states"
        for state in allowed:
            assert model.is_valid_state(state), f"{stage}: {state} not in vocabulary"


def test_oos_decision_enum_matches_repo_truth() -> None:
    # The OOS gate contract (PR #567) decision enum is repo truth.
    assert model.OOS_GATE_DECISIONS == ("pass", "fail", "blocked", "advisory_only")
    for decision, state in model.OOS_DECISION_TO_STATE.items():
        assert decision in model.OOS_GATE_DECISIONS
        assert model.is_valid_state(state)


def test_reason_codes_reuse_generic_review_contract_families() -> None:
    # No-packet and blocked codes come verbatim from PR #566's contract.
    assert "NO_GO_PRIMARY_RISK_SCREEN_FAILED" in model.NO_PACKET_REASON_CODES
    assert "BLOCKED_OOS_GATE_UNAVAILABLE" in model.BLOCKED_REASON_CODES
    # Every advertised reason code is in the combined set.
    for code in model.NO_PACKET_REASON_CODES + model.BLOCKED_REASON_CODES:
        assert code in model.ALL_REASON_CODES


def test_non_authority_declaration_is_read_only() -> None:
    decl = model.NON_AUTHORITY_DECLARATION
    assert decl["read_only"] is True
    assert decl["executes_transition"] is False
    assert decl["authorizes_edge_search"] is False
    assert decl["authorizes_paper_live_runtime"] is False


def test_edge_search_hold_note_present() -> None:
    assert "No further edge-search is authorized" in model.EDGE_SEARCH_HOLD_NOTE


def test_overall_precedence_states_are_declared_overall_states() -> None:
    # Every state the resolver's overall precedence can emit must be declared in
    # the contracted OVERALL_STATES (and therefore in state_model_contract.json).
    from tools.lab_state import resolver

    emittable = set(resolver._OVERALL_PRECEDENCE)
    # overall_state() also normalizes a NO-GO no-packet review into no_go/blocked.
    emittable.update({"no_go", "blocked"})
    undeclared = emittable - set(model.OVERALL_STATES)
    assert not undeclared, f"resolver can emit undeclared overall states: {undeclared}"


def test_candidate_review_blocked_is_declared_overall_state() -> None:
    assert "candidate_review_blocked" in model.OVERALL_STATES
