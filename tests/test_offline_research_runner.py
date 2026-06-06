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


def _write_15m_ohlcv_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "canonical_15m_ohlcv_fixture.csv"
    index = pd.date_range("2026-01-01T00:00:00Z", periods=96, freq="15min")
    close = []
    pattern = [100.0] * 20 + [94.0, 98.0, 101.0, 90.0, 96.0, 102.0, 88.0, 100.0]
    while len(close) < len(index):
        close.extend(pattern)
    close = close[: len(index)]
    frame = pd.DataFrame(
        {
            "timestamp": index,
            "open": [value + 0.1 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        }
    )
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
    assert {row["data_coverage"]["timeframe"] for row in payload["variant_result_rows"]} == {"15m"}
    assert payload["parent_strategy_spec"]["strategy_spec_id"] == "STRAT-SPEC-0001"
    assert payload["parent_variant_manifest"]["variant_manifest_id"] == "VM-0001"
    assert payload["parent_sweep_plan"]["sweep_plan_id"] == "SWEEP-PLAN-0001"
    assert payload["committed_denominator_snapshot"]["committed_denominator"] == 7
    assert payload["outcome_category_counts"]["counts_sum"] == 7
    assert len(payload["variant_result_rows"]) == 7


def test_canonical_15m_scratch_result_population_validates(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    output_dir = tmp_path / "scratch_result_populations"
    expected_canonical_files = [runner.CANONICAL_RESULT_POPULATIONS_DIR / "RP-2134.result_population.json"]
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
