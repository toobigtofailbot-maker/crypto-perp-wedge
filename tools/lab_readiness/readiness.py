"""Build the deterministic read-only lab readiness projection.

This module reads committed repo metadata only. It does not import or invoke
network/provider clients, does not call the runner, and does not write files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.lab_readiness.model import (
    NON_AUTHORITY_DECLARATION,
    READINESS_STATUSES,
    SCHEMA_VERSION,
    ReadinessItem,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
AVAILABILITY_CATALOG_PATH = (
    REPO_ROOT
    / "research"
    / "data_feature_availability"
    / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
)
INDICATOR_CATALOG_PATH = (
    REPO_ROOT / "research" / "indicator_catalogs" / "IND-CATALOG-0001.indicator_catalog.json"
)
COMPILER_PATH = REPO_ROOT / "tools" / "research_runner" / "spec_signal_compiler.py"
RUNNER_PATH = REPO_ROOT / "tools" / "research_runner" / "run_offline_sweep.py"
BACKTEST_PATH = REPO_ROOT / "lib" / "backtest.py"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _text_contains(path: Path, *needles: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return all(needle in text for needle in needles)


def _availability_index(catalog: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    if not isinstance(catalog, dict):
        return index
    for entry in catalog.get("entries", []):
        if isinstance(entry, dict) and isinstance(entry.get("feature_name"), str):
            index.setdefault(entry["feature_name"], []).append(entry)
    return index


def _indicator_ids(catalog: dict[str, Any] | None) -> set[str]:
    if not isinstance(catalog, dict):
        return set()
    return {
        str(entry["indicator_id"])
        for entry in catalog.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("indicator_id"), str)
    }


def _availability_support(feature: str, index: dict[str, list[dict[str, Any]]]) -> list[str]:
    rows = index.get(feature, [])
    if not rows:
        return ["availability catalog row not found"]
    return [
        (
            f"{row.get('feature_name')} / {row.get('source_class')} / "
            f"{row.get('coverage_class')} / full_history={row.get('canonical_full_history_allowed')}"
        )
        for row in rows
    ]


def _base_repo_support(repo_root: Path = REPO_ROOT) -> dict[str, bool]:
    compiler_path = repo_root / "tools" / "research_runner" / "spec_signal_compiler.py"
    runner_path = repo_root / "tools" / "research_runner" / "run_offline_sweep.py"
    backtest_path = repo_root / "lib" / "backtest.py"
    return {
        "compiler_builtin_indicators": _text_contains(
            compiler_path,
            "APPROVED_BUILTINS",
            "sma_v1",
            "ema_v1",
            "donchian_v1",
            "rvol_v1",
            "rolling_vwap_v1",
        ),
        "compiler_timestamp_fields": _text_contains(
            compiler_path,
            "ALLOWED_TIMESTAMP_DERIVED_FIELDS",
            "hour_of_day_utc",
            "day_of_week_utc",
            "is_weekend_utc",
        ),
        "runner_declared_non_ohlcv": _text_contains(
            runner_path,
            "_declared_non_ohlcv_columns",
            "data_availability_claim",
        ),
        "runner_canonical_real_data": _text_contains(
            runner_path,
            "canonical_15m",
            "canonical_4h",
            "canonical_real_data",
            "compile_signal",
        ),
        "backtest_funding_opt_in": _text_contains(
            backtest_path,
            "funding_cost_mode",
            "_FUNDING_COST_MODE_ON",
        ),
        "backtest_close_mark_only": _text_contains(
            backtest_path,
            "mark_price_source",
            "external mark/index data",
            "not supported here",
        ),
        "backtest_realism_disclosures": _text_contains(
            backtest_path,
            "fill_mode",
            "liquidity_cap_fraction",
            "liquidation_mode",
            "bar_path_assumption",
        ),
    }


def _item(
    *,
    subject_id: str,
    label: str,
    feature_or_family: str,
    status: str,
    reason_code: str,
    evidence: list[str],
    support: list[str],
    blocker: str,
    next_category: str,
) -> ReadinessItem:
    return ReadinessItem(
        subject_id=subject_id,
        label=label,
        feature_or_family=feature_or_family,
        status=status,
        reason_code=reason_code,
        required_source_evidence=evidence,
        current_repo_support=support,
        blocker_detail=blocker,
        next_prerequisite_category=next_category,
    )


def build_readiness_items(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Return deterministic readiness rows for the required lab intake coverage."""

    availability = _availability_index(
        _read_json(
            repo_root
            / "research"
            / "data_feature_availability"
            / "PERP-DERIVED-FEATURE-AVAILABILITY-0001.json"
        )
    )
    indicator_ids = _indicator_ids(
        _read_json(repo_root / "research" / "indicator_catalogs" / "IND-CATALOG-0001.indicator_catalog.json")
    )
    support = _base_repo_support(repo_root)

    indicator_support = [
        f"indicator catalog active ids={','.join(sorted(indicator_ids)) or 'none'}",
        f"compiler builtins present={support['compiler_builtin_indicators']}",
        f"offline real-data runner path present={support['runner_canonical_real_data']}",
    ]

    rows = [
        _item(
            subject_id="READINESS-OHLCV-INDICATORS",
            label="OHLCV-only indicators",
            feature_or_family="ohlcv_indicators",
            status=(
                "testable_now_with_current_public_history"
                if {"sma", "ema", "stddev", "rsi", "donchian", "rvol", "rolling_vwap"} <= indicator_ids
                and support["compiler_builtin_indicators"]
                and support["runner_canonical_real_data"]
                else "unknown_needs_review"
            ),
            reason_code="OHLCV_INDICATOR_COMPILER_AND_OFFLINE_RUNNER_PRESENT",
            evidence=["BTCUSDT OHLCV public history/catalog lineage", "indicator catalog", "spec_signal_compiler builtins"],
            support=indicator_support,
            blocker="None for closed OHLCV builtin families on the offline research path; still not paper/live or promotion authority.",
            next_category="none_for_offline_research_display",
        ),
        _item(
            subject_id="READINESS-FUNDING-RATE-FEATURE-HISTORY",
            label="Funding-rate feature history",
            feature_or_family="funding_rate_feature",
            status="needs_local_full_history_materialization",
            reason_code="FUNDING_FEATURE_PUBLIC_HISTORY_CONDITIONAL_BUT_RUNNER_CSV_MISSING",
            evidence=["aligned funding_rate column covering the claimed evidence window", "data_availability_claim binding"],
            support=[
                *_availability_support("funding_rate", availability),
                f"runner declared non-OHLCV support present={support['runner_declared_non_ohlcv']}",
                "WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01 records runner-consumable funding-feature CSV as missing",
            ],
            blocker="Funding-rate values are cataloged as conditional public-archive history, but the runner-consumable full-history feature CSV is not created by this display.",
            next_category="local_full_history_materialization",
        ),
        _item(
            subject_id="READINESS-FUNDING-PNL-COST-REALISM",
            label="Funding PnL / cost realism",
            feature_or_family="funding_cost_realism",
            status="needs_runner_or_compiler_support",
            reason_code="FUNDING_CASHFLOW_CORE_OPT_IN_BUT_CANONICAL_RUNNER_PATH_NOT_WIRED",
            evidence=["funding_rate event frame aligned to execution window", "runner/backtester path with funding_cost_mode enabled"],
            support=[
                f"backtest funding opt-in present={support['backtest_funding_opt_in']}",
                "canonical runner execution inputs currently use zero_funding_for_ohlcv on the inspected paths",
                "funding_cost_mode is default-off and prior funding NO-GO docs warn price-PnL funding signal tests were not funding-carry-PnL tests",
            ],
            blocker="Backtest core can model opt-in funding cashflows, but current canonical runner inputs do not supply real funding events for a full funding-carry PnL claim.",
            next_category="runner_support_and_local_funding_materialization",
        ),
        _item(
            subject_id="READINESS-TAKER-FLOW-D4-NATIVE",
            label="Taker-flow canonical five-timeframe support",
            feature_or_family="taker_flow",
            status="needs_local_full_history_materialization",
            reason_code="TAKER_FLOW_CANONICAL_DERIVATION_CONDITIONAL_NOT_MATERIALIZED",
            evidence=[
                "exact legacy 15m canonical D4 parent identity",
                "exact D2-021 canonical 30m/1h/4h/1d parent identity",
                "deterministic row-local feature table and provenance-bound manifest",
            ],
            support=[
                *_availability_support("taker_buy_sell_ratio", availability),
                *_availability_support("taker_buy_volume", availability),
                *_availability_support("taker_sell_volume", availability),
                f"runner declared non-OHLCV support present={support['runner_declared_non_ohlcv']}",
            ],
            blocker="Repo truth permits conditional legacy 15m D4 and D2-021 canonical-kline derivation for 30m/1h/4h/1d, but a local provenance-bound feature table must be materialized before use.",
            next_category="local_full_history_materialization",
        ),
        _item(
            subject_id="READINESS-OPEN-INTEREST",
            label="Open interest",
            feature_or_family="open_interest",
            status="needs_vendor_or_captured_history",
            reason_code="OPEN_INTEREST_NOT_PUBLIC_FULL_HISTORY",
            evidence=["vendor or captured historical open-interest dataset with provenance"],
            support=[
                *_availability_support("open_interest", availability),
                *_availability_support("open_interest_value", availability),
            ],
            blocker="Current open interest is snapshot/recent-only in repo truth; trades or aggregate trades cannot reconstruct true open interest.",
            next_category="vendor_or_captured_history",
        ),
        _item(
            subject_id="READINESS-LONG-SHORT-RATIO",
            label="Long/short ratio",
            feature_or_family="long_short_ratio",
            status="needs_vendor_or_captured_history",
            reason_code="LONG_SHORT_RATIO_PUBLIC_REST_RECENT_ONLY",
            evidence=["vendor or captured historical long/short ratio dataset with alignment provenance"],
            support=[
                *_availability_support("top_trader_position_long_short_ratio", availability),
                *_availability_support("top_trader_account_long_short_ratio", availability),
                *_availability_support("global_long_short_account_ratio", availability),
            ],
            blocker="Public long/short ratio endpoints are recent-only under the committed availability labels and cannot support full-history evidence without an override dataset.",
            next_category="vendor_or_captured_history",
        ),
        _item(
            subject_id="READINESS-LIQUIDATION-HISTORY",
            label="Liquidation volume/history",
            feature_or_family="liquidation_history",
            status="needs_vendor_or_captured_history",
            reason_code="LIQUIDATION_VOLUME_VENDOR_ONLY_AND_NOT_COMPILER_VISIBLE",
            evidence=["vendor or captured historical liquidation dataset", "future compiler/runner binding if used in signals"],
            support=_availability_support("liquidation_volume", availability),
            blocker="The catalog keeps liquidation_volume vendor-only for history and not compiler-visible; simulator liquidation assumptions are not liquidation-volume data.",
            next_category="vendor_or_captured_history_then_runner_or_compiler_support",
        ),
        _item(
            subject_id="READINESS-L2-ORDERBOOK",
            label="L2 / order-book features",
            feature_or_family="order_book_microstructure",
            status="needs_vendor_or_captured_history",
            reason_code="NO_COMMITTED_L2_HISTORY_OR_COMPILER_BINDING",
            evidence=["captured or vendor historical L2/order-book dataset", "separately authorized microstructure compiler/runner/simulator support"],
            support=["no committed L2/order-book availability catalog row found", "no inspected runner/backtester path consumes order-book depth"],
            blocker="No repo-truth full-history L2 source or Strategy Spec/compiler binding exists for order-book features.",
            next_category="vendor_or_captured_history_and_runner_or_compiler_support",
        ),
        _item(
            subject_id="READINESS-MARK-INDEX-PREMIUM-FIELDS",
            label="Mark / index / premium index fields",
            feature_or_family="mark_index_premium_fields",
            status="needs_local_full_history_materialization",
            reason_code="CONDITIONAL_PUBLIC_ARCHIVE_FIELDS_NEED_ALIGNED_RUNNER_COLUMNS",
            evidence=["aligned mark/index/premium history for the evidence window", "irreparable-gap policy handling", "declared runner columns"],
            support=[
                *_availability_support("mark_price", availability),
                *_availability_support("index_price", availability),
                *_availability_support("premium_index", availability),
                f"backtest close-only mark source enforced={support['backtest_close_mark_only']}",
            ],
            blocker="These fields are conditional public-archive data features for signal use when aligned and materialized; the backtester still marks/liquidates on close, not external mark/index data.",
            next_category="local_full_history_materialization_for_signal_features_or_simulator_realism_upgrade_for_marking",
        ),
        _item(
            subject_id="READINESS-UTC-TIME-FIELDS",
            label="UTC/session/time-derived fields",
            feature_or_family="time_session_fields",
            status="testable_now_with_current_public_history",
            reason_code="TIMESTAMP_FIELDS_AND_SESSION_PRIMITIVES_PRESENT",
            evidence=["UTC bar timestamp from aligned OHLCV bars", "Strategy Spec session/time primitives when used"],
            support=[
                *_availability_support("hour_of_day_utc", availability),
                *_availability_support("day_of_week_utc", availability),
                *_availability_support("is_weekend_utc", availability),
                f"compiler timestamp/session support present={support['compiler_timestamp_fields']}",
            ],
            blocker="No data blocker for UTC-derived fields when source bars exist; complex session behavior remains offline research only.",
            next_category="none_for_offline_research_display",
        ),
        _item(
            subject_id="READINESS-DONCHIAN-BREAKOUT",
            label="Donchian / breakout family",
            feature_or_family="donchian_breakout",
            status="testable_now_with_current_public_history",
            reason_code="DONCHIAN_AND_CROSSOVER_COMPILER_SUPPORT_PRESENT",
            evidence=["OHLCV high/low history", "donchian_v1 indicator", "closed crossover/comparison operators"],
            support=indicator_support,
            blocker="No data blocker for closed Donchian/OHLCV breakout variants on the offline research path; not a candidate or promotion claim.",
            next_category="none_for_offline_research_display",
        ),
        _item(
            subject_id="READINESS-SMA-STDDEV-MEAN-REVERSION",
            label="SMA / StdDev mean-reversion",
            feature_or_family="sma_stddev_mean_reversion",
            status="testable_now_with_current_public_history",
            reason_code="SMA_STDDEV_ZSCORE_COMPILER_SUPPORT_PRESENT",
            evidence=["OHLCV close history", "sma_v1 and stddev_v1 indicators", "z_score composed operand when specified"],
            support=indicator_support,
            blocker="No data blocker for closed SMA/StdDev OHLCV variants on the offline research path; trial/candidate authority remains separate.",
            next_category="none_for_offline_research_display",
        ),
        _item(
            subject_id="READINESS-EMA-RVOL-VWAP-SESSION",
            label="EMA / RVOL / rolling VWAP / session families",
            feature_or_family="ema_rvol_vwap_session",
            status="testable_now_with_current_caveats",
            reason_code="SUPPORTED_BUILTINS_WITH_CAVEATED_VWAP_AND_SESSION_SEMANTICS",
            evidence=["OHLCV history", "ema_v1, rvol_v1, rolling_vwap_v1 indicator interfaces", "session primitives when declared"],
            support=indicator_support + ["rolling_vwap_v1 is candle OHLCV approximation, not true trade-level VWAP"],
            blocker="EMA/RVOL/session are closed offline compiler surfaces; rolling VWAP is a candle approximation and must not be represented as true trade-level VWAP.",
            next_category="none_for_offline_research_display_or_taker_trade_history_for_true_vwap",
        ),
        _item(
            subject_id="READINESS-SIMULATOR-PAPER-SHADOW-BOUNDARY",
            label="Simulator realism / paper-shadow phase boundary",
            feature_or_family="simulator_realism_boundary",
            status="go_gated_or_paper_phase_only",
            reason_code="PAPER_LIVE_RUNTIME_REMAINS_PROTECTED_AND_HUMAN_GATED",
            evidence=["explicit later GO package for paper/shadow/runtime contact", "protected runtime review"],
            support=[
                f"backtest realism disclosures present={support['backtest_realism_disclosures']}",
                "LAB_COMPLETION_MAP records paper/live/runtime as GO-gated protected",
            ],
            blocker="Offline simulator realism disclosures do not authorize paper/shadow/live, runtime, OMS, risk, broker/exchange, or autonomous dispatch.",
            next_category="protected_phase_gate",
        ),
    ]

    return [row.to_dict() for row in rows]


def build_readiness_projection(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    items = build_readiness_items(repo_root=repo_root)
    by_status = {status: 0 for status in READINESS_STATUSES}
    for item in items:
        by_status[item["status"]] += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "surface_kind": "read_only_data_sim_readiness_display",
        "item_count": len(items),
        "status_taxonomy": list(READINESS_STATUSES),
        "summary_by_status": by_status,
        "items": items,
        "non_authority_declaration": dict(NON_AUTHORITY_DECLARATION),
        "source_files": [
            "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json",
            "research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json",
            "tools/research_runner/spec_signal_compiler.py",
            "tools/research_runner/run_offline_sweep.py",
            "lib/backtest.py",
            "docs/research/LAB_COMPLETION_MAP.md",
        ],
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Lab Data / Simulator Readiness Display",
        "",
        "Read-only readiness display only; no data acquisition, runner/compiler behavior change, execution, candidate, crossing, promotion, paper/live/runtime, provider/API, credential, dependency, config, or protected-path authority.",
        "",
        "## Taxonomy",
        "",
    ]
    lines.extend(f"- `{status}`: {data['summary_by_status'][status]}" for status in data["status_taxonomy"])
    lines.extend(["", "## Items", ""])
    for item in data["items"]:
        lines.extend(
            [
                f"### {item['label']}",
                "",
                f"- `subject_id`: `{item['subject_id']}`",
                f"- `feature_or_family`: `{item['feature_or_family']}`",
                f"- `status`: `{item['status']}`",
                f"- `reason_code`: `{item['reason_code']}`",
                f"- `blocker_detail`: {item['blocker_detail']}",
                f"- `next_prerequisite_category`: `{item['next_prerequisite_category']}`",
                f"- `non_authority_flags`: {', '.join(f'`{flag}`' for flag in item['non_authority_flags'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
