from __future__ import annotations

import ast
import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tools.hermes.prepare.models import PREPARED_PAYLOAD_TYPES, PreparedPayloadType
from tools.hermes.prepare.serialization import canonical_json_bytes, canonical_sha256
from tools.hermes.prepare.validation import COMPATIBILITY_MATRIX
from tools.hermes.proposals.models import (
    AffectedDomain,
    AuthorityClass,
    ProposalType,
    TypedProposal,
)
from tools.mcp.project_evidence.models import ProjectEvidenceError, ResourceDeniedError
from tools.mcp.project_evidence.outbox import PreparedPayloadOutbox
from tools.mcp.project_evidence.service import ProjectEvidenceService

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "e67fe2773a64adce7947a98ea940ad3f58b14480"
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


def _proposal_body(proposal_type: ProposalType, ref: str) -> dict[str, Any]:
    common: dict[ProposalType, dict[str, Any]] = {
        ProposalType.STRATEGY: {
            "hypothesis": "A bounded mechanism may contain testable lab-only edge.",
            "mechanism": "A preregistered mechanism can be falsified offline.",
            "strategy_family": "test-family",
            "target_market_data_context": "Repo-evidenced BTC research context.",
            "why_it_may_contain_edge": "This remains an inference.",
            "evidence_basis": "The current status fixes the research boundary.",
            "proposed_lab_evaluation_concept": "Compare against a fixed null.",
            "falsification_criteria": ["Stop when the fixed criterion fails."],
            "expected_research_cost": "One bounded future lab package.",
            "claims_promotion_or_readiness": False,
        },
        ProposalType.STRATEGY_ADJUSTMENT: {
            "target_strategy_or_candidate_identity": "H-005",
            "observed_evidence_or_performance_issue": "A future lab question remains open.",
            "proposed_adjustment": "Draft a narrower offline comparison.",
            "why_adjustment_might_help": "This is an unproven inference.",
            "baseline_vs_adjustment_lab_test_concept": "Use fixed folds and costs.",
            "stop_or_falsification_condition": "Stop when the fixed delta is absent.",
            "application_scope": "future_lab_evaluation_only",
        },
        ProposalType.BUG_FIX: {
            "observed_defect_or_failure": "A hypothetical defect needs diagnosis.",
            "suspected_root_cause": "UNKNOWN.",
            "affected_components_or_files": [],
            "protected_boundary_assessment": "No action is authorized.",
            "proposed_fix_scope": "Draft a future bounded package.",
            "validation_plan": ["Reproduce before any future fix."],
            "rollback_notes": "Nothing changes in PREPARE.",
            "confidence": 0.5,
        },
        ProposalType.LAB_IMPROVEMENT: {
            "observed_bottleneck_waste_or_failure_mode": "A lab review is manual.",
            "evidence_or_metrics": "Current exact metric is UNKNOWN.",
            "proposed_lab_or_process_improvement": "Draft a bounded review aid.",
            "expected_throughput_reliability_or_value_effect": "Potential review value.",
            "measurement_plan": ["Compare fixed review outputs."],
            "rollback_or_stop_condition": "Stop if fidelity falls.",
        },
        ProposalType.DATA_ACQUISITION: {
            "requested_dataset_or_source": "A future exact public source.",
            "research_question_enabled": "Whether it adds independent information.",
            "provenance_or_source_identity": "UNKNOWN pending review.",
            "availability_or_timing_assumptions": "UNKNOWN pending review.",
            "storage_compute_network_cost_impact": "UNKNOWN pending review.",
            "validation_plan": ["Verify source, checksum, schema, and gaps."],
            "data_quality_risks": ["Source revisions"],
            "silent_repair_or_fabrication_allowed": False,
        },
        ProposalType.DEPENDENCY_UPGRADE: {
            "dependency_and_current_version": "mcp==1.28.1",
            "proposed_target_or_change": "UNKNOWN pending repo evidence.",
            "evidence_or_source": "The repo status is the only FACT source.",
            "compatibility_concerns": "Must be tested in a future package.",
            "security_or_reliability_rationale": "Advisory only.",
            "validation_plan": ["Run focused compatibility tests later."],
            "rollback_plan": "Restore the exact prior lock later.",
            "automatic_install_or_update": False,
        },
        ProposalType.INVESTIGATION: {
            "observed_question_or_anomaly": "Which exact evidence gap matters?",
            "why_investigation_is_valuable": "It may focus human review.",
            "bounded_investigation_scope": "Read only exact allowlisted evidence.",
            "expected_output": "A cited non-authoritative diagnostic.",
            "expected_cost_and_time": "One bounded future review.",
            "stop_conditions": ["Stop on missing or conflicting evidence."],
        },
    }
    return {
        "proposal_type": proposal_type.value,
        "evidence_refs": [ref],
        **common[proposal_type],
    }


def _default_domain(proposal_type: ProposalType) -> AffectedDomain:
    return {
        ProposalType.STRATEGY: AffectedDomain.STRATEGY_RESEARCH,
        ProposalType.STRATEGY_ADJUSTMENT: AffectedDomain.STRATEGY_ADJUSTMENT_RESEARCH,
        ProposalType.BUG_FIX: AffectedDomain.BUG_FIX,
        ProposalType.LAB_IMPROVEMENT: AffectedDomain.LAB_PROCESS,
        ProposalType.DATA_ACQUISITION: AffectedDomain.DATA_ACQUISITION,
        ProposalType.DEPENDENCY_UPGRADE: AffectedDomain.DEPENDENCY_MAINTENANCE,
        ProposalType.INVESTIGATION: AffectedDomain.BOUNDED_INVESTIGATION,
    }[proposal_type]


def _default_class(proposal_type: ProposalType) -> AuthorityClass:
    if proposal_type in {ProposalType.LAB_IMPROVEMENT, ProposalType.INVESTIGATION}:
        return AuthorityClass.A2
    return AuthorityClass.A1


def _create_parent(
    service: ProjectEvidenceService,
    proposal_type: ProposalType,
    *,
    authority_class: AuthorityClass | None = None,
    domain: AffectedDomain | None = None,
    ref: str = STATUS_REF,
) -> tuple[dict[str, Any], TypedProposal]:
    selected_class = authority_class or _default_class(proposal_type)
    selected_domain = domain or _default_domain(proposal_type)
    payload = {
        "schema_version": "hermes_typed_proposal_v1",
        "proposal_type": proposal_type.value,
        "title": f"Source for {proposal_type.value}",
        "repo_sha": REPO_SHA,
        "source_session_id": "hermes-h25-test-session",
        "evidence_refs": [ref],
        "evidence_anchors": [_anchor(service, ref)],
        "facts": [{"statement": "Exact repo evidence is available.", "evidence_refs": [ref]}],
        "inferences": ["A future human-reviewed plan may help."],
        "open_questions": ["Whether a human will authorize later work."],
        "rationale": "Create an inert source proposal only.",
        "expected_benefit": "A reviewable future decision surface.",
        "confidence": 0.6,
        "affected_scope": ["proposal outbox only"],
        "affected_domains": [selected_domain.value],
        "authority_class": selected_class.value,
        "estimates": {"cost": "UNKNOWN", "compute": "bounded", "time": "bounded"},
        "requested_authority": {
            "kind": "human_review_for_separate_work_package",
            "description": "Human review only.",
            "self_approval": False,
            "direct_execution": False,
            "standing_authority": False,
        },
        "approval_required": True,
        "validation_plan": ["Re-resolve exact evidence."],
        "rollback_or_stop_conditions": ["Stop on conflicting evidence."],
        "not_authority": True,
        "review_required": True,
        "automatic_consumers": [],
        "body": _proposal_body(proposal_type, ref),
    }
    typed = TypedProposal.model_validate(payload)
    return service.submit_proposal(proposal=typed), typed


def _prepared_body(prepared_type: PreparedPayloadType) -> dict[str, Any]:
    return {
        PreparedPayloadType.STRATEGY_LAB: {
            "future_lab_only_experiment_or_spec_draft": "Draft one offline experiment.",
            "parameters_or_search_space_draft": ["window is an exact string range"],
            "data_or_evidence_inputs": [STATUS_REF],
            "falsification_criteria": ["Reject on the fixed null criterion."],
            "candidate_or_promotion_authority": False,
            "go_authority": False,
        },
        PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN: {
            "intended_future_campaign_purpose": "Draft a bounded legal search campaign.",
            "intended_surface": "tools/research_search",
            "legal_search_intent": "Use only a future Governor-approved surface.",
            "seed": 17,
            "objective": "Evaluate a preregistered research objective.",
            "constraints": ["No holdout access."],
            "holdout_access": False,
            "governor_call": False,
            "winner_semantics": False,
        },
        PreparedPayloadType.CODEX_WORK_PACKAGE: {
            "objective": "Draft one future bounded research-tooling package.",
            "why_now": "Exact repo evidence identifies a review question.",
            "allowed_scope": ["research tooling only"],
            "forbidden_scope": ["runtime, canonical writers, dispatch, and KDAUTH"],
            "expected_files_or_targets": ["UNKNOWN until human review"],
            "dependencies": [],
            "model_recommendation": "strong",
            "reasoning_recommendation": "HIGH",
            "explicitly_non_protected_research_tooling": True,
            "task_creation": False,
            "branch_creation": False,
            "pull_request_creation": False,
        },
        PreparedPayloadType.PREFECT_WORKFLOW: {
            "future_workflow_definition": "Draft one future workflow definition.",
            "tasks": [
                {
                    "task_name": "read evidence",
                    "future_behavior": "Read an exact future input.",
                    "inputs": ["evidence ref"],
                    "outputs": ["review artifact"],
                }
            ],
            "workflow_inputs": ["exact evidence"],
            "workflow_outputs": ["future inert artifact"],
            "retry_expectations": "No automatic retry in H2.5.",
            "timeout_expectations": "Use the envelope hard timeout.",
            "idempotency_expectations": "A future design must define idempotency.",
            "evidence_or_output_contract": "Outputs remain non-authoritative.",
            "prefect_call": False,
            "deployment_creation": False,
            "workflow_run": False,
        },
        PreparedPayloadType.BOUNDED_DIAGNOSTIC: {
            "diagnostic_question": "What exact evidence explains the question?",
            "read_only_targets": ["docs/project_status.md"],
            "allowed_diagnostic_concept": "A future read-only comparison.",
            "diagnostic_outputs": ["cited report"],
            "execution": False,
        },
        PreparedPayloadType.DATA_HYDRATION: {
            "source": "UNKNOWN pending exact source review.",
            "dataset": "UNKNOWN pending exact source review.",
            "exact_range": "UNKNOWN pending exact source review.",
            "storage_estimate": "UNKNOWN",
            "network_estimate": "UNKNOWN",
            "provenance_rules": ["Record exact source identity."],
            "checksum_rules": ["Verify exact bytes before any future use."],
            "causality_rules": ["Prevent look-ahead in any future design."],
            "availability_rules": ["Treat missing data as unavailable."],
            "network_access": False,
            "hydration": False,
        },
        PreparedPayloadType.DEPENDENCY_MAINTENANCE: {
            "repo_evidenced_current_dependency": "mcp==1.28.1",
            "proposed_target_or_unknown": "UNKNOWN",
            "compatibility_plan": ["Run focused tests in a future package."],
            "lock_update_plan": ["Draft exact lock changes only after review."],
            "rollback_plan": ["Restore the prior exact lock."],
            "watch_advisory_context": ["Any live watch observation is advisory only."],
            "install_or_update": False,
            "transient_watch_fact": False,
        },
    }[prepared_type]


def _future_action(prepared_type: PreparedPayloadType) -> str:
    return {
        PreparedPayloadType.STRATEGY_LAB: "future_strategy_lab_experiment_or_spec_draft",
        PreparedPayloadType.SEARCH_GOVERNOR_CAMPAIGN: ("future_search_governor_campaign_draft"),
        PreparedPayloadType.CODEX_WORK_PACKAGE: "future_codex_work_package_draft",
        PreparedPayloadType.PREFECT_WORKFLOW: "future_prefect_workflow_definition_draft",
        PreparedPayloadType.BOUNDED_DIAGNOSTIC: ("future_read_only_bounded_diagnostic_draft"),
        PreparedPayloadType.DATA_HYDRATION: "future_data_hydration_plan_draft",
        PreparedPayloadType.DEPENDENCY_MAINTENANCE: ("future_dependency_maintenance_plan_draft"),
    }[prepared_type]


def prepared_payload(
    service: ProjectEvidenceService,
    prepared_type: PreparedPayloadType,
    proposal_type: ProposalType,
    *,
    authority_class: AuthorityClass | None = None,
    domain: AffectedDomain | None = None,
    ref: str = STATUS_REF,
) -> dict[str, Any]:
    parent_result, parent = _create_parent(
        service,
        proposal_type,
        authority_class=authority_class,
        domain=domain,
        ref=ref,
    )
    payload: dict[str, Any] = {
        "schema_version": "hermes_prepared_payload_v1",
        "prepared_payload_type": prepared_type.value,
        "repo_sha": REPO_SHA,
        "source_session_id": parent.source_session_id,
        "source_proposal_id": parent_result["proposal_id"],
        "source_proposal_type": parent.proposal_type.value,
        "source_proposal_content_sha256": canonical_sha256(parent),
        "source_proposal_repo_sha": parent.repo_sha,
        "source_authority_class": parent.authority_class.value,
        "evidence_refs": [ref],
        "evidence_anchors": [_anchor(service, ref)],
        "facts": [{"statement": "Exact repo evidence is available.", "evidence_refs": [ref]}],
        "inferences": ["A future human-reviewed plan may help."],
        "open_questions": ["Whether a later package will be authorized."],
        "future_action_type": _future_action(prepared_type),
        "target": "One exact future target defined for human review only.",
        "scope": "One inert bounded plan; no action.",
        "parameters": {"mode": "draft", "unicode": "México/東京"},
        "count_or_quantity_bound": {"amount": 10, "unit": "items", "hard_limit": True},
        "budget_bound": {"amount": 100, "unit": "review credits", "hard_limit": True},
        "timeout": {"seconds": 900, "hard_limit": True},
        "expected_outputs": ["One inert review artifact."],
        "validation_plan": ["Re-resolve evidence and repeat canonical hashing."],
        "rollback_or_stop_conditions": ["Stop on missing or conflicting evidence."],
        "authority_class": parent.authority_class.value,
        "human_review_required": True,
        "not_authority": True,
        "automatic_consumers": [],
        "self_approval": False,
        "direct_execution": False,
        "standing_authority": False,
        "approval_token_eligible": False,
        "broker_eligible": False,
        "dispatch_eligible": False,
        "body": _prepared_body(prepared_type),
    }
    if parent.authority_class is AuthorityClass.A0:
        payload["permanent_non_executable"] = True
        payload["protected_human_gate_only"] = True
    return payload


@pytest.mark.parametrize(
    ("prepared_type", "proposal_type"),
    [
        (prepared_type, proposal_type)
        for prepared_type, proposal_types in COMPATIBILITY_MATRIX.items()
        for proposal_type in proposal_types
    ],
)
def test_closed_compatibility_matrix_accepts_valid_pairs(
    service: ProjectEvidenceService,
    prepared_type: PreparedPayloadType,
    proposal_type: ProposalType,
) -> None:
    result = service.submit_prepared_payload(
        prepared_payload=prepared_payload(service, prepared_type, proposal_type)
    )
    assert result["prepared_payload_type"] == prepared_type.value
    assert result["not_authority"] is True
    assert result["automatic_consumers"] == []


@pytest.mark.parametrize("prepared_type", list(PreparedPayloadType))
def test_all_seven_identities_persist_canonical_hash_scoped_records(
    service: ProjectEvidenceService, prepared_type: PreparedPayloadType
) -> None:
    proposal_type = next(iter(COMPATIBILITY_MATRIX[prepared_type]))
    payload = prepared_payload(service, prepared_type, proposal_type)
    result = service.submit_prepared_payload(prepared_payload=payload)
    path = service.prepared_outbox.root / result["outbox_file"]
    record = json.loads(path.read_text(encoding="utf-8"))

    assert path.name.endswith(".prepared.json")
    assert path.read_bytes() == canonical_json_bytes(record)
    nested_bytes = canonical_json_bytes(record["prepared_payload"])
    assert hashlib.sha256(nested_bytes).hexdigest() == record["prepared_payload_sha256"]
    assert result["prepared_payload_sha256"] == record["prepared_payload_sha256"]
    outer_mutation = copy.deepcopy(record)
    outer_mutation["created_at_utc"] = "2099-01-01T00:00:00Z"
    assert canonical_sha256(outer_mutation["prepared_payload"]) == result["prepared_payload_sha256"]


def test_canonical_serialization_is_repeatable_order_independent_lf_and_unicode() -> None:
    left = {"z": ["東京", "México"], "a": {"y": 2, "x": True}}
    right = {"a": {"x": True, "y": 2}, "z": ["東京", "México"]}
    first = canonical_json_bytes(left)
    assert first == canonical_json_bytes(left) == canonical_json_bytes(right)
    assert first.endswith(b"\n") and not first.endswith(b"\n\n")
    assert b"\r\n" not in first
    assert "東京".encode() in first and b"\\u" not in first


def test_a0_is_permanently_non_executable_and_cannot_be_relabelled(
    service: ProjectEvidenceService,
) -> None:
    payload = prepared_payload(
        service,
        PreparedPayloadType.STRATEGY_LAB,
        ProposalType.STRATEGY_ADJUSTMENT,
        authority_class=AuthorityClass.A0,
        domain=AffectedDomain.STRATEGY_SPEC_AUTHORITY_MUTATION,
    )
    result = service.submit_prepared_payload(prepared_payload=payload)
    assert result["authority_class"] == "A0"
    for mutation in (
        lambda value: value.update(authority_class="A1"),
        lambda value: value.update(source_authority_class="A2", authority_class="A2"),
        lambda value: value.update(permanent_non_executable=False),
        lambda value: value.update(protected_human_gate_only=False),
        lambda value: value.update(broker_eligible=True),
        lambda value: value.update(approval_token_eligible=True),
        lambda value: value.update(dispatch_eligible=True),
    ):
        invalid = copy.deepcopy(payload)
        mutation(invalid)
        with pytest.raises(REJECTIONS):
            service.submit_prepared_payload(prepared_payload=invalid)


@pytest.mark.parametrize(
    ("case", "mutation"),
    [
        ("fabricated parent hash", lambda p: p.update(source_proposal_content_sha256="0" * 64)),
        ("parent type mismatch", lambda p: p.update(source_proposal_type="BugFixProposal")),
        ("repo SHA mismatch", lambda p: p.update(repo_sha="0" * 40)),
        ("authority mismatch", lambda p: p.update(authority_class="A1")),
        ("self approval", lambda p: p.update(self_approval=True)),
        ("direct execution", lambda p: p.update(direct_execution=True)),
        ("standing authority", lambda p: p.update(standing_authority=True)),
        ("automatic consumer", lambda p: p.update(automatic_consumers=["runner"])),
        (
            "fabricated evidence",
            lambda p: p["evidence_anchors"][0]["evidence_identities"][0].update(sha256="0" * 64),
        ),
        ("missing FACT evidence", lambda p: p.update(facts=[])),
        ("unsupported prepared type", lambda p: p.update(prepared_payload_type="Unknown")),
        ("malformed typed body", lambda p: p["body"].pop("execution")),
        (
            "embedded approval token",
            lambda p: p["parameters"].update(approval_token="secret"),
        ),
        (
            "broker endpoint",
            lambda p: p["parameters"].update(broker_endpoint="https://broker.invalid"),
        ),
        (
            "automatic dispatch target",
            lambda p: p["parameters"].update(automatic_dispatch_target="runner"),
        ),
        (
            "already authorized state",
            lambda p: p["parameters"].update(already_approved=True),
        ),
    ],
)
def test_adversarial_payloads_reject_without_prepared_write(
    service: ProjectEvidenceService, case: str, mutation: Any
) -> None:
    payload = prepared_payload(
        service, PreparedPayloadType.BOUNDED_DIAGNOSTIC, ProposalType.INVESTIGATION
    )
    before = list(service.prepared_outbox.root.glob("*.prepared.json"))
    mutation(payload)
    with pytest.raises(REJECTIONS):
        service.submit_prepared_payload(prepared_payload=payload)
    assert list(service.prepared_outbox.root.glob("*.prepared.json")) == before


def test_missing_parent_rejects_without_write(service: ProjectEvidenceService) -> None:
    payload = prepared_payload(
        service, PreparedPayloadType.BOUNDED_DIAGNOSTIC, ProposalType.INVESTIGATION
    )
    payload["source_proposal_id"] = "HERMES-PROP-20260101T000000Z-0000000000000000"
    with pytest.raises(ProjectEvidenceError, match="absent"):
        service.submit_prepared_payload(prepared_payload=payload)
    assert not list(service.prepared_outbox.root.glob("*.prepared.json"))


def test_invalid_source_prepared_mapping_rejects(service: ProjectEvidenceService) -> None:
    payload = prepared_payload(
        service, PreparedPayloadType.STRATEGY_LAB, ProposalType.DATA_ACQUISITION
    )
    with pytest.raises(ResourceDeniedError, match="incompatible"):
        service.submit_prepared_payload(prepared_payload=payload)
    assert not list(service.prepared_outbox.root.glob("*.prepared.json"))


def test_parent_symlink_path_is_rejected(
    service: ProjectEvidenceService, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = prepared_payload(
        service, PreparedPayloadType.BOUNDED_DIAGNOSTIC, ProposalType.INVESTIGATION
    )
    source_path = service.outbox.root / f"{payload['source_proposal_id']}.proposal.json"
    path_type = type(source_path)
    original = path_type.is_symlink
    monkeypatch.setattr(
        path_type,
        "is_symlink",
        lambda path: path == source_path or original(path),
    )
    with pytest.raises(ResourceDeniedError, match="regular non-symlink"):
        service.submit_prepared_payload(prepared_payload=payload)
    assert not list(service.prepared_outbox.root.glob("*.prepared.json"))


def test_research_memory_and_watch_cannot_anchor_facts(
    service: ProjectEvidenceService,
) -> None:
    memory_payload = prepared_payload(
        service,
        PreparedPayloadType.BOUNDED_DIAGNOSTIC,
        ProposalType.INVESTIGATION,
        ref="project://research-memory-index",
    )
    with pytest.raises(ResourceDeniedError, match="index/hint"):
        service.submit_prepared_payload(prepared_payload=memory_payload)

    watch_payload = copy.deepcopy(memory_payload)
    watch_payload["evidence_refs"] = ["watch://dependency/mcp"]
    watch_payload["evidence_anchors"][0]["ref"] = "watch://dependency/mcp"
    watch_payload["facts"][0]["evidence_refs"] = ["watch://dependency/mcp"]
    with pytest.raises(ValidationError):
        service.submit_prepared_payload(prepared_payload=watch_payload)


def test_duplicate_prepared_id_is_exclusive(service: ProjectEvidenceService) -> None:
    service.prepared_outbox = PreparedPayloadOutbox(
        service.outbox.root,
        service.identity,
        clock=lambda: datetime(2026, 8, 17, 12, 0, tzinfo=UTC),
        id_factory=lambda: "0123456789abcdef",
    )
    payload = prepared_payload(
        service, PreparedPayloadType.BOUNDED_DIAGNOSTIC, ProposalType.INVESTIGATION
    )
    service.submit_prepared_payload(prepared_payload=payload)
    with pytest.raises(FileExistsError):
        service.submit_prepared_payload(prepared_payload=payload)
    assert len(list(service.prepared_outbox.root.glob("*.prepared.json"))) == 1


def test_outbox_symlink_escape_is_rejected(
    service: ProjectEvidenceService, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = prepared_payload(
        service, PreparedPayloadType.BOUNDED_DIAGNOSTIC, ProposalType.INVESTIGATION
    )
    root = service.outbox.root
    path_type = type(root)
    original = path_type.is_symlink
    monkeypatch.setattr(path_type, "is_symlink", lambda path: path == root or original(path))
    with pytest.raises(ResourceDeniedError, match="symlink"):
        service.submit_prepared_payload(prepared_payload=payload)
    assert not list(root.glob("*.prepared.json"))


def test_stable_identities_and_exactly_eight_mcp_tools() -> None:
    assert tuple(PREPARED_PAYLOAD_TYPES) == tuple(PreparedPayloadType)
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
        "submit_prepared_payload",
    }


def test_actual_surfaces_have_no_prepared_consumer_or_dispatch() -> None:
    existing_surfaces = {
        "search_governor": REPO_ROOT / "tools/research_search",
        "dispatch_kdauth_and_canonical_writers": REPO_ROOT / "tools/canon_intake",
        "offline_runner": REPO_ROOT / "tools/research_runner",
        "execution_adapter": REPO_ROOT / "tools/canon_intake/execution_runner_adapter.py",
        "runtime_paper_execution_overlay": REPO_ROOT / "src",
        "canonical_queue": REPO_ROOT / "research/queue",
    }
    assert all(path.exists() for path in existing_surfaces.values())
    needles = (
        ".prepared.json",
        "PreparedPayload",
        "submit_prepared_payload",
        "HERMES-PREP",
    )
    hits: list[str] = []
    for path in existing_surfaces.values():
        candidates = [path] if path.is_file() else path.rglob("*")
        for candidate in candidates:
            if not candidate.is_file() or candidate.is_symlink():
                continue
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            if any(needle in text for needle in needles):
                hits.append(candidate.relative_to(REPO_ROOT).as_posix())
    assert hits == []

    implementation_paths = [
        path
        for path in REPO_ROOT.rglob("*.py")
        if "tools/hermes" not in path.relative_to(REPO_ROOT).as_posix()
        and "tools/mcp/project_evidence" not in path.relative_to(REPO_ROOT).as_posix()
        and "tests" not in path.parts
    ]
    implementation_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in implementation_paths
    ).lower()
    assert "prefect" not in implementation_text
    assert "codexworkpackagepreparedpayload" not in implementation_text
