from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd


ZERO = Decimal("0")
MILLIS_PER_SECOND = 1000


def _parse_iso_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"Expected timezone-aware UTC timestamp, got: {value}")
    return dt.astimezone(timezone.utc)


def _iso_utc_from_ms(value: int) -> str:
    dt = datetime.fromtimestamp(value / MILLIS_PER_SECOND, tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _decimal_from_value(value: Any) -> Decimal | None:
    if value is None or pd.isna(value):
        return None

    try:
        return Decimal(str(value))
    except Exception:
        return None


@dataclass(frozen=True)
class PriceReference:
    price_ref: Decimal
    price_ref_source: str
    price_ref_asof_utc: str

    def to_event_fields(self) -> dict[str, str]:
        return {
            "price_ref": _decimal_text(self.price_ref) or "0",
            "price_ref_source": self.price_ref_source,
            "price_ref_asof_utc": self.price_ref_asof_utc,
        }


class PriceRefProvider:
    def __init__(
        self,
        *,
        bookticker_parquet: str | None,
        premiumindex_parquet: str | None,
        lookback_seconds: int,
        fixed_fallback: Decimal,
    ) -> None:
        self.bookticker_parquet = bookticker_parquet
        self.premiumindex_parquet = premiumindex_parquet
        self.lookback_seconds = max(int(lookback_seconds), 0)
        self.fixed_fallback = fixed_fallback
        self._cache: dict[str, pd.DataFrame | None] = {}

    def resolve(self, *, symbol: str, evaluation_time_utc: str, mode: str) -> PriceReference:
        requested_mode = mode.strip().lower()
        if requested_mode == "mid_bookticker":
            book_ref = self._resolve_bookticker(symbol=symbol, evaluation_time_utc=evaluation_time_utc)
            if book_ref is not None:
                return book_ref

            premium_ref = self._resolve_premiumindex(symbol=symbol, evaluation_time_utc=evaluation_time_utc)
            if premium_ref is not None:
                return premium_ref

            return self._fixed_reference(evaluation_time_utc=evaluation_time_utc, source="fixed_fallback")

        if requested_mode == "mark_premiumindex":
            premium_ref = self._resolve_premiumindex(symbol=symbol, evaluation_time_utc=evaluation_time_utc)
            if premium_ref is not None:
                return premium_ref

            return self._fixed_reference(evaluation_time_utc=evaluation_time_utc, source="fixed_fallback")

        if requested_mode == "fixed":
            return self._fixed_reference(evaluation_time_utc=evaluation_time_utc, source="fixed")

        raise ValueError(f"Unsupported paper_fill_price_mode: {mode}")

    def _resolve_bookticker(self, *, symbol: str, evaluation_time_utc: str) -> PriceReference | None:
        df = self._load_parquet(self.bookticker_parquet)
        return self._select_reference(
            df=df,
            symbol=symbol,
            evaluation_time_utc=evaluation_time_utc,
            source="mid_bookticker",
            extractor=self._extract_bookticker_mid,
        )

    def _resolve_premiumindex(self, *, symbol: str, evaluation_time_utc: str) -> PriceReference | None:
        df = self._load_parquet(self.premiumindex_parquet)
        return self._select_reference(
            df=df,
            symbol=symbol,
            evaluation_time_utc=evaluation_time_utc,
            source="mark_premiumindex",
            extractor=self._extract_mark_price,
        )

    def _load_parquet(self, path_text: str | None) -> pd.DataFrame | None:
        if path_text is None:
            return None

        candidate = str(path_text).strip()
        if candidate == "" or candidate.lower() == "null":
            return None

        if candidate in self._cache:
            return self._cache[candidate]

        try:
            df = pd.read_parquet(Path(candidate))
        except Exception:
            df = None

        if df is not None and not isinstance(df, pd.DataFrame):
            df = None

        self._cache[candidate] = df
        return df

    def _select_reference(
        self,
        *,
        df: pd.DataFrame | None,
        symbol: str,
        evaluation_time_utc: str,
        source: str,
        extractor: Any,
    ) -> PriceReference | None:
        if df is None or df.empty:
            return None

        timestamp_column = self._timestamp_column(df)
        if timestamp_column is None:
            return None

        work = df
        if "symbol" in work.columns:
            work = work[work["symbol"].astype(str) == symbol]
        if work.empty:
            return None

        evaluation_ms = int(_parse_iso_utc(evaluation_time_utc).timestamp() * MILLIS_PER_SECOND)
        lower_bound_ms = evaluation_ms - (self.lookback_seconds * MILLIS_PER_SECOND)

        work = work.assign(
            _ts_ms=pd.to_numeric(work[timestamp_column], errors="coerce"),
            _row_seq=range(len(work)),
        )
        work = work[(work["_ts_ms"] <= evaluation_ms) & (work["_ts_ms"] >= lower_bound_ms)]
        if work.empty:
            return None

        ordered = work.sort_values(["_ts_ms", "_row_seq"], kind="mergesort")
        for _, row in ordered.iloc[::-1].iterrows():
            price_ref = extractor(row)
            if price_ref is None or price_ref <= ZERO:
                continue

            return PriceReference(
                price_ref=price_ref,
                price_ref_source=source,
                price_ref_asof_utc=_iso_utc_from_ms(int(row["_ts_ms"])),
            )

        return None

    def _timestamp_column(self, df: pd.DataFrame) -> str | None:
        for column in ("event_time_ms", "observed_at_ms"):
            if column in df.columns:
                return column
        return None

    def _extract_bookticker_mid(self, row: Any) -> Decimal | None:
        bid = _decimal_from_value(row.get("bestBidPrice"))
        ask = _decimal_from_value(row.get("bestAskPrice"))
        if bid is None or ask is None:
            return None
        return (bid + ask) / Decimal("2")

    def _extract_mark_price(self, row: Any) -> Decimal | None:
        return _decimal_from_value(row.get("markPrice"))

    def _fixed_reference(self, *, evaluation_time_utc: str, source: str) -> PriceReference:
        return PriceReference(
            price_ref=self.fixed_fallback,
            price_ref_source=source,
            price_ref_asof_utc=evaluation_time_utc,
        )
