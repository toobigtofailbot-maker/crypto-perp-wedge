from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from tools.data.materialize_takerflow_features import (
    HYDRATION_MANIFEST_VERSION,
    TakerflowMaterializationError,
    build_completed_bar_features,
    inspect_hydration_manifest,
    materialize_takerflow_features,
)
from tools.data_ingestion.takerflow_archive_recon import (
    parse_binance_um_aggtrade_archive,
    parse_binance_um_trade_archive,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "takerflow_archive_recon"
TRADES = FIXTURES / "trades_hand_calc.csv"
AGGTRADES = FIXTURES / "aggtrades_hand_calc.csv"
AVAILABILITY = (
    REPO_ROOT
    / "research"
    / "data_feature_availability"
    / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
HYDRATION = (
    REPO_ROOT
    / "research"
    / "data_feature_availability"
    / "BINANCE-USDM-BTCUSDT-AGGTRADES-HYDRATION-0001.json"
)
START = "2024-01-01T00:00:00.000Z"
END = "2024-01-01T00:45:00.000Z"


def _materialize(tmp_path: Path, inputs: list[Path], archive_type: str = "trades"):
    output = tmp_path / "features.csv"
    manifest_path = tmp_path / "manifest.json"
    manifest = materialize_takerflow_features(
        input_paths=inputs,
        archive_type=archive_type,
        interval="15m",
        start_utc=START,
        end_utc=END,
        output_path=output,
        manifest_path=manifest_path,
        availability_catalog_path=AVAILABILITY,
    )
    return output, manifest_path, manifest


def test_materializes_compiler_features_and_proves_buyer_maker_direction(tmp_path: Path):
    output, _, manifest = _materialize(tmp_path, [TRADES])
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["taker_buy_volume"] == "4"
    assert rows[0]["taker_sell_volume"] == "2"
    assert rows[0]["taker_total_volume"] == "6"
    assert rows[0]["taker_net_volume"] == "2"
    assert rows[0]["taker_imbalance"].startswith("0.333333333333333333")
    assert rows[0]["taker_buy_sell_ratio"] == "2"
    assert rows[0]["feature_available_at"] == "2024-01-01T00:15:00.000Z"
    assert manifest["buyer_maker_direction"]["is_buyer_maker_true"].startswith(
        "buyer is maker; seller is taker"
    )
    assert manifest["requested_range_data_complete"] is True


def test_aggtrades_preserve_underlying_trade_count_and_base_volume(tmp_path: Path):
    output, _, manifest = _materialize(tmp_path, [AGGTRADES], archive_type="aggTrades")
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["taker_buy_volume"] == "1"
    assert rows[0]["taker_sell_volume"] == "2"
    assert rows[0]["trade_count"] == "4"
    assert rows[0]["source_record_count"] == "2"
    assert manifest["archive_type"] == "aggTrades"


def test_exact_overlap_duplicate_is_removed_and_fully_accounted(tmp_path: Path):
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    first.write_text("\n".join([lines[0], *lines[1:4]]) + "\n", encoding="utf-8")
    second.write_text("\n".join([lines[0], *lines[3:]]) + "\n", encoding="utf-8")
    _, _, manifest = _materialize(tmp_path, [first, second])

    accounting = manifest["source_accounting"]
    assert accounting["parsed_source_row_count"] == 6
    assert accounting["exact_duplicate_row_count_removed"] == 1
    assert accounting["unique_source_row_count"] == 5
    assert manifest["coverage"]["source_rows_in_requested_range"] == 5


def test_conflicting_duplicate_fails_closed(tmp_path: Path):
    first = tmp_path / "a.csv"
    conflicting = tmp_path / "b.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    first.write_text("\n".join([lines[0], *lines[1:4]]) + "\n", encoding="utf-8")
    fields = lines[3].split(",")
    fields[1] = "999"
    conflicting.write_text(
        "\n".join([lines[0], ",".join(fields), *lines[4:]]) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(TakerflowMaterializationError, match="conflicting duplicate event_id"):
        _materialize(tmp_path, [first, conflicting])


def test_gap_and_no_silent_row_drop_accounting_are_explicit(tmp_path: Path):
    gapped = tmp_path / "gapped.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    kept = [lines[0], *lines[1:4], lines[5]]
    gapped.write_text("\n".join(kept) + "\n", encoding="utf-8")
    _, _, manifest = _materialize(tmp_path, [gapped])

    assert manifest["coverage"]["expected_bar_count"] == 3
    assert manifest["coverage"]["observed_bar_count"] == 2
    assert manifest["coverage"]["missing_bar_count"] == 1
    assert manifest["coverage"]["missing_bar_ranges"][0]["first_open_time_utc"] == (
        "2024-01-01T00:15:00.000Z"
    )
    assert manifest["source_event_id_gaps"]["gap_count"] == 1
    assert manifest["requested_range_data_complete"] is False


def test_completed_bar_bucketing_is_utc_boundary_causal():
    rows = parse_binance_um_trade_archive(TRADES)
    boundary = replace(rows[0], event_id=999, timestamp_ms=1704068100000)
    features, _ = build_completed_bar_features(
        [rows[0], boundary],
        interval="15m",
        start_ms=1704067200000,
        end_ms=1704069000000,
    )

    assert [row["open_time_ms"] for row in features] == [1704067200000, 1704068100000]
    assert features[0]["taker_sell_volume"] == "2"
    assert features[1]["taker_sell_volume"] == "2"


def test_future_rows_do_not_change_prior_completed_bars():
    rows = parse_binance_um_trade_archive(TRADES)
    prior, _ = build_completed_bar_features(
        rows[:3],
        interval="15m",
        start_ms=1704067200000,
        end_ms=1704068100000,
    )
    complete, _ = build_completed_bar_features(
        rows,
        interval="15m",
        start_ms=1704067200000,
        end_ms=1704069900000,
    )

    assert complete[0] == prior[0]


def test_output_and_manifest_hash_are_deterministic_on_rerun(tmp_path: Path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first_output, _, first = _materialize(first_dir, [TRADES])
    second_output, _, second = _materialize(second_dir, [TRADES])

    assert first_output.read_bytes() == second_output.read_bytes()
    assert first["output"]["sha256"] == second["output"]["sha256"]
    assert first["output"]["size_bytes"] == second["output"]["size_bytes"]
    assert len(first["output"]["sha256"]) == 64


def test_full_history_hydration_manifest_is_exact():
    payload = json.loads(HYDRATION.read_text(encoding="utf-8"))
    inspection = inspect_hydration_manifest(HYDRATION)

    assert payload["manifest_version"] == HYDRATION_MANIFEST_VERSION
    assert payload["request"]["requested_bar_count"] == 220128
    assert inspection["expected_file_count"] == 76
    assert inspection["expected_checksum_file_count"] == 76
    assert inspection["present_file_count"] + inspection["missing_file_count"] == 76
    all_paths = sorted([*inspection["present_paths"], *inspection["missing_paths"]])
    assert all_paths[0].endswith("BTCUSDT-aggTrades-2020-01.zip")
    assert all_paths[-1].endswith("BTCUSDT-aggTrades-2026-04.zip")


def test_hydration_inspection_reports_exact_missing_partitions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    payload = json.loads(HYDRATION.read_text(encoding="utf-8"))
    payload["local_archive_root"] = "archives"
    manifest = tmp_path / "hydration.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    inspection = inspect_hydration_manifest(manifest)

    assert inspection["present_file_count"] == 0
    assert inspection["missing_file_count"] == 76
    assert inspection["missing_checksum_file_count"] == 76
    assert inspection["status"] == "READY-FOR-HYDRATION"


def test_hydration_requires_matching_official_checksum_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    payload = json.loads(HYDRATION.read_text(encoding="utf-8"))
    payload["local_archive_root"] = "archives"
    payload["request"]["end_utc_exclusive"] = "2020-02-01T00:00:00.000Z"
    payload["partition_contract"]["last_partition"] = "2020-01"
    payload["partition_contract"]["expected_partition_count"] = 1
    manifest = tmp_path / "hydration.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    archive_dir = tmp_path / "archives"
    archive_dir.mkdir()
    archive = archive_dir / "BTCUSDT-aggTrades-2020-01.zip"
    archive.write_bytes(b"fixture archive bytes")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_name(archive.name + ".CHECKSUM")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert inspect_hydration_manifest(manifest)["status"] == "READY"

    checksum.write_text(f"{'0' * 64}  {archive.name}\n", encoding="utf-8")
    blocked = inspect_hydration_manifest(manifest)
    assert blocked["status"] == "BLOCKED"
    assert blocked["checksum_mismatch_count"] == 1


def test_non_project_interval_and_unaligned_window_fail_closed():
    rows = parse_binance_um_trade_archive(TRADES)
    with pytest.raises(TakerflowMaterializationError, match="interval must be one of"):
        build_completed_bar_features(rows, interval="5m", start_ms=0, end_ms=300000)
    with pytest.raises(TakerflowMaterializationError, match="interval boundaries"):
        build_completed_bar_features(
            rows,
            interval="15m",
            start_ms=1704067200001,
            end_ms=1704068100000,
        )


def test_source_files_are_hashed_in_stable_path_order(tmp_path: Path):
    later = tmp_path / "z.csv"
    earlier = tmp_path / "a.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    earlier.write_text("\n".join([lines[0], *lines[1:4]]) + "\n", encoding="utf-8")
    later.write_text("\n".join([lines[0], *lines[4:]]) + "\n", encoding="utf-8")
    _, _, manifest = _materialize(tmp_path, [later, earlier])

    assert [Path(item["path"]).name for item in manifest["source_files"]] == ["a.csv", "z.csv"]
    assert all(len(item["sha256"]) == 64 for item in manifest["source_files"])


def test_non_monotonic_source_archive_fails_closed(tmp_path: Path):
    unordered = tmp_path / "unordered.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    unordered.write_text(
        "\n".join([lines[0], lines[2], lines[1], *lines[3:]]) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(TakerflowMaterializationError, match="not monotonic"):
        _materialize(tmp_path, [unordered])


def test_ratio_precision_uses_decimal_not_binary_float():
    rows = parse_binance_um_trade_archive(TRADES)
    adjusted = [
        replace(rows[1], base_quantity=Decimal("0.1")),
        replace(rows[2], base_quantity=Decimal("0.2")),
    ]
    features, _ = build_completed_bar_features(
        adjusted,
        interval="15m",
        start_ms=1704067200000,
        end_ms=1704068100000,
    )

    assert features[0]["taker_buy_volume"] == "0.3"
