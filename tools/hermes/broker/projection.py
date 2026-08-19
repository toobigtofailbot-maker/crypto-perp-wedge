"""Fixed BROKER-3 dry-run proof registry and one closed typed projection.

This module carries no callable adapter, no network, no file capability, no
child-process capability, and no generic parameter passthrough. It translates
exactly one closed proof executable action into one immutable, canonically
hashed dry-run projection.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from tools.hermes.proposals.models import AffectedDomain, AuthorityClass

from .models import (
    ExactBound,
    ExecutableAction,
    Identity,
    Sha256,
    StrictBrokerModel,
    TimeoutBound,
)
from .registry import REGISTRY_SCHEMA_VERSION, ActionRegistry, RegistryEntry
from .serialization import broker_sha256

DRY_RUN_PROOF_ACTION_TYPE = "broker3.proof.dry_run_noop_v1"
DRY_RUN_PROOF_REGISTRY_VERSION = "broker3-proof-registry-v1"
DRY_RUN_PROOF_ADAPTER_ID = "broker3-dry-run-noop"
DRY_RUN_PROOF_ADAPTER_VERSION = "1.0.0"
DRY_RUN_PROJECTION_SCHEMA_VERSION = "hermes_broker_dry_run_projection_v1"

DRY_RUN_OUTCOME = Literal["completed", "failed"]
DRY_RUN_OPERATION = "dry_run_noop_only"


class ProjectionError(ValueError):
    """Raised when an object has no permitted BROKER-3 dry-run projection."""


class Broker3ProofTarget(StrictBrokerModel):
    kind: Literal["broker3_dry_run_fixture"]
    fixture_id: Identity


class Broker3ProofScope(StrictBrokerModel):
    domain: Literal[AffectedDomain.TEST_ONLY_TOOLING]
    operation: Literal["dry_run_noop_only"]


class Broker3ProofParameters(StrictBrokerModel):
    challenge: Annotated[str, Field(min_length=1, max_length=128)]
    requested_dry_run_outcome: DRY_RUN_OUTCOME


class Broker3ProofExecutableAction(
    ExecutableAction[Broker3ProofTarget, Broker3ProofScope, Broker3ProofParameters]
):
    action_type: Literal[DRY_RUN_PROOF_ACTION_TYPE]


class DryRunProjectedParameters(StrictBrokerModel):
    """Closed schema; every field is copied explicitly from typed action fields."""

    challenge: Annotated[str, Field(min_length=1, max_length=128)]
    requested_dry_run_outcome: DRY_RUN_OUTCOME
    fixture_id: Identity
    operation: Literal["dry_run_noop_only"]


class DryRunProjection(StrictBrokerModel):
    """Immutable projected dry-run request bound to one reserved authority claim."""

    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity
    single_use_nonce: Annotated[str, Field(pattern=r"^[0-9a-f]{32,128}$")]
    action_type: Literal["broker3.proof.dry_run_noop_v1"]
    action_registry_version: Literal["broker3-proof-registry-v1"]
    adapter_id: Literal["broker3-dry-run-noop"]
    adapter_version: Literal["1.0.0"]
    projected_parameters: DryRunProjectedParameters
    projection_schema_version: Literal["hermes_broker_dry_run_projection_v1"]
    projection_sha256: Sha256
    dry_run: Literal[True]


def dry_run_proof_registry() -> ActionRegistry:
    """The single proof-only registry that identifies the fixed no-op adapter."""

    return ActionRegistry(
        version=DRY_RUN_PROOF_REGISTRY_VERSION,
        entries=(
            RegistryEntry(
                registry_schema_version=REGISTRY_SCHEMA_VERSION,
                registry_version=DRY_RUN_PROOF_REGISTRY_VERSION,
                action_type=DRY_RUN_PROOF_ACTION_TYPE,
                action_model=Broker3ProofExecutableAction,
                required_authority_class=AuthorityClass.A1,
                target_model=Broker3ProofTarget,
                scope_model=Broker3ProofScope,
                parameters_model=Broker3ProofParameters,
                budget_model=ExactBound,
                count_or_quantity_model=ExactBound,
                timeout_model=TimeoutBound,
                adapter_id=DRY_RUN_PROOF_ADAPTER_ID,
                adapter_version=DRY_RUN_PROOF_ADAPTER_VERSION,
                affected_domains=frozenset({AffectedDomain.TEST_ONLY_TOOLING}),
                # BROKER-1 registry model forbids a dispatch-capable entry; the
                # proof entry stays non-dispatch-capable and carries no callable.
                dispatch_capable=False,
                proof_only=True,
            ),
        ),
    )


def build_dry_run_projection(
    *,
    action: Broker3ProofExecutableAction,
    action_registry: ActionRegistry,
    approval_id: str,
    reservation_id: str,
    single_use_nonce: str,
) -> DryRunProjection:
    """Fail-closed translation of one reserved proof action into a dry-run request."""

    if not isinstance(action, Broker3ProofExecutableAction):
        raise ProjectionError("projection requires the exact broker3 proof action model")
    if action_registry.version != DRY_RUN_PROOF_REGISTRY_VERSION:
        raise ProjectionError("projection requires the exact broker3 proof registry version")
    entry = action_registry.get(DRY_RUN_PROOF_ACTION_TYPE)
    if entry is None:
        raise ProjectionError("projection registry has no broker3 proof entry")
    if action.action_type != DRY_RUN_PROOF_ACTION_TYPE:
        raise ProjectionError("unknown action_type for dry-run projection")
    if action.action_registry_version != DRY_RUN_PROOF_REGISTRY_VERSION:
        raise ProjectionError("stale registry version for dry-run projection")
    if action.adapter_id != DRY_RUN_PROOF_ADAPTER_ID:
        raise ProjectionError("wrong adapter id for dry-run projection")
    if action.adapter_version != DRY_RUN_PROOF_ADAPTER_VERSION:
        raise ProjectionError("wrong adapter version for dry-run projection")

    projected_parameters = DryRunProjectedParameters(
        challenge=action.parameters.challenge,
        requested_dry_run_outcome=action.parameters.requested_dry_run_outcome,
        fixture_id=action.target.fixture_id,
        operation=action.scope.operation,
    )
    action_sha256 = broker_sha256(action)
    identity_document = {
        "schema_version": DRY_RUN_PROJECTION_SCHEMA_VERSION,
        "executable_action_id": action.executable_action_id,
        "executable_action_sha256": action_sha256,
        "approval_id": approval_id,
        "reservation_id": reservation_id,
        "single_use_nonce": single_use_nonce,
        "action_type": DRY_RUN_PROOF_ACTION_TYPE,
        "action_registry_version": DRY_RUN_PROOF_REGISTRY_VERSION,
        "adapter_id": DRY_RUN_PROOF_ADAPTER_ID,
        "adapter_version": DRY_RUN_PROOF_ADAPTER_VERSION,
        "projected_parameters": projected_parameters.model_dump(mode="json"),
        "dry_run": True,
    }
    projection_sha256 = broker_sha256(identity_document)
    return DryRunProjection(
        executable_action_id=action.executable_action_id,
        executable_action_sha256=action_sha256,
        approval_id=approval_id,
        reservation_id=reservation_id,
        single_use_nonce=single_use_nonce,
        action_type=DRY_RUN_PROOF_ACTION_TYPE,
        action_registry_version=DRY_RUN_PROOF_REGISTRY_VERSION,
        adapter_id=DRY_RUN_PROOF_ADAPTER_ID,
        adapter_version=DRY_RUN_PROOF_ADAPTER_VERSION,
        projected_parameters=projected_parameters,
        projection_schema_version=DRY_RUN_PROJECTION_SCHEMA_VERSION,
        projection_sha256=projection_sha256,
        dry_run=True,
    )
