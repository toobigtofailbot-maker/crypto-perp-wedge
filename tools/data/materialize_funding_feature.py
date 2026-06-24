"""Materialize an offline funding-rate feature onto a 15-minute OHLCV slice.

This helper is local-file-only. It does not fetch data and does not apply funding
cash flows. Funding events are joined to bars using information available by the
bar close, then carried forward until the next observed event.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


MATERIALIZATION_VERSION = "funding-feature-15m-v1"
FEATURE_NAME = "funding_rate"
REQUIRED_SOURCE_CLASS = "PUBLIC_FUNDING_ARCHIVE"
REQUIRED_COVERAGE_CLASS = "FULL_HISTORY_PUBLIC_ARCHIVE"
OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
FUNDING_GAP_THRESHOLD = pd.Timedelta(hours=8, minutes=1)


class FundingMaterializationError(ValueError):
    """Raised when local inputs cannot satisfy the materialization contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_iso(value: pd.Timestamp) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _load_table(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FundingMaterializationError(f"local input does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise FundingMaterializationError(f"unsupported local input format: {path.suffix}")


def _availability_entry(catalog_path: Path) -> dict[str, Any]:
    if not catalog_path.is_file():
        raise FundingMaterializationError("funding source identity/availability catalog is missing")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    matches = [
        entry
        for entry in catalog.get("entries", [])
        if entry.get("feature_name") == FEATURE_NAME
        and entry.get("compiler_visible") is True
        and entry.get("coverage_class") == REQUIRED_COVERAGE_CLASS
        and entry.get("source_class") == REQUIRED_SOURCE_CLASS
    ]
    if not matches:
        raise FundingMaterializationError(
            "funding_rate lacks an approved full-history public local source label"
        )
    return matches[0]


def _ohlcv_times(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    if "open_time_ms" in frame:
        opens = pd.to_datetime(frame["open_time_ms"], unit="ms", utc=True, errors="coerce")
    elif "open_time" in frame:
        opens = pd.to_datetime(frame["open_time"], utc=True, errors="coerce")
    elif "timestamp" in frame:
        opens = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    else:
        raise FundingMaterializationError("OHLCV input lacks a supported timestamp column")
    if "close_time_ms" in frame:
        closes = pd.to_datetime(frame["close_time_ms"], unit="ms", utc=True, errors="coerce")
    else:
        closes = opens + pd.Timedelta(minutes=15) - pd.Timedelta(milliseconds=1)
    if opens.isna().any() or closes.isna().any():
        raise FundingMaterializationError("OHLCV input contains invalid timestamps")
    return pd.Series(opens), pd.Series(closes)


def _prepare_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(OHLCV_COLUMNS) - set(frame.columns)
    if missing:
        raise FundingMaterializationError(f"OHLCV input missing columns: {sorted(missing)}")
    opens, closes = _ohlcv_times(frame)
    prepared = frame.loc[:, OHLCV_COLUMNS].copy()
    prepared.insert(0, "timestamp", opens.map(_utc_iso))
    prepared["_open_time"] = opens
    prepared["_close_time"] = closes
    if prepared["_open_time"].duplicated().any():
        raise FundingMaterializationError("OHLCV input contains duplicate timestamps")
    if not prepared["_open_time"].is_monotonic_increasing:
        raise FundingMaterializationError("OHLCV input timestamps are not sorted")
    deltas = prepared["_open_time"].diff().dropna()
    if not deltas.empty and not (deltas == pd.Timedelta(minutes=15)).all():
        raise FundingMaterializationError("OHLCV input is not exactly 15-minute spaced")
    return prepared


def _prepare_funding(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    time_col = "fundingTime" if "fundingTime" in frame else "funding_time_ms"
    rate_col = "fundingRate" if "fundingRate" in frame else FEATURE_NAME
    if time_col not in frame or rate_col not in frame:
        raise FundingMaterializationError("funding input lacks timestamp or rate columns")
    if "symbol" not in frame:
        raise FundingMaterializationError("funding source identity is missing symbol")
    symbols = set(frame["symbol"].dropna().astype(str))
    if symbols != {symbol}:
        raise FundingMaterializationError(f"funding input symbol mismatch: {sorted(symbols)}")
    times = pd.to_datetime(frame[time_col], unit="ms", utc=True, errors="coerce")
    rates = pd.to_numeric(frame[rate_col], errors="coerce")
    prepared = pd.DataFrame({"_funding_time": times, FEATURE_NAME: rates})
    if prepared.isna().any().any():
        raise FundingMaterializationError("funding input contains invalid timestamps or rates")
    if prepared["_funding_time"].duplicated().any():
        raise FundingMaterializationError("funding input contains duplicate timestamps")
    if not prepared["_funding_time"].is_monotonic_increasing:
        raise FundingMaterializationError("funding input timestamps are not sorted")
    return prepared


def materialize_funding_feature(
    *,
    ohlcv_path: Path,
    funding_path: Path,
    availability_catalog_path: Path,
    output_path: Path,
    manifest_path: Path,
    symbol: str = "BTCUSDT",
    parent_catalog_ref: str | None = None,
    parent_slice_identity: str | None = None,
) -> dict[str, Any]:
    """Write a deterministic runner CSV and lineage manifest from local inputs."""
    availability = _availability_entry(availability_catalog_path)
    ohlcv = _prepare_ohlcv(_load_table(ohlcv_path))
    funding = _prepare_funding(_load_table(funding_path), symbol)
    if ohlcv.empty or funding.empty:
        raise FundingMaterializationError("inputs must not be empty")

    first_close = ohlcv["_close_time"].iloc[0]
    last_close = ohlcv["_close_time"].iloc[-1]
    if funding["_funding_time"].iloc[0] > first_close:
        raise FundingMaterializationError("funding history does not cover the first OHLCV bar close")
    relevant = funding.loc[funding["_funding_time"] <= last_close].copy()
    if relevant.empty:
        raise FundingMaterializationError("funding history has no events available in the OHLCV window")

    joined = pd.merge_asof(
        ohlcv.sort_values("_close_time"),
        relevant,
        left_on="_close_time",
        right_on="_funding_time",
        direction="backward",
        allow_exact_matches=True,
    )
    if joined[FEATURE_NAME].isna().any():
        raise FundingMaterializationError("funding alignment produced uncovered OHLCV rows")
    if (joined["_funding_time"] > joined["_close_time"]).any():
        raise FundingMaterializationError("funding alignment violated the no-lookahead boundary")

    output = joined.loc[:, ["timestamp", *OHLCV_COLUMNS, FEATURE_NAME]]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False, lineterminator="\n", float_format="%.12g")

    window_events = relevant.loc[relevant["_funding_time"] >= ohlcv["_open_time"].iloc[0]]
    deltas = window_events["_funding_time"].diff().dropna()
    gaps = [
        {
            "previous_event_utc": _utc_iso(window_events["_funding_time"].iloc[index - 1]),
            "next_event_utc": _utc_iso(window_events["_funding_time"].iloc[index]),
            "delta_hours": float(delta / pd.Timedelta(hours=1)),
        }
        for index, delta in enumerate(deltas, start=1)
        if delta > FUNDING_GAP_THRESHOLD
    ]
    manifest = {
        "materialization_version": MATERIALIZATION_VERSION,
        "symbol": symbol,
        "timeframe": "15m",
        "feature_columns": [FEATURE_NAME],
        "alignment": {
            "rule": "latest funding event timestamp at or before each 15m bar close",
            "carry": "forward until the next observed funding event",
            "no_lookahead": True,
            "uncovered_row_count": 0,
        },
        "coverage": {
            "row_count": len(output),
            "start_utc": output["timestamp"].iloc[0],
            "end_utc": output["timestamp"].iloc[-1],
            "funding_event_count_in_window": len(window_events),
            "gap_threshold": "8h plus 1m timestamp-jitter tolerance",
            "gap_count_over_threshold": len(gaps),
            "gaps_over_threshold": gaps,
        },
        "availability": {
            "coverage_class": availability["coverage_class"],
            "source_class": availability["source_class"],
            "conditions": availability.get("conditions", []),
            "catalog_path": str(availability_catalog_path),
            "catalog_sha256": _sha256(availability_catalog_path),
        },
        "parent_ohlcv": {
            "path": str(ohlcv_path),
            "sha256": _sha256(ohlcv_path),
            "catalog_ref": parent_catalog_ref,
            "data_slice_identity": parent_slice_identity,
        },
        "source_funding": {
            "path": str(funding_path),
            "sha256": _sha256(funding_path),
            "row_count": len(funding),
            "start_utc": _utc_iso(funding["_funding_time"].iloc[0]),
            "end_utc": _utc_iso(funding["_funding_time"].iloc[-1]),
        },
        "output": {
            "path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "sha256": _sha256(output_path),
            "columns": list(output.columns),
            "git_tracking_status": "local_ignored_data",
        },
        "materialization_command": " ".join(
            [
                "python -m tools.data.materialize_funding_feature",
                f'--ohlcv-path "{ohlcv_path}"',
                f'--funding-path "{funding_path}"',
                f'--availability-catalog-path "{availability_catalog_path}"',
                f'--output-path "{output_path}"',
                f'--manifest-path "{manifest_path}"',
                f"--symbol {symbol}",
                *(
                    [f'--parent-catalog-ref "{parent_catalog_ref}"']
                    if parent_catalog_ref is not None
                    else []
                ),
                *(
                    [f'--parent-slice-identity "{parent_slice_identity}"']
                    if parent_slice_identity is not None
                    else []
                ),
            ]
        ),
        "authority": "research-lab feature materialization only; no funding P&L or execution authority",
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ohlcv-path", type=Path, required=True)
    parser.add_argument("--funding-path", type=Path, required=True)
    parser.add_argument("--availability-catalog-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--manifest-path", type=Path, required=True)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--parent-catalog-ref")
    parser.add_argument("--parent-slice-identity")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    manifest = materialize_funding_feature(**vars(args))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
