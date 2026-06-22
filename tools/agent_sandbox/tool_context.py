"""ToolContext gate that audits before any bounded agent action executes."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any, TypeVar

from .audit import AuditRecord, AuditSink
from .permissions import POLICY_ID, SUPPORTED_ROLES, decide


T = TypeVar("T")


@dataclass(frozen=True)
class ToolAction:
    action_type: str
    target_path: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


class BlockedActionError(PermissionError):
    """Raised after a blocked action has been recorded by the audit sink."""

    def __init__(self, record: AuditRecord) -> None:
        super().__init__(
            f"blocked {record.action_type} for {record.role} at {record.target_path}: "
            f"{record.reason}"
        )
        self.record = record


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("ToolContext clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _normalize_target_path(target_path: str) -> str:
    if not isinstance(target_path, str) or not target_path.strip():
        raise ValueError("target_path must be a non-empty repo-relative path")
    candidate = target_path.strip().replace("\\", "/")
    if "\x00" in candidate or candidate.startswith(("/", "//")):
        raise ValueError("target_path must be a safe repo-relative path")
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError("target_path must be a safe repo-relative path")
    if pure.parts and pure.parts[0].endswith(":"):
        raise ValueError("target_path must be a safe repo-relative path")
    return pure.as_posix().casefold()


class ToolContext:
    """Bind one repo work package and role to closed-default tool permissions."""

    def __init__(
        self,
        *,
        wp_id: str,
        role: str,
        audit_sink: AuditSink,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        if not wp_id or "/" in wp_id or "\\" in wp_id or ".." in wp_id:
            raise ValueError("wp_id must be a non-empty path-safe identifier")
        if role not in SUPPORTED_ROLES:
            raise ValueError(f"unsupported role={role}")
        self.wp_id = wp_id
        self.role = role
        self._audit_sink = audit_sink
        self._clock = clock

    def authorize(self, action: ToolAction) -> AuditRecord:
        """Audit and return the policy decision without executing the action."""

        if not action.action_type or not action.action_type.strip():
            raise ValueError("action_type must be non-empty")
        action_type = action.action_type.strip().casefold()
        target_path = _normalize_target_path(action.target_path)
        decision = decide(self.role, self.wp_id, action_type, target_path)
        record = AuditRecord(
            timestamp_utc=_format_timestamp(self._clock()),
            wp_id=self.wp_id,
            role=self.role,
            action_type=action_type,
            target_path=target_path,
            decision="allowed" if decision.allowed else "blocked",
            reason=decision.reason,
            policy_id=POLICY_ID,
        )
        self._audit_sink.record(record)
        return record

    def require_allowed(self, action: ToolAction) -> AuditRecord:
        """Return an allowed record or raise after recording the block."""

        record = self.authorize(action)
        if record.decision != "allowed":
            raise BlockedActionError(record)
        return record

    def run_allowed(self, action: ToolAction, operation: Callable[[], T]) -> T:
        """Execute a zero-argument operation only after an allowed audit decision."""

        self.require_allowed(action)
        return operation()
