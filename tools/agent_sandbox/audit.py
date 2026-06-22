"""Deterministic audit records and sinks for agent ToolContext decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Protocol


NON_AUTHORITY_STATEMENT = (
    "audit record only; no canonical, candidate-lifecycle, promotion, paper/live, "
    "runtime, or execution authority"
)


@dataclass(frozen=True)
class AuditRecord:
    """One allowed or blocked ToolContext authorization decision."""

    timestamp_utc: str
    wp_id: str
    role: str
    action_type: str
    target_path: str
    decision: str
    reason: str
    policy_id: str
    non_authority: str = NON_AUTHORITY_STATEMENT

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class AuditSink(Protocol):
    def record(self, audit_record: AuditRecord) -> None:
        """Persist one audit record without changing its contents."""


class MemoryAuditSink:
    """In-memory sink used by deterministic tests and bounded harnesses."""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def record(self, audit_record: AuditRecord) -> None:
        self.records.append(audit_record)


class JsonLinesAuditSink:
    """Append deterministic, key-sorted audit records to a caller-approved path."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def record(self, audit_record: AuditRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(audit_record.to_dict(), sort_keys=True, separators=(",", ":")))
            stream.write("\n")
