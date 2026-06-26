"""Read-only resolver that maps existing repo/scratch artifacts to lab states.

The resolver never executes a transition, never writes canonical or candidate
lifecycle evidence, never runs a strategy, and never fetches data. It reads
committed JSON / markdown artifacts and reports the legible coordinator state of
each pipeline stage plus one overall snapshot.

Reading is separated from resolving: ``resolve_*`` helpers accept already-parsed
artifact payloads so they are trivially testable, while ``build_snapshot`` does
the read-only file I/O over a subject manifest.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.lab_state import model


REPO_ROOT = Path(__file__).resolve().parents[2]


# Overall-state precedence: earlier entries dominate later ones when several
# stages have resolved. A NO-GO conclusion dominates an incomplete OOS gate.
_OVERALL_PRECEDENCE: tuple[str, ...] = (
    "candidate_ready_for_human_review",
    "operator_gate_pending",
    "no_go",
    "blocked",
    "oos_gate_fail",
    "oos_gate_blocked",
    "candidate_review_blocked",
    "robustness_advisory",
    "reported",
    "replay_checked",
    "experiment_complete",
    "formalized",
    "not_started",
)


@dataclass
class ArtifactRef:
    """A read-only pointer to a repo artifact consulted during resolution."""

    role: str
    path: str
    present: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "path": self.path,
            "present": self.present,
            "note": self.note,
        }


@dataclass
class StageState:
    """Resolved state of a single pipeline stage."""

    stage: str
    state: str
    reason_code: str | None = None
    detail: str = ""
    artifact_refs: list[ArtifactRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "state": self.state,
            "reason_code": self.reason_code,
            "detail": self.detail,
            "artifact_refs": [ref.to_dict() for ref in self.artifact_refs],
        }


class LabStateResolverError(ValueError):
    """Raised when a resolved state violates the canonical vocabulary."""


def _check(stage_state: StageState) -> StageState:
    if not model.is_valid_stage(stage_state.stage):
        raise LabStateResolverError(f"unknown stage: {stage_state.stage}")
    if not model.is_valid_state(stage_state.state):
        raise LabStateResolverError(
            f"{stage_state.stage}: unknown state {stage_state.state}"
        )
    if not model.state_allowed_for_stage(stage_state.stage, stage_state.state):
        raise LabStateResolverError(
            f"{stage_state.stage}: state {stage_state.state} not allowed for stage"
        )
    if (
        stage_state.reason_code is not None
        and stage_state.reason_code not in model.ALL_REASON_CODES
    ):
        raise LabStateResolverError(
            f"{stage_state.stage}: unknown reason_code {stage_state.reason_code}"
        )
    return stage_state


# ---------------------------------------------------------------------------
# Per-stage pure resolvers (operate on parsed payloads).
# ---------------------------------------------------------------------------
def resolve_formalization(
    *, status_entry_present: bool, refs: list[ArtifactRef]
) -> StageState:
    if status_entry_present:
        return _check(
            StageState(
                stage="formalization",
                state="formalized",
                reason_code="STATE_FORMALIZED_FROM_STATUS_ENTRY",
                detail="Hypothesis formalized in a repo status entry.",
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="formalization",
            state="not_started",
            reason_code="STATE_STAGE_NOT_REACHED",
            detail="No formalization status entry found.",
            artifact_refs=refs,
        )
    )


def resolve_experiment_run(
    *, conclusion: dict[str, Any] | None, refs: list[ArtifactRef]
) -> StageState:
    if conclusion is None:
        return _check(
            StageState(
                stage="experiment_run",
                state="not_started",
                reason_code="STATE_ARTIFACT_MISSING",
                detail="No experiment conclusion artifact available.",
                artifact_refs=refs,
            )
        )
    if conclusion.get("status") == "blocked_before_variant_denominator":
        return _check(
            StageState(
                stage="experiment_run",
                state="blocked",
                reason_code="BLOCKED_RESULT_POPULATION_UNAVAILABLE",
                detail="Legacy denominator audit blocked before variant denominator.",
                artifact_refs=refs,
            )
        )
    if conclusion.get("denominator_preserved") is True:
        planned = conclusion.get("planned_rows") or conclusion.get("expected_rows")
        complete = conclusion.get("complete_rows")
        blocked = conclusion.get("blocked_rows")
        if complete:
            return _check(
                StageState(
                    stage="experiment_run",
                    state="experiment_complete",
                    reason_code="STATE_EXPERIMENT_DENOMINATOR_PRESERVED",
                    detail=(
                        f"Legacy denominator preserved: {complete}/{planned} "
                        "complete."
                    ),
                    artifact_refs=refs,
                )
            )
        return _check(
            StageState(
                stage="experiment_run",
                state="blocked",
                reason_code="BLOCKED_RESULT_POPULATION_UNAVAILABLE",
                detail=(
                    f"Legacy denominator preserved but no completed Result "
                    f"Population rows (blocked {blocked}/{planned})."
                ),
                artifact_refs=refs,
            )
        )
    denominator = conclusion.get("denominator") or {}
    populations = conclusion.get("result_populations") or []
    if not populations or not denominator.get("preserved", False):
        return _check(
            StageState(
                stage="experiment_run",
                state="blocked",
                reason_code="BLOCKED_DENOMINATOR_MANIFEST_UNAVAILABLE",
                detail="Result Populations or preserved denominator unavailable.",
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="experiment_run",
            state="experiment_complete",
            reason_code="STATE_EXPERIMENT_DENOMINATOR_PRESERVED",
            detail=(
                f"{len(populations)} Result Population(s); denominator "
                f"{denominator.get('complete')}/{denominator.get('planned')} "
                "preserved."
            ),
            artifact_refs=refs,
        )
    )


def resolve_replay_normalization(
    *, replay_summary: dict[str, Any] | None, refs: list[ArtifactRef]
) -> StageState:
    if replay_summary is None:
        return _check(
            StageState(
                stage="replay_normalization",
                state="not_started",
                reason_code="STATE_ARTIFACT_MISSING",
                detail="No replay normalization summary available.",
                artifact_refs=refs,
            )
        )
    fixtures = replay_summary.get("fixtures") or []
    normalized = [f for f in fixtures if f.get("normalized_stable_hash")]
    if not normalized:
        return _check(
            StageState(
                stage="replay_normalization",
                state="not_started",
                reason_code="STATE_STAGE_NOT_REACHED",
                detail="No fixtures carry a normalized stable hash.",
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="replay_normalization",
            state="replay_checked",
            reason_code="STATE_REPLAY_NORMALIZED",
            detail=(
                f"{len(normalized)} Result Population(s) normalized under the "
                "replay contract (equivalence only, not approval)."
            ),
            artifact_refs=refs,
        )
    )


def resolve_oos_gate(
    *,
    gate_decision: str | None = None,
    oos_dry_run: dict[str, Any] | None = None,
    refs: list[ArtifactRef] | None = None,
) -> StageState:
    refs = refs or []
    # Preferred path: a real OOS gate artifact carrying gate_decision.
    if gate_decision is not None:
        if gate_decision not in model.OOS_GATE_DECISIONS:
            return _check(
                StageState(
                    stage="walkforward_oos_gate",
                    state="oos_gate_blocked",
                    reason_code="BLOCKED_OOS_GATE_UNAVAILABLE",
                    detail=f"Unrecognized gate_decision: {gate_decision}.",
                    artifact_refs=refs,
                )
            )
        state = model.OOS_DECISION_TO_STATE[gate_decision]
        return _check(
            StageState(
                stage="walkforward_oos_gate",
                state=state,
                reason_code=f"OOS_GATE_{gate_decision.upper()}",
                detail=f"OOS gate decision: {gate_decision}.",
                artifact_refs=refs,
            )
        )
    # Fallback: a dry-run-only OOS summary is not a rigorous gate pass.
    if oos_dry_run is not None:
        status = str(oos_dry_run.get("status", ""))
        if "dry_run" in status or not oos_dry_run.get(
            "canonical_result_population_written", False
        ):
            return _check(
                StageState(
                    stage="walkforward_oos_gate",
                    state="oos_gate_blocked",
                    reason_code="STATE_OOS_DRY_RUN_ONLY",
                    detail=(
                        "OOS evidence is dry-run-only with deferred "
                        "purge/embargo; not a rigorous gate pass."
                    ),
                    artifact_refs=refs,
                )
            )
    return _check(
        StageState(
            stage="walkforward_oos_gate",
            state="not_started",
            reason_code="BLOCKED_OOS_GATE_UNAVAILABLE",
            detail="No OOS gate artifact available.",
            artifact_refs=refs,
        )
    )


def resolve_robustness(
    *, robustness: dict[str, Any] | None, refs: list[ArtifactRef]
) -> StageState:
    if robustness is None:
        return _check(
            StageState(
                stage="robustness",
                state="not_started",
                reason_code="STATE_ARTIFACT_MISSING",
                detail="No robustness summary available.",
                artifact_refs=refs,
            )
        )
    if robustness.get("descriptive_reports_produced", False):
        withheld = robustness.get("withheld_statistics") or []
        return _check(
            StageState(
                stage="robustness",
                state="robustness_advisory",
                reason_code="STATE_ROBUSTNESS_ADVISORY_ONLY",
                detail=(
                    "Descriptive robustness reports produced; withheld "
                    f"{', '.join(withheld) if withheld else 'no'} statistics "
                    "rather than fabricating inputs."
                ),
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="robustness",
            state="blocked",
            reason_code="BLOCKED_REQUIRED_STAT_INPUTS_UNAVAILABLE",
            detail="Robustness inputs unavailable.",
            artifact_refs=refs,
        )
    )


def resolve_candidate_review_reach(
    *, review: dict[str, Any] | None, refs: list[ArtifactRef]
) -> StageState:
    if review is None:
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="not_started",
                reason_code="STATE_ARTIFACT_MISSING",
                detail="No candidate-review reach record available.",
                artifact_refs=refs,
            )
        )
    if (
        review.get("packet_generated") is False
        or review.get("status") == "not_generated"
    ):
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="candidate_review_not_created",
                reason_code="NO_GO_PRIMARY_RISK_SCREEN_FAILED",
                detail=str(review.get("reason", "No candidate-review packet generated.")),
                artifact_refs=refs,
            )
        )
    if str(review.get("status", "")).lower() == "blocked":
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="candidate_review_blocked",
                reason_code="BLOCKED_RESULT_POPULATION_UNAVAILABLE",
                detail=str(review.get("reason", "Candidate-review packet blocked.")),
                artifact_refs=refs,
            )
        )
    if review.get("candidate_review_packet_created", False):
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="candidate_ready_for_human_review",
                detail=(
                    "A candidate-review packet was produced under its own "
                    "non-authority boundary; not registration, ranking, "
                    "readiness, promotion, or gate satisfaction."
                ),
                artifact_refs=refs,
            )
        )
    blocked = review.get("blocked_review_reason")
    no_packet = review.get("no_candidate_review_packet_reason")
    if blocked:
        code = blocked.get("code") if isinstance(blocked, dict) else None
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="candidate_review_blocked",
                reason_code=code if code in model.ALL_REASON_CODES else None,
                detail=(blocked.get("detail") if isinstance(blocked, dict) else ""),
                artifact_refs=refs,
            )
        )
    if no_packet:
        code = no_packet.get("code") if isinstance(no_packet, dict) else None
        return _check(
            StageState(
                stage="candidate_review_reach",
                state="candidate_review_not_created",
                reason_code=code if code in model.ALL_REASON_CODES else None,
                detail=(no_packet.get("detail") if isinstance(no_packet, dict) else ""),
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="candidate_review_reach",
            state="not_started",
            reason_code="STATE_STAGE_NOT_REACHED",
            detail="No packet created and no reason recorded.",
            artifact_refs=refs,
        )
    )


def resolve_reporting(
    *, reported: bool, refs: list[ArtifactRef]
) -> StageState:
    if reported:
        return _check(
            StageState(
                stage="reporting",
                state="reported",
                reason_code="STATE_REPORTED_FROM_SYNTHESIS",
                detail="Conclusion recorded in a synthesis doc / status entry.",
                artifact_refs=refs,
            )
        )
    return _check(
        StageState(
            stage="reporting",
            state="not_started",
            reason_code="STATE_STAGE_NOT_REACHED",
            detail="No synthesis/report artifact found.",
            artifact_refs=refs,
        )
    )


def resolve_operator_gate(*, candidate_review_state: str) -> StageState:
    """Operator gate is pending only when a candidate is ready for human review.

    A NO-GO / blocked / not-created review produces nothing to gate, so the
    operator gate stays ``not_started`` (held). This stage never executes a
    transition; the downstream human-gated candidate lifecycle engine owns that.
    """
    if candidate_review_state == "candidate_ready_for_human_review":
        return _check(
            StageState(
                stage="operator_gate",
                state="operator_gate_pending",
                reason_code="STATE_OPERATOR_GATE_HELD",
                detail=(
                    "Candidate is ready for human review; operator decision is "
                    "pending. The state model does not auto-promote."
                ),
            )
        )
    return _check(
        StageState(
            stage="operator_gate",
            state="not_started",
            reason_code="STATE_NO_CANDIDATE_PRODUCED",
            detail="No candidate produced; nothing for the operator to gate.",
        )
    )


# ---------------------------------------------------------------------------
# Snapshot assembly.
# ---------------------------------------------------------------------------
def overall_state(stage_states: list[StageState]) -> str:
    """Pick the highest-precedence resolved state across all stages.

    The candidate-review reach outcome is normalized first: a NO-GO no-packet
    review is the dominant overall conclusion (``no_go``) and must outrank an
    incomplete OOS gate or advisory robustness.
    """
    present = {s.state for s in stage_states}
    review = next(
        (s for s in stage_states if s.stage == "candidate_review_reach"), None
    )
    if review is not None and review.state == "candidate_review_not_created":
        present.discard("candidate_review_not_created")
        if review.reason_code in model.NO_PACKET_REASON_CODES:
            present.add("no_go")
        else:
            present.add("blocked")
    for state in _OVERALL_PRECEDENCE:
        if state in present:
            return state
    return "not_started"


@dataclass
class ArtifactLoad:
    """Result of a read-only artifact read.

    Distinguishes an absent artifact (``payload is None`` and not ``unreadable``)
    from one that exists but cannot be parsed (``unreadable`` true). The latter
    must fail closed to a blocked state rather than be mistaken for "not reached".
    """

    payload: dict[str, Any] | None = None
    unreadable: bool = False
    error: str = ""


def _read_json(path: Path | None) -> ArtifactLoad:
    if path is None or not path.exists():
        return ArtifactLoad(payload=None, unreadable=False)
    try:
        return ArtifactLoad(payload=json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        return ArtifactLoad(payload=None, unreadable=True, error=str(exc))
    except OSError as exc:
        return ArtifactLoad(payload=None, unreadable=True, error=str(exc))


def _blocked_unreadable(stage: str, load: ArtifactLoad, refs: list[ArtifactRef]) -> StageState:
    """Fail-closed state for an existing-but-unreadable / malformed artifact."""
    return _check(
        StageState(
            stage=stage,
            state="blocked",
            reason_code="STATE_ARTIFACT_UNREADABLE",
            detail=f"Configured artifact exists but could not be parsed: {load.error}",
            artifact_refs=refs,
        )
    )


def build_snapshot(subject: dict[str, Any], repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Resolve a full read-only lab state snapshot for one subject.

    ``subject`` maps stages to artifact relative paths. Missing or unreadable
    artifacts resolve fail-closed to ``not_started`` / ``blocked`` with an
    explicit state reason code; they never fabricate progress.
    """

    paths = subject.get("artifacts", {})
    supplemental_refs = [
        ArtifactRef(
            role=str(item.get("role", "supplemental_evidence")),
            path=str(item.get("path", "")),
            present=(repo_root / str(item.get("path", ""))).exists()
            if item.get("path")
            else False,
            note=str(item.get("note", "")),
        )
        for item in subject.get("supplemental_artifacts", [])
    ]

    def ref(role: str, key: str) -> tuple[ArtifactRef, Path | None]:
        rel = paths.get(key)
        if not rel:
            return ArtifactRef(role=role, path="", present=False, note="not configured"), None
        path = repo_root / rel
        return ArtifactRef(role=role, path=rel, present=path.exists()), path

    # formalization
    f_ref, f_path = ref("formalization_status_entry", "formalization")
    formalization = resolve_formalization(
        status_entry_present=f_ref.present, refs=[f_ref]
    )

    # experiment_run (existing-but-unreadable artifacts fail closed to blocked).
    e_ref, e_path = ref("conclusion_traceability", "experiment_run")
    e_load = _read_json(e_path)
    conclusion = e_load.payload
    if e_load.unreadable:
        experiment = _blocked_unreadable("experiment_run", e_load, [e_ref])
    else:
        experiment = resolve_experiment_run(conclusion=conclusion, refs=[e_ref])

    # replay_normalization
    r_ref, r_path = ref("replay_fixture_summary", "replay_normalization")
    r_load = _read_json(r_path)
    if r_load.unreadable:
        replay = _blocked_unreadable("replay_normalization", r_load, [r_ref])
    else:
        replay = resolve_replay_normalization(replay_summary=r_load.payload, refs=[r_ref])

    # walkforward_oos_gate
    o_ref, o_path = ref("oos_gate_summary", "walkforward_oos_gate")
    o_load = _read_json(o_path)
    if o_load.unreadable:
        oos = _blocked_unreadable("walkforward_oos_gate", o_load, [o_ref])
    else:
        oos_summary = o_load.payload
        gate_decision = oos_summary.get("gate_decision") if oos_summary else None
        oos_dry_run = (
            (conclusion or {}).get("oos") if subject.get("oos_from_conclusion") else None
        )
        oos = resolve_oos_gate(
            gate_decision=gate_decision, oos_dry_run=oos_dry_run, refs=[o_ref]
        )

    # robustness (shares the conclusion artifact; unreadable there blocks here too).
    rb_ref, _ = ref("conclusion_traceability", "experiment_run")
    if e_load.unreadable:
        robustness = _blocked_unreadable("robustness", e_load, [rb_ref])
    else:
        robustness_payload = (conclusion or {}).get("robustness")
        robustness = resolve_robustness(robustness=robustness_payload, refs=[rb_ref])

    # candidate_review_reach
    cr_ref, cr_path = ref("generic_review_contract", "candidate_review_reach")
    cr_load = _read_json(cr_path)
    if cr_load.unreadable:
        candidate_review = _blocked_unreadable("candidate_review_reach", cr_load, [cr_ref])
    else:
        review_record = _select_review_example(
            cr_load.payload, subject.get("review_example_id")
        )
        candidate_review = resolve_candidate_review_reach(
            review=review_record, refs=[cr_ref]
        )

    # reporting
    rp_ref, rp_path = ref("reporting_doc", "reporting")
    reporting = resolve_reporting(
        reported=bool(rp_path and rp_path.exists()), refs=[rp_ref]
    )

    # operator_gate
    operator_gate = resolve_operator_gate(
        candidate_review_state=candidate_review.state
    )

    stage_states = [
        formalization,
        experiment,
        replay,
        oos,
        robustness,
        candidate_review,
        reporting,
        operator_gate,
    ]
    # idea_intake mirrors formalization presence for legibility.
    idea_intake = _check(
        StageState(
            stage="idea_intake",
            state="formalized" if formalization.state == "formalized" else "not_started",
            reason_code=(
                "STATE_FORMALIZED_FROM_STATUS_ENTRY"
                if formalization.state == "formalized"
                else "STATE_STAGE_NOT_REACHED"
            ),
            detail="Idea intake recorded for the hypothesis."
            if formalization.state == "formalized"
            else "No idea intake found.",
            artifact_refs=[f_ref],
        )
    )
    ordered = [idea_intake, *stage_states]

    override = subject.get("overall_override")
    if override is not None:
        if override not in model.OVERALL_STATES:
            raise LabStateResolverError(f"unknown overall_override: {override}")
        overall = override
    else:
        overall = overall_state(ordered)

    return {
        "schema_version": model.SCHEMA_VERSION,
        "subject_id": subject.get("subject_id"),
        "subject_label": subject.get("subject_label"),
        "overall_state": overall,
        "stages": [s.to_dict() for s in ordered],
        "supplemental_artifact_refs": [ref.to_dict() for ref in supplemental_refs],
        "non_authority_declaration": dict(model.NON_AUTHORITY_DECLARATION),
        "edge_search_hold": model.EDGE_SEARCH_HOLD_NOTE,
    }


def _select_review_example(
    review_doc: dict[str, Any] | None, example_id: str | None
) -> dict[str, Any] | None:
    if review_doc is None:
        return None
    # A flat review record.
    if (
        "candidate_review_packet_created" in review_doc
        or "packet_generated" in review_doc
        or review_doc.get("status") in {"not_generated", "blocked"}
    ):
        return review_doc
    examples = review_doc.get("examples") or []
    if example_id:
        for example in examples:
            if example.get("example_id") == example_id:
                return example
    return examples[0] if examples else None
