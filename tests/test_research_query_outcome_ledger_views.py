import json

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


OUTCOME_LEDGER_VIEWS = {
    "v_outcome_ledger_overview",
    "v_outcome_ledger_candidate_pipeline_summary",
    "v_integrity_outcome_ledger_refs",
    "v_integrity_outcome_ledger_window_bounds",
    "v_integrity_outcome_ledger_derivation",
    "v_integrity_outcome_ledger_scope",
}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _base_outcome(outcome_id="OL-9001"):
    return {
        "schema_version": "v1",
        "outcome_id": outcome_id,
        "candidate_id": "H-005",
        "lifecycle_state_during_window": "in_research",
        "evaluation_window_start": None,
        "evaluation_window_end": None,
        "outcome_kind": "research_oos",
        "metrics": {
            "source_field": "trial_log.oos_sharpe",
            "window_convention": "No separate IS/OOS split convention existed in repo truth.",
            "sharpe": 0.3751092454780985,
            "max_drawdown": 2.120802633322742,
            "n_obs": 55031,
            "trades": 934,
            "hit_rate": 0.364026,
            "profit_factor": 0.9581,
            "final_equity": -35556.0483,
            "total_pnl": -45556.0483,
            "gross_pnl": 13184.28,
            "fees_paid": 38149.5906,
            "slippage_paid": 19074.7953,
            "funding_paid": 1515.9424,
            "cost_drag_fraction": 4.4553,
            "dsr": 1.0,
            "walk_forward_efficiency": 1.0,
            "gates_passed": 3,
            "gates_total": 8,
        },
        "data_provenance": {
            "source_data_refs": ["ohlcv_1h"],
            "source_data_window_start": None,
            "source_data_window_end": None,
        },
        "derivation_record": {
            "derivation_method": "from_rep_artifact",
            "source_artifact_id": "REP-0001",
            "source_artifact_path": "research/experiments/REP-0001.report.json",
            "derivation_timestamp": "2026-04-30T12:00:00Z",
        },
        "pipeline_version": "pre_wp_5b",
        "linked_artifacts": ["REP-0001"],
        "retrospective_flag": True,
        "retrospective_disclosure": "Pytest retrospective fixture.",
        "linked_advisory_artifacts": ["PGAS-0001"],
    }


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_outcome_ledgers_relation_current_committed_state(conn):
    assert conn.execute("SELECT COUNT(*) FROM outcome_ledgers").fetchone()[0] == 27

    overview_rows = conn.execute(
        """
        SELECT
            outcome_id,
            candidate_id,
            outcome_kind,
            pipeline_version,
            lifecycle_state_during_window,
            retrospective_flag,
            source_artifact_id,
            source_artifact_path,
            linked_artifact_count,
            linked_advisory_artifact_count
        FROM v_outcome_ledger_overview
        ORDER BY outcome_id
        """
    ).fetchall()
    summary_rows = conn.execute(
        """
        SELECT candidate_id, outcome_kind, pipeline_version, outcome_count, retrospective_count
        FROM v_outcome_ledger_candidate_pipeline_summary
        ORDER BY candidate_id, pipeline_version
        """
    ).fetchall()

    assert overview_rows == [
        (
            "OL-0001",
            "H-001",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0002",
            "research/experiments/REP-0002.report.json",
            2,
            0,
        ),
        (
            "OL-0002",
            "H-005",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0001",
            "research/experiments/REP-0001.report.json",
            2,
            0,
        ),
        (
            "OL-0003",
            "H-002",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0003",
            "research/experiments/REP-0003.report.json",
            2,
            0,
        ),
        (
            "OL-0004",
            "H-003",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0004",
            "research/experiments/REP-0004.report.json",
            2,
            0,
        ),
        (
            "OL-0005",
            "H-004",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0005",
            "research/experiments/REP-0005.report.json",
            2,
            0,
        ),
        (
            "OL-0006",
            "H-006",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0006",
            "research/experiments/REP-0006.report.json",
            2,
            0,
        ),
        (
            "OL-0007",
            "H-007",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0007",
            "research/experiments/REP-0007.report.json",
            2,
            0,
        ),
        (
            "OL-0008",
            "H-008",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0008",
            "research/experiments/REP-0008.report.json",
            2,
            0,
        ),
        (
            "OL-0009",
            "H-009",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0009",
            "research/experiments/REP-0009.report.json",
            2,
            0,
        ),
        (
            "OL-0010",
            "H-010",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            True,
            "REP-0010",
            "research/experiments/REP-0010.report.json",
            2,
            0,
        ),
        (
            "OL-0011",
            "H-004",
            "research_oos",
            "post_wp_5b",
            "in_research",
            True,
            "REP-0011",
            "research/experiments/REP-0011.report.json",
            2,
            0,
        ),
        (
            "OL-0012",
            "H-004",
            "research_oos",
            "post_wp_5b",
            "in_research",
            False,
            "REP-0012",
            "research/experiments/REP-0012.report.json",
            2,
            0,
        ),
        (
            "OL-0013",
            "H-004",
            "research_oos",
            "post_wp_5b",
            "in_research",
            False,
            "REP-0013",
            "research/experiments/REP-0013.report.json",
            2,
            0,
        ),
        (
            "OL-0014",
            "H-004",
            "research_oos",
            "post_wp_5b",
            "in_research",
            False,
            "REP-0014",
            "research/experiments/REP-0014.report.json",
            2,
            0,
        ),
        (
            "OL-0015",
            "H-004",
            "research_oos",
            "post_wp_5b",
            "in_research",
            False,
            "REP-0015",
            "research/experiments/REP-0015.report.json",
            2,
            0,
        ),
        (
            "OL-0016",
            "H-001",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0016",
            "research/experiments/REP-0016.report.json",
            2,
            0,
        ),
        (
            "OL-0017",
            "H-001",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0017",
            "research/experiments/REP-0017.report.json",
            2,
            0,
        ),
        (
            "OL-0018",
            "H-001",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0018",
            "research/experiments/REP-0018.report.json",
            2,
            0,
        ),
        (
            "OL-0019",
            "H-001",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0019",
            "research/experiments/REP-0019.report.json",
            2,
            0,
        ),
        (
            "OL-0020",
            "H-005",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0020",
            "research/experiments/REP-0020.report.json",
            2,
            0,
        ),
        (
            "OL-0021",
            "H-005",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0021",
            "research/experiments/REP-0021.report.json",
            2,
            0,
        ),
        (
            "OL-0022",
            "H-005",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0022",
            "research/experiments/REP-0022.report.json",
            2,
            0,
        ),
        (
            "OL-0023",
            "H-005",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0023",
            "research/experiments/REP-0023.report.json",
            2,
            0,
        ),
        (
            "OL-0024",
            "H-006",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0024",
            "research/experiments/REP-0024.report.json",
            2,
            0,
        ),
        (
            "OL-0025",
            "H-006",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0025",
            "research/experiments/REP-0025.report.json",
            2,
            0,
        ),
        (
            "OL-0026",
            "H-002",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0026",
            "research/experiments/REP-0026.report.json",
            2,
            0,
        ),
        (
            "OL-0027",
            "H-002",
            "research_oos",
            "pre_wp_5b",
            "in_research",
            False,
            "REP-0027",
            "research/experiments/REP-0027.report.json",
            2,
            0,
        ),
    ]
    assert summary_rows == [
        ("H-001", "research_oos", "pre_wp_5b", 5, 1),
        ("H-002", "research_oos", "pre_wp_5b", 3, 1),
        ("H-003", "research_oos", "pre_wp_5b", 1, 1),
        ("H-004", "research_oos", "post_wp_5b", 5, 1),
        ("H-004", "research_oos", "pre_wp_5b", 1, 1),
        ("H-005", "research_oos", "pre_wp_5b", 5, 1),
        ("H-006", "research_oos", "pre_wp_5b", 3, 1),
        ("H-007", "research_oos", "pre_wp_5b", 1, 1),
        ("H-008", "research_oos", "pre_wp_5b", 1, 1),
        ("H-009", "research_oos", "pre_wp_5b", 1, 1),
        ("H-010", "research_oos", "pre_wp_5b", 1, 1),
    ]

    for view_name in {
        "v_integrity_outcome_ledger_refs",
        "v_integrity_outcome_ledger_window_bounds",
        "v_integrity_outcome_ledger_derivation",
        "v_integrity_outcome_ledger_scope",
    }:
        rows = conn.execute(f'SELECT * FROM "{view_name}"').fetchall()

        assert rows == []


def test_outcome_ledgers_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", tmp_path / "missing_outcome_ledgers")

    connection = init_duckdb()
    try:
        assert connection.execute("SELECT COUNT(*) FROM outcome_ledgers").fetchone()[0] == 0
        assert connection.execute("SELECT * FROM v_outcome_ledger_overview").fetchall() == []
    finally:
        connection.close()


def test_outcome_ledger_views_are_listed(conn):
    assert OUTCOME_LEDGER_VIEWS <= set(list_views(conn))


def test_temp_valid_outcome_ledger_appears_in_overview_and_summary(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", _base_outcome())
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        overview_rows = connection.execute(
            """
            SELECT
                outcome_id,
                candidate_id,
                outcome_kind,
                pipeline_version,
                lifecycle_state_during_window,
                retrospective_flag,
                source_artifact_id,
                source_artifact_path,
                linked_artifact_count,
                linked_advisory_artifact_count
            FROM v_outcome_ledger_overview
            """
        ).fetchall()
        summary_rows = connection.execute(
            """
            SELECT candidate_id, outcome_kind, pipeline_version, outcome_count, retrospective_count
            FROM v_outcome_ledger_candidate_pipeline_summary
            """
        ).fetchall()

        assert overview_rows == [
            (
                "OL-9001",
                "H-005",
                "research_oos",
                "pre_wp_5b",
                "in_research",
                True,
                "REP-0001",
                "research/experiments/REP-0001.report.json",
                1,
                1,
            )
        ]
        assert summary_rows == [("H-005", "research_oos", "pre_wp_5b", 1, 1)]
    finally:
        connection.close()


def test_temp_valid_outcome_ledger_integrity_views_empty(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", _base_outcome())
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        for view_name in {
            "v_integrity_outcome_ledger_refs",
            "v_integrity_outcome_ledger_window_bounds",
            "v_integrity_outcome_ledger_derivation",
            "v_integrity_outcome_ledger_scope",
        }:
            assert connection.execute(f'SELECT * FROM "{view_name}"').fetchall() == []
    finally:
        connection.close()


def test_temp_invalid_outcome_ledger_refs_emit_stable_issues(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    payload = _base_outcome()
    payload["candidate_id"] = "H-999"
    payload["derivation_record"]["source_artifact_id"] = "REP-9999"
    payload["linked_artifacts"] = ["EXP-9999"]
    payload["linked_advisory_artifacts"] = ["PGAS-9999"]
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        issue_types = {
            row[0]
            for row in connection.execute("SELECT issue_type FROM v_integrity_outcome_ledger_refs").fetchall()
        }

        assert {
            "outcome_unknown_candidate_ref",
            "outcome_unknown_rep_ref",
            "outcome_unknown_linked_artifact_ref",
            "outcome_unknown_linked_advisory_ref",
        } <= issue_types
    finally:
        connection.close()


def test_temp_invalid_outcome_ledger_windows_emit_stable_issue(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    payload = _base_outcome()
    payload["evaluation_window_start"] = "2026-02-01"
    payload["evaluation_window_end"] = "2026-01-01"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_outcome_ledger_window_bounds"
            ).fetchall()
        }

        assert issue_types == {"outcome_window_start_after_end"}
    finally:
        connection.close()


def test_temp_invalid_outcome_ledger_derivation_emit_stable_issue(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    payload = _base_outcome()
    payload["derivation_record"]["source_artifact_path"] = "research/experiments/REP-0011.report.json"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        rows = connection.execute(
            "SELECT issue_type FROM v_integrity_outcome_ledger_derivation"
        ).fetchall()

        assert rows == [("outcome_source_artifact_mismatch",)]
    finally:
        connection.close()


def test_temp_invalid_outcome_ledger_scope_emit_stable_issues(monkeypatch, tmp_path):
    outcome_ledgers_dir = tmp_path / "research" / "outcome_ledgers"
    payload = _base_outcome()
    payload["schema_version"] = "v2"
    payload["outcome_kind"] = "paper_oos"
    payload["lifecycle_state_during_window"] = "paper_active"
    payload["pipeline_version"] = "future_pipeline"
    _write_json(outcome_ledgers_dir / "OL-9001.outcome_ledger.json", payload)
    monkeypatch.setattr(query_layer, "OUTCOME_LEDGERS_DIR", outcome_ledgers_dir)

    connection = init_duckdb()
    try:
        issue_types = {
            row[0]
            for row in connection.execute("SELECT issue_type FROM v_integrity_outcome_ledger_scope").fetchall()
        }

        assert issue_types == {
            "outcome_invalid_schema_version",
            "outcome_invalid_kind",
            "outcome_invalid_lifecycle_state",
            "outcome_invalid_pipeline_version",
        }
    finally:
        connection.close()


def test_existing_query_layer_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE outcome_ledger_fixture AS SELECT 1 AS x")
