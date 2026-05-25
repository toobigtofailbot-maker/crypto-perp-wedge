"""AUTO bridge candidate-artifact draft primitives.

This module produces in-memory bridge-local draft records only. It does not
read AUTO output directories, write files, emit artifacts, append trial-log
rows, or expose query-layer state.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from tools.research_automation.bridge.transform import BridgeNormalizedRecord
from tools.research_automation.bridge.validate import (
    BridgeValidationResult,
    assert_valid_normalized_record,
)


CANDIDATE_ARTIFACT_DRAFT_STAGE = "candidate_artifact_draft"

_CANONICAL_ID_RE = re.compile(r"\b(?:REP|OL|REC|EXP)-\d+\b", re.IGNORECASE)

_FORBIDDEN_BINDING_KEYS = frozenset(
    {
        "a2c",
        "a2c_id",
        "candidate",
        "candidate_bound",
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
        "canonical_id",
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
        "output_path",
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
_FORBIDDEN_AUTHORITY_KEYS = frozenset(
    {
        "approval",
        "lifecycle",
        "lifecycle_artifact",
        "query",
        "query_view",
        "readiness",
        "registry",
        "registry_row",
    }
)


class BridgeCandidateArtifactError(ValueError):
    """Raised when candidate-artifact draft production fails closed."""


@dataclass(frozen=True)
class BridgeCandidateArtifactDraft:
    """Bridge-local, in-memory, non-canonical candidate-artifact draft."""

    source_record: BridgeNormalizedRecord
    validation_result: BridgeValidationResult
    draft_type: str
    target_label: str
    draft_payload: Mapping[str, Any]
    provenance_summary: Mapping[str, Any]
    validation_issue_summary: tuple[str, ...] = field(default_factory=tuple)
    bridge_stage: str = CANDIDATE_ARTIFACT_DRAFT_STAGE
    local_only: bool = True
    non_canonical: bool = True
    candidate_bound: bool = False
    creates_canonical_artifact: bool = False
    creates_committed_evidence: bool = False
    draft_sha256: str | None = None


def create_candidate_artifact_draft(
    normalized_record: BridgeNormalizedRecord,
    validation_result: BridgeValidationResult | None = None,
    *,
    draft_type: str,
    target_label: str,
    draft_payload: Mapping[str, Any],
) -> BridgeCandidateArtifactDraft:
    """Create a local-only candidate-artifact draft from a valid record."""

    if not isinstance(normalized_record, BridgeNormalizedRecord):
        raise BridgeCandidateArtifactError(
            "normalized_record must be a BridgeNormalizedRecord"
        )

    checked_validation = _validate_result_for_record(
        normalized_record, validation_result
    )
    normalized_draft_type = _normalize_label("draft_type", draft_type)
    normalized_target_label = _normalize_label("target_label", target_label)
    normalized_payload = _normalize_mapping("draft_payload", draft_payload)
    _validate_mapping("draft_payload", normalized_payload)
    _validate_text("draft_type", normalized_draft_type)
    _validate_text("target_label", normalized_target_label)

    provenance_summary = _build_provenance_summary(normalized_record)
    digest = sha256_draft_payload(
        {
            "draft_type": normalized_draft_type,
            "target_label": normalized_target_label,
            "draft_payload": normalized_payload,
            "provenance_summary": provenance_summary,
            "source_payload_sha256": normalized_record.payload_sha256,
        }
    )

    return BridgeCandidateArtifactDraft(
        source_record=normalized_record,
        validation_result=checked_validation,
        draft_type=normalized_draft_type,
        target_label=normalized_target_label,
        draft_payload=_immutable_mapping(normalized_payload),
        provenance_summary=_immutable_mapping(provenance_summary),
        validation_issue_summary=tuple(
            issue.code for issue in checked_validation.issues
        ),
        draft_sha256=digest,
    )


def sha256_draft_payload(payload: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 digest for a JSON-serializable draft mapping."""

    normalized_payload = _normalize_mapping("payload", payload)
    serialized = _stable_json(normalized_payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_result_for_record(
    normalized_record: BridgeNormalizedRecord,
    validation_result: BridgeValidationResult | None,
) -> BridgeValidationResult:
    checked_validation = (
        assert_valid_normalized_record(normalized_record)
        if validation_result is None
        else validation_result
    )
    if not isinstance(checked_validation, BridgeValidationResult):
        raise BridgeCandidateArtifactError(
            "validation_result must be a BridgeValidationResult"
        )
    if checked_validation.valid is not True:
        raise BridgeCandidateArtifactError("validation_result must be valid")
    if checked_validation.issues:
        raise BridgeCandidateArtifactError("validation_result must not contain issues")
    if checked_validation.stage_checked != normalized_record.bridge_stage:
        raise BridgeCandidateArtifactError(
            "validation_result stage must match normalized record stage"
        )
    if (
        checked_validation.local_only is not True
        or checked_validation.non_canonical is not True
    ):
        raise BridgeCandidateArtifactError(
            "validation_result must preserve local-only/non-canonical state"
        )
    if checked_validation.creates_canonical_artifact is not False:
        raise BridgeCandidateArtifactError(
            "validation_result must not create canonical artifacts"
        )
    if checked_validation.creates_committed_evidence is not False:
        raise BridgeCandidateArtifactError(
            "validation_result must not create committed evidence"
        )
    return checked_validation


def _build_provenance_summary(
    normalized_record: BridgeNormalizedRecord,
) -> dict[str, Any]:
    intake_record = normalized_record.intake_record
    return {
        "bridge_stage": normalized_record.bridge_stage,
        "normalized_payload_sha256": normalized_record.payload_sha256,
        "source_id": intake_record.source.source_id,
        "source_kind": intake_record.source.source_kind,
        "source_content_sha256": intake_record.source.content_sha256,
        "run_id": intake_record.run_context.run_id,
        "run_timestamp": intake_record.run_context.run_timestamp,
        "tool_name": intake_record.run_context.tool_name,
        "tool_version": intake_record.run_context.tool_version,
        "commit_id": intake_record.run_context.commit_id,
        "local_only": True,
        "non_canonical": True,
    }


def _normalize_label(label: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BridgeCandidateArtifactError(f"{label} must be a non-empty string")
    return value.strip()


def _normalize_mapping(
    label: str, value: Mapping[str, Any], *, allow_empty: bool = False
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise BridgeCandidateArtifactError(f"{label} must be an in-memory mapping")
    if not value and not allow_empty:
        raise BridgeCandidateArtifactError(f"{label} must not be empty")
    try:
        return json.loads(_stable_json(value))
    except (TypeError, ValueError) as exc:
        raise BridgeCandidateArtifactError(
            f"{label} must be deterministically JSON-serializable"
        ) from exc


def _stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _immutable_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


def _validate_mapping(label: str, metadata: Mapping[str, Any]) -> None:
    for key, value in _flatten_mapping(metadata):
        normalized_key = key.rsplit(".", 1)[-1].lower()
        location = f"{label}.{key}"
        if normalized_key in _FORBIDDEN_BINDING_KEYS:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden candidate-binding metadata"
            )
        if normalized_key in _FORBIDDEN_CANONICAL_KEYS:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden canonical-status metadata"
            )
        if normalized_key in _FORBIDDEN_COMMITMENT_KEYS:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden artifact-commitment metadata"
            )
        if normalized_key in _FORBIDDEN_RETROACTIVITY_KEYS:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden pre-bridge/retroactive metadata"
            )
        if normalized_key in _FORBIDDEN_AUTHORITY_KEYS:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden lifecycle/registry/query metadata"
            )
        if normalized_key in {"bridge_era", "source_era"} and value != "post_bridge":
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden pre-bridge/retroactive metadata"
            )
        if normalized_key in {"local_only", "non_canonical"} and value is not True:
            raise BridgeCandidateArtifactError(
                f"{location} must preserve local-only/non-canonical state"
            )
        if normalized_key in {"candidate_bound", "candidate_binding"} and value:
            raise BridgeCandidateArtifactError(
                f"{location} is forbidden candidate-binding metadata"
            )
        _validate_value_claim(location, value)


def _validate_text(label: str, value: str) -> None:
    lowered = value.lower()
    if _CANONICAL_ID_RE.search(value):
        raise BridgeCandidateArtifactError(f"{label} contains a canonical artifact ID")
    if any(token in lowered for token in ("trial_log", "registry", "query_view")):
        raise BridgeCandidateArtifactError(
            f"{label} contains a forbidden lifecycle/registry/query claim"
        )


def _validate_value_claim(location: str, value: Any) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if _CANONICAL_ID_RE.search(value):
            raise BridgeCandidateArtifactError(
                f"{location} contains a canonical artifact ID"
            )
        if any(
            token in lowered
            for token in (
                "artifact_path",
                "lifecycle",
                "output_path",
                "query_view",
                "registry",
                "trial_log",
            )
        ):
            raise BridgeCandidateArtifactError(
                f"{location} contains a forbidden artifact/path authority claim"
            )


def _flatten_mapping(
    metadata: Mapping[str, Any], prefix: str = ""
) -> tuple[tuple[str, Any], ...]:
    flattened: list[tuple[str, Any]] = []
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            raise BridgeCandidateArtifactError("metadata keys must be non-empty strings")
        key_path = f"{prefix}.{key.strip()}" if prefix else key.strip()
        flattened.append((key_path, value))
        if isinstance(value, Mapping):
            flattened.extend(_flatten_mapping(value, key_path))
    return tuple(flattened)
