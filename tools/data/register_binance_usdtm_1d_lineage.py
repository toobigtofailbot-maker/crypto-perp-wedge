"""Validate and register the existing offline BTCUSDT USDT-M 1d snapshot.

This tool is offline-only. It does not fetch market data, read credentials, or
write a dataset. It validates one existing Parquet snapshot and emits a
deterministic lineage/catalog record suitable for later Gate-Q dataset binding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import pandas as pd


PACKAGE_ID = "WP-CANON-H004-DATASET-LINEAGE-01"
DATASET_ID = "binance_usdtm_btcusdt_ohlcv_1d"
SNAPSHOT_VERSION = "2026-04-12T1655Z"
MARKET = "BTCUSDT_BINANCE_USDTM_PERPETUAL"
MARKET_TYPE = "USDT-M perpetual"
SYMBOL = "BTCUSDT"
VENUE = "Binance"
STREAM = "ohlcv"
TIMEFRAME = "1d"
CADENCE_MS = 86_400_000
SNAPSHOT_CUTOFF_UTC = "2026-04-12T16:55:00Z"
EXPECTED_SOURCE_SHA256 = "c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802"
DEFAULT_LOGICAL_PATH = (
    "data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_"
    "2026-04-12T1655Z.parquet"
)
DEFAULT_OUTPUT_PATH = (
    "research/data_slices/binance_usdtm_btcusdt_1d/"
    "binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json"
)
REQUIRED_COLUMNS = [
    "open_time_ms",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time_ms",
    "quote_asset_volume",
    "num_trades",
    "taker_buy_base_vol",
    "taker_buy_quote_vol",
    "ignore",
]
NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_asset_volume",
    "num_trades",
    "taker_buy_base_vol",
    "taker_buy_quote_vol",
]


class LineageError(RuntimeError):
    """Raised when the local snapshot cannot satisfy the lineage contract."""


@dataclass(frozen=True)
class RegistrationResult:
    ok: bool
    output_path: str
    dataset_id: str
    snapshot_version: str
    dataset_path: str
    sha256: str
    row_count: int
    coverage_start_utc: str
    coverage_end_utc: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _iso_from_ms(value: int) -> str:
    return pd.to_datetime(value, unit="ms", utc=True).isoformat().replace("+00:00", "Z")


def _cutoff_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LineageError("snapshot cutoff must be timezone-aware")
    return int(parsed.timestamp() * 1000)


def _logical_repo_path(value: str) -> str:
    logical = PurePosixPath(value.replace("\\", "/"))
    if logical.is_absolute() or ".." in logical.parts:
        raise LineageError("logical dataset path must be a repository-relative path")
    return logical.as_posix()


def _integer_series(frame: pd.DataFrame, column: str) -> pd.Series:
    values = pd.to_numeric(frame[column], errors="raise")
    if values.isna().any() or ((values % 1) != 0).any():
        raise LineageError(f"{column} must contain non-null integer values")
    return values.astype("int64")


def _numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    values = pd.to_numeric(frame[column], errors="raise")
    if values.isna().any():
        raise LineageError(f"{column} contains null values")
    finite = values.map(lambda value: bool(pd.notna(value)) and float(value) not in {float("inf"), float("-inf")})
    if not finite.all():
        raise LineageError(f"{column} contains non-finite values")
    return values


def build_lineage(
    source_path: Path,
    *,
    logical_path: str = DEFAULT_LOGICAL_PATH,
    expected_sha256: str = EXPECTED_SOURCE_SHA256,
    snapshot_cutoff_utc: str = SNAPSHOT_CUTOFF_UTC,
) -> dict[str, Any]:
    if not source_path.is_file():
        raise LineageError(f"source snapshot does not exist: {source_path}")
    if source_path.suffix.lower() != ".parquet":
        raise LineageError("source snapshot must be a Parquet file")

    logical_path = _logical_repo_path(logical_path)
    actual_sha256 = sha256_file(source_path)
    if actual_sha256 != expected_sha256:
        raise LineageError(
            f"whole-file checksum mismatch: expected {expected_sha256}, observed {actual_sha256}"
        )

    frame = pd.read_parquet(source_path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    unexpected_columns = sorted(set(frame.columns) - set(REQUIRED_COLUMNS))
    if missing_columns or unexpected_columns:
        raise LineageError(
            f"column contract mismatch: missing={missing_columns}, unexpected={unexpected_columns}"
        )
    if list(frame.columns) != REQUIRED_COLUMNS:
        raise LineageError("column ordering does not match the registered snapshot contract")
    if frame.empty:
        raise LineageError("source snapshot is empty")
    if frame[REQUIRED_COLUMNS].isna().any().any():
        raise LineageError("source snapshot contains null values")

    open_time_ms = _integer_series(frame, "open_time_ms")
    close_time_ms = _integer_series(frame, "close_time_ms")
    numeric = {column: _numeric_series(frame, column) for column in NUMERIC_COLUMNS}

    duplicate_mask = open_time_ms.duplicated(keep=False)
    duplicate_row_count = int(duplicate_mask.sum())
    duplicate_group_count = int(open_time_ms[duplicate_mask].nunique())
    if duplicate_row_count:
        raise LineageError(
            f"duplicate daily open_time values detected: {duplicate_row_count} rows in "
            f"{duplicate_group_count} groups"
        )

    deltas = open_time_ms.diff().dropna()
    if not open_time_ms.is_monotonic_increasing or (deltas <= 0).any():
        raise LineageError("daily bars must be strictly sorted by open_time_ms")
    unexpected_deltas = deltas[deltas != CADENCE_MS]
    if not unexpected_deltas.empty:
        missing_bar_count = sum(max(int(delta // CADENCE_MS) - 1, 0) for delta in unexpected_deltas)
        raise LineageError(
            f"daily cadence gap detected: {len(unexpected_deltas)} intervals, "
            f"{missing_bar_count} missing bars"
        )
    if (open_time_ms % CADENCE_MS != 0).any():
        raise LineageError("open_time_ms values must align to 00:00:00 UTC daily boundaries")
    if (close_time_ms != open_time_ms + CADENCE_MS - 1).any():
        raise LineageError("close_time_ms must equal open_time_ms + 1d - 1ms")

    malformed_ohlc = (
        (numeric["high"] < numeric["open"])
        | (numeric["high"] < numeric["close"])
        | (numeric["high"] < numeric["low"])
        | (numeric["low"] > numeric["open"])
        | (numeric["low"] > numeric["close"])
    )
    if malformed_ohlc.any():
        raise LineageError(f"malformed OHLC rows detected: {int(malformed_ohlc.sum())}")
    for column in [
        "volume",
        "quote_asset_volume",
        "num_trades",
        "taker_buy_base_vol",
        "taker_buy_quote_vol",
    ]:
        if (numeric[column] < 0).any():
            raise LineageError(f"negative {column} values detected")

    cutoff_ms = _cutoff_ms(snapshot_cutoff_utc)
    open_bar_count = int((close_time_ms >= cutoff_ms).sum())
    if open_bar_count:
        raise LineageError(
            f"snapshot includes {open_bar_count} bars not completed before {snapshot_cutoff_utc}"
        )

    row_count = int(len(frame))
    expected_row_count = int((open_time_ms.iloc[-1] - open_time_ms.iloc[0]) // CADENCE_MS + 1)
    if row_count != expected_row_count:
        raise LineageError(
            f"row count {row_count} does not match inclusive daily coverage {expected_row_count}"
        )

    coverage_start_utc = _iso_from_ms(int(open_time_ms.iloc[0]))
    coverage_end_utc = _iso_from_ms(int(open_time_ms.iloc[-1]))
    coverage_end_close_utc = _iso_from_ms(int(close_time_ms.iloc[-1]))
    checksum = f"sha256:{actual_sha256}"
    gate_q_dataset = {
        "dataset_id": DATASET_ID,
        "market": MARKET,
        "path": logical_path,
        "sha256": checksum,
        "snapshot_version": SNAPSHOT_VERSION,
        "timeframe": TIMEFRAME,
        "unresolved_policy": "reject",
    }

    return {
        "boundary": {
            "credentials_used": False,
            "network_access_used_by_this_package": False,
            "no_candidate_change": True,
            "no_execution_or_result_population_change": True,
            "no_gate_q_or_queue_change": True,
            "no_oms_risk_or_reconciliation_change": True,
            "no_paper_live_or_runtime_change": True,
        },
        "catalog_status": "valid_offline_provenance_tracked_snapshot",
        "catalog_version": "h004-r2-btcusdt-1d-lineage-v1",
        "consumer_requirement": {
            "completed_1d_ohlcv_only": True,
            "strategy_spec_id": "STRAT-SPEC-0007",
            "strategy_source_requirement": "BTCUSDT Binance USDT-M perpetual; completed 1d OHLCV only",
        },
        "coverage": {
            "end_close_utc": coverage_end_close_utc,
            "end_open_utc": coverage_end_utc,
            "expected_row_count": expected_row_count,
            "row_count": row_count,
            "start_open_utc": coverage_start_utc,
        },
        "dataset_id": DATASET_ID,
        "findings": {
            "close_time_rule_violation_count": 0,
            "duplicate_group_count": duplicate_group_count,
            "duplicate_policy": "reject_without_deduplication",
            "duplicate_row_count": duplicate_row_count,
            "gap_count": 0,
            "gap_policy": "reject_without_fill_or_interpolation",
            "malformed_ohlc_row_count": 0,
            "missing_bar_count": 0,
            "negative_volume_row_count": 0,
            "open_or_incomplete_bar_count": open_bar_count,
            "utc_boundary_alignment_violation_count": 0,
        },
        "gate_q_dataset": gate_q_dataset,
        "market": MARKET,
        "market_type": MARKET_TYPE,
        "normalization": {
            "completed_bar_policy": (
                f"include only rows with close_time_ms before {snapshot_cutoff_utc}; "
                "the 2026-04-12 open daily bar is excluded"
            ),
            "current_registration_mutates_dataset": False,
            "current_registration_policy": (
                "validate exact existing Parquet bytes; require canonical column order, strictly "
                "ascending UTC daily opens, exact close times, valid OHLC, and non-negative volumes"
            ),
            "producer_duplicate_policy": (
                "scripts/fetch_btcusdt_klines_bulk.py drop_duplicates(open_time_ms, keep=first); "
                "this lineage makes no claim about pre-export archive duplicates"
            ),
            "producer_normalization": (
                "parse Binance kline columns, coerce numeric fields, sort by open_time_ms, "
                "filter the explicit UTC date window, and serialize Parquet with index=false"
            ),
            "silent_fill_or_interpolation": False,
        },
        "package_id": PACKAGE_ID,
        "path": logical_path,
        "sha256": checksum,
        "snapshot_version": SNAPSHOT_VERSION,
        "source": {
            "archive_checksum_policy": (
                "verify each data.binance.vision .CHECKSUM when present; the producer warns and "
                "continues for legacy archives without a checksum file"
            ),
            "credentials_used": False,
            "endpoint_templates": [
                "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/{interval}/",
                "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/{interval}/",
            ],
            "method": "existing local public archive snapshot; no fetch performed by this package",
            "documented_invocation": "python scripts/fetch_btcusdt_klines_bulk.py --interval 1d",
            "parameters": {
                "from": "2019-09-08 (producer default; earliest available bar is 2020-01-01)",
                "interval": "1d",
                "output_dir": "data/processed (producer default)",
                "symbol": SYMBOL,
                "to": "2026-04-12 (UTC execution-date default; last available completed bar is 2026-04-11)",
            },
            "producer": "scripts/fetch_btcusdt_klines_bulk.py",
            "public_private_classification": "public market data",
            "source_file_sha256": checksum,
        },
        "stream": STREAM,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "unresolved_policy": "reject",
        "venue": VENUE,
    }


def write_lineage(
    source_path: Path,
    output_path: Path,
    *,
    logical_path: str = DEFAULT_LOGICAL_PATH,
    expected_sha256: str = EXPECTED_SOURCE_SHA256,
    snapshot_cutoff_utc: str = SNAPSHOT_CUTOFF_UTC,
) -> RegistrationResult:
    lineage = build_lineage(
        source_path,
        logical_path=logical_path,
        expected_sha256=expected_sha256,
        snapshot_cutoff_utc=snapshot_cutoff_utc,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(canonical_json_bytes(lineage))
    return RegistrationResult(
        ok=True,
        output_path=str(output_path),
        dataset_id=DATASET_ID,
        snapshot_version=SNAPSHOT_VERSION,
        dataset_path=lineage["path"],
        sha256=lineage["sha256"],
        row_count=lineage["coverage"]["row_count"],
        coverage_start_utc=lineage["coverage"]["start_open_utc"],
        coverage_end_utc=lineage["coverage"]["end_close_utc"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing local Parquet snapshot.")
    parser.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--logical-path", default=DEFAULT_LOGICAL_PATH)
    parser.add_argument("--expected-sha256", default=EXPECTED_SOURCE_SHA256)
    parser.add_argument("--snapshot-cutoff-utc", default=SNAPSHOT_CUTOFF_UTC)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = write_lineage(
            args.input,
            args.output,
            logical_path=args.logical_path,
            expected_sha256=args.expected_sha256,
            snapshot_cutoff_utc=args.snapshot_cutoff_utc,
        )
    except (LineageError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "ok": False}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
