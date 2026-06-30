from pathlib import Path

from tools.lab_event_tape.replay_notify_report import replay_tape, write_outputs


REFERENCE_TAPE = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")


def test_notify_report_replay_matches_expected_actions():
    replay = replay_tape(REFERENCE_TAPE)
    result = replay["result"]

    assert result["input_tape_id"] == "LAB-EVENT-TAPE-REFERENCE-001"
    assert result["schema_version"] == "lab_event_tape.v1"
    assert result["event_count"] == 40
    assert result["job_count"] == 10
    assert result["notification_actions_matched"] is True
    assert result["report_actions_matched"] is True
    assert result["daily_windows_generated"] == 2
    assert result["weekly_windows_generated"] == 1
    assert result["mismatches"] == []


def test_dry_run_notifications_cover_expected_types_without_real_send():
    replay = replay_tape(REFERENCE_TAPE)
    notifications = replay["notifications"]

    assert notifications["real_notification_send_performed"] is False
    assert notifications["notification_actions"] == {
        "dry_run_blocked": 1,
        "dry_run_daily_summary": 2,
        "dry_run_failed": 1,
        "dry_run_resource_limited": 1,
        "dry_run_review_needed": 1,
        "dry_run_weekly_summary": 1,
        "dry_run_withheld": 1,
    }
    assert all(notice["dry_run"] is True for notice in notifications["notifications"])
    assert all(notice["real_send_performed"] is False for notice in notifications["notifications"])


def test_report_windows_are_deterministic_operating_test_evidence():
    replay = replay_tape(REFERENCE_TAPE)

    assert [w["tick_event_id"] for w in replay["daily"]["windows"]] == ["EVT-0033", "EVT-0036"]
    assert [w["tick_event_id"] for w in replay["weekly"]["windows"]] == ["EVT-0037"]
    assert replay["daily"]["evidence_class"] == "operating_test_evidence"
    assert replay["weekly"]["evidence_class"] == "operating_test_evidence"
    assert all(w["deterministic_from_tape_timestamps"] is True for w in replay["daily"]["windows"])
    assert all(w["deterministic_from_tape_timestamps"] is True for w in replay["weekly"]["windows"])

    observed_categories = set()
    for payload in (replay["daily"], replay["weekly"]):
        for window in payload["windows"]:
            observed_categories.update(window["category_counts"])
    assert {
        "blocked",
        "failed",
        "invalid",
        "withheld",
        "insufficient",
        "resource_limited",
        "review_needed",
    } <= observed_categories


def test_non_authority_assertions_remain_false():
    replay = replay_tape(REFERENCE_TAPE)
    assertions = replay["non_authority"]

    assert assertions["operating_test_evidence"] is True
    for key in (
        "strategy_evidence",
        "candidate_evidence",
        "edge_claim_allowed",
        "real_notification_sending_authorized",
        "real_notification_send_performed",
        "recommendation_authority_created",
        "readiness_authority_created",
        "candidate_authority_created",
        "canonical_crossing_authority_created",
        "paper_live_authority_created",
        "protected_paths_touched",
    ):
        assert assertions[key] is False


def test_write_outputs_is_explicit_and_scoped(tmp_path):
    replay = replay_tape(REFERENCE_TAPE)
    write_outputs(replay, tmp_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "daily_report_replay.json",
        "daily_report_replay.md",
        "dry_run_notifications.json",
        "dry_run_notifications.md",
        "non_authority_assertions.json",
        "notify_report_replay_result.json",
        "notify_report_replay_result.md",
        "validation_summary.txt",
        "weekly_report_replay.json",
        "weekly_report_replay.md",
    ]
