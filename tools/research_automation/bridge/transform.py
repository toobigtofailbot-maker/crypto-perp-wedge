"""AUTO bridge transformation/normalization primitives.

This module normalizes explicit caller-provided in-memory payloads only. It
does not read AUTO output directories, write files, emit artifacts, or expose
query-layer state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
    BridgeIntakeRecord,
)


NORMALIZED_BRIDGE_STAGE = "normalized"

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
_FORBIDDEN_RETROACTIVITY_KEYS = frozenset(
    {
        "pre_bridge",
        "pre_bridge_source",
        "retroactive",
        "retroactive_transformation",
        "source_bridge_era",
        "source_era",
        "transform_pre_bridge",
    }
)


class BridgeTransformError(ValueError):
    """Raised when AUTO bridge transformation input fails closed."""


@dataclass(frozen=True)
class BridgeNormalizedRecord:
    """Local-only, non-canonical normalized bridge representation."""

    intake_record: BridgeIntakeRecord
    normalized_payload: Mapping[str, Any]
    normalized_metadata: Mapping[str, Any] = field(default_factory=dict)
    bridge_stage: str = NORMALIZED_BRIDGE_STAGE
    local_only: bool = True
    non_canonical: bool = True
    creates_canonical_artifact: bool = False
    creates_committed_evidence: bool = False
    payload_sha256: str | None = None


def normalize_bridge_payload(
    intake_record: BridgeIntakeRecord,
    payload: Mapping[str, Any],
    metadata: Mapping[str, Any] | None = None,
) -> BridgeNormalizedRecord:
    """Normalize a caller-provided in-memory payload mapping."""

    _validate_intake_record(intake_record)
    normalized_payload = _normalize_mapping("payload", payload)
    normalized_metadata = _normalize_mapping("metadata", metadata or {}, allow_empty=True)
    _validate_mapping("payload", normalized_payload)
    _validate_mapping("metadata", normalized_metadata)

    return BridgeNormalizedRecord(
        intake_record=intake_record,
        normalized_payload=_immutable_mapping(normalized_payload),
        normalized_metadata=_immutable_mapping(normalized_metadata),
        payload_sha256=sha256_json_payload(normalized_payload),
    )


def sha256_json_payload(payload: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 digest for a JSON-serializable mapping."""

    normalized_payload = _normalize_mapping("payload", payload)
    serialized = _stable_json(normalized_payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_intake_record(intake_record: BridgeIntakeRecord) -> None:
    if not isinstance(intake_record, BridgeIntakeRecord):
        raise BridgeTransformError("intake_record must be a BridgeIntakeRecord")
    if intake_record.bridge_era != POST_BRIDGE_ELIGIBILITY_MARKER:
        raise BridgeTransformError("intake record bridge era must be post_bridge")
    if intake_record.local_state != LOCAL_ONLY_STATE_MARKER:
        raise BridgeTransformError(
            "intake record local state must be local_only_non_canonical"
        )
    if intake_record.local_only is not True or intake_record.non_canonical is not True:
        raise BridgeTransformError(
            "intake record must preserve local-only/non-canonical state"
        )
    if intake_record.creates_canonical_artifact is not False:
        raise BridgeTransformError("intake record must not create canonical artifacts")
    if intake_record.creates_committed_evidence is not False:
        raise BridgeTransformError("intake record must not create committed evidence")


def _normalize_mapping(
    label: str, value: Mapping[str, Any], *, allow_empty: bool = False
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise BridgeTransformError(f"{label} must be an in-memory mapping")
    if not value and not allow_empty:
        raise BridgeTransformError(f"{label} must not be empty")
    try:
        return json.loads(_stable_json(value))
    except (TypeError, ValueError) as exc:
        raise BridgeTransformError(
            f"{label} must be deterministically JSON-serializable"
        ) from exc


def _stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _immutable_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


def _validate_mapping(label: str, metadata: Mapping[str, Any]) -> None:
    for key, value in _flatten_mapping(metadata):
        normalized_key = key.rsplit(".", 1)[-1].lower()
        if normalized_key in _FORBIDDEN_BINDING_KEYS:
            raise BridgeTransformError(
                f"{label}.{key} is forbidden candidate-binding metadata"
            )
        if normalized_key in _FORBIDDEN_CANONICAL_KEYS:
            raise BridgeTransformError(
                f"{label}.{key} is forbidden canonical-status metadata"
            )
        if normalized_key in _FORBIDDEN_COMMITMENT_KEYS:
            raise BridgeTransformError(
                f"{label}.{key} is forbidden artifact-commitment metadata"
            )
        if normalized_key in _FORBIDDEN_RETROACTIVITY_KEYS:
            raise BridgeTransformError(
                f"{label}.{key} is forbidden pre-bridge/retroactive metadata"
            )
        if normalized_key in {"bridge_era", "source_era"} and value != (
            POST_BRIDGE_ELIGIBILITY_MARKER
        ):
            raise BridgeTransformError(
                f"{label}.{key} is forbidden pre-bridge/retroactive metadata"
            )
        if normalized_key in {"local_only", "non_canonical"} and value is not True:
            raise BridgeTransformError(
                f"{label}.{key} must preserve local-only/non-canonical state"
            )


def _flatten_mapping(
    metadata: Mapping[str, Any], prefix: str = ""
) -> tuple[tuple[str, Any], ...]:
    flattened: list[tuple[str, Any]] = []
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise BridgeTransformError("metadata keys must be non-empty strings")
        key_path = f"{prefix}.{key.strip()}" if prefix else key.strip()
        flattened.append((key_path, value))
        if isinstance(value, Mapping):
            flattened.extend(_flatten_mapping(value, key_path))
    return tuple(flattened)
