import ast
import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from tests.test_validate_variant_sweep_artifacts import (
    _base_strategy_spec_for_variant,
    _base_sweep_plan,
    _base_variant_manifest,
    _hash_scope_payload,
    _write_json,
    sha256_prefixed,
)
from tools.registry.validate_result_populations import OUTCOME_CATEGORIES, validate_result_populations
from tools.research_runner import run_offline_sweep as runner
from tools.research_runner.spec_signal_compiler import compile_signal as real_compile_signal


D4_CATALOG_REF = (
    "binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m."
    "20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b"
)
D4_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)
D3_VALIDATION_REPORT_SHA256 = "785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c"
D2_IMPORT_REPORT_SHA256 = "543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad"
D4_CATALOG_ARTIFACT_SHA256 = "f7b98c4d7759b6ba0c9bf8559bcea5e3311d3abe877930da254aeca96f53105a"


def _fixture_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "research"
    return root / "strategy_specs", root / "variant_manifests", root / "sweep_plans"


def _refresh_manifest_hash(manifest: dict) -> None:
    manifest["manifest_hash_pinning"]["manifest_hash"] = None
    scoped = _hash_scope_payload(manifest, manifest["manifest_hash_pinning"]["hash_scope"])
    manifest["manifest_hash_pinning"]["manifest_hash"] = sha256_prefixed(scoped)


def _set_variant_count(manifest: dict, count: int) -> None:
    variants = []
    values = [10 + index * 10 for index in range(count)]
    manifest["population_governance"]["population_cap"]["max_variants"] = count
    manifest["parameter_axes"][0]["allowed_values"] = values
    manifest["parameter_axes"][0]["range"] = {
        "min": min(values),
        "max": max(values),
        "step": 10,
        "inclusive_min": True,
        "inclusive_max": True,
    }
    for index, value in enumerate(values, start=1):
        variants.append(
            {
                "variant_id": f"VAR-{index:06d}",
                "assignment_status": "included",
                "parameter_values": {"lookback": value},
                "parameter_value_hash": None,
                "axis_refs": ["AXIS-001"],
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {"generated_by_rule": "manual-grid", "generation_order": index},
            }
        )
    manifest["variant_assignments"] = variants
    declared = manifest["population_governance"]["declared_population"]
    declared.update(
        {
            "committed_population_count": count,
            "declared_variant_count": count,
            "included_variant_count": count,
            "excluded_variant_count": 0,
            "invalid_variant_count": 0,
            "not_attempted_variant_count": 0,
        }
    )
    manifest["population_governance"]["trial_budget"]["planned_trial_count"] = count
    manifest["population_governance"]["trial_budget"]["trial_budget_denominator"] = count
    manifest["population_governance"]["trial_budget"]["denominator_count"] = count


def _apply_status_counts(manifest: dict) -> None:
    declared = manifest["population_governance"]["declared_population"]
    counts = {"included": 0, "excluded": 0, "invalid": 0, "not_attempted": 0}
    for variant in manifest["variant_assignments"]:
        counts[variant["assignment_status"]] += 1
    declared["included_variant_count"] = counts["included"]
    declared["excluded_variant_count"] = counts["excluded"]
    declared["invalid_variant_count"] = counts["invalid"]
    declared["not_attempted_variant_count"] = counts["not_attempted"]


def _rebuild_sweep(manifest: dict) -> dict:
    sweep = _base_sweep_plan(manifest)
    count = manifest["population_governance"]["declared_population"]["committed_population_count"]
    included = [
        variant["variant_id"]
        for variant in manifest["variant_assignments"]
        if variant["assignment_status"] == "included"
    ]
    excluded = [
        variant["variant_id"]
        for variant in manifest["variant_assignments"]
        if variant["assignment_status"] == "excluded"
    ]
    sweep["parent_variant_manifest"]["manifest_population_count"] = count
    sweep["parent_variant_manifest"]["manifest_committed_population_count"] = count
    sweep["parent_variant_manifest"]["manifest_population_cap"] = manifest["population_governance"][
        "population_cap"
    ]["max_variants"]
    sweep["test_selection"]["selected_variant_ids"] = included
    sweep["test_selection"]["excluded_variant_ids"] = excluded
    sweep["trial_accounting"]["committed_population_count"] = count
    sweep["trial_accounting"]["selected_variant_count"] = len(included)
    sweep["trial_accounting"]["multiple_testing_denominator"] = count
    sweep["trial_accounting"]["not_attempted_variant_count"] = count
    return sweep


def _write_fixture(tmp_path: Path, manifest_mutator=None) -> tuple[Path, Path, Path, dict, dict, dict]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_dirs(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    if manifest_mutator is not None:
        manifest_mutator(manifest)
        _apply_status_counts(manifest)
        _refresh_manifest_hash(manifest)
    sweep_plan = _rebuild_sweep(manifest)
    strategy_path = strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json"
    manifest_path = variant_manifests_dir / "VM-0001.variant_manifest.json"
    sweep_path = sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json"
    _write_json(strategy_path, strategy_spec)
    _write_json(manifest_path, manifest)
    _write_json(sweep_path, sweep_plan)
    return strategy_path, manifest_path, sweep_path, strategy_spec, manifest, sweep_plan


def _run(strategy_path: Path, manifest_path: Path, sweep_path: Path, **kwargs):
    return runner.run_offline_sweep(
        strategy_path,
        manifest_path,
        sweep_path,
        **kwargs,
    )


def _canonical_parent_paths() -> tuple[Path, Path, Path]:
    root = runner.REPO_ROOT
    return (
        root / "research" / "strategy_specs" / "STRAT-SPEC-0001.strategy_spec.json",
        root / "research" / "variant_manifests" / "VM-0001.variant_manifest.json",
        root / "research" / "sweep_plans" / "SWEEP-PLAN-0001.sweep_plan.json",
    )


def _d4_artifact_paths() -> tuple[Path, Path]:
    root = (
        runner.REPO_ROOT
        / "research"
        / "data_slices"
        / "binance_usdtm_btcusdt_15m"
    )
    return (
        root / "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json",
        root / "binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json",
    )


def _write_15m_ohlcv_fixture(
    tmp_path: Path,
    *,
    timestamp_column: str = "timestamp",
    include_timestamp: bool = True,
    include_open_time: bool = False,
    include_open_time_ms: bool = False,
    timestamp_offset_minutes: int = 0,
    open_time_offset_minutes: int = 0,
    open_time_ms_offset_minutes: int = 0,
) -> Path:
    path = tmp_path / "canonical_15m_ohlcv_fixture.csv"
    index = pd.date_range("2026-01-01T00:00:00Z", periods=96, freq="15min")
    timestamp_index = index + pd.Timedelta(minutes=timestamp_offset_minutes)
    open_time_index = index + pd.Timedelta(minutes=open_time_offset_minutes)
    open_time_ms_index = index + pd.Timedelta(minutes=open_time_ms_offset_minutes)
    close = []
    pattern = [100.0] * 20 + [94.0, 98.0, 101.0, 90.0, 96.0, 102.0, 88.0, 100.0]
    while len(close) < len(index):
        close.extend(pattern)
    close = close[: len(index)]
    rows = {
        "open": [value + 0.1 for value in close],
        "high": [value + 1.0 for value in close],
        "low": [value - 1.0 for value in close],
        "close": close,
        "volume": [1000.0] * len(index),
    }
    if include_timestamp:
        rows[timestamp_column] = timestamp_index
    if include_open_time:
        rows["open_time"] = open_time_index
    if include_open_time_ms:
        rows["open_time_ms"] = [int(timestamp.timestamp() * 1000) for timestamp in open_time_ms_index]
        rows["close_time_ms"] = [value + 899_999 for value in rows["open_time_ms"]]
        rows["quote_asset_volume"] = [0.0] * len(index)
        rows["num_trades"] = [1] * len(index)
        rows["taker_buy_base_vol"] = [0.0] * len(index)
        rows["taker_buy_quote_vol"] = [0.0] * len(index)
        rows["ignore"] = [0] * len(index)
    ordered_columns = [
        column
        for column in (
            "timestamp",
            "open_time_ms",
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time_ms",
            "quote_asset_volume",
            "num_trades",
            "taker_buy_base_vol",
            "taker_buy_quote_vol",
            "ignore",
        )
        if column in rows
    ]
    frame = pd.DataFrame(rows)[ordered_columns]
    frame.to_csv(path, index=False)
    return path


def _identity_payload(result: dict) -> dict:
    payload = copy.deepcopy(result["result_population"])
    payload.pop("audit_envelope")
    return payload


def test_runner_api_dry_run_performs_no_file_write(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert result["output_path"] is None
    assert after == before


def test_cli_dry_run_prints_summary_and_writes_nothing(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.research_runner.run_offline_sweep",
            "--strategy-spec",
            str(strategy_path),
            "--variant-manifest",
            str(manifest_path),
            "--sweep-plan",
            str(sweep_path),
            "--deterministic-seed",
            "7",
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["dry_run"] is True
    assert after == before


def test_write_result_population_writes_one_temp_file_and_validates(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    output_dir = tmp_path / "output"

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        output_dir=output_dir,
        write_result_population=True,
        deterministic_seed=7,
    )

    written = list(output_dir.glob("*.result_population.json"))
    assert result["wrote"] is True
    assert len(written) == 1
    assert written[0].name == f"{result['result_population_id']}.result_population.json"
    assert validate_result_populations(
        result_populations_dir=output_dir,
        strategy_specs_dir=strategy_path.parent,
        variant_manifests_dir=manifest_path.parent,
        sweep_plans_dir=sweep_path.parent,
    ) == []


def test_one_result_row_per_committed_variant_and_counts_sum(tmp_path):
    def mutate(manifest: dict) -> None:
        _set_variant_count(manifest, 3)

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)
    payload = result["result_population"]

    assert len(payload["variant_result_rows"]) == 3
    assert payload["outcome_category_counts"]["counts_sum"] == 3
    assert payload["committed_denominator_snapshot"]["committed_denominator"] == 3


def test_closed_outcome_enum_preserved(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert tuple(OUTCOME_CATEGORIES) == runner.OUTCOME_CATEGORIES
    count_keys = set(result["outcome_category_counts"]) - {
        "counts_sum",
        "counts_sum_equals_committed_denominator",
    }
    assert count_keys == set(OUTCOME_CATEGORIES)


def test_per_variant_error_is_retained_and_run_continues(tmp_path):
    def mutate(manifest: dict) -> None:
        _set_variant_count(manifest, 3)
        manifest["variant_assignments"][1]["status_reason"] = "runner_fixture:errored"

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)
    rows = result["result_population"]["variant_result_rows"]

    assert [row["variant_id"] for row in rows] == ["VAR-000001", "VAR-000002", "VAR-000003"]
    assert rows[1]["outcome_category"] == "errored"
    assert rows[2]["outcome_category"] == "successful"


def test_missing_data_fixture_creates_data_unavailable_row(tmp_path):
    def mutate(manifest: dict) -> None:
        manifest["variant_assignments"][1]["status_reason"] = "runner_fixture:data_unavailable"

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert result["outcome_category_counts"]["data_unavailable"] == 1
    assert any(
        row["outcome_category"] == "data_unavailable"
        for row in result["result_population"]["variant_result_rows"]
    )


def test_infrastructure_abort_emits_not_attempted_rows_and_cli_nonzero(tmp_path):
    def mutate(manifest: dict) -> None:
        _set_variant_count(manifest, 3)
        manifest["variant_assignments"][0]["status_reason"] = "runner_fixture:infra_abort"

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.research_runner.run_offline_sweep",
            "--strategy-spec",
            str(strategy_path),
            "--variant-manifest",
            str(manifest_path),
            "--sweep-plan",
            str(sweep_path),
            "--deterministic-seed",
            "7",
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result["ok"] is False
    assert result["outcome_category_counts"]["aborted"] == 1
    assert result["outcome_category_counts"]["not_attempted"] == 2
    assert completed.returncode == 1


def test_repeat_run_determinism_identity_hash_scoped_payload(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    first = _run(strategy_path, manifest_path, sweep_path, run_label="one", deterministic_seed=7)
    second = _run(strategy_path, manifest_path, sweep_path, run_label="two", deterministic_seed=7)

    assert first["result_population_id"] == second["result_population_id"]
    assert _identity_payload(first) == _identity_payload(second)


def test_audit_envelope_run_label_excluded_from_determinism(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    first = _run(strategy_path, manifest_path, sweep_path, run_label="alpha", deterministic_seed=7)
    second = _run(strategy_path, manifest_path, sweep_path, run_label="beta", deterministic_seed=7)

    assert first["result_population"]["audit_envelope"] != second["result_population"]["audit_envelope"]
    assert first["result_population"]["result_population_identity_hash"] == second["result_population"][
        "result_population_identity_hash"
    ]


def test_parent_strategy_spec_hash_mismatch_stops_before_execution_and_write(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    strategy = json.loads(strategy_path.read_text(encoding="utf-8"))
    strategy["title"] = "Hash mismatch"
    _write_json(strategy_path, strategy)
    output_dir = tmp_path / "output"
    called = False

    def fake_backtest(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("should not execute")

    monkeypatch.setattr(runner, "run_backtest", fake_backtest)

    with pytest.raises(runner.OfflineSweepError):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
        )

    assert called is False
    assert not output_dir.exists()


def test_parent_manifest_hash_mismatch_stops_before_execution_and_write(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
    sweep["parent_variant_manifest"]["manifest_hash"] = "sha256:" + ("0" * 64)
    _write_json(sweep_path, sweep)
    output_dir = tmp_path / "output"
    monkeypatch.setattr(runner, "run_backtest", lambda *args, **kwargs: pytest.fail("executed"))

    with pytest.raises(runner.OfflineSweepError):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
        )

    assert not output_dir.exists()


def test_manifest_sweep_denominator_mismatch_stops_before_execution_and_write(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
    sweep["trial_accounting"]["committed_population_count"] = 999
    _write_json(sweep_path, sweep)
    output_dir = tmp_path / "output"
    monkeypatch.setattr(runner, "run_backtest", lambda *args, **kwargs: pytest.fail("executed"))

    with pytest.raises(runner.OfflineSweepError):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
        )

    assert not output_dir.exists()


def test_selected_variant_outside_manifest_stops_before_execution_and_write(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
    sweep["test_selection"]["selected_variant_ids"].append("VAR-999999")
    _write_json(sweep_path, sweep)
    output_dir = tmp_path / "output"
    monkeypatch.setattr(runner, "run_backtest", lambda *args, **kwargs: pytest.fail("executed"))

    with pytest.raises(runner.OfflineSweepError):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
        )

    assert not output_dir.exists()


def test_canonical_result_population_output_path_is_rejected(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="canonical"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=runner.CANONICAL_RESULT_POPULATIONS_DIR,
            write_result_population=True,
        )


def test_no_writes_outside_caller_supplied_output_dir(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    output_dir = tmp_path / "out"

    _run(
        strategy_path,
        manifest_path,
        sweep_path,
        output_dir=output_dir,
        write_result_population=True,
        deterministic_seed=7,
    )

    result_files = list(tmp_path.rglob("*.result_population.json"))
    assert result_files
    assert all(output_dir in path.parents for path in result_files)


def test_runtime_paper_live_protected_path_guard_imports_only_allowed_modules():
    module = importlib.import_module("tools.research_runner.run_offline_sweep")
    forbidden_module_prefixes = {
        "src.",
        "configs.",
        "scripts.g4",
        "broker",
        "exchange",
        "order",
        "paper",
        "live",
        "oms",
        "reconciliation",
        "risk",
        "safe_mode",
        "kill_switch",
    }
    source = Path(module.__file__).read_text(encoding="utf-8")
    parsed = ast.parse(source)
    imported = set()
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert module.__name__ == "tools.research_runner.run_offline_sweep"
    assert not any(
        name == forbidden or name.startswith(f"{forbidden}.")
        for name in imported
        for forbidden in forbidden_module_prefixes
    )


def test_no_authority_fields_appear_in_output(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)
    encoded = json.dumps(result["result_population"]).lower()

    forbidden = ["approval_action", "ranking_score", "readiness_update", "transition_trigger"]
    assert all(token not in encoded for token in forbidden)
    assert result["result_population"]["non_authority_declaration"]["not_runtime_authority"] is True


def test_schema_validator_query_files_unchanged_by_runner_execution(tmp_path):
    watched = [
        runner.REPO_ROOT / "research" / "schemas" / "result_population.schema.json",
        runner.REPO_ROOT / "tools" / "registry" / "validate_result_populations.py",
        runner.REPO_ROOT / "tools" / "research_query" / "query_layer.py",
        runner.REPO_ROOT / "tools" / "research_query" / "views.sql",
    ]
    before = {path: path.read_bytes() for path in watched}
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert {path: path.read_bytes() for path in watched} == before


def test_backtester_called_through_read_only_adapter_for_successful_variants(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    calls = []
    real_run_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append((args, kwargs))
        return real_run_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert len(calls) == result["outcome_category_counts"]["successful"]
    assert all(kwargs["bar_path_assumption"] == "next_open_close_mark" for _, kwargs in calls)


def test_adapter_does_not_modify_backtest_or_evaluation_files(tmp_path):
    watched = [runner.REPO_ROOT / "lib" / "backtest.py", runner.REPO_ROOT / "lib" / "evaluation.py"]
    before = {path: path.read_bytes() for path in watched}
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert {path: path.read_bytes() for path in watched} == before


def test_canonical_15m_path_compiles_frozen_variants_and_uses_15m_input(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    compile_calls = []
    backtest_calls = []
    real_backtest = runner.run_backtest

    def recording_compile(strategy_spec, variant_assignment, ohlcv, funding=None, indicator_catalog=None):
        compile_calls.append((strategy_spec, variant_assignment, ohlcv.copy(), funding.copy()))
        return real_compile_signal(
            strategy_spec,
            variant_assignment,
            ohlcv,
            funding=funding,
            indicator_catalog=indicator_catalog,
        )

    def recording_backtest(*args, **kwargs):
        backtest_calls.append((args, kwargs))
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "compile_signal", recording_compile)
    monkeypatch.setattr(runner, "_run_synthetic_backtest", lambda *args, **kwargs: pytest.fail("synthetic path used"))
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )
    payload = result["result_population"]

    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert len(compile_calls) == 7
    assert len(backtest_calls) == 7
    assert [call[1]["variant_id"] for call in compile_calls] == [f"VAR-{index:06d}" for index in range(1, 8)]
    assert [call[1]["parameter_values"]["entry_distance_threshold"] for call in compile_calls] == [
        0.005,
        0.01,
        0.015,
        0.02,
        0.03,
        0.04,
        0.05,
    ]
    entry_condition = compile_calls[0][0]["entry_logic"]["groups"][0]["conditions"][0]
    exit_condition = compile_calls[0][0]["exit_logic"]["groups"][0]["conditions"][0]
    assert entry_condition["left_operand"]["ref"] == "close"
    assert entry_condition["operator"] == "lt"
    assert entry_condition["right_operand"]["operand_type"] == "composed_operand"
    assert entry_condition["right_operand"]["composition_type"] == "scale_by_one_minus_parameter"
    assert exit_condition["left_operand"]["ref"] == "close"
    assert exit_condition["operator"] == "gte"
    assert exit_condition["right_operand"]["ref"] == "sma"
    assert all(call[2].index.to_series().diff().dropna().eq(pd.Timedelta(minutes=15)).all() for call in compile_calls)
    assert all(kwargs["interval"] == "15m" for _, kwargs in backtest_calls)
    assert payload["data_coverage_summary"]["timeframe"] == "15m"
    assert payload["data_coverage_summary"]["data_catalog_ref"] == runner.CANONICAL_15M_DATA_CATALOG_REF
    assert payload["data_coverage_summary"]["data_slice_identity"].startswith("csv_fixture:sha256:")
    assert runner.D4_PROVENANCE_MODE_NOTE not in payload["data_coverage_summary"]["data_coverage_notes"]
    assert {row["data_coverage"]["timeframe"] for row in payload["variant_result_rows"]} == {"15m"}
    assert payload["parent_strategy_spec"]["strategy_spec_id"] == "STRAT-SPEC-0001"
    assert payload["parent_variant_manifest"]["variant_manifest_id"] == "VM-0001"
    assert payload["parent_sweep_plan"]["sweep_plan_id"] == "SWEEP-PLAN-0001"
    assert payload["committed_denominator_snapshot"]["committed_denominator"] == 7
    assert payload["outcome_category_counts"]["counts_sum"] == 7
    assert len(payload["variant_result_rows"]) == 7


def test_canonical_15m_accepts_open_time_without_timestamp(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_timestamp=False,
        include_open_time=True,
    )

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert result["result_population"]["data_coverage_summary"]["timeframe"] == "15m"
    assert result["result_population"]["outcome_category_counts"]["counts_sum"] == 7


def test_canonical_15m_accepts_open_time_ms_without_timestamp_or_open_time(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_timestamp=False,
        include_open_time_ms=True,
    )

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert result["result_population"]["data_coverage_summary"]["timeframe"] == "15m"
    assert result["result_population"]["outcome_category_counts"]["counts_sum"] == 7


def test_canonical_15m_fails_closed_without_supported_timestamp_column(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path, include_timestamp=False)

    with pytest.raises(runner.OfflineSweepError, match="timestamp, open_time, open_time_ms"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )


def test_canonical_15m_fails_closed_on_conflicting_timestamp_and_open_time(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_open_time=True,
        open_time_offset_minutes=15,
    )

    with pytest.raises(runner.OfflineSweepError, match="conflicting timestamp columns"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )


@pytest.mark.parametrize("timestamp_column", ["timestamp", "open_time"])
def test_canonical_15m_fails_closed_on_invalid_timestamp_strings(tmp_path, timestamp_column):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_timestamp=timestamp_column == "timestamp",
        include_open_time=timestamp_column == "open_time",
    )
    frame = pd.read_csv(ohlcv_path)
    frame.loc[0, timestamp_column] = "not-a-timestamp"
    frame.to_csv(ohlcv_path, index=False)
    output_dir = tmp_path / "scratch_result_populations"

    with pytest.raises(runner.OfflineSweepError, match="invalid timestamps"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )

    assert not output_dir.exists()


@pytest.mark.parametrize("bad_open_time_ms", ["not-ms", "1704067200000.5"])
def test_canonical_15m_fails_closed_on_invalid_open_time_ms_values(tmp_path, bad_open_time_ms):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_timestamp=False,
        include_open_time_ms=True,
    )
    frame = pd.read_csv(ohlcv_path)
    frame["open_time_ms"] = frame["open_time_ms"].astype("object")
    frame.loc[0, "open_time_ms"] = bad_open_time_ms
    frame.to_csv(ohlcv_path, index=False)
    output_dir = tmp_path / "scratch_result_populations"

    with pytest.raises(
        runner.OfflineSweepError,
        match="open_time_ms contains invalid epoch milliseconds",
    ):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=output_dir,
            write_result_population=True,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )

    assert not output_dir.exists()


def test_canonical_15m_d4_style_open_time_columns_preserve_d4_provenance(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        include_timestamp=False,
        include_open_time=True,
        include_open_time_ms=True,
    )
    catalog_path, import_report_path = _d4_artifact_paths()

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_report_path,
        deterministic_seed=7,
    )
    coverage = result["result_population"]["data_coverage_summary"]

    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert coverage["data_catalog_ref"] == D4_CATALOG_REF
    assert coverage["data_slice_identity"] == D4_SLICE_IDENTITY
    assert runner.D4_PROVENANCE_MODE_NOTE in coverage["data_coverage_notes"]


def test_canonical_15m_d4_provenance_records_d4_catalog_and_slice_identity(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_report_path,
        deterministic_seed=7,
    )
    payload = result["result_population"]
    coverage = payload["data_coverage_summary"]
    notes = set(coverage["data_coverage_notes"])

    assert coverage["data_catalog_ref"] == D4_CATALOG_REF
    assert coverage["data_slice_identity"] == D4_SLICE_IDENTITY
    assert runner.D4_PROVENANCE_MODE_NOTE in notes
    assert f"d3_validation_report_sha256={D3_VALIDATION_REPORT_SHA256}" in notes
    assert f"d2_import_report_sha256={D2_IMPORT_REPORT_SHA256}" in notes
    assert f"d4_catalog_artifact_sha256={D4_CATALOG_ARTIFACT_SHA256}" in notes
    assert "row_count=220128" in notes
    assert "expected_row_count=220128" in notes
    assert "start_utc=2020-01-01T00:00:00Z" in notes
    assert "end_utc=2026-04-11T23:45:00Z" in notes
    assert "gap_count=0" in notes
    assert "missing_bar_count=0" in notes
    assert "gaps=[]" in notes
    assert "duplicate_group_count=0" in notes
    assert "duplicate_row_count=0" in notes
    assert "duplicates=[]" in notes
    assert "raw_source_sha256=343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4" in notes
    assert "normalized_sha256=c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab" in notes
    assert {row["data_coverage"]["data_catalog_ref"] for row in payload["variant_result_rows"]} == {
        D4_CATALOG_REF
    }
    assert {row["data_coverage"]["data_slice_identity"] for row in payload["variant_result_rows"]} == {
        D4_SLICE_IDENTITY
    }


def test_canonical_15m_d4_provenance_fails_closed_without_catalog_ref(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()
    broken_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    del broken_catalog["catalog_ref"]
    broken_path = tmp_path / "broken_catalog.json"
    _write_json(broken_path, broken_catalog)

    with pytest.raises(runner.OfflineSweepError, match="catalog_ref"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            d4_catalog_slice_path=broken_path,
            d2_import_report_path=import_report_path,
            deterministic_seed=7,
        )


def test_canonical_15m_d4_provenance_fails_closed_without_slice_identity(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()
    broken_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    del broken_catalog["slice_identity"]["data_slice_identity"]
    broken_path = tmp_path / "broken_catalog.json"
    _write_json(broken_path, broken_catalog)

    with pytest.raises(runner.OfflineSweepError, match="slice_identity.data_slice_identity"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            d4_catalog_slice_path=broken_path,
            d2_import_report_path=import_report_path,
            deterministic_seed=7,
        )


def test_canonical_15m_d4_provenance_fails_closed_without_d3_identity(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()
    broken_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    del broken_catalog["validation_report"]["sha256"]
    broken_path = tmp_path / "broken_catalog.json"
    _write_json(broken_path, broken_catalog)

    with pytest.raises(runner.OfflineSweepError, match="validation_report.sha256"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            d4_catalog_slice_path=broken_path,
            d2_import_report_path=import_report_path,
            deterministic_seed=7,
        )


def test_canonical_15m_d4_provenance_rejects_fixture_disguised_as_d4(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()
    broken_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    broken_catalog["catalog_ref"] = runner.CANONICAL_15M_DATA_CATALOG_REF
    broken_catalog["slice_identity"]["data_slice_identity"] = "csv_fixture:sha256:" + "0" * 64
    broken_path = tmp_path / "broken_catalog.json"
    _write_json(broken_path, broken_catalog)

    with pytest.raises(runner.OfflineSweepError, match="fixture data_catalog_ref"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            d4_catalog_slice_path=broken_path,
            d2_import_report_path=import_report_path,
            deterministic_seed=7,
        )


def test_canonical_15m_scratch_result_population_validates(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    output_dir = tmp_path / "scratch_result_populations"
    expected_canonical_files = [
        runner.CANONICAL_RESULT_POPULATIONS_DIR / "RP-2134.result_population.json",
        runner.CANONICAL_RESULT_POPULATIONS_DIR / "RP-4492.result_population.json",
        runner.CANONICAL_RESULT_POPULATIONS_DIR / "RP-6688.result_population.json",
    ]
    canonical_files_before = (
        sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json"))
        if runner.CANONICAL_RESULT_POPULATIONS_DIR.exists()
        else []
    )

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        output_dir=output_dir,
        write_result_population=True,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    written = list(output_dir.glob("*.result_population.json"))
    assert result["wrote"] is True
    assert len(written) == 1
    assert result["result_population"]["data_coverage_summary"]["timeframe"] == "15m"
    assert validate_result_populations(
        result_populations_dir=output_dir,
        strategy_specs_dir=strategy_path.parent,
        variant_manifests_dir=manifest_path.parent,
        sweep_plans_dir=sweep_path.parent,
    ) == []
    canonical_files_after = (
        sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json"))
        if runner.CANONICAL_RESULT_POPULATIONS_DIR.exists()
        else []
    )
    assert canonical_files_before == expected_canonical_files
    assert canonical_files_after == expected_canonical_files
    assert written[0].parent == output_dir


def test_canonical_15m_output_is_deterministic_for_same_fixture(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        run_label="first",
        deterministic_seed=7,
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        run_label="second",
        deterministic_seed=7,
    )

    assert first["result_population_id"] == second["result_population_id"]
    assert _identity_payload(first) == _identity_payload(second)
    assert "execution_provenance_class=fixture_offline" in first["result_population"][
        "execution_context"
    ]["environment_summary"]


def test_canonical_15m_fixture_and_d4_provenance_have_distinct_result_population_ids(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()

    fixture = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )
    d4 = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_report_path,
        deterministic_seed=7,
    )

    assert fixture["result_population_id"] != d4["result_population_id"]
    assert fixture["result_population"]["data_coverage_summary"]["data_catalog_ref"] == (
        runner.CANONICAL_15M_DATA_CATALOG_REF
    )
    assert fixture["result_population"]["data_coverage_summary"]["data_slice_identity"].startswith(
        "csv_fixture:sha256:"
    )
    assert d4["result_population"]["data_coverage_summary"]["data_catalog_ref"] == D4_CATALOG_REF
    assert d4["result_population"]["data_coverage_summary"]["data_slice_identity"] == D4_SLICE_IDENTITY
    assert "execution_provenance_class=fixture_offline" in fixture["result_population"][
        "execution_context"
    ]["environment_summary"]
    assert "execution_provenance_class=canonical_real_data" in d4["result_population"][
        "execution_context"
    ]["environment_summary"]


def test_result_population_id_basis_uses_provenance_identity_components():
    parent_args = {
        "strategy_hash": "sha256:" + "1" * 64,
        "manifest_hash": "sha256:" + "2" * 64,
        "sweep_hash": "sha256:" + "3" * 64,
        "backtest_assumption_summary": {"records_assumptions_only": True},
        "data_slice_identity": D4_SLICE_IDENTITY,
        "d3_validation_identity": D3_VALIDATION_REPORT_SHA256,
        "execution_provenance_class": "canonical_real_data",
    }

    baseline = runner._deterministic_result_population_id(**parent_args)

    for key, replacement in (
        ("data_slice_identity", D4_SLICE_IDENTITY + ":changed"),
        ("d3_validation_identity", "0" * 64),
        ("execution_provenance_class", "fixture_offline"),
    ):
        changed = dict(parent_args)
        changed[key] = replacement
        assert runner._deterministic_result_population_id(**changed) != baseline


def test_canonical_15m_d4_provenance_output_is_deterministic(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    catalog_path, import_report_path = _d4_artifact_paths()

    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_report_path,
        run_label="first",
        deterministic_seed=7,
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_report_path,
        run_label="second",
        deterministic_seed=7,
    )

    assert first["result_population_id"] == second["result_population_id"]
    assert _identity_payload(first) == _identity_payload(second)
    assert first["result_population"]["data_coverage_summary"]["data_catalog_ref"] == D4_CATALOG_REF
    assert first["result_population"]["data_coverage_summary"]["data_slice_identity"] == D4_SLICE_IDENTITY
    assert "execution_provenance_class=canonical_real_data" in first["result_population"][
        "execution_context"
    ]["environment_summary"]
