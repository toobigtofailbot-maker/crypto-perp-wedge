"""Models for the scratch-only notification and approval pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


ApprovalStatus = Literal["pending", "approved", "rejected", "blocked"]
NotificationSeverity = Literal["info", "warning", "error", "blocked"]

NON_AUTHORITY_FLAGS = [
    "scratch_only",
    "dry_run",
    "one_way_notification",
    "manual_approval_required",
    "not_auto_approval",
    "not_execution",
    "not_paper_live",
    "not_candidate_promotion",
    "not_canonical_write",
]


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    request_type: str
    requested_by: str
    required_human: bool
    status: ApprovalStatus
    evidence_links: list[str]
    non_authority_flags: list[str]
    created_at_utc: str
    updated_at_utc: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        _require_flags(payload["non_authority_flags"])
        if payload["required_human"] is not True:
            raise ValueError("approval requests must require a human")
        if payload["status"] not in {"pending", "approved", "rejected", "blocked"}:
            raise ValueError(f"unsupported approval status: {payload['status']}")
        return payload


@dataclass(frozen=True)
class NotificationEvent:
    event_id: str
    severity: NotificationSeverity
    channel_kind: str
    dry_run: bool
    message: str
    evidence_links: list[str]
    requires_action: bool
    created_at_utc: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        if payload["dry_run"] is not True:
            raise ValueError("notification events must remain dry-run")
        if payload["severity"] not in {"info", "warning", "error", "blocked"}:
            raise ValueError(f"unsupported notification severity: {payload['severity']}")
        return payload


def non_authority_flag_map() -> dict[str, bool]:
    return {flag: True for flag in NON_AUTHORITY_FLAGS}


def _require_flags(flags: list[str]) -> None:
    missing = sorted(set(NON_AUTHORITY_FLAGS) - set(flags))
    if missing:
        raise ValueError(f"missing non-authority flags: {', '.join(missing)}")
