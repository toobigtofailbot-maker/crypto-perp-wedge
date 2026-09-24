"""Pure CPW preregistration and exact human-approval semantics."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .contracts import (
    LAB_NON_AUTHORITY_FLAGS,
    PREREG_APPROVAL_EXTRA_FALSE_FIELDS,
    PREREG_APPROVAL_REQUIRED_FIELDS,
    PREREG_APPROVAL_SCHEMA_VERSION,
    PREREG_APPROVAL_SCOPE,
    PREREG_APPROVAL_STATEMENT,
    PREREG_NON_AUTHORITY_ASSERTIONS,
)


def _sha256_payload(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _packet_hash(packet: Mapping[str, Any]) -> str:
    unhashed = dict(packet)
    unhashed.pop("packet_sha256", None)
    return _sha256_payload(unhashed)


def build_preregistration_packet(
    *,
    pipeline_run_id: str,
    request: Mapping[str, Any],
    formalized: Mapping[str, Any],
    availability: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic non-canonical lab preregistration packet."""

    if not pipeline_run_id or "request_id" not in request:
        raise ValueError("pipeline_run_id and request.request_id are required")
    packet: dict[str, Any] = {
        "schema_version": "lab_pipeline_preregistration_packet_v1",
        "pipeline_run_id": pipeline_run_id,
        "request_id": request["request_id"],
        "frozen_content": {
            "request": dict(request),
            "formalized_idea": dict(formalized),
            "availability_check": dict(availability),
            "execution_scope": "noncanonical_offline_research_only",
            "canonical_write_allowed": False,
            "candidate_lifecycle_write_allowed": False,
            "paper_live_runtime_contact_allowed": False,
            "scheduler_autonomy_allowed": False,
            "notification_firing_allowed": False,
            "provider_api_network_allowed": False,
            "denominator_policy": "preserve_all_generated_rows_no_winner_only_selection",
        },
        "approval_binding": {
            "required_approval_scope": PREREG_APPROVAL_SCOPE,
            "required_approval_statement": PREREG_APPROVAL_STATEMENT,
            "hash_algorithm": "sha256",
            "hash_scope": "packet_without_packet_sha256",
        },
        "non_authority_flags": dict(LAB_NON_AUTHORITY_FLAGS),
    }
    packet["packet_sha256"] = _sha256_payload(packet)
    return packet


def build_approval_requirement(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Bind the exact current lab approval requirement to a packet."""

    errors = _packet_errors(packet)
    if errors:
        raise ValueError("invalid preregistration packet: " + ", ".join(errors))
    packet_hash = packet["packet_sha256"]
    return {
        "schema_version": "lab_pipeline_approval_requirement_v1",
        "pipeline_run_id": packet["pipeline_run_id"],
        "request_id": packet["request_id"],
        "preregistration_packet_sha256": packet_hash,
        "approval_marker_schema": PREREG_APPROVAL_SCHEMA_VERSION,
        "required_fields": {
            "schema_version": PREREG_APPROVAL_SCHEMA_VERSION,
            "approved_by": "Karl",
            "approval_scope": PREREG_APPROVAL_SCOPE,
            "approval_statement": PREREG_APPROVAL_STATEMENT,
            "authorizes_noncanonical_offline_research_execution": True,
            "authorizes_canonical_write": False,
            "authorizes_candidate_lifecycle": False,
            "authorizes_paper_live_runtime": False,
            "authorizes_scheduler_autonomy": False,
            "authorizes_notifications": False,
            "preregistration_packet_sha256": packet_hash,
        },
        "non_authority_flags": dict(LAB_NON_AUTHORITY_FLAGS),
    }


def build_approval_template(
    packet: Mapping[str, Any], *, approval_timestamp_utc: str
) -> dict[str, Any]:
    """Build an exact approval template without reading or writing files."""

    errors = _packet_errors(packet)
    if errors:
        raise ValueError("invalid preregistration packet: " + ", ".join(errors))
    if not isinstance(approval_timestamp_utc, str) or not approval_timestamp_utc:
        raise ValueError("approval_timestamp_utc is required")
    return {
        "schema_version": PREREG_APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": PREREG_APPROVAL_SCOPE,
        "approval_statement": PREREG_APPROVAL_STATEMENT,
        "approval_timestamp_utc": approval_timestamp_utc,
        "authorizes_noncanonical_offline_research_execution": True,
        "authorizes_canonical_write": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "preregistration_packet_sha256": packet["packet_sha256"],
    }


def _packet_errors(packet: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if packet.get("schema_version") != "lab_pipeline_preregistration_packet_v1":
        errors.append("preregistration_packet_schema_version_mismatch")
    packet_hash = packet.get("packet_sha256")
    if not isinstance(packet_hash, str) or not packet_hash:
        errors.append("preregistration_packet_hash_missing")
    elif _packet_hash(packet) != packet_hash:
        errors.append("preregistration_packet_hash_mismatch")
    return tuple(errors)


def validate_bound_requirement(
    requirement: Mapping[str, Any], packet: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return stable semantic error codes for packet/requirement binding."""

    errors = list(_packet_errors(packet))
    packet_hash = packet.get("packet_sha256")
    if requirement.get("schema_version") != "lab_pipeline_approval_requirement_v1":
        errors.append("approval_requirement_schema_version_mismatch")
    if requirement.get("preregistration_packet_sha256") != packet_hash:
        errors.append("approval_requirement_packet_hash_mismatch")
    if requirement.get("approval_marker_schema") != PREREG_APPROVAL_SCHEMA_VERSION:
        errors.append("approval_requirement_marker_schema_mismatch")
    required = requirement.get("required_fields")
    if not isinstance(required, Mapping):
        errors.append("approval_requirement_required_fields_missing")
    elif required.get("preregistration_packet_sha256") != packet_hash:
        errors.append("approval_requirement_required_fields_hash_mismatch")
    if requirement.get("pipeline_run_id") != packet.get("pipeline_run_id"):
        errors.append("approval_requirement_pipeline_run_id_mismatch")
    if requirement.get("request_id") != packet.get("request_id"):
        errors.append("approval_requirement_request_id_mismatch")
    return tuple(errors)


def validate_prereg_approval(
    approval: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    requirement: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Validate the exact current non-canonical preregistration approval."""

    errors: list[str] = []
    if requirement is not None:
        errors.extend(validate_bound_requirement(requirement, packet))
    else:
        errors.extend(_packet_errors(packet))
    if approval.get("schema_version") != PREREG_APPROVAL_SCHEMA_VERSION:
        errors.append("approval_schema_version_mismatch")
    if approval.get("approved_by") != "Karl":
        errors.append("approval_actor_not_karl")
    if approval.get("approval_scope") != PREREG_APPROVAL_SCOPE:
        errors.append("approval_scope_not_noncanonical_offline_only")
    if approval.get("approval_statement") != PREREG_APPROVAL_STATEMENT:
        errors.append("approval_statement_not_exact")
    if approval.get("authorizes_noncanonical_offline_research_execution") is not True:
        errors.append("approval_missing_noncanonical_execution_flag")
    if approval.get("preregistration_packet_sha256") != packet.get("packet_sha256"):
        errors.append("approval_hash_mismatch")
    timestamp = approval.get("approval_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp.strip():
        errors.append("approval_timestamp_missing")
    for field in (
        "authorizes_canonical_write",
        "authorizes_candidate_lifecycle",
        "authorizes_paper_live_runtime",
        "authorizes_scheduler_autonomy",
        "authorizes_notifications",
    ):
        if approval.get(field) is not False:
            errors.append(f"approval_too_broad:{field}")
    for field in PREREG_APPROVAL_EXTRA_FALSE_FIELDS:
        if approval.get(field, False) is not False:
            errors.append(f"approval_too_broad:{field}")
    return tuple(errors)


def build_approval_marker(
    *,
    action_id: str,
    requirement: Mapping[str, Any],
    packet: Mapping[str, Any],
    operator_fields: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the current gate-action marker after exact semantic validation."""

    missing = [field for field in PREREG_APPROVAL_REQUIRED_FIELDS if field not in operator_fields]
    if missing:
        raise ValueError(f"operator fields missing required approval fields: {missing}")
    errors = validate_prereg_approval(operator_fields, packet, requirement=requirement)
    if errors:
        raise ValueError("invalid prereg approval operator fields: " + ", ".join(errors))
    marker = {field: operator_fields[field] for field in PREREG_APPROVAL_REQUIRED_FIELDS}
    marker.update({field: False for field in PREREG_APPROVAL_EXTRA_FALSE_FIELDS})
    marker.update(
        {
            "gate_action_id": action_id,
            "approval_requirement_ref": {
                "pipeline_run_id": requirement["pipeline_run_id"],
                "request_id": requirement["request_id"],
                "preregistration_packet_sha256": requirement["preregistration_packet_sha256"],
            },
            "non_authority_assertions": dict(PREREG_NON_AUTHORITY_ASSERTIONS),
            "non_authority_flags": dict(LAB_NON_AUTHORITY_FLAGS),
        }
    )
    return marker
