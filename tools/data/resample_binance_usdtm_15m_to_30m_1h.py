"""Derive canonical 30m or 1h BTCUSDT OHLCV from the canonical D4 15m CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


SYMBOL = "BTCUSDT"
VENUE = "Binance"
MARKET_TYPE = "USDT-M perpetual"
STREAM = "ohlcv"
SOURCE_TYPE = "derived_offline_resample"
PARENT_TIMEFRAME = "15m"
PARENT_DATASET_ID = "binance_usdtm_btcusdt_ohlcv_15m"
PARENT_CADENCE_MS = 15 * 60 * 1000
PARENT_ROW_COUNT = 220_128
PARENT_START_UTC = "2020-01-01T00:00:00Z"
PARENT_END_UTC = "2026-04-11T23:45:00Z"
PARENT_NORMALIZED_SHA256 = "c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab"
PARENT_VALIDATION_SHA256 = "785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c"
PARENT_DATA_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)
PACKAGE_ID = "WP-FT-01-CANONICAL-30M-1H-LINEAGE-RUNNER-ROUTES-01"

OUTPUT_COLUMNS = [
    "open_time_ms",
    "open_time",
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

AGGREGATION_MAP = {
    "open_time_ms": "first",
    "open_time": "first",
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
    "close_time_ms": "last_15m_close_time_ms",
    "quote_asset_volume": "sum",
    "num_trades": "sum",
    "taker_buy_base_vol": "sum",
    "taker_buy_quote_vol": "sum",
    "ignore": "sum_numeric",
}

DEFAULT_PARENT_CSV = Path(
    "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
)
DEFAULT_PARENT_CATALOG = Path(
    "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
)
DEFAULT_PARENT_VALIDATION = Path(
    "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json"
)


@dataclass(frozen=True)
class TargetConfig:
    timeframe: str
    dataset_id: str
    group_size: int
    cadence_ms: int
    expected_row_count: int
    expected_start_utc: str
    expected_end_utc: str
    data_contract_version: str
    resampling_version: str
    validator_version: str
    catalog_version: str
    slice_identity_version: str
    output_csv: Path
    validation_report: Path
    derivation_report: Path
    catalog_slice: Path


def _target(
    timeframe: str,
    *,
    group_size: int,
    cadence_ms: int,
    expected_row_count: int,
    expected_end_utc: str,
) -> TargetConfig:
    family = f"binance_usdtm_btcusdt_{timeframe}"
    stem = f"{family}_20200101_20260411"
    return TargetConfig(
        timeframe=timeframe,
        dataset_id=f"binance_usdtm_btcusdt_ohlcv_{timeframe}",
        group_size=group_size,
        cadence_ms=cadence_ms,
        expected_row_count=expected_row_count,
        expected_start_utc=PARENT_START_UTC,
        expected_end_utc=expected_end_utc,
        data_contract_version=f"2026-10-binance-usdtm-{timeframe}-derived-contract-v1",
        resampling_version=f"wp-ft-01-{timeframe}-resample-v1",
        validator_version=f"wp-ft-01-{timeframe}-validator-v1",
        catalog_version=f"wp-ft-01-{timeframe}-catalog-v1",
        slice_identity_version=(
            f"binance-usdtm-btcusdt-ohlcv-{timeframe}-derived-slice-identity-v1"
        ),
        output_csv=Path(
            f"data/processed/d4_{timeframe}/"
            f"binance_um_perp_BTCUSDT_{timeframe}_2020-01-01_2026-04-11_d4_resampled.csv"
        ),
        validation_report=Path(
            f"research/data_slices/{family}/{stem}.validation_report.json"
        ),
        derivation_report=Path(
            f"research/data_slices/{family}/{stem}.derivation_report.json"
        ),
        catalog_slice=Path(f"research/data_slices/{family}/{stem}.catalog_slice.json"),
    )


TARGETS: Mapping[str, TargetConfig] = MappingProxyType(
    {
        "30m": _target(
            "30m",
            group_size=2,
            cadence_ms=30 * 60 * 1000,
            expected_row_count=110_064,
            expected_end_utc="2026-04-11T23:30:00Z",
        ),
        "1h": _target(
            "1h",
            group_size=4,
            cadence_ms=60 * 60 * 1000,
            expected_row_count=55_032,
            expected_end_utc="2026-04-11T23:00:00Z",
        ),
    }
)


class ResampleError(RuntimeError):
    """Raised when a canonical target cannot be derived exactly."""


@dataclass(frozen=True)
class ResampleResult:
    ok: bool
    target: str
    output_csv_path: str
    output_csv_sha256: str
    validation_report_path: str
    validation_report_sha256: str
    derivation_report_path: str
    derivation_report_sha256: str
    catalog_path: str
    catalog_sha256: str
    data_slice_identity: str
    row_count: int
    expected_row_count: int
    start_utc: str
    end_utc: str


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _identity_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _hash_file(path: Path) -> str:
    if not path.is_file():
        raise ResampleError(f"file does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_text(path: Path) -> str:
    return path.as_posix()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(encoded)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ResampleError(f"cannot read JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ResampleError(f"JSON payload must be an object: {path}")
    return payload


def _iso_from_ms(value: int) -> str:
    return (
        datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _decimal(value: str, label: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ResampleError(f"row {row_number}: {label} contains non-numeric value") from exc
    if not parsed.is_finite():
        raise ResampleError(f"row {row_number}: {label} contains non-finite value")
    return parsed


def _integer(value: str, label: str, row_number: int) -> int:
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ResampleError(f"row {row_number}: {label} contains non-integer value") from exc


def _decimal_string(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal(1)))
    return format(value.normalize(), "f")


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ResampleError(f"file does not exist: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != OUTPUT_COLUMNS:
            raise ResampleError(f"15m CSV columns must exactly match {OUTPUT_COLUMNS}")
        rows = []
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(row.get(column) is None for column in OUTPUT_COLUMNS):
                raise ResampleError(f"row {row_number}: malformed CSV row")
            rows.append({column: str(row[column]) for column in OUTPUT_COLUMNS})
        return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _validate_parent_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    if len(rows) != PARENT_ROW_COUNT:
        raise ResampleError(f"parent row count must be {PARENT_ROW_COUNT}; got {len(rows)}")
    opens: list[int] = []
    decimal_columns = (
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_vol",
        "taker_buy_quote_vol",
        "ignore",
    )
    for offset, row in enumerate(rows, start=2):
        open_ms = _integer(row["open_time_ms"], "open_time_ms", offset)
        close_ms = _integer(row["close_time_ms"], "close_time_ms", offset)
        trades = _integer(row["num_trades"], "num_trades", offset)
        if trades < 0:
            raise ResampleError(f"row {offset}: num_trades must be non-negative")
        if row["open_time"] != _iso_from_ms(open_ms):
            raise ResampleError(f"row {offset}: open_time disagrees with open_time_ms")
        if close_ms != open_ms + PARENT_CADENCE_MS - 1:
            raise ResampleError(f"row {offset}: invalid 15m close_time_ms")
        parsed = {name: _decimal(row[name], name, offset) for name in decimal_columns}
        if parsed["high"] < max(parsed["open"], parsed["low"], parsed["close"]):
            raise ResampleError(f"row {offset}: OHLC high integrity failure")
        if parsed["low"] > min(parsed["open"], parsed["high"], parsed["close"]):
            raise ResampleError(f"row {offset}: OHLC low integrity failure")
        opens.append(open_ms)
    if len(set(opens)) != len(opens):
        raise ResampleError("parent contains duplicate open_time_ms values")
    if any(right - left != PARENT_CADENCE_MS for left, right in zip(opens, opens[1:])):
        raise ResampleError("parent contains a cadence gap or is not monotonically increasing")
    if _iso_from_ms(opens[0]) != PARENT_START_UTC or _iso_from_ms(opens[-1]) != PARENT_END_UTC:
        raise ResampleError("parent coverage range differs from the canonical range")
    return {
        "row_count": len(rows),
        "start_utc": _iso_from_ms(opens[0]),
        "end_utc": _iso_from_ms(opens[-1]),
        "gap_count": 0,
        "missing_bar_count": 0,
        "duplicate_row_count": 0,
    }


def _validate_parent_metadata(
    parent_csv_path: Path,
    parent_catalog_path: Path,
    parent_validation_path: Path,
) -> dict[str, Any]:
    parent_sha = _hash_file(parent_csv_path)
    validation_sha = _hash_file(parent_validation_path)
    catalog = _load_json(parent_catalog_path)
    validation = _load_json(parent_validation_path)
    checks = [
        (parent_sha == PARENT_NORMALIZED_SHA256, "parent normalized SHA differs"),
        (validation_sha == PARENT_VALIDATION_SHA256, "parent validation SHA differs"),
        (catalog.get("dataset_id") == PARENT_DATASET_ID, "parent dataset_id differs"),
        (catalog.get("timeframe") == PARENT_TIMEFRAME, "parent timeframe differs"),
        (catalog.get("normalized", {}).get("sha256") == parent_sha, "parent catalog normalized SHA differs"),
        (catalog.get("validation_report", {}).get("sha256") == validation_sha, "parent catalog validation SHA differs"),
        (catalog.get("validation_report", {}).get("status") == "PASS", "parent catalog validation status differs"),
        (catalog.get("slice_identity", {}).get("data_slice_identity") == PARENT_DATA_SLICE_IDENTITY, "parent identity differs"),
        (validation.get("ok") is True, "parent validation ok is not true"),
        (validation.get("validation", {}).get("status") == "PASS", "parent validation status is not PASS"),
    ]
    failures = [message for ok, message in checks if not ok]
    if failures:
        raise ResampleError("; ".join(failures))
    return {
        "catalog": catalog,
        "normalized_sha256": parent_sha,
        "validation_report_sha256": validation_sha,
        "catalog_path": _path_text(parent_catalog_path),
        "validation_path": _path_text(parent_validation_path),
        "csv_path": _path_text(parent_csv_path),
        "data_slice_identity": PARENT_DATA_SLICE_IDENTITY,
    }


def resample_rows(
    rows: list[dict[str, str]], config: TargetConfig
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    parent_facts = _validate_parent_rows(rows)
    if len(rows) % config.group_size:
        raise ResampleError(f"partial {config.timeframe} group detected")
    output: list[dict[str, str]] = []
    decimal_sum_columns = (
        "volume",
        "quote_asset_volume",
        "taker_buy_base_vol",
        "taker_buy_quote_vol",
        "ignore",
    )
    for position in range(0, len(rows), config.group_size):
        group = rows[position : position + config.group_size]
        first = group[0]
        last = group[-1]
        open_ms = int(first["open_time_ms"])
        if open_ms % config.cadence_ms:
            raise ResampleError(f"group {position // config.group_size}: non-UTC-boundary open")
        expected = [open_ms + index * PARENT_CADENCE_MS for index in range(config.group_size)]
        actual = [int(row["open_time_ms"]) for row in group]
        if actual != expected:
            raise ResampleError(f"group {position // config.group_size}: children are not contiguous")
        if int(last["close_time_ms"]) != open_ms + config.cadence_ms - 1:
            raise ResampleError(f"group {position // config.group_size}: bad close_time_ms")
        output.append(
            {
                "open_time_ms": first["open_time_ms"],
                "open_time": first["open_time"],
                "open": first["open"],
                "high": _decimal_string(max(Decimal(row["high"]) for row in group)),
                "low": _decimal_string(min(Decimal(row["low"]) for row in group)),
                "close": last["close"],
                "volume": _decimal_string(sum((Decimal(row["volume"]) for row in group), Decimal(0))),
                "close_time_ms": last["close_time_ms"],
                "quote_asset_volume": _decimal_string(sum((Decimal(row["quote_asset_volume"]) for row in group), Decimal(0))),
                "num_trades": str(sum(int(row["num_trades"]) for row in group)),
                "taker_buy_base_vol": _decimal_string(sum((Decimal(row["taker_buy_base_vol"]) for row in group), Decimal(0))),
                "taker_buy_quote_vol": _decimal_string(sum((Decimal(row["taker_buy_quote_vol"]) for row in group), Decimal(0))),
                "ignore": _decimal_string(sum((Decimal(row["ignore"]) for row in group), Decimal(0))),
            }
        )
    if len(output) != config.expected_row_count:
        raise ResampleError(f"{config.timeframe} row count differs from contract")
    start_utc = output[0]["open_time"]
    end_utc = output[-1]["open_time"]
    if start_utc != config.expected_start_utc or end_utc != config.expected_end_utc:
        raise ResampleError(f"{config.timeframe} coverage range differs from contract")
    return output, {
        "row_count": len(output),
        "expected_row_count": config.expected_row_count,
        "start_utc": start_utc,
        "end_utc": end_utc,
        "gap_count": 0,
        "missing_bar_count": 0,
        "duplicate_row_count": 0,
        "partial_window_count": 0,
        "parent": parent_facts,
    }


def _common_derivation(config: TargetConfig) -> dict[str, Any]:
    return {
        "method": f"deterministic 15m-to-{config.timeframe} UTC-boundary resampling",
        "resampling_version": config.resampling_version,
        "aggregation_map": AGGREGATION_MAP,
        "expected_bars_per_output_row": config.group_size,
        "close_time_ms_rule": (
            f"last 15m row close_time_ms; validated to equal {config.timeframe} "
            f"open_time_ms + {config.cadence_ms}ms - 1ms"
        ),
        "no_fill": True,
        "no_interpolation": True,
        "no_deduplication": True,
        "no_synthetic_bars": True,
    }


def _zero_summaries() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "gap_count": 0,
            "missing_bar_count": 0,
            "gaps": [],
            "policy": "detect_report_do_not_fill_or_interpolate",
        },
        {
            "duplicate_group_count": 0,
            "duplicate_row_count": 0,
            "duplicates": [],
            "policy": "detect_report_do_not_deduplicate",
        },
    )


def _boundary() -> dict[str, bool]:
    return {
        "offline_local_input_only": True,
        "no_exchange_contact": True,
        "no_runtime_contact": True,
        "no_paper_live_contact": True,
        "no_result_population_write": True,
        "no_strategy_artifact_mutation": True,
    }


def _range(facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "start_utc": facts["start_utc"],
        "end_utc": facts["end_utc"],
        "row_count": facts["row_count"],
        "expected_row_count": facts["expected_row_count"],
    }


def _validation_report(
    config: TargetConfig,
    output_csv_path: Path,
    output_sha: str,
    facts: dict[str, Any],
    parent: dict[str, Any],
) -> dict[str, Any]:
    gaps, duplicates = _zero_summaries()
    return {
        "ok": True,
        "data_contract_version": config.data_contract_version,
        "validator_version": config.validator_version,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": config.timeframe,
        "source_type": SOURCE_TYPE,
        "source": {
            "parent_dataset_id": PARENT_DATASET_ID,
            "parent_local_processed_file_path": parent["csv_path"],
            "parent_normalized_sha256": parent["normalized_sha256"],
            "parent_validation_report_sha256": parent["validation_report_sha256"],
            "parent_catalog_slice_path": parent["catalog_path"],
            "parent_catalog_ref": parent["catalog"]["catalog_ref"],
            "parent_data_slice_identity": parent["data_slice_identity"],
            "offline_only": True,
        },
        "derivation": _common_derivation(config),
        "normalized": {"path": _path_text(output_csv_path), "sha256": output_sha},
        "range": _range(facts),
        "validation": {
            "status": "PASS",
            "errors": [],
            "utc_boundary_alignment": "PASS",
            "cadence_ms": config.cadence_ms,
            "duplicate_count": 0,
            "gap_count": 0,
            "missing_bar_count": 0,
            "partial_window_count": 0,
            "ohlc_integrity": "PASS",
            "no_fill": True,
            "no_interpolation": True,
            "no_deduplication": True,
            "no_synthesis": True,
        },
        "gap_summary": gaps,
        "duplicate_summary": duplicates,
        "boundary": _boundary(),
    }


def _derivation_report(
    config: TargetConfig,
    output_csv_path: Path,
    output_sha: str,
    facts: dict[str, Any],
    parent: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "package": PACKAGE_ID,
        "derivation_type": SOURCE_TYPE,
        "method": _common_derivation(config)["method"],
        "resampling_version": config.resampling_version,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": config.timeframe,
        "parent_timeframe": PARENT_TIMEFRAME,
        "parent": {
            "dataset_id": PARENT_DATASET_ID,
            "local_processed_file_path": parent["csv_path"],
            "normalized_sha256": parent["normalized_sha256"],
            "validation_report_path": parent["validation_path"],
            "validation_report_sha256": parent["validation_report_sha256"],
            "catalog_slice_path": parent["catalog_path"],
            "catalog_ref": parent["catalog"]["catalog_ref"],
            "data_slice_identity": parent["data_slice_identity"],
            "row_count": facts["parent"]["row_count"],
            "range": {
                "start_utc": facts["parent"]["start_utc"],
                "end_utc": facts["parent"]["end_utc"],
            },
            "gap_count": 0,
            "duplicate_row_count": 0,
        },
        "output": {
            "dataset_id": config.dataset_id,
            "path": _path_text(output_csv_path),
            "sha256": output_sha,
            **_range(facts),
        },
        **_common_derivation(config),
        "determinism": {
            "canonical_json_sort_keys_minified_ascii_for_identity": True,
            "utf8_lf_artifacts": True,
            "no_timezone_local_alignment": True,
        },
        "boundary": _boundary(),
    }


def _catalog_ref(config: TargetConfig, facts: dict[str, Any], slice_hash: str) -> str:
    start = facts["start_utc"].replace(":", "").replace("-", "")
    end = facts["end_utc"].replace(":", "").replace("-", "")
    return (
        f"{config.dataset_id}.{SOURCE_TYPE}.{config.timeframe}."
        f"{start}.{end}.sha256_{slice_hash[:16]}"
    )


def _catalog_entry(
    config: TargetConfig,
    output_csv_path: Path,
    output_sha: str,
    validation_path: Path,
    validation_sha: str,
    derivation_path: Path,
    derivation_sha: str,
    facts: dict[str, Any],
    parent: dict[str, Any],
) -> dict[str, Any]:
    gaps, duplicates = _zero_summaries()
    range_facts = _range(facts)
    identity_inputs = {
        "slice_identity_version": config.slice_identity_version,
        "dataset_id": config.dataset_id,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": config.timeframe,
        "source_type": SOURCE_TYPE,
        "parent_dataset_id": PARENT_DATASET_ID,
        "parent_normalized_sha256": parent["normalized_sha256"],
        "parent_validation_report_sha256": parent["validation_report_sha256"],
        "parent_catalog_ref": parent["catalog"]["catalog_ref"],
        "parent_data_slice_identity": parent["data_slice_identity"],
        "normalized_sha256": output_sha,
        "validation_report_sha256": validation_sha,
        "validation_status": "PASS",
        "resampling_method": _common_derivation(config)["method"],
        "resampling_version": config.resampling_version,
        "aggregation_map": AGGREGATION_MAP,
        "range": range_facts,
        "gap_summary": gaps,
        "duplicate_summary": duplicates,
        "partial_window_count": 0,
    }
    slice_hash = _identity_hash(identity_inputs)
    identity = f"{config.dataset_id}:sha256:{slice_hash}"
    return {
        "catalog_version": config.catalog_version,
        "catalog_ref": _catalog_ref(config, facts, slice_hash),
        "catalog_status": "valid_offline_derived_slice",
        "dataset_id": config.dataset_id,
        "source_type": SOURCE_TYPE,
        "symbol": SYMBOL,
        "venue": VENUE,
        "market_type": MARKET_TYPE,
        "stream": STREAM,
        "timeframe": config.timeframe,
        "data_contract_version": config.data_contract_version,
        "resampling_version": config.resampling_version,
        "validator_version": config.validator_version,
        "normalized": {"path": _path_text(output_csv_path), "sha256": output_sha},
        "validation_report": {
            "path": _path_text(validation_path),
            "sha256": validation_sha,
            "status": "PASS",
        },
        "derivation_report": {
            "path": _path_text(derivation_path),
            "sha256": derivation_sha,
        },
        "parent": {
            "dataset_id": PARENT_DATASET_ID,
            "normalized_path": parent["csv_path"],
            "normalized_sha256": parent["normalized_sha256"],
            "validation_report_path": parent["validation_path"],
            "validation_report_sha256": parent["validation_report_sha256"],
            "catalog_slice_path": parent["catalog_path"],
            "catalog_ref": parent["catalog"]["catalog_ref"],
            "data_slice_identity": parent["data_slice_identity"],
        },
        "range": range_facts,
        "gap_summary": gaps,
        "duplicate_summary": duplicates,
        "derivation": _common_derivation(config),
        "slice_identity": {
            "data_slice_identity": identity,
            "hash": slice_hash,
            "hash_algorithm": "sha256",
            "identity_inputs": identity_inputs,
            "identity_input_ordering": "canonical_json_sort_keys_minified_ascii",
        },
        "evidence_limit": {
            "diagnostic_direct_parquet_is_not_authority": True,
            "not_strategy_quality_evidence": True,
            "no_result_population": True,
        },
        "boundary": _boundary(),
    }


def derive_slice(
    target: str,
    *,
    parent_csv_path: Path = DEFAULT_PARENT_CSV,
    parent_catalog_path: Path = DEFAULT_PARENT_CATALOG,
    parent_validation_path: Path = DEFAULT_PARENT_VALIDATION,
    output_csv_path: Path | None = None,
    validation_report_path: Path | None = None,
    derivation_report_path: Path | None = None,
    catalog_path: Path | None = None,
) -> ResampleResult:
    if target not in TARGETS:
        raise ResampleError(f"unsupported target {target!r}; expected one of {tuple(TARGETS)}")
    config = TARGETS[target]
    output_csv_path = output_csv_path or config.output_csv
    validation_report_path = validation_report_path or config.validation_report
    derivation_report_path = derivation_report_path or config.derivation_report
    catalog_path = catalog_path or config.catalog_slice
    parent = _validate_parent_metadata(
        parent_csv_path, parent_catalog_path, parent_validation_path
    )
    rows = _read_csv(parent_csv_path)
    output, facts = resample_rows(rows, config)
    _write_csv(output_csv_path, output)
    output_sha = _hash_file(output_csv_path)
    validation = _validation_report(config, output_csv_path, output_sha, facts, parent)
    _write_json(validation_report_path, validation)
    validation_sha = _hash_file(validation_report_path)
    derivation = _derivation_report(config, output_csv_path, output_sha, facts, parent)
    _write_json(derivation_report_path, derivation)
    derivation_sha = _hash_file(derivation_report_path)
    catalog = _catalog_entry(
        config,
        output_csv_path,
        output_sha,
        validation_report_path,
        validation_sha,
        derivation_report_path,
        derivation_sha,
        facts,
        parent,
    )
    _write_json(catalog_path, catalog)
    return ResampleResult(
        ok=True,
        target=target,
        output_csv_path=_path_text(output_csv_path),
        output_csv_sha256=output_sha,
        validation_report_path=_path_text(validation_report_path),
        validation_report_sha256=validation_sha,
        derivation_report_path=_path_text(derivation_report_path),
        derivation_report_sha256=derivation_sha,
        catalog_path=_path_text(catalog_path),
        catalog_sha256=_hash_file(catalog_path),
        data_slice_identity=catalog["slice_identity"]["data_slice_identity"],
        row_count=facts["row_count"],
        expected_row_count=facts["expected_row_count"],
        start_utc=facts["start_utc"],
        end_utc=facts["end_utc"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=tuple(TARGETS), required=True)
    parser.add_argument("--parent-csv", type=Path, default=DEFAULT_PARENT_CSV)
    parser.add_argument("--parent-catalog", type=Path, default=DEFAULT_PARENT_CATALOG)
    parser.add_argument("--parent-validation", type=Path, default=DEFAULT_PARENT_VALIDATION)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--validation-report", type=Path)
    parser.add_argument("--derivation-report", type=Path)
    parser.add_argument("--catalog", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = derive_slice(
            args.target,
            parent_csv_path=args.parent_csv,
            parent_catalog_path=args.parent_catalog,
            parent_validation_path=args.parent_validation,
            output_csv_path=args.output_csv,
            validation_report_path=args.validation_report,
            derivation_report_path=args.derivation_report,
            catalog_path=args.catalog,
        )
    except ResampleError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
