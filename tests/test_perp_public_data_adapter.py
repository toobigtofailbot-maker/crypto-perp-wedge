import json
import shutil

import pytest

from tools.data_ingestion import perp_public_data_adapter as adapter


def test_adapter_labels_are_complete():
    assert adapter.ADAPTER_LABELS == [
        "REPO-OWNED PUBLIC PERP-DATA COVERAGE OUTPUT",
        "NOT CANONICAL DATA AUTHORITY WITHOUT SEPARATE PROMOTION",
        "NOT A RESULT POPULATION",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT BACKTEST COST-MODEL AUTHORITY",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
        "PUBLIC-ONLY SAMPLE PARSING; NO NETWORK CALLS IN DEFAULT MODE",
    ]


def test_coverage_matrix_has_required_fields_and_history_classes():
    rows = adapter.coverage_matrix()

    assert len(rows) == len(adapter.ENDPOINT_DEFINITIONS)
    assert {row["history_depth_class"] for row in rows} >= {"backfillable", "recent_only"}
    for row in rows:
        assert set(row) == set(adapter.COVERAGE_FIELDS)
        assert row["requires_credentials"] is False
        assert row["public_private_classification"].startswith("public")
        assert row["history_depth_class"] in adapter.HISTORY_DEPTH_CLASSES
        assert row["timezone_policy"] == "millisecond epoch normalized to UTC"


def test_existing_funding_mark_index_premium_surfaces_are_preserved():
    rows = {row["lineage_key"]: row for row in adapter.coverage_matrix()}

    preserved = [
        "binance_usds_m_btcusdt_funding_history_public_preserved",
        "binance_usds_m_btcusdt_mark_price_klines_public_preserved",
        "binance_usds_m_btcusdt_index_price_klines_public_preserved",
        "binance_usds_m_btcusdt_premium_index_klines_public_preserved",
    ]
    for lineage_key in preserved:
        assert rows[lineage_key]["status"] == "preserved"
        assert rows[lineage_key]["history_depth_class"] == "backfillable"


@pytest.mark.parametrize(
    "endpoint_key,expected_data_type",
    [
        ("current_open_interest", "current_open_interest"),
        ("open_interest_statistics", "open_interest_statistics"),
        ("top_trader_long_short_position_ratio", "top_trader_long_short_position_ratio"),
        ("top_trader_long_short_account_ratio", "top_trader_long_short_account_ratio"),
        ("global_long_short_account_ratio", "global_long_short_account_ratio"),
        ("taker_buy_sell_volume_ratio", "taker_buy_sell_volume_ratio"),
        ("aggregate_trades_rest", "aggregate_trade"),
        ("recent_trades_rest", "trade"),
        ("exchange_metadata", "exchange_metadata"),
    ],
)
def test_normalize_sample_responses(endpoint_key, expected_data_type):
    payload = adapter._load_sample(adapter.DEFAULT_SAMPLE_DIR, endpoint_key)
    rows = adapter.normalize_sample(endpoint_key, payload)

    assert rows
    assert rows[0]["symbol"] == "BTCUSDT"
    assert rows[0]["data_type"] == expected_data_type
    assert rows[0]["event_time_utc"].endswith("Z")
    assert rows[0]["sample_only"] is True
    assert rows[0]["canonical_data_authority"] is False
    assert rows[0]["runtime_authority"] is False
    assert "raw" in rows[0]


def test_normalize_kline_sample_response():
    payload = adapter._load_sample(adapter.DEFAULT_SAMPLE_DIR, "premium_index_klines_preserved")
    rows = adapter.normalize_sample("premium_index_klines_preserved", payload)

    assert rows == [
        {
            "exchange": "binance",
            "market_type": "USDT-M perpetual",
            "symbol": "BTCUSDT",
            "source_name": "binance_usds_m_public_rest",
            "endpoint_or_method": "GET /fapi/v1/premiumIndexKlines",
            "lineage_key": "binance_usds_m_btcusdt_premium_index_klines_public_preserved",
            "sample_only": True,
            "canonical_data_authority": False,
            "runtime_authority": False,
            "event_time_ms": 1577836800000,
            "event_time_utc": "2020-01-01T00:00:00Z",
            "data_type": "premium_index_klines",
            "open_time_ms": 1577836800000,
            "open_time_utc": "2020-01-01T00:00:00Z",
            "open": "0.00010000",
            "high": "0.00020000",
            "low": "-0.00005000",
            "close": "0.00015000",
            "close_time_ms": 1577837699999,
            "close_time_utc": "2020-01-01T00:14:59.999000Z",
            "raw": [
                1577836800000,
                "0.00010000",
                "0.00020000",
                "-0.00005000",
                "0.00015000",
                "0",
                1577837699999,
                "0",
                900,
                "0",
                "0",
                "0",
            ],
        }
    ]


def test_fail_closed_on_missing_required_fields():
    with pytest.raises(adapter.PerpPublicDataError, match="openInterest is required"):
        adapter.normalize_sample(
            "current_open_interest",
            {"symbol": "BTCUSDT", "time": 1577836800000},
        )

    with pytest.raises(adapter.PerpPublicDataError, match="unexpected symbol"):
        adapter.normalize_sample(
            "current_open_interest",
            {"symbol": "ETHUSDT", "openInterest": "1.0", "time": 1577836800000},
        )


def test_run_coverage_only_writes_expected_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    sample_dir = tmp_path / "tests" / "fixtures" / "data_ingestion" / "perp_public_data"
    shutil.copytree(adapter.DEFAULT_SAMPLE_DIR, sample_dir)
    output_dir = tmp_path / "scratch" / adapter.PACKAGE_ID
    result = adapter.write_coverage_artifacts(output_dir=output_dir, sample_dir=sample_dir)

    assert result["status"] == "PASS"
    assert result["canonical_write"] is False
    assert result["runtime_paper_live_contact"] is False
    assert {path.name for path in output_dir.iterdir()} == {
        "coverage_matrix.json",
        "coverage_matrix.md",
        "provenance.json",
        "sample_catalog_lineage.json",
        "validation_report.json",
        "validation_report.md",
    }
    coverage = json.loads((output_dir / "coverage_matrix.json").read_text(encoding="utf-8"))
    assert coverage["package"] == adapter.PACKAGE_ID
    assert len(coverage["coverage"]) == len(adapter.ENDPOINT_DEFINITIONS)
    lineage = json.loads((output_dir / "sample_catalog_lineage.json").read_text(encoding="utf-8"))
    assert lineage["canonical_data_authority"] is False
    assert lineage["promotion_readiness_authority"] is False
    validation = json.loads((output_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert validation["status"] == "PASS"
    assert validation["network_calls_performed"] is False
    assert validation["sample_endpoint_count"] == len(adapter.ENDPOINT_DEFINITIONS)


def test_adapter_source_has_no_credentials_account_order_or_private_method_calls():
    source = (
        adapter.REPO_ROOT / "tools/data_ingestion/perp_public_data_adapter.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = [
        "apiKey",
        "secret",
        "createOrder",
        "fetchBalance",
        "fetchPositions",
        "fetchOpenOrders",
        "cancelOrder",
        "fapiPrivate",
        "dapiPrivate",
        "USER_DATA",
    ]
    assert not any(term in source for term in forbidden_terms)
