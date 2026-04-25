import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


SHADOW_SIGNAL_SUMMARY_VIEWS = {
    "v_shadow_signal_summaries_overview",
    "v_integrity_shadow_signal_summary_derivation",
    "v_shadow_signal_summaries_v2_overview",
    "v_integrity_shadow_signal_summary_v2_derivation",
}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_shadow_signal_summaries_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM shadow_signal_summaries").fetchone()[0]

    assert count == 1


def test_shadow_signal_summaries_v2_relation_registered_under_current_state(conn):
    count = conn.execute("SELECT COUNT(*) FROM shadow_signal_summaries_v2").fetchone()[0]

    assert count == 1


def test_shadow_signal_summaries_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(
        query_layer,
        "SHADOW_SIGNAL_SUMMARIES_DIR",
        tmp_path / "missing_shadow_signal_summaries",
    )

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM shadow_signal_summaries").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_shadow_signal_summaries_v2_relation_registered_empty_with_missing_dir(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        query_layer,
        "SHADOW_SIGNAL_SUMMARIES_V2_DIR",
        tmp_path / "missing_shadow_signal_summaries_v2",
    )

    connection = init_duckdb()
    try:
        count = connection.execute("SELECT COUNT(*) FROM shadow_signal_summaries_v2").fetchone()[0]

        assert count == 0
    finally:
        connection.close()


def test_shadow_signal_summary_views_are_listed(conn):
    view_names = set(list_views(conn))

    assert SHADOW_SIGNAL_SUMMARY_VIEWS <= view_names


def test_shadow_signal_summary_overview_exposes_current_segments(conn):
    rows = conn.execute(
        """
        SELECT
            shadow_signal_summary_id,
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            fixture_identity,
            match_count,
            mismatch_count,
            abstention_count,
            observation_count,
            signal_outcome
        FROM v_shadow_signal_summaries_overview
        ORDER BY
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            fixture_identity
        """
    ).fetchall()

    assert rows == [
        ("SSS-0001", "BMAP", "BMAP-0001", None, "_02", 0, 1, 0, 1, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "BMAP", "BMAP-0001", None, "canonical", 0, 2, 0, 2, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "BMAP", "BMAP-0002", None, "_02", 1, 0, 0, 1, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "BMAP", "BMAP-0002", None, "canonical", 1, 0, 0, 1, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "PGAS", "BMAP-0001", "PGAS-0002", "_02", 0, 1, 0, 1, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "PGAS", "BMAP-0001", "PGAS-0002", "canonical", 0, 2, 0, 2, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "PGAS", "BMAP-0002", "PGAS-0003", "_02", 1, 0, 0, 1, "INSUFFICIENT_EVIDENCE"),
        ("SSS-0001", "PGAS", "BMAP-0002", "PGAS-0003", "canonical", 1, 0, 0, 1, "INSUFFICIENT_EVIDENCE"),
    ]


def test_shadow_signal_summary_v2_overview_exposes_current_segments(conn):
    rows = conn.execute(
        """
        SELECT
            shadow_signal_summary_id,
            schema_version,
            segmentation_axes,
            segmentation_axes_json,
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            fixture_identity,
            match_count,
            mismatch_count,
            abstention_count,
            observation_count,
            rate_denominator,
            agreement_rate,
            disagreement_rate,
            insufficient_evidence,
            signal_outcome,
            first_segment_observed_at,
            last_segment_observed_at
        FROM v_shadow_signal_summaries_v2_overview
        ORDER BY advisory_source
        """
    ).fetchall()

    assert rows == [
        (
            "SSS-0002",
            "v2",
            "advisory_source",
            '["advisory_source"]',
            "BMAP",
            None,
            None,
            None,
            2,
            3,
            0,
            5,
            5,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-19T17:00:00Z",
            "2026-04-22T07:00:00Z",
        ),
        (
            "SSS-0002",
            "v2",
            "advisory_source",
            '["advisory_source"]',
            "PGAS",
            None,
            None,
            None,
            2,
            3,
            0,
            5,
            5,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-19T18:00:00Z",
            "2026-04-22T08:00:00Z",
        ),
    ]


def test_shadow_signal_summary_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_shadow_signal_summary_derivation").fetchall()

    assert rows == []


def test_shadow_signal_summary_v2_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_shadow_signal_summary_v2_derivation").fetchall()

    assert rows == []


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE shadow_signal_summary_fixture AS SELECT 1 AS x")
