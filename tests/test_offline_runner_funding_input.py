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
    _canonical_parent_paths,
    _write_15m_ohlcv_fixture,
)
from tools.research_runner import run_offline_sweep as runner


REAL_REPO_ROOT = runner.REPO_ROOT


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _funding_times() -> list[int]:
    return [
        int(timestamp.timestamp() * 1000)
        for timestamp in pd.date_range("2026-01-01T00:00:00Z", periods=4, freq="8h")
    ]


def _configure_canonical_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, Path, dict[str, object]]:
    artifact, source, payload = _funding_provenance_fixture(
        tmp_path,
        times=_funding_times(),
        rates=[0.0001, -0.0002, 0.0003, -0.0004],
    )
    expected = {
        "funding_series_id": payload["funding_series_id"],
        "provenance_artifact_id": payload["provenance_artifact"]["artifact_id"],
        "provenance_artifact_path": artifact.relative_to(tmp_path).as_posix(),
        "provenance_artifact_sha256": _sha256(artifact),
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
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(runner, "CANONICAL_FUNDING_EXPECTED_IDENTITY", expected)
    return artifact, source, payload


def _manifest_funding_identity(payload: dict[str, object]) -> dict[str, object]:
    notes = payload["data_coverage_summary"]["data_coverage_notes"]
    encoded = next(note for note in notes if note.startswith("funding_input_identity="))
    return json.loads(encoded.split("=", 1)[1])


def test_canonical_funding_loader_preserves_exact_actual_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)

    funding, identity = runner._load_validated_funding_input(artifact, tmp_path)

    assert list(funding.index) == list(pd.to_datetime(_funding_times(), unit="ms", utc=True))
    assert funding["funding_rate"].tolist() == [0.0001, -0.0002, 0.0003, -0.0004]
    assert identity["funding_mode"] == "on"
    assert identity["timestamp_semantics"] == "actual_exchange_funding_event_timestamp"
    assert identity["boundary_rule_id"] == (
        "existing_backtest_left_open_right_closed_pre_fill_v1"
    )


def test_funding_on_reaches_backtester_and_binds_scratch_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    output_dir = tmp_path / "scratch_result_populations"
    calls: list[dict[str, object]] = []
    real_backtest = runner.run_backtest

    def no_network(*args, **kwargs):
        pytest.fail(f"network access attempted: args={args!r}, kwargs={kwargs!r}")

    def recording_backtest(*args, **kwargs):
        calls.append(kwargs)
        return real_backtest(*args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setattr(runner, "run_backtest", recording_backtest)

    first = runner.run_offline_sweep(
        strategy_path,
        manifest_path,
        sweep_path,
        output_dir=output_dir,
        write_result_population=True,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        funding_cost_mode="on",
        funding_provenance_path=artifact,
        funding_data_root=tmp_path,
        deterministic_seed=7,
    )
    second = runner.run_offline_sweep(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        funding_cost_mode="on",
        funding_provenance_path=artifact,
        funding_data_root=tmp_path,
        deterministic_seed=7,
    )

    assert calls
    assert all(call["funding_cost_mode"] == "on" for call in calls)
    expected_events = pd.to_datetime(_funding_times()[:3], unit="ms", utc=True)
    assert all(call["funding"].index.equals(expected_events) for call in calls)
    identity = _manifest_funding_identity(first["result_population"])
    assert set(identity) == {
        "funding_mode",
        "funding_series_id",
        "provenance_artifact_id",
        "provenance_artifact_path",
        "provenance_artifact_sha256",
        "funding_parquet_path",
        "funding_parquet_sha256",
        "coverage_start_utc",
        "coverage_end_utc",
        "timestamp_semantics",
        "rate_units",
        "boundary_rule_id",
    }
    assert identity["funding_mode"] == "on"
    assert runner._funding_identity_note(identity) in first["result_population"][
        "backtest_assumption_summary"
    ]["order_size_assumption"]
    assert first["result_population_id"] == second["result_population_id"]
    assert first["result_population"]["input_identity_hash"] == second["result_population"][
        "input_identity_hash"
    ]
    assert len(list(output_dir.glob("*.result_population.json"))) == 1


def test_funding_mode_changes_scientific_and_scratch_output_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    ohlcv_path = _write_15m_ohlcv_fixture(tmp_path)
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)

    off = runner.run_offline_sweep(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        deterministic_seed=7,
    )
    on = runner.run_offline_sweep(
        strategy_path,
        manifest_path,
        sweep_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_path,
        funding_cost_mode="on",
        funding_provenance_path=artifact,
        funding_data_root=tmp_path,
        deterministic_seed=7,
    )

    assert _manifest_funding_identity(off["result_population"])["funding_mode"] == "off"
    assert _manifest_funding_identity(on["result_population"])["funding_mode"] == "on"
    assert off["result_population_id"] != on["result_population_id"]
    assert off["result_population"]["input_identity_hash"]["hash"] != on[
        "result_population"
    ]["input_identity_hash"]["hash"]


@pytest.mark.parametrize("mode", ["auto", "required", "ON"])
def test_invalid_funding_mode_fails_closed(mode: str):
    with pytest.raises(runner.OfflineSweepError, match="funding-cost-mode"):
        runner._validate_funding_cost_mode(mode)


def test_funding_on_requires_provenance_and_canonical_input(tmp_path: Path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    with pytest.raises(runner.OfflineSweepError, match="funding-provenance is required"):
        runner.run_offline_sweep(
            strategy_path,
            manifest_path,
            sweep_path,
            funding_cost_mode="on",
        )


def test_funding_off_rejects_contradictory_provenance_argument(tmp_path: Path):
    strategy_path, manifest_path, sweep_path = _canonical_parent_paths()
    with pytest.raises(runner.OfflineSweepError, match="invalid when --funding-cost-mode=off"):
        runner.run_offline_sweep(
            strategy_path,
            manifest_path,
            sweep_path,
            funding_provenance_path=tmp_path / "anything.json",
        )


def test_wrong_artifact_path_and_hash_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    unbound = tmp_path / "research/data_provenance/funding/unbound.json"
    shutil.copy2(artifact, unbound)
    with pytest.raises(runner.OfflineSweepError, match="canonical funding provenance artifact"):
        runner._load_validated_funding_input(unbound, tmp_path)

    artifact.write_bytes(artifact.read_bytes() + b" ")
    with pytest.raises(runner.OfflineSweepError, match="provenance_artifact_sha256"):
        runner._load_validated_funding_input(artifact, tmp_path)


def test_tampered_parquet_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, source, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    source.write_bytes(source.read_bytes() + b"tamper")

    with pytest.raises(runner.OfflineSweepError, match="funding input validation failed"):
        runner._load_validated_funding_input(artifact, tmp_path)


def test_provenance_mutated_after_validation_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    real_validate = runner.validate_funding_artifact

    def validate_then_mutate(*args, **kwargs):
        validation = real_validate(*args, **kwargs)
        artifact.write_bytes(artifact.read_bytes() + b" ")
        return validation

    monkeypatch.setattr(runner, "validate_funding_artifact", validate_then_mutate)

    with pytest.raises(runner.OfflineSweepError, match="mutated after validation"):
        runner._load_validated_funding_input(artifact, tmp_path)


def test_on_mode_never_substitutes_zero_for_empty_window(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, _, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    funding, _ = runner._load_validated_funding_input(artifact, tmp_path)

    sliced = runner._slice_funding_for_window(
        funding,
        pd.Timestamp("2026-01-01T01:00:00Z"),
        pd.Timestamp("2026-01-01T02:00:00Z"),
    )

    assert sliced.empty
    assert list(sliced.columns) == ["funding_rate"]


def test_h004_contract_is_machine_guarded_as_funding_required():
    strategy = json.loads(
        (REAL_REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json").read_text(
            encoding="utf-8"
        )
    )
    sweep = json.loads(
        (REAL_REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json").read_text(
            encoding="utf-8"
        )
    )

    assert runner._requires_funding_costs(strategy, sweep) is True


def test_cli_has_no_arbitrary_funding_file_or_network_source_flag():
    parser = runner._build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert "--funding-cost-mode" in option_strings
    assert "--funding-provenance" in option_strings
    assert "--funding-data-root" in option_strings
    assert "--funding-input" not in option_strings
    assert not any("url" in option or "network" in option for option in option_strings)


def test_symlinked_funding_source_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    artifact, source, _ = _configure_canonical_fixture(tmp_path, monkeypatch)
    target = source.with_name("funding-target.parquet")
    source.rename(target)
    try:
        source.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")

    with pytest.raises(runner.OfflineSweepError, match="SYMLINK_REJECTED"):
        runner._load_validated_funding_input(artifact, tmp_path)
