"""Deterministic read-only data model for the lab approval / gate queue.

The queue is a pure projection of committed repo truth:

- per-stage and overall **state** come verbatim from ``tools/lab_state`` (the
  merged coordinator state model); this surface never re-derives or re-ranks
  state and introduces no new state vocabulary;
- **gate / blocker facts** (operator gate pending, blocked validation, the
  ``no_candidate_review_packet_reason`` / ``blocked_review_reason`` carried by
  the generic robustness review reach contract, and
  ``candidate_review_packet_created`` *only when evidence exists*) are read from
  the same committed artifacts the resolver already consults.

It carries no clock, no git, no network, and no executable control, so two runs
over the same checkout produce byte-identical output. The queue *displays*
gates; it never executes one. It writes no approval, fires no notification,
writes no candidate lifecycle record, and declares no readiness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT, build_snapshot, _select_review_example
from tools.lab_state.run import SUBJECTS

SCHEMA_VERSION = "lab_approval_queue_surface_v1"

# Read-only visibility surface. Inherits the coordinator state model's
# non-authority declaration and adds the explicit gate / approval guarantees an
# operator queue must carry (package §6 "Additional forbidden approval
# behavior"): it shows pending gates but holds *no* execution authority.
APPROVAL_QUEUE_NON_AUTHORITY: dict[str, bool] = {
    **model.NON_AUTHORITY_DECLARATION,
    "renders_executable_control": False,
    "executes_approval": False,
    "writes_approval": False,
    "fires_notification": False,
    "executes_canonical_crossing": False,
    "executes_promotion": False,
    "declares_readiness": False,
    "has_approve_button": False,
    "has_reject_button": False,
    "has_promote_button": False,
    "has_run_button": False,
    "fetches_live_data": False,
    "auto_refreshes_from_network": False,
}

# Queue status vocabulary. Each entry maps deterministically from the coordinator
# overall state + operator-gate stage; it adds no new *state* vocabulary, it only
# buckets the existing states into operator-facing queue lanes.
QUEUE_STATUSES: tuple[str, ...] = (
    "operator_gate_pending",  # candidate ready for human review; decision held
    "no_go",                  # concluded NO-GO; nothing to gate
    "blocked_validation",     # a validation stage is blocked / failed
    "advisory_only",          # progress recorded, advisory, nothing to gate
    "not_actionable",         # not yet reached an actionable state
)

# Stage states that constitute a *blocker* on forward validation. These are
# exactly the blocking states from the coordinator vocabulary; nothing new.
_BLOCKER_STATES: frozenset[str] = frozenset(
    {
        "blocked",
        "oos_gate_fail",
        "oos_gate_blocked",
        "candidate_review_blocked",
    }
)

# Human-readable blocker kind per pipeline stage (legibility only).
_BLOCKER_KIND_BY_STAGE: dict[str, str] = {
    "experiment_run": "validation_blocker",
    "replay_normalization": "replay_blocker",
    "walkforward_oos_gate": "oos_gate_blocker",
    "robustness": "robustness_blocker",
    "candidate_review_reach": "candidate_review_blocker",
}


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Fail closed: an unreadable artifact yields no gate facts. State truth
        # (which fails closed to ``blocked`` in the resolver) is still surfaced,
        # so the queue never fabricates a candidate-ready gate.
        return None


def _stage_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["stage"]: s for s in snapshot["stages"]}


def _reason(reason: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize a contract reason object (``code`` / ``detail`` / ``source``).

    Returns ``None`` for an absent reason; never fabricates a code.
    """
    if not isinstance(reason, dict):
        return None
    return {
        "code": reason.get("code"),
        "detail": reason.get("detail", ""),
        "source": reason.get("source", ""),
    }


def _legacy_review_reason(review: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize older flat review records into queue-display reason objects."""
    if not isinstance(review, dict):
        return None
    status = str(review.get("status", "")).lower()
    if review.get("packet_generated") is False or status == "not_generated":
        return {
            "code": "NO_GO_PRIMARY_RISK_SCREEN_FAILED",
            "detail": str(review.get("reason", "No candidate-review packet generated.")),
            "source": str(review.get("source", "legacy_review_record")),
        }
    if status == "blocked":
        return {
            "code": "BLOCKED_RESULT_POPULATION_UNAVAILABLE",
            "detail": str(review.get("reason", "Candidate-review packet blocked.")),
            "source": str(review.get("source", "legacy_review_record")),
        }
    return None


def _review_record(
    subject: dict[str, Any], repo_root: Path
) -> dict[str, Any] | None:
    """Read the committed candidate-review reach record for this subject."""
    rel = subject.get("artifacts", {}).get("candidate_review_reach")
    if not rel:
        return None
    doc = _read_json(repo_root / rel)
    return _select_review_example(doc, subject.get("review_example_id"))


def _blockers(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate blocking stages (validation / replay / OOS / robustness / review).

    Surfaced in pipeline order; ``operator_gate`` is excluded because a held gate
    is a human decision surface, not a validation blocker.
    """
    blockers: list[dict[str, Any]] = []
    for stage in snapshot["stages"]:
        if stage["stage"] == "operator_gate":
            continue
        if stage["state"] in _BLOCKER_STATES:
            blockers.append(
                {
                    "stage": stage["stage"],
                    "blocker_kind": _BLOCKER_KIND_BY_STAGE.get(
                        stage["stage"], "validation_blocker"
                    ),
                    "state": stage["state"],
                    "reason_code": stage["reason_code"],
                    "detail": stage["detail"],
                }
            )
    return blockers


def _artifact_refs(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """De-duplicated artifact pointers across all stages, with present flags."""
    seen: dict[str, dict[str, Any]] = {}
    for stage in snapshot["stages"]:
        for ref in stage.get("artifact_refs", []):
            path = ref.get("path") or ""
            if not path or path in seen:
                continue
            seen[path] = {
                "role": ref.get("role"),
                "path": path,
                "present": bool(ref.get("present")),
            }
    for ref in snapshot.get("supplemental_artifact_refs", []):
        path = ref.get("path") or ""
        if not path or path in seen:
            continue
        seen[path] = {
            "role": ref.get("role"),
            "path": path,
            "present": bool(ref.get("present")),
        }
    return [seen[path] for path in sorted(seen)]


def _queue_status(
    overall_state: str, human_decision_pending: bool, blockers: list[dict[str, Any]]
) -> str:
    if human_decision_pending:
        return "operator_gate_pending"
    if overall_state == "no_go":
        return "no_go"
    if blockers:
        return "blocked_validation"
    if overall_state in {
        "robustness_advisory",
        "replay_checked",
        "experiment_complete",
        "reported",
    }:
        return "advisory_only"
    return "not_actionable"


def build_queue_entry(
    subject: dict[str, Any], repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    """Project one subject's coordinator snapshot into a queue entry (read-only)."""
    snapshot = build_snapshot(subject, repo_root)
    stages = _stage_map(snapshot)
    overall = snapshot["overall_state"]

    operator_gate = stages.get("operator_gate") or {}
    human_decision_pending = operator_gate.get("state") == "operator_gate_pending"

    review = _review_record(subject, repo_root)
    # candidate_review_packet_created is surfaced as True ONLY when the committed
    # evidence actually records it. A NO-GO / blocked review surfaces False.
    packet_created = bool(
        review.get("candidate_review_packet_created", False)
    ) if review else False
    no_packet_reason = (
        _reason(review.get("no_candidate_review_packet_reason")) if review else None
    )
    blocked_review_reason = (
        _reason(review.get("blocked_review_reason")) if review else None
    )
    legacy_reason = _legacy_review_reason(review)
    if legacy_reason and legacy_reason["code"].startswith("NO_GO_"):
        no_packet_reason = legacy_reason
    if legacy_reason and legacy_reason["code"].startswith("BLOCKED_"):
        blocked_review_reason = legacy_reason

    blockers = _blockers(snapshot)
    queue_status = _queue_status(overall, human_decision_pending, blockers)

    # The human decision surface: present only when the operator gate is pending.
    # The queue states the decision is *held*; it cannot make or record it.
    human_decision = None
    if human_decision_pending:
        human_decision = {
            "decision_kind": "operator_go_no_go_on_candidate_review_packet",
            "pending": True,
            "executable_here": False,
            "detail": operator_gate.get("detail", ""),
            "owner": "human operator via candidate lifecycle engine (separate)",
        }

    return {
        "subject_id": snapshot["subject_id"],
        "subject_label": snapshot["subject_label"],
        "overall_state": overall,
        "queue_status": queue_status,
        "actionable_by_operator": human_decision_pending,
        "human_decision_pending": human_decision_pending,
        "human_decision": human_decision,
        "candidate_review_packet_created": packet_created,
        "no_candidate_review_packet_reason": no_packet_reason,
        "blocked_review_reason": blocked_review_reason,
        "operator_gate": {
            "state": operator_gate.get("state", "not_started"),
            "reason_code": operator_gate.get("reason_code"),
            "detail": operator_gate.get("detail", ""),
        },
        "blockers": blockers,
        "artifact_refs": _artifact_refs(snapshot),
    }


def _queue_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate queue counts — every lane is listed, including zero buckets."""
    by_status = {status: 0 for status in QUEUE_STATUSES}
    for entry in entries:
        by_status[entry["queue_status"]] = by_status.get(
            entry["queue_status"], 0
        ) + 1

    operator_pending = by_status.get("operator_gate_pending", 0)
    candidate_ready = sum(
        1 for e in entries if e["candidate_review_packet_created"]
    )
    nothing_candidate_ready = operator_pending == 0 and candidate_ready == 0

    return {
        "subject_count": len(entries),
        "by_queue_status": by_status,
        "operator_gate_pending_count": operator_pending,
        "blocked_validation_count": by_status.get("blocked_validation", 0),
        "no_go_count": by_status.get("no_go", 0),
        "candidate_review_packet_created_count": candidate_ready,
        "nothing_candidate_ready": nothing_candidate_ready,
        "honest_state_note": (
            "No candidate is ready for human review and no operator gate is "
            "pending. The queue correctly shows only NO-GO / blocked / "
            "advisory-only items. This is the honest current state, not an error."
            if nothing_candidate_ready
            else "One or more human decision surfaces are pending; the operator "
            "must act through the candidate lifecycle engine. This queue cannot "
            "grant approval, promotion, or readiness."
        ),
    }


def _global_caveats() -> list[str]:
    return [
        "This queue displays pending human gates and blockers; it does not "
        "execute any gate.",
        "No approval, promotion, crossing, notification, candidate-lifecycle "
        "write, or readiness declaration is performed by this surface.",
        "candidate_review_packet_created is shown True only when committed "
        "evidence records it; a NO-GO / blocked review surfaces False.",
        "Blocked / NO-GO / advisory-only items are first-class queue contents, "
        "not failures of the queue.",
        "Any real operator decision requires separate human action through the "
        "human-gated candidate lifecycle engine; this queue cannot grant it.",
        "Ordering is deterministic display order only and confers no ranking, "
        "recommendation, readiness, or promotion authority.",
    ]


def build_queue_data(
    subjects: dict[str, dict[str, Any]] | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the full read-only approval / gate queue data model (deterministic).

    Subjects are projected in sorted key order so output is byte-stable.
    """
    subjects = SUBJECTS if subjects is None else subjects
    entries = [
        build_queue_entry(subjects[key], repo_root) for key in sorted(subjects)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_operator_gate_queue",
        "non_authority_declaration": dict(APPROVAL_QUEUE_NON_AUTHORITY),
        "edge_search_hold": model.EDGE_SEARCH_HOLD_NOTE,
        "queue_summary": _queue_summary(entries),
        "caveats": _global_caveats(),
        "entries": entries,
    }
