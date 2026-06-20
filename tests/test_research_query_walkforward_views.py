import shutil
from pathlib import Path

from tools.research_query import query_layer
from tools.research_query.query_layer import init_duckdb, run_named_view


FIXTURE = Path(__file__).parent / "fixtures" / "walkforward" / "valid_walkforward_fold_manifest.json"


def test_walkforward_views_expose_manifest_and_fold_rows(tmp_path, monkeypatch):
    manifests_dir = tmp_path / "walkforward_fold_manifests"
    manifests_dir.mkdir()
    shutil.copyfile(FIXTURE, manifests_dir / "WFM-0001.walkforward_fold_manifest.json")
    monkeypatch.setattr(query_layer, "WALKFORWARD_FOLD_MANIFESTS_DIR", manifests_dir)

    conn = init_duckdb()

    manifests = run_named_view(conn, "v_walkforward_manifest_overview")
    folds = run_named_view(conn, "v_walkforward_fold_boundaries")

    assert manifests == [
        {
            "manifest_id": "WFM-0001",
            "schema_version": "v1",
            "created_at_utc": "2026-06-20 00:00:00",
            "source_commit": "2348f89",
            "strategy_spec_id": "STRAT-SPEC-0002",
            "variant_manifest_id": "VM-0002",
            "sweep_plan_id": "SWEEP-PLAN-0002",
            "data_slice_id": "BTCUSDT-15m-D4",
            "timeframe": "15m",
            "timezone": "UTC",
            "boundary_semantics": "start_inclusive_end_exclusive",
            "window_policy_id": "rolling_1y_selection_90d_evaluation_v1",
            "window_type": "rolling",
            "selection_rule_id": "carry_full_population",
            "selection_rule_type": "carry_full_population",
            "fold_count": 2,
        }
    ]
    assert [row["fold_id"] for row in folds] == ["FOLD-001", "FOLD-002"]
    assert folds[0]["planned_result_population_ref"] == "planned:RP-WF-0001-FOLD-001"
    assert folds[1]["result_population_ref"] == "RP-7520"


def test_walkforward_integrity_views_clean_for_valid_fixture(tmp_path, monkeypatch):
    manifests_dir = tmp_path / "walkforward_fold_manifests"
    manifests_dir.mkdir()
    shutil.copyfile(FIXTURE, manifests_dir / "WFM-0001.walkforward_fold_manifest.json")
    monkeypatch.setattr(query_layer, "WALKFORWARD_FOLD_MANIFESTS_DIR", manifests_dir)

    conn = init_duckdb()

    assert run_named_view(conn, "v_integrity_walkforward_fold_chronology") == []
    assert run_named_view(conn, "v_integrity_walkforward_fold_denominator") == []
    assert run_named_view(conn, "v_integrity_walkforward_non_authority") == []
