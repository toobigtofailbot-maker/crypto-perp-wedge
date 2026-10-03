"""Pure scientific identity and semantic validation for research feature tables."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from tools.execution_evidence_contract import canonical_json_bytes, content_sha256


FEATURE_TABLE_SCHEMA_VERSION = "cpw_research_feature_table_v1"
FEATURE_JOIN_CONTRACT_VERSION = "cpw_research_feature_join_v1"
FEATURE_TABLE_IDENTITY_VERSION = "cpw_research_feature_table_identity_v1"
COMPOSITE_DATA_IDENTITY_VERSION = "cpw_research_composite_data_identity_v1"
D4_TAKER_SOURCE_CLASS = "CANONICAL_D4_KLINE_DERIVATION"
D4_TAKER_DERIVATION_VERSION = "cpw_d4_native_takerflow_v1"
D4_TAKER_PARENT_FIELDS = ("volume", "num_trades", "taker_buy_base_vol")
D4_TAKER_FEATURE_DEFINITIONS = (
    {
        "feature_name": "taker_buy_volume",
        "formula": "taker_buy_base_vol",
        "null_policy": "forbidden",
    },
    {
        "feature_name": "taker_sell_volume",
        "formula": "volume - taker_buy_base_vol",
        "null_policy": "forbidden",
    },
    {
        "feature_name": "taker_buy_sell_ratio",
        "formula": (
            "null if taker_sell_volume == 0 else "
            "taker_buy_volume / taker_sell_volume"
        ),
        "null_policy": "null_when_taker_sell_volume_zero",
    },
)

_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_SOURCE_CLASS = re.compile(r"^[A-Z][A-Z0-9_]*$")
_CONTRACT_FIELDS = {
    "schema_version",
    "family_id",
    "market_identity",
    "timeframe",
    "feature_names",
    "source_class",
    "availability_assertions",
    "source_set_identity",
    "output_identity",
    "coverage",
    "causality",
    "quality_policy",
    "feature_table_identity",
    "non_authority",
}
_OPTIONAL_CONTRACT_FIELDS = {"parent_identity", "derivation"}
_PARENT_IDENTITY_FIELDS = {
    "data_slice_identity",
    "normalized_sha256",
    "row_count",
    "coverage_start_utc_inclusive",
    "coverage_end_utc_exclusive",
}
_DERIVATION_FIELDS = {"derivation_version", "parent_fields", "features"}
_MARKET_FIELDS = {"venue", "market_type", "symbol"}
_OUTPUT_FIELDS = {"format", "sha256", "row_count", "columns"}
_COVERAGE_FIELDS = {
    "start_utc_inclusive",
    "end_utc_exclusive",
    "expected_row_count",
    "observed_row_count",
    "complete",
}
_CAUSALITY = {
    "timestamp_semantics": "UTC bar open",
    "feature_available_at_semantics": "exclusive bar close",
    "completed_bar_only": True,
    "future_events_can_change_prior_completed_bars": False,
}
_QUALITY_POLICY = {
    "fill": "forbidden",
    "forward_fill": "forbidden",
    "backfill": "forbidden",
    "interpolation": "forbidden",
    "timestamp_tolerance": "forbidden",
    "missing_row": "fail_closed",
    "duplicate_join_key": "fail_closed",
}
_NON_AUTHORITY = {
    "authorizes_execution": False,
    "authorizes_result_population": False,
    "authorizes_candidate": False,
    "authorizes_promotion": False,
    "authorizes_runtime_paper_live": False,
    "authorizes_oms_risk_reconciliation": False,
}


class FeatureDataContractError(ValueError):
    """Raised when feature-data content fails the closed scientific contract."""


def _closed(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    keys = set(value)
    if keys != expected:
        raise FeatureDataContractError(
            f"{label} fields mismatch; missing={sorted(expected - keys)}, "
            f"unknown={sorted(keys - expected)}"
        )


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FeatureDataContractError(f"{label} must be an object")
    return value


def _non_empty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FeatureDataContractError(f"{label} must be a non-empty string")
    return value


def _identity_sources(source_files: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, source in enumerate(source_files):
        required = {
            "logical_filename",
            "sha256",
            "size_bytes",
            "parsed_row_count",
            "source_type",
        }
        missing = required - set(source)
        if missing:
            raise FeatureDataContractError(
                f"source_files.{index} missing stable identity fields: {sorted(missing)}"
            )
        filename = _non_empty(source["logical_filename"], f"source_files.{index}.logical_filename")
        if "/" in filename or "\\" in filename:
            raise FeatureDataContractError("logical_filename must not contain a local path")
        digest = _non_empty(source["sha256"], f"source_files.{index}.sha256")
        if not _HEX_SHA256.fullmatch(digest):
            raise FeatureDataContractError("source file sha256 must be 64 lowercase hex")
        size = source["size_bytes"]
        rows = source["parsed_row_count"]
        if not isinstance(size, int) or size <= 0 or not isinstance(rows, int) or rows <= 0:
            raise FeatureDataContractError("source size and parsed row count must be positive integers")
        normalized.append(
            {
                "logical_filename": filename,
                "sha256": digest,
                "size_bytes": size,
                "parsed_row_count": rows,
                "source_type": _non_empty(source["source_type"], f"source_files.{index}.source_type"),
            }
        )
    if not normalized:
        raise FeatureDataContractError("source_files must not be empty")
    normalized.sort(key=lambda item: (item["logical_filename"], item["sha256"]))
    if len({item["logical_filename"] for item in normalized}) != len(normalized):
        raise FeatureDataContractError("source logical filenames must be unique")
    return normalized


def build_source_set_identity(
    source_files: Sequence[Mapping[str, Any]],
    *,
    identity_context: Mapping[str, Any] | None = None,
) -> str:
    """Hash stable source facts, deliberately excluding machine-local paths."""

    payload: dict[str, Any] = {
        "identity_version": "cpw_research_feature_source_set_identity_v1",
        "source_files": _identity_sources(source_files),
    }
    if identity_context is not None:
        payload["identity_context"] = dict(identity_context)
    return content_sha256(payload)


def build_feature_table_identity(contract: Mapping[str, Any]) -> str:
    """Hash every generic scientific contract field except its self hash."""

    payload = dict(contract)
    payload.pop("feature_table_identity", None)
    payload = {
        "identity_version": FEATURE_TABLE_IDENTITY_VERSION,
        "feature_table": payload,
    }
    return content_sha256(payload)


def build_composite_research_data_identity(
    *,
    base_data_slice_identity: str,
    base_normalized_sha256: str,
    feature_table_identity: str,
    feature_output_sha256: str,
    market_identity: Mapping[str, Any],
    timeframe: str,
    coverage_start_utc_inclusive: str,
    coverage_end_utc_exclusive: str,
    joined_row_count: int,
    selected_feature_names: Sequence[str],
) -> str:
    """Build the path-independent identity for a base grid plus one feature table."""

    names = list(selected_feature_names)
    if not names or len(names) != len(set(names)) or names != sorted(names):
        raise FeatureDataContractError("selected_feature_names must be non-empty, unique, and sorted")
    if not _HEX_SHA256.fullmatch(base_normalized_sha256):
        raise FeatureDataContractError("base_normalized_sha256 must be 64 lowercase hex")
    if not _HEX_SHA256.fullmatch(feature_output_sha256):
        raise FeatureDataContractError("feature_output_sha256 must be 64 lowercase hex")
    if not _SHA256.fullmatch(feature_table_identity):
        raise FeatureDataContractError("feature_table_identity must be sha256:<64 lowercase hex>")
    if not isinstance(joined_row_count, int) or joined_row_count <= 0:
        raise FeatureDataContractError("joined_row_count must be a positive integer")
    payload = {
        "identity_version": COMPOSITE_DATA_IDENTITY_VERSION,
        "join_contract_version": FEATURE_JOIN_CONTRACT_VERSION,
        "base_data_slice_identity": _non_empty(base_data_slice_identity, "base_data_slice_identity"),
        "base_normalized_sha256": base_normalized_sha256,
        "feature_table_identity": feature_table_identity,
        "feature_output_sha256": feature_output_sha256,
        "market_identity": dict(market_identity),
        "timeframe": _non_empty(timeframe, "timeframe"),
        "coverage": {
            "start_utc_inclusive": _non_empty(
                coverage_start_utc_inclusive, "coverage_start_utc_inclusive"
            ),
            "end_utc_exclusive": _non_empty(
                coverage_end_utc_exclusive, "coverage_end_utc_exclusive"
            ),
            "joined_row_count": joined_row_count,
        },
        "selected_feature_names": names,
    }
    digest = content_sha256(payload).split(":", 1)[1]
    return f"cpw_research_composite_15m:sha256:{digest}"


def validate_feature_table_contract(
    contract: Mapping[str, Any],
    *,
    source_files: Sequence[Mapping[str, Any]] | None = None,
    source_identity_context: Mapping[str, Any] | None = None,
) -> None:
    """Validate semantic invariants not safely expressed by JSON Schema alone."""

    contract = _mapping(contract, "research_feature_table")
    missing = _CONTRACT_FIELDS - set(contract)
    unknown = set(contract) - _CONTRACT_FIELDS - _OPTIONAL_CONTRACT_FIELDS
    if missing or unknown:
        raise FeatureDataContractError(
            "research_feature_table fields mismatch; "
            f"missing={sorted(missing)}, unknown={sorted(unknown)}"
        )
    if contract.get("schema_version") != FEATURE_TABLE_SCHEMA_VERSION:
        raise FeatureDataContractError("unsupported feature-table schema version")
    family_id = _non_empty(contract.get("family_id"), "family_id")
    if not _NAME.fullmatch(family_id):
        raise FeatureDataContractError("family_id must be lowercase snake case")
    market = _mapping(contract.get("market_identity"), "market_identity")
    _closed(market, _MARKET_FIELDS, "market_identity")
    for field in sorted(_MARKET_FIELDS):
        _non_empty(market.get(field), f"market_identity.{field}")
    _non_empty(contract.get("timeframe"), "timeframe")
    source_class = _non_empty(contract.get("source_class"), "source_class")
    if not _SOURCE_CLASS.fullmatch(source_class):
        raise FeatureDataContractError("source_class must be uppercase underscore notation")

    parent_identity = contract.get("parent_identity")
    derivation = contract.get("derivation")
    if source_class == D4_TAKER_SOURCE_CLASS:
        if not isinstance(parent_identity, Mapping) or not isinstance(derivation, Mapping):
            raise FeatureDataContractError(
                "canonical D4 kline derivation requires parent_identity and derivation"
            )
        _closed(parent_identity, _PARENT_IDENTITY_FIELDS, "parent_identity")
        if not _non_empty(
            parent_identity.get("data_slice_identity"),
            "parent_identity.data_slice_identity",
        ).startswith("binance_usdtm_btcusdt_ohlcv_15m:sha256:"):
            raise FeatureDataContractError("parent identity must be canonical BTCUSDT 15m D4")
        if not _HEX_SHA256.fullmatch(str(parent_identity.get("normalized_sha256", ""))):
            raise FeatureDataContractError("parent normalized SHA-256 must be 64 lowercase hex")
        if not isinstance(parent_identity.get("row_count"), int) or parent_identity["row_count"] <= 0:
            raise FeatureDataContractError("parent row_count must be a positive integer")
        _non_empty(
            parent_identity.get("coverage_start_utc_inclusive"),
            "parent_identity.coverage_start_utc_inclusive",
        )
        _non_empty(
            parent_identity.get("coverage_end_utc_exclusive"),
            "parent_identity.coverage_end_utc_exclusive",
        )
        _closed(derivation, _DERIVATION_FIELDS, "derivation")
        if derivation.get("derivation_version") != D4_TAKER_DERIVATION_VERSION:
            raise FeatureDataContractError("unsupported canonical D4 taker derivation version")
        if derivation.get("parent_fields") != list(D4_TAKER_PARENT_FIELDS):
            raise FeatureDataContractError("canonical D4 taker parent fields mismatch")
        if derivation.get("features") != [dict(item) for item in D4_TAKER_FEATURE_DEFINITIONS]:
            raise FeatureDataContractError("canonical D4 taker feature formulas/null policy mismatch")
    elif parent_identity is not None or derivation is not None:
        raise FeatureDataContractError(
            "parent_identity and derivation are reserved for canonical D4 kline derivation"
        )

    names = contract.get("feature_names")
    if not isinstance(names, list) or not names:
        raise FeatureDataContractError("feature_names must be a non-empty deterministic list")
    if len(names) != len(set(names)) or any(not isinstance(name, str) or not _NAME.fullmatch(name) for name in names):
        raise FeatureDataContractError("feature_names must be unique lowercase identifiers")
    assertions = contract.get("availability_assertions")
    if not isinstance(assertions, list) or [item.get("feature_name") for item in assertions if isinstance(item, Mapping)] != names:
        raise FeatureDataContractError("availability_assertions must match feature_names in order")
    for index, assertion in enumerate(assertions):
        assertion = _mapping(assertion, f"availability_assertions.{index}")
        _closed(assertion, {"feature_name", "source_class", "condition_assertions"}, f"availability_assertions.{index}")
        if assertion["source_class"] != source_class:
            raise FeatureDataContractError("availability assertion source class mismatch")
        conditions = assertion["condition_assertions"]
        if not isinstance(conditions, list) or not conditions or len(conditions) != len(set(conditions)):
            raise FeatureDataContractError("condition_assertions must be non-empty and unique")

    source_identity = contract.get("source_set_identity")
    if not isinstance(source_identity, str) or not _SHA256.fullmatch(source_identity):
        raise FeatureDataContractError("source_set_identity must be sha256:<64 lowercase hex>")
    if source_files is not None and build_source_set_identity(
        source_files, identity_context=source_identity_context
    ) != source_identity:
        raise FeatureDataContractError("source_set_identity does not match stable source facts")

    output = _mapping(contract.get("output_identity"), "output_identity")
    _closed(output, _OUTPUT_FIELDS, "output_identity")
    if not _HEX_SHA256.fullmatch(str(output.get("sha256", ""))):
        raise FeatureDataContractError("output_identity.sha256 must be 64 lowercase hex")
    if not isinstance(output.get("row_count"), int) or output["row_count"] <= 0:
        raise FeatureDataContractError("output_identity.row_count must be positive")
    columns = output.get("columns")
    if not isinstance(columns, list) or not columns or len(columns) != len(set(columns)):
        raise FeatureDataContractError("output_identity.columns must be non-empty and unique")
    if any(name not in columns for name in names):
        raise FeatureDataContractError("research feature is absent from output columns")

    coverage = _mapping(contract.get("coverage"), "coverage")
    _closed(coverage, _COVERAGE_FIELDS, "coverage")
    expected = coverage.get("expected_row_count")
    observed = coverage.get("observed_row_count")
    if not isinstance(expected, int) or expected <= 0 or not isinstance(observed, int) or observed <= 0:
        raise FeatureDataContractError("coverage row counts must be positive integers")
    if output["row_count"] != observed:
        raise FeatureDataContractError("output and coverage row counts disagree")
    complete = coverage.get("complete")
    if not isinstance(complete, bool):
        raise FeatureDataContractError("coverage.complete must be boolean")
    if complete and expected != observed:
        raise FeatureDataContractError("complete feature tables require exact expected/observed equality")
    _non_empty(coverage.get("start_utc_inclusive"), "coverage.start_utc_inclusive")
    _non_empty(coverage.get("end_utc_exclusive"), "coverage.end_utc_exclusive")
    if source_class == D4_TAKER_SOURCE_CLASS:
        assert isinstance(parent_identity, Mapping)
        if (
            parent_identity["row_count"] != expected
            or parent_identity["coverage_start_utc_inclusive"]
            != coverage["start_utc_inclusive"]
            or parent_identity["coverage_end_utc_exclusive"]
            != coverage["end_utc_exclusive"]
        ):
            raise FeatureDataContractError(
                "canonical D4 parent row count/coverage must equal feature coverage"
            )

    causality = _mapping(contract.get("causality"), "causality")
    _closed(causality, set(_CAUSALITY), "causality")
    if dict(causality) != _CAUSALITY:
        raise FeatureDataContractError("causality must preserve completed-bar-only semantics")
    quality = _mapping(contract.get("quality_policy"), "quality_policy")
    _closed(quality, set(_QUALITY_POLICY), "quality_policy")
    if dict(quality) != _QUALITY_POLICY:
        raise FeatureDataContractError("quality policy must forbid repair and fail closed")
    non_authority = _mapping(contract.get("non_authority"), "non_authority")
    _closed(non_authority, set(_NON_AUTHORITY), "non_authority")
    if dict(non_authority) != _NON_AUTHORITY:
        raise FeatureDataContractError("feature table must not expand authority")

    identity = contract.get("feature_table_identity")
    if not isinstance(identity, str) or not _SHA256.fullmatch(identity):
        raise FeatureDataContractError("feature_table_identity must be sha256:<64 lowercase hex>")
    if build_feature_table_identity(contract) != identity:
        raise FeatureDataContractError("feature_table_identity does not match contract content")


def canonical_feature_table_bytes(contract: Mapping[str, Any]) -> bytes:
    """Expose the canonical serialization used for deterministic comparisons."""

    validate_feature_table_contract(contract)
    return canonical_json_bytes(dict(contract))
