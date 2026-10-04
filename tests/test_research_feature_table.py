from __future__ import annotations

import json
import os
import csv
import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from tools.data.materialize_takerflow_features import (
    materialize_canonical_kline_takerflow_features,
    materialize_d4_native_takerflow_features,
)
from tools.data.research_feature_table import (
    ResearchFeatureTableError,
    resolve_research_feature_table,
)
from tools.registry.validate_research_feature_table_manifest import (
    validate_research_feature_table_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AVAILABILITY = REPO_ROOT / "research" / "data_feature_availability" / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
MARKET = {"venue": "Binance", "market_type": "USD-M perpetual", "symbol": "BTCUSDT"}
PARENT_IDENTITY = "binance_usdtm_btcusdt_ohlcv_15m:sha256:" + "1" * 64


def _fixture(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    d4_path = tmp_path / "d4.csv"
    with d4_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["open_time_ms", "open_time", "volume", "close_time_ms", "num_trades", "taker_buy_base_vol"])
        for index, (volume, trades, buy) in enumerate((("6", 3, "4"), ("4", 0, "4"), ("5", 2, "0"))):
            open_ms = 1704067200000 + index * 900000
            writer.writerow([
                open_ms,
                datetime.fromtimestamp(open_ms / 1000, tz=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                volume,
                open_ms + 899999,
                trades,
                buy,
            ])
    d4_sha = hashlib.sha256(d4_path.read_bytes()).hexdigest()
    feature_csv = tmp_path / "features.csv"
    manifest_path = tmp_path / "manifest.json"
    manifest = materialize_d4_native_takerflow_features(
        d4_path=d4_path,
        output_path=feature_csv, manifest_path=manifest_path,
        availability_catalog_path=AVAILABILITY,
        data_slice_identity=PARENT_IDENTITY,
        expected_sha256=d4_sha,
        expected_rows=3,
        coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
        coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
    )
    feature = pd.read_csv(feature_csv)
    base = pd.DataFrame(
        {"timestamp": feature["timestamp"], "open": [100, 101, 102], "high": [101, 102, 103], "low": [99, 100, 101], "close": [100, 101, 102], "volume": [6, 4, 5]}
    )
    base_frame = base.assign(timestamp=pd.to_datetime(base["timestamp"], utc=True)).set_index("timestamp")
    base_frame = base_frame[["open", "high", "low", "close", "volume"]].astype(float)
    return base_frame, d4_path, d4_sha, feature_csv, manifest_path, manifest


def _resolve(tmp_path: Path, **overrides):
    base, base_path, base_sha, feature_csv, manifest_path, manifest = _fixture(tmp_path)
    kwargs = dict(
        base_frame=base, base_input_path=base_path,
        base_data_slice_identity=PARENT_IDENTITY,
        base_normalized_sha256=base_sha, base_market_identity=MARKET,
        base_timeframe="15m", base_coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
        base_coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
        feature_manifest_path=manifest_path, feature_csv_path=feature_csv,
        requested_feature_names=["taker_buy_volume", "taker_sell_volume"],
    )
    kwargs.update(overrides)
    return resolve_research_feature_table(**kwargs), (base, base_path, base_sha, feature_csv, manifest_path, manifest)


def _generic_fixture(tmp_path: Path, timeframe: str):
    tmp_path.mkdir(parents=True, exist_ok=True)
    delta = pd.to_timedelta(timeframe)
    index = pd.date_range("2024-01-01", periods=3, freq=delta, tz="UTC")
    parent = pd.DataFrame(
        {
            "open_time_ms": index.as_unit("ms").asi8,
            "volume": [6.0, 4.0, 5.0],
            "close_time_ms": (index + delta).as_unit("ms").asi8 - 1,
            "num_trades": [3, 0, 2],
            "taker_buy_base_vol": [4.0, 4.0, 0.0],
        }
    )
    parent_path = tmp_path / ("parent.parquet" if timeframe == "1d" else "parent.csv")
    if timeframe == "1d":
        parent.to_parquet(parent_path, index=False)
        parent_format = "parquet"
    else:
        parent.insert(1, "open_time", index.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        parent.to_csv(parent_path, index=False, lineterminator="\n")
        parent_format = "csv"
    parent_sha = hashlib.sha256(parent_path.read_bytes()).hexdigest()
    hash_label = "identity_sha256" if timeframe == "1d" else "sha256"
    parent_identity = f"binance_usdtm_btcusdt_ohlcv_{timeframe}:{hash_label}:" + "2" * 64
    end = index[-1] + delta
    manifest_path = tmp_path / "manifest.json"
    feature_csv = tmp_path / "features.csv"
    materialize_canonical_kline_takerflow_features(
        canonical_kline_path=parent_path,
        timeframe=timeframe,
        output_path=feature_csv,
        manifest_path=manifest_path,
        availability_catalog_path=AVAILABILITY,
        _parent_config={
            "sha256": parent_sha,
            "row_count": 3,
            "coverage_start": "2024-01-01T00:00:00.000Z",
            "coverage_end": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "data_slice_identity": parent_identity,
            "format": parent_format,
        },
    )
    base = pd.DataFrame(
        {"open": [100, 101, 102], "high": [101, 102, 103], "low": [99, 100, 101], "close": [100, 101, 102], "volume": [6, 4, 5]},
        index=index,
    ).astype(float)
    return {
        "base_frame": base,
        "base_input_path": parent_path,
        "base_data_slice_identity": parent_identity,
        "base_normalized_sha256": parent_sha,
        "base_market_identity": MARKET,
        "base_timeframe": timeframe,
        "base_coverage_start_utc_inclusive": "2024-01-01T00:00:00.000Z",
        "base_coverage_end_utc_exclusive": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "feature_manifest_path": manifest_path,
        "feature_csv_path": feature_csv,
        "requested_feature_names": ["taker_buy_sell_ratio", "taker_buy_volume", "taker_sell_volume"],
    }


def test_exact_join_is_causal_selective_and_identity_bearing(tmp_path: Path) -> None:
    resolved, (_, _, _, _, manifest_path, _) = _resolve(tmp_path)
    assert list(resolved.joined_frame.columns) == ["open", "high", "low", "close", "volume", "taker_buy_volume", "taker_sell_volume"]
    assert "taker_total_volume" not in resolved.joined_frame
    assert resolved.composite_data_slice_identity.startswith("cpw_research_composite_15m:sha256:")
    assert validate_research_feature_table_manifest(manifest_path) == []
    repeated, _ = _resolve(tmp_path / "repeat")
    assert repeated.composite_data_slice_identity == resolved.composite_data_slice_identity


@pytest.mark.parametrize("timeframe", ["30m", "1h", "4h", "1d"])
def test_generic_canonical_feature_table_exact_join_and_identity_prefix(
    tmp_path: Path, timeframe: str
) -> None:
    resolved = resolve_research_feature_table(**_generic_fixture(tmp_path, timeframe))
    assert len(resolved.joined_frame) == 3
    assert resolved.source_class == "CANONICAL_KLINE_TAKERFLOW_DERIVATION"
    assert resolved.composite_data_slice_identity.startswith(
        f"cpw_research_composite_{timeframe}:sha256:"
    )
    assert resolved.joined_frame["taker_buy_sell_ratio"].isna().tolist() == [False, True, False]


def test_generic_parent_timeframe_and_hash_mismatch_fail_closed(tmp_path: Path) -> None:
    kwargs = _generic_fixture(tmp_path, "30m")
    with pytest.raises(ResearchFeatureTableError, match="source class"):
        resolve_research_feature_table(**{**kwargs, "base_timeframe": "15m"})
    with pytest.raises(ResearchFeatureTableError, match="SHA-256"):
        resolve_research_feature_table(**{**kwargs, "base_normalized_sha256": "0" * 64})


def test_ratio_null_is_allowed_only_when_sell_is_zero(tmp_path: Path) -> None:
    resolved, fixture = _resolve(
        tmp_path, requested_feature_names=["taker_buy_sell_ratio"]
    )
    assert resolved.joined_frame["taker_buy_sell_ratio"].isna().tolist() == [
        False,
        True,
        False,
    ]
    _, _, _, feature_csv, manifest_path, _ = fixture
    rows = list(csv.DictReader(feature_csv.open(encoding="utf-8", newline="")))
    rows[0]["taker_buy_sell_ratio"] = ""
    with feature_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(feature_csv.read_bytes()).hexdigest()
    manifest["output"]["sha256"] = digest
    manifest["research_feature_table"]["output_identity"]["sha256"] = digest
    from tools.research_domain.feature_data import build_feature_table_identity
    manifest["research_feature_table"]["feature_table_identity"] = build_feature_table_identity(
        manifest["research_feature_table"]
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    base, base_path, base_sha, _, _, _ = fixture
    with pytest.raises(ResearchFeatureTableError, match="ratio formula"):
        resolve_research_feature_table(
            base_frame=base,
            base_input_path=base_path,
            base_data_slice_identity=PARENT_IDENTITY,
            base_normalized_sha256=base_sha,
            base_market_identity=MARKET,
            base_timeframe="15m",
            base_coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z",
            base_coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
            feature_manifest_path=manifest_path,
            feature_csv_path=feature_csv,
            requested_feature_names=["taker_buy_sell_ratio"],
        )


def test_parent_identity_mismatch_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ResearchFeatureTableError, match="parent identity"):
        _resolve(tmp_path, base_data_slice_identity="wrong")


def test_feature_bytes_and_causal_alignment_fail_closed(tmp_path: Path) -> None:
    _, (_, _, _, feature_csv, manifest_path, _) = _resolve(tmp_path)
    feature_csv.write_bytes(feature_csv.read_bytes() + b"\n")
    with pytest.raises(ResearchFeatureTableError, match="SHA-256"):
        resolve_research_feature_table(
            base_frame=pd.DataFrame(), base_input_path=feature_csv, base_data_slice_identity="x",
            base_normalized_sha256="0" * 64, base_market_identity=MARKET, base_timeframe="15m",
            base_coverage_start_utc_inclusive="x", base_coverage_end_utc_exclusive="y",
            feature_manifest_path=manifest_path, feature_csv_path=feature_csv,
            requested_feature_names=["taker_buy_volume"],
        )


def test_missing_requested_feature_and_timestamp_mismatch_fail_closed(tmp_path: Path) -> None:
    _, (base, base_path, base_sha, feature_csv, manifest_path, _) = _resolve(tmp_path)
    with pytest.raises(ResearchFeatureTableError, match="not advertised"):
        resolve_research_feature_table(
            base_frame=base, base_input_path=base_path, base_data_slice_identity=PARENT_IDENTITY,
            base_normalized_sha256=base_sha, base_market_identity=MARKET, base_timeframe="15m",
            base_coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z", base_coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
            feature_manifest_path=manifest_path, feature_csv_path=feature_csv,
            requested_feature_names=["trade_count"],
        )
    shifted = base.copy()
    shifted.index = shifted.index + pd.Timedelta(minutes=15)
    with pytest.raises(ResearchFeatureTableError, match="timestamp"):
        resolve_research_feature_table(
            base_frame=shifted, base_input_path=base_path, base_data_slice_identity=PARENT_IDENTITY,
            base_normalized_sha256=base_sha, base_market_identity=MARKET, base_timeframe="15m",
            base_coverage_start_utc_inclusive="2024-01-01T00:00:00.000Z", base_coverage_end_utc_exclusive="2024-01-01T00:45:00.000Z",
            feature_manifest_path=manifest_path, feature_csv_path=feature_csv,
            requested_feature_names=["taker_buy_volume"],
        )


@pytest.mark.skipif(os.getenv("CPW_RESEARCH02_RUN_FULL_HISTORY") != "1", reason="explicit physical acceptance only")
def test_full_history_exact_feature_table_join() -> None:
    d4_path = Path(os.environ["CPW_RESEARCH02_D4_CSV"])
    feature_path = Path(os.environ["CPW_RESEARCH02_FEATURE_CSV"])
    manifest_path = Path(os.environ["CPW_RESEARCH02_FEATURE_MANIFEST"])
    import hashlib
    base = pd.read_csv(d4_path)
    timestamp_column = "open_time" if "open_time" in base else "timestamp"
    base[timestamp_column] = pd.to_datetime(base[timestamp_column], utc=True)
    base_frame = base.set_index(timestamp_column)[["open", "high", "low", "close", "volume"]].astype(float)
    resolved = resolve_research_feature_table(
        base_frame=base_frame, base_input_path=d4_path,
        base_data_slice_identity="binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664",
        base_normalized_sha256=hashlib.sha256(d4_path.read_bytes()).hexdigest(),
        base_market_identity=MARKET, base_timeframe="15m",
        base_coverage_start_utc_inclusive="2020-01-01T00:00:00.000Z",
        base_coverage_end_utc_exclusive="2026-04-12T00:00:00.000Z",
        feature_manifest_path=manifest_path, feature_csv_path=feature_path,
        requested_feature_names=["taker_buy_sell_ratio", "taker_buy_volume", "taker_sell_volume"],
    )
    assert len(base_frame) == len(resolved.joined_frame) == 220128
    assert resolved.joined_frame.index.equals(base_frame.index)
