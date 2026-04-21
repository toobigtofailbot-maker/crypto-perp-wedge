import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


PRE_GATE_ADVISORY_SNAPSHOT_VIEWS = {
    "v_pre_gate_advisory_snapshots_overview",
    "v_pre_gate_advisory_snapshots_latest",
    "v_integrity_pre_gate_advisory_snapshot_refs",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_pre_gate_advisory_snapshots_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM pre_gate_advisory_snapshots").fetchone()[0]

    assert count == 2


def test_pre_gate_advisory_snapshots_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(
        query_layer,
        "PRE_GATE_ADVISORY_SNAPSHOTS_DIR",
        tmp_path / "missing_pre_gate_advisory_snapshots",
    )

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM pre_gate_advisory_snapshots").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_pre_gate_advisory_snapshot_views_listed(conn):
    view_names = set(list_views(conn))

    assert PRE_GATE_ADVISORY_SNAPSHOT_VIEWS <= view_names


def test_pre_gate_advisory_snapshot_overview_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            pre_gate_advisory_snapshot_id,
            source_agent_output_id,
            source_bucket_mapping_id,
            source_macro_window_agent_output_id,
            mapped_bucket,
            size_multiplier,
            macro_window_flag,
            combination_rule_applied,
            combined_bucket,
            deterministic,
            advisory_only
        FROM v_pre_gate_advisory_snapshots_overview
        ORDER BY pre_gate_advisory_snapshot_id
        """
    ).fetchall()

    assert rows == [
        (
            "PGAS-0001",
            "AOUT-0001",
            "BMAP-0001",
            "MOUT-0001",
            "ALLOW_REDUCED",
            0.5,
            True,
            "NONE_BUNDLE_ONLY",
            None,
            True,
            True,
        ),
        (
            "PGAS-0002",
            "AOUT-0001",
            "BMAP-0001",
            "MOUT-0001",
            "ALLOW_REDUCED",
            0.5,
            True,
            "MACRO_AWARE_FLOOR",
            "ALLOW_REDUCED",
            True,
            True,
        )
    ]


def test_pre_gate_advisory_snapshot_latest_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            pre_gate_advisory_snapshot_id,
            source_agent_output_id,
            source_bucket_mapping_id,
            source_macro_window_agent_output_id
        FROM v_pre_gate_advisory_snapshots_latest
        """
    ).fetchall()

    assert rows == [("PGAS-0002", "AOUT-0001", "BMAP-0001", "MOUT-0001")]


def test_pre_gate_advisory_snapshot_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_pre_gate_advisory_snapshot_refs").fetchall()

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
        "v_integrity_macro_window_agent_output_refs",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE pre_gate_advisory_snapshot_fixture AS SELECT 1 AS x")
