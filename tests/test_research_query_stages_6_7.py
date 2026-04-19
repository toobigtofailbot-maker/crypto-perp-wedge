import pytest

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


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_stage_6_7_relations_registered_empty_under_current_state(conn):
    decision_count = conn.execute("SELECT COUNT(*) FROM decision_changes").fetchone()[0]
    release_count = conn.execute("SELECT COUNT(*) FROM release_notes").fetchone()[0]

    assert decision_count == 0
    assert release_count == 0


def test_stage_6_7_views_listed(conn):
    view_names = set(list_views(conn))

    assert NEW_VIEWS <= view_names


def test_stage_6_7_views_empty_under_current_state(conn):
    for view_name in NEW_VIEWS:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


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
