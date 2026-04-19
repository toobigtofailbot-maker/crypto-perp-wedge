import hashlib
import json
from pathlib import Path

import pytest

from tools.research_query.query_layer import (
    EXPERIMENTS_DIR,
    REGISTRY_PATH,
    TRIAL_LOG_PATH,
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_named_view,
    run_sql,
)


REQUIRED_VIEWS = {
    "v_candidate_overview",
    "v_concluded_candidates",
    "v_experiment_instances",
    "v_oos_metrics_by_candidate",
    "v_is_metrics_by_candidate",
    "v_gate_results_flat",
    "v_candidate_by_family",
    "v_information_inputs",
    "v_integrity_plan_report_pairs",
    "v_integrity_candidate_refs",
}

EXPECTED_COLUMNS = {
    "v_candidate_overview": [
        "candidate_id",
        "name",
        "status",
        "overall_verdict",
        "strategy_family",
        "timeframe",
        "free_parameter_count",
        "pipeline_stage",
        "hypothesis_md_path",
        "decision_record_path",
        "trial_id_count",
    ],
    "v_experiment_instances": [
        "candidate_id",
        "plan_id",
        "report_id",
        "plan_type",
        "execution_date",
        "overall_verdict",
        "trial_id_count",
    ],
    "v_oos_metrics_by_candidate": [
        "candidate_id",
        "report_id",
        "strategy_family",
        "timeframe",
        "oos_sharpe",
        "oos_max_drawdown",
        "oos_total_trades",
        "oos_cost_drag",
    ],
    "v_is_metrics_by_candidate": [
        "candidate_id",
        "report_id",
        "strategy_family",
        "timeframe",
        "is_sharpe",
        "is_source_field",
        "is_window_convention",
    ],
    "v_gate_results_flat": [
        "candidate_id",
        "report_id",
        "gate_id",
        "threshold",
        "observed",
        "pass",
    ],
    "v_candidate_by_family": [
        "strategy_family",
        "timeframe",
        "n_candidates",
        "n_no_go",
        "n_pass",
        "n_conditional",
        "n_inconclusive",
    ],
    "v_information_inputs": [
        "candidate_id",
        "information_input",
    ],
}


def _jsonl_row_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _registry_candidate_ids() -> set[str]:
    return {
        json.loads(line)["candidate_id"]
        for line in REGISTRY_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _file_checksums(paths: list[Path]) -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_init_succeeds():
    connection = init_duckdb()
    connection.close()


def test_candidate_row_count(conn):
    expected_count = _jsonl_row_count(REGISTRY_PATH)

    actual_count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]

    assert actual_count == expected_count


def test_experiment_plan_count(conn):
    expected_count = len(list(EXPERIMENTS_DIR.glob("EXP-*.plan.json")))

    actual_count = conn.execute("SELECT COUNT(*) FROM exp_plans").fetchone()[0]

    assert actual_count == expected_count


def test_experiment_report_count(conn):
    expected_count = len(list(EXPERIMENTS_DIR.glob("REP-*.report.json")))

    actual_count = conn.execute("SELECT COUNT(*) FROM exp_reports").fetchone()[0]

    assert actual_count == expected_count


def test_named_views_present(conn):
    view_names = set(list_views(conn))

    assert REQUIRED_VIEWS <= view_names
    for view_name in REQUIRED_VIEWS:
        conn.execute(f'SELECT * FROM "{view_name}" LIMIT 1').fetchall()


def test_named_views_return_expected_columns(conn):
    for view_name, expected_columns in EXPECTED_COLUMNS.items():
        rows = conn.execute(f'SELECT * FROM "{view_name}" LIMIT 0')
        actual_columns = [description[0] for description in rows.description]

        assert actual_columns == expected_columns


def test_candidate_overview_contains_all_registered_candidates(conn):
    expected_candidate_ids = _registry_candidate_ids()

    rows = conn.execute("SELECT candidate_id FROM v_candidate_overview").fetchall()
    actual_candidate_ids = {row[0] for row in rows}

    assert actual_candidate_ids == expected_candidate_ids


def test_oos_metrics_only_concluded(conn):
    non_concluded_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM v_oos_metrics_by_candidate AS metrics
        JOIN candidates AS candidates
          ON metrics.candidate_id = candidates.candidate_id
        WHERE candidates.status <> 'CONCLUDED'
        """
    ).fetchone()[0]

    assert non_concluded_count == 0


def test_integrity_plan_report_pairs_empty_under_healthy_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_plan_report_pairs").fetchall()

    assert rows == []


def test_integrity_candidate_refs_empty_under_healthy_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_candidate_refs").fetchall()

    assert rows == []


def test_report_trial_ids_resolve_to_trial_log(conn):
    missing_trial_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM exp_reports AS reports,
        UNNEST(reports.trial_ids) AS report_trial_ids(trial_id)
        LEFT JOIN trial_log AS trials
          ON report_trial_ids.trial_id = trials.trial_id
        WHERE trials.trial_id IS NULL
        """
    ).fetchone()[0]

    assert missing_trial_count == 0


def test_read_only_guard_rejects_insert(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "INSERT INTO candidates VALUES (1)")


def test_read_only_guard_rejects_delete(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "DELETE FROM candidates")


def test_read_only_guard_rejects_create(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE scratch AS SELECT 1 AS x")


def test_read_only_guard_rejects_external_file_reads(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "SELECT * FROM read_json_auto('research/candidate_registry.jsonl')")


def test_read_only_guard_rejects_pragma(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "PRAGMA show_tables")


def test_read_only_guard_rejects_call(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CALL something()")


def test_read_only_guard_rejects_multi_statement_select_then_drop(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "SELECT 1 AS x; DROP VIEW candidates")


def test_read_only_guard_rejects_multi_statement_with_trailing_write(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "WITH t AS (SELECT 1 AS x) SELECT * FROM t; DELETE FROM exp_plans")


def test_read_only_guard_accepts_select(conn):
    rows = run_sql(conn, "SELECT 1 AS x")

    assert rows == [{"x": 1}]


def test_read_only_guard_accepts_with_select(conn):
    rows = run_sql(conn, "WITH t AS (SELECT 1 AS x) SELECT * FROM t")

    assert rows == [{"x": 1}]


def test_no_research_files_modified(conn):
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
    ]
    before = _file_checksums(research_files)

    for view_name in list_views(conn):
        run_named_view(conn, view_name)
    run_sql(conn, "SELECT COUNT(*) AS n FROM candidates")
    run_sql(conn, "SELECT candidate_id FROM v_candidate_overview ORDER BY candidate_id")

    after = _file_checksums(research_files)

    assert after == before
