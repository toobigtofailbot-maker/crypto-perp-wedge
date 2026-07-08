"""Local non-canonical gate actions for the lab pipeline.

These actions create product-callable packets for human gate surfaces without
granting canonical, candidate lifecycle, paper/live/runtime, scheduler,
notification, provider/API, credential, dependency, config, data-acquisition, or
protected-path authority.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from tools.lab_pipeline import model
from tools.lab_pipeline.state import file_sha256, read_json, sha256_payload, write_json, write_text


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-LABPROD-INPRODUCT-GATE-ACTIONS-01"
DEFAULT_SCRATCH_ROOT = REPO_ROOT / "scratch" / WP_ID
DEFAULT_OUTPUT_ROOT = DEFAULT_SCRATCH_ROOT / "outputs"

APPROVAL_MARKER_FILENAME = "approval_marker.json"
APPROVAL_PREVIEW_FILENAME = "approval_preview.md"
CANDIDATE_DECISION_FILENAME = "candidate_surface_decision.json"

ACTION_SCHEMA_VERSION = "lab_pipeline_gate_action_v1"
PREVIEW_SCHEMA_VERSION = "lab_pipeline_prereg_approval_preview_v1"
CANDIDATE_DECISION_SCHEMA_VERSION = "lab_pipeline_candidate_surface_decision_v1"

ALLOWED_CANDIDATE_SURFACE_DECISIONS = frozenset(
    {"hold_for_review", "needs_more_evidence", "do_not_escalate"}
)

FORBIDDEN_DECISION_VALUES = frozenset(
    {
        "admit_candidate",
        "cross",
        "promote",
        "ready_for_paper",
        "start_paper",
        "start_shadow",
        "start_live",
    }
)

FORBIDDEN_DECISION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\badmit[_ -]?candidate\b", re.I), "candidate_admission"),
    (re.compile(r"\bcandidate[_ -]?(lifecycle|registry|write)\b", re.I), "candidate_lifecycle_write"),
    (re.compile(r"\bcross(ing)?\b", re.I), "crossing"),
    (re.compile(r"\bpromot(e|ion)\b", re.I), "promotion"),
    (re.compile(r"\bready[_ -]?for[_ -]?paper\b", re.I), "paper_readiness"),
    (re.compile(r"\bstart[_ -]?paper\b|\bpaper[_ -]?active\b", re.I), "paper_start"),
    (re.compile(r"\bstart[_ -]?shadow\b|\bshadow[_ -]?active\b", re.I), "shadow_start"),
    (re.compile(r"\bstart[_ -]?live\b|\blive[_ -]?active\b", re.I), "live_start"),
    (re.compile(r"\bruntime\b", re.I), "runtime"),
    (re.compile(r"\bscheduler\b|\bautonom(y|ous)\b", re.I), "scheduler_autonomy"),
    (re.compile(r"\bprovider\b|\bapi\b|\bcredential\b|\bsecret\b", re.I), "provider_api_credential"),
)

APPROVAL_REQUIRED_FIELDS = (
    "schema_version",
    "approved_by",
    "approval_scope",
    "approval_statement",
    "approval_timestamp_utc",
    "authorizes_noncanonical_offline_research_execution",
    "authorizes_canonical_write",
    "authorizes_candidate_lifecycle",
    "authorizes_paper_live_runtime",
    "authorizes_scheduler_autonomy",
    "authorizes_notifications",
    "preregistration_packet_sha256",
)

APPROVAL_EXTRA_FALSE_FIELDS = (
    "authorizes_crossing",
    "authorizes_promotion_or_readiness",
    "authorizes_provider_api_or_credentials",
    "authorizes_dependency_config_data_acquisition",
    "authorizes_protected_path_touch",
)

NON_AUTHORITY_ASSERTIONS: dict[str, bool] = {
    "canonical_write": False,
    "candidate_lifecycle_write": False,
    "crossing": False,
    "promotion_or_readiness": False,
    "paper_live_runtime": False,
    "scheduler_autonomy": False,
    "notification_sending": False,
    "provider_api_credential": False,
    "dependency_config_data_acquisition": False,
    "protected_path_touch": False,
}


class GateActionError(ValueError):
    """Raised when a gate action cannot safely produce an output."""


@dataclass(frozen=True)
class GateActionResult:
    gate_action_id: str
    action_kind: str
    output_path: Path
    output_sha256: str
    payload: dict[str, Any] | None = None
    preview_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema_version": ACTION_SCHEMA_VERSION,
            "gate_action_id": self.gate_action_id,
            "action_kind": self.action_kind,
            "output_path": self.output_path.as_posix(),
            "output_sha256": self.output_sha256,
            "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
        }
        if self.payload is not None:
            result["payload"] = self.payload
        if self.preview_text is not None:
            result["preview_text"] = self.preview_text
        return result


def preview_prereg_approval(
    *,
    approval_requirement_path: Path,
    preregistration_packet_path: Path,
    output_file: Path | None = None,
    gate_action_id: str | None = None,
) -> GateActionResult:
    """Write or return a human-readable preview without creating approval."""

    requirement, packet = _load_bound_requirement_and_packet(
        approval_requirement_path, preregistration_packet_path
    )
    action_id = gate_action_id or _gate_action_id(
        "prereg-preview",
        {
            "approval_requirement": _path_hash(approval_requirement_path),
            "packet": _path_hash(preregistration_packet_path),
        },
    )
    target = _resolve_output_file(
        action_id=action_id,
        filename=APPROVAL_PREVIEW_FILENAME,
        output_file=output_file,
    )
    preview_text = _approval_preview_markdown(requirement, packet, action_id)
    write_text(target, preview_text)
    return GateActionResult(
        gate_action_id=action_id,
        action_kind="prereg_approval_preview",
        output_path=target,
        output_sha256=file_sha256(target),
        preview_text=preview_text,
    )


def create_prereg_approval_marker(
    *,
    approval_requirement_path: Path,
    preregistration_packet_path: Path,
    operator_fields: Mapping[str, Any],
    output_file: Path | None = None,
    gate_action_id: str | None = None,
) -> GateActionResult:
    """Create an exact-content prereg approval marker from explicit fields."""

    requirement, packet = _load_bound_requirement_and_packet(
        approval_requirement_path, preregistration_packet_path
    )
    _validate_operator_fields(operator_fields, requirement, packet)
    action_id = gate_action_id or _gate_action_id(
        "prereg-approval",
        {
            "approval_requirement": _path_hash(approval_requirement_path),
            "packet": _path_hash(preregistration_packet_path),
            "operator_fields": dict(operator_fields),
        },
    )
    target = _resolve_output_file(
        action_id=action_id,
        filename=APPROVAL_MARKER_FILENAME,
        output_file=output_file,
    )
    marker = _approval_marker_payload(
        action_id=action_id,
        requirement=requirement,
        packet=packet,
        operator_fields=operator_fields,
    )
    write_json(target, marker)
    return GateActionResult(
        gate_action_id=action_id,
        action_kind="prereg_approval_marker",
        output_path=target,
        output_sha256=file_sha256(target),
        payload=marker,
    )


def record_candidate_surface_decision(
    *,
    decision: str,
    decided_by: str,
    decision_timestamp_utc: str,
    advisory_packet_path: Path | None = None,
    rationale: str = "",
    output_file: Path | None = None,
    gate_action_id: str | None = None,
) -> GateActionResult:
    """Record a non-authority advisory decision for a candidate-surface packet."""

    normalized_decision = str(decision).strip()
    _validate_candidate_decision(normalized_decision, rationale)
    if not str(decided_by).strip():
        raise GateActionError("decided_by is required")
    if not str(decision_timestamp_utc).strip():
        raise GateActionError("decision_timestamp_utc is required")

    advisory_ref = _advisory_packet_ref(advisory_packet_path)
    action_id = gate_action_id or _gate_action_id(
        "candidate-surface-decision",
        {
            "decision": normalized_decision,
            "decided_by": decided_by,
            "decision_timestamp_utc": decision_timestamp_utc,
            "advisory_ref": advisory_ref,
            "rationale": rationale,
        },
    )
    target = _resolve_output_file(
        action_id=action_id,
        filename=CANDIDATE_DECISION_FILENAME,
        output_file=output_file,
    )
    payload = {
        "schema_version": CANDIDATE_DECISION_SCHEMA_VERSION,
        "gate_action_id": action_id,
        "decision": normalized_decision,
        "decided_by": decided_by,
        "decision_timestamp_utc": decision_timestamp_utc,
        "rationale": rationale,
        "advisory_packet_ref": advisory_ref,
        "writes_candidate_lifecycle": False,
        "writes_crossing": False,
        "writes_promotion_or_readiness": False,
        "writes_paper_live_runtime": False,
        "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
        "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
        "authority_boundary": (
            "Records only a local advisory decision value; it does not admit a "
            "candidate, cross evidence, promote, mark readiness, start paper, "
            "start shadow, start live, touch runtime, use scheduler/autonomy, "
            "send notifications, contact providers/APIs, or use credentials."
        ),
    }
    write_json(target, payload)
    return GateActionResult(
        gate_action_id=action_id,
        action_kind="candidate_surface_decision",
        output_path=target,
        output_sha256=file_sha256(target),
        payload=payload,
    )


def _load_bound_requirement_and_packet(
    approval_requirement_path: Path, preregistration_packet_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    requirement = read_json(approval_requirement_path)
    packet = read_json(preregistration_packet_path)
    if requirement.get("schema_version") != "lab_pipeline_approval_requirement_v1":
        raise GateActionError("approval_requirement schema_version mismatch")
    if packet.get("schema_version") != "lab_pipeline_preregistration_packet_v1":
        raise GateActionError("preregistration_packet schema_version mismatch")
    packet_hash = packet.get("packet_sha256")
    if not isinstance(packet_hash, str) or not packet_hash:
        raise GateActionError("preregistration_packet lacks packet_sha256")
    recomputed_hash = _recompute_packet_hash(packet)
    if recomputed_hash != packet_hash:
        raise GateActionError("preregistration_packet_sha256 does not match packet content")
    if requirement.get("preregistration_packet_sha256") != packet_hash:
        raise GateActionError("approval_requirement does not bind to preregistration packet hash")
    if requirement.get("approval_marker_schema") != model.APPROVAL_SCHEMA_VERSION:
        raise GateActionError("approval_requirement marker schema mismatch")
    required_fields = requirement.get("required_fields")
    if not isinstance(required_fields, dict):
        raise GateActionError("approval_requirement missing required_fields")
    if required_fields.get("preregistration_packet_sha256") != packet_hash:
        raise GateActionError("approval_requirement required_fields hash mismatch")
    if requirement.get("pipeline_run_id") != packet.get("pipeline_run_id"):
        raise GateActionError("approval_requirement pipeline_run_id mismatch")
    if requirement.get("request_id") != packet.get("request_id"):
        raise GateActionError("approval_requirement request_id mismatch")
    return requirement, packet


def _validate_operator_fields(
    operator_fields: Mapping[str, Any],
    requirement: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> None:
    missing = [field for field in APPROVAL_REQUIRED_FIELDS if field not in operator_fields]
    if missing:
        raise GateActionError(f"operator fields missing required approval fields: {missing}")

    required = requirement["required_fields"]
    expected = {
        "schema_version": model.APPROVAL_SCHEMA_VERSION,
        "approved_by": "Karl",
        "approval_scope": model.APPROVAL_SCOPE,
        "approval_statement": required["approval_statement"],
        "authorizes_noncanonical_offline_research_execution": True,
        "authorizes_canonical_write": False,
        "authorizes_candidate_lifecycle": False,
        "authorizes_paper_live_runtime": False,
        "authorizes_scheduler_autonomy": False,
        "authorizes_notifications": False,
        "preregistration_packet_sha256": packet["packet_sha256"],
    }
    errors: list[str] = []
    for field, expected_value in expected.items():
        if operator_fields.get(field) != expected_value:
            errors.append(f"{field}_mismatch")
    timestamp = operator_fields.get("approval_timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp.strip():
        errors.append("approval_timestamp_utc_missing")
    for field in APPROVAL_EXTRA_FALSE_FIELDS:
        if operator_fields.get(field, False) is not False:
            errors.append(f"approval_too_broad:{field}")
    if errors:
        raise GateActionError("invalid prereg approval operator fields: " + ", ".join(errors))


def _approval_marker_payload(
    *,
    action_id: str,
    requirement: Mapping[str, Any],
    packet: Mapping[str, Any],
    operator_fields: Mapping[str, Any],
) -> dict[str, Any]:
    marker = {field: operator_fields[field] for field in APPROVAL_REQUIRED_FIELDS}
    for field in APPROVAL_EXTRA_FALSE_FIELDS:
        marker[field] = False
    marker.update(
        {
            "gate_action_id": action_id,
            "approval_requirement_ref": {
                "pipeline_run_id": requirement["pipeline_run_id"],
                "request_id": requirement["request_id"],
                "preregistration_packet_sha256": requirement["preregistration_packet_sha256"],
            },
            "non_authority_assertions": dict(NON_AUTHORITY_ASSERTIONS),
            "non_authority_flags": dict(model.NON_AUTHORITY_FLAGS),
        }
    )
    return marker


def _approval_preview_markdown(
    requirement: Mapping[str, Any], packet: Mapping[str, Any], action_id: str
) -> str:
    frozen = packet.get("frozen_content", {})
    request = frozen.get("request", {}) if isinstance(frozen, Mapping) else {}
    authority_flags = {
        "canonical_write_allowed": frozen.get("canonical_write_allowed"),
        "candidate_lifecycle_write_allowed": frozen.get("candidate_lifecycle_write_allowed"),
        "paper_live_runtime_contact_allowed": frozen.get("paper_live_runtime_contact_allowed"),
        "scheduler_autonomy_allowed": frozen.get("scheduler_autonomy_allowed"),
        "notification_firing_allowed": frozen.get("notification_firing_allowed"),
        "provider_api_network_allowed": frozen.get("provider_api_network_allowed"),
    }
    lines = [
        "# Prereg Approval Preview",
        "",
        f"- Gate action ID: {action_id}",
        f"- Packet hash: {packet['packet_sha256']}",
        f"- Source idea: {request.get('source_idea', '')}",
        f"- Symbol/timeframe: {request.get('symbol', '')} / {request.get('timeframe', '')}",
        f"- Execution scope: {frozen.get('execution_scope')}",
        f"- Denominator policy: {frozen.get('denominator_policy')}",
        f"- Required approval scope: {requirement['required_fields']['approval_scope']}",
        f"- Required approval statement: {requirement['required_fields']['approval_statement']}",
        "",
        "## Authority Flags",
    ]
    for key, value in authority_flags.items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(
        [
            "",
            "## Would Authorize",
            "- Non-canonical offline research execution for the exact frozen packet content only.",
            "",
            "## Would Not Authorize",
            "- Canonical writes.",
            "- Candidate lifecycle writes.",
            "- Crossing.",
            "- Promotion or readiness.",
            "- Paper/live/runtime contact.",
            "- Scheduler or autonomy.",
            "- Notification sending.",
            "- Provider/API/credential use.",
            "- Dependency/config/data acquisition.",
            "- Protected-path touch.",
            "",
            "## Non-Authority Assertions",
        ]
    )
    for key, value in NON_AUTHORITY_ASSERTIONS.items():
        lines.append(f"- {key}: {str(value).lower()}")
    return "\n".join(lines) + "\n"


def _validate_candidate_decision(decision: str, rationale: str) -> None:
    if decision in FORBIDDEN_DECISION_VALUES:
        raise GateActionError(f"candidate-surface decision is forbidden: {decision}")
    if decision not in ALLOWED_CANDIDATE_SURFACE_DECISIONS:
        raise GateActionError(f"unsupported candidate-surface decision: {decision}")
    scan_text = "\n".join([decision, rationale])
    findings = [code for pattern, code in FORBIDDEN_DECISION_PATTERNS if pattern.search(scan_text)]
    if findings:
        raise GateActionError("candidate-surface decision implies forbidden authority: " + ", ".join(findings))


def _advisory_packet_ref(advisory_packet_path: Path | None) -> dict[str, Any]:
    if advisory_packet_path is None:
        return {
            "path": None,
            "sha256": None,
            "future_input_placeholder": True,
        }
    resolved = Path(advisory_packet_path)
    return {
        "path": resolved.as_posix(),
        "sha256": file_sha256(resolved),
        "future_input_placeholder": False,
    }


def _resolve_output_file(
    *,
    action_id: str,
    filename: str,
    output_file: Path | None,
) -> Path:
    target = Path(output_file) if output_file is not None else DEFAULT_OUTPUT_ROOT / action_id / filename
    resolved = target.resolve()
    _validate_output_path(resolved)
    return resolved


def _validate_output_path(resolved: Path) -> None:
    repo_root = REPO_ROOT.resolve()
    scratch_root = DEFAULT_SCRATCH_ROOT.resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        temp_root = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(temp_root)
        except ValueError as exc:
            raise GateActionError(
                "output file outside repo must be under the system temporary directory"
            ) from exc
        return
    try:
        resolved.relative_to(scratch_root)
    except ValueError as exc:
        raise GateActionError(
            "output file inside repo must be under "
            f"{scratch_root.as_posix()}; got {resolved.as_posix()}"
        ) from exc


def _gate_action_id(kind: str, payload: Mapping[str, Any]) -> str:
    return "GATE-ACTION-" + sha256_payload({"kind": kind, "payload": dict(payload)}).split(":", 1)[1][:16]


def _path_hash(path: Path) -> str:
    return file_sha256(Path(path))


def _recompute_packet_hash(packet: Mapping[str, Any]) -> str:
    packet_without_hash = dict(packet)
    packet_without_hash.pop("packet_sha256", None)
    return sha256_payload(packet_without_hash)
