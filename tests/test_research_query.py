import hashlib
import json
from pathlib import Path

import pytest

from tools.research_query import query_layer
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


def _valid_candidate_row(**overrides):
    row = {
        "candidate_id": "H-900",
        "name": "Fixture Candidate",
        "status": "DRAFT",
        "overall_verdict": "PENDING",
        "strategy_family": "fixture",
        "timeframe": "15m",
        "information_inputs": ["ohlcv_15m"],
        "free_parameter_count": 1,
        "hypothesis_md_path": "research/hypotheses/H-900/HYPOTHESIS.md",
        "decision_record_path": None,
        "trial_ids": [],
        "pipeline_stage": "pre_registered",
        "created_at": "2026-05-30",
        "updated_at": "2026-05-30",
        "differentiation_summary": "Fixture candidate.",
        "notes": "pytest fixture",
    }
    row.update(overrides)
    return row


def _valid_plan(plan_id="EXP-9000", candidate_id="H-900"):
    return {
        "plan_id": plan_id,
        "candidate_id": candidate_id,
        "plan_type": "baseline",
        "rationale": "Fixture plan.",
        "hypothesis_to_test": "Fixture hypothesis.",
        "success_criteria": {
            "gates": ["D2-006"],
            "additional_criteria": ["Fixture criterion"],
        },
        "evaluation_window": {
            "in_sample": {"start": None, "end": None},
            "out_of_sample": {"start": None, "end": None},
        },
        "parameters": {"lookback": 12},
        "data_requirements": ["binance_um_perp_BTCUSDT_15m"],
        "pre_registration_date": "2026-05-30",
        "author": "pytest",
        "human_approval_required": False,
    }


def _valid_report(report_id="REP-9000", plan_id="EXP-9000", candidate_id="H-900"):
    return {
        "report_id": report_id,
        "plan_id": plan_id,
        "candidate_id": candidate_id,
        "execution_date": "2026-05-30",
        "trial_ids": ["trial-fixture"],
        "metrics": {
            "in_sample": {
                "sharpe": 0.0,
                "source_field": "fixture",
                "window_convention": "fixture",
            },
            "out_of_sample": {
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "trades": 1,
                "cost_drag_fraction": 0.0,
            },
        },
        "gate_results": [
            {
                "gate_id": "D2-006-G1",
                "threshold": 1.0,
                "observed": 0.0,
                "pass": False,
            }
        ],
        "overall_verdict": "NO-GO",
        "observations": "Fixture report.",
        "next_step_recommendation": "archive",
        "diagnostic_findings": ["Fixture diagnostic."],
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _init_temp_query_layer(monkeypatch, tmp_path, candidates, plans, reports):
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    trial_log_path = tmp_path / "research" / "trial_log.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        "\n".join(json.dumps(candidate) for candidate in candidates) + "\n",
        encoding="utf-8",
    )
    trial_log_path.write_text(json.dumps({"trial_id": "trial-fixture"}) + "\n", encoding="utf-8")

    for plan in plans:
        _write_json(experiments_dir / f"{plan['plan_id']}.plan.json", plan)
    for report in reports:
        _write_json(experiments_dir / f"{report['report_id']}.report.json", report)

    monkeypatch.setattr(query_layer, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(query_layer, "TRIAL_LOG_PATH", trial_log_path)
    monkeypatch.setattr(query_layer, "EXPERIMENTS_DIR", experiments_dir)

    return init_duckdb()


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


def test_integrity_plan_report_pairs_allows_valid_pre_execution_plan(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-012")
    plan = _valid_plan(plan_id="EXP-9012", candidate_id="H-012")
    report = _valid_report(report_id="REP-9000", plan_id="EXP-9001", candidate_id="H-012")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute("SELECT * FROM v_integrity_plan_report_pairs").fetchall()

        assert ("plan_without_report", "EXP-9012", "H-012", None) not in rows
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_unknown_candidate_without_report(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-900")
    plan = _valid_plan(plan_id="EXP-9000", candidate_id="H-999")
    report = _valid_report(report_id="REP-9000", plan_id="EXP-9001", candidate_id="H-900")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9000", "H-999", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_concluded_candidate_without_report(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(
        candidate_id="H-901",
        status="CONCLUDED",
        overall_verdict="NO-GO",
        pipeline_stage="baseline_tested",
        trial_ids=["trial-fixture"],
        decision_record_path="research/decisions/DEC-9001.md",
    )
    plan = _valid_plan(plan_id="EXP-9001", candidate_id="H-901")
    report = _valid_report(report_id="REP-9001", plan_id="EXP-9002", candidate_id="H-901")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9001", "H-901", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_candidate_with_trial_ids(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-902", trial_ids=["trial-fixture"])
    plan = _valid_plan(plan_id="EXP-9002", candidate_id="H-902")
    report = _valid_report(report_id="REP-9002", plan_id="EXP-9003", candidate_id="H-902")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9002", "H-902", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_candidate_with_decision_record(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(
        candidate_id="H-903",
        decision_record_path="research/decisions/DEC-9003.md",
    )
    plan = _valid_plan(plan_id="EXP-9003", candidate_id="H-903")
    report = _valid_report(report_id="REP-9003", plan_id="EXP-9004", candidate_id="H-903")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9003", "H-903", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_preserves_report_without_plan(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-904")
    plan = _valid_plan(plan_id="EXP-9004", candidate_id="H-904")
    report = _valid_report(report_id="REP-9004", plan_id="EXP-9999", candidate_id="H-904")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'report_without_plan'
            """
        ).fetchall()

        assert rows == [("report_without_plan", "EXP-9999", "H-904", "REP-9004")]
    finally:
        connection.close()


def test_current_integrity_views_empty_under_pre_execution_refinement(conn):
    view_names = [
        row[0]
        for row in conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_type = 'VIEW'
              AND table_name LIKE 'v_integrity\\_%' ESCAPE '\\'
            ORDER BY table_name
            """
        ).fetchall()
    ]

    assert view_names
    for view_name in view_names:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


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
