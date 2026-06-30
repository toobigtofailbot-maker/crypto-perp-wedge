from pathlib import Path

from tools.lab_event_tape.replay_agent_dashboard import replay_tape, write_outputs


REFERENCE_TAPE = Path("scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json")


def test_agent_dashboard_replay_matches_reference_tape_actions() -> None:
    replay = replay_tape(REFERENCE_TAPE)
    result = replay["result"]

    assert result["status"] == "complete"
    assert result["input_tape_id"] == "LAB-EVENT-TAPE-REFERENCE-001"
    assert result["schema_version"] == "lab_event_tape.v1"
    assert result["event_count"] == 40
    assert result["job_count"] == 10
    assert result["queue_scheduler_replay_consumed"] is True
    assert result["notify_report_replay_consumed"] is True
    assert result["agent_actions_matched"] is True
    assert result["dashboard_actions_matched"] is True
    assert result["mismatches"] == []


def test_all_jobs_remain_non_promotable_no_candidate_no_authority() -> None:
    replay = replay_tape(REFERENCE_TAPE)
    job_summary = replay["agent_loop_job_summary"]
    assertions = replay["non_authority_assertions"]

    assert job_summary["job_count"] == 10
    assert job_summary["final_outcome_counts"] == {
        "blocked": 1,
        "completed": 1,
        "delayed": 1,
        "failed": 1,
        "insufficient": 1,
        "invalid": 1,
        "no_candidate": 1,
        "resource_limited": 1,
        "review_needed": 1,
        "withheld": 1,
    }
    assert job_summary["candidate_eligible_any"] is False
    assert job_summary["promotion_eligible_any"] is False
    assert job_summary["canonical_crossing_allowed_any"] is False
    assert job_summary["paper_live_eligible_any"] is False
    assert job_summary["edge_claim_allowed_any"] is False
    assert job_summary["strategy_evidence_any"] is False
    assert job_summary["candidate_admitted_any"] is False
    assert assertions["operating_test_evidence"] is True
    assert assertions["strategy_evidence"] is False
    assert assertions["candidate_evidence"] is False
    assert assertions["edge_claim_allowed"] is False
    assert assertions["candidate_admitted"] is False
    assert assertions["protected_paths_touched"] is False
    assert all(job["construction_payload"] is True for job in job_summary["jobs"])
    assert all(job["non_promotable"] is True for job in job_summary["jobs"])
    assert all(job["no_candidate_label"] is True for job in job_summary["jobs"])
    assert all(job["no_authority_label"] is True for job in job_summary["jobs"])


def test_agent_loop_creates_no_rescue_or_authority_recommendations() -> None:
    replay = replay_tape(REFERENCE_TAPE)
    result = replay["result"]
    trace = replay["agent_loop_event_trace"]

    assert result["candidate_admitted"] is False
    assert result["rescue_recommended"] is False
    assert result["retuning_recommended"] is False
    assert result["ranking_recommended"] is False
    assert result["readiness_recommended"] is False
    assert result["promotion_recommended"] is False
    assert result["real_crossing_created"] is False
    assert result["strategy_run_performed"] is False
    assert result["edge_search_authorized_here"] is False
    assert result["paper_live_authority_created"] is False
    assert all(row["rescue_recommended"] is False for row in trace)
    assert all(row["retuning_recommended"] is False for row in trace)
    assert all(row["candidate_admitted"] is False for row in trace)
    assert all(row["real_crossing_created"] is False for row in trace)


def test_dashboard_snapshots_are_labeled_operating_test_only() -> None:
    replay = replay_tape(REFERENCE_TAPE)
    dashboard = replay["dashboard_state_transitions"]
    label_audit = replay["dashboard_operating_test_label_audit"]

    assert dashboard["snapshot_count"] == 40
    assert dashboard["deterministic_from_event_timestamps_and_sequence_index"] is True
    assert dashboard["operating_test_labels_present"] is True
    assert dashboard["real_research_evidence_labels_present"] is False
    assert dashboard["no_candidate_labels_present"] is True
    assert dashboard["no_authority_labels_present"] is True
    assert dashboard["prior_replay_references_included"] is True
    assert dashboard["aggregates_operating_test_into_real_strategy_evidence"] is False
    assert label_audit["operating_test_evidence_label_present"] is True
    assert label_audit["real_research_evidence_label_present"] is False
    assert label_audit["strategy_evidence_label_present"] is False
    assert label_audit["candidate_evidence_label_present"] is False
    assert label_audit["forbidden_authority_terms_present"] is False
    assert label_audit["required_operating_categories_present"] is True
    assert {
        "blocked",
        "failed",
        "invalid",
        "withheld",
        "insufficient",
        "resource_limited",
        "review_needed",
        "completed",
        "no_candidate",
    } <= set(label_audit["observed_categories"])


def test_prior_replay_outputs_are_consumed_as_non_authoritative() -> None:
    replay = replay_tape(REFERENCE_TAPE)
    links = replay["prior_replay_evidence_links"]

    assert links["queue_scheduler_replay_consumed"] is True
    assert links["notify_report_replay_consumed"] is True
    assert links["mismatches"] == []
    assert len(links["links"]) == 4
    for link in links["links"]:
        assert link["present"] is True
        assert link["non_authoritative"] is True


def test_write_outputs_is_explicit_and_scoped(tmp_path) -> None:
    replay = replay_tape(REFERENCE_TAPE)
    write_outputs(replay, tmp_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "agent_dashboard_replay_result.json",
        "agent_dashboard_replay_result.md",
        "agent_loop_event_trace.json",
        "agent_loop_job_summary.json",
        "dashboard_operating_test_label_audit.json",
        "dashboard_state_transitions.json",
        "dashboard_state_transitions.md",
        "non_authority_assertions.json",
        "prior_replay_evidence_links.json",
        "validation_summary.txt",
    ]
