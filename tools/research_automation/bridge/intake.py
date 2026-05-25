"""AUTO bridge intake/source-layer primitives.

This module validates explicit caller-provided source identity only. It does
not scan files, transform AUTO output, write artifacts, or expose query-layer
state.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


POST_BRIDGE_ELIGIBILITY_MARKER = "post_bridge"
LOCAL_ONLY_STATE_MARKER = "local_only_non_canonical"

_FORBIDDEN_BINDING_KEYS = frozenset(
    {
        "a2c",
        "a2c_id",
        "candidate",
        "candidate_binding",
        "candidate_id",
        "candidate_symbol",
        "cohort",
        "cohort_id",
        "evidence_track",
        "hypothesis_id",
        "path_b",
        "selected_candidate",
        "symbol",
    }
)
_FORBIDDEN_CANONICAL_KEYS = frozenset(
    {
        "canonical",
        "canonical_artifact",
        "canonical_artifact_path",
        "canonical_status",
        "canonical_target",
        "committed_artifact",
        "creates_canonical_artifact",
        "creates_committed_evidence",
        "evidence_artifact",
        "is_canonical",
        "registry_artifact",
        "research_artifact",
    }
)
_FORBIDDEN_COMMITMENT_KEYS = frozenset(
    {
        "artifact_commitment",
        "artifact_emission",
        "artifact_path",
        "artifact_written",
        "commit_artifact",
        "committed",
        "emits_artifact",
        "emitted_artifact",
        "output_artifact",
        "trial_log_append",
        "trial_log_row",
        "writes_artifact",
    }
)


class BridgeIntakeError(ValueError):
    """Raised when AUTO bridge intake input fails closed."""


@dataclass(frozen=True)
class BridgeSourceRef:
    """Caller-provided local source identity for post-bridge AUTO material."""

    source_id: str
    source_kind: str
    bridge_era: str
    local_state: str
    content_sha256: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BridgeRunContext:
    """Caller-provided run/provenance context for bridge intake."""

    run_id: str
    run_timestamp: str
    tool_name: str | None = None
    tool_version: str | None = None
    commit_id: str | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BridgeIntakeRecord:
    """Validated local-only, non-canonical bridge intake record."""

    source: BridgeSourceRef
    run_context: BridgeRunContext
    bridge_era: str
    local_state: str
    local_only: bool
    non_canonical: bool
    creates_canonical_artifact: bool
    creates_committed_evidence: bool


def sha256_bytes(content: bytes) -> str:
    """Return a deterministic SHA-256 digest for caller-supplied bytes."""

    return hashlib.sha256(content).hexdigest()


def create_intake_record(
    source: BridgeSourceRef,
    run_context: BridgeRunContext,
) -> BridgeIntakeRecord:
    """Validate source/run context and return a local-only intake record."""

    normalized_source = _normalize_source(source)
    normalized_run_context = _normalize_run_context(run_context)
    _validate_source(normalized_source)
    _validate_run_context(normalized_run_context)
    _validate_metadata("source.metadata", normalized_source.metadata)
    _validate_metadata("run_context.metadata", normalized_run_context.metadata)
    _validate_metadata("run_context.parameters", normalized_run_context.parameters)

    return BridgeIntakeRecord(
        source=normalized_source,
        run_context=normalized_run_context,
        bridge_era=POST_BRIDGE_ELIGIBILITY_MARKER,
        local_state=LOCAL_ONLY_STATE_MARKER,
        local_only=True,
        non_canonical=True,
        creates_canonical_artifact=False,
        creates_committed_evidence=False,
    )


def _normalize_source(source: BridgeSourceRef) -> BridgeSourceRef:
    return BridgeSourceRef(
        source_id=_normalize_required_string(source.source_id),
        source_kind=_normalize_required_string(source.source_kind),
        bridge_era=_normalize_required_string(source.bridge_era),
        local_state=_normalize_required_string(source.local_state),
        content_sha256=_normalize_optional_string(source.content_sha256),
        metadata=_immutable_mapping(source.metadata),
    )


def _normalize_run_context(run_context: BridgeRunContext) -> BridgeRunContext:
    return BridgeRunContext(
        run_id=_normalize_required_string(run_context.run_id),
        run_timestamp=_normalize_required_string(run_context.run_timestamp),
        tool_name=_normalize_optional_string(run_context.tool_name),
        tool_version=_normalize_optional_string(run_context.tool_version),
        commit_id=_normalize_optional_string(run_context.commit_id),
        parameters=_immutable_mapping(run_context.parameters),
        metadata=_immutable_mapping(run_context.metadata),
    )


def _normalize_required_string(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _normalize_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _immutable_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


def _validate_source(source: BridgeSourceRef) -> None:
    if not source.source_id:
        raise BridgeIntakeError("source identity is required")
    if not source.source_kind:
        raise BridgeIntakeError("source kind is required")
    if source.bridge_era != POST_BRIDGE_ELIGIBILITY_MARKER:
        raise BridgeIntakeError("source bridge era must be post_bridge")
    if source.local_state != LOCAL_ONLY_STATE_MARKER:
        raise BridgeIntakeError("source local state must be local_only_non_canonical")
    if source.content_sha256 is not None and not _is_sha256_hex(source.content_sha256):
        raise BridgeIntakeError("content_sha256 must be a SHA-256 hex digest")


def _validate_run_context(run_context: BridgeRunContext) -> None:
    if not run_context.run_id:
        raise BridgeIntakeError("run identity is required")
    if not run_context.run_timestamp:
        raise BridgeIntakeError("run timestamp is required")


def _validate_metadata(label: str, metadata: Mapping[str, Any]) -> None:
    for key, value in _flatten_metadata(metadata):
        normalized_key = key.rsplit(".", 1)[-1].lower()
        if normalized_key in _FORBIDDEN_BINDING_KEYS:
            raise BridgeIntakeError(f"{label}.{key} is forbidden candidate-binding metadata")
        if normalized_key in _FORBIDDEN_CANONICAL_KEYS:
            raise BridgeIntakeError(f"{label}.{key} is forbidden canonical-status metadata")
        if normalized_key in _FORBIDDEN_COMMITMENT_KEYS:
            raise BridgeIntakeError(f"{label}.{key} is forbidden artifact-commitment metadata")
        if normalized_key in {"local_only", "non_canonical"} and value is not True:
            raise BridgeIntakeError(f"{label}.{key} must preserve local-only/non-canonical state")


def _flatten_metadata(metadata: Mapping[str, Any], prefix: str = "") -> tuple[tuple[str, Any], ...]:
    flattened: list[tuple[str, Any]] = []
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise BridgeIntakeError("metadata keys must be non-empty strings")
        key_path = f"{prefix}.{key.strip()}" if prefix else key.strip()
        flattened.append((key_path, value))
        if isinstance(value, Mapping):
            flattened.extend(_flatten_metadata(value, key_path))
    return tuple(flattened)


def _is_sha256_hex(value: str) -> bool:
    if len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True
