import ast
import copy
import importlib
import json
import math
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
from tools.data.materialize_takerflow_features import (
    D4_OUTPUT_COLUMNS,
    materialize_canonical_kline_takerflow_features,
)
from tools.research_domain.feature_data import (
    CANONICAL_KLINE_TAKER_DERIVATION_VERSION,
    CANONICAL_KLINE_TAKER_SOURCE_CLASS,
    D4_TAKER_DERIVATION_VERSION,
    D4_TAKER_FEATURE_DEFINITIONS,
    D4_TAKER_PARENT_FIELDS,
    D4_TAKER_SOURCE_CLASS,
    build_feature_table_identity,
    build_source_set_identity,
)


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
D4H_CATALOG_REF = (
    "binance_usdtm_btcusdt_ohlcv_4h.derived_offline_resample.4h."
    "20200101T000000Z.20260411T200000Z.sha256_4379d2f0fad5e79b"
)
D4H_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_4h:sha256:"
    "4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30"
)
D4H_CSV_SHA256 = "828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1"
D4H_VALIDATION_REPORT_SHA256 = "b995532fe76e5960740ffc86cc4e6bb22e4489c38e0920e611b8a1669814cfd8"
D4H_DERIVATION_REPORT_SHA256 = "44288299817bd7b11df91ee4335129987980e0e111e49a6ae5635632d1285933"
DYNAMIC_SIZING_METADATA = {
    "sizing_mode": runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
    "target_leverage": 1.0,
    "sizing_equity_basis": runner.DYNAMIC_SIZING_EQUITY_BASIS,
    "entry_reference_price_basis": runner.DYNAMIC_ENTRY_REFERENCE_PRICE_BASIS,
}


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


def _write_fixture(
    tmp_path: Path,
    manifest_mutator=None,
    strategy_mutator=None,
) -> tuple[Path, Path, Path, dict, dict, dict]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_dirs(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    if strategy_mutator is not None:
        strategy_mutator(strategy_spec)
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    if manifest_mutator is not None:
        manifest_mutator(manifest)
        _apply_status_counts(manifest)
        _refresh_manifest_hash(manifest)
    sweep_plan = _rebuild_sweep(manifest)
    sweep_plan["data_and_timeframe_assumptions"]["primary_timeframe"] = strategy_spec[
        "timeframe_and_data"
    ]["primary_timeframe"]
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


def _canonical_0006_parent_paths() -> tuple[Path, Path, Path]:
    root = runner.REPO_ROOT
    return (
        root / "research" / "strategy_specs" / "STRAT-SPEC-0006.strategy_spec.json",
        root / "research" / "variant_manifests" / "VM-0006.variant_manifest.json",
        root / "research" / "sweep_plans" / "SWEEP-PLAN-0006.sweep_plan.json",
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


def _d4h_artifact_paths() -> tuple[Path, Path, Path]:
    root = (
        runner.REPO_ROOT
        / "research"
        / "data_slices"
        / "binance_usdtm_btcusdt_4h"
    )
    return (
        root / "binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json",
        root / "binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json",
        root / "binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json",
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
    extra_columns: dict[str, list[float]] | None = None,
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
    if extra_columns:
        rows.update(extra_columns)
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
            *(extra_columns or {}).keys(),
        )
        if column in rows
    ]
    frame = pd.DataFrame(rows)[ordered_columns]
    frame.to_csv(path, index=False)
    return path


def _write_small_d4_metadata(tmp_path: Path, ohlcv_path: Path) -> tuple[Path, Path]:
    catalog_path, import_path = _d4_artifact_paths()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    import_report = json.loads(import_path.read_text(encoding="utf-8"))
    frame = pd.read_csv(ohlcv_path)
    digest = runner._sha256_file_hex(ohlcv_path)
    timestamps = pd.to_datetime(frame["timestamp"], utc=True)
    catalog["catalog_ref"] = "test_d4_feature_parent"
    catalog["slice_identity"]["data_slice_identity"] = (
        "binance_usdtm_btcusdt_ohlcv_15m:sha256:" + digest
    )
    catalog["normalized"]["sha256"] = digest
    catalog["range"].update(
        start_utc=timestamps.iloc[0].isoformat().replace("+00:00", "Z"),
        end_utc=timestamps.iloc[-1].isoformat().replace("+00:00", "Z"),
        row_count=len(frame),
        expected_row_count=len(frame),
    )
    import_report["normalized"]["sha256"] = digest
    out_catalog = tmp_path / "small.catalog.json"
    out_import = tmp_path / "small.import.json"
    _write_json(out_catalog, catalog)
    _write_json(out_import, import_report)
    return out_catalog, out_import


def _write_research_feature_fixture(
    tmp_path: Path,
    ohlcv_path: Path,
    *,
    timestamp_shift_minutes: int = 0,
    availability_shift_minutes: int | None = None,
    timeframe: str = "15m",
    parent_identity: str | None = None,
) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(ohlcv_path)
    timestamp_column = "timestamp" if "timestamp" in base.columns else "open_time"
    timestamps = pd.to_datetime(base[timestamp_column], utc=True) + pd.Timedelta(
        minutes=timestamp_shift_minutes
    )
    timeframe_delta = pd.to_timedelta(timeframe)
    available = timestamps + (
        timeframe_delta
        if availability_shift_minutes is None
        else pd.Timedelta(minutes=availability_shift_minutes)
    )
    sell = base["volume"] - base["taker_buy_base_vol"]
    ratio = [
        "" if value == 0 else format(buy / value, ".15g")
        for buy, value in zip(base["taker_buy_base_vol"], sell, strict=True)
    ]
    rows = pd.DataFrame(
        {
            "timestamp": timestamps.map(lambda value: value.strftime("%Y-%m-%dT%H:%M:%S.000Z")),
            "open_time_ms": timestamps.map(lambda value: int(value.timestamp() * 1000)),
            "feature_available_at": available.map(lambda value: value.strftime("%Y-%m-%dT%H:%M:%S.000Z")),
            "feature_available_at_ms": available.map(lambda value: int(value.timestamp() * 1000)),
            "taker_buy_volume": base["taker_buy_base_vol"],
            "taker_sell_volume": sell,
            "taker_buy_sell_ratio": ratio,
        }
    )[list(D4_OUTPUT_COLUMNS)]
    feature_path = tmp_path / "research_features.csv"
    rows.to_csv(feature_path, index=False, lineterminator="\n")
    feature_sha = runner._sha256_file_hex(feature_path)
    base_sha = runner._sha256_file_hex(ohlcv_path)
    source_class = (
        D4_TAKER_SOURCE_CLASS
        if timeframe == "15m"
        else CANONICAL_KLINE_TAKER_SOURCE_CLASS
    )
    parent_identity = parent_identity or (
        "binance_usdtm_btcusdt_ohlcv_15m:sha256:" + base_sha
    )
    source_files = [{"logical_filename": ohlcv_path.name, "sha256": base_sha, "size_bytes": ohlcv_path.stat().st_size, "parsed_row_count": len(base), "source_type": "canonical_d4_kline"}]
    source_identity_context = {
        "data_slice_identity": parent_identity,
        "normalized_sha256": base_sha,
        "derivation_version": (
            D4_TAKER_DERIVATION_VERSION
            if timeframe == "15m"
            else CANONICAL_KLINE_TAKER_DERIVATION_VERSION
        ),
    }
    coverage_start = pd.to_datetime(base[timestamp_column].iloc[0], utc=True).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    coverage_end = (
        pd.to_datetime(base[timestamp_column].iloc[-1], utc=True) + timeframe_delta
    ).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    contract = {
        "schema_version": "cpw_research_feature_table_v1",
        "family_id": "binance_usdm_takerflow_v1",
        "market_identity": {"venue": "Binance", "market_type": "USD-M perpetual", "symbol": "BTCUSDT"},
        "timeframe": timeframe,
        "feature_names": ["taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio"],
        "source_class": source_class,
        "availability_assertions": [
            {"feature_name": name, "source_class": source_class, "condition_assertions": ["fixture complete"]}
            for name in ("taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio")
        ],
        "source_set_identity": build_source_set_identity(source_files, identity_context=source_identity_context),
        "parent_identity": {
            "data_slice_identity": parent_identity,
            "normalized_sha256": base_sha,
            "row_count": len(base),
            "coverage_start_utc_inclusive": coverage_start,
            "coverage_end_utc_exclusive": coverage_end,
        },
        "derivation": {
            "derivation_version": (
                D4_TAKER_DERIVATION_VERSION
                if timeframe == "15m"
                else CANONICAL_KLINE_TAKER_DERIVATION_VERSION
            ),
            "parent_fields": list(D4_TAKER_PARENT_FIELDS),
            "features": [dict(item) for item in D4_TAKER_FEATURE_DEFINITIONS],
        },
        "output_identity": {"format": "CSV UTF-8 LF", "sha256": feature_sha, "row_count": len(base), "columns": list(D4_OUTPUT_COLUMNS)},
        "coverage": {
            "start_utc_inclusive": coverage_start,
            "end_utc_exclusive": coverage_end,
            "expected_row_count": len(base), "observed_row_count": len(base), "complete": True,
        },
        "causality": {"timestamp_semantics": "UTC bar open", "feature_available_at_semantics": "exclusive bar close", "completed_bar_only": True, "future_events_can_change_prior_completed_bars": False},
        "quality_policy": {"fill": "forbidden", "forward_fill": "forbidden", "backfill": "forbidden", "interpolation": "forbidden", "timestamp_tolerance": "forbidden", "missing_row": "fail_closed", "duplicate_join_key": "fail_closed"},
        "feature_table_identity": "",
        "non_authority": {"authorizes_execution": False, "authorizes_result_population": False, "authorizes_candidate": False, "authorizes_promotion": False, "authorizes_runtime_paper_live": False, "authorizes_oms_risk_reconciliation": False},
    }
    contract["feature_table_identity"] = build_feature_table_identity(contract)
    manifest = {
        "source_type": "canonical_d4_kline",
        "source_files": [{"path": ohlcv_path.as_posix(), **source_files[0]}],
        "source_set_identity_context": source_identity_context,
        "output": {"sha256": feature_sha},
        "research_feature_table": contract,
    }
    manifest_path = tmp_path / "research_features.manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path, feature_path


def _write_4h_ohlcv_fixture(tmp_path: Path, *, freq: str = "4h", periods: int = 32) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "canonical_4h_ohlcv_fixture.csv"
    index = pd.date_range("2026-01-01T00:00:00Z", periods=periods, freq=freq)
    close = [100.0 + index_number for index_number in range(len(index))]
    frame = pd.DataFrame(
        {
            "open_time_ms": [int(timestamp.timestamp() * 1000) for timestamp in index],
            "open_time": index,
            "open": [value - 0.1 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
            "close_time_ms": [
                int((timestamp + pd.Timedelta(hours=4)).timestamp() * 1000) - 1
                for timestamp in index
            ],
            "quote_asset_volume": [0.0] * len(index),
            "num_trades": [1] * len(index),
            "taker_buy_base_vol": [0.0] * len(index),
            "taker_buy_quote_vol": [0.0] * len(index),
            "ignore": [0] * len(index),
        }
    )
    frame.to_csv(path, index=False)
    return path


def _write_4h_metadata_fixture(
    tmp_path: Path,
    ohlcv_path: Path,
    *,
    validation_status: str = "PASS",
    partial_window_count: int = 0,
    data_slice_identity: str | None = None,
) -> tuple[Path, Path, Path, dict]:
    catalog_path, validation_path, derivation_path = _d4h_artifact_paths()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    derivation = json.loads(derivation_path.read_text(encoding="utf-8"))
    frame = pd.read_csv(ohlcv_path)
    row_count = len(frame)
    start_utc = str(frame["open_time"].iloc[0])
    end_utc = str(frame["open_time"].iloc[-1])
    csv_sha256 = runner._sha256_file_hex(ohlcv_path)
    synthetic_identity = data_slice_identity or f"test_4h:sha256:{csv_sha256}"

    catalog["catalog_ref"] = f"test_4h_catalog.sha256_{csv_sha256[:16]}"
    catalog["slice_identity"]["data_slice_identity"] = synthetic_identity
    catalog["normalized"]["sha256"] = csv_sha256
    catalog["range"]["row_count"] = row_count
    catalog["range"]["expected_row_count"] = row_count
    catalog["range"]["start_utc"] = start_utc
    catalog["range"]["end_utc"] = end_utc
    catalog["validation_report"]["status"] = validation_status

    validation["ok"] = validation_status == "PASS"
    validation["normalized"]["sha256"] = csv_sha256
    validation["range"]["row_count"] = row_count
    validation["range"]["expected_row_count"] = row_count
    validation["range"]["start_utc"] = start_utc
    validation["range"]["end_utc"] = end_utc
    validation["validation"]["status"] = validation_status
    validation["validation"]["partial_window_count"] = partial_window_count

    derivation["ok"] = True
    derivation["output"]["sha256"] = csv_sha256
    derivation["output"]["row_count"] = row_count
    derivation["output"]["expected_row_count"] = row_count
    derivation["output"]["range"]["start_utc"] = start_utc
    derivation["output"]["range"]["end_utc"] = end_utc

    out_validation_path = tmp_path / "d4h.validation_report.json"
    out_derivation_path = tmp_path / "d4h.derivation_report.json"
    out_catalog_path = tmp_path / "d4h.catalog_slice.json"
    _write_json(out_validation_path, validation)
    _write_json(out_derivation_path, derivation)
    catalog["validation_report"]["sha256"] = runner._sha256_file_hex(out_validation_path)
    catalog["derivation_report"]["sha256"] = runner._sha256_file_hex(out_derivation_path)
    _write_json(out_catalog_path, catalog)
    return out_catalog_path, out_validation_path, out_derivation_path, catalog


def _write_intraday_derived_fixture(
    tmp_path: Path,
    monkeypatch,
    timeframe: str,
    *,
    periods: int = 32,
    freq: str | None = None,
    validation_status: str = "PASS",
    partial_window_count: int = 0,
    gap_count: int = 0,
    duplicate_row_count: int = 0,
    identity_suffix: str | None = None,
) -> tuple[Path, Path, Path, Path, dict]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    base_config = runner.CANONICAL_INTRADAY_DERIVED_CONFIG[timeframe]
    cadence = base_config["cadence"]
    index = pd.date_range(
        "2026-01-01T00:00:00Z",
        periods=periods,
        freq=freq or ("30min" if timeframe == "30m" else timeframe),
    )
    csv_path = tmp_path / f"canonical_{timeframe}.csv"
    close = [100.0 + index_number for index_number in range(periods)]
    frame = pd.DataFrame(
        {
            "open_time_ms": [int(timestamp.timestamp() * 1000) for timestamp in index],
            "open_time": index,
            "open": [value - 0.1 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * periods,
            "close_time_ms": [
                int((timestamp + cadence).timestamp() * 1000) - 1 for timestamp in index
            ],
            "quote_asset_volume": [100000.0] * periods,
            "num_trades": [10] * periods,
            "taker_buy_base_vol": [500.0] * periods,
            "taker_buy_quote_vol": [50000.0] * periods,
            "ignore": [0] * periods,
        }
    )
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    csv_sha = runner._sha256_file_hex(csv_path)
    config = dict(base_config)
    config.update(
        row_count=periods,
        start_utc=index[0].isoformat().replace("+00:00", "Z"),
        end_utc=index[-1].isoformat().replace("+00:00", "Z"),
    )
    configs = copy.deepcopy(runner.CANONICAL_INTRADAY_DERIVED_CONFIG)
    configs[timeframe] = config
    monkeypatch.setattr(runner, "CANONICAL_INTRADAY_DERIVED_CONFIG", configs)

    catalog = json.loads(Path(base_config["catalog"]).read_text(encoding="utf-8"))
    validation = json.loads(Path(base_config["validation"]).read_text(encoding="utf-8"))
    derivation = json.loads(Path(base_config["derivation"]).read_text(encoding="utf-8"))
    identity_hash = identity_suffix or csv_sha
    catalog["catalog_ref"] = f"fixture_{timeframe}_{identity_hash[:16]}"
    catalog["slice_identity"]["data_slice_identity"] = (
        f"{config['dataset_id']}:sha256:{identity_hash}"
    )
    catalog["normalized"]["sha256"] = csv_sha
    catalog["range"].update(
        row_count=periods,
        expected_row_count=periods,
        start_utc=config["start_utc"],
        end_utc=config["end_utc"],
    )
    catalog["gap_summary"]["gap_count"] = gap_count
    catalog["gap_summary"]["missing_bar_count"] = gap_count
    catalog["gap_summary"]["gaps"] = [] if gap_count == 0 else [{"fixture": True}]
    catalog["duplicate_summary"]["duplicate_group_count"] = int(duplicate_row_count > 0)
    catalog["duplicate_summary"]["duplicate_row_count"] = duplicate_row_count
    catalog["duplicate_summary"]["duplicates"] = (
        [] if duplicate_row_count == 0 else [{"fixture": True}]
    )
    catalog["validation_report"]["status"] = validation_status

    validation["ok"] = validation_status == "PASS"
    validation["normalized"]["sha256"] = csv_sha
    validation["range"].update(
        row_count=periods,
        expected_row_count=periods,
        start_utc=config["start_utc"],
        end_utc=config["end_utc"],
    )
    validation["validation"]["status"] = validation_status
    validation["validation"]["partial_window_count"] = partial_window_count
    validation["validation"]["cadence_ms"] = config["cadence_ms"]

    derivation["output"].update(
        sha256=csv_sha,
        row_count=periods,
        expected_row_count=periods,
        start_utc=config["start_utc"],
        end_utc=config["end_utc"],
    )
    validation_path = tmp_path / f"{timeframe}.validation.json"
    derivation_path = tmp_path / f"{timeframe}.derivation.json"
    catalog_path = tmp_path / f"{timeframe}.catalog.json"
    _write_json(validation_path, validation)
    _write_json(derivation_path, derivation)
    catalog["validation_report"]["sha256"] = runner._sha256_file_hex(validation_path)
    catalog["derivation_report"]["sha256"] = runner._sha256_file_hex(derivation_path)
    _write_json(catalog_path, catalog)
    config.update(
        catalog=catalog_path,
        validation=validation_path,
        derivation=derivation_path,
    )
    return csv_path, catalog_path, validation_path, derivation_path, catalog


def _identity_payload(result: dict) -> dict:
    payload = copy.deepcopy(result["result_population"])
    payload.pop("audit_envelope")
    return payload


def _replace_first_data_ref_field(payload: object, field: str) -> bool:
    if isinstance(payload, dict):
        if payload.get("operand_type") == "data_ref":
            payload["ref"] = field
            payload["field"] = field
            return True
        return any(_replace_first_data_ref_field(child, field) for child in payload.values())
    if isinstance(payload, list):
        return any(_replace_first_data_ref_field(child, field) for child in payload)
    return False


def _append_required_data_ref_filter(strategy_spec: dict, field: str, threshold: float) -> None:
    strategy_spec["filters"]["groups"].append(
        {
            "group_id": f"G-{field}",
            "group_role": "funding",
            "logic": "all",
            "conditions": [
                {
                    "condition_id": f"C-{field}",
                    "condition_role": "filter",
                    "left_operand": {
                        "operand_type": "data_ref",
                        "ref": field,
                        "field": field,
                        "timeframe": None,
                        "lookback": None,
                    },
                    "operator": "gt",
                    "right_operand": {
                        "operand_type": "constant",
                        "ref": threshold,
                        "field": None,
                        "timeframe": None,
                        "lookback": None,
                    },
                    "units": None,
                    "notes": None,
                }
            ],
            "subgroups": [],
            "notes": None,
        }
    )


def _set_primary_timeframe(strategy_spec: dict, timeframe: str) -> None:
    strategy_spec["timeframe_and_data"]["primary_timeframe"] = timeframe


def test_target_leverage_resolution_uses_initial_equity_and_first_open():
    ohlcv = pd.DataFrame(
        {
            "open": [20_000.0, 50_000.0],
            "high": [20_100.0, 50_100.0],
            "low": [19_900.0, 49_900.0],
            "close": [20_050.0, 50_050.0],
            "volume": [1000.0, 1000.0],
        }
    )

    sizing = runner._resolve_order_size(
        target_leverage=1.0,
        initial_equity=10_000.0,
        ohlcv=ohlcv,
    )

    assert sizing.sizing_model == runner.SIZING_MODEL
    assert sizing.reference_price_basis == runner.REFERENCE_PRICE_BASIS
    assert sizing.reference_price == 20_000.0
    assert sizing.resolved_order_size == 0.5


def test_default_target_leverage_is_one_x(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    calls = []
    real_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )
    assumptions = result["result_population"]["backtest_assumption_summary"][
        "order_size_assumption"
    ]

    expected = runner.INITIAL_EQUITY / 100.1
    assert calls
    assert all(math.isclose(call["order_size"], expected) for call in calls)
    assert all(call["sizing_mode"] == runner.SIZING_MODE_FIXED_ORDER_SIZE for call in calls)
    assert all(call["target_leverage"] == runner.DEFAULT_TARGET_LEVERAGE for call in calls)
    assert "sizing_mode=fixed_order_size" in assumptions
    assert "target_leverage=1" in assumptions


def test_explicit_fixed_sizing_mode_passes_order_size_and_target_leverage(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    calls = []
    real_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_FIXED_ORDER_SIZE,
        target_leverage=1.5,
    )

    expected = 1.5 * runner.INITIAL_EQUITY / 100.1
    assert calls
    assert all(math.isclose(call["order_size"], expected) for call in calls)
    assert all(call["sizing_mode"] == runner.SIZING_MODE_FIXED_ORDER_SIZE for call in calls)
    assert all(call["target_leverage"] == 1.5 for call in calls)


def test_dynamic_sizing_mode_passes_mode_and_target_leverage(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    calls = []
    real_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )
    assumptions = result["result_population"]["backtest_assumption_summary"][
        "order_size_assumption"
    ]

    assert calls
    assert all(
        call["sizing_mode"] == runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE
        for call in calls
    )
    assert all(call["target_leverage"] == 1.0 for call in calls)
    assert all(call["order_size"] > 0.0 for call in calls)
    assert "sizing_mode=dynamic_equity_target_leverage" in assumptions
    assert "sizing_equity_basis=realized_available_equity_at_entry" in assumptions
    assert "entry_reference_price_basis=next_bar_open_pre_fee_slippage" in assumptions
    assert "structured_sizing_metadata=present" in assumptions
    assert result["result_population"]["sizing_metadata"] == DYNAMIC_SIZING_METADATA


def test_dynamic_output_includes_sizing_metadata_in_both_identity_scopes(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )

    payload = result["result_population"]
    assert payload["sizing_metadata"] == DYNAMIC_SIZING_METADATA
    assert "sizing_metadata" in payload["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" in payload["result_population_identity_hash"]["hash_scope"]


def test_default_fixed_output_does_not_emit_sizing_metadata(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    payload = result["result_population"]
    assumptions = payload["backtest_assumption_summary"]["order_size_assumption"]
    assert "sizing_metadata" not in payload
    assert "sizing_metadata" not in payload["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" not in payload["result_population_identity_hash"]["hash_scope"]
    assert "sizing_mode=fixed_order_size" in assumptions
    assert "structured_sizing_metadata=not_emitted_for_fixed_mode" in assumptions


def test_explicit_fixed_output_does_not_emit_sizing_metadata(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_FIXED_ORDER_SIZE,
        target_leverage=1.0,
    )

    payload = result["result_population"]
    assert "sizing_metadata" not in payload
    assert "sizing_metadata" not in payload["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" not in payload["result_population_identity_hash"]["hash_scope"]


def test_invalid_sizing_mode_rejected_by_api(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="sizing-mode"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            deterministic_seed=7,
            sizing_mode="unknown_mode",
        )


def test_invalid_sizing_mode_rejected_by_cli(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

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
            "--sizing-mode",
            "unknown_mode",
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "invalid choice" in completed.stderr


@pytest.mark.parametrize("bad_leverage", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_target_leverage_rejected_by_api(tmp_path, bad_leverage):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="target-leverage"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            deterministic_seed=7,
            target_leverage=bad_leverage,
        )


@pytest.mark.parametrize("bad_cli_value", ["0", "-1", "nan", "inf", "not-a-number"])
def test_invalid_target_leverage_rejected_by_cli(tmp_path, bad_cli_value):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

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
            "--target-leverage",
            bad_cli_value,
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "target-leverage" in completed.stderr


@pytest.mark.parametrize("bad_open", [None, 0.0, -1.0, float("nan"), float("inf")])
def test_invalid_reference_price_fails_closed_before_write(tmp_path, bad_open):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    frame = pd.read_csv(ohlcv_path)
    frame.loc[0, "open"] = bad_open
    frame.to_csv(ohlcv_path, index=False)
    output_dir = tmp_path / "scratch_result_populations"

    with pytest.raises(runner.OfflineSweepError, match="first_in_sample_open"):
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


def test_order_size_resolution_uses_no_later_prices():
    baseline = pd.DataFrame(
        {
            "open": [20_000.0, 25_000.0],
            "high": [20_100.0, 25_100.0],
            "low": [19_900.0, 24_900.0],
            "close": [20_050.0, 25_050.0],
            "volume": [1000.0, 1000.0],
        }
    )
    changed_later = baseline.copy()
    changed_later.loc[1, ["open", "high", "low", "close"]] = [90_000.0, 91_000.0, 89_000.0, 90_500.0]

    first = runner._resolve_order_size(
        target_leverage=1.5,
        initial_equity=10_000.0,
        ohlcv=baseline,
    )
    second = runner._resolve_order_size(
        target_leverage=1.5,
        initial_equity=10_000.0,
        ohlcv=changed_later,
    )

    assert first.resolved_order_size == second.resolved_order_size
    assert first.reference_price == second.reference_price == 20_000.0


def test_sizing_metadata_is_deterministic_for_same_input(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        target_leverage=2.0,
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        target_leverage=2.0,
    )

    first_assumption = first["result_population"]["backtest_assumption_summary"][
        "order_size_assumption"
    ]
    second_assumption = second["result_population"]["backtest_assumption_summary"][
        "order_size_assumption"
    ]
    assert first_assumption == second_assumption
    assert "sizing_mode=fixed_order_size" in first_assumption
    assert "sizing_model=runner_resolved_fixed_order_size" in first_assumption
    assert "reference_price_basis=first_in_sample_open" in first_assumption
    assert "resolved_order_size=" in first_assumption
    assert first["result_population_id"] == second["result_population_id"]
    assert _identity_payload(first) == _identity_payload(second)


def test_dynamic_sizing_dry_run_is_deterministic_for_same_input(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )

    assert first["dry_run"] is True
    assert first["wrote"] is False
    assert first["result_population"]["sizing_metadata"] == DYNAMIC_SIZING_METADATA
    assert first["result_population_id"] == second["result_population_id"]
    assert _identity_payload(first) == _identity_payload(second)


def test_sizing_mode_provenance_is_identity_bearing(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    fixed = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_FIXED_ORDER_SIZE,
        target_leverage=1.0,
    )
    dynamic = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )

    fixed_payload = fixed["result_population"]
    dynamic_payload = dynamic["result_population"]
    assert "sizing_metadata" not in fixed_payload
    assert dynamic_payload["sizing_metadata"] == DYNAMIC_SIZING_METADATA
    assert "backtest_assumption_summary" in fixed_payload["input_identity_hash"]["hash_scope"]
    assert "backtest_assumption_summary" in dynamic_payload["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" in dynamic_payload["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" in dynamic_payload["result_population_identity_hash"]["hash_scope"]
    assert fixed_payload["input_identity_hash"]["hash"] != dynamic_payload["input_identity_hash"]["hash"]
    assert fixed_payload["result_population_identity_hash"]["hash"] != dynamic_payload[
        "result_population_identity_hash"
    ]["hash"]


def test_dynamic_target_leverage_changes_identity_hashes(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    baseline = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )
    changed = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=2.0,
    )

    baseline_payload = baseline["result_population"]
    changed_payload = changed["result_population"]
    assert baseline_payload["sizing_metadata"]["target_leverage"] == 1.0
    assert changed_payload["sizing_metadata"]["target_leverage"] == 2.0
    assert baseline_payload["input_identity_hash"]["hash"] != changed_payload[
        "input_identity_hash"
    ]["hash"]
    assert baseline_payload["result_population_identity_hash"]["hash"] != changed_payload[
        "result_population_identity_hash"
    ]["hash"]


def test_dynamic_sizing_dry_run_preserves_no_canonical_write(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    canonical_files_before = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )

    canonical_files_after = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )
    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert result["result_population"]["sizing_metadata"] == DYNAMIC_SIZING_METADATA
    assert canonical_files_after == canonical_files_before


def test_short_real_like_sub_window_sizing_uses_fixture_first_open(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    frame = pd.read_csv(ohlcv_path)
    frame.loc[0, "open"] = 20_000.0
    frame.loc[1:, "open"] = 50_000.0
    frame.to_csv(ohlcv_path, index=False)
    calls = []
    real_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        target_leverage=1.0,
    )

    assert calls
    assert all(call["order_size"] == 0.5 for call in calls)


def test_effective_leverage_drift_is_measured_not_solved():
    ohlcv = pd.DataFrame(
        {
            "open": [10_000.0, 50_000.0],
            "high": [10_100.0, 50_100.0],
            "low": [9_900.0, 49_900.0],
            "close": [10_000.0, 50_000.0],
            "volume": [1000.0, 1000.0],
        }
    )

    sizing = runner._resolve_order_size(
        target_leverage=1.0,
        initial_equity=10_000.0,
        ohlcv=ohlcv,
    )
    start_effective_leverage = (
        sizing.resolved_order_size * sizing.reference_price / sizing.initial_equity
    )
    end_effective_leverage = (
        sizing.resolved_order_size * float(ohlcv["close"].iloc[-1]) / sizing.initial_equity
    )

    assert sizing.resolved_order_size == 1.0
    assert start_effective_leverage == 1.0
    assert end_effective_leverage == 5.0
    assert runner.DRIFT_CAVEAT == (
        "fixed_order_size_caps_leverage_at_reference_price_only_effective_leverage_can_drift"
    )


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


def test_default_max_workers_uses_sequential_path(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    monkeypatch.setattr(
        runner,
        "_execute_rows_parallel",
        lambda *args, **kwargs: pytest.fail("parallel path should be opt-in"),
    )

    result = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7)

    assert result["ok"] is True


def test_cli_accepts_max_workers_and_rejects_zero(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    accepted = subprocess.run(
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
            "--max-workers",
            "2",
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    rejected = subprocess.run(
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
            "--max-workers",
            "0",
        ],
        cwd=runner.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert accepted.returncode == 0
    assert json.loads(accepted.stdout)["dry_run"] is True
    assert rejected.returncode != 0
    assert "--max-workers must be a positive integer" in rejected.stderr


def test_invalid_max_workers_rejected_by_api(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="max_workers"):
        _run(strategy_path, manifest_path, sweep_path, max_workers=0)


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


def test_parallel_synthetic_payload_matches_sequential_with_non_success_rows(tmp_path):
    def mutate(manifest: dict) -> None:
        _set_variant_count(manifest, 6)
        manifest["variant_assignments"][1]["status_reason"] = "runner_fixture:errored"
        manifest["variant_assignments"][2]["status_reason"] = "runner_fixture:data_unavailable"
        manifest["variant_assignments"][3]["assignment_status"] = "excluded"
        manifest["variant_assignments"][3]["status_reason"] = "excluded_fixture"
        manifest["variant_assignments"][4]["assignment_status"] = "invalid"
        manifest["variant_assignments"][4]["status_reason"] = "invalid_fixture"

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    sequential = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7, max_workers=1)
    parallel = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7, max_workers=2)

    rows = parallel["result_population"]["variant_result_rows"]
    assert _identity_payload(sequential) == _identity_payload(parallel)
    assert [row["variant_id"] for row in rows] == [f"VAR-{index:06d}" for index in range(1, 7)]
    assert [row["outcome_category"] for row in rows] == [
        "successful",
        "errored",
        "data_unavailable",
        "excluded",
        "invalid",
        "successful",
    ]
    assert parallel["outcome_category_counts"]["counts_sum"] == 6


def test_parallel_abort_matches_sequential_and_marks_later_rows_not_attempted(tmp_path):
    def mutate(manifest: dict) -> None:
        _set_variant_count(manifest, 4)
        manifest["variant_assignments"][1]["status_reason"] = "runner_fixture:infra_abort"
        manifest["variant_assignments"][2]["status_reason"] = "runner_fixture:errored"

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path, mutate)

    sequential = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7, max_workers=1)
    parallel = _run(strategy_path, manifest_path, sweep_path, deterministic_seed=7, max_workers=2)
    rows = parallel["result_population"]["variant_result_rows"]

    assert _identity_payload(sequential) == _identity_payload(parallel)
    assert parallel["ok"] is False
    assert [row["outcome_category"] for row in rows] == [
        "successful",
        "aborted",
        "not_attempted",
        "not_attempted",
    ]
    assert parallel["outcome_category_counts"]["aborted"] == 1
    assert parallel["outcome_category_counts"]["not_attempted"] == 2


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
    assert all(kwargs["funding_cost_mode"] == "off" for _, kwargs in backtest_calls)
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


def test_canonical_cli_flags_accept_15m_and_4h_modes(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    parser = runner._build_parser()

    parsed_15m = parser.parse_args(
        [
            "--strategy-spec",
            str(strategy_path),
            "--variant-manifest",
            str(manifest_path),
            "--sweep-plan",
            str(sweep_path),
            "--canonical-15m",
            "--ohlcv-input",
            str(tmp_path / "input.csv"),
        ]
    )
    parsed_4h = parser.parse_args(
        [
            "--strategy-spec",
            str(strategy_path),
            "--variant-manifest",
            str(manifest_path),
            "--sweep-plan",
            str(sweep_path),
            "--canonical-4h",
            "--ohlcv-input",
            str(tmp_path / "input.csv"),
        ]
    )

    assert parsed_15m.canonical_15m is True
    assert parsed_15m.canonical_4h is False
    assert parsed_4h.canonical_15m is False
    assert parsed_4h.canonical_4h is True


def test_canonical_4h_path_uses_4h_interval_and_binds_lineage(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_0006_parent_paths()
    ohlcv_path = _write_4h_ohlcv_fixture(tmp_path)
    catalog_path, validation_path, derivation_path, catalog = _write_4h_metadata_fixture(
        tmp_path,
        ohlcv_path,
    )
    backtest_calls = []
    canonical_files_before = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )

    def fake_compile_signal(strategy_spec, variant_assignment, ohlcv, funding=None):
        del strategy_spec, variant_assignment, funding
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[2:-2] = 1.0
        return signal

    def fake_backtest(signal, ohlcv, funding, **kwargs):
        del signal, funding
        backtest_calls.append(kwargs)
        equity = pd.Series(
            [runner.INITIAL_EQUITY + index for index in range(len(ohlcv))],
            index=ohlcv.index,
            name="equity",
        )
        return type(
            "FakeBacktestResult",
            (),
            {
                "equity_curve": equity,
                "trades_df": pd.DataFrame({"net_pnl": [1.0]}),
                "fees_paid": 0.0,
                "funding_paid": 0.0,
                "slippage_paid": 0.0,
                "params": {"initial_equity": runner.INITIAL_EQUITY},
            },
        )()

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    monkeypatch.setattr(runner, "run_backtest", fake_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_4h=True,
        ohlcv_input_path=ohlcv_path,
        d4h_catalog_slice_path=catalog_path,
        d4h_validation_report_path=validation_path,
        d4h_derivation_report_path=derivation_path,
        deterministic_seed=7,
    )
    payload = result["result_population"]
    coverage = payload["data_coverage_summary"]
    notes = set(coverage["data_coverage_notes"])

    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")) == (
        canonical_files_before
    )
    assert backtest_calls
    assert all(call["interval"] == "4h" for call in backtest_calls)
    assert all(call["funding_cost_mode"] == "off" for call in backtest_calls)
    assert coverage["timeframe"] == "4h"
    assert coverage["data_catalog_ref"] == catalog["catalog_ref"]
    assert coverage["data_slice_identity"] == catalog["slice_identity"]["data_slice_identity"]
    assert runner.D4H_PROVENANCE_MODE_NOTE in notes
    assert f"d4h_csv_sha256={runner._sha256_file_hex(ohlcv_path)}" in notes
    assert "d4h_validation_status=PASS" in notes
    assert f"parent_15m_data_slice_identity={D4_SLICE_IDENTITY}" in notes
    assert "parent_15m_normalized_sha256=c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab" in notes
    assert "resampling_version=wp-data-resample-4h-01-v1" in notes
    assert {row["data_coverage"]["timeframe"] for row in payload["variant_result_rows"]} == {"4h"}
    assert payload["parent_strategy_spec"]["strategy_spec_id"] == "STRAT-SPEC-0006"
    assert payload["parent_variant_manifest"]["variant_manifest_id"] == "VM-0006"
    assert payload["parent_sweep_plan"]["sweep_plan_id"] == "SWEEP-PLAN-0006"
    assert payload["committed_denominator_snapshot"]["committed_denominator"] == 8
    assert payload["outcome_category_counts"]["counts_sum"] == 8


def test_research_features_bind_on_canonical_4h_route(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path / "parents",
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "4h"),
            _replace_first_data_ref_field(strategy, "taker_sell_volume"),
        ),
    )
    csv_path = _write_4h_ohlcv_fixture(tmp_path / "data")
    parent_identity = (
        "binance_usdtm_btcusdt_ohlcv_4h:sha256:"
        + runner._sha256_file_hex(csv_path)
    )
    catalog_path, validation_path, derivation_path, catalog = _write_4h_metadata_fixture(
        tmp_path / "metadata", csv_path, data_slice_identity=parent_identity
    )
    feature_manifest, feature_input = _write_research_feature_fixture(
        tmp_path / "features",
        csv_path,
        timeframe="4h",
        parent_identity=catalog["slice_identity"]["data_slice_identity"],
    )
    monkeypatch.setattr(
        runner,
        "compile_signal",
        lambda strategy_spec, variant, ohlcv, funding=None: pd.Series(0.0, index=ohlcv.index),
    )
    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_4h=True,
        ohlcv_input_path=csv_path,
        d4h_catalog_slice_path=catalog_path,
        d4h_validation_report_path=validation_path,
        d4h_derivation_report_path=derivation_path,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_input,
    )
    assert result["wrote"] is False
    assert result["result_population"]["data_coverage_summary"]["data_slice_identity"].startswith(
        "cpw_research_composite_4h:sha256:"
    )


def test_research_features_bind_on_canonical_1d_parquet_route(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path / "parents",
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "1d"),
            _replace_first_data_ref_field(strategy, "taker_buy_volume"),
        ),
    )
    index = pd.date_range("2024-01-01", periods=32, freq="1D", tz="UTC")
    parent = pd.DataFrame(
        {
            "open_time_ms": index.as_unit("ms").asi8,
            "open": [100.0] * 32,
            "high": [101.0] * 32,
            "low": [99.0] * 32,
            "close": [100.0] * 32,
            "volume": [10.0] * 32,
            "close_time_ms": (index + pd.Timedelta(days=1)).as_unit("ms").asi8 - 1,
            "num_trades": [2] * 32,
            "taker_buy_base_vol": [4.0] * 32,
        }
    )
    parent_path = tmp_path / "canonical_1d.parquet"
    parent.to_parquet(parent_path, index=False)
    parent_sha = runner._sha256_file_hex(parent_path)
    parent_identity = (
        "binance_usdtm_btcusdt_ohlcv_1d:identity_sha256:" + "5" * 64
    )
    coverage_start = "2024-01-01T00:00:00.000Z"
    coverage_end = "2024-02-02T00:00:00.000Z"
    feature_path = tmp_path / "features.csv"
    feature_manifest = tmp_path / "features.manifest.json"
    materialize_canonical_kline_takerflow_features(
        canonical_kline_path=parent_path,
        timeframe="1d",
        output_path=feature_path,
        manifest_path=feature_manifest,
        availability_catalog_path=runner.DATA_FEATURE_AVAILABILITY_CATALOG_PATH,
        _parent_config={
            "sha256": parent_sha,
            "row_count": 32,
            "coverage_start": coverage_start,
            "coverage_end": coverage_end,
            "data_slice_identity": parent_identity,
            "format": "parquet",
        },
    )
    base_frame = parent[list(runner.REQUIRED_OHLCV_COLUMNS)].astype(float).copy()
    base_frame.index = index
    execution_input = runner._ExecutionInput(
        mode="canonical_1d_test",
        execution_provenance_class="canonical_direct_real_data",
        ohlcv=base_frame,
        funding=runner._zero_funding_for_ohlcv(base_frame),
        timeframe="1d",
        data_catalog_ref="fixture_1d",
        data_slice_identity=parent_identity,
        environment_summary=["offline_only_no_exchange_api"],
        data_coverage_notes=["fixture canonical 1d"],
        base_input_path=parent_path,
        base_normalized_sha256=parent_sha,
        base_coverage_start_utc_inclusive=coverage_start,
        base_coverage_end_utc_exclusive=coverage_end,
    )
    monkeypatch.setattr(runner, "_canonical_1d_execution_input", lambda additional_columns=(): execution_input)
    monkeypatch.setattr(
        runner,
        "compile_signal",
        lambda strategy_spec, variant, ohlcv, funding=None: pd.Series(0.0, index=ohlcv.index),
    )
    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_1d=True,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_path,
    )
    assert result["wrote"] is False
    assert result["result_population"]["data_coverage_summary"]["data_slice_identity"].startswith(
        "cpw_research_composite_1d:sha256:"
    )


def test_canonical_4h_rejects_non_4h_spacing(tmp_path):
    ohlcv_path = _write_4h_ohlcv_fixture(tmp_path, freq="1h")

    with pytest.raises(runner.OfflineSweepError, match="exactly 4h-spaced"):
        runner._load_4h_ohlcv_input(ohlcv_path)


def test_canonical_4h_rejects_csv_sha_mismatch(tmp_path):
    ohlcv_path = _write_4h_ohlcv_fixture(tmp_path)
    catalog_path, validation_path, derivation_path, _ = _write_4h_metadata_fixture(
        tmp_path,
        ohlcv_path,
    )
    frame = pd.read_csv(ohlcv_path)
    frame.loc[0, "close"] = 999.0
    frame.to_csv(ohlcv_path, index=False)

    with pytest.raises(runner.OfflineSweepError, match="CSV SHA256"):
        runner._canonical_4h_execution_input(
            ohlcv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


def test_canonical_4h_rejects_validation_status_not_pass(tmp_path):
    ohlcv_path = _write_4h_ohlcv_fixture(tmp_path)
    catalog_path, validation_path, derivation_path, _ = _write_4h_metadata_fixture(
        tmp_path,
        ohlcv_path,
        validation_status="FAIL",
    )

    with pytest.raises(runner.OfflineSweepError, match="validation status PASS"):
        runner._canonical_4h_execution_input(
            ohlcv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


def test_canonical_4h_official_identity_requires_committed_row_count(tmp_path):
    ohlcv_path = _write_4h_ohlcv_fixture(tmp_path)
    catalog_path, validation_path, derivation_path, _ = _write_4h_metadata_fixture(
        tmp_path,
        ohlcv_path,
        data_slice_identity=D4H_SLICE_IDENTITY,
    )

    with pytest.raises(runner.OfflineSweepError, match="row_count 13758"):
        runner._canonical_4h_execution_input(
            ohlcv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


def test_annualization_uses_distinct_15m_and_4h_factors():
    returns = pd.Series([0.01, -0.005] * 20)

    sharpe_15m = runner.sharpe(returns, "15m")
    sharpe_4h = runner.sharpe(returns, "4h")

    assert math.isclose(sharpe_15m / sharpe_4h, 4.0)


def test_metrics_from_backtest_passes_requested_timeframe_to_sharpe(monkeypatch):
    calls = []

    def fake_sharpe(returns, freq):
        del returns
        calls.append(freq)
        return {"15m": 35_040.0, "4h": 2_190.0}[freq]

    fake_result = type(
        "FakeBacktestResult",
        (),
        {
            "equity_curve": pd.Series([10_000.0, 10_010.0, 10_005.0]),
            "trades_df": pd.DataFrame({"net_pnl": [1.0]}),
            "fees_paid": 0.0,
            "funding_paid": 0.0,
            "slippage_paid": 0.0,
            "params": {"initial_equity": runner.INITIAL_EQUITY},
        },
    )()
    monkeypatch.setattr(runner, "sharpe", fake_sharpe)

    metrics_15m = runner._metrics_from_backtest(fake_result, "15m")
    metrics_4h = runner._metrics_from_backtest(fake_result, "4h")

    assert calls == ["15m", "4h"]
    assert metrics_15m["sharpe"] == 35_040.0
    assert metrics_4h["sharpe"] == 2_190.0


def test_15m_input_identity_scope_remains_unchanged():
    assert runner._input_scope() == [
        "parent_strategy_spec.strategy_spec_hash",
        "parent_variant_manifest.manifest_hash",
        "parent_sweep_plan.sweep_plan_identity_hash",
        "parent_variant_manifest.committed_population_count",
        "parent_sweep_plan.committed_population_count",
        "execution_context.runner_code_ref",
        "execution_context.repo_commit",
        "data_coverage_summary.data_catalog_ref",
        "data_coverage_summary.data_slice_identity",
        "backtest_assumption_summary",
    ]


def test_research_feature_cli_arguments_are_a_required_pair_and_need_canonical_route(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    feature = tmp_path / "feature.csv"
    manifest = tmp_path / "feature.json"
    with pytest.raises(runner.OfflineSweepError, match="required pair"):
        _run(
            strategy_path, manifest_path, sweep_path,
            research_feature_manifest_path=manifest,
        )
    with pytest.raises(runner.OfflineSweepError, match="one canonical timeframe route"):
        _run(
            strategy_path, manifest_path, sweep_path,
            research_feature_manifest_path=manifest,
            research_feature_input_path=feature,
        )
    parsed = runner._build_parser().parse_args(
        ["--strategy-spec", str(strategy_path), "--variant-manifest", str(manifest_path),
         "--sweep-plan", str(sweep_path), "--canonical-15m", "--ohlcv-input", str(tmp_path / "base.csv"),
         "--research-feature-manifest", str(manifest), "--research-feature-input", str(feature)]
    )
    assert parsed.research_feature_manifest == manifest
    assert parsed.research_feature_input == feature


def test_15m_feature_binding_still_requires_d4_provenance(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, "15m"),
    )
    with pytest.raises(runner.OfflineSweepError, match="require D4 15m provenance"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=_write_15m_ohlcv_fixture(tmp_path),
            research_feature_manifest_path=tmp_path / "feature.json",
            research_feature_input_path=tmp_path / "feature.csv",
        )


def test_generic_feature_table_joins_declared_fields_and_changes_identity(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "taker_buy_sell_ratio"),
        ),
    )
    base_path = _write_15m_ohlcv_fixture(tmp_path, include_open_time_ms=True)
    catalog_path, import_path = _write_small_d4_metadata(tmp_path, base_path)
    feature_manifest, feature_input = _write_research_feature_fixture(tmp_path, base_path)
    observed_columns = []

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        observed_columns.append(list(ohlcv.columns))
        return pd.Series(0.0, index=ohlcv.index)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    result = _run(
        strategy_path, manifest_path, sweep_path,
        canonical_15m=True, ohlcv_input_path=base_path,
        d4_catalog_slice_path=catalog_path, d2_import_report_path=import_path,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_input,
        deterministic_seed=7,
    )
    coverage = result["result_population"]["data_coverage_summary"]
    assert coverage["data_slice_identity"].startswith("cpw_research_composite_15m:sha256:")
    assert all("taker_buy_sell_ratio" in columns for columns in observed_columns)
    assert all("taker_total_volume" not in columns for columns in observed_columns)
    assert any(note.startswith("feature_table_identity=sha256:") for note in coverage["data_coverage_notes"])
    assert result["result_population"]["data_availability_claim"]["feature_sources"][0][
        "source_class"
    ] == D4_TAKER_SOURCE_CLASS


def test_generic_feature_table_rejects_hash_timestamp_and_lookahead_mismatch(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "taker_buy_volume"),
        ),
    )
    base_path = _write_15m_ohlcv_fixture(tmp_path, include_open_time_ms=True)
    catalog_path, import_path = _write_small_d4_metadata(tmp_path, base_path)

    def run_with(feature_manifest: Path, feature_input: Path):
        return _run(
            strategy_path, manifest_path, sweep_path,
            canonical_15m=True, ohlcv_input_path=base_path,
            d4_catalog_slice_path=catalog_path, d2_import_report_path=import_path,
            research_feature_manifest_path=feature_manifest,
            research_feature_input_path=feature_input,
        )

    hash_manifest, hash_input = _write_research_feature_fixture(tmp_path / "hash", base_path)
    hash_input.write_bytes(hash_input.read_bytes() + b"\n")
    with pytest.raises(runner.OfflineSweepError, match="SHA-256"):
        run_with(hash_manifest, hash_input)
    timestamp_manifest, timestamp_input = _write_research_feature_fixture(
        tmp_path / "timestamp", base_path, timestamp_shift_minutes=15
    )
    with pytest.raises(runner.OfflineSweepError, match="timestamp"):
        run_with(timestamp_manifest, timestamp_input)
    causal_manifest, causal_input = _write_research_feature_fixture(
        tmp_path / "causal", base_path, availability_shift_minutes=0
    )
    with pytest.raises(runner.OfflineSweepError, match="availability"):
        run_with(causal_manifest, causal_input)


def test_unbound_taker_source_is_ambiguous_and_fails_closed(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "taker_buy_sell_ratio"),
        ),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        extra_columns={"taker_buy_sell_ratio": [1.1] * 96},
    )
    with pytest.raises(runner.OfflineSweepError, match="ambiguous FULL_HISTORY"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )


def test_multiple_declared_non_ohlcv_columns_are_retained(tmp_path, monkeypatch):
    def mutate(strategy: dict) -> None:
        _set_primary_timeframe(strategy, "15m")
        assert _replace_first_data_ref_field(strategy, "taker_buy_sell_ratio")
        _append_required_data_ref_filter(strategy, "taker_buy_volume", 10.0)

    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=mutate,
    )
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path, include_open_time_ms=True)
    catalog_path, import_path = _write_small_d4_metadata(tmp_path, ohlcv_path)
    feature_manifest, feature_input = _write_research_feature_fixture(tmp_path, ohlcv_path)
    observed_columns = []

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        observed_columns.append(list(ohlcv.columns))
        return pd.Series(0.0, index=ohlcv.index)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_path,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_input,
        deterministic_seed=7,
    )

    assert observed_columns
    assert all("taker_buy_sell_ratio" in columns for columns in observed_columns)
    assert all("taker_buy_volume" in columns for columns in observed_columns)
    assert all("undeclared_extra" not in columns for columns in observed_columns)
    assert [
        source["feature_name"]
        for source in result["result_population"]["data_availability_claim"]["feature_sources"]
    ] == ["taker_buy_sell_ratio", "taker_buy_volume"]


def test_missing_declared_non_ohlcv_column_fails_closed(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "taker_sell_volume"),
        ),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="missing declared non-OHLCV columns"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )


def test_recent_only_declared_non_ohlcv_field_fails_closed(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "open_interest"),
        ),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        extra_columns={"open_interest": [100.0] * 96},
    )

    with pytest.raises(runner.OfflineSweepError, match="no FULL_HISTORY_PUBLIC_ARCHIVE"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            deterministic_seed=7,
        )


def test_undeclared_extra_input_column_is_not_retained(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, "15m"),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        extra_columns={"taker_buy_sell_ratio": [1.1] * 96},
    )
    observed_columns = []

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        observed_columns.append(list(ohlcv.columns))
        return pd.Series(0.0, index=ohlcv.index)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    assert observed_columns
    assert all(columns == list(runner.REQUIRED_OHLCV_COLUMNS) for columns in observed_columns)
    assert "data_availability_claim" not in result["result_population"]


def test_declared_non_ohlcv_runner_smoke_reaches_backtester(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "taker_buy_sell_ratio"),
        ),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path, include_open_time_ms=True)
    catalog_path, import_path = _write_small_d4_metadata(tmp_path, ohlcv_path)
    feature_manifest, feature_input = _write_research_feature_fixture(tmp_path, ohlcv_path)
    calls = []
    real_backtest = runner.run_backtest

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        assert "taker_buy_sell_ratio" in ohlcv.columns
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[2:6] = 1.0
        return signal

    def recording_backtest(signal, ohlcv, funding, **kwargs):
        calls.append({"columns": list(ohlcv.columns), "signal_rows": len(signal)})
        return real_backtest(signal, ohlcv, funding, **kwargs)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        d4_catalog_slice_path=catalog_path,
        d2_import_report_path=import_path,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_input,
        deterministic_seed=7,
    )

    assert result["ok"] is True
    assert calls
    assert all("taker_buy_sell_ratio" in call["columns"] for call in calls)
    assert all(call["signal_rows"] == 96 for call in calls)


def test_declared_funding_rate_runner_smoke_reaches_backtester(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, "15m"),
            _replace_first_data_ref_field(strategy, "funding_rate"),
        ),
    )
    ohlcv_path = _write_15m_ohlcv_fixture(
        tmp_path,
        extra_columns={"funding_rate": [0.0001] * 96},
    )
    calls = []
    real_backtest = runner.run_backtest

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        assert "funding_rate" in ohlcv.columns
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[2:6] = 1.0
        return signal

    def recording_backtest(signal, ohlcv, funding, **kwargs):
        calls.append(list(ohlcv.columns))
        return real_backtest(signal, ohlcv, funding, **kwargs)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )

    assert result["ok"] is True
    assert calls and all("funding_rate" in columns for columns in calls)
    assert result["result_population"]["data_availability_claim"]["feature_sources"] == [
        {
            "feature_name": "funding_rate",
            "source_class": "PUBLIC_FUNDING_ARCHIVE",
            "condition_assertions": [
                "Aligned funding records cover the claimed evidence window."
            ],
        }
    ]


def test_runner_cli_introduces_no_runtime_authority_flags():
    parser = runner._build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert not any(
        forbidden in option
        for option in option_strings
        for forbidden in ("runtime", "paper", "live", "oms", "risk", "broker", "exchange")
    )


def test_canonical_15m_scratch_result_population_validates(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    output_dir = tmp_path / "scratch_result_populations"
    canonical_files_before = (
        sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json"))
        if runner.CANONICAL_RESULT_POPULATIONS_DIR.exists()
        else []
    )
    assert "RP-7520.result_population.json" in {path.name for path in canonical_files_before}

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
    assert canonical_files_after == canonical_files_before
    assert written[0].parent == output_dir


def test_dynamic_canonical_15m_scratch_result_population_validates(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    output_dir = tmp_path / "dynamic_scratch_result_populations"
    canonical_files_before = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
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
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
    )

    written = list(output_dir.glob("*.result_population.json"))
    assert result["wrote"] is True
    assert len(written) == 1
    assert result["result_population"]["sizing_metadata"] == DYNAMIC_SIZING_METADATA
    assert "sizing_metadata" in result["result_population"]["input_identity_hash"]["hash_scope"]
    assert "sizing_metadata" in result["result_population"][
        "result_population_identity_hash"
    ]["hash_scope"]
    assert validate_result_populations(
        result_populations_dir=output_dir,
        strategy_specs_dir=strategy_path.parent,
        variant_manifests_dir=manifest_path.parent,
        sweep_plans_dir=sweep_path.parent,
    ) == []
    canonical_files_after = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )
    assert canonical_files_after == canonical_files_before
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


def test_parallel_canonical_15m_fixture_matches_sequential(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    sequential = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        max_workers=1,
    )
    parallel = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        max_workers=2,
    )

    assert _identity_payload(sequential) == _identity_payload(parallel)
    assert [
        row["row_identity_hash"]
        for row in sequential["result_population"]["variant_result_rows"]
    ] == [
        row["row_identity_hash"]
        for row in parallel["result_population"]["variant_result_rows"]
    ]


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


def test_walkforward_window_generation_uses_explicit_non_overlapping_boundaries():
    index = pd.date_range("2026-01-01T00:00:00Z", periods=96, freq="15min")

    windows = runner._build_walkforward_windows(
        index,
        in_sample_bars=24,
        out_of_sample_bars=24,
        step_bars=48,
    )

    assert [window.window_id for window in windows] == ["WF-0001", "WF-0002"]
    assert windows[0].in_sample_start == index[0]
    assert windows[0].in_sample_end_exclusive == index[24]
    assert windows[0].out_of_sample_start == index[24]
    assert windows[0].out_of_sample_end_exclusive == index[48]
    assert windows[1].in_sample_start == index[48]
    assert windows[1].out_of_sample_start == index[72]
    assert windows[0].out_of_sample_end_exclusive <= windows[1].in_sample_start


def test_walkforward_rejects_overlapping_step():
    index = pd.date_range("2026-01-01T00:00:00Z", periods=96, freq="15min")

    with pytest.raises(runner.OfflineSweepError, match="preserve non-overlap"):
        runner._build_walkforward_windows(
            index,
            in_sample_bars=24,
            out_of_sample_bars=24,
            step_bars=24,
        )


def test_walkforward_dry_run_partitions_and_does_not_write(tmp_path, monkeypatch):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    calls = []
    canonical_files_before = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[1:-1] = 1.0
        return signal

    def fake_backtest(signal, ohlcv, funding, **kwargs):
        del signal, funding
        calls.append(
            {
                "start": ohlcv.index[0],
                "end": ohlcv.index[-1],
                "rows": len(ohlcv),
                "order_size": kwargs["order_size"],
            }
        )
        equity = pd.Series(
            [runner.INITIAL_EQUITY + index for index in range(len(ohlcv))],
            index=ohlcv.index,
            name="equity",
        )
        return type(
            "FakeBacktestResult",
            (),
            {
                "equity_curve": equity,
                "trades_df": pd.DataFrame({"net_pnl": [1.0]}),
                "fees_paid": 0.0,
                "funding_paid": 0.0,
                "slippage_paid": 0.0,
                "params": {"initial_equity": runner.INITIAL_EQUITY},
            },
        )()

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    monkeypatch.setattr(runner, "run_backtest", fake_backtest)

    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        walkforward=True,
        walkforward_is_bars=24,
        walkforward_oos_bars=24,
        walkforward_step_bars=48,
        walkforward_max_windows=2,
    )

    walkforward = result["walkforward"]
    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert walkforward["dry_run_only"] is True
    assert walkforward["canonical_result_population_written"] is False
    assert walkforward["window_count"] == 2
    assert walkforward["variant_count_per_window"] == 7
    assert len(walkforward["rows"]) == 14
    assert all(
        row["selection_behavior"] == "no_selection_partition_and_report_all_included_variants"
        for row in walkforward["rows"]
    )
    assert all(
        row["in_sample_end_exclusive"] == row["out_of_sample_start"]
        for row in walkforward["rows"]
    )
    assert all(row["oos_is_sharpe_efficiency"] is not None for row in walkforward["rows"])
    window_calls = [call for call in calls if call["rows"] == 24]
    base_calls = [call for call in calls if call["rows"] == 96]
    assert len(base_calls) == 7
    assert len(window_calls) == 28
    canonical_files_after = sorted(
        runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")
    )
    assert canonical_files_after == canonical_files_before


def test_parallel_walkforward_dry_run_matches_sequential(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    sequential = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        walkforward=True,
        walkforward_is_bars=24,
        walkforward_oos_bars=24,
        walkforward_step_bars=48,
        walkforward_max_windows=2,
        max_workers=1,
    )
    parallel = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
        walkforward=True,
        walkforward_is_bars=24,
        walkforward_oos_bars=24,
        walkforward_step_bars=48,
        walkforward_max_windows=2,
        max_workers=2,
    )

    assert _identity_payload(sequential) == _identity_payload(parallel)
    assert sequential["walkforward"] == parallel["walkforward"]
    assert [
        (row["window_index"], row["variant_id"])
        for row in parallel["walkforward"]["rows"]
    ] == sorted(
        (row["window_index"], row["variant_id"])
        for row in parallel["walkforward"]["rows"]
    )


def test_walkforward_mode_is_dry_run_only(tmp_path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)

    with pytest.raises(runner.OfflineSweepError, match="dry-run-only"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            output_dir=tmp_path / "scratch_result_populations",
            write_result_population=True,
            canonical_15m=True,
            ohlcv_input_path=ohlcv_path,
            walkforward=True,
            walkforward_is_bars=24,
            walkforward_oos_bars=24,
        )


def test_canonical_cli_flags_accept_30m_and_1h_modes(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    common = [
        "--strategy-spec",
        str(strategy_path),
        "--variant-manifest",
        str(manifest_path),
        "--sweep-plan",
        str(sweep_path),
        "--ohlcv-input",
        str(tmp_path / "input.csv"),
    ]
    parsed_30m = runner._build_parser().parse_args([*common, "--canonical-30m"])
    parsed_1h = runner._build_parser().parse_args([*common, "--canonical-1h"])
    assert parsed_30m.canonical_30m is True
    assert parsed_30m.canonical_1h is False
    assert parsed_1h.canonical_30m is False
    assert parsed_1h.canonical_1h is True


def test_all_five_canonical_routes_are_mutually_exclusive(tmp_path):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(tmp_path)
    selectors = {
        "canonical_15m": True,
        "canonical_30m": True,
        "canonical_1h": True,
        "canonical_4h": True,
        "canonical_1d": True,
    }
    for first, second in zip(selectors, list(selectors)[1:]):
        with pytest.raises(runner.OfflineSweepError, match="mutually exclusive"):
            _run(
                strategy_path,
                manifest_path,
                sweep_path,
                **{first: True, second: True},
            )


@pytest.mark.parametrize("timeframe", ["30m", "1h"])
def test_intraday_route_requires_matching_strategy_and_sweep_timeframe(
    tmp_path,
    timeframe,
):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, "15m"),
    )
    with pytest.raises(
        runner.OfflineSweepError,
        match=rf"canonical_{timeframe} requires {timeframe}",
    ):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            **{f"canonical_{timeframe}": True},
            ohlcv_input_path=tmp_path / "missing.csv",
        )


@pytest.mark.parametrize("timeframe", ["30m", "1h"])
def test_intraday_route_binds_timeframe_lineage_and_does_not_write(
    tmp_path,
    monkeypatch,
    timeframe,
):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path / "parents",
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, timeframe),
    )
    csv_path, _, _, _, catalog = _write_intraday_derived_fixture(
        tmp_path / "data",
        monkeypatch,
        timeframe,
    )
    before = sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json"))
    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        **{f"canonical_{timeframe}": True},
        ohlcv_input_path=csv_path,
        deterministic_seed=7,
    )
    coverage = result["result_population"]["data_coverage_summary"]
    assert result["dry_run"] is True
    assert result["wrote"] is False
    assert coverage["timeframe"] == timeframe
    assert coverage["data_catalog_ref"] == catalog["catalog_ref"]
    assert coverage["data_slice_identity"] == catalog["slice_identity"]["data_slice_identity"]
    assert runner.FT01_PROVENANCE_MODE_NOTE in coverage["data_coverage_notes"]
    assert {row["data_coverage"]["timeframe"] for row in result["result_population"]["variant_result_rows"]} == {timeframe}
    assert sorted(runner.CANONICAL_RESULT_POPULATIONS_DIR.glob("*.result_population.json")) == before


@pytest.mark.parametrize("timeframe", ["30m", "1h"])
def test_intraday_route_rejects_missing_and_wrong_csv(tmp_path, monkeypatch, timeframe):
    csv_path, catalog_path, validation_path, derivation_path, _ = (
        _write_intraday_derived_fixture(tmp_path, monkeypatch, timeframe)
    )
    with pytest.raises(runner.OfflineSweepError, match="does not exist"):
        runner._canonical_intraday_derived_execution_input(
            timeframe,
            tmp_path / "missing.csv",
            catalog_path,
            validation_path,
            derivation_path,
        )
    frame = pd.read_csv(csv_path)
    frame.loc[0, "close"] = 999.0
    frame.to_csv(csv_path, index=False, lineterminator="\n")
    with pytest.raises(runner.OfflineSweepError, match="CSV SHA256"):
        runner._canonical_intraday_derived_execution_input(
            timeframe,
            csv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("report_sha", "validation report SHA256"),
        ("parent_identity", "parent identity differs"),
        ("gap", "gap facts differ"),
        ("duplicate", "duplicate facts differ"),
        ("partial", "partial-window facts differ"),
        ("range", "coverage end differs"),
    ],
)
def test_intraday_route_rejects_broken_lineage_facts(
    tmp_path,
    monkeypatch,
    mutation,
    message,
):
    csv_path, catalog_path, validation_path, derivation_path, _ = (
        _write_intraday_derived_fixture(tmp_path, monkeypatch, "30m")
    )
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if mutation == "report_sha":
        catalog["validation_report"]["sha256"] = "0" * 64
    elif mutation == "parent_identity":
        catalog["parent"]["data_slice_identity"] = "wrong"
    elif mutation == "gap":
        catalog["gap_summary"]["gap_count"] = 1
        catalog["gap_summary"]["gaps"] = [{"fixture": True}]
    elif mutation == "duplicate":
        catalog["duplicate_summary"]["duplicate_row_count"] = 1
        catalog["duplicate_summary"]["duplicates"] = [{"fixture": True}]
    elif mutation == "partial":
        validation["validation"]["partial_window_count"] = 1
        _write_json(validation_path, validation)
        catalog["validation_report"]["sha256"] = runner._sha256_file_hex(validation_path)
    else:
        catalog["range"]["end_utc"] = "2026-12-31T00:00:00Z"
    _write_json(catalog_path, catalog)
    with pytest.raises(runner.OfflineSweepError, match=message):
        runner._canonical_intraday_derived_execution_input(
            "30m",
            csv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


def test_intraday_route_rejects_wrong_cadence(tmp_path, monkeypatch):
    csv_path, catalog_path, validation_path, derivation_path, _ = (
        _write_intraday_derived_fixture(
            tmp_path,
            monkeypatch,
            "30m",
            freq="1h",
        )
    )
    with pytest.raises(runner.OfflineSweepError, match="exactly 30m-spaced"):
        runner._canonical_intraday_derived_execution_input(
            "30m",
            csv_path,
            catalog_path,
            validation_path,
            derivation_path,
        )


@pytest.mark.parametrize("timeframe", ["30m", "1h"])
def test_research_features_bind_on_intraday_canonical_routes(
    tmp_path, monkeypatch, timeframe
):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path / "parents",
        strategy_mutator=lambda strategy: (
            _set_primary_timeframe(strategy, timeframe),
            _replace_first_data_ref_field(strategy, "taker_buy_sell_ratio"),
        ),
    )
    csv_path, _, _, _, catalog = _write_intraday_derived_fixture(
        tmp_path / "data", monkeypatch, timeframe
    )
    feature_manifest, feature_input = _write_research_feature_fixture(
        tmp_path / "features",
        csv_path,
        timeframe=timeframe,
        parent_identity=catalog["slice_identity"]["data_slice_identity"],
    )
    observed = []

    def fake_compile_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        observed.append(tuple(ohlcv.columns))
        return pd.Series(0.0, index=ohlcv.index)

    monkeypatch.setattr(runner, "compile_signal", fake_compile_signal)
    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        **{f"canonical_{timeframe}": True},
        ohlcv_input_path=csv_path,
        research_feature_manifest_path=feature_manifest,
        research_feature_input_path=feature_input,
    )
    coverage = result["result_population"]["data_coverage_summary"]
    assert result["wrote"] is False
    assert coverage["data_slice_identity"].startswith(
        f"cpw_research_composite_{timeframe}:sha256:"
    )
    assert all("taker_buy_sell_ratio" in columns for columns in observed)
    assert result["result_population"]["data_availability_claim"]["feature_sources"][0][
        "source_class"
    ] == CANONICAL_KLINE_TAKER_SOURCE_CLASS


@pytest.mark.parametrize("timeframe", ["30m", "1h"])
def test_intraday_identity_changes_result_identity_and_funding_binding_is_compatible(
    tmp_path,
    monkeypatch,
    timeframe,
):
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path / "parents",
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, timeframe),
    )
    csv_path, _, _, _, _ = _write_intraday_derived_fixture(
        tmp_path / "data",
        monkeypatch,
        timeframe,
    )
    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        **{f"canonical_{timeframe}": True},
        ohlcv_input_path=csv_path,
    )
    csv_path, catalog_path, validation_path, derivation_path, catalog = (
        _write_intraday_derived_fixture(
            tmp_path / "data",
            monkeypatch,
            timeframe,
            identity_suffix="a" * 64,
        )
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        **{f"canonical_{timeframe}": True},
        ohlcv_input_path=csv_path,
    )
    assert first["result_population_id"] != second["result_population_id"]
    execution_input = runner._canonical_intraday_derived_execution_input(
        timeframe,
        csv_path,
        catalog_path,
        validation_path,
        derivation_path,
    )
    funding = pd.DataFrame(
        {"funding_rate": [0.0001]},
        index=pd.DatetimeIndex([execution_input.ohlcv.index[0]]),
    )
    bound = runner._bind_funding_input(
        execution_input,
        funding_cost_mode="on",
        funding=funding,
        funding_identity={
            "funding_mode": "on",
            "fixture": True,
            "coverage_start_utc": execution_input.ohlcv.index[0].isoformat(),
            "coverage_end_utc": execution_input.ohlcv.index[-1].isoformat(),
        },
    )
    assert bound.timeframe == timeframe
    assert bound.data_slice_identity == catalog["slice_identity"]["data_slice_identity"]
    assert bound.funding_input_identity["funding_mode"] == "on"
