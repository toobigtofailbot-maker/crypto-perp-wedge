from __future__ import annotations

import hashlib
import json
import shutil
import socket
from pathlib import Path

import pandas as pd
import pytest

from tests.test_funding_series_provenance import _fixture as _funding_provenance_fixture
from tests.test_offline_research_runner import (
    _run,
    _set_primary_timeframe,
    _set_variant_count,
    _write_fixture,
)
from tools.data.register_binance_usdtm_1d_lineage import (
    DEFAULT_LOGICAL_PATH,
    build_lineage,
    canonical_json_bytes,
)
from tools.research_runner import run_offline_sweep as runner
from tools.research_runner.spec_signal_compiler import compile_signal


REAL_REPO_ROOT = runner.REPO_ROOT


def _sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _daily_frame(*, periods: int = 240, first_open: float = 100.0) -> pd.DataFrame:
    rows = []
    for index, timestamp in enumerate(
        pd.date_range("2025-01-01T00:00:00Z", periods=periods, freq="1D")
    ):
        open_time_ms = int(timestamp.timestamp() * 1000)
        open_price = first_open + index * 0.25
        close_price = open_price + (0.5 if index % 2 == 0 else -0.25)
        rows.append(
            {
                "open_time_ms": open_time_ms,
                "open": open_price,
                "high": max(open_price, close_price) + 1.0,
                "low": min(open_price, close_price) - 1.0,
                "close": close_price,
                "volume": 1000.0 + index,
                "close_time_ms": open_time_ms + 86_400_000 - 1,
                "quote_asset_volume": 100_000.0 + index,
                "num_trades": 100 + index,
                "taker_buy_base_vol": 500.0 + index,
                "taker_buy_quote_vol": 50_000.0 + index,
                "ignore": "0",
            }
        )
    return pd.DataFrame(rows)


def _configure_1d_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    frame: pd.DataFrame | None = None,
) -> tuple[Path, Path]:
    source_path = tmp_path.joinpath(*Path(DEFAULT_LOGICAL_PATH).parts)
    source_path.parent.mkdir(parents=True, exist_ok=True)
    (frame if frame is not None else _daily_frame()).to_parquet(source_path, index=False)
    source_sha256 = _sha256_hex(source_path)

    catalog_path = (
        tmp_path
        / "research/data_slices/binance_usdtm_btcusdt_1d/"
        "binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json"
    )
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_bytes(
        canonical_json_bytes(
            build_lineage(
                source_path,
                logical_path=DEFAULT_LOGICAL_PATH,
                expected_sha256=source_sha256,
            )
        )
    )

    validator_path = tmp_path / "tools/data/register_binance_usdtm_1d_lineage.py"
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REAL_REPO_ROOT / "tools/data/register_binance_usdtm_1d_lineage.py",
        validator_path,
    )

    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "DEFAULT_1D_CATALOG_SLICE_PATH", catalog_path)
    monkeypatch.setattr(runner, "DEFAULT_1D_VALIDATOR_PATH", validator_path)
    monkeypatch.setattr(runner, "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256", _sha256_hex(catalog_path))
    monkeypatch.setattr(runner, "OFFICIAL_1D_SOURCE_SHA256", source_sha256)
    monkeypatch.setattr(runner, "OFFICIAL_1D_SOURCE_BYTE_LENGTH", source_path.stat().st_size)
    monkeypatch.setattr(
        runner,
        "OFFICIAL_1D_ROW_COUNT",
        len(frame) if frame is not None else 240,
    )
    return catalog_path, source_path


def _one_variant_1d_parents(tmp_path: Path) -> tuple[Path, Path, Path]:
    strategy_path, manifest_path, sweep_path, *_ = _write_fixture(
        tmp_path,
        manifest_mutator=lambda manifest: _set_variant_count(manifest, 1),
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, "1d"),
    )
    return strategy_path, manifest_path, sweep_path


def _configure_funding_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    times = [
        int(timestamp.timestamp() * 1000)
        for timestamp in pd.date_range(
            "2024-12-31T16:00:00Z",
            "2025-08-29T08:00:00Z",
            freq="8h",
        )
    ]
    artifact, _, payload = _funding_provenance_fixture(
        tmp_path,
        times=times,
        rates=[0.0001 if index % 2 == 0 else -0.0001 for index in range(len(times))],
    )
    expected = {
        "funding_series_id": payload["funding_series_id"],
        "provenance_artifact_id": payload["provenance_artifact"]["artifact_id"],
        "provenance_artifact_path": artifact.relative_to(tmp_path).as_posix(),
        "provenance_artifact_sha256": "sha256:" + _sha256_hex(artifact),
        "funding_parquet_path": payload["file_identity"]["source_data_path"],
        "funding_parquet_sha256": payload["file_identity"]["raw_sha256"],
        "funding_parquet_byte_length": payload["file_identity"]["byte_length"],
        "funding_parquet_row_count": payload["file_identity"]["row_count"],
        "coverage_start_utc": payload["coverage"]["start_utc"],
        "coverage_end_utc": payload["coverage"]["end_utc"],
        "timestamp_semantics": payload["event_fields"]["timestamp"]["semantics"],
        "rate_units": payload["event_fields"]["funding_rate"]["units"],
        "boundary_rule_id": payload["alignment"]["boundary_rule_id"],
    }
    monkeypatch.setattr(runner, "CANONICAL_FUNDING_EXPECTED_IDENTITY", expected)
    return artifact


def _identity(payload: dict[str, object]) -> dict[str, object]:
    notes = payload["data_coverage_summary"]["data_coverage_notes"]
    encoded = next(
        note for note in notes if note.startswith("canonical_1d_input_identity=")
    )
    return json.loads(encoded.split("=", 1)[1])


def test_canonical_1d_loads_exact_validated_catalog_data_and_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    catalog_path, source_path = _configure_1d_fixture(tmp_path, monkeypatch)

    first = runner._canonical_1d_execution_input()
    second = runner._canonical_1d_execution_input()
    identity = json.loads(
        next(
            note
            for note in first.data_coverage_notes
            if note.startswith("canonical_1d_input_identity=")
        ).split("=", 1)[1]
    )

    assert first.timeframe == "1d"
    assert first.ohlcv.index.tz is not None
    assert first.ohlcv.index[0] == pd.Timestamp("2025-01-01T00:00:00Z")
    assert first.ohlcv.index.to_series().diff().dropna().eq(pd.Timedelta(days=1)).all()
    assert list(first.ohlcv.columns) == list(runner.REQUIRED_OHLCV_COLUMNS)
    assert first.data_slice_identity == second.data_slice_identity
    assert first.data_catalog_ref == second.data_catalog_ref
    assert identity["canonical_route"] == "1d"
    assert identity["catalog_sha256"] == "sha256:" + _sha256_hex(catalog_path)
    assert identity["source_raw_sha256"] == "sha256:" + _sha256_hex(source_path)
    assert identity["source_byte_length"] == source_path.stat().st_size
    assert identity["row_count"] == 240
    assert identity["timeframe"] == "1d"
    assert identity["cadence_ms"] == 86_400_000
    assert identity["timezone"] == "UTC"
    assert identity["source_type"] == "direct_public_archive_snapshot"
    assert identity["parent_identity"] is None
    assert identity["derivation_identity"] is None
    assert identity["duplicate_row_count"] == 0
    assert identity["gap_count"] == 0
    assert identity["open_or_incomplete_bar_count"] == 0


def test_generic_1d_smoke_reaches_unchanged_backtester_and_binds_scratch_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_1d_fixture(tmp_path, monkeypatch)
    strategy_path, manifest_path, sweep_path = _one_variant_1d_parents(tmp_path)
    calls: list[dict[str, object]] = []
    real_backtest = runner.run_backtest

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    def fixture_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[2:20] = 1.0
        return signal

    monkeypatch.setattr(runner, "compile_signal", fixture_signal)
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)
    first = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_1d=True,
        deterministic_seed=7,
    )
    second = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_1d=True,
        deterministic_seed=7,
    )

    assert first["ok"] is True
    assert calls
    assert all(call["interval"] == "1d" for call in calls)
    assert all(call["funding_cost_mode"] == "off" for call in calls)
    assert first["result_population_id"] == second["result_population_id"]
    assert first["result_population"]["input_identity_hash"] == second["result_population"][
        "input_identity_hash"
    ]
    identity = _identity(first["result_population"])
    assert identity["canonical_route"] == "1d"
    assert first["result_population"]["data_coverage_summary"]["timeframe"] == "1d"
    assert "data_coverage_summary.data_slice_identity" in first["result_population"][
        "input_identity_hash"
    ]["hash_scope"]


def test_canonical_1d_funding_on_reaches_unchanged_backtester_with_actual_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_1d_fixture(tmp_path, monkeypatch)
    artifact = _configure_funding_fixture(tmp_path, monkeypatch)
    strategy_path, manifest_path, sweep_path = _one_variant_1d_parents(tmp_path)
    calls: list[dict[str, object]] = []
    real_backtest = runner.run_backtest

    def no_network(*args, **kwargs):
        pytest.fail(f"network access attempted: args={args!r}, kwargs={kwargs!r}")

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    def fixture_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        signal = pd.Series(0.0, index=ohlcv.index)
        signal.iloc[2:20] = 1.0
        return signal

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(runner, "compile_signal", fixture_signal)
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)
    result = _run(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_1d=True,
        funding_cost_mode="on",
        funding_provenance_path=artifact,
        funding_data_root=tmp_path,
        deterministic_seed=7,
    )

    assert result["ok"] is True
    assert calls
    assert all(call["interval"] == "1d" for call in calls)
    assert all(call["funding_cost_mode"] == "on" for call in calls)
    assert all(not call["funding"].empty for call in calls)
    assert all(
        call["funding"].index.equals(
            pd.DatetimeIndex(call["funding"].index).sort_values()
        )
        for call in calls
    )
    assert _identity(result["result_population"])["canonical_route"] == "1d"
    assert any(
        note.startswith("funding_input_identity=")
        for note in result["result_population"]["data_coverage_summary"][
            "data_coverage_notes"
        ]
    )


def test_h004_primitives_compile_on_validated_1d_without_running_sweep(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_1d_fixture(tmp_path, monkeypatch)
    execution_input = runner._canonical_1d_execution_input()
    strategy = json.loads(
        (
            REAL_REPO_ROOT
            / "research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (
            REAL_REPO_ROOT
            / "research/variant_manifests/VM-0007.variant_manifest.json"
        ).read_text(encoding="utf-8")
    )

    signal = compile_signal(
        strategy,
        manifest["variant_assignments"][0],
        execution_input.ohlcv,
        funding=execution_input.funding,
    )

    assert signal.index.equals(execution_input.ohlcv.index)
    assert len(signal) == len(execution_input.ohlcv)


@pytest.mark.parametrize(
    ("canonical_15m", "canonical_4h", "canonical_1d"),
    [
        (True, True, False),
        (True, False, True),
        (False, True, True),
    ],
)
def test_canonical_route_flags_are_mutually_exclusive(
    tmp_path: Path,
    canonical_15m: bool,
    canonical_4h: bool,
    canonical_1d: bool,
):
    strategy_path, manifest_path, sweep_path = _one_variant_1d_parents(tmp_path)
    with pytest.raises(runner.OfflineSweepError, match="mutually exclusive"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_15m=canonical_15m,
            canonical_4h=canonical_4h,
            canonical_1d=canonical_1d,
        )


def test_canonical_1d_rejects_non_1d_parents_and_arbitrary_input(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_1d_fixture(tmp_path, monkeypatch)
    non_1d = _write_fixture(
        tmp_path / "non_1d",
        manifest_mutator=lambda manifest: _set_variant_count(manifest, 1),
        strategy_mutator=lambda strategy: _set_primary_timeframe(strategy, "4h"),
    )
    with pytest.raises(runner.OfflineSweepError, match="requires 1d"):
        _run(*non_1d[:3], canonical_1d=True)

    one_day = _one_variant_1d_parents(tmp_path / "one_day")
    with pytest.raises(runner.OfflineSweepError, match="forbidden"):
        _run(
            *one_day,
            canonical_1d=True,
            ohlcv_input_path=tmp_path / "arbitrary.parquet",
        )


def test_h004_canonical_1d_fails_before_execution_when_funding_is_off(
    monkeypatch: pytest.MonkeyPatch,
):
    strategy_path = (
        REAL_REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json"
    )
    manifest_path = (
        REAL_REPO_ROOT / "research/variant_manifests/VM-0007.variant_manifest.json"
    )
    sweep_path = REAL_REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json"

    monkeypatch.setattr(
        runner,
        "run_backtest",
        lambda *args, **kwargs: pytest.fail("H-004 backtest must not execute"),
    )
    with pytest.raises(runner.OfflineSweepError, match="funding mode is off"):
        _run(
            strategy_path,
            manifest_path,
            sweep_path,
            canonical_1d=True,
            funding_cost_mode="off",
        )


def test_canonical_1d_rejects_ohlcv_outside_funding_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _configure_1d_fixture(tmp_path, monkeypatch)
    execution_input = runner._canonical_1d_execution_input()
    funding = pd.DataFrame(
        {"funding_rate": [0.0001]},
        index=pd.DatetimeIndex([pd.Timestamp("2025-01-02T00:00:00Z")]),
    )
    identity = {
        "coverage_start_utc": "2025-01-02T00:00:00Z",
        "coverage_end_utc": "2025-08-29T00:00:00Z",
    }
    with pytest.raises(runner.OfflineSweepError, match="starts before"):
        runner._bind_funding_input(
            execution_input,
            funding_cost_mode="on",
            funding=funding,
            funding_identity=identity,
        )

    identity["coverage_start_utc"] = "2024-12-31T00:00:00Z"
    identity["coverage_end_utc"] = "2025-08-27T00:00:00Z"
    with pytest.raises(runner.OfflineSweepError, match="ends after"):
        runner._bind_funding_input(
            execution_input,
            funding_cost_mode="on",
            funding=funding,
            funding_identity=identity,
        )


def test_canonical_1d_rejects_path_escape_backslash_and_symlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    catalog_path, source_path = _configure_1d_fixture(tmp_path, monkeypatch)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    catalog["path"] = "../outside.parquet"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(runner, "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256", _sha256_hex(catalog_path))
    with pytest.raises(runner.OfflineSweepError, match="repository-relative"):
        runner._canonical_1d_execution_input()

    catalog["path"] = r"data\processed\source.parquet"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(runner, "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256", _sha256_hex(catalog_path))
    with pytest.raises(runner.OfflineSweepError, match="POSIX path"):
        runner._canonical_1d_execution_input()

    catalog["path"] = DEFAULT_LOGICAL_PATH
    catalog_path.write_bytes(canonical_json_bytes(catalog))
    monkeypatch.setattr(runner, "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256", _sha256_hex(catalog_path))
    target = source_path.with_name("target.parquet")
    source_path.rename(target)
    try:
        source_path.symlink_to(target)
    except OSError:
        real_is_symlink = Path.is_symlink
        monkeypatch.setattr(
            Path,
            "is_symlink",
            lambda path: path == source_path or real_is_symlink(path),
        )
    with pytest.raises(runner.OfflineSweepError, match="link"):
        runner._canonical_1d_execution_input()


def test_canonical_1d_rejects_missing_or_private_catalog_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    catalog_path, _ = _configure_1d_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        runner,
        "DEFAULT_1D_CATALOG_SLICE_PATH",
        catalog_path.with_name("missing.catalog_slice.json"),
    )
    with pytest.raises(runner.OfflineSweepError, match="does not exist"):
        runner._canonical_1d_execution_input()

    monkeypatch.setattr(runner, "DEFAULT_1D_CATALOG_SLICE_PATH", catalog_path)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["source"]["credentials_used"] = True
    catalog_path.write_bytes(canonical_json_bytes(catalog))
    monkeypatch.setattr(
        runner,
        "OFFICIAL_1D_CATALOG_ARTIFACT_SHA256",
        _sha256_hex(catalog_path),
    )
    with pytest.raises(runner.OfflineSweepError, match="credential-free"):
        runner._canonical_1d_execution_input()


def test_canonical_1d_rejects_post_validation_source_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _, source_path = _configure_1d_fixture(tmp_path, monkeypatch)
    real_build = runner.build_1d_lineage

    def validate_then_mutate(*args, **kwargs):
        result = real_build(*args, **kwargs)
        changed = _daily_frame(first_open=101.0)
        changed.to_parquet(source_path, index=False)
        return result

    monkeypatch.setattr(runner, "build_1d_lineage", validate_then_mutate)

    with pytest.raises(runner.OfflineSweepError, match="mutated after validation/read"):
        runner._canonical_1d_execution_input()


def test_1d_data_identity_change_changes_scientific_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    first_root = tmp_path / "first"
    _configure_1d_fixture(first_root, monkeypatch)
    first_parents = _one_variant_1d_parents(first_root)

    def fixture_signal(strategy_spec, variant, ohlcv, funding=None):
        del strategy_spec, variant, funding
        return pd.Series(0.0, index=ohlcv.index)

    monkeypatch.setattr(runner, "compile_signal", fixture_signal)
    first = _run(*first_parents, canonical_1d=True, deterministic_seed=7)

    second_root = tmp_path / "second"
    _configure_1d_fixture(
        second_root,
        monkeypatch,
        frame=_daily_frame(first_open=101.0),
    )
    second_parents = _one_variant_1d_parents(second_root)
    second = _run(*second_parents, canonical_1d=True, deterministic_seed=7)

    assert first["result_population_id"] != second["result_population_id"]
    assert first["result_population"]["input_identity_hash"]["hash"] != second[
        "result_population"
    ]["input_identity_hash"]["hash"]


def test_canonical_1d_cli_is_explicit_and_has_no_acquisition_surface():
    parser = runner._build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert "--canonical-1d" in option_strings
    assert not any(
        token in option
        for option in option_strings
        for token in ("url", "network", "fetch", "credential", "private")
    )
