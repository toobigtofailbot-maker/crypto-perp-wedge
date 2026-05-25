"""AUTO bridge validation/integrity primitives.

This module validates in-memory normalized bridge records only. It does not
read files, write artifacts, append trial-log rows, or expose query-layer state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.research_automation.bridge.intake import (
    LOCAL_ONLY_STATE_MARKER,
    POST_BRIDGE_ELIGIBILITY_MARKER,
    BridgeIntakeRecord,
)
from tools.research_automation.bridge.transform import (
    NORMALIZED_BRIDGE_STAGE,
    BridgeNormalizedRecord,
)


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


class BridgeValidationError(ValueError):
    """Raised when normalized AUTO bridge validation fails closed."""


@dataclass(frozen=True)
class BridgeValidationIssue:
    """One bridge-local validation/integrity issue."""

    code: str
    message: str
    location: str


@dataclass(frozen=True)
class BridgeValidationResult:
    """Deterministic in-memory validation result for a normalized record."""

    valid: bool
    issues: tuple[BridgeValidationIssue, ...]
    stage_checked: str | None
    local_only: bool
    non_canonical: bool
    creates_canonical_artifact: bool = False
    creates_committed_evidence: bool = False


def validate_normalized_record(record: Any) -> BridgeValidationResult:
    """Validate a WP-12dc normalized bridge record without side effects."""

    issues: list[BridgeValidationIssue] = []
    if not isinstance(record, BridgeNormalizedRecord):
        issues.append(
            BridgeValidationIssue(
                code="not_normalized_record",
                message="record must be a BridgeNormalizedRecord",
                location="record",
            )
        )
        return _result(issues, None, False, False)

    _validate_normalized_record(record, issues)
    _validate_intake_record(record.intake_record, issues)
    _validate_mapping("normalized_payload", record.normalized_payload, issues)
    _validate_mapping("normalized_metadata", record.normalized_metadata, issues)

    return _result(
        issues,
        record.bridge_stage,
        record.local_only is True,
        record.non_canonical is True,
    )


def assert_valid_normalized_record(record: Any) -> BridgeValidationResult:
    """Return a valid result or raise BridgeValidationError fail-closed."""

    result = validate_normalized_record(record)
    if not result.valid:
        issue_codes = ", ".join(issue.code for issue in result.issues)
        raise BridgeValidationError(f"normalized bridge record is invalid: {issue_codes}")
    return result


def _validate_normalized_record(
    record: BridgeNormalizedRecord, issues: list[BridgeValidationIssue]
) -> None:
    if record.bridge_stage != NORMALIZED_BRIDGE_STAGE:
        _add_issue(
            issues,
            "unsupported_bridge_stage",
            "bridge stage must be normalized",
            "record.bridge_stage",
        )
    if record.local_only is not True or record.non_canonical is not True:
        _add_issue(
            issues,
            "not_local_only_non_canonical",
            "record must preserve local-only/non-canonical state",
            "record",
        )
    if record.creates_canonical_artifact is not False:
        _add_issue(
            issues,
            "canonical_artifact_claim",
            "record must not create canonical artifacts",
            "record.creates_canonical_artifact",
        )
    if record.creates_committed_evidence is not False:
        _add_issue(
            issues,
            "committed_evidence_claim",
            "record must not create committed evidence",
            "record.creates_committed_evidence",
        )
    if not isinstance(record.normalized_payload, Mapping) or not record.normalized_payload:
        _add_issue(
            issues,
            "empty_normalized_payload",
            "normalized payload must be a non-empty mapping",
            "record.normalized_payload",
        )
    if not _is_sha256_hex(record.payload_sha256):
        _add_issue(
            issues,
            "malformed_payload_digest",
            "payload_sha256 must be a SHA-256 hex digest",
            "record.payload_sha256",
        )


def _validate_intake_record(
    intake_record: BridgeIntakeRecord, issues: list[BridgeValidationIssue]
) -> None:
    if not isinstance(intake_record, BridgeIntakeRecord):
        _add_issue(
            issues,
            "missing_intake_record",
            "intake_record must be a BridgeIntakeRecord",
            "record.intake_record",
        )
        return

    if intake_record.bridge_era != POST_BRIDGE_ELIGIBILITY_MARKER:
        _add_issue(
            issues,
            "invalid_intake_bridge_era",
            "intake record bridge era must be post_bridge",
            "record.intake_record.bridge_era",
        )
    if intake_record.local_state != LOCAL_ONLY_STATE_MARKER:
        _add_issue(
            issues,
            "invalid_intake_local_state",
            "intake record local state must be local_only_non_canonical",
            "record.intake_record.local_state",
        )
    if intake_record.local_only is not True or intake_record.non_canonical is not True:
        _add_issue(
            issues,
            "invalid_intake_boundary",
            "intake record must preserve local-only/non-canonical state",
            "record.intake_record",
        )
    if intake_record.creates_canonical_artifact is not False:
        _add_issue(
            issues,
            "intake_canonical_artifact_claim",
            "intake record must not create canonical artifacts",
            "record.intake_record.creates_canonical_artifact",
        )
    if intake_record.creates_committed_evidence is not False:
        _add_issue(
            issues,
            "intake_committed_evidence_claim",
            "intake record must not create committed evidence",
            "record.intake_record.creates_committed_evidence",
        )
    if not intake_record.source.source_id:
        _add_issue(
            issues,
            "missing_source_identity",
            "intake source identity is required",
            "record.intake_record.source.source_id",
        )
    if not intake_record.run_context.run_id:
        _add_issue(
            issues,
            "missing_run_identity",
            "intake run identity is required",
            "record.intake_record.run_context.run_id",
        )
    _validate_mapping("intake_source_metadata", intake_record.source.metadata, issues)
    _validate_mapping(
        "intake_run_context_parameters", intake_record.run_context.parameters, issues
    )
    _validate_mapping("intake_run_context_metadata", intake_record.run_context.metadata, issues)


def _validate_mapping(
    label: str,
    metadata: Mapping[str, Any],
    issues: list[BridgeValidationIssue],
) -> None:
    if not isinstance(metadata, Mapping):
        _add_issue(
            issues,
            "malformed_metadata",
            f"{label} must be a mapping",
            label,
        )
        return

    for key, value in _flatten_mapping(metadata):
        normalized_key = key.rsplit(".", 1)[-1].lower()
        location = f"{label}.{key}"
        if normalized_key in _FORBIDDEN_BINDING_KEYS:
            _add_issue(
                issues,
                "candidate_binding_metadata",
                "candidate-binding metadata is forbidden",
                location,
            )
        if normalized_key in _FORBIDDEN_CANONICAL_KEYS:
            _add_issue(
                issues,
                "canonical_status_metadata",
                "canonical-status metadata is forbidden",
                location,
            )
        if normalized_key in _FORBIDDEN_COMMITMENT_KEYS:
            _add_issue(
                issues,
                "artifact_commitment_metadata",
                "artifact-commitment metadata is forbidden",
                location,
            )
        if normalized_key in _FORBIDDEN_RETROACTIVITY_KEYS:
            _add_issue(
                issues,
                "pre_bridge_retroactive_metadata",
                "pre-bridge/retroactive-transformation metadata is forbidden",
                location,
            )
        if normalized_key in {"bridge_era", "source_era"} and value != (
            POST_BRIDGE_ELIGIBILITY_MARKER
        ):
            _add_issue(
                issues,
                "pre_bridge_retroactive_metadata",
                "pre-bridge/retroactive-transformation metadata is forbidden",
                location,
            )
        if normalized_key in {"local_only", "non_canonical"} and value is not True:
            _add_issue(
                issues,
                "not_local_only_non_canonical",
                "local-only/non-canonical markers must be true",
                location,
            )


def _flatten_mapping(
    metadata: Mapping[str, Any], prefix: str = ""
) -> tuple[tuple[str, Any], ...]:
    flattened: list[tuple[str, Any]] = []
    for key, value in metadata.items():
        if not isinstance(key, str) or not key.strip():
            flattened.append(("<malformed_key>", value))
            continue
        key_path = f"{prefix}.{key.strip()}" if prefix else key.strip()
        flattened.append((key_path, value))
        if isinstance(value, Mapping):
            flattened.extend(_flatten_mapping(value, key_path))
    return tuple(flattened)


def _is_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _add_issue(
    issues: list[BridgeValidationIssue], code: str, message: str, location: str
) -> None:
    issues.append(BridgeValidationIssue(code=code, message=message, location=location))


def _result(
    issues: list[BridgeValidationIssue],
    stage_checked: str | None,
    local_only: bool,
    non_canonical: bool,
) -> BridgeValidationResult:
    return BridgeValidationResult(
        valid=not issues,
        issues=tuple(issues),
        stage_checked=stage_checked,
        local_only=local_only,
        non_canonical=non_canonical,
        creates_canonical_artifact=False,
        creates_committed_evidence=False,
    )
