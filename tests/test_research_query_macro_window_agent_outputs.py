import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


MACRO_WINDOW_AGENT_OUTPUT_VIEWS = {
    "v_macro_window_agent_outputs_overview",
    "v_macro_window_agent_outputs_latest",
    "v_integrity_macro_window_agent_output_refs",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_macro_window_agent_outputs_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM macro_window_agent_outputs").fetchone()[0]

    assert count == 2


def test_macro_window_agent_outputs_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(
        query_layer,
        "MACRO_WINDOW_AGENT_OUTPUTS_DIR",
        tmp_path / "missing_macro_window_agent_outputs",
    )

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM macro_window_agent_outputs").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_macro_window_agent_output_views_listed(conn):
    view_names = set(list_views(conn))

    assert MACRO_WINDOW_AGENT_OUTPUT_VIEWS <= view_names


def test_macro_window_agent_output_overview_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            macro_window_agent_output_id,
            macro_window_flag,
            event_class,
            event_name,
            deterministic,
            advisory_only
        FROM v_macro_window_agent_outputs_overview
        ORDER BY macro_window_agent_output_id
        """
    ).fetchall()

    assert rows == [
        (
            "MOUT-0001",
            True,
            "SYNTHETIC_MACRO_EVENT",
            "Synthetic macro risk window fixture",
            True,
            True,
        ),
        (
            "MOUT-0002",
            False,
            "SYNTHETIC_MACRO_EVENT",
            "Synthetic macro calm window fixture",
            True,
            True,
        ),
    ]


def test_macro_window_agent_output_latest_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT macro_window_agent_output_id, macro_window_flag
        FROM v_macro_window_agent_outputs_latest
        """
    ).fetchall()

    assert rows == [("MOUT-0002", False)]


def test_macro_window_agent_output_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_macro_window_agent_output_refs").fetchall()

    assert rows == []


def test_existing_integrity_views_still_empty(conn):
    for view_name in {
        "v_integrity_plan_report_pairs",
        "v_integrity_candidate_refs",
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
        "v_integrity_agent_output_refs",
        "v_integrity_bucket_mapping_refs",
        "v_integrity_overlay_shadow_refs",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE macro_window_agent_output_fixture AS SELECT 1 AS x")
