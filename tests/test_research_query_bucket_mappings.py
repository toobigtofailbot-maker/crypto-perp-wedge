import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


BUCKET_MAPPING_VIEWS = {
    "v_bucket_mappings_overview",
    "v_bucket_mappings_latest",
    "v_integrity_bucket_mapping_refs",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_bucket_mappings_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM bucket_mappings").fetchone()[0]

    assert count == 1


def test_bucket_mappings_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "BUCKET_MAPPINGS_DIR", tmp_path / "missing_bucket_mappings")

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM bucket_mappings").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_bucket_mapping_views_listed(conn):
    view_names = set(list_views(conn))

    assert BUCKET_MAPPING_VIEWS <= view_names


def test_bucket_mapping_overview_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT
            bucket_mapping_id,
            source_agent_output_id,
            agent_type,
            mapped_bucket,
            size_multiplier,
            source_setup_score,
            source_confidence,
            deterministic,
            advisory_only
        FROM v_bucket_mappings_overview
        """
    ).fetchall()

    assert rows == [
        (
            "BMAP-0001",
            "AOUT-0001",
            "REGIME_SCORING",
            "ALLOW_REDUCED",
            0.5,
            72.95,
            0.891,
            True,
            True,
        )
    ]


def test_bucket_mapping_latest_returns_current_rows(conn):
    rows = conn.execute(
        """
        SELECT bucket_mapping_id, source_agent_output_id, agent_type
        FROM v_bucket_mappings_latest
        """
    ).fetchall()

    assert rows == [("BMAP-0001", "AOUT-0001", "REGIME_SCORING")]


def test_bucket_mapping_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_bucket_mapping_refs").fetchall()

    assert rows == []


def test_existing_integrity_views_still_empty(conn):
    for view_name in {
        "v_integrity_plan_report_pairs",
        "v_integrity_candidate_refs",
        "v_integrity_decision_refs",
        "v_integrity_release_refs",
        "v_integrity_agent_output_refs",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE bucket_mapping_fixture AS SELECT 1 AS x")
