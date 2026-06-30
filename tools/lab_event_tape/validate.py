"""Validate deterministic no-edge lab event tapes.

This helper is intentionally read-only. It validates contract shape, closed
enums, deterministic ordering, non-authority flags, and declared synthetic
population references without replaying events through lab operating surfaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lab_event_tape.v1"
PACKAGE = "WP-LAB-EVENT-TAPE-CONTRACT-01"
REFERENCE_TAPE_ID = "LAB-EVENT-TAPE-REFERENCE-001"
SOURCE_MANIFEST_PATH = Path(
    "scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/synthetic_population_manifest.json"
)

EVENT_TYPES = {
    "job_enqueued",
    "job_started",
    "job_completed",
    "job_failed",
    "job_invalid",
    "job_blocked",
    "metrics_withheld",
    "metrics_insufficient",
    "resource_limited",
    "job_delayed",
    "review_needed",
    "notification_worthy",
    "daily_window_tick",
    "weekly_window_tick",
    "dashboard_snapshot_tick",
    "registry_checkpoint",
}
JOB_OUTCOMES = {
    "not_terminal",
    "completed",
    "failed",
    "invalid",
    "blocked",
    "withheld",
    "insufficient",
    "resource_limited",
    "delayed",
    "review_needed",
    "no_candidate",
}
JOB_STATES = {
    "not_seen",
    "queued",
    "running",
    "completed",
    "failed",
    "invalid",
    "blocked",
    "withheld",
    "insufficient",
    "resource_limited",
    "delayed",
    "review_needed",
    "no_candidate",
}
PRIORITIES = {"low", "normal", "high", "urgent"}
EXPECTED_QUEUE_ACTIONS = {
    "none",
    "enqueue",
    "mark_running",
    "mark_terminal",
    "mark_invalid",
    "mark_blocked",
    "mark_withheld",
    "mark_insufficient",
    "mark_resource_limited",
    "mark_delayed",
    "mark_review_needed",
}
EXPECTED_SCHEDULER_ACTIONS = {
    "no_autonomous_dispatch",
    "eligible_for_dry_run_start",
    "hold_resource_limit",
    "hold_dependency_blocked",
    "mark_delayed",
    "mark_terminal",
}
EXPECTED_NOTIFICATION_ACTIONS = {
    "none",
    "dry_run_blocked",
    "dry_run_failed",
    "dry_run_review_needed",
    "dry_run_withheld",
    "dry_run_resource_limited",
    "dry_run_daily_summary",
    "dry_run_weekly_summary",
}
EXPECTED_REPORT_ACTIONS = {
    "none",
    "include_if_window_matches",
    "include_in_daily_window",
    "include_in_weekly_window",
    "include_terminal_summary",
    "include_blocker_summary",
    "include_withheld_summary",
}
EXPECTED_DASHBOARD_ACTIONS = {
    "show_operating_test_state",
    "show_queued",
    "show_running",
    "show_terminal",
    "show_blocked",
    "show_withheld",
    "show_review_needed",
    "show_resource_limited",
    "show_no_candidate",
}
EXPECTED_AGENT_ACTIONS = {
    "none",
    "track_no_candidate_authority",
    "track_terminal_no_candidate",
    "track_blocker_no_candidate_authority",
    "track_summary_no_candidate_authority",
}
EXPECTED_REGISTRY_ACTIONS = {
    "none",
    "record_operating_test_event",
    "record_operating_test_checkpoint",
}

REQUIRED_TAPE_FLAGS = {
    "deterministic": True,
    "construction_payload": True,
    "non_promotable": True,
    "operating_test_evidence": True,
    "strategy_evidence": False,
    "candidate_evidence": False,
    "edge_claim_allowed": False,
    "canonical_crossing_allowed": False,
    "paper_live_eligible": False,
    "real_notification_sending_allowed": False,
    "autonomous_scheduler_allowed": False,
}
REQUIRED_EVENT_FLAGS = {
    "construction_payload": True,
    "non_promotable": True,
    "operating_test_evidence": True,
    "strategy_evidence": False,
    "candidate_eligible": False,
    "promotion_eligible": False,
    "paper_live_eligible": False,
    "canonical_crossing_allowed": False,
    "edge_claim_allowed": False,
    "real_notification_sending_allowed": False,
    "autonomous_scheduler_allowed": False,
}
REQUIRED_EVENT_FIELDS = {
    "event_id",
    "sequence_index",
    "event_time",
    "event_type",
    "job_id",
    "source_row_id",
    "source_variant_id",
    "construction_payload",
    "non_promotable",
    "operating_test_evidence",
    "strategy_evidence",
    "candidate_eligible",
    "promotion_eligible",
    "paper_live_eligible",
    "canonical_crossing_allowed",
    "edge_claim_allowed",
    "real_notification_sending_allowed",
    "autonomous_scheduler_allowed",
    "priority",
    "job_state_before",
    "job_state_after",
    "job_outcome",
    "expected_operating_outcome",
}
REQUIRED_OUTCOME_FIELDS = {
    "queue_action",
    "scheduler_action",
    "notification_action",
    "report_action",
    "dashboard_action",
    "agent_action",
    "registry_action",
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    deterministic_replay_validation: str
    closed_enum_validation: str
    non_promotable_validation: str
    source_reference_validation: str
    errors: list[str]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "deterministic_replay_validation": self.deterministic_replay_validation,
            "closed_enum_validation": self.closed_enum_validation,
            "non_promotable_validation": self.non_promotable_validation,
            "source_reference_validation": self.source_reference_validation,
            "errors": self.errors,
            "summary": self.summary,
        }


def _parse_utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo != timezone.utc:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _load_source_refs(repo_root: Path) -> tuple[set[tuple[str, str]], str, str | None]:
    manifest_path = repo_root / SOURCE_MANIFEST_PATH
    if not manifest_path.exists():
        return set(), "missing_manifest", None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    refs = {
        (row.get("row_id"), row.get("variant_id"))
        for row in manifest.get("rows", [])
        if row.get("row_id") and row.get("variant_id")
    }
    return refs, "strict_row_reference_validation", _sha256_file(manifest_path)


def validate_tape(path: Path, repo_root: Path | None = None) -> ValidationResult:
    repo_root = repo_root or Path.cwd()
    errors: list[str] = []
    closed_enum_errors: list[str] = []
    non_promotable_errors: list[str] = []
    source_errors: list[str] = []

    tape = json.loads(path.read_text(encoding="utf-8"))
    for field, expected in REQUIRED_TAPE_FLAGS.items():
        if tape.get(field) is not expected:
            non_promotable_errors.append(f"tape.{field} must be {expected!r}")
    if tape.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if tape.get("package") != PACKAGE:
        errors.append(f"package must be {PACKAGE}")
    if not tape.get("seed"):
        errors.append("seed is required")

    events = tape.get("events")
    if not isinstance(events, list):
        errors.append("events must be a list")
        events = []
    source_refs, source_mode, source_hash = _load_source_refs(repo_root)
    if source_mode == "missing_manifest":
        source_errors.append(f"missing source manifest: {SOURCE_MANIFEST_PATH.as_posix()}")

    seen_ids: set[str] = set()
    seen_jobs: set[str] = set()
    event_types: set[str] = set()
    job_outcomes: set[str] = set()
    priorities: set[str] = set()
    daily_windows = 0
    weekly_windows = 0
    dashboard_ticks = 0
    registry_checkpoints = 0
    previous_time: datetime | None = None

    for index, event in enumerate(events, start=1):
        missing = REQUIRED_EVENT_FIELDS - event.keys()
        if missing:
            errors.append(f"event {index} missing fields: {sorted(missing)}")
            continue
        if event.get("sequence_index") != index:
            errors.append(f"event {event.get('event_id')} sequence_index must be {index}")
        expected_event_id = f"EVT-{index:04d}"
        if event.get("event_id") != expected_event_id:
            errors.append(f"event at sequence {index} must use event_id {expected_event_id}")
        if event["event_id"] in seen_ids:
            errors.append(f"duplicate event_id: {event['event_id']}")
        seen_ids.add(event["event_id"])

        event_time = _parse_utc_timestamp(event.get("event_time"))
        if event_time is None:
            errors.append(f"event {event['event_id']} has invalid UTC event_time")
        elif previous_time is not None and event_time < previous_time:
            errors.append(f"event {event['event_id']} time decreases")
        previous_time = event_time or previous_time

        for field, expected in REQUIRED_EVENT_FLAGS.items():
            if event.get(field) is not expected:
                non_promotable_errors.append(
                    f"event {event['event_id']} {field} must be {expected!r}"
                )

        event_type = event.get("event_type")
        job_outcome = event.get("job_outcome")
        priority = event.get("priority")
        state_before = event.get("job_state_before")
        state_after = event.get("job_state_after")
        if event_type not in EVENT_TYPES:
            closed_enum_errors.append(f"event {event['event_id']} invalid event_type {event_type!r}")
        if job_outcome not in JOB_OUTCOMES:
            closed_enum_errors.append(f"event {event['event_id']} invalid job_outcome {job_outcome!r}")
        if priority not in PRIORITIES:
            closed_enum_errors.append(f"event {event['event_id']} invalid priority {priority!r}")
        if state_before not in JOB_STATES:
            closed_enum_errors.append(
                f"event {event['event_id']} invalid job_state_before {state_before!r}"
            )
        if state_after not in JOB_STATES:
            closed_enum_errors.append(
                f"event {event['event_id']} invalid job_state_after {state_after!r}"
            )

        outcome = event.get("expected_operating_outcome")
        if not isinstance(outcome, dict):
            errors.append(f"event {event['event_id']} expected_operating_outcome must be an object")
        else:
            missing_outcome = REQUIRED_OUTCOME_FIELDS - outcome.keys()
            if missing_outcome:
                errors.append(
                    f"event {event['event_id']} missing expected outcome fields: "
                    f"{sorted(missing_outcome)}"
                )
            enum_checks = [
                ("queue_action", EXPECTED_QUEUE_ACTIONS),
                ("scheduler_action", EXPECTED_SCHEDULER_ACTIONS),
                ("notification_action", EXPECTED_NOTIFICATION_ACTIONS),
                ("report_action", EXPECTED_REPORT_ACTIONS),
                ("dashboard_action", EXPECTED_DASHBOARD_ACTIONS),
                ("agent_action", EXPECTED_AGENT_ACTIONS),
                ("registry_action", EXPECTED_REGISTRY_ACTIONS),
            ]
            for field, allowed in enum_checks:
                if outcome.get(field) not in allowed:
                    closed_enum_errors.append(
                        f"event {event['event_id']} invalid expected {field} "
                        f"{outcome.get(field)!r}"
                    )

        source_ref = (event.get("source_row_id"), event.get("source_variant_id"))
        if source_refs and source_ref not in source_refs:
            source_errors.append(
                f"event {event['event_id']} source reference not in #588 manifest: {source_ref}"
            )

        seen_jobs.add(event.get("job_id"))
        if event_type:
            event_types.add(event_type)
        if job_outcome:
            job_outcomes.add(job_outcome)
        if priority:
            priorities.add(priority)
        daily_windows += 1 if event_type == "daily_window_tick" else 0
        weekly_windows += 1 if event_type == "weekly_window_tick" else 0
        dashboard_ticks += 1 if event_type == "dashboard_snapshot_tick" else 0
        registry_checkpoints += 1 if event_type == "registry_checkpoint" else 0

    missing_event_types = EVENT_TYPES - event_types
    if missing_event_types:
        errors.append(f"missing required event types: {sorted(missing_event_types)}")
    missing_job_outcomes = JOB_OUTCOMES - job_outcomes
    if missing_job_outcomes:
        errors.append(f"missing required job outcomes: {sorted(missing_job_outcomes)}")
    if len(seen_jobs) < 10:
        errors.append("reference tape must contain at least 10 distinct job_ids")
    if len(events) < 40:
        errors.append("reference tape must contain at least 40 events")
    if len(priorities) < 4:
        errors.append("reference tape must cover low, normal, high, and urgent priorities")
    if daily_windows < 2:
        errors.append("reference tape must include at least 2 daily windows")
    if weekly_windows < 1:
        errors.append("reference tape must include at least 1 weekly window")
    if dashboard_ticks < 1:
        errors.append("reference tape must include at least 1 dashboard snapshot tick")
    if registry_checkpoints < 1:
        errors.append("reference tape must include at least 1 registry checkpoint")

    errors.extend(closed_enum_errors)
    errors.extend(non_promotable_errors)
    errors.extend(source_errors)
    summary = build_summary(tape, source_mode, source_hash)
    valid = not errors
    return ValidationResult(
        valid=valid,
        deterministic_replay_validation="pass" if valid else "fail",
        closed_enum_validation="pass" if not closed_enum_errors else "fail",
        non_promotable_validation="pass" if not non_promotable_errors else "fail",
        source_reference_validation="pass_strict_row_reference_validation"
        if not source_errors and source_mode == "strict_row_reference_validation"
        else source_mode,
        errors=errors,
        summary=summary,
    )


def build_summary(
    tape: dict[str, Any], source_reference_validation_mode: str, source_manifest_sha256: str | None
) -> dict[str, Any]:
    events = tape.get("events", [])
    job_ids = {event.get("job_id") for event in events}
    event_types = sorted({event.get("event_type") for event in events if event.get("event_type")})
    job_outcomes = sorted(
        {event.get("job_outcome") for event in events if event.get("job_outcome")}
    )
    return {
        "package": PACKAGE,
        "tape_id": tape.get("tape_id"),
        "schema_version": tape.get("schema_version"),
        "event_count": len(events),
        "job_count": len(job_ids),
        "deterministic": tape.get("deterministic") is True,
        "construction_payload_all_events": all(
            event.get("construction_payload") is True for event in events
        ),
        "non_promotable_all_events": all(event.get("non_promotable") is True for event in events),
        "operating_test_evidence_all_events": all(
            event.get("operating_test_evidence") is True for event in events
        ),
        "strategy_evidence_any": any(event.get("strategy_evidence") is True for event in events),
        "candidate_eligible_any": any(event.get("candidate_eligible") is True for event in events),
        "promotion_eligible_any": any(event.get("promotion_eligible") is True for event in events),
        "paper_live_eligible_any": any(event.get("paper_live_eligible") is True for event in events),
        "canonical_crossing_allowed_any": any(
            event.get("canonical_crossing_allowed") is True for event in events
        ),
        "edge_claim_allowed_any": any(event.get("edge_claim_allowed") is True for event in events),
        "real_notification_sending_allowed_any": any(
            event.get("real_notification_sending_allowed") is True for event in events
        ),
        "autonomous_scheduler_allowed_any": any(
            event.get("autonomous_scheduler_allowed") is True for event in events
        ),
        "event_types_covered": event_types,
        "job_outcomes_covered": job_outcomes,
        "daily_windows": sum(1 for event in events if event.get("event_type") == "daily_window_tick"),
        "weekly_windows": sum(
            1 for event in events if event.get("event_type") == "weekly_window_tick"
        ),
        "dashboard_ticks": sum(
            1 for event in events if event.get("event_type") == "dashboard_snapshot_tick"
        ),
        "registry_checkpoints": sum(
            1 for event in events if event.get("event_type") == "registry_checkpoint"
        ),
        "source_reference_validation_mode": source_reference_validation_mode,
        "source_manifest_path": SOURCE_MANIFEST_PATH.as_posix(),
        "source_manifest_sha256": source_manifest_sha256,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tape_path", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--result-out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args(argv)

    result = validate_tape(args.tape_path, repo_root=args.repo_root)
    result_payload = result.to_dict()
    if args.result_out:
        args.result_out.write_text(
            json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.summary_out:
        args.summary_out.write_text(
            json.dumps(result.summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result_payload, indent=2, sort_keys=True))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
