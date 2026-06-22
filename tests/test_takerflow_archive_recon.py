from __future__ import annotations

import json
import zipfile
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from tools.data_ingestion.takerflow_archive_recon import (
    COVERAGE_CLASS,
    TakerflowArchiveError,
    aggregate_takerflow_to_bars,
    build_lineage,
    derive_taker_side,
    parse_binance_um_aggtrade_archive,
    parse_binance_um_trade_archive,
    reconstruct_archive,
    validate_takerflow_slice,
)


FIXTURES = Path(__file__).parent / "fixtures" / "takerflow_archive_recon"
TRADES = FIXTURES / "trades_hand_calc.csv"
AGGTRADES = FIXTURES / "aggtrades_hand_calc.csv"
GENERATION_TIME = "2026-06-21T18:00:00Z"


def test_buyer_maker_semantics_map_to_taker_side():
    rows = parse_binance_um_trade_archive(TRADES)

    assert derive_taker_side(rows[0]) == "sell"
    assert derive_taker_side(rows[1]) == "buy"


def test_trade_fixture_matches_hand_calculation_and_boundaries():
    bars = aggregate_takerflow_to_bars(parse_binance_um_trade_archive(TRADES), "15m")

    assert bars == [
        {
            "open_time_ms": 1704067200000,
            "open_time": "2024-01-01T00:00:00.000Z",
            "taker_buy_base_volume": "4",
            "taker_sell_base_volume": "2",
            "taker_net_base_volume": "2",
            "taker_total_base_volume": "6",
            "taker_buy_sell_ratio": "2",
            "trade_count": 3,
            "taker_buy_quote_volume": "407",
            "taker_sell_quote_volume": "200",
            "taker_net_quote_volume": "207",
            "taker_total_quote_volume": "607",
        },
        {
            "open_time_ms": 1704068100000,
            "open_time": "2024-01-01T00:15:00.000Z",
            "taker_buy_base_volume": "4",
            "taker_sell_base_volume": "0",
            "taker_net_base_volume": "4",
            "taker_total_base_volume": "4",
            "taker_buy_sell_ratio": None,
            "trade_count": 1,
            "taker_buy_quote_volume": "412",
            "taker_sell_quote_volume": "0",
            "taker_net_quote_volume": "412",
            "taker_total_quote_volume": "412",
        },
        {
            "open_time_ms": 1704069000000,
            "open_time": "2024-01-01T00:30:00.000Z",
            "taker_buy_base_volume": "0",
            "taker_sell_base_volume": "5",
            "taker_net_base_volume": "-5",
            "taker_total_base_volume": "5",
            "taker_buy_sell_ratio": "0",
            "trade_count": 1,
            "taker_buy_quote_volume": "0",
            "taker_sell_quote_volume": "520",
            "taker_net_quote_volume": "-520",
            "taker_total_quote_volume": "520",
        },
    ]


def test_future_rows_do_not_change_prior_bars():
    rows = parse_binance_um_trade_archive(TRADES)
    prior = aggregate_takerflow_to_bars(rows[:3], "15m")
    complete = aggregate_takerflow_to_bars(rows, "15m")

    assert complete[0] == prior[0]


def test_aggtrade_fixture_counts_underlying_trades_and_omits_quote_features():
    rows = parse_binance_um_aggtrade_archive(AGGTRADES)
    bars = aggregate_takerflow_to_bars(rows, "15m")

    assert bars[0]["taker_buy_base_volume"] == "1"
    assert bars[0]["taker_sell_base_volume"] == "2"
    assert bars[0]["trade_count"] == 4
    assert "taker_buy_quote_volume" not in bars[0]
    assert bars[1]["trade_count"] == 2


def test_local_zip_archive_is_supported(tmp_path: Path):
    archive = tmp_path / "trades.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.write(TRADES, "BTCUSDT-trades-2024-01-01.csv")

    assert parse_binance_um_trade_archive(archive) == parse_binance_um_trade_archive(TRADES)


def test_lineage_is_written_and_validated(tmp_path: Path):
    output = tmp_path / "slice.json"
    reconstruct_archive(
        TRADES,
        "trades",
        output,
        "BTCUSDT",
        "15m",
        generation_time=GENERATION_TIME,
    )
    payload = validate_takerflow_slice(output)
    lineage = payload["lineage"]

    assert lineage["source_archive_path"] == str(TRADES.resolve())
    assert lineage["source_archive_type"] == "trades"
    assert lineage["coverage_class"] == COVERAGE_CLASS
    assert lineage["source_public"] is True
    assert lineage["private_endpoint_used"] is False
    assert lineage["network_used"] is False
    assert lineage["archive_file_hash"].startswith("sha256:")
    assert lineage["row_count"] == 3
    assert lineage["source_row_count"] == 5


def test_fixed_generation_time_produces_identical_slice_bytes(tmp_path: Path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for output in (first, second):
        reconstruct_archive(
            TRADES,
            "trades",
            output,
            "BTCUSDT",
            "15m",
            generation_time=GENERATION_TIME,
        )

    assert first.read_bytes() == second.read_bytes()


def test_recent_only_rest_is_rejected_as_historical_source():
    rows = parse_binance_um_trade_archive(TRADES)
    bars = aggregate_takerflow_to_bars(rows, "15m")

    with pytest.raises(TakerflowArchiveError, match="recent-only REST"):
        build_lineage(
            TRADES,
            "trades",
            "BTCUSDT",
            "15m",
            rows,
            bars,
            coverage_class="RECENT_ONLY_REST",
        )


@pytest.mark.parametrize(
    "contents",
    [
        "trade_id,price,qty,quote_qty,time\n1,100,1,100,1704067200000\n",
        "trade_id,price,qty,quote_qty,time,is_buyer_maker\n1,100,1,100,1704067200000,unknown\n",
        "trade_id,price,qty,quote_qty,time,is_buyer_maker\n1,100,-1,-100,1704067200000,false\n",
    ],
)
def test_invalid_or_missing_rows_fail_closed(tmp_path: Path, contents: str):
    archive = tmp_path / "invalid.csv"
    archive.write_text(contents, encoding="utf-8")

    with pytest.raises(TakerflowArchiveError):
        parse_binance_um_trade_archive(archive)


def test_headerless_official_archive_layout_is_supported(tmp_path: Path):
    source_lines = TRADES.read_text(encoding="utf-8").splitlines()
    archive = tmp_path / "headerless.csv"
    archive.write_text("\n".join(source_lines[1:]) + "\n", encoding="utf-8")

    assert parse_binance_um_trade_archive(archive) == parse_binance_um_trade_archive(TRADES)


def test_non_utc_or_invalid_interval_fails_closed():
    rows = parse_binance_um_trade_archive(TRADES)

    with pytest.raises(TakerflowArchiveError, match="only UTC"):
        aggregate_takerflow_to_bars(rows, "15m", timezone="America/New_York")
    with pytest.raises(TakerflowArchiveError, match="interval"):
        aggregate_takerflow_to_bars(rows, "calendar-month")


def test_slice_validator_rejects_invalid_arithmetic(tmp_path: Path):
    output = tmp_path / "slice.json"
    reconstruct_archive(
        TRADES,
        "trades",
        output,
        "BTCUSDT",
        "15m",
        generation_time=GENERATION_TIME,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    payload["data"][0]["taker_total_base_volume"] = "999"
    output.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(TakerflowArchiveError, match="arithmetic"):
        validate_takerflow_slice(output)


def test_derive_taker_side_rejects_non_boolean():
    row = parse_binance_um_trade_archive(TRADES)[0]

    with pytest.raises(TakerflowArchiveError, match="boolean"):
        derive_taker_side(replace(row, buyer_maker="false"))  # type: ignore[arg-type]


def test_decimal_aggregation_remains_exact():
    rows = parse_binance_um_trade_archive(TRADES)
    adjusted = [
        replace(rows[1], base_quantity=Decimal("0.1")),
        replace(rows[2], base_quantity=Decimal("0.2")),
    ]

    assert aggregate_takerflow_to_bars(adjusted, "15m")[0]["taker_buy_base_volume"] == "0.3"
