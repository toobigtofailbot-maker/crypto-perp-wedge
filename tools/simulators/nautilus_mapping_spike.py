"""Bounded, non-canonical NautilusTrader mapping spike for RP-2592.

This module reads the frozen 0004 fixture chain, compiles its signals through the
repo's read-only signal compiler, and passes those target positions to an
isolated NautilusTrader offline backtest. It does not modify or replace the
canonical runner/backtester.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from tools.research_runner.spec_signal_compiler import compile_signal


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01"
DEFAULT_SPEC = REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"
DEFAULT_MANIFEST = REPO_ROOT / "research/variant_manifests/VM-0004.variant_manifest.json"
DEFAULT_SWEEP = REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"
DEFAULT_RP = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_CATALOG = (
    REPO_ROOT
    / "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID

LABELS = [
    "NON-CANONICAL NAUTILUS MAPPING SPIKE",
    "NOT CANONICAL EVIDENCE",
    "NOT RUNNER REPLACEMENT",
    "NOT PAPER/LIVE/RUNTIME AUTHORITY",
    (
        "CANONICAL USE REQUIRES SEPARATE MAPPING, VALIDATION, DETERMINISM, "
        "AUDITABILITY, PROVENANCE, AND MAIN APPROVAL"
    ),
]


class MappingSpikeError(RuntimeError):
    """Raised when the bounded mapping cannot safely continue."""


@dataclass(frozen=True)
class Fixture:
    spec: dict[str, Any]
    manifest: dict[str, Any]
    sweep: dict[str, Any]
    rp: dict[str, Any]
    catalog: dict[str, Any]
    variants: tuple[dict[str, Any], ...]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MappingSpikeError(f"expected JSON object: {path}")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _payload_checksum(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _portable(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def load_fixture(
    *,
    spec_path: Path = DEFAULT_SPEC,
    manifest_path: Path = DEFAULT_MANIFEST,
    sweep_path: Path = DEFAULT_SWEEP,
    rp_path: Path = DEFAULT_RP,
    catalog_path: Path = DEFAULT_CATALOG,
) -> Fixture:
    spec = _load_json(spec_path)
    manifest = _load_json(manifest_path)
    sweep = _load_json(sweep_path)
    rp = _load_json(rp_path)
    catalog = _load_json(catalog_path)

    expected = {
        "strategy_spec_id": spec.get("strategy_spec_id"),
        "variant_manifest_id": manifest.get("variant_manifest_id"),
        "sweep_plan_id": sweep.get("sweep_plan_id"),
    }
    observed = {
        key: rp.get("lineage", {}).get(key)
        for key in ("strategy_spec_id", "variant_manifest_id", "sweep_plan_id")
    }
    if observed != expected:
        raise MappingSpikeError(f"fixture lineage mismatch: {observed=} {expected=}")

    selected = set(sweep.get("test_selection", {}).get("selected_variant_ids", []))
    variants = tuple(
        sorted(
            (
                row
                for row in manifest.get("variant_assignments", [])
                if row.get("assignment_status") == "included" and row.get("variant_id") in selected
            ),
            key=lambda row: row["variant_id"],
        )
    )
    rp_rows = rp.get("variant_result_rows", [])
    if not variants or len(variants) != len(rp_rows):
        raise MappingSpikeError("selected variants do not match RP-2592 result rows")
    if [row["variant_id"] for row in variants] != sorted(row["variant_id"] for row in rp_rows):
        raise MappingSpikeError("variant ids do not match RP-2592")

    assumptions = rp.get("backtest_assumption_summary", {})
    required = {
        "bar_path_assumption": "next_open_close_mark",
        "fee_side_assumption": "taker_entry_taker_exit",
        "fill_mode": "complete",
        "liquidation_mode": "zero_equity",
        "mark_price_source": "close",
        "slippage_model": "fixed_bps",
    }
    mismatches = {key: assumptions.get(key) for key, value in required.items() if assumptions.get(key) != value}
    if mismatches:
        raise MappingSpikeError(f"unsupported fixture assumptions: {mismatches}")
    sizing = rp.get("sizing_metadata", {})
    if sizing != {
        "entry_reference_price_basis": "next_bar_open_pre_fee_slippage",
        "sizing_equity_basis": "realized_available_equity_at_entry",
        "sizing_mode": "dynamic_equity_target_leverage",
        "target_leverage": 1.0,
    }:
        raise MappingSpikeError(f"unsupported sizing metadata: {sizing}")
    return Fixture(spec, manifest, sweep, rp, catalog, variants)


def load_ohlcv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise MappingSpikeError(f"OHLCV input does not exist: {path}")
    frame = pd.read_csv(
        path,
        usecols=["open_time", "open", "high", "low", "close", "volume", "close_time_ms"],
    )
    frame["open_time"] = pd.to_datetime(frame["open_time"], utc=True)
    frame = frame.set_index("open_time")
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if not frame.index.is_monotonic_increasing or frame.index.has_duplicates:
        raise MappingSpikeError("OHLCV timestamps must be unique and increasing")
    if frame.isna().any().any():
        raise MappingSpikeError("OHLCV input contains nulls")
    return frame


def _coverage_fact(*, fixture_value: str | None, notes: tuple[str, ...] | list[str]) -> int | None:
    prefix = f"{fixture_value}=" if fixture_value else "row_count="
    for note in notes:
        if note.startswith(prefix):
            return int(note.split("=", 1)[1])
    return None


def _rp_rows(fixture: Fixture) -> dict[str, dict[str, Any]]:
    return {row["variant_id"]: row for row in fixture.rp["variant_result_rows"]}


def _compile_signals(fixture: Fixture, ohlcv: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        variant["variant_id"]: compile_signal(
            fixture.spec,
            variant,
            ohlcv[["open", "high", "low", "close", "volume"]],
        )
        for variant in fixture.variants
    }


def _run_nautilus_variants(
    fixture: Fixture,
    ohlcv: pd.DataFrame,
    signals: dict[str, pd.Series],
) -> dict[str, dict[str, Any]]:
    """Import Nautilus lazily so repo tests need no optional dependency."""
    try:
        import nautilus_trader
        from nautilus_trader.backtest.engine import BacktestEngine
        from nautilus_trader.config import BacktestEngineConfig, LoggingConfig, StrategyConfig
        from nautilus_trader.model.currencies import BTC, USDT
        from nautilus_trader.model.data import Bar, BarType
        from nautilus_trader.model.enums import AccountType, OmsType, OrderSide, TimeInForce
        from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
        from nautilus_trader.model.instruments import CryptoPerpetual
        from nautilus_trader.model.objects import Money, Price, Quantity
        from nautilus_trader.trading.strategy import Strategy
    except Exception as exc:  # pragma: no cover - exercised by the isolated command
        raise MappingSpikeError(f"NautilusTrader offline API unavailable: {type(exc).__name__}: {exc}") from exc

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
    next_open = {
        int(ohlcv.iloc[index]["close_time_ms"]) * 1_000_000: float(ohlcv.iloc[index + 1]["open"])
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
                raise MappingSpikeError("Nautilus instrument missing from cache")
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
                return
            order = self.order_factory.market(
                instrument_id=instrument_id,
                order_side=OrderSide.BUY if desired > 0 else OrderSide.SELL,
                quantity=self.instrument.make_qty(quantity),
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(order)

        def on_stop(self) -> None:
            # Canonical RP marks an open final position; it does not force an end fill.
            pass

    results: dict[str, dict[str, Any]] = {}
    for variant in fixture.variants:
        variant_id = variant["variant_id"]
        signal = signals[variant_id]
        targets = {
            int(close_time) * 1_000_000: int(value)
            for close_time, value in zip(ohlcv["close_time_ms"], signal, strict=True)
        }
        engine = BacktestEngine(
            config=BacktestEngineConfig(logging=LoggingConfig(log_level="ERROR"), run_analysis=False)
        )
        engine.add_venue(
            venue=instrument_id.venue,
            oms_type=OmsType.NETTING,
            account_type=AccountType.MARGIN,
            starting_balances=[Money(10_000, USDT)],
            base_currency=USDT,
            default_leverage=Decimal(1),
            use_random_ids=False,
            bar_execution=True,
            bar_adaptive_high_low_ordering=False,
        )
        engine.add_instrument(instrument)
        engine.add_data(bars, sort=False)
        engine.add_strategy(TargetSignalStrategy(targets))
        engine.run()

        account = engine.portfolio.account(instrument_id.venue)
        realized_equity = float(account.balance_total(USDT).as_decimal())
        unrealized_money = engine.portfolio.unrealized_pnl(
            instrument_id,
            Price.from_str(f"{float(ohlcv.iloc[-1]['close']):.2f}"),
        )
        unrealized = float(unrealized_money.as_decimal()) if unrealized_money is not None else 0.0
        commission_money = account.commission(USDT)
        combined_cost = float(commission_money.as_decimal()) if commission_money is not None else 0.0
        final_equity = realized_equity + unrealized
        closed_positions = engine.cache.positions_closed(instrument_id=instrument_id)
        open_positions = engine.cache.positions_open(instrument_id=instrument_id)
        result = engine.get_result()
        completed_order_count = result.total_orders - len(open_positions)
        if completed_order_count < 0 or completed_order_count % 2:
            raise MappingSpikeError(
                f"cannot derive closed trade count for {variant_id}: "
                f"orders={result.total_orders} open_positions={len(open_positions)}"
            )
        results[variant_id] = {
            "variant_id": variant_id,
            "parameters": variant["parameter_values"],
            # NETTING retains one reusable Position object. Each canonical closed
            # trade is an entry/exit market-order pair; a final open position
            # contributes its one unmatched entry order.
            "trade_count": completed_order_count // 2,
            "nautilus_closed_position_objects": len(closed_positions),
            "open_position_count": len(open_positions),
            "final_equity": final_equity,
            "return_pct": (final_equity / 10_000.0) - 1.0,
            "combined_fee_slippage_cost": combined_cost,
            "allocated_fees": combined_cost * 0.8,
            "allocated_slippage": combined_cost * 0.2,
            "funding": 0.0,
            "total_orders": result.total_orders,
            "total_positions": result.total_positions,
        }
        engine.dispose()
    results["_environment"] = {
        "nautilus_version": nautilus_trader.__version__,
        "python_version": platform.python_version(),
        "platform": platform.system(),
    }
    return results


def _normalize_run(run: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return json.loads(json.dumps(run, sort_keys=True))


def _comparison(fixture: Fixture, run: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rp_rows = _rp_rows(fixture)
    comparisons = []
    for variant in fixture.variants:
        variant_id = variant["variant_id"]
        observed = run[variant_id]
        expected = rp_rows[variant_id]["metrics"]
        comparisons.append(
            {
                "variant_id": variant_id,
                "rp": {
                    key: expected[key]
                    for key in ("trade_count", "return_pct", "fees", "slippage", "funding")
                },
                "nautilus": {
                    key: observed[key]
                    for key in (
                        "trade_count",
                        "return_pct",
                        "allocated_fees",
                        "allocated_slippage",
                        "funding",
                        "final_equity",
                    )
                },
                "delta": {
                    "trade_count": observed["trade_count"] - expected["trade_count"],
                    "return_pct": observed["return_pct"] - expected["return_pct"],
                    "fees": observed["allocated_fees"] - expected["fees"],
                    "slippage": observed["allocated_slippage"] - expected["slippage"],
                },
            }
        )
    return comparisons


def _reconciliation_summary(comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    max_abs_return_delta = max(abs(row["delta"]["return_pct"]) for row in comparisons)
    exact_trade_counts = all(row["delta"]["trade_count"] == 0 for row in comparisons)
    # This is a bounded spike tolerance, not a canonical acceptance threshold.
    return {
        "exact_trade_counts": exact_trade_counts,
        "max_abs_return_delta": max_abs_return_delta,
        "bounded_spike_return_tolerance": 0.005,
        "sufficient_for_candidate_label": exact_trade_counts and max_abs_return_delta <= 0.005,
        "not_canonical_acceptance_threshold": True,
    }


def build_report(
    *,
    fixture: Fixture,
    ohlcv_path: Path,
    executor: Callable[[Fixture, pd.DataFrame, dict[str, pd.Series]], dict[str, dict[str, Any]]] = _run_nautilus_variants,
) -> dict[str, Any]:
    ohlcv = load_ohlcv(ohlcv_path)
    coverage = fixture.rp["data_coverage_summary"]
    notes = coverage.get("data_coverage_notes", [])
    expected_rows = _coverage_fact(fixture_value="row_count", notes=notes)
    if expected_rows != len(ohlcv):
        raise MappingSpikeError(f"OHLCV row count mismatch: observed={len(ohlcv)} expected={expected_rows}")
    expected_sha = next(
        (note.split("=", 1)[1] for note in notes if note.startswith("normalized_sha256=")),
        None,
    )
    observed_sha = _sha256_file(ohlcv_path)
    if expected_sha != observed_sha:
        raise MappingSpikeError(f"OHLCV checksum mismatch: observed={observed_sha} expected={expected_sha}")

    signals = _compile_signals(fixture, ohlcv)
    run_1 = _normalize_run(executor(fixture, ohlcv, signals))
    run_2 = _normalize_run(executor(fixture, ohlcv, signals))
    checksum_1 = _payload_checksum(run_1)
    checksum_2 = _payload_checksum(run_2)
    deterministic = checksum_1 == checksum_2 and run_1 == run_2
    comparisons = _comparison(fixture, run_1)
    reconciliation_summary = _reconciliation_summary(comparisons)
    decision = (
        "VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE"
        if deterministic and reconciliation_summary["sufficient_for_candidate_label"]
        else "INFEASIBLE_FOR_NOW"
    )

    report = {
        "labels": LABELS,
        "package_id": PACKAGE_ID,
        "decision_label": decision,
        "fixture": {
            "result_population_id": fixture.rp["result_population_id"],
            "strategy_spec_id": fixture.spec["strategy_spec_id"],
            "variant_manifest_id": fixture.manifest["variant_manifest_id"],
            "sweep_plan_id": fixture.sweep["sweep_plan_id"],
            "variants_available": len(fixture.variants),
            "variants_attempted": len(fixture.variants),
            "variants_expressible": len(fixture.variants),
            "data_slice_identity": coverage["data_slice_identity"],
            "normalized_data_path": fixture.catalog["normalized"]["path"].replace("\\", "/"),
            "normalized_data_sha256": observed_sha,
            "row_count": len(ohlcv),
        },
        "mapping": {
            "signal_source": "read-only compile_signal output for STRAT-SPEC-0004",
            "offline_only": True,
            "next_open_execution": True,
            "dynamic_equity_target_leverage": 1.0,
            "combined_cost_rate_bps": 5.0,
            "combined_cost_equivalence": (
                "RP-2592 computes 4 bps taker fee plus 1 bps slippage as separate additive "
                "cash costs on the same fill notional; Nautilus applies an equivalent 5 bps taker commission."
            ),
            "funding": "zero, matching every RP-2592 row",
            "unsupported_semantics": [
                "Nautilus 1.221.0 does not expose the RP zero-equity liquidation rule through this low-level bounded mapping; no RP-2592 variant liquidated.",
                "Continuous canonical quantities are rounded to 8 decimal places by the synthetic offline instrument.",
            ],
        },
        "run_1": run_1,
        "run_2": run_2,
        "reconciliation": comparisons,
        "reconciliation_summary": reconciliation_summary,
        "determinism": {
            "repeated_runs": True,
            "normalized_identical": deterministic,
            "checksum_run_1": checksum_1,
            "checksum_run_2": checksum_2,
        },
        "boundary": {
            "runtime_paper_live_touched": False,
            "private_apis_credentials_orders_used": False,
            "canonical_artifacts_mutated": False,
            "runner_backtester_mutated": False,
            "dependency_files_mutated": False,
            "external_dependency_isolated": True,
            "promotion_readiness_screen_gate_authority_created": False,
        },
    }
    report["report_checksum"] = _payload_checksum(report)
    return report


def _markdown(report: dict[str, Any]) -> str:
    det = report["determinism"]
    fixture = report["fixture"]
    lines = [
        f"# {PACKAGE_ID} Nautilus Mapping Report",
        "",
        *[f"- {label}" for label in LABELS],
        "",
        f"Decision label: `{report['decision_label']}`",
        f"Report checksum: `{report['report_checksum']}`",
        "",
        "## Fixture",
        "",
        f"- RP: `{fixture['result_population_id']}`",
        f"- Strategy / VM / sweep: `{fixture['strategy_spec_id']}` / `{fixture['variant_manifest_id']}` / `{fixture['sweep_plan_id']}`",
        f"- Data slice: `{fixture['data_slice_identity']}`",
        f"- Rows: `{fixture['row_count']}`",
        f"- Variants attempted / expressible: `{fixture['variants_attempted']}` / `{fixture['variants_expressible']}`",
        "",
        "## Determinism",
        "",
        f"- Repeated runs: `{det['repeated_runs']}`",
        f"- Normalized identical: `{det['normalized_identical']}`",
        f"- Run 1 checksum: `{det['checksum_run_1']}`",
        f"- Run 2 checksum: `{det['checksum_run_2']}`",
        "",
        "## Reconciliation",
        "",
        "| Variant | RP trades | Nautilus trades | Return delta |",
        "|---|---:|---:|---:|",
    ]
    for row in report["reconciliation"]:
        lines.append(
            f"| {row['variant_id']} | {row['rp']['trade_count']} | {row['nautilus']['trade_count']} | {row['delta']['return_pct']:.12f} |"
        )
    lines.extend(["", "## Unsupported Semantics", ""])
    lines.extend(f"- {item}" for item in report["mapping"]["unsupported_semantics"])
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {key}: `{value}`" for key, value in sorted(report["boundary"].items()))
    lines.append("")
    return "\n".join(lines)


def write_report(report: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown = _markdown(report)
    for text in (json_text, markdown):
        if ":\\" in text or ":/" in text:
            raise MappingSpikeError("machine-local absolute path detected in report")
    (output_dir / "nautilus_mapping_report.json").write_text(json_text, encoding="utf-8")
    (output_dir / "nautilus_mapping_report.md").write_text(markdown, encoding="utf-8")
    (output_dir / "nautilus_mapping_report.sha256").write_text(
        report["report_checksum"] + "\n", encoding="utf-8"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ohlcv-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        fixture = load_fixture()
        report = build_report(fixture=fixture, ohlcv_path=args.ohlcv_input)
        write_report(report, args.output_dir)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "decision_label": report["decision_label"],
                "variants_attempted": report["fixture"]["variants_attempted"],
                "variants_expressible": report["fixture"]["variants_expressible"],
                "deterministic": report["determinism"]["normalized_identical"],
                "report_checksum": report["report_checksum"],
                "output_dir": _portable(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
