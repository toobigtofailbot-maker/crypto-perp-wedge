"""
Download BTCUSDT USDT-M mark/index/premium-index kline history with repaired
official-source gaps.

Pipeline:
1. data.binance.vision monthly archive base
2. full historical daily archive overlay, filling only monthly-missing bars
3. targeted Binance REST backfill for bars still missing
4. irreparable official-source gap manifest update
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "BTCUSDT"
VALID_INTERVALS = ["15m", "30m", "1h", "4h", "1d"]
VALID_STREAMS = ["markPriceKlines", "indexPriceKlines", "premiumIndexKlines"]
STREAM_OUTPUT_NAMES = {
    "markPriceKlines": "mark_price",
    "indexPriceKlines": "index_price",
    "premiumIndexKlines": "premium_index",
}
REST_ENDPOINTS = {
    "markPriceKlines": ("/fapi/v1/markPriceKlines", "symbol"),
    "indexPriceKlines": ("/fapi/v1/indexPriceKlines", "pair"),
    "premiumIndexKlines": ("/fapi/v1/premiumIndexKlines", "symbol"),
}
INTERVAL_MS = {
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
}
MONTHLY_BASE = "https://data.binance.vision/data/futures/um/monthly/{stream}/{symbol}/{interval}/"
DAILY_BASE = "https://data.binance.vision/data/futures/um/daily/{stream}/{symbol}/{interval}/"
REST_BASE = "https://fapi.binance.com"
MAX_WORKERS = 4
MAX_RETRIES = 3
REST_SLEEP_S = 0.2
MANIFEST_PATH = REPO_ROOT / "data" / "irreparable_gaps.json"

KLINE_COLS = [
    "open_time_ms", "open", "high", "low", "close", "volume",
    "close_time_ms", "quote_asset_volume", "num_trades",
    "taker_buy_base_vol", "taker_buy_quote_vol", "ignore",
]
FLOAT_COLS = [
    "open", "high", "low", "close", "volume",
    "quote_asset_volume", "taker_buy_base_vol", "taker_buy_quote_vol",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_url(url: str, max_retries: int = MAX_RETRIES, timeout: int = 120) -> bytes:
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            with urlopen(url, timeout=timeout) as resp:
                return resp.read()
        except HTTPError:
            raise
        except URLError as exc:
            last_exc = exc
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    raise last_exc  # type: ignore[misc]


def verify_checksum(zip_data: bytes, checksum_text: str, zip_filename: str) -> None:
    line = checksum_text.strip()
    parts = line.split("  ", 1)
    if len(parts) != 2:
        raise ValueError(f"CHECKSUM MISMATCH: cannot parse checksum file for {zip_filename}: {line!r}")
    expected_hash = parts[0].strip().lower()
    actual_hash = sha256_bytes(zip_data)
    if actual_hash != expected_hash:
        raise ValueError(
            f"CHECKSUM MISMATCH for {zip_filename}\n"
            f"  expected: {expected_hash}\n"
            f"  actual:   {actual_hash}"
        )


def parse_csv_from_zip_bytes(zip_data: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_names:
            raise ValueError("No CSV found in ZIP archive")
        with zf.open(csv_names[0]) as f:
            reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8"))
            return [
                row for row in reader
                if row and not row[0].strip().lower().startswith("open_time")
            ]


def download_and_parse(url: str, zip_filename: str) -> tuple[list[list[str]], bool]:
    try:
        zip_data = fetch_url(url)
    except HTTPError as e:
        if e.code == 404:
            return [], False
        raise

    checksum_data = fetch_url(url + ".CHECKSUM")
    verify_checksum(zip_data, checksum_data.decode("utf-8"), zip_filename)
    return parse_csv_from_zip_bytes(zip_data), True


def months_sequence(from_date: date, until_exclusive: date):
    y, m = from_date.year, from_date.month
    ey, em = until_exclusive.year, until_exclusive.month
    while (y, m) < (ey, em):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def days_sequence(from_date: date, to_date: date):
    d = from_date
    while d <= to_date:
        yield d
        d += timedelta(days=1)


def rows_to_df(rows: list[list[str]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=KLINE_COLS)
    for c in FLOAT_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["num_trades"] = pd.to_numeric(df["num_trades"], errors="coerce").astype("Int64")
    df["open_time_ms"] = pd.to_numeric(df["open_time_ms"], errors="coerce").astype("int64")
    df["close_time_ms"] = pd.to_numeric(df["close_time_ms"], errors="coerce").astype("int64")
    return df


def normalize_rows(rows: list[list[str]]) -> list[dict]:
    if not rows:
        return []
    return rows_to_df(rows).to_dict("records")


def fetch_monthly_batch(stream: str, interval: str, months: list[tuple[int, int]]) -> dict[tuple[int, int], list[dict] | None]:
    base = MONTHLY_BASE.format(stream=stream, symbol=SYMBOL, interval=interval)
    results: dict[tuple[int, int], list[dict] | None] = {}

    def _task(ym: tuple[int, int]) -> tuple[tuple[int, int], list[dict] | None]:
        y, m = ym
        zip_name = f"{SYMBOL}-{interval}-{y:04d}-{m:02d}.zip"
        rows, found = download_and_parse(base + zip_name, zip_name)
        return ym, (normalize_rows(rows) if found else None)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_task, ym): ym for ym in months}
        for fut in as_completed(futures):
            ym, rows = fut.result()
            results[ym] = rows
    return results


def fetch_daily_batch(stream: str, interval: str, days: list[date]) -> dict[date, list[dict] | None]:
    base = DAILY_BASE.format(stream=stream, symbol=SYMBOL, interval=interval)
    results: dict[date, list[dict] | None] = {}

    def _task(d: date) -> tuple[date, list[dict] | None]:
        ds = d.strftime("%Y-%m-%d")
        zip_name = f"{SYMBOL}-{interval}-{ds}.zip"
        rows, found = download_and_parse(base + zip_name, zip_name)
        return d, (normalize_rows(rows) if found else None)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_task, d): d for d in days}
        for fut in as_completed(futures):
            d, rows = fut.result()
            results[d] = rows
    return results


def rest_fetch_window(stream: str, interval: str, start_ms: int, end_ms: int) -> list[dict]:
    endpoint, param_name = REST_ENDPOINTS[stream]
    params = {
        param_name: SYMBOL,
        "interval": interval,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1500,
    }
    url = f"{REST_BASE}{endpoint}?{urlencode(params)}"
    delay = 1.0
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            time.sleep(REST_SLEEP_S)
            data = fetch_url(url, max_retries=0, timeout=30)
            rows = json.loads(data.decode("utf-8"))
            return normalize_rows(rows)
        except HTTPError as exc:
            last_exc = exc
            if exc.code in {418, 429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except URLError as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= 2
                continue
    raise last_exc  # type: ignore[misc]


def find_missing_windows(timestamps: list[int], cadence_ms: int) -> list[dict]:
    windows = []
    for prev_ts, next_ts in zip(timestamps, timestamps[1:]):
        missing_bars = (next_ts - prev_ts) // cadence_ms - 1
        if missing_bars > 0:
            windows.append({
                "start_ms": prev_ts + cadence_ms,
                "end_ms": next_ts - cadence_ms,
                "missing_bars": int(missing_bars),
            })
    return windows


def ms_to_iso(ms_value: int) -> str:
    return datetime.fromtimestamp(ms_value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"schema_version": 1, "updated_utc": utc_now_iso(), "entries": []}


def manifest_key(entry: dict) -> tuple:
    return (entry["stream"], entry["interval"], entry["start_utc"], entry["end_utc"])


def update_manifest(stream: str, interval: str, windows: list[dict]) -> dict:
    manifest = load_manifest()
    existing = {manifest_key(entry): entry for entry in manifest.get("entries", [])}
    verified_utc = utc_now_iso()
    for window in windows:
        entry = {
            "stream": stream,
            "interval": interval,
            "start_utc": ms_to_iso(window["start_ms"]),
            "end_utc": ms_to_iso(window["end_ms"]),
            "missing_bars": int(window["missing_bars"]),
            "verified_utc": verified_utc,
            "sources_checked": ["monthly_archive", "daily_archive", "rest"],
        }
        existing.setdefault(manifest_key(entry), entry)
    entries = sorted(existing.values(), key=lambda e: (e["stream"], e["interval"], e["start_utc"], e["end_utc"]))
    manifest = {"schema_version": 1, "updated_utc": verified_utc, "entries": entries}
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download repaired BTCUSDT USDT-M mark/index/premium-index kline history"
    )
    parser.add_argument("--stream", required=True, choices=VALID_STREAMS)
    parser.add_argument("--interval", required=True, choices=VALID_INTERVALS)
    parser.add_argument("--from", dest="from_date", default="2019-09-08")
    parser.add_argument("--to", dest="to_date", default=None)
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "data" / "processed"))
    args = parser.parse_args()

    from_date = datetime.strptime(args.from_date, "%Y-%m-%d").date()
    to_date = (
        datetime.strptime(args.to_date, "%Y-%m-%d").date()
        if args.to_date
        else datetime.now(timezone.utc).date()
    )
    stream = args.stream
    interval = args.interval
    cadence_ms = INTERVAL_MS[interval]
    stream_output_name = STREAM_OUTPUT_NAMES[stream]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {SYMBOL} {stream} {interval} from {from_date} to {to_date}", flush=True)

    current_month_start = date(to_date.year, to_date.month, 1)
    monthly_months = [
        (y, m) for y, m in months_sequence(from_date, current_month_start)
        if date(y, m, 1) <= to_date
    ]
    print(f"Stage 1 monthly base: {len(monthly_months)} candidate archives", flush=True)
    monthly_results = fetch_monthly_batch(stream, interval, monthly_months)

    rows_by_ts: dict[int, dict] = {}
    monthly_bars = 0
    seen_data = False
    for ym in monthly_months:
        rows = monthly_results[ym]
        if rows is None:
            if seen_data:
                print(f"  monthly {ym[0]:04d}-{ym[1]:02d}: archive unavailable", flush=True)
            else:
                print(f"  monthly {ym[0]:04d}-{ym[1]:02d}: pre-history unavailable", flush=True)
            continue
        seen_data = True
        monthly_bars += len(rows)
        for row in rows:
            row = dict(row)
            row["is_repaired"] = False
            rows_by_ts.setdefault(int(row["open_time_ms"]), row)
        print(f"  monthly {ym[0]:04d}-{ym[1]:02d}: {len(rows)} rows", flush=True)

    daily_days = list(days_sequence(from_date, to_date))
    print(f"Stage 2 daily overlay: {len(daily_days)} candidate archives", flush=True)
    daily_results = fetch_daily_batch(stream, interval, daily_days)
    daily_overlay_bars = 0
    for d in daily_days:
        rows = daily_results[d]
        if rows is None:
            continue
        for row in rows:
            ts = int(row["open_time_ms"])
            if ts not in rows_by_ts:
                row = dict(row)
                row["is_repaired"] = True
                rows_by_ts[ts] = row
                daily_overlay_bars += 1

    if not rows_by_ts:
        print("ERROR: No rows collected from official archives.", file=sys.stderr)
        return 1

    timestamps = sorted(rows_by_ts)
    from_ms = int(datetime(from_date.year, from_date.month, from_date.day, tzinfo=timezone.utc).timestamp() * 1000)
    to_ms = int(datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59, tzinfo=timezone.utc).timestamp() * 1000)
    timestamps = [ts for ts in timestamps if from_ms <= ts <= to_ms]
    rows_by_ts = {ts: rows_by_ts[ts] for ts in timestamps}
    missing_after_daily = find_missing_windows(timestamps, cadence_ms)

    print(f"Stage 3 REST backfill: {len(missing_after_daily)} missing window(s) after daily overlay", flush=True)
    rest_bars = 0
    for window in missing_after_daily:
        rest_rows = rest_fetch_window(stream, interval, window["start_ms"], window["end_ms"])
        for row in rest_rows:
            ts = int(row["open_time_ms"])
            if from_ms <= ts <= to_ms and ts not in rows_by_ts:
                row = dict(row)
                row["is_repaired"] = True
                rows_by_ts[ts] = row
                rest_bars += 1

    timestamps = sorted(rows_by_ts)
    missing_after_rest = find_missing_windows(timestamps, cadence_ms)
    manifest = update_manifest(stream, interval, missing_after_rest)
    irreparable_bars = sum(int(w["missing_bars"]) for w in missing_after_rest)

    df = pd.DataFrame([rows_by_ts[ts] for ts in timestamps])
    for c in KLINE_COLS:
        if c not in df.columns:
            print(f"ERROR: Missing output column {c}", file=sys.stderr)
            return 1
    df = df[KLINE_COLS + ["is_repaired"]]

    actual_start = datetime.fromtimestamp(int(df["open_time_ms"].iloc[0]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    actual_end = datetime.fromtimestamp(int(df["open_time_ms"].iloc[-1]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    out_path = out_dir / (
        f"binance_um_perp_{SYMBOL}_{stream_output_name}_{interval}_"
        f"{actual_start}_{actual_end}_{created_utc}.parquet"
    )
    df.to_parquet(out_path, index=False)
    digest = sha256_file(out_path)

    print(f"\n=== {stream_output_name.upper()} EXPORT OK ===")
    print(f"symbol:              {SYMBOL}")
    print(f"stream:              {stream}")
    print(f"interval:            {interval}")
    print(f"rows:                {len(df)}")
    print(f"range:               {actual_start} / {actual_end}")
    print(f"monthly_bars:        {monthly_bars}")
    print(f"daily_overlay_bars:  {daily_overlay_bars}")
    print(f"rest_bars:           {rest_bars}")
    print(f"irreparable_bars:    {irreparable_bars}")
    print(f"manifest_entries:    {len(manifest.get('entries', []))}")
    print(f"created_utc:         {created_utc}")
    print(f"path:                {out_path}")
    print(f"sha256:              {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
