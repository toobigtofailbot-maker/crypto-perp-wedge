import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


OVERLAY_SHADOW_LOG_VIEWS = {
    "v_overlay_shadow_logs_overview",
    "v_overlay_shadow_logs_latest",
    "v_integrity_overlay_shadow_refs",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_overlay_shadow_logs_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM overlay_shadow_logs").fetchone()[0]

    assert count == 4


def test_overlay_shadow_logs_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "OVERLAY_SHADOW_LOGS_DIR", tmp_path / "missing_overlay_shadow_logs")

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM overlay_shadow_logs").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_overlay_shadow_log_views_listed(conn):
    view_names = set(list_views(conn))

    assert OVERLAY_SHADOW_LOG_VIEWS <= view_names


def test_overlay_shadow_log_overview_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            overlay_shadow_log_id,
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            source_agent_output_id,
            observed_overlay_bucket,
            mapped_bucket,
            size_multiplier,
            comparison_result,
            override_applied,
            fail_open_preserved,
            advisory_only
        FROM v_overlay_shadow_logs_overview
        ORDER BY overlay_shadow_log_id
        """
    ).fetchall()

    assert rows == [
        (
            "OSH-0001",
            "BMAP",
            "BMAP-0001",
            None,
            "AOUT-0001",
            "ALLOW",
            "ALLOW_REDUCED",
            0.5,
            "MISMATCH",
            False,
            True,
            True,
        ),
        (
            "OSH-0002",
            "PGAS",
            "BMAP-0001",
            "PGAS-0002",
            "AOUT-0001",
            "ALLOW",
            "ALLOW_REDUCED",
            0.5,
            "MISMATCH",
            False,
            True,
            True,
        ),
        (
            "OSH-0003",
            "BMAP",
            "BMAP-0001",
            None,
            "AOUT-0001",
            "ALLOW",
            "ALLOW_REDUCED",
            0.5,
            "MISMATCH",
            False,
            True,
            True,
        ),
        (
            "OSH-0004",
            "PGAS",
            "BMAP-0001",
            "PGAS-0002",
            "AOUT-0001",
            "ALLOW",
            "ALLOW_REDUCED",
            0.5,
            "MISMATCH",
            False,
            True,
            True,
        )
    ]


def test_overlay_shadow_log_latest_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            overlay_shadow_log_id,
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            source_agent_output_id
        FROM v_overlay_shadow_logs_latest
        ORDER BY advisory_source
        """
    ).fetchall()

    assert rows == [
        ("OSH-0003", "BMAP", "BMAP-0001", None, "AOUT-0001"),
        ("OSH-0004", "PGAS", "BMAP-0001", "PGAS-0002", "AOUT-0001"),
    ]


def test_overlay_shadow_log_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_overlay_shadow_refs").fetchall()

    assert rows == []


def test_existing_integrity_views_still_empty(conn):
    for view_name in {
        "v_integrity_plan_report_pairs",
        "v_integrity_candidate_refs",
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
        "v_integrity_agent_output_refs",
        "v_integrity_bucket_mapping_refs",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE overlay_shadow_fixture AS SELECT 1 AS x")
