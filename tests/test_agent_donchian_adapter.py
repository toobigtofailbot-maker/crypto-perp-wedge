from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import RUN_NONCANONICAL_OFFLINE_SWEEP
from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import validate_variant_sweep_artifacts
from tools.research_agents.formalizer_runner_bridge import (
    APPROVAL_SCOPE,
    DONCHIAN_ADAPTER_WP_ID,
    FormalizerRunnerBridge,
    FormalizerRunnerBridgeConfig,
    FormalizerRunnerBridgeError,
)
from tools.research_agents.idea_formalizer_agent import (
    AVAILABILITY_CATALOG_PATH,
    INDICATOR_CATALOG_PATH,
    STRATEGY_TEMPLATE_PATH,
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
)
from tools.research_agents.reasoning_providers import FakeOfflineProvider


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc)
IDEA = (
    "Because range expansion momentum persists, test BTCUSDT 15m price with a Donchian "
    "channel breakout; channel_lookback_bars from 20 to 55."
)


@pytest.fixture
def adapter_repo(tmp_path: Path) -> Path:
    for relative in (
        INDICATOR_CATALOG_PATH,
        AVAILABILITY_CATALOG_PATH,
        STRATEGY_TEMPLATE_PATH,
        Path("research/variant_manifests/VM-0003.variant_manifest.json"),
        Path("research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json"),
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    return tmp_path


def _context(role: str) -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(
            wp_id=DONCHIAN_ADAPTER_WP_ID,
            role=role,
            audit_sink=sink,
            clock=lambda: FIXED_TIME,
        ),
        sink,
    )


def _formalize(root: Path) -> tuple[dict, MemoryAuditSink]:
    context, sink = _context("idea_formalizer")
    agent = IdeaFormalizerAgent(
        config=IdeaFormalizerConfig(),
        tool_context=context,
        provider=FakeOfflineProvider(),
        repo_root=root,
    )
    return agent.run(idea=IDEA), sink


def _write_fixture(root: Path) -> str:
    relative = f"scratch/{DONCHIAN_ADAPTER_WP_ID}/fixtures/donchian_15m_ohlcv.csv"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    index = pd.date_range("2025-01-01T00:00:00Z", periods=360, freq="15min")
    cycle = [100.0] * 60 + list(range(101, 121)) + [120.0] * 20 + list(range(119, 79, -1))
    close = (cycle * 3)[: len(index)]
    pd.DataFrame(
        {
            "timestamp": index,
            "open": [value - 0.1 for value in close],
            "high": [value + 0.5 for value in close],
            "low": [value - 0.5 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        }
    ).to_csv(path, index=False)
    return relative


def _approve(root: Path, result: dict) -> str:
    formalizer_path = result["draft_strategy_spec"]["path"].rsplit("/", 1)[0]
    relative = f"{formalizer_path}/bridge_approval.json"
    path = root / relative
    path.write_text(
        json.dumps(
            {
                "approved_for_noncanonical_runner_bridge": True,
                "approved_by": "operator",
                "approval_scope": APPROVAL_SCOPE,
                "approval_timestamp_utc": "2026-06-23T12:00:00Z",
                "source_formalizer_run_id": result["run_id"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return relative


def _run_bridge(root: Path, formalized: dict) -> tuple[dict, MemoryAuditSink]:
    approval_path = _approve(root, formalized)
    fixture_path = _write_fixture(root)
    context, sink = _context("formalizer_runner_bridge")
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=root,
    )
    formalizer_path = (
        f"scratch/{DONCHIAN_ADAPTER_WP_ID}/formalizer/outputs/"
        f"{formalized['run_id']}/formalized_idea.json"
    )
    return (
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
        ),
        sink,
    )


def test_donchian_formalizer_is_deterministic_valid_and_distinct(adapter_repo: Path):
    first, sink = _formalize(adapter_repo)
    second, _ = _formalize(adapter_repo)

    assert first == second
    assert first["status"] == "accepted"
    assert first["adapter_metadata"]["family_id"] == "donchian_channel_breakout_v1"
    assert first["draft_strategy_spec"]["produced"] is True
    spec_path = adapter_repo / first["draft_strategy_spec"]["path"]
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    canonical = json.loads((adapter_repo / STRATEGY_TEMPLATE_PATH).read_text(encoding="utf-8"))
    assert validate_strategy_specs(strategy_specs_dir=spec_path.parent, repo_root=adapter_repo) == []
    assert spec["entry_logic"] != canonical["entry_logic"]
    assert '"ref": "donchian"' in json.dumps(spec)
    assert '"ref": "sma"' not in json.dumps(spec)
    assert '"ref": "stddev"' not in json.dumps(spec)
    assert set(first["adapter_metadata"]["freshness_distinct_from"]) >= {
        "STRAT-SPEC-0003",
        "RP-7134",
    }
    assert spec_path.is_relative_to(adapter_repo / "scratch" / DONCHIAN_ADAPTER_WP_ID)
    assert any(record.action_type == "run_read_only_validation" for record in sink.records)


def test_donchian_bridge_builds_two_variant_grid_and_runs_real_runner(adapter_repo: Path):
    formalized, _ = _formalize(adapter_repo)
    result, sink = _run_bridge(adapter_repo, formalized)

    assert result["status"] == "completed"
    assert result["manual_reconciliation_result"]["passed"] is True
    assert sum(result["trial_status_counts"].values()) == 2
    assert result["trial_status_counts"]["completed"] == 2
    inputs_dir = (adapter_repo / result["artifact_paths"]["strategy_spec"]).parent
    assert validate_strategy_specs(strategy_specs_dir=inputs_dir, repo_root=adapter_repo) == []
    assert (
        validate_variant_sweep_artifacts(
            strategy_specs_dir=inputs_dir,
            variant_manifests_dir=inputs_dir,
            sweep_plans_dir=inputs_dir,
        )
        == []
    )
    manifest = json.loads((adapter_repo / result["artifact_paths"]["variant_manifest"]).read_text())
    sweep = json.loads((adapter_repo / result["artifact_paths"]["sweep_plan"]).read_text())
    ledger = json.loads((adapter_repo / result["artifact_paths"]["denominator_ledger"]).read_text())
    assert manifest["variant_manifest_id"] != "VM-0003"
    assert manifest["parameter_axes"][0]["parameter_name"] == "channel_lookback_bars"
    assert [row["parameter_values"] for row in manifest["variant_assignments"]] == [
        {"channel_lookback_bars": 20},
        {"channel_lookback_bars": 55},
    ]
    assert sweep["sweep_plan_id"] != "SWEEP-PLAN-0003"
    assert sweep["trial_accounting"]["multiple_testing_denominator"] == 2
    assert ledger["denominator_preserved"] is True
    assert len(ledger["rows"]) == 2
    assert all(row["strategy_family"] == "donchian_channel_breakout_v1" for row in ledger["rows"])
    assert all(row["funding_cost_mode"] == "off" for row in ledger["rows"])
    assert any(
        record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP and record.decision == "allowed"
        for record in sink.records
    )


@pytest.mark.parametrize(
    "features",
    [
        ["sma", "stddev"],
        ["donchian", "sma", "stddev"],
    ],
)
def test_donchian_bridge_rejects_mismatched_or_ambiguous_family(
    adapter_repo: Path, features: list[str]
):
    formalized, _ = _formalize(adapter_repo)
    formalizer_path = (
        adapter_repo
        / "scratch"
        / DONCHIAN_ADAPTER_WP_ID
        / "formalizer"
        / "outputs"
        / formalized["run_id"]
        / "formalized_idea.json"
    )
    payload = json.loads(formalizer_path.read_text(encoding="utf-8"))
    payload["research_object"]["features"] = features
    formalizer_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    approval_path = _approve(adapter_repo, formalized)
    context, _ = _context("formalizer_runner_bridge")
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=_write_fixture(adapter_repo)),
        tool_context=context,
        repo_root=adapter_repo,
    )

    with pytest.raises(FormalizerRunnerBridgeError):
        bridge.run(
            formalizer_output_path=formalizer_path.relative_to(adapter_repo),
            approval_path=approval_path,
        )


def test_donchian_bridge_rejects_sma_indicator_refs(adapter_repo: Path):
    formalized, _ = _formalize(adapter_repo)
    draft_path = adapter_repo / formalized["draft_strategy_spec"]["path"]
    spec = json.loads(draft_path.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(spec)
    mutated["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["ref"] = "sma"
    mutated["entry_logic"]["groups"][0]["conditions"][0]["right_operand"]["field"] = "value"
    draft_path.write_text(json.dumps(mutated, indent=2) + "\n", encoding="utf-8")
    approval_path = _approve(adapter_repo, formalized)
    context, _ = _context("formalizer_runner_bridge")
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=_write_fixture(adapter_repo)),
        tool_context=context,
        repo_root=adapter_repo,
    )

    with pytest.raises(FormalizerRunnerBridgeError):
        bridge.run(
            formalizer_output_path=(
                f"scratch/{DONCHIAN_ADAPTER_WP_ID}/formalizer/outputs/"
                f"{formalized['run_id']}/formalized_idea.json"
            ),
            approval_path=approval_path,
        )


@pytest.mark.parametrize(
    "action_type,target_path",
    [
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("write_scratch", "research/variant_manifests/VM-9999.variant_manifest.json"),
        ("write_scratch", "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json"),
        ("write_scratch", "research/result_populations/RP-9999.result_population.json"),
        ("trial_log_mutation", "research/trial_log.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("candidate_readiness", "research/candidate_registry.jsonl"),
        ("candidate_lifecycle_transition", "research/candidate_registry.jsonl"),
        ("fixture_canonical_crossing_build", "scratch/canonical-crossing/output.json"),
        ("runtime_control", "src/runtime/paper_trader.py"),
        ("paper_control", "src/paper/runner.py"),
        ("live_control", "src/live/runner.py"),
        ("oms_access", "src/oms/state.py"),
        ("risk_control", "src/risk/caps.py"),
        ("reconciliation_control", "src/reconciliation/state.py"),
        ("capital_access", "src/capital/state.py"),
        ("private_endpoint_access", "exchange/private"),
        ("credential_access", ".env"),
        ("network_access", "provider/network"),
        ("provider_api_call", "provider/network"),
        ("evidence_suppression", "scratch/evidence.json"),
        ("canonical_write", "research/canonical_crossing.json"),
    ],
)
def test_donchian_toolcontext_preserves_hard_prohibitions(
    action_type: str, target_path: str
):
    context, sink = _context("formalizer_runner_bridge")

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))
    assert sink.records[-1].decision == "blocked"
