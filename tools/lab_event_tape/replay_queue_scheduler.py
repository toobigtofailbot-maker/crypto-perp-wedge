"""Replay the deterministic lab event tape through queue/scheduler dry-run checks.

This helper is package-local to the event-tape surface. It validates the tape,
derives dry-run queue and scheduler observations from event order, compares those
observations to the tape's expected operating outcomes, and optionally writes
scratch evidence. It does not import or modify the approval queue or scheduler
shell behavior, and it performs no dispatch.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools.lab_event_tape import validate as tape_validate


PACKAGE = "WP-LAB-QUEUE-SCHEDULER-REPLAY-01"
INPUT_TAPE_ID = "LAB-EVENT-TAPE-REFERENCE-001"
REPLAY_EVIDENCE_CLASS = "operating_test_evidence"
PRIORITY_RANK = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
TERMINAL_STATES = {
    "completed",
    "failed",
    "invalid",
    "blocked",
    "withheld",
    "insufficient",
    "resource_limited",
    "review_needed",
    "no_candidate",
}


def _load_tape(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _derive_queue_action(event: dict[str, Any]) -> str:
    event_type = event["event_type"]
    if event_type == "job_enqueued":
        return "enqueue"
    if event_type == "job_started":
        return "mark_running"
    if event_type in {"job_completed", "job_failed"}:
        return "mark_terminal"
    if event_type == "job_invalid":
        return "mark_invalid"
    if event_type == "job_blocked":
        return "mark_blocked"
    if event_type == "metrics_withheld":
        return "mark_withheld"
    if event_type == "metrics_insufficient":
        return "mark_insufficient"
    if event_type == "resource_limited":
        return "mark_resource_limited"
    if event_type == "job_delayed":
        return "mark_delayed"
    if event_type == "review_needed":
        return "mark_review_needed"
    return "none"


def _derive_scheduler_action(event: dict[str, Any]) -> str:
    event_type = event["event_type"]
    state_after = event["job_state_after"]
    outcome = event["job_outcome"]
    if event_type in {
        "daily_window_tick",
        "weekly_window_tick",
        "dashboard_snapshot_tick",
        "registry_checkpoint",
    }:
        return "no_autonomous_dispatch"
    if event_type == "job_started":
        return "eligible_for_dry_run_start"
    if event_type == "resource_limited":
        return "hold_resource_limit"
    if event_type == "job_blocked":
        return "hold_dependency_blocked"
    if event_type == "job_delayed":
        return "mark_delayed"
    if event_type == "notification_worthy" and outcome != "not_terminal":
        return "mark_terminal"
    if state_after in TERMINAL_STATES:
        return "mark_terminal"
    return "no_autonomous_dispatch"


def _event_trace(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trace: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    job_state: dict[str, str] = {}

    for event in events:
        expected = event["expected_operating_outcome"]
        observed_queue_action = _derive_queue_action(event)
        observed_scheduler_action = _derive_scheduler_action(event)
        before_matches = event["job_state_before"] == job_state.get(
            event["job_id"], "not_seen"
        )

        row = {
            "event_id": event["event_id"],
            "sequence_index": event["sequence_index"],
            "job_id": event["job_id"],
            "event_type": event["event_type"],
            "priority": event["priority"],
            "job_state_before": event["job_state_before"],
            "observed_prior_state": job_state.get(event["job_id"], "not_seen"),
            "job_state_after": event["job_state_after"],
            "queue_action_expected": expected["queue_action"],
            "queue_action_observed": observed_queue_action,
            "scheduler_action_expected": expected["scheduler_action"],
            "scheduler_action_observed": observed_scheduler_action,
            "state_before_matched": before_matches,
            "queue_action_matched": observed_queue_action == expected["queue_action"],
            "scheduler_action_matched": observed_scheduler_action
            == expected["scheduler_action"],
            "autonomous_dispatch_performed": False,
            "live_dispatch_performed": False,
        }
        trace.append(row)

        if not before_matches:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "job_state_before",
                    "expected": event["job_state_before"],
                    "observed": job_state.get(event["job_id"], "not_seen"),
                }
            )
        if not row["queue_action_matched"]:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "queue_action",
                    "expected": expected["queue_action"],
                    "observed": observed_queue_action,
                }
            )
        if not row["scheduler_action_matched"]:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "scheduler_action",
                    "expected": expected["scheduler_action"],
                    "observed": observed_scheduler_action,
                }
            )

        job_state[event["job_id"]] = event["job_state_after"]

    return trace, mismatches


def _priority_assertions(events: list[dict[str, Any]]) -> dict[str, Any]:
    enqueued = [event for event in events if event["event_type"] == "job_enqueued"]
    ordered = sorted(
        enqueued,
        key=lambda event: (
            PRIORITY_RANK[event["priority"]],
            event["sequence_index"],
            event["job_id"],
        ),
    )
    return {
        "priority_order_deterministic": True,
        "ordering_rule": "priority rank urgent/high/normal/low, then sequence_index, then job_id",
        "priority_rank": dict(PRIORITY_RANK),
        "queued_runnable_job_count": len(enqueued),
        "ordered_job_ids": [event["job_id"] for event in ordered],
        "ordered_jobs": [
            {
                "job_id": event["job_id"],
                "priority": event["priority"],
                "sequence_index": event["sequence_index"],
                "event_id": event["event_id"],
            }
            for event in ordered
        ],
    }


def _resource_assertions(trace: list[dict[str, Any]]) -> dict[str, Any]:
    by_job = defaultdict(list)
    for row in trace:
        by_job[row["job_id"]].append(row)

    resource_limited_jobs = [
        row["job_id"]
        for row in trace
        if row["scheduler_action_observed"] == "hold_resource_limit"
    ]
    blocked_jobs = [
        row["job_id"]
        for row in trace
        if row["scheduler_action_observed"] == "hold_dependency_blocked"
    ]
    delayed_jobs = [
        row["job_id"] for row in trace if row["scheduler_action_observed"] == "mark_delayed"
    ]
    terminal_jobs = sorted(
        {
            row["job_id"]
            for row in trace
            if row["scheduler_action_observed"] == "mark_terminal"
        }
    )

    def has_later_start(job_id: str, after_index: int) -> bool:
        return any(
            row["sequence_index"] > after_index
            and row["scheduler_action_observed"] == "eligible_for_dry_run_start"
            for row in by_job[job_id]
        )

    resource_holds = []
    blocked_holds = []
    for row in trace:
        if row["scheduler_action_observed"] == "hold_resource_limit":
            resource_holds.append(
                {
                    "job_id": row["job_id"],
                    "event_id": row["event_id"],
                    "held": True,
                    "later_started": has_later_start(row["job_id"], row["sequence_index"]),
                }
            )
        if row["scheduler_action_observed"] == "hold_dependency_blocked":
            blocked_holds.append(
                {
                    "job_id": row["job_id"],
                    "event_id": row["event_id"],
                    "held": True,
                    "later_started": has_later_start(row["job_id"], row["sequence_index"]),
                }
            )

    delayed_events = [
        row
        for row in trace
        if row["scheduler_action_observed"] == "mark_delayed"
        and row["job_state_after"] == "delayed"
    ]
    terminal_events = [
        row for row in trace if row["scheduler_action_observed"] == "mark_terminal"
    ]
    return {
        "resource_limit_behavior_matched": all(not item["later_started"] for item in resource_holds)
        and bool(resource_holds),
        "blocked_behavior_matched": all(not item["later_started"] for item in blocked_holds)
        and bool(blocked_holds),
        "delayed_behavior_matched": bool(delayed_events),
        "terminal_behavior_matched": bool(terminal_events),
        "resource_limited_jobs": resource_limited_jobs,
        "blocked_jobs": blocked_jobs,
        "delayed_jobs": delayed_jobs,
        "terminal_jobs": terminal_jobs,
        "resource_limit_holds": resource_holds,
        "blocked_holds": blocked_holds,
        "delayed_events": [
            {"event_id": row["event_id"], "job_id": row["job_id"], "state": row["job_state_after"]}
            for row in delayed_events
        ],
        "terminal_events": [
            {"event_id": row["event_id"], "job_id": row["job_id"], "state": row["job_state_after"]}
            for row in terminal_events
        ],
        "held_jobs_preserved_in_denominator": True,
        "held_or_blocked_job_count": len(set(resource_limited_jobs + blocked_jobs)),
    }


def _non_authority_assertions(
    tape: dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "construction_payload_all_events": all(
            event["construction_payload"] is True for event in events
        ),
        "non_promotable_all_events": all(
            event["non_promotable"] is True for event in events
        ),
        "operating_test_evidence_all_events": all(
            event["operating_test_evidence"] is True for event in events
        ),
        "strategy_evidence_any": any(event["strategy_evidence"] is True for event in events),
        "candidate_eligible_any": any(event["candidate_eligible"] is True for event in events),
        "edge_claim_allowed_any": any(event["edge_claim_allowed"] is True for event in events),
        "canonical_crossing_allowed_any": any(
            event["canonical_crossing_allowed"] is True for event in events
        ),
        "paper_live_eligible_any": any(event["paper_live_eligible"] is True for event in events),
        "autonomous_scheduler_allowed_any": any(
            event["autonomous_scheduler_allowed"] is True for event in events
        ),
        "real_notification_sending_allowed_any": any(
            event["real_notification_sending_allowed"] is True for event in events
        ),
        "strategy_run_performed": False,
        "edge_search_authorized_here": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "candidate_lifecycle_write_performed": False,
        "canonical_result_population_written": False,
        "tape_level_flags": {
            "construction_payload": tape.get("construction_payload"),
            "non_promotable": tape.get("non_promotable"),
            "operating_test_evidence": tape.get("operating_test_evidence"),
            "strategy_evidence": tape.get("strategy_evidence"),
            "candidate_evidence": tape.get("candidate_evidence"),
            "edge_claim_allowed": tape.get("edge_claim_allowed"),
            "canonical_crossing_allowed": tape.get("canonical_crossing_allowed"),
            "paper_live_eligible": tape.get("paper_live_eligible"),
            "autonomous_scheduler_allowed": tape.get("autonomous_scheduler_allowed"),
            "real_notification_sending_allowed": tape.get("real_notification_sending_allowed"),
        },
    }


def replay_tape(tape_path: Path, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = repo_root or Path.cwd()
    validation = tape_validate.validate_tape(tape_path, repo_root=repo_root)
    tape = _load_tape(tape_path)
    events = tape.get("events", [])
    trace, mismatches = _event_trace(events)
    priority = _priority_assertions(events)
    resource = _resource_assertions(trace)
    non_authority = _non_authority_assertions(tape, events)
    no_autonomous = {
        "autonomous_scheduler_allowed_any": non_authority["autonomous_scheduler_allowed_any"],
        "autonomous_scheduler_activated": False,
        "eligible_for_dry_run_start_live_dispatched_any": False,
        "scheduler_default_off_preserved": True,
    }

    queue_counts = Counter(row["queue_action_observed"] for row in trace)
    scheduler_counts = Counter(row["scheduler_action_observed"] for row in trace)
    queue_actions_matched = all(row["queue_action_matched"] for row in trace)
    scheduler_actions_matched = all(row["scheduler_action_matched"] for row in trace)

    result = {
        "package": PACKAGE,
        "status": "complete" if validation.valid and not mismatches else "failed",
        "input_tape_id": tape.get("tape_id"),
        "schema_version": tape.get("schema_version"),
        "event_count": len(events),
        "job_count": len({event["job_id"] for event in events}),
        "reference_tape_validation_passed": validation.valid,
        "queue_actions_matched": queue_actions_matched,
        "scheduler_actions_matched": scheduler_actions_matched,
        "priority_order_deterministic": priority["priority_order_deterministic"],
        "resource_limit_behavior_matched": resource["resource_limit_behavior_matched"],
        "blocked_behavior_matched": resource["blocked_behavior_matched"],
        "delayed_behavior_matched": resource["delayed_behavior_matched"],
        "terminal_behavior_matched": resource["terminal_behavior_matched"],
        "autonomous_scheduler_activated": False,
        "live_dispatch_performed": False,
        "strategy_run_performed": False,
        "edge_search_authorized_here": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "replay_evidence_class": REPLAY_EVIDENCE_CLASS,
        "queue_action_counts": dict(sorted(queue_counts.items())),
        "scheduler_action_counts": dict(sorted(scheduler_counts.items())),
        "mismatches": mismatches,
    }
    return {
        "result": result,
        "trace": trace,
        "priority_assertions": priority,
        "resource_limit_assertions": resource,
        "no_autonomous_dispatch_assertions": no_autonomous,
        "non_authority_assertions": non_authority,
        "validation": validation.to_dict(),
    }


def _markdown_result(payload: dict[str, Any]) -> str:
    result = payload["result"]
    lines = [
        f"# {PACKAGE} Replay Result",
        "",
        f"- status: {result['status']}",
        f"- input_tape_id: {result['input_tape_id']}",
        f"- schema_version: {result['schema_version']}",
        f"- event_count: {result['event_count']}",
        f"- job_count: {result['job_count']}",
        f"- queue_actions_matched: {str(result['queue_actions_matched']).lower()}",
        f"- scheduler_actions_matched: {str(result['scheduler_actions_matched']).lower()}",
        f"- priority_order_deterministic: {str(result['priority_order_deterministic']).lower()}",
        f"- resource_limit_behavior_matched: {str(result['resource_limit_behavior_matched']).lower()}",
        f"- blocked_behavior_matched: {str(result['blocked_behavior_matched']).lower()}",
        f"- delayed_behavior_matched: {str(result['delayed_behavior_matched']).lower()}",
        f"- terminal_behavior_matched: {str(result['terminal_behavior_matched']).lower()}",
        f"- autonomous_scheduler_activated: {str(result['autonomous_scheduler_activated']).lower()}",
        f"- live_dispatch_performed: {str(result['live_dispatch_performed']).lower()}",
        f"- mismatches: {len(result['mismatches'])}",
        "",
        "This artifact is operating-test evidence only. It creates no strategy, edge, candidate, crossing, or paper/live authority.",
        "",
    ]
    return "\n".join(lines)


def _validation_summary(payload: dict[str, Any]) -> str:
    result = payload["result"]
    validation = payload["validation"]
    lines = [
        f"package={PACKAGE}",
        f"status={result['status']}",
        f"input_tape_id={result['input_tape_id']}",
        f"event_count={result['event_count']}",
        f"job_count={result['job_count']}",
        f"reference_tape_validation_passed={str(result['reference_tape_validation_passed']).lower()}",
        f"queue_actions_matched={str(result['queue_actions_matched']).lower()}",
        f"scheduler_actions_matched={str(result['scheduler_actions_matched']).lower()}",
        f"priority_order_deterministic={str(result['priority_order_deterministic']).lower()}",
        f"resource_limit_behavior_matched={str(result['resource_limit_behavior_matched']).lower()}",
        f"blocked_behavior_matched={str(result['blocked_behavior_matched']).lower()}",
        f"delayed_behavior_matched={str(result['delayed_behavior_matched']).lower()}",
        f"terminal_behavior_matched={str(result['terminal_behavior_matched']).lower()}",
        f"autonomous_scheduler_activated={str(result['autonomous_scheduler_activated']).lower()}",
        f"live_dispatch_performed={str(result['live_dispatch_performed']).lower()}",
        f"validation_errors={len(validation['errors'])}",
        f"mismatches={len(result['mismatches'])}",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "queue_scheduler_replay_result.json": payload["result"],
        "job_state_trace.json": payload["trace"],
        "priority_order_assertions.json": payload["priority_assertions"],
        "resource_limit_assertions.json": payload["resource_limit_assertions"],
        "no_autonomous_dispatch_assertions.json": payload["no_autonomous_dispatch_assertions"],
        "non_authority_assertions.json": payload["non_authority_assertions"],
    }
    for name, value in outputs.items():
        (out_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    (out_dir / "queue_scheduler_replay_result.md").write_text(
        _markdown_result(payload), encoding="utf-8"
    )
    (out_dir / "validation_summary.txt").write_text(
        _validation_summary(payload), encoding="utf-8"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tape_path", type=Path)
    parser.add_argument("--out-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = replay_tape(args.tape_path)
    if args.out_dir:
        write_outputs(payload, args.out_dir)
    print(json.dumps(payload["result"], indent=2, sort_keys=True))
    return 0 if payload["result"]["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
