"""H3-1 first real A1 read-only action: registry, closed projection, result model.

This module carries no callable adapter, no network, no file capability, no
child-process capability, and no generic parameter passthrough. It defines exactly
one real, read-only, dispatch-capable A1 action and translates one reserved
executable action into one immutable, canonically hashed read-only projection.

The action is *read-only*: the fixed adapter (in
``tools.hermes.broker.adapters.readonly_repo_evidence``) only reads committed repo
evidence at the bound repo SHA and returns a structured summary record. Nothing in
the repo, the canonical store, or any protected surface is mutated.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from tools.hermes.proposals.models import AffectedDomain, AuthorityClass

from .models import (
    ExactBound,
    ExecutableAction,
    Identity,
    RepoSha,
    Sha256,
    StrictBrokerModel,
    TimeoutBound,
)
from .registry import REGISTRY_SCHEMA_VERSION, ActionRegistry, RegistryEntry
from .serialization import broker_sha256

READONLY_ACTION_TYPE = "h3_1.readonly.repo_evidence_summary_v1"
READONLY_REGISTRY_VERSION = "h3-1-readonly-registry-v1"
READONLY_ADAPTER_ID = "h3-1-readonly-repo-evidence"
READONLY_ADAPTER_VERSION = "1.0.0"
READONLY_PROJECTION_SCHEMA_VERSION = "hermes_broker_h3_1_readonly_projection_v1"
READONLY_RESULT_SCHEMA_VERSION = "hermes_broker_h3_1_readonly_result_v1"
READONLY_RESULT_IDENTITY_SCHEMA_VERSION = "hermes_broker_h3_1_readonly_result_identity_v1"

# The single fixed, non-protected evidence root and file selection for this first
# action: the committed Hermes broker/status evidence documents at the bound SHA.
READONLY_EVIDENCE_ROOT_RELPATH = "docs/status_entries"
READONLY_FILENAME_PREFIX = "WP-HERMES-"
READONLY_FILENAME_SUFFIX = ".md"
READONLY_OPERATION = "readonly_repo_evidence_summary_only"

# Hard read caps enforced by the adapter (also mirrored in the signed bounds).
READONLY_MAX_FILES = 512
READONLY_MAX_FILE_BYTES = 2_000_000

READONLY_OUTCOME = Literal["completed", "failed"]
# Deterministic controlled-failure reasons the adapter may return.
READONLY_FILE_COUNT_EXCEEDED_REASON = "matched_file_count_exceeds_cap"
READONLY_FILE_BYTES_EXCEEDED_REASON = "matched_file_exceeds_byte_cap"


class ProjectionError(ValueError):
    """Raised when an object has no permitted H3-1 read-only projection."""


class H3ReadonlyTarget(StrictBrokerModel):
    kind: Literal["repo_status_entry_evidence"]
    evidence_root_relpath: Literal["docs/status_entries"]


class H3ReadonlyScope(StrictBrokerModel):
    domain: Literal[AffectedDomain.BOUNDED_INVESTIGATION]
    operation: Literal["readonly_repo_evidence_summary_only"]


class H3ReadonlyParameters(StrictBrokerModel):
    filename_prefix: Literal["WP-HERMES-"]
    filename_suffix: Literal[".md"]
    max_files: Annotated[int, Field(ge=1, le=READONLY_MAX_FILES)]
    max_file_bytes: Annotated[int, Field(ge=1, le=READONLY_MAX_FILE_BYTES)]


class H3ReadonlyExecutableAction(
    ExecutableAction[H3ReadonlyTarget, H3ReadonlyScope, H3ReadonlyParameters]
):
    action_type: Literal[READONLY_ACTION_TYPE]


class H3ReadonlyProjectedParameters(StrictBrokerModel):
    """Closed schema; every field is copied explicitly from typed action fields."""

    evidence_root_relpath: Literal["docs/status_entries"]
    filename_prefix: Literal["WP-HERMES-"]
    filename_suffix: Literal[".md"]
    max_files: Annotated[int, Field(ge=1, le=READONLY_MAX_FILES)]
    max_file_bytes: Annotated[int, Field(ge=1, le=READONLY_MAX_FILE_BYTES)]
    operation: Literal["readonly_repo_evidence_summary_only"]


class H3ReadonlyProjection(StrictBrokerModel):
    """Immutable projected read-only request bound to one reserved authority claim."""

    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity
    single_use_nonce: Annotated[str, Field(pattern=r"^[0-9a-f]{32,128}$")]
    repo_sha: RepoSha
    action_type: Literal["h3_1.readonly.repo_evidence_summary_v1"]
    action_registry_version: Literal["h3-1-readonly-registry-v1"]
    adapter_id: Literal["h3-1-readonly-repo-evidence"]
    adapter_version: Literal["1.0.0"]
    projected_parameters: H3ReadonlyProjectedParameters
    projection_schema_version: Literal["hermes_broker_h3_1_readonly_projection_v1"]
    projection_sha256: Sha256
    read_only: Literal[True]


class H3EvidenceEntry(StrictBrokerModel):
    """One committed evidence file summarized read-only at the bound repo SHA."""

    relpath: Annotated[str, Field(min_length=1, max_length=500)]
    byte_size: Annotated[int, Field(ge=0, le=READONLY_MAX_FILE_BYTES)]
    sha256: Sha256


class H3ReadonlyResultRecord(StrictBrokerModel):
    """Immutable structured read-only report; it carries no mutation and no authority."""

    result_schema_version: Literal["hermes_broker_h3_1_readonly_result_v1"]
    result_record_id: Identity
    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity
    dispatch_id: Identity
    repo_sha: RepoSha
    action_type: Literal["h3_1.readonly.repo_evidence_summary_v1"]
    adapter_id: Literal["h3-1-readonly-repo-evidence"]
    adapter_version: Literal["1.0.0"]
    projection_sha256: Sha256
    evidence_root_relpath: Literal["docs/status_entries"]
    entries: tuple[H3EvidenceEntry, ...]
    file_count: Annotated[int, Field(ge=0, le=READONLY_MAX_FILES)]
    total_byte_size: Annotated[int, Field(ge=0)]
    outcome: READONLY_OUTCOME
    reason_code: str | None
    # Explicit read-only / no-side-effect assertions on every produced record.
    mutation_side_effect: Literal[False]
    protected_surface_touched: Literal[False]
    network_access: Literal[False]
    child_process_spawned: Literal[False]
    wrote_repo_or_canonical: Literal[False]


def h3_1_readonly_registry() -> ActionRegistry:
    """The single real production registry: one A1, read-only, dispatch-capable action."""

    return ActionRegistry(
        version=READONLY_REGISTRY_VERSION,
        entries=(
            RegistryEntry(
                registry_schema_version=REGISTRY_SCHEMA_VERSION,
                registry_version=READONLY_REGISTRY_VERSION,
                action_type=READONLY_ACTION_TYPE,
                action_model=H3ReadonlyExecutableAction,
                required_authority_class=AuthorityClass.A1,
                target_model=H3ReadonlyTarget,
                scope_model=H3ReadonlyScope,
                parameters_model=H3ReadonlyParameters,
                budget_model=ExactBound,
                count_or_quantity_model=ExactBound,
                timeout_model=TimeoutBound,
                adapter_id=READONLY_ADAPTER_ID,
                adapter_version=READONLY_ADAPTER_VERSION,
                affected_domains=frozenset({AffectedDomain.BOUNDED_INVESTIGATION}),
                # The first real dispatch-capable entry. It is read-only; the fixed
                # adapter performs only reads and carries no callable here.
                dispatch_capable=True,
                proof_only=False,
                read_only=True,
            ),
        ),
    )


def build_h3_readonly_projection(
    *,
    action: H3ReadonlyExecutableAction,
    action_registry: ActionRegistry,
    approval_id: str,
    reservation_id: str,
    single_use_nonce: str,
) -> H3ReadonlyProjection:
    """Fail-closed translation of one reserved read-only action into a read request."""

    if not isinstance(action, H3ReadonlyExecutableAction):
        raise ProjectionError("projection requires the exact H3-1 read-only action model")
    if action_registry.version != READONLY_REGISTRY_VERSION:
        raise ProjectionError("projection requires the exact H3-1 read-only registry version")
    entry = action_registry.get(READONLY_ACTION_TYPE)
    if entry is None:
        raise ProjectionError("projection registry has no H3-1 read-only entry")
    if action.action_type != READONLY_ACTION_TYPE:
        raise ProjectionError("unknown action_type for read-only projection")
    if action.action_registry_version != READONLY_REGISTRY_VERSION:
        raise ProjectionError("stale registry version for read-only projection")
    if action.adapter_id != READONLY_ADAPTER_ID:
        raise ProjectionError("wrong adapter id for read-only projection")
    if action.adapter_version != READONLY_ADAPTER_VERSION:
        raise ProjectionError("wrong adapter version for read-only projection")

    projected_parameters = H3ReadonlyProjectedParameters(
        evidence_root_relpath=action.target.evidence_root_relpath,
        filename_prefix=action.parameters.filename_prefix,
        filename_suffix=action.parameters.filename_suffix,
        max_files=action.parameters.max_files,
        max_file_bytes=action.parameters.max_file_bytes,
        operation=action.scope.operation,
    )
    action_sha256 = broker_sha256(action)
    identity_document = {
        "schema_version": READONLY_PROJECTION_SCHEMA_VERSION,
        "executable_action_id": action.executable_action_id,
        "executable_action_sha256": action_sha256,
        "approval_id": approval_id,
        "reservation_id": reservation_id,
        "single_use_nonce": single_use_nonce,
        "repo_sha": action.repo_sha,
        "action_type": READONLY_ACTION_TYPE,
        "action_registry_version": READONLY_REGISTRY_VERSION,
        "adapter_id": READONLY_ADAPTER_ID,
        "adapter_version": READONLY_ADAPTER_VERSION,
        "projected_parameters": projected_parameters.model_dump(mode="json"),
        "read_only": True,
    }
    projection_sha256 = broker_sha256(identity_document)
    return H3ReadonlyProjection(
        executable_action_id=action.executable_action_id,
        executable_action_sha256=action_sha256,
        approval_id=approval_id,
        reservation_id=reservation_id,
        single_use_nonce=single_use_nonce,
        repo_sha=action.repo_sha,
        action_type=READONLY_ACTION_TYPE,
        action_registry_version=READONLY_REGISTRY_VERSION,
        adapter_id=READONLY_ADAPTER_ID,
        adapter_version=READONLY_ADAPTER_VERSION,
        projected_parameters=projected_parameters,
        projection_schema_version=READONLY_PROJECTION_SCHEMA_VERSION,
        projection_sha256=projection_sha256,
        read_only=True,
    )


def derive_result_record_id(
    projection: H3ReadonlyProjection,
    dispatch_id: str,
    entries: tuple[H3EvidenceEntry, ...],
) -> str:
    """Derive one deterministic result-record identity from exact read bytes."""

    identity_document = {
        "schema_version": READONLY_RESULT_IDENTITY_SCHEMA_VERSION,
        "projection_sha256": projection.projection_sha256,
        "dispatch_id": dispatch_id,
        "entries": [entry.model_dump(mode="json") for entry in entries],
    }
    return f"H3RO-{broker_sha256(identity_document)[:32]}"
