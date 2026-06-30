"""Deterministic read-only data model for the lab results dashboard.

The model is a pure projection of committed repo truth:

- per-subject and overall **state** comes verbatim from
  ``tools/lab_state`` (the merged coordinator state model); this surface never
  re-derives or re-ranks state, and introduces no new state vocabulary;
- **display facts** (denominator breakdown, Result Population identities,
  withheld statistics, evidence class, NO-GO caveats) are read from the same
  committed artifacts the resolver already consults.

It carries no clock, no git, no network, and no executable control, so two runs
over the same checkout produce byte-identical output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.lab_state import model
from tools.lab_state.resolver import REPO_ROOT, build_snapshot
from tools.lab_state.run import SUBJECTS

SCHEMA_VERSION = "lab_results_dashboard_v2"

# ---------------------------------------------------------------------------
# Committed scratch artifact paths for the PR #583-#587 baseline proof
# sequence. These are read-only references; no writes are performed.
# ---------------------------------------------------------------------------
_BASELINE_PROOF_ARTIFACTS: dict[str, str] = {
    "baseline_payload_catalog": (
        "scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json"
    ),
    "baseline_gate_expectations": (
        "scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/"
        "baseline_gate_expectations.json"
    ),
    "guard_validation_summary": (
        "scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_validation_summary.json"
    ),
    "baseline_loop_result": (
        "scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/baseline_loop_result.json"
    ),
    "no_candidate_review_result": (
        "scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/no_candidate_review_result.json"
    ),
    "crossing_rejection_result": (
        "scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/crossing_rejection_result.json"
    ),
    "completion_state_update": (
        "scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/"
        "completion_state_update.json"
    ),
    "held_boundary_map": (
        "scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json"
    ),
}

# Read-only visibility surface. Inherits the coordinator state model's
# non-authority declaration and adds the explicit "no executable control"
# guarantees required of an operator dashboard (package §5).
DASHBOARD_NON_AUTHORITY: dict[str, bool] = {
    **model.NON_AUTHORITY_DECLARATION,
    "renders_executable_control": False,
    "has_run_button": False,
    "has_approve_button": False,
    "has_promote_button": False,
    "has_retry_button": False,
    "has_scheduler_toggle": False,
    "fetches_live_data": False,
    "auto_refreshes_from_network": False,
    "ranks_as_authority": False,
    "shows_recommendation_labels": False,
}

# Overall states that count as a "completed experiment run" reached, for the
# denominator summary. These are legibility buckets only, never a ranking.
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


def _read_json(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Fail closed: an unreadable artifact yields no display facts. State
        # truth (which fails closed to ``blocked``) still comes from the
        # resolver, so the surface never fabricates progress.
        return None


def _stage_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["stage"]: s for s in snapshot["stages"]}


def _stage_status(stage: dict[str, Any] | None) -> dict[str, Any]:
    if stage is None:
        return {"state": "not_started", "reason_code": None, "detail": ""}
    return {
        "state": stage["state"],
        "reason_code": stage["reason_code"],
        "detail": stage["detail"],
    }


def _evidence_class(conclusion: dict[str, Any] | None) -> str:
    """Surface the canonical vs non-canonical evidence class (never a ranking)."""
    if not conclusion:
        return "unknown"
    classes = [str(c).lower() for c in (conclusion.get("evidence_class") or [])]
    if any("non-canonical" in c or "scratch" in c for c in classes):
        return "non_canonical"
    if any("canonical" in c for c in classes):
        return "canonical"
    return "unknown"


def _denominator(conclusion: dict[str, Any] | None) -> dict[str, Any]:
    """Full denominator breakdown — never winners only (package §5)."""
    if not conclusion or "denominator" not in conclusion:
        if conclusion and conclusion.get("denominator_preserved") is True:
            return {
                "available": True,
                "planned": conclusion.get("planned_rows")
                or conclusion.get("expected_rows"),
                "complete": conclusion.get("complete_rows"),
                "failed": conclusion.get("failed_rows"),
                "invalid": conclusion.get("invalid_rows"),
                "blocked": conclusion.get("blocked_rows"),
                "pruned": conclusion.get("pruned_rows"),
                "preserved": True,
            }
        return {"available": False}
    d = conclusion["denominator"]
    return {
        "available": True,
        "planned": d.get("planned"),
        "complete": d.get("complete"),
        "failed": d.get("failed"),
        "invalid": d.get("invalid"),
        "blocked": d.get("blocked"),
        "pruned": d.get("pruned"),
        "preserved": bool(d.get("preserved", False)),
    }


def _result_populations(conclusion: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not conclusion:
        return []
    rows = conclusion.get("result_populations") or []
    result_populations = [
        {
            "result_population_id": rp.get("result_population_id"),
            "exit_mode": rp.get("exit_mode"),
            "rows": rp.get("rows"),
            "sha256": rp.get("sha256"),
        }
        for rp in rows
    ]
    artifact_hashes = conclusion.get("artifact_paths_and_hashes") or {}
    for key, value in sorted(artifact_hashes.items()):
        if not isinstance(value, dict) or "result" not in key:
            continue
        path = str(value.get("path", ""))
        filename = path.rsplit("/", 1)[-1]
        result_id = filename.split(".", 1)[0] if filename.startswith("RP-") else key
        result_populations.append(
            {
                "result_population_id": result_id,
                "exit_mode": key.replace("_result", ""),
                "rows": None,
                "sha256": value.get("sha256"),
            }
        )
    return result_populations


def _robustness_facts(
    conclusion: dict[str, Any] | None, stage: dict[str, Any] | None
) -> dict[str, Any]:
    rob = (conclusion or {}).get("robustness") or {}
    return {
        **_stage_status(stage),
        "descriptive_reports_produced": bool(
            rob.get("descriptive_reports_produced", False)
        ),
        "withheld_statistics": list(rob.get("withheld_statistics") or []),
        "per_trade_monte_carlo": rob.get("per_trade_monte_carlo"),
    }


def _oos_facts(
    conclusion: dict[str, Any] | None, stage: dict[str, Any] | None
) -> dict[str, Any]:
    oos = (conclusion or {}).get("oos") or {}
    facts = _stage_status(stage)
    facts["oos_evidence_status"] = oos.get("status")
    facts["canonical_result_population_written"] = oos.get(
        "canonical_result_population_written"
    )
    return facts


def _no_go_caveats(
    overall_state: str, conclusion: dict[str, Any] | None
) -> list[str]:
    """Deterministic NO-GO caveats, read from the conclusion (no fabrication)."""
    if overall_state != "no_go" or not conclusion:
        return []
    caveats: list[str] = []
    failure = conclusion.get("primary_failure") or {}
    screen = failure.get("screen")
    threshold = failure.get("threshold")
    if screen is not None:
        caveats.append(
            f"NO-GO on the primary {screen} screen"
            + (f" (threshold {threshold})." if threshold is not None else ".")
        )
    interp = conclusion.get("interpretation_caveats") or {}
    if interp.get("funding_payments_wired") is False:
        caveats.append(
            "Funding payments were not wired; this is a price/PnL signal test, "
            "not a complete funding-carry PnL test."
        )
    if interp.get("statement_about_all_funding_strategies") is False:
        caveats.append(
            "The NO-GO is about this hypothesis only, not a statement about all "
            "funding strategies."
        )
    return caveats


def _artifact_drilldown(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """De-duplicated artifact pointers across all stages, with present flags."""
    seen: dict[str, dict[str, Any]] = {}
    for stage in snapshot["stages"]:
        for ref in stage.get("artifact_refs", []):
            path = ref.get("path") or ""
            if not path:
                continue
            existing = seen.get(path)
            if existing is None:
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


def build_subject_view(
    subject: dict[str, Any], repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    """Project one subject's coordinator snapshot + display facts (read-only)."""
    snapshot = build_snapshot(subject, repo_root)
    stages = _stage_map(snapshot)

    conclusion_rel = subject.get("artifacts", {}).get("experiment_run")
    conclusion = (
        _read_json(repo_root / conclusion_rel) if conclusion_rel else None
    )

    overall = snapshot["overall_state"]
    return {
        "subject_id": snapshot["subject_id"],
        "subject_label": snapshot["subject_label"],
        "overall_state": overall,
        "evidence_class": _evidence_class(conclusion),
        "denominator": _denominator(conclusion),
        "result_populations": _result_populations(conclusion),
        "replay_status": _stage_status(stages.get("replay_normalization")),
        "oos_gate_status": _oos_facts(
            conclusion, stages.get("walkforward_oos_gate")
        ),
        "robustness_status": _robustness_facts(
            conclusion, stages.get("robustness")
        ),
        "candidate_review_status": _stage_status(
            stages.get("candidate_review_reach")
        ),
        "reporting_status": _stage_status(stages.get("reporting")),
        "operator_gate_status": _stage_status(stages.get("operator_gate")),
        "no_go_caveats": _no_go_caveats(overall, conclusion),
        "withheld_statistics": list(
            (conclusion or {}).get("robustness", {}).get("withheld_statistics")
            or []
        ),
        "stages": snapshot["stages"],
        "artifact_drilldown": _artifact_drilldown(snapshot),
    }


def _overall_denominator(views: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate denominator over subjects — full population, never winners only.

    The ``by_overall_state`` map lists **every** overall state in the model with
    its count (including zeros), so failed / blocked / NO-GO buckets are always
    visible alongside any ready bucket.
    """
    by_state = {state: 0 for state in model.OVERALL_STATES}
    for view in views:
        by_state[view["overall_state"]] = by_state.get(
            view["overall_state"], 0
        ) + 1

    # Distinct experiment artifacts so a shared conclusion is not double-counted.
    trial_totals = {
        "planned": 0,
        "complete": 0,
        "failed": 0,
        "invalid": 0,
        "blocked": 0,
        "pruned": 0,
    }
    seen_populations: set[str] = set()
    distinct_denominators = 0
    for view in views:
        rp_ids = tuple(
            rp.get("result_population_id") for rp in view["result_populations"]
        )
        key = "|".join(str(r) for r in rp_ids)
        denom = view["denominator"]
        if denom.get("available") and key and key not in seen_populations:
            seen_populations.add(key)
            distinct_denominators += 1
            for field in trial_totals:
                trial_totals[field] += denom.get(field) or 0

    return {
        "subject_count": len(views),
        "by_overall_state": by_state,
        "completed_experiment_run_count": sum(
            1 for v in views if v["overall_state"] in _COMPLETED_EXPERIMENT_STATES
        ),
        "no_go_count": by_state.get("no_go", 0),
        "blocked_count": by_state.get("blocked", 0),
        "candidate_ready_count": by_state.get(
            "candidate_ready_for_human_review", 0
        ),
        "operator_gate_pending_count": by_state.get(
            "operator_gate_pending", 0
        ),
        "distinct_result_population_sets": distinct_denominators,
        "trial_denominator_over_distinct_sets": trial_totals,
    }


def _global_caveats() -> list[str]:
    return [
        "This surface shows the full denominator (every run and state), not "
        "winners only.",
        "Evidence shown is non-canonical / scratch-only unless a row's evidence "
        "class says otherwise; nothing here is crossed, candidate-registered, "
        "paper-ready, or live-ready.",
        "Dry-run-only OOS evidence is not a rigorous gate pass.",
        "Withheld statistics (e.g. PSR / DSR / MinTRL) are shown explicitly "
        "rather than fabricated.",
        "Ordering is deterministic display order only and confers no ranking, "
        "recommendation, readiness, or promotion authority.",
        "Any real transition or approval requires separate human action through "
        "the candidate lifecycle engine; this dashboard cannot grant it.",
    ]


# ---------------------------------------------------------------------------
# Baseline proof panel — reads from committed PR #583-#587 scratch artifacts.
# Fails closed: missing artifact -> blocker/withheld label, no fabrication.
# ---------------------------------------------------------------------------

def _baseline_payload_rows(catalog: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Extract per-baseline construction payload facts (read-only, no ranking)."""
    if not catalog:
        return []
    rows = []
    for b in catalog.get("baselines") or []:
        rows.append(
            {
                "baseline_id": b.get("baseline_id"),
                "label": b.get("label"),
                "strategy_family": b.get("strategy_family"),
                "construction_payload": bool(b.get("construction_payload", False)),
                "non_promotable": bool(b.get("non_promotable", False)),
                "candidate_eligible": bool(b.get("candidate_eligible", True)),
                "expected_gate_result": b.get("expected_gate_result"),
                "expected_candidate_review_result": b.get(
                    "expected_candidate_review_result"
                ),
                "expected_crossing_result": b.get("expected_crossing_result"),
            }
        )
    return rows


def _gate_expectation_rows(
    gate_data: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Per-baseline WFO/OOS, robustness/MC, statistical gate posture (read-only)."""
    if not gate_data:
        return []
    global_rule = gate_data.get("global_rule") or {}
    rows = []
    for b in gate_data.get("baselines") or []:
        rows.append(
            {
                "baseline_id": b.get("baseline_id"),
                "wfo_oos_gate_expected": b.get("wfo_oos_gate_expected"),
                "robustness_mc_gate_expected": b.get("robustness_mc_gate_expected"),
                "statistical_diagnostics_gate_expected": b.get(
                    "statistical_diagnostics_gate_expected"
                ),
                "denominator_integrity_expected": b.get(
                    "denominator_integrity_expected"
                ),
                "crossing_expected": b.get("crossing_expected"),
                "numeric_override_allowed": bool(
                    b.get("numeric_override_allowed", False)
                ),
                "retuning_allowed": bool(b.get("retuning_allowed", False)),
            }
        )
    return rows, global_rule


def _guard_summary(guard: dict[str, Any] | None) -> dict[str, Any]:
    """Non-promotable crossing guard hardening result (read-only)."""
    if not guard:
        return {"available": False, "guard_implemented": None}
    val = guard.get("validation") or {}
    tests = val.get("candidate_crossing_tests") or {}
    return {
        "available": True,
        "guard_implemented": bool(guard.get("guard_implemented", False)),
        "non_promotable_crossing_guard_hardened": bool(
            guard.get("non_promotable_crossing_guard_hardened", False)
        ),
        "lab_declared_finished": bool(guard.get("lab_declared_finished", False)),
        "test_result": tests.get("result"),
        "tests_observed": tests.get("observed"),
    }


def _agent_loop_summary(
    loop: dict[str, Any] | None,
    no_cand: dict[str, Any] | None,
    crossing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Baseline agent loop exercise summary (fixture-only, no autonomy implied)."""
    if not loop:
        return {"available": False}
    denom = (no_cand or {}).get("denominator_and_gate_caveats") or {}
    agent_beh = (no_cand or {}).get("agent_loop_behavior") or {}
    return {
        "available": True,
        "fixture_only": bool(loop.get("fixture_only", True)),
        "baseline_id": loop.get("baseline_id"),
        "status": loop.get("status"),
        "non_promotable": bool(loop.get("non_promotable", True)),
        "candidate_eligible": bool(loop.get("candidate_eligible", False)),
        "crossing_rejection_reason_code": loop.get("crossing_rejection_reason_code"),
        "canonical_result_population_written": bool(
            loop.get("canonical_result_population_written", False)
        ),
        "candidate_registry_written": bool(
            loop.get("candidate_registry_written", False)
        ),
        "no_candidate_result": {
            "status": (no_cand or {}).get("status"),
            "review_outcome": (no_cand or {}).get("review_outcome"),
            "declared_rows": denom.get("declared_rows"),
            "completed_rows": denom.get("completed_rows"),
            "wfo_oos_status": denom.get("wfo_oos_status"),
            "robustness_mc_status": denom.get("robustness_mc_status"),
            "missing_or_unavailable_metrics_fabricated": bool(
                denom.get("missing_or_unavailable_metrics_fabricated", False)
            ),
        },
        "crossing_rejection": {
            "status": (crossing or {}).get("status"),
            "reason_code": (crossing or {}).get("reason_code"),
            "check": (crossing or {}).get("check"),
            "crossing_action_authorized": bool(
                (crossing or {}).get("crossing_action_authorized", False)
            ),
            "first_real_crossing_remains_karl_gated": bool(
                (crossing or {}).get("first_real_crossing_remains_karl_gated", True)
            ),
        },
        "agent_loop_behavior": {
            "recommended_rescue": bool(agent_beh.get("recommended_rescue", False)),
            "recommended_retuning": bool(agent_beh.get("recommended_retuning", False)),
            "ranked_as_edge": bool(agent_beh.get("ranked_as_edge", False)),
            "proposed_promotion": bool(agent_beh.get("proposed_promotion", False)),
            "proposed_readiness": bool(agent_beh.get("proposed_readiness", False)),
            "proposed_paper_live": bool(agent_beh.get("proposed_paper_live", False)),
            "proposed_real_crossing": bool(
                agent_beh.get("proposed_real_crossing", False)
            ),
        },
    }


def _provenance_trace(completion: dict[str, Any] | None) -> dict[str, Any]:
    """PR #583-#587 proof provenance (what was proven, what was NOT proven)."""
    if not completion:
        return {"available": False}
    return {
        "available": True,
        "baseline_sequence_prs": list(completion.get("baseline_sequence_prs") or []),
        "core_pipe_fixture_proven": bool(
            completion.get("core_pipe_fixture_proven", False)
        ),
        "no_candidate_result_observed": bool(
            completion.get("no_candidate_result_observed", False)
        ),
        "crossing_rejection_observed": bool(
            completion.get("crossing_rejection_observed", False)
        ),
        "real_candidate_crossing_completed": bool(
            completion.get("real_candidate_crossing_completed", False)
        ),
        "full_always_on_factory_completed": bool(
            completion.get("full_always_on_factory_completed", False)
        ),
        "lab_declared_finished_without_qualification": bool(
            completion.get("lab_declared_finished_without_qualification", False)
        ),
        "agent_rescue_recommended": bool(
            completion.get("agent_rescue_recommended", False)
        ),
        "agent_ranked_as_edge": bool(completion.get("agent_ranked_as_edge", False)),
        "baseline_candidate_eligible": bool(
            completion.get("baseline_candidate_eligible", False)
        ),
        "held_b_requires_real_edge_search_or_candidate_flow": bool(
            completion.get("held_b_requires_real_edge_search_or_candidate_flow", True)
        ),
        "paper_live_runtime_go_gated": bool(
            completion.get("paper_live_runtime_go_gated", True)
        ),
        "edge_search_authorized_here": bool(
            completion.get("edge_search_authorized_here", False)
        ),
        "canonical_writes_authorized_here": bool(
            completion.get("canonical_writes_authorized_here", False)
        ),
    }


def build_baseline_proof_panel(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Build the baseline proof panel from committed PR #583-#587 artifacts.

    Fails closed: if an artifact is missing or unreadable, the relevant
    sub-panel is marked unavailable rather than fabricating values.

    This panel is read-only, non-authoritative, and fixture-only.
    It contains no ranking, readiness, recommendation, or promotion language.
    """
    catalog = _read_json(repo_root / _BASELINE_PROOF_ARTIFACTS["baseline_payload_catalog"])
    gate_data = _read_json(
        repo_root / _BASELINE_PROOF_ARTIFACTS["baseline_gate_expectations"]
    )
    guard = _read_json(repo_root / _BASELINE_PROOF_ARTIFACTS["guard_validation_summary"])
    loop = _read_json(repo_root / _BASELINE_PROOF_ARTIFACTS["baseline_loop_result"])
    no_cand = _read_json(
        repo_root / _BASELINE_PROOF_ARTIFACTS["no_candidate_review_result"]
    )
    crossing = _read_json(
        repo_root / _BASELINE_PROOF_ARTIFACTS["crossing_rejection_result"]
    )
    completion = _read_json(
        repo_root / _BASELINE_PROOF_ARTIFACTS["completion_state_update"]
    )

    gate_rows, global_rule = _gate_expectation_rows(gate_data) if gate_data else ([], {})

    return {
        "panel_kind": "baseline_fixture_proof",
        "non_authority_note": (
            "Fixture-only / non-promotable baseline proof. "
            "Not ranking, not readiness, not recommendation, not trading authority."
        ),
        "baseline_payloads": {
            "available": bool(catalog),
            "baseline_count": (catalog or {}).get("baseline_count"),
            "selected_primitive_family": (catalog or {}).get("selected_primitive_family"),
            "contract_only_route_used": bool(
                (catalog or {}).get("contract_only_route_used", False)
            ),
            "baselines": _baseline_payload_rows(catalog),
        },
        "gate_expectations": {
            "available": bool(gate_data),
            "global_rule": global_rule,
            "per_baseline": gate_rows,
        },
        "guard_validation": _guard_summary(guard),
        "agent_loop_exercise": _agent_loop_summary(loop, no_cand, crossing),
        "provenance_trace": _provenance_trace(completion),
        "artifact_refs": {
            key: {
                "path": path,
                "present": (repo_root / path).exists(),
            }
            for key, path in _BASELINE_PROOF_ARTIFACTS.items()
            if key != "held_boundary_map"
        },
    }


def build_held_boundary_panel(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Build the held-boundary / deferred-B panel from the PR #587 artifact.

    Shows what is held until real research flow resumes, what requires a first
    real GO candidate, and what is GO-gated protected.

    Read-only, non-authoritative, descriptive-only.
    """
    held = _read_json(repo_root / _BASELINE_PROOF_ARTIFACTS["held_boundary_map"])
    artifact_path = _BASELINE_PROOF_ARTIFACTS["held_boundary_map"]
    return {
        "panel_kind": "held_boundary_deferred_b",
        "non_authority_note": (
            "Deferred-B boundary map. These items are not authorized in the current "
            "phase. They require separate explicit operator authorization."
        ),
        "available": bool(held),
        "held_b_until_real_research_flow": list(
            (held or {}).get("held_b_until_real_research_flow") or []
        ),
        "requires_real_go_candidate": list(
            (held or {}).get("requires_real_go_candidate") or []
        ),
        "go_gated_protected": list((held or {}).get("go_gated_protected") or []),
        "current_fork": list((held or {}).get("current_fork") or []),
        "artifact_ref": {
            "path": artifact_path,
            "present": (repo_root / artifact_path).exists(),
        },
    }


def build_dashboard_data(
    subjects: dict[str, dict[str, Any]] | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the full read-only dashboard data model (deterministic).

    Subjects are projected in sorted key order so the output is stable.
    New panels added by WP-LAB-DASHBOARD-GAP-COMPLETE-01:
    - baseline_proof_panel: strategy detail, sweep posture, WFO/OOS, MC/robustness,
      agent loop activity, data/provenance, candidate/no-candidate state
    - held_boundary_panel: deferred-B items, GO-candidate required, GO-gated protected
    """
    subjects = SUBJECTS if subjects is None else subjects
    views = [
        build_subject_view(subjects[key], repo_root)
        for key in sorted(subjects)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_operator_visibility",
        "non_authority_declaration": dict(DASHBOARD_NON_AUTHORITY),
        "edge_search_hold": model.EDGE_SEARCH_HOLD_NOTE,
        "denominator_summary": _overall_denominator(views),
        "caveats": _global_caveats(),
        "baseline_proof_panel": build_baseline_proof_panel(repo_root),
        "held_boundary_panel": build_held_boundary_panel(repo_root),
        "subjects": views,
    }
