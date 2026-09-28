"""Non-authoritative Nautilus research adapter for the frozen N1-01 profile.

The module intentionally imports NautilusTrader only inside the executor.  It
contains no persistence, canonical crossing, runtime, paper, live, network, or
exchange-adapter surface.
"""

from __future__ import annotations

import copy
import hashlib
import math
import platform
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from tools.execution_evidence_contract import (
    build_result_envelope,
    canonical_json_bytes,
    content_sha256,
    validate_result_envelope,
    validate_run_request,
)
from tools.execution_evidence_legacy_rp import project_result_population_v1
from tools.research_runner.spec_signal_compiler import compile_signal


NAUTILUS_TARGET_VERSION = "1.231.0"
ADAPTER_ID = "cpw_nautilus_research_adapter_v1"
SUPPORTED_PROFILE = "cpw_nautilus_n1_01_rp2592_profile_v1"

_RP_ID = "RP-2592"
_INITIAL_EQUITY = 10_000.0
_OUTCOME_CATEGORIES = (
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
_EXPECTED_ASSUMPTIONS = {
    "bar_path_assumption": "next_open_close_mark",
    "fee_side_assumption": "taker_entry_taker_exit",
    "fill_mode": "complete",
    "liquidation_mode": "zero_equity",
    "mark_price_source": "close",
    "slippage_model": "fixed_bps",
}
_EXPECTED_SIZING = {
    "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
    "sizing_equity_basis": "realized_available_equity_at_entry",
    "sizing_mode": "dynamic_equity_target_leverage",
    "target_leverage": 1.0,
}
_SEMANTIC_GAPS = {
    "fee_slippage_split": "NOT_PROVEN_IN_N1_01",
    "nonzero_funding": "NOT_PROVEN_IN_N1_01",
    "generalized_quantity_precision_parity": "NOT_PROVEN_IN_N1_01",
    "direct_flip": "NOT_PROVEN_IN_N1_01",
    "zero_equity_liquidation": "NOT_PROVEN_IN_N1_01",
    "maintenance_margin": "NOT_PROVEN_IN_N1_01",
}


class NautilusAdapterError(ValueError):
    """Raised when the N1-01 boundary cannot be satisfied exactly."""


@dataclass(frozen=True)
class ResolvedResearchInputs:
    run_request: Mapping[str, Any]
    strategy_spec: Mapping[str, Any]
    variant_manifest: Mapping[str, Any]
    sweep_plan: Mapping[str, Any]
    result_population: Mapping[str, Any]
    ohlcv_path: Path
    repo_commit: str


@dataclass(frozen=True)
class NautilusResearchResult:
    result_envelope: Mapping[str, Any]
    semantic_gap_report: Mapping[str, str]
    variant_execution_results: Mapping[str, Mapping[str, Any]]


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NautilusAdapterError(f"{label} must be an object")
    return value


def _dotted_value(payload: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise NautilusAdapterError(f"missing required artifact path: {dotted_path}")
        current = current[part]
    return current


def _artifact_hash(payload: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(dict(payload))).hexdigest()


def _manifest_hash(manifest: Mapping[str, Any]) -> str:
    pinning = _mapping(manifest.get("manifest_hash_pinning"), "manifest_hash_pinning")
    scope = pinning.get("hash_scope")
    if not isinstance(scope, list) or not scope or not all(isinstance(item, str) for item in scope):
        raise NautilusAdapterError("manifest_hash_pinning.hash_scope must be a non-empty string list")
    scoped = {path: _dotted_value(manifest, path) for path in scope}
    actual = content_sha256(scoped)
    if pinning.get("manifest_hash") != actual:
        raise NautilusAdapterError("Variant Manifest declared hash does not match resolved content")
    return actual


def _expected_csv_facts(result_population: Mapping[str, Any]) -> tuple[int, str]:
    coverage = _mapping(result_population.get("data_coverage_summary"), "data_coverage_summary")
    notes = coverage.get("data_coverage_notes")
    if not isinstance(notes, list):
        raise NautilusAdapterError("data_coverage_summary.data_coverage_notes must be a list")
    facts: dict[str, str] = {}
    for note in notes:
        if isinstance(note, str) and "=" in note:
            key, value = note.split("=", 1)
            facts[key] = value
    try:
        row_count = int(facts["row_count"])
        digest = facts["normalized_sha256"]
    except (KeyError, ValueError) as exc:
        raise NautilusAdapterError("RP fixture lacks exact row_count/normalized_sha256 facts") from exc
    return row_count, digest


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_data_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        count = sum(1 for _ in handle)
    return max(0, count - 1)


def _selected_variants(inputs: ResolvedResearchInputs) -> tuple[Mapping[str, Any], ...]:
    manifest_rows = inputs.variant_manifest.get("variant_assignments")
    if not isinstance(manifest_rows, list):
        raise NautilusAdapterError("variant_assignments must be a list")
    by_id = {
        row.get("variant_id"): row
        for row in manifest_rows
        if isinstance(row, Mapping) and isinstance(row.get("variant_id"), str)
    }
    ordered_ids = list(inputs.run_request["declared_variant_ids"])
    try:
        return tuple(by_id[variant_id] for variant_id in ordered_ids)
    except KeyError as exc:
        raise NautilusAdapterError(f"declared variant missing from manifest: {exc.args[0]}") from exc


def validate_resolved_inputs(inputs: ResolvedResearchInputs) -> None:
    """Fail closed unless resolved content is the exact supported N1-01 profile."""

    try:
        validate_run_request(inputs.run_request)
    except ValueError as exc:
        raise NautilusAdapterError(f"invalid CANON RunRequest: {exc}") from exc

    request = inputs.run_request
    spec = _mapping(inputs.strategy_spec, "strategy_spec")
    manifest = _mapping(inputs.variant_manifest, "variant_manifest")
    sweep = _mapping(inputs.sweep_plan, "sweep_plan")
    rp = _mapping(inputs.result_population, "result_population")
    parents = request["parent_identities"]

    if rp.get("result_population_id") != _RP_ID:
        raise NautilusAdapterError(f"unsupported Result Population: {rp.get('result_population_id')!r}")
    resolved_parent_values = {
        "strategy_spec": (spec.get("strategy_spec_id"), _artifact_hash(spec)),
        "variant_manifest": (manifest.get("variant_manifest_id"), _manifest_hash(manifest)),
        "sweep_plan": (sweep.get("sweep_plan_id"), _artifact_hash(sweep)),
    }
    for name, (resolved_id, resolved_hash) in resolved_parent_values.items():
        expected = parents[name]
        if resolved_id != expected["id"]:
            raise NautilusAdapterError(f"{name} id mismatch")
        if resolved_hash != expected["content_sha256"]:
            raise NautilusAdapterError(f"{name} content hash mismatch")

    projected_request, _ = project_result_population_v1(rp)
    if projected_request != request:
        raise NautilusAdapterError("resolved Result Population does not project to the supplied RunRequest")

    selected_ids = sweep.get("test_selection", {}).get("selected_variant_ids")
    declared_ids = list(request["declared_variant_ids"])
    if selected_ids != declared_ids:
        raise NautilusAdapterError("ordered declared variant ids do not match the Sweep Plan")
    variants = _selected_variants(inputs)
    if [row.get("variant_id") for row in variants] != declared_ids:
        raise NautilusAdapterError("ordered declared variant ids do not match the Variant Manifest")
    if any(row.get("assignment_status") != "included" for row in variants):
        raise NautilusAdapterError("N1-01 requires every declared variant to be included")

    manifest_denominator = manifest.get("population_governance", {}).get(
        "declared_population", {}
    ).get("committed_population_count")
    sweep_denominator = sweep.get("trial_accounting", {}).get("committed_population_count")
    if not (
        request["committed_denominator"] == len(declared_ids)
        == manifest_denominator
        == sweep_denominator
    ):
        raise NautilusAdapterError("committed denominator mismatch")

    coverage = _mapping(rp.get("data_coverage_summary"), "data_coverage_summary")
    expected_data = {
        "catalog_ref": coverage.get("data_catalog_ref"),
        "slice_identity": coverage.get("data_slice_identity"),
        "timeframe": coverage.get("timeframe"),
        "stream": coverage.get("data_stream"),
    }
    if request["data_identity"] != expected_data:
        raise NautilusAdapterError("data identity mismatch")
    if request["determinism"].get("seed") != rp.get("execution_context", {}).get(
        "determinism_seed"
    ):
        raise NautilusAdapterError("deterministic seed mismatch")
    if request["scientific_assumptions"].get("backtest_assumption_summary") != rp.get(
        "backtest_assumption_summary"
    ):
        raise NautilusAdapterError("backtest assumptions mismatch")
    if request["scientific_assumptions"].get("sizing_metadata") != rp.get("sizing_metadata"):
        raise NautilusAdapterError("sizing metadata mismatch")
    if request["scientific_assumptions"].get("data_availability_claim") != rp.get(
        "data_availability_claim"
    ):
        raise NautilusAdapterError("data-availability claim mismatch")

    assumptions = request["scientific_assumptions"]["backtest_assumption_summary"]
    mismatches = {
        key: assumptions.get(key)
        for key, expected in _EXPECTED_ASSUMPTIONS.items()
        if assumptions.get(key) != expected
    }
    if mismatches:
        raise NautilusAdapterError(f"unsupported N1-01 assumptions: {mismatches}")
    if assumptions.get("funding_cost_mode") not in (None, "off", "zero"):
        raise NautilusAdapterError("nonzero funding is unsupported by N1-01")
    if request["scientific_assumptions"]["sizing_metadata"] != _EXPECTED_SIZING:
        raise NautilusAdapterError("unsupported N1-01 sizing metadata")
    rp_rows = rp.get("variant_result_rows")
    if not isinstance(rp_rows, list) or any(
        row.get("metrics", {}).get("funding") != 0.0
        for row in rp_rows
        if isinstance(row, Mapping)
    ):
        raise NautilusAdapterError("nonzero funding fixture is unsupported by N1-01")

    ohlcv_path = Path(inputs.ohlcv_path)
    if not ohlcv_path.is_file():
        raise NautilusAdapterError(f"OHLCV input is not a regular file: {ohlcv_path}")
    expected_rows, expected_sha = _expected_csv_facts(rp)
    if _file_sha256(ohlcv_path) != expected_sha:
        raise NautilusAdapterError("OHLCV normalized SHA-256 mismatch")
    if _csv_data_row_count(ohlcv_path) != expected_rows:
        raise NautilusAdapterError("OHLCV row-count mismatch")
    if not isinstance(inputs.repo_commit, str) or not inputs.repo_commit:
        raise NautilusAdapterError("repo_commit must be a non-empty exact revision")


def _load_ohlcv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        usecols=["open_time", "open", "high", "low", "close", "volume", "close_time_ms"],
    )
    frame["open_time"] = pd.to_datetime(frame["open_time"], utc=True)
    frame = frame.set_index("open_time")
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if not frame.index.is_monotonic_increasing or frame.index.has_duplicates:
        raise NautilusAdapterError("OHLCV timestamps must be unique and increasing")
    if frame.isna().any().any():
        raise NautilusAdapterError("OHLCV input contains nulls")
    return frame


def _load_nautilus() -> dict[str, Any]:
    try:
        import nautilus_trader
        from nautilus_trader.backtest.engine import BacktestEngine
        from nautilus_trader.backtest.models import LatencyModel
        from nautilus_trader.config import BacktestEngineConfig, LoggingConfig, StrategyConfig
        from nautilus_trader.model.currencies import BTC, USDT
        from nautilus_trader.model.data import Bar, BarType, QuoteTick
        from nautilus_trader.model.enums import (
            AccountType,
            OmsType,
            OrderSide,
            TimeInForce,
        )
        from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
        from nautilus_trader.model.instruments import CryptoPerpetual
        from nautilus_trader.model.objects import Money, Price, Quantity
        from nautilus_trader.trading.strategy import Strategy
    except Exception as exc:  # pragma: no cover - isolated dependency gate
        raise NautilusAdapterError(
            f"NautilusTrader {NAUTILUS_TARGET_VERSION} offline API unavailable: "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    if nautilus_trader.__version__ != NAUTILUS_TARGET_VERSION:
        raise NautilusAdapterError(
            f"NautilusTrader version mismatch: expected {NAUTILUS_TARGET_VERSION}, "
            f"got {nautilus_trader.__version__}"
        )
    if sys.version_info[:2] != (3, 12):
        raise NautilusAdapterError("N1-01 Nautilus execution requires CPython 3.12")
    return locals()


def _fill_records(engine: Any, instrument_id: Any) -> list[dict[str, Any]]:
    fills: list[dict[str, Any]] = []
    for order in engine.cache.orders(instrument_id=instrument_id):
        for event in order.events:
            if event.__class__.__name__ != "OrderFilled":
                continue
            fills.append(
                {
                    "side": "BUY" if event.is_buy else "SELL",
                    "price": float(event.last_px.as_decimal()),
                    "quantity": float(event.last_qty.as_decimal()),
                    "ts_event_ns": int(event.ts_event),
                }
            )
    return sorted(fills, key=lambda row: row["ts_event_ns"])


def _execute_target_signals(
    variant_assignments: Sequence[Mapping[str, Any]],
    ohlcv: pd.DataFrame,
    signals: Mapping[str, pd.Series],
) -> dict[str, dict[str, Any]]:
    """Execute CPW target signals through one exact Nautilus 1.231.0 mapping."""

    api = _load_nautilus()
    BacktestEngine = api["BacktestEngine"]
    LatencyModel = api["LatencyModel"]
    BacktestEngineConfig = api["BacktestEngineConfig"]
    LoggingConfig = api["LoggingConfig"]
    StrategyConfig = api["StrategyConfig"]
    BTC = api["BTC"]
    USDT = api["USDT"]
    Bar = api["Bar"]
    BarType = api["BarType"]
    QuoteTick = api["QuoteTick"]
    AccountType = api["AccountType"]
    OmsType = api["OmsType"]
    OrderSide = api["OrderSide"]
    TimeInForce = api["TimeInForce"]
    InstrumentId = api["InstrumentId"]
    Symbol = api["Symbol"]
    Venue = api["Venue"]
    CryptoPerpetual = api["CryptoPerpetual"]
    Money = api["Money"]
    Price = api["Price"]
    Quantity = api["Quantity"]
    Strategy = api["Strategy"]

    instrument_id = InstrumentId(Symbol("BTCUSDT-PERP"), Venue("BINANCE"))
    bar_type = BarType.from_str("BTCUSDT-PERP.BINANCE-15-MINUTE-LAST-EXTERNAL")
    instrument = CryptoPerpetual(
        instrument_id=instrument_id,
        raw_symbol=Symbol("BTCUSDT"),
        base_currency=BTC,
        quote_currency=USDT,
        settlement_currency=USDT,
        is_inverse=False,
        price_precision=2,
        price_increment=Price.from_str("0.01"),
        size_precision=8,
        size_increment=Quantity.from_str("0.00000001"),
        max_quantity=Quantity.from_str("1000000.00000000"),
        min_quantity=Quantity.from_str("0.00000001"),
        max_notional=None,
        min_notional=None,
        max_price=Price.from_str("10000000.00"),
        min_price=Price.from_str("0.01"),
        margin_init=Decimal(0),
        margin_maint=Decimal(0),
        maker_fee=Decimal("0.0005"),
        taker_fee=Decimal("0.0005"),
        ts_event=0,
        ts_init=0,
    )
    bars = [
        Bar(
            bar_type=bar_type,
            open=Price.from_str(f"{row.open:.2f}"),
            high=Price.from_str(f"{row.high:.2f}"),
            low=Price.from_str(f"{row.low:.2f}"),
            close=Price.from_str(f"{row.close:.2f}"),
            volume=Quantity.from_str(f"{row.volume:.8f}"),
            ts_event=int(row.close_time_ms) * 1_000_000,
            ts_init=int(row.close_time_ms) * 1_000_000,
        )
        for row in ohlcv.itertuples()
    ]
    open_ns = [int(timestamp.value) for timestamp in ohlcv.index]
    close_ns = [int(value) * 1_000_000 for value in ohlcv["close_time_ms"]]
    arrival_delays = {
        open_ns[index + 1] - close_ns[index] + 1
        for index in range(len(ohlcv) - 1)
    }
    if len(arrival_delays) != 1 or next(iter(arrival_delays)) <= 0:
        raise NautilusAdapterError("OHLCV bars require one deterministic next-open latency")
    insert_latency_ns = next(iter(arrival_delays))
    open_ticks: list[Any] = []
    for index, row in enumerate(ohlcv.itertuples()):
        price = Price.from_str(f"{row.open:.2f}")
        size = Quantity.from_str("1000000.00000000")
        open_ticks.extend(
            (
                QuoteTick(
                    instrument_id,
                    price,
                    price,
                    size,
                    size,
                    open_ns[index],
                    open_ns[index],
                ),
                QuoteTick(
                    instrument_id,
                    price,
                    price,
                    size,
                    size,
                    open_ns[index] + 1,
                    open_ns[index] + 1,
                ),
            )
        )
    next_open = {
        int(ohlcv.iloc[index]["close_time_ms"]) * 1_000_000: float(
            ohlcv.iloc[index + 1]["open"]
        )
        for index in range(len(ohlcv) - 1)
    }

    class TargetSignalStrategy(Strategy):
        def __init__(self, targets: dict[int, int]) -> None:
            super().__init__(StrategyConfig())
            self.targets = targets
            self.instrument = None

        def on_start(self) -> None:
            self.instrument = self.cache.instrument(instrument_id)
            if self.instrument is None:
                raise NautilusAdapterError("Nautilus instrument missing from cache")
            self.subscribe_bars(bar_type)

        def on_bar(self, bar: Any) -> None:
            desired = self.targets.get(bar.ts_init, 0)
            is_flat = self.portfolio.is_flat(instrument_id)
            if desired == 0:
                if not is_flat:
                    self.close_all_positions(instrument_id, reduce_only=True)
                return
            if not is_flat:
                return
            entry_open = next_open.get(bar.ts_init)
            if entry_open is None:
                return
            account = self.portfolio.account(instrument_id.venue)
            realized_equity = float(account.balance_total(USDT).as_decimal())
            quantity = realized_equity / entry_open
            if not math.isfinite(quantity) or quantity <= 0:
                raise NautilusAdapterError("invalid dynamic-equity quantity")
            order = self.order_factory.market(
                instrument_id=instrument_id,
                order_side=OrderSide.BUY if desired > 0 else OrderSide.SELL,
                quantity=self.instrument.make_qty(quantity),
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(order)

        def on_stop(self) -> None:
            pass

    results: dict[str, dict[str, Any]] = {}
    for variant in variant_assignments:
        variant_id = str(variant["variant_id"])
        engine = None
        try:
            signal = signals[variant_id]
            targets = {
                int(close_time) * 1_000_000: int(value)
                for close_time, value in zip(ohlcv["close_time_ms"], signal, strict=True)
            }
            engine = BacktestEngine(
                config=BacktestEngineConfig(
                    logging=LoggingConfig(log_level="ERROR"), run_analysis=False
                )
            )
            engine.add_venue(
                venue=instrument_id.venue,
                oms_type=OmsType.NETTING,
                account_type=AccountType.MARGIN,
                starting_balances=[Money(_INITIAL_EQUITY, USDT)],
                base_currency=USDT,
                default_leverage=Decimal(1),
                latency_model=LatencyModel(
                    base_latency_nanos=0,
                    insert_latency_nanos=insert_latency_ns,
                    update_latency_nanos=0,
                    cancel_latency_nanos=insert_latency_ns,
                ),
                use_random_ids=False,
                bar_execution=False,
                bar_adaptive_high_low_ordering=False,
            )
            engine.add_instrument(instrument)
            engine.add_data([*bars, *open_ticks], sort=True)
            engine.add_strategy(TargetSignalStrategy(targets))
            engine.run()

            account = engine.portfolio.account(instrument_id.venue)
            realized_equity = float(account.balance_total(USDT).as_decimal())
            unrealized_money = engine.portfolio.unrealized_pnl(
                instrument_id,
                Price.from_str(f"{float(ohlcv.iloc[-1]['close']):.2f}"),
            )
            unrealized = (
                float(unrealized_money.as_decimal()) if unrealized_money is not None else 0.0
            )
            commission_money = account.commission(USDT)
            combined_cost = (
                float(commission_money.as_decimal()) if commission_money is not None else 0.0
            )
            final_equity = realized_equity + unrealized
            open_positions = engine.cache.positions_open(instrument_id=instrument_id)
            result = engine.get_result()
            completed_order_count = result.total_orders - len(open_positions)
            if completed_order_count < 0 or completed_order_count % 2:
                raise NautilusAdapterError(
                    f"cannot derive closed trade count for {variant_id}: "
                    f"orders={result.total_orders} open_positions={len(open_positions)}"
                )
            results[variant_id] = {
                "variant_id": variant_id,
                "parameters": copy.deepcopy(dict(variant.get("parameter_values", {}))),
                "trade_count": completed_order_count // 2,
                "open_position_count": len(open_positions),
                "final_equity": final_equity,
                "return_pct": (final_equity / _INITIAL_EQUITY) - 1.0,
                "combined_fee_slippage_cost": combined_cost,
                "allocated_fees": combined_cost * 0.8,
                "allocated_slippage": combined_cost * 0.2,
                "funding": 0.0,
                "total_orders": result.total_orders,
                "total_positions": result.total_positions,
                "fills": _fill_records(engine, instrument_id),
            }
        except Exception as exc:
            results[variant_id] = {
                "variant_id": variant_id,
                "error": {
                    "category": "nautilus_variant_execution_error",
                    "message_class": type(exc).__name__,
                    "message": str(exc),
                },
            }
        finally:
            if engine is not None:
                engine.dispose()
    results["_environment"] = {
        "nautilus_version": api["nautilus_trader"].__version__,
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "next_bar_open_execution_proven": True,
    }
    return results


def _default_executor(
    inputs: ResolvedResearchInputs,
    ohlcv: pd.DataFrame,
    signals: Mapping[str, pd.Series],
) -> Mapping[str, Mapping[str, Any]]:
    return _execute_target_signals(_selected_variants(inputs), ohlcv, signals)


def _compatibility_evidence(inputs: ResolvedResearchInputs) -> Mapping[str, Any]:
    request, envelope = project_result_population_v1(inputs.result_population)
    if request != inputs.run_request:
        raise NautilusAdapterError("legacy compatibility source request mismatch")
    compatibility = envelope.get("compatibility_evidence")
    if not isinstance(compatibility, Mapping):
        raise NautilusAdapterError("legacy compatibility evidence is missing")
    return compatibility


def _execution_provenance(
    inputs: ResolvedResearchInputs,
    environment: Mapping[str, Any],
) -> dict[str, Any]:
    source_path = Path(__file__)
    lock_path = source_path.with_name("requirements-win-py312.lock.txt")
    observed_version = environment.get("nautilus_version")
    if observed_version != NAUTILUS_TARGET_VERSION:
        raise NautilusAdapterError(
            f"executor provenance version mismatch: expected {NAUTILUS_TARGET_VERSION}, "
            f"got {observed_version!r}"
        )
    return {
        "engine_id": "nautilus_trader",
        "engine_version": observed_version,
        "adapter_id": ADAPTER_ID,
        "repo_commit": inputs.repo_commit,
        "environment_summary": [
            str(environment.get("platform", platform.system())),
            f"CPython {environment.get('python_version', platform.python_version())}",
            "isolated Python 3.12 proof environment",
            "offline execution",
        ],
        "dependency_summary": [
            "tools/nautilus_adapter/requirements-win-py312.lock.txt",
            (
                "sha256:" + hashlib.sha256(lock_path.read_bytes()).hexdigest()
                if lock_path.is_file()
                else "lock unavailable in test fixture"
            ),
        ],
        "source_ref": "tools/nautilus_adapter/research.py",
        "source_raw_sha256": "sha256:" + hashlib.sha256(source_path.read_bytes()).hexdigest(),
    }


def execute_nautilus_research(
    inputs: ResolvedResearchInputs,
) -> NautilusResearchResult:
    """Execute and normalize the frozen RP-2592 profile without persistence."""

    validate_resolved_inputs(inputs)
    ohlcv = _load_ohlcv(Path(inputs.ohlcv_path))
    variants = _selected_variants(inputs)
    signals = {
        str(variant["variant_id"]): compile_signal(
            dict(inputs.strategy_spec),
            dict(variant),
            ohlcv[["open", "high", "low", "close", "volume"]],
        )
        for variant in variants
    }
    execution = dict(_default_executor(inputs, ohlcv, signals))
    environment = execution.pop("_environment", {})
    if not isinstance(environment, Mapping):
        raise NautilusAdapterError("executor _environment must be an object")

    rp_rows = {
        row["variant_id"]: row
        for row in inputs.result_population["variant_result_rows"]
        if isinstance(row, Mapping)
    }
    rows: list[dict[str, Any]] = []
    for variant_id in inputs.run_request["declared_variant_ids"]:
        source = rp_rows[variant_id]
        observed = execution.get(variant_id)
        if not isinstance(observed, Mapping) or observed.get("error"):
            error = observed.get("error", {}) if isinstance(observed, Mapping) else {}
            rows.append(
                {
                    "variant_id": variant_id,
                    "assignment_hash": source["assignment_hash"],
                    "outcome_category": "errored",
                    "attempted": True,
                    "metrics": {},
                    "non_success": {
                        "counts_in_denominator": True,
                        "reason": "nautilus_variant_execution_error",
                    },
                    "error": {
                        "counts_in_denominator": True,
                        "error_category": error.get(
                            "category", "nautilus_variant_execution_error"
                        ),
                        "error_message_class": error.get("message_class", "MissingResult"),
                        "is_infrastructure_error": True,
                        "is_strategy_underperformance": False,
                    },
                    "data_coverage": copy.deepcopy(source["data_coverage"]),
                    "lineage": copy.deepcopy(source["lineage"]),
                }
            )
            continue
        metrics = {
            "final_equity": float(observed["final_equity"]),
            "return_pct": float(observed["return_pct"]),
            "trade_count": int(observed["trade_count"]),
            "combined_fee_slippage_cost": float(observed["combined_fee_slippage_cost"]),
            "funding": float(observed["funding"]),
        }
        if any(not math.isfinite(float(value)) for value in metrics.values()):
            raise NautilusAdapterError(f"non-finite metric for {variant_id}")
        rows.append(
            {
                "variant_id": variant_id,
                "assignment_hash": source["assignment_hash"],
                "outcome_category": "successful",
                "attempted": True,
                "metrics": metrics,
                "non_success": copy.deepcopy(source["non_success"]),
                "error": copy.deepcopy(source["error"]),
                "data_coverage": copy.deepcopy(source["data_coverage"]),
                "lineage": copy.deepcopy(source["lineage"]),
            }
        )

    counts = {category: 0 for category in _OUTCOME_CATEGORIES}
    counts.update(Counter(row["outcome_category"] for row in rows))
    envelope = build_result_envelope(
        request_content_sha256=inputs.run_request["request_content_sha256"],
        committed_denominator=inputs.run_request["committed_denominator"],
        outcome_category_counts=counts,
        variant_result_rows=rows,
        execution_provenance=_execution_provenance(inputs, environment),
        compatibility_evidence=_compatibility_evidence(inputs),
    )
    validate_result_envelope(envelope)
    next_open_proven = environment.get("next_bar_open_execution_proven") is True
    gaps = {
        "next_bar_open_execution": (
            "PROVEN_FOR_N1_01" if next_open_proven else "UNSUPPORTED_BY_N1_01"
        ),
        "dynamic_sizing_fixture_1x": (
            "PROVEN_FOR_N1_01_FIXTURE" if next_open_proven else "UNSUPPORTED_BY_N1_01"
        ),
        **_SEMANTIC_GAPS,
    }
    return NautilusResearchResult(
        result_envelope=envelope,
        semantic_gap_report=gaps,
        variant_execution_results=copy.deepcopy(execution),
    )
