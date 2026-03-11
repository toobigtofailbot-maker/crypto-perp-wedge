from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE_FAPI_URL = "https://fapi.binance.com"
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_BUCKET_SECONDS = 10


@dataclass(frozen=True)
class CollectionConfig:
    symbol: str = DEFAULT_SYMBOL
    polls: int = 20
    poll_interval_seconds: float = 1.0
    book_ticker_bucket_seconds: int = DEFAULT_BUCKET_SECONDS
    offline_sample: bool = False


def _utc_now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _http_json(path: str, params: dict[str, Any] | None = None) -> Any:
    params = params or {}
    query = urlencode(params)
    url = f"{BASE_FAPI_URL}{path}"
    if query:
        url = f"{url}?{query}"
    with urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _to_float(value: Any) -> float:
    return float(value) if value is not None else float("nan")


def fetch_premium_index_snapshot(symbol: str, observed_at_ms: int) -> dict[str, Any]:
    row = _http_json("/fapi/v1/premiumIndex", {"symbol": symbol})
    return {
        "symbol": row.get("symbol", symbol),
        "observed_at_ms": observed_at_ms,
        "event_time_ms": int(row.get("time") or observed_at_ms),
        "markPrice": _to_float(row.get("markPrice")),
        "indexPrice": _to_float(row.get("indexPrice")),
        "lastFundingRate": _to_float(row.get("lastFundingRate")),
        "nextFundingTime": int(row.get("nextFundingTime")) if row.get("nextFundingTime") else None,
    }


def fetch_book_ticker_snapshot(symbol: str, observed_at_ms: int) -> dict[str, Any]:
    row = _http_json("/fapi/v1/ticker/bookTicker", {"symbol": symbol})
    return {
        "symbol": row.get("symbol", symbol),
        "observed_at_ms": observed_at_ms,
        "event_time_ms": observed_at_ms,
        "bestBidPrice": _to_float(row.get("bidPrice")),
        "bestBidQty": _to_float(row.get("bidQty")),
        "bestAskPrice": _to_float(row.get("askPrice")),
        "bestAskQty": _to_float(row.get("askQty")),
        "updateId": int(row.get("lastUpdateId")) if row.get("lastUpdateId") else None,
    }


def fetch_funding_schedule_metadata(symbol: str, observed_at_ms: int) -> dict[str, Any]:
    info_rows = _http_json("/fapi/v1/fundingInfo", {"symbol": symbol})
    if isinstance(info_rows, list):
        info = info_rows[0] if info_rows else {}
    else:
        info = info_rows

    premium = _http_json("/fapi/v1/premiumIndex", {"symbol": symbol})

    return {
        "symbol": symbol,
        "observed_at_ms": observed_at_ms,
        "nextFundingTime": int(premium.get("nextFundingTime")) if premium.get("nextFundingTime") else None,
        "fundingIntervalHours": int(info.get("fundingIntervalHours")) if info.get("fundingIntervalHours") else None,
        "adjustedFundingRateCap": _to_float(info.get("adjustedFundingRateCap")) if info else None,
        "adjustedFundingRateFloor": _to_float(info.get("adjustedFundingRateFloor")) if info else None,
        "disclaimer": info.get("disclaimer") if info else None,
    }




def _offline_sample_rows(symbol: str, observed_at_ms: int, seq: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    drift = seq * 5.0
    premium = {
        "symbol": symbol,
        "observed_at_ms": observed_at_ms,
        "event_time_ms": observed_at_ms,
        "markPrice": 90000.0 + drift,
        "indexPrice": 89990.0 + drift,
        "lastFundingRate": 0.0001,
        "nextFundingTime": ((observed_at_ms // (8 * 60 * 60 * 1000)) + 1) * (8 * 60 * 60 * 1000),
    }
    book = {
        "symbol": symbol,
        "observed_at_ms": observed_at_ms,
        "event_time_ms": observed_at_ms,
        "bestBidPrice": 89999.0 + drift,
        "bestBidQty": 2.0 + seq * 0.01,
        "bestAskPrice": 90001.0 + drift,
        "bestAskQty": 1.5 + seq * 0.01,
        "updateId": seq + 1,
    }
    schedule = {
        "symbol": symbol,
        "observed_at_ms": observed_at_ms,
        "nextFundingTime": premium["nextFundingTime"],
        "fundingIntervalHours": 8,
        "adjustedFundingRateCap": 0.025,
        "adjustedFundingRateFloor": -0.025,
        "disclaimer": False,
    }
    return premium, book, schedule

def deterministic_book_ticker_downsample(df: pd.DataFrame, bucket_seconds: int) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    if bucket_seconds <= 0:
        raise ValueError("bucket_seconds must be positive")

    work = df.copy()
    bucket_ms = bucket_seconds * 1000
    work["snapshot_seq"] = range(len(work))
    work["bucket_start_ms"] = (pd.to_numeric(work["event_time_ms"], errors="coerce") // bucket_ms) * bucket_ms

    work = work.sort_values(["bucket_start_ms", "event_time_ms", "snapshot_seq"], kind="mergesort")
    sampled = work.groupby("bucket_start_ms", as_index=False).tail(1)
    sampled = sampled.sort_values(["bucket_start_ms", "event_time_ms", "snapshot_seq"], kind="mergesort")
    sampled = sampled.drop(columns=["snapshot_seq"]).reset_index(drop=True)
    return sampled


def _write_parquet(df: pd.DataFrame, path: Path, metadata: dict[str, str] | None = None) -> None:
    table = pa.Table.from_pandas(df, preserve_index=False)
    if metadata:
        encoded = {k.encode("utf-8"): v.encode("utf-8") for k, v in metadata.items()}
        table = table.replace_schema_metadata({**(table.schema.metadata or {}), **encoded})
    pq.write_table(table, path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_and_store(config: CollectionConfig, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    premium_rows: list[dict[str, Any]] = []
    book_rows: list[dict[str, Any]] = []
    schedule_rows: list[dict[str, Any]] = []

    for i in range(config.polls):
        observed_at_ms = _utc_now_ms()
        if config.offline_sample:
            premium, book, schedule = _offline_sample_rows(config.symbol, observed_at_ms, i)
        else:
            premium = fetch_premium_index_snapshot(config.symbol, observed_at_ms)
            book = fetch_book_ticker_snapshot(config.symbol, observed_at_ms)
            schedule = fetch_funding_schedule_metadata(config.symbol, observed_at_ms)
        premium_rows.append(premium)
        book_rows.append(book)
        schedule_rows.append(schedule)
        if i != config.polls - 1:
            time.sleep(config.poll_interval_seconds)

    premium_df = pd.DataFrame(premium_rows).sort_values("event_time_ms").reset_index(drop=True)
    book_df = pd.DataFrame(book_rows).sort_values("event_time_ms").reset_index(drop=True)
    schedule_df = pd.DataFrame(schedule_rows).sort_values("observed_at_ms").reset_index(drop=True)

    sampled_book_df = deterministic_book_ticker_downsample(book_df, config.book_ticker_bucket_seconds)

    start_dt = datetime.fromtimestamp(min(premium_df["event_time_ms"]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    end_dt = datetime.fromtimestamp(max(premium_df["event_time_ms"]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")

    premium_path = output_dir / (
        f"binance_um_perp_{config.symbol}_premium_index_snapshots_{start_dt}_{end_dt}_{created_utc}.parquet"
    )
    book_path = output_dir / (
        f"binance_um_perp_{config.symbol}_book_ticker_{config.book_ticker_bucket_seconds}s_{start_dt}_{end_dt}_{created_utc}.parquet"
    )
    schedule_path = output_dir / (
        f"binance_um_perp_{config.symbol}_funding_schedule_metadata_{start_dt}_{end_dt}_{created_utc}.parquet"
    )

    _write_parquet(premium_df, premium_path, metadata={"dataset": "premium_index_snapshots"})
    _write_parquet(
        sampled_book_df,
        book_path,
        metadata={
            "dataset": "book_ticker",
            "bucket_seconds": str(config.book_ticker_bucket_seconds),
            "downsample_method": "floor_bucket_last_snapshot",
        },
    )
    _write_parquet(schedule_df, schedule_path, metadata={"dataset": "funding_schedule_metadata"})

    return {
        "premium": {"path": premium_path.as_posix(), "sha256": sha256_file(premium_path), "rows": len(premium_df)},
        "book_ticker": {
            "path": book_path.as_posix(),
            "sha256": sha256_file(book_path),
            "rows": len(sampled_book_df),
            "bucket_seconds": config.book_ticker_bucket_seconds,
        },
        "funding_schedule": {
            "path": schedule_path.as_posix(),
            "sha256": sha256_file(schedule_path),
            "rows": len(schedule_df),
        },
        "range": {"start_date": start_dt, "end_date": end_dt, "created_utc": created_utc},
    }
