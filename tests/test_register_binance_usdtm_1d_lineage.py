from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest
from jsonschema import Draft7Validator

from tools.data.register_binance_usdtm_1d_lineage import (
    DEFAULT_LOGICAL_PATH,
    LineageError,
    build_lineage,
    canonical_json_bytes,
    write_lineage,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _validate_gate_q_dataset(gate_q_schema: dict[str, object], dataset: dict[str, object]) -> None:
    dataset_validator_schema = {
        "$schema": gate_q_schema["$schema"],
        "$ref": "#/definitions/dataset",
        "definitions": gate_q_schema["definitions"],
    }
    Draft7Validator(dataset_validator_schema).validate(dataset)


def _frame() -> pd.DataFrame:
    base = 1_704_067_200_000
    rows: list[dict[str, object]] = []
    for index in range(4):
        open_time_ms = base + index * 86_400_000
        open_price = 100.0 + index
        close = open_price + 1.0
        rows.append(
            {
                "open_time_ms": open_time_ms,
                "open": open_price,
                "high": close + 2.0,
                "low": open_price - 2.0,
                "close": close,
                "volume": 10.0 + index,
                "close_time_ms": open_time_ms + 86_400_000 - 1,
                "quote_asset_volume": 1000.0 + index,
                "num_trades": 20 + index,
                "taker_buy_base_vol": 5.0 + index,
                "taker_buy_quote_vol": 500.0 + index,
                "ignore": "0",
            }
        )
    return pd.DataFrame(rows)


def _write_parquet(path: Path, frame: pd.DataFrame | None = None) -> tuple[Path, str]:
    (frame if frame is not None else _frame()).to_parquet(path, index=False)
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha256


def _build(path: Path, sha256: str, *, cutoff: str = "2024-01-05T00:00:00Z"):
    return build_lineage(
        path,
        logical_path=DEFAULT_LOGICAL_PATH,
        expected_sha256=sha256,
        snapshot_cutoff_utc=cutoff,
    )


def test_valid_snapshot_lineage_is_byte_deterministic_and_gate_q_compatible(tmp_path: Path):
    source, sha256 = _write_parquet(tmp_path / "source.parquet")
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = write_lineage(
        source,
        first_path,
        expected_sha256=sha256,
        snapshot_cutoff_utc="2024-01-05T00:00:00Z",
    )
    second = write_lineage(
        source,
        second_path,
        expected_sha256=sha256,
        snapshot_cutoff_utc="2024-01-05T00:00:00Z",
    )
    lineage = json.loads(first_path.read_text(encoding="utf-8"))
    gate_q_schema = json.loads(
        (REPO_ROOT / "research/schemas/gate_q_approval.schema.json").read_text(encoding="utf-8")
    )

    assert first.ok is True
    assert second.ok is True
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes() == canonical_json_bytes(lineage)
    assert lineage["coverage"]["row_count"] == 4
    assert lineage["findings"]["gap_count"] == 0
    assert lineage["findings"]["duplicate_row_count"] == 0
    assert lineage["findings"]["open_or_incomplete_bar_count"] == 0
    assert lineage["boundary"]["credentials_used"] is False
    assert lineage["boundary"]["network_access_used_by_this_package"] is False
    _validate_gate_q_dataset(gate_q_schema, lineage["gate_q_dataset"])


def test_duplicate_daily_bar_is_rejected_without_deduplication(tmp_path: Path):
    frame = _frame()
    frame.loc[2, "open_time_ms"] = frame.loc[1, "open_time_ms"]
    frame.loc[2, "close_time_ms"] = frame.loc[1, "close_time_ms"]
    source, sha256 = _write_parquet(tmp_path / "duplicate.parquet", frame)

    with pytest.raises(LineageError, match="duplicate daily open_time"):
        _build(source, sha256)


def test_missing_daily_bar_is_rejected_without_interpolation(tmp_path: Path):
    frame = _frame().drop(index=2).reset_index(drop=True)
    source, sha256 = _write_parquet(tmp_path / "gap.parquet", frame)

    with pytest.raises(LineageError, match="daily cadence gap"):
        _build(source, sha256)


def test_open_daily_bar_is_rejected(tmp_path: Path):
    source, sha256 = _write_parquet(tmp_path / "open-bar.parquet")

    with pytest.raises(LineageError, match="bars not completed"):
        _build(source, sha256, cutoff="2024-01-04T12:00:00Z")


def test_whole_file_checksum_mismatch_is_rejected(tmp_path: Path):
    source, _ = _write_parquet(tmp_path / "checksum.parquet")

    with pytest.raises(LineageError, match="whole-file checksum mismatch"):
        _build(source, "0" * 64)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("high", 99.0, "malformed OHLC"),
        ("low", 105.0, "malformed OHLC"),
        ("volume", -1.0, "negative volume"),
    ],
)
def test_malformed_ohlc_or_negative_volume_is_rejected(
    tmp_path: Path, column: str, value: float, message: str
):
    frame = _frame()
    frame.loc[1, column] = value
    source, sha256 = _write_parquet(tmp_path / f"bad-{column}.parquet", frame)

    with pytest.raises(LineageError, match=message):
        _build(source, sha256)


def test_committed_lineage_has_required_h004_and_gate_q_identity():
    path = (
        REPO_ROOT
        / "research/data_slices/binance_usdtm_btcusdt_1d/"
        "binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json"
    )
    lineage = json.loads(path.read_text(encoding="utf-8"))
    gate_q_schema = json.loads(
        (REPO_ROOT / "research/schemas/gate_q_approval.schema.json").read_text(encoding="utf-8")
    )

    assert lineage["dataset_id"] == "binance_usdtm_btcusdt_ohlcv_1d"
    assert lineage["snapshot_version"] == "2026-04-12T1655Z"
    assert lineage["market"] == "BTCUSDT_BINANCE_USDTM_PERPETUAL"
    assert lineage["timeframe"] == "1d"
    assert lineage["unresolved_policy"] == "reject"
    assert lineage["coverage"]["row_count"] == 2293
    assert lineage["sha256"] == (
        "sha256:c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802"
    )
    _validate_gate_q_dataset(gate_q_schema, lineage["gate_q_dataset"])
