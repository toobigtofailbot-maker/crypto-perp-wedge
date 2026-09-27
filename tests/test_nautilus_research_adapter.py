from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

from tools.execution_evidence_contract import build_run_request, validate_result_envelope
from tools.execution_evidence_legacy_rp import project_result_population_v1
from tools.nautilus_adapter import research


REPO_ROOT = Path(__file__).resolve().parents[1]
RP_PATH = REPO_ROOT / "research/result_populations/RP-2592.result_population.json"
CSV_PATH = (
    REPO_ROOT
    / "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv"
)


def _load(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def _inputs() -> research.ResolvedResearchInputs:
    rp = _load("research/result_populations/RP-2592.result_population.json")
    request, _ = project_result_population_v1(rp)
    return research.ResolvedResearchInputs(
        run_request=request,
        strategy_spec=_load("research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json"),
        variant_manifest=_load("research/variant_manifests/VM-0004.variant_manifest.json"),
        sweep_plan=_load("research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json"),
        result_population=rp,
        ohlcv_path=CSV_PATH,
        repo_commit="unit-test-head",
    )


@pytest.fixture(autouse=True)
def _fast_scientific_inputs(monkeypatch):
    expected_rows, expected_sha = research._expected_csv_facts(_inputs().result_population)
    monkeypatch.setattr(research, "_file_sha256", lambda path: expected_sha)
    monkeypatch.setattr(research, "_csv_data_row_count", lambda path: expected_rows)
    index = pd.date_range("2026-01-01", periods=4, freq="15min", tz="UTC")
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [10.0] * 4,
            "close_time_ms": [1577837699999 + index * 900000 for index in range(4)],
        },
        index=index,
    )
    monkeypatch.setattr(research, "_load_ohlcv", lambda path: frame.copy(deep=True))
    monkeypatch.setattr(
        research,
        "compile_signal",
        lambda strategy_spec, variant, ohlcv: pd.Series(0.0, index=ohlcv.index),
    )


def _fake_executor(inputs, ohlcv, signals, *, error_variant=None):
    result = {
        variant_id: (
            {"error": {"category": "test_error", "message_class": "TestError"}}
            if variant_id == error_variant
            else {
                "final_equity": 10_001.0,
                "return_pct": 0.0001,
                "trade_count": 1,
                "combined_fee_slippage_cost": 5.0,
                "funding": 0.0,
            }
        )
        for variant_id in inputs.run_request["declared_variant_ids"]
    }
    result["_environment"] = {
        "nautilus_version": "test",
        "python_version": "test",
        "platform": "test",
        "next_bar_open_execution_proven": False,
    }
    return result


def test_import_without_nautilus_and_public_constants() -> None:
    assert research.NAUTILUS_TARGET_VERSION == "1.231.0"
    assert research.ADAPTER_ID == "cpw_nautilus_research_adapter_v1"
    assert research.SUPPORTED_PROFILE == "cpw_nautilus_n1_01_rp2592_profile_v1"
    assert not any(name == "nautilus_trader" for name in sys.modules)


def test_exact_run_request_is_required() -> None:
    inputs = _inputs()
    invalid = copy.deepcopy(dict(inputs.run_request))
    invalid["determinism"]["seed"] = 999
    with pytest.raises(research.NautilusAdapterError, match="invalid CANON RunRequest"):
        research.validate_resolved_inputs(
            research.ResolvedResearchInputs(**{**inputs.__dict__, "run_request": invalid})
        )


@pytest.mark.parametrize(
    "field,mutator",
    [
        ("strategy_spec", lambda value: value.__setitem__("strategy_spec_id", "WRONG")),
        ("strategy_spec", lambda value: value.__setitem__("title", "changed")),
        ("variant_manifest", lambda value: value.__setitem__("variant_manifest_id", "WRONG")),
        ("variant_manifest", lambda value: value["variant_assignments"][0].__setitem__("parameter_values", {})),
        ("sweep_plan", lambda value: value.__setitem__("sweep_plan_id", "WRONG")),
        ("sweep_plan", lambda value: value["test_selection"]["selected_variant_ids"].reverse()),
    ],
)
def test_parent_id_hash_and_variant_order_mismatches_fail(field, mutator) -> None:
    inputs = _inputs()
    changed = copy.deepcopy(getattr(inputs, field))
    mutator(changed)
    with pytest.raises(research.NautilusAdapterError):
        research.validate_resolved_inputs(
            research.ResolvedResearchInputs(**{**inputs.__dict__, field: changed})
        )


def test_denominator_data_and_assumption_mismatches_fail() -> None:
    inputs = _inputs()
    for replacement in (
        {"committed_denominator": 7},
        {"data_identity": {**inputs.run_request["data_identity"], "timeframe": "1h"}},
        {
            "scientific_assumptions": {
                **inputs.run_request["scientific_assumptions"],
                "sizing_metadata": {**research._EXPECTED_SIZING, "target_leverage": 2.0},
            }
        },
    ):
        request_args = {
            key: copy.deepcopy(inputs.run_request[key])
            for key in (
                "parent_identities",
                "declared_variant_ids",
                "committed_denominator",
                "data_identity",
                "determinism",
                "scientific_assumptions",
            )
        }
        request_args.update(replacement)
        if request_args["committed_denominator"] != len(request_args["declared_variant_ids"]):
            request_args["declared_variant_ids"] = request_args["declared_variant_ids"][:7]
        changed_request = build_run_request(**request_args)
        with pytest.raises(research.NautilusAdapterError):
            research.validate_resolved_inputs(
                research.ResolvedResearchInputs(
                    **{**inputs.__dict__, "run_request": changed_request}
                )
            )


def test_nonzero_funding_profile_fails_closed() -> None:
    inputs = _inputs()
    rp = copy.deepcopy(inputs.result_population)
    rp["variant_result_rows"][0]["metrics"]["funding"] = 1.0
    with pytest.raises(research.NautilusAdapterError):
        research.validate_resolved_inputs(
            research.ResolvedResearchInputs(**{**inputs.__dict__, "result_population": rp})
        )


def test_fake_executor_builds_valid_full_denominator_envelope() -> None:
    inputs = _inputs()
    result = research.execute_nautilus_research(inputs, executor=_fake_executor)
    validate_result_envelope(result.result_envelope)
    rows = result.result_envelope["scientific_result"]["variant_result_rows"]
    assert [row["variant_id"] for row in rows] == inputs.run_request["declared_variant_ids"]
    assert len(rows) == inputs.run_request["committed_denominator"] == 8


def test_fake_variant_error_remains_as_errored_denominator_row() -> None:
    inputs = _inputs()
    result = research.execute_nautilus_research(
        inputs,
        executor=lambda *args: _fake_executor(*args, error_variant="VAR-000004"),
    )
    rows = result.result_envelope["scientific_result"]["variant_result_rows"]
    assert len(rows) == 8
    assert rows[3]["variant_id"] == "VAR-000004"
    assert rows[3]["outcome_category"] == "errored"
    assert result.result_envelope["scientific_result"]["outcome_category_counts"]["errored"] == 1


def test_provenance_does_not_change_evidence_identity() -> None:
    inputs = _inputs()
    left = research.execute_nautilus_research(
        inputs, executor=_fake_executor, execution_provenance={"repo_commit": "left"}
    )
    right = research.execute_nautilus_research(
        inputs, executor=_fake_executor, execution_provenance={"repo_commit": "right"}
    )
    assert left.result_envelope["evidence_content_sha256"] == right.result_envelope[
        "evidence_content_sha256"
    ]
    assert left.result_envelope["execution_provenance"] != right.result_envelope[
        "execution_provenance"
    ]


def test_source_artifacts_are_not_mutated() -> None:
    inputs = _inputs()
    before = copy.deepcopy(inputs)
    research.execute_nautilus_research(inputs, executor=_fake_executor)
    assert inputs == before


def test_module_exposes_no_writer_and_keeps_forbidden_imports_unreachable() -> None:
    public_names = {name for name in dir(research) if not name.startswith("_")}
    assert not public_names & {"write", "persist", "cross", "canonical_write"}
    tree = ast.parse(Path(research.__file__).read_text(encoding="utf-8"))
    top_level_imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_level_imports.append(node.module)
    forbidden = ("nautilus_trader", "src.runtime", "paper", "live", "requests", "httpx", "urllib")
    assert not [name for name in top_level_imports if name.startswith(forbidden)]
