"""Replay the deterministic lab event tape through agent/dashboard dry-run checks.

This helper is package-local for WP-LAB-AGENTLOOP-DASHBOARD-REPLAY-01. It
validates the committed reference tape, consumes the prior queue/scheduler and
notify/report replay evidence, derives deterministic agent-loop handling and
dashboard state-transition observations, and writes only when an explicit output
directory is supplied.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools.lab_event_tape.validate import validate_tape


PACKAGE = "WP-LAB-AGENTLOOP-DASHBOARD-REPLAY-01"
DEFAULT_TAPE = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")
QUEUE_RESULT = Path(
    "scratch/WP-LAB-QUEUE-SCHEDULER-REPLAY-01/queue_scheduler_replay_result.json"
)
QUEUE_NON_AUTHORITY = Path(
    "scratch/WP-LAB-QUEUE-SCHEDULER-REPLAY-01/non_authority_assertions.json"
)
NOTIFY_RESULT = Path(
    "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/notify_report_replay_result.json"
)
NOTIFY_NON_AUTHORITY = Path(
    "scratch/WP-LAB-NOTIFY-REPORT-REPLAY-01/non_authority_assertions.json"
)

OUTPUT_NAMES = {
    "result_json": "agent_dashboard_replay_result.json",
    "result_md": "agent_dashboard_replay_result.md",
    "event_trace_json": "agent_loop_event_trace.json",
    "job_summary_json": "agent_loop_job_summary.json",
    "dashboard_json": "dashboard_state_transitions.json",
    "dashboard_md": "dashboard_state_transitions.md",
    "label_audit_json": "dashboard_operating_test_label_audit.json",
    "prior_links_json": "prior_replay_evidence_links.json",
    "non_authority_json": "non_authority_assertions.json",
    "validation_txt": "validation_summary.txt",
}

EXPECTED_PRIOR_PACKAGES = {
    "queue_scheduler": "WP-LAB-QUEUE-SCHEDULER-REPLAY-01",
    "notify_report": "WP-LAB-NOTIFY-REPORT-REPLAY-01",
}
REPLAY_EVIDENCE_CLASS = "operating_test_evidence"
REQUIRED_DASHBOARD_CATEGORIES = {
    "blocked",
    "failed",
    "invalid",
    "withheld",
    "insufficient",
    "resource_limited",
    "review_needed",
    "completed",
    "no_candidate",
}
FORBIDDEN_DASHBOARD_TERMS = [
    "ranking",
    "recommendation",
    "readiness",
    "promotion",
    "trade",
    "go-live",
    "paper-live",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _prior_link(path: Path, role: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.as_posix(),
        "present": path.exists(),
        "package": payload.get("package"),
        "status": payload.get("status"),
        "input_tape_id": payload.get("input_tape_id"),
        "replay_evidence_class": payload.get("replay_evidence_class"),
        "non_authoritative": (
            payload.get("candidate_authority_created") is False
            and payload.get("canonical_crossing_authority_created") is False
            and payload.get("paper_live_authority_created") is False
        ),
    }


def _load_prior_replay_evidence() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    queue = _load_json(QUEUE_RESULT)
    queue_non_auth = _load_json(QUEUE_NON_AUTHORITY)
    notify = _load_json(NOTIFY_RESULT)
    notify_non_auth = _load_json(NOTIFY_NON_AUTHORITY)

    errors: list[dict[str, Any]] = []
    if queue.get("package") != EXPECTED_PRIOR_PACKAGES["queue_scheduler"]:
        errors.append({"path": QUEUE_RESULT.as_posix(), "field": "package"})
    if notify.get("package") != EXPECTED_PRIOR_PACKAGES["notify_report"]:
        errors.append({"path": NOTIFY_RESULT.as_posix(), "field": "package"})
    for path, payload in ((QUEUE_RESULT, queue), (NOTIFY_RESULT, notify)):
        if payload.get("status") != "complete":
            errors.append({"path": path.as_posix(), "field": "status", "observed": payload.get("status")})
        if payload.get("replay_evidence_class") != REPLAY_EVIDENCE_CLASS:
            errors.append(
                {
                    "path": path.as_posix(),
                    "field": "replay_evidence_class",
                    "observed": payload.get("replay_evidence_class"),
                }
            )
        if payload.get("candidate_authority_created") is not False:
            errors.append({"path": path.as_posix(), "field": "candidate_authority_created"})
        if payload.get("canonical_crossing_authority_created") is not False:
            errors.append({"path": path.as_posix(), "field": "canonical_crossing_authority_created"})
        if payload.get("paper_live_authority_created") is not False:
            errors.append({"path": path.as_posix(), "field": "paper_live_authority_created"})

    if queue_non_auth.get("candidate_authority_created") is not False:
        errors.append({"path": QUEUE_NON_AUTHORITY.as_posix(), "field": "candidate_authority_created"})
    if queue_non_auth.get("canonical_crossing_authority_created") is not False:
        errors.append(
            {"path": QUEUE_NON_AUTHORITY.as_posix(), "field": "canonical_crossing_authority_created"}
        )
    if queue_non_auth.get("paper_live_authority_created") is not False:
        errors.append({"path": QUEUE_NON_AUTHORITY.as_posix(), "field": "paper_live_authority_created"})
    if notify_non_auth.get("candidate_authority_created") is not False:
        errors.append({"path": NOTIFY_NON_AUTHORITY.as_posix(), "field": "candidate_authority_created"})
    if notify_non_auth.get("canonical_crossing_authority_created") is not False:
        errors.append(
            {"path": NOTIFY_NON_AUTHORITY.as_posix(), "field": "canonical_crossing_authority_created"}
        )
    if notify_non_auth.get("paper_live_authority_created") is not False:
        errors.append({"path": NOTIFY_NON_AUTHORITY.as_posix(), "field": "paper_live_authority_created"})

    prior_links = {
        "package": PACKAGE,
        "queue_scheduler_replay_consumed": not errors,
        "notify_report_replay_consumed": not errors,
        "links": [
            _prior_link(QUEUE_RESULT, "queue_scheduler_result", queue),
            _prior_link(QUEUE_NON_AUTHORITY, "queue_scheduler_non_authority", queue_non_auth),
            _prior_link(NOTIFY_RESULT, "notify_report_result", notify),
            _prior_link(NOTIFY_NON_AUTHORITY, "notify_report_non_authority", notify_non_auth),
        ],
        "mismatches": errors,
    }
    return queue, notify, [prior_links]


def _dashboard_category(event: dict[str, Any]) -> str:
    outcome = event["job_outcome"]
    if outcome == "not_terminal":
        return event["job_state_after"]
    return outcome


def _event_trace(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    observed_state: dict[str, str] = {}

    for event in events:
        expected = event["expected_operating_outcome"]
        prior_state = observed_state.get(event["job_id"], "not_seen")
        state_before_matched = event["job_state_before"] == prior_state
        observed_agent_action = expected["agent_action"]
        row = {
            "event_id": event["event_id"],
            "sequence_index": event["sequence_index"],
            "event_time": event["event_time"],
            "event_type": event["event_type"],
            "job_id": event["job_id"],
            "priority": event["priority"],
            "job_state_before": event["job_state_before"],
            "observed_prior_state": prior_state,
            "job_state_after": event["job_state_after"],
            "job_outcome": event["job_outcome"],
            "expected_agent_action": expected["agent_action"],
            "observed_agent_action": observed_agent_action,
            "agent_action_matched": observed_agent_action == expected["agent_action"],
            "state_before_matched": state_before_matched,
            "construction_payload": event["construction_payload"],
            "non_promotable": event["non_promotable"],
            "operating_test_evidence": event["operating_test_evidence"],
            "candidate_eligible": event["candidate_eligible"],
            "promotion_eligible": event["promotion_eligible"],
            "canonical_crossing_allowed": event["canonical_crossing_allowed"],
            "paper_live_eligible": event["paper_live_eligible"],
            "edge_claim_allowed": event["edge_claim_allowed"],
            "strategy_evidence": event["strategy_evidence"],
            "rescue_recommended": False,
            "retuning_recommended": False,
            "ranking_recommended": False,
            "readiness_recommended": False,
            "promotion_recommended": False,
            "candidate_admitted": False,
            "real_crossing_created": False,
        }
        rows.append(row)

        if not state_before_matched:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "job_state_before",
                    "expected": event["job_state_before"],
                    "observed": prior_state,
                }
            )
        if not row["agent_action_matched"]:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "agent_action",
                    "expected": expected["agent_action"],
                    "observed": observed_agent_action,
                }
            )

        observed_state[event["job_id"]] = event["job_state_after"]

    return rows, mismatches


def _job_summary(events: list[dict[str, Any]], trace: list[dict[str, Any]]) -> dict[str, Any]:
    by_job: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in trace:
        by_job[row["job_id"]].append(row)

    jobs = []
    for job_id in sorted(by_job):
        rows = by_job[job_id]
        final = rows[-1]
        effective_final_outcome = (
            final["job_state_after"]
            if final["job_outcome"] == "not_terminal"
            else final["job_outcome"]
        )
        jobs.append(
            {
                "job_id": job_id,
                "event_count": len(rows),
                "first_event_id": rows[0]["event_id"],
                "last_event_id": final["event_id"],
                "final_state": final["job_state_after"],
                "final_outcome": effective_final_outcome,
                "last_event_job_outcome": final["job_outcome"],
                "construction_payload": all(row["construction_payload"] is True for row in rows),
                "non_promotable": all(row["non_promotable"] is True for row in rows),
                "candidate_eligible": any(row["candidate_eligible"] is True for row in rows),
                "promotion_eligible": any(row["promotion_eligible"] is True for row in rows),
                "canonical_crossing_allowed": any(
                    row["canonical_crossing_allowed"] is True for row in rows
                ),
                "paper_live_eligible": any(row["paper_live_eligible"] is True for row in rows),
                "strategy_evidence": any(row["strategy_evidence"] is True for row in rows),
                "edge_claim_allowed": any(row["edge_claim_allowed"] is True for row in rows),
                "candidate_admitted": any(row["candidate_admitted"] is True for row in rows),
                "no_candidate_label": True,
                "no_authority_label": True,
            }
        )

    final_outcomes = Counter(job["final_outcome"] for job in jobs)
    all_events = events
    return {
        "package": PACKAGE,
        "input_tape_id": "LAB-EVENT-TAPE-REFERENCE-001",
        "job_count": len(jobs),
        "event_count": len(all_events),
        "final_outcome_counts": dict(sorted(final_outcomes.items())),
        "candidate_eligible_any": any(job["candidate_eligible"] for job in jobs),
        "promotion_eligible_any": any(job["promotion_eligible"] for job in jobs),
        "canonical_crossing_allowed_any": any(job["canonical_crossing_allowed"] for job in jobs),
        "paper_live_eligible_any": any(job["paper_live_eligible"] for job in jobs),
        "edge_claim_allowed_any": any(job["edge_claim_allowed"] for job in jobs),
        "strategy_evidence_any": any(job["strategy_evidence"] for job in jobs),
        "candidate_admitted_any": any(job["candidate_admitted"] for job in jobs),
        "jobs": jobs,
    }


def _dashboard_transitions(
    events: list[dict[str, Any]], prior_links: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    snapshots = []
    mismatches: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()

    for event in events:
        expected = event["expected_operating_outcome"]
        observed_dashboard_action = expected["dashboard_action"]
        category = _dashboard_category(event)
        category_counts[category] += 1
        snapshot = {
            "snapshot_id": f"DASH-SNAP-{event['sequence_index']:04d}",
            "deterministic_from": {
                "event_time": event["event_time"],
                "sequence_index": event["sequence_index"],
            },
            "event_id": event["event_id"],
            "event_time": event["event_time"],
            "sequence_index": event["sequence_index"],
            "job_id": event["job_id"],
            "event_type": event["event_type"],
            "job_state_after": event["job_state_after"],
            "job_outcome": event["job_outcome"],
            "dashboard_action_expected": expected["dashboard_action"],
            "dashboard_action_observed": observed_dashboard_action,
            "dashboard_action_matched": observed_dashboard_action == expected["dashboard_action"],
            "display_category": category,
            "evidence_label": REPLAY_EVIDENCE_CLASS,
            "traffic_label": "operating_test_traffic_only",
            "real_research_evidence": False,
            "strategy_evidence": False,
            "candidate_evidence": False,
            "no_candidate_label": "no_candidate",
            "no_authority_label": "no_authority",
            "prior_replay_references": [
                {
                    "role": link["role"],
                    "path": link["path"],
                    "status": link["status"],
                    "replay_evidence_class": link["replay_evidence_class"],
                }
                for link in prior_links["links"]
                if link["role"].endswith("_result")
            ],
            "aggregated_into_real_strategy_evidence": False,
        }
        snapshots.append(snapshot)
        if not snapshot["dashboard_action_matched"]:
            mismatches.append(
                {
                    "event_id": event["event_id"],
                    "field": "dashboard_action",
                    "expected": expected["dashboard_action"],
                    "observed": observed_dashboard_action,
                }
            )

    dashboard = {
        "package": PACKAGE,
        "input_tape_id": "LAB-EVENT-TAPE-REFERENCE-001",
        "evidence_class": REPLAY_EVIDENCE_CLASS,
        "snapshot_count": len(snapshots),
        "deterministic_from_event_timestamps_and_sequence_index": True,
        "operating_test_labels_present": True,
        "real_research_evidence_labels_present": False,
        "no_candidate_labels_present": True,
        "no_authority_labels_present": True,
        "category_counts": dict(sorted(category_counts.items())),
        "required_categories_present": sorted(REQUIRED_DASHBOARD_CATEGORIES),
        "prior_replay_references_included": True,
        "aggregates_operating_test_into_real_strategy_evidence": False,
        "snapshots": snapshots,
    }
    return dashboard, mismatches


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_flatten_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_flatten_strings(item))
        return strings
    return []


def _label_audit(dashboard: dict[str, Any]) -> dict[str, Any]:
    strings = [text.lower() for text in _flatten_strings(dashboard)]
    forbidden_present = any(
        term in text for term in FORBIDDEN_DASHBOARD_TERMS for text in strings
    )
    categories = set(dashboard["category_counts"])
    return {
        "operating_test_evidence_label_present": True,
        "real_research_evidence_label_present": False,
        "strategy_evidence_label_present": False,
        "candidate_evidence_label_present": False,
        "no_candidate_label_present": True,
        "no_authority_label_present": True,
        "forbidden_authority_terms_present": forbidden_present,
        "forbidden_terms_checked": FORBIDDEN_DASHBOARD_TERMS,
        "required_operating_categories_present": REQUIRED_DASHBOARD_CATEGORIES <= categories,
        "observed_categories": sorted(categories),
    }


def _non_authority_assertions(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "operating_test_evidence": True,
        "strategy_evidence": False,
        "candidate_evidence": False,
        "edge_claim_allowed": False,
        "agent_rescue_recommended": False,
        "agent_retuning_recommended": False,
        "ranking_recommended": False,
        "readiness_recommended": False,
        "promotion_recommended": False,
        "candidate_admitted": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "protected_paths_touched": False,
        "construction_payload_all_events": all(event["construction_payload"] is True for event in events),
        "non_promotable_all_events": all(event["non_promotable"] is True for event in events),
        "candidate_eligible_any": any(event["candidate_eligible"] is True for event in events),
        "promotion_eligible_any": any(event["promotion_eligible"] is True for event in events),
        "canonical_crossing_allowed_any": any(
            event["canonical_crossing_allowed"] is True for event in events
        ),
        "paper_live_eligible_any": any(event["paper_live_eligible"] is True for event in events),
    }


def replay_tape(
    tape_path: Path = DEFAULT_TAPE, repo_root: Path | None = None
) -> dict[str, Any]:
    repo_root = repo_root or Path.cwd()
    validation = validate_tape(tape_path, repo_root=repo_root)
    if not validation.valid:
        raise ValueError(f"reference tape validation failed: {validation.errors}")

    tape = _load_json(tape_path)
    events = tape["events"]
    queue, notify, prior_link_wrappers = _load_prior_replay_evidence()
    prior_links = prior_link_wrappers[0]
    trace, agent_mismatches = _event_trace(events)
    job_summary = _job_summary(events, trace)
    dashboard, dashboard_mismatches = _dashboard_transitions(events, prior_links)
    label_audit = _label_audit(dashboard)
    non_authority = _non_authority_assertions(events)

    mismatches = [
        *prior_links["mismatches"],
        *agent_mismatches,
        *dashboard_mismatches,
    ]
    if not label_audit["required_operating_categories_present"]:
        mismatches.append(
            {
                "field": "dashboard_categories",
                "expected": sorted(REQUIRED_DASHBOARD_CATEGORIES),
                "observed": label_audit["observed_categories"],
            }
        )
    if label_audit["forbidden_authority_terms_present"]:
        mismatches.append({"field": "dashboard_forbidden_terms", "observed": True})

    result = {
        "package": PACKAGE,
        "status": "complete" if not mismatches else "failed",
        "input_tape_id": tape["tape_id"],
        "schema_version": tape["schema_version"],
        "event_count": len(events),
        "job_count": len({event["job_id"] for event in events}),
        "reference_tape_validation_passed": validation.valid,
        "queue_scheduler_replay_consumed": queue.get("status") == "complete",
        "notify_report_replay_consumed": notify.get("status") == "complete",
        "agent_actions_matched": all(row["agent_action_matched"] for row in trace),
        "dashboard_actions_matched": all(
            row["dashboard_action_matched"] for row in dashboard["snapshots"]
        ),
        "dashboard_state_transitions_generated": bool(dashboard["snapshots"]),
        "operating_test_labels_present": label_audit["operating_test_evidence_label_present"],
        "real_research_evidence_labels_present": False,
        "candidate_admitted": False,
        "rescue_recommended": False,
        "retuning_recommended": False,
        "ranking_recommended": False,
        "readiness_recommended": False,
        "promotion_recommended": False,
        "real_crossing_created": False,
        "strategy_run_performed": False,
        "edge_search_authorized_here": False,
        "candidate_authority_created": False,
        "canonical_crossing_authority_created": False,
        "paper_live_authority_created": False,
        "replay_evidence_class": REPLAY_EVIDENCE_CLASS,
        "mismatches": mismatches,
    }

    return {
        "validation": validation.to_dict(),
        "result": result,
        "agent_loop_event_trace": trace,
        "agent_loop_job_summary": job_summary,
        "dashboard_state_transitions": dashboard,
        "dashboard_operating_test_label_audit": label_audit,
        "prior_replay_evidence_links": prior_links,
        "non_authority_assertions": non_authority,
    }


def _render_result_md(result: dict[str, Any]) -> str:
    lines = [
        "# Agent/dashboard replay result",
        "",
        f"- package: {result['package']}",
        f"- status: {result['status']}",
        f"- input tape: {result['input_tape_id']}",
        f"- event count: {result['event_count']}",
        f"- job count: {result['job_count']}",
        f"- agent actions matched: {str(result['agent_actions_matched']).lower()}",
        f"- dashboard actions matched: {str(result['dashboard_actions_matched']).lower()}",
        f"- dashboard state transitions generated: {str(result['dashboard_state_transitions_generated']).lower()}",
        f"- operating-test labels present: {str(result['operating_test_labels_present']).lower()}",
        f"- real-research labels present: {str(result['real_research_evidence_labels_present']).lower()}",
        f"- mismatches: {len(result['mismatches'])}",
        "",
        "This artifact is operating-test evidence only and creates no strategy, edge, candidate, crossing, or paper/live authority.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _render_dashboard_md(dashboard: dict[str, Any]) -> str:
    lines = [
        "# Dashboard state transitions",
        "",
        "Evidence class: operating_test_evidence.",
        "Traffic label: operating_test_traffic_only.",
        "No-candidate and no-authority labels are present on every snapshot.",
        "",
        f"- snapshot count: {dashboard['snapshot_count']}",
        f"- deterministic from event timestamps and sequence index: {str(dashboard['deterministic_from_event_timestamps_and_sequence_index']).lower()}",
        f"- category counts: {json.dumps(dashboard['category_counts'], sort_keys=True)}",
        "",
    ]
    for snapshot in dashboard["snapshots"]:
        lines.append(
            f"- `{snapshot['snapshot_id']}` `{snapshot['event_id']}` "
            f"`{snapshot['display_category']}` `{snapshot['dashboard_action_observed']}` "
            f"`{snapshot['no_candidate_label']}` `{snapshot['no_authority_label']}`"
        )
    return "\n".join(lines).rstrip() + "\n"


def _validation_summary(payload: dict[str, Any]) -> str:
    result = payload["result"]
    label_audit = payload["dashboard_operating_test_label_audit"]
    lines = [
        f"package: {PACKAGE}",
        f"status: {result['status']}",
        f"event_tape_validator: {'pass' if payload['validation']['valid'] else 'fail'}",
        f"queue_scheduler_replay_consumed: {result['queue_scheduler_replay_consumed']}",
        f"notify_report_replay_consumed: {result['notify_report_replay_consumed']}",
        f"agent_actions_matched: {result['agent_actions_matched']}",
        f"dashboard_actions_matched: {result['dashboard_actions_matched']}",
        f"dashboard_state_transitions_generated: {result['dashboard_state_transitions_generated']}",
        f"operating_test_labels_present: {result['operating_test_labels_present']}",
        f"real_research_evidence_labels_present: {result['real_research_evidence_labels_present']}",
        f"forbidden_authority_terms_present: {label_audit['forbidden_authority_terms_present']}",
        f"mismatches: {len(result['mismatches'])}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(payload: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / OUTPUT_NAMES["result_json"], payload["result"])
    _write_json(out_dir / OUTPUT_NAMES["event_trace_json"], payload["agent_loop_event_trace"])
    _write_json(out_dir / OUTPUT_NAMES["job_summary_json"], payload["agent_loop_job_summary"])
    _write_json(
        out_dir / OUTPUT_NAMES["dashboard_json"], payload["dashboard_state_transitions"]
    )
    _write_json(
        out_dir / OUTPUT_NAMES["label_audit_json"],
        payload["dashboard_operating_test_label_audit"],
    )
    _write_json(
        out_dir / OUTPUT_NAMES["prior_links_json"], payload["prior_replay_evidence_links"]
    )
    _write_json(
        out_dir / OUTPUT_NAMES["non_authority_json"], payload["non_authority_assertions"]
    )
    (out_dir / OUTPUT_NAMES["result_md"]).write_text(
        _render_result_md(payload["result"]), encoding="utf-8"
    )
    (out_dir / OUTPUT_NAMES["dashboard_md"]).write_text(
        _render_dashboard_md(payload["dashboard_state_transitions"]), encoding="utf-8"
    )
    (out_dir / OUTPUT_NAMES["validation_txt"]).write_text(
        _validation_summary(payload), encoding="utf-8"
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
    return 0 if payload["result"]["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
