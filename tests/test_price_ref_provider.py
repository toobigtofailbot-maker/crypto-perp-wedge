from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd

from src.marketdata.price_ref_provider import PriceRefProvider


def _utc_ms(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return int(dt.astimezone(timezone.utc).timestamp() * 1000)


def _write_parquet(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_parquet(path, index=False)


def test_price_ref_provider_selects_nearest_prior_bookticker_mid(tmp_path: Path) -> None:
    book_path = tmp_path / "bookticker.parquet"
    premium_path = tmp_path / "premium.parquet"

    _write_parquet(
        book_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:40Z"),
                "bestBidPrice": 99990,
                "bestAskPrice": 100010,
            },
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:55Z"),
                "bestBidPrice": 100000,
                "bestAskPrice": 100020,
            },
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T01:00:05Z"),
                "bestBidPrice": 200000,
                "bestAskPrice": 200020,
            },
        ],
    )
    _write_parquet(
        premium_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:58Z"),
                "markPrice": 99950,
            }
        ],
    )

    provider = PriceRefProvider(
        bookticker_parquet=str(book_path),
        premiumindex_parquet=str(premium_path),
        lookback_seconds=3600,
        fixed_fallback=Decimal("123456"),
    )

    reference = provider.resolve(
        symbol="BTCUSDT",
        evaluation_time_utc="2026-01-01T01:00:00Z",
        mode="mid_bookticker",
    )

    assert reference.price_ref == Decimal("100010")
    assert reference.price_ref_source == "mid_bookticker"
    assert reference.price_ref_asof_utc == "2026-01-01T00:59:55Z"


def test_price_ref_provider_falls_back_to_mark_price_when_bookticker_misses_lookback(tmp_path: Path) -> None:
    book_path = tmp_path / "bookticker.parquet"
    premium_path = tmp_path / "premium.parquet"

    _write_parquet(
        book_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:00:00Z"),
                "bestBidPrice": 99990,
                "bestAskPrice": 100010,
            }
        ],
    )
    _write_parquet(
        premium_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:57Z"),
                "markPrice": 100123,
            }
        ],
    )

    provider = PriceRefProvider(
        bookticker_parquet=str(book_path),
        premiumindex_parquet=str(premium_path),
        lookback_seconds=60,
        fixed_fallback=Decimal("123456"),
    )

    reference = provider.resolve(
        symbol="BTCUSDT",
        evaluation_time_utc="2026-01-01T01:00:00Z",
        mode="mid_bookticker",
    )

    assert reference.price_ref == Decimal("100123")
    assert reference.price_ref_source == "mark_premiumindex"
    assert reference.price_ref_asof_utc == "2026-01-01T00:59:57Z"


def test_price_ref_provider_fails_open_to_fixed_on_invalid_local_parquet(tmp_path: Path) -> None:
    invalid_book_path = tmp_path / "bookticker.parquet"
    invalid_book_path.write_text("not parquet", encoding="utf-8")

    provider = PriceRefProvider(
        bookticker_parquet=str(invalid_book_path),
        premiumindex_parquet=str(tmp_path / "missing.parquet"),
        lookback_seconds=3600,
        fixed_fallback=Decimal("101001"),
    )

    reference = provider.resolve(
        symbol="BTCUSDT",
        evaluation_time_utc="2026-01-01T01:00:00Z",
        mode="mid_bookticker",
    )

    assert reference.price_ref == Decimal("101001")
    assert reference.price_ref_source == "fixed_fallback"
    assert reference.price_ref_asof_utc == "2026-01-01T01:00:00Z"
