"""Deterministic read-only data model for the operator brief / weekly report.

The model is a pure shaping of the read-only lab dashboard data model
(``tools/lab_dashboard``), which is itself a deterministic projection of the
merged coordinator state model (``tools/lab_state``). This surface therefore:

- never re-derives or re-ranks **state** — every per-subject and overall state
  comes verbatim from the dashboard projection, which takes it verbatim from
  ``tools.lab_state.resolver.build_snapshot``;
- introduces **no new state vocabulary**;
- is **descriptive only** — it emits no recommendation, ranking-as-authority,
  promotion label, decision label, readiness verdict, edge-search suggestion,
  auto-send, or notification.

Determinism: the model reads no clock, no git, and no network. The brief / report
``as_of`` and ``period`` are explicit descriptive labels supplied by the caller
(default ``"unspecified"``), so two builds over the same checkout and the same
labels produce byte-identical output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.lab_dashboard.data_model import build_dashboard_data
from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT

SCHEMA_VERSION = "lab_operator_brief_report_v1"

UNSPECIFIED_LABEL = "unspecified"

# Read-only reporting surface. Inherits the dashboard's non-authority
# declaration (which already inherits the coordinator state model's) and adds
# the explicit reporting guarantees required by package §5.
REPORTING_NON_AUTHORITY: dict[str, bool] = {
    **model.NON_AUTHORITY_DECLARATION,
    "descriptive_only": True,
    "emits_recommendations": False,
    "ranks_as_authority": False,
    "applies_promotion_labels": False,
    "applies_decision_labels": False,
    "declares_readiness_verdict": False,
    "auto_sends": False,
    "fires_notifications": False,
    "integrates_scheduler": False,
    "suggests_edge_search": False,
}

# Overall states that mean a completed experiment run was reached. Mirrors the
# dashboard's legibility bucket; these are buckets only, never a ranking.
_COMPLETED_EXPERIMENT_STATES: frozenset[str] = frozenset(
    {
        "experiment_complete",
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
        "no_go",
    }
)

# Overall states that mean the subject is blocked on a legibility obstacle
# (missing/unreadable artifact, unavailable input). NO-GO is a *conclusion*, not
# a block, so it is reported separately.
_BLOCKED_OVERALL_STATES: frozenset[str] = frozenset({"blocked"})

# Open operator decision surfaces: a human decision is pending. These are
# surfaced descriptively; the surface never makes the decision.
_OPEN_DECISION_STATES: frozenset[str] = frozenset(
    {"candidate_ready_for_human_review", "operator_gate_pending"}
)


def _label(value: str | None) -> str:
    text = (value or "").strip()
    return text or UNSPECIFIED_LABEL


def _is_stage_blocked(view: dict[str, Any]) -> bool:
    return any(stage.get("state") == "blocked" for stage in view.get("stages", []))


def _subject_line(view: dict[str, Any]) -> dict[str, Any]:
    """One descriptive line item shared by brief and report sections."""
    oos = view["oos_gate_status"]
    review = view["candidate_review_status"]
    return {
        "subject_id": view["subject_id"],
        "subject_label": view["subject_label"],
        "overall_state": view["overall_state"],
        "evidence_class": view["evidence_class"],
        "oos_gate_state": oos["state"],
        "oos_gate_reason_code": oos["reason_code"],
        "oos_evidence_status": oos["oos_evidence_status"],
        "replay_state": view["replay_status"]["state"],
        "robustness_state": view["robustness_status"]["state"],
        "candidate_review_state": review["state"],
        "candidate_review_reason_code": review["reason_code"],
        "reporting_state": view["reporting_status"]["state"],
        "operator_gate_state": view["operator_gate_status"]["state"],
        "withheld_statistics": list(view["withheld_statistics"]),
        "no_go_caveats": list(view["no_go_caveats"]),
    }


def _validation_status(view: dict[str, Any]) -> dict[str, Any]:
    """Descriptive validation legibility (replay + OOS gate), never a verdict."""
    oos = view["oos_gate_status"]
    return {
        "subject_id": view["subject_id"],
        "replay_state": view["replay_status"]["state"],
        "replay_reason_code": view["replay_status"]["reason_code"],
        "oos_gate_state": oos["state"],
        "oos_gate_reason_code": oos["reason_code"],
        "oos_evidence_status": oos["oos_evidence_status"],
        "robustness_state": view["robustness_status"]["state"],
        "withheld_statistics": list(view["robustness_status"]["withheld_statistics"]),
    }


def _candidate_review_readiness(view: dict[str, Any]) -> dict[str, Any]:
    """Surface candidate-review readiness **only when evidence exists**.

    When a candidate-review packet has actually been produced (state
    ``candidate_ready_for_human_review``) this records that a human review is
    pending — it is *not* a registration, ranking, readiness verdict, or
    promotion. In every other case it records, descriptively, that there is no
    candidate-review evidence to surface and why.
    """
    review = view["candidate_review_status"]
    has_evidence = review["state"] == "candidate_ready_for_human_review"
    if has_evidence:
        detail = (
            "A candidate-review packet exists; a human review is pending. This "
            "is not a registration, ranking, readiness verdict, or promotion."
        )
    else:
        detail = (
            "No candidate-review packet evidence to surface "
            f"(state `{review['state']}`)."
        )
    return {
        "subject_id": view["subject_id"],
        "has_candidate_review_evidence": has_evidence,
        "candidate_review_state": review["state"],
        "candidate_review_reason_code": review["reason_code"],
        "detail": detail,
    }


def _artifact_links(view: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "subject_id": view["subject_id"],
            "role": ref["role"],
            "path": ref["path"],
            "present": bool(ref["present"]),
        }
        for ref in view["artifact_drilldown"]
    ]


def _section_subjects(
    views: list[dict[str, Any]], predicate
) -> list[dict[str, Any]]:
    return [_subject_line(v) for v in views if predicate(v)]


def build_report_data(
    *,
    as_of: str | None = None,
    period: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the read-only brief/report data model (deterministic).

    ``as_of`` / ``period`` are descriptive labels only (no clock is read). The
    underlying dashboard projects subjects in sorted key order, so output is
    stable.
    """
    dashboard = build_dashboard_data(repo_root=repo_root)
    views = dashboard["subjects"]
    summary = dashboard["denominator_summary"]

    completed_runs = _section_subjects(
        views, lambda v: v["overall_state"] in _COMPLETED_EXPERIMENT_STATES
    )
    blocked_runs = _section_subjects(
        views,
        lambda v: v["overall_state"] in _BLOCKED_OVERALL_STATES
        or _is_stage_blocked(v),
    )
    no_gos = _section_subjects(views, lambda v: v["overall_state"] == "no_go")
    open_decision_surfaces = _section_subjects(
        views, lambda v: v["overall_state"] in _OPEN_DECISION_STATES
    )

    validation_status = [_validation_status(v) for v in views]
    candidate_review_readiness = [_candidate_review_readiness(v) for v in views]
    artifact_links = [link for v in views for link in _artifact_links(v)]

    withheld_statistics = sorted(
        {
            stat
            for v in views
            for stat in v["withheld_statistics"]
        }
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_operator_brief_report",
        "as_of": _label(as_of),
        "period": _label(period),
        "non_authority_declaration": dict(REPORTING_NON_AUTHORITY),
        "edge_search_hold": dashboard["edge_search_hold"],
        "counts": {
            "subjects": summary["subject_count"],
            "completed_runs": len(completed_runs),
            "blocked_runs": len(blocked_runs),
            "no_gos": len(no_gos),
            "open_decision_surfaces": len(open_decision_surfaces),
            "candidate_review_evidence": sum(
                1 for c in candidate_review_readiness if c["has_candidate_review_evidence"]
            ),
            "by_overall_state": dict(summary["by_overall_state"]),
        },
        "completed_runs": completed_runs,
        "blocked_runs": blocked_runs,
        "no_gos": no_gos,
        "open_decision_surfaces": open_decision_surfaces,
        "validation_status": validation_status,
        "candidate_review_readiness": candidate_review_readiness,
        "artifact_links": artifact_links,
        "withheld_statistics": withheld_statistics,
        "caveats": list(dashboard["caveats"]),
        "charting": {
            "enabled": False,
            "note": (
                "Charting deferred: weekly report is table-based static output "
                "only; no safe dependency-light static-chart path is adopted."
            ),
        },
    }
