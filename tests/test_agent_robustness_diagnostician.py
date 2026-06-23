from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tests.test_agent_formalizer_runner_bridge import _run as run_real_bridge
from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC
from tools.research_agents.robustness_diagnostician_agent import (
    APPROVAL_SCOPE,
    NON_AUTHORITY_FLAGS,
    ROLE,
    TRIAL_STATUSES,
    WP_ID,
    RobustnessDiagnosticianAgent,
    RobustnessDiagnosticianConfig,
    RobustnessDiagnosticianError,
)


FIXED_TIME = datetime(2026, 6, 22, 3, 4, 5, tzinfo=timezone.utc)


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return relative


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME),
        sink,
    )


def _setup(root: Path, *, approval_overrides: dict | None = None):
    bridge_result, bridge_sink = run_real_bridge(root)
    approval = {
        "approved_for_noncanonical_robustness_diagnostics": True,
        "approved_by": "operator",
        "approval_scope": APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-06-22T03:00:00Z",
        "source_bridge_run_id": bridge_result["run_id"],
    }
    approval.update(approval_overrides or {})
    approval_path = _write_json(
        root,
        f"scratch/{WP_ID}/inputs/operator_robustness_approval.json",
        approval,
    )
    context, sink = _context()
    agent = RobustnessDiagnosticianAgent(
        config=RobustnessDiagnosticianConfig(bootstrap_samples=50),
        tool_context=context,
        repo_root=root,
    )
    paths = bridge_result["artifact_paths"]
    arguments = {
        "bridge_review_packet_path": paths["human_review_packet"],
        "bridge_result_population_artifact_path": paths["runner_result"],
        "bridge_denominator_ledger_path": paths["denominator_ledger"],
        "operator_robustness_approval_path": approval_path,
    }
    return bridge_result, bridge_sink, agent, sink, arguments


def _load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def test_setup_generates_real_bridge_artifacts_and_approved_diagnostics(tmp_path: Path):
    bridge, bridge_sink, agent, sink, arguments = _setup(tmp_path)

    result = agent.run(**arguments)

    assert bridge["status"] == "completed"
    assert bridge["manual_reconciliation_result"]["passed"] is True
    assert any(
        record.action_type == "noncanonical_offline_sweep_run"
        and record.decision == "allowed"
        for record in bridge_sink.records
    )
    assert result["status"] == "completed"
    assert result["source_bridge_run_id"] == bridge["run_id"]
    assert all(
        path.startswith(f"scratch/{WP_ID}/outputs/")
        for path in result["artifact_paths"].values()
    )
    packet = _load(tmp_path, result["artifact_paths"]["robustness_review_packet"])
    diagnostics = _load(tmp_path, result["artifact_paths"]["robustness_diagnostics"])
    assert packet["result_population_validation"]["status"] == "passed"
    assert set(NON_AUTHORITY_FLAGS).issubset(packet["non_authority_flags"])
    assert diagnostics["bootstrap_mc_summary"]
    assert diagnostics["parameter_sensitivity_summary"]["status"] == "performed"
    assert diagnostics["lineage_hash_preservation"]["status"] == "passed"
    assert all(record.decision == "allowed" for record in sink.records)


def test_seeded_diagnostics_are_deterministic(tmp_path: Path):
    _bridge, _bridge_sink, agent, _sink, arguments = _setup(tmp_path)

    first = agent.run(**arguments)
    first_diagnostics = _load(tmp_path, first["artifact_paths"]["robustness_diagnostics"])
    second = agent.run(**arguments)
    second_diagnostics = _load(tmp_path, second["artifact_paths"]["robustness_diagnostics"])

    assert first["run_id"] == second["run_id"]
    assert first_diagnostics == second_diagnostics
    assert first_diagnostics["bootstrap_samples_hash"] == second_diagnostics[
        "bootstrap_samples_hash"
    ]


@pytest.mark.parametrize(
    "approval_overrides",
    [
        {"approved_for_noncanonical_robustness_diagnostics": False},
        {"source_bridge_run_id": "different-bridge-run"},
        {"approval_scope": "canonical_robustness"},
    ],
)
def test_missing_or_mismatched_approval_is_blocked_and_audited(
    tmp_path: Path, approval_overrides: dict
):
    _bridge, _bridge_sink, agent, sink, arguments = _setup(
        tmp_path, approval_overrides=approval_overrides
    )

    with pytest.raises(BlockedActionError):
        agent.run(**arguments)

    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"
    assert not (tmp_path / f"scratch/{WP_ID}/outputs").exists()


def test_denominator_preserves_every_status_and_skipped_reason(tmp_path: Path):
    _bridge, _bridge_sink, agent, _sink, arguments = _setup(tmp_path)
    review = _load(tmp_path, arguments["bridge_review_packet_path"])
    ledger = _load(tmp_path, arguments["bridge_denominator_ledger_path"])
    result_population = _load(tmp_path, arguments["bridge_result_population_artifact_path"])
    statuses = ["completed", "completed", "completed", "completed", "failed", "invalid", "pruned", "blocked"]
    outcomes = {
        "completed": "successful",
        "failed": "failed",
        "invalid": "invalid",
        "pruned": "excluded",
        "blocked": "not_attempted",
    }
    for ledger_row, result_row, status in zip(
        ledger["rows"], result_population["variant_result_rows"], statuses, strict=True
    ):
        ledger_row["trial_status"] = status
        ledger_row["status_reason"] = f"test-{status}"
        ledger_row["runner_outcome_category"] = outcomes[status]
        result_row["outcome_category"] = outcomes[status]
        if status != "completed":
            result_row["attempted"] = False
    counts = {status: statuses.count(status) for status in TRIAL_STATUSES}
    ledger["trial_status_counts"] = counts
    review["denominator_counts"] = counts
    review["completed_trial_count"] = counts["completed"]
    review["failed_trial_count"] = counts["failed"]
    review["invalid_trial_count"] = counts["invalid"]
    review["pruned_trial_count"] = counts["pruned"]
    review["blocked_trial_count"] = counts["blocked"]
    denominator = agent._denominator_snapshot(
        review=review,
        ledger=ledger,
        result_rows=result_population["variant_result_rows"],
        target_path=f"scratch/{WP_ID}/outputs/test/robustness_diagnostics.json",
    )

    assert denominator["source_status_counts"] == counts
    assert denominator["result_row_count"] == 8
    assert len(denominator["row_disposition"]) == 8
    assert sum(row["eligible_for_metrics"] for row in denominator["row_disposition"]) == 4
    assert {row["status_reason"] for row in denominator["row_disposition"]} >= {
        "test-failed",
        "test-invalid",
        "test-pruned",
        "test-blocked",
    }


def test_denominator_shrinkage_is_blocked_and_audited(tmp_path: Path):
    _bridge, _bridge_sink, agent, sink, arguments = _setup(tmp_path)
    ledger = _load(tmp_path, arguments["bridge_denominator_ledger_path"])
    ledger["rows"].pop()
    _write_json(tmp_path, arguments["bridge_denominator_ledger_path"], ledger)

    with pytest.raises(BlockedActionError):
        agent.run(**arguments)

    assert sink.records[-1].action_type == "evidence_suppression"
    assert sink.records[-1].decision == "blocked"


def test_missing_data_funding_off_and_warnings_are_explicit(tmp_path: Path):
    _bridge, _bridge_sink, agent, _sink, arguments = _setup(tmp_path)
    review = _load(tmp_path, arguments["bridge_review_packet_path"])
    review["data_availability_warnings"] = [
        "open_interest_recent_only_not_reconstructable_from_trades",
        "liquidation_history_requires_vendor_or_captured_history",
    ]
    _write_json(tmp_path, arguments["bridge_review_packet_path"], review)

    output = agent.run(**arguments)
    packet = _load(tmp_path, output["artifact_paths"]["robustness_review_packet"])

    assert packet["per_trade_status"]["status"] == "QUEUE_PER_TRADE_INSTRUMENTATION"
    assert packet["per_trade_status"]["fabricated_per_trade_data"] is False
    assert packet["oos_walkforward_status"]["status"] == "missing_fold_inputs"
    assert packet["funding_stress_status"] == {
        "performed": False,
        "status": "not_applicable_funding_mode_off",
    }
    assert packet["data_availability_warnings"] == review["data_availability_warnings"]


@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("write_scratch", "research/result_populations/RP-X.result_population.json"),
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-X.strategy_spec.json"),
        ("write_scratch", "research/variant_manifests/VM-X.variant_manifest.json"),
        ("write_scratch", "research/sweep_plans/SWEEP-X.sweep_plan.json"),
        ("write_scratch", "research/trial_log.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_readiness", "research/candidate_registry.jsonl"),
        ("paper_control", "paper/runner.py"),
        ("live_control", "live/runner.py"),
        ("runtime_control", "runtime/runner.py"),
        ("oms_access", "oms/state.py"),
        ("risk_control", "risk/caps.py"),
        ("reconciliation_control", "reconciliation/state.py"),
        ("capital_access", "capital/allocation.py"),
        ("private_endpoint_access", "exchange/private/orders"),
        ("credential_access", "secrets/exchange.key"),
        ("funding_mode_mutation", "configs/research.json"),
        ("evidence_deletion", "research/result_populations/RP-X.result_population.json"),
        ("toolcontext_bypass", f"scratch/{WP_ID}/outputs/x.json"),
        ("fabricated_per_trade_data", f"scratch/{WP_ID}/outputs/trades.json"),
        ("provider_memory_as_truth", f"scratch/{WP_ID}/outputs/provider.json"),
        ("network_access", "public.example/api"),
    ],
)
def test_adversarial_actions_are_blocked_and_audited(action_type: str, target_path: str):
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))

    assert sink.records[-1].decision == "blocked"


def test_diagnostic_action_and_writes_are_restricted_to_active_scratch_prefix():
    context, sink = _context()

    context.require_allowed(
        ToolAction(
            RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC,
            f"scratch/{WP_ID}/outputs/run/robustness_diagnostics.json",
        )
    )
    with pytest.raises(BlockedActionError):
        context.require_allowed(
            ToolAction(
                RUN_SCRATCH_ROBUSTNESS_DIAGNOSTIC,
                "scratch/OTHER-WP/outputs/robustness_diagnostics.json",
            )
        )
    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction("write_scratch", "scratch/OTHER-WP/output.json"))

    assert [record.decision for record in sink.records] == ["allowed", "blocked", "blocked"]


def test_unbound_bridge_paths_fail_before_outputs(tmp_path: Path):
    _bridge, _bridge_sink, agent, _sink, arguments = _setup(tmp_path)
    review = _load(tmp_path, arguments["bridge_review_packet_path"])
    review["runner_artifact_paths"] = []
    _write_json(tmp_path, arguments["bridge_review_packet_path"], review)

    with pytest.raises(RobustnessDiagnosticianError, match="not bound"):
        agent.run(**arguments)

    assert not (tmp_path / f"scratch/{WP_ID}/outputs").exists()


def test_out_of_prefix_derived_validation_path_is_blocked_and_audited(tmp_path: Path):
    _bridge, _bridge_sink, agent, sink, arguments = _setup(tmp_path)
    review = _load(tmp_path, arguments["bridge_review_packet_path"])
    review["derived_input_artifact_paths"]["strategy_spec"] = (
        "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json"
    )
    _write_json(tmp_path, arguments["bridge_review_packet_path"], review)

    with pytest.raises(BlockedActionError):
        agent.run(**arguments)

    assert sink.records[-1].action_type == "toolcontext_bypass"
    assert sink.records[-1].decision == "blocked"
