import json
from pathlib import Path

import pandas as pd
import pytest

from tools.data.materialize_funding_feature import (
    FundingMaterializationError,
    materialize_funding_feature,
)


def _write_inputs(tmp_path: Path, *, coverage_class="FULL_HISTORY_PUBLIC_ARCHIVE"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    opens = pd.date_range("2026-01-01T00:00:00Z", periods=8, freq="15min")
    ohlcv = pd.DataFrame(
        {
            "open_time_ms": [int(value.timestamp() * 1000) for value in opens],
            "close_time_ms": [
                int((value + pd.Timedelta(minutes=15) - pd.Timedelta(milliseconds=1)).timestamp() * 1000)
                for value in opens
            ],
            "open": range(100, 108),
            "high": range(101, 109),
            "low": range(99, 107),
            "close": range(100, 108),
            "volume": [10.0] * 8,
        }
    )
    funding = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT"],
            "fundingTime": [
                int(pd.Timestamp("2025-12-31T16:00:00Z").timestamp() * 1000),
                int(pd.Timestamp("2026-01-01T00:30:00Z").timestamp() * 1000),
            ],
            "fundingRate": [0.0001, -0.0002],
        }
    )
    catalog = {
        "entries": [
            {
                "feature_name": "funding_rate",
                "compiler_visible": True,
                "coverage_class": coverage_class,
                "source_class": "PUBLIC_FUNDING_ARCHIVE",
                "conditions": ["Aligned funding records cover the claimed evidence window."],
            }
        ]
    }
    ohlcv_path = tmp_path / "ohlcv.csv"
    funding_path = tmp_path / "funding.parquet"
    catalog_path = tmp_path / "availability.json"
    ohlcv.to_csv(ohlcv_path, index=False)
    funding.to_parquet(funding_path, index=False)
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    return ohlcv_path, funding_path, catalog_path


def _run(tmp_path: Path, **overrides):
    ohlcv_path, funding_path, catalog_path = _write_inputs(
        tmp_path, coverage_class=overrides.pop("coverage_class", "FULL_HISTORY_PUBLIC_ARCHIVE")
    )
    output_path = tmp_path / "materialized.csv"
    manifest_path = tmp_path / "manifest.json"
    manifest = materialize_funding_feature(
        ohlcv_path=ohlcv_path,
        funding_path=funding_path,
        availability_catalog_path=overrides.pop("catalog_path", catalog_path),
        output_path=output_path,
        manifest_path=manifest_path,
        parent_catalog_ref="catalog-ref",
        parent_slice_identity="slice-id",
        **overrides,
    )
    return manifest, pd.read_csv(output_path), output_path


def test_materializes_bar_close_asof_without_lookahead(tmp_path):
    manifest, output, _ = _run(tmp_path)

    assert output["funding_rate"].tolist() == [0.0001, 0.0001, -0.0002, -0.0002, -0.0002, -0.0002, -0.0002, -0.0002]
    assert manifest["alignment"]["no_lookahead"] is True
    assert manifest["availability"]["source_class"] == "PUBLIC_FUNDING_ARCHIVE"
    assert manifest["parent_ohlcv"]["data_slice_identity"] == "slice-id"


def test_materialization_is_byte_deterministic(tmp_path):
    _, _, first = _run(tmp_path / "first")
    _, _, second = _run(tmp_path / "second")

    assert first.read_bytes() == second.read_bytes()


def test_recent_only_availability_fails_closed(tmp_path):
    with pytest.raises(FundingMaterializationError, match="approved full-history"):
        _run(tmp_path, coverage_class="RECENT_ONLY_PUBLIC_ENDPOINT")


def test_missing_source_identity_fails_closed(tmp_path):
    ohlcv_path, funding_path, _ = _write_inputs(tmp_path)
    with pytest.raises(FundingMaterializationError, match="identity/availability"):
        materialize_funding_feature(
            ohlcv_path=ohlcv_path,
            funding_path=funding_path,
            availability_catalog_path=tmp_path / "missing.json",
            output_path=tmp_path / "out.csv",
            manifest_path=tmp_path / "manifest.json",
        )


def test_incomplete_funding_coverage_fails_closed(tmp_path):
    ohlcv_path, funding_path, catalog_path = _write_inputs(tmp_path)
    funding = pd.read_parquet(funding_path).iloc[1:].copy()
    funding.to_parquet(funding_path, index=False)

    with pytest.raises(FundingMaterializationError, match="first OHLCV bar close"):
        materialize_funding_feature(
            ohlcv_path=ohlcv_path,
            funding_path=funding_path,
            availability_catalog_path=catalog_path,
            output_path=tmp_path / "out.csv",
            manifest_path=tmp_path / "manifest.json",
        )
