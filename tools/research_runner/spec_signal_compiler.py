"""Build-and-test-only Strategy Spec to signal compiler."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDICATOR_CATALOG_PATH = (
    REPO_ROOT / "research" / "indicator_catalogs" / "IND-CATALOG-0001.indicator_catalog.json"
)
ALLOWED_DATA_FIELDS = {"open", "high", "low", "close", "volume"}
APPROVED_BUILTINS = {
    "sma": "sma_v1",
    "ema": "ema_v1",
    "atr": "atr_v1",
    "stddev": "stddev_v1",
}
SUPPORTED_OPERATORS = {"gt", "gte", "lt", "lte", "eq", "neq"}
UNSUPPORTED_OPERATORS = {
    "crosses_above",
    "crosses_below",
    "in_set",
    "is_true",
    "is_false",
}
ENTRY_GROUP_ROLES = {
    "required",
    "confirming",
    "filter",
    "regime",
    "session",
    "funding",
    "volatility",
    "other",
}
BLOCKING_GROUP_ROLES = {"blocking", "no_trade", "cooldown"}
EXIT_GROUP_ROLES = {"exit", "invalidation", "risk_exit", "time_stop"}
FORBIDDEN_PAYLOAD_KEYS = {
    "expression",
    "formula",
    "code",
    "script",
    "eval",
    "function",
    "callback",
    "lambda",
    "sql",
    "shell",
    "python",
    "javascript",
    "url",
    "file_path",
    "command",
    "runtime_action",
    "order_instruction",
    "broker_instruction",
    "exchange_instruction",
    "live_action",
    "paper_action",
    "readiness_update",
    "transition_trigger",
    "approval_action",
    "ranking_score",
    "recommendation",
    "broker",
    "oms",
    "reconciliation",
    "risk_cap",
    "safe_mode",
    "kill_switch",
    "credentials",
    "private_key",
    "tier_4",
}


class SpecSignalCompilerError(RuntimeError):
    """Raised when a Strategy Spec cannot be compiled safely."""


class UnsupportedSpecSignalCompilerFeature(SpecSignalCompilerError):
    """Raised for closed grammar features that this first slice does not implement."""


def compile_signal(
    strategy_spec: dict[str, Any],
    variant_assignment: dict[str, Any],
    ohlcv: pd.DataFrame,
    funding: pd.DataFrame | None = None,
    indicator_catalog: dict[str, Any] | None = None,
) -> pd.Series:
    """Compile a declarative Strategy Spec-like payload into a deterministic signal series."""
    del funding
    _guard_forbidden_payload_keys(strategy_spec, "strategy_spec")
    _guard_forbidden_payload_keys(variant_assignment, "variant_assignment")
    catalog = _load_default_catalog() if indicator_catalog is None else _copy_mapping(indicator_catalog)
    _guard_forbidden_payload_keys(catalog, "indicator_catalog")
    _validate_catalog(catalog)
    _validate_ohlcv(ohlcv)

    direction = strategy_spec.get("entry_logic", {}).get("direction")
    if direction not in {"long", "short", "both"}:
        raise SpecSignalCompilerError(f"unsupported or missing entry direction: {direction!r}")
    if direction == "both":
        raise UnsupportedSpecSignalCompilerFeature("entry direction 'both' is not supported in WP-S2c-199")
    position_value = 1.0 if direction == "long" else -1.0

    context = _CompileContext(
        strategy_spec=strategy_spec,
        variant_assignment=variant_assignment,
        ohlcv=ohlcv,
        catalog=catalog,
    )
    entry_groups = _collect_groups(strategy_spec.get("entry_logic"))
    filter_groups = _collect_groups(strategy_spec.get("filters"))
    all_entry_groups = [*entry_groups, *filter_groups]
    exit_groups = _collect_groups(strategy_spec.get("exit_logic"))
    max_holding_bars = _max_holding_bars(strategy_spec)

    signal = pd.Series(0.0, index=ohlcv.index, name="signal")
    current_position = 0.0
    held_bars = 0
    for timestamp in ohlcv.index:
        should_exit = False
        if current_position:
            should_exit = _any_group_true(exit_groups, EXIT_GROUP_ROLES, context, timestamp)
            if max_holding_bars is not None and held_bars >= max_holding_bars:
                should_exit = True
            if should_exit:
                current_position = 0.0
                held_bars = 0

        if not current_position:
            entry_allowed = _entry_allowed(all_entry_groups, context, timestamp)
            if entry_allowed:
                current_position = position_value
                held_bars = 0

        signal.loc[timestamp] = current_position
        if current_position:
            held_bars += 1
    return signal


class _CompileContext:
    def __init__(
        self,
        *,
        strategy_spec: Mapping[str, Any],
        variant_assignment: Mapping[str, Any],
        ohlcv: pd.DataFrame,
        catalog: Mapping[str, Any],
    ) -> None:
        self.strategy_spec = strategy_spec
        self.variant_assignment = variant_assignment
        self.ohlcv = ohlcv
        self.catalog_entries = _catalog_entries_by_id(catalog)
        self.indicator_cache: dict[tuple[str, int, str], pd.Series] = {}


def _copy_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def _load_default_catalog() -> dict[str, Any]:
    return json.loads(DEFAULT_INDICATOR_CATALOG_PATH.read_text(encoding="utf-8"))


def _guard_forbidden_payload_keys(value: Any, label: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_PAYLOAD_KEYS:
                raise SpecSignalCompilerError(f"forbidden executable/protected key at {label}.{key}")
            _guard_forbidden_payload_keys(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _guard_forbidden_payload_keys(child, f"{label}.{index}")


def _validate_catalog(catalog: Mapping[str, Any]) -> None:
    entries = _catalog_entries_by_id(catalog)
    if set(entries) != set(APPROVED_BUILTINS):
        raise SpecSignalCompilerError(f"indicator catalog must contain {sorted(APPROVED_BUILTINS)}")
    for indicator_id, expected_builtin in APPROVED_BUILTINS.items():
        entry = entries[indicator_id]
        binding = entry.get("implementation_binding")
        if not isinstance(binding, Mapping):
            raise SpecSignalCompilerError(f"{indicator_id} implementation_binding must be an object")
        if binding.get("builtin_key") != expected_builtin:
            raise SpecSignalCompilerError(
                f"{indicator_id} builtin mismatch: expected {expected_builtin}, got {binding.get('builtin_key')!r}"
            )
        if binding.get("binding_type") != "compiler_builtin_closed_set":
            raise SpecSignalCompilerError(f"{indicator_id} binding_type must be compiler_builtin_closed_set")
        if binding.get("implementation_owner") != "spec_signal_compiler":
            raise SpecSignalCompilerError(f"{indicator_id} implementation_owner must be spec_signal_compiler")
        if binding.get("computation_defined_in_catalog") is not False:
            raise SpecSignalCompilerError(f"{indicator_id} computation_defined_in_catalog must be false")
        if binding.get("arbitrary_expression_allowed") is not False:
            raise SpecSignalCompilerError(f"{indicator_id} arbitrary_expression_allowed must be false")


def _catalog_entries_by_id(catalog: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    entries = catalog.get("entries")
    if not isinstance(entries, list):
        raise SpecSignalCompilerError("indicator catalog entries must be an array")
    by_id: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("indicator_id"), str):
            raise SpecSignalCompilerError("indicator catalog entry is missing indicator_id")
        indicator_id = entry["indicator_id"]
        if indicator_id in by_id:
            raise SpecSignalCompilerError(f"duplicate indicator catalog entry: {indicator_id}")
        by_id[indicator_id] = entry
    return by_id


def _validate_ohlcv(ohlcv: pd.DataFrame) -> None:
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        raise SpecSignalCompilerError("ohlcv index must be a pandas DatetimeIndex")
    missing = ALLOWED_DATA_FIELDS - set(ohlcv.columns)
    if missing:
        raise SpecSignalCompilerError(f"ohlcv missing required fields: {sorted(missing)}")


def _collect_groups(container: Any) -> list[Mapping[str, Any]]:
    if not isinstance(container, Mapping):
        return []
    groups = container.get("groups", [])
    if groups is None:
        return []
    if not isinstance(groups, list):
        raise SpecSignalCompilerError("condition groups must be an array")
    return [_require_mapping(group, "condition group") for group in groups]


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SpecSignalCompilerError(f"{label} must be an object")
    return value


def _max_holding_bars(strategy_spec: Mapping[str, Any]) -> int | None:
    max_holding = strategy_spec.get("exit_logic", {}).get("max_holding_period")
    if not isinstance(max_holding, Mapping) or max_holding.get("enabled") is not True:
        return None
    bars = max_holding.get("bars")
    if not isinstance(bars, int) or bars < 1:
        raise SpecSignalCompilerError("enabled max_holding_period requires integer bars >= 1")
    return bars


def _entry_allowed(groups: list[Mapping[str, Any]], context: _CompileContext, timestamp: Any) -> bool:
    entry_groups = [group for group in groups if group.get("group_role") in ENTRY_GROUP_ROLES]
    blocking_groups = [group for group in groups if group.get("group_role") in BLOCKING_GROUP_ROLES]
    for group in groups:
        role = group.get("group_role")
        if role not in ENTRY_GROUP_ROLES | BLOCKING_GROUP_ROLES:
            raise UnsupportedSpecSignalCompilerFeature(f"unsupported entry/filter group role: {role!r}")
    if not entry_groups:
        return False
    if any(_evaluate_group(group, context, timestamp) for group in blocking_groups):
        return False
    return all(_evaluate_group(group, context, timestamp) for group in entry_groups)


def _any_group_true(
    groups: list[Mapping[str, Any]],
    allowed_roles: set[str],
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    relevant = []
    for group in groups:
        role = group.get("group_role")
        if role in allowed_roles:
            relevant.append(group)
        else:
            raise UnsupportedSpecSignalCompilerFeature(f"unsupported exit group role: {role!r}")
    return any(_evaluate_group(group, context, timestamp) for group in relevant)


def _evaluate_group(group: Mapping[str, Any], context: _CompileContext, timestamp: Any) -> bool:
    logic = group.get("logic")
    if logic not in {"all", "any"}:
        raise SpecSignalCompilerError(f"unsupported condition group logic: {logic!r}")
    conditions = group.get("conditions", [])
    subgroups = group.get("subgroups", [])
    if not isinstance(conditions, list) or not isinstance(subgroups, list):
        raise SpecSignalCompilerError("condition group conditions/subgroups must be arrays")
    values = [
        _evaluate_condition(_require_mapping(condition, "condition"), context, timestamp)
        for condition in conditions
    ]
    values.extend(
        _evaluate_group(_require_mapping(subgroup, "condition subgroup"), context, timestamp)
        for subgroup in subgroups
    )
    if not values:
        return False
    return all(values) if logic == "all" else any(values)


def _evaluate_condition(condition: Mapping[str, Any], context: _CompileContext, timestamp: Any) -> bool:
    role = condition.get("condition_role")
    if role not in {"required", "confirming", "blocking", "exit", "invalidation", "filter"}:
        raise UnsupportedSpecSignalCompilerFeature(f"unsupported condition role: {role!r}")
    operator = condition.get("operator")
    if operator in UNSUPPORTED_OPERATORS:
        raise UnsupportedSpecSignalCompilerFeature(f"operator {operator!r} is not supported in WP-S2c-199")
    if operator not in SUPPORTED_OPERATORS:
        raise SpecSignalCompilerError(f"unknown operator: {operator!r}")
    left = _resolve_operand(_require_mapping(condition.get("left_operand"), "left_operand"), context)
    right = _resolve_operand(_require_mapping(condition.get("right_operand"), "right_operand"), context)
    left_value = _value_at(left, timestamp)
    right_value = _value_at(right, timestamp)
    if _is_null(left_value) or _is_null(right_value):
        return False
    if operator == "gt":
        return bool(left_value > right_value)
    if operator == "gte":
        return bool(left_value >= right_value)
    if operator == "lt":
        return bool(left_value < right_value)
    if operator == "lte":
        return bool(left_value <= right_value)
    if operator == "eq":
        return bool(left_value == right_value)
    if operator == "neq":
        return bool(left_value != right_value)
    raise SpecSignalCompilerError(f"unhandled operator: {operator!r}")


def _resolve_operand(operand: Mapping[str, Any], context: _CompileContext) -> Any:
    operand_type = operand.get("operand_type")
    if operand_type == "data_ref":
        return _resolve_data_ref(operand, context.ohlcv)
    if operand_type == "indicator_ref":
        return _resolve_indicator_ref(operand, context)
    if operand_type == "parameter_ref":
        return _resolve_parameter_ref(operand, context.variant_assignment)
    if operand_type == "constant":
        return operand.get("ref")
    raise SpecSignalCompilerError(f"unknown operand_type: {operand_type!r}")


def _resolve_data_ref(operand: Mapping[str, Any], ohlcv: pd.DataFrame) -> pd.Series:
    field = operand.get("field") or operand.get("ref")
    if field not in ALLOWED_DATA_FIELDS:
        raise SpecSignalCompilerError(f"unsupported data_ref field: {field!r}")
    timeframe = operand.get("timeframe")
    if timeframe not in (None, ""):
        raise UnsupportedSpecSignalCompilerFeature("data_ref timeframe resampling is not supported")
    return ohlcv[str(field)]


def _resolve_indicator_ref(operand: Mapping[str, Any], context: _CompileContext) -> pd.Series:
    indicator_id = operand.get("ref")
    if indicator_id not in APPROVED_BUILTINS:
        raise SpecSignalCompilerError(f"unknown indicator_ref: {indicator_id!r}")
    output_field = operand.get("field")
    if output_field not in (None, "", "value"):
        raise SpecSignalCompilerError(f"unsupported indicator output field: {output_field!r}")
    timeframe = operand.get("timeframe")
    if timeframe not in (None, ""):
        raise UnsupportedSpecSignalCompilerFeature("indicator_ref timeframe resampling is not supported")
    lookback = operand.get("lookback")
    if not isinstance(lookback, Mapping) or not isinstance(lookback.get("bars"), int):
        raise UnsupportedSpecSignalCompilerFeature(
            "indicator lookback must be literal operand.lookback.bars in WP-S2c-199"
        )
    lookback_bars = lookback["bars"]
    if lookback_bars < 1:
        raise SpecSignalCompilerError("indicator lookback.bars must be >= 1")

    builtin_key = context.catalog_entries[str(indicator_id)]["implementation_binding"]["builtin_key"]
    cache_key = (str(indicator_id), lookback_bars, builtin_key)
    if cache_key in context.indicator_cache:
        return context.indicator_cache[cache_key]
    if builtin_key == "sma_v1":
        result = _sma_v1(context.ohlcv["close"], lookback_bars)
    elif builtin_key == "ema_v1":
        result = _ema_v1(context.ohlcv["close"], lookback_bars)
    elif builtin_key == "atr_v1":
        result = _atr_v1(context.ohlcv, lookback_bars)
    elif builtin_key == "stddev_v1":
        result = _stddev_v1(context.ohlcv["close"], lookback_bars, ddof=0)
    else:
        raise SpecSignalCompilerError(f"unknown builtin key: {builtin_key!r}")
    context.indicator_cache[cache_key] = result
    return result


def _resolve_parameter_ref(operand: Mapping[str, Any], variant_assignment: Mapping[str, Any]) -> Any:
    ref = operand.get("ref")
    if not isinstance(ref, str) or not ref:
        raise SpecSignalCompilerError("parameter_ref ref must be a non-empty string")
    parameter_values = variant_assignment.get("parameter_values")
    if not isinstance(parameter_values, Mapping):
        raise SpecSignalCompilerError("variant_assignment.parameter_values must be an object")
    if ref not in parameter_values:
        raise SpecSignalCompilerError(f"missing required parameter_ref: {ref}")
    return parameter_values[ref]


def _value_at(value: Any, timestamp: Any) -> Any:
    if isinstance(value, pd.Series):
        return value.loc[timestamp]
    return value


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def _sma_v1(series: pd.Series, lookback_bars: int) -> pd.Series:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("sma_v1 lookback_bars must be >= 1")
    return series.astype(float).rolling(lookback_bars, min_periods=lookback_bars).mean()


def _ema_v1(series: pd.Series, lookback_bars: int) -> pd.Series:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("ema_v1 lookback_bars must be >= 1")
    source = series.astype(float)
    result = pd.Series(math.nan, index=series.index, dtype=float)
    if len(source) < lookback_bars:
        return result
    alpha = 2.0 / (lookback_bars + 1.0)
    previous = source.iloc[:lookback_bars].mean()
    if math.isnan(previous):
        return result
    result.iloc[lookback_bars - 1] = previous
    for index in range(lookback_bars, len(source)):
        current = source.iloc[index]
        if pd.isna(current) or pd.isna(previous):
            previous = math.nan
            result.iloc[index] = math.nan
            continue
        previous = (alpha * float(current)) + ((1.0 - alpha) * float(previous))
        result.iloc[index] = previous
    return result


def _atr_v1(ohlcv: pd.DataFrame, lookback_bars: int) -> pd.Series:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("atr_v1 lookback_bars must be >= 1")
    high = ohlcv["high"].astype(float)
    low = ohlcv["low"].astype(float)
    close = ohlcv["close"].astype(float)
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1, skipna=True)
    if len(true_range):
        true_range.iloc[0] = high.iloc[0] - low.iloc[0]

    result = pd.Series(math.nan, index=ohlcv.index, dtype=float)
    if len(true_range) < lookback_bars:
        return result
    previous = true_range.iloc[:lookback_bars].mean()
    if math.isnan(previous):
        return result
    result.iloc[lookback_bars - 1] = previous
    for index in range(lookback_bars, len(true_range)):
        current = true_range.iloc[index]
        if pd.isna(current) or pd.isna(previous):
            previous = math.nan
            result.iloc[index] = math.nan
            continue
        previous = ((float(previous) * (lookback_bars - 1)) + float(current)) / lookback_bars
        result.iloc[index] = previous
    return result


def _stddev_v1(series: pd.Series, lookback_bars: int, *, ddof: int = 0) -> pd.Series:
    if lookback_bars < 2:
        raise SpecSignalCompilerError("stddev_v1 lookback_bars must be >= 2")
    if ddof not in {0, 1}:
        raise SpecSignalCompilerError("stddev_v1 ddof must be 0 or 1")
    return series.astype(float).rolling(lookback_bars, min_periods=lookback_bars).std(ddof=ddof)
