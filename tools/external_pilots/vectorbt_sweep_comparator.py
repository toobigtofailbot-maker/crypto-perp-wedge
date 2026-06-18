"""Non-canonical vectorbt sidecar comparator for an offline sweep fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

from lib.evaluation import max_drawdown, sharpe
from tools.research_runner import run_offline_sweep as runner
from tools.research_runner.spec_signal_compiler import compile_signal


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_SPEC = REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"
DEFAULT_VARIANT_MANIFEST = REPO_ROOT / "research/variant_manifests/VM-0004.variant_manifest.json"
DEFAULT_SWEEP_PLAN = REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"
DEFAULT_RP_COMPARATOR = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_D4_CATALOG = (
    REPO_ROOT
    / "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
)
DEFAULT_D2_IMPORT_REPORT = (
    REPO_ROOT
    / "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json"
)
DEFAULT_SCRATCH_DIR = REPO_ROOT / "scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01"

NON_CANONICAL_LABELS = [
    "NON-CANONICAL EXTERNAL SIDECAR OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT STRATEGY AUTHORITY",
    "NOT VM/SWEEP AUTHORITY",
    "NOT CANDIDATE EVIDENCE",
    "NOT PAPER/LIVE/RUNTIME AUTHORITY",
]


class VectorbtPilotError(RuntimeError):
    """Raised when the non-canonical pilot cannot run safely."""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_payload(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_vectorbt():
    try:
        import vectorbt as vbt  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - exercised through CLI behavior
        raise VectorbtPilotError(
            "vectorbt is not installed in this Python environment. Install vectorbt in an "
            "isolated research-side environment; do not add it to the current broad runtime "
            "requirements file while it requires pandas<3."
        ) from exc
    return vbt


def _resolve_ohlcv_path(catalog_path: Path, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path
    catalog = _load_json(catalog_path)
    raw_path = catalog.get("normalized", {}).get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise VectorbtPilotError("D4 catalog missing normalized.path")
    return REPO_ROOT / raw_path


def _load_fixture_context(
    *,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    ohlcv_input_path: Path,
    d4_catalog_slice_path: Path,
    d2_import_report_path: Path,
) -> dict[str, Any]:
    strategy_spec, manifest, sweep_plan = runner._validate_parent_inputs(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
    )
    execution_input = runner._d4_catalog_execution_input(
        ohlcv_input_path,
        d4_catalog_slice_path,
        d2_import_report_path,
    )
    return {
        "strategy_spec": strategy_spec,
        "manifest": manifest,
        "sweep_plan": sweep_plan,
        "execution_input": execution_input,
    }


def _selected_variants(manifest: dict[str, Any], sweep_plan: dict[str, Any]) -> list[dict[str, Any]]:
    selected = set(sweep_plan["test_selection"]["selected_variant_ids"])
    return [
        variant
        for variant in manifest["variant_assignments"]
        if variant["variant_id"] in selected and variant["assignment_status"] == "included"
    ]


def _execution_signals(signal: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    desired = signal.shift(1).fillna(0.0)
    previous = desired.shift(1).fillna(0.0)
    long_entries = (desired == 1.0) & (previous != 1.0)
    long_exits = (previous == 1.0) & (desired != 1.0)
    short_entries = (desired == -1.0) & (previous != -1.0)
    short_exits = (previous == -1.0) & (desired != -1.0)
    return long_entries, long_exits, short_entries, short_exits


def _portfolio_metrics(portfolio: Any, timeframe: str) -> dict[str, Any]:
    value = portfolio.value()
    returns = value.pct_change().dropna()
    drawdown, _, _ = max_drawdown(value)
    initial_equity = float(value.iloc[0])
    final_equity = float(value.iloc[-1])
    trade_count = int(portfolio.trades.count())
    return {
        "final_equity": final_equity,
        "return_pct": float((final_equity - initial_equity) / initial_equity),
        "drawdown": float(drawdown),
        "trade_count": trade_count,
        "sharpe": float(sharpe(returns, timeframe)),
    }


def _run_vectorbt_once(
    *,
    vbt: Any,
    strategy_spec: dict[str, Any],
    variants: list[dict[str, Any]],
    ohlcv: pd.DataFrame,
    funding: pd.DataFrame,
    timeframe: str,
) -> dict[str, Any]:
    del funding
    rows = []
    started = time.perf_counter()
    close = ohlcv["close"].astype(float)
    execution_price = ohlcv["open"].astype(float)
    for variant in variants:
        signal = compile_signal(strategy_spec, variant, ohlcv)
        long_entries, long_exits, short_entries, short_exits = _execution_signals(signal)
        portfolio = vbt.Portfolio.from_signals(
            close=close,
            entries=long_entries,
            exits=long_exits,
            short_entries=short_entries,
            short_exits=short_exits,
            price=execution_price,
            init_cash=runner.INITIAL_EQUITY,
            size=1.0,
            size_type="percent",
            fees=0.0004,
            slippage=0.0001,
            accumulate=False,
            upon_opposite_entry="reverse",
            freq="15min" if timeframe == "15m" else timeframe,
        )
        metrics = _portfolio_metrics(portfolio, timeframe)
        rows.append(
            {
                "variant_id": variant["variant_id"],
                "parameter_values": variant.get("parameter_values", {}),
                "metrics": metrics,
                "signal_hash": _sha256_payload(signal.astype(float).tolist()),
            }
        )
    elapsed = time.perf_counter() - started
    payload = {
        "labels": NON_CANONICAL_LABELS,
        "engine": "vectorbt",
        "vectorbt_version": getattr(vbt, "__version__", "unknown"),
        "wall_clock_seconds": elapsed,
        "variant_rows": rows,
        "determinism_hash": _sha256_payload(rows),
        "semantics": {
            "signal_source": "repo compiler output from tools.research_runner.spec_signal_compiler",
            "execution_price": "bar open aligned to repo next-bar-open fill by shifting desired signal one bar",
            "sizing": "vectorbt size_type=percent size=1.0 approximate 1x dynamic equity exposure",
            "known_limitations": [
                "vectorbt accounting is not the canonical repo backtester",
                "zero-equity liquidation semantics are not modeled as repo-equivalent",
                "funding cashflows are not modeled in this sidecar run",
                "report is scratch comparator output only",
            ],
        },
    }
    payload["run_hash"] = _sha256_payload(payload)
    return payload


def _run_repo_baseline(
    *,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    ohlcv_input_path: Path,
    d4_catalog_slice_path: Path,
    d2_import_report_path: Path,
    max_workers: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    result = runner.run_offline_sweep(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
        canonical_15m=True,
        ohlcv_input_path=ohlcv_input_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        deterministic_seed=190,
        sizing_mode=runner.SIZING_MODE_DYNAMIC_EQUITY_TARGET_LEVERAGE,
        target_leverage=1.0,
        max_workers=max_workers,
    )
    elapsed = time.perf_counter() - started
    payload = {
        "labels": NON_CANONICAL_LABELS,
        "engine": "repo_runner_dry_run",
        "wall_clock_seconds": elapsed,
        "dry_run": result["dry_run"],
        "wrote": result["wrote"],
        "result_population_id": result["result_population_id"],
        "outcome_category_counts": result["outcome_category_counts"],
        "variant_rows": result["result_population"]["variant_result_rows"],
        "result_population_identity_hash": result["result_population"]["result_population_identity_hash"][
            "hash"
        ],
    }
    payload["run_hash"] = _sha256_payload(payload)
    return payload


def _rows_by_variant(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["variant_id"]: row for row in rows}


def _delta(left: Any, right: Any) -> float | None:
    if left is None or right is None:
        return None
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        return None
    if not math.isfinite(float(left)) or not math.isfinite(float(right)):
        return None
    return float(right) - float(left)


def _comparison(
    *,
    vectorbt_run_1: dict[str, Any],
    vectorbt_run_2: dict[str, Any],
    repo_baseline: dict[str, Any],
    rp_comparator: dict[str, Any],
) -> dict[str, Any]:
    vectorbt_by_id = _rows_by_variant(vectorbt_run_1["variant_rows"])
    repo_by_id = _rows_by_variant(repo_baseline["variant_rows"])
    rows = []
    matched = []
    explained = []
    unexplained = []
    for variant_id in sorted(repo_by_id):
        repo_row = repo_by_id[variant_id]
        vbt_row = vectorbt_by_id.get(variant_id)
        repo_metrics = repo_row["metrics"]
        vbt_metrics = vbt_row["metrics"] if vbt_row else {}
        trade_delta = _delta(repo_metrics.get("trade_count"), vbt_metrics.get("trade_count"))
        return_delta = _delta(repo_metrics.get("return_pct"), vbt_metrics.get("return_pct"))
        drawdown_delta = _delta(repo_metrics.get("drawdown"), vbt_metrics.get("drawdown"))
        sharpe_delta = _delta(repo_metrics.get("sharpe"), vbt_metrics.get("sharpe"))
        exact_match = (
            trade_delta == 0.0
            and return_delta is not None
            and abs(return_delta) <= 1e-12
            and drawdown_delta is not None
            and abs(drawdown_delta) <= 1e-12
        )
        notes = []
        missing_vectorbt_row = vbt_row is None
        if not exact_match and not missing_vectorbt_row:
            notes.extend(
                [
                    "vectorbt uses non-canonical portfolio accounting",
                    "vectorbt percent sizing is only an approximate analogue for repo dynamic_equity_target_leverage",
                    "zero-equity liquidation and repo funding accounting are not modeled as repo-equivalent",
                ]
            )
        if exact_match:
            matched.append(variant_id)
        elif notes:
            explained.append(variant_id)
        else:
            unexplained.append(variant_id)
        rows.append(
            {
                "variant_id": variant_id,
                "trade_count_repo": repo_metrics.get("trade_count"),
                "trade_count_vectorbt": vbt_metrics.get("trade_count"),
                "trade_count_delta": trade_delta,
                "final_return_repo": repo_metrics.get("return_pct"),
                "final_return_vectorbt": vbt_metrics.get("return_pct"),
                "final_return_delta": return_delta,
                "max_drawdown_repo": repo_metrics.get("drawdown"),
                "max_drawdown_vectorbt": vbt_metrics.get("drawdown"),
                "max_drawdown_delta": drawdown_delta,
                "sharpe_repo": repo_metrics.get("sharpe"),
                "sharpe_vectorbt": vbt_metrics.get("sharpe"),
                "sharpe_delta": sharpe_delta,
                "equity_curve_match_status": "not_compared_not_exported_by_sidecar",
                "explained_difference_notes": notes,
                "unexplained_difference_notes": (
                    ["no vectorbt row produced"] if missing_vectorbt_row else []
                ),
            }
        )
    deterministic = vectorbt_run_1["determinism_hash"] == vectorbt_run_2["determinism_hash"]
    recommendation = "EXPLORATION_ONLY" if deterministic and not unexplained else "BLOCKED"
    speed_ratio = None
    if repo_baseline["wall_clock_seconds"] > 0:
        speed_ratio = vectorbt_run_1["wall_clock_seconds"] / repo_baseline["wall_clock_seconds"]
    return {
        "labels": NON_CANONICAL_LABELS,
        "package": "EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01",
        "fixture": {
            "strategy_spec_id": rp_comparator["lineage"]["strategy_spec_id"],
            "variant_manifest_id": rp_comparator["lineage"]["variant_manifest_id"],
            "sweep_plan_id": rp_comparator["lineage"]["sweep_plan_id"],
            "rp_comparator_id": rp_comparator["result_population_id"],
            "data_slice_identity": rp_comparator["data_coverage_summary"]["data_slice_identity"],
        },
        "vectorbt_wall_clock_seconds": vectorbt_run_1["wall_clock_seconds"],
        "repo_runner_wall_clock_seconds": repo_baseline["wall_clock_seconds"],
        "speed_ratio_vectorbt_over_repo": speed_ratio,
        "determinism_run_1_hash": vectorbt_run_1["determinism_hash"],
        "determinism_run_2_hash": vectorbt_run_2["determinism_hash"],
        "determinism_match": deterministic,
        "matched_variants": matched,
        "explained_difference_variants": explained,
        "unexplained_difference_variants": unexplained,
        "variant_comparisons": rows,
        "recommendation": recommendation,
        "recommendation_rationale": (
            "vectorbt is deterministic and useful as an exploration-only sidecar, but this pilot "
            "does not establish repo-equivalent accounting or canonical evidence parity."
            if recommendation == "EXPLORATION_ONLY"
            else "pilot blocked by missing or unexplained variant comparisons"
        ),
    }


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01 Scratch Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Recommendation: `{report['recommendation']}`",
        f"Determinism match: `{report['determinism_match']}`",
        f"Vectorbt wall-clock seconds: `{report['vectorbt_wall_clock_seconds']:.6f}`",
        f"Repo runner wall-clock seconds: `{report['repo_runner_wall_clock_seconds']:.6f}`",
        f"Speed ratio vectorbt/repo: `{report['speed_ratio_vectorbt_over_repo']}`",
        "",
        "## Fixture",
        "",
        f"- Strategy: `{report['fixture']['strategy_spec_id']}`",
        f"- VM: `{report['fixture']['variant_manifest_id']}`",
        f"- Sweep: `{report['fixture']['sweep_plan_id']}`",
        f"- RP comparator: `{report['fixture']['rp_comparator_id']}`",
        f"- Data slice: `{report['fixture']['data_slice_identity']}`",
        "",
        "## Variant Deltas",
        "",
        "| variant | repo trades | vectorbt trades | return delta | drawdown delta | sharpe delta | status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["variant_comparisons"]:
        status = "matched" if row["variant_id"] in report["matched_variants"] else "explained_difference"
        lines.append(
            "| {variant_id} | {trade_count_repo} | {trade_count_vectorbt} | {ret} | {dd} | {sr} | {status} |".format(
                variant_id=row["variant_id"],
                trade_count_repo=row["trade_count_repo"],
                trade_count_vectorbt=row["trade_count_vectorbt"],
                ret=row["final_return_delta"],
                dd=row["max_drawdown_delta"],
                sr=row["sharpe_delta"],
                status=status,
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Differences are expected unless explicitly marked matched.",
            "- This sidecar uses repo compiler signals, but vectorbt accounting is not the canonical repo backtester.",
            "- No canonical Result Population is written by this report.",
            "",
        ]
    )
    return "\n".join(lines)


def run_pilot(
    *,
    strategy_spec_path: Path = DEFAULT_STRATEGY_SPEC,
    variant_manifest_path: Path = DEFAULT_VARIANT_MANIFEST,
    sweep_plan_path: Path = DEFAULT_SWEEP_PLAN,
    rp_comparator_path: Path = DEFAULT_RP_COMPARATOR,
    ohlcv_input_path: Path | None = None,
    d4_catalog_slice_path: Path = DEFAULT_D4_CATALOG,
    d2_import_report_path: Path = DEFAULT_D2_IMPORT_REPORT,
    output_dir: Path = DEFAULT_SCRATCH_DIR,
    repo_max_workers: int = 2,
) -> dict[str, Any]:
    vbt = _load_vectorbt()
    resolved_ohlcv = _resolve_ohlcv_path(d4_catalog_slice_path, ohlcv_input_path)
    context = _load_fixture_context(
        strategy_spec_path=strategy_spec_path,
        variant_manifest_path=variant_manifest_path,
        sweep_plan_path=sweep_plan_path,
        ohlcv_input_path=resolved_ohlcv,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
    )
    rp_comparator = _load_json(rp_comparator_path)
    if rp_comparator["lineage"]["strategy_spec_id"] != context["strategy_spec"]["strategy_spec_id"]:
        raise VectorbtPilotError("RP comparator does not match selected Strategy Spec")
    variants = _selected_variants(context["manifest"], context["sweep_plan"])
    repo_baseline = _run_repo_baseline(
        strategy_spec_path=strategy_spec_path,
        variant_manifest_path=variant_manifest_path,
        sweep_plan_path=sweep_plan_path,
        ohlcv_input_path=resolved_ohlcv,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        max_workers=repo_max_workers,
    )
    vectorbt_run_1 = _run_vectorbt_once(
        vbt=vbt,
        strategy_spec=context["strategy_spec"],
        variants=variants,
        ohlcv=context["execution_input"].ohlcv,
        funding=context["execution_input"].funding,
        timeframe=context["execution_input"].timeframe,
    )
    vectorbt_run_2 = _run_vectorbt_once(
        vbt=vbt,
        strategy_spec=context["strategy_spec"],
        variants=variants,
        ohlcv=context["execution_input"].ohlcv,
        funding=context["execution_input"].funding,
        timeframe=context["execution_input"].timeframe,
    )
    report = _comparison(
        vectorbt_run_1=vectorbt_run_1,
        vectorbt_run_2=vectorbt_run_2,
        repo_baseline=repo_baseline,
        rp_comparator=rp_comparator,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "vectorbt_run_1.json", vectorbt_run_1)
    _write_json(output_dir / "vectorbt_run_2.json", vectorbt_run_2)
    _write_json(output_dir / "runner_baseline.json", repo_baseline)
    _write_json(output_dir / "comparison_report.json", report)
    (output_dir / "comparison_report.md").write_text(_markdown_report(report), encoding="utf-8")
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy-spec", type=Path, default=DEFAULT_STRATEGY_SPEC)
    parser.add_argument("--variant-manifest", type=Path, default=DEFAULT_VARIANT_MANIFEST)
    parser.add_argument("--sweep-plan", type=Path, default=DEFAULT_SWEEP_PLAN)
    parser.add_argument("--rp-comparator", type=Path, default=DEFAULT_RP_COMPARATOR)
    parser.add_argument("--ohlcv-input", type=Path)
    parser.add_argument("--d4-catalog-slice", type=Path, default=DEFAULT_D4_CATALOG)
    parser.add_argument("--d2-import-report", type=Path, default=DEFAULT_D2_IMPORT_REPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_SCRATCH_DIR)
    parser.add_argument("--repo-max-workers", type=int, default=2)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_pilot(
            strategy_spec_path=args.strategy_spec,
            variant_manifest_path=args.variant_manifest,
            sweep_plan_path=args.sweep_plan,
            rp_comparator_path=args.rp_comparator,
            ohlcv_input_path=args.ohlcv_input,
            d4_catalog_slice_path=args.d4_catalog_slice,
            d2_import_report_path=args.d2_import_report,
            output_dir=args.output_dir,
            repo_max_workers=args.repo_max_workers,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "labels": NON_CANONICAL_LABELS,
                "recommendation": report["recommendation"],
                "determinism_match": report["determinism_match"],
                "matched_variants": report["matched_variants"],
                "explained_difference_variants": report["explained_difference_variants"],
                "unexplained_difference_variants": report["unexplained_difference_variants"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
