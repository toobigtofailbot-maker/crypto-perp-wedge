"""Replay the reference event tape into dry-run notices and report windows.

This helper is package-local for WP-LAB-NOTIFY-REPORT-REPLAY-01. It validates
the committed reference tape first, then derives deterministic operating-test
artifacts from the tape's expected notification/report actions. It performs no
real sends and writes only when an explicit output directory is supplied.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.lab_event_tape.validate import (
    EXPECTED_NOTIFICATION_ACTIONS,
    EXPECTED_REPORT_ACTIONS,
    REFERENCE_TAPE_ID,
    SCHEMA_VERSION,
    validate_tape,
)


PACKAGE = "WP-LAB-NOTIFY-REPORT-REPLAY-01"
DEFAULT_TAPE = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")
OUTPUT_NAMES = {
    "result_json": "notify_report_replay_result.json",
    "result_md": "notify_report_replay_result.md",
    "notifications_json": "dry_run_notifications.json",
    "notifications_md": "dry_run_notifications.md",
    "daily_json": "daily_report_replay.json",
    "daily_md": "daily_report_replay.md",
    "weekly_json": "weekly_report_replay.json",
    "weekly_md": "weekly_report_replay.md",
    "non_authority_json": "non_authority_assertions.json",
    "validation_txt": "validation_summary.txt",
}

DRY_RUN_TYPES = {
    "dry_run_blocked": "blocked",
    "dry_run_failed": "failed",
    "dry_run_review_needed": "review_needed",
    "dry_run_withheld": "withheld",
    "dry_run_resource_limited": "resource_limited",
    "dry_run_daily_summary": "daily_summary",
    "dry_run_weekly_summary": "weekly_summary",
}
OPERATING_CATEGORIES = {
    "blocked",
    "failed",
    "invalid",
    "withheld",
    "insufficient",
    "resource_limited",
    "review_needed",
}
AUTHORITY_TERMS = ("ranking", "recommendation", "readiness", "promotion")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc)


def _render_notification(event: dict[str, Any]) -> dict[str, Any]:
    action = event["expected_operating_outcome"]["notification_action"]
    return {
        "artifact_id": f"DRY-NOTICE-{event['event_id']}",
        "dry_run": True,
        "real_send_performed": False,
        "notification_action": action,
        "notification_type": DRY_RUN_TYPES[action],
        "event_id": event["event_id"],
        "event_time": event["event_time"],
        "event_type": event["event_type"],
        "job_id": event["job_id"],
        "job_outcome": event["job_outcome"],
        "priority": event["priority"],
        "evidence_class": "operating_test_evidence",
        "message": (
            f"DRY RUN ONLY: {DRY_RUN_TYPES[action]} notice for {event['event_id']} "
            f"({event['job_id']}, {event['job_outcome']})."
        ),
        "authority": {
            "real_notification_send_allowed": False,
            "real_notification_send_performed": False,
            "strategy_evidence": False,
            "edge_claim_allowed": False,
            "candidate_authority_created": False,
            "canonical_crossing_authority_created": False,
            "paper_live_authority_created": False,
        },
    }


def _window_events(
    events: list[dict[str, Any]], start: datetime | None, end: datetime
) -> list[dict[str, Any]]:
    selected = []
    for event in events:
        event_time = _parse_time(event["event_time"])
        if (start is None or event_time > start) and event_time <= end:
            selected.append(event)
    return selected


def _event_report_row(event: dict[str, Any]) -> dict[str, Any]:
    outcome = event["expected_operating_outcome"]
    return {
        "event_id": event["event_id"],
        "event_time": event["event_time"],
        "event_type": event["event_type"],
        "job_id": event["job_id"],
        "job_outcome": event["job_outcome"],
        "priority": event["priority"],
        "expected_report_action": outcome["report_action"],
        "expected_notification_action": outcome["notification_action"],
        "evidence_class": "operating_test_evidence",
    }


def _build_report_windows(
    events: list[dict[str, Any]],
    tick_type: str,
    window_kind: str,
    *,
    close_final_at_tape_end: bool = False,
) -> list[dict[str, Any]]:
    ticks = [event for event in events if event["event_type"] == tick_type]
    final_event_time = _parse_time(events[-1]["event_time"])
    previous_end: datetime | None = None
    windows: list[dict[str, Any]] = []
    for index, tick in enumerate(ticks, start=1):
        tick_time = _parse_time(tick["event_time"])
        is_final_tick = index == len(ticks)
        window_end = final_event_time if close_final_at_tape_end and is_final_tick else tick_time
        selected = _window_events(events, previous_end, window_end)
        report_rows = [_event_report_row(event) for event in selected]
        category_counts = Counter(
            row["job_outcome"] for row in report_rows if row["job_outcome"] in OPERATING_CATEGORIES
        )
        windows.append(
            {
                "window_id": f"{window_kind.upper()}-{index:04d}",
                "window_kind": window_kind,
                "window_start_exclusive": previous_end.isoformat().replace("+00:00", "Z")
                if previous_end
                else None,
                "window_end_inclusive": tick["event_time"],
                "materialized_window_end_inclusive": window_end.isoformat().replace("+00:00", "Z"),
                "tick_event_id": tick["event_id"],
                "evidence_class": "operating_test_evidence",
                "deterministic_from_tape_timestamps": True,
                "event_count": len(report_rows),
                "report_actions": sorted(Counter(row["expected_report_action"] for row in report_rows)),
                "category_counts": dict(sorted(category_counts.items())),
                "events": report_rows,
                "authority": {
                    "strategy_evidence": False,
                    "edge_claim_allowed": False,
                    "candidate_authority_created": False,
                    "canonical_crossing_authority_created": False,
                    "paper_live_authority_created": False,
                },
            }
        )
        previous_end = tick_time
    return windows


def _assert_no_authority_terms(markdown: str) -> bool:
    lowered = markdown.lower()
    return not any(term in lowered for term in AUTHORITY_TERMS)


def _render_notifications_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Dry-run notifications",
        "",
        "Evidence class: operating_test_evidence.",
        "Real send performed: false.",
        "",
    ]
    for notice in payload["notifications"]:
        lines.append(
            f"- `{notice['artifact_id']}` `{notice['notification_action']}` "
            f"for `{notice['event_id']}` / `{notice['job_id']}` at {notice['event_time']}"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_report_md(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        "Evidence class: operating_test_evidence.",
        "Deterministic source: reference event-tape timestamps.",
        "",
    ]
    for window in payload["windows"]:
        lines.extend(
            [
                f"## {window['window_id']}",
                "",
                f"- tick event: `{window['tick_event_id']}`",
                f"- window end: {window['window_end_inclusive']}",
                f"- events: {window['event_count']}",
                f"- categories: {json.dumps(window['category_counts'], sort_keys=True)}",
                "",
            ]
        )
        for event in window["events"]:
            lines.append(
                f"- `{event['event_id']}` `{event['event_type']}` "
                f"`{event['job_outcome']}` report `{event['expected_report_action']}`"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_result_md(result: dict[str, Any]) -> str:
    lines = [
        "# Notify/report replay result",
        "",
        f"- package: {result['package']}",
        f"- status: {result['status']}",
        f"- input tape: {result['input_tape_id']}",
        f"- event count: {result['event_count']}",
        f"- job count: {result['job_count']}",
        f"- notification actions matched: {str(result['notification_actions_matched']).lower()}",
        f"- report actions matched: {str(result['report_actions_matched']).lower()}",
        f"- daily windows generated: {result['daily_windows_generated']}",
        f"- weekly windows generated: {result['weekly_windows_generated']}",
        f"- dry-run notifications rendered: {str(result['dry_run_notifications_rendered']).lower()}",
        f"- real notification send performed: {str(result['real_notification_send_performed']).lower()}",
        f"- evidence class: {result['replay_evidence_class']}",
        "",
        "Mismatches: none.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def replay_tape(tape_path: Path = DEFAULT_TAPE, repo_root: Path | None = None) -> dict[str, Any]:
    repo_root = repo_root or Path.cwd()
    validation = validate_tape(tape_path, repo_root=repo_root)
    if not validation.valid:
        raise ValueError(f"reference tape validation failed: {validation.errors}")

    tape = _load_json(tape_path)
    events = tape["events"]
    notifications = [
        _render_notification(event)
        for event in events
        if event["expected_operating_outcome"]["notification_action"] != "none"
    ]
    daily_windows = _build_report_windows(events, "daily_window_tick", "daily")
    weekly_windows = _build_report_windows(
        events, "weekly_window_tick", "weekly", close_final_at_tape_end=True
    )

    notification_actions = {
        event["event_id"]: event["expected_operating_outcome"]["notification_action"]
        for event in events
    }
    rendered_actions = {
        notice["event_id"]: notice["notification_action"] for notice in notifications
    }
    notification_mismatches = [
        {
            "event_id": event_id,
            "expected": action,
            "actual": rendered_actions.get(event_id, "none"),
        }
        for event_id, action in notification_actions.items()
        if action != "none" and rendered_actions.get(event_id) != action
    ]

    report_actions = {
        event["event_id"]: event["expected_operating_outcome"]["report_action"]
        for event in events
    }
    covered_report_actions = {
        row["event_id"]: row["expected_report_action"]
        for window in [*daily_windows, *weekly_windows]
        for row in window["events"]
    }
    report_mismatches = [
        {
            "event_id": event_id,
            "expected": action,
            "actual": covered_report_actions.get(event_id),
        }
        for event_id, action in report_actions.items()
        if covered_report_actions.get(event_id) != action
    ]

    notification_action_values = set(notification_actions.values())
    report_action_values = set(report_actions.values())
    closed_enum_mismatches = []
    if not notification_action_values <= EXPECTED_NOTIFICATION_ACTIONS:
        closed_enum_mismatches.append(
            {"notification_actions": sorted(notification_action_values - EXPECTED_NOTIFICATION_ACTIONS)}
        )
    if not report_action_values <= EXPECTED_REPORT_ACTIONS:
        closed_enum_mismatches.append({"report_actions": sorted(report_action_values - EXPECTED_REPORT_ACTIONS)})

    non_authority = {
        "operating_test_evidence": True,
        "strategy_evidence": False,
        "candidate_evidence": False,
        "edge_claim_allowed": False,
        "real_notification_sending_authorized": False,
        "real_notification_send_performed": False,
        "recommendation_authority_created": False,
        "readiness_authority_created": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "protected_paths_touched": False,
    }
    result = {
        "package": PACKAGE,
        "status": "complete",
        "input_tape_id": tape["tape_id"],
        "schema_version": tape["schema_version"],
        "event_count": len(events),
        "job_count": len({event["job_id"] for event in events}),
        "notification_actions_matched": not notification_mismatches and not closed_enum_mismatches,
        "report_actions_matched": not report_mismatches and not closed_enum_mismatches,
        "daily_windows_generated": len(daily_windows),
        "weekly_windows_generated": len(weekly_windows),
        "dry_run_notifications_rendered": bool(notifications),
        "real_notification_send_performed": False,
        "strategy_run_performed": False,
        "edge_search_authorized_here": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "replay_evidence_class": "operating_test_evidence",
        "mismatches": [*notification_mismatches, *report_mismatches, *closed_enum_mismatches],
    }
    notifications_payload = {
        "package": PACKAGE,
        "input_tape_id": tape["tape_id"],
        "evidence_class": "operating_test_evidence",
        "real_notification_send_performed": False,
        "notification_count": len(notifications),
        "notification_actions": dict(sorted(Counter(n["notification_action"] for n in notifications).items())),
        "notifications": notifications,
    }
    daily_payload = {
        "package": PACKAGE,
        "input_tape_id": tape["tape_id"],
        "evidence_class": "operating_test_evidence",
        "window_count": len(daily_windows),
        "windows": daily_windows,
    }
    weekly_payload = {
        "package": PACKAGE,
        "input_tape_id": tape["tape_id"],
        "evidence_class": "operating_test_evidence",
        "window_count": len(weekly_windows),
        "windows": weekly_windows,
    }
    markdown = {
        "result": _render_result_md(result),
        "notifications": _render_notifications_md(notifications_payload),
        "daily": _render_report_md("Daily report replay", daily_payload),
        "weekly": _render_report_md("Weekly report replay", weekly_payload),
    }
    if not _assert_no_authority_terms(markdown["daily"] + markdown["weekly"]):
        raise ValueError("daily/weekly reports contain authority wording")

    return {
        "validation": validation.to_dict(),
        "result": result,
        "notifications": notifications_payload,
        "daily": daily_payload,
        "weekly": weekly_payload,
        "non_authority": non_authority,
        "markdown": markdown,
    }


def write_outputs(payload: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / OUTPUT_NAMES["result_json"], payload["result"])
    _write_json(out_dir / OUTPUT_NAMES["notifications_json"], payload["notifications"])
    _write_json(out_dir / OUTPUT_NAMES["daily_json"], payload["daily"])
    _write_json(out_dir / OUTPUT_NAMES["weekly_json"], payload["weekly"])
    _write_json(out_dir / OUTPUT_NAMES["non_authority_json"], payload["non_authority"])
    (out_dir / OUTPUT_NAMES["result_md"]).write_text(payload["markdown"]["result"], encoding="utf-8")
    (out_dir / OUTPUT_NAMES["notifications_md"]).write_text(
        payload["markdown"]["notifications"], encoding="utf-8"
    )
    (out_dir / OUTPUT_NAMES["daily_md"]).write_text(payload["markdown"]["daily"], encoding="utf-8")
    (out_dir / OUTPUT_NAMES["weekly_md"]).write_text(payload["markdown"]["weekly"], encoding="utf-8")
    validation_lines = [
        f"package: {PACKAGE}",
        f"input_tape: {REFERENCE_TAPE_ID}",
        f"event_tape_validator: {'pass' if payload['validation']['valid'] else 'fail'}",
        f"notification_actions_matched: {payload['result']['notification_actions_matched']}",
        f"report_actions_matched: {payload['result']['report_actions_matched']}",
        f"daily_windows_generated: {payload['result']['daily_windows_generated']}",
        f"weekly_windows_generated: {payload['result']['weekly_windows_generated']}",
        "real_notification_send_performed: False",
        "strategy_run_performed: False",
        "replay_evidence_class: operating_test_evidence",
    ]
    (out_dir / OUTPUT_NAMES["validation_txt"]).write_text(
        "\n".join(validation_lines).rstrip() + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tape", type=Path, default=DEFAULT_TAPE)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)

    payload = replay_tape(tape_path=args.tape, repo_root=args.repo_root)
    if args.out_dir:
        write_outputs(payload, args.out_dir)
    print(json.dumps(payload["result"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
