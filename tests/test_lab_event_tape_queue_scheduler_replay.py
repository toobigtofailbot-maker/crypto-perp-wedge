from pathlib import Path

from tools.lab_event_tape.replay_queue_scheduler import replay_tape


TAPE_PATH = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")


def test_queue_scheduler_replay_matches_reference_tape_actions() -> None:
    payload = replay_tape(TAPE_PATH)
    result = payload["result"]

    assert result["status"] == "complete"
    assert result["input_tape_id"] == "LAB-EVENT-TAPE-REFERENCE-001"
    assert result["schema_version"] == "lab_event_tape.v1"
    assert result["event_count"] == 40
    assert result["job_count"] == 10
    assert result["reference_tape_validation_passed"] is True
    assert result["queue_actions_matched"] is True
    assert result["scheduler_actions_matched"] is True
    assert result["mismatches"] == []


def test_replay_preserves_default_off_no_dispatch_invariants() -> None:
    payload = replay_tape(TAPE_PATH)
    result = payload["result"]
    no_dispatch = payload["no_autonomous_dispatch_assertions"]

    assert result["autonomous_scheduler_activated"] is False
    assert result["live_dispatch_performed"] is False
    assert no_dispatch == {
        "autonomous_scheduler_allowed_any": False,
        "autonomous_scheduler_activated": False,
        "eligible_for_dry_run_start_live_dispatched_any": False,
        "scheduler_default_off_preserved": True,
    }


def test_replay_resource_blocked_delayed_and_terminal_behavior() -> None:
    payload = replay_tape(TAPE_PATH)
    result = payload["result"]
    resource = payload["resource_limit_assertions"]

    assert result["resource_limit_behavior_matched"] is True
    assert result["blocked_behavior_matched"] is True
    assert result["delayed_behavior_matched"] is True
    assert result["terminal_behavior_matched"] is True
    assert resource["resource_limited_jobs"] == ["TAPE-JOB-0007"]
    assert resource["blocked_jobs"] == ["TAPE-JOB-0004"]
    assert "TAPE-JOB-0008" in resource["delayed_jobs"]
    assert resource["held_jobs_preserved_in_denominator"] is True
    assert all(item["later_started"] is False for item in resource["resource_limit_holds"])
    assert all(item["later_started"] is False for item in resource["blocked_holds"])


def test_replay_priority_order_is_deterministic() -> None:
    payload = replay_tape(TAPE_PATH)
    priority = payload["priority_assertions"]

    assert priority["priority_order_deterministic"] is True
    assert priority["ordered_job_ids"] == [
        "TAPE-JOB-0004",
        "TAPE-JOB-0007",
        "TAPE-JOB-0002",
        "TAPE-JOB-0006",
        "TAPE-JOB-0010",
        "TAPE-JOB-0001",
        "TAPE-JOB-0005",
        "TAPE-JOB-0009",
        "TAPE-JOB-0003",
        "TAPE-JOB-0008",
    ]


def test_replay_creates_no_strategy_candidate_or_paper_live_authority() -> None:
    payload = replay_tape(TAPE_PATH)
    non_authority = payload["non_authority_assertions"]

    assert non_authority["construction_payload_all_events"] is True
    assert non_authority["non_promotable_all_events"] is True
    assert non_authority["operating_test_evidence_all_events"] is True
    assert non_authority["strategy_evidence_any"] is False
    assert non_authority["candidate_eligible_any"] is False
    assert non_authority["edge_claim_allowed_any"] is False
    assert non_authority["canonical_crossing_allowed_any"] is False
    assert non_authority["paper_live_eligible_any"] is False
    assert non_authority["autonomous_scheduler_allowed_any"] is False
    assert non_authority["real_notification_sending_allowed_any"] is False
    assert non_authority["strategy_run_performed"] is False
    assert non_authority["candidate_authority_created"] is False
    assert non_authority["canonical_crossing_authority_created"] is False
    assert non_authority["paper_live_authority_created"] is False
