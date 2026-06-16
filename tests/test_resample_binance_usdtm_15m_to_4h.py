from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.data.resample_binance_usdtm_15m_to_4h import (
    AGGREGATION_MAP,
    DATASET_ID,
    OUTPUT_COLUMNS,
    ResampleError,
    _build_catalog_entry,
    _build_validation_report,
    resample_rows,
)


PARENT_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)
PARENT_SHA = "c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab"
PARENT_VALIDATION_SHA = "785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c"


def _iso(timestamp: datetime) -> str:
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _row(timestamp: datetime, index: int) -> dict[str, str]:
    open_time_ms = int(timestamp.timestamp() * 1000)
    open_price = 100 + index
    close_price = 101 + index
    return {
        "open_time_ms": str(open_time_ms),
        "open_time": _iso(timestamp),
        "open": str(open_price),
        "high": str(105 + index),
        "low": str(95 - index),
        "close": str(close_price),
        "volume": "1.5",
        "close_time_ms": str(open_time_ms + 15 * 60 * 1000 - 1),
        "quote_asset_volume": "10.25",
        "num_trades": str(2 + index),
        "taker_buy_base_vol": "0.5",
        "taker_buy_quote_vol": "3.75",
        "ignore": "0",
    }


def _rows(count: int = 16, *, start_hour: int = 0) -> list[dict[str, str]]:
    start = datetime(2024, 1, 1, start_hour, 0, tzinfo=timezone.utc)
    return [_row(start + timedelta(minutes=15 * index), index) for index in range(count)]


def _parent_metadata() -> dict:
    return {
        "catalog": {"catalog_ref": "parent-catalog-ref"},
        "parent_validation_sha256": PARENT_VALIDATION_SHA,
        "parent_catalog_path": "research/data_slices/binance_usdtm_btcusdt_15m/parent.catalog_slice.json",
        "parent_validation_path": "research/data_slices/binance_usdtm_btcusdt_15m/parent.validation_report.json",
        "parent_csv_path": "data/processed/d4a/parent.csv",
        "parent_normalized_sha256": PARENT_SHA,
        "parent_data_slice_identity": PARENT_IDENTITY,
    }


def _output_facts() -> dict:
    return {
        "row_count": 1,
        "expected_row_count": 1,
        "start_utc": "2024-01-01T00:00:00Z",
        "end_utc": "2024-01-01T00:00:00Z",
        "parent": {
            "row_count": 16,
            "start_utc": "2024-01-01T00:00:00Z",
            "end_utc": "2024-01-01T03:45:00Z",
        },
    }


def test_synthetic_16_row_group_aggregates_to_one_4h_row():
    output, facts = resample_rows(_rows())

    assert len(output) == 1
    row = output[0]
    assert list(row) == OUTPUT_COLUMNS
    assert row["open_time"] == "2024-01-01T00:00:00Z"
    assert row["open"] == "100"
    assert row["high"] == "120"
    assert row["low"] == "80"
    assert row["close"] == "116"
    assert row["volume"] == "24"
    assert row["quote_asset_volume"] == "164"
    assert row["num_trades"] == str(sum(range(2, 18)))
    assert row["taker_buy_base_vol"] == "8"
    assert row["taker_buy_quote_vol"] == "60"
    assert row["ignore"] == "0"
    assert row["close_time_ms"] == str(int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000) + 4 * 60 * 60 * 1000 - 1)
    assert facts["row_count"] == 1
    assert facts["expected_row_count"] == 1


def test_multiple_4h_groups_preserve_ordering_and_row_count():
    output, facts = resample_rows(_rows(32))

    assert [row["open_time"] for row in output] == [
        "2024-01-01T00:00:00Z",
        "2024-01-01T04:00:00Z",
    ]
    assert facts["row_count"] == 2
    assert facts["expected_row_count"] == 2


def test_non_utc_boundary_start_fails():
    with pytest.raises(ResampleError, match="UTC 4h boundary"):
        resample_rows(_rows(start_hour=1))


def test_missing_15m_bar_fails():
    rows = _rows(17)
    del rows[5]

    with pytest.raises(ResampleError, match="missing 15m bars detected: 1 bars"):
        resample_rows(rows)


def test_duplicate_15m_open_time_fails():
    rows = _rows()
    rows[2]["open_time_ms"] = rows[1]["open_time_ms"]
    rows[2]["open_time"] = rows[1]["open_time"]

    with pytest.raises(ResampleError, match="duplicate open_time values detected"):
        resample_rows(rows)


def test_partial_final_group_fails():
    with pytest.raises(ResampleError, match="not divisible by 16"):
        resample_rows(_rows(17))


def test_deterministic_identity_is_stable_for_same_inputs(tmp_path: Path):
    kwargs = {
        "output_csv_path": tmp_path / "out.csv",
        "output_csv_sha256": "a" * 64,
        "validation_report_path": tmp_path / "validation.json",
        "validation_report_sha256": "b" * 64,
        "derivation_report_path": tmp_path / "derivation.json",
        "derivation_report_sha256": "c" * 64,
        "output_facts": _output_facts(),
        "parent_metadata": _parent_metadata(),
    }

    first = _build_catalog_entry(**kwargs)
    second = _build_catalog_entry(**kwargs)

    assert first["slice_identity"]["data_slice_identity"] == second["slice_identity"]["data_slice_identity"]
    assert first["slice_identity"]["identity_input_ordering"] == "canonical_json_sort_keys_minified_ascii"
    assert first["dataset_id"] == DATASET_ID


def test_validation_report_has_no_exchange_runtime_paper_live_or_rp_authority(tmp_path: Path):
    report = _build_validation_report(
        output_csv_path=tmp_path / "out.csv",
        output_csv_sha256="a" * 64,
        output_facts=_output_facts(),
        parent_metadata=_parent_metadata(),
    )

    assert report["ok"] is True
    assert report["boundary"]["offline_local_input_only"] is True
    assert report["boundary"]["no_exchange_contact"] is True
    assert report["boundary"]["no_runtime_contact"] is True
    assert report["boundary"]["no_paper_live_contact"] is True
    assert report["boundary"]["no_result_population_write"] is True
    assert report["boundary"]["no_strategy_artifact_mutation"] is True


def test_catalog_entry_references_parent_identity_and_hashes(tmp_path: Path):
    entry = _build_catalog_entry(
        output_csv_path=tmp_path / "out.csv",
        output_csv_sha256="a" * 64,
        validation_report_path=tmp_path / "validation.json",
        validation_report_sha256="b" * 64,
        derivation_report_path=tmp_path / "derivation.json",
        derivation_report_sha256="c" * 64,
        output_facts=_output_facts(),
        parent_metadata=_parent_metadata(),
    )

    identity_inputs = entry["slice_identity"]["identity_inputs"]
    assert entry["parent"]["data_slice_identity"] == PARENT_IDENTITY
    assert entry["parent"]["normalized_sha256"] == PARENT_SHA
    assert entry["parent"]["validation_report_sha256"] == PARENT_VALIDATION_SHA
    assert identity_inputs["parent_data_slice_identity"] == PARENT_IDENTITY
    assert identity_inputs["parent_normalized_sha256"] == PARENT_SHA
    assert identity_inputs["parent_validation_report_sha256"] == PARENT_VALIDATION_SHA
    assert identity_inputs["aggregation_map"] == AGGREGATION_MAP
    assert entry["evidence_limit"]["not_strategy_quality_evidence"] is True
    assert entry["evidence_limit"]["no_result_population"] is True


def test_resampling_does_not_mutate_source_input():
    rows = _rows()
    original = deepcopy(rows)

    resample_rows(rows)

    assert rows == original
