import json

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

    assert count == 3


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
        ORDER BY
            shadow_signal_summary_id,
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id
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
        (
            "SSS-0003",
            "v2",
            "advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id",
            '["advisory_source","source_bucket_mapping_id","source_pre_gate_advisory_snapshot_id"]',
            "BMAP",
            "BMAP-0001",
            None,
            None,
            0,
            3,
            0,
            3,
            3,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-19T17:00:00Z",
            "2026-04-22T05:00:00Z",
        ),
        (
            "SSS-0003",
            "v2",
            "advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id",
            '["advisory_source","source_bucket_mapping_id","source_pre_gate_advisory_snapshot_id"]',
            "BMAP",
            "BMAP-0002",
            None,
            None,
            2,
            0,
            0,
            2,
            2,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-22T03:00:00Z",
            "2026-04-22T07:00:00Z",
        ),
        (
            "SSS-0003",
            "v2",
            "advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id",
            '["advisory_source","source_bucket_mapping_id","source_pre_gate_advisory_snapshot_id"]',
            "PGAS",
            "BMAP-0001",
            "PGAS-0002",
            None,
            0,
            3,
            0,
            3,
            3,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-19T18:00:00Z",
            "2026-04-22T06:00:00Z",
        ),
        (
            "SSS-0003",
            "v2",
            "advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id",
            '["advisory_source","source_bucket_mapping_id","source_pre_gate_advisory_snapshot_id"]',
            "PGAS",
            "BMAP-0002",
            "PGAS-0003",
            None,
            2,
            0,
            0,
            2,
            2,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-22T04:00:00Z",
            "2026-04-22T08:00:00Z",
        ),
        (
            "SSS-0004",
            "v2",
            "fixture_identity",
            '["fixture_identity"]',
            None,
            None,
            None,
            "_02",
            2,
            2,
            0,
            4,
            4,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-22T05:00:00Z",
            "2026-04-22T08:00:00Z",
        ),
        (
            "SSS-0004",
            "v2",
            "fixture_identity",
            '["fixture_identity"]',
            None,
            None,
            None,
            "canonical",
            2,
            4,
            0,
            6,
            6,
            None,
            None,
            True,
            "INSUFFICIENT_EVIDENCE",
            "2026-04-19T17:00:00Z",
            "2026-04-22T04:00:00Z",
        ),
    ]


def test_shadow_signal_summary_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_shadow_signal_summary_derivation").fetchall()

    assert rows == []


def test_shadow_signal_summary_v2_integrity_view_empty_under_current_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_shadow_signal_summary_v2_derivation").fetchall()

    assert rows == []


def test_shadow_signal_summary_v2_integrity_supports_advisory_lineage_form(
    monkeypatch,
    tmp_path,
):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    summaries_dir.mkdir(parents=True)
    lineage_payload = {
        "shadow_signal_summary_id": "SSS-9003",
        "schema_version": "v2",
        "generated_at": "2026-04-22T08:00:00Z",
        "corpus_window": {
            "first_overlay_shadow_log_id": "OSH-0001",
            "last_overlay_shadow_log_id": "OSH-0010",
            "first_observed_at": "2026-04-19T17:00:00Z",
            "last_observed_at": "2026-04-22T08:00:00Z",
            "total_source_observation_count": 10,
        },
        "derivation_method": "shadow_signal_summary_option_a_floor_10_v1",
        "segmentation_axes": [
            "advisory_source",
            "source_bucket_mapping_id",
            "source_pre_gate_advisory_snapshot_id",
        ],
        "derivation_inputs": {
            "source_relation": "overlay_shadow_logs",
            "source_artifact_family": "overlay_shadow_logs",
            "fixture_identity_rule": "committed_overlay_input_pair_v1",
            "rate_denominator_rule": "match_plus_mismatch",
        },
        "segments": [
            {
                "advisory_source": "BMAP",
                "source_bucket_mapping_id": "BMAP-0001",
                "source_pre_gate_advisory_snapshot_id": None,
                "match_count": 0,
                "mismatch_count": 3,
                "abstention_count": 0,
                "observation_count": 3,
                "rate_denominator": 3,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-19T17:00:00Z",
                "last_observed_at": "2026-04-22T05:00:00Z",
            },
            {
                "advisory_source": "BMAP",
                "source_bucket_mapping_id": "BMAP-0002",
                "source_pre_gate_advisory_snapshot_id": None,
                "match_count": 2,
                "mismatch_count": 0,
                "abstention_count": 0,
                "observation_count": 2,
                "rate_denominator": 2,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-22T03:00:00Z",
                "last_observed_at": "2026-04-22T07:00:00Z",
            },
            {
                "advisory_source": "PGAS",
                "source_bucket_mapping_id": "BMAP-0001",
                "source_pre_gate_advisory_snapshot_id": "PGAS-0002",
                "match_count": 0,
                "mismatch_count": 3,
                "abstention_count": 0,
                "observation_count": 3,
                "rate_denominator": 3,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-19T18:00:00Z",
                "last_observed_at": "2026-04-22T06:00:00Z",
            },
            {
                "advisory_source": "PGAS",
                "source_bucket_mapping_id": "BMAP-0002",
                "source_pre_gate_advisory_snapshot_id": "PGAS-0003",
                "match_count": 2,
                "mismatch_count": 0,
                "abstention_count": 0,
                "observation_count": 2,
                "rate_denominator": 2,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-22T04:00:00Z",
                "last_observed_at": "2026-04-22T08:00:00Z",
            },
        ],
        "deterministic": True,
        "advisory_only": True,
        "notes": "Temporary test artifact for advisory-lineage v2 integrity coverage.",
    }
    artifact_path = summaries_dir / "SSS-9003.shadow_signal_summary.json"
    artifact_path.write_text(json.dumps(lineage_payload, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(query_layer, "SHADOW_SIGNAL_SUMMARIES_V2_DIR", summaries_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute(
            "SELECT * FROM v_integrity_shadow_signal_summary_v2_derivation"
        ).fetchall()

        assert rows == []
    finally:
        connection.close()


def test_shadow_signal_summary_v2_integrity_supports_fixture_identity_form(
    monkeypatch,
    tmp_path,
):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    summaries_dir.mkdir(parents=True)
    fixture_payload = {
        "shadow_signal_summary_id": "SSS-9004",
        "schema_version": "v2",
        "generated_at": "2026-04-22T08:00:00Z",
        "corpus_window": {
            "first_overlay_shadow_log_id": "OSH-0001",
            "last_overlay_shadow_log_id": "OSH-0010",
            "first_observed_at": "2026-04-19T17:00:00Z",
            "last_observed_at": "2026-04-22T08:00:00Z",
            "total_source_observation_count": 10,
        },
        "derivation_method": "shadow_signal_summary_option_a_floor_10_v1",
        "segmentation_axes": ["fixture_identity"],
        "derivation_inputs": {
            "source_relation": "overlay_shadow_logs",
            "source_artifact_family": "overlay_shadow_logs",
            "fixture_identity_rule": "committed_overlay_input_pair_v1",
            "rate_denominator_rule": "match_plus_mismatch",
        },
        "segments": [
            {
                "fixture_identity": "_02",
                "match_count": 2,
                "mismatch_count": 2,
                "abstention_count": 0,
                "observation_count": 4,
                "rate_denominator": 4,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-22T05:00:00Z",
                "last_observed_at": "2026-04-22T08:00:00Z",
            },
            {
                "fixture_identity": "canonical",
                "match_count": 2,
                "mismatch_count": 4,
                "abstention_count": 0,
                "observation_count": 6,
                "rate_denominator": 6,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": "2026-04-19T17:00:00Z",
                "last_observed_at": "2026-04-22T04:00:00Z",
            },
        ],
        "deterministic": True,
        "advisory_only": True,
        "notes": "Temporary test artifact for fixture-only v2 integrity coverage.",
    }
    artifact_path = summaries_dir / "SSS-9004.shadow_signal_summary.json"
    artifact_path.write_text(json.dumps(fixture_payload, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(query_layer, "SHADOW_SIGNAL_SUMMARIES_V2_DIR", summaries_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute(
            "SELECT * FROM v_integrity_shadow_signal_summary_v2_derivation"
        ).fetchall()

        assert rows == []
    finally:
        connection.close()


def test_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE shadow_signal_summary_fixture AS SELECT 1 AS x")
