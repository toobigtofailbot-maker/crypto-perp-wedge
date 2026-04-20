import pytest

from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


SHADOW_SIGNAL_VIEWS = {
    "v_overlay_shadow_agreement_summary",
    "v_overlay_shadow_override_audit",
}

INTEGRITY_VIEWS = {
    "v_integrity_plan_report_pairs",
    "v_integrity_candidate_refs",
    "v_integrity_decision_refs",
    "v_integrity_release_refs",
    "v_integrity_agent_output_refs",
    "v_integrity_bucket_mapping_refs",
    "v_integrity_overlay_shadow_refs",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_shadow_signal_views_are_listed(conn):
    view_names = set(list_views(conn))

    assert SHADOW_SIGNAL_VIEWS <= view_names


def test_shadow_agreement_summary_reflects_current_committed_entry(conn):
    rows = conn.execute(
        """
        SELECT
            comparison_result,
            entry_count,
            match_count,
            mismatch_count,
            override_true_count,
            first_observed_at,
            last_observed_at
        FROM v_overlay_shadow_agreement_summary
        ORDER BY comparison_result
        """
    ).fetchall()

    assert rows == [
        (
            "MISMATCH",
            1,
            0,
            1,
            0,
            "2026-04-19T17:00:00Z",
            "2026-04-19T17:00:00Z",
        )
    ]


def test_shadow_override_audit_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_overlay_shadow_override_audit").fetchall()

    assert rows == []


def test_integrity_views_still_empty(conn):
    for view_name in INTEGRITY_VIEWS:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE shadow_signal_fixture AS SELECT 1 AS x")
