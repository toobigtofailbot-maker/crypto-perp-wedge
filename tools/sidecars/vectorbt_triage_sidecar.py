"""Run bounded, non-canonical vectorbt triage over a repo sweep fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from lib.evaluation import max_drawdown, sharpe
from tools.research_runner import run_offline_sweep as runner
from tools.research_runner.spec_signal_compiler import compile_signal


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01"
TOOL_IDENTITY = "tools.sidecars.vectorbt_triage_sidecar"
DEFAULT_STRATEGY_SPEC = REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"
DEFAULT_VARIANT_MANIFEST = REPO_ROOT / "research/variant_manifests/VM-0004.variant_manifest.json"
DEFAULT_SWEEP_PLAN = REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"
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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_MAX_VARIANTS = 512
HARD_MAX_VARIANTS = 10_000

NON_AUTHORITY_LABELS = [
    "NON-CANONICAL VECTORBT TRIAGE SIDECAR OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT CANONICAL EVIDENCE",
    "NOT CANDIDATE EVIDENCE",
    "NOT RANKING / SCREEN-GATE / READINESS AUTHORITY",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT RUNNER / BACKTESTER AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    "CANONICAL RUNNER CONFIRMATION REQUIRED FOR EVERY FINALIST",
]


class VectorbtTriageError(RuntimeError):
    """Raised when the bounded sidecar cannot proceed safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VectorbtTriageError(f"input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise VectorbtTriageError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise VectorbtTriageError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _artifact_provenance(path: Path, *, optional: bool = False) -> dict[str, Any]:
    exists = path.is_file()
    if not exists and not optional:
        raise VectorbtTriageError(f"input file does not exist: {path}")
    return {
        "path": _repo_relative(path),
        "exists": exists,
        "checksum": _sha256_file(path) if exists else None,
    }


def _load_parent_inputs(
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        return runner._validate_parent_inputs(  # noqa: SLF001 - established repo fixture loader
            strategy_spec_path,
            variant_manifest_path,
            sweep_plan_path,
        )
    except Exception as exc:
        raise VectorbtTriageError(f"fixture validation failed: {exc}") from exc


def _selected_variants(
    manifest: dict[str, Any],
    sweep_plan: dict[str, Any],
    *,
    max_variants: int,
) -> list[dict[str, Any]]:
    if not 1 <= max_variants <= HARD_MAX_VARIANTS:
        raise VectorbtTriageError(
            f"max_variants must be between 1 and {HARD_MAX_VARIANTS}, got {max_variants}"
        )
    selected_ids = sweep_plan.get("test_selection", {}).get("selected_variant_ids")
    assignments = manifest.get("variant_assignments")
    if not isinstance(selected_ids, list) or not all(
        isinstance(item, str) for item in selected_ids
    ):
        raise VectorbtTriageError("Sweep Plan selected_variant_ids must be an array of strings")
    if not isinstance(assignments, list):
        raise VectorbtTriageError("Variant Manifest variant_assignments must be an array")
    if len(selected_ids) > max_variants:
        raise VectorbtTriageError(
            f"selected variant count {len(selected_ids)} exceeds bounded cap {max_variants}"
        )
    by_id = {
        row.get("variant_id"): row
        for row in assignments
        if isinstance(row, dict) and row.get("assignment_status") == "included"
    }
    missing = sorted(variant_id for variant_id in selected_ids if variant_id not in by_id)
    if missing:
        raise VectorbtTriageError(
            "selected variants missing from included manifest assignments: " + ", ".join(missing)
        )
    return [by_id[variant_id] for variant_id in sorted(selected_ids)]


def _resolve_ohlcv_path(catalog_path: Path, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path
    catalog = _load_json(catalog_path)
    raw_path = catalog.get("normalized", {}).get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise VectorbtTriageError("D4 catalog missing normalized.path")
    return REPO_ROOT / raw_path


def _load_execution_context(
    *,
    ohlcv_input_path: Path,
    d4_catalog_slice_path: Path,
    d2_import_report_path: Path,
) -> Any:
    try:
        return runner._d4_catalog_execution_input(  # noqa: SLF001 - read-only fixture loader
            ohlcv_input_path,
            d4_catalog_slice_path,
            d2_import_report_path,
        )
    except Exception as exc:
        raise VectorbtTriageError(f"OHLCV fixture loading failed: {exc}") from exc


def _load_vectorbt_optional() -> tuple[Any | None, str | None]:
    try:
        import vectorbt as vbt  # type: ignore[import-not-found]
    except Exception as exc:  # optional dependency may fail for version/platform reasons
        return None, f"{type(exc).__name__}: {exc}"
    return vbt, None


def _execution_signals(signal: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    desired = signal.shift(1).fillna(0.0)
    previous = desired.shift(1).fillna(0.0)
    return (
        (desired == 1.0) & (previous != 1.0),
        (previous == 1.0) & (desired != 1.0),
        (desired == -1.0) & (previous != -1.0),
        (previous == -1.0) & (desired != -1.0),
    )


def _portfolio_metrics(portfolio: Any, timeframe: str) -> dict[str, Any]:
    value = portfolio.value()
    returns = value.pct_change().dropna()
    drawdown, _, _ = max_drawdown(value)
    initial_equity = float(value.iloc[0])
    final_equity = float(value.iloc[-1])
    return {
        "final_equity": final_equity,
        "return_pct": float((final_equity - initial_equity) / initial_equity),
        "drawdown": float(drawdown),
        "trade_count": int(portfolio.trades.count()),
        "sharpe": float(sharpe(returns, timeframe)),
    }


def _run_vectorbt(
    *,
    vbt: Any,
    strategy_spec: dict[str, Any],
    variants: list[dict[str, Any]],
    ohlcv: pd.DataFrame,
    timeframe: str,
) -> list[dict[str, Any]]:
    close = ohlcv["close"].astype(float)
    execution_price = ohlcv["open"].astype(float)
    rows: list[dict[str, Any]] = []
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
        rows.append(
            {
                "variant_id": variant["variant_id"],
                "parameter_values": variant.get("parameter_values", {}),
                "metrics": _portfolio_metrics(portfolio, timeframe),
                "signal_checksum": _sha256_payload(signal.astype(float).tolist()),
            }
        )
    return rows


def _fixture_provenance(
    *,
    strategy_spec_path: Path,
    variant_manifest_path: Path,
    sweep_plan_path: Path,
    d4_catalog_slice_path: Path,
    d2_import_report_path: Path,
    ohlcv_input_path: Path,
) -> dict[str, Any]:
    return {
        "strategy_spec": _artifact_provenance(strategy_spec_path),
        "variant_manifest": _artifact_provenance(variant_manifest_path),
        "sweep_plan": _artifact_provenance(sweep_plan_path),
        "d4_catalog_slice": _artifact_provenance(d4_catalog_slice_path),
        "d2_import_report": _artifact_provenance(d2_import_report_path),
        "ohlcv_input": _artifact_provenance(ohlcv_input_path, optional=True),
    }


def build_report(
    *,
    strategy_spec_path: Path = DEFAULT_STRATEGY_SPEC,
    variant_manifest_path: Path = DEFAULT_VARIANT_MANIFEST,
    sweep_plan_path: Path = DEFAULT_SWEEP_PLAN,
    ohlcv_input_path: Path | None = None,
    d4_catalog_slice_path: Path = DEFAULT_D4_CATALOG,
    d2_import_report_path: Path = DEFAULT_D2_IMPORT_REPORT,
    max_variants: int = DEFAULT_MAX_VARIANTS,
) -> dict[str, Any]:
    """Build a deterministic triage or deferred report without canonical writes."""

    strategy_spec, manifest, sweep_plan = _load_parent_inputs(
        strategy_spec_path,
        variant_manifest_path,
        sweep_plan_path,
    )
    variants = _selected_variants(manifest, sweep_plan, max_variants=max_variants)
    resolved_ohlcv = _resolve_ohlcv_path(d4_catalog_slice_path, ohlcv_input_path)
    provenance = _fixture_provenance(
        strategy_spec_path=strategy_spec_path,
        variant_manifest_path=variant_manifest_path,
        sweep_plan_path=sweep_plan_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        ohlcv_input_path=resolved_ohlcv,
    )
    vbt, import_error = _load_vectorbt_optional()
    rows: list[dict[str, Any]] = []
    data_slice_identity: str | None = None
    if vbt is None:
        execution_status = "DEFERRED_OPTIONAL_DEPENDENCY_UNAVAILABLE"
        decision_label = "BLOCKED"
        vectorbt_version = None
    else:
        execution_input = _load_execution_context(
            ohlcv_input_path=resolved_ohlcv,
            d4_catalog_slice_path=d4_catalog_slice_path,
            d2_import_report_path=d2_import_report_path,
        )
        rows = _run_vectorbt(
            vbt=vbt,
            strategy_spec=strategy_spec,
            variants=variants,
            ohlcv=execution_input.ohlcv,
            timeframe=execution_input.timeframe,
        )
        data_slice_identity = execution_input.data_slice_identity
        execution_status = "COMPLETED_NON_CANONICAL_TRIAGE"
        decision_label = "ADOPT_AS_NON_CANONICAL_TRIAGE_SIDECAR"
        vectorbt_version = str(getattr(vbt, "__version__", "unknown"))

    report: dict[str, Any] = {
        "labels": NON_AUTHORITY_LABELS,
        "package_id": PACKAGE_ID,
        "tool_identity": TOOL_IDENTITY,
        "report_type": "bounded_vectorbt_triage",
        "execution_status": execution_status,
        "decision_label": decision_label,
        "dependency": {
            "name": "vectorbt",
            "availability": "available" if vbt is not None else "unavailable",
            "version": vectorbt_version,
            "import_error": import_error,
            "installation_posture": (
                "optional isolated research environment only; no repo dependency mutation"
            ),
        },
        "fixture": {
            "strategy_spec_id": strategy_spec.get("strategy_spec_id"),
            "variant_manifest_id": manifest.get("variant_manifest_id"),
            "sweep_plan_id": sweep_plan.get("sweep_plan_id"),
            "data_slice_identity": data_slice_identity,
            "selected_variant_count": len(variants),
            "processed_variant_count": len(rows),
            "max_variants": max_variants,
            "hard_max_variants": HARD_MAX_VARIANTS,
            "variant_ordering": "variant_id_ascending_not_metric_ranked",
            "provenance": provenance,
        },
        "triage_rows": rows,
        "triage_rows_checksum": _sha256_payload(rows),
        "semantics": {
            "signal_source": "repo Strategy Spec compiler output",
            "fill_model": "vectorbt from_signals at next bar open after one-bar signal shift",
            "cost_model": "fixed 4 bps fees plus 1 bp slippage",
            "sizing_model": "vectorbt percent sizing; approximate 1x dynamic equity exposure",
            "known_limitations": [
                "vectorized fills and portfolio accounting are not canonical runner semantics",
                "funding cashflows are not modeled",
                "repo-equivalent liquidation and zero-equity behavior are not modeled",
                "metrics are triage diagnostics only and are not finalist confirmation",
            ],
        },
        "canonical_confirmation_required": True,
        "boundary_statement": {
            "canonical_evidence_written": False,
            "canonical_result_population_written": False,
            "strategy_spec_vm_sweep_written": False,
            "runner_or_backtester_replaced": False,
            "candidate_ranking_authority_created": False,
            "screen_gate_or_readiness_authority_created": False,
            "runtime_paper_live_touched": False,
            "dependency_files_mutated": False,
        },
    }
    report["output_checksum"] = _sha256_payload(report)
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Vectorbt Triage Report",
        "",
        *[f"- {label}" for label in NON_AUTHORITY_LABELS],
        "",
        f"Execution status: `{report['execution_status']}`",
        f"Decision label: `{report['decision_label']}`",
        f"Output checksum: `{report['output_checksum']}`",
        f"Vectorbt: `{report['dependency']['availability']}` / `{report['dependency']['version']}`",
        "",
        "## Fixture",
        "",
        f"- Strategy Spec: `{report['fixture']['strategy_spec_id']}`",
        f"- Variant Manifest: `{report['fixture']['variant_manifest_id']}`",
        f"- Sweep Plan: `{report['fixture']['sweep_plan_id']}`",
        f"- Data slice: `{report['fixture']['data_slice_identity']}`",
        f"- Selected variants: `{report['fixture']['selected_variant_count']}`",
        f"- Processed variants: `{report['fixture']['processed_variant_count']}`",
        "- Bound: "
        f"`{report['fixture']['max_variants']}` "
        f"(hard maximum `{report['fixture']['hard_max_variants']}`)",
        "",
        "## Triage Metrics",
        "",
        "| variant | trades | return | drawdown | sharpe |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["triage_rows"]:
        metrics = row["metrics"]
        lines.append(
            f"| {row['variant_id']} | {metrics['trade_count']} | {metrics['return_pct']} | "
            f"{metrics['drawdown']} | {metrics['sharpe']} |"
        )
    if not report["triage_rows"]:
        lines.append("| _not run_ | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Limitations and Boundary",
            "",
            *[f"- {item}" for item in report["semantics"]["known_limitations"]],
            "- Rows are ordered by variant id, not by a readiness or promotion score.",
            "- Every finalist requires later confirmation through the repo-owned canonical "
            "runner/evidence path.",
            "- This sidecar writes no canonical Result Population, Strategy Spec, Variant "
            "Manifest, or Sweep Plan.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    *,
    strategy_spec_path: Path = DEFAULT_STRATEGY_SPEC,
    variant_manifest_path: Path = DEFAULT_VARIANT_MANIFEST,
    sweep_plan_path: Path = DEFAULT_SWEEP_PLAN,
    ohlcv_input_path: Path | None = None,
    d4_catalog_slice_path: Path = DEFAULT_D4_CATALOG,
    d2_import_report_path: Path = DEFAULT_D2_IMPORT_REPORT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    max_variants: int = DEFAULT_MAX_VARIANTS,
) -> dict[str, Any]:
    report = build_report(
        strategy_spec_path=strategy_spec_path,
        variant_manifest_path=variant_manifest_path,
        sweep_plan_path=sweep_plan_path,
        ohlcv_input_path=ohlcv_input_path,
        d4_catalog_slice_path=d4_catalog_slice_path,
        d2_import_report_path=d2_import_report_path,
        max_variants=max_variants,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "vectorbt_triage_report.json", report)
    (output_dir / "vectorbt_triage_report.md").write_text(
        _markdown_report(report), encoding="utf-8"
    )
    (output_dir / "vectorbt_triage_report.sha256").write_text(
        report["output_checksum"] + "\n", encoding="utf-8"
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy-spec", type=Path, default=DEFAULT_STRATEGY_SPEC)
    parser.add_argument("--variant-manifest", type=Path, default=DEFAULT_VARIANT_MANIFEST)
    parser.add_argument("--sweep-plan", type=Path, default=DEFAULT_SWEEP_PLAN)
    parser.add_argument("--ohlcv-input", type=Path)
    parser.add_argument("--d4-catalog-slice", type=Path, default=DEFAULT_D4_CATALOG)
    parser.add_argument("--d2-import-report", type=Path, default=DEFAULT_D2_IMPORT_REPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-variants", type=int, default=DEFAULT_MAX_VARIANTS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = run(
            strategy_spec_path=args.strategy_spec,
            variant_manifest_path=args.variant_manifest,
            sweep_plan_path=args.sweep_plan,
            ohlcv_input_path=args.ohlcv_input,
            d4_catalog_slice_path=args.d4_catalog_slice,
            d2_import_report_path=args.d2_import_report,
            output_dir=args.output_dir,
            max_variants=args.max_variants,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "execution_status": report["execution_status"],
                "decision_label": report["decision_label"],
                "selected_variant_count": report["fixture"]["selected_variant_count"],
                "processed_variant_count": report["fixture"]["processed_variant_count"],
                "canonical_confirmation_required": report["canonical_confirmation_required"],
                "output_checksum": report["output_checksum"],
                "output_dir": _repo_relative(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
