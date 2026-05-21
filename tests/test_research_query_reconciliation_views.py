import json
from pathlib import Path

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_sql,
)


RECONCILIATION_VIEWS = {
    "v_reconciliation_overview",
    "v_reconciliation_candidate_pipeline_summary",
    "v_integrity_reconciliation_refs",
    "v_integrity_reconciliation_scope",
    "v_integrity_reconciliation_expectation_source",
    "v_integrity_reconciliation_derivation",
    "v_integrity_reconciliation_realized_metrics",
}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _committed_metrics(outcome_id: str = "OL-0002") -> dict:
    path = query_layer.REPO_ROOT / "research" / "outcome_ledgers" / f"{outcome_id}.outcome_ledger.json"
    return json.loads(path.read_text(encoding="utf-8"))["metrics"]


def _base_rec(reconciliation_id: str = "REC-9001") -> dict:
    metrics = _committed_metrics()
    return {
        "schema_version": "v1",
        "reconciliation_id": reconciliation_id,
        "candidate_id": "H-005",
        "outcome_id": "OL-0002",
        "outcome_kind": "research_oos",
        "pipeline_version": "pre_wp_5b",
        "expectation_source_type": "exp_success_criteria",
        "expectation_source_artifact_id": "EXP-0001",
        "expectation_source_artifact_path": "research/experiments/EXP-0001.plan.json",
        "expectation_extracted": {
            "source_type": "exp_success_criteria",
            "source_artifact_id": "EXP-0001",
            "source_artifact_path": "research/experiments/EXP-0001.plan.json",
            "extraction_method": "pytest fixture",
            "extracted_at": "2026-05-04T12:00:00Z",
            "metric_expectations": [
                {
                    "metric_name": "sharpe",
                    "expected_operator": "gte",
                    "expected_value": 1.0,
                    "expected_unit": None,
                    "source_field_path": "success_criteria.gates",
                    "source_text": "Fixture expectation",
                }
            ],
        },
        "realized_metrics": metrics,
        "comparison": {
            "metric_comparisons": [
                {
                    "metric_name": "sharpe",
                    "expected_value": 1.0,
                    "realized_value": metrics["sharpe"],
                    "delta_absolute": metrics["sharpe"] - 1.0,
                    "delta_relative": metrics["sharpe"] - 1.0,
                    "comparison_verdict": "not_met",
                    "comparison_notes": "Fixture comparison.",
                }
            ]
        },
        "overall_verdict": "none_met",
        "interpretation": "Pytest fixture REC.",
        "derivation_record": {
            "derivation_method": "pytest fixture",
            "source_artifact_id": "OL-0002",
            "source_artifact_path": "research/outcome_ledgers/OL-0002.outcome_ledger.json",
            "derivation_timestamp": "2026-05-04T12:00:00Z",
            "source_outcome_id": "OL-0002",
            "expectation_source_type": "exp_success_criteria",
        },
        "retrospective_flag": True,
        "retrospective_disclosure": "Pytest retrospective fixture.",
        "linked_advisory_artifacts": [],
        "linked_lifecycle_artifacts": [],
    }


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_reconciliations_relation_registered_empty_with_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(query_layer, "RECONCILIATIONS_DIR", tmp_path / "missing_reconciliations")

    connection = init_duckdb()
    try:
        assert connection.execute("SELECT COUNT(*) FROM reconciliations").fetchone()[0] == 0
        assert connection.execute("SELECT * FROM v_reconciliation_overview").fetchall() == []
    finally:
        connection.close()


def test_reconciliation_views_are_listed(conn):
    assert RECONCILIATION_VIEWS <= set(list_views(conn))


def test_committed_reconciliation_corpus_appears_in_views_and_integrity_empty(conn):
    overview_rows = conn.execute(
        """
        SELECT
            reconciliation_id,
            candidate_id,
            outcome_id,
            outcome_kind,
            pipeline_version,
            expectation_source_type,
            expectation_source_artifact_id,
            overall_verdict,
            retrospective_flag,
            derivation_method
        FROM v_reconciliation_overview
        ORDER BY reconciliation_id
        """
    ).fetchall()
    summary_rows = conn.execute(
        """
        SELECT
            candidate_id,
            outcome_kind,
            pipeline_version,
            expectation_source_type,
            reconciliation_count,
            overall_verdicts
        FROM v_reconciliation_candidate_pipeline_summary
        """
    ).fetchall()

    exp_rows = [
        (
            "REC-0001",
            "H-001",
            "OL-0001",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0002",
            "none_met",
            True,
            "manual_retrospective_wp9w_seed_v1",
        ),
        (
            "REC-0002",
            "H-005",
            "OL-0002",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0001",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0003",
            "H-002",
            "OL-0003",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0003",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0004",
            "H-003",
            "OL-0004",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0004",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0005",
            "H-004",
            "OL-0005",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0005",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0006",
            "H-006",
            "OL-0006",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0006",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0007",
            "H-007",
            "OL-0007",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0007",
            "none_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0008",
            "H-008",
            "OL-0008",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0008",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0009",
            "H-009",
            "OL-0009",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0009",
            "none_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0010",
            "H-010",
            "OL-0010",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0010",
            "partially_met",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0011",
            "H-004",
            "OL-0011",
            "research_oos",
            "post_wp_5b",
            "exp_success_criteria",
            "EXP-0011",
            "insufficient_evidence",
            True,
            "manual_retrospective_wp9x_backfill_v1",
        ),
        (
            "REC-0012",
            "H-001",
            "OL-0001",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            True,
            "manual_retrospective_wp10b_d2_006_seed_v1",
        ),
    ]
    d2_rows = [
        (
            "REC-0013",
            "H-005",
            "OL-0002",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0014",
            "H-002",
            "OL-0003",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0015",
            "H-003",
            "OL-0004",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0016",
            "H-004",
            "OL-0005",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0017",
            "H-006",
            "OL-0006",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0018",
            "H-007",
            "OL-0007",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0019",
            "H-008",
            "OL-0008",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0020",
            "H-009",
            "OL-0009",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0021",
            "H-010",
            "OL-0010",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0022",
            "H-004",
            "OL-0011",
            "research_oos",
            "post_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            True,
            "manual_retrospective_wp10c_d2_006_backfill_v1",
        ),
        (
            "REC-0023",
            "H-004",
            "OL-0012",
            "research_oos",
            "post_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            False,
            "manual_forward_wp10t_d2_006_rec_append_v1",
        ),
        (
            "REC-0024",
            "H-004",
            "OL-0013",
            "research_oos",
            "post_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            False,
            "manual_forward_wp10y_d2_006_rec_append_v1",
        ),
    ]
    rec_0025_row = [
        (
            "REC-0025",
            "H-004",
            "OL-0014",
            "research_oos",
            "post_wp_5b",
            "exp_success_criteria",
            "EXP-0011",
            "insufficient_evidence",
            False,
            "manual_forward_wp12af_exp_success_rec_append_v1",
        )
    ]
    rec_0026_row = [
        (
            "REC-0026",
            "H-004",
            "OL-0015",
            "research_oos",
            "post_wp_5b",
            "exp_success_criteria",
            "EXP-0011",
            "insufficient_evidence",
            False,
            "manual_forward_wp12ai_exp_success_rec_append_v1",
        )
    ]
    rec_0027_row = [
        (
            "REC-0027",
            "H-001",
            "OL-0016",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            False,
            "manual_forward_wp12as_d2_006_rec_append_v1",
        )
    ]
    rec_0028_row = [
        (
            "REC-0028",
            "H-001",
            "OL-0017",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            False,
            "manual_forward_wp12av_d2_006_rec_append_v1",
        )
    ]
    rec_0029_row = [
        (
            "REC-0029",
            "H-001",
            "OL-0018",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0002",
            "none_met",
            False,
            "manual_forward_wp12ay_exp_success_rec_append_v1",
        )
    ]
    rec_0030_row = [
        (
            "REC-0030",
            "H-001",
            "OL-0019",
            "research_oos",
            "pre_wp_5b",
            "exp_success_criteria",
            "EXP-0002",
            "partially_met",
            False,
            "manual_forward_wp12bb_exp_success_rec_append_v1",
        )
    ]
    rec_0031_row = [
        (
            "REC-0031",
            "H-005",
            "OL-0020",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "partially_met",
            False,
            "manual_forward_wp12bg_d2_006_rec_append_v1",
        )
    ]
    rec_0032_row = [
        (
            "REC-0032",
            "H-005",
            "OL-0021",
            "research_oos",
            "pre_wp_5b",
            "d2_006_gates",
            "D2-006",
            "none_met",
            False,
            "manual_forward_wp12bm_d2_006_rec_append_v1",
        )
    ]
    assert (
        overview_rows
        == exp_rows
        + d2_rows
        + rec_0025_row
        + rec_0026_row
        + rec_0027_row
        + rec_0028_row
        + rec_0029_row
        + rec_0030_row
        + rec_0031_row
        + rec_0032_row
    )
    assert len(overview_rows) == 32
    assert [row[0] for row in overview_rows] == [f"REC-{idx:04d}" for idx in range(1, 33)]
    assert {
        row[2] for row in overview_rows if row[5] == "d2_006_gates"
    } == {f"OL-{idx:04d}" for idx in range(1, 14)} | {"OL-0016", "OL-0017", "OL-0020", "OL-0021"}
    assert {
        row[5]: sum(1 for candidate in overview_rows if candidate[5] == row[5])
        for row in overview_rows
    } == {
        "exp_success_criteria": 15,
        "d2_006_gates": 17,
    }
    assert sorted(summary_rows) == sorted(
        [
            ("H-001", "research_oos", "pre_wp_5b", "exp_success_criteria", 3, ["none_met", "partially_met"]),
            ("H-001", "research_oos", "pre_wp_5b", "d2_006_gates", 3, ["none_met", "partially_met"]),
            ("H-002", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["partially_met"]),
            ("H-002", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-003", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["partially_met"]),
            ("H-003", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-004", "research_oos", "post_wp_5b", "d2_006_gates", 3, ["partially_met"]),
            ("H-004", "research_oos", "post_wp_5b", "exp_success_criteria", 3, ["insufficient_evidence"]),
            ("H-004", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["partially_met"]),
            ("H-004", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-005", "research_oos", "pre_wp_5b", "d2_006_gates", 3, ["none_met", "partially_met"]),
            ("H-005", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-006", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["none_met"]),
            ("H-006", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-007", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["none_met"]),
            ("H-007", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["none_met"]),
            ("H-008", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["none_met"]),
            ("H-008", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
            ("H-009", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["none_met"]),
            ("H-009", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["none_met"]),
            ("H-010", "research_oos", "pre_wp_5b", "d2_006_gates", 1, ["partially_met"]),
            ("H-010", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["partially_met"]),
        ]
    )
    assert max(row[4] for row in summary_rows) == 3
    assert sorted(
        row[:5]
        for row in summary_rows
        if row[4] == 3
    ) == [
        ("H-001", "research_oos", "pre_wp_5b", "d2_006_gates", 3),
        ("H-001", "research_oos", "pre_wp_5b", "exp_success_criteria", 3),
        ("H-004", "research_oos", "post_wp_5b", "d2_006_gates", 3),
        ("H-004", "research_oos", "post_wp_5b", "exp_success_criteria", 3),
        ("H-005", "research_oos", "pre_wp_5b", "d2_006_gates", 3),
    ]
    assert sorted(
        (row[0], row[2], row[4], row[5], row[6]) for row in overview_rows if row[1] == "H-004"
    ) == [
        ("REC-0005", "OL-0005", "pre_wp_5b", "exp_success_criteria", "EXP-0005"),
        ("REC-0011", "OL-0011", "post_wp_5b", "exp_success_criteria", "EXP-0011"),
        ("REC-0016", "OL-0005", "pre_wp_5b", "d2_006_gates", "D2-006"),
        ("REC-0022", "OL-0011", "post_wp_5b", "d2_006_gates", "D2-006"),
        ("REC-0023", "OL-0012", "post_wp_5b", "d2_006_gates", "D2-006"),
        ("REC-0024", "OL-0013", "post_wp_5b", "d2_006_gates", "D2-006"),
        ("REC-0025", "OL-0014", "post_wp_5b", "exp_success_criteria", "EXP-0011"),
        ("REC-0026", "OL-0015", "post_wp_5b", "exp_success_criteria", "EXP-0011"),
    ]
    for view_name in {
        "v_integrity_reconciliation_refs",
        "v_integrity_reconciliation_scope",
        "v_integrity_reconciliation_expectation_source",
        "v_integrity_reconciliation_derivation",
        "v_integrity_reconciliation_realized_metrics",
    }:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_temp_valid_reconciliation_appears_in_overview_and_summary(monkeypatch, tmp_path):
    reconciliations_dir = tmp_path / "research" / "reconciliations"
    _write_json(reconciliations_dir / "REC-9001.reconciliation.json", _base_rec())
    monkeypatch.setattr(query_layer, "RECONCILIATIONS_DIR", reconciliations_dir)

    connection = init_duckdb()
    try:
        overview_rows = connection.execute(
            """
            SELECT
                reconciliation_id,
                candidate_id,
                outcome_id,
                outcome_kind,
                pipeline_version,
                expectation_source_type,
                expectation_source_artifact_id,
                overall_verdict,
                retrospective_flag,
                derivation_method,
                derivation_timestamp
            FROM v_reconciliation_overview
            """
        ).fetchall()
        summary_rows = connection.execute(
            """
            SELECT
                candidate_id,
                outcome_kind,
                pipeline_version,
                expectation_source_type,
                reconciliation_count,
                overall_verdicts
            FROM v_reconciliation_candidate_pipeline_summary
            """
        ).fetchall()

        assert overview_rows == [
            (
                "REC-9001",
                "H-005",
                "OL-0002",
                "research_oos",
                "pre_wp_5b",
                "exp_success_criteria",
                "EXP-0001",
                "none_met",
                True,
                "pytest fixture",
                "2026-05-04T12:00:00Z",
            )
        ]
        assert summary_rows == [
            ("H-005", "research_oos", "pre_wp_5b", "exp_success_criteria", 1, ["none_met"])
        ]
    finally:
        connection.close()


def test_temp_valid_reconciliation_integrity_views_empty(monkeypatch, tmp_path):
    reconciliations_dir = tmp_path / "research" / "reconciliations"
    _write_json(reconciliations_dir / "REC-9001.reconciliation.json", _base_rec())
    monkeypatch.setattr(query_layer, "RECONCILIATIONS_DIR", reconciliations_dir)

    connection = init_duckdb()
    try:
        for view_name in {
            "v_integrity_reconciliation_refs",
            "v_integrity_reconciliation_scope",
            "v_integrity_reconciliation_expectation_source",
            "v_integrity_reconciliation_derivation",
            "v_integrity_reconciliation_realized_metrics",
        }:
            assert connection.execute(f'SELECT * FROM "{view_name}"').fetchall() == []
    finally:
        connection.close()


def test_temp_invalid_reconciliation_integrity_views_emit_stable_issues(monkeypatch, tmp_path):
    reconciliations_dir = tmp_path / "research" / "reconciliations"
    payload = _base_rec()
    payload["candidate_id"] = "H-999"
    payload["outcome_kind"] = "paper_oos"
    payload["pipeline_version"] = "future_pipeline"
    payload["expectation_source_artifact_id"] = "EXP-9999"
    payload["expectation_extracted"]["source_artifact_id"] = "EXP-9999"
    payload["derivation_record"]["source_outcome_id"] = "OL-9999"
    payload["realized_metrics"]["sharpe"] = 9.9
    payload["linked_advisory_artifacts"] = ["PGAS-9999"]
    _write_json(reconciliations_dir / "REC-9001.reconciliation.json", payload)
    monkeypatch.setattr(query_layer, "RECONCILIATIONS_DIR", reconciliations_dir)

    connection = init_duckdb()
    try:
        ref_issue_types = {
            row[0]
            for row in connection.execute("SELECT issue_type FROM v_integrity_reconciliation_refs").fetchall()
        }
        scope_issue_types = {
            row[0]
            for row in connection.execute("SELECT issue_type FROM v_integrity_reconciliation_scope").fetchall()
        }
        expectation_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_reconciliation_expectation_source"
            ).fetchall()
        }
        derivation_issue_types = {
            row[0]
            for row in connection.execute("SELECT issue_type FROM v_integrity_reconciliation_derivation").fetchall()
        }
        realized_issue_types = {
            row[0]
            for row in connection.execute(
                "SELECT issue_type FROM v_integrity_reconciliation_realized_metrics"
            ).fetchall()
        }

        assert {
            "reconciliation_unknown_candidate_ref",
            "reconciliation_outcome_candidate_mismatch",
            "reconciliation_unknown_linked_advisory_ref",
        } <= ref_issue_types
        assert {
            "reconciliation_invalid_kind",
            "reconciliation_invalid_pipeline_version",
            "reconciliation_outcome_kind_mismatch",
            "reconciliation_pipeline_version_mismatch",
        } <= scope_issue_types
        assert {"reconciliation_unknown_exp_source"} <= expectation_issue_types
        assert {"reconciliation_source_outcome_mismatch"} <= derivation_issue_types
        assert realized_issue_types == {"reconciliation_realized_metric_mismatch"}
    finally:
        connection.close()


def test_existing_query_layer_read_only_guard_still_rejects_writes(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE reconciliation_fixture AS SELECT 1 AS x")


def test_committed_rec_cross_source_q05_cost_drag_non_positive_posture(conn):
    q05_sql = (
        query_layer.REPO_ROOT
        / "research"
        / "briefs"
        / "2026-04-rec_cross_expectation_source_consumer"
        / "queries"
        / "Q05.sql"
    ).read_text(encoding="utf-8")

    rows = run_sql(conn, q05_sql)
    posture_by_rec = {
        row["reconciliation_id"]: row["cost_drag_non_positive_gross_pnl_posture"]
        for row in rows
    }
    compared_with_non_positive = [
        row["reconciliation_id"]
        for row in rows
        if row["cost_drag_non_positive_gross_pnl_posture"]
        == "compared_despite_non_positive_gross_pnl_pre_wp10c_seed_requires_followup"
    ]

    assert {
        rec_id: posture_by_rec[rec_id]
        for rec_id in ("REC-0012", "REC-0017", "REC-0019")
    } == {
        "REC-0012": "skipped_due_to_non_positive_gross_pnl",
        "REC-0017": "skipped_due_to_non_positive_gross_pnl",
        "REC-0019": "skipped_due_to_non_positive_gross_pnl",
    }
    assert compared_with_non_positive == []


def test_existing_outcome_ledger_behavior_preserved(conn):
    assert conn.execute("SELECT COUNT(*) FROM v_outcome_ledger_overview").fetchone()[0] == 22
    assert conn.execute(
        """
        SELECT pipeline_version, COUNT(*)
        FROM v_outcome_ledger_overview
        GROUP BY pipeline_version
        ORDER BY pipeline_version
        """
    ).fetchall() == [("post_wp_5b", 5), ("pre_wp_5b", 17)]
    assert conn.execute(
        """
        SELECT candidate_id, pipeline_version, outcome_count
        FROM v_outcome_ledger_candidate_pipeline_summary
        WHERE candidate_id = 'H-004'
        ORDER BY pipeline_version
        """
    ).fetchall() == [
        ("H-004", "post_wp_5b", 5),
        ("H-004", "pre_wp_5b", 1),
    ]
