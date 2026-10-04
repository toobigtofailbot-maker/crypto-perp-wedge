"""Build-and-test-only offline research sweep runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import pandas as pd
from jsonschema import Draft7Validator

from lib.backtest import run_backtest
from lib.evaluation import max_drawdown, sharpe
from tools.data.research_feature_table import (
    ResearchFeatureTableError,
    resolve_research_feature_table,
)
from tools.data.register_binance_usdtm_1d_lineage import (
    CADENCE_MS as CANONICAL_1D_CADENCE_MS,
    DATASET_ID as CANONICAL_1D_DATASET_ID,
    REQUIRED_COLUMNS as CANONICAL_1D_SOURCE_COLUMNS,
    SNAPSHOT_VERSION as CANONICAL_1D_SNAPSHOT_VERSION,
    build_lineage as build_1d_lineage,
    canonical_json_bytes as canonical_1d_catalog_bytes,
)
from tools.registry.validate_funding_series_provenance import (
    DEFAULT_SCHEMA_PATH as DEFAULT_FUNDING_PROVENANCE_SCHEMA_PATH,
    FundingProvenanceError,
    validate_artifact as validate_funding_artifact,
)
from tools.registry.validate_result_populations import (
    DEFAULT_RESULT_POPULATION_SCHEMA_PATH,
    HASH_ALGORITHM,
    OUTCOME_CATEGORIES,
    RESULT_POPULATION_HASH_SCOPE_VERSION,
    validate_result_populations,
)
from tools.registry.validate_strategy_specs import (
    DEFAULT_SCHEMA_PATH as DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    validate_strategy_specs,
)
from tools.registry.validate_variant_sweep_artifacts import (
    DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    validate_variant_sweep_artifacts,
)
from tools.research_runner.spec_signal_compiler import compile_signal
from tools.research_runner.spec_signal_compiler import (
    ALLOWED_OHLCV_FIELDS,
    ALLOWED_TIMESTAMP_DERIVED_FIELDS,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RESULT_POPULATIONS_DIR = REPO_ROOT / "research" / "result_populations"
HASH_ALGORITHM = "sha256"
OUTCOME_CATEGORIES = (
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
    "not_attempted",
)
RUNNER_VERSION = "wp-s2c-190-build-test-v1"
RUNNER_CODE_REF = "tools.research_runner.run_offline_sweep"
FIXED_AUDIT_TIMESTAMP = "2026-06-01T00:00:00Z"
FUNDING_COST_MODES = ("off", "on")
FUNDING_REQUIRED_STRATEGY_SPEC_IDS = frozenset({"STRAT-SPEC-0007"})
CANONICAL_FUNDING_EXPECTED_IDENTITY: dict[str, Any] = {
    "funding_series_id": (
        "binance_usdtm_btcusdt_funding_events_20190910t080000z_"
        "20260412t160000z_sha256_5f0da7478ccf3514"
    ),
    "provenance_artifact_id": (
        "FUNDING-PROV-BINANCE-USDTM-BTCUSDT-20190910T080000Z-"
        "20260412T160000Z-5F0DA7478CCF3514"
    ),
    "provenance_artifact_path": (
        "research/data_provenance/funding/"
        "binance_usdtm_btcusdt_funding_events_20190910t080000z_"
        "20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json"
    ),
    "provenance_artifact_sha256": (
        "sha256:fe84062a6426b7b5aa1653e87eb0038486925f5c5c6263cc33595870d4e6c692"
    ),
    "funding_parquet_path": (
        "data/processed/binance_um_perp_BTCUSDT_funding_8h_"
        "2019-09-10_2026-04-12_2026-04-12T1655Z.parquet"
    ),
    "funding_parquet_sha256": (
        "sha256:5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798"
    ),
    "funding_parquet_byte_length": 126_987,
    "funding_parquet_row_count": 7_220,
    "coverage_start_utc": "2019-09-10T08:00:00Z",
    "coverage_end_utc": "2026-04-12T16:00:00Z",
    "timestamp_semantics": "actual_exchange_funding_event_timestamp",
    "rate_units": "decimal_fraction_of_notional_per_funding_event",
    "boundary_rule_id": "existing_backtest_left_open_right_closed_pre_fill_v1",
}
CANONICAL_15M_DATA_CATALOG_REF = "15m_ohlcv_test_fixture_offline_only"
D4_PROVENANCE_MODE_NOTE = "provenance_mode=d4_catalog_slice"
D4H_PROVENANCE_MODE_NOTE = "provenance_mode=d4h_derived_catalog_slice"
FT01_PROVENANCE_MODE_NOTE = "provenance_mode=ft01_15m_d4_derived_catalog_slice"
CANONICAL_1D_PROVENANCE_MODE_NOTE = "provenance_mode=canonical_1d_public_archive_snapshot"
DEFAULT_1D_CATALOG_SLICE_PATH = (
    REPO_ROOT
    / "research"
    / "data_slices"
    / "binance_usdtm_btcusdt_1d"
    / "binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json"
)
DEFAULT_1D_VALIDATOR_PATH = (
    REPO_ROOT / "tools" / "data" / "register_binance_usdtm_1d_lineage.py"
)
OFFICIAL_1D_CATALOG_ARTIFACT_SHA256 = (
    "51fc09918841cd3ac353efe375af91a4732080571f9b1af634f5d1a426217adb"
)
OFFICIAL_1D_SOURCE_SHA256 = (
    "c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802"
)
OFFICIAL_1D_SOURCE_BYTE_LENGTH = 200_961
OFFICIAL_1D_ROW_COUNT = 2_293
DEFAULT_4H_CATALOG_SLICE_PATH = (
    REPO_ROOT
    / "research"
    / "data_slices"
    / "binance_usdtm_btcusdt_4h"
    / "binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json"
)
DEFAULT_4H_VALIDATION_REPORT_PATH = (
    REPO_ROOT
    / "research"
    / "data_slices"
    / "binance_usdtm_btcusdt_4h"
    / "binance_usdtm_btcusdt_4h_20200101_20260411.validation_report.json"
)
DEFAULT_4H_DERIVATION_REPORT_PATH = (
    REPO_ROOT
    / "research"
    / "data_slices"
    / "binance_usdtm_btcusdt_4h"
    / "binance_usdtm_btcusdt_4h_20200101_20260411.derivation_report.json"
)
OFFICIAL_4H_DATA_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_4h:sha256:"
    "4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30"
)
OFFICIAL_4H_ROW_COUNT = 13_758
CANONICAL_D4_PARENT_DATASET_ID = "binance_usdtm_btcusdt_ohlcv_15m"
CANONICAL_D4_PARENT_NORMALIZED_SHA256 = (
    "c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab"
)
CANONICAL_D4_PARENT_VALIDATION_SHA256 = (
    "785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c"
)
CANONICAL_D4_PARENT_DATA_SLICE_IDENTITY = (
    "binance_usdtm_btcusdt_ohlcv_15m:sha256:"
    "3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664"
)
CANONICAL_INTRADAY_DERIVED_CONFIG: dict[str, dict[str, Any]] = {
    "30m": {
        "dataset_id": "binance_usdtm_btcusdt_ohlcv_30m",
        "cadence": pd.Timedelta(minutes=30),
        "cadence_ms": 1_800_000,
        "row_count": 110_064,
        "start_utc": "2020-01-01T00:00:00Z",
        "end_utc": "2026-04-11T23:30:00Z",
        "catalog": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.catalog_slice.json",
        "validation": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.validation_report.json",
        "derivation": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_30m/binance_usdtm_btcusdt_30m_20200101_20260411.derivation_report.json",
    },
    "1h": {
        "dataset_id": "binance_usdtm_btcusdt_ohlcv_1h",
        "cadence": pd.Timedelta(hours=1),
        "cadence_ms": 3_600_000,
        "row_count": 55_032,
        "start_utc": "2020-01-01T00:00:00Z",
        "end_utc": "2026-04-11T23:00:00Z",
        "catalog": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.catalog_slice.json",
        "validation": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.validation_report.json",
        "derivation": REPO_ROOT / "research/data_slices/binance_usdtm_btcusdt_1h/binance_usdtm_btcusdt_1h_20200101_20260411.derivation_report.json",
    },
}
INITIAL_EQUITY = 10_000.0
DEFAULT_TARGET_LEVERAGE = 1.0
DEFAULT_MAX_WORKERS = 1
REQUIRED_OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
DATA_FEATURE_AVAILABILITY_CATALOG_PATH = (
    REPO_ROOT
    / "research"
    / "data_feature_availability"
    / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
SIZING_MODE_FIXED_ORDER_SIZE = "fixed_order_size"
SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE = "dynamic_equity_target_leverage"
SIZING_MODES = (
    SIZING_MODE_FIXED_ORDER_SIZE,
    SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
)
SIZING_MODEL = "runner_resolved_fixed_order_size"
DYNAMIC_SIZING_MODEL = "dynamic_equity_target_leverage"
REFERENCE_PRICE_BASIS = "first_in_sample_open"
DYNAMIC_SIZING_EQUITY_BASIS = "realized_available_equity_at_entry"
DYNAMIC_ENTRY_REFERENCE_PRICE_BASIS = "next_bar_open_pre_fee_slippage"
DRIFT_CAVEAT = (
    "fixed_order_size_caps_leverage_at_reference_price_only_effective_leverage_can_drift"
)


class OfflineSweepError(RuntimeError):
    """Raised for preflight or output validation failures."""


class OfflineSweepAbort(RuntimeError):
    """Raised for deterministic fixture infrastructure aborts."""


@dataclass(frozen=True)
class _ExecutionInput:
    mode: str
    execution_provenance_class: str
    ohlcv: pd.DataFrame
    funding: pd.DataFrame
    timeframe: str
    data_catalog_ref: str
    data_slice_identity: str
    environment_summary: list[str]
    data_coverage_notes: list[str]
    funding_input_identity: dict[str, Any] = field(
        default_factory=lambda: _funding_input_identity_off()
    )


@dataclass(frozen=True)
class _SizingResolution:
    target_leverage: float
    initial_equity: float
    reference_price: float
    reference_price_basis: str
    resolved_order_size: float
    sizing_model: str


@dataclass(frozen=True)
class _SizingContext:
    sizing_mode: str
    target_leverage: float
    exact_resolution: _SizingResolution | None


@dataclass(frozen=True)
class _WalkForwardWindow:
    window_id: str
    window_index: int
    in_sample_start: pd.Timestamp
    in_sample_end_exclusive: pd.Timestamp
    out_of_sample_start: pd.Timestamp
    out_of_sample_end_exclusive: pd.Timestamp
    in_sample_row_count: int
    out_of_sample_row_count: int


def _validate_sizing_mode(value: str) -> str:
    if value not in SIZING_MODES:
        raise OfflineSweepError(
            "--sizing-mode must be 'fixed_order_size' or 'dynamic_equity_target_leverage'"
        )
    return value


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _sha256_prefixed(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_file_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_funding_cost_mode(value: str) -> str:
    if value not in FUNDING_COST_MODES:
        raise OfflineSweepError("--funding-cost-mode must be 'off' or 'on'")
    return value


def _funding_input_identity_off() -> dict[str, Any]:
    return {
        "funding_mode": "off",
        "funding_series_id": None,
        "provenance_artifact_id": None,
        "provenance_artifact_path": None,
        "provenance_artifact_sha256": None,
        "funding_parquet_path": None,
        "funding_parquet_sha256": None,
        "coverage_start_utc": None,
        "coverage_end_utc": None,
        "timestamp_semantics": None,
        "rate_units": None,
        "boundary_rule_id": None,
    }


def _funding_identity_note(identity: dict[str, Any]) -> str:
    return "funding_input_identity=" + json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
    )


def _load_validated_funding_input(
    artifact_path: Path,
    data_root: Path | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    expected = CANONICAL_FUNDING_EXPECTED_IDENTITY
    expected_artifact = REPO_ROOT.joinpath(*expected["provenance_artifact_path"].split("/"))
    supplied_artifact = artifact_path if artifact_path.is_absolute() else REPO_ROOT / artifact_path
    try:
        if supplied_artifact.resolve(strict=True) != expected_artifact.resolve(strict=True):
            raise OfflineSweepError(
                "--funding-provenance must identify the canonical funding provenance artifact"
            )
    except FileNotFoundError as exc:
        raise OfflineSweepError(
            f"--funding-provenance does not exist: {artifact_path}"
        ) from exc

    if data_root is not None and data_root.is_symlink():
        raise OfflineSweepError("--funding-data-root must not be a symlink")
    source_root = data_root or REPO_ROOT
    try:
        validation = validate_funding_artifact(
            supplied_artifact,
            schema_path=DEFAULT_FUNDING_PROVENANCE_SCHEMA_PATH,
            repo_root=REPO_ROOT,
            data_root=source_root,
        )
    except (FundingProvenanceError, FileNotFoundError, OSError) as exc:
        raise OfflineSweepError(f"funding input validation failed: {exc}") from exc

    observed = {
        "funding_series_id": validation.funding_series_id,
        "provenance_artifact_id": validation.artifact_id,
        "provenance_artifact_path": validation.artifact_path,
        "provenance_artifact_sha256": validation.artifact_sha256,
        "funding_parquet_path": validation.source_data_path,
        "funding_parquet_sha256": validation.source_data_sha256,
        "funding_parquet_row_count": validation.row_count,
        "coverage_start_utc": validation.coverage_start_utc,
        "coverage_end_utc": validation.coverage_end_utc,
    }
    for field, value in observed.items():
        if value != expected[field]:
            raise OfflineSweepError(
                f"canonical funding identity mismatch for {field}: expected={expected[field]!r}, "
                f"observed={value!r}"
            )

    payload = _load_json(supplied_artifact)
    try:
        post_validation_artifact_sha256 = _sha256_file(supplied_artifact)
    except OSError as exc:
        raise OfflineSweepError(
            f"funding provenance read failed after validation: {exc}"
        ) from exc
    if post_validation_artifact_sha256 != expected["provenance_artifact_sha256"]:
        raise OfflineSweepError("funding provenance mutated after validation")
    if payload["file_identity"]["byte_length"] != expected["funding_parquet_byte_length"]:
        raise OfflineSweepError(
            "canonical funding identity mismatch for funding_parquet_byte_length"
        )
    if payload["event_fields"]["timestamp"]["semantics"] != expected["timestamp_semantics"]:
        raise OfflineSweepError("canonical funding identity mismatch for timestamp_semantics")
    if payload["event_fields"]["funding_rate"]["units"] != expected["rate_units"]:
        raise OfflineSweepError("canonical funding identity mismatch for rate_units")
    if payload["alignment"]["boundary_rule_id"] != expected["boundary_rule_id"]:
        raise OfflineSweepError("canonical funding identity mismatch for boundary_rule_id")

    source_path = source_root.resolve(strict=True).joinpath(
        *validation.source_data_path.split("/")
    )
    try:
        source_path = source_path.resolve(strict=True)
        source_frame = pd.read_parquet(source_path, columns=["fundingTime", "fundingRate"])
    except Exception as exc:
        raise OfflineSweepError(f"funding input read failed after validation: {exc}") from exc
    if _sha256_file(source_path) != expected["funding_parquet_sha256"]:
        raise OfflineSweepError("funding source mutated after provenance validation")

    timestamps = pd.to_datetime(source_frame["fundingTime"], unit="ms", utc=True)
    funding = pd.DataFrame(
        {"funding_rate": source_frame["fundingRate"].astype("float64").to_numpy()},
        index=pd.DatetimeIndex(timestamps),
    )
    funding.index.name = "fundingTime"
    identity = {
        "funding_mode": "on",
        "funding_series_id": validation.funding_series_id,
        "provenance_artifact_id": validation.artifact_id,
        "provenance_artifact_path": validation.artifact_path,
        "provenance_artifact_sha256": validation.artifact_sha256,
        "funding_parquet_path": validation.source_data_path,
        "funding_parquet_sha256": validation.source_data_sha256,
        "coverage_start_utc": validation.coverage_start_utc,
        "coverage_end_utc": validation.coverage_end_utc,
        "timestamp_semantics": payload["event_fields"]["timestamp"]["semantics"],
        "rate_units": payload["event_fields"]["funding_rate"]["units"],
        "boundary_rule_id": payload["alignment"]["boundary_rule_id"],
    }
    return funding, identity


def _payload_declares_required_funding(payload: Any) -> bool:
    if isinstance(payload, dict):
        if payload.get("stream") == "funding" and payload.get("availability") in {
            "required",
            "blocker_if_missing",
        }:
            return True
        return any(_payload_declares_required_funding(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_payload_declares_required_funding(value) for value in payload)
    return False


def _requires_funding_costs(
    strategy_spec: dict[str, Any],
    sweep_plan: dict[str, Any],
) -> bool:
    return (
        strategy_spec.get("strategy_spec_id") in FUNDING_REQUIRED_STRATEGY_SPEC_IDS
        or _payload_declares_required_funding(strategy_spec.get("timeframe_and_data"))
        or _payload_declares_required_funding(sweep_plan.get("data_and_timeframe_assumptions"))
    )


def _bind_funding_input(
    execution_input: _ExecutionInput,
    *,
    funding_cost_mode: str,
    funding: pd.DataFrame | None = None,
    funding_identity: dict[str, Any] | None = None,
) -> _ExecutionInput:
    if funding_cost_mode == "off":
        identity = _funding_input_identity_off()
        bound_funding = execution_input.funding
    else:
        if funding is None or funding_identity is None:
            raise OfflineSweepError("funding mode on requires validated funding data and identity")
        coverage_start = pd.Timestamp(funding_identity["coverage_start_utc"])
        coverage_end = pd.Timestamp(funding_identity["coverage_end_utc"])
        if execution_input.ohlcv.index[0] < coverage_start:
            raise OfflineSweepError("OHLCV starts before canonical funding coverage")
        if execution_input.ohlcv.index[-1] > coverage_end:
            raise OfflineSweepError("OHLCV ends after canonical funding coverage")
        identity = funding_identity
        bound_funding = funding.loc[
            (funding.index >= execution_input.ohlcv.index[0])
            & (funding.index <= execution_input.ohlcv.index[-1])
        ].copy()
    note = _funding_identity_note(identity)
    return _ExecutionInput(
        mode=execution_input.mode,
        execution_provenance_class=execution_input.execution_provenance_class,
        ohlcv=execution_input.ohlcv,
        funding=bound_funding,
        timeframe=execution_input.timeframe,
        data_catalog_ref=execution_input.data_catalog_ref,
        data_slice_identity=execution_input.data_slice_identity,
        environment_summary=[*execution_input.environment_summary, note],
        data_coverage_notes=[*execution_input.data_coverage_notes, note],
        funding_input_identity=identity,
    )


def _validate_target_leverage(value: float) -> float:
    leverage = float(value)
    if not math.isfinite(leverage) or leverage <= 0.0:
        raise OfflineSweepError("--target-leverage must be finite and positive")
    return leverage


def _parse_target_leverage(value: str) -> float:
    try:
        return _validate_target_leverage(float(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--target-leverage must be numeric") from exc
    except OfflineSweepError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _positive_int_arg(name: str):
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} must be a positive integer") from exc
        if parsed <= 0:
            raise argparse.ArgumentTypeError(f"{name} must be a positive integer")
        return parsed

    return parse


def _validate_max_workers(value: int) -> int:
    workers = int(value)
    if workers <= 0:
        raise OfflineSweepError("max_workers must be a positive integer")
    return workers


def _resolve_order_size(
    *,
    target_leverage: float,
    initial_equity: float,
    ohlcv: pd.DataFrame,
) -> _SizingResolution:
    target_leverage = _validate_target_leverage(target_leverage)
    if "open" not in ohlcv.columns:
        raise OfflineSweepError("reference price basis requires OHLCV open column")
    try:
        reference_price = float(ohlcv["open"].iloc[0])
    except IndexError as exc:
        raise OfflineSweepError("reference price basis requires at least one OHLCV row") from exc
    if not math.isfinite(reference_price) or reference_price <= 0.0:
        raise OfflineSweepError(
            "reference price first_in_sample_open must be finite and positive"
        )
    if not math.isfinite(initial_equity) or initial_equity <= 0.0:
        raise OfflineSweepError("initial_equity must be finite and positive")
    resolved_order_size = target_leverage * initial_equity / reference_price
    if not math.isfinite(resolved_order_size) or resolved_order_size <= 0.0:
        raise OfflineSweepError("resolved_order_size must be finite and positive")
    return _SizingResolution(
        target_leverage=target_leverage,
        initial_equity=initial_equity,
        reference_price=reference_price,
        reference_price_basis=REFERENCE_PRICE_BASIS,
        resolved_order_size=resolved_order_size,
        sizing_model=SIZING_MODEL,
    )


def _sizing_context(
    execution_input: _ExecutionInput | None,
    sizing_mode: str,
    target_leverage: float,
) -> _SizingContext:
    sizing_mode = _validate_sizing_mode(sizing_mode)
    target_leverage = _validate_target_leverage(target_leverage)
    if execution_input is None:
        return _SizingContext(
            sizing_mode=sizing_mode,
            target_leverage=target_leverage,
            exact_resolution=None,
        )
    return _SizingContext(
        sizing_mode=sizing_mode,
        target_leverage=target_leverage,
        exact_resolution=_resolve_order_size(
            target_leverage=target_leverage,
            initial_equity=INITIAL_EQUITY,
            ohlcv=execution_input.ohlcv,
        ),
    )


def _format_sizing_value(value: float) -> str:
    return format(value, ".17g")


def _get_path(payload: dict[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise OfflineSweepError(f"missing required path: {dotted_path}")
        current = current[part]
    return current


def _hash_scope_payload(payload: dict[str, Any], scope: list[str]) -> dict[str, Any]:
    return {path: _get_path(payload, path) for path in scope}


def _canonical_hash(payload: dict[str, Any], scope: list[str]) -> str:
    return _sha256_prefixed(_hash_scope_payload(payload, scope))


def _validate_schema_file(path: Path, schema_path: Path) -> None:
    schema = _load_json(schema_path)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(_load_json(path)), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path)
        prefix = f"{location}: " if location else ""
        raise OfflineSweepError(f"{path}: {prefix}{first.message}")


def _validate_parent_inputs(
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for path in (strategy_spec_path, variant_manifest_path, sweep_plan_path):
        if not path.exists():
            raise OfflineSweepError(f"input file does not exist: {path}")

    _validate_schema_file(strategy_spec_path, DEFAULT_STRATEGY_SPEC_SCHEMA_PATH)
    _validate_schema_file(variant_manifest_path, DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH)
    _validate_schema_file(sweep_plan_path, DEFAULT_SWEEP_PLAN_SCHEMA_PATH)

    strategy_errors = validate_strategy_specs(strategy_specs_dir=strategy_spec_path.parent)
    if strategy_errors:
        raise OfflineSweepError("; ".join(strategy_errors))

    variant_errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=variant_manifest_path.parent,
        sweep_plans_dir=sweep_plan_path.parent,
        strategy_specs_dir=strategy_spec_path.parent,
    )
    if variant_errors:
        raise OfflineSweepError("; ".join(variant_errors))

    strategy_spec = _load_json(strategy_spec_path)
    manifest = _load_json(variant_manifest_path)
    sweep_plan = _load_json(sweep_plan_path)

    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    sweep_manifest_hash = sweep_plan["parent_variant_manifest"]["manifest_hash"]
    if manifest["parent_strategy_spec"]["strategy_spec_hash"] != strategy_hash:
        raise OfflineSweepError("parent Strategy Spec hash mismatch")
    if sweep_manifest_hash != manifest_hash:
        raise OfflineSweepError("parent manifest hash mismatch")

    pre_registration = manifest["population_governance"]["pre_registration"]
    if pre_registration["pre_registration_status"] != "frozen_for_sweep_planning":
        raise OfflineSweepError("manifest is not frozen_for_sweep_planning")

    manifest_count = manifest["population_governance"]["declared_population"][
        "committed_population_count"
    ]
    sweep_count = sweep_plan["trial_accounting"]["committed_population_count"]
    if manifest_count != sweep_count:
        raise OfflineSweepError("manifest/sweep committed denominator mismatch")
    if sweep_plan["parent_variant_manifest"]["manifest_committed_population_count"] != manifest_count:
        raise OfflineSweepError("sweep parent manifest committed count mismatch")

    manifest_ids = {row["variant_id"] for row in manifest["variant_assignments"]}
    selected_ids = set(sweep_plan["test_selection"]["selected_variant_ids"])
    excluded_ids = set(sweep_plan["test_selection"]["excluded_variant_ids"])
    outside = (selected_ids | excluded_ids) - manifest_ids
    if outside:
        raise OfflineSweepError(f"selected variant outside manifest: {sorted(outside)}")

    accounting = manifest["population_governance"]["multiple_testing_accounting"]
    if accounting["adaptive_search_used"] is not False:
        raise OfflineSweepError("adaptive search is forbidden")
    if sweep_plan["test_selection"]["post_hoc_addition_forbidden"] is not True:
        raise OfflineSweepError("post-hoc expansion is forbidden")
    if sweep_plan["validation_methods"]["no_runner_hooks"] is not True:
        raise OfflineSweepError("runner hooks are forbidden in sweep plan")
    if sweep_plan["validation_methods"]["no_formulas"] is not True:
        raise OfflineSweepError("formula execution is forbidden in sweep plan")

    _guard_no_runtime_contact_config(strategy_spec, manifest, sweep_plan)
    if not DEFAULT_RESULT_POPULATION_SCHEMA_PATH.exists():
        raise OfflineSweepError("result population schema is missing")
    return strategy_spec, manifest, sweep_plan


def _guard_no_runtime_contact_config(*payloads: dict[str, Any]) -> None:
    forbidden = (
        "broker",
        "exchange_instruction",
        "order_instruction",
        "paper_action",
        "live_action",
        "oms",
        "reconciliation",
        "risk_cap",
        "safe_mode",
        "kill_switch",
        "credentials",
        "private_key",
        "tier_4",
    )

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lower_key = str(key).lower()
                if lower_key in forbidden:
                    raise OfflineSweepError(f"protected runtime key forbidden: {path}.{key}")
                walk(child, f"{path}.{key}" if path else str(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}.{index}")

    for payload in payloads:
        walk(payload)


def _guard_output_dir(output_dir: Path | None, write_result_population: bool) -> Path | None:
    if not write_result_population:
        return None
    if output_dir is None:
        raise OfflineSweepError("--output-dir is required with --write-result-population")
    resolved = output_dir.resolve()
    canonical = CANONICAL_RESULT_POPULATIONS_DIR.resolve()
    if resolved == canonical or canonical in resolved.parents:
        raise OfflineSweepError("canonical research/result_populations output is disabled")
    return resolved


def _collect_declared_data_ref_fields(value: Any) -> set[str]:
    fields: set[str] = set()
    if isinstance(value, dict):
        if value.get("operand_type") == "data_ref":
            field = value.get("field") or value.get("ref")
            if (
                isinstance(field, str)
                and field not in ALLOWED_OHLCV_FIELDS
                and field not in ALLOWED_TIMESTAMP_DERIVED_FIELDS
            ):
                fields.add(field)
        for child in value.values():
            fields.update(_collect_declared_data_ref_fields(child))
    elif isinstance(value, list):
        for child in value:
            fields.update(_collect_declared_data_ref_fields(child))
    return fields


def _collect_declared_host_data_fields(strategy_spec: dict[str, Any]) -> set[str]:
    timeframe_and_data = strategy_spec.get("timeframe_and_data")
    host_data_refs = (
        timeframe_and_data.get("host_data_refs")
        if isinstance(timeframe_and_data, dict)
        else None
    )
    if not isinstance(host_data_refs, list):
        return set()
    fields: set[str] = set()
    for host_ref in host_data_refs:
        if not isinstance(host_ref, dict) or host_ref.get("stream") == "indicator_catalog":
            continue
        field = host_ref.get("field")
        if (
            isinstance(field, str)
            and field not in ALLOWED_OHLCV_FIELDS
            and field not in ALLOWED_TIMESTAMP_DERIVED_FIELDS
        ):
            fields.add(field)
    return fields


def _declared_non_ohlcv_columns(strategy_spec: dict[str, Any]) -> tuple[str, ...]:
    fields = _collect_declared_data_ref_fields(strategy_spec)
    fields.update(_collect_declared_host_data_fields(strategy_spec))
    return tuple(sorted(fields))


def _availability_catalog_entries() -> dict[str, list[dict[str, Any]]]:
    catalog = _load_json(DATA_FEATURE_AVAILABILITY_CATALOG_PATH)
    entries: dict[str, list[dict[str, Any]]] = {}
    for entry in catalog.get("entries", []):
        if not isinstance(entry, dict):
            continue
        feature_name = entry.get("feature_name")
        if isinstance(feature_name, str):
            entries.setdefault(feature_name, []).append(entry)
    return entries


def _availability_entry_for_feature(feature_name: str) -> dict[str, Any]:
    entries = _availability_catalog_entries().get(feature_name, [])
    if not entries:
        raise OfflineSweepError(f"unknown data-derived feature availability label: {feature_name}")
    full_history = [
        entry
        for entry in entries
        if entry.get("coverage_class") == "FULL_HISTORY_PUBLIC_ARCHIVE"
        and entry.get("compiler_visible") is True
    ]
    if full_history:
        return full_history[0]
    source_classes = sorted(
        str(entry.get("source_class"))
        for entry in entries
        if isinstance(entry.get("source_class"), str)
    )
    raise OfflineSweepError(
        f"{feature_name} has no FULL_HISTORY_PUBLIC_ARCHIVE availability source; "
        f"available_sources={source_classes}"
    )


def _data_availability_claim(strategy_spec: dict[str, Any]) -> dict[str, Any] | None:
    declared_fields = _declared_non_ohlcv_columns(strategy_spec)
    if not declared_fields:
        return None
    feature_sources = []
    for field in declared_fields:
        entry = _availability_entry_for_feature(field)
        source_class = entry.get("source_class")
        if not isinstance(source_class, str):
            raise OfflineSweepError(f"availability entry for {field} missing source_class")
        feature_sources.append(
            {
                "feature_name": field,
                "source_class": source_class,
                "condition_assertions": [
                    condition
                    for condition in entry.get("conditions", [])
                    if isinstance(condition, str) and condition
                ],
            }
        )
    return {
        "coverage_claim": "FULL_HISTORY",
        "feature_sources": feature_sources,
        "historical_dataset_overrides": [],
        "claim_notes": [
            "Generated by offline runner from declared non-OHLCV data_ref/host_data_refs.",
            "Claim is metadata only and does not authorize canonical evidence or execution.",
        ],
    }


def _variant_fixture_mode(variant: dict[str, Any]) -> str | None:
    reason = variant.get("status_reason")
    if isinstance(reason, str) and reason.startswith("runner_fixture:"):
        return reason.split(":", 1)[1]
    return None


def _synthetic_inputs(variant_id: str, deterministic_seed: int) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    seed_offset = int(hashlib.sha256(f"{variant_id}:{deterministic_seed}".encode()).hexdigest()[:4], 16)
    index = pd.date_range("2026-01-01", periods=48, freq="h", tz="UTC")
    base = 100.0 + (seed_offset % 11)
    close = [base + (i * 0.15) + ((i % 5) * 0.03) for i in range(len(index))]
    open_ = [price - 0.05 for price in close]
    high = [price + 0.2 for price in close]
    low = [price - 0.2 for price in close]
    ohlcv = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": [1000.0] * len(index)},
        index=index,
    )
    direction = 1.0 if seed_offset % 2 == 0 else -1.0
    signal = pd.Series(0.0, index=index)
    signal.iloc[3:28] = direction
    signal.iloc[28:] = 0.0
    funding = pd.DataFrame({"funding_rate": [0.0] * 6}, index=index[::8][:6])
    return signal, ohlcv, funding


def _run_synthetic_backtest(
    variant_id: str,
    deterministic_seed: int,
    sizing_mode: str,
    target_leverage: float,
) -> Any:
    signal, ohlcv, funding = _synthetic_inputs(variant_id, deterministic_seed)
    sizing = _resolve_order_size(
        target_leverage=target_leverage,
        initial_equity=INITIAL_EQUITY,
        ohlcv=ohlcv,
    )
    return run_backtest(
        signal=signal,
        ohlcv=ohlcv,
        funding=funding,
        fee_bps_taker=4.0,
        fee_bps_maker=2.0,
        slippage_bps=1.0,
        initial_equity=INITIAL_EQUITY,
        stream="klines",
        interval="1h",
        gaps_path=REPO_ROOT / "tools" / "research_runner" / "_nonexistent_empty_gaps.json",
        entry_fee_side="taker",
        exit_fee_side="taker",
        funding_cost_mode="off",
        funding_notional_mode="entry_price",
        order_size=sizing.resolved_order_size,
        sizing_mode=sizing_mode,
        target_leverage=target_leverage,
        fill_mode="complete",
        slippage_model="fixed_bps",
        liquidation_mode="zero_equity",
        mark_price_source="close",
        bar_path_assumption="next_open_close_mark",
    )


def _load_ohlcv_input(
    path: Path,
    *,
    timeframe: str,
    expected_delta: pd.Timedelta,
    min_rows: int,
    additional_columns: tuple[str, ...] = (),
) -> pd.DataFrame:
    if not path.exists():
        raise OfflineSweepError(f"{timeframe} OHLCV input does not exist: {path}")
    if path.suffix.lower() != ".csv":
        raise OfflineSweepError(f"canonical {timeframe} OHLCV input must be a CSV fixture/input")
    frame = pd.read_csv(path)
    timestamp = _select_ohlcv_timestamp(frame)
    required_columns = set(REQUIRED_OHLCV_COLUMNS)
    missing = required_columns - set(frame.columns)
    if missing:
        raise OfflineSweepError(f"{timeframe} OHLCV input missing columns: {sorted(missing)}")
    missing_declared = set(additional_columns) - set(frame.columns)
    if missing_declared:
        raise OfflineSweepError(
            f"{timeframe} input missing declared non-OHLCV columns: {sorted(missing_declared)}"
        )
    frame["timestamp"] = timestamp
    frame = frame.set_index("timestamp").sort_index()
    retained_columns = [*REQUIRED_OHLCV_COLUMNS, *additional_columns]
    frame = frame[retained_columns].astype(float)
    if frame.index.has_duplicates:
        raise OfflineSweepError(f"{timeframe} OHLCV input must have no duplicate timestamps")
    if len(frame.index) < min_rows:
        raise OfflineSweepError(
            f"{timeframe} OHLCV input must contain at least {min_rows} rows"
        )
    deltas = frame.index.to_series().diff().dropna().unique()
    if len(deltas) != 1 or deltas[0] != expected_delta:
        raise OfflineSweepError(f"canonical OHLCV input must be exactly {timeframe}-spaced")
    return frame


def _load_15m_ohlcv_input(
    path: Path,
    additional_columns: tuple[str, ...] = (),
) -> pd.DataFrame:
    return _load_ohlcv_input(
        path,
        timeframe="15m",
        expected_delta=pd.Timedelta(minutes=15),
        min_rows=20,
        additional_columns=additional_columns,
    )


def _load_4h_ohlcv_input(
    path: Path,
    additional_columns: tuple[str, ...] = (),
) -> pd.DataFrame:
    return _load_ohlcv_input(
        path,
        timeframe="4h",
        expected_delta=pd.Timedelta(hours=4),
        min_rows=20,
        additional_columns=additional_columns,
    )


def _canonical_1d_repo_path(value: Any, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise OfflineSweepError(f"canonical 1d {label} must be a non-empty POSIX path")
    logical = PurePosixPath(value)
    if logical.is_absolute() or ".." in logical.parts:
        raise OfflineSweepError(f"canonical 1d {label} must remain repository-relative")
    return logical


def _canonical_1d_configured_path(path: Path, label: str) -> PurePosixPath:
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise OfflineSweepError(
            f"canonical 1d configured {label} must remain under the repository root"
        ) from exc
    return _canonical_1d_repo_path(relative.as_posix(), label)


def _path_is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and is_junction())


def _resolve_canonical_1d_path(
    logical: PurePosixPath,
    *,
    label: str,
) -> Path:
    if _path_is_link(REPO_ROOT):
        raise OfflineSweepError("canonical 1d repository root must not be a link")
    try:
        root = REPO_ROOT.resolve(strict=True)
        candidate = root.joinpath(*logical.parts)
        current = root
        for part in logical.parts:
            current = current / part
            if _path_is_link(current):
                raise OfflineSweepError(f"canonical 1d {label} must not traverse a link")
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise OfflineSweepError(f"canonical 1d {label} does not exist: {logical}") from exc
    if resolved == root or root not in resolved.parents:
        raise OfflineSweepError(f"canonical 1d {label} escapes the repository root")
    if not resolved.is_file():
        raise OfflineSweepError(f"canonical 1d {label} must be a file")
    return resolved


def _canonical_1d_execution_input(
    additional_columns: tuple[str, ...] = (),
) -> _ExecutionInput:
    catalog_logical = _canonical_1d_configured_path(
        DEFAULT_1D_CATALOG_SLICE_PATH,
        "catalog path",
    )
    catalog_path = _resolve_canonical_1d_path(catalog_logical, label="catalog")
    validator_logical = _canonical_1d_configured_path(
        DEFAULT_1D_VALIDATOR_PATH,
        "validator path",
    )
    validator_path = _resolve_canonical_1d_path(validator_logical, label="validator")

    catalog_bytes = catalog_path.read_bytes()
    catalog_sha256 = _sha256_file_hex(catalog_path)
    if catalog_sha256 != OFFICIAL_1D_CATALOG_ARTIFACT_SHA256:
        raise OfflineSweepError("canonical 1d catalog SHA256 does not match official identity")
    try:
        catalog = json.loads(catalog_bytes)
    except (TypeError, ValueError) as exc:
        raise OfflineSweepError("canonical 1d catalog is not valid JSON") from exc
    if not isinstance(catalog, dict):
        raise OfflineSweepError("canonical 1d catalog root must be an object")

    if catalog.get("dataset_id") != CANONICAL_1D_DATASET_ID:
        raise OfflineSweepError("canonical 1d catalog dataset_id mismatch")
    if catalog.get("snapshot_version") != CANONICAL_1D_SNAPSHOT_VERSION:
        raise OfflineSweepError("canonical 1d catalog snapshot_version mismatch")
    if catalog.get("timeframe") != "1d":
        raise OfflineSweepError("canonical 1d catalog timeframe mismatch")
    if catalog.get("catalog_status") != "valid_offline_provenance_tracked_snapshot":
        raise OfflineSweepError("canonical 1d catalog status is not valid")
    if catalog.get("unresolved_policy") != "reject":
        raise OfflineSweepError("canonical 1d catalog must use unresolved_policy=reject")
    if catalog.get("source", {}).get("method") != (
        "existing local public archive snapshot; no fetch performed by this package"
    ):
        raise OfflineSweepError("canonical 1d source posture must be the registered direct snapshot")
    if catalog.get("source", {}).get("credentials_used") is not False:
        raise OfflineSweepError("canonical 1d source must be public and credential-free")

    source_logical = _canonical_1d_repo_path(catalog.get("path"), "source path")
    source_path = _resolve_canonical_1d_path(source_logical, label="source")
    pre_read_source_sha256 = _sha256_file_hex(source_path)
    pre_read_source_size = source_path.stat().st_size
    if pre_read_source_sha256 != OFFICIAL_1D_SOURCE_SHA256:
        raise OfflineSweepError("canonical 1d source SHA256 does not match official identity")
    if pre_read_source_size != OFFICIAL_1D_SOURCE_BYTE_LENGTH:
        raise OfflineSweepError("canonical 1d source byte length does not match official identity")

    try:
        rebuilt_catalog = build_1d_lineage(
            source_path,
            logical_path=source_logical.as_posix(),
            expected_sha256=OFFICIAL_1D_SOURCE_SHA256,
        )
    except Exception as exc:
        raise OfflineSweepError(f"canonical 1d lineage validation failed: {exc}") from exc
    if canonical_1d_catalog_bytes(rebuilt_catalog) != catalog_bytes:
        raise OfflineSweepError("canonical 1d catalog does not match validated source lineage")

    try:
        source_frame = pd.read_parquet(source_path)
    except Exception as exc:
        raise OfflineSweepError(f"canonical 1d source read failed after validation: {exc}") from exc
    if list(source_frame.columns) != CANONICAL_1D_SOURCE_COLUMNS:
        raise OfflineSweepError("canonical 1d source columns changed after validation")
    if len(source_frame) != OFFICIAL_1D_ROW_COUNT:
        raise OfflineSweepError("canonical 1d source row count does not match official identity")
    missing_declared = set(additional_columns) - set(source_frame.columns)
    if missing_declared:
        raise OfflineSweepError(
            "canonical 1d source missing declared non-OHLCV columns: "
            f"{sorted(missing_declared)}"
        )

    timestamps = pd.to_datetime(
        source_frame["open_time_ms"].astype("int64"),
        unit="ms",
        utc=True,
    )
    retained_columns = [*REQUIRED_OHLCV_COLUMNS, *additional_columns]
    ohlcv = source_frame[retained_columns].astype(float).copy()
    ohlcv.index = pd.DatetimeIndex(timestamps, name="timestamp")
    if ohlcv.index.has_duplicates or not ohlcv.index.is_monotonic_increasing:
        raise OfflineSweepError("canonical 1d source timestamps changed after validation")
    deltas = ohlcv.index.to_series().diff().dropna().unique()
    if len(deltas) != 1 or deltas[0] != pd.Timedelta(milliseconds=CANONICAL_1D_CADENCE_MS):
        raise OfflineSweepError("canonical 1d source cadence changed after validation")

    post_read_source_sha256 = _sha256_file_hex(source_path)
    post_read_source_size = source_path.stat().st_size
    post_read_catalog_sha256 = _sha256_file_hex(catalog_path)
    if (
        post_read_source_sha256 != pre_read_source_sha256
        or post_read_source_size != pre_read_source_size
    ):
        raise OfflineSweepError("canonical 1d source mutated after validation/read")
    if post_read_catalog_sha256 != catalog_sha256:
        raise OfflineSweepError("canonical 1d catalog mutated after validation/read")

    coverage = catalog["coverage"]
    findings = catalog["findings"]
    validator_sha256 = _sha256_file_hex(validator_path)
    columns_schema_identity = _sha256_prefixed(CANONICAL_1D_SOURCE_COLUMNS)
    validation_identity = _sha256_prefixed(
        {
            "catalog_sha256": f"sha256:{catalog_sha256}",
            "validator_path": validator_logical.as_posix(),
            "validator_sha256": f"sha256:{validator_sha256}",
            "catalog_matches_rebuilt_lineage": True,
        }
    )
    input_identity = {
        "canonical_route": "1d",
        "dataset_id": catalog["dataset_id"],
        "snapshot_version": catalog["snapshot_version"],
        "catalog_path": catalog_logical.as_posix(),
        "catalog_sha256": f"sha256:{catalog_sha256}",
        "source_path": source_logical.as_posix(),
        "source_raw_sha256": f"sha256:{post_read_source_sha256}",
        "source_byte_length": post_read_source_size,
        "row_count": len(ohlcv),
        "coverage_start_utc": coverage["start_open_utc"],
        "coverage_end_open_utc": coverage["end_open_utc"],
        "coverage_end_close_utc": coverage["end_close_utc"],
        "timeframe": "1d",
        "cadence_ms": CANONICAL_1D_CADENCE_MS,
        "timezone": "UTC",
        "columns": CANONICAL_1D_SOURCE_COLUMNS,
        "columns_schema_identity": columns_schema_identity,
        "duplicate_policy": findings["duplicate_policy"],
        "duplicate_row_count": findings["duplicate_row_count"],
        "gap_policy": findings["gap_policy"],
        "gap_count": findings["gap_count"],
        "missing_bar_count": findings["missing_bar_count"],
        "partial_window_posture": "completed_bars_only_reject_partial",
        "open_or_incomplete_bar_count": findings["open_or_incomplete_bar_count"],
        "source_type": "direct_public_archive_snapshot",
        "source_identity": catalog["source"],
        "parent_identity": None,
        "derivation_identity": None,
        "validation_identity": validation_identity,
        "validation_artifact_kind": "catalog_slice_with_embedded_validation_findings",
        "validator_path": validator_logical.as_posix(),
        "validator_sha256": f"sha256:{validator_sha256}",
    }
    input_identity_hash = _sha256_prefixed(input_identity)
    identity_note = "canonical_1d_input_identity=" + json.dumps(
        input_identity,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _ExecutionInput(
        mode="canonical_1d_public_archive_snapshot",
        execution_provenance_class="canonical_direct_real_data",
        ohlcv=ohlcv,
        funding=_zero_funding_for_ohlcv(ohlcv),
        timeframe="1d",
        data_catalog_ref=(
            f"{catalog_logical.as_posix()}#sha256:{catalog_sha256}"
        ),
        data_slice_identity=(
            f"{CANONICAL_1D_DATASET_ID}:identity_{input_identity_hash}"
        ),
        environment_summary=[
            "canonical_1d_public_archive_snapshot_input",
            "execution_provenance_class=canonical_direct_real_data",
            "offline_only_no_exchange_api",
        ],
        data_coverage_notes=[
            CANONICAL_1D_PROVENANCE_MODE_NOTE,
            identity_note,
            f"1d_validation_identity={validation_identity}",
            "offline only",
            "no exchange/API contact",
            "not live/paper input",
        ],
        funding_input_identity=_funding_input_identity_off(),
    )


def _parse_ohlcv_timestamp_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column == "open_time_ms":
        numeric = pd.to_numeric(frame[column], errors="coerce")
        if numeric.isna().any() or not numeric.map(lambda value: float(value).is_integer()).all():
            raise OfflineSweepError("15m OHLCV input open_time_ms contains invalid epoch milliseconds")
        parsed = pd.to_datetime(numeric.astype("int64"), unit="ms", utc=True, errors="coerce")
    else:
        parsed = pd.to_datetime(frame[column], utc=True, errors="coerce")
    if pd.Series(parsed).isna().any():
        raise OfflineSweepError(f"15m OHLCV input {column} contains invalid timestamps")
    return pd.Series(parsed, index=frame.index)


def _select_ohlcv_timestamp(frame: pd.DataFrame) -> pd.Series:
    ordered_columns = ("timestamp", "open_time", "open_time_ms")
    present = [column for column in ordered_columns if column in frame.columns]
    if not present:
        raise OfflineSweepError(
            "15m OHLCV input must include one of: timestamp, open_time, open_time_ms"
        )
    parsed = {column: _parse_ohlcv_timestamp_series(frame, column) for column in present}
    selected_column = present[0]
    selected = parsed[selected_column]
    for column, candidate in parsed.items():
        if column == selected_column:
            continue
        if (selected != candidate).any():
            raise OfflineSweepError(
                f"15m OHLCV input conflicting timestamp columns: {selected_column} and {column}"
            )
    return selected


def _zero_funding_for_ohlcv(ohlcv: pd.DataFrame) -> pd.DataFrame:
    funding_index = pd.date_range(ohlcv.index[0], ohlcv.index[-1], freq="8h", tz="UTC")
    if len(funding_index) == 0:
        funding_index = pd.DatetimeIndex([ohlcv.index[0]])
    return pd.DataFrame({"funding_rate": [0.0] * len(funding_index)}, index=funding_index)


def _slice_funding_for_window(funding: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return funding.loc[(funding.index >= start) & (funding.index < end)].copy()


def _slice_execution_input(
    execution_input: _ExecutionInput,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    window_label: str,
) -> _ExecutionInput:
    ohlcv = execution_input.ohlcv.loc[
        (execution_input.ohlcv.index >= start) & (execution_input.ohlcv.index < end)
    ].copy()
    if len(ohlcv) < 2:
        raise OfflineSweepError(f"{window_label} requires at least two OHLCV rows")
    return _ExecutionInput(
        mode=f"{execution_input.mode}:{window_label}",
        execution_provenance_class=execution_input.execution_provenance_class,
        ohlcv=ohlcv,
        funding=_slice_funding_for_window(execution_input.funding, ohlcv.index[0], end),
        timeframe=execution_input.timeframe,
        data_catalog_ref=execution_input.data_catalog_ref,
        data_slice_identity=execution_input.data_slice_identity,
        environment_summary=execution_input.environment_summary,
        data_coverage_notes=execution_input.data_coverage_notes,
        funding_input_identity=execution_input.funding_input_identity,
    )


def _slice_execution_input_for_evaluation_end(
    execution_input: _ExecutionInput,
    evaluation_end: pd.Timestamp,
) -> _ExecutionInput:
    """Truncate execution input to bars strictly before evaluation_end.

    Eliminates post-window OHLCV bars and funding entries so the backtest
    cannot open trades or accumulate costs after the evaluation boundary.
    The warmup prefix (bars before evaluation_start) is preserved in full
    so that rolling indicator state is correctly established before the
    evaluation window opens.
    """
    ohlcv = execution_input.ohlcv.loc[execution_input.ohlcv.index < evaluation_end].copy()
    if len(ohlcv) < 2:
        raise OfflineSweepError(
            f"after truncating to evaluation_end ({evaluation_end.isoformat()}), "
            "fewer than 2 OHLCV rows remain — cannot run backtest"
        )
    return _ExecutionInput(
        mode=execution_input.mode,
        execution_provenance_class=execution_input.execution_provenance_class,
        ohlcv=ohlcv,
        funding=_slice_funding_for_window(execution_input.funding, ohlcv.index[0], evaluation_end),
        timeframe=execution_input.timeframe,
        data_catalog_ref=execution_input.data_catalog_ref,
        data_slice_identity=execution_input.data_slice_identity,
        environment_summary=execution_input.environment_summary,
        data_coverage_notes=execution_input.data_coverage_notes,
        funding_input_identity=execution_input.funding_input_identity,
    )


def _build_walkforward_windows(
    index: pd.DatetimeIndex,
    *,
    in_sample_bars: int,
    out_of_sample_bars: int,
    step_bars: int | None = None,
    max_windows: int | None = None,
) -> list[_WalkForwardWindow]:
    if not isinstance(index, pd.DatetimeIndex):
        raise OfflineSweepError("walk-forward input index must be a DatetimeIndex")
    if index.tz is None or str(index.tz) not in ("UTC", "utc", "Etc/UTC"):
        raise OfflineSweepError("walk-forward input index must be UTC-localized")
    if not index.is_monotonic_increasing or index.has_duplicates:
        raise OfflineSweepError("walk-forward input index must be monotonic with no duplicates")
    if in_sample_bars <= 1:
        raise OfflineSweepError("--walkforward-is-bars must be greater than 1")
    if out_of_sample_bars <= 1:
        raise OfflineSweepError("--walkforward-oos-bars must be greater than 1")

    step = step_bars if step_bars is not None else in_sample_bars + out_of_sample_bars
    if step < in_sample_bars + out_of_sample_bars:
        raise OfflineSweepError(
            "--walkforward-step-bars must be at least IS+OOS bars to preserve non-overlap"
        )
    if max_windows is not None and max_windows <= 0:
        raise OfflineSweepError("--walkforward-max-windows must be positive when provided")

    total_required = in_sample_bars + out_of_sample_bars
    windows: list[_WalkForwardWindow] = []
    start_pos = 0
    while start_pos + total_required <= len(index):
        is_start_pos = start_pos
        is_end_pos = start_pos + in_sample_bars
        oos_start_pos = is_end_pos
        oos_end_pos = oos_start_pos + out_of_sample_bars
        window_number = len(windows) + 1
        windows.append(
            _WalkForwardWindow(
                window_id=f"WF-{window_number:04d}",
                window_index=window_number,
                in_sample_start=index[is_start_pos],
                in_sample_end_exclusive=index[is_end_pos],
                out_of_sample_start=index[oos_start_pos],
                out_of_sample_end_exclusive=(
                    index[oos_end_pos] if oos_end_pos < len(index) else index[-1] + (index[-1] - index[-2])
                ),
                in_sample_row_count=in_sample_bars,
                out_of_sample_row_count=out_of_sample_bars,
            )
        )
        if max_windows is not None and len(windows) >= max_windows:
            break
        start_pos += step
    if not windows:
        raise OfflineSweepError("walk-forward input does not contain enough rows for one IS/OOS window")
    return windows


def _canonical_15m_execution_input(
    ohlcv_input_path: Path | None,
    additional_columns: tuple[str, ...] = (),
) -> _ExecutionInput:
    if ohlcv_input_path is None:
        raise OfflineSweepError("--ohlcv-input is required with --canonical-15m")
    resolved = ohlcv_input_path.resolve()
    ohlcv = _load_15m_ohlcv_input(resolved, additional_columns)
    digest = _sha256_file(resolved)
    declared_note = (
        [f"declared_non_ohlcv_columns={','.join(additional_columns)}"]
        if additional_columns
        else []
    )
    return _ExecutionInput(
        mode="canonical_15m_fixture",
        execution_provenance_class="fixture_offline",
        ohlcv=ohlcv,
        funding=_zero_funding_for_ohlcv(ohlcv),
        timeframe="15m",
        data_catalog_ref=CANONICAL_15M_DATA_CATALOG_REF,
        data_slice_identity=f"csv_fixture:{digest}",
        environment_summary=[
            "canonical_15m_ohlcv_fixture_input",
            "execution_provenance_class=fixture_offline",
            "offline_only_no_exchange_api",
        ],
        data_coverage_notes=[
            "15m OHLCV test fixture/input",
            *declared_note,
            "offline only",
            "no exchange/API contact",
            "not production data",
            "not live/paper input",
        ],
        funding_input_identity=_funding_input_identity_off(),
    )


def _required_non_empty_string(payload: dict[str, Any], dotted_path: str) -> str:
    value = _get_path(payload, dotted_path)
    if not isinstance(value, str) or not value:
        raise OfflineSweepError(f"missing or malformed required D4 provenance path: {dotted_path}")
    return value


def _required_int(payload: dict[str, Any], dotted_path: str) -> int:
    value = _get_path(payload, dotted_path)
    if not isinstance(value, int) or value < 0:
        raise OfflineSweepError(f"missing or malformed required D4 provenance path: {dotted_path}")
    return value


def _required_list(payload: dict[str, Any], dotted_path: str) -> list[Any]:
    value = _get_path(payload, dotted_path)
    if not isinstance(value, list):
        raise OfflineSweepError(f"missing or malformed required D4 provenance path: {dotted_path}")
    return value


def _require_path_exists(path: Path, flag_name: str) -> None:
    if not path.exists():
        raise OfflineSweepError(f"{flag_name} does not exist: {path}")


def _parse_metadata_timestamp(value: str, label: str) -> pd.Timestamp:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise OfflineSweepError(f"invalid metadata timestamp: {label}")
    return pd.Timestamp(parsed)


def _d4_catalog_execution_input(
    ohlcv_input_path: Path | None,
    d4_catalog_slice_path: Path | None,
    d2_import_report_path: Path | None,
    additional_columns: tuple[str, ...] = (),
) -> _ExecutionInput:
    if d4_catalog_slice_path is None:
        raise OfflineSweepError("--d4-catalog-slice is required for D4 provenance mode")
    if d2_import_report_path is None:
        raise OfflineSweepError("--d2-import-report is required for D4 provenance mode")
    if not d4_catalog_slice_path.exists():
        raise OfflineSweepError(f"D4 catalog slice does not exist: {d4_catalog_slice_path}")
    if not d2_import_report_path.exists():
        raise OfflineSweepError(f"D2 import report does not exist: {d2_import_report_path}")

    catalog = _load_json(d4_catalog_slice_path)
    import_report = _load_json(d2_import_report_path)
    catalog_ref = _required_non_empty_string(catalog, "catalog_ref")
    data_slice_identity = _required_non_empty_string(catalog, "slice_identity.data_slice_identity")
    d3_validation_report_sha256 = _required_non_empty_string(catalog, "validation_report.sha256")
    validation_status = _required_non_empty_string(catalog, "validation_report.status")
    row_count = _required_int(catalog, "range.row_count")
    expected_row_count = _required_int(catalog, "range.expected_row_count")
    start_utc = _required_non_empty_string(catalog, "range.start_utc")
    end_utc = _required_non_empty_string(catalog, "range.end_utc")
    gap_count = _required_int(catalog, "gap_summary.gap_count")
    missing_bar_count = _required_int(catalog, "gap_summary.missing_bar_count")
    gaps = _required_list(catalog, "gap_summary.gaps")
    duplicate_group_count = _required_int(catalog, "duplicate_summary.duplicate_group_count")
    duplicate_row_count = _required_int(catalog, "duplicate_summary.duplicate_row_count")
    duplicates = _required_list(catalog, "duplicate_summary.duplicates")
    raw_source_sha256 = _required_non_empty_string(catalog, "source.raw_source_sha256")
    normalized_sha256 = _required_non_empty_string(catalog, "normalized.sha256")
    import_raw_sha256 = _required_non_empty_string(import_report, "source.sha256")
    import_normalized_sha256 = _required_non_empty_string(import_report, "normalized.sha256")

    if catalog_ref == CANONICAL_15M_DATA_CATALOG_REF:
        raise OfflineSweepError("D4 provenance mode cannot use fixture data_catalog_ref")
    if data_slice_identity.startswith("csv_fixture:"):
        raise OfflineSweepError("D4 provenance mode cannot use fixture data_slice_identity")
    if validation_status != "PASS":
        raise OfflineSweepError("D4 provenance mode requires D3 validation status PASS")
    if row_count != expected_row_count:
        raise OfflineSweepError("D4 provenance mode requires row_count to equal expected_row_count")
    if gap_count != 0 or missing_bar_count != 0 or gaps:
        raise OfflineSweepError("D4 provenance mode requires gap-free D4 catalog facts")
    if duplicate_group_count != 0 or duplicate_row_count != 0 or duplicates:
        raise OfflineSweepError("D4 provenance mode requires duplicate-free D4 catalog facts")
    if import_raw_sha256 != raw_source_sha256:
        raise OfflineSweepError("D2 import report raw source SHA256 does not match D4 catalog")
    if import_normalized_sha256 != normalized_sha256:
        raise OfflineSweepError("D2 import report normalized SHA256 does not match D4 catalog")

    d2_import_report_sha256 = _sha256_file_hex(d2_import_report_path)
    d4_catalog_artifact_sha256 = _sha256_file_hex(d4_catalog_slice_path)
    execution_input = _canonical_15m_execution_input(ohlcv_input_path, additional_columns)
    return _ExecutionInput(
        mode="canonical_15m_d4_provenance",
        execution_provenance_class="canonical_real_data",
        ohlcv=execution_input.ohlcv,
        funding=execution_input.funding,
        timeframe=execution_input.timeframe,
        data_catalog_ref=catalog_ref,
        data_slice_identity=data_slice_identity,
        environment_summary=[
            "canonical_15m_ohlcv_input",
            "d4_catalog_slice_provenance",
            "execution_provenance_class=canonical_real_data",
            "offline_only_no_exchange_api",
        ],
        data_coverage_notes=[
            D4_PROVENANCE_MODE_NOTE,
            *(
                [f"declared_non_ohlcv_columns={','.join(additional_columns)}"]
                if additional_columns
                else []
            ),
            "offline only",
            "no exchange/API contact",
            "not live/paper input",
            f"d3_validation_report_sha256={d3_validation_report_sha256}",
            f"d2_import_report_sha256={d2_import_report_sha256}",
            f"d4_catalog_artifact_sha256={d4_catalog_artifact_sha256}",
            f"row_count={row_count}",
            f"expected_row_count={expected_row_count}",
            f"start_utc={start_utc}",
            f"end_utc={end_utc}",
            f"gap_count={gap_count}",
            f"missing_bar_count={missing_bar_count}",
            f"gaps={json.dumps(gaps, sort_keys=True, separators=(',', ':'))}",
            f"duplicate_group_count={duplicate_group_count}",
            f"duplicate_row_count={duplicate_row_count}",
            f"duplicates={json.dumps(duplicates, sort_keys=True, separators=(',', ':'))}",
            f"raw_source_sha256={raw_source_sha256}",
            f"normalized_sha256={normalized_sha256}",
        ],
        funding_input_identity=_funding_input_identity_off(),
    )


def _bind_research_feature_input(
    execution_input: _ExecutionInput,
    *,
    ohlcv_input_path: Path,
    d4_catalog_slice_path: Path,
    feature_manifest_path: Path,
    feature_input_path: Path,
    requested_feature_names: tuple[str, ...],
) -> _ExecutionInput:
    """Thin transitional consumer of the generic feature-table resolver."""

    catalog = _load_json(d4_catalog_slice_path)
    if _required_non_empty_string(catalog, "symbol") != "BTCUSDT":
        raise OfflineSweepError("research feature input requires the BTCUSDT D4 parent")
    if _required_non_empty_string(catalog, "venue") != "Binance":
        raise OfflineSweepError("research feature input requires the Binance D4 parent")
    if _required_non_empty_string(catalog, "timeframe") != "15m":
        raise OfflineSweepError("research feature input requires the 15m D4 parent")
    if _required_non_empty_string(catalog, "market_type") not in {
        "USDT-M perpetual",
        "USD-M perpetual",
    }:
        raise OfflineSweepError("research feature input requires the USD-M perpetual D4 parent")
    start = _parse_metadata_timestamp(
        _required_non_empty_string(catalog, "range.start_utc"),
        "D4 range.start_utc",
    )
    last_open = _parse_metadata_timestamp(
        _required_non_empty_string(catalog, "range.end_utc"),
        "D4 range.end_utc",
    )

    def iso_ms(value: pd.Timestamp) -> str:
        return value.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S.000Z")

    try:
        resolved = resolve_research_feature_table(
            base_frame=execution_input.ohlcv,
            base_input_path=ohlcv_input_path.resolve(),
            base_data_slice_identity=execution_input.data_slice_identity,
            base_normalized_sha256=_required_non_empty_string(
                catalog, "normalized.sha256"
            ),
            base_market_identity={
                "venue": "Binance",
                "market_type": "USD-M perpetual",
                "symbol": "BTCUSDT",
            },
            base_timeframe="15m",
            base_coverage_start_utc_inclusive=iso_ms(start),
            base_coverage_end_utc_exclusive=iso_ms(
                last_open + pd.Timedelta(minutes=15)
            ),
            feature_manifest_path=feature_manifest_path,
            feature_csv_path=feature_input_path,
            requested_feature_names=requested_feature_names,
        )
    except ResearchFeatureTableError as exc:
        raise OfflineSweepError(f"research feature-table resolution failed: {exc}") from exc
    return _ExecutionInput(
        mode=execution_input.mode + ":research_feature_table",
        execution_provenance_class=execution_input.execution_provenance_class,
        ohlcv=resolved.joined_frame,
        funding=execution_input.funding,
        timeframe=execution_input.timeframe,
        data_catalog_ref=execution_input.data_catalog_ref,
        data_slice_identity=resolved.composite_data_slice_identity,
        environment_summary=[
            *execution_input.environment_summary,
            "research_feature_table_compatibility_consumer",
        ],
        data_coverage_notes=[
            *execution_input.data_coverage_notes,
            *resolved.provenance_notes,
        ],
        funding_input_identity=execution_input.funding_input_identity,
    )


def _canonical_4h_execution_input(
    ohlcv_input_path: Path | None,
    d4h_catalog_slice_path: Path | None,
    d4h_validation_report_path: Path | None,
    d4h_derivation_report_path: Path | None,
    additional_columns: tuple[str, ...] = (),
) -> _ExecutionInput:
    if ohlcv_input_path is None:
        raise OfflineSweepError("--ohlcv-input is required with --canonical-4h")
    catalog_path = d4h_catalog_slice_path or DEFAULT_4H_CATALOG_SLICE_PATH
    validation_path = d4h_validation_report_path or DEFAULT_4H_VALIDATION_REPORT_PATH
    derivation_path = d4h_derivation_report_path or DEFAULT_4H_DERIVATION_REPORT_PATH
    _require_path_exists(catalog_path, "--d4h-catalog-slice")
    _require_path_exists(validation_path, "--d4h-validation-report")
    _require_path_exists(derivation_path, "--d4h-derivation-report")

    catalog = _load_json(catalog_path)
    validation_report = _load_json(validation_path)
    derivation_report = _load_json(derivation_path)

    catalog_ref = _required_non_empty_string(catalog, "catalog_ref")
    data_slice_identity = _required_non_empty_string(catalog, "slice_identity.data_slice_identity")
    normalized_sha256 = _required_non_empty_string(catalog, "normalized.sha256")
    validation_report_sha256 = _required_non_empty_string(catalog, "validation_report.sha256")
    validation_status = _required_non_empty_string(catalog, "validation_report.status")
    derivation_report_sha256 = _required_non_empty_string(catalog, "derivation_report.sha256")
    parent_data_slice_identity = _required_non_empty_string(catalog, "parent.data_slice_identity")
    parent_normalized_sha256 = _required_non_empty_string(catalog, "parent.normalized_sha256")
    parent_validation_report_sha256 = _required_non_empty_string(
        catalog,
        "parent.validation_report_sha256",
    )
    resampling_method = _required_non_empty_string(catalog, "derivation.method")
    resampling_version = _required_non_empty_string(catalog, "resampling_version")
    row_count = _required_int(catalog, "range.row_count")
    expected_row_count = _required_int(catalog, "range.expected_row_count")
    start_utc = _required_non_empty_string(catalog, "range.start_utc")
    end_utc = _required_non_empty_string(catalog, "range.end_utc")
    gap_count = _required_int(catalog, "gap_summary.gap_count")
    missing_bar_count = _required_int(catalog, "gap_summary.missing_bar_count")
    gaps = _required_list(catalog, "gap_summary.gaps")
    duplicate_group_count = _required_int(catalog, "duplicate_summary.duplicate_group_count")
    duplicate_row_count = _required_int(catalog, "duplicate_summary.duplicate_row_count")
    duplicates = _required_list(catalog, "duplicate_summary.duplicates")
    partial_window_count = _required_int(validation_report, "validation.partial_window_count")

    if catalog.get("timeframe") != "4h" or validation_report.get("timeframe") != "4h":
        raise OfflineSweepError("canonical 4h mode requires 4h catalog and validation metadata")
    if catalog.get("source_type") != "derived_offline_resample":
        raise OfflineSweepError("canonical 4h mode requires derived_offline_resample source_type")
    if validation_status != "PASS" or _get_path(validation_report, "validation.status") != "PASS":
        raise OfflineSweepError("canonical 4h mode requires validation status PASS")
    if validation_report.get("ok") is not True or derivation_report.get("ok") is not True:
        raise OfflineSweepError("canonical 4h mode requires ok=true validation and derivation reports")
    if row_count != expected_row_count:
        raise OfflineSweepError("canonical 4h mode requires row_count to equal expected_row_count")
    if data_slice_identity == OFFICIAL_4H_DATA_SLICE_IDENTITY and row_count != OFFICIAL_4H_ROW_COUNT:
        raise OfflineSweepError("canonical 4h mode requires row_count 13758")
    if gap_count != 0 or missing_bar_count != 0 or gaps:
        raise OfflineSweepError("canonical 4h mode requires gap-free catalog facts")
    if duplicate_group_count != 0 or duplicate_row_count != 0 or duplicates:
        raise OfflineSweepError("canonical 4h mode requires duplicate-free catalog facts")
    if partial_window_count != 0:
        raise OfflineSweepError("canonical 4h mode requires zero partial windows")
    if _required_non_empty_string(validation_report, "normalized.sha256") != normalized_sha256:
        raise OfflineSweepError("4h validation report normalized SHA256 does not match catalog")
    if _required_non_empty_string(derivation_report, "output.sha256") != normalized_sha256:
        raise OfflineSweepError("4h derivation report output SHA256 does not match catalog")
    if _required_non_empty_string(derivation_report, "parent.data_slice_identity") != parent_data_slice_identity:
        raise OfflineSweepError("4h derivation parent data slice identity does not match catalog")
    if _required_non_empty_string(derivation_report, "parent.normalized_sha256") != parent_normalized_sha256:
        raise OfflineSweepError("4h derivation parent normalized SHA256 does not match catalog")

    actual_validation_sha256 = _sha256_file_hex(validation_path)
    actual_derivation_sha256 = _sha256_file_hex(derivation_path)
    if actual_validation_sha256 != validation_report_sha256:
        raise OfflineSweepError("4h validation report SHA256 does not match catalog")
    if actual_derivation_sha256 != derivation_report_sha256:
        raise OfflineSweepError("4h derivation report SHA256 does not match catalog")

    resolved = ohlcv_input_path.resolve()
    actual_csv_sha256 = _sha256_file_hex(resolved)
    if actual_csv_sha256 != normalized_sha256:
        raise OfflineSweepError("4h OHLCV CSV SHA256 does not match catalog")
    ohlcv = _load_4h_ohlcv_input(resolved, additional_columns)
    if len(ohlcv) != row_count:
        raise OfflineSweepError("4h OHLCV row count does not match catalog")
    metadata_start = _parse_metadata_timestamp(start_utc, "range.start_utc")
    metadata_end = _parse_metadata_timestamp(end_utc, "range.end_utc")
    if ohlcv.index[0] != metadata_start or ohlcv.index[-1] != metadata_end:
        raise OfflineSweepError("4h OHLCV range does not match catalog")

    catalog_artifact_sha256 = _sha256_file_hex(catalog_path)
    return _ExecutionInput(
        mode="canonical_4h_derived",
        execution_provenance_class="canonical_derived_real_data",
        ohlcv=ohlcv,
        funding=_zero_funding_for_ohlcv(ohlcv),
        timeframe="4h",
        data_catalog_ref=catalog_ref,
        data_slice_identity=data_slice_identity,
        environment_summary=[
            "canonical_4h_derived_ohlcv_input",
            "d4h_catalog_slice_provenance",
            "execution_provenance_class=canonical_derived_real_data",
            "offline_only_no_exchange_api",
        ],
        data_coverage_notes=[
            D4H_PROVENANCE_MODE_NOTE,
            *(
                [f"declared_non_ohlcv_columns={','.join(additional_columns)}"]
                if additional_columns
                else []
            ),
            "offline only",
            "no exchange/API contact",
            "not live/paper input",
            "zero_funding_synthetic_current_runner_behavior",
            f"d4h_validation_report_sha256={validation_report_sha256}",
            f"d4h_derivation_report_sha256={derivation_report_sha256}",
            f"d4h_catalog_artifact_sha256={catalog_artifact_sha256}",
            f"d4h_csv_sha256={normalized_sha256}",
            f"d4h_validation_status={validation_status}",
            f"parent_15m_data_slice_identity={parent_data_slice_identity}",
            f"parent_15m_normalized_sha256={parent_normalized_sha256}",
            f"parent_15m_validation_report_sha256={parent_validation_report_sha256}",
            f"resampling_method={resampling_method}",
            f"resampling_version={resampling_version}",
            f"row_count={row_count}",
            f"expected_row_count={expected_row_count}",
            f"start_utc={start_utc}",
            f"end_utc={end_utc}",
            f"gap_count={gap_count}",
            f"missing_bar_count={missing_bar_count}",
            f"gaps={json.dumps(gaps, sort_keys=True, separators=(',', ':'))}",
            f"duplicate_group_count={duplicate_group_count}",
            f"duplicate_row_count={duplicate_row_count}",
            f"duplicates={json.dumps(duplicates, sort_keys=True, separators=(',', ':'))}",
            f"partial_window_count={partial_window_count}",
        ],
        funding_input_identity=_funding_input_identity_off(),
    )


def _canonical_intraday_derived_execution_input(
    timeframe: str,
    ohlcv_input_path: Path | None,
    catalog_path: Path | None = None,
    validation_path: Path | None = None,
    derivation_path: Path | None = None,
    additional_columns: tuple[str, ...] = (),
) -> _ExecutionInput:
    if timeframe not in CANONICAL_INTRADAY_DERIVED_CONFIG:
        raise OfflineSweepError("canonical derived route is limited to 30m and 1h")
    if ohlcv_input_path is None:
        raise OfflineSweepError(f"--ohlcv-input is required with --canonical-{timeframe}")
    _require_path_exists(ohlcv_input_path, "--ohlcv-input")
    config = CANONICAL_INTRADAY_DERIVED_CONFIG[timeframe]
    catalog_path = catalog_path or config["catalog"]
    validation_path = validation_path or config["validation"]
    derivation_path = derivation_path or config["derivation"]
    _require_path_exists(catalog_path, f"canonical {timeframe} catalog")
    _require_path_exists(validation_path, f"canonical {timeframe} validation report")
    _require_path_exists(derivation_path, f"canonical {timeframe} derivation report")

    catalog = _load_json(catalog_path)
    validation = _load_json(validation_path)
    derivation = _load_json(derivation_path)
    catalog_ref = _required_non_empty_string(catalog, "catalog_ref")
    data_slice_identity = _required_non_empty_string(
        catalog, "slice_identity.data_slice_identity"
    )
    normalized_sha = _required_non_empty_string(catalog, "normalized.sha256")
    validation_sha = _required_non_empty_string(catalog, "validation_report.sha256")
    derivation_sha = _required_non_empty_string(catalog, "derivation_report.sha256")
    validation_status = _required_non_empty_string(catalog, "validation_report.status")
    row_count = _required_int(catalog, "range.row_count")
    expected_row_count = _required_int(catalog, "range.expected_row_count")
    start_utc = _required_non_empty_string(catalog, "range.start_utc")
    end_utc = _required_non_empty_string(catalog, "range.end_utc")
    gap_count = _required_int(catalog, "gap_summary.gap_count")
    missing_bar_count = _required_int(catalog, "gap_summary.missing_bar_count")
    gaps = _required_list(catalog, "gap_summary.gaps")
    duplicate_group_count = _required_int(catalog, "duplicate_summary.duplicate_group_count")
    duplicate_row_count = _required_int(catalog, "duplicate_summary.duplicate_row_count")
    duplicates = _required_list(catalog, "duplicate_summary.duplicates")
    partial_window_count = _required_int(validation, "validation.partial_window_count")
    parent_dataset_id = _required_non_empty_string(catalog, "parent.dataset_id")
    parent_normalized_sha = _required_non_empty_string(catalog, "parent.normalized_sha256")
    parent_validation_sha = _required_non_empty_string(
        catalog, "parent.validation_report_sha256"
    )
    parent_catalog_ref = _required_non_empty_string(catalog, "parent.catalog_ref")
    parent_identity = _required_non_empty_string(catalog, "parent.data_slice_identity")
    resampling_method = _required_non_empty_string(catalog, "derivation.method")
    resampling_version = _required_non_empty_string(catalog, "resampling_version")

    expected_identity_prefix = f"{config['dataset_id']}:sha256:"
    checks = [
        (catalog.get("dataset_id") == config["dataset_id"], "dataset_id differs"),
        (catalog.get("timeframe") == timeframe, "catalog timeframe differs"),
        (validation.get("timeframe") == timeframe, "validation timeframe differs"),
        (derivation.get("timeframe") == timeframe, "derivation timeframe differs"),
        (catalog.get("source_type") == "derived_offline_resample", "source type differs"),
        (validation_status == "PASS", "catalog validation status is not PASS"),
        (_get_path(validation, "validation.status") == "PASS", "validation report status is not PASS"),
        (validation.get("ok") is True, "validation report ok is not true"),
        (derivation.get("ok") is True, "derivation report ok is not true"),
        (data_slice_identity.startswith(expected_identity_prefix), "data-slice identity prefix differs"),
        (row_count == expected_row_count == config["row_count"], "row count differs"),
        (start_utc == config["start_utc"], "coverage start differs"),
        (end_utc == config["end_utc"], "coverage end differs"),
        (gap_count == 0 and missing_bar_count == 0 and not gaps, "gap facts differ"),
        (duplicate_group_count == 0 and duplicate_row_count == 0 and not duplicates, "duplicate facts differ"),
        (partial_window_count == 0, "partial-window facts differ"),
        (parent_dataset_id == CANONICAL_D4_PARENT_DATASET_ID, "parent dataset_id differs"),
        (parent_normalized_sha == CANONICAL_D4_PARENT_NORMALIZED_SHA256, "parent normalized SHA differs"),
        (parent_validation_sha == CANONICAL_D4_PARENT_VALIDATION_SHA256, "parent validation SHA differs"),
        (parent_identity == CANONICAL_D4_PARENT_DATA_SLICE_IDENTITY, "parent identity differs"),
        (_required_non_empty_string(derivation, "parent.dataset_id") == parent_dataset_id, "derivation parent dataset_id differs"),
        (_required_non_empty_string(derivation, "parent.normalized_sha256") == parent_normalized_sha, "derivation parent SHA differs"),
        (_required_non_empty_string(derivation, "parent.validation_report_sha256") == parent_validation_sha, "derivation parent validation SHA differs"),
        (_required_non_empty_string(derivation, "parent.catalog_ref") == parent_catalog_ref, "derivation parent catalog ref differs"),
        (_required_non_empty_string(derivation, "parent.data_slice_identity") == parent_identity, "derivation parent identity differs"),
        (_required_non_empty_string(validation, "normalized.sha256") == normalized_sha, "validation CSV SHA differs"),
        (_required_non_empty_string(derivation, "output.sha256") == normalized_sha, "derivation CSV SHA differs"),
        (_required_int(validation, "range.row_count") == row_count, "validation row count differs"),
        (_required_int(derivation, "output.row_count") == row_count, "derivation row count differs"),
        (_required_int(validation, "validation.cadence_ms") == config["cadence_ms"], "validation cadence differs"),
    ]
    failures = [message for ok, message in checks if not ok]
    if failures:
        raise OfflineSweepError(
            f"canonical {timeframe} lineage validation failed: {'; '.join(failures)}"
        )
    if _sha256_file_hex(validation_path) != validation_sha:
        raise OfflineSweepError(f"{timeframe} validation report SHA256 does not match catalog")
    if _sha256_file_hex(derivation_path) != derivation_sha:
        raise OfflineSweepError(f"{timeframe} derivation report SHA256 does not match catalog")
    resolved = ohlcv_input_path.resolve()
    if _sha256_file_hex(resolved) != normalized_sha:
        raise OfflineSweepError(f"{timeframe} OHLCV CSV SHA256 does not match catalog")
    ohlcv = _load_ohlcv_input(
        resolved,
        timeframe=timeframe,
        expected_delta=config["cadence"],
        min_rows=20,
        additional_columns=additional_columns,
    )
    if len(ohlcv) != row_count:
        raise OfflineSweepError(f"{timeframe} OHLCV row count does not match catalog")
    if (
        ohlcv.index[0] != _parse_metadata_timestamp(start_utc, "range.start_utc")
        or ohlcv.index[-1] != _parse_metadata_timestamp(end_utc, "range.end_utc")
    ):
        raise OfflineSweepError(f"{timeframe} OHLCV range does not match catalog")
    catalog_sha = _sha256_file_hex(catalog_path)
    return _ExecutionInput(
        mode=f"canonical_{timeframe}_derived",
        execution_provenance_class="canonical_derived_real_data",
        ohlcv=ohlcv,
        funding=_zero_funding_for_ohlcv(ohlcv),
        timeframe=timeframe,
        data_catalog_ref=catalog_ref,
        data_slice_identity=data_slice_identity,
        environment_summary=[
            f"canonical_{timeframe}_derived_ohlcv_input",
            "ft01_15m_d4_derived_catalog_slice_provenance",
            "execution_provenance_class=canonical_derived_real_data",
            "offline_only_no_exchange_api",
        ],
        data_coverage_notes=[
            FT01_PROVENANCE_MODE_NOTE,
            *(
                [f"declared_non_ohlcv_columns={','.join(additional_columns)}"]
                if additional_columns
                else []
            ),
            "offline only",
            "no exchange/API contact",
            "not live/paper input",
            "zero_funding_synthetic_current_runner_behavior",
            f"target_timeframe={timeframe}",
            f"catalog_artifact_sha256={catalog_sha}",
            f"validation_report_sha256={validation_sha}",
            f"derivation_report_sha256={derivation_sha}",
            f"derived_csv_sha256={normalized_sha}",
            f"validation_status={validation_status}",
            f"parent_15m_dataset_id={parent_dataset_id}",
            f"parent_15m_catalog_ref={parent_catalog_ref}",
            f"parent_15m_data_slice_identity={parent_identity}",
            f"parent_15m_normalized_sha256={parent_normalized_sha}",
            f"parent_15m_validation_report_sha256={parent_validation_sha}",
            f"resampling_method={resampling_method}",
            f"resampling_version={resampling_version}",
            f"row_count={row_count}",
            f"expected_row_count={expected_row_count}",
            f"start_utc={start_utc}",
            f"end_utc={end_utc}",
            f"cadence_ms={config['cadence_ms']}",
            f"gap_count={gap_count}",
            f"missing_bar_count={missing_bar_count}",
            f"duplicate_group_count={duplicate_group_count}",
            f"duplicate_row_count={duplicate_row_count}",
            f"partial_window_count={partial_window_count}",
        ],
        funding_input_identity=_funding_input_identity_off(),
    )


def _run_canonical_15m_backtest(
    strategy_spec: dict[str, Any],
    variant: dict[str, Any],
    execution_input: _ExecutionInput,
    sizing_context: _SizingContext,
    sizing: _SizingResolution,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> Any:
    if evaluation_end is not None:
        execution_input = _slice_execution_input_for_evaluation_end(execution_input, evaluation_end)
    signal = compile_signal(
        strategy_spec,
        variant,
        execution_input.ohlcv,
        funding=execution_input.funding,
    )
    if evaluation_start is not None:
        signal = _mask_signal_before_window(signal, evaluation_start)
    return run_backtest(
        signal=signal,
        ohlcv=execution_input.ohlcv,
        funding=execution_input.funding,
        fee_bps_taker=4.0,
        fee_bps_maker=2.0,
        slippage_bps=1.0,
        initial_equity=INITIAL_EQUITY,
        stream="klines",
        interval=execution_input.timeframe,
        gaps_path=REPO_ROOT / "tools" / "research_runner" / "_nonexistent_empty_gaps.json",
        entry_fee_side="taker",
        exit_fee_side="taker",
        funding_cost_mode=execution_input.funding_input_identity["funding_mode"],
        funding_notional_mode="entry_price",
        order_size=sizing.resolved_order_size,
        sizing_mode=sizing_context.sizing_mode,
        target_leverage=sizing_context.target_leverage,
        fill_mode="complete",
        slippage_model="fixed_bps",
        liquidation_mode="zero_equity",
        mark_price_source="close",
        bar_path_assumption="next_open_close_mark",
    )


def _metrics_from_backtest(result: Any, freq: str) -> dict[str, Any]:
    returns = result.equity_curve.pct_change().dropna()
    drawdown, _, _ = max_drawdown(result.equity_curve)
    final_equity = float(result.equity_curve.iloc[-1])
    initial_equity = float(result.params["initial_equity"])
    trade_count = int(len(result.trades_df))
    win_rate = 0.0
    if trade_count and "net_pnl" in result.trades_df.columns:
        win_rate = float((result.trades_df["net_pnl"] > 0).sum() / trade_count)
    return {
        "pnl": float(final_equity - initial_equity),
        "return_pct": float((final_equity - initial_equity) / initial_equity),
        "drawdown": float(drawdown),
        "trade_count": trade_count,
        "win_rate": win_rate,
        "sharpe": float(sharpe(returns, freq)),
        "fees": float(result.fees_paid),
        "funding": float(result.funding_paid),
        "slippage": float(result.slippage_paid),
        "exposure": 1.0 if trade_count else 0.0,
    }


# ---------------------------------------------------------------------------
# Evaluation-window support (warmup-preserving, offline-only)
# ---------------------------------------------------------------------------


def _validate_evaluation_window(
    evaluation_start: pd.Timestamp,
    evaluation_end: pd.Timestamp,
    ohlcv: pd.DataFrame,
) -> None:
    """Fail closed if the evaluation window is invalid or leaves no evaluable bars."""
    if evaluation_start >= evaluation_end:
        raise OfflineSweepError(
            "evaluation_start must be strictly before evaluation_end"
        )
    if ohlcv.empty:
        raise OfflineSweepError("OHLCV frame is empty — cannot validate evaluation window")
    first_bar = ohlcv.index[0]
    last_bar = ohlcv.index[-1]
    if evaluation_start < first_bar:
        raise OfflineSweepError(
            f"evaluation_start ({evaluation_start.isoformat()}) is before the first OHLCV bar "
            f"({first_bar.isoformat()}) — warmup prefix is missing from the input frame"
        )
    inferred_period = (ohlcv.index[1] - ohlcv.index[0]) if len(ohlcv) >= 2 else pd.Timedelta(minutes=15)
    if evaluation_end > last_bar + inferred_period:
        raise OfflineSweepError(
            f"evaluation_end ({evaluation_end.isoformat()}) extends beyond the last available OHLCV bar "
            f"({last_bar.isoformat()}) — partial evaluation window not allowed; "
            "supply a frame that covers the full evaluation period"
        )
    eval_rows = ohlcv.loc[
        (ohlcv.index >= evaluation_start) & (ohlcv.index < evaluation_end)
    ]
    if len(eval_rows) < 2:
        raise OfflineSweepError(
            "evaluation window contains fewer than 2 OHLCV bars — no evaluable data"
        )


def _mask_signal_before_window(
    signal: pd.Series,
    evaluation_start: pd.Timestamp,
) -> pd.Series:
    """Force signal to 0.0 for all bars before evaluation_start.

    Prevents any position from opening during the warmup prefix so no
    pre-window trade can contaminate evaluation-window metrics.  The signal
    compiler still runs on the full frame (warmup + evaluation), so rolling
    indicator state is correctly established before the window opens.
    """
    masked = signal.copy()
    masked.loc[masked.index < evaluation_start] = 0.0
    return masked


def _metrics_from_backtest_windowed(
    result: Any,
    freq: str,
    evaluation_start: pd.Timestamp,
    evaluation_end: pd.Timestamp,
) -> dict[str, Any]:
    """Compute metrics restricted to the evaluation window [start, end).

    Callers must ensure the backtest was run on a frame truncated to
    rows strictly before evaluation_end (via
    _slice_execution_input_for_evaluation_end) and that the signal was
    masked to 0.0 before evaluation_start (via _mask_signal_before_window).
    Under those preconditions:
      - result.trades_df contains only evaluation-window trades
      - result.fees_paid / funding_paid / slippage_paid are window-scoped
      - trade_count, win_rate, and exposure reflect only window activity
    The equity curve is still sliced to [evaluation_start, evaluation_end)
    to compute returns, drawdown, and Sharpe correctly.
    """
    eval_curve = result.equity_curve.loc[
        (result.equity_curve.index >= evaluation_start)
        & (result.equity_curve.index < evaluation_end)
    ]
    if len(eval_curve) < 2:
        raise OfflineSweepError(
            "evaluation window produced fewer than 2 equity curve points — "
            "cannot compute windowed metrics"
        )
    returns = eval_curve.pct_change().dropna()
    drawdown, _, _ = max_drawdown(eval_curve)
    window_initial = float(eval_curve.iloc[0])
    final_equity = float(eval_curve.iloc[-1])
    pnl = final_equity - window_initial
    return_pct = pnl / window_initial if window_initial != 0.0 else 0.0
    trade_count = int(len(result.trades_df))
    win_rate = 0.0
    if trade_count and "net_pnl" in result.trades_df.columns:
        win_rate = float((result.trades_df["net_pnl"] > 0).sum() / trade_count)
    return {
        "pnl": float(pnl),
        "return_pct": float(return_pct),
        "drawdown": float(drawdown),
        "trade_count": trade_count,
        "win_rate": win_rate,
        "sharpe": float(sharpe(returns, freq)),
        "fees": float(result.fees_paid),
        "funding": float(result.funding_paid),
        "slippage": float(result.slippage_paid),
        "exposure": 1.0 if trade_count else 0.0,
    }


def _window_boundary_payload(window: _WalkForwardWindow) -> dict[str, Any]:
    return {
        "window_id": window.window_id,
        "window_index": window.window_index,
        "in_sample_start": window.in_sample_start.isoformat().replace("+00:00", "Z"),
        "in_sample_end_exclusive": window.in_sample_end_exclusive.isoformat().replace("+00:00", "Z"),
        "out_of_sample_start": window.out_of_sample_start.isoformat().replace("+00:00", "Z"),
        "out_of_sample_end_exclusive": window.out_of_sample_end_exclusive.isoformat().replace("+00:00", "Z"),
        "in_sample_row_count": window.in_sample_row_count,
        "out_of_sample_row_count": window.out_of_sample_row_count,
        "boundary_semantics": "start_inclusive_end_exclusive",
        "paired_is_oos_overlap_allowed": False,
    }


def _efficiency_ratio(in_sample_sharpe: Any, out_of_sample_sharpe: Any) -> float | None:
    if not isinstance(in_sample_sharpe, (int, float)) or isinstance(in_sample_sharpe, bool):
        return None
    if not isinstance(out_of_sample_sharpe, (int, float)) or isinstance(out_of_sample_sharpe, bool):
        return None
    if not math.isfinite(float(in_sample_sharpe)) or not math.isfinite(float(out_of_sample_sharpe)):
        return None
    if float(in_sample_sharpe) <= 0.0:
        return None
    return float(out_of_sample_sharpe) / float(in_sample_sharpe)


def _run_window_variant_backtest(
    strategy_spec: dict[str, Any],
    variant: dict[str, Any],
    execution_input: _ExecutionInput,
    sizing_mode: str,
    target_leverage: float,
) -> dict[str, Any]:
    sizing_context = _sizing_context(execution_input, sizing_mode, target_leverage)
    assert sizing_context.exact_resolution is not None
    result = _run_canonical_15m_backtest(
        strategy_spec,
        variant,
        execution_input,
        sizing_context,
        sizing_context.exact_resolution,
    )
    return _metrics_from_backtest(result, execution_input.timeframe)


def _walkforward_result_row(
    window: _WalkForwardWindow,
    variant: dict[str, Any],
    outcome_category: str,
    in_sample_metrics: dict[str, Any] | None,
    out_of_sample_metrics: dict[str, Any] | None,
    efficiency: float | None,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        **_window_boundary_payload(window),
        "variant_id": variant["variant_id"],
        "selection_behavior": "no_selection_partition_and_report_all_included_variants",
        "outcome_category": outcome_category,
        "in_sample_metrics": in_sample_metrics,
        "out_of_sample_metrics": out_of_sample_metrics,
        "oos_is_sharpe_efficiency": efficiency,
        "missing_input_warnings": warnings,
    }


def _run_walkforward_variant_worker(
    *,
    task_index: int,
    strategy_spec: dict[str, Any],
    variant: dict[str, Any],
    in_sample_input: _ExecutionInput,
    out_of_sample_input: _ExecutionInput,
    sizing_mode: str,
    target_leverage: float,
) -> dict[str, Any]:
    try:
        is_metrics = _run_window_variant_backtest(
            strategy_spec,
            variant,
            in_sample_input,
            sizing_mode,
            target_leverage,
        )
        oos_metrics = _run_window_variant_backtest(
            strategy_spec,
            variant,
            out_of_sample_input,
            sizing_mode,
            target_leverage,
        )
        ratio = _efficiency_ratio(is_metrics.get("sharpe"), oos_metrics.get("sharpe"))
        warnings = []
        if ratio is None:
            warnings.append("oos_is_sharpe_efficiency_unavailable_non_positive_or_missing_is_sharpe")
        return {
            "task_index": task_index,
            "outcome_category": "successful",
            "in_sample_metrics": is_metrics,
            "out_of_sample_metrics": oos_metrics,
            "oos_is_sharpe_efficiency": ratio,
            "missing_input_warnings": warnings,
        }
    except Exception as exc:
        return {
            "task_index": task_index,
            "outcome_category": "errored",
            "in_sample_metrics": None,
            "out_of_sample_metrics": None,
            "oos_is_sharpe_efficiency": None,
            "missing_input_warnings": [f"window_variant_error:{exc.__class__.__name__}"],
        }


def _run_walkforward_dry_run_parallel(
    *,
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    execution_input: _ExecutionInput,
    sizing_mode: str,
    target_leverage: float,
    in_sample_bars: int,
    out_of_sample_bars: int,
    step_bars: int | None,
    max_windows: int | None,
    max_workers: int,
) -> dict[str, Any]:
    windows = _build_walkforward_windows(
        execution_input.ohlcv.index,
        in_sample_bars=in_sample_bars,
        out_of_sample_bars=out_of_sample_bars,
        step_bars=step_bars,
        max_windows=max_windows,
    )
    selected_variants = [
        variant
        for variant in sorted(manifest["variant_assignments"], key=lambda row: row["variant_id"])
        if variant["assignment_status"] == "included"
    ]
    tasks: list[dict[str, Any]] = []
    windows_by_task: dict[int, _WalkForwardWindow] = {}
    variants_by_task: dict[int, dict[str, Any]] = {}
    for window in windows:
        is_input = _slice_execution_input(
            execution_input,
            start=window.in_sample_start,
            end=window.in_sample_end_exclusive,
            window_label=f"{window.window_id}:in_sample",
        )
        oos_input = _slice_execution_input(
            execution_input,
            start=window.out_of_sample_start,
            end=window.out_of_sample_end_exclusive,
            window_label=f"{window.window_id}:out_of_sample",
        )
        for variant in selected_variants:
            task_index = len(tasks)
            windows_by_task[task_index] = window
            variants_by_task[task_index] = variant
            tasks.append(
                {
                    "task_index": task_index,
                    "strategy_spec": strategy_spec,
                    "variant": variant,
                    "in_sample_input": is_input,
                    "out_of_sample_input": oos_input,
                    "sizing_mode": sizing_mode,
                    "target_leverage": target_leverage,
                }
            )

    results: dict[int, dict[str, Any]] = {}
    if tasks:
        worker_count = min(max_workers, len(tasks))
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            future_to_task = {
                executor.submit(_run_walkforward_variant_worker, **task): task
                for task in tasks
            }
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                task_index = task["task_index"]
                try:
                    results[task_index] = future.result()
                except Exception as exc:
                    results[task_index] = {
                        "task_index": task_index,
                        "outcome_category": "errored",
                        "in_sample_metrics": None,
                        "out_of_sample_metrics": None,
                        "oos_is_sharpe_efficiency": None,
                        "missing_input_warnings": [f"window_variant_error:{exc.__class__.__name__}"],
                    }

    rows: list[dict[str, Any]] = []
    missing_input_warnings: list[str] = []
    for task_index in range(len(tasks)):
        result = results[task_index]
        warnings = result["missing_input_warnings"]
        missing_input_warnings.extend(warnings)
        rows.append(
            _walkforward_result_row(
                windows_by_task[task_index],
                variants_by_task[task_index],
                result["outcome_category"],
                result["in_sample_metrics"],
                result["out_of_sample_metrics"],
                result["oos_is_sharpe_efficiency"],
                warnings,
            )
        )

    return _walkforward_summary(
        in_sample_bars=in_sample_bars,
        out_of_sample_bars=out_of_sample_bars,
        step_bars=step_bars,
        windows=windows,
        selected_variants=selected_variants,
        rows=rows,
        missing_input_warnings=missing_input_warnings,
    )


def _walkforward_summary(
    *,
    in_sample_bars: int,
    out_of_sample_bars: int,
    step_bars: int | None,
    windows: list[_WalkForwardWindow],
    selected_variants: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    missing_input_warnings: list[str],
) -> dict[str, Any]:
    return {
        "enabled": True,
        "dry_run_only": True,
        "canonical_result_population_written": False,
        "window_protocol": {
            "window_type": "rolling_non_overlapping_build_test",
            "boundary_semantics": "start_inclusive_end_exclusive",
            "timezone": "UTC",
            "in_sample_bars": in_sample_bars,
            "out_of_sample_bars": out_of_sample_bars,
            "step_bars": step_bars if step_bars is not None else in_sample_bars + out_of_sample_bars,
            "purge_embargo": "not_implemented_deferred_by_design",
            "selection_behavior": "no_selection_partition_and_report_all_included_variants",
            "no_lookahead_boundary": "OOS rows are never used to choose variants; each row reports the same predeclared included variants across IS and later OOS windows.",
        },
        "window_count": len(windows),
        "variant_count_per_window": len(selected_variants),
        "rows": rows,
        "missing_input_warnings": sorted(set(missing_input_warnings)),
        "non_authority_declaration": [
            "build_test_only",
            "not_canonical_evidence",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_promotion_authority",
            "not_paper_live_runtime_authority",
        ],
    }


def _run_walkforward_dry_run(
    *,
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    execution_input: _ExecutionInput,
    sizing_mode: str,
    target_leverage: float,
    in_sample_bars: int,
    out_of_sample_bars: int,
    step_bars: int | None,
    max_windows: int | None,
    max_workers: int,
) -> dict[str, Any]:
    if max_workers > 1:
        return _run_walkforward_dry_run_parallel(
            strategy_spec=strategy_spec,
            manifest=manifest,
            execution_input=execution_input,
            sizing_mode=sizing_mode,
            target_leverage=target_leverage,
            in_sample_bars=in_sample_bars,
            out_of_sample_bars=out_of_sample_bars,
            step_bars=step_bars,
            max_windows=max_windows,
            max_workers=max_workers,
        )
    windows = _build_walkforward_windows(
        execution_input.ohlcv.index,
        in_sample_bars=in_sample_bars,
        out_of_sample_bars=out_of_sample_bars,
        step_bars=step_bars,
        max_windows=max_windows,
    )
    selected_variants = [
        variant
        for variant in sorted(manifest["variant_assignments"], key=lambda row: row["variant_id"])
        if variant["assignment_status"] == "included"
    ]
    rows: list[dict[str, Any]] = []
    missing_input_warnings: list[str] = []
    for window in windows:
        is_input = _slice_execution_input(
            execution_input,
            start=window.in_sample_start,
            end=window.in_sample_end_exclusive,
            window_label=f"{window.window_id}:in_sample",
        )
        oos_input = _slice_execution_input(
            execution_input,
            start=window.out_of_sample_start,
            end=window.out_of_sample_end_exclusive,
            window_label=f"{window.window_id}:out_of_sample",
        )
        for variant in selected_variants:
            outcome_category = "successful"
            is_metrics = None
            oos_metrics = None
            ratio = None
            warnings: list[str] = []
            try:
                is_metrics = _run_window_variant_backtest(
                    strategy_spec,
                    variant,
                    is_input,
                    sizing_mode,
                    target_leverage,
                )
                oos_metrics = _run_window_variant_backtest(
                    strategy_spec,
                    variant,
                    oos_input,
                    sizing_mode,
                    target_leverage,
                )
                ratio = _efficiency_ratio(is_metrics.get("sharpe"), oos_metrics.get("sharpe"))
                if ratio is None:
                    warning = "oos_is_sharpe_efficiency_unavailable_non_positive_or_missing_is_sharpe"
                    warnings.append(warning)
                    missing_input_warnings.append(warning)
            except Exception as exc:
                outcome_category = "errored"
                warnings.append(f"window_variant_error:{exc.__class__.__name__}")
                missing_input_warnings.append(f"window_variant_error:{exc.__class__.__name__}")
            rows.append(
                _walkforward_result_row(
                    window,
                    variant,
                    outcome_category,
                    is_metrics,
                    oos_metrics,
                    ratio,
                    warnings,
                )
            )

    return _walkforward_summary(
        in_sample_bars=in_sample_bars,
        out_of_sample_bars=out_of_sample_bars,
        step_bars=step_bars,
        windows=windows,
        selected_variants=selected_variants,
        rows=rows,
        missing_input_warnings=missing_input_warnings,
    )


def _empty_metrics() -> dict[str, Any]:
    return {
        "pnl": None,
        "return_pct": None,
        "drawdown": None,
        "trade_count": None,
        "win_rate": None,
        "sharpe": None,
        "fees": None,
        "funding": None,
        "slippage": None,
        "exposure": None,
    }


def _non_success(outcome: str, reason: str | None) -> dict[str, Any]:
    return {
        "reason": reason,
        "rule_ref": None,
        "declared_before_results": None if outcome == "successful" else True,
        "counts_in_denominator": True,
    }


def _error(outcome: str, message_class: str | None, infrastructure: bool = False) -> dict[str, Any]:
    category = None
    if outcome in {"errored", "aborted"}:
        category = "runner_error"
    elif outcome == "data_unavailable":
        category = "data_error"
    elif outcome == "failed":
        category = "strategy_underperformance"
    return {
        "error_category": category,
        "error_message_class": message_class,
        "is_infrastructure_error": infrastructure if category else None,
        "is_strategy_underperformance": outcome == "failed" if category else None,
        "counts_in_denominator": True,
    }


def _data_coverage(outcome: str, execution_input: _ExecutionInput | None = None) -> dict[str, Any]:
    unavailable = outcome == "data_unavailable"
    if execution_input is not None:
        return {
            "data_catalog_ref": execution_input.data_catalog_ref,
            "data_slice_identity": execution_input.data_slice_identity,
            "timeframe": execution_input.timeframe,
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap": unavailable,
            "counts_in_denominator": True,
        }
    return {
        "data_catalog_ref": "synthetic_fixture_only",
        "data_slice_identity": "synthetic-offline-runner-v1",
        "timeframe": "1h",
        "data_stream": "ohlcv",
        "missing_data_policy": "block_if_missing",
        "irreparable_gap": unavailable,
        "counts_in_denominator": True,
    }


def _row(
    result_population_id: str,
    row_number: int,
    variant: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    outcome: str,
    metrics: dict[str, Any] | None = None,
    reason: str | None = None,
    error_message_class: str | None = None,
    infrastructure_error: bool = False,
    execution_input: _ExecutionInput | None = None,
) -> dict[str, Any]:
    variant_id = variant["variant_id"]
    row = {
        "variant_id": variant_id,
        "row_id": f"{result_population_id}-ROW-{row_number:06d}",
        "row_identity_hash": None,
        "assignment_hash": variant.get("parameter_value_hash"),
        "assignment_ref": None,
        "outcome_category": outcome,
        "attempted": outcome in {"successful", "failed", "errored", "data_unavailable"},
        "metrics": metrics if outcome == "successful" else _empty_metrics(),
        "non_success": _non_success(outcome, reason),
        "error": _error(outcome, error_message_class, infrastructure_error),
        "data_coverage": _data_coverage(outcome, execution_input),
        "backtest_assumption_ref": "backtest_assumption_summary",
        "lineage": {
            "parent_variant_id": variant_id,
            "parent_variant_assignment_hash": variant.get("parameter_value_hash"),
            "parent_variant_assignment_ref": None,
            "parent_sweep_plan_id": sweep_plan["sweep_plan_id"],
            "parent_manifest_id": manifest["variant_manifest_id"],
        },
        "row_mutation_policy": {
            "scientific_row_identity_immutable_after_commit": True,
            "corrections_require_append_only_event": True,
            "post_commit_in_place_mutation_forbidden": True,
            "post_hoc_cleanup_forbidden": True,
        },
    }
    row["row_identity_hash"] = _sha256_prefixed(
        {
            "variant_id": row["variant_id"],
            "assignment_hash": row["assignment_hash"],
            "outcome_category": row["outcome_category"],
            "metrics": row["metrics"],
            "non_success": row["non_success"],
            "error": row["error"],
            "data_coverage": row["data_coverage"],
            "lineage": row["lineage"],
        }
    )
    return row


def _deterministic_result_population_id(
    strategy_hash: str,
    manifest_hash: str,
    sweep_hash: str,
    backtest_assumption_summary: dict[str, Any],
    data_slice_identity: str,
    d3_validation_identity: str | None,
    execution_provenance_class: str,
    funding_input_identity: dict[str, Any] | None = None,
) -> str:
    identity_payload = {
        "strategy_hash": strategy_hash,
        "manifest_hash": manifest_hash,
        "sweep_hash": sweep_hash,
        "backtest_assumption_summary": backtest_assumption_summary,
        "data_slice_identity": data_slice_identity,
        "d3_validation_identity": d3_validation_identity,
        "execution_provenance_class": execution_provenance_class,
    }
    if funding_input_identity is not None:
        identity_payload["funding_input_identity"] = funding_input_identity
    digest = hashlib.sha256(
        _canonical_json_bytes(identity_payload)
    ).hexdigest()
    return f"RP-{int(digest[:8], 16) % 10000:04d}"


def _execution_provenance_identity(execution_input: _ExecutionInput | None) -> dict[str, Any]:
    if execution_input is None:
        return {
            "data_slice_identity": "synthetic-offline-runner-v1",
            "d3_validation_identity": None,
            "execution_provenance_class": "fixture_offline",
            "funding_input_identity": None,
        }
    d3_validation_identity = None
    for note in execution_input.data_coverage_notes:
        if note.startswith("1d_validation_identity="):
            d3_validation_identity = note.split("=", 1)[1]
            break
        if note.startswith("d4h_validation_report_sha256="):
            d3_validation_identity = note.split("=", 1)[1]
            break
        if note.startswith("d3_validation_report_sha256="):
            d3_validation_identity = note.split("=", 1)[1]
            break
    return {
        "data_slice_identity": execution_input.data_slice_identity,
        "d3_validation_identity": d3_validation_identity,
        "execution_provenance_class": execution_input.execution_provenance_class,
        "funding_input_identity": execution_input.funding_input_identity,
    }


def _order_size_assumption(
    sweep_plan: dict[str, Any],
    sizing_context: _SizingContext,
) -> str:
    base_assumption = (
        sweep_plan["realism_assumptions"]["order_size_assumption"] or "fixed_1_contract"
    )
    if sizing_context.sizing_mode == SIZING_MODE_FIXED_ORDER_SIZE:
        sizing_model = SIZING_MODEL
    else:
        sizing_model = DYNAMIC_SIZING_MODEL
    parts = [
        f"sizing_mode={sizing_context.sizing_mode}",
        f"sizing_model={sizing_model}",
        f"target_leverage={_format_sizing_value(sizing_context.target_leverage)}",
        f"initial_equity={_format_sizing_value(INITIAL_EQUITY)}",
        "dynamic_mode_opt_in_required=True",
    ]
    if sizing_context.sizing_mode == SIZING_MODE_FIXED_ORDER_SIZE:
        parts.extend(
            [
                "structured_sizing_metadata=not_emitted_for_fixed_mode",
                f"reference_price_basis={REFERENCE_PRICE_BASIS}",
            ]
        )
    else:
        parts.extend(
            [
                "structured_sizing_metadata=present",
                f"sizing_equity_basis={DYNAMIC_SIZING_EQUITY_BASIS}",
                f"entry_reference_price_basis={DYNAMIC_ENTRY_REFERENCE_PRICE_BASIS}",
                "fixed_mode_order_size_still_resolved_for_backtest_argument_compatibility",
            ]
        )
    if sizing_context.exact_resolution is None:
        parts.extend(
            [
                "reference_price=per_variant_first_in_sample_open",
                "resolved_order_size=per_variant_target_leverage_times_initial_equity_over_reference_price",
                "synthetic_fixture_resolution=per_variant",
            ]
        )
    else:
        sizing = sizing_context.exact_resolution
        parts.extend(
            [
                f"reference_price={_format_sizing_value(sizing.reference_price)}",
                f"resolved_order_size={_format_sizing_value(sizing.resolved_order_size)}",
            ]
        )
    if sizing_context.sizing_mode == SIZING_MODE_FIXED_ORDER_SIZE:
        parts.append(f"drift_caveat={DRIFT_CAVEAT}")
    parts.append(f"prior_assumption={base_assumption}")
    return "; ".join(parts)


def _backtest_assumption_summary(
    sweep_plan: dict[str, Any],
    sizing_context: _SizingContext,
    funding_input_identity: dict[str, Any] | None,
) -> dict[str, Any]:
    assumptions = sweep_plan["realism_assumptions"]
    order_size_assumption = _order_size_assumption(sweep_plan, sizing_context)
    if funding_input_identity is not None:
        order_size_assumption = (
            f"{order_size_assumption}; {_funding_identity_note(funding_input_identity)}"
        )
    return {
        "fee_side_assumption": assumptions["fee_side_assumption"] or "taker_entry_taker_exit",
        "exchange_constraint_disclosure": str(assumptions["exchange_constraints_disclosed"]),
        "funding_notional": "entry_price",
        "slippage_model": "fixed_bps",
        "fill_mode": "complete",
        "order_size_assumption": order_size_assumption,
        "liquidity_capacity_assumption": assumptions["liquidity_capacity_assumption"],
        "liquidation_mode": "zero_equity",
        "maintenance_margin_assumption": assumptions["maintenance_margin_assumption"],
        "mark_price_source": "close",
        "bar_path_assumption": "next_open_close_mark",
        "records_assumptions_only": True,
    }


def _sizing_metadata(sizing_context: _SizingContext) -> dict[str, Any] | None:
    if sizing_context.sizing_mode != SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE:
        return None
    return {
        "sizing_mode": SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        "target_leverage": sizing_context.target_leverage,
        "sizing_equity_basis": DYNAMIC_SIZING_EQUITY_BASIS,
        "entry_reference_price_basis": DYNAMIC_ENTRY_REFERENCE_PRICE_BASIS,
    }


def _execute_variant_worker(
    *,
    row_number: int,
    strategy_spec: dict[str, Any],
    variant: dict[str, Any],
    deterministic_seed: int,
    execution_input: _ExecutionInput | None,
    sizing_context: _SizingContext,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> dict[str, Any]:
    mode = _variant_fixture_mode(variant)
    try:
        if mode == "errored":
            raise RuntimeError("fixture variant error")
        if execution_input is None:
            result = _run_synthetic_backtest(
                variant["variant_id"],
                deterministic_seed,
                sizing_context.sizing_mode,
                sizing_context.target_leverage,
            )
            metrics = _metrics_from_backtest(result, "1h")
        else:
            assert sizing_context.exact_resolution is not None
            result = _run_canonical_15m_backtest(
                strategy_spec,
                variant,
                execution_input,
                sizing_context,
                sizing_context.exact_resolution,
                evaluation_start=evaluation_start,
                evaluation_end=evaluation_end,
            )
            if evaluation_start is not None and evaluation_end is not None:
                metrics = _metrics_from_backtest_windowed(
                    result, execution_input.timeframe, evaluation_start, evaluation_end
                )
            else:
                metrics = _metrics_from_backtest(result, execution_input.timeframe)
        outcome = "successful" if math.isfinite(metrics["return_pct"]) else "failed"
        return {
            "row_number": row_number,
            "outcome": outcome,
            "metrics": metrics,
            "reason": None if outcome == "successful" else "non-finite return",
            "error_message_class": None,
            "infrastructure_error": False,
        }
    except Exception as exc:
        return {
            "row_number": row_number,
            "outcome": "errored",
            "metrics": None,
            "reason": "per-variant runner error",
            "error_message_class": exc.__class__.__name__,
            "infrastructure_error": False,
        }


def _collect_parallel_variant_results(
    tasks: list[dict[str, Any]],
    max_workers: int,
) -> dict[int, dict[str, Any]]:
    if not tasks:
        return {}
    worker_count = min(max_workers, len(tasks))
    results: dict[int, dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        future_to_task = {
            executor.submit(_execute_variant_worker, **task): task
            for task in tasks
        }
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            row_number = task["row_number"]
            try:
                results[row_number] = future.result()
            except Exception as exc:
                results[row_number] = {
                    "row_number": row_number,
                    "outcome": "errored",
                    "metrics": None,
                    "reason": "per-variant runner error",
                    "error_message_class": exc.__class__.__name__,
                    "infrastructure_error": False,
                }
    return results


def _execute_rows(
    result_population_id: str,
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    deterministic_seed: int,
    execution_input: _ExecutionInput | None,
    sizing_context: _SizingContext,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    aborted = False
    variants = sorted(manifest["variant_assignments"], key=lambda row: row["variant_id"])
    for index, variant in enumerate(variants, start=1):
        if aborted:
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "not_attempted",
                    reason="infrastructure abort before variant attempt",
                    execution_input=execution_input,
                )
            )
            continue

        mode = _variant_fixture_mode(variant)
        status = variant["assignment_status"]
        if status == "invalid":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "invalid",
                    reason=status,
                    execution_input=execution_input,
                )
            )
            continue
        if status == "excluded":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "excluded",
                    reason=status,
                    execution_input=execution_input,
                )
            )
            continue
        if status == "not_attempted":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "not_attempted",
                    reason=status,
                    execution_input=execution_input,
                )
            )
            continue
        if mode == "data_unavailable":
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "data_unavailable",
                    reason="fixture declared missing synthetic data",
                    error_message_class="FixtureDataUnavailable",
                    execution_input=execution_input,
                )
            )
            continue
        if mode == "infra_abort":
            aborted = True
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "aborted",
                    reason="fixture infrastructure abort",
                    error_message_class="OfflineSweepAbort",
                    infrastructure_error=True,
                    execution_input=execution_input,
                )
            )
            continue
        try:
            if mode == "errored":
                raise RuntimeError("fixture variant error")
            if execution_input is None:
                result = _run_synthetic_backtest(
                    variant["variant_id"],
                    deterministic_seed,
                    sizing_context.sizing_mode,
                    sizing_context.target_leverage,
                )
                metrics = _metrics_from_backtest(result, "1h")
            else:
                assert sizing_context.exact_resolution is not None
                result = _run_canonical_15m_backtest(
                    strategy_spec,
                    variant,
                    execution_input,
                    sizing_context,
                    sizing_context.exact_resolution,
                    evaluation_start=evaluation_start,
                    evaluation_end=evaluation_end,
                )
                if evaluation_start is not None and evaluation_end is not None:
                    metrics = _metrics_from_backtest_windowed(
                        result, execution_input.timeframe, evaluation_start, evaluation_end
                    )
                else:
                    metrics = _metrics_from_backtest(result, execution_input.timeframe)
            outcome = "successful" if math.isfinite(metrics["return_pct"]) else "failed"
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    outcome,
                    metrics=metrics,
                    reason=None if outcome == "successful" else "non-finite return",
                    execution_input=execution_input,
                )
            )
        except Exception as exc:
            rows.append(
                _row(
                    result_population_id,
                    index,
                    variant,
                    manifest,
                    sweep_plan,
                    "errored",
                    reason="per-variant runner error",
                    error_message_class=exc.__class__.__name__,
                    execution_input=execution_input,
                )
            )
    return rows, aborted


def _execute_rows_parallel(
    result_population_id: str,
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    deterministic_seed: int,
    execution_input: _ExecutionInput | None,
    sizing_context: _SizingContext,
    max_workers: int,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    rows_by_number: dict[int, dict[str, Any]] = {}
    tasks: list[dict[str, Any]] = []
    aborted = False
    variants = sorted(manifest["variant_assignments"], key=lambda row: row["variant_id"])
    for index, variant in enumerate(variants, start=1):
        if aborted:
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "not_attempted",
                reason="infrastructure abort before variant attempt",
                execution_input=execution_input,
            )
            continue

        mode = _variant_fixture_mode(variant)
        status = variant["assignment_status"]
        if status == "invalid":
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "invalid",
                reason=status,
                execution_input=execution_input,
            )
            continue
        if status == "excluded":
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "excluded",
                reason=status,
                execution_input=execution_input,
            )
            continue
        if status == "not_attempted":
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "not_attempted",
                reason=status,
                execution_input=execution_input,
            )
            continue
        if mode == "data_unavailable":
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "data_unavailable",
                reason="fixture declared missing synthetic data",
                error_message_class="FixtureDataUnavailable",
                execution_input=execution_input,
            )
            continue
        if mode == "infra_abort":
            aborted = True
            rows_by_number[index] = _row(
                result_population_id,
                index,
                variant,
                manifest,
                sweep_plan,
                "aborted",
                reason="fixture infrastructure abort",
                error_message_class="OfflineSweepAbort",
                infrastructure_error=True,
                execution_input=execution_input,
            )
            continue

        tasks.append(
            {
                "row_number": index,
                "strategy_spec": strategy_spec,
                "variant": variant,
                "deterministic_seed": deterministic_seed,
                "execution_input": execution_input,
                "sizing_context": sizing_context,
                "evaluation_start": evaluation_start,
                "evaluation_end": evaluation_end,
            }
        )

    worker_results = _collect_parallel_variant_results(tasks, max_workers)
    variants_by_number = {
        index: variant
        for index, variant in enumerate(variants, start=1)
    }
    for task in tasks:
        index = task["row_number"]
        result = worker_results[index]
        rows_by_number[index] = _row(
            result_population_id,
            index,
            variants_by_number[index],
            manifest,
            sweep_plan,
            result["outcome"],
            metrics=result["metrics"],
            reason=result["reason"],
            error_message_class=result["error_message_class"],
            infrastructure_error=result["infrastructure_error"],
            execution_input=execution_input,
        )

    return [rows_by_number[index] for index in range(1, len(variants) + 1)], aborted


def _build_result_population(
    strategy_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    run_label: str | None,
    deterministic_seed: int,
    execution_input: _ExecutionInput | None,
    sizing_mode: str,
    target_leverage: float,
    max_workers: int,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> tuple[dict[str, Any], bool]:
    strategy_hash = _sha256_prefixed(strategy_spec)
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    sweep_hash = _sha256_prefixed(sweep_plan)
    committed_count = manifest["population_governance"]["declared_population"][
        "committed_population_count"
    ]
    selected_count = sweep_plan["trial_accounting"]["selected_variant_count"]
    sizing_context = _sizing_context(execution_input, sizing_mode, target_leverage)
    funding_input_identity = (
        execution_input.funding_input_identity
        if execution_input is not None
        else None
    )
    backtest_assumptions = _backtest_assumption_summary(
        sweep_plan,
        sizing_context,
        funding_input_identity,
    )
    sizing_metadata = _sizing_metadata(sizing_context)
    data_availability_claim = _data_availability_claim(strategy_spec)
    input_scope = _input_scope(
        include_sizing_metadata=sizing_metadata is not None,
        include_data_availability_claim=data_availability_claim is not None,
    )
    result_scope = _result_scope(
        include_sizing_metadata=sizing_metadata is not None,
        include_data_availability_claim=data_availability_claim is not None,
    )
    provenance_identity = _execution_provenance_identity(execution_input)
    result_population_id = _deterministic_result_population_id(
        strategy_hash,
        manifest_hash,
        sweep_hash,
        backtest_assumptions,
        provenance_identity["data_slice_identity"],
        provenance_identity["d3_validation_identity"],
        provenance_identity["execution_provenance_class"],
        provenance_identity["funding_input_identity"],
    )
    if max_workers == 1:
        rows, aborted = _execute_rows(
            result_population_id,
            strategy_spec,
            manifest,
            sweep_plan,
            deterministic_seed,
            execution_input,
            sizing_context,
            evaluation_start=evaluation_start,
            evaluation_end=evaluation_end,
        )
    else:
        rows, aborted = _execute_rows_parallel(
            result_population_id,
            strategy_spec,
            manifest,
            sweep_plan,
            deterministic_seed,
            execution_input,
            sizing_context,
            max_workers,
            evaluation_start=evaluation_start,
            evaluation_end=evaluation_end,
        )
    counts = {category: 0 for category in OUTCOME_CATEGORIES}
    counts.update(Counter(row["outcome_category"] for row in rows))
    counts["counts_sum"] = sum(counts[category] for category in OUTCOME_CATEGORIES)
    counts["counts_sum_equals_committed_denominator"] = True
    error_counts = {category: counts[category] for category in OUTCOME_CATEGORIES if category != "successful"}

    payload = {
        "schema_version": "v1",
        "result_population_id": result_population_id,
        "status": "generated",
        "non_authority_declaration": _non_authority_declaration(),
        "parent_strategy_spec": {
            "strategy_spec_id": strategy_spec["strategy_spec_id"],
            "strategy_spec_schema_version": strategy_spec["schema_version"],
            "strategy_spec_hash": strategy_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_ref": None,
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
        },
        "parent_variant_manifest": {
            "variant_manifest_id": manifest["variant_manifest_id"],
            "variant_manifest_schema_version": manifest["schema_version"],
            "manifest_hash": manifest_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "manifest_ref": None,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "committed_population_count": committed_count,
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
        },
        "parent_sweep_plan": {
            "sweep_plan_id": sweep_plan["sweep_plan_id"],
            "sweep_plan_schema_version": sweep_plan["schema_version"],
            "sweep_plan_identity_hash": sweep_hash,
            "hash_algorithm": HASH_ALGORITHM,
            "hash_scope_version": "sweep_plan_identity_hash_scope_v1",
            "sweep_plan_ref": None,
            "manifest_id": manifest["variant_manifest_id"],
            "manifest_hash": manifest_hash,
            "committed_population_count": committed_count,
            "selected_variant_count": selected_count,
            "mismatch_policy": "block",
            "missing_sweep_plan_policy": "block",
        },
        "execution_context": {
            "runner_id": "offline-research-runner",
            "runner_version": RUNNER_VERSION,
            "runner_code_ref": RUNNER_CODE_REF,
            "repo_commit": "build-test-only",
            "environment_summary": (
                execution_input.environment_summary
                if execution_input is not None
                else ["synthetic_fixture_only"]
            ),
            "dependency_summary": ["pandas", "jsonschema"],
            "determinism_seed": deterministic_seed,
            "execution_mode": "offline_research",
            "offline_only": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_broker_exchange_order_contact": True,
            "no_protected_path_contact": True,
        },
        "input_identity_hash": _identity_hash_object("input_identity_hash_scope_v1", input_scope),
        "result_population_identity_hash": _identity_hash_object(
            RESULT_POPULATION_HASH_SCOPE_VERSION,
            result_scope,
        ),
        "audit_envelope": {
            "excluded_from_input_identity_hash": True,
            "excluded_from_result_population_identity_hash": True,
            "may_contain_scientific_content": False,
            "administrative_only": True,
            "created_at": FIXED_AUDIT_TIMESTAMP,
            "created_by": "tools.research_runner.run_offline_sweep",
            "review_notes": [],
            "operator_notes": [f"run_label={run_label}"] if run_label else [],
            "validation_run_logs": [],
            "administrative_lineage": [],
        },
        "committed_denominator_snapshot": {
            "denominator_basis": "committed_pre_registered_population_count",
            "parent_manifest_committed_population_count": committed_count,
            "parent_sweep_plan_committed_population_count": committed_count,
            "selected_variant_count": selected_count,
            "result_row_count": len(rows),
            "outcome_counts_sum": counts["counts_sum"],
            "committed_denominator": committed_count,
            **_denominator_flags(),
        },
        "variant_result_rows": rows,
        "outcome_category_counts": counts,
        "append_only_ledger": {
            "ledger_required": True,
            "append_only": True,
            "post_commit_in_place_mutation_forbidden": True,
            "scientific_identity_mutation_forbidden_after_finalization": True,
            "corrections_require_append_only_event": True,
            "supersession_preserves_prior_result_population": True,
            "creation_event_ref": f"{result_population_id}-EVENT-001",
            "events": [
                {
                    "event_id": f"{result_population_id}-EVENT-001",
                    "event_type": "created",
                    "event_timestamp": FIXED_AUDIT_TIMESTAMP,
                    "actor_or_tool": "tools.research_runner.run_offline_sweep",
                    "related_artifact_refs": [],
                    "notes": [
                        "build-and-test-only canonical 15m runner output"
                        if execution_input is not None
                        else "build-and-test-only synthetic runner output"
                    ],
                }
            ],
        },
        "validation_summary": {
            "schema_validation_status": "passed",
            "validator_status": "passed",
            "validator_version": "wp-s2c-189",
            "validator_identity": "tools.registry.validate_result_populations",
            "validation_timestamp": FIXED_AUDIT_TIMESTAMP,
            "blocking_errors": [],
            "non_blocking_warnings": [],
            "validator_authority_boundary": "evidence_only_no_approval_no_execution",
            "validator_does_not_approve": True,
            "validator_does_not_recommend": True,
            "validator_does_not_rank": True,
            "validator_does_not_execute": True,
            "validator_does_not_contact_runtime": True,
        },
        "error_summary": {
            "failed": error_counts["failed"],
            "errored": error_counts["errored"],
            "aborted": error_counts["aborted"],
            "filtered": error_counts["filtered"],
            "data_unavailable": error_counts["data_unavailable"],
            "not_attempted": error_counts["not_attempted"],
            "invalid": error_counts["invalid"],
            "excluded": error_counts["excluded"],
            "all_error_categories_counted_in_denominator": True,
            "error_rows_preserved": True,
        },
        "data_coverage_summary": {
            "data_catalog_ref": (
                execution_input.data_catalog_ref
                if execution_input is not None
                else "synthetic_fixture_only"
            ),
            "data_slice_identity": (
                execution_input.data_slice_identity
                if execution_input is not None
                else "synthetic-offline-runner-v1"
            ),
            "timeframe": execution_input.timeframe if execution_input is not None else "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap_count": counts["data_unavailable"],
            "data_unavailable_count": counts["data_unavailable"],
            "data_coverage_notes": (
                [
                    *execution_input.data_coverage_notes,
                    *(
                        [
                            f"evaluation_window_start={evaluation_start.isoformat().replace('+00:00', 'Z')}",
                            f"evaluation_window_end={evaluation_end.isoformat().replace('+00:00', 'Z')}",
                            "evaluation_window_warmup_masked=true",
                            "pre_window_entries_blocked_by_signal_mask",
                        ]
                        if evaluation_start is not None and evaluation_end is not None
                        else []
                    ),
                ]
                if execution_input is not None
                else ["fixture/synthetic data only"]
            ),
        },
        "backtest_assumption_summary": backtest_assumptions,
        "lineage": {
            "strategy_spec_id": strategy_spec["strategy_spec_id"],
            "variant_manifest_id": manifest["variant_manifest_id"],
            "sweep_plan_id": sweep_plan["sweep_plan_id"],
            "result_population_id": result_population_id,
            "parent_hash_chain": {
                "strategy_spec_hash": strategy_hash,
                "variant_manifest_hash": manifest_hash,
                "sweep_plan_identity_hash": sweep_hash,
                "input_identity_hash": None,
            },
            "created_from_validated_inputs": True,
            "complete_population_lineage_preserved": True,
        },
        "review": {
            "review_status": "not_reviewed",
            "review_scope": "none",
            "review_notes": [],
            "non_authority_acknowledgement": {
                "not_approval": True,
                "not_recommendation": True,
                "not_readiness": True,
                "not_transition": True,
                "not_gate_satisfaction": True,
                "not_runtime_authority": True,
                "not_paper_live_authority": True,
            },
        },
    }
    if sizing_metadata is not None:
        payload["sizing_metadata"] = sizing_metadata
    if data_availability_claim is not None:
        payload["data_availability_claim"] = data_availability_claim
    payload["input_identity_hash"]["hash"] = _canonical_hash(payload, input_scope)
    payload["lineage"]["parent_hash_chain"]["input_identity_hash"] = payload["input_identity_hash"][
        "hash"
    ]
    payload["result_population_identity_hash"]["hash"] = _canonical_hash(payload, result_scope)
    return payload, aborted


def _identity_hash_object(scope_version: str, scope: list[str]) -> dict[str, Any]:
    return {
        "hash": None,
        "hash_algorithm": HASH_ALGORITHM,
        "canonicalization": "json_canonical_v1",
        "hash_scope_version": scope_version,
        "hash_scope": scope,
        "audit_envelope_excluded": True,
        "audit_envelope_exclusion_reason": (
            "administrative_audit_metadata_is_excluded_from_scientific_identity"
        ),
    }


def _input_scope(
    *,
    include_sizing_metadata: bool = False,
    include_data_availability_claim: bool = False,
) -> list[str]:
    scope = [
        "parent_strategy_spec.strategy_spec_hash",
        "parent_variant_manifest.manifest_hash",
        "parent_sweep_plan.sweep_plan_identity_hash",
        "parent_variant_manifest.committed_population_count",
        "parent_sweep_plan.committed_population_count",
        "execution_context.runner_code_ref",
        "execution_context.repo_commit",
        "data_coverage_summary.data_catalog_ref",
        "data_coverage_summary.data_slice_identity",
        "backtest_assumption_summary",
    ]
    if include_data_availability_claim:
        scope.insert(scope.index("backtest_assumption_summary"), "data_availability_claim")
    if include_sizing_metadata:
        scope.append("sizing_metadata")
    return scope


def _result_scope(
    *,
    include_sizing_metadata: bool = False,
    include_data_availability_claim: bool = False,
) -> list[str]:
    return [
        *_input_scope(
            include_sizing_metadata=include_sizing_metadata,
            include_data_availability_claim=include_data_availability_claim,
        ),
        "committed_denominator_snapshot",
        "variant_result_rows",
        "outcome_category_counts",
        "append_only_ledger.creation_event_ref",
        "validation_summary.validator_identity",
    ]


def _non_authority_declaration() -> dict[str, Any]:
    flags = [
        "not_executable",
        "not_runner_authority",
        "not_sweep_authority",
        "not_result_authority",
        "not_candidate_approval",
        "not_exp_approval",
        "not_ranking_authority",
        "not_recommendation_authority",
        "not_readiness_authority",
        "not_transition_authority",
        "not_runtime_authority",
        "not_paper_live_authority",
        "not_gate_authority",
        "not_canonical_evidence_replacement",
        "not_trial_log_replacement",
        "not_outcome_ledger_replacement",
        "not_reconciliation_authority",
        "not_decision_authority",
        "not_exp_replacement",
        "not_rep_replacement",
        "not_ol_replacement",
        "not_rec_replacement",
        "not_dec_replacement",
    ]
    return {**{flag: True for flag in flags}, "canonical_evidence_relationship": "reference_only"}


def _denominator_flags() -> dict[str, bool]:
    return {
        "denominator_equals_parent_manifest_committed_population_count": True,
        "denominator_equals_parent_sweep_plan_committed_population_count": True,
        "outcome_counts_sum_equals_committed_denominator": True,
        "result_row_count_equals_committed_denominator": True,
        "executed_only_denominator_forbidden": True,
        "successful_only_denominator_forbidden": True,
        "winner_only_retention_forbidden": True,
        "post_hoc_cleanup_forbidden": True,
        "failed_variants_remain_in_denominator": True,
        "invalid_variants_remain_in_denominator": True,
        "excluded_variants_remain_in_denominator": True,
        "errored_variants_remain_in_denominator": True,
        "aborted_variants_remain_in_denominator": True,
        "filtered_variants_remain_in_denominator": True,
        "data_unavailable_variants_remain_in_denominator": True,
        "not_attempted_variants_remain_in_denominator": True,
    }


def _validate_in_memory_payload(payload: dict[str, Any]) -> None:
    schema = _load_json(DEFAULT_RESULT_POPULATION_SCHEMA_PATH)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path)
        prefix = f"{location}: " if location else ""
        raise OfflineSweepError(f"result-population schema validation failed: {prefix}{first.message}")
    for object_path in ("input_identity_hash", "result_population_identity_hash"):
        scope = payload[object_path]["hash_scope"]
        if payload[object_path]["hash"] != _canonical_hash(payload, scope):
            raise OfflineSweepError(f"{object_path}.hash mismatch")


def _write_and_validate(
    payload: dict[str, Any],
    output_dir: Path,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{payload['result_population_id']}.result_population.json"
    _write_json(path, payload)
    errors = validate_result_populations(
        result_populations_dir=output_dir,
        strategy_specs_dir=strategy_spec_path.parent,
        variant_manifests_dir=variant_manifest_path.parent,
        sweep_plans_dir=sweep_plan_path.parent,
    )
    if errors:
        raise OfflineSweepError("; ".join(errors))
    return path


def run_offline_sweep(
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    output_dir: Path | None = None,
    *,
    write_result_population: bool = False,
    run_label: str | None = None,
    deterministic_seed: int = 0,
    canonical_15m: bool = False,
    canonical_30m: bool = False,
    canonical_1h: bool = False,
    canonical_4h: bool = False,
    canonical_1d: bool = False,
    ohlcv_input_path: Path | None = None,
    funding_cost_mode: str = "off",
    funding_provenance_path: Path | None = None,
    funding_data_root: Path | None = None,
    d4_catalog_slice_path: Path | None = None,
    d2_import_report_path: Path | None = None,
    d4h_catalog_slice_path: Path | None = None,
    d4h_validation_report_path: Path | None = None,
    d4h_derivation_report_path: Path | None = None,
    research_feature_manifest_path: Path | None = None,
    research_feature_input_path: Path | None = None,
    sizing_mode: str = SIZING_MODE_FIXED_ORDER_SIZE,
    target_leverage: float = DEFAULT_TARGET_LEVERAGE,
    walkforward: bool = False,
    walkforward_is_bars: int | None = None,
    walkforward_oos_bars: int | None = None,
    walkforward_step_bars: int | None = None,
    walkforward_max_windows: int | None = None,
    max_workers: int = DEFAULT_MAX_WORKERS,
    evaluation_start: pd.Timestamp | None = None,
    evaluation_end: pd.Timestamp | None = None,
) -> dict[str, Any]:
    """Run a deterministic build-and-test-only offline research sweep."""
    if deterministic_seed is None:
        raise OfflineSweepError("deterministic_seed must be fixed")
    if walkforward and write_result_population:
        raise OfflineSweepError("walk-forward mode is dry-run-only and cannot write result populations")
    if walkforward and (walkforward_is_bars is None or walkforward_oos_bars is None):
        raise OfflineSweepError(
            "walk-forward mode requires --walkforward-is-bars and --walkforward-oos-bars"
        )
    sizing_mode = _validate_sizing_mode(sizing_mode)
    target_leverage = _validate_target_leverage(target_leverage)
    max_workers = _validate_max_workers(max_workers)
    funding_cost_mode = _validate_funding_cost_mode(funding_cost_mode)
    if funding_cost_mode == "off" and (
        funding_provenance_path is not None or funding_data_root is not None
    ):
        raise OfflineSweepError(
            "funding provenance/data-root arguments are invalid when --funding-cost-mode=off"
        )
    if funding_cost_mode == "on" and funding_provenance_path is None:
        raise OfflineSweepError("--funding-provenance is required when --funding-cost-mode=on")
    if sum((canonical_15m, canonical_30m, canonical_1h, canonical_4h, canonical_1d)) > 1:
        raise OfflineSweepError("canonical 15m, 30m, 1h, 4h, and 1d routes are mutually exclusive")
    feature_args_present = (
        research_feature_manifest_path is not None,
        research_feature_input_path is not None,
    )
    if any(feature_args_present) and not all(feature_args_present):
        raise OfflineSweepError(
            "--research-feature-manifest and --research-feature-input are a required pair"
        )
    if all(feature_args_present) and not canonical_15m:
        raise OfflineSweepError("research feature-table inputs are supported only with --canonical-15m")
    guarded_output_dir = _guard_output_dir(output_dir, write_result_population)
    strategy_spec, manifest, sweep_plan = _validate_parent_inputs(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
    )
    if funding_cost_mode == "off" and _requires_funding_costs(strategy_spec, sweep_plan):
        raise OfflineSweepError("strategy/sweep requires funding costs but funding mode is off")
    declared_non_ohlcv_columns = _declared_non_ohlcv_columns(strategy_spec)
    execution_input = None
    if canonical_15m:
        primary_timeframe = strategy_spec.get("timeframe_and_data", {}).get("primary_timeframe")
        sweep_timeframe = sweep_plan.get("data_and_timeframe_assumptions", {}).get("primary_timeframe")
        if primary_timeframe != "15m" or sweep_timeframe != "15m":
            raise OfflineSweepError("canonical_15m requires 15m Strategy Spec and Sweep Plan")
        if d4_catalog_slice_path is not None or d2_import_report_path is not None:
            execution_input = _d4_catalog_execution_input(
                ohlcv_input_path,
                d4_catalog_slice_path,
                d2_import_report_path,
                () if all(feature_args_present) else declared_non_ohlcv_columns,
            )
        else:
            execution_input = _canonical_15m_execution_input(
                ohlcv_input_path,
                declared_non_ohlcv_columns,
            )
        if all(feature_args_present):
            if d4_catalog_slice_path is None or d2_import_report_path is None:
                raise OfflineSweepError(
                    "research feature-table inputs require D4 15m provenance mode"
                )
            assert execution_input is not None
            assert ohlcv_input_path is not None
            assert research_feature_manifest_path is not None
            assert research_feature_input_path is not None
            execution_input = _bind_research_feature_input(
                execution_input,
                ohlcv_input_path=ohlcv_input_path,
                d4_catalog_slice_path=d4_catalog_slice_path,
                feature_manifest_path=research_feature_manifest_path,
                feature_input_path=research_feature_input_path,
                requested_feature_names=declared_non_ohlcv_columns,
            )
    elif canonical_30m or canonical_1h:
        timeframe = "30m" if canonical_30m else "1h"
        primary_timeframe = strategy_spec.get("timeframe_and_data", {}).get("primary_timeframe")
        sweep_timeframe = sweep_plan.get("data_and_timeframe_assumptions", {}).get(
            "primary_timeframe"
        )
        if primary_timeframe != timeframe or sweep_timeframe != timeframe:
            raise OfflineSweepError(
                f"canonical_{timeframe} requires {timeframe} Strategy Spec and Sweep Plan"
            )
        if d4_catalog_slice_path is not None or d2_import_report_path is not None:
            raise OfflineSweepError("D4 15m provenance flags require --canonical-15m")
        if (
            d4h_catalog_slice_path is not None
            or d4h_validation_report_path is not None
            or d4h_derivation_report_path is not None
        ):
            raise OfflineSweepError("D4H provenance flags require --canonical-4h")
        execution_input = _canonical_intraday_derived_execution_input(
            timeframe,
            ohlcv_input_path,
            additional_columns=declared_non_ohlcv_columns,
        )
    elif canonical_4h:
        primary_timeframe = strategy_spec.get("timeframe_and_data", {}).get("primary_timeframe")
        sweep_timeframe = sweep_plan.get("data_and_timeframe_assumptions", {}).get("primary_timeframe")
        if primary_timeframe != "4h" or sweep_timeframe != "4h":
            raise OfflineSweepError("canonical_4h requires 4h Strategy Spec and Sweep Plan")
        if d4_catalog_slice_path is not None or d2_import_report_path is not None:
            raise OfflineSweepError("D4 15m provenance flags require --canonical-15m")
        execution_input = _canonical_4h_execution_input(
            ohlcv_input_path,
            d4h_catalog_slice_path,
            d4h_validation_report_path,
            d4h_derivation_report_path,
            declared_non_ohlcv_columns,
        )
    elif canonical_1d:
        primary_timeframe = strategy_spec.get("timeframe_and_data", {}).get("primary_timeframe")
        sweep_timeframe = sweep_plan.get("data_and_timeframe_assumptions", {}).get(
            "primary_timeframe"
        )
        if primary_timeframe != "1d" or sweep_timeframe != "1d":
            raise OfflineSweepError("canonical_1d requires 1d Strategy Spec and Sweep Plan")
        if ohlcv_input_path is not None:
            raise OfflineSweepError("--ohlcv-input is forbidden with --canonical-1d")
        if d4_catalog_slice_path is not None or d2_import_report_path is not None:
            raise OfflineSweepError("D4 15m provenance flags require --canonical-15m")
        if (
            d4h_catalog_slice_path is not None
            or d4h_validation_report_path is not None
            or d4h_derivation_report_path is not None
        ):
            raise OfflineSweepError("D4H provenance flags require --canonical-4h")
        execution_input = _canonical_1d_execution_input(declared_non_ohlcv_columns)
    elif d4_catalog_slice_path is not None or d2_import_report_path is not None:
        raise OfflineSweepError("D4 provenance mode requires --canonical-15m")
    elif (
        d4h_catalog_slice_path is not None
        or d4h_validation_report_path is not None
        or d4h_derivation_report_path is not None
    ):
        raise OfflineSweepError("D4H provenance mode requires --canonical-4h")
    if funding_cost_mode == "on":
        if execution_input is None:
            raise OfflineSweepError(
                "funding mode on requires an existing canonical 15m, 30m, 1h, 4h, or 1d input route"
            )
        assert funding_provenance_path is not None
        funding_frame, funding_identity = _load_validated_funding_input(
            funding_provenance_path,
            funding_data_root,
        )
        execution_input = _bind_funding_input(
            execution_input,
            funding_cost_mode="on",
            funding=funding_frame,
            funding_identity=funding_identity,
        )
    elif execution_input is not None:
        execution_input = _bind_funding_input(
            execution_input,
            funding_cost_mode="off",
        )
    if walkforward and execution_input is None:
        raise OfflineSweepError("walk-forward mode currently requires canonical input data")
    if evaluation_start is not None or evaluation_end is not None:
        if evaluation_start is None or evaluation_end is None:
            raise OfflineSweepError(
                "--evaluation-start and --evaluation-end must both be provided together"
            )
        if execution_input is None:
            raise OfflineSweepError(
                "evaluation window requires canonical input data "
                "(--canonical-15m, --canonical-30m, --canonical-1h, "
                "--canonical-4h, or --canonical-1d)"
            )
        _validate_evaluation_window(evaluation_start, evaluation_end, execution_input.ohlcv)
    payload, aborted = _build_result_population(
        strategy_spec,
        manifest,
        sweep_plan,
        run_label,
        deterministic_seed,
        execution_input,
        sizing_mode,
        target_leverage,
        max_workers,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
    )
    _validate_in_memory_payload(payload)

    output_path = None
    if write_result_population:
        assert guarded_output_dir is not None
        output_path = _write_and_validate(
            payload,
            guarded_output_dir,
            strategy_spec_path,
            variant_manifest_path,
            sweep_plan_path,
        )
    walkforward_summary = None
    if walkforward:
        assert execution_input is not None
        assert walkforward_is_bars is not None
        assert walkforward_oos_bars is not None
        walkforward_summary = _run_walkforward_dry_run(
            strategy_spec=strategy_spec,
            manifest=manifest,
            execution_input=execution_input,
            sizing_mode=sizing_mode,
            target_leverage=target_leverage,
            in_sample_bars=walkforward_is_bars,
            out_of_sample_bars=walkforward_oos_bars,
            step_bars=walkforward_step_bars,
            max_windows=walkforward_max_windows,
            max_workers=max_workers,
        )
    return {
        "ok": not aborted,
        "aborted": aborted,
        "dry_run": not write_result_population,
        "wrote": output_path is not None,
        "output_path": str(output_path) if output_path else None,
        "result_population": payload,
        "result_population_id": payload["result_population_id"],
        "committed_denominator": payload["committed_denominator_snapshot"][
            "committed_denominator"
        ],
        "outcome_category_counts": payload["outcome_category_counts"],
        "walkforward": walkforward_summary,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy-spec", required=True, type=Path)
    parser.add_argument("--variant-manifest", required=True, type=Path)
    parser.add_argument("--sweep-plan", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-result-population", action="store_true")
    parser.add_argument("--run-label")
    parser.add_argument("--deterministic-seed", type=int, default=0)
    parser.add_argument("--canonical-15m", action="store_true")
    parser.add_argument("--canonical-30m", action="store_true")
    parser.add_argument("--canonical-1h", action="store_true")
    parser.add_argument("--canonical-4h", action="store_true")
    parser.add_argument("--canonical-1d", action="store_true")
    parser.add_argument("--ohlcv-input", type=Path)
    parser.add_argument(
        "--funding-cost-mode",
        choices=FUNDING_COST_MODES,
        default="off",
        help=(
            "Funding cost mode. Defaults to off; on requires the canonical local "
            "provenance artifact."
        ),
    )
    parser.add_argument("--funding-provenance", type=Path)
    parser.add_argument(
        "--funding-data-root",
        type=Path,
        help="Optional clean local checkout root containing the bound data/processed Parquet.",
    )
    parser.add_argument("--d4-catalog-slice", type=Path)
    parser.add_argument("--d2-import-report", type=Path)
    parser.add_argument("--d4h-catalog-slice", type=Path)
    parser.add_argument("--d4h-validation-report", type=Path)
    parser.add_argument("--d4h-derivation-report", type=Path)
    parser.add_argument("--research-feature-manifest", type=Path)
    parser.add_argument("--research-feature-input", type=Path)
    parser.add_argument(
        "--sizing-mode",
        choices=SIZING_MODES,
        default=SIZING_MODE_FIXED_ORDER_SIZE,
        help=(
            "Backtest sizing mode. Defaults to fixed_order_size; "
            "dynamic_equity_target_leverage is opt-in."
        ),
    )
    parser.add_argument(
        "--target-leverage",
        type=_parse_target_leverage,
        default=DEFAULT_TARGET_LEVERAGE,
        help="Positive finite leverage used by fixed resolution or dynamic equity sizing.",
    )
    parser.add_argument(
        "--walkforward",
        action="store_true",
        help="Run dry-run-only build-test walk-forward IS/OOS partition reporting.",
    )
    parser.add_argument("--walkforward-is-bars", type=_positive_int_arg("--walkforward-is-bars"))
    parser.add_argument("--walkforward-oos-bars", type=_positive_int_arg("--walkforward-oos-bars"))
    parser.add_argument("--walkforward-step-bars", type=_positive_int_arg("--walkforward-step-bars"))
    parser.add_argument("--walkforward-max-windows", type=_positive_int_arg("--walkforward-max-windows"))
    parser.add_argument(
        "--max-workers",
        type=_positive_int_arg("--max-workers"),
        default=DEFAULT_MAX_WORKERS,
        help="Opt-in process worker count for variant/window-level parallelism. Defaults to 1.",
    )
    parser.add_argument(
        "--evaluation-start",
        help=(
            "Warmup-preserving evaluation window start (UTC ISO-8601, inclusive). "
            "Indicators are compiled on the full input frame starting from the first bar; "
            "only bars from evaluation_start onward are scored. "
            "Must be paired with --evaluation-end."
        ),
    )
    parser.add_argument(
        "--evaluation-end",
        help=(
            "Evaluation window end (UTC ISO-8601, exclusive). "
            "Must be paired with --evaluation-start."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        evaluation_start = (
            _parse_metadata_timestamp(args.evaluation_start, "--evaluation-start")
            if args.evaluation_start
            else None
        )
        evaluation_end = (
            _parse_metadata_timestamp(args.evaluation_end, "--evaluation-end")
            if args.evaluation_end
            else None
        )
        result = run_offline_sweep(
            args.strategy_spec,
            args.variant_manifest,
            args.sweep_plan,
            args.output_dir,
            write_result_population=args.write_result_population,
            run_label=args.run_label,
            deterministic_seed=args.deterministic_seed,
            canonical_15m=args.canonical_15m,
            canonical_30m=args.canonical_30m,
            canonical_1h=args.canonical_1h,
            canonical_4h=args.canonical_4h,
            canonical_1d=args.canonical_1d,
            ohlcv_input_path=args.ohlcv_input,
            funding_cost_mode=args.funding_cost_mode,
            funding_provenance_path=args.funding_provenance,
            funding_data_root=args.funding_data_root,
            d4_catalog_slice_path=args.d4_catalog_slice,
            d2_import_report_path=args.d2_import_report,
            d4h_catalog_slice_path=args.d4h_catalog_slice,
            d4h_validation_report_path=args.d4h_validation_report,
            d4h_derivation_report_path=args.d4h_derivation_report,
            research_feature_manifest_path=args.research_feature_manifest,
            research_feature_input_path=args.research_feature_input,
            sizing_mode=args.sizing_mode,
            target_leverage=args.target_leverage,
            walkforward=args.walkforward,
            walkforward_is_bars=args.walkforward_is_bars,
            walkforward_oos_bars=args.walkforward_oos_bars,
            walkforward_step_bars=args.walkforward_step_bars,
            walkforward_max_windows=args.walkforward_max_windows,
            max_workers=args.max_workers,
            evaluation_start=evaluation_start,
            evaluation_end=evaluation_end,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": result["ok"],
                "aborted": result["aborted"],
                "dry_run": result["dry_run"],
                "wrote": result["wrote"],
                "output_path": result["output_path"],
                "result_population_id": result["result_population_id"],
                "committed_denominator": result["committed_denominator"],
                "outcome_category_counts": result["outcome_category_counts"],
                "walkforward": result["walkforward"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
