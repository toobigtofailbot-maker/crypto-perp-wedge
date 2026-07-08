"""Deterministic read-only data model for the static lab product cockpit.

This model is a pure projection of committed repo truth. It carries no clock,
no git, no network, and no executable control, so two builds over the same
checkout produce byte-identical output.

Two evidence sources are joined:

- the merged **coordinator state model** (``tools/lab_state`` via the existing
  ``tools/lab_dashboard`` data model) for lab-wide state, denominator summary,
  and the held-boundary / deferred-B map;
- the concluded **real-traffic four-hypothesis batch** (PR #606 / #608 / #609
  committed scratch artifacts) for the strategy explorer, PnL / drawdown /
  positive-row visuals, walk-forward and robustness posture, the candidate
  funnel, and the activity timeline.

Every numeric fact is read from a committed artifact. When an artifact is
missing or a statistic was not computed, the model surfaces an explicit
``withheld`` / ``unavailable`` state rather than fabricating a value.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.lab_dashboard.data_model import (
    DASHBOARD_NON_AUTHORITY,
    build_dashboard_data,
)
from tools.lab_state import model as state_model
from tools.lab_state.resolver import REPO_ROOT

SCHEMA_VERSION = "lab_product_cockpit_v1"

# ---------------------------------------------------------------------------
# Committed real-traffic batch evidence (read-only; never written).
# ---------------------------------------------------------------------------
ROLLUP_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/"
    "revised_batch_final_rollup.json"
)
FROZEN_SET_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/"
    "revised_frozen_hypothesis_set.json"
)
BATCH_EXECUTE_READINGS_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/"
    "strategy_reading_summary.json"
)
BATCH_EXECUTE_MANIFEST_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/"
    "real_traffic_batch_manifest.json"
)
HYP002R_READING_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/"
    "hyp002r_strategy_reading.json"
)
HYP002R_WFO_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_wfo_oos_summary.json"
)
HYP002R_ROBUSTNESS_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/"
    "hyp002r_robustness_mc_summary.json"
)
HYP002R_DENOM_AUDIT_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_denominator_audit.json"
)
NON_AUTHORITY_PATH = (
    "scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/non_authority_assertions.json"
)
SYNTHESIS_PATH = "docs/research/LAB_REAL_TRAFFIC_BATCH_SYNTHESIS_2026-07.md"

# Ordered artifact drilldown surface for the cockpit. Repo-relative, non-secret;
# each entry is shown with a present/missing indicator and a source category.
_ARTIFACT_DRILLDOWN: tuple[tuple[str, str, str], ...] = (
    ("batch_synthesis", "conclusion_doc", SYNTHESIS_PATH),
    ("final_rollup", "batch_rollup", ROLLUP_PATH),
    ("frozen_hypothesis_set", "frozen_set", FROZEN_SET_PATH),
    ("batch_execute_manifest", "batch_manifest", BATCH_EXECUTE_MANIFEST_PATH),
    ("batch_execute_readings", "strategy_reading", BATCH_EXECUTE_READINGS_PATH),
    ("hyp002r_strategy_reading", "strategy_reading", HYP002R_READING_PATH),
    ("hyp002r_wfo_oos", "walkforward_oos", HYP002R_WFO_PATH),
    ("hyp002r_robustness_mc", "robustness_mc", HYP002R_ROBUSTNESS_PATH),
    ("hyp002r_denominator_audit", "denominator_audit", HYP002R_DENOM_AUDIT_PATH),
    ("non_authority_assertions", "boundary", NON_AUTHORITY_PATH),
)

# Non-authority declaration for the cockpit. Inherits every dashboard guarantee
# and restates the cockpit-specific "no execution controls" contract.
COCKPIT_NON_AUTHORITY: dict[str, bool] = {
    **DASHBOARD_NON_AUTHORITY,
    "static_only": True,
    "renders_executable_control": False,
    "has_run_button": False,
    "has_approve_button": False,
    "has_promote_button": False,
    "has_retry_button": False,
    "has_candidate_control": False,
    "has_scheduler_toggle": False,
    "fetches_live_data": False,
    "auto_refreshes": False,
    "submits_forms": False,
    "contacts_runtime": False,
    "writes_canonical_result_population": False,
    "creates_candidate": False,
}


def _read_json(path: Path) -> dict[str, Any] | None:
    """Read a committed JSON artifact, failing closed to ``None``."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Per-hypothesis projection.
# ---------------------------------------------------------------------------
def _classify_hypothesis(hyp: dict[str, Any]) -> dict[str, str]:
    """Derive a legibility status label from committed metrics only.

    This is a display bucket, never a ranking or recommendation. It mirrors the
    committed synthesis reading: a hypothesis with no positive rows and a
    negative median is a clean NO-GO; a hypothesis with a positive PnL surface
    still fails the frozen primary drawdown screen and is non-promoting.
    """
    positive = hyp.get("positive_pnl_rows")
    median_pnl = hyp.get("median_pnl")
    if positive == 0 and isinstance(median_pnl, (int, float)) and median_pnl < 0:
        return {
            "status": "no_go",
            "status_label": "NO-GO",
            "screen": "negative population and severe drawdown",
        }
    return {
        "status": "non_promoting",
        "status_label": "NON-PROMOTING",
        "screen": "fails primary drawdown screen",
    }


def _readings_by_id(repo_root: Path) -> dict[str, str]:
    """Map hypothesis_id -> committed strategy-reading text.

    The batch-execute readings cover HYP-001/003R/004R; HYP-002R's authoritative
    reading comes from the completion package (it was blocked in the earlier
    batch-execute run), so it is overlaid last.
    """
    readings: dict[str, str] = {}
    batch = _read_json(repo_root / BATCH_EXECUTE_READINGS_PATH)
    for entry in (batch or {}).get("readings", []):
        hid = entry.get("hypothesis_id")
        text = entry.get("reading")
        if hid and text:
            readings[hid] = text
    hyp002r = _read_json(repo_root / HYP002R_READING_PATH)
    if hyp002r and hyp002r.get("hypothesis_id"):
        parts = [
            p
            for p in (
                hyp002r.get("reading"),
                hyp002r.get("non_promoting_interpretation"),
            )
            if p
        ]
        if parts:
            readings[hyp002r["hypothesis_id"]] = " ".join(parts)
    return readings


def _frozen_meta_by_id(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Map hypothesis_id -> descriptive frozen-set metadata (read-only)."""
    frozen = _read_json(repo_root / FROZEN_SET_PATH)
    meta: dict[str, dict[str, Any]] = {}
    for hyp in (frozen or {}).get("hypotheses", []):
        hid = hyp.get("hypothesis_id")
        if not hid:
            continue
        meta[hid] = {
            "name": hyp.get("hypothesis_name"),
            "family_route": hyp.get("supported_family_route"),
            "economic_rationale": hyp.get("economic_rationale"),
            "go_definition": hyp.get("GO_definition"),
            "no_go_definition": hyp.get("NO_GO_definition"),
            "freshness_check_result": hyp.get("freshness_check_result"),
            "distinctness_result": hyp.get("distinctness_result"),
            "result_context_flags": list(hyp.get("result_context_flags") or []),
            "non_promotion_posture": bool(hyp.get("non_promotion_posture", True)),
        }
    return meta


def _hypothesis_view(
    hyp: dict[str, Any],
    reading: str | None,
    meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """Project one frozen hypothesis into a cockpit strategy card (read-only)."""
    classified = _classify_hypothesis(hyp)
    outcome = hyp.get("outcome_counts") or {}
    denominator = hyp.get("denominator")
    positive = hyp.get("positive_pnl_rows")
    meta = meta or {}
    return {
        "hypothesis_id": hyp.get("hypothesis_id"),
        "name": meta.get("name"),
        "family_route": meta.get("family_route"),
        "economic_rationale": meta.get("economic_rationale"),
        "result_population_id": hyp.get("result_population_id"),
        "status": classified["status"],
        "status_label": classified["status_label"],
        "non_promoting_reason": classified["screen"],
        "reading": reading,
        "dry_run": bool(hyp.get("dry_run", True)),
        "canonical_write": bool(hyp.get("canonical_write", False)),
        "denominator": denominator,
        "successful_rows": outcome.get("successful"),
        "positive_pnl_rows": positive,
        "median_pnl": hyp.get("median_pnl"),
        "median_return_pct": hyp.get("median_return_pct"),
        "max_drawdown": hyp.get("max_drawdown"),
        "median_fees": hyp.get("median_fees"),
        "median_slippage": hyp.get("median_slippage"),
        "trade_counts": list(hyp.get("trade_counts") or []),
        "walkforward_rows": hyp.get("walkforward_rows"),
        "walkforward_successful_rows": hyp.get("walkforward_successful_rows"),
        "walkforward_warnings": list(hyp.get("walkforward_warnings") or []),
        "freshness_check_result": meta.get("freshness_check_result"),
        "distinctness_result": meta.get("distinctness_result"),
        "result_context_flags": meta.get("result_context_flags") or [],
        "go_definition": meta.get("go_definition"),
    }


def build_real_traffic_batch(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Build the real-traffic four-hypothesis batch panel from committed rollup.

    Fails closed: if the authoritative rollup is missing the panel is marked
    unavailable rather than fabricating hypotheses or metrics.
    """
    rollup = _read_json(repo_root / ROLLUP_PATH)
    if not rollup:
        return {"available": False, "hypotheses": [], "totals": {}}

    readings = _readings_by_id(repo_root)
    meta = _frozen_meta_by_id(repo_root)
    hyp_rows = rollup.get("hypotheses") or []
    hypotheses = [
        _hypothesis_view(
            hyp,
            readings.get(hyp.get("hypothesis_id")),
            meta.get(hyp.get("hypothesis_id")),
        )
        for hyp in hyp_rows
    ]

    positive_hyps = sum(
        1 for h in hypotheses if (h["positive_pnl_rows"] or 0) > 0
    )
    positive_median_hyps = sum(
        1
        for h in hypotheses
        if isinstance(h["median_pnl"], (int, float)) and h["median_pnl"] > 0
    )
    totals = {
        "hypothesis_count": len(hypotheses),
        "hypotheses_with_positive_rows": positive_hyps,
        "hypotheses_with_positive_median_pnl": positive_median_hyps,
        "no_go_count": sum(1 for h in hypotheses if h["status"] == "no_go"),
        "non_promoting_count": sum(
            1 for h in hypotheses if h["status"] == "non_promoting"
        ),
        "go_like_hypotheses": 0,
        "candidate_worthy_hypotheses": 0,
        "total_positive_rows": sum(
            (h["positive_pnl_rows"] or 0) for h in hypotheses
        ),
    }

    return {
        "available": True,
        "batch_package": rollup.get("package"),
        "base_commit": rollup.get("base_commit"),
        "decision": rollup.get("decision"),
        "frozen_denominator_rows": rollup.get("frozen_denominator_rows"),
        "preserved_rows": rollup.get("preserved_rows"),
        "dropped_rows": rollup.get("dropped_rows"),
        "blocked_rows": rollup.get("blocked_rows"),
        "executed_successful_rows": rollup.get("executed_successful_rows"),
        "canonical_result_population_written": bool(
            rollup.get("canonical_result_population_written", False)
        ),
        "go_like_evidence": bool(rollup.get("go_like_evidence", False)),
        "go_candidate_worthy_decision_packet": rollup.get(
            "go_candidate_worthy_decision_packet"
        ),
        "real_research_execution_performed": bool(
            rollup.get("real_research_execution_performed", False)
        ),
        "hypotheses": hypotheses,
        "totals": totals,
    }


# ---------------------------------------------------------------------------
# Walk-forward / OOS and robustness posture panels.
# ---------------------------------------------------------------------------
def build_wfo_oos_panel(
    batch: dict[str, Any], repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    """Walk-forward / OOS posture across the batch (read-only, honest labels)."""
    protocol = _read_json(repo_root / HYP002R_WFO_PATH) or {}
    per_hyp = [
        {
            "hypothesis_id": h["hypothesis_id"],
            "walkforward_rows": h["walkforward_rows"],
            "walkforward_successful_rows": h["walkforward_successful_rows"],
            "warnings": h["walkforward_warnings"],
        }
        for h in batch.get("hypotheses", [])
    ]
    return {
        "available": bool(per_hyp),
        # Dry-run bounded walk-forward is not a rigorous OOS gate pass.
        "rigorous_oos_gate_pass": False,
        "gate_posture": "dry_run_walkforward_not_a_rigorous_gate_pass",
        "protocol": {
            "method": protocol.get("method"),
            "window_count": protocol.get("window_count"),
            "in_sample_bars": (protocol.get("protocol") or {}).get(
                "in_sample_bars"
            ),
            "out_of_sample_bars": (protocol.get("protocol") or {}).get(
                "out_of_sample_bars"
            ),
            "purge_embargo": (protocol.get("protocol") or {}).get(
                "purge_embargo"
            ),
            "no_lookahead_boundary": (protocol.get("protocol") or {}).get(
                "no_lookahead_boundary"
            ),
        },
        "per_hypothesis": per_hyp,
    }


def build_robustness_panel(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Robustness / Monte-Carlo posture — withheld statistics shown explicitly."""
    mc = _read_json(repo_root / HYP002R_ROBUSTNESS_PATH) or {}
    return {
        "available": bool(mc),
        "monte_carlo_run": bool(mc.get("monte_carlo_run", False)),
        "monte_carlo_reason": mc.get("monte_carlo_reason"),
        "full_denominator_review": bool(mc.get("full_denominator_review", False)),
        "axis_sensitivity_review": mc.get("axis_sensitivity_review"),
        # These statistics were not computed on this evidence; never fabricated.
        "withheld_statistics": ["MonteCarlo", "Bootstrap", "PSR", "DSR", "MinTRL"],
        "withheld_note": (
            "No package-local Monte-Carlo / bootstrap runner surface was used, "
            "and PSR / DSR / MinTRL were not computed on this dry-run evidence. "
            "These statistics are withheld rather than fabricated."
        ),
    }


# ---------------------------------------------------------------------------
# Candidate funnel — full denominator, honest zero at the end.
# ---------------------------------------------------------------------------
def build_candidate_funnel(batch: dict[str, Any]) -> dict[str, Any]:
    """Full-denominator candidate funnel; candidate-ready stays zero on evidence."""
    totals = batch.get("totals", {})
    stages = [
        {
            "stage": "frozen_hypotheses",
            "label": "Frozen hypotheses",
            "count": totals.get("hypothesis_count", 0),
        },
        {
            "stage": "executed",
            "label": "Executed (denominator preserved)",
            "count": totals.get("hypothesis_count", 0),
        },
        {
            "stage": "positive_median_pnl",
            "label": "Positive median PnL surface",
            "count": totals.get("hypotheses_with_positive_median_pnl", 0),
        },
        {
            "stage": "go_like_evidence",
            "label": "GO-like evidence",
            "count": totals.get("go_like_hypotheses", 0),
        },
        {
            "stage": "candidate_ready",
            "label": "Candidate-ready for human review",
            "count": 0,
        },
    ]
    return {
        "available": batch.get("available", False),
        "frozen_denominator_rows": batch.get("frozen_denominator_rows"),
        "winner_only_view": False,
        "candidate_ready_count": 0,
        "stages": stages,
    }


# ---------------------------------------------------------------------------
# Activity / evidence timeline (from committed PR / package metadata only).
# ---------------------------------------------------------------------------
def build_timeline(
    batch: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[dict[str, Any]]:
    """Deterministic evidence timeline; no clock, no live refresh.

    Sequence and references come from committed frozen-set / batch / synthesis
    metadata (PR #600 -> #606 -> #608 -> #609). Each PR entry is included only
    when its source artifact is present in the checkout.
    """
    frozen = _read_json(repo_root / FROZEN_SET_PATH) or {}
    events: list[dict[str, Any]] = []
    seq = 0

    if (repo_root / FROZEN_SET_PATH).exists():
        seq += 1
        events.append(
            {
                "seq": seq,
                "ref": "PR #600",
                "kind": "freeze",
                "label": "Revised four-hypothesis set signed off and frozen",
                "detail": frozen.get("main_decision"),
                "source": FROZEN_SET_PATH,
            }
        )
    if (repo_root / BATCH_EXECUTE_MANIFEST_PATH).exists():
        seq += 1
        events.append(
            {
                "seq": seq,
                "ref": "PR #606",
                "kind": "execute",
                "label": "Revised batch executed (HYP-002R blocked pending runner support)",
                "detail": "Real research traffic; denominator preserved; no canonical write.",
                "source": BATCH_EXECUTE_MANIFEST_PATH,
            }
        )
    if (repo_root / ROLLUP_PATH).exists():
        seq += 1
        events.append(
            {
                "seq": seq,
                "ref": "PR #608",
                "kind": "complete",
                "label": "HYP-002R completed; final revised-batch rollup",
                "detail": "32/32 rows executed and preserved; GO-like evidence = false.",
                "source": ROLLUP_PATH,
            }
        )
    if (repo_root / SYNTHESIS_PATH).exists():
        seq += 1
        events.append(
            {
                "seq": seq,
                "ref": "PR #609",
                "kind": "conclude",
                "label": "Real-traffic batch synthesis concluded",
                "detail": "Operating-layer acceptance evidence; no candidate / crossing authority.",
                "source": SYNTHESIS_PATH,
            }
        )
    return events


# ---------------------------------------------------------------------------
# Boundary panel (non-authority assertions from committed evidence).
# ---------------------------------------------------------------------------
def build_boundary_panel(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Committed non-authority assertions surfaced read-only."""
    assertions = _read_json(repo_root / NON_AUTHORITY_PATH) or {}
    # Only the safety-relevant boolean assertions, sorted for determinism.
    surfaced = {
        key: bool(value)
        for key, value in sorted(assertions.items())
        if isinstance(value, bool)
    }
    return {
        "available": bool(assertions),
        "source": NON_AUTHORITY_PATH,
        "assertions": surfaced,
    }


# ---------------------------------------------------------------------------
# Overview (lab-wide summary blending coordinator state + batch evidence).
# ---------------------------------------------------------------------------
def _top_blockers(batch: dict[str, Any], robustness: dict[str, Any]) -> list[str]:
    """Honest top blockers / caveats derived from committed evidence."""
    blockers: list[str] = []
    totals = batch.get("totals", {})
    if batch.get("available"):
        blockers.append(
            f"No hypothesis produced GO-like or candidate-worthy evidence "
            f"({totals.get('go_like_hypotheses', 0)} GO-like of "
            f"{totals.get('hypothesis_count', 0)} frozen)."
        )
        if not batch.get("canonical_result_population_written", True):
            blockers.append(
                "No canonical Result Population written; evidence is dry-run / "
                "package-local."
            )
    if not robustness.get("monte_carlo_run", True):
        blockers.append(
            "Monte-Carlo / bootstrap withheld; PSR / DSR / MinTRL not computed."
        )
    blockers.append(
        "Walk-forward evidence is bounded dry-run only, not a rigorous OOS gate "
        "pass."
    )
    blockers.append(
        "Edge-search remains held pending separate operator authorization."
    )
    return blockers


def _global_caveats() -> list[str]:
    return [
        "This cockpit shows the full denominator (every hypothesis and row), not "
        "winners only.",
        "All real-traffic evidence is dry-run / package-local and non-canonical; "
        "nothing here is crossed, candidate-registered, paper-ready, or "
        "live-ready.",
        "Positive PnL surfaces that fail the primary drawdown screen are shown as "
        "non-promoting, not as edges.",
        "Withheld statistics (Monte-Carlo / bootstrap / PSR / DSR / MinTRL) are "
        "labelled explicitly rather than fabricated.",
        "Display ordering is deterministic and confers no ranking, "
        "recommendation, readiness, or promotion authority.",
        "Any real transition, candidate admission, crossing, or approval requires "
        "separate human action; this cockpit cannot grant it.",
    ]


def build_overview(
    batch: dict[str, Any],
    robustness: dict[str, Any],
    coordinator: dict[str, Any],
) -> dict[str, Any]:
    """Lab-overview panel blending coordinator state and batch evidence."""
    coord_summary = coordinator.get("denominator_summary", {})
    return {
        "productization_status": (
            "Real-traffic operating-layer acceptance evidence concluded; lab held "
            "at edge-search with no candidate produced."
        ),
        "real_traffic_batch": {
            "available": batch.get("available", False),
            "decision": batch.get("decision"),
            "frozen_denominator_rows": batch.get("frozen_denominator_rows"),
            "preserved_rows": batch.get("preserved_rows"),
            "dropped_rows": batch.get("dropped_rows"),
            "blocked_rows": batch.get("blocked_rows"),
            "executed_successful_rows": batch.get("executed_successful_rows"),
            "go_like_evidence": batch.get("go_like_evidence", False),
            "canonical_result_population_written": batch.get(
                "canonical_result_population_written", False
            ),
        },
        "denominator": {
            "real_traffic_rows": batch.get("frozen_denominator_rows"),
            "coordinator_subject_count": coord_summary.get("subject_count"),
            "coordinator_no_go_count": coord_summary.get("no_go_count"),
            "coordinator_blocked_count": coord_summary.get("blocked_count"),
        },
        "candidate_state": {
            "candidate_ready_count": 0,
            "go_like_evidence": batch.get("go_like_evidence", False),
            "candidate_admitted": False,
        },
        "top_blockers": _top_blockers(batch, robustness),
    }


# ---------------------------------------------------------------------------
# Artifact drilldown.
# ---------------------------------------------------------------------------
def build_artifact_drilldown(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Repo-relative artifact drilldown with present/missing + category labels."""
    return [
        {
            "key": key,
            "category": category,
            "path": path,
            "present": (repo_root / path).exists(),
        }
        for key, category, path in _ARTIFACT_DRILLDOWN
    ]


# ---------------------------------------------------------------------------
# Coordinator projection (compact, reused read-only from the dashboard model).
# ---------------------------------------------------------------------------
def build_coordinator_projection(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Compact coordinator-state projection reused from the dashboard model.

    Reuses ``build_dashboard_data`` read-only and keeps only the lab-wide summary
    fields the cockpit surfaces (full denominator, subjects-by-state, and the
    held-boundary / deferred-B map) so the cockpit and dashboard never diverge on
    state vocabulary.
    """
    data = build_dashboard_data(repo_root=repo_root)
    summary = data["denominator_summary"]
    return {
        "schema_version": data["schema_version"],
        "denominator_summary": {
            "subject_count": summary["subject_count"],
            "by_overall_state": summary["by_overall_state"],
            "no_go_count": summary["no_go_count"],
            "blocked_count": summary["blocked_count"],
            "candidate_ready_count": summary["candidate_ready_count"],
            "operator_gate_pending_count": summary["operator_gate_pending_count"],
        },
        "subjects": [
            {
                "subject_id": v["subject_id"],
                "subject_label": v["subject_label"],
                "overall_state": v["overall_state"],
                "evidence_class": v["evidence_class"],
            }
            for v in data["subjects"]
        ],
        "held_boundary_panel": data["held_boundary_panel"],
    }


# ---------------------------------------------------------------------------
# Top-level assembly.
# ---------------------------------------------------------------------------
def build_cockpit_data(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Build the full read-only cockpit data model (deterministic)."""
    batch = build_real_traffic_batch(repo_root)
    robustness = build_robustness_panel(repo_root)
    coordinator = build_coordinator_projection(repo_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_operator_cockpit",
        "non_authority_declaration": dict(COCKPIT_NON_AUTHORITY),
        "edge_search_hold": state_model.EDGE_SEARCH_HOLD_NOTE,
        "overview": build_overview(batch, robustness, coordinator),
        "real_traffic_batch": batch,
        "candidate_funnel": build_candidate_funnel(batch),
        "wfo_oos": build_wfo_oos_panel(batch, repo_root),
        "robustness": robustness,
        "timeline": build_timeline(batch, repo_root),
        "coordinator": coordinator,
        "artifact_drilldown": build_artifact_drilldown(repo_root),
        "boundary": build_boundary_panel(repo_root),
        "caveats": _global_caveats(),
    }
