from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest


nautilus_trader = pytest.importorskip(
    "nautilus_trader",
    reason="isolated Python 3.12 environment with NautilusTrader 1.231.0 is required",
)

from tools.execution_evidence_contract import validate_result_envelope
from tools.execution_evidence_legacy_rp import project_result_population_v1
from tools.nautilus_adapter import research


REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = (
    REPO_ROOT
    / "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
)


def _load(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def _resolved_inputs() -> research.ResolvedResearchInputs:
    rp = _load("research/result_populations/RP-2592.result_population.json")
    request, _ = project_result_population_v1(rp)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return research.ResolvedResearchInputs(
        run_request=request,
        strategy_spec=_load("research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"),
        variant_manifest=_load("research/variant_manifests/VM-0004.variant_manifest.json"),
        sweep_plan=_load("research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"),
        result_population=rp,
        ohlcv_path=CSV_PATH,
        repo_commit=head,
    )


def test_exact_environment_version_gate() -> None:
    assert nautilus_trader.__version__ == "1.231.0"
    assert research.sys.version_info[:2] == (3, 12)


def test_next_bar_open_micro_proof_is_exact_and_repeatable() -> None:
    index = pd.date_range("2026-01-01T00:00:00Z", periods=3, freq="15min")
    frame = pd.DataFrame(
        {
            "open": [100.0, 125.0, 130.0],
            "high": [110.0, 130.0, 135.0],
            "low": [95.0, 115.0, 125.0],
            "close": [105.0, 120.0, 132.0],
            "volume": [1_000.0, 1_000.0, 1_000.0],
            "close_time_ms": [1767226499999, 1767227399999, 1767228299999],
        },
        index=index,
    )
    signal = pd.Series([1.0, 1.0, 1.0], index=index)
    variants = [{"variant_id": "MICRO", "parameter_values": {}}]
    first = research._execute_target_signals(variants, frame, {"MICRO": signal})["MICRO"]
    second = research._execute_target_signals(variants, frame, {"MICRO": signal})["MICRO"]
    expected_fill = {
        "side": "BUY",
        "price": 125.0,
        "quantity": 80.0,
        "ts_event_ns": 1767226500000000001,
    }
    assert first["fills"] == [expected_fill]
    assert second["fills"] == [expected_fill]


def test_full_rp2592_acceptance_is_deterministic() -> None:
    inputs = _resolved_inputs()
    research.validate_resolved_inputs(inputs)
    first = research.execute_nautilus_research(inputs)
    second = research.execute_nautilus_research(inputs)
    validate_result_envelope(first.result_envelope)
    validate_result_envelope(second.result_envelope)
    first_science = first.result_envelope["scientific_result"]
    second_science = second.result_envelope["scientific_result"]
    assert first_science == second_science
    assert first.result_envelope["evidence_content_sha256"] == second.result_envelope[
        "evidence_content_sha256"
    ]
    assert first.result_envelope["request_content_sha256"] == (
        "sha256:179ef4d8e20af186ead25e7b482175b441863070e4a90f4e7f02c0188cd9da01"
    )
    rows = first_science["variant_result_rows"]
    assert first_science["committed_denominator"] == len(rows) == 8
    assert first_science["outcome_category_counts"]["successful"] == 8
    assert all(row["outcome_category"] == "successful" for row in rows)
    assert [row["variant_id"] for row in rows] == inputs.run_request["declared_variant_ids"]
    assert [row["row_content_sha256"] for row in rows] == [
        row["row_content_sha256"] for row in second_science["variant_result_rows"]
    ]
    provenance = first.result_envelope["execution_provenance"]
    assert provenance["engine_id"] == "nautilus_trader"
    assert provenance["engine_version"] == "1.231.0"
    assert provenance["adapter_id"] == research.ADAPTER_ID
    assert set(first.semantic_gap_report) == {
        "next_bar_open_execution",
        "fee_slippage_split",
        "nonzero_funding",
        "dynamic_sizing_fixture_1x",
        "generalized_quantity_precision_parity",
        "direct_flip",
        "zero_equity_liquidation",
        "maintenance_margin",
    }
    assert first.semantic_gap_report == {
        "next_bar_open_execution": "PROVEN_FOR_N1_01",
        "dynamic_sizing_fixture_1x": "PROVEN_FOR_N1_01_FIXTURE",
        "fee_slippage_split": "NOT_PROVEN_IN_N1_01",
        "nonzero_funding": "NOT_PROVEN_IN_N1_01",
        "generalized_quantity_precision_parity": "NOT_PROVEN_IN_N1_01",
        "direct_flip": "NOT_PROVEN_IN_N1_01",
        "zero_equity_liquidation": "NOT_PROVEN_IN_N1_01",
        "maintenance_margin": "NOT_PROVEN_IN_N1_01",
    }
    print(
        json.dumps(
            {
                "request_content_sha256": inputs.run_request["request_content_sha256"],
                "run_1_evidence_content_sha256": first.result_envelope[
                    "evidence_content_sha256"
                ],
                "run_2_evidence_content_sha256": second.result_envelope[
                    "evidence_content_sha256"
                ],
            },
            sort_keys=True,
        )
    )
