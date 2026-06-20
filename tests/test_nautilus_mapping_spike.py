from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from tools.simulators import nautilus_mapping_spike as spike


def test_fixture_chain_and_assumptions_are_repo_truth():
    fixture = spike.load_fixture()

    assert fixture.spec["strategy_spec_id"] == "STRAT-SPEC-0004"
    assert fixture.manifest["variant_manifest_id"] == "VM-0004"
    assert fixture.sweep["sweep_plan_id"] == "SWEEP-PLAN-0004"
    assert fixture.rp["result_population_id"] == "RP-2592"
    assert len(fixture.variants) == 8
    assert fixture.rp["sizing_metadata"]["sizing_mode"] == "dynamic_equity_target_leverage"


def test_report_runs_twice_and_reconciles_all_variants(tmp_path, monkeypatch):
    fixture = spike.load_fixture()
    rows = 4
    csv_path = tmp_path / "slice.csv"
    frame = pd.DataFrame(
        {
            "open_time": pd.date_range("2020-01-01", periods=rows, freq="15min", tz="UTC"),
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [10.0] * rows,
            "close_time_ms": [1577837699999 + index * 900000 for index in range(rows)],
        }
    )
    frame.to_csv(csv_path, index=False)
    checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    fixture.rp["data_coverage_summary"]["data_coverage_notes"] = [
        f"row_count={rows}",
        f"normalized_sha256={checksum}",
    ]
    monkeypatch.setattr(
        spike,
        "_compile_signals",
        lambda fixture, ohlcv: {
            variant["variant_id"]: pd.Series(0.0, index=ohlcv.index)
            for variant in fixture.variants
        },
    )
    calls = 0

    def fake_executor(fixture, ohlcv, signals):
        nonlocal calls
        calls += 1
        result = {}
        for index, variant in enumerate(fixture.variants):
            expected = fixture.rp["variant_result_rows"][index]["metrics"]
            result[variant["variant_id"]] = {
                "variant_id": variant["variant_id"],
                "parameters": variant["parameter_values"],
                "trade_count": expected["trade_count"],
                "open_position_count": 0,
                "final_equity": 10_000.0 * (1.0 + expected["return_pct"]),
                "return_pct": expected["return_pct"],
                "combined_fee_slippage_cost": 0.0,
                "allocated_fees": 0.0,
                "allocated_slippage": 0.0,
                "funding": 0.0,
                "total_orders": 0,
                "total_positions": 0,
            }
        result["_environment"] = {
            "nautilus_version": "test",
            "python_version": "test",
            "platform": "test",
        }
        return result

    report = spike.build_report(fixture=fixture, ohlcv_path=csv_path, executor=fake_executor)

    assert calls == 2
    assert report["decision_label"] == "VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE"
    assert report["determinism"]["normalized_identical"] is True
    assert len(report["reconciliation"]) == 8


def test_non_deterministic_runs_hit_hard_kill(tmp_path, monkeypatch):
    fixture = spike.load_fixture()
    csv_path = tmp_path / "slice.csv"
    frame = pd.DataFrame(
        {
            "open_time": pd.date_range("2020-01-01", periods=2, freq="15min", tz="UTC"),
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [100.5, 101.5],
            "volume": [10.0, 10.0],
            "close_time_ms": [1577837699999, 1577838599999],
        }
    )
    frame.to_csv(csv_path, index=False)
    checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    fixture.rp["data_coverage_summary"]["data_coverage_notes"] = [
        "row_count=2",
        f"normalized_sha256={checksum}",
    ]
    monkeypatch.setattr(
        spike,
        "_compile_signals",
        lambda fixture, ohlcv: {
            variant["variant_id"]: pd.Series(0.0, index=ohlcv.index)
            for variant in fixture.variants
        },
    )
    count = 0

    def changing_executor(fixture, ohlcv, signals):
        nonlocal count
        count += 1
        result = {}
        for index, variant in enumerate(fixture.variants):
            expected = fixture.rp["variant_result_rows"][index]["metrics"]
            result[variant["variant_id"]] = {
                "variant_id": variant["variant_id"],
                "parameters": variant["parameter_values"],
                "trade_count": expected["trade_count"],
                "open_position_count": 0,
                "final_equity": 10_000.0 + count,
                "return_pct": count / 10_000.0,
                "combined_fee_slippage_cost": 0.0,
                "allocated_fees": 0.0,
                "allocated_slippage": 0.0,
                "funding": 0.0,
                "total_orders": 0,
                "total_positions": 0,
            }
        result["_environment"] = {"nautilus_version": "test"}
        return result

    report = spike.build_report(fixture=fixture, ohlcv_path=csv_path, executor=changing_executor)

    assert report["decision_label"] == "INFEASIBLE_FOR_NOW"
    assert report["determinism"]["normalized_identical"] is False


def test_write_report_rejects_absolute_paths(tmp_path):
    report = {
        "labels": spike.LABELS,
        "package_id": spike.PACKAGE_ID,
        "decision_label": "INFEASIBLE_FOR_NOW",
        "report_checksum": "abc",
        "fixture": {
            "result_population_id": "RP-2592",
            "strategy_spec_id": "STRAT-SPEC-0004",
            "variant_manifest_id": "VM-0004",
            "sweep_plan_id": "SWEEP-PLAN-0004",
            "data_slice_identity": "slice",
            "row_count": 1,
            "variants_attempted": 0,
            "variants_expressible": 0,
        },
        "determinism": {
            "repeated_runs": False,
            "normalized_identical": False,
            "checksum_run_1": None,
            "checksum_run_2": None,
        },
        "reconciliation": [],
        "mapping": {"unsupported_semantics": [r"C:\\local\\file.csv"]},
        "boundary": {},
    }

    with pytest.raises(spike.MappingSpikeError, match="absolute path"):
        spike.write_report(report, tmp_path)
