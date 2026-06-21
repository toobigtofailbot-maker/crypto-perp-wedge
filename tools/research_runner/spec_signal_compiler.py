"""Build-and-test-only Strategy Spec to signal compiler."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Mapping

import numpy as np
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
    "rsi": "rsi_v1",
    "donchian": "donchian_v1",
    "ma_distance": "ma_distance_v1",
    "rvol": "rvol_v1",
    "rolling_vwap": "rolling_vwap_v1",
}
COMPOSED_OPERAND_TYPE = "composed_operand"
COMPOSITION_TYPE_SCALE_BY_ONE_MINUS_PARAMETER = "scale_by_one_minus_parameter"
COMPOSITION_TYPE_SCALE_BY_ONE_PLUS_PARAMETER = "scale_by_one_plus_parameter"
COMPOSITION_TYPE_Z_SCORE = "z_score"
COMPOSITION_TYPES = {
    COMPOSITION_TYPE_SCALE_BY_ONE_MINUS_PARAMETER,
    COMPOSITION_TYPE_SCALE_BY_ONE_PLUS_PARAMETER,
    COMPOSITION_TYPE_Z_SCORE,
}
COMPOSED_BASE_OPERAND_TYPES = {"data_ref", "indicator_ref"}
COMPOSED_PARAMETER_OPERAND_TYPE = "parameter_ref"
Z_SCORE_OPERAND_TYPES = {"data_ref", "indicator_ref"}
Z_SCORE_ZERO_SCALE_POLICY = "null_output"
LOOKBACK_PARAMETER_REF_KEY = "bars_parameter_ref"
VALUE_PARAMETER_REF_KEY = "parameter_ref"
CROSSOVER_OPERATORS = {"crosses_above", "crosses_below"}
BOOLEAN_OPERATORS = {"is_true", "is_false"}
SUPPORTED_OPERATORS = {"gt", "gte", "lt", "lte", "eq", "neq"} | CROSSOVER_OPERATORS | BOOLEAN_OPERATORS
UNSUPPORTED_OPERATORS = {
    "in_set",
}
ENTRY_GROUP_ROLES = {
    "required",
    "confirming",
    "filter",
    "trend",
    "regime",
    "session",
    "funding",
    "volatility",
    "other",
}
BLOCKING_GROUP_ROLES = {"blocking", "no_trade", "cooldown"}
EXIT_GROUP_ROLES = {"exit", "invalidation", "risk_exit", "time_stop"}
ENTRY_CONDITION_ROLES = {"required", "confirming", "filter"}
BLOCKING_CONDITION_ROLES = {"blocking"}
EXIT_CONDITION_ROLES = {"exit", "invalidation"}
SIDE_LABELS = {"long", "short"}
ATR_STOP_ENTRY_REFERENCE_PRICE = "next_bar_open_pre_fee_slippage"
ATR_STOP_EVALUATION_PRICE = "close"
ATR_STOP_EVALUATION_TIMING = "bar_close"
ATR_STOP_ALLOWED_KEYS = {
    "enabled",
    "atr_lookback",
    "atr_multiplier",
    "entry_reference_price",
    "evaluation_price",
    "evaluation_timing",
}
ATR_STOP_MAX_LOOKBACK_BARS = 100000
ATR_STOP_MAX_MULTIPLIER = 1000.0
PRIMITIVE_REF_OPERAND_TYPE = "primitive_ref"
ONLINE_OHLCV_PRIMITIVES_KEY = "online_ohlcv_primitives"
SESSION_WINDOWS_KEY = "session_windows"
OPENING_RANGES_KEY = "opening_ranges"
OPENING_RANGE_BREAKOUTS_KEY = "opening_range_breakouts"
OPENING_RANGE_RETESTS_KEY = "opening_range_retests"
CANDLE_SHAPES_KEY = "candle_shapes"
TIME_EXIT_ALLOWED_KEYS = {"session_end"}
SESSION_END_ALLOWED_KEYS = {
    "enabled",
    "session_ref",
    "exit_signal_timing",
    "fill_timing",
    "partial_session_policy",
}
SESSION_END_EXIT_SIGNAL_TIMING = "last_bar_close_before_session_end"
SESSION_END_FILL_TIMING = "next_bar_open"
SESSION_END_PARTIAL_SESSION_POLICY = "no_exit"
OR_OPPOSITE_SIDE_ALLOWED_KEYS = {
    "enabled",
    "range_ref",
    "entry_reference_price",
    "evaluation_price",
    "evaluation_timing",
    "long_stop_level",
    "short_stop_level",
    "same_bar_entry_stop_policy",
}
OR_OPPOSITE_SIDE_ENTRY_REFERENCE_PRICE = "next_bar_open_pre_fee_slippage"
OR_OPPOSITE_SIDE_EVALUATION_PRICE = "close"
OR_OPPOSITE_SIDE_EVALUATION_TIMING = "bar_close"
OR_OPPOSITE_SIDE_LONG_STOP_LEVEL = "opening_range.low"
OR_OPPOSITE_SIDE_SHORT_STOP_LEVEL = "opening_range.high"
OR_OPPOSITE_SIDE_SAME_BAR_POLICY = "not_evaluated_until_after_entry_bar"
FIXED_R_TARGET_ALLOWED_KEYS = {
    "enabled",
    "r_multiple",
    "entry_reference_price",
    "stop_ref",
    "evaluation_price",
    "evaluation_timing",
    "same_bar_stop_target_policy",
}
FIXED_R_TARGET_ENTRY_REFERENCE_PRICE = "next_bar_open_pre_fee_slippage"
FIXED_R_TARGET_STOP_REF = "opening_range_opposite_side"
FIXED_R_TARGET_EVALUATION_PRICE = "close"
FIXED_R_TARGET_EVALUATION_TIMING = "bar_close"
FIXED_R_TARGET_SAME_BAR_POLICY = "defer_intrabar_realism"
FIXED_R_TARGET_MAX_MULTIPLE = 1000.0
FORBIDDEN_PAYLOAD_KEYS = {
    "expression",
    "formula",
    "code",
    "script",
    "eval",
    "exec",
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
    "lookahead",
    "forward_fill",
    "backfill",
    "interpolation",
    "future_value",
}


class SpecSignalCompilerError(RuntimeError):
    """Raised when a Strategy Spec cannot be compiled safely."""


class UnsupportedSpecSignalCompilerFeature(SpecSignalCompilerError):
    """Raised for closed grammar features that this first slice does not implement."""


@dataclass(frozen=True)
class _AtrStopConfig:
    atr_lookback: int
    atr_multiplier: float
    atr_series: pd.Series


@dataclass(frozen=True)
class _PendingAtrStopEntry:
    side: str
    signal_bar_index: int
    atr_at_entry: float


@dataclass(frozen=True)
class _AtrStopState:
    side: str
    entry_reference_price: float
    atr_at_entry: float


@dataclass(frozen=True)
class _SessionEndExitConfig:
    session_ref: str


@dataclass(frozen=True)
class _OpeningRangeOppositeSideConfig:
    range_ref: str


@dataclass(frozen=True)
class _FixedRTargetConfig:
    r_multiple: float


@dataclass(frozen=True)
class _PendingCloseOnlyExitEntry:
    side: str
    signal_bar_index: int


@dataclass(frozen=True)
class _CloseOnlyExitState:
    side: str
    entry_reference_price: float
    long_stop_level: float
    short_stop_level: float


@dataclass(frozen=True)
class _EntryControls:
    min_bars_between_entries: int | None
    max_trades_per_session: int | None
    session_ref: str | None


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

    context = _CompileContext(
        strategy_spec=strategy_spec,
        variant_assignment=variant_assignment,
        ohlcv=ohlcv,
        catalog=catalog,
    )
    entry_groups = _collect_groups(strategy_spec.get("entry_logic"))
    filter_groups = _collect_groups(strategy_spec.get("filters"))
    exit_groups = _collect_groups(strategy_spec.get("exit_logic"))
    max_holding_bars = _max_holding_bars(strategy_spec)
    entry_controls = _entry_controls(strategy_spec, context)
    atr_stop_config = _atr_stop_config(strategy_spec, context)
    session_end_exit_config = _session_end_exit_config(strategy_spec)
    or_opposite_side_config = _opening_range_opposite_side_config(strategy_spec)
    fixed_r_target_config = _fixed_r_target_config(strategy_spec, or_opposite_side_config, context)

    if direction == "both":
        return _compile_both_direction_signal(
            ohlcv=ohlcv,
            context=context,
            entry_groups=entry_groups,
            filter_groups=filter_groups,
            exit_groups=exit_groups,
            max_holding_bars=max_holding_bars,
            entry_controls=entry_controls,
            atr_stop_config=atr_stop_config,
            session_end_exit_config=session_end_exit_config,
            or_opposite_side_config=or_opposite_side_config,
            fixed_r_target_config=fixed_r_target_config,
        )

    position_value = 1.0 if direction == "long" else -1.0
    all_entry_groups = [*entry_groups, *filter_groups]

    signal = pd.Series(0.0, index=ohlcv.index, name="signal")
    current_position = 0.0
    held_bars = 0
    last_entry_bar: int | None = None
    session_trade_counts: dict[Any, int] = {}
    atr_stop_state: _AtrStopState | None = None
    pending_atr_stop_entry: _PendingAtrStopEntry | None = None
    close_only_exit_state: _CloseOnlyExitState | None = None
    pending_close_only_exit_entry: _PendingCloseOnlyExitEntry | None = None
    side = "long" if direction == "long" else "short"
    for bar_index, timestamp in enumerate(ohlcv.index):
        block_same_bar_reentry = False
        if current_position and pending_atr_stop_entry is not None:
            atr_stop_state = _capture_atr_stop_state(
                pending_entry=pending_atr_stop_entry,
                ohlcv=ohlcv,
                fill_bar_index=bar_index,
            )
            pending_atr_stop_entry = None
        if current_position and pending_close_only_exit_entry is not None:
            close_only_exit_state = _capture_close_only_exit_state(
                pending_entry=pending_close_only_exit_entry,
                config=or_opposite_side_config,
                context=context,
                fill_bar_index=bar_index,
            )
            pending_close_only_exit_entry = None

        should_exit = False
        if current_position:
            should_exit = _any_group_true(exit_groups, EXIT_GROUP_ROLES, context, timestamp)
            if _atr_stop_triggered(atr_stop_config, atr_stop_state, context, timestamp):
                should_exit = True
            if _opening_range_opposite_side_triggered(
                or_opposite_side_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _fixed_r_target_triggered(
                fixed_r_target_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _session_end_exit_triggered(
                session_end_exit_config,
                context,
                timestamp,
            ):
                should_exit = True
            if max_holding_bars is not None and held_bars >= max_holding_bars:
                should_exit = True
            if should_exit:
                current_position = 0.0
                held_bars = 0
                atr_stop_state = None
                pending_atr_stop_entry = None
                close_only_exit_state = None
                pending_close_only_exit_entry = None
                block_same_bar_reentry = any(
                    config is not None
                    for config in (
                        atr_stop_config,
                        session_end_exit_config,
                        or_opposite_side_config,
                        fixed_r_target_config,
                    )
                )

        if not current_position and not block_same_bar_reentry:
            entry_allowed = _entry_allowed(all_entry_groups, context, timestamp)
            if entry_allowed and not _entry_control_allows_entry(
                bar_index=bar_index,
                last_entry_bar=last_entry_bar,
                entry_controls=entry_controls,
                context=context,
                timestamp=timestamp,
                session_trade_counts=session_trade_counts,
            ):
                entry_allowed = False
            if entry_allowed:
                current_position = position_value
                last_entry_bar = bar_index
                _record_session_entry(
                    entry_controls=entry_controls,
                    context=context,
                    timestamp=timestamp,
                    session_trade_counts=session_trade_counts,
                )
                held_bars = 0
                pending_atr_stop_entry = _new_pending_atr_stop_entry(
                    atr_stop_config,
                    side,
                    bar_index,
                    timestamp,
                )
                pending_close_only_exit_entry = _new_pending_close_only_exit_entry(
                    or_opposite_side_config,
                    fixed_r_target_config,
                    side,
                    bar_index,
                )

        signal.loc[timestamp] = current_position
        if current_position:
            held_bars += 1
    return signal


def _compile_both_direction_signal(
    *,
    ohlcv: pd.DataFrame,
    context: _CompileContext,
    entry_groups: list[Mapping[str, Any]],
    filter_groups: list[Mapping[str, Any]],
    exit_groups: list[Mapping[str, Any]],
    max_holding_bars: int | None,
    entry_controls: _EntryControls,
    atr_stop_config: _AtrStopConfig | None,
    session_end_exit_config: _SessionEndExitConfig | None,
    or_opposite_side_config: _OpeningRangeOppositeSideConfig | None,
    fixed_r_target_config: _FixedRTargetConfig | None,
) -> pd.Series:
    _guard_no_side_labels(filter_groups, "filters.groups")
    entry_groups_by_side = _split_root_side_groups(
        entry_groups,
        "entry_logic.groups",
        require_both_sides=True,
    )
    exit_groups_by_side = _split_root_side_groups(
        exit_groups,
        "exit_logic.groups",
        require_both_sides=False,
    )

    signal_values = np.zeros(len(ohlcv.index), dtype=float)
    current_side: str | None = None
    held_bars = 0
    last_entry_bar: int | None = None
    session_trade_counts: dict[Any, int] = {}
    atr_stop_state: _AtrStopState | None = None
    pending_atr_stop_entry: _PendingAtrStopEntry | None = None
    close_only_exit_state: _CloseOnlyExitState | None = None
    pending_close_only_exit_entry: _PendingCloseOnlyExitEntry | None = None
    long_entry_values = _entry_allowed_series(
        [*entry_groups_by_side["long"], *filter_groups],
        context,
    ).to_numpy(dtype=bool)
    short_entry_values = _entry_allowed_series(
        [*entry_groups_by_side["short"], *filter_groups],
        context,
    ).to_numpy(dtype=bool)
    for bar_index, timestamp in enumerate(ohlcv.index):
        if current_side is not None and pending_atr_stop_entry is not None:
            atr_stop_state = _capture_atr_stop_state(
                pending_entry=pending_atr_stop_entry,
                ohlcv=ohlcv,
                fill_bar_index=bar_index,
            )
            pending_atr_stop_entry = None
        if current_side is not None and pending_close_only_exit_entry is not None:
            close_only_exit_state = _capture_close_only_exit_state(
                pending_entry=pending_close_only_exit_entry,
                config=or_opposite_side_config,
                context=context,
                fill_bar_index=bar_index,
            )
            pending_close_only_exit_entry = None

        if current_side == "long":
            should_exit = _any_group_true(
                exit_groups_by_side["long"],
                EXIT_GROUP_ROLES,
                context,
                timestamp,
            )
            if _atr_stop_triggered(atr_stop_config, atr_stop_state, context, timestamp):
                should_exit = True
            if _opening_range_opposite_side_triggered(
                or_opposite_side_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _fixed_r_target_triggered(
                fixed_r_target_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _session_end_exit_triggered(
                session_end_exit_config,
                context,
                timestamp,
            ):
                should_exit = True
            if max_holding_bars is not None and held_bars >= max_holding_bars:
                should_exit = True
            if should_exit:
                current_side = None
                held_bars = 0
                atr_stop_state = None
                pending_atr_stop_entry = None
                close_only_exit_state = None
                pending_close_only_exit_entry = None
                continue
        elif current_side == "short":
            should_exit = _any_group_true(
                exit_groups_by_side["short"],
                EXIT_GROUP_ROLES,
                context,
                timestamp,
            )
            if _atr_stop_triggered(atr_stop_config, atr_stop_state, context, timestamp):
                should_exit = True
            if _opening_range_opposite_side_triggered(
                or_opposite_side_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _fixed_r_target_triggered(
                fixed_r_target_config,
                close_only_exit_state,
                context,
                timestamp,
            ):
                should_exit = True
            if _session_end_exit_triggered(
                session_end_exit_config,
                context,
                timestamp,
            ):
                should_exit = True
            if max_holding_bars is not None and held_bars >= max_holding_bars:
                should_exit = True
            if should_exit:
                current_side = None
                held_bars = 0
                atr_stop_state = None
                pending_atr_stop_entry = None
                close_only_exit_state = None
                pending_close_only_exit_entry = None
                continue
        else:
            long_entry = bool(long_entry_values[bar_index])
            short_entry = bool(short_entry_values[bar_index])
            if long_entry and not short_entry:
                if _entry_control_allows_entry(
                    bar_index=bar_index,
                    last_entry_bar=last_entry_bar,
                    entry_controls=entry_controls,
                    context=context,
                    timestamp=timestamp,
                    session_trade_counts=session_trade_counts,
                ):
                    current_side = "long"
                    last_entry_bar = bar_index
                    _record_session_entry(
                        entry_controls=entry_controls,
                        context=context,
                        timestamp=timestamp,
                        session_trade_counts=session_trade_counts,
                    )
                    held_bars = 0
                    pending_atr_stop_entry = _new_pending_atr_stop_entry(
                        atr_stop_config,
                        "long",
                        bar_index,
                        timestamp,
                    )
                    pending_close_only_exit_entry = _new_pending_close_only_exit_entry(
                        or_opposite_side_config,
                        fixed_r_target_config,
                        "long",
                        bar_index,
                    )
            elif short_entry and not long_entry:
                if _entry_control_allows_entry(
                    bar_index=bar_index,
                    last_entry_bar=last_entry_bar,
                    entry_controls=entry_controls,
                    context=context,
                    timestamp=timestamp,
                    session_trade_counts=session_trade_counts,
                ):
                    current_side = "short"
                    last_entry_bar = bar_index
                    _record_session_entry(
                        entry_controls=entry_controls,
                        context=context,
                        timestamp=timestamp,
                        session_trade_counts=session_trade_counts,
                    )
                    held_bars = 0
                    pending_atr_stop_entry = _new_pending_atr_stop_entry(
                        atr_stop_config,
                        "short",
                        bar_index,
                        timestamp,
                    )
                    pending_close_only_exit_entry = _new_pending_close_only_exit_entry(
                        or_opposite_side_config,
                        fixed_r_target_config,
                        "short",
                        bar_index,
                    )

        if current_side == "long":
            signal_values[bar_index] = 1.0
            held_bars += 1
        elif current_side == "short":
            signal_values[bar_index] = -1.0
            held_bars += 1
    return pd.Series(signal_values, index=ohlcv.index, name="signal")


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
        self.indicator_cache: dict[tuple[str, int, str], pd.Series | dict[str, pd.Series]] = {}
        self.primitive_cache: dict[tuple[str, str], pd.Series] = {}
        self.primitive_config_cache: dict[tuple[str, str], dict[str, Mapping[str, Any]]] = {}
        self.condition_cache: dict[tuple[int, tuple[str, ...]], pd.Series] = {}
        self.group_cache: dict[tuple[int, tuple[str, ...]], pd.Series] = {}
        self.bar_delta = _infer_bar_delta(ohlcv.index)


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


def _walk_group_mappings(group: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    groups = [group]
    subgroups = group.get("subgroups", [])
    if not isinstance(subgroups, list):
        raise SpecSignalCompilerError("condition group conditions/subgroups must be arrays")
    for subgroup in subgroups:
        groups.extend(_walk_group_mappings(_require_mapping(subgroup, "condition subgroup")))
    return groups


def _guard_no_side_labels(groups: list[Mapping[str, Any]], label: str) -> None:
    for index, group in enumerate(groups):
        for nested_group in _walk_group_mappings(group):
            if "side" in nested_group:
                raise SpecSignalCompilerError(f"{label}.{index}.side is not allowed")


def _validate_nested_side_labels(
    root_group: Mapping[str, Any],
    root_side: str,
    label: str,
) -> None:
    for nested_group in _walk_group_mappings(root_group)[1:]:
        if "side" not in nested_group:
            continue
        nested_side = nested_group.get("side")
        if nested_side not in SIDE_LABELS:
            raise SpecSignalCompilerError(f"{label} nested side label is invalid: {nested_side!r}")
        if nested_side != root_side:
            raise SpecSignalCompilerError(
                f"{label} nested side {nested_side!r} contradicts root side {root_side!r}"
            )


def _split_root_side_groups(
    groups: list[Mapping[str, Any]],
    label: str,
    *,
    require_both_sides: bool,
) -> dict[str, list[Mapping[str, Any]]]:
    groups_by_side: dict[str, list[Mapping[str, Any]]] = {"long": [], "short": []}
    for index, group in enumerate(groups):
        side = group.get("side")
        group_label = f"{label}.{index}"
        if side not in SIDE_LABELS:
            raise SpecSignalCompilerError(
                f"{group_label}.side must be one of {sorted(SIDE_LABELS)} for direction 'both'"
            )
        _validate_nested_side_labels(group, str(side), group_label)
        groups_by_side[str(side)].append(group)
    if require_both_sides:
        for side in sorted(SIDE_LABELS):
            if not groups_by_side[side]:
                raise SpecSignalCompilerError(
                    f"entry_logic.direction 'both' requires at least one {side!r} root entry group"
                )
    return groups_by_side


def _max_holding_bars(strategy_spec: Mapping[str, Any]) -> int | None:
    max_holding = strategy_spec.get("exit_logic", {}).get("max_holding_period")
    if not isinstance(max_holding, Mapping) or max_holding.get("enabled") is not True:
        return None
    bars = max_holding.get("bars")
    if not isinstance(bars, int) or bars < 1:
        raise SpecSignalCompilerError("enabled max_holding_period requires integer bars >= 1")
    return bars


def _entry_controls(strategy_spec: Mapping[str, Any], context: _CompileContext) -> _EntryControls:
    entry_logic = strategy_spec.get("entry_logic", {})
    if not isinstance(entry_logic, Mapping) or "entry_controls" not in entry_logic:
        return _EntryControls(None, None, None)
    controls = entry_logic.get("entry_controls")
    if not isinstance(controls, Mapping):
        raise SpecSignalCompilerError("entry_controls must be an object when provided")
    allowed_keys = {"min_bars_between_entries", "max_trades_per_session"}
    if not set(controls) <= allowed_keys:
        raise SpecSignalCompilerError(
            "entry_controls supports only min_bars_between_entries and max_trades_per_session"
        )
    min_bars_between_entries = None
    if "min_bars_between_entries" in controls:
        bars = controls.get("min_bars_between_entries")
        if isinstance(bars, bool) or not isinstance(bars, Integral) or bars < 1 or bars > 100000:
            raise SpecSignalCompilerError(
                "entry_controls.min_bars_between_entries requires integer bars in [1, 100000]"
            )
        min_bars_between_entries = int(bars)

    max_trades_per_session = None
    session_ref = None
    if "max_trades_per_session" in controls:
        max_control = controls.get("max_trades_per_session")
        if not isinstance(max_control, Mapping):
            raise SpecSignalCompilerError("entry_controls.max_trades_per_session must be an object")
        expected_keys = {"enabled", "count_basis", "max_trades", "session_ref", "reset"}
        if set(max_control) != expected_keys:
            raise SpecSignalCompilerError(
                f"entry_controls.max_trades_per_session supports exactly {sorted(expected_keys)}"
            )
        if max_control.get("enabled") is not True:
            raise SpecSignalCompilerError("entry_controls.max_trades_per_session.enabled must be true")
        if max_control.get("count_basis") != "entries_filled":
            raise SpecSignalCompilerError(
                "entry_controls.max_trades_per_session.count_basis must be 'entries_filled'"
            )
        max_trades = _resolve_parameter_bound_value(
            max_control.get("max_trades"),
            context,
            "entry_controls.max_trades_per_session.max_trades",
        )
        if (
            isinstance(max_trades, bool)
            or not isinstance(max_trades, Integral)
            or max_trades < 1
            or max_trades > 100000
        ):
            raise SpecSignalCompilerError(
                "entry_controls.max_trades_per_session.max_trades requires integer in [1, 100000]"
            )
        if max_control.get("reset") != "session_start":
            raise SpecSignalCompilerError(
                "entry_controls.max_trades_per_session.reset must be 'session_start'"
            )
        raw_session_ref = max_control.get("session_ref")
        if not isinstance(raw_session_ref, str) or not raw_session_ref:
            raise SpecSignalCompilerError(
                "entry_controls.max_trades_per_session.session_ref must be non-empty"
            )
        max_trades_per_session = int(max_trades)
        session_ref = raw_session_ref
    return _EntryControls(min_bars_between_entries, max_trades_per_session, session_ref)


def _atr_stop_config(
    strategy_spec: Mapping[str, Any],
    context: _CompileContext,
) -> _AtrStopConfig | None:
    exit_logic = strategy_spec.get("exit_logic", {})
    if not isinstance(exit_logic, Mapping) or "atr_stop" not in exit_logic:
        return None
    atr_stop = exit_logic.get("atr_stop")
    if not isinstance(atr_stop, Mapping):
        raise SpecSignalCompilerError("exit_logic.atr_stop must be an object when provided")
    if set(atr_stop) != ATR_STOP_ALLOWED_KEYS:
        raise SpecSignalCompilerError(
            f"exit_logic.atr_stop supports exactly {sorted(ATR_STOP_ALLOWED_KEYS)}"
        )
    if atr_stop.get("enabled") is not True:
        raise SpecSignalCompilerError("exit_logic.atr_stop.enabled must be true when atr_stop is provided")
    atr_lookback = atr_stop.get("atr_lookback")
    if (
        isinstance(atr_lookback, bool)
        or not isinstance(atr_lookback, Integral)
        or atr_lookback < 1
        or atr_lookback > ATR_STOP_MAX_LOOKBACK_BARS
    ):
        raise SpecSignalCompilerError(
            f"exit_logic.atr_stop.atr_lookback requires integer bars in [1, {ATR_STOP_MAX_LOOKBACK_BARS}]"
        )
    multiplier = _resolve_parameter_bound_value(
        atr_stop.get("atr_multiplier"),
        context,
        "exit_logic.atr_stop.atr_multiplier",
    )
    if isinstance(multiplier, bool) or not isinstance(multiplier, Real):
        raise SpecSignalCompilerError("exit_logic.atr_stop.atr_multiplier requires a positive finite number")
    multiplier_float = float(multiplier)
    if (
        not math.isfinite(multiplier_float)
        or multiplier_float <= 0.0
        or multiplier_float > ATR_STOP_MAX_MULTIPLIER
    ):
        raise SpecSignalCompilerError(
            f"exit_logic.atr_stop.atr_multiplier requires a positive finite number <= {ATR_STOP_MAX_MULTIPLIER:g}"
        )
    if atr_stop.get("entry_reference_price") != ATR_STOP_ENTRY_REFERENCE_PRICE:
        raise SpecSignalCompilerError(
            "exit_logic.atr_stop.entry_reference_price must be "
            f"{ATR_STOP_ENTRY_REFERENCE_PRICE!r}"
        )
    if atr_stop.get("evaluation_price") != ATR_STOP_EVALUATION_PRICE:
        raise SpecSignalCompilerError(
            f"exit_logic.atr_stop.evaluation_price must be {ATR_STOP_EVALUATION_PRICE!r}"
        )
    if atr_stop.get("evaluation_timing") != ATR_STOP_EVALUATION_TIMING:
        raise SpecSignalCompilerError(
            f"exit_logic.atr_stop.evaluation_timing must be {ATR_STOP_EVALUATION_TIMING!r}"
        )

    atr_series = _resolve_indicator_ref(
        {
            "operand_type": "indicator_ref",
            "ref": "atr",
            "field": "value",
            "timeframe": None,
            "lookback": {"bars": int(atr_lookback)},
        },
        context,
    )
    return _AtrStopConfig(
        atr_lookback=int(atr_lookback),
        atr_multiplier=multiplier_float,
        atr_series=atr_series,
    )


def _session_end_exit_config(strategy_spec: Mapping[str, Any]) -> _SessionEndExitConfig | None:
    exit_logic = strategy_spec.get("exit_logic", {})
    if not isinstance(exit_logic, Mapping) or "time_exit" not in exit_logic:
        return None
    time_exit = exit_logic.get("time_exit")
    if not isinstance(time_exit, Mapping):
        raise SpecSignalCompilerError("exit_logic.time_exit must be an object when provided")
    if set(time_exit) != TIME_EXIT_ALLOWED_KEYS:
        raise SpecSignalCompilerError(f"exit_logic.time_exit supports exactly {sorted(TIME_EXIT_ALLOWED_KEYS)}")
    session_end = time_exit.get("session_end")
    if not isinstance(session_end, Mapping):
        raise SpecSignalCompilerError("exit_logic.time_exit.session_end must be an object")
    if set(session_end) != SESSION_END_ALLOWED_KEYS:
        raise SpecSignalCompilerError(
            f"exit_logic.time_exit.session_end supports exactly {sorted(SESSION_END_ALLOWED_KEYS)}"
        )
    if session_end.get("enabled") is not True:
        raise SpecSignalCompilerError("exit_logic.time_exit.session_end.enabled must be true")
    session_ref = session_end.get("session_ref")
    if not isinstance(session_ref, str) or not session_ref:
        raise SpecSignalCompilerError("exit_logic.time_exit.session_end.session_ref must be non-empty")
    if session_end.get("exit_signal_timing") != SESSION_END_EXIT_SIGNAL_TIMING:
        raise SpecSignalCompilerError(
            "exit_logic.time_exit.session_end.exit_signal_timing must be "
            f"{SESSION_END_EXIT_SIGNAL_TIMING!r}"
        )
    if session_end.get("fill_timing") != SESSION_END_FILL_TIMING:
        raise SpecSignalCompilerError(
            f"exit_logic.time_exit.session_end.fill_timing must be {SESSION_END_FILL_TIMING!r}"
        )
    if session_end.get("partial_session_policy") != SESSION_END_PARTIAL_SESSION_POLICY:
        raise SpecSignalCompilerError(
            "exit_logic.time_exit.session_end.partial_session_policy must be "
            f"{SESSION_END_PARTIAL_SESSION_POLICY!r}"
        )
    return _SessionEndExitConfig(session_ref=session_ref)


def _opening_range_opposite_side_config(
    strategy_spec: Mapping[str, Any],
) -> _OpeningRangeOppositeSideConfig | None:
    exit_logic = strategy_spec.get("exit_logic", {})
    if not isinstance(exit_logic, Mapping) or "opening_range_opposite_side" not in exit_logic:
        return None
    config = exit_logic.get("opening_range_opposite_side")
    if not isinstance(config, Mapping):
        raise SpecSignalCompilerError("exit_logic.opening_range_opposite_side must be an object")
    if set(config) != OR_OPPOSITE_SIDE_ALLOWED_KEYS:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side supports exactly "
            f"{sorted(OR_OPPOSITE_SIDE_ALLOWED_KEYS)}"
        )
    if config.get("enabled") is not True:
        raise SpecSignalCompilerError("exit_logic.opening_range_opposite_side.enabled must be true")
    range_ref = config.get("range_ref")
    if not isinstance(range_ref, str) or not range_ref:
        raise SpecSignalCompilerError("exit_logic.opening_range_opposite_side.range_ref must be non-empty")
    if config.get("entry_reference_price") != OR_OPPOSITE_SIDE_ENTRY_REFERENCE_PRICE:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.entry_reference_price must be "
            f"{OR_OPPOSITE_SIDE_ENTRY_REFERENCE_PRICE!r}"
        )
    if config.get("evaluation_price") != OR_OPPOSITE_SIDE_EVALUATION_PRICE:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.evaluation_price must be "
            f"{OR_OPPOSITE_SIDE_EVALUATION_PRICE!r}"
        )
    if config.get("evaluation_timing") != OR_OPPOSITE_SIDE_EVALUATION_TIMING:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.evaluation_timing must be "
            f"{OR_OPPOSITE_SIDE_EVALUATION_TIMING!r}"
        )
    if config.get("long_stop_level") != OR_OPPOSITE_SIDE_LONG_STOP_LEVEL:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.long_stop_level must be "
            f"{OR_OPPOSITE_SIDE_LONG_STOP_LEVEL!r}"
        )
    if config.get("short_stop_level") != OR_OPPOSITE_SIDE_SHORT_STOP_LEVEL:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.short_stop_level must be "
            f"{OR_OPPOSITE_SIDE_SHORT_STOP_LEVEL!r}"
        )
    if config.get("same_bar_entry_stop_policy") != OR_OPPOSITE_SIDE_SAME_BAR_POLICY:
        raise SpecSignalCompilerError(
            "exit_logic.opening_range_opposite_side.same_bar_entry_stop_policy must be "
            f"{OR_OPPOSITE_SIDE_SAME_BAR_POLICY!r}"
        )
    return _OpeningRangeOppositeSideConfig(range_ref=str(range_ref))


def _fixed_r_target_config(
    strategy_spec: Mapping[str, Any],
    or_opposite_side_config: _OpeningRangeOppositeSideConfig | None,
    context: _CompileContext,
) -> _FixedRTargetConfig | None:
    exit_logic = strategy_spec.get("exit_logic", {})
    if not isinstance(exit_logic, Mapping) or "fixed_R_target" not in exit_logic:
        return None
    config = exit_logic.get("fixed_R_target")
    if not isinstance(config, Mapping):
        raise SpecSignalCompilerError("exit_logic.fixed_R_target must be an object")
    if set(config) != FIXED_R_TARGET_ALLOWED_KEYS:
        raise SpecSignalCompilerError(
            f"exit_logic.fixed_R_target supports exactly {sorted(FIXED_R_TARGET_ALLOWED_KEYS)}"
        )
    if config.get("enabled") is not True:
        raise SpecSignalCompilerError("exit_logic.fixed_R_target.enabled must be true")
    if or_opposite_side_config is None:
        raise SpecSignalCompilerError(
            "exit_logic.fixed_R_target requires exit_logic.opening_range_opposite_side"
        )
    multiple = _resolve_parameter_bound_value(
        config.get("r_multiple"),
        context,
        "exit_logic.fixed_R_target.r_multiple",
    )
    if isinstance(multiple, bool) or not isinstance(multiple, Real):
        raise SpecSignalCompilerError("exit_logic.fixed_R_target.r_multiple requires a positive finite number")
    multiple_float = float(multiple)
    if (
        not math.isfinite(multiple_float)
        or multiple_float <= 0.0
        or multiple_float > FIXED_R_TARGET_MAX_MULTIPLE
    ):
        raise SpecSignalCompilerError(
            "exit_logic.fixed_R_target.r_multiple requires a positive finite number "
            f"<= {FIXED_R_TARGET_MAX_MULTIPLE:g}"
        )
    if config.get("entry_reference_price") != FIXED_R_TARGET_ENTRY_REFERENCE_PRICE:
        raise SpecSignalCompilerError(
            "exit_logic.fixed_R_target.entry_reference_price must be "
            f"{FIXED_R_TARGET_ENTRY_REFERENCE_PRICE!r}"
        )
    if config.get("stop_ref") != FIXED_R_TARGET_STOP_REF:
        raise SpecSignalCompilerError(f"exit_logic.fixed_R_target.stop_ref must be {FIXED_R_TARGET_STOP_REF!r}")
    if config.get("evaluation_price") != FIXED_R_TARGET_EVALUATION_PRICE:
        raise SpecSignalCompilerError(
            f"exit_logic.fixed_R_target.evaluation_price must be {FIXED_R_TARGET_EVALUATION_PRICE!r}"
        )
    if config.get("evaluation_timing") != FIXED_R_TARGET_EVALUATION_TIMING:
        raise SpecSignalCompilerError(
            f"exit_logic.fixed_R_target.evaluation_timing must be {FIXED_R_TARGET_EVALUATION_TIMING!r}"
        )
    if config.get("same_bar_stop_target_policy") != FIXED_R_TARGET_SAME_BAR_POLICY:
        raise SpecSignalCompilerError(
            "exit_logic.fixed_R_target.same_bar_stop_target_policy must be "
            f"{FIXED_R_TARGET_SAME_BAR_POLICY!r}"
        )
    return _FixedRTargetConfig(r_multiple=multiple_float)


def _new_pending_atr_stop_entry(
    atr_stop_config: _AtrStopConfig | None,
    side: str,
    bar_index: int,
    timestamp: Any,
) -> _PendingAtrStopEntry | None:
    if atr_stop_config is None:
        return None
    atr_at_entry = _value_at(atr_stop_config.atr_series, timestamp)
    if _is_null(atr_at_entry):
        raise SpecSignalCompilerError("exit_logic.atr_stop ATR is not available at entry signal bar")
    atr_float = float(atr_at_entry)
    if not math.isfinite(atr_float) or atr_float <= 0.0:
        raise SpecSignalCompilerError("exit_logic.atr_stop ATR at entry must be positive and finite")
    return _PendingAtrStopEntry(
        side=side,
        signal_bar_index=bar_index,
        atr_at_entry=atr_float,
    )


def _capture_atr_stop_state(
    *,
    pending_entry: _PendingAtrStopEntry,
    ohlcv: pd.DataFrame,
    fill_bar_index: int,
) -> _AtrStopState:
    if fill_bar_index <= pending_entry.signal_bar_index:
        raise SpecSignalCompilerError("exit_logic.atr_stop fill bar must follow entry signal bar")
    entry_reference_price = ohlcv["open"].iloc[fill_bar_index]
    if _is_null(entry_reference_price):
        raise SpecSignalCompilerError("exit_logic.atr_stop entry reference price is null at fill bar")
    entry_reference_float = float(entry_reference_price)
    if not math.isfinite(entry_reference_float) or entry_reference_float <= 0.0:
        raise SpecSignalCompilerError(
            "exit_logic.atr_stop entry reference price must be positive and finite"
        )
    return _AtrStopState(
        side=pending_entry.side,
        entry_reference_price=entry_reference_float,
        atr_at_entry=pending_entry.atr_at_entry,
    )


def _new_pending_close_only_exit_entry(
    or_opposite_side_config: _OpeningRangeOppositeSideConfig | None,
    fixed_r_target_config: _FixedRTargetConfig | None,
    side: str,
    bar_index: int,
) -> _PendingCloseOnlyExitEntry | None:
    if or_opposite_side_config is None and fixed_r_target_config is None:
        return None
    return _PendingCloseOnlyExitEntry(side=side, signal_bar_index=bar_index)


def _open_price_at_bar(ohlcv: pd.DataFrame, bar_index: int, label: str) -> float:
    price = ohlcv["open"].iloc[bar_index]
    if _is_null(price):
        raise SpecSignalCompilerError(f"{label} entry reference price is null at fill bar")
    price_float = float(price)
    if not math.isfinite(price_float) or price_float <= 0.0:
        raise SpecSignalCompilerError(f"{label} entry reference price must be positive and finite")
    return price_float


def _capture_close_only_exit_state(
    *,
    pending_entry: _PendingCloseOnlyExitEntry,
    config: _OpeningRangeOppositeSideConfig | None,
    context: _CompileContext,
    fill_bar_index: int,
) -> _CloseOnlyExitState | None:
    if config is None or fill_bar_index >= len(context.ohlcv):
        return None
    if fill_bar_index <= pending_entry.signal_bar_index:
        raise SpecSignalCompilerError("close-only exit fill bar must follow entry signal bar")
    entry_reference_price = _open_price_at_bar(
        context.ohlcv,
        fill_bar_index,
        "close-only exit",
    )
    range_state = _opening_range_state(context, config.range_ref)
    signal_timestamp = context.ohlcv.index[pending_entry.signal_bar_index]
    long_stop_level = range_state["low"].loc[signal_timestamp]
    short_stop_level = range_state["high"].loc[signal_timestamp]
    values = (long_stop_level, short_stop_level)
    if any(_is_null(value) for value in values):
        return None
    long_stop_float = float(long_stop_level)
    short_stop_float = float(short_stop_level)
    if (
        not math.isfinite(long_stop_float)
        or not math.isfinite(short_stop_float)
        or short_stop_float <= long_stop_float
    ):
        return None
    return _CloseOnlyExitState(
        side=pending_entry.side,
        entry_reference_price=entry_reference_price,
        long_stop_level=long_stop_float,
        short_stop_level=short_stop_float,
    )


def _atr_stop_triggered(
    atr_stop_config: _AtrStopConfig | None,
    atr_stop_state: _AtrStopState | None,
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    if atr_stop_config is None or atr_stop_state is None:
        return False
    close_value = _value_at(context.ohlcv[ATR_STOP_EVALUATION_PRICE], timestamp)
    if _is_null(close_value):
        return False
    close_float = float(close_value)
    if not math.isfinite(close_float):
        return False
    if atr_stop_state.side == "long":
        stop_level = (
            atr_stop_state.entry_reference_price
            - (atr_stop_config.atr_multiplier * atr_stop_state.atr_at_entry)
        )
        return close_float <= stop_level
    if atr_stop_state.side == "short":
        stop_level = (
            atr_stop_state.entry_reference_price
            + (atr_stop_config.atr_multiplier * atr_stop_state.atr_at_entry)
        )
        return close_float >= stop_level
    raise SpecSignalCompilerError(f"unknown ATR-stop side: {atr_stop_state.side!r}")


def _opening_range_opposite_side_triggered(
    config: _OpeningRangeOppositeSideConfig | None,
    state: _CloseOnlyExitState | None,
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    if config is None or state is None:
        return False
    close_value = _value_at(context.ohlcv[OR_OPPOSITE_SIDE_EVALUATION_PRICE], timestamp)
    if _is_null(close_value):
        return False
    close_float = float(close_value)
    if not math.isfinite(close_float):
        return False
    if state.side == "long":
        return close_float <= state.long_stop_level
    if state.side == "short":
        return close_float >= state.short_stop_level
    raise SpecSignalCompilerError(f"unknown close-only exit side: {state.side!r}")


def _fixed_r_target_triggered(
    config: _FixedRTargetConfig | None,
    state: _CloseOnlyExitState | None,
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    if config is None or state is None:
        return False
    close_value = _value_at(context.ohlcv[FIXED_R_TARGET_EVALUATION_PRICE], timestamp)
    if _is_null(close_value):
        return False
    close_float = float(close_value)
    if not math.isfinite(close_float):
        return False
    if state.side == "long":
        r_base = state.entry_reference_price - state.long_stop_level
        if not math.isfinite(r_base) or r_base <= 0.0:
            return False
        return close_float >= state.entry_reference_price + (config.r_multiple * r_base)
    if state.side == "short":
        r_base = state.short_stop_level - state.entry_reference_price
        if not math.isfinite(r_base) or r_base <= 0.0:
            return False
        return close_float <= state.entry_reference_price - (config.r_multiple * r_base)
    raise SpecSignalCompilerError(f"unknown fixed-R target side: {state.side!r}")


def _session_end_exit_triggered(
    config: _SessionEndExitConfig | None,
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    if config is None:
        return False
    return bool(_session_end_exit_series(context, config.session_ref).loc[timestamp])


def _session_end_exit_series(context: _CompileContext, session_ref: str) -> pd.Series:
    cache_key = ("session_end_exit", session_ref)
    if cache_key in context.primitive_cache:
        return context.primitive_cache[cache_key]
    in_session, session_keys = _session_membership(context, session_ref)
    index = context.ohlcv.index
    result = pd.Series(False, index=index, dtype=bool)
    bar_delta = context.bar_delta
    if bar_delta is None or bar_delta <= pd.Timedelta(0):
        context.primitive_cache[cache_key] = result
        return result
    in_values = in_session.to_numpy(dtype=bool)
    key_values = session_keys.to_numpy(dtype=object)
    output = np.zeros(len(index), dtype=bool)
    for position, session_start in enumerate(key_values):
        if not in_values[position] or session_start is None:
            continue
        expected_final_bar = pd.Timestamp(session_start) + pd.Timedelta(days=1) - bar_delta
        output[position] = pd.Timestamp(index[position]) == expected_final_bar
    result = pd.Series(output, index=index, dtype=bool)
    context.primitive_cache[cache_key] = result
    return result


def _entry_control_allows_entry(
    *,
    bar_index: int,
    last_entry_bar: int | None,
    entry_controls: _EntryControls,
    context: _CompileContext,
    timestamp: Any,
    session_trade_counts: dict[Any, int],
) -> bool:
    if (
        entry_controls.min_bars_between_entries is not None
        and last_entry_bar is not None
        and bar_index - last_entry_bar <= entry_controls.min_bars_between_entries
    ):
        return False
    if entry_controls.max_trades_per_session is None:
        return True
    session_key = _session_key_for_ref(context, entry_controls.session_ref, timestamp)
    if session_key is None:
        return False
    return session_trade_counts.get(session_key, 0) < entry_controls.max_trades_per_session


def _record_session_entry(
    *,
    entry_controls: _EntryControls,
    context: _CompileContext,
    timestamp: Any,
    session_trade_counts: dict[Any, int],
) -> None:
    if entry_controls.max_trades_per_session is None:
        return
    session_key = _session_key_for_ref(context, entry_controls.session_ref, timestamp)
    if session_key is None:
        return
    session_trade_counts[session_key] = session_trade_counts.get(session_key, 0) + 1


def _entry_allowed(groups: list[Mapping[str, Any]], context: _CompileContext, timestamp: Any) -> bool:
    return bool(_entry_allowed_series(groups, context).loc[timestamp])


def _entry_allowed_series(groups: list[Mapping[str, Any]], context: _CompileContext) -> pd.Series:
    entry_groups = [group for group in groups if group.get("group_role") in ENTRY_GROUP_ROLES]
    blocking_groups = [group for group in groups if group.get("group_role") in BLOCKING_GROUP_ROLES]
    for group in groups:
        role = group.get("group_role")
        if role not in ENTRY_GROUP_ROLES | BLOCKING_GROUP_ROLES:
            raise UnsupportedSpecSignalCompilerFeature(f"unsupported entry/filter group role: {role!r}")
    if not entry_groups:
        return pd.Series(False, index=context.ohlcv.index, dtype=bool)
    result = pd.Series(True, index=context.ohlcv.index, dtype=bool)
    for group in entry_groups:
        result = result & _evaluate_group_series(group, context, ENTRY_CONDITION_ROLES)
    for group in blocking_groups:
        result = result & ~_evaluate_group_series(group, context, BLOCKING_CONDITION_ROLES)
    return result.fillna(False)


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
    return any(
        bool(_evaluate_group_series(group, context, EXIT_CONDITION_ROLES).loc[timestamp])
        for group in relevant
    )


def _evaluate_group_series(
    group: Mapping[str, Any],
    context: _CompileContext,
    allowed_condition_roles: set[str],
) -> pd.Series:
    cache_key = (id(group), tuple(sorted(allowed_condition_roles)))
    if cache_key in context.group_cache:
        return context.group_cache[cache_key]
    logic = group.get("logic")
    if logic not in {"all", "any"}:
        raise SpecSignalCompilerError(f"unsupported condition group logic: {logic!r}")
    conditions = group.get("conditions", [])
    subgroups = group.get("subgroups", [])
    if not isinstance(conditions, list) or not isinstance(subgroups, list):
        raise SpecSignalCompilerError("condition group conditions/subgroups must be arrays")
    values = [
        _evaluate_condition_series(
            _require_mapping(condition, "condition"),
            context,
            allowed_condition_roles,
        )
        for condition in conditions
    ]
    values.extend(
        _evaluate_group_series(
            _require_mapping(subgroup, "condition subgroup"),
            context,
            allowed_condition_roles,
        )
        for subgroup in subgroups
    )
    if not values:
        result = pd.Series(False, index=context.ohlcv.index, dtype=bool)
    elif logic == "all":
        result = values[0].copy()
        for value in values[1:]:
            result = result & value
    else:
        result = values[0].copy()
        for value in values[1:]:
            result = result | value
    context.group_cache[cache_key] = result.fillna(False)
    return context.group_cache[cache_key]


def _evaluate_condition_series(
    condition: Mapping[str, Any],
    context: _CompileContext,
    allowed_condition_roles: set[str],
) -> pd.Series:
    cache_key = (id(condition), tuple(sorted(allowed_condition_roles)))
    if cache_key in context.condition_cache:
        return context.condition_cache[cache_key]
    role = condition.get("condition_role")
    if role not in {"required", "confirming", "blocking", "exit", "invalidation", "filter"}:
        raise UnsupportedSpecSignalCompilerFeature(f"unsupported condition role: {role!r}")
    if role not in allowed_condition_roles:
        raise UnsupportedSpecSignalCompilerFeature(
            f"condition role {role!r} is incompatible with this group context"
        )
    operator = condition.get("operator")
    if operator in UNSUPPORTED_OPERATORS:
        raise UnsupportedSpecSignalCompilerFeature(f"operator {operator!r} is not supported in WP-S2c-199")
    if operator not in SUPPORTED_OPERATORS:
        raise SpecSignalCompilerError(f"unknown operator: {operator!r}")
    left = _resolve_operand(_require_mapping(condition.get("left_operand"), "left_operand"), context)
    right = _resolve_operand(_require_mapping(condition.get("right_operand"), "right_operand"), context)
    if operator in BOOLEAN_OPERATORS:
        left_series = _as_series(left, context)
        if operator == "is_true":
            result = left_series.map(lambda value: bool(value is True or value == 1) if not _is_null(value) else False)
        else:
            result = left_series.map(lambda value: bool(value is False or value == 0) if not _is_null(value) else False)
    elif operator in CROSSOVER_OPERATORS:
        result = _evaluate_crossover_series(operator, left, right, context)
    else:
        left_series = _as_series(left, context)
        right_series = _as_series(right, context)
        valid = ~(left_series.isna() | right_series.isna())
        if operator == "gt":
            result = valid & (left_series > right_series)
        elif operator == "gte":
            result = valid & (left_series >= right_series)
        elif operator == "lt":
            result = valid & (left_series < right_series)
        elif operator == "lte":
            result = valid & (left_series <= right_series)
        elif operator == "eq":
            result = valid & (left_series == right_series)
        elif operator == "neq":
            result = valid & (left_series != right_series)
        else:
            raise SpecSignalCompilerError(f"unhandled operator: {operator!r}")
    context.condition_cache[cache_key] = result.fillna(False).astype(bool)
    return context.condition_cache[cache_key]


def _as_series(value: Any, context: _CompileContext) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    return pd.Series([value] * len(context.ohlcv.index), index=context.ohlcv.index)


def _evaluate_crossover_series(
    operator: str,
    left: Any,
    right: Any,
    context: _CompileContext,
) -> pd.Series:
    left_series = _as_series(left, context)
    right_series = _as_series(right, context)
    previous_left = left_series.shift(1)
    previous_right = right_series.shift(1)
    valid = ~(previous_left.isna() | previous_right.isna() | left_series.isna() | right_series.isna())
    if operator == "crosses_above":
        return valid & (previous_left <= previous_right) & (left_series > right_series)
    if operator == "crosses_below":
        return valid & (previous_left >= previous_right) & (left_series < right_series)
    raise SpecSignalCompilerError(f"unhandled crossover operator: {operator!r}")


def _evaluate_group(
    group: Mapping[str, Any],
    context: _CompileContext,
    timestamp: Any,
    allowed_condition_roles: set[str],
) -> bool:
    logic = group.get("logic")
    if logic not in {"all", "any"}:
        raise SpecSignalCompilerError(f"unsupported condition group logic: {logic!r}")
    conditions = group.get("conditions", [])
    subgroups = group.get("subgroups", [])
    if not isinstance(conditions, list) or not isinstance(subgroups, list):
        raise SpecSignalCompilerError("condition group conditions/subgroups must be arrays")
    values = [
        _evaluate_condition(
            _require_mapping(condition, "condition"),
            context,
            timestamp,
            allowed_condition_roles,
        )
        for condition in conditions
    ]
    values.extend(
        _evaluate_group(
            _require_mapping(subgroup, "condition subgroup"),
            context,
            timestamp,
            allowed_condition_roles,
        )
        for subgroup in subgroups
    )
    if not values:
        return False
    return all(values) if logic == "all" else any(values)


def _evaluate_condition(
    condition: Mapping[str, Any],
    context: _CompileContext,
    timestamp: Any,
    allowed_condition_roles: set[str],
) -> bool:
    role = condition.get("condition_role")
    if role not in {"required", "confirming", "blocking", "exit", "invalidation", "filter"}:
        raise UnsupportedSpecSignalCompilerFeature(f"unsupported condition role: {role!r}")
    if role not in allowed_condition_roles:
        raise UnsupportedSpecSignalCompilerFeature(
            f"condition role {role!r} is incompatible with this group context"
        )
    operator = condition.get("operator")
    if operator in UNSUPPORTED_OPERATORS:
        raise UnsupportedSpecSignalCompilerFeature(f"operator {operator!r} is not supported in WP-S2c-199")
    if operator not in SUPPORTED_OPERATORS:
        raise SpecSignalCompilerError(f"unknown operator: {operator!r}")
    left = _resolve_operand(_require_mapping(condition.get("left_operand"), "left_operand"), context)
    right = _resolve_operand(_require_mapping(condition.get("right_operand"), "right_operand"), context)
    if operator in BOOLEAN_OPERATORS:
        left_value = _value_at(left, timestamp)
        if _is_null(left_value):
            return False
        if operator == "is_true":
            return bool(left_value is True or left_value == 1)
        if operator == "is_false":
            return bool(left_value is False or left_value == 0)
    if operator in CROSSOVER_OPERATORS:
        return _evaluate_crossover(operator, left, right, context, timestamp)
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


def _evaluate_crossover(
    operator: str,
    left: Any,
    right: Any,
    context: _CompileContext,
    timestamp: Any,
) -> bool:
    previous_timestamp = _previous_timestamp(context.ohlcv.index, timestamp)
    if previous_timestamp is None:
        return False
    previous_left = _value_at(left, previous_timestamp)
    previous_right = _value_at(right, previous_timestamp)
    current_left = _value_at(left, timestamp)
    current_right = _value_at(right, timestamp)
    if any(
        _is_null(value)
        for value in (previous_left, previous_right, current_left, current_right)
    ):
        return False
    if operator == "crosses_above":
        return bool(previous_left <= previous_right and current_left > current_right)
    if operator == "crosses_below":
        return bool(previous_left >= previous_right and current_left < current_right)
    raise SpecSignalCompilerError(f"unhandled crossover operator: {operator!r}")


def _previous_timestamp(index: pd.DatetimeIndex, timestamp: Any) -> Any | None:
    location = index.get_loc(timestamp)
    if not isinstance(location, Integral):
        raise SpecSignalCompilerError("ohlcv index timestamps must be unique for crossover operators")
    if location == 0:
        return None
    return index[location - 1]


def _online_primitives(context: _CompileContext) -> Mapping[str, Any]:
    primitives = context.strategy_spec.get(ONLINE_OHLCV_PRIMITIVES_KEY, {})
    if primitives in ({}, None):
        return {}
    if not isinstance(primitives, Mapping):
        raise SpecSignalCompilerError("online_ohlcv_primitives must be an object when provided")
    return primitives


def _primitive_items(context: _CompileContext, key: str) -> list[Mapping[str, Any]]:
    value = _online_primitives(context).get(key, [])
    if not isinstance(value, list):
        raise SpecSignalCompilerError(f"online_ohlcv_primitives.{key} must be an array")
    return [_require_mapping(item, f"online_ohlcv_primitives.{key} item") for item in value]


def _primitive_by_id(context: _CompileContext, key: str, id_key: str) -> dict[str, Mapping[str, Any]]:
    cache_key = (key, id_key)
    if cache_key in context.primitive_config_cache:
        return context.primitive_config_cache[cache_key]
    by_id: dict[str, Mapping[str, Any]] = {}
    for item in _primitive_items(context, key):
        item_id = item.get(id_key)
        if not isinstance(item_id, str) or not item_id:
            raise SpecSignalCompilerError(f"{key} item missing {id_key}")
        if item_id in by_id:
            raise SpecSignalCompilerError(f"duplicate {id_key}: {item_id}")
        by_id[item_id] = item
    context.primitive_config_cache[cache_key] = by_id
    return by_id


def _session_windows(context: _CompileContext) -> dict[str, Mapping[str, Any]]:
    return _primitive_by_id(context, SESSION_WINDOWS_KEY, "session_id")


def _parse_hhmm(value: Any, label: str) -> tuple[int, int]:
    if not isinstance(value, str):
        raise SpecSignalCompilerError(f"{label} must be HH:MM UTC")
    parts = value.split(":")
    if len(parts) != 2 or not all(part.isdigit() and len(part) == 2 for part in parts):
        raise SpecSignalCompilerError(f"{label} must be HH:MM UTC")
    hour, minute = int(parts[0]), int(parts[1])
    if hour > 23 or minute > 59:
        raise SpecSignalCompilerError(f"{label} must be HH:MM UTC")
    return hour, minute


def _session_start_for_timestamp(timestamp: pd.Timestamp, anchor_hour: int, anchor_minute: int) -> pd.Timestamp:
    anchor = timestamp.normalize() + pd.Timedelta(hours=anchor_hour, minutes=anchor_minute)
    if timestamp < anchor:
        anchor -= pd.Timedelta(days=1)
    return anchor


def _infer_bar_delta(index: pd.DatetimeIndex) -> pd.Timedelta | None:
    if len(index) < 2:
        return None
    deltas = index.to_series().diff().dropna().unique()
    if len(deltas) != 1:
        return None
    return pd.Timedelta(deltas[0])


def _session_membership(context: _CompileContext, session_id: str) -> tuple[pd.Series, pd.Series]:
    cache_key = ("session", session_id)
    key_cache = ("session_key", session_id)
    if cache_key in context.primitive_cache and key_cache in context.primitive_cache:
        return context.primitive_cache[cache_key], context.primitive_cache[key_cache]
    session = _session_windows(context).get(session_id)
    if session is None:
        raise SpecSignalCompilerError(f"unknown session_window ref: {session_id}")
    if session.get("timezone") != "UTC":
        raise SpecSignalCompilerError("session_window.timezone must be 'UTC'")
    duration = session.get("duration")
    if not isinstance(duration, Mapping) or duration.get("value") != 1 or duration.get("units") != "day":
        raise SpecSignalCompilerError("session_window.duration must be {value: 1, units: 'day'}")
    anchor_hour, anchor_minute = _parse_hhmm(session.get("anchor_time"), "session_window.anchor_time")
    index = context.ohlcv.index
    if index.tz is None:
        raise SpecSignalCompilerError("session_window requires UTC-aware OHLCV timestamps")
    bar_delta = context.bar_delta
    in_values = np.zeros(len(index), dtype=bool)
    key_values = np.empty(len(index), dtype=object)
    key_values[:] = None
    if bar_delta is None or bar_delta <= pd.Timedelta(0) or pd.Timedelta(days=1) % bar_delta != pd.Timedelta(0):
        in_session = pd.Series(in_values, index=index, dtype=bool)
        keys = pd.Series(key_values, index=index, dtype=object)
        context.primitive_cache[cache_key] = in_session
        context.primitive_cache[key_cache] = keys
        return in_session, keys
    for position, timestamp in enumerate(index):
        ts = pd.Timestamp(timestamp)
        session_start = _session_start_for_timestamp(ts, anchor_hour, anchor_minute)
        offset = ts - session_start
        if pd.Timedelta(0) <= offset < pd.Timedelta(days=1) and offset % bar_delta == pd.Timedelta(0):
            in_values[position] = True
            key_values[position] = session_start
    in_session = pd.Series(in_values, index=index, dtype=bool)
    keys = pd.Series(key_values, index=index, dtype=object)
    context.primitive_cache[cache_key] = in_session
    context.primitive_cache[key_cache] = keys
    return in_session, keys


def _session_key_for_ref(
    context: _CompileContext,
    session_ref: str | None,
    timestamp: Any,
) -> Any | None:
    if session_ref is None:
        return None
    in_session, session_keys = _session_membership(context, session_ref)
    if not bool(in_session.loc[timestamp]):
        return None
    return session_keys.loc[timestamp]


def _opening_range_state(context: _CompileContext, range_id: str) -> dict[str, pd.Series]:
    cache_key = ("opening_range_complete", range_id)
    if cache_key in context.primitive_cache:
        return {
            "complete": context.primitive_cache[("opening_range_complete", range_id)],
            "valid": context.primitive_cache[("opening_range_valid", range_id)],
            "high": context.primitive_cache[("opening_range_high", range_id)],
            "low": context.primitive_cache[("opening_range_low", range_id)],
        }
    ranges = _primitive_by_id(context, OPENING_RANGES_KEY, "range_id")
    config = ranges.get(range_id)
    if config is None:
        raise SpecSignalCompilerError(f"unknown opening_range ref: {range_id}")
    session_ref = config.get("session_ref")
    if not isinstance(session_ref, str) or not session_ref:
        raise SpecSignalCompilerError("opening_range.session_ref is required")
    if config.get("high_source") != "high" or config.get("low_source") != "low":
        raise SpecSignalCompilerError("opening_range high_source/low_source must be high/low")
    if config.get("close_after_range_required") is not True:
        raise SpecSignalCompilerError("opening_range.close_after_range_required must be true")
    start_offset = _bars_value(config.get("start_offset"), "opening_range.start_offset", minimum=0)
    length = _bars_value(config.get("length"), "opening_range.length", minimum=1)
    in_session, session_keys = _session_membership(context, session_ref)
    index = context.ohlcv.index
    complete_values = np.zeros(len(index), dtype=bool)
    valid_values = np.zeros(len(index), dtype=bool)
    high_values = np.full(len(index), math.nan, dtype=float)
    low_values = np.full(len(index), math.nan, dtype=float)
    by_session: dict[Any, list[int]] = {}
    in_values = in_session.to_numpy(dtype=bool)
    key_values = session_keys.to_numpy(dtype=object)
    for position, session_key in enumerate(key_values):
        if in_values[position]:
            by_session.setdefault(session_key, []).append(position)
    bar_delta = context.bar_delta
    high_source = context.ohlcv["high"].to_numpy(dtype=float)
    low_source = context.ohlcv["low"].to_numpy(dtype=float)
    for positions in by_session.values():
        if len(positions) < start_offset + length or bar_delta is None:
            continue
        range_positions = positions[start_offset : start_offset + length]
        range_timestamps = index[range_positions]
        expected = pd.date_range(range_timestamps[0], periods=length, freq=bar_delta)
        if list(expected) != list(range_timestamps):
            continue
        range_high = high_source[range_positions]
        range_low = low_source[range_positions]
        if np.isnan(range_high).any() or np.isnan(range_low).any():
            continue
        high = float(np.max(range_high))
        low = float(np.min(range_low))
        if not math.isfinite(high) or not math.isfinite(low) or high <= low:
            continue
        ready_from_index = start_offset + length
        ready_positions = positions[ready_from_index:]
        complete_values[ready_positions] = True
        valid_values[ready_positions] = True
        high_values[ready_positions] = high
        low_values[ready_positions] = low
    complete = pd.Series(complete_values, index=index, dtype=bool)
    valid = pd.Series(valid_values, index=index, dtype=bool)
    high_out = pd.Series(high_values, index=index, dtype=float)
    low_out = pd.Series(low_values, index=index, dtype=float)
    context.primitive_cache[("opening_range_complete", range_id)] = complete
    context.primitive_cache[("opening_range_valid", range_id)] = valid
    context.primitive_cache[("opening_range_high", range_id)] = high_out
    context.primitive_cache[("opening_range_low", range_id)] = low_out
    return {"complete": complete, "valid": valid, "high": high_out, "low": low_out}


def _bars_value(value: Any, label: str, *, minimum: int) -> int:
    if not isinstance(value, Mapping) or value.get("units") != "bars":
        raise SpecSignalCompilerError(f"{label} must be a bars object")
    raw = value.get("value")
    if isinstance(raw, bool) or not isinstance(raw, Integral) or raw < minimum:
        raise SpecSignalCompilerError(f"{label}.value must be an integer >= {minimum}")
    return int(raw)


def _atr_tolerance(context: _CompileContext, tolerance: Any) -> pd.Series:
    if not isinstance(tolerance, Mapping):
        raise SpecSignalCompilerError("tolerance must be an object")
    if tolerance.get("mode") != "atr_multiple" or tolerance.get("units") != "ATR":
        raise SpecSignalCompilerError("tolerance.mode must be atr_multiple with units ATR")
    lookback = tolerance.get("atr_lookback_bars")
    multiple = _resolve_parameter_bound_value(tolerance.get("multiple"), context, "tolerance.multiple")
    if isinstance(lookback, bool) or not isinstance(lookback, Integral) or lookback < 1:
        raise SpecSignalCompilerError("tolerance.atr_lookback_bars must be an integer >= 1")
    if isinstance(multiple, bool) or not isinstance(multiple, Real):
        raise SpecSignalCompilerError("tolerance.multiple must be a positive finite number")
    multiple_float = float(multiple)
    if not math.isfinite(multiple_float) or multiple_float < 0.0:
        raise SpecSignalCompilerError("tolerance.multiple must be finite and non-negative")
    atr = _resolve_indicator_ref(
        {
            "operand_type": "indicator_ref",
            "ref": "atr",
            "field": "value",
            "timeframe": None,
            "lookback": {"bars": int(lookback)},
        },
        context,
    )
    return atr * multiple_float


def _breakout_state(context: _CompileContext, breakout_id: str) -> dict[str, pd.Series]:
    if ("breakout_long", breakout_id) in context.primitive_cache:
        return {
            "long": context.primitive_cache[("breakout_long", breakout_id)],
            "short": context.primitive_cache[("breakout_short", breakout_id)],
            "side": context.primitive_cache[("breakout_side", breakout_id)],
            "bar_index": context.primitive_cache[("breakout_bar_index", breakout_id)],
        }
    breakouts = _primitive_by_id(context, OPENING_RANGE_BREAKOUTS_KEY, "breakout_id")
    config = breakouts.get(breakout_id)
    if config is None:
        raise SpecSignalCompilerError(f"unknown opening_range_breakout ref: {breakout_id}")
    if config.get("confirmation_price") != "close" or config.get("confirmation_timing") != "bar_close":
        raise SpecSignalCompilerError("opening_range_breakout must be close/bar_close confirmed")
    if config.get("entry_timing") != "next_bar_open":
        raise SpecSignalCompilerError("opening_range_breakout.entry_timing must be next_bar_open")
    range_ref = config.get("range_ref")
    if not isinstance(range_ref, str) or not range_ref:
        raise SpecSignalCompilerError("opening_range_breakout.range_ref is required")
    range_state = _opening_range_state(context, range_ref)
    tolerance = _atr_tolerance(context, config.get("tolerance"))
    close = context.ohlcv["close"].astype(float)
    long = (range_state["valid"] & (close > (range_state["high"] + tolerance))).fillna(False)
    short = (range_state["valid"] & (close < (range_state["low"] - tolerance))).fillna(False)
    simultaneous = long & short
    long = long & ~simultaneous
    short = short & ~simultaneous
    side_values = np.empty(len(close), dtype=object)
    side_values[:] = None
    bar_index_values = np.full(len(close), math.nan, dtype=float)
    active_session: Any = None
    seen_side: str | None = None
    _, session_keys = _session_membership(context, _range_session_ref(context, range_ref))
    session_values = session_keys.to_numpy(dtype=object)
    long_values = long.to_numpy(dtype=bool)
    short_values = short.to_numpy(dtype=bool)
    for index_number, session_key in enumerate(session_values):
        if session_key != active_session:
            active_session = session_key
            seen_side = None
        if seen_side is None:
            if bool(long_values[index_number]):
                seen_side = "long"
                bar_index_values[index_number] = float(index_number)
            elif bool(short_values[index_number]):
                seen_side = "short"
                bar_index_values[index_number] = float(index_number)
        side_values[index_number] = seen_side
    side = pd.Series(side_values, index=close.index, dtype=object)
    bar_index = pd.Series(bar_index_values, index=close.index, dtype=float)
    context.primitive_cache[("breakout_long", breakout_id)] = long
    context.primitive_cache[("breakout_short", breakout_id)] = short
    context.primitive_cache[("breakout_side", breakout_id)] = side
    context.primitive_cache[("breakout_bar_index", breakout_id)] = bar_index
    return {"long": long, "short": short, "side": side, "bar_index": bar_index}


def _range_session_ref(context: _CompileContext, range_id: str) -> str:
    config = _primitive_by_id(context, OPENING_RANGES_KEY, "range_id").get(range_id)
    if config is None or not isinstance(config.get("session_ref"), str):
        raise SpecSignalCompilerError(f"unknown opening_range ref: {range_id}")
    return str(config["session_ref"])


def _retest_state(context: _CompileContext, retest_id: str) -> dict[str, pd.Series]:
    if ("retest_long", retest_id) in context.primitive_cache:
        return {
            "long": context.primitive_cache[("retest_long", retest_id)],
            "short": context.primitive_cache[("retest_short", retest_id)],
        }
    retests = _primitive_by_id(context, OPENING_RANGE_RETESTS_KEY, "retest_id")
    config = retests.get(retest_id)
    if config is None:
        raise SpecSignalCompilerError(f"unknown opening_range_retest ref: {retest_id}")
    if config.get("touch_price_source") != "close":
        raise SpecSignalCompilerError("opening_range_retest.touch_price_source must be close")
    if config.get("entry_timing") != "next_bar_open_after_retest_confirmation":
        raise SpecSignalCompilerError("opening_range_retest.entry_timing is invalid")
    breakout_ref = config.get("breakout_ref")
    if not isinstance(breakout_ref, str) or not breakout_ref:
        raise SpecSignalCompilerError("opening_range_retest.breakout_ref is required")
    window = config.get("window")
    if not isinstance(window, Mapping):
        raise SpecSignalCompilerError("opening_range_retest.window is required")
    min_after = _resolve_parameter_bound_value(
        window.get("min_bars_after_breakout"),
        context,
        "opening_range_retest.window.min_bars_after_breakout",
    )
    max_after = _resolve_parameter_bound_value(
        window.get("max_bars_after_breakout"),
        context,
        "opening_range_retest.window.max_bars_after_breakout",
    )
    if (
        isinstance(min_after, bool)
        or isinstance(max_after, bool)
        or not isinstance(min_after, Integral)
        or not isinstance(max_after, Integral)
        or min_after < 1
        or max_after < min_after
    ):
        raise SpecSignalCompilerError("opening_range_retest window is invalid")
    breakout_config = _primitive_by_id(context, OPENING_RANGE_BREAKOUTS_KEY, "breakout_id").get(breakout_ref)
    if breakout_config is None:
        raise SpecSignalCompilerError(f"unknown opening_range_breakout ref: {breakout_ref}")
    range_ref = breakout_config.get("range_ref")
    if not isinstance(range_ref, str):
        raise SpecSignalCompilerError("opening_range_breakout.range_ref is required")
    range_state = _opening_range_state(context, range_ref)
    breakout = _breakout_state(context, breakout_ref)
    tolerance = _atr_tolerance(context, config.get("tolerance"))
    close = context.ohlcv["close"].astype(float)
    long_values = np.zeros(len(close), dtype=bool)
    short_values = np.zeros(len(close), dtype=bool)
    _, session_keys = _session_membership(context, _range_session_ref(context, range_ref))
    session_side: str | None = None
    breakout_index: int | None = None
    cancelled = False
    active_session: Any = None
    emitted = False
    session_values = session_keys.to_numpy(dtype=object)
    breakout_long = breakout["long"].to_numpy(dtype=bool)
    breakout_short = breakout["short"].to_numpy(dtype=bool)
    tolerance_values = tolerance.to_numpy(dtype=float)
    close_values = close.to_numpy(dtype=float)
    range_high_values = range_state["high"].to_numpy(dtype=float)
    range_low_values = range_state["low"].to_numpy(dtype=float)
    for index_number, session_key in enumerate(session_values):
        if session_key != active_session:
            active_session = session_key
            session_side = None
            breakout_index = None
            cancelled = False
            emitted = False
        if session_side is None:
            if bool(breakout_long[index_number]):
                session_side = "long"
                breakout_index = index_number
            elif bool(breakout_short[index_number]):
                session_side = "short"
                breakout_index = index_number
            continue
        if emitted or cancelled or breakout_index is None:
            continue
        if session_side == "long" and bool(breakout_short[index_number]):
            cancelled = True
            continue
        if session_side == "short" and bool(breakout_long[index_number]):
            cancelled = True
            continue
        bars_after = index_number - breakout_index
        if bars_after > int(max_after):
            continue
        if bars_after < int(min_after):
            continue
        tolerance_value = tolerance_values[index_number]
        close_value = close_values[index_number]
        if not math.isfinite(tolerance_value) or not math.isfinite(close_value):
            continue
        if session_side == "long" and close_value <= range_high_values[index_number] + tolerance_value:
            long_values[index_number] = True
            emitted = True
        elif session_side == "short" and close_value >= range_low_values[index_number] - tolerance_value:
            short_values[index_number] = True
            emitted = True
    long = pd.Series(long_values, index=close.index, dtype=bool)
    short = pd.Series(short_values, index=close.index, dtype=bool)
    context.primitive_cache[("retest_long", retest_id)] = long
    context.primitive_cache[("retest_short", retest_id)] = short
    return {"long": long, "short": short}


def _candle_shape_state(context: _CompileContext, predicate_id: str) -> dict[str, pd.Series]:
    if ("candle_shape_long", predicate_id) in context.primitive_cache:
        return {
            "long": context.primitive_cache[("candle_shape_long", predicate_id)],
            "short": context.primitive_cache[("candle_shape_short", predicate_id)],
            "value": context.primitive_cache[("candle_shape_value", predicate_id)],
        }
    shapes = _primitive_by_id(context, CANDLE_SHAPES_KEY, "predicate_id")
    config = shapes.get(predicate_id)
    if config is None:
        raise SpecSignalCompilerError(f"unknown candle_shape ref: {predicate_id}")
    if config.get("range_source") != "high_low":
        raise SpecSignalCompilerError("candle_shape.range_source must be high_low")
    if config.get("zero_range_policy") != "false" or config.get("missing_ohlc_policy") != "false":
        raise SpecSignalCompilerError("candle_shape fail-closed policies must be false")
    ohlc = context.ohlcv[["open", "high", "low", "close"]].astype(float)
    candle_range = ohlc["high"] - ohlc["low"]
    finite = ohlc.apply(lambda col: col.map(lambda value: math.isfinite(float(value)))).all(axis=1)
    valid = finite & (candle_range > 0.0)
    upper = (ohlc["high"] - pd.concat([ohlc["open"], ohlc["close"]], axis=1).max(axis=1)) / candle_range
    lower = (pd.concat([ohlc["open"], ohlc["close"]], axis=1).min(axis=1) - ohlc["low"]) / candle_range
    body = (ohlc["close"] - ohlc["open"]).abs() / candle_range
    predicate = valid.copy()
    for key, values in (
        ("upper_wick_pct", upper),
        ("lower_wick_pct", lower),
        ("body_pct", body),
    ):
        if key in config:
            predicate = predicate & _ratio_predicate(values, config.get(key), context, f"candle_shape.{key}")
    predicate = predicate.fillna(False)
    side_mode = config.get("side_mode", "neutral")
    if side_mode == "side_specific":
        long = predicate & (ohlc["close"] > ohlc["open"])
        short = predicate & (ohlc["close"] < ohlc["open"])
    elif side_mode == "neutral":
        long = predicate
        short = predicate
    else:
        raise SpecSignalCompilerError("candle_shape.side_mode must be neutral or side_specific")
    context.primitive_cache[("candle_shape_long", predicate_id)] = long.fillna(False)
    context.primitive_cache[("candle_shape_short", predicate_id)] = short.fillna(False)
    context.primitive_cache[("candle_shape_value", predicate_id)] = predicate.fillna(False)
    return {"long": long.fillna(False), "short": short.fillna(False), "value": predicate.fillna(False)}


def _ratio_predicate(
    values: pd.Series,
    config: Any,
    context: _CompileContext,
    label: str,
) -> pd.Series:
    if not isinstance(config, Mapping):
        raise SpecSignalCompilerError(f"{label} must be an object")
    operator = config.get("operator")
    threshold = _resolve_parameter_bound_value(config.get("value"), context, f"{label}.value")
    if operator not in {"lte", "gte"}:
        raise SpecSignalCompilerError(f"{label}.operator must be lte or gte")
    if isinstance(threshold, bool) or not isinstance(threshold, Real):
        raise SpecSignalCompilerError(f"{label}.value must be numeric")
    threshold_float = float(threshold)
    if not math.isfinite(threshold_float) or threshold_float < 0.0 or threshold_float > 1.0:
        raise SpecSignalCompilerError(f"{label}.value must be in [0, 1]")
    if config.get("units") != "fraction_of_range":
        raise SpecSignalCompilerError(f"{label}.units must be fraction_of_range")
    if operator == "lte":
        return values <= threshold_float
    return values >= threshold_float


def _resolve_primitive_ref(operand: Mapping[str, Any], context: _CompileContext) -> pd.Series:
    ref = operand.get("ref")
    field = operand.get("field")
    if not isinstance(ref, str) or not ref:
        raise SpecSignalCompilerError("primitive_ref.ref must be non-empty")
    if not isinstance(field, str) or not field:
        raise SpecSignalCompilerError("primitive_ref.field must be non-empty")
    if operand.get("timeframe") not in (None, "") or operand.get("lookback") is not None:
        raise SpecSignalCompilerError("primitive_ref does not support timeframe or lookback")
    if ref in _session_windows(context):
        in_session, _ = _session_membership(context, ref)
        if field != "in_session":
            raise SpecSignalCompilerError("session_window primitive_ref.field must be in_session")
        return in_session
    if ref in _primitive_by_id(context, OPENING_RANGES_KEY, "range_id"):
        state = _opening_range_state(context, ref)
        if field not in state:
            raise SpecSignalCompilerError("opening_range primitive_ref.field is invalid")
        return state[field]
    if ref in _primitive_by_id(context, OPENING_RANGE_BREAKOUTS_KEY, "breakout_id"):
        state = _breakout_state(context, ref)
        if field not in {"long", "short"}:
            raise SpecSignalCompilerError("opening_range_breakout primitive_ref.field must be long or short")
        return state[field]
    if ref in _primitive_by_id(context, OPENING_RANGE_RETESTS_KEY, "retest_id"):
        state = _retest_state(context, ref)
        if field not in {"long", "short"}:
            raise SpecSignalCompilerError("opening_range_retest primitive_ref.field must be long or short")
        return state[field]
    if ref in _primitive_by_id(context, CANDLE_SHAPES_KEY, "predicate_id"):
        state = _candle_shape_state(context, ref)
        if field not in {"long", "short", "value"}:
            raise SpecSignalCompilerError("candle_shape primitive_ref.field must be long, short, or value")
        return state[field]
    raise SpecSignalCompilerError(f"unknown primitive_ref: {ref}")


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
    if operand_type == PRIMITIVE_REF_OPERAND_TYPE:
        return _resolve_primitive_ref(operand, context)
    if operand_type == COMPOSED_OPERAND_TYPE:
        return _resolve_composed_operand(operand, context)
    raise SpecSignalCompilerError(f"unknown operand_type: {operand_type!r}")


def _resolve_composed_operand(operand: Mapping[str, Any], context: _CompileContext) -> Any:
    composition_type = operand.get("composition_type")
    if composition_type not in COMPOSITION_TYPES:
        raise UnsupportedSpecSignalCompilerFeature(
            f"unsupported composition_type: {composition_type!r}"
        )
    if composition_type == COMPOSITION_TYPE_Z_SCORE:
        return _resolve_z_score_composed_operand(operand, context)

    expected_keys = {
        "operand_type",
        "composition_type",
        "base_operand",
        "parameter_operand",
    }
    if set(operand) != expected_keys:
        raise SpecSignalCompilerError("composed_operand has invalid properties")

    base_operand = operand.get("base_operand")
    parameter_operand = operand.get("parameter_operand")
    if not isinstance(base_operand, Mapping):
        raise SpecSignalCompilerError("composed_operand.base_operand must be an object")
    if not isinstance(parameter_operand, Mapping):
        raise SpecSignalCompilerError("composed_operand.parameter_operand must be an object")

    base_type = base_operand.get("operand_type")
    parameter_type = parameter_operand.get("operand_type")
    if base_type == COMPOSED_OPERAND_TYPE or parameter_type == COMPOSED_OPERAND_TYPE:
        raise UnsupportedSpecSignalCompilerFeature("nested composed_operand is not supported")
    if base_type not in COMPOSED_BASE_OPERAND_TYPES:
        raise UnsupportedSpecSignalCompilerFeature(
            f"composed_operand base_operand.operand_type must be one of "
            f"{sorted(COMPOSED_BASE_OPERAND_TYPES)}"
        )
    if parameter_type != COMPOSED_PARAMETER_OPERAND_TYPE:
        raise UnsupportedSpecSignalCompilerFeature(
            "composed_operand parameter_operand.operand_type must be 'parameter_ref'"
        )

    base_value = _resolve_operand(base_operand, context)
    parameter_value = _resolve_operand(parameter_operand, context)
    if not isinstance(parameter_value, Real) or isinstance(parameter_value, bool):
        raise SpecSignalCompilerError("composed_operand parameter value must be numeric")
    parameter_float = float(parameter_value)
    if not math.isfinite(parameter_float) or not (0.0 < parameter_float < 1.0):
        raise SpecSignalCompilerError("composed_operand parameter value must be in (0, 1)")
    if composition_type == COMPOSITION_TYPE_SCALE_BY_ONE_MINUS_PARAMETER:
        return base_value * (1.0 - parameter_float)
    if composition_type == COMPOSITION_TYPE_SCALE_BY_ONE_PLUS_PARAMETER:
        return base_value * (1.0 + parameter_float)
    raise SpecSignalCompilerError(f"unhandled composition_type: {composition_type!r}")


def _resolve_z_score_composed_operand(operand: Mapping[str, Any], context: _CompileContext) -> pd.Series:
    expected_keys = {
        "operand_type",
        "composition_type",
        "value_operand",
        "center_operand",
        "scale_operand",
        "zero_scale_policy",
    }
    if set(operand) != expected_keys:
        raise SpecSignalCompilerError("composed_operand has invalid properties")
    if operand.get("zero_scale_policy") != Z_SCORE_ZERO_SCALE_POLICY:
        raise SpecSignalCompilerError(
            f"z_score zero_scale_policy must be {Z_SCORE_ZERO_SCALE_POLICY!r}"
        )

    resolved: dict[str, pd.Series] = {}
    for operand_key in ("value_operand", "center_operand", "scale_operand"):
        child_operand = operand.get(operand_key)
        if not isinstance(child_operand, Mapping):
            raise SpecSignalCompilerError(f"z_score {operand_key} must be an object")
        child_type = child_operand.get("operand_type")
        if child_type == COMPOSED_OPERAND_TYPE:
            raise UnsupportedSpecSignalCompilerFeature("nested composed_operand is not supported")
        if child_type not in Z_SCORE_OPERAND_TYPES:
            raise UnsupportedSpecSignalCompilerFeature(
                f"z_score {operand_key}.operand_type must be one of {sorted(Z_SCORE_OPERAND_TYPES)}"
            )
        child_value = _resolve_operand(child_operand, context)
        if not isinstance(child_value, pd.Series):
            raise SpecSignalCompilerError(f"z_score {operand_key} must resolve to a numeric series")
        resolved[operand_key] = child_value.astype(float)

    scale = resolved["scale_operand"]
    result = (resolved["value_operand"] - resolved["center_operand"]) / scale
    return result.mask(scale.isna() | (scale == 0.0))


def _resolve_data_ref(operand: Mapping[str, Any], ohlcv: pd.DataFrame) -> pd.Series:
    lookback = operand.get("lookback")
    if isinstance(lookback, Mapping) and LOOKBACK_PARAMETER_REF_KEY in lookback:
        raise UnsupportedSpecSignalCompilerFeature(
            "bars_parameter_ref is only supported for indicator_ref.lookback"
        )
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
    timeframe = operand.get("timeframe")
    if timeframe not in (None, ""):
        raise UnsupportedSpecSignalCompilerFeature("indicator_ref timeframe resampling is not supported")
    lookback_bars = _resolve_indicator_lookback_bars(operand, context.variant_assignment)

    builtin_key = context.catalog_entries[str(indicator_id)]["implementation_binding"]["builtin_key"]
    cache_key = (str(indicator_id), lookback_bars, builtin_key)
    if cache_key not in context.indicator_cache:
        if builtin_key == "sma_v1":
            result: pd.Series | dict[str, pd.Series] = _sma_v1(context.ohlcv["close"], lookback_bars)
        elif builtin_key == "ema_v1":
            result = _ema_v1(context.ohlcv["close"], lookback_bars)
        elif builtin_key == "atr_v1":
            result = _atr_v1(context.ohlcv, lookback_bars)
        elif builtin_key == "stddev_v1":
            result = _stddev_v1(context.ohlcv["close"], lookback_bars, ddof=0)
        elif builtin_key == "rsi_v1":
            result = _rsi_v1(context.ohlcv["close"], lookback_bars)
        elif builtin_key == "donchian_v1":
            result = _donchian_v1(context.ohlcv, lookback_bars)
        elif builtin_key == "ma_distance_v1":
            result = _ma_distance_v1(context.ohlcv["close"], lookback_bars)
        elif builtin_key == "rvol_v1":
            result = _rvol_v1(context.ohlcv["volume"], lookback_bars)
        elif builtin_key == "rolling_vwap_v1":
            result = _rolling_vwap_v1(context.ohlcv, lookback_bars)
        else:
            raise SpecSignalCompilerError(f"unknown builtin key: {builtin_key!r}")
        context.indicator_cache[cache_key] = result

    cached = context.indicator_cache[cache_key]
    if isinstance(cached, pd.Series):
        if output_field not in (None, "", "value"):
            raise SpecSignalCompilerError(f"unsupported indicator output field: {output_field!r}")
        return cached

    if output_field in (None, "", "value"):
        raise SpecSignalCompilerError(f"indicator_ref {indicator_id!r} requires an explicit output field")
    if output_field not in cached:
        raise SpecSignalCompilerError(f"unsupported indicator output field: {output_field!r}")
    return cached[str(output_field)]


def _resolve_indicator_lookback_bars(
    operand: Mapping[str, Any],
    variant_assignment: Mapping[str, Any],
) -> int:
    lookback = operand.get("lookback")
    if not isinstance(lookback, Mapping):
        raise UnsupportedSpecSignalCompilerFeature(
            "indicator lookback must be literal bars or bars_parameter_ref"
        )
    if set(lookback) == {"bars"}:
        lookback_bars = lookback["bars"]
        if not isinstance(lookback_bars, int) or isinstance(lookback_bars, bool):
            raise SpecSignalCompilerError("indicator lookback.bars must be an integer >= 1")
        if lookback_bars < 1:
            raise SpecSignalCompilerError("indicator lookback.bars must be >= 1")
        return lookback_bars
    if set(lookback) == {LOOKBACK_PARAMETER_REF_KEY}:
        parameter_name = lookback[LOOKBACK_PARAMETER_REF_KEY]
        if not isinstance(parameter_name, str) or not parameter_name:
            raise SpecSignalCompilerError("indicator lookback.bars_parameter_ref must be a non-empty string")
        parameter_values = variant_assignment.get("parameter_values")
        if not isinstance(parameter_values, Mapping):
            raise SpecSignalCompilerError("variant_assignment.parameter_values must be an object")
        if parameter_name not in parameter_values:
            raise SpecSignalCompilerError(f"missing required lookback parameter_ref: {parameter_name}")
        lookback_bars = parameter_values[parameter_name]
        if not isinstance(lookback_bars, int) or isinstance(lookback_bars, bool):
            raise SpecSignalCompilerError(
                f"lookback parameter {parameter_name!r} must resolve to an integer >= 1"
            )
        if lookback_bars < 1:
            raise SpecSignalCompilerError(
                f"lookback parameter {parameter_name!r} must resolve to an integer >= 1"
            )
        return lookback_bars
    raise UnsupportedSpecSignalCompilerFeature(
        "indicator lookback must use exactly one of bars or bars_parameter_ref"
    )


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


def _resolve_parameter_bound_value(
    value: Any,
    context: _CompileContext,
    label: str,
) -> Any:
    if not isinstance(value, Mapping):
        return value
    if set(value) != {VALUE_PARAMETER_REF_KEY}:
        raise SpecSignalCompilerError(f"{label} parameter binding must use only parameter_ref")
    ref = value.get(VALUE_PARAMETER_REF_KEY)
    if not isinstance(ref, str) or not ref:
        raise SpecSignalCompilerError(f"{label}.parameter_ref must be a non-empty string")
    parameter_values = context.variant_assignment.get("parameter_values")
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


def _rsi_value(avg_gain: float, avg_loss: float) -> float:
    if avg_gain == 0.0 and avg_loss == 0.0:
        return 50.0
    if avg_loss == 0.0:
        return 100.0
    if avg_gain == 0.0:
        return 0.0
    relative_strength = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + relative_strength))


def _rsi_v1(series: pd.Series, lookback_bars: int) -> pd.Series:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("rsi_v1 lookback_bars must be >= 1")
    source = series.astype(float)
    result = pd.Series(math.nan, index=series.index, dtype=float)
    if len(source) <= lookback_bars:
        return result

    index = 0
    while index < len(source):
        while index < len(source) and pd.isna(source.iloc[index]):
            index += 1
        segment_start = index
        while index < len(source) and not pd.isna(source.iloc[index]):
            index += 1
        segment_end = index
        if segment_end - segment_start <= lookback_bars:
            continue

        close_values = source.iloc[segment_start:segment_end].to_numpy(dtype=float)
        deltas = np.diff(close_values)
        gains = np.where(deltas > 0.0, deltas, 0.0)
        losses = np.where(deltas < 0.0, -deltas, 0.0)
        avg_gain = float(np.mean(gains[:lookback_bars]))
        avg_loss = float(np.mean(losses[:lookback_bars]))
        output_index = segment_start + lookback_bars
        result.iloc[output_index] = _rsi_value(avg_gain, avg_loss)

        for offset in range(lookback_bars, len(deltas)):
            avg_gain = ((avg_gain * (lookback_bars - 1)) + float(gains[offset])) / lookback_bars
            avg_loss = ((avg_loss * (lookback_bars - 1)) + float(losses[offset])) / lookback_bars
            result.iloc[segment_start + offset + 1] = _rsi_value(avg_gain, avg_loss)
    return result


def _donchian_v1(ohlcv: pd.DataFrame, lookback_bars: int) -> dict[str, pd.Series]:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("donchian_v1 lookback_bars must be >= 1")
    upper = ohlcv["high"].astype(float).rolling(lookback_bars, min_periods=lookback_bars).max()
    lower = ohlcv["low"].astype(float).rolling(lookback_bars, min_periods=lookback_bars).min()
    mid = (upper + lower) / 2.0
    width = upper - lower
    return {
        "upper": upper,
        "lower": lower,
        "mid": mid,
        "width": width,
        "upper_lag1": upper.shift(1),
        "lower_lag1": lower.shift(1),
        "mid_lag1": mid.shift(1),
        "width_lag1": width.shift(1),
    }


def _ma_distance_v1(series: pd.Series, lookback_bars: int) -> dict[str, pd.Series]:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("ma_distance_v1 lookback_bars must be >= 1")
    price = series.astype(float)
    ma = _sma_v1(price, lookback_bars)
    distance_abs = price - ma
    distance_ratio = distance_abs / ma
    distance_ratio = distance_ratio.mask(ma.isna() | (ma == 0.0))
    distance_pct = distance_ratio * 100.0
    return {
        "distance_abs": distance_abs,
        "distance_ratio": distance_ratio,
        "distance_pct": distance_pct,
    }


def _rvol_v1(series: pd.Series, lookback_bars: int) -> dict[str, pd.Series]:
    if lookback_bars < 1:
        raise SpecSignalCompilerError("rvol_v1 lookback_bars must be >= 1")
    volume = series.astype(float)
    volume_ma = volume.rolling(lookback_bars, min_periods=lookback_bars).mean()
    rvol = (volume / volume_ma).mask(volume_ma.isna() | (volume_ma == 0.0))
    return {"rvol": rvol, "volume_ma": volume_ma}


def _rolling_vwap_v1(ohlcv: pd.DataFrame, lookback_bars: int) -> dict[str, pd.Series]:
    """Return rolling candle-VWAP; this is not true trade-level VWAP."""
    if lookback_bars < 1:
        raise SpecSignalCompilerError("rolling_vwap_v1 lookback_bars must be >= 1")
    high = ohlcv["high"].astype(float)
    low = ohlcv["low"].astype(float)
    close = ohlcv["close"].astype(float)
    volume = ohlcv["volume"].astype(float)
    typical_price = (high + low + close) / 3.0
    weighted_price = typical_price * volume
    rolling_weighted_price = weighted_price.rolling(
        lookback_bars, min_periods=lookback_bars
    ).sum()
    rolling_volume = volume.rolling(lookback_bars, min_periods=lookback_bars).sum()
    rolling_vwap = (rolling_weighted_price / rolling_volume).mask(
        rolling_volume.isna() | (rolling_volume == 0.0)
    )
    return {"rolling_vwap": rolling_vwap}
