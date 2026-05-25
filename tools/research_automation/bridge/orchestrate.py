"""AUTO bridge end-to-end local orchestration.

This module composes existing bridge primitives over explicit caller-provided
in-memory values only. It does not read files, scan directories, write
artifacts, append trial-log rows, or expose query-layer state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.research_automation.bridge.candidate_artifact import (
    BridgeCandidateArtifactDraft,
    create_candidate_artifact_draft,
)
from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
    BridgeIntakeRecord,
    BridgeRunContext,
    BridgeSourceRef,
    create_intake_record,
    sha256_bytes,
)
from tools.research_automation.bridge.transform import (
    BridgeNormalizedRecord,
    normalize_bridge_payload,
)
from tools.research_automation.bridge.validate import (
    BridgeValidationResult,
    assert_valid_normalized_record,
)


class BridgeOrchestrationError(ValueError):
    """Raised when local AUTO bridge orchestration fails closed."""


@dataclass(frozen=True)
class BridgeRunResult:
    """In-memory result for one local-only AUTO bridge pipeline run."""

    intake_record: BridgeIntakeRecord
    normalized_record: BridgeNormalizedRecord
    validation_result: BridgeValidationResult
    candidate_artifact_draft: BridgeCandidateArtifactDraft
    bridge_stage_summary: tuple[str, ...]
    local_only: bool = True
    non_canonical: bool = True
    creates_canonical_artifact: bool = False
    creates_committed_evidence: bool = False


def run_bridge_pipeline(
    *,
    source_id: str,
    source_kind: str,
    run_id: str,
    run_timestamp: str,
    normalized_payload: Mapping[str, Any],
    draft_payload: Mapping[str, Any],
    draft_type: str,
    target_label: str,
    source_content: bytes | None = None,
    source_content_sha256: str | None = None,
    source_bridge_era: str = POST_BRIDGE_ELIGIBILITY_MARKER,
    source_local_state: str = LOCAL_ONLY_STATE_MARKER,
    source_metadata: Mapping[str, Any] | None = None,
    run_parameters: Mapping[str, Any] | None = None,
    run_metadata: Mapping[str, Any] | None = None,
    tool_name: str | None = None,
    tool_version: str | None = None,
    commit_id: str | None = None,
    normalized_metadata: Mapping[str, Any] | None = None,
) -> BridgeRunResult:
    """Run the local in-memory bridge pipeline over caller-provided values."""

    content_sha256 = _resolve_content_sha256(source_content, source_content_sha256)

    source = BridgeSourceRef(
        source_id=source_id,
        source_kind=source_kind,
        bridge_era=source_bridge_era,
        local_state=source_local_state,
        content_sha256=content_sha256,
        metadata=source_metadata or {},
    )
    run_context = BridgeRunContext(
        run_id=run_id,
        run_timestamp=run_timestamp,
        tool_name=tool_name,
        tool_version=tool_version,
        commit_id=commit_id,
        parameters=run_parameters or {},
        metadata=run_metadata or {},
    )

    intake_record = create_intake_record(source, run_context)
    normalized_record = normalize_bridge_payload(
        intake_record,
        normalized_payload,
        metadata=normalized_metadata,
    )
    validation_result = assert_valid_normalized_record(normalized_record)
    candidate_artifact_draft = create_candidate_artifact_draft(
        normalized_record,
        validation_result,
        draft_type=draft_type,
        target_label=target_label,
        draft_payload=draft_payload,
    )

    if candidate_artifact_draft.creates_canonical_artifact is not False:
        raise BridgeOrchestrationError("draft must not create canonical artifacts")
    if candidate_artifact_draft.creates_committed_evidence is not False:
        raise BridgeOrchestrationError("draft must not create committed evidence")
    if candidate_artifact_draft.candidate_bound is not False:
        raise BridgeOrchestrationError("draft must not be candidate-bound")

    return BridgeRunResult(
        intake_record=intake_record,
        normalized_record=normalized_record,
        validation_result=validation_result,
        candidate_artifact_draft=candidate_artifact_draft,
        bridge_stage_summary=(
            "intake",
            normalized_record.bridge_stage,
            "validation",
            candidate_artifact_draft.bridge_stage,
        ),
    )


def _resolve_content_sha256(
    source_content: bytes | None,
    source_content_sha256: str | None,
) -> str | None:
    if source_content is not None and not isinstance(source_content, bytes):
        raise BridgeOrchestrationError("source_content must be bytes")

    computed_digest = (
        sha256_bytes(source_content) if source_content is not None else None
    )
    if computed_digest is not None and source_content_sha256 is not None:
        if computed_digest != source_content_sha256:
            raise BridgeOrchestrationError(
                "source_content_sha256 must match source_content"
            )
    return source_content_sha256 or computed_digest
