import json

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


LIFECYCLE_VIEWS = {
    "v_lifecycle_change_overview",
    "v_lifecycle_state_transitions",
    "v_integrity_lifecycle_change_refs",
    "v_integrity_lifecycle_transition_graph",
    "v_integrity_lifecycle_approval_completeness",
    "v_integrity_lifecycle_fast_track_completeness",
}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _base_lifecycle_change(lifecycle_change_id="LCH-9001"):
    return {
        "lifecycle_change_id": lifecycle_change_id,
        "schema_version": "v1",
        "candidate_id": "H-005",
        "from_state": "proposed",
        "to_state": "in_research",
        "transition_edge": "proposed->in_research",
        "decided_by": "pytest fixture",
        "decided_at": "2026-04-23T12:00:00Z",
        "evidence_summary": "Fixture lifecycle evidence summary.",
        "risk_acknowledgment": "Fixture risk acknowledgment.",
        "evidence_artifact_refs": [],
        "supersedes_lch_id": None,
        "notes": "Temporary query-layer test artifact.",
        "linked_advisory_artifacts": [],
        "retrospective_flag": False,
        "retrospective_disclosure": None,
        "fast_track_flag": False,
        "strong_candidate_criteria_refs": [],
    }


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_lifecycle_relation_registered_empty_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM lifecycle_changes").fetchone()[0]

    assert count == 0


def test_lifecycle_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "LIFECYCLE_CHANGES_DIR", tmp_path / "missing_lifecycle_changes")

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM lifecycle_changes").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_lifecycle_views_are_listed(conn):
    view_names = set(list_views(conn))

    assert LIFECYCLE_VIEWS <= view_names


def test_lifecycle_overview_and_transition_views_empty_under_current_state(conn):
    overview_rows = conn.execute("SELECT * FROM v_lifecycle_change_overview").fetchall()
    transition_rows = conn.execute("SELECT * FROM v_lifecycle_state_transitions").fetchall()

    assert overview_rows == []
    assert transition_rows == []


def test_lifecycle_integrity_views_empty_under_current_state(conn):
    for view_name in {
        "v_integrity_lifecycle_change_refs",
        "v_integrity_lifecycle_transition_graph",
        "v_integrity_lifecycle_approval_completeness",
        "v_integrity_lifecycle_fast_track_completeness",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_temp_lifecycle_change_refs_accept_real_repo_refs(monkeypatch, tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    payload = _base_lifecycle_change()
    payload["candidate_id"] = "H-001"
    payload["evidence_artifact_refs"] = [
        "research/hypotheses/H-001/HYPOTHESIS.md",
        "REP-0002",
        "research/decisions/DEC-0001.md",
    ]
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)
    monkeypatch.setattr(query_layer, "LIFECYCLE_CHANGES_DIR", lifecycle_changes_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute("SELECT * FROM v_integrity_lifecycle_change_refs").fetchall()

        assert rows == []
    finally:
        connection.close()


def test_temp_lifecycle_change_refs_emit_unknown_known_pattern_issue(monkeypatch, tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    payload = _base_lifecycle_change()
    payload["candidate_id"] = "H-001"
    payload["evidence_artifact_refs"] = ["REP-9999"]
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)
    monkeypatch.setattr(query_layer, "LIFECYCLE_CHANGES_DIR", lifecycle_changes_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute(
            """
            SELECT issue_type, lifecycle_change_id, candidate_id, ref_kind, ref_value
            FROM v_integrity_lifecycle_change_refs
            """
        ).fetchall()

        assert rows == [
            (
                "lifecycle_unknown_rep_ref",
                "LCH-9001",
                "H-001",
                "evidence_artifact_refs",
                "REP-9999",
            )
        ]
    finally:
        connection.close()


def test_temp_valid_lifecycle_change_produces_overview_row(monkeypatch, tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    payload = _base_lifecycle_change()
    payload["from_state"] = "paper_concluded"
    payload["to_state"] = "live_eligible"
    payload["transition_edge"] = "paper_concluded->live_eligible"
    payload["evidence_artifact_refs"] = ["REP-0001"]
    payload["linked_advisory_artifacts"] = ["PGAS-0001"]
    payload["fast_track_flag"] = True
    payload["strong_candidate_criteria_refs"] = ["REP-0001"]
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)
    monkeypatch.setattr(query_layer, "LIFECYCLE_CHANGES_DIR", lifecycle_changes_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute(
            """
            SELECT
                lifecycle_change_id,
                candidate_id,
                from_state,
                to_state,
                transition_edge,
                evidence_ref_count,
                linked_advisory_ref_count,
                strong_candidate_criteria_ref_count
            FROM v_lifecycle_change_overview
            """
        ).fetchall()
        transitions = connection.execute(
            """
            SELECT from_state, to_state, transition_edge, transition_count
            FROM v_lifecycle_state_transitions
            """
        ).fetchall()
        integrity_rows = connection.execute(
            "SELECT * FROM v_integrity_lifecycle_fast_track_completeness"
        ).fetchall()

        assert rows == [
            (
                "LCH-9001",
                "H-005",
                "paper_concluded",
                "live_eligible",
                "paper_concluded->live_eligible",
                1,
                1,
                1,
            )
        ]
        assert transitions == [("paper_concluded", "live_eligible", "paper_concluded->live_eligible", 1)]
        assert integrity_rows == []
    finally:
        connection.close()


def test_temp_invalid_lifecycle_change_produces_integrity_rows(monkeypatch, tmp_path):
    lifecycle_changes_dir = tmp_path / "research" / "lifecycle_changes"
    payload = _base_lifecycle_change()
    payload["candidate_id"] = "H-999"
    payload["from_state"] = "paper_eligible"
    payload["to_state"] = "paper_active"
    payload["transition_edge"] = "proposed->in_research"
    payload["decided_by"] = ""
    payload["decided_at"] = ""
    payload["risk_acknowledgment"] = ""
    payload["evidence_artifact_refs"] = ["REP-9999"]
    payload["linked_advisory_artifacts"] = ["PGAS-9999"]
    payload["supersedes_lch_id"] = "LCH-9999"
    payload["fast_track_flag"] = True
    payload["strong_candidate_criteria_refs"] = []
    _write_json(lifecycle_changes_dir / "LCH-9001.lifecycle_change.json", payload)
    monkeypatch.setattr(query_layer, "LIFECYCLE_CHANGES_DIR", lifecycle_changes_dir)

    connection = init_duckdb()
    try:
        ref_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_lifecycle_change_refs"
            ).fetchall()
        }
        graph_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_lifecycle_transition_graph"
            ).fetchall()
        }
        approval_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_lifecycle_approval_completeness"
            ).fetchall()
        }
        fast_track_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_lifecycle_fast_track_completeness"
            ).fetchall()
        }

        assert {
            "lifecycle_unknown_candidate",
            "lifecycle_unknown_supersedes",
            "lifecycle_unknown_rep_ref",
            "lifecycle_unknown_pgas_ref",
        } <= ref_issue_types
        assert graph_issue_types == {"lifecycle_transition_shape_mismatch"}
        assert {
            "lifecycle_missing_risk_acknowledgment",
            "lifecycle_missing_decided_by",
            "lifecycle_missing_decided_at",
        } <= approval_issue_types
        assert {
            "lifecycle_fast_track_wrong_to_state",
            "lifecycle_fast_track_missing_strong_candidate_criteria",
            "lifecycle_fast_track_missing_risk_acknowledgment",
        } <= fast_track_issue_types
    finally:
        connection.close()


def test_existing_query_layer_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE lifecycle_fixture AS SELECT 1 AS x")


def test_existing_views_and_integrity_regressions_preserved(conn):
    view_names = set(list_views(conn))
    assert {
        "v_candidate_overview",
        "v_integrity_plan_report_pairs",
        "v_integrity_candidate_refs",
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
    } <= view_names

    candidate_count = conn.execute("SELECT COUNT(*) FROM v_candidate_overview").fetchone()[0]
    assert candidate_count == 11

    for view_name in {
        "v_integrity_plan_report_pairs",
        "v_integrity_candidate_refs",
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
        "v_integrity_agent_output_refs",
        "v_integrity_bucket_mapping_refs",
        "v_integrity_overlay_shadow_refs",
        "v_integrity_macro_window_agent_output_refs",
        "v_integrity_pre_gate_advisory_snapshot_refs",
        "v_integrity_shadow_signal_summary_derivation",
        "v_integrity_shadow_signal_summary_v2_derivation",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []
