"""Canonical read-only research-lab coordinator state vocabulary.

This module defines the *names* used by every operator surface (dashboard,
brief/report surface, approval queue, scheduler shell) so they read from one
coherent state model rather than inventing separate status vocabularies.

It contains no behavior that executes a transition. The vocabulary here is
composed from existing merged repo truth:

- replay normalization contract (PR #565),
- walk-forward / OOS gate contract (PR #567, ``gate_decision`` enum),
- generic robustness review reach contract (PR #566, output fields and
  reason-code families),
- candidate lifecycle engine human-gated boundary (downstream consumer).

No new status names are invented. See
``docs/research/LAB_COORDINATOR_STATE_MODEL.md``.
"""

from __future__ import annotations

from typing import Final


SCHEMA_VERSION: Final = "lab_coordinator_state_model_v1"

# ---------------------------------------------------------------------------
# Ordered lab pipeline stages.
# ---------------------------------------------------------------------------
# These mirror the lifecycle described in the package objective:
#   idea intake -> formalization -> experiment run -> replay normalization
#   -> walk-forward/OOS gate -> robustness -> candidate-review reach
#   -> reporting -> operator gate.
STAGES: Final[tuple[str, ...]] = (
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

# ---------------------------------------------------------------------------
# Canonical state vocabulary (read-only). Exactly the set named in the package
# objective; each maps to an existing repo-truth vocabulary.
# ---------------------------------------------------------------------------
STATES: Final[tuple[str, ...]] = (
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
)

# Which states a given stage is allowed to resolve to. This is a legibility
# constraint only; it does not authorize any transition.
STAGE_ALLOWED_STATES: Final[dict[str, tuple[str, ...]]] = {
    "idea_intake": ("not_started", "formalized", "blocked"),
    "formalization": ("not_started", "formalized", "blocked"),
    "experiment_run": (
        "not_started",
        "experiment_complete",
        "no_go",
        "blocked",
    ),
    "replay_normalization": ("not_started", "replay_checked", "blocked"),
    "walkforward_oos_gate": (
        "not_started",
        "oos_gate_pass",
        "oos_gate_fail",
        "oos_gate_blocked",
        "blocked",
    ),
    "robustness": ("not_started", "robustness_advisory", "blocked"),
    "candidate_review_reach": (
        "not_started",
        "candidate_review_blocked",
        "candidate_review_not_created",
        "candidate_ready_for_human_review",
        "blocked",
    ),
    "reporting": ("not_started", "reported", "blocked"),
    "operator_gate": ("not_started", "operator_gate_pending", "blocked"),
}

# Terminal/overall states the snapshot may surface for the whole subject.
OVERALL_STATES: Final[tuple[str, ...]] = (
    "not_started",
    "formalized",
    "experiment_complete",
    "replay_checked",
    "oos_gate_fail",
    "oos_gate_blocked",
    "candidate_review_blocked",
    "robustness_advisory",
    "no_go",
    "blocked",
    "candidate_ready_for_human_review",
    "operator_gate_pending",
    "reported",
)

# ---------------------------------------------------------------------------
# Reason codes. Re-used verbatim from the generic robustness review reach
# contract (PR #566) plus the OOS gate decision enum (PR #567). State-model
# specific codes are namespaced ``STATE_*`` and only describe legibility, never
# a judgement about a strategy.
# ---------------------------------------------------------------------------
NO_PACKET_REASON_CODES: Final[tuple[str, ...]] = (
    "NO_GO_PRIMARY_RISK_SCREEN_FAILED",
    "NO_GO_DRAWDOWN_SCREEN_FAILED",
    "NO_GO_RETURN_SHARPE_SCREEN_FAILED",
    "NO_GO_DENOMINATOR_INTEGRITY_FAILED",
)
BLOCKED_REASON_CODES: Final[tuple[str, ...]] = (
    "BLOCKED_REPLAY_CONTRACT_UNAVAILABLE",
    "BLOCKED_OOS_GATE_UNAVAILABLE",
    "BLOCKED_DENOMINATOR_MANIFEST_UNAVAILABLE",
    "BLOCKED_RESULT_POPULATION_UNAVAILABLE",
    "BLOCKED_REQUIRED_STAT_INPUTS_UNAVAILABLE",
    "BLOCKED_PARALLEL_SEQUENCE",
)
# OOS gate decision enum, repo truth from the OOS gate contract.
OOS_GATE_DECISIONS: Final[tuple[str, ...]] = (
    "pass",
    "fail",
    "blocked",
    "advisory_only",
)
# State-model legibility codes (never a strategy judgement).
STATE_REASON_CODES: Final[tuple[str, ...]] = (
    "STATE_ARTIFACT_MISSING",
    "STATE_ARTIFACT_UNREADABLE",
    "STATE_STAGE_NOT_REACHED",
    "STATE_FORMALIZED_FROM_STATUS_ENTRY",
    "STATE_EXPERIMENT_DENOMINATOR_PRESERVED",
    "STATE_REPLAY_NORMALIZED",
    "STATE_OOS_DRY_RUN_ONLY",
    "STATE_ROBUSTNESS_ADVISORY_ONLY",
    "STATE_REPORTED_FROM_SYNTHESIS",
    "STATE_OPERATOR_GATE_HELD",
    "STATE_NO_CANDIDATE_PRODUCED",
)

ALL_REASON_CODES: Final[frozenset[str]] = frozenset(
    NO_PACKET_REASON_CODES
    + BLOCKED_REASON_CODES
    + tuple(f"OOS_GATE_{d.upper()}" for d in OOS_GATE_DECISIONS)
    + STATE_REASON_CODES
)

# Maps the repo-truth OOS gate decision to the coordinator stage state.
OOS_DECISION_TO_STATE: Final[dict[str, str]] = {
    "pass": "oos_gate_pass",
    "fail": "oos_gate_fail",
    "blocked": "oos_gate_blocked",
    "advisory_only": "oos_gate_blocked",
}

# Explicit non-authority declaration carried by every snapshot.
NON_AUTHORITY_DECLARATION: Final[dict[str, bool]] = {
    "read_only": True,
    "executes_transition": False,
    "writes_canonical_evidence": False,
    "writes_candidate_lifecycle": False,
    "executes_canonical_crossing": False,
    "ranks_or_recommends": False,
    "authorizes_edge_search": False,
    "authorizes_paper_live_runtime": False,
}

# Required edge-search hold note (package §7).
EDGE_SEARCH_HOLD_NOTE: Final = (
    "No further edge-search is authorized by the coordinator state model. "
    "Strategy generation/search remains held until separate operator "
    "authorization."
)


def is_valid_state(state: str) -> bool:
    """Return True if ``state`` is in the canonical vocabulary."""
    return state in STATES


def is_valid_stage(stage: str) -> bool:
    """Return True if ``stage`` is a recognized pipeline stage."""
    return stage in STAGES


def state_allowed_for_stage(stage: str, state: str) -> bool:
    """Return True if ``state`` is a legible resolution for ``stage``."""
    return state in STAGE_ALLOWED_STATES.get(stage, ())
