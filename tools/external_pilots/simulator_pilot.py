"""Non-canonical external simulator feasibility pilot for NautilusTrader concepts."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-SIMULATOR-PILOT-01"
DEFAULT_RP_FIXTURE = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
DEFAULT_STRATEGY_SPEC = REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"
DEFAULT_VARIANT_MANIFEST = REPO_ROOT / "research/variant_manifests/VM-0004.variant_manifest.json"
DEFAULT_SWEEP_PLAN = REPO_ROOT / "research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"
DEFAULT_D4_CATALOG = (
    REPO_ROOT
    / "research/data_slices/binance_usdtm_btcusdt_15m/"
    "binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID

NON_CANONICAL_LABELS = [
    "NON-CANONICAL EXTERNAL SIMULATOR PILOT OUTPUT",
    "NOT A RESULT POPULATION",
    "NOT STRATEGY / VM / SWEEP AUTHORITY",
    "NOT CANONICAL RUNNER AUTHORITY",
    "NOT BACKTEST REPLACEMENT AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    "NOT OMS / RISK / RECONCILIATION AUTHORITY",
    (
        "CANONICAL-EVIDENCE USE REQUIRES SEPARATE MAPPING, VALIDATION, "
        "DETERMINISM, AUDITABILITY, PROVENANCE, AND MAIN/KARL APPROVAL"
    ),
]

DANGEROUS_SOURCE_PATTERNS = [
    r"\brequests\b",
    r"\burllib\b",
    r"\bsocket\b",
    r"Binance[A-Za-z]*(Data|Exec|Http|WebSocket|Client|Factory)",
    r"submit_order\(",
    r"cancel_order\(",
    r"cancel_all_orders\(",
    r"place_order",
    r"query_order",
    r"open_orders",
    r"private_key",
    r"api_secret",
]


class SimulatorPilotError(RuntimeError):
    """Raised when the simulator pilot cannot build a safe report."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SimulatorPilotError(f"invalid JSON in {_portable_path(path)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SimulatorPilotError(f"JSON root must be an object: {_portable_path(path)}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_payload(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _sha256_bytes(data)


def _portable_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _assert_portable_text(text: str) -> None:
    root = REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    if any(token and token in text for token in bad_tokens):
        raise SimulatorPilotError("report text contains a machine-local checkout path")
    if re.search(r"\b[A-Za-z]:[\\/]", text):
        raise SimulatorPilotError("report text contains a Windows absolute path")


def _source_guard() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8")
    findings = []
    for pattern in DANGEROUS_SOURCE_PATTERNS:
        if re.search(pattern, source):
            findings.append(pattern)
    allowed_self_references = sorted(set(DANGEROUS_SOURCE_PATTERNS) & set(findings))
    # The pattern constants themselves are allowed; scan the source with constants removed.
    stripped = re.sub(
        r"DANGEROUS_SOURCE_PATTERNS = \[.*?\]\n\n",
        "",
        source,
        flags=re.DOTALL,
    )
    active_findings = [
        pattern for pattern in DANGEROUS_SOURCE_PATTERNS if re.search(pattern, stripped)
    ]
    return {
        "checked": True,
        "source_path": _portable_path(Path(__file__)),
        "active_forbidden_pattern_hits": active_findings,
        "pattern_constants_present": allowed_self_references,
        "no_network_or_exchange_adapter_calls": not active_findings,
    }


def _selected_rows(manifest: dict[str, Any], sweep: dict[str, Any]) -> list[dict[str, Any]]:
    selected = set(sweep.get("test_selection", {}).get("selected_variant_ids", []))
    rows = [
        row
        for row in manifest.get("variant_assignments", [])
        if isinstance(row, dict)
        and row.get("variant_id") in selected
        and row.get("assignment_status") == "included"
    ]
    return sorted(rows, key=lambda row: str(row.get("variant_id", "")))


def _fixture_summary(
    *,
    rp_path: Path,
    spec_path: Path,
    manifest_path: Path,
    sweep_path: Path,
    catalog_path: Path,
) -> dict[str, Any]:
    rp = _load_json(rp_path)
    spec = _load_json(spec_path)
    manifest = _load_json(manifest_path)
    sweep = _load_json(sweep_path)
    catalog = _load_json(catalog_path)

    lineage = rp.get("lineage", {})
    expected = {
        "strategy_spec_id": spec.get("strategy_spec_id"),
        "variant_manifest_id": manifest.get("variant_manifest_id"),
        "sweep_plan_id": sweep.get("sweep_plan_id"),
    }
    observed = {
        "strategy_spec_id": lineage.get("strategy_spec_id"),
        "variant_manifest_id": lineage.get("variant_manifest_id"),
        "sweep_plan_id": lineage.get("sweep_plan_id"),
    }
    if observed != expected:
        raise SimulatorPilotError(f"fixture lineage mismatch: observed={observed} expected={expected}")

    rp_rows = rp.get("variant_result_rows", [])
    if not isinstance(rp_rows, list) or not rp_rows:
        raise SimulatorPilotError("RP fixture lacks variant_result_rows")
    selected = _selected_rows(manifest, sweep)
    normalized_path = catalog.get("normalized", {}).get("path")
    normalized_exists = bool(normalized_path and (REPO_ROOT / normalized_path).exists())
    return {
        "result_population_id": rp.get("result_population_id"),
        "result_population_path": _portable_path(rp_path),
        "result_population_checksum": _sha256_file(rp_path),
        "strategy_spec_id": spec.get("strategy_spec_id"),
        "strategy_spec_path": _portable_path(spec_path),
        "variant_manifest_id": manifest.get("variant_manifest_id"),
        "variant_manifest_path": _portable_path(manifest_path),
        "sweep_plan_id": sweep.get("sweep_plan_id"),
        "sweep_plan_path": _portable_path(sweep_path),
        "data_slice_identity": rp.get("data_coverage_summary", {}).get("data_slice_identity"),
        "data_catalog_path": _portable_path(catalog_path),
        "normalized_data_path": normalized_path.replace("\\", "/") if isinstance(normalized_path, str) else None,
        "normalized_data_local_exists": normalized_exists,
        "timeframe": rp.get("data_coverage_summary", {}).get("timeframe"),
        "rp_successful_row_count": sum(
            1 for row in rp_rows if row.get("outcome_category") == "successful"
        ),
        "rp_row_count": len(rp_rows),
        "selected_variant_count": len(selected),
        "selected_variant_ids": [row["variant_id"] for row in selected],
        "fee_assumption": sweep.get("realism_assumptions", {}).get("fee_side_assumption"),
        "slippage_assumption": sweep.get("realism_assumptions", {}).get("slippage_model"),
        "sizing_assumption": sweep.get("realism_assumptions", {}).get("order_size_assumption"),
        "funding_assumption": "RP-2592 metrics record funding=0.0 for all rows",
        "fill_assumption": sweep.get("realism_assumptions", {}).get("fill_mode"),
        "bar_timing_assumption": sweep.get("realism_assumptions", {}).get("bar_path_assumption"),
        "liquidation_assumption": sweep.get("realism_assumptions", {}).get("liquidation_mode"),
        "variant_parameters": {
            row["variant_id"]: row.get("parameter_values", {}) for row in selected
        },
        "rp_metric_summary": _rp_metric_summary(rp_rows),
    }


def _rp_metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = ["trade_count", "return_pct", "drawdown", "sharpe", "fees", "slippage", "funding"]
    summary: dict[str, Any] = {}
    for metric in metrics:
        values = [
            row.get("metrics", {}).get(metric)
            for row in rows
            if isinstance(row.get("metrics", {}).get(metric), (int, float))
        ]
        if not values:
            continue
        summary[metric] = {
            "min": min(values),
            "max": max(values),
            "mean": sum(float(value) for value in values) / len(values),
        }
    return summary


def _nautilus_source_inspection() -> dict[str, Any]:
    spec = importlib.util.find_spec("nautilus_trader")
    if spec is None or spec.origin is None:
        return {
            "status": "not_available",
            "source_read": False,
            "concepts": {},
            "notes": ["NautilusTrader package not import-locatable in this Python process."],
        }
    package_root = Path(spec.origin).resolve().parent
    config_path = package_root / "backtest" / "config.py"
    if not config_path.exists():
        return {
            "status": "not_found",
            "source_read": False,
            "concepts": {},
            "notes": ["NautilusTrader backtest/config.py source was not present."],
        }
    text = config_path.read_text(encoding="utf-8", errors="replace")
    concept_names = [
        "bar_execution",
        "fill_model",
        "fee_model",
        "margin_model",
        "default_leverage",
        "liquidation_enabled",
        "liquidation_trigger_ratio",
        "bar_adaptive_high_low_ordering",
        "liquidity_consumption",
        "queue_position",
    ]
    concepts = {name: (name in text) for name in concept_names}
    return {
        "status": "performed",
        "source_read": True,
        "source_path": "external:nautilus_trader/backtest/config.py",
        "concepts": concepts,
        "notes": [
            "Source inspection is advisory only and does not import exchange adapters.",
            "The inspected config source exposes simulator knobs relevant to fill, bar path, margin, and liquidation review.",
        ],
    }


def _nautilus_probe(
    *,
    isolated_environment_used: bool,
    isolated_install_command: str | None,
) -> dict[str, Any]:
    version = None
    metadata_available = False
    try:
        version = importlib.metadata.version("nautilus_trader")
        metadata_available = True
    except importlib.metadata.PackageNotFoundError:
        pass

    source_inspection = _nautilus_source_inspection()
    backtest_api_importable = False
    import_error = None
    try:
        importlib.import_module("nautilus_trader.backtest.config")
        backtest_api_importable = True
    except Exception as exc:  # pragma: no cover - depends on local optional package state
        import_error = f"{type(exc).__name__}: {exc}"

    return {
        "candidate": "NautilusTrader",
        "metadata_available": metadata_available,
        "version": version,
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "isolated_environment_used": isolated_environment_used,
        "isolated_install_command": isolated_install_command,
        "dependency_files_changed": False,
        "backtest_api_importable": backtest_api_importable,
        "backtest_api_import_error": import_error,
        "source_inspection": source_inspection,
        "offline_backtest_executed": False,
        "offline_backtest_blocked_reason": (
            "Safe repo-specific Nautilus strategy/data mapping was not implemented in this blocked pilot."
            if backtest_api_importable
            else "NautilusTrader backtest API could not be imported in the available process."
        ),
    }


def _reconciliation(fixture: dict[str, Any], nautilus: dict[str, Any]) -> dict[str, Any]:
    attempted = fixture["selected_variant_count"] if nautilus["offline_backtest_executed"] else 0
    expressible = fixture["selected_variant_count"] if nautilus["offline_backtest_executed"] else 0
    return {
        "variants_attempted": attempted,
        "variants_expressible": expressible,
        "rp_variants_available": fixture["selected_variant_count"],
        "trade_count_comparison": "not_performed",
        "final_equity_return_comparison": "not_performed",
        "cost_model_differences": [
            "Nautilus source exposes fee_model, but no run established repo fee parity.",
        ],
        "fill_model_differences": [
            "Nautilus source exposes bar_execution/fill_model/bar path controls; no run established repo next-open parity.",
        ],
        "margin_liquidation_differences": [
            "Nautilus source exposes margin_model and liquidation_enabled controls; no run established repo zero-equity parity.",
        ],
        "funding_differences": [
            "RP-2592 funding metrics are zero; no Nautilus funding cashflow mapping was executed.",
        ],
        "bar_timing_differences": [
            "Repo fixture records next_open_close_mark assumptions; Nautilus bar processing order was source-inspected only.",
        ],
        "unexplained_differences": [
            "No simulator metrics were produced because no Nautilus offline backtest executed."
        ],
        "integration_burden": "unmeasured_until_safe_offline_backtest_mapping_is_implemented",
    }


def _determinism(nautilus: dict[str, Any]) -> dict[str, Any]:
    if not nautilus["offline_backtest_executed"]:
        return {
            "repeated_runs": False,
            "byte_identical": False,
            "normalized_identical": False,
            "checksum": None,
            "result": "not_established",
            "reason": "NautilusTrader offline backtest did not execute.",
        }
    return {
        "repeated_runs": False,
        "byte_identical": False,
        "normalized_identical": False,
        "checksum": None,
        "result": "not_established",
        "reason": "determinism branch not implemented for this blocked pilot",
    }


def build_report(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    strategy_spec_path: Path = DEFAULT_STRATEGY_SPEC,
    variant_manifest_path: Path = DEFAULT_VARIANT_MANIFEST,
    sweep_plan_path: Path = DEFAULT_SWEEP_PLAN,
    d4_catalog_path: Path = DEFAULT_D4_CATALOG,
    isolated_environment_used: bool = False,
    isolated_install_command: str | None = None,
) -> dict[str, Any]:
    fixture = _fixture_summary(
        rp_path=rp_fixture_path,
        spec_path=strategy_spec_path,
        manifest_path=variant_manifest_path,
        sweep_path=sweep_plan_path,
        catalog_path=d4_catalog_path,
    )
    nautilus = _nautilus_probe(
        isolated_environment_used=isolated_environment_used,
        isolated_install_command=isolated_install_command,
    )
    recommendation = "EXPLORATION_ONLY" if nautilus["offline_backtest_executed"] else "BLOCKED"
    report: dict[str, Any] = {
        "labels": NON_CANONICAL_LABELS,
        "package_id": PACKAGE_ID,
        "fixture": fixture,
        "simulator_candidate": nautilus,
        "jesse_concept_source": {
            "used": False,
            "installed_or_executed": False,
            "status": "deferred",
            "reason": "Jesse was not installed or needed after Nautilus execution was blocked.",
        },
        "offline_guard": {
            "exchange_sandbox_live_connection_used": False,
            "credentials_used": False,
            "private_order_account_methods_used": False,
            "source_guard": _source_guard(),
        },
        "reconciliation": _reconciliation(fixture, nautilus),
        "determinism": _determinism(nautilus),
        "boundary_statement": {
            "external_dependency_added_to_repo": False,
            "canonical_result_population_write": False,
            "strategy_spec_mutation": False,
            "variant_manifest_mutation": False,
            "sweep_plan_mutation": False,
            "runner_backtester_changed": False,
            "oms_risk_reconciliation_changed": False,
            "runtime_paper_live_touched": False,
            "screen_gate_authority_created": False,
            "promotion_readiness_authority_created": False,
            "candidate_evidence_authority_created": False,
            "machine_local_absolute_paths_in_outputs": False,
        },
        "decision_recommendation": recommendation,
        "broader_adoption_taxonomy": "blocked" if recommendation == "BLOCKED" else "exploration-only",
        "recommendation_rationale": (
            "NautilusTrader installed in isolation and source inspection found relevant simulator "
            "concepts, but no offline backtest produced simulator metrics in this package, so "
            "offline-only execution, reconciliation, and determinism are not established."
            if recommendation == "BLOCKED"
            else "NautilusTrader is importable, but this pilot has not established simulator parity."
        ),
        "next_gated_wp_suggestion": (
            "Narrow environment-compatibility and minimal Nautilus offline backtest spike on a machine "
            "where the optional binary modules are allowed to load; no repo dependency mutation."
        ),
    }
    report["output_checksum"] = _sha256_payload(report)
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    fixture = report["fixture"]
    sim = report["simulator_candidate"]
    rec = report["reconciliation"]
    det = report["determinism"]
    lines = [
        f"# {PACKAGE_ID} Scratch Simulator Pilot Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Recommendation: `{report['decision_recommendation']}`",
        f"Broader taxonomy: `{report['broader_adoption_taxonomy']}`",
        f"Output checksum: `{report['output_checksum']}`",
        "",
        "## Fixture",
        "",
        f"- Result Population: `{fixture['result_population_id']}`",
        f"- Strategy Spec: `{fixture['strategy_spec_id']}`",
        f"- Variant Manifest: `{fixture['variant_manifest_id']}`",
        f"- Sweep Plan: `{fixture['sweep_plan_id']}`",
        f"- Data slice: `{fixture['data_slice_identity']}`",
        f"- Variants: `{fixture['selected_variant_count']}`",
        "",
        "## NautilusTrader Probe",
        "",
        f"- Metadata available: `{sim['metadata_available']}`",
        f"- Version: `{sim['version']}`",
        f"- Isolated environment used: `{sim['isolated_environment_used']}`",
        f"- Install command: `{sim['isolated_install_command']}`",
        f"- Backtest API importable: `{sim['backtest_api_importable']}`",
        f"- Import error: `{sim['backtest_api_import_error']}`",
        f"- Source inspection: `{sim['source_inspection']['status']}`",
        f"- Offline backtest executed: `{sim['offline_backtest_executed']}`",
        "",
        "## Reconciliation",
        "",
        f"- Variants attempted: `{rec['variants_attempted']}`",
        f"- Variants expressible: `{rec['variants_expressible']}`",
        f"- Trade count comparison: `{rec['trade_count_comparison']}`",
        f"- Final equity / return comparison: `{rec['final_equity_return_comparison']}`",
        f"- Integration burden: `{rec['integration_burden']}`",
        "",
        "## Determinism",
        "",
        f"- Repeated runs: `{det['repeated_runs']}`",
        f"- Byte-identical: `{det['byte_identical']}`",
        f"- Normalized-identical: `{det['normalized_identical']}`",
        f"- Result: `{det['result']}`",
        "",
        "## Boundary",
        "",
    ]
    for key, value in sorted(report["boundary_statement"].items()):
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Rationale",
            "",
            report["recommendation_rationale"],
            "",
        ]
    )
    return "\n".join(lines)


def run_pilot(
    *,
    rp_fixture_path: Path = DEFAULT_RP_FIXTURE,
    strategy_spec_path: Path = DEFAULT_STRATEGY_SPEC,
    variant_manifest_path: Path = DEFAULT_VARIANT_MANIFEST,
    sweep_plan_path: Path = DEFAULT_SWEEP_PLAN,
    d4_catalog_path: Path = DEFAULT_D4_CATALOG,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    isolated_environment_used: bool = False,
    isolated_install_command: str | None = None,
) -> dict[str, Any]:
    report = build_report(
        rp_fixture_path=rp_fixture_path,
        strategy_spec_path=strategy_spec_path,
        variant_manifest_path=variant_manifest_path,
        sweep_plan_path=sweep_plan_path,
        d4_catalog_path=d4_catalog_path,
        isolated_environment_used=isolated_environment_used,
        isolated_install_command=isolated_install_command,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    md_text = _markdown_report(report)
    _assert_portable_text(json_text)
    _assert_portable_text(md_text)
    (output_dir / "simulator_pilot_report.json").write_text(json_text, encoding="utf-8")
    (output_dir / "simulator_pilot_report.md").write_text(md_text, encoding="utf-8")
    (output_dir / "simulator_pilot_report.sha256").write_text(
        report["output_checksum"] + "\n", encoding="utf-8"
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rp-fixture", type=Path, default=DEFAULT_RP_FIXTURE)
    parser.add_argument("--strategy-spec", type=Path, default=DEFAULT_STRATEGY_SPEC)
    parser.add_argument("--variant-manifest", type=Path, default=DEFAULT_VARIANT_MANIFEST)
    parser.add_argument("--sweep-plan", type=Path, default=DEFAULT_SWEEP_PLAN)
    parser.add_argument("--d4-catalog", type=Path, default=DEFAULT_D4_CATALOG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--isolated-environment-used", action="store_true")
    parser.add_argument("--isolated-install-command", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_pilot(
            rp_fixture_path=args.rp_fixture,
            strategy_spec_path=args.strategy_spec,
            variant_manifest_path=args.variant_manifest,
            sweep_plan_path=args.sweep_plan,
            d4_catalog_path=args.d4_catalog,
            output_dir=args.output_dir,
            isolated_environment_used=args.isolated_environment_used,
            isolated_install_command=args.isolated_install_command,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "fixture": report["fixture"]["result_population_id"],
                "nautilus_version": report["simulator_candidate"]["version"],
                "nautilus_backtest_api_importable": report["simulator_candidate"][
                    "backtest_api_importable"
                ],
                "offline_backtest_executed": report["simulator_candidate"][
                    "offline_backtest_executed"
                ],
                "recommendation": report["decision_recommendation"],
                "output_checksum": report["output_checksum"],
                "output_dir": _portable_path(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
