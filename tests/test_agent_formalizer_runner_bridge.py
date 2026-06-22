from __future__ import annotations

import copy
import json
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
    FORMALIZER_OUTPUT_PREFIX,
    NON_AUTHORITY_FLAGS,
    ROLE,
    TRIAL_STATUSES,
    WP_ID,
    FormalizerRunnerBridge,
    FormalizerRunnerBridgeConfig,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 6, 22, 1, 2, 3, tzinfo=timezone.utc)


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return relative


def _copy_templates(root: Path) -> None:
    for relative in (
        "research/variant_manifests/VM-0003.variant_manifest.json",
        "research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO_ROOT / relative).read_bytes())


def _draft_strategy_spec(formalizer_path: str) -> dict:
    spec = copy.deepcopy(
        json.loads(
            (REPO_ROOT / "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json").read_text()
        )
    )
    spec["strategy_spec_id"] = "STRAT-SPEC-9001"
    spec["title"] = "Draft provider-assisted SMA/stddev mean-reversion Strategy Spec"
    spec["short_name"] = "draft-bridge-test"
    spec["status"] = "draft"
    spec["provenance"] = {
        "source_type": "manual_idea",
        "source_refs": [formalizer_path],
        "prepared_by": "bounded idea_formalizer agent",
        "created_at": None,
        "updated_at": None,
        "rationale": "Test the merged SMA/stddev mean-reversion family.",
        "source_constraints": [
            "Scratch-only draft adapted from the merged STRAT-SPEC-0003 capability family."
        ],
        "unresolved_claims": ["Human review required."],
    }
    spec["review"].update(
        {
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": ["Scratch-only provider-assisted draft."],
            "approval_scope": "none",
        }
    )
    spec["lineage"] = {
        "parent_refs": [
            {
                "ref_type": "concept",
                "ref_id": "IDEA-BRIDGE-TEST",
                "ref_path": formalizer_path,
                "ref_hash": None,
            }
        ],
        "supersedes": [],
        "amendment_of": None,
    }
    spec["hash_pinning"].update({"canonical_spec_hash": None, "hash_status": "not_computed"})
    spec["pre_registration_support"] = {
        "intended_for_variant_manifest": False,
        "variant_manifest_ref": None,
        "frozen_snapshot_ref": None,
    }
    return spec


def _feature_assessment(
    feature: str,
    *,
    coverage: str = "FULL_HISTORY_PUBLIC_ARCHIVE",
    source: str = "INDICATOR_DERIVED_FROM_OHLCV",
    testability: str = "available_when_source_bars_exist",
) -> dict:
    return {
        "feature": feature,
        "compiler_field_exists": True,
        "historical_testability": testability,
        "coverage_class": coverage,
        "source_class": source,
        "warnings": [],
    }


def _write_ohlcv_fixture(root: Path) -> str:
    relative = f"scratch/{WP_ID}/fixtures/canonical_15m_ohlcv.csv"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    index = pd.date_range("2026-01-01T00:00:00Z", periods=160, freq="15min")
    pattern = [100.0] * 40 + [94.0, 98.0, 101.0, 90.0, 96.0, 102.0, 88.0, 100.0]
    close = (pattern * 4)[: len(index)]
    pd.DataFrame(
        {
            "timestamp": index,
            "open": [value + 0.1 for value in close],
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [1000.0] * len(index),
        }
    ).to_csv(path, index=False)
    return relative


def _setup_source(
    root: Path,
    *,
    approved: bool = True,
    extra_assessments: list[dict] | None = None,
    funding_approved: bool = False,
) -> tuple[str, str, str]:
    run_id = "formalizerbridge1"
    prefix = f"{FORMALIZER_OUTPUT_PREFIX}{run_id}"
    formalizer_path = f"{prefix}/formalized_idea.json"
    draft_path = f"{prefix}/STRAT-SPEC-9001.strategy_spec.json"
    assessments = [_feature_assessment("sma"), _feature_assessment("stddev")]
    assessments.extend(extra_assessments or [])
    payload = {
        "schema_version": "agent_formalized_idea_v1",
        "run_id": run_id,
        "status": "accepted",
        "input": {
            "idea": "Fade z-score extremes using SMA and standard deviation.",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
        },
        "capability_assessment": {
            "detected_features": [row["feature"] for row in assessments],
            "feature_assessments": assessments,
            "historically_testable_now": True,
            "blocking_features": [],
        },
        "research_object": {
            "summary": "bounded SMA/stddev mean-reversion idea",
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": [row["feature"] for row in assessments],
        },
        "draft_strategy_spec": {"produced": True, "path": draft_path, "blockers": []},
        "non_authority": {"scratch_only": True, "not_canonical": True},
    }
    _write_json(root, draft_path, _draft_strategy_spec(formalizer_path))
    _write_json(root, formalizer_path, payload)
    approval = {
        "approved_for_noncanonical_runner_bridge": approved,
        "approved_by": "operator",
        "approval_scope": APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-06-22T00:00:00Z",
        "source_formalizer_run_id": run_id,
    }
    if funding_approved:
        approval["approved_funding_cost_mode"] = "on"
    approval_path = _write_json(root, f"{prefix}/operator_bridge_approval.json", approval)
    fixture_path = _write_ohlcv_fixture(root)
    return formalizer_path, approval_path, fixture_path


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME),
        sink,
    )


def _run(root: Path, *, config: FormalizerRunnerBridgeConfig | None = None, **source_kwargs):
    _copy_templates(root)
    formalizer_path, approval_path, fixture_path = _setup_source(root, **source_kwargs)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=config or FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=root,
    )
    return (
        bridge.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
        ),
        sink,
    )


def test_approved_bridge_runs_real_runner_and_reconciles(tmp_path: Path):
    result, sink = _run(tmp_path)

    assert result["status"] == "completed"
    assert result["manual_reconciliation_result"]["passed"] is True
    assert result["trial_status_counts"]["completed"] == 8
    assert sum(result["trial_status_counts"].values()) == 8
    assert result["artifact_paths"]["runner_result"].startswith(
        f"scratch/{WP_ID}/outputs/"
    )
    assert (tmp_path / result["artifact_paths"]["runner_result"]).is_file()

    input_dir = (tmp_path / result["artifact_paths"]["strategy_spec"]).parent
    assert validate_strategy_specs(strategy_specs_dir=input_dir) == []
    assert (
        validate_variant_sweep_artifacts(
            strategy_specs_dir=input_dir,
            variant_manifests_dir=input_dir,
            sweep_plans_dir=input_dir,
        )
        == []
    )
    manifest = json.loads((tmp_path / result["artifact_paths"]["variant_manifest"]).read_text())
    assert manifest["status"] == "approved_for_sweep_planning"
    assert "grants no canonical freeze authority" in " ".join(manifest["lineage"]["audit_notes"])

    ledger = json.loads((tmp_path / result["artifact_paths"]["denominator_ledger"]).read_text())
    assert ledger["denominator_preserved"] is True
    assert len(ledger["rows"]) == 8
    assert all(row["funding_cost_mode"] == "off" for row in ledger["rows"])
    assert all(row["non_authority_flags"] == list(NON_AUTHORITY_FLAGS) for row in ledger["rows"])
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["manual_reconciliation_result"]["passed"] is True
    assert review["full_ledger_path"] == result["artifact_paths"]["denominator_ledger"]
    assert review["runner_artifact_paths"] == [result["artifact_paths"]["runner_result"]]
    assert review["funding_mode"]["effective"] == "off"
    assert any(
        record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP and record.decision == "allowed"
        for record in sink.records
    )


def test_missing_bridge_approval_is_blocked_and_audited(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, fixture_path = _setup_source(tmp_path, approved=False)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(ohlcv_input_path=fixture_path),
        tool_context=context,
        repo_root=tmp_path,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(formalizer_output_path=formalizer_path, approval_path=approval_path)
    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"


def test_explicit_funding_on_is_approval_gated_then_blocked_as_runner_unsupported(tmp_path: Path):
    config = FormalizerRunnerBridgeConfig(
        ohlcv_input_path=f"scratch/{WP_ID}/fixtures/canonical_15m_ohlcv.csv",
        funding_cost_mode="on",
    )
    result, sink = _run(tmp_path, config=config, funding_approved=True)

    assert result["status"] == "blocked"
    assert "no explicit funding-on input" in result["blockers"][0]
    assert result["trial_status_counts"] == {
        "completed": 0,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
        "blocked": 8,
    }
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["funding_mode"]["requested"] == "on"
    assert review["funding_mode"]["effective"] == "not_run"
    assert not any(
        record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP and record.decision == "allowed"
        for record in sink.records
    )


def test_explicit_funding_on_without_matching_approval_is_blocked_and_audited(tmp_path: Path):
    _copy_templates(tmp_path)
    formalizer_path, approval_path, fixture_path = _setup_source(tmp_path)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(
            ohlcv_input_path=fixture_path,
            funding_cost_mode="on",
        ),
        tool_context=context,
        repo_root=tmp_path,
    )

    with pytest.raises(BlockedActionError):
        bridge.run(formalizer_output_path=formalizer_path, approval_path=approval_path)
    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"


@pytest.mark.parametrize(
    "assessment, expected",
    [
        (
            _feature_assessment(
                "open_interest",
                coverage="PUBLIC_SNAPSHOT_ONLY",
                source="PUBLIC_SNAPSHOT",
                testability="vendor_or_capture_constrained",
            ),
            "open interest cannot be reconstructed from trades",
        ),
        (
            _feature_assessment(
                "liquidation_volume",
                coverage="VENDOR_ONLY_FOR_HISTORY",
                source="VENDOR_HISTORICAL_DATASET",
                testability="vendor_or_capture_constrained",
            ),
            "liquidation history requires vendor/captured data",
        ),
        (
            _feature_assessment(
                "taker_buy_sell_ratio",
                coverage="FULL_HISTORY_PUBLIC_ARCHIVE",
                source="PUBLIC_TRADE_ARCHIVE_DERIVATION",
                testability="available_when_source_bars_exist",
            ),
            "the OHLCV runner fixture is insufficient",
        ),
    ],
)
def test_constrained_full_history_data_is_blocked_before_runner(
    tmp_path: Path, assessment, expected
):
    result, sink = _run(tmp_path, extra_assessments=[assessment])

    assert result["status"] == "blocked"
    assert any(expected in blocker for blocker in result["blockers"])
    assert result["trial_status_counts"]["blocked"] == 8
    assert not any(record.action_type == RUN_NONCANONICAL_OFFLINE_SWEEP for record in sink.records)
    assert any(
        record.action_type == "data_availability_bypass" and record.decision == "blocked"
        for record in sink.records
    )


def test_runner_outcomes_map_to_complete_denominator_statuses(tmp_path: Path):
    outcomes = ["successful", "failed", "invalid", "filtered", "data_unavailable"]
    manifest = {
        "variant_assignments": [
            {
                "variant_id": f"VAR-{index:06d}",
                "parameter_values": {"lookback": index},
            }
            for index in range(1, 6)
        ]
    }
    runner_result = {
        "result_population": {
            "variant_result_rows": [
                {
                    "variant_id": f"VAR-{index:06d}",
                    "outcome_category": outcome,
                    "non_success": {"reason": outcome},
                    "metrics": {"sharpe": 1.0},
                    "row_identity_hash": f"sha256:{index:064x}",
                }
                for index, outcome in enumerate(outcomes, start=1)
            ]
        }
    }
    rows = FormalizerRunnerBridge._ledger_rows(
        run_id="run",
        runner_invocation_id="invocation",
        formalizer_run_id="formalizer",
        formalizer_path="scratch/source.json",
        approval_scope=APPROVAL_SCOPE,
        input_paths={"strategy_spec": "scratch/spec.json"},
        manifest=manifest,
        runner_result=runner_result,
        runner_artifact_path="scratch/result.json",
        blockers=[],
        funding_cost_mode="off",
        timestamp_utc="2026-06-22T00:00:00Z",
    )

    assert [row["trial_status"] for row in rows] == list(TRIAL_STATUSES)
    context, sink = _context()
    bridge = FormalizerRunnerBridge(
        config=FormalizerRunnerBridgeConfig(
            ohlcv_input_path=f"scratch/{WP_ID}/fixtures/unused.csv"
        ),
        tool_context=context,
        repo_root=tmp_path,
    )
    target = f"scratch/{WP_ID}/outputs/run/denominator_ledger.json"
    bridge._assert_denominator(rows, manifest, target_path=target)
    with pytest.raises(BlockedActionError):
        bridge._assert_denominator(rows[:-1], manifest, target_path=target)
    assert sink.records[-1].action_type == "evidence_suppression"
    assert sink.records[-1].decision == "blocked"


@pytest.mark.parametrize(
    "action_type,target_path",
    [
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("write_scratch", "research/variant_manifests/VM-9999.variant_manifest.json"),
        ("write_scratch", "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json"),
        ("write_scratch", "research/result_populations/RP-9999.result_population.json"),
        ("trial_log_mutation", "research/trial_log.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("runtime_control", "src/runtime/paper_trader.py"),
        ("oms_access", "src/oms/state.py"),
        ("risk_control", "src/risk/caps.py"),
        ("reconciliation_control", "src/reconciliation/state.py"),
        ("capital_access", "src/capital/state.py"),
        ("private_endpoint_access", "exchange/private"),
        ("credential_access", ".env"),
        ("funding_mode_mutation", "configs/research.json"),
        ("evidence_suppression", "scratch/evidence.json"),
        ("evidence_deletion", "scratch/evidence.json"),
        ("toolcontext_bypass", "tools/agent_sandbox"),
        ("network_access", "provider/network"),
        (RUN_NONCANONICAL_OFFLINE_SWEEP, "scratch/other/outputs/run.json"),
    ],
)
def test_adversarial_actions_are_blocked_and_audited(action_type: str, target_path: str):
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))
    assert sink.records[-1].decision == "blocked"
    assert sink.records[-1].action_type == action_type


def test_bridge_source_has_no_provider_or_network_client():
    source = (REPO_ROOT / "tools/research_agents/formalizer_runner_bridge.py").read_text()
    for forbidden in ("requests", "httpx", "urllib", "OpenAI", "Anthropic", "socket"):
        assert forbidden not in source
