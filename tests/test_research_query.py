import hashlib
import json
from pathlib import Path

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    EXPERIMENTS_DIR,
    REGISTRY_PATH,
    STRATEGY_SPECS_DIR,
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
    "v_strategy_spec_overview",
    "v_strategy_spec_parameters",
    "v_strategy_spec_condition_groups",
    "v_strategy_spec_backtest_assumptions",
    "v_integrity_strategy_spec_non_authority",
    "v_integrity_strategy_spec_bounds",
    "v_integrity_strategy_spec_hash_readiness",
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
    "v_strategy_spec_overview": [
        "strategy_spec_id",
        "title",
        "status",
        "source_type",
        "instrument_family",
        "market_type",
        "primary_timeframe",
        "direction",
        "free_parameter_count",
        "max_free_parameters",
        "max_condition_group_depth",
        "operator_depth_bound",
        "hash_status",
        "intended_for_variant_manifest",
        "approval_scope",
    ],
    "v_strategy_spec_parameters": [
        "strategy_spec_id",
        "parameter_name",
        "parameter_type",
        "role",
        "default_value",
        "range_min",
        "range_max",
        "range_step",
        "included_in_variant_generation",
        "rationale",
    ],
    "v_strategy_spec_condition_groups": [
        "strategy_spec_id",
        "section",
        "group_id",
        "group_role",
        "logic",
        "condition_count",
        "subgroup_count",
        "declared_depth",
    ],
    "v_strategy_spec_backtest_assumptions": [
        "strategy_spec_id",
        "fee_side_assumption",
        "exchange_constraints_disclosed",
        "funding_notional_mode",
        "slippage_model",
        "fill_mode",
        "order_size_assumption",
        "liquidity_capacity_assumption",
        "liquidation_mode",
        "maintenance_margin_assumption",
        "mark_price_source",
        "bar_path_assumption",
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


def _operand(ref="close") -> dict:
    return {
        "operand_type": "data_ref",
        "ref": ref,
        "field": "close",
        "timeframe": "1h",
        "lookback": {"bars": 1},
    }


def _condition(condition_id: str = "COND-1") -> dict:
    return {
        "condition_id": condition_id,
        "condition_role": "required",
        "left_operand": _operand("close"),
        "operator": "gt",
        "right_operand": {
            "operand_type": "constant",
            "ref": 100.0,
            "field": None,
            "timeframe": None,
            "lookback": None,
        },
        "units": None,
        "notes": None,
    }


def _condition_group(group_id: str = "GROUP-1") -> dict:
    return {
        "group_id": group_id,
        "group_role": "required",
        "logic": "all",
        "conditions": [_condition()],
        "subgroups": [],
        "notes": None,
    }


def _strategy_parameter(name: str = "lookback") -> dict:
    return {
        "name": name,
        "label": None,
        "description": None,
        "type": "integer",
        "units": "bars",
        "default": 20,
        "range": {
            "min": 5,
            "max": 50,
            "step": 5,
            "inclusive_min": True,
            "inclusive_max": True,
        },
        "allowed_values": [],
        "is_free_parameter": True,
        "included_in_variant_generation": True,
        "role": "entry",
        "rationale": "Pytest fixture parameter.",
        "constraints": [],
    }


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _valid_strategy_spec(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    return {
        "schema_version": "v1",
        "strategy_spec_id": strategy_spec_id,
        "title": "Pytest Strategy Spec",
        "short_name": "pytest-spec",
        "status": "draft",
        "non_execution_declaration": _true_flags(
            "human_review_surface_only",
            "not_executable",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_sweep_authority",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
        ),
        "provenance": {
            "source_type": "manual_idea",
            "source_refs": ["pytest-fixture"],
            "prepared_by": "pytest",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "rationale": "Pytest fixture.",
            "source_constraints": [],
            "unresolved_claims": [],
        },
        "instruments": {
            "symbols": ["BTCUSDT"],
            "instrument_family": "crypto_perp",
            "venue_assumption": "Binance USDT-M",
            "market_type": "perpetual",
            "directions_allowed": ["long"],
            "leverage_assumption": None,
            "exchange_constraint_refs": [],
            "blockers": [],
        },
        "timeframe_and_data": {
            "primary_timeframe": "1h",
            "confirmation_timeframes": [],
            "host_data_refs": [
                {
                    "stream": "ohlcv",
                    "timeframe": "1h",
                    "field": "close",
                    "availability": "required",
                }
            ],
            "gap_handling_assumption": None,
            "missing_data_blockers": [],
        },
        "entry_logic": {
            "direction": "long",
            "groups": [_condition_group()],
            "notes": None,
        },
        "exit_logic": {
            "groups": [_condition_group("EXIT-GROUP-1")],
            "max_holding_period": {"enabled": False, "bars": None},
            "notes": None,
        },
        "risk_model": {
            "sizing_intent": "review_only",
            "exposure_limits": [],
            "stop_distance": None,
            "target_distance": None,
            "leverage_visibility": None,
            "liquidation_sensitivity_notes": None,
        },
        "filters": {
            "groups": [_condition_group("FILTER-GROUP-1")],
            "none_declared": False,
        },
        "free_parameters": {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; "
                "maxItems 5 enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [_strategy_parameter()],
            "no_free_parameters_declared": False,
        },
        "constraints": {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [],
            "none_declared": True,
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "none",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_sweep_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
        "lineage": {
            "parent_refs": [],
            "supersedes": [],
            "amendment_of": None,
        },
        "hash_pinning": {
            "canonical_spec_hash": None,
            "hash_algorithm": None,
            "hash_scope_version": None,
            "hash_scope": [],
            "hash_status": "not_computed",
        },
        "pre_registration_support": {
            "intended_for_variant_manifest": False,
            "variant_manifest_ref": None,
            "frozen_snapshot_ref": None,
        },
        "backtest_realism_assumptions": {
            "fee_side_assumption": "maker_taker_visible",
            "exchange_constraints_disclosed": True,
            "funding_notional_mode": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": "fixture size only",
            "liquidity_capacity_assumption": "fixture capacity only",
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
        },
        "max_condition_group_depth": 3,
    }


def _init_temp_query_layer(
    monkeypatch,
    tmp_path,
    candidates,
    plans,
    reports,
    strategy_specs=None,
):
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    trial_log_path = tmp_path / "research" / "trial_log.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"

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
    for strategy_spec in strategy_specs or []:
        _write_json(
            strategy_specs_dir / f"{strategy_spec['strategy_spec_id']}.strategy_spec.json",
            strategy_spec,
        )

    monkeypatch.setattr(query_layer, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(query_layer, "TRIAL_LOG_PATH", trial_log_path)
    monkeypatch.setattr(query_layer, "EXPERIMENTS_DIR", experiments_dir)
    monkeypatch.setattr(query_layer, "STRATEGY_SPECS_DIR", strategy_specs_dir)

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


def test_strategy_spec_relation_zero_instance_repo_state(conn):
    rows = conn.execute("SELECT * FROM strategy_specs").fetchall()

    assert rows == []


def test_strategy_spec_views_zero_rows_under_current_zero_instance_state(conn):
    for view_name in [
        "v_strategy_spec_overview",
        "v_strategy_spec_parameters",
        "v_strategy_spec_condition_groups",
        "v_strategy_spec_backtest_assumptions",
    ]:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_strategy_spec_integrity_views_empty_under_current_zero_instance_state(conn):
    for view_name in [
        "v_integrity_strategy_spec_non_authority",
        "v_integrity_strategy_spec_bounds",
        "v_integrity_strategy_spec_hash_readiness",
    ]:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_temp_strategy_spec_appears_in_read_only_views(monkeypatch, tmp_path):
    candidate = _valid_candidate_row()
    plan = _valid_plan()
    report = _valid_report()
    strategy_spec = _valid_strategy_spec()

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [candidate],
        [plan],
        [report],
        strategy_specs=[strategy_spec],
    )
    try:
        overview = connection.execute(
            """
            SELECT strategy_spec_id, instrument_family, market_type, primary_timeframe,
                   direction, free_parameter_count, max_free_parameters, hash_status,
                   intended_for_variant_manifest, approval_scope
            FROM v_strategy_spec_overview
            """
        ).fetchall()
        parameters = connection.execute(
            """
            SELECT strategy_spec_id, parameter_name, parameter_type, role, range_min,
                   range_max, range_step, included_in_variant_generation
            FROM v_strategy_spec_parameters
            """
        ).fetchall()
        condition_groups = connection.execute(
            """
            SELECT strategy_spec_id, section, group_id, condition_count, subgroup_count,
                   declared_depth
            FROM v_strategy_spec_condition_groups
            ORDER BY section, group_id
            """
        ).fetchall()
        assumptions = connection.execute(
            """
            SELECT strategy_spec_id, fee_side_assumption, exchange_constraints_disclosed,
                   order_size_assumption, liquidity_capacity_assumption
            FROM v_strategy_spec_backtest_assumptions
            """
        ).fetchall()

        assert overview == [
            (
                "STRAT-SPEC-9001",
                "crypto_perp",
                "perpetual",
                "1h",
                "long",
                1,
                5,
                "not_computed",
                False,
                "none",
            )
        ]
        assert parameters == [
            ("STRAT-SPEC-9001", "lookback", "integer", "entry", 5.0, 50.0, 5.0, True)
        ]
        assert condition_groups == [
            ("STRAT-SPEC-9001", "entry_logic", "GROUP-1", 1, 0, 1),
            ("STRAT-SPEC-9001", "exit_logic", "EXIT-GROUP-1", 1, 0, 1),
            ("STRAT-SPEC-9001", "filters", "FILTER-GROUP-1", 1, 0, 1),
        ]
        assert assumptions == [
            (
                "STRAT-SPEC-9001",
                "maker_taker_visible",
                True,
                "fixture size only",
                "fixture capacity only",
            )
        ]
    finally:
        connection.close()


def test_strategy_spec_non_authority_integrity_flags_visible_violation(monkeypatch, tmp_path):
    strategy_spec = _valid_strategy_spec()
    strategy_spec["non_execution_declaration"]["not_runtime_authority"] = False
    strategy_spec["review"]["non_authority_acknowledgement"]["not_recommendation_authority"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[strategy_spec],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_non_authority
            ORDER BY source_field
            """
        ).fetchall()

        assert rows == [
            (
                "STRAT-SPEC-9001",
                "non_execution_declaration.not_runtime_authority",
                "true",
                "false",
            ),
            (
                "STRAT-SPEC-9001",
                "review.non_authority_acknowledgement.not_recommendation_authority",
                "true",
                "false",
            ),
        ]
    finally:
        connection.close()


def test_strategy_spec_bounds_integrity_flags_visible_violation(monkeypatch, tmp_path):
    strategy_spec = _valid_strategy_spec()
    strategy_spec["max_condition_group_depth"] = 4
    strategy_spec["free_parameters"]["max_free_parameters"] = 6
    strategy_spec["free_parameters"]["parameters"] = [
        _strategy_parameter(f"p{i}") for i in range(6)
    ]

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[strategy_spec],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_bounds
            ORDER BY source_field
            """
        ).fetchall()

        assert rows == [
            ("STRAT-SPEC-9001", "free_parameters.max_free_parameters", "5", "6"),
            ("STRAT-SPEC-9001", "free_parameters.parameters.count", "<=5", "6"),
            ("STRAT-SPEC-9001", "max_condition_group_depth", "3", "4"),
        ]
    finally:
        connection.close()


def test_strategy_spec_hash_readiness_integrity_flags_visible_violation(monkeypatch, tmp_path):
    missing_hash = _valid_strategy_spec("STRAT-SPEC-9001")
    missing_hash["hash_pinning"]["hash_status"] = "computed"
    missing_hash["hash_pinning"]["canonical_spec_hash"] = None

    prereg_without_hash = _valid_strategy_spec("STRAT-SPEC-9002")
    prereg_without_hash["pre_registration_support"]["intended_for_variant_manifest"] = True
    prereg_without_hash["hash_pinning"]["hash_status"] = "not_computed"

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[missing_hash, prereg_without_hash],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_hash_readiness
            ORDER BY strategy_spec_id, source_field
            """
        ).fetchall()

        assert rows == [
            (
                "STRAT-SPEC-9001",
                "hash_pinning.canonical_spec_hash",
                "non-empty when hash_status=computed",
                None,
            ),
            (
                "STRAT-SPEC-9002",
                "hash_pinning.hash_status",
                "computed when intended_for_variant_manifest=true",
                "not_computed",
            ),
        ]
    finally:
        connection.close()


def test_querying_strategy_spec_views_does_not_modify_research_files(conn):
    strategy_spec_files = sorted(STRATEGY_SPECS_DIR.glob("*.json")) if STRATEGY_SPECS_DIR.exists() else []
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
        *strategy_spec_files,
    ]
    before = _file_checksums(research_files)

    for view_name in [
        "v_strategy_spec_overview",
        "v_strategy_spec_parameters",
        "v_strategy_spec_condition_groups",
        "v_strategy_spec_backtest_assumptions",
        "v_integrity_strategy_spec_non_authority",
        "v_integrity_strategy_spec_bounds",
        "v_integrity_strategy_spec_hash_readiness",
    ]:
        run_named_view(conn, view_name)

    after = _file_checksums(research_files)

    assert after == before


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
