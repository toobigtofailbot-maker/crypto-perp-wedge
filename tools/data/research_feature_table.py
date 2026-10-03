"""Resolve and exactly join provenance-bound research feature tables."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from tools.registry.validate_research_feature_table_manifest import validate_manifest_payload
from tools.research_domain.feature_data import (
    FEATURE_JOIN_CONTRACT_VERSION,
    FeatureDataContractError,
    build_composite_research_data_identity,
)


class ResearchFeatureTableError(ValueError):
    """Raised when bytes, provenance, grids, or causality fail closed."""


@dataclass(frozen=True)
class ResolvedResearchFeatureTable:
    joined_frame: pd.DataFrame
    selected_feature_names: tuple[str, ...]
    feature_table_identity: str
    source_set_identity: str
    composite_data_slice_identity: str
    provenance_notes: tuple[str, ...]
    source_class: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _utc(value: Any, label: str) -> pd.Timestamp:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise ResearchFeatureTableError(f"{label} must be an ISO-8601 UTC timestamp")
    return pd.Timestamp(parsed)


def _interval_delta(timeframe: str) -> pd.Timedelta:
    try:
        delta = pd.to_timedelta(timeframe)
    except ValueError as exc:
        raise ResearchFeatureTableError(f"unsupported timeframe: {timeframe}") from exc
    if delta <= pd.Timedelta(0):
        raise ResearchFeatureTableError("timeframe must be positive")
    return delta


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchFeatureTableError(f"cannot read feature manifest: {path}") from exc
    if not isinstance(payload, dict):
        raise ResearchFeatureTableError("feature manifest must be a JSON object")
    errors = validate_manifest_payload(payload)
    if errors:
        raise ResearchFeatureTableError("feature manifest invalid: " + "; ".join(errors))
    return payload


def _load_feature_csv(path: Path, columns: Sequence[str]) -> pd.DataFrame:
    if not path.is_file():
        raise ResearchFeatureTableError(f"feature CSV does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
    except (OSError, StopIteration, UnicodeDecodeError) as exc:
        raise ResearchFeatureTableError("feature CSV is unreadable or empty") from exc
    if header != list(columns) or len(header) != len(set(header)):
        raise ResearchFeatureTableError("feature CSV columns/order do not match output identity")
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise ResearchFeatureTableError("feature CSV cannot be parsed") from exc


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _ratio(numerator: Decimal, denominator: Decimal) -> str:
    with localcontext() as context:
        context.prec = 38
        return _decimal_text(numerator / denominator)


def _validate_d4_taker_values(feature: pd.DataFrame, parent_path: Path) -> None:
    required = {"open_time_ms", "volume", "num_trades", "taker_buy_base_vol"}
    try:
        with parent_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ResearchFeatureTableError(
                    "canonical D4 parent lacks required taker derivation columns"
                )
            parent_rows = list(reader)
    except (OSError, UnicodeDecodeError) as exc:
        raise ResearchFeatureTableError("canonical D4 parent cannot be parsed") from exc
    if len(parent_rows) != len(feature):
        raise ResearchFeatureTableError("canonical D4 parent/feature row counts differ")
    for index, (parent, derived) in enumerate(
        zip(parent_rows, feature.to_dict("records"), strict=True), start=1
    ):
        try:
            volume = Decimal(parent["volume"])
            buy = Decimal(parent["taker_buy_base_vol"])
            trades = int(parent["num_trades"])
            derived_buy = Decimal(str(derived["taker_buy_volume"]))
            derived_sell = Decimal(str(derived["taker_sell_volume"]))
        except (InvalidOperation, ValueError, TypeError, KeyError) as exc:
            raise ResearchFeatureTableError(
                f"canonical D4 taker values are invalid at row {index}"
            ) from exc
        if (
            not volume.is_finite()
            or not buy.is_finite()
            or volume < 0
            or buy < 0
            or buy > volume
            or trades < 0
        ):
            raise ResearchFeatureTableError(
                f"canonical D4 parent values are invalid at row {index}"
            )
        sell = volume - buy
        if derived_buy != buy or derived_sell != sell:
            raise ResearchFeatureTableError(
                f"canonical D4 feature formula mismatch at row {index}"
            )
        if str(derived["open_time_ms"]) != parent["open_time_ms"]:
            raise ResearchFeatureTableError(
                f"canonical D4 parent timestamp mismatch at row {index}"
            )
        ratio = str(derived["taker_buy_sell_ratio"])
        if sell == 0:
            if ratio != "":
                raise ResearchFeatureTableError(
                    f"zero-sell ratio must be null at row {index}"
                )
        elif ratio != _ratio(buy, sell):
            raise ResearchFeatureTableError(
                f"canonical D4 ratio formula mismatch at row {index}"
            )


def resolve_research_feature_table(
    *,
    base_frame: pd.DataFrame,
    base_input_path: Path,
    base_data_slice_identity: str,
    base_normalized_sha256: str,
    base_market_identity: Mapping[str, str],
    base_timeframe: str,
    base_coverage_start_utc_inclusive: str,
    base_coverage_end_utc_exclusive: str,
    feature_manifest_path: Path,
    feature_csv_path: Path,
    requested_feature_names: Sequence[str],
) -> ResolvedResearchFeatureTable:
    """Verify physical bytes and perform a strict one-to-one completed-bar join."""

    if not base_input_path.is_file() or _sha256(base_input_path) != base_normalized_sha256:
        raise ResearchFeatureTableError("base normalized SHA-256 does not match physical bytes")
    if not isinstance(base_frame.index, pd.DatetimeIndex) or base_frame.index.tz is None:
        raise ResearchFeatureTableError("base frame requires a timezone-aware DatetimeIndex")
    if base_frame.index.has_duplicates or not base_frame.index.is_monotonic_increasing:
        raise ResearchFeatureTableError("base timestamp keys must be unique and strictly ordered")
    requested = tuple(sorted(requested_feature_names))
    if not requested or len(requested) != len(set(requested)):
        raise ResearchFeatureTableError("requested feature names must be non-empty and unique")

    manifest = _load_manifest(feature_manifest_path)
    contract = manifest["research_feature_table"]
    if contract["source_class"] != "CANONICAL_D4_KLINE_DERIVATION":
        raise ResearchFeatureTableError(
            "research taker feature input must use canonical D4 kline derivation"
        )
    parent = contract["parent_identity"]
    if (
        parent["data_slice_identity"] != base_data_slice_identity
        or parent["normalized_sha256"] != base_normalized_sha256
        or parent["row_count"] != len(base_frame)
        or parent["coverage_start_utc_inclusive"]
        != base_coverage_start_utc_inclusive
        or parent["coverage_end_utc_exclusive"]
        != base_coverage_end_utc_exclusive
    ):
        raise ResearchFeatureTableError(
            "feature manifest parent identity does not match the physical D4 parent"
        )
    if dict(contract["market_identity"]) != dict(base_market_identity):
        raise ResearchFeatureTableError("base and feature market identities differ")
    if contract["timeframe"] != base_timeframe:
        raise ResearchFeatureTableError("base and feature timeframes differ")
    advertised = tuple(contract["feature_names"])
    missing = sorted(set(requested) - set(advertised))
    if missing:
        raise ResearchFeatureTableError(f"requested features are not advertised: {missing}")
    coverage = contract["coverage"]
    if coverage["complete"] is not True:
        raise ResearchFeatureTableError("feature table coverage is incomplete")
    if (
        coverage["start_utc_inclusive"] != base_coverage_start_utc_inclusive
        or coverage["end_utc_exclusive"] != base_coverage_end_utc_exclusive
    ):
        raise ResearchFeatureTableError("base and feature coverage windows differ")
    if coverage["expected_row_count"] != len(base_frame):
        raise ResearchFeatureTableError("base row count does not match feature coverage")

    output = contract["output_identity"]
    actual_feature_sha = _sha256(feature_csv_path)
    if actual_feature_sha != output["sha256"]:
        raise ResearchFeatureTableError("feature output SHA-256 does not match physical bytes")
    outer_output = manifest.get("output")
    if isinstance(outer_output, Mapping) and outer_output.get("sha256") != actual_feature_sha:
        raise ResearchFeatureTableError("outer and generic feature output identities disagree")
    feature = _load_feature_csv(feature_csv_path, output["columns"])
    if len(feature) != output["row_count"] or len(feature) != len(base_frame):
        raise ResearchFeatureTableError("feature/base row counts are not exactly equal")
    _validate_d4_taker_values(feature, base_input_path)

    timestamps = pd.to_datetime(feature["timestamp"], utc=True, errors="coerce")
    available = pd.to_datetime(feature["feature_available_at"], utc=True, errors="coerce")
    if timestamps.isna().any() or available.isna().any():
        raise ResearchFeatureTableError("feature timestamps must be valid UTC timestamps")
    feature_index = pd.DatetimeIndex(timestamps)
    if feature_index.has_duplicates or not feature_index.is_monotonic_increasing:
        raise ResearchFeatureTableError("feature timestamp keys must be unique and strictly ordered")
    base_index = pd.DatetimeIndex(base_frame.index).tz_convert("UTC")
    if not feature_index.equals(base_index):
        raise ResearchFeatureTableError("base and feature timestamp key sets/order differ")
    delta = _interval_delta(base_timeframe)
    if not pd.DatetimeIndex(available).equals(feature_index + delta):
        raise ResearchFeatureTableError("feature availability must equal exclusive bar close")
    open_ms = pd.to_numeric(feature["open_time_ms"], errors="coerce")
    available_ms = pd.to_numeric(feature["feature_available_at_ms"], errors="coerce")
    expected_open_ms = pd.Series(feature_index.as_unit("ns").asi8 // 1_000_000)
    expected_available_ms = pd.Series(
        (feature_index + delta).as_unit("ns").asi8 // 1_000_000
    )
    if open_ms.isna().any() or available_ms.isna().any():
        raise ResearchFeatureTableError("feature epoch timestamps are invalid")
    if not open_ms.reset_index(drop=True).astype("int64").equals(expected_open_ms.astype("int64")):
        raise ResearchFeatureTableError("open_time_ms disagrees with timestamp")
    if not available_ms.reset_index(drop=True).astype("int64").equals(expected_available_ms.astype("int64")):
        raise ResearchFeatureTableError("feature_available_at_ms disagrees with bar close")

    selected = pd.DataFrame(index=base_index)
    for name in requested:
        values = pd.to_numeric(feature[name], errors="coerce")
        permitted_ratio_nulls = (
            name == "taker_buy_sell_ratio"
            and values.isna().equals(
                pd.to_numeric(feature["taker_sell_volume"], errors="coerce").eq(0)
            )
        )
        finite_values = values.dropna().map(lambda value: math.isfinite(float(value))).all()
        if (values.isna().any() and not permitted_ratio_nulls) or not finite_values:
            raise ResearchFeatureTableError(f"requested feature {name} contains invalid values")
        selected[name] = values.astype(float).to_numpy()
    joined = base_frame.copy()
    joined.index = base_index
    for name in requested:
        if name in joined.columns:
            raise ResearchFeatureTableError(f"base frame already contains requested feature: {name}")
        joined[name] = selected[name]
    if len(joined) != len(base_frame) or joined.index.has_duplicates:
        raise ResearchFeatureTableError("exact join cardinality was not preserved")

    try:
        composite = build_composite_research_data_identity(
            base_data_slice_identity=base_data_slice_identity,
            base_normalized_sha256=base_normalized_sha256,
            feature_table_identity=contract["feature_table_identity"],
            feature_output_sha256=actual_feature_sha,
            market_identity=base_market_identity,
            timeframe=base_timeframe,
            coverage_start_utc_inclusive=base_coverage_start_utc_inclusive,
            coverage_end_utc_exclusive=base_coverage_end_utc_exclusive,
            joined_row_count=len(joined),
            selected_feature_names=requested,
        )
    except FeatureDataContractError as exc:
        raise ResearchFeatureTableError(str(exc)) from exc
    notes = (
        f"feature_join_contract_version={FEATURE_JOIN_CONTRACT_VERSION}",
        f"feature_source_set_identity={contract['source_set_identity']}",
        f"feature_output_sha256={actual_feature_sha}",
        f"feature_table_identity={contract['feature_table_identity']}",
        f"feature_source_class={contract['source_class']}",
        f"selected_research_features={','.join(requested)}",
        "feature_join=exact_one_to_one_no_fill_no_tolerance_no_interpolation",
        "feature_availability=exclusive_bar_close",
    )
    return ResolvedResearchFeatureTable(
        joined_frame=joined,
        selected_feature_names=requested,
        feature_table_identity=contract["feature_table_identity"],
        source_set_identity=contract["source_set_identity"],
        composite_data_slice_identity=composite,
        provenance_notes=notes,
        source_class=contract["source_class"],
    )
