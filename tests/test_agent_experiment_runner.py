from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.research_agents.experiment_runner_agent import (
    FORMALIZER_OUTPUT_PREFIX,
    NON_AUTHORITY_FLAGS,
    ROLE,
    TRIAL_STATUSES,
    WP_ID,
    ExperimentRunnerAgent,
    ExperimentRunnerConfig,
    ExperimentRunnerError,
)


FIXED_TIME = datetime(2026, 6, 22, 1, 2, 3, tzinfo=timezone.utc)


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return relative


def _feature_assessment(
    feature: str = "sma",
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


def _formalizer_payload(run_id: str = "formalizer123", assessment: dict | None = None) -> dict:
    assessment = assessment or _feature_assessment()
    return {
        "schema_version": "agent_formalized_idea_v1",
        "run_id": run_id,
        "status": "accepted",
        "input": {
            "idea": "SMA momentum because trend persists",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
        },
        "capability_assessment": {
            "detected_features": [assessment["feature"]],
            "feature_assessments": [assessment],
            "historically_testable_now": True,
            "blocking_features": [],
        },
        "research_object": {
            "summary": "bounded fixture idea",
            "symbols": ["BTCUSDT"],
            "timeframe": "15m",
            "features": [assessment["feature"]],
        },
        "draft_strategy_spec": {"produced": False, "path": None, "blockers": []},
        "non_authority": {"scratch_only": True, "not_canonical": True},
    }


def _setup_source(
    root: Path,
    *,
    approved: bool = True,
    payload: dict | None = None,
    with_draft: bool = False,
) -> tuple[str, str]:
    formalized = payload or _formalizer_payload()
    run_id = formalized["run_id"]
    run_prefix = f"{FORMALIZER_OUTPUT_PREFIX}{run_id}"
    if with_draft:
        draft_path = f"{run_prefix}/STRAT-SPEC-9001.strategy_spec.json"
        _write_json(root, draft_path, {"strategy_spec_id": "STRAT-SPEC-9001", "status": "draft"})
        formalized["draft_strategy_spec"] = {
            "produced": True,
            "path": draft_path,
            "blockers": [],
        }
    formalizer_path = _write_json(root, f"{run_prefix}/formalized_idea.json", formalized)
    approval_path = _write_json(
        root,
        f"{run_prefix}/operator_approval.json",
        {
            "approved_for_noncanonical_experiment": approved,
            "approved_by": "operator",
            "approval_scope": "noncanonical_scratch_only",
            "approval_timestamp_utc": "2026-06-22T00:00:00Z",
            "source_formalizer_run_id": run_id,
        },
    )
    return formalizer_path, approval_path


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(
            wp_id=WP_ID,
            role=ROLE,
            audit_sink=sink,
            clock=lambda: FIXED_TIME,
        ),
        sink,
    )


def _trials() -> list[dict]:
    return [
        {
            "strategy_family": "fixture_family",
            "variant_id": f"VAR-{index:03d}",
            "trial_id": f"TRIAL-{index:03d}",
            "params": {"lookback": index},
            "fixture_status": status,
            "metrics_summary": {"sharpe": 1.25, "return_pct": 0.05, "max_drawdown": 0.1},
        }
        for index, status in enumerate(TRIAL_STATUSES, start=1)
    ]


def _run(root: Path, config: ExperimentRunnerConfig | None = None, **source_kwargs):
    formalizer_path, approval_path = _setup_source(root, **source_kwargs)
    context, sink = _context()
    agent = ExperimentRunnerAgent(
        config=config or ExperimentRunnerConfig(),
        tool_context=context,
        repo_root=root,
    )
    result = agent.run(
        formalizer_output_path=formalizer_path,
        approval_path=approval_path,
        trials=_trials(),
    )
    return result, sink


def test_approved_formalizer_output_preserves_all_trial_statuses_and_packets(tmp_path: Path):
    result, sink = _run(tmp_path, with_draft=True)

    assert result["status"] == "completed"
    assert result["trial_status_counts"] == {status: 1 for status in TRIAL_STATUSES}
    ledger = json.loads((tmp_path / result["artifact_paths"]["denominator_ledger"]).read_text())
    assert [row["trial_status"] for row in ledger["rows"]] == list(TRIAL_STATUSES)
    assert ledger["declared_trial_count"] == len(TRIAL_STATUSES)
    assert ledger["denominator_preserved"] is True
    assert all(row["non_authority_flags"] == list(NON_AUTHORITY_FLAGS) for row in ledger["rows"])
    review = json.loads((tmp_path / result["artifact_paths"]["human_review_packet"]).read_text())
    assert review["completed_trial_count"] == 1
    assert review["failed_trial_count"] == 1
    assert review["invalid_trial_count"] == 1
    assert review["pruned_trial_count"] == 1
    assert review["blocked_trial_count"] == 1
    assert review["full_ledger_path"] == result["artifact_paths"]["denominator_ledger"]
    assert review["top_metrics"]["sharpe"] == 1.25
    run_packet = json.loads(
        (tmp_path / result["artifact_paths"]["experiment_run_packet"]).read_text()
    )
    assert run_packet["source_draft_strategy_spec_hash"].startswith("sha256:")
    assert (
        run_packet["runner_configuration"]["real_offline_sweep_integration"]
        == "blocked_not_contract_compatible"
    )
    assert all(record.decision == "allowed" for record in sink.records)


def test_unapproved_formalizer_output_is_blocked_and_audited(tmp_path: Path):
    formalizer_path, approval_path = _setup_source(tmp_path, approved=False)
    context, sink = _context()
    agent = ExperimentRunnerAgent(
        config=ExperimentRunnerConfig(), tool_context=context, repo_root=tmp_path
    )

    with pytest.raises(BlockedActionError, match="approval_gate_bypass"):
        agent.run(
            formalizer_output_path=formalizer_path,
            approval_path=approval_path,
            trials=_trials(),
        )

    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"
    assert not (tmp_path / "scratch" / WP_ID / "outputs").exists()


def test_default_funding_is_off_and_explicit_on_is_visible(tmp_path: Path):
    off_result, _ = _run(tmp_path / "off")
    on_result, _ = _run(tmp_path / "on", config=ExperimentRunnerConfig(funding_cost_mode="on"))

    off_packet = json.loads(
        ((tmp_path / "off") / off_result["artifact_paths"]["human_review_packet"]).read_text()
    )
    on_packet = json.loads(
        ((tmp_path / "on") / on_result["artifact_paths"]["human_review_packet"]).read_text()
    )
    assert off_packet["runner_configuration"]["funding_cost_mode"] == "off"
    assert off_packet["runner_configuration"]["funding_explicitly_enabled"] is False
    assert on_packet["runner_configuration"]["funding_cost_mode"] == "on"
    assert on_packet["runner_configuration"]["funding_explicitly_enabled"] is True


def test_taker_flow_archive_can_proceed_only_with_present_fixture(tmp_path: Path):
    assessment = _feature_assessment(
        "taker_buy_sell_ratio",
        source="PUBLIC_TRADE_ARCHIVE_DERIVATION",
        testability="conditionally_public_archive_backfillable",
    )
    payload = _formalizer_payload(assessment=assessment)
    fixture = "tests/fixtures/takerflow/archive.csv"
    fixture_path = tmp_path / fixture
    fixture_path.parent.mkdir(parents=True)
    fixture_path.write_text("timestamp,buyer_maker,qty\n1,false,2\n", encoding="utf-8")

    result, _ = _run(
        tmp_path,
        config=ExperimentRunnerConfig(data_fixture_paths=(fixture,)),
        payload=payload,
    )

    assert result["status"] == "completed"
    assert not result["blockers"]


@pytest.mark.parametrize(
    "assessment",
    [
        _feature_assessment(
            "open_interest",
            coverage="PUBLIC_SNAPSHOT_ONLY",
            source="PUBLIC_REST_CURRENT_OPEN_INTEREST",
            testability="vendor_or_capture_constrained",
        ),
        _feature_assessment(
            "liquidation_volume",
            coverage="VENDOR_ONLY_FOR_HISTORY",
            source="VENDOR_HISTORICAL_DATASET",
            testability="vendor_or_capture_constrained",
        ),
        _feature_assessment(
            "global_long_short_account_ratio",
            coverage="RECENT_ONLY_PUBLIC_REST",
            source="PUBLIC_REST_GLOBAL_ACCOUNT_RATIO",
            testability="vendor_or_capture_constrained",
        ),
    ],
)
def test_constrained_full_history_ideas_are_blocked_and_remain_in_denominator(
    tmp_path: Path, assessment: dict
):
    result, sink = _run(tmp_path, payload=_formalizer_payload(assessment=assessment))

    assert result["status"] == "blocked"
    assert result["trial_status_counts"] == {
        "completed": 0,
        "failed": 0,
        "invalid": 0,
        "pruned": 0,
        "blocked": len(TRIAL_STATUSES),
    }
    assert result["blockers"]
    assert any(record.action_type == "noncanonical_experiment_run" for record in sink.records)


def test_denominator_guard_rejects_winner_only_or_dropped_rows():
    with pytest.raises(ExperimentRunnerError, match="does not preserve"):
        ExperimentRunnerAgent._assert_denominator(
            [{"trial_id": "TRIAL-001", "trial_status": "completed"}],
            {"TRIAL-001", "TRIAL-002"},
        )


@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("write_scratch", "research/result_populations/RP-9999.result_population.json"),
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"),
        ("canonical_write", "research/variant_manifests/VM-9999.variant_manifest.json"),
        ("canonical_write", "research/sweep_plans/SWEEP-PLAN-9999.sweep_plan.json"),
        ("trial_log_mutation", "research/trial_log.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("paper_control", "paper/runner.py"),
        ("live_control", "live/runner.py"),
        ("runtime_control", "src/runtime/paper_trader.py"),
        ("oms_access", "src/oms/state.py"),
        ("risk_control", "src/risk/caps.py"),
        ("reconciliation_control", "src/reconciliation/state.py"),
        ("capital_access", "src/capital/allocation.py"),
        ("private_endpoint_access", "exchange/private/orders"),
        ("credential_access", ".env"),
        ("funding_mode_mutation", "configs/research.json"),
        ("evidence_suppression", "research"),
        ("evidence_deletion", "research"),
        ("toolcontext_bypass", "tools/agent_sandbox"),
        ("sweep_execution", "tools/research_runner/run_offline_sweep.py"),
    ],
)
def test_experiment_runner_adversarial_actions_are_blocked_audited_and_do_not_mutate(
    tmp_path: Path, action_type: str, target_path: str
):
    context, sink = _context()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("unchanged\n", encoding="utf-8")

    with pytest.raises(BlockedActionError):
        context.run_allowed(
            ToolAction(action_type, target_path),
            lambda: sentinel.write_text("mutated\n", encoding="utf-8"),
        )

    assert sentinel.read_text(encoding="utf-8") == "unchanged\n"
    assert sink.records[-1].decision == "blocked"


def test_noncanonical_action_is_scoped_to_active_output_prefix():
    context, sink = _context()

    with pytest.raises(BlockedActionError, match="outside active outputs"):
        context.require_allowed(
            ToolAction("noncanonical_experiment_run", "scratch/another-wp/outputs/run.json")
        )

    assert sink.records[-1].decision == "blocked"


def test_formalizer_input_contract_rejects_non_scratch_source(tmp_path: Path):
    source = _write_json(tmp_path, "research/formalized_idea.json", _formalizer_payload())
    approval = _write_json(tmp_path, "research/operator_approval.json", {})
    context, _ = _context()
    agent = ExperimentRunnerAgent(
        config=ExperimentRunnerConfig(), tool_context=context, repo_root=tmp_path
    )

    with pytest.raises(ExperimentRunnerError, match="scoped scratch artifact"):
        agent.run(formalizer_output_path=source, approval_path=approval, trials=_trials())
