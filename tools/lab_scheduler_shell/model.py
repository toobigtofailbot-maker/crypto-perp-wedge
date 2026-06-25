"""Data model for the inert research-lab run queue.

Defines the run-queue schema, the (non-executing) run-status vocabulary, the
retry/block-state vocabulary, and an artifact-link model. None of these names
imply execution: a queue entry describes *what a future scheduler would target*,
and in the default-off posture every entry is held.

Lab *pipeline* state (e.g. ``no_go``, ``oos_gate_fail``) is owned by
``tools.lab_state.model`` and is not redefined here. A queue entry may carry a
``subject_id`` that binds it to a committed read-only lab-state subject; the
subject's true pipeline state is resolved by ``tools/lab_state`` alone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from tools.lab_state import model as lab_state_model

SCHEMA_VERSION: Final = "lab_scheduler_shell_v1"

# ---------------------------------------------------------------------------
# Run-status vocabulary. These describe a *queued* item's disposition in an
# inert shell — none of them means "executing" or "completed a run". There is
# deliberately no ``running`` / ``succeeded`` status because nothing runs.
# ---------------------------------------------------------------------------
RUN_STATUSES: Final[tuple[str, ...]] = (
    "queued",            # present in the queue, not actioned
    "held_default_off",  # would be eligible, but autonomy is disabled
    "blocked",           # cannot proceed; carries a block reason code
    "retry_scheduled",   # a retry is *recorded* (not executed) for visibility
    "planned_noop",      # a dry-run plan exists; the planned action is a no-op
    "cancelled",         # withdrawn from consideration (no side effect)
)

# Statuses that are terminal for the shell's purposes (no further planning).
TERMINAL_RUN_STATUSES: Final[frozenset[str]] = frozenset(
    {"blocked", "cancelled"}
)

# ---------------------------------------------------------------------------
# Retry / block visibility vocabulary.
# ---------------------------------------------------------------------------
RETRY_STATES: Final[tuple[str, ...]] = (
    "none",        # no retry recorded
    "scheduled",   # a retry is recorded for visibility (never executed)
    "exhausted",   # retry budget recorded as spent
)

# Block reason codes are namespaced ``SCHED_*`` so they never collide with the
# lab-state reason codes and never imply a strategy judgement.
BLOCK_REASON_CODES: Final[tuple[str, ...]] = (
    "SCHED_AUTONOMY_DISABLED",          # default-off posture holds the entry
    "SCHED_RUN_TRIGGERING_DISABLED",    # run creation disabled
    "SCHED_DEPENDENCY_UNRESOLVED",      # an upstream queue dependency is unmet
    "SCHED_SUBJECT_NOT_FOUND",          # bound subject_id not in lab_state
    "SCHED_ARTIFACT_MISSING",           # a referenced artifact is absent
    "SCHED_RETRY_BUDGET_EXHAUSTED",     # recorded retry budget spent
    "SCHED_MANUAL_HOLD",                # explicitly held by an operator note
)


def is_valid_status(status: str) -> bool:
    return status in RUN_STATUSES


def is_valid_retry_state(state: str) -> bool:
    return state in RETRY_STATES


# ---------------------------------------------------------------------------
# Artifact-link model (reuses the lab_state ArtifactRef shape: role/path/present).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ArtifactLink:
    """Read-only pointer from a queue entry to a repo artifact.

    ``present`` is a static, caller-supplied flag (resolved by reading the
    fixture / repo tree); the model itself performs no I/O.
    """

    role: str
    path: str
    present: bool = False
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "path": self.path,
            "present": self.present,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ArtifactLink":
        return cls(
            role=str(raw.get("role", "")),
            path=str(raw.get("path", "")),
            present=bool(raw.get("present", False)),
            note=str(raw.get("note", "")),
        )


@dataclass(frozen=True)
class RetryState:
    """Recorded retry/block visibility for a queue entry (never executed)."""

    state: str = "none"
    attempts: int = 0
    max_attempts: int = 0
    block_reason_code: str | None = None
    block_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "block_reason_code": self.block_reason_code,
            "block_detail": self.block_detail,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "RetryState":
        raw = raw or {}
        return cls(
            state=str(raw.get("state", "none")),
            attempts=int(raw.get("attempts", 0)),
            max_attempts=int(raw.get("max_attempts", 0)),
            block_reason_code=raw.get("block_reason_code"),
            block_detail=str(raw.get("block_detail", "")),
        )


@dataclass(frozen=True)
class QueueEntry:
    """One inert run-queue entry. Describes a *would-be* target, runs nothing."""

    run_id: str
    subject_id: str
    target_stage: str
    priority: int = 100
    status: str = "queued"
    requested_by: str = "shell_fixture"
    retry: RetryState = field(default_factory=RetryState)
    artifact_links: tuple[ArtifactLink, ...] = ()
    depends_on: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "subject_id": self.subject_id,
            "target_stage": self.target_stage,
            "priority": self.priority,
            "status": self.status,
            "requested_by": self.requested_by,
            "retry": self.retry.to_dict(),
            "artifact_links": [a.to_dict() for a in self.artifact_links],
            "depends_on": list(self.depends_on),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "QueueEntry":
        return cls(
            run_id=str(raw["run_id"]),
            subject_id=str(raw.get("subject_id", "")),
            target_stage=str(raw.get("target_stage", "")),
            priority=int(raw.get("priority", 100)),
            status=str(raw.get("status", "queued")),
            requested_by=str(raw.get("requested_by", "shell_fixture")),
            retry=RetryState.from_dict(raw.get("retry")),
            artifact_links=tuple(
                ArtifactLink.from_dict(a) for a in raw.get("artifact_links", [])
            ),
            depends_on=tuple(str(d) for d in raw.get("depends_on", [])),
            note=str(raw.get("note", "")),
        )


class QueueValidationError(ValueError):
    """Raised when a queue or entry violates the schema."""


@dataclass(frozen=True)
class RunQueue:
    """An ordered, validated, inert run queue."""

    schema_version: str
    entries: tuple[QueueEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
        }

    def ordered(self) -> tuple[QueueEntry, ...]:
        """Deterministic display order: priority asc, then run_id."""
        return tuple(
            sorted(self.entries, key=lambda e: (e.priority, e.run_id))
        )


def validate_entry(entry: QueueEntry, *, known_subject_ids: frozenset[str]) -> list[str]:
    """Return a list of validation problems for one entry (empty == valid)."""
    problems: list[str] = []
    if not entry.run_id:
        problems.append("entry missing run_id")
    if not is_valid_status(entry.status):
        problems.append(f"{entry.run_id}: unknown status {entry.status!r}")
    if entry.target_stage and not lab_state_model.is_valid_stage(entry.target_stage):
        problems.append(
            f"{entry.run_id}: target_stage {entry.target_stage!r} is not a lab stage"
        )
    if entry.subject_id and entry.subject_id not in known_subject_ids:
        problems.append(
            f"{entry.run_id}: subject_id {entry.subject_id!r} not a known lab subject"
        )
    if not is_valid_retry_state(entry.retry.state):
        problems.append(
            f"{entry.run_id}: unknown retry state {entry.retry.state!r}"
        )
    code = entry.retry.block_reason_code
    if code is not None and code not in BLOCK_REASON_CODES:
        problems.append(f"{entry.run_id}: unknown block reason code {code!r}")
    if entry.retry.attempts < 0 or entry.retry.max_attempts < 0:
        problems.append(f"{entry.run_id}: negative retry counters")
    return problems


def build_queue(
    raw: dict[str, Any], *, known_subject_ids: frozenset[str]
) -> RunQueue:
    """Parse and validate a run-queue fixture payload (no I/O, no execution)."""
    if not isinstance(raw, dict):
        raise QueueValidationError("queue fixture must be a JSON object")
    version = raw.get("schema_version")
    if version != SCHEMA_VERSION:
        raise QueueValidationError(
            f"unexpected schema_version {version!r}; expected {SCHEMA_VERSION!r}"
        )
    raw_entries = raw.get("entries")
    if not isinstance(raw_entries, list):
        raise QueueValidationError("queue fixture 'entries' must be a list")

    entries = tuple(QueueEntry.from_dict(e) for e in raw_entries)

    problems: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if entry.run_id in seen:
            problems.append(f"duplicate run_id {entry.run_id!r}")
        seen.add(entry.run_id)
        problems.extend(validate_entry(entry, known_subject_ids=known_subject_ids))
    # Dependency references must resolve to a run_id in the same queue.
    for entry in entries:
        for dep in entry.depends_on:
            if dep not in seen:
                problems.append(f"{entry.run_id}: depends_on unknown run_id {dep!r}")

    if problems:
        raise QueueValidationError("; ".join(problems))

    return RunQueue(schema_version=SCHEMA_VERSION, entries=entries)
