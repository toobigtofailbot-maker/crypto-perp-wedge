from __future__ import annotations

import csv
import calendar
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
import pandas as pd

from tools.data.materialize_takerflow_features import (
    CANONICAL_KLINE_PARENT_CONFIG,
    CANONICAL_KLINE_TAKER_SOURCE_CLASS,
    CANONICAL_ORDER_VERSION,
    D4_PROJECTION_SHA256,
    D4_TAKER_SOURCE_CLASS,
    PARTITION_CACHE_VERSION,
    SOURCE_POLICY_VERSION,
    TakerflowMaterializationError,
    _build_parser,
    build_completed_bar_features,
    inspect_hydration_manifest,
    materialize_takerflow_features,
    materialize_d4_native_takerflow_features,
    materialize_canonical_kline_takerflow_features,
    materialize_partitioned_takerflow_features,
)
from tools.data_ingestion.takerflow_archive_recon import (
    parse_binance_um_aggtrade_archive,
    parse_binance_um_trade_archive,
)
from tools.registry.validate_research_feature_table_manifest import (
    validate_manifest_payload,
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


def _write_d4_fixture(tmp_path: Path, rows: list[tuple[str, int, str]] | None = None) -> Path:
    path = tmp_path / "d4.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    values = rows or [("6", 3, "4"), ("4", 0, "4"), ("5", 2, "0")]
    start_ms = 1704067200000
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "open_time_ms",
                "open_time",
                "volume",
                "close_time_ms",
                "num_trades",
                "taker_buy_base_vol",
            ]
        )
        for index, (volume, trades, buy) in enumerate(values):
            open_ms = start_ms + index * 900000
            writer.writerow(
                [
                    open_ms,
                    datetime.fromtimestamp(open_ms / 1000, tz=UTC)
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                    volume,
                    open_ms + 899999,
                    trades,
                    buy,
                ]
            )
    return path


def _materialize_d4(tmp_path: Path, *, rows=None, identity: str | None = None):
    d4 = _write_d4_fixture(tmp_path, rows)
    output = tmp_path / "d4-features.csv"
    manifest_path = tmp_path / "d4-features.manifest.json"
    digest = hashlib.sha256(d4.read_bytes()).hexdigest()
    kwargs = {}
    if identity is not None:
        kwargs["data_slice_identity"] = identity
    manifest = materialize_d4_native_takerflow_features(
        d4_path=d4,
        output_path=output,
        manifest_path=manifest_path,
        availability_catalog_path=AVAILABILITY,
        expected_sha256=digest,
        expected_rows=3,
        coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
        coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
        **kwargs,
    )
    return d4, output, manifest_path, manifest


def _write_generic_parent(tmp_path: Path, timeframe: str, *, parquet: bool = False) -> tuple[Path, dict]:
    delta = {"30m": 1_800_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}[timeframe]
    start_ms = 1704067200000
    rows = [
        {"open_time_ms": start_ms + index * delta, "open_time": _iso, "volume": volume,
         "close_time_ms": start_ms + (index + 1) * delta - 1, "num_trades": trades,
         "taker_buy_base_vol": buy}
        for index, (volume, trades, buy) in enumerate((("6", 3, "4"), ("4", 0, "4"), ("5", 2, "0")))
        for _iso in [datetime.fromtimestamp((start_ms + index * delta) / 1000, tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")]
    ]
    path = tmp_path / ("parent.parquet" if parquet else "parent.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    if parquet:
        pd.DataFrame(rows).drop(columns=["open_time"]).to_parquet(path, index=False)
    else:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    hash_label = "identity_sha256" if timeframe == "1d" else "sha256"
    config = {
        "sha256": digest,
        "row_count": 3,
        "coverage_start": "2024-01-01T00:00:00.000Z",
        "coverage_end": datetime.fromtimestamp((start_ms + 3 * delta) / 1000, tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "data_slice_identity": f"binance_usdtm_btcusdt_ohlcv_{timeframe}:{hash_label}:" + "1" * 64,
        "format": "parquet" if parquet else "csv",
    }
    return path, config


def _materialize_generic(tmp_path: Path, timeframe: str, *, parquet: bool = False, config_override=None):
    parent, config = _write_generic_parent(tmp_path, timeframe, parquet=parquet)
    original_parent_bytes = parent.read_bytes()
    original_parent_mtime_ns = parent.stat().st_mtime_ns
    if config_override:
        config.update(config_override)
    manifest = materialize_canonical_kline_takerflow_features(
        canonical_kline_path=parent,
        timeframe=timeframe,
        output_path=tmp_path / "features.csv",
        manifest_path=tmp_path / "features.manifest.json",
        availability_catalog_path=AVAILABILITY,
        _parent_config=config,
    )
    assert parent.read_bytes() == original_parent_bytes
    assert parent.stat().st_mtime_ns == original_parent_mtime_ns
    return parent, tmp_path / "features.csv", manifest


def _write_zip(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "id,price,qty,quoteQty,time,isBuyerMaker\n"
    body = header + "".join(",".join(row) + "\n" for row in rows)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(path.with_suffix(".csv").name, body)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_name(path.name + ".CHECKSUM").write_text(
        f"{digest}  {path.name}\n", encoding="utf-8"
    )


def _month_rows(year: int = 2024, month: int = 1) -> list[list[str]]:
    start = datetime(year, month, 1, tzinfo=UTC)
    count = calendar.monthrange(year, month)[1] * 96
    first_id = 1_000_000
    rows = []
    for offset in range(count):
        event_id = first_id + offset
        timestamp_ms = int((start + timedelta(minutes=15 * offset)).timestamp() * 1000)
        rows.append(
            [
                str(event_id), "100", "1", "100", str(timestamp_ms),
                "true" if offset % 2 else "false",
            ]
        )
    return rows


def _write_partition_fixture(
    tmp_path: Path,
    *,
    monthly_rows: list[list[str]] | None = None,
    write_daily: bool = False,
) -> dict[str, Path | str | int]:
    rows = _month_rows()
    monthly_root = tmp_path / "monthly"
    daily_root = tmp_path / "daily"
    monthly = monthly_root / "BTCUSDT-trades-2024-01.zip"
    _write_zip(monthly, rows if monthly_rows is None else monthly_rows)
    if write_daily:
        for day in range(1, 32):
            daily_rows = rows[(day - 1) * 96 : day * 96]
            _write_zip(
                daily_root / f"BTCUSDT-trades-2024-01-{day:02d}.zip",
                daily_rows,
            )
    d4 = tmp_path / "d4.csv"
    with d4.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["open_time_ms", "volume", "num_trades", "taker_buy_base_vol"])
        for index, row in enumerate(rows):
            writer.writerow([row[4], "1", "1", "0" if index % 2 else "1"])
    d4_sha = hashlib.sha256(d4.read_bytes()).hexdigest()
    return {
        "monthly_root": monthly_root,
        "daily_root": daily_root,
        "cache_root": tmp_path / "cache",
        "output": tmp_path / "features.csv",
        "manifest": tmp_path / "features.manifest.json",
        "d4": d4,
        "d4_sha": d4_sha,
        "row_count": len(rows),
    }


def _partitioned(fixture: dict[str, Path | str | int], **overrides):
    kwargs = {
        "monthly_root": fixture["monthly_root"],
        "daily_root": fixture["daily_root"],
        "cache_root": fixture["cache_root"],
        "start_utc": "2024-01-01T00:00:00.000Z",
        "end_utc": "2024-02-01T00:00:00.000Z",
        "output_path": fixture["output"],
        "manifest_path": fixture["manifest"],
        "availability_catalog_path": AVAILABILITY,
        "d4_path": fixture["d4"],
        "d4_expected_sha256": fixture["d4_sha"],
        "d4_expected_rows": fixture["row_count"],
        "chunk_rows": 101,
    }
    kwargs.update(overrides)
    return materialize_partitioned_takerflow_features(**kwargs)


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


def test_d4_native_materializer_has_exact_formulas_nulls_and_identity(tmp_path: Path):
    _, output, _, manifest = _materialize_d4(tmp_path)
    rows = list(csv.DictReader(output.open(encoding="utf-8", newline="")))
    assert [(row["taker_buy_volume"], row["taker_sell_volume"]) for row in rows] == [
        ("4", "2"),
        ("4", "0"),
        ("0", "5"),
    ]
    assert [row["taker_buy_sell_ratio"] for row in rows] == ["2", "", "0"]
    assert manifest["research_feature_table"]["source_class"] == D4_TAKER_SOURCE_CLASS
    assert manifest["proof"]["zero_sell_count"] == 1
    assert manifest["proof"]["null_ratio_count"] == 1
    assert validate_manifest_payload(manifest) == []


@pytest.mark.parametrize("timeframe", ["30m", "1h", "4h"])
def test_generic_canonical_kline_materializer_is_closed_and_row_local(
    tmp_path: Path, timeframe: str
) -> None:
    _, output, manifest = _materialize_generic(tmp_path, timeframe)
    rows = list(csv.DictReader(output.open(encoding="utf-8", newline="")))
    assert [(row["taker_buy_volume"], row["taker_sell_volume"]) for row in rows] == [
        ("4", "2"), ("4", "0"), ("0", "5")
    ]
    assert [row["taker_buy_sell_ratio"] for row in rows] == ["2", "", "0"]
    contract = manifest["research_feature_table"]
    assert contract["source_class"] == CANONICAL_KLINE_TAKER_SOURCE_CLASS
    assert contract["derivation"]["derivation_version"] == "cpw_canonical_kline_takerflow_v2"
    assert contract["timeframe"] == timeframe
    assert manifest["proof"]["zero_sell_count"] == manifest["proof"]["null_ratio_count"] == 1
    assert validate_manifest_payload(manifest) == []


def test_generic_one_day_materializer_reads_exact_parquet_parent(tmp_path: Path) -> None:
    _, output, manifest = _materialize_generic(tmp_path, "1d", parquet=True)
    assert len(list(csv.DictReader(output.open(encoding="utf-8", newline="")))) == 3
    assert manifest["source_type"] == "canonical_1d_kline_parquet"
    assert manifest["research_feature_table"]["parent_identity"]["data_slice_identity"].startswith(
        "binance_usdtm_btcusdt_ohlcv_1d:identity_sha256:"
    )


def test_generic_materializer_rejects_15m_and_locked_parent_drift(tmp_path: Path) -> None:
    parent, _ = _write_generic_parent(tmp_path, "30m")
    with pytest.raises(TakerflowMaterializationError, match="limited"):
        materialize_canonical_kline_takerflow_features(
            canonical_kline_path=parent,
            timeframe="15m",
            output_path=tmp_path / "features.csv",
            manifest_path=tmp_path / "manifest.json",
            availability_catalog_path=AVAILABILITY,
        )
    for override, error in (({"sha256": "0" * 64}, "IDENTITY_BLOCKER"), ({"row_count": 4}, "row count")):
        with pytest.raises(TakerflowMaterializationError, match=error):
            _materialize_generic(tmp_path / error, "30m", config_override=override)


def test_generic_production_parent_config_is_exact() -> None:
    assert set(CANONICAL_KLINE_PARENT_CONFIG) == {"30m", "1h", "4h", "1d"}
    assert CANONICAL_KLINE_PARENT_CONFIG["30m"]["row_count"] == 110064
    assert CANONICAL_KLINE_PARENT_CONFIG["1h"]["sha256"] == "28b750e90ee9957e6fc22811c4ae632355a239f2b958ed65c9b3c56cb2d9e79e"
    assert CANONICAL_KLINE_PARENT_CONFIG["4h"]["data_slice_identity"].endswith("4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30")
    assert CANONICAL_KLINE_PARENT_CONFIG["1d"]["format"] == "parquet"


def test_generic_cli_mode_requires_closed_path_timeframe_pair(tmp_path: Path) -> None:
    parser = _build_parser()
    parsed = parser.parse_args(
        [
            "--canonical-kline-path", str(tmp_path / "parent.csv"),
            "--canonical-kline-timeframe", "30m",
            "--output-path", str(tmp_path / "features.csv"),
            "--manifest-path", str(tmp_path / "manifest.json"),
            "--availability-catalog-path", str(AVAILABILITY),
        ]
    )
    assert parsed.canonical_kline_timeframe == "30m"
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["--d4-path", str(tmp_path / "d4.csv"), "--canonical-kline-path", str(tmp_path / "parent.csv")]
        )


@pytest.mark.parametrize(
    "rows",
    [
        [("6", 1, "7"), ("4", 0, "4"), ("5", 2, "0")],
        [("-1", 1, "0"), ("4", 0, "4"), ("5", 2, "0")],
        [("6", -1, "4"), ("4", 0, "4"), ("5", 2, "0")],
    ],
)
def test_d4_native_invalid_parent_values_fail_closed(tmp_path: Path, rows) -> None:
    with pytest.raises(TakerflowMaterializationError, match="derivation bounds"):
        _materialize_d4(tmp_path, rows=rows)


def test_d4_native_parent_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    d4 = _write_d4_fixture(tmp_path)
    with pytest.raises(TakerflowMaterializationError, match="D4_PARENT_IDENTITY_BLOCKER"):
        materialize_d4_native_takerflow_features(
            d4_path=d4,
            output_path=tmp_path / "features.csv",
            manifest_path=tmp_path / "manifest.json",
            availability_catalog_path=AVAILABILITY,
            expected_sha256="0" * 64,
            expected_rows=3,
            coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
            coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
        )


def test_d4_native_identity_is_path_independent_and_parent_identity_bearing(tmp_path: Path):
    identity_a = "binance_usdtm_btcusdt_ohlcv_15m:sha256:" + "1" * 64
    identity_b = "binance_usdtm_btcusdt_ohlcv_15m:sha256:" + "2" * 64
    *_, first = _materialize_d4(tmp_path / "first", identity=identity_a)
    *_, relocated = _materialize_d4(tmp_path / "relocated", identity=identity_a)
    *_, changed_parent = _materialize_d4(tmp_path / "changed", identity=identity_b)
    first_contract = first["research_feature_table"]
    relocated_contract = relocated["research_feature_table"]
    changed_contract = changed_parent["research_feature_table"]
    assert first_contract["source_set_identity"] == relocated_contract["source_set_identity"]
    assert first_contract["feature_table_identity"] == relocated_contract["feature_table_identity"]
    assert first_contract["feature_table_identity"] != changed_contract["feature_table_identity"]


def test_d4_native_future_mutation_does_not_change_prior_rows(tmp_path: Path):
    _, first_output, _, _ = _materialize_d4(tmp_path / "first")
    _, second_output, _, _ = _materialize_d4(
        tmp_path / "second", rows=[("6", 3, "4"), ("4", 0, "4"), ("9", 2, "1")]
    )
    first = list(csv.DictReader(first_output.open(encoding="utf-8", newline="")))
    second = list(csv.DictReader(second_output.open(encoding="utf-8", newline="")))
    assert first[:2] == second[:2]
    assert first[2] != second[2]


@pytest.mark.skipif(
    os.getenv("CPW_RESEARCH02_RUN_FULL_HISTORY") != "1",
    reason="explicit physical acceptance only",
)
def test_full_history_d4_native_physical_proof(tmp_path: Path) -> None:
    d4 = REPO_ROOT / "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
    manifests = []
    for name in ("first", "second"):
        manifests.append(
            materialize_d4_native_takerflow_features(
                d4_path=d4,
                output_path=tmp_path / name / "features.csv",
                manifest_path=tmp_path / name / "manifest.json",
                availability_catalog_path=AVAILABILITY,
            )
        )
    first, second = manifests
    assert first["proof"] == {
        "parent_row_count": 220128,
        "feature_row_count": 220128,
        "missing_bar_count": 0,
        "duplicate_timestamp_count": 0,
        "invalid_buy_count": 0,
        "invalid_sell_count": 0,
        "zero_sell_count": 15,
        "null_ratio_count": 15,
        "three_column_projection_sha256": D4_PROJECTION_SHA256,
    }
    assert first["output"]["sha256"] == second["output"]["sha256"]
    assert first["output"]["sha256"] == (
        "c726d5a73a2d2168404c2a3599c477f9bea7ab5066d59c3f090a456b8efeffba"
    )
    assert first["research_feature_table"]["source_set_identity"] == (
        "sha256:a706affa0f3b3be362ffeb523d8dcd6805235127618760e13a16b7d6969f411e"
    )
    assert first["research_feature_table"]["feature_table_identity"] == (
        "sha256:0ab8af18c78d274d7ac4e3b11a9701d7e604e5c9a8e746b6000e1cca4f79403c"
    )
    assert (
        first["research_feature_table"]["feature_table_identity"]
        == second["research_feature_table"]["feature_table_identity"]
    )


@pytest.mark.skipif(
    os.getenv("CPW_RESEARCH02_RUN_FULL_HISTORY") != "1",
    reason="accepted May-2023 local diagnostic evidence required",
)
def test_may_2023_d4_native_matches_accepted_raw_proof() -> None:
    accepted = (
        Path(os.environ["TEMP"])
        / "cpw-research-02-raw-continuation/may-final3-cache/2023-05.csv"
    )
    d4 = REPO_ROOT / "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
    accepted_rows = list(csv.DictReader(accepted.open(encoding="utf-8", newline="")))
    d4_rows = {
        row["open_time"]: row
        for row in csv.DictReader(d4.open(encoding="utf-8", newline=""))
        if row["open_time"].startswith("2023-05-")
    }
    mismatches = {name: 0 for name in ("taker_buy_volume", "taker_sell_volume", "taker_buy_sell_ratio")}
    for row in accepted_rows:
        parent = d4_rows[row["timestamp"].replace(".000Z", "Z")]
        buy = Decimal(parent["taker_buy_base_vol"])
        sell = Decimal(parent["volume"]) - buy
        with localcontext() as context:
            context.prec = 38
            ratio = None if sell == 0 else buy / sell
        expected = {
            "taker_buy_volume": buy,
            "taker_sell_volume": sell,
            "taker_buy_sell_ratio": ratio,
        }
        for name, value in expected.items():
            observed = row[name]
            if (value is None and observed != "") or (
                value is not None and Decimal(observed) != value
            ):
                mismatches[name] += 1
    assert len(accepted_rows) == len(d4_rows) == 2976
    assert mismatches == {name: 0 for name in mismatches}


def test_may_2024_d4_native_authoritative_discrepancy_is_exact() -> None:
    d4 = REPO_ROOT / "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
    row = next(
        item
        for item in csv.DictReader(d4.open(encoding="utf-8", newline=""))
        if item["open_time"] == "2024-05-06T07:00:00Z"
    )
    buy = Decimal(row["taker_buy_base_vol"])
    sell = Decimal(row["volume"]) - buy
    assert (row["volume"], row["num_trades"], buy, sell) == (
        "1725.914",
        "29627",
        Decimal("822.33"),
        Decimal("903.584"),
    )
    assert (Decimal("1726.888") - Decimal(row["volume"])) == Decimal("0.974")
    assert (29673 - int(row["num_trades"])) == 46
    assert (Decimal("823.011") - buy) == Decimal("0.681")
    assert (Decimal("903.877") - sell) == Decimal("0.293")


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


def test_official_raw_trade_header_maps_exactly(tmp_path: Path):
    official = tmp_path / "official.csv"
    lines = TRADES.read_text(encoding="utf-8").splitlines()
    official.write_text(
        "id,price,qty,quoteQty,time,isBuyerMaker\n" + "\n".join(lines[1:]) + "\n",
        encoding="utf-8",
    )
    output, _, manifest = _materialize(tmp_path, [official])
    assert output.is_file()
    assert manifest["archive_type"] == "trades"


@pytest.mark.parametrize(
    "header",
    [
        "id,price,qty,time,isBuyerMaker",
        "id,price,qty,quoteQty,time,isBuyerMaker,unknown",
    ],
)
def test_official_raw_trade_missing_or_unknown_columns_fail_closed(
    tmp_path: Path, header: str
) -> None:
    path = tmp_path / "invalid.csv"
    path.write_text(header + "\n1,100,1,100,1704067200000,false\n", encoding="utf-8")
    with pytest.raises(TakerflowMaterializationError, match="columns do not match"):
        _materialize(tmp_path, [path])


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
    assert validate_manifest_payload(first) == []
    assert first["research_feature_table"] == second["research_feature_table"]
    assert first["research_feature_table"]["feature_names"] == [
        "taker_buy_volume",
        "taker_sell_volume",
        "taker_buy_sell_ratio",
    ]
    assert first["research_feature_table"]["output_identity"]["sha256"] == first["output"]["sha256"]


def test_generic_identities_ignore_local_paths_and_reject_tampering(tmp_path: Path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first_source = first_dir / "same.csv"
    second_source = second_dir / "same.csv"
    first_source.write_bytes(TRADES.read_bytes())
    second_source.write_bytes(TRADES.read_bytes())
    _, _, first = _materialize(first_dir, [first_source])
    _, _, second = _materialize(second_dir, [second_source])
    assert first["research_feature_table"]["source_set_identity"] == second["research_feature_table"]["source_set_identity"]
    assert first["research_feature_table"]["feature_table_identity"] == second["research_feature_table"]["feature_table_identity"]
    tampered = json.loads(json.dumps(first))
    tampered["research_feature_table"]["feature_table_identity"] = "sha256:" + "0" * 64
    assert any("feature_table_identity" in error for error in validate_manifest_payload(tampered))


def test_historical_aggtrades_hydration_manifest_equals_origin_main() -> None:
    expected = subprocess.run(
        ["git", "show", "origin/main:research/data_feature_availability/BINANCE-USDM-BTCUSDT-AGGTRADES-HYDRATION-0001.json"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert HYDRATION.read_bytes() == expected


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


def test_interleaved_complete_month_normalizes_deterministically(tmp_path: Path):
    rows = _month_rows()
    interleaved = [*rows[100:200], *rows[:100], *rows[200:]]
    fixture = _write_partition_fixture(tmp_path, monthly_rows=interleaved)

    first = _partitioned(fixture)
    first_bytes = Path(fixture["output"]).read_bytes()
    second = _partitioned(fixture)

    partition = json.loads((Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text())
    assert partition["source_mode"] == "monthly"
    assert partition["source_diagnostics"]["physical_row_order_monotonic"] is False
    assert partition["source_diagnostics"]["out_of_order_pair_count"] > 0
    assert partition["source_diagnostics"]["canonical_order_mode"] == "bounded_external_merge"
    assert partition["source_diagnostics"]["canonical_output_row_count"] == len(rows)
    assert partition["source_diagnostics"]["source_parsed_row_count"] == len(rows)
    assert partition["source_diagnostics"]["canonical_rows_added_removed_changed"] == 0
    assert partition["source_diagnostics"]["canonical_run_count"] > 1
    assert len(partition["source_diagnostics"]["canonical_record_sha256"]) == 64
    assert first_bytes == Path(fixture["output"]).read_bytes()
    assert first["research_feature_table"] == second["research_feature_table"]


def test_monotonic_month_uses_direct_single_pass_mode(tmp_path: Path):
    fixture = _write_partition_fixture(tmp_path)
    _partitioned(fixture)
    partition = json.loads(
        (Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text()
    )
    diagnostics = partition["source_diagnostics"]
    assert diagnostics["physical_row_order_monotonic"] is True
    assert diagnostics["canonical_order_mode"] == "direct_stream"
    assert diagnostics["canonical_run_count"] == 1
    assert diagnostics["canonical_output_row_count"] == diagnostics["source_parsed_row_count"]
    assert diagnostics["canonical_rows_added_removed_changed"] == 0


def test_missing_day_rejects_monthly_and_complete_daily_union_passes(tmp_path: Path):
    rows = _month_rows()
    missing_day_nine = [row for index, row in enumerate(rows) if not (8 * 96 <= index < 9 * 96)]
    fixture = _write_partition_fixture(
        tmp_path, monthly_rows=missing_day_nine, write_daily=True
    )

    manifest = _partitioned(fixture)
    partition = json.loads((Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text())

    assert partition["source_mode"] == "daily_union"
    assert len(partition["consumed_source_files"]) == 31
    assert partition["rejected_monthly_source"]["sha256"] not in {
        item["sha256"] for item in manifest["source_files"]
    }
    assert any(
        "2024-01-09" in reason
        for reason in partition["rejected_monthly_source"]["semantic_rejection_reasons"]
    )
    assert all(value == 0 for value in partition["d4_reconciliation"]["mismatch_counts"].values())


def test_missing_monthly_archive_uses_complete_daily_union(tmp_path: Path):
    fixture = _write_partition_fixture(tmp_path, write_daily=True)
    monthly = Path(fixture["monthly_root"]) / "BTCUSDT-trades-2024-01.zip"
    monthly.unlink()
    monthly.with_name(monthly.name + ".CHECKSUM").unlink()

    _partitioned(fixture)
    partition = json.loads(
        (Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text()
    )
    assert partition["source_mode"] == "daily_union"
    assert partition["rejected_monthly_source"]["checksum_verified"] is False
    assert len(partition["consumed_source_files"]) == 31
    assert _partitioned(fixture)["partition_summary"]["source_mode_counts"] == {
        "monthly": 0,
        "daily_union": 1,
    }


def test_daily_union_requires_every_file_and_checksum(tmp_path: Path):
    rows = _month_rows()
    fixture = _write_partition_fixture(tmp_path, monthly_rows=rows[96:], write_daily=True)
    missing = Path(fixture["daily_root"]) / "BTCUSDT-trades-2024-01-17.zip"
    missing.unlink()
    with pytest.raises(TakerflowMaterializationError, match="required source archive is missing"):
        _partitioned(fixture)

    fixture = _write_partition_fixture(tmp_path / "checksum", monthly_rows=rows[96:], write_daily=True)
    sidecar = Path(fixture["daily_root"]) / "BTCUSDT-trades-2024-01-17.zip.CHECKSUM"
    sidecar.write_text(f"{'0' * 64}  BTCUSDT-trades-2024-01-17.zip\n", encoding="utf-8")
    with pytest.raises(TakerflowMaterializationError, match="checksum verification failed"):
        _partitioned(fixture)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("duplicate", "daily_union rejected"),
        ("conflicting_duplicate", "daily_union rejected"),
        ("backwards_overlap", "daily_union rejected"),
        ("zero_quantity", "qty must be finite and positive"),
        ("negative_price", "price must be finite and positive"),
        ("out_of_month", "daily_union rejected"),
        ("timestamp_inconsistency", "daily_union rejected"),
    ],
)
def test_strict_source_semantic_gates_fail_closed(
    tmp_path: Path, mutation: str, expected: str
):
    rows = _month_rows()
    fixture = _write_partition_fixture(tmp_path, monthly_rows=rows[96:], write_daily=True)
    daily_root = Path(fixture["daily_root"])
    day = 12
    day_rows = [list(row) for row in rows[(day - 1) * 96 : day * 96]]
    if mutation == "duplicate":
        day_rows.insert(20, list(day_rows[19]))
    elif mutation == "conflicting_duplicate":
        duplicate = list(day_rows[19])
        duplicate[2] = "2"
        day_rows.insert(20, duplicate)
    elif mutation == "backwards_overlap":
        day_rows[20][0] = day_rows[19][0]
    elif mutation == "zero_quantity":
        day_rows[20][2] = "0"
    elif mutation == "negative_price":
        day_rows[20][1] = "-1"
    elif mutation == "out_of_month":
        day_rows[20][4] = str(int(datetime(2024, 2, 1, tzinfo=UTC).timestamp() * 1000))
    elif mutation == "timestamp_inconsistency":
        day_rows[20][4], day_rows[21][4] = day_rows[21][4], day_rows[20][4]
    _write_zip(daily_root / f"BTCUSDT-trades-2024-01-{day:02d}.zip", day_rows)

    with pytest.raises(TakerflowMaterializationError, match=expected):
        _partitioned(fixture)


def test_daily_union_duplicate_across_files_blocks(tmp_path: Path):
    rows = _month_rows()
    fixture = _write_partition_fixture(tmp_path, monthly_rows=rows[96:], write_daily=True)
    daily_root = Path(fixture["daily_root"])
    day_one = [list(row) for row in rows[:96]]
    day_one.append(list(rows[96]))
    _write_zip(daily_root / "BTCUSDT-trades-2024-01-01.zip", day_one)
    with pytest.raises(TakerflowMaterializationError, match="daily_union rejected"):
        _partitioned(fixture)


def test_raw_trade_id_gap_is_diagnostic_and_not_added_to_trade_count(tmp_path: Path):
    rows = _month_rows()
    fixture = _write_partition_fixture(tmp_path)
    monthly = Path(fixture["monthly_root"]) / "BTCUSDT-trades-2024-01.zip"
    adjusted = [list(row) for row in rows]
    for row in adjusted[20:]:
        row[0] = str(int(row[0]) + 3)
    _write_zip(monthly, adjusted)

    manifest = _partitioned(fixture)
    partition = json.loads(
        (Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text()
    )
    diagnostics = partition["source_diagnostics"]
    assert diagnostics["trade_id_gap_range_count"] == 1
    assert diagnostics["absent_trade_id_count"] == 3
    assert diagnostics["trade_id_gap_ranges"] == [
        {"first": int(rows[19][0]) + 1, "last": int(adjusted[20][0]) - 1}
    ]
    assert diagnostics["trade_id_gap_ranges_sha256"].startswith("sha256:")
    with Path(fixture["output"]).open(encoding="utf-8", newline="") as handle:
        output_rows = list(csv.DictReader(handle))
    assert sum(int(row["trade_count"]) for row in output_rows) == len(rows)
    assert manifest["source_accounting"]["absent_trade_id_count"] == 3


def test_non_raw_partition_cache_is_not_reused(tmp_path: Path):
    fixture = _write_partition_fixture(tmp_path)
    first = _partitioned(fixture)
    partition_manifest = Path(fixture["cache_root"]) / "2024-01.manifest.json"
    stale = json.loads(partition_manifest.read_text())
    stale["source_policy_version"] = "cpw_binance_aggtrades_partition_source_policy_v3"
    stale["output"]["sha256"] = "0" * 64
    partition_manifest.write_text(json.dumps(stale), encoding="utf-8")

    rebuilt = _partitioned(fixture)
    restored = json.loads(partition_manifest.read_text())
    assert restored["source_policy_version"] == SOURCE_POLICY_VERSION
    assert restored["output"]["sha256"] == first["output"]["sha256"]
    assert rebuilt["research_feature_table"] == first["research_feature_table"]


@pytest.mark.parametrize(
    ("field", "expected_mismatch"),
    [
        ("volume", "volume=1"),
        ("num_trades", "trade_count=1"),
        ("taker_buy_base_vol", "taker_buy=1"),
        ("taker_buy_base_vol", "taker_sell=1"),
    ],
)
def test_d4_exact_reconciliation_mismatches_block(
    tmp_path: Path, field: str, expected_mismatch: str
):
    fixture = _write_partition_fixture(tmp_path, write_daily=True)
    d4 = Path(fixture["d4"])
    rows = list(csv.DictReader(d4.open(encoding="utf-8", newline="")))
    rows[10][field] = "2"
    with d4.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    fixture["d4_sha"] = hashlib.sha256(d4.read_bytes()).hexdigest()
    with pytest.raises(
        TakerflowMaterializationError,
        match=f"D4_RECONCILIATION_BLOCKER.*{expected_mismatch}",
    ):
        _partitioned(fixture)


def test_cache_resume_tamper_invalidation_and_path_independence(tmp_path: Path):
    fixture = _write_partition_fixture(tmp_path / "first")
    with pytest.raises(TakerflowMaterializationError, match="intentional interruption"):
        _partitioned(fixture, stop_after_partitions=1)
    cold_manifest = json.loads(
        (Path(fixture["cache_root"]) / "2024-01.manifest.json").read_text()
    )
    completed = _partitioned(fixture)
    expected_bytes = Path(fixture["output"]).read_bytes()

    cached_csv = Path(fixture["cache_root"]) / "2024-01.csv"
    cached_csv.write_bytes(cached_csv.read_bytes() + b"tamper")
    rebuilt = _partitioned(fixture)
    assert cached_csv.read_bytes() == expected_bytes
    assert rebuilt["research_feature_table"] == completed["research_feature_table"]

    cached_manifest = Path(fixture["cache_root"]) / "2024-01.manifest.json"
    tampered = json.loads(cached_manifest.read_text())
    tampered["partition_identity"] = "sha256:" + "0" * 64
    cached_manifest.write_text(json.dumps(tampered), encoding="utf-8")
    restored = _partitioned(fixture)
    assert restored["research_feature_table"] == completed["research_feature_table"]

    relocated = _write_partition_fixture(tmp_path / "relocated")
    shutil.copy2(
        Path(fixture["monthly_root"]) / "BTCUSDT-trades-2024-01.zip",
        Path(relocated["monthly_root"]) / "BTCUSDT-trades-2024-01.zip",
    )
    shutil.copy2(
        Path(fixture["monthly_root"]) / "BTCUSDT-trades-2024-01.zip.CHECKSUM",
        Path(relocated["monthly_root"]) / "BTCUSDT-trades-2024-01.zip.CHECKSUM",
    )
    relocated_manifest = _partitioned(relocated)
    assert relocated_manifest["research_feature_table"]["source_set_identity"] == completed["research_feature_table"]["source_set_identity"]
    assert relocated_manifest["research_feature_table"]["feature_table_identity"] == completed["research_feature_table"]["feature_table_identity"]
    assert cold_manifest["partition_identity"] == json.loads(cached_manifest.read_text())["partition_identity"]


def test_rejected_monthly_bytes_are_not_consumed_identity(tmp_path: Path):
    rows = _month_rows()
    missing = rows[96:]
    fixture = _write_partition_fixture(tmp_path, monthly_rows=missing, write_daily=True)
    first = _partitioned(fixture)
    monthly = Path(fixture["monthly_root"]) / "BTCUSDT-trades-2024-01.zip"
    _write_zip(monthly, [*missing[100:], *missing[:100]])
    second = _partitioned(fixture)

    assert first["research_feature_table"]["source_set_identity"] == second["research_feature_table"]["source_set_identity"]
    assert first["research_feature_table"]["feature_table_identity"] == second["research_feature_table"]["feature_table_identity"]
    assert first["rejected_monthly_sources"][0]["sha256"] != second["rejected_monthly_sources"][0]["sha256"]


def test_locked_partition_policy_versions_are_exact():
    assert SOURCE_POLICY_VERSION == "cpw_binance_raw_trades_partition_source_policy_v1"
    assert CANONICAL_ORDER_VERSION == "cpw_binance_raw_trades_canonical_order_v1"
    assert PARTITION_CACHE_VERSION == "cpw_takerflow_partition_cache_v1"
