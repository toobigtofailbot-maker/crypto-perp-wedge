import json

import pytest

from tools.data_ingestion import ccxt_public_funding_adapter as adapter


class FakeExchange:
    def __init__(self, pages):
        self.pages = list(pages)
        self.requests = []

    def fapiPublicGetFundingRate(self, request):
        self.requests.append(dict(request))
        if not self.pages:
            return []
        return self.pages.pop(0)


class FakeCcxtModule:
    __version__ = "fake-ccxt"

    def __init__(self, exchange):
        self._exchange = exchange

    def binanceusdm(self, config):
        assert config == {"enableRateLimit": True}
        return self._exchange


def _row(timestamp_ms: int, rate: str = "0.0001") -> dict:
    return {
        "symbol": "BTCUSDT",
        "fundingTime": str(timestamp_ms),
        "fundingRate": rate,
        "markPrice": "10000.0",
    }


def test_adapter_labels_are_complete():
    assert adapter.ADAPTER_LABELS == [
        "REPO-OWNED CCXT PUBLIC-DATA ADAPTER OUTPUT",
        "NOT CANONICAL DATA AUTHORITY WITHOUT SEPARATE PROMOTION",
        "NOT A RESULT POPULATION",
        "NOT STRATEGY / VM / SWEEP AUTHORITY",
        "NOT BACKTEST COST-MODEL AUTHORITY",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
        "FUNDING-INTO-BACKTEST REQUIRES A SEPARATE GATED WP",
    ]


def test_fetch_paginates_with_public_method_only():
    start = 1577836800000
    exchange = FakeExchange(
        [
            [_row(start), _row(start + adapter.FUNDING_INTERVAL_MS)],
            [_row(start + 2 * adapter.FUNDING_INTERVAL_MS)],
        ]
    )

    rows, pages = adapter.fetch_raw_funding_rows(
        exchange,
        symbol="BTCUSDT",
        start_ms=start,
        end_ms=start + 2 * adapter.FUNDING_INTERVAL_MS,
        limit=2,
    )

    assert len(rows) == 3
    assert [page.row_count for page in pages] == [2, 1]
    assert exchange.requests[0]["startTime"] == start
    assert exchange.requests[1]["startTime"] == start + adapter.FUNDING_INTERVAL_MS + 1
    assert set(exchange.requests[0]) == {"symbol", "startTime", "endTime", "limit"}


def test_normalization_preserves_raw_provenance_fields():
    normalized = adapter.normalize_raw_row(
        _row(1577836800000, "-0.00012359"),
        page_index=2,
        row_index=3,
    )

    assert normalized == {
        "exchange": "binance",
        "market_type": "USDT-M perpetual",
        "symbol": "BTCUSDT",
        "data_type": "funding_rate",
        "funding_time_utc": "2020-01-01T00:00:00Z",
        "funding_time_ms": 1577836800000,
        "exchange_funding_time_utc": "2020-01-01T00:00:00Z",
        "exchange_funding_time_ms": 1577836800000,
        "exchange_funding_time_offset_ms": 0,
        "funding_rate": "-0.00012359",
        "mark_price": "10000.0",
        "source_method": "ccxt.binanceusdm.fapiPublicGetFundingRate",
        "raw_symbol": "BTCUSDT",
        "raw_page_index": 2,
        "raw_row_index": 3,
    }


def test_run_ingest_writes_snapshot_validation_provenance_and_lineage(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    start = 1577836800000
    rows = [
        _row(start, "0.0001"),
        _row(start + adapter.FUNDING_INTERVAL_MS, "0.0002"),
        _row(start + 2 * adapter.FUNDING_INTERVAL_MS, "-0.0003"),
    ]
    exchange = FakeExchange([rows])
    result = adapter.run_ingest(
        output_dir=tmp_path,
        start_utc="2020-01-01T00:00:00Z",
        end_utc="2020-01-01T16:00:00Z",
        ccxt_module=FakeCcxtModule(exchange),
        limit=1000,
    )

    assert result["validation_status"] == "PASS"
    assert result["recommendation"] == "ADOPT_AS_PUBLIC_DATA_ADAPTER"
    assert result["dependency_mode"] == "optional_ccxt_import_no_repo_dependency_change"
    assert result["row_count"] == 3
    assert {path.name for path in tmp_path.iterdir()} == {
        "catalog_lineage.json",
        "funding_snapshot.normalized.jsonl",
        "funding_snapshot.raw.jsonl",
        "funding_snapshot.sha256",
        "provenance.json",
        "validation_report.json",
        "validation_report.md",
    }
    checksum = (tmp_path / "funding_snapshot.sha256").read_text(encoding="utf-8").strip()
    assert checksum == result["checksum"]
    assert checksum.startswith("sha256:")
    validation = json.loads((tmp_path / "validation_report.json").read_text(encoding="utf-8"))
    assert validation["labels"] == adapter.ADAPTER_LABELS
    assert validation["coverage"]["expected_event_count"] == 3
    assert validation["required_fields"]["pass"] is True
    provenance = json.loads((tmp_path / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["ccxt_public_method_allowlist"] == ["fapiPublicGetFundingRate"]
    assert provenance["credentials_used"] is False
    assert provenance["output_files"]["normalized_snapshot"]["path"].endswith(
        "funding_snapshot.normalized.jsonl"
    )
    assert not provenance["output_files"]["normalized_snapshot"]["path"].startswith("C:")
    lineage = json.loads((tmp_path / "catalog_lineage.json").read_text(encoding="utf-8"))
    assert lineage["catalog_status"] == "repo_owned_public_data_adapter_snapshot"
    assert lineage["canonical_data_authority"] is False
    assert lineage["decision_label"] == "ADOPT_AS_PUBLIC_DATA_ADAPTER"
    assert not lineage["normalized_snapshot_path"].startswith("C:")


def test_run_ingest_deduplicates_normalized_snapshot_and_reports_raw_duplicate(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(adapter, "REPO_ROOT", tmp_path)
    start = 1577836800000
    rows = [
        _row(start, "0.0001"),
        _row(start, "0.0001"),
        _row(start + adapter.FUNDING_INTERVAL_MS, "0.0002"),
    ]
    exchange = FakeExchange([rows])
    result = adapter.run_ingest(
        output_dir=tmp_path,
        start_utc="2020-01-01T00:00:00Z",
        end_utc="2020-01-01T08:00:00Z",
        ccxt_module=FakeCcxtModule(exchange),
        limit=1000,
    )

    assert result["validation_status"] == "PASS"
    normalized_lines = (tmp_path / "funding_snapshot.normalized.jsonl").read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(normalized_lines) == 2
    validation = json.loads((tmp_path / "validation_report.json").read_text(encoding="utf-8"))
    assert validation["duplicates"]["duplicate_group_count"] == 0
    assert validation["duplicates"]["dedupe_report"] == {
        "raw_duplicate_group_count_removed": 1,
        "raw_duplicate_row_count_removed": 1,
        "raw_duplicate_timestamps_utc": ["2020-01-01T00:00:00Z"],
    }


def test_validation_detects_duplicates_gaps_and_unsorted_rows():
    start = 1577836800000
    rows = [
        {
            "funding_time_ms": start + 2 * adapter.FUNDING_INTERVAL_MS,
            "funding_time_utc": "2020-01-01T16:00:00Z",
            "funding_rate": "0.1",
            "mark_price": None,
        },
        {
            "funding_time_ms": start,
            "funding_time_utc": "2020-01-01T00:00:00Z",
            "funding_rate": "0.1",
            "mark_price": None,
        },
        {
            "funding_time_ms": start,
            "funding_time_utc": "2020-01-01T00:00:00Z",
            "funding_rate": "0.1",
            "mark_price": None,
        },
    ]

    report = adapter.validate_normalized_rows(
        rows,
        start_ms=start,
        end_ms=start + 3 * adapter.FUNDING_INTERVAL_MS,
        checksum="sha256:abc",
        provenance_complete=True,
    )

    assert report["status"] == "FAIL"
    assert report["sorted"]["pass"] is False
    assert report["duplicates"]["duplicate_group_count"] == 1
    assert report["gaps"]["missing_event_count"] == 2


def test_validation_detects_misaligned_timestamp_and_bad_numeric_value():
    start = 1577836800000
    rows = [
        {
            "funding_time_ms": start + 1,
            "funding_time_utc": "2020-01-01T00:00:00.001Z",
            "funding_rate": "not-numeric",
            "mark_price": None,
        }
    ]

    report = adapter.validate_normalized_rows(
        rows,
        start_ms=start,
        end_ms=start + adapter.FUNDING_INTERVAL_MS,
        checksum="sha256:abc",
        provenance_complete=True,
    )

    assert report["status"] == "FAIL"
    assert report["utc_alignment"]["misaligned_count"] == 1
    assert report["numeric"]["funding_values_parse"] is False


def test_validation_detects_missing_required_fields():
    start = 1577836800000
    report = adapter.validate_normalized_rows(
        [{"funding_time_ms": start, "funding_rate": "0.0"}],
        start_ms=start,
        end_ms=start,
        checksum="sha256:abc",
        provenance_complete=True,
    )

    assert report["status"] == "FAIL"
    assert report["required_fields"]["pass"] is False
    assert report["required_fields"]["missing_field_counts"]["exchange"] == 1


def test_normalization_preserves_small_exchange_timestamp_offset():
    normalized = adapter.normalize_raw_row(
        _row(1577836800003, "0.0001"),
        page_index=0,
        row_index=0,
    )

    assert normalized["funding_time_ms"] == 1577836800000
    assert normalized["funding_time_utc"] == "2020-01-01T00:00:00Z"
    assert normalized["exchange_funding_time_ms"] == 1577836800003
    assert normalized["exchange_funding_time_utc"] == "2020-01-01T00:00:00.003000Z"
    assert normalized["exchange_funding_time_offset_ms"] == 3


def test_adapter_source_has_no_credentials_account_order_or_private_method_calls():
    source = (
        adapter.REPO_ROOT / "tools/data_ingestion/ccxt_public_funding_adapter.py"
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
    ]
    assert not any(term in source for term in forbidden_terms)
    assert adapter.PUBLIC_METHOD == "fapiPublicGetFundingRate"


def test_missing_ccxt_has_clear_dependency_error(monkeypatch):
    def fail_import(_name):
        raise ModuleNotFoundError("ccxt")

    monkeypatch.setattr(adapter.importlib, "import_module", fail_import)

    with pytest.raises(adapter.FundingIngestError, match="ccxt is not installed"):
        adapter._load_ccxt()
