from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tests.test_agent_formalizer_runner_bridge import _run as run_real_bridge
from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET
from tools.research_agents.candidate_review_packet_agent import (
    APPROVAL_SCOPE,
    LIFECYCLE_HELPER_PATHS,
    NON_AUTHORITY_FLAGS,
    ROLE,
    WP_ID,
    CandidateReviewPacketAgent,
    CandidateReviewPacketConfig,
)
from tools.research_agents.robustness_diagnostician_agent import (
    APPROVAL_SCOPE as ROBUSTNESS_APPROVAL_SCOPE,
)
from tools.research_agents.robustness_diagnostician_agent import (
    ROLE as ROBUSTNESS_ROLE,
)
from tools.research_agents.robustness_diagnostician_agent import (
    WP_ID as ROBUSTNESS_WP_ID,
)
from tools.research_agents.robustness_diagnostician_agent import (
    RobustnessDiagnosticianAgent,
    RobustnessDiagnosticianConfig,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 6, 22, 4, 5, 6, tzinfo=timezone.utc)


def _write_json(root: Path, relative: str, payload: dict) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return relative


def _load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME),
        sink,
    )


def _copy_lifecycle_refs(root: Path) -> None:
    for relative in LIFECYCLE_HELPER_PATHS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)


def _run_robustness(root: Path, bridge_result: dict) -> dict:
    approval = {
        "approved_for_noncanonical_robustness_diagnostics": True,
        "approved_by": "operator",
        "approval_scope": ROBUSTNESS_APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-06-22T03:00:00Z",
        "source_bridge_run_id": bridge_result["run_id"],
    }
    approval_path = _write_json(
        root,
        f"scratch/{ROBUSTNESS_WP_ID}/inputs/operator_robustness_approval.json",
        approval,
    )
    sink = MemoryAuditSink()
    context = ToolContext(
        wp_id=ROBUSTNESS_WP_ID,
        role=ROBUSTNESS_ROLE,
        audit_sink=sink,
        clock=lambda: FIXED_TIME,
    )
    agent = RobustnessDiagnosticianAgent(
        config=RobustnessDiagnosticianConfig(bootstrap_samples=50),
        tool_context=context,
        repo_root=root,
    )
    paths = bridge_result["artifact_paths"]
    return agent.run(
        bridge_review_packet_path=paths["human_review_packet"],
        bridge_result_population_artifact_path=paths["runner_result"],
        bridge_denominator_ledger_path=paths["denominator_ledger"],
        operator_robustness_approval_path=approval_path,
    )


def _setup(root: Path, *, approval_overrides: dict | None = None):
    _copy_lifecycle_refs(root)
    bridge_result, _bridge_sink = run_real_bridge(root)
    bridge_packet = _load(root, bridge_result["artifact_paths"]["human_review_packet"])
    bridge_packet["data_availability_warnings"] = [
        "open_interest_recent_only_not_reconstructable_from_trades",
        "liquidation_history_requires_vendor_or_captured_history",
    ]
    _write_json(root, bridge_result["artifact_paths"]["human_review_packet"], bridge_packet)
    robustness_result = _run_robustness(root, bridge_result)
    ledger = _load(root, bridge_result["artifact_paths"]["denominator_ledger"])
    formalizer_path = ledger["rows"][0]["source_formalizer_artifact_path"]
    formalizer = _load(root, formalizer_path)
    draft_path = formalizer["draft_strategy_spec"]["path"]
    approval = {
        "approved_for_noncanonical_candidate_review_packet": True,
        "approved_by": "operator",
        "approval_scope": APPROVAL_SCOPE,
        "approval_timestamp_utc": "2026-06-22T04:00:00Z",
        "source_bridge_run_id": bridge_result["run_id"],
        "source_robustness_run_id": robustness_result["run_id"],
    }
    approval.update(approval_overrides or {})
    approval_path = _write_json(
        root,
        f"scratch/{WP_ID}/inputs/operator_candidate_review_approval.json",
        approval,
    )
    context, sink = _context()
    agent = CandidateReviewPacketAgent(
        config=CandidateReviewPacketConfig(),
        tool_context=context,
        repo_root=root,
    )
    arguments = {
        "formalizer_research_object_path": formalizer_path,
        "formalizer_draft_strategy_spec_path": draft_path,
        "bridge_review_packet_path": bridge_result["artifact_paths"]["human_review_packet"],
        "bridge_result_population_artifact_path": bridge_result["artifact_paths"]["runner_result"],
        "bridge_denominator_ledger_path": bridge_result["artifact_paths"]["denominator_ledger"],
        "robustness_diagnostics_path": robustness_result["artifact_paths"][
            "robustness_diagnostics"
        ],
        "robustness_review_packet_path": robustness_result["artifact_paths"][
            "robustness_review_packet"
        ],
        "operator_candidate_review_approval_path": approval_path,
    }
    return bridge_result, robustness_result, agent, sink, arguments


def test_approved_source_bundle_writes_scratch_json_and_markdown_packets(tmp_path: Path):
    bridge, robustness, agent, sink, arguments = _setup(tmp_path)

    result = agent.run(**arguments)

    assert result["status"] == "completed"
    assert result["source_bridge_run_id"] == bridge["run_id"]
    assert result["source_robustness_run_id"] == robustness["run_id"]
    assert all(
        path.startswith(f"scratch/{WP_ID}/outputs/")
        for path in result["artifact_paths"].values()
    )
    packet = _load(tmp_path, result["artifact_paths"]["candidate_review_packet_json"])
    markdown = (tmp_path / result["artifact_paths"]["candidate_review_packet_markdown"]).read_text(
        encoding="utf-8"
    )
    assert packet["denominator_snapshot"]["counts"] == result["source_denominator_counts"]
    assert packet["denominator_snapshot"]["all_source_rows_preserved"] is True
    assert len(packet["denominator_snapshot"]["row_disposition"]) == 8
    assert set(NON_AUTHORITY_FLAGS).issubset(packet["non_authority_flags"])
    assert packet["operator_approval"]["not_candidate_registration"] is True
    assert packet["operator_approval"]["not_paper_live_approval"] is True
    assert "not promotion authority" in markdown
    assert "not a trading signal" in markdown
    assert packet["source_formalizer"]["draft_strategy_spec_path"] == arguments[
        "formalizer_draft_strategy_spec_path"
    ]
    assert packet["source_bridge"]["runner_artifact_path"] == arguments[
        "bridge_result_population_artifact_path"
    ]
    assert len(packet["candidate_lifecycle_context_refs"]) == len(LIFECYCLE_HELPER_PATHS)
    assert any(
        record.action_type == BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET
        and record.decision == "allowed"
        for record in sink.records
    )


def test_missing_data_and_robustness_skips_remain_explicit(tmp_path: Path):
    _bridge, _robustness, agent, _sink, arguments = _setup(tmp_path)

    result = agent.run(**arguments)
    packet = _load(tmp_path, result["artifact_paths"]["candidate_review_packet_json"])

    assert packet["data_and_funding_summary"]["data_availability_warnings"] == [
        "open_interest_recent_only_not_reconstructable_from_trades",
        "liquidation_history_requires_vendor_or_captured_history",
    ]
    assert packet["missing_data_limitations"]["per_trade"]["fabricated_per_trade_data"] is False
    assert packet["missing_data_limitations"]["oos_walkforward"]["status"] == "missing_fold_inputs"
    assert packet["missing_data_limitations"]["funding_stress"]["status"] == (
        "not_applicable_funding_mode_off"
    )
    assert "needs real trade rows for per-trade diagnostics" in packet["evidence_gaps"]
    assert "needs fold/OOS inputs for walk-forward diagnostics" in packet["evidence_gaps"]


@pytest.mark.parametrize(
    "approval_overrides",
    [
        {"approved_for_noncanonical_candidate_review_packet": False},
        {"source_bridge_run_id": "different-bridge-run"},
        {"source_robustness_run_id": "different-robustness-run"},
        {"approval_scope": "canonical_candidate_review"},
    ],
)
def test_missing_or_mismatched_approval_is_blocked_and_audited(
    tmp_path: Path, approval_overrides: dict
):
    _bridge, _robustness, agent, sink, arguments = _setup(
        tmp_path, approval_overrides=approval_overrides
    )

    with pytest.raises(BlockedActionError):
        agent.run(**arguments)

    assert sink.records[-1].action_type == "approval_gate_bypass"
    assert sink.records[-1].decision == "blocked"
    assert not (tmp_path / f"scratch/{WP_ID}/outputs").exists()


def test_lineage_mismatch_blocks_before_outputs(tmp_path: Path):
    _bridge, _robustness, agent, _sink, arguments = _setup(tmp_path)
    diagnostics = _load(tmp_path, arguments["robustness_diagnostics_path"])
    diagnostics["source_bridge_run_id"] = "wrong-bridge"
    _write_json(tmp_path, arguments["robustness_diagnostics_path"], diagnostics)

    with pytest.raises(Exception, match="source bridge ID mismatch"):
        agent.run(**arguments)

    assert not (tmp_path / f"scratch/{WP_ID}/outputs").exists()


def test_denominator_shrinkage_is_blocked_and_audited(tmp_path: Path):
    _bridge, _robustness, agent, sink, arguments = _setup(tmp_path)
    ledger = _load(tmp_path, arguments["bridge_denominator_ledger_path"])
    ledger["rows"].pop()
    _write_json(tmp_path, arguments["bridge_denominator_ledger_path"], ledger)

    with pytest.raises(BlockedActionError):
        agent.run(**arguments)

    assert sink.records[-1].action_type == "evidence_suppression"
    assert sink.records[-1].decision == "blocked"


@pytest.mark.parametrize(
    ("action_type", "target_path"),
    [
        ("write_scratch", "research/candidate_registry.jsonl"),
        ("write_scratch", "research/result_populations/RP-X.result_population.json"),
        ("write_scratch", "research/strategy_specs/STRAT-SPEC-X.strategy_spec.json"),
        ("write_scratch", "research/variant_manifests/VM-X.variant_manifest.json"),
        ("write_scratch", "research/sweep_plans/SWEEP-X.sweep_plan.json"),
        ("write_scratch", "research/trial_log.jsonl"),
        ("candidate_registration", "research/candidate_registry.jsonl"),
        ("candidate_freeze", "research/candidate_registry.jsonl"),
        ("candidate_promotion", "research/candidate_registry.jsonl"),
        ("candidate_readiness", "research/candidate_registry.jsonl"),
        ("ranking_as_promotion_ready", "scratch/ranking.json"),
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
        ("evidence_suppression", "research/result_populations/RP-X.result_population.json"),
        ("evidence_deletion", "research/result_populations/RP-X.result_population.json"),
        ("toolcontext_bypass", f"scratch/{WP_ID}/outputs/x.json"),
        ("fabricated_robustness_diagnostic", f"scratch/{WP_ID}/outputs/fabricated.json"),
        ("provider_api_call", "provider/api"),
        ("network_access", "public.example/api"),
    ],
)
def test_adversarial_actions_are_blocked_and_audited(action_type: str, target_path: str):
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))

    assert sink.records[-1].action_type == action_type
    assert sink.records[-1].decision == "blocked"


def test_candidate_review_action_is_scoped_to_active_output_prefix():
    context, sink = _context()

    context.require_allowed(
        ToolAction(
            BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET,
            f"scratch/{WP_ID}/outputs/run/candidate_review_packet.json",
        )
    )
    with pytest.raises(BlockedActionError):
        context.require_allowed(
            ToolAction(
                BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET,
                "scratch/OTHER-WP/outputs/candidate_review_packet.json",
            )
        )
    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction("write_scratch", "scratch/OTHER-WP/output.json"))

    assert [record.decision for record in sink.records] == ["allowed", "blocked", "blocked"]


def test_packet_agent_source_has_no_provider_or_network_client():
    source = (REPO_ROOT / "tools/research_agents/candidate_review_packet_agent.py").read_text()
    for forbidden in ("requests", "httpx", "urllib", "OpenAI", "Anthropic", "socket"):
        assert forbidden not in source
