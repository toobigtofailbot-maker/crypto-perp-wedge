from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.agent_sandbox import BlockedActionError, MemoryAuditSink, ToolAction, ToolContext
from tools.agent_sandbox.permissions import RUN_SCRATCH_LANGGRAPH_PILOT
from tools.research_agents.candidate_review_packet_agent import LIFECYCLE_HELPER_PATHS
from tools.research_agents.langgraph_pilot import (
    NODE_ORDER,
    ROLE,
    WP_ID,
    LangGraphPilot,
    LangGraphPilotConfig,
    ProhibitedActionProbe,
)


ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 6, 22, 6, 0, tzinfo=timezone.utc)


def _copy_repo_inputs(root: Path) -> None:
    for relative in (
        "research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json",
        "research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json",
        "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json",
        "research/variant_manifests/VM-0003.variant_manifest.json",
        "research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json",
        *LIFECYCLE_HELPER_PATHS,
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)


def _context() -> tuple[ToolContext, MemoryAuditSink]:
    sink = MemoryAuditSink()
    return (
        ToolContext(wp_id=WP_ID, role=ROLE, audit_sink=sink, clock=lambda: FIXED_TIME),
        sink,
    )


def _pilot(root: Path, config: LangGraphPilotConfig | None = None):
    _copy_repo_inputs(root)
    context, sink = _context()
    pilot = LangGraphPilot(
        config=config or LangGraphPilotConfig(),
        tool_context=context,
        repo_root=root,
    )
    return pilot, sink


def _load(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def test_graph_builds_with_expected_four_nodes(tmp_path: Path):
    pilot, _sink = _pilot(tmp_path)

    compiled = pilot.build_graph()
    graph = compiled.get_graph()

    assert all(node in graph.nodes for node in NODE_ORDER)


def test_deterministic_scratch_flow_writes_required_outputs(tmp_path: Path):
    pilot, sink = _pilot(tmp_path)

    state = pilot.run()

    assert [item["node"] for item in state["node_statuses"]] == list(NODE_ORDER)
    assert [item["status"] for item in state["node_statuses"]] == ["completed"] * 4
    assert state["blocked_actions"] == []
    assert all(
        path.startswith(f"scratch/{WP_ID}/outputs/{state['run_id']}/")
        for path in state["graph_output_paths"].values()
    )
    for relative in (
        "graph_state",
        "graph_trace",
        "node_statuses",
        "final_candidate_review_packet_reference",
        "pilot_evaluation",
    ):
        assert (tmp_path / state["graph_output_paths"][relative]).is_file()

    packet_ref = _load(
        tmp_path, state["graph_output_paths"]["final_candidate_review_packet_reference"]
    )
    assert packet_ref["status"] == "produced"
    assert packet_ref["paths"]["candidate_review_packet_json"].startswith(
        "scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/"
    )
    assert packet_ref["candidate_review_packet_sha256"].startswith("sha256:")
    trace = _load(tmp_path, state["graph_output_paths"]["graph_trace"])
    json.dumps(trace, sort_keys=True)
    evaluation = (tmp_path / state["graph_output_paths"]["pilot_evaluation"]).read_text(
        encoding="utf-8"
    )
    assert "Finding: defer." in evaluation
    assert "ToolContext boundaries" in evaluation
    assert any(
        record.action_type == RUN_SCRATCH_LANGGRAPH_PILOT and record.decision == "allowed"
        for record in sink.records
    )
    audit = _load(tmp_path, state["graph_output_paths"]["toolcontext_audit"])
    assert any(
        record["action_type"] == "build_scratch_candidate_review_packet"
        for record in audit["records"]
    )
    assert not any(
        record["action_type"] in {"network_access", "provider_api_call"}
        and record["decision"] == "allowed"
        for record in audit["records"]
    )


def test_repeated_run_has_stable_selected_fields(tmp_path: Path):
    first_pilot, _first_sink = _pilot(tmp_path)
    first = first_pilot.run()
    second_pilot, _second_sink = _pilot(tmp_path)
    second = second_pilot.run()

    assert first["run_id"] == second["run_id"]
    assert first["node_statuses"] == second["node_statuses"]
    first_ref = _load(
        tmp_path, first["graph_output_paths"]["final_candidate_review_packet_reference"]
    )
    second_ref = _load(
        tmp_path, second["graph_output_paths"]["final_candidate_review_packet_reference"]
    )
    assert first_ref["candidate_review_packet_sha256"] == second_ref[
        "candidate_review_packet_sha256"
    ]


def test_prohibited_node_action_is_blocked_audited_and_halts_graph(tmp_path: Path):
    config = LangGraphPilotConfig(
        prohibited_action_probe=ProhibitedActionProbe(
            node_name="formalizer_runner_bridge_node",
            action_type="canonical_write",
            target_path="research/result_populations/RP-X.result_population.json",
        )
    )
    pilot, _sink = _pilot(tmp_path, config)

    state = pilot.run()

    assert state["halted"] is True
    assert [item["node"] for item in state["node_statuses"]] == [
        "idea_formalizer_node",
        "formalizer_runner_bridge_node",
    ]
    assert state["node_statuses"][-1]["status"] == "blocked"
    assert state["blocked_actions"][-1]["action_type"] == "canonical_write"
    packet_ref = _load(
        tmp_path, state["graph_output_paths"]["final_candidate_review_packet_reference"]
    )
    assert packet_ref["status"] == "not_produced"


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
        ("provider_api_call", "provider/api"),
        ("network_access", "public.example/api"),
    ],
)
def test_adversarial_actions_remain_blocked(action_type: str, target_path: str):
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(ToolAction(action_type, target_path))

    assert sink.records[-1].action_type == action_type
    assert sink.records[-1].decision == "blocked"


def test_out_of_prefix_graph_output_is_blocked():
    context, sink = _context()

    with pytest.raises(BlockedActionError):
        context.require_allowed(
            ToolAction(RUN_SCRATCH_LANGGRAPH_PILOT, "scratch/OTHER-WP/outputs/run.json")
        )

    assert sink.records[-1].decision == "blocked"


def test_langgraph_pilot_source_has_no_provider_or_network_client():
    source = (ROOT / "tools/research_agents/langgraph_pilot.py").read_text(encoding="utf-8")
    for forbidden in ("requests", "httpx", "urllib", "OpenAI", "Anthropic", "socket"):
        assert forbidden not in source
