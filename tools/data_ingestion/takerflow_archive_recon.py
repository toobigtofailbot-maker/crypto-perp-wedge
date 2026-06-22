"""Reconstruct UTC taker-flow bars from local Binance USD-M trade archives.

The tool is deliberately offline. It accepts local CSV files or ZIP archives
containing one CSV member and writes a lineage-tracked JSON slice. It has no
download, REST, credential, runtime, or canonical research-artifact path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


TOOL_VERSION = "takerflow-archive-recon-v1"
COVERAGE_CLASS = "FULL_HISTORY_PUBLIC_ARCHIVE"
MARKET_TYPE = "USD-M perpetual"
SOURCE_ARCHIVE_TYPES = {"trades", "aggTrades"}
FEATURE_FIELDS = (
    "taker_buy_base_volume",
    "taker_sell_base_volume",
    "taker_net_base_volume",
    "taker_total_base_volume",
    "taker_buy_sell_ratio",
    "trade_count",
)
QUOTE_FEATURE_FIELDS = (
    "taker_buy_quote_volume",
    "taker_sell_quote_volume",
    "taker_net_quote_volume",
    "taker_total_quote_volume",
)

TRADES_COLUMNS = (
    "trade_id",
    "price",
    "qty",
    "quote_qty",
    "time",
    "is_buyer_maker",
)
AGGTRADES_COLUMNS = (
    "agg_trade_id",
    "price",
    "quantity",
    "first_trade_id",
    "last_trade_id",
    "transact_time",
    "is_buyer_maker",
)


class TakerflowArchiveError(RuntimeError):
    """Raised when archive parsing, aggregation, or validation fails closed."""


@dataclass(frozen=True)
class TradeRow:
    event_id: int
    timestamp_ms: int
    price: Decimal
    base_quantity: Decimal
    quote_quantity: Decimal | None
    buyer_maker: bool
    trade_count: int


def _decimal(value: Any, field: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise TakerflowArchiveError(f"row {row_number}: {field} is not a decimal") from exc
    if not parsed.is_finite() or parsed < 0:
        raise TakerflowArchiveError(f"row {row_number}: {field} must be finite and non-negative")
    return parsed


def _integer(value: Any, field: str, row_number: int, *, positive: bool = False) -> int:
    text = str(value).strip()
    if not re.fullmatch(r"-?\d+", text):
        raise TakerflowArchiveError(f"row {row_number}: {field} is not an integer")
    parsed = int(text)
    if (positive and parsed <= 0) or (not positive and parsed < 0):
        qualifier = "positive" if positive else "non-negative"
        raise TakerflowArchiveError(f"row {row_number}: {field} must be {qualifier}")
    return parsed


def _boolean(value: Any, field: str, row_number: int) -> bool:
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise TakerflowArchiveError(f"row {row_number}: {field} must be true or false")


def _read_archive_text(path: Path) -> str:
    if not path.is_file():
        raise TakerflowArchiveError(f"archive path is not a file: {path}")
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                members = [
                    name
                    for name in archive.namelist()
                    if not name.endswith("/") and name.lower().endswith(".csv")
                ]
                if len(members) != 1:
                    raise TakerflowArchiveError("ZIP archive must contain exactly one CSV member")
                return archive.read(members[0]).decode("utf-8-sig")
        except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
            raise TakerflowArchiveError(f"cannot read ZIP archive: {path}") from exc
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise TakerflowArchiveError(f"archive CSV is not UTF-8: {path}") from exc


def _canonical_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _csv_rows(path: Path, required_columns: tuple[str, ...]) -> list[dict[str, str]]:
    text = _read_archive_text(path)
    raw_rows = list(csv.reader(io.StringIO(text)))
    if not raw_rows:
        raise TakerflowArchiveError("archive contains no rows")
    first = tuple(_canonical_header(value) for value in raw_rows[0])
    has_header = set(required_columns).issubset(first)
    if has_header:
        header = first
        data_rows = raw_rows[1:]
    else:
        header = required_columns
        data_rows = raw_rows
    if len(header) != len(required_columns) or set(header) != set(required_columns):
        missing = sorted(set(required_columns) - set(header))
        unexpected = sorted(set(header) - set(required_columns))
        raise TakerflowArchiveError(
            "archive columns do not match required schema; "
            f"missing={missing}, unexpected={unexpected}"
        )
    records: list[dict[str, str]] = []
    for row_number, values in enumerate(data_rows, start=2 if has_header else 1):
        if not values or all(not value.strip() for value in values):
            raise TakerflowArchiveError(f"row {row_number}: blank rows are not accepted")
        if len(values) != len(header):
            raise TakerflowArchiveError(
                f"row {row_number}: expected {len(header)} columns, found {len(values)}"
            )
        records.append(dict(zip(header, values, strict=True)))
    if not records:
        raise TakerflowArchiveError("archive contains no data rows")
    return records


def parse_binance_um_trade_archive(path: str | Path) -> list[TradeRow]:
    """Parse an official USD-M ``trades`` CSV/ZIP archive."""

    rows: list[TradeRow] = []
    for row_number, raw in enumerate(_csv_rows(Path(path), TRADES_COLUMNS), start=2):
        price = _decimal(raw["price"], "price", row_number)
        quantity = _decimal(raw["qty"], "qty", row_number)
        quote_quantity = _decimal(raw["quote_qty"], "quote_qty", row_number)
        if price <= 0 or quantity <= 0:
            raise TakerflowArchiveError(f"row {row_number}: price and qty must be positive")
        rows.append(
            TradeRow(
                event_id=_integer(raw["trade_id"], "trade_id", row_number),
                timestamp_ms=_integer(raw["time"], "time", row_number, positive=True),
                price=price,
                base_quantity=quantity,
                quote_quantity=quote_quantity,
                buyer_maker=_boolean(raw["is_buyer_maker"], "is_buyer_maker", row_number),
                trade_count=1,
            )
        )
    return rows


def parse_binance_um_aggtrade_archive(path: str | Path) -> list[TradeRow]:
    """Parse an official USD-M ``aggTrades`` CSV/ZIP archive."""

    rows: list[TradeRow] = []
    for row_number, raw in enumerate(_csv_rows(Path(path), AGGTRADES_COLUMNS), start=2):
        price = _decimal(raw["price"], "price", row_number)
        quantity = _decimal(raw["quantity"], "quantity", row_number)
        first_trade_id = _integer(raw["first_trade_id"], "first_trade_id", row_number)
        last_trade_id = _integer(raw["last_trade_id"], "last_trade_id", row_number)
        if price <= 0 or quantity <= 0:
            raise TakerflowArchiveError(f"row {row_number}: price and quantity must be positive")
        if last_trade_id < first_trade_id:
            raise TakerflowArchiveError(f"row {row_number}: last_trade_id precedes first_trade_id")
        rows.append(
            TradeRow(
                event_id=_integer(raw["agg_trade_id"], "agg_trade_id", row_number),
                timestamp_ms=_integer(
                    raw["transact_time"], "transact_time", row_number, positive=True
                ),
                price=price,
                base_quantity=quantity,
                quote_quantity=None,
                buyer_maker=_boolean(raw["is_buyer_maker"], "is_buyer_maker", row_number),
                trade_count=last_trade_id - first_trade_id + 1,
            )
        )
    return rows


def derive_taker_side(row: TradeRow | dict[str, Any]) -> str:
    """Map Binance buyer-maker semantics to the aggressor/taker side."""

    buyer_maker = row.buyer_maker if isinstance(row, TradeRow) else row.get("buyer_maker")
    if not isinstance(buyer_maker, bool):
        raise TakerflowArchiveError("buyer_maker must be boolean")
    return "sell" if buyer_maker else "buy"


def _interval_ms(interval: str) -> int:
    match = re.fullmatch(r"([1-9]\d*)([mhd])", interval)
    if not match:
        raise TakerflowArchiveError(
            "interval must be a positive UTC duration such as 15m, 1h, or 1d"
        )
    multiplier = {"m": 60_000, "h": 3_600_000, "d": 86_400_000}[match.group(2)]
    return int(match.group(1)) * multiplier


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _iso_ms(timestamp_ms: int) -> str:
    return (
        datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def aggregate_takerflow_to_bars(
    rows: Iterable[TradeRow], interval: str, timezone: str = "UTC"
) -> list[dict[str, Any]]:
    """Aggregate rows into UTC bar-open intervals without filling missing bars."""

    if timezone != "UTC":
        raise TakerflowArchiveError("only UTC aggregation is supported")
    interval_ms = _interval_ms(interval)
    ordered = sorted(rows, key=lambda row: (row.timestamp_ms, row.event_id))
    if not ordered:
        raise TakerflowArchiveError("cannot aggregate an empty row set")
    include_quote = all(row.quote_quantity is not None for row in ordered)
    groups: dict[int, dict[str, Any]] = {}
    for row in ordered:
        bar_open_ms = row.timestamp_ms - (row.timestamp_ms % interval_ms)
        group = groups.setdefault(
            bar_open_ms,
            {
                "buy_base": Decimal(0),
                "sell_base": Decimal(0),
                "buy_quote": Decimal(0),
                "sell_quote": Decimal(0),
                "trade_count": 0,
            },
        )
        side = derive_taker_side(row)
        group[f"{side}_base"] += row.base_quantity
        if include_quote:
            group[f"{side}_quote"] += row.quote_quantity or Decimal(0)
        group["trade_count"] += row.trade_count

    bars: list[dict[str, Any]] = []
    for bar_open_ms in sorted(groups):
        group = groups[bar_open_ms]
        buy_base = group["buy_base"]
        sell_base = group["sell_base"]
        bar: dict[str, Any] = {
            "open_time_ms": bar_open_ms,
            "open_time": _iso_ms(bar_open_ms),
            "taker_buy_base_volume": _decimal_text(buy_base),
            "taker_sell_base_volume": _decimal_text(sell_base),
            "taker_net_base_volume": _decimal_text(buy_base - sell_base),
            "taker_total_base_volume": _decimal_text(buy_base + sell_base),
            "taker_buy_sell_ratio": None if sell_base == 0 else _decimal_text(buy_base / sell_base),
            "trade_count": group["trade_count"],
        }
        if include_quote:
            buy_quote = group["buy_quote"]
            sell_quote = group["sell_quote"]
            bar.update(
                {
                    "taker_buy_quote_volume": _decimal_text(buy_quote),
                    "taker_sell_quote_volume": _decimal_text(sell_quote),
                    "taker_net_quote_volume": _decimal_text(buy_quote - sell_quote),
                    "taker_total_quote_volume": _decimal_text(buy_quote + sell_quote),
                }
            )
        bars.append(bar)
    return bars


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def build_lineage(
    source_archive_path: str | Path,
    source_archive_type: str,
    symbol: str,
    interval: str,
    rows: Iterable[TradeRow],
    bars: list[dict[str, Any]],
    *,
    generation_time: str | None = None,
    coverage_class: str = COVERAGE_CLASS,
) -> dict[str, Any]:
    """Build fail-closed public-archive lineage for a reconstructed slice."""

    path = Path(source_archive_path)
    materialized_rows = list(rows)
    _interval_ms(interval)
    if source_archive_type not in SOURCE_ARCHIVE_TYPES:
        raise TakerflowArchiveError("source_archive_type must be trades or aggTrades")
    if coverage_class != COVERAGE_CLASS:
        raise TakerflowArchiveError("recent-only REST is not accepted as a historical source")
    if not re.fullmatch(r"[A-Z0-9_-]+", symbol):
        raise TakerflowArchiveError("symbol must be uppercase exchange notation")
    if not materialized_rows or not bars:
        raise TakerflowArchiveError("lineage requires non-empty source rows and bars")
    generated = generation_time or (
        datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    )
    try:
        parsed_generation = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TakerflowArchiveError("generation_time must be an ISO-8601 timestamp") from exc
    if (
        parsed_generation.tzinfo is None
        or parsed_generation.utcoffset() != UTC.utcoffset(parsed_generation)
    ):
        raise TakerflowArchiveError("generation_time must be UTC")
    return {
        "source_archive_path": str(path.resolve()),
        "source_archive_type": source_archive_type,
        "symbol": symbol,
        "market_type": MARKET_TYPE,
        "interval": interval,
        "start_time": bars[0]["open_time"],
        "end_time": bars[-1]["open_time"],
        "source_event_start_time": _iso_ms(min(row.timestamp_ms for row in materialized_rows)),
        "source_event_end_time": _iso_ms(max(row.timestamp_ms for row in materialized_rows)),
        "row_count": len(bars),
        "source_row_count": len(materialized_rows),
        "archive_file_hash": _sha256(path),
        "tool_version": TOOL_VERSION,
        "generation_time": generated,
        "coverage_class": COVERAGE_CLASS,
        "source_public": True,
        "private_endpoint_used": False,
        "network_used": False,
        "bar_timestamp_convention": "UTC interval open",
        "bar_interval_membership": "[open_time, open_time + interval)",
        "fill_policy": "no fill, backfill, or interpolation",
    }


def _validate_decimal_relation(bar: dict[str, Any], prefix: str) -> None:
    buy = Decimal(str(bar[f"taker_buy_{prefix}_volume"]))
    sell = Decimal(str(bar[f"taker_sell_{prefix}_volume"]))
    net = Decimal(str(bar[f"taker_net_{prefix}_volume"]))
    total = Decimal(str(bar[f"taker_total_{prefix}_volume"]))
    if buy < 0 or sell < 0 or net != buy - sell or total != buy + sell:
        raise TakerflowArchiveError(f"invalid {prefix}-volume arithmetic")


def validate_takerflow_slice(path: str | Path) -> dict[str, Any]:
    """Validate a written taker-flow slice and return its payload."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TakerflowArchiveError(f"cannot read taker-flow slice: {path}") from exc
    if (
        set(payload) != {"slice_type", "lineage", "data"}
        or payload["slice_type"] != "takerflow_archive_reconstruction_v1"
    ):
        raise TakerflowArchiveError("slice envelope is invalid")
    lineage = payload["lineage"]
    data = payload["data"]
    required_lineage = {
        "source_archive_path",
        "source_archive_type",
        "symbol",
        "market_type",
        "interval",
        "start_time",
        "end_time",
        "row_count",
        "archive_file_hash",
        "tool_version",
        "generation_time",
        "coverage_class",
        "source_public",
        "private_endpoint_used",
    }
    missing = sorted(required_lineage - set(lineage))
    if missing:
        raise TakerflowArchiveError(f"lineage fields missing: {missing}")
    if lineage["source_archive_type"] not in SOURCE_ARCHIVE_TYPES:
        raise TakerflowArchiveError("slice source is not a supported archive type")
    if lineage["coverage_class"] != COVERAGE_CLASS:
        raise TakerflowArchiveError("slice is not full-history public-archive class")
    if lineage["source_public"] is not True or lineage["private_endpoint_used"] is not False:
        raise TakerflowArchiveError("slice violates public/private source boundary")
    if lineage["market_type"] != MARKET_TYPE or lineage["row_count"] != len(data) or not data:
        raise TakerflowArchiveError("slice lineage does not match data rows")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", lineage["archive_file_hash"]):
        raise TakerflowArchiveError("archive_file_hash must be a SHA256 digest")
    source_path = Path(lineage["source_archive_path"])
    if source_path.is_file() and _sha256(source_path) != lineage["archive_file_hash"]:
        raise TakerflowArchiveError("source archive hash does not match lineage")
    try:
        generated = datetime.fromisoformat(lineage["generation_time"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise TakerflowArchiveError("generation_time must be an ISO-8601 timestamp") from exc
    if generated.tzinfo is None or generated.utcoffset() != UTC.utcoffset(generated):
        raise TakerflowArchiveError("generation_time must be UTC")
    interval_ms = _interval_ms(lineage["interval"])
    previous: int | None = None
    for bar in data:
        missing_features = sorted(set(FEATURE_FIELDS) - set(bar))
        if missing_features:
            raise TakerflowArchiveError(f"bar feature fields missing: {missing_features}")
        open_time_ms = _integer(bar.get("open_time_ms"), "open_time_ms", 0)
        if open_time_ms % interval_ms != 0 or (previous is not None and open_time_ms <= previous):
            raise TakerflowArchiveError("bar timestamps must be aligned and strictly increasing")
        if bar.get("open_time") != _iso_ms(open_time_ms):
            raise TakerflowArchiveError("open_time and open_time_ms disagree")
        previous = open_time_ms
        _validate_decimal_relation(bar, "base")
        sell = Decimal(str(bar["taker_sell_base_volume"]))
        expected_ratio = None if sell == 0 else _decimal_text(
            Decimal(str(bar["taker_buy_base_volume"])) / sell
        )
        if bar["taker_buy_sell_ratio"] != expected_ratio:
            raise TakerflowArchiveError("taker_buy_sell_ratio is inconsistent")
        quote_presence = [field in bar for field in QUOTE_FEATURE_FIELDS]
        if any(quote_presence) and not all(quote_presence):
            raise TakerflowArchiveError("quote-volume features must be all present or all absent")
        if all(quote_presence):
            _validate_decimal_relation(bar, "quote")
        if not isinstance(bar["trade_count"], int) or bar["trade_count"] <= 0:
            raise TakerflowArchiveError("trade_count must be a positive integer")
    if (
        lineage["start_time"] != data[0]["open_time"]
        or lineage["end_time"] != data[-1]["open_time"]
    ):
        raise TakerflowArchiveError("lineage time range does not match data")
    return payload


def write_takerflow_slice(
    output_path: str | Path,
    data: list[dict[str, Any]],
    lineage: dict[str, Any],
) -> Path:
    """Write stable JSON and validate it before leaving an output artifact."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "slice_type": "takerflow_archive_reconstruction_v1",
        "lineage": lineage,
        "data": data,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        validate_takerflow_slice(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return output


def reconstruct_archive(
    source_archive_path: str | Path,
    source_archive_type: str,
    output_path: str | Path,
    symbol: str,
    interval: str,
    *,
    generation_time: str | None = None,
) -> Path:
    parser = {
        "trades": parse_binance_um_trade_archive,
        "aggTrades": parse_binance_um_aggtrade_archive,
    }.get(source_archive_type)
    if parser is None:
        raise TakerflowArchiveError("source_archive_type must be trades or aggTrades")
    rows = parser(source_archive_path)
    bars = aggregate_takerflow_to_bars(rows, interval)
    lineage = build_lineage(
        source_archive_path,
        source_archive_type,
        symbol,
        interval,
        rows,
        bars,
        generation_time=generation_time,
    )
    return write_takerflow_slice(output_path, bars, lineage)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, required=True, help="Local Binance CSV or ZIP archive"
    )
    parser.add_argument("--archive-type", choices=sorted(SOURCE_ARCHIVE_TYPES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", required=True)
    parser.add_argument(
        "--generation-time",
        help="Optional fixed UTC ISO timestamp for reproducible lineage",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = reconstruct_archive(
            args.input,
            args.archive_type,
            args.output,
            args.symbol,
            args.interval,
            generation_time=args.generation_time,
        )
    except TakerflowArchiveError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"ok": True, "output": str(output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
