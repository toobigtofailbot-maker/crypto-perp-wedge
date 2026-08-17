from __future__ import annotations

import ast
import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tools.hermes.proposals.models import (
    PROPOSAL_BODY_TYPES,
    AffectedDomain,
    AuthorityClass,
    ProposalType,
    TypedProposal,
)
from tools.mcp.project_evidence.models import ProjectEvidenceError, ResourceDeniedError
from tools.mcp.project_evidence.outbox import ProposalOutbox
from tools.mcp.project_evidence.service import ProjectEvidenceService

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "6115753fd623bcec668ec9a3dd814c52182f088a"
SESSION_ID = "hermes-h2-test-session"
STATUS_REF = "project://status"
REJECTIONS = (ValidationError, ProjectEvidenceError)


@pytest.fixture()
def service(tmp_path: Path) -> ProjectEvidenceService:
    return ProjectEvidenceService(
        REPO_ROOT,
        repo_sha=REPO_SHA,
        branch="test",
        outbox_root=tmp_path / "outbox",
        watch_manifest_path=REPO_ROOT / "tools/hermes/upstream_watch.json",
    )


def _anchor(service: ProjectEvidenceService, ref: str = STATUS_REF) -> dict[str, Any]:
    result = service.resources.read(ref)
    return {
        "ref": ref,
        "repo_sha": REPO_SHA,
        "evidence_identities": [
            {
                "path": result["evidence"]["path"],
                "sha256": result["evidence"]["artifact_sha256"],
            }
        ],
        "query_limit": None,
    }


def _query_anchor(
    service: ProjectEvidenceService, query_name: str, limit: int = 3
) -> dict[str, Any]:
    result = service.queries.run(query_name, limit=limit)
    return {
        "ref": f"query://{query_name}",
        "repo_sha": REPO_SHA,
        "evidence_identities": [
            {"path": item["path"], "sha256": item["sha256"]} for item in result["evidence_inputs"]
        ],
        "query_limit": limit,
    }


def _bodies() -> dict[ProposalType, dict[str, Any]]:
    return {
        ProposalType.STRATEGY: {
            "proposal_type": ProposalType.STRATEGY.value,
            "hypothesis": "A bounded funding-regime signal may contain testable edge.",
            "mechanism": "Funding regimes may proxy crowded positioning.",
            "strategy_family": "funding-regime",
            "target_market_data_context": "BTCUSDT perpetual research data; availability UNKNOWN.",
            "why_it_may_contain_edge": "The mechanism is plausible but unproven.",
            "evidence_basis": "Project status establishes the research-only boundary.",
            "evidence_refs": [STATUS_REF],
            "proposed_lab_evaluation_concept": "Compare a preregistered signal with a null.",
            "falsification_criteria": ["Reject if preregistered OOS criteria fail."],
            "expected_research_cost": "One bounded offline lab work package.",
            "claims_promotion_or_readiness": False,
        },
        ProposalType.STRATEGY_ADJUSTMENT: {
            "proposal_type": ProposalType.STRATEGY_ADJUSTMENT.value,
            "target_strategy_or_candidate_identity": "H-005",
            "observed_evidence_or_performance_issue": "Current status records an open research lane.",
            "evidence_refs": [STATUS_REF],
            "proposed_adjustment": "Evaluate a narrower lab-only regime filter.",
            "why_adjustment_might_help": "It may isolate conditions; this is an inference.",
            "baseline_vs_adjustment_lab_test_concept": "Use identical offline folds and costs.",
            "stop_or_falsification_condition": "Stop if the preregistered delta is absent.",
            "application_scope": "future_lab_evaluation_only",
        },
        ProposalType.BUG_FIX: {
            "proposal_type": ProposalType.BUG_FIX.value,
            "observed_defect_or_failure": "A hypothetical defect requires reproduction first.",
            "evidence_refs": [STATUS_REF],
            "suspected_root_cause": "UNKNOWN pending a bounded investigation.",
            "affected_components_or_files": [],
            "protected_boundary_assessment": "No protected change is requested by this proposal.",
            "proposed_fix_scope": "Reproduce and propose a narrow later work package.",
            "validation_plan": ["Add a failing regression before any separately approved fix."],
            "rollback_notes": "No change exists to roll back in H2.",
            "confidence": 0.35,
        },
        ProposalType.LAB_IMPROVEMENT: {
            "proposal_type": ProposalType.LAB_IMPROVEMENT.value,
            "observed_bottleneck_waste_or_failure_mode": "Status evidence is costly to scan manually.",
            "evidence_or_metrics": "No quantified throughput metric is available; UNKNOWN.",
            "evidence_refs": [STATUS_REF],
            "proposed_lab_or_process_improvement": "Design a read-only summary view later.",
            "expected_throughput_reliability_or_value_effect": "Potential review-time reduction.",
            "measurement_plan": ["Compare bounded review time before and after."],
            "rollback_or_stop_condition": "Stop if evidence fidelity decreases.",
        },
        ProposalType.DATA_ACQUISITION: {
            "proposal_type": ProposalType.DATA_ACQUISITION.value,
            "requested_dataset_or_source": "An explicitly approved public dataset; exact source UNKNOWN.",
            "research_question_enabled": "Whether the proposed feature adds independent information.",
            "provenance_or_source_identity": "UNKNOWN until source review.",
            "availability_or_timing_assumptions": "UNKNOWN; must be verified before acquisition.",
            "storage_compute_network_cost_impact": "UNKNOWN; estimate in a separate work package.",
            "evidence_refs": [STATUS_REF],
            "validation_plan": ["Verify source identity, hashes, schema, and gaps."],
            "data_quality_risks": ["Missing intervals", "Silent source revisions"],
            "silent_repair_or_fabrication_allowed": False,
        },
        ProposalType.DEPENDENCY_UPGRADE: {
            "proposal_type": ProposalType.DEPENDENCY_UPGRADE.value,
            "dependency_and_current_version": "A pinned dependency; exact candidate UNKNOWN.",
            "proposed_target_or_change": "Review a later pinned target.",
            "evidence_or_source": "Project status only; upstream impact remains UNKNOWN.",
            "evidence_refs": [STATUS_REF],
            "compatibility_concerns": "Must be established with focused tests.",
            "security_or_reliability_rationale": "Potential maintenance value, not yet proven.",
            "validation_plan": ["Install only in an approved isolated work package and test."],
            "rollback_plan": "Restore the prior exact lock in that future package.",
            "automatic_install_or_update": False,
        },
        ProposalType.INVESTIGATION: {
            "proposal_type": ProposalType.INVESTIGATION.value,
            "observed_question_or_anomaly": "Which current research lane has the clearest evidence gap?",
            "evidence_refs": [STATUS_REF],
            "why_investigation_is_valuable": "It may focus a later human-approved package.",
            "bounded_investigation_scope": "Read only allowlisted evidence and report UNKNOWNs.",
            "expected_output": "A cited, non-authoritative gap report.",
            "expected_cost_and_time": "One bounded model session under existing limits.",
            "stop_conditions": ["Stop on conflicting or unavailable exact evidence."],
        },
    }


def proposal_payload(
    service: ProjectEvidenceService,
    proposal_type: ProposalType = ProposalType.INVESTIGATION,
    *,
    authority_class: AuthorityClass = AuthorityClass.A1,
    domain: AffectedDomain = AffectedDomain.BOUNDED_INVESTIGATION,
) -> dict[str, Any]:
    return {
        "schema_version": "hermes_typed_proposal_v1",
        "proposal_type": proposal_type.value,
        "title": f"Review {proposal_type.value}",
        "repo_sha": REPO_SHA,
        "source_session_id": SESSION_ID,
        "evidence_refs": [STATUS_REF],
        "evidence_anchors": [_anchor(service)],
        "facts": [
            {
                "statement": "The project status is the current-state evidence anchor.",
                "evidence_refs": [STATUS_REF],
            }
        ],
        "inferences": ["A bounded follow-up may provide value."],
        "open_questions": ["Whether a human will authorize a separate work package."],
        "rationale": "Convert exact evidence into a reviewable proposal without taking action.",
        "expected_benefit": "A clearer human decision surface.",
        "confidence": 0.6,
        "affected_scope": ["proposal outbox only"],
        "affected_domains": [domain.value],
        "authority_class": authority_class.value,
        "estimates": {
            "cost": "No project action; future cost UNKNOWN.",
            "compute": "One bounded review/model pass.",
            "time": "One bounded review cycle.",
        },
        "requested_authority": {
            "kind": "human_review_for_separate_work_package",
            "description": "Human review only; any action requires a separate approved package.",
            "self_approval": False,
            "direct_execution": False,
            "standing_authority": False,
        },
        "approval_required": True,
        "validation_plan": ["Re-resolve every evidence identity before any later decision."],
        "rollback_or_stop_conditions": ["Stop if exact evidence is unavailable or conflicts."],
        "not_authority": True,
        "review_required": True,
        "automatic_consumers": [],
        "body": copy.deepcopy(_bodies()[proposal_type]),
    }


@pytest.mark.parametrize("proposal_type", list(ProposalType))
def test_all_seven_typed_proposals_validate_and_persist_exclusively(
    service: ProjectEvidenceService, proposal_type: ProposalType
) -> None:
    payload = proposal_payload(service, proposal_type)
    protected_inputs = [
        REPO_ROOT / "docs/project_status.md",
        REPO_ROOT / "research/candidate_registry.jsonl",
    ]
    before = {path: path.read_bytes() for path in protected_inputs}

    result = service.submit_proposal(proposal=payload)
    files = list(service.outbox.root.glob("*.proposal.json"))
    persisted = json.loads(files[0].read_text(encoding="utf-8"))

    assert len(files) == 1
    assert result["proposal_type"] == proposal_type.value
    assert persisted["schema_version"] == "hermes_proposal_outbox_v2"
    assert persisted["proposal"]["proposal_type"] == proposal_type.value
    assert persisted["source"]["repo_sha"] == REPO_SHA
    assert persisted["not_authority"] is True
    assert persisted["review_required"] is True
    assert persisted["automatic_consumers"] == []
    assert {path: path.read_bytes() for path in protected_inputs} == before


def test_base_envelope_and_seven_type_identities_are_stable() -> None:
    assert tuple(TypedProposal.model_fields) == (
        "schema_version",
        "proposal_type",
        "title",
        "repo_sha",
        "source_session_id",
        "evidence_refs",
        "evidence_anchors",
        "facts",
        "inferences",
        "open_questions",
        "rationale",
        "expected_benefit",
        "confidence",
        "affected_scope",
        "affected_domains",
        "authority_class",
        "estimates",
        "requested_authority",
        "approval_required",
        "validation_plan",
        "rollback_or_stop_conditions",
        "not_authority",
        "review_required",
        "automatic_consumers",
        "body",
    )
    assert tuple(PROPOSAL_BODY_TYPES) == tuple(ProposalType)


def test_correct_a0_is_accepted_and_misclassified_a0_fails_closed(
    service: ProjectEvidenceService,
) -> None:
    correct = proposal_payload(
        service,
        authority_class=AuthorityClass.A0,
        domain=AffectedDomain.RESULT_POPULATION_MUTATION,
    )
    assert service.submit_proposal(proposal=correct)["authority_class"] == "A0"

    for wrong_class in (AuthorityClass.A1, AuthorityClass.A2):
        wrong = copy.deepcopy(correct)
        wrong["authority_class"] = wrong_class.value
        with pytest.raises(REJECTIONS):
            service.submit_proposal(proposal=wrong)


@pytest.mark.parametrize(
    ("case", "mutate"),
    [
        ("missing classification", lambda p: p.pop("authority_class")),
        ("invalid classification", lambda p: p.update(authority_class="A9")),
        ("missing requested authority", lambda p: p.pop("requested_authority")),
        (
            "automatic consumer",
            lambda p: p.update(automatic_consumers=["dispatch-runner"]),
        ),
        ("not authority false", lambda p: p.update(not_authority=False)),
        (
            "self approval",
            lambda p: p["requested_authority"].update(self_approval=True),
        ),
        (
            "direct execution",
            lambda p: p["requested_authority"].update(direct_execution=True),
        ),
        ("malformed typed body", lambda p: p["body"].pop("expected_output")),
        ("missing evidence refs", lambda p: p.update(evidence_refs=[])),
    ],
)
def test_contract_rejections_create_no_file(
    service: ProjectEvidenceService, case: str, mutate: Any
) -> None:
    payload = proposal_payload(service)
    mutate(payload)

    with pytest.raises(REJECTIONS):
        service.submit_proposal(proposal=payload)
    assert not service.outbox.root.exists() or list(service.outbox.root.iterdir()) == []


@pytest.mark.parametrize(
    "requested_kind",
    [
        "direct_trade_or_order",
        "direct_live_parameter_change",
        "direct_promotion_or_go",
        "direct_kdauth_or_dispatch",
        "direct_result_population_mutation",
        "arbitrary_shell_filesystem_or_sql",
        "direct_apply_execute_merge_or_promote",
    ],
)
def test_action_authority_requests_are_rejected_without_writes(
    service: ProjectEvidenceService, requested_kind: str
) -> None:
    payload = proposal_payload(
        service,
        authority_class=AuthorityClass.A0,
        domain=AffectedDomain.AMBIGUOUS_PROTECTED_SCOPE,
    )
    payload["requested_authority"]["kind"] = requested_kind

    with pytest.raises(REJECTIONS):
        service.submit_proposal(proposal=payload)
    assert not service.outbox.root.exists()


def test_a0_with_approval_required_false_is_rejected_without_write(
    service: ProjectEvidenceService,
) -> None:
    payload = proposal_payload(
        service,
        authority_class=AuthorityClass.A0,
        domain=AffectedDomain.RESULT_POPULATION_MUTATION,
    )
    payload["approval_required"] = False

    with pytest.raises(ValidationError):
        service.submit_proposal(proposal=payload)
    assert not service.outbox.root.exists()


@pytest.mark.parametrize("bad_ref", ["project://dispatch", "evidence://hypothesis/H-999"])
def test_unallowlisted_or_nonexistent_evidence_is_rejected(
    service: ProjectEvidenceService, bad_ref: str
) -> None:
    payload = proposal_payload(service)
    payload["evidence_refs"] = [bad_ref]
    payload["evidence_anchors"][0]["ref"] = bad_ref
    payload["facts"][0]["evidence_refs"] = [bad_ref]
    payload["body"]["evidence_refs"] = [bad_ref]

    with pytest.raises(REJECTIONS):
        service.submit_proposal(proposal=payload)
    assert not service.outbox.root.exists()


def test_fabricated_evidence_identity_is_rejected(service: ProjectEvidenceService) -> None:
    payload = proposal_payload(service)
    payload["evidence_anchors"][0]["evidence_identities"][0]["sha256"] = "0" * 64

    with pytest.raises(ResourceDeniedError, match="does not match resolved evidence"):
        service.submit_proposal(proposal=payload)
    assert not service.outbox.root.exists()


def test_query_evidence_inputs_and_limit_are_re_resolved(service: ProjectEvidenceService) -> None:
    ref = "query://candidate-overview"
    payload = proposal_payload(service)
    payload["evidence_refs"] = [ref]
    payload["evidence_anchors"] = [_query_anchor(service, "candidate-overview")]
    payload["facts"][0]["evidence_refs"] = [ref]
    payload["body"]["evidence_refs"] = [ref]

    assert service.submit_proposal(proposal=payload)["proposal_type"] == "InvestigationProposal"

    tampered = copy.deepcopy(payload)
    tampered["evidence_anchors"][0]["evidence_identities"][0]["sha256"] = "0" * 64
    with pytest.raises(ResourceDeniedError, match="does not match resolved evidence"):
        service.submit_proposal(proposal=tampered)


def test_duplicate_proposal_file_attempt_is_exclusive(
    service: ProjectEvidenceService, tmp_path: Path
) -> None:
    service.outbox = ProposalOutbox(
        tmp_path / "outbox",
        service.identity,
        clock=lambda: datetime(2026, 8, 17, 12, 0, tzinfo=UTC),
        id_factory=lambda: "0123456789abcdef",
    )
    payload = proposal_payload(service)
    service.submit_proposal(proposal=payload)

    with pytest.raises(FileExistsError):
        service.submit_proposal(proposal=payload)
    assert len(list(service.outbox.root.glob("*.proposal.json"))) == 1


def test_proposal_outbox_rejects_symlink_escape(
    service: ProjectEvidenceService, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    linked_parent = tmp_path / "linked-parent"
    linked_parent.mkdir()
    outbox = linked_parent / "outbox"
    path_type = type(linked_parent)
    original_is_symlink = path_type.is_symlink

    def report_link(candidate: Path) -> bool:
        return candidate == linked_parent or original_is_symlink(candidate)

    monkeypatch.setattr(path_type, "is_symlink", report_link)
    service.outbox = ProposalOutbox(outbox, service.identity)

    with pytest.raises(ResourceDeniedError, match="symlink"):
        service.submit_proposal(proposal=proposal_payload(service))
    assert list(linked_parent.iterdir()) == []


def test_legitimate_a1_and_bounded_a2_are_classifications_not_authority(
    service: ProjectEvidenceService,
) -> None:
    a1 = proposal_payload(
        service,
        proposal_type=ProposalType.STRATEGY,
        authority_class=AuthorityClass.A1,
        domain=AffectedDomain.STRATEGY_RESEARCH,
    )
    a2 = proposal_payload(
        service,
        authority_class=AuthorityClass.A2,
        domain=AffectedDomain.BOUNDED_INVESTIGATION,
    )

    assert service.submit_proposal(proposal=a1)["authority_class"] == "A1"
    assert service.submit_proposal(proposal=a2)["authority_class"] == "A2"
    for path in service.outbox.root.glob("*.proposal.json"):
        persisted = json.loads(path.read_text(encoding="utf-8"))
        assert persisted["proposal"]["requested_authority"]["standing_authority"] is False
        assert persisted["proposal"]["requested_authority"]["direct_execution"] is False


def test_a2_rejects_domains_not_explicitly_low_risk(service: ProjectEvidenceService) -> None:
    payload = proposal_payload(
        service,
        authority_class=AuthorityClass.A2,
        domain=AffectedDomain.DEPENDENCY_MAINTENANCE,
    )

    with pytest.raises(ValidationError, match="A2 is limited"):
        service.submit_proposal(proposal=payload)


def test_exactly_seven_project_evidence_tools_remain_registered() -> None:
    module = ast.parse((REPO_ROOT / "tools/mcp/project_evidence/server.py").read_text())
    tools = {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "tool"
            for decorator in node.decorator_list
        )
    }
    assert tools == {
        "project_evidence_manifest",
        "list_project_resources",
        "read_project_resource",
        "run_evidence_query",
        "lookup_research_memory",
        "check_dependency_security_watch",
        "submit_proposal",
    }


def test_no_action_or_automatic_consumer_exists_for_typed_proposals() -> None:
    roots = [
        REPO_ROOT / "src",
        REPO_ROOT / "lib",
        REPO_ROOT / "tools/canon_intake",
        REPO_ROOT / "tools/runner",
        REPO_ROOT / "tools/search_governor",
        REPO_ROOT / "research/queue",
    ]
    needles = {
        "hermes_proposal_outbox",
        *(proposal_type.value for proposal_type in ProposalType),
    }
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if any(needle in text for needle in needles):
                hits.append(path.relative_to(REPO_ROOT).as_posix())
    assert hits == []
