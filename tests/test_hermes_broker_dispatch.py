from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tools.hermes.broker.acceptance import proof_registry as broker1_proof_registry
from tools.hermes.broker.dispatch import (
    BrokerDispatchResult,
    BrokerDryRunDispatchService,
    derive_dispatch_id,
)
from tools.hermes.broker.dry_run_adapter import (
    DRY_RUN_FAILED_REASON,
    DryRunAdapterResult,
    dry_run_noop,
)
from tools.hermes.broker.projection import (
    DRY_RUN_PROJECTION_SCHEMA_VERSION,
    DRY_RUN_PROOF_ACTION_TYPE,
    DRY_RUN_PROOF_ADAPTER_ID,
    DRY_RUN_PROOF_ADAPTER_VERSION,
    DRY_RUN_PROOF_REGISTRY_VERSION,
    Broker3ProofExecutableAction,
    DryRunProjectedParameters,
    DryRunProjection,
    ProjectionError,
    build_dry_run_projection,
    dry_run_proof_registry,
)
from tools.hermes.broker.registry import production_registry
from tools.hermes.broker.state import BrokerActionState, BrokerAuditEventType
from tools.hermes.proposals.models import A0_DOMAINS, AffectedDomain, AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]


def _action(
    *,
    outcome: str = "completed",
    adapter_id: str = DRY_RUN_PROOF_ADAPTER_ID,
    adapter_version: str = DRY_RUN_PROOF_ADAPTER_VERSION,
    registry_version: str = DRY_RUN_PROOF_REGISTRY_VERSION,
    action_id: str = "broker3-act-1",
) -> Broker3ProofExecutableAction:
    return Broker3ProofExecutableAction(
        executable_action_schema_version="hermes_executable_action_v1",
        executable_action_id=action_id,
        action_type=DRY_RUN_PROOF_ACTION_TYPE,
        prepared_record_id="HERMES-PREP-20260819T120000Z-1111111111111111",
        prepared_payload_sha256="a" * 64,
        source_proposal_id="HERMES-PROP-20260819T120000Z-1111111111111111",
        source_proposal_content_sha256="b" * 64,
        repo_sha="3" * 40,
        action_registry_version=registry_version,
        adapter_id=adapter_id,
        adapter_version=adapter_version,
        authority_class=AuthorityClass.A1,
        human_authored=True,
        hermes_authored=False,
        target={"kind": "broker3_dry_run_fixture", "fixture_id": action_id},
        scope={"domain": AffectedDomain.TEST_ONLY_TOOLING, "operation": "dry_run_noop_only"},
        parameters={"challenge": "exact-byte-proof", "requested_dry_run_outcome": outcome},
        budget_bound={"amount": 1, "unit": "proof-credit", "hard_limit": True},
        count_or_quantity_bound={"amount": 1, "unit": "decision", "hard_limit": True},
        timeout={"seconds": 60, "hard_limit": True},
    )


def _projection(**kwargs: Any) -> DryRunProjection:
    return build_dry_run_projection(
        action=kwargs.pop("action", _action()),
        action_registry=kwargs.pop("action_registry", dry_run_proof_registry()),
        approval_id=kwargs.pop("approval_id", "APPROVAL-broker3-act-1"),
        reservation_id=kwargs.pop("reservation_id", "BROKER-RES-" + "0" * 32),
        single_use_nonce=kwargs.pop("single_use_nonce", "f" * 64),
    )


def test_proof_registry_identity_is_exact_and_carries_no_callable() -> None:
    registry = dry_run_proof_registry()
    assert registry.version == DRY_RUN_PROOF_REGISTRY_VERSION
    assert len(registry.entries) == 1
    entry = registry.entries[0]
    assert entry.action_type == DRY_RUN_PROOF_ACTION_TYPE
    assert entry.adapter_id == DRY_RUN_PROOF_ADAPTER_ID
    assert entry.adapter_version == DRY_RUN_PROOF_ADAPTER_VERSION
    assert entry.required_authority_class is AuthorityClass.A1
    assert entry.affected_domains == frozenset({AffectedDomain.TEST_ONLY_TOOLING})
    assert not (entry.affected_domains & A0_DOMAINS)
    assert entry.dispatch_capable is False
    assert entry.proof_only is True
    assert not any(callable(value) for name, value in vars(entry).items() if "model" not in name)


def test_production_registry_still_has_zero_actions() -> None:
    assert production_registry().entries == ()


def test_typed_projection_binds_exact_reserved_identity() -> None:
    projection = _projection()
    assert projection.action_type == DRY_RUN_PROOF_ACTION_TYPE
    assert projection.action_registry_version == DRY_RUN_PROOF_REGISTRY_VERSION
    assert projection.adapter_id == DRY_RUN_PROOF_ADAPTER_ID
    assert projection.adapter_version == DRY_RUN_PROOF_ADAPTER_VERSION
    assert projection.approval_id == "APPROVAL-broker3-act-1"
    assert projection.reservation_id == "BROKER-RES-" + "0" * 32
    assert projection.single_use_nonce == "f" * 64
    assert projection.projection_schema_version == DRY_RUN_PROJECTION_SCHEMA_VERSION
    assert projection.dry_run is True
    assert projection.projected_parameters.requested_dry_run_outcome == "completed"
    assert projection.projected_parameters.fixture_id == "broker3-act-1"
    assert projection.projected_parameters.operation == "dry_run_noop_only"


def test_projection_and_its_canonical_hash_are_deterministic() -> None:
    first = _projection()
    second = _projection()
    assert first == second
    assert first.projection_sha256 == second.projection_sha256
    assert len(first.projection_sha256) == 64


def test_projection_has_no_generic_parameter_passthrough() -> None:
    # The closed projected-parameter schema is exactly these four typed fields.
    assert set(DryRunProjectedParameters.model_fields) == {
        "challenge",
        "requested_dry_run_outcome",
        "fixture_id",
        "operation",
    }


def test_projection_fails_closed_on_wrong_registry_adapter_and_type() -> None:
    with pytest.raises(ProjectionError, match="registry"):
        build_dry_run_projection(
            action=_action(),
            action_registry=broker1_proof_registry(),
            approval_id="APPROVAL-x",
            reservation_id="BROKER-RES-" + "0" * 32,
            single_use_nonce="f" * 64,
        )
    with pytest.raises(ProjectionError, match="registry version"):
        _projection(action=_action(registry_version="broker3-proof-registry-v2"))
    with pytest.raises(ProjectionError, match="adapter id"):
        _projection(action=_action(adapter_id="not-the-noop"))
    with pytest.raises(ProjectionError, match="adapter version"):
        _projection(action=_action(adapter_version="9.9.9"))


def test_extra_parameter_fails_action_validation_before_projection() -> None:
    with pytest.raises(ValidationError):
        Broker3ProofExecutableAction.model_validate(
            {
                **_action().model_dump(mode="python"),
                "parameters": {
                    "challenge": "x",
                    "requested_dry_run_outcome": "completed",
                    "extra": True,
                },
            }
        )


def test_wrong_action_type_literal_is_rejected_by_the_model() -> None:
    with pytest.raises(ValidationError):
        Broker3ProofExecutableAction.model_validate(
            {**_action().model_dump(mode="python"), "action_type": "broker3.proof.other_v1"}
        )


def test_no_op_adapter_completed_result_is_deterministic_and_inert() -> None:
    projection = _projection()
    first = dry_run_noop(projection)
    second = dry_run_noop(projection)
    assert first == second
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.outcome == "completed"
    assert first.reason_code is None
    assert first.downstream_side_effect is False
    assert first.projection_sha256 == projection.projection_sha256


def test_no_op_adapter_failed_result_is_deterministic_with_reason() -> None:
    projection = _projection(action=_action(outcome="failed"))
    result = dry_run_noop(projection)
    assert result.outcome == "failed"
    assert result.reason_code == DRY_RUN_FAILED_REASON
    assert result.downstream_side_effect is False


def test_no_op_adapter_result_model_is_closed() -> None:
    with pytest.raises(ValidationError):
        DryRunAdapterResult(
            adapter_id=DRY_RUN_PROOF_ADAPTER_ID,
            adapter_version=DRY_RUN_PROOF_ADAPTER_VERSION,
            projection_sha256="a" * 64,
            outcome="completed",
            reason_code="unexpected",
            downstream_side_effect=False,
        )
    with pytest.raises(ValidationError):
        DryRunAdapterResult(
            adapter_id=DRY_RUN_PROOF_ADAPTER_ID,
            adapter_version=DRY_RUN_PROOF_ADAPTER_VERSION,
            projection_sha256="a" * 64,
            outcome="failed",
            reason_code=None,
            downstream_side_effect=False,
        )


def test_dispatch_id_derivation_is_deterministic_and_binds_identity() -> None:
    first = _projection()
    assert derive_dispatch_id(first) == derive_dispatch_id(first)
    assert derive_dispatch_id(first).startswith("BROKER-DIS-")
    assert len(derive_dispatch_id(first)) == len("BROKER-DIS-") + 32
    other = _projection(action=_action(outcome="failed"))
    assert derive_dispatch_id(first) != derive_dispatch_id(other)


def test_closed_full_state_vocabulary_is_exactly_eight_values() -> None:
    assert {state.value for state in BrokerActionState} == {
        "submitted",
        "verified",
        "reserved",
        "rejected",
        "dispatched",
        "completed",
        "failed",
        "reconcile_required",
    }


def test_closed_full_audit_vocabulary_is_exactly_eight_values() -> None:
    assert {event.value for event in BrokerAuditEventType} == {
        "claim_submitted",
        "claim_verified",
        "claim_rejected",
        "nonce_reserved",
        "dispatch_requested",
        "dispatch_completed",
        "dispatch_failed",
        "reconcile_required",
    }


def _result(**overrides: Any) -> dict[str, Any]:
    base = {
        "outcome": "completed",
        "executable_action_id": "broker3-act-1",
        "executable_action_sha256": "a" * 64,
        "approval_id": "APPROVAL-broker3-act-1",
        "reservation_id": "BROKER-RES-" + "0" * 32,
        "dispatch_id": "BROKER-DIS-" + "0" * 32,
        "state": BrokerActionState.COMPLETED,
        "idempotent_existing": False,
        "reason_code": None,
        "downstream_side_effect": False,
    }
    base.update(overrides)
    return base


def test_broker3_result_contract_is_closed() -> None:
    assert BrokerDispatchResult(**_result()).outcome == "completed"
    assert (
        BrokerDispatchResult(
            **_result(
                outcome="failed",
                state=BrokerActionState.FAILED,
                reason_code=DRY_RUN_FAILED_REASON,
            )
        ).outcome
        == "failed"
    )
    assert (
        BrokerDispatchResult(
            **_result(
                outcome="reconcile_required",
                state=BrokerActionState.RECONCILE_REQUIRED,
                reason_code="dry_run_dispatch_completion_unknown",
            )
        ).state
        is BrokerActionState.RECONCILE_REQUIRED
    )
    assert (
        BrokerDispatchResult(
            **_result(
                outcome="rejected",
                state=BrokerActionState.REJECTED,
                reservation_id=None,
                dispatch_id=None,
                reason_code="a0_forbidden",
            )
        ).outcome
        == "rejected"
    )
    # completed cannot carry a reason; failed must; rejected cannot carry a dispatch.
    with pytest.raises(ValidationError):
        BrokerDispatchResult(**_result(reason_code="unexpected"))
    with pytest.raises(ValidationError):
        BrokerDispatchResult(**_result(outcome="failed", state=BrokerActionState.FAILED))
    with pytest.raises(ValidationError):
        BrokerDispatchResult(
            **_result(outcome="rejected", state=BrokerActionState.REJECTED, reason_code="x")
        )


def test_dry_run_adapter_import_surface_is_minimal() -> None:
    tree = ast.parse((REPO_ROOT / "tools/hermes/broker/dry_run_adapter.py").read_text())
    external_roots: set[str] = set()
    internal_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            external_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                internal_modules.add(node.module.split(".")[0])
            elif node.module:
                external_roots.add(node.module.split(".")[0])
    assert external_roots <= {"__future__", "typing", "pydantic"}
    assert internal_modules <= {"models", "projection"}


def test_dispatch_service_exposes_no_adapter_dispatcher_or_retry_seam() -> None:
    init_annotations = set(BrokerDryRunDispatchService.__init__.__annotations__)
    assert "adapter" not in init_annotations
    assert "dispatcher" not in init_annotations
    assert "callback" not in init_annotations
    assert "retry" not in init_annotations
