import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

import pandas as pd
import pyarrow.parquet as pq

from src.data_sources.binance_perp_realism import _write_parquet, deterministic_book_ticker_downsample


def test_deterministic_book_ticker_downsample_last_in_bucket():
    df = pd.DataFrame(
        [
            {"event_time_ms": 1000, "bestBidPrice": 1.0},
            {"event_time_ms": 9000, "bestBidPrice": 2.0},
            {"event_time_ms": 10001, "bestBidPrice": 3.0},
            {"event_time_ms": 19999, "bestBidPrice": 4.0},
        ]
    )

    out = deterministic_book_ticker_downsample(df, bucket_seconds=10)

    assert out["bucket_start_ms"].tolist() == [0, 10000]
    assert out["bestBidPrice"].tolist() == [2.0, 4.0]


def test_write_parquet_metadata_roundtrip(tmp_path):
    path = tmp_path / "x.parquet"
    _write_parquet(pd.DataFrame([{"event_time_ms": 1000}]), path, metadata={"bucket_seconds": "10"})

    md = pq.read_schema(path).metadata
    assert md[b"bucket_seconds"] == b"10"
