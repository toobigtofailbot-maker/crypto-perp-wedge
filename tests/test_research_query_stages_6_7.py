import json

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


NEW_VIEWS = {
    "v_decision_changes_overview",
    "v_release_notes_overview",
    "v_stage_transitions",
    "v_integrity_decision_refs",
    "v_integrity_release_refs",
}


def _decision_change_fixture(decision_change_id, supersedes_decision_id):
    return {
        "decision_change_id": decision_change_id,
        "candidate_id": "H-005",
        "report_ids": ["REP-0001"],
        "decision": "REJECT_AT_THIS_STAGE",
        "stage_transition": {
            "from_stage": "baseline_tested",
            "to_stage": "archived",
        },
        "decided_by": "pytest fixture",
        "decided_at": "2026-04-19T12:00:00Z",
        "rationale": "Fixture rationale.",
        "evidence_summary": "Fixture evidence summary.",
        "risk_acknowledgment": "Fixture risk acknowledgment.",
        "supersedes_decision_id": supersedes_decision_id,
    }


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_stage_6_7_relations_registered_under_current_state(conn):
    decision_count = conn.execute("SELECT COUNT(*) FROM decision_changes").fetchone()[0]
    release_count = conn.execute("SELECT COUNT(*) FROM release_notes").fetchone()[0]

    assert decision_count > 0
    assert release_count > 0


def test_stage_6_7_relations_registered_empty_with_missing_dirs(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "DECISION_CHANGES_DIR", tmp_path / "missing_decision_changes")
    monkeypatch.setattr(query_layer, "RELEASE_NOTES_DIR", tmp_path / "missing_release_notes")

    connection = init_duckdb()
    try:
        decision_count = connection.execute("SELECT COUNT(*) FROM decision_changes").fetchone()[0]
        release_count = connection.execute("SELECT COUNT(*) FROM release_notes").fetchone()[0]

        assert decision_count == 0
        assert release_count == 0
    finally:
        connection.close()


def test_stage_6_7_views_listed(conn):
    view_names = set(list_views(conn))

    assert NEW_VIEWS <= view_names


def test_stage_6_7_overview_views_return_current_rows(conn):
    for view_name in {
        "v_decision_changes_overview",
        "v_release_notes_overview",
        "v_stage_transitions",
    }:
        count = conn.execute(f'SELECT COUNT(*) FROM "{view_name}"').fetchone()[0]

        assert count > 0


def test_stage_6_7_integrity_views_empty_under_current_state(conn):
    for view_name in {
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_decision_integrity_accepts_null_and_flags_invalid_supersedes(monkeypatch, tmp_path):
    decision_changes_dir = tmp_path / "decision_changes"
    _write_json(
        decision_changes_dir / "DCH-9001.decision_change.json",
        _decision_change_fixture("DCH-9001", None),
    )
    _write_json(
        decision_changes_dir / "DCH-9002.decision_change.json",
        _decision_change_fixture("DCH-9002", "DCH-9999"),
    )
    monkeypatch.setattr(query_layer, "DECISION_CHANGES_DIR", decision_changes_dir)
    monkeypatch.setattr(query_layer, "RELEASE_NOTES_DIR", tmp_path / "missing_release_notes")

    connection = init_duckdb()
    try:
        rows = connection.execute(
            """
            SELECT issue_type, decision_change_id, supersedes_decision_id
            FROM v_integrity_decision_refs
            ORDER BY decision_change_id
            """
        ).fetchall()

        assert rows == [("decision_unknown_supersedes", "DCH-9002", "DCH-9999")]
    finally:
        connection.close()


def test_existing_integrity_views_still_empty(conn):
    plan_report_rows = conn.execute("SELECT * FROM v_integrity_plan_report_pairs").fetchall()
    candidate_ref_rows = conn.execute("SELECT * FROM v_integrity_candidate_refs").fetchall()

    assert plan_report_rows == []
    assert candidate_ref_rows == []


def test_existing_candidate_view_still_returns_registered_rows(conn):
    candidate_count = conn.execute("SELECT COUNT(*) FROM v_candidate_overview").fetchone()[0]

    assert candidate_count == 11


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE stage_fixture AS SELECT 1 AS x")
