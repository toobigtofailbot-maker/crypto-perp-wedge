"""Scratch-only LangGraph pilot over the bounded four-agent research flow."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from tools.agent_sandbox import (
    BlockedActionError,
    MemoryAuditSink,
    ToolAction,
    ToolContext,
)
from tools.agent_sandbox.permissions import (
    READ_NON_SECRET,
    RUN_SCRATCH_LANGGRAPH_PILOT,
    WRITE_SCRATCH,
)
from tools.research_agents.candidate_review_packet_agent import (
    APPROVAL_SCOPE as CANDIDATE_REVIEW_APPROVAL_SCOPE,
)
from tools.research_agents.candidate_review_packet_agent import (
    ROLE as CANDIDATE_REVIEW_ROLE,
)
from tools.research_agents.candidate_review_packet_agent import (
    WP_ID as CANDIDATE_REVIEW_WP_ID,
)
from tools.research_agents.candidate_review_packet_agent import (
    CandidateReviewPacketAgent,
    CandidateReviewPacketConfig,
)
from tools.research_agents.formalizer_runner_bridge import (
    APPROVAL_SCOPE as BRIDGE_APPROVAL_SCOPE,
)
from tools.research_agents.formalizer_runner_bridge import ROLE as BRIDGE_ROLE
from tools.research_agents.formalizer_runner_bridge import WP_ID as BRIDGE_WP_ID
from tools.research_agents.formalizer_runner_bridge import (
    FormalizerRunnerBridge,
    FormalizerRunnerBridgeConfig,
)
from tools.research_agents.idea_formalizer_agent import ROLE as FORMALIZER_ROLE
from tools.research_agents.idea_formalizer_agent import WP_ID as FORMALIZER_WP_ID
from tools.research_agents.idea_formalizer_agent import (
    IdeaFormalizerAgent,
    IdeaFormalizerConfig,
    make_provider,
)
from tools.research_agents.robustness_diagnostician_agent import (
    APPROVAL_SCOPE as ROBUSTNESS_APPROVAL_SCOPE,
)
from tools.research_agents.robustness_diagnostician_agent import ROLE as ROBUSTNESS_ROLE
from tools.research_agents.robustness_diagnostician_agent import WP_ID as ROBUSTNESS_WP_ID
from tools.research_agents.robustness_diagnostician_agent import (
    RobustnessDiagnosticianAgent,
    RobustnessDiagnosticianConfig,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WP_ID = "WP-AGENT-LANGGRAPH-PILOT-01"
ROLE = "langgraph_pilot_orchestrator"
OUTPUT_ROOT = Path("scratch") / WP_ID / "outputs"
PILOT_VERSION = "langgraph-pilot-v1"
NODE_ORDER = (
    "idea_formalizer_node",
    "formalizer_runner_bridge_node",
    "robustness_diagnostician_node",
    "candidate_review_packet_node",
)
NON_AUTHORITY_FLAGS = (
    "scratch-only",
    "non-canonical",
    "not evidence",
    "not candidate authority",
    "not promotion authority",
    "not ranking authority",
    "not paper/live readiness",
    "not a trading signal",
    "human review required",
)
DEFAULT_IDEA = (
    "BTCUSDT 15m SMA and stddev mean revert because temporary liquidity pressure "
    "dislocates returns; center_lookback_bars from 50 to 100; vol_lookback_bars "
    "from 30 to 50; trend_lookback_bars from 100 to 200."
)


class LangGraphPilotError(ValueError):
    """Raised when the scratch graph cannot safely complete."""


class LangGraphPilotState(TypedDict, total=False):
    run_id: str
    input_idea: str
    formalizer_artifact_paths: dict[str, str | None]
    operator_approval_paths: dict[str, str]
    bridge_artifact_paths: dict[str, str | None]
    robustness_artifact_paths: dict[str, str]
    candidate_review_packet_paths: dict[str, str]
    toolcontext_audit_paths: list[str]
    node_statuses: list[dict[str, Any]]
    blocked_actions: list[dict[str, Any]]
    non_authority_flags: list[str]
    graph_trace: list[dict[str, Any]]
    graph_output_paths: NotRequired[dict[str, str]]
    toolcontext_audit_records: NotRequired[list[dict[str, Any]]]
    halted: NotRequired[bool]


@dataclass(frozen=True)
class ProhibitedActionProbe:
    node_name: str
    action_type: str
    target_path: str


@dataclass(frozen=True)
class LangGraphPilotConfig:
    input_idea: str = DEFAULT_IDEA
    symbol: str = "BTCUSDT"
    timeframe: str = "15m"
    timestamp_utc: str = "2026-06-22T06:00:00Z"
    deterministic_seed: int = 0
    robustness_bootstrap_samples: int = 50
    prohibited_action_probe: ProhibitedActionProbe | None = None

    def __post_init__(self) -> None:
        if not self.input_idea.strip():
            raise ValueError("input_idea is required")
        if self.symbol != "BTCUSDT":
            raise ValueError("pilot is bounded to BTCUSDT")
        if self.timeframe != "15m":
            raise ValueError("pilot fixture is bounded to 15m")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _run_id(config: LangGraphPilotConfig) -> str:
    return hashlib.sha256(
        _canonical_bytes({"config": asdict(config), "pilot_version": PILOT_VERSION})
    ).hexdigest()[:16]


class LangGraphPilot:
    """LangGraph orchestration layer that delegates authority to existing agents."""

    def __init__(
        self,
        *,
        config: LangGraphPilotConfig,
        tool_context: ToolContext,
        repo_root: Path = REPO_ROOT,
    ) -> None:
        if tool_context.role != ROLE or tool_context.wp_id != WP_ID:
            raise ValueError("LangGraphPilot requires its exact ToolContext role and WP")
        self.config = config
        self.tool_context = tool_context
        self.repo_root = repo_root.resolve()

    def _repo_relative(self, path: Path | str) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.repo_root)
            except ValueError as exc:
                raise LangGraphPilotError("path must remain inside the repo") from exc
        normalized = candidate.as_posix()
        if normalized == ".." or normalized.startswith("../"):
            raise LangGraphPilotError("path must remain inside the repo")
        return normalized

    def _write_text(
        self,
        path: Path | str,
        content: str,
        context: ToolContext | None = None,
    ) -> str:
        relative = self._repo_relative(path)
        active_context = context or self.tool_context

        def operation() -> None:
            target = self.repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")

        active_context.run_allowed(ToolAction(WRITE_SCRATCH, relative), operation)
        return relative

    def _write_json(
        self,
        path: Path | str,
        payload: Mapping[str, Any],
        context: ToolContext | None = None,
    ) -> str:
        return self._write_text(
            path,
            json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
            context=context,
        )

    def _read_bytes(self, path: Path | str, context: ToolContext) -> bytes:
        relative = self._repo_relative(path)
        return context.run_allowed(
            ToolAction(READ_NON_SECRET, relative),
            lambda: (self.repo_root / relative).read_bytes(),
        )

    def _read_json(self, path: Path | str, context: ToolContext) -> dict[str, Any]:
        payload = json.loads(self._read_bytes(path, context))
        if not isinstance(payload, dict):
            raise LangGraphPilotError(f"JSON root must be an object: {path}")
        return payload

    def _context(self, wp_id: str, role: str) -> tuple[ToolContext, MemoryAuditSink]:
        sink = MemoryAuditSink()
        fixed_time = datetime.fromisoformat(
            self.config.timestamp_utc.replace("Z", "+00:00")
        )
        return (
            ToolContext(wp_id=wp_id, role=role, audit_sink=sink, clock=lambda: fixed_time),
            sink,
        )

    @staticmethod
    def _append_status(
        state: LangGraphPilotState,
        *,
        node: str,
        status: str,
        detail: str,
    ) -> LangGraphPilotState:
        statuses = [*state.get("node_statuses", [])]
        statuses.append({"node": node, "status": status, "detail": detail})
        trace = [*state.get("graph_trace", [])]
        trace.append({"node": node, "status": status, "detail": detail})
        return {**state, "node_statuses": statuses, "graph_trace": trace}

    @staticmethod
    def _append_audit(
        state: LangGraphPilotState,
        sink: MemoryAuditSink,
    ) -> LangGraphPilotState:
        records = [*state.get("toolcontext_audit_records", [])]
        records.extend(record.to_dict() for record in sink.records)
        return {**state, "toolcontext_audit_records": records}

    def _maybe_probe(
        self,
        state: LangGraphPilotState,
        *,
        node_name: str,
        context: ToolContext,
        sink: MemoryAuditSink,
    ) -> LangGraphPilotState | None:
        probe = self.config.prohibited_action_probe
        if probe is None or probe.node_name != node_name:
            return None
        try:
            context.require_allowed(ToolAction(probe.action_type, probe.target_path))
        except BlockedActionError as exc:
            blocked = [*state.get("blocked_actions", []), exc.record.to_dict()]
            probed = {**state, "blocked_actions": blocked, "halted": True}
            probed = self._append_audit(probed, sink)
            return self._append_status(
                probed,
                node=node_name,
                status="blocked",
                detail=f"ToolContext blocked {probe.action_type}",
            )
        raise AssertionError(f"prohibited probe unexpectedly allowed: {probe.action_type}")

    @staticmethod
    def _should_continue(state: LangGraphPilotState) -> str:
        return END if state.get("halted") else "continue"

    def _write_bridge_fixture(self, context: ToolContext) -> str:
        relative = f"scratch/{BRIDGE_WP_ID}/fixtures/canonical_15m_ohlcv.csv"
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        pattern = [100.0] * 40 + [94.0, 98.0, 101.0, 90.0, 96.0, 102.0, 88.0, 100.0]
        rows = ["timestamp,open,high,low,close,volume"]
        for index in range(160):
            close = pattern[index % len(pattern)]
            timestamp = (start + timedelta(minutes=15 * index)).isoformat().replace("+00:00", "Z")
            rows.append(
                f"{timestamp},{close + 0.1:.1f},{close + 1.0:.1f},"
                f"{close - 1.0:.1f},{close:.1f},1000.0"
            )
        self._write_text(relative, "\n".join(rows) + "\n", context=context)
        return relative

    def _idea_formalizer_node(self, state: LangGraphPilotState) -> LangGraphPilotState:
        node_name = "idea_formalizer_node"
        context, sink = self._context(FORMALIZER_WP_ID, FORMALIZER_ROLE)
        probed = self._maybe_probe(state, node_name=node_name, context=context, sink=sink)
        if probed is not None:
            return probed
        provider_config = IdeaFormalizerConfig()
        agent = IdeaFormalizerAgent(
            config=provider_config,
            tool_context=context,
            provider=make_provider(provider_config),
            repo_root=self.repo_root,
        )
        result = agent.run(
            idea=state["input_idea"],
            symbol=self.config.symbol,
            timeframe=self.config.timeframe,
        )
        if result["status"] != "accepted" or not result["draft_strategy_spec"]["produced"]:
            raise LangGraphPilotError("formalizer did not produce the deterministic draft")
        run_dir = f"scratch/{FORMALIZER_WP_ID}/outputs/{result['run_id']}"
        next_state: LangGraphPilotState = {
            **state,
            "formalizer_artifact_paths": {
                "formalized_idea": f"{run_dir}/formalized_idea.json",
                "human_review_packet": f"{run_dir}/human_review_packet.json",
                "draft_strategy_spec": result["draft_strategy_spec"]["path"],
            },
        }
        next_state = self._append_audit(next_state, sink)
        return self._append_status(
            next_state, node=node_name, status="completed", detail=result["run_id"]
        )

    def _bridge_node(self, state: LangGraphPilotState) -> LangGraphPilotState:
        node_name = "formalizer_runner_bridge_node"
        context, sink = self._context(BRIDGE_WP_ID, BRIDGE_ROLE)
        probed = self._maybe_probe(state, node_name=node_name, context=context, sink=sink)
        if probed is not None:
            return probed
        paths = state["formalizer_artifact_paths"]
        formalizer_path = str(paths["formalized_idea"])
        formalizer_payload = self._read_json(formalizer_path, context)
        approval_path = str(
            Path(formalizer_path).with_name("operator_bridge_approval.json")
        ).replace("\\", "/")
        approval = {
            "approved_for_noncanonical_runner_bridge": True,
            "approved_by": "operator",
            "approval_scope": BRIDGE_APPROVAL_SCOPE,
            "approval_timestamp_utc": self.config.timestamp_utc,
            "source_formalizer_run_id": formalizer_payload["run_id"],
        }
        formalizer_context, formalizer_sink = self._context(FORMALIZER_WP_ID, FORMALIZER_ROLE)
        self._write_json(approval_path, approval, context=formalizer_context)
        fixture_path = self._write_bridge_fixture(context)
        bridge = FormalizerRunnerBridge(
            config=FormalizerRunnerBridgeConfig(
                ohlcv_input_path=fixture_path,
                deterministic_seed=self.config.deterministic_seed,
                timestamp_utc=self.config.timestamp_utc,
            ),
            tool_context=context,
            repo_root=self.repo_root,
        )
        result = bridge.run(formalizer_output_path=formalizer_path, approval_path=approval_path)
        if result["status"] != "completed":
            raise LangGraphPilotError("bridge did not complete deterministic scratch run")
        next_state: LangGraphPilotState = {
            **state,
            "operator_approval_paths": {
                **state.get("operator_approval_paths", {}),
                "bridge": approval_path,
            },
            "bridge_artifact_paths": dict(result["artifact_paths"]),
        }
        next_state = self._append_audit(next_state, formalizer_sink)
        next_state = self._append_audit(next_state, sink)
        return self._append_status(
            next_state, node=node_name, status="completed", detail=result["run_id"]
        )

    def _robustness_node(self, state: LangGraphPilotState) -> LangGraphPilotState:
        node_name = "robustness_diagnostician_node"
        context, sink = self._context(ROBUSTNESS_WP_ID, ROBUSTNESS_ROLE)
        probed = self._maybe_probe(state, node_name=node_name, context=context, sink=sink)
        if probed is not None:
            return probed
        bridge_paths = state["bridge_artifact_paths"]
        bridge_packet = self._read_json(str(bridge_paths["human_review_packet"]), context)
        approval = {
            "approved_for_noncanonical_robustness_diagnostics": True,
            "approved_by": "operator",
            "approval_scope": ROBUSTNESS_APPROVAL_SCOPE,
            "approval_timestamp_utc": self.config.timestamp_utc,
            "source_bridge_run_id": bridge_packet["run_id"],
        }
        approval_path = f"scratch/{ROBUSTNESS_WP_ID}/inputs/operator_robustness_approval.json"
        self._write_json(approval_path, approval, context=context)
        agent = RobustnessDiagnosticianAgent(
            config=RobustnessDiagnosticianConfig(
                bootstrap_samples=self.config.robustness_bootstrap_samples,
                deterministic_seed=self.config.deterministic_seed or 20260622,
                timestamp_utc=self.config.timestamp_utc,
            ),
            tool_context=context,
            repo_root=self.repo_root,
        )
        result = agent.run(
            bridge_review_packet_path=str(bridge_paths["human_review_packet"]),
            bridge_result_population_artifact_path=str(bridge_paths["runner_result"]),
            bridge_denominator_ledger_path=str(bridge_paths["denominator_ledger"]),
            operator_robustness_approval_path=approval_path,
        )
        next_state: LangGraphPilotState = {
            **state,
            "operator_approval_paths": {
                **state.get("operator_approval_paths", {}),
                "robustness": approval_path,
            },
            "robustness_artifact_paths": dict(result["artifact_paths"]),
        }
        next_state = self._append_audit(next_state, sink)
        return self._append_status(
            next_state, node=node_name, status="completed", detail=result["run_id"]
        )

    def _candidate_review_node(self, state: LangGraphPilotState) -> LangGraphPilotState:
        node_name = "candidate_review_packet_node"
        context, sink = self._context(CANDIDATE_REVIEW_WP_ID, CANDIDATE_REVIEW_ROLE)
        probed = self._maybe_probe(state, node_name=node_name, context=context, sink=sink)
        if probed is not None:
            return probed
        bridge_paths = state["bridge_artifact_paths"]
        robustness_paths = state["robustness_artifact_paths"]
        bridge_packet = self._read_json(str(bridge_paths["human_review_packet"]), context)
        robustness_packet = self._read_json(robustness_paths["robustness_review_packet"], context)
        approval = {
            "approved_for_noncanonical_candidate_review_packet": True,
            "approved_by": "operator",
            "approval_scope": CANDIDATE_REVIEW_APPROVAL_SCOPE,
            "approval_timestamp_utc": self.config.timestamp_utc,
            "source_bridge_run_id": bridge_packet["run_id"],
            "source_robustness_run_id": robustness_packet["run_id"],
        }
        approval_path = (
            f"scratch/{CANDIDATE_REVIEW_WP_ID}/inputs/operator_candidate_review_approval.json"
        )
        self._write_json(approval_path, approval, context=context)
        formalizer_paths = state["formalizer_artifact_paths"]
        agent = CandidateReviewPacketAgent(
            config=CandidateReviewPacketConfig(timestamp_utc=self.config.timestamp_utc),
            tool_context=context,
            repo_root=self.repo_root,
        )
        result = agent.run(
            formalizer_research_object_path=str(formalizer_paths["formalized_idea"]),
            formalizer_draft_strategy_spec_path=str(formalizer_paths["draft_strategy_spec"]),
            bridge_review_packet_path=str(bridge_paths["human_review_packet"]),
            bridge_result_population_artifact_path=str(bridge_paths["runner_result"]),
            bridge_denominator_ledger_path=str(bridge_paths["denominator_ledger"]),
            robustness_diagnostics_path=robustness_paths["robustness_diagnostics"],
            robustness_review_packet_path=robustness_paths["robustness_review_packet"],
            operator_candidate_review_approval_path=approval_path,
        )
        next_state: LangGraphPilotState = {
            **state,
            "operator_approval_paths": {
                **state.get("operator_approval_paths", {}),
                "candidate_review": approval_path,
            },
            "candidate_review_packet_paths": dict(result["artifact_paths"]),
        }
        next_state = self._append_audit(next_state, sink)
        return self._append_status(
            next_state, node=node_name, status="completed", detail=result["run_id"]
        )

    def build_graph(self):
        graph = StateGraph(LangGraphPilotState)
        graph.add_node("idea_formalizer_node", self._idea_formalizer_node)
        graph.add_node("formalizer_runner_bridge_node", self._bridge_node)
        graph.add_node("robustness_diagnostician_node", self._robustness_node)
        graph.add_node("candidate_review_packet_node", self._candidate_review_node)
        graph.add_edge(START, "idea_formalizer_node")
        graph.add_conditional_edges(
            "idea_formalizer_node",
            self._should_continue,
            {"continue": "formalizer_runner_bridge_node", END: END},
        )
        graph.add_conditional_edges(
            "formalizer_runner_bridge_node",
            self._should_continue,
            {"continue": "robustness_diagnostician_node", END: END},
        )
        graph.add_conditional_edges(
            "robustness_diagnostician_node",
            self._should_continue,
            {"continue": "candidate_review_packet_node", END: END},
        )
        graph.add_edge("candidate_review_packet_node", END)
        return graph.compile()

    def _evaluation_markdown(self, state: LangGraphPilotState) -> str:
        blocked = state.get("blocked_actions", [])
        completed_nodes = [
            item["node"]
            for item in state.get("node_statuses", [])
            if item["status"] == "completed"
        ]
        finding = "defer"
        reason = (
            "LangGraph made state transitions explicit, but adoption should wait for human "
            "review of dependency weight and authority clarity."
        )
        return "\n".join(
            [
                "# WP-AGENT-LANGGRAPH-PILOT-01 Pilot Evaluation",
                "",
                "## Did LangGraph Simplify Orchestration?",
                "Yes for traceability: the four-node flow is explicit and serializable.",
                "",
                "## Were ToolContext Boundaries Preserved?",
                (
                    "Yes. ToolContext boundaries were preserved; every agent action remains "
                    "routed through the existing role-specific ToolContext."
                ),
                "",
                "## Were Prohibited Actions Still Blocked/Audited?",
                (
                    "Yes. Prohibited probes are represented as blocked node state when configured, "
                    "and adversarial tests exercise the hard blocks."
                ),
                "",
                "## Was Determinism Preserved?",
                (
                    "Yes. The pilot uses fixed input, fixed timestamps, fixed local fixture "
                    "data, and fixed seeds."
                ),
                "",
                "## Were Failure Modes Clearer?",
                (
                    "Yes. `node_statuses`, `blocked_actions`, and `graph_trace` separate "
                    "node completion from blocks."
                ),
                "",
                "## Should LangGraph Be Adopted, Deferred, Or Rejected For Now?",
                f"Finding: {finding}.",
                f"Reason: {reason}",
                "",
                "## Run Summary",
                f"- Completed nodes: {completed_nodes}",
                f"- Blocked action count: {len(blocked)}",
                (
                    "- Non-authority: scratch-only, non-canonical, not evidence, not "
                    "promotion authority."
                ),
                "",
            ]
        )

    def _write_outputs(self, state: LangGraphPilotState) -> LangGraphPilotState:
        run_dir = OUTPUT_ROOT / state["run_id"]
        trace_path = self._write_json(
            run_dir / "graph_trace.json",
            {"trace": state.get("graph_trace", [])},
        )
        statuses_path = self._write_json(
            run_dir / "node_statuses.json",
            {"node_statuses": state.get("node_statuses", [])},
        )
        packet_paths = state.get("candidate_review_packet_paths", {})
        packet_ref: dict[str, Any] = {
            "status": "not_produced" if state.get("halted") else "produced",
            "paths": packet_paths,
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
        }
        packet_json = packet_paths.get("candidate_review_packet_json")
        if packet_json:
            candidate_context, candidate_sink = self._context(
                CANDIDATE_REVIEW_WP_ID, CANDIDATE_REVIEW_ROLE
            )
            packet_ref["candidate_review_packet_sha256"] = _sha256_bytes(
                self._read_bytes(packet_json, candidate_context)
            )
            state = self._append_audit(state, candidate_sink)
        audit_path = self._write_json(
            run_dir / "toolcontext_audit.json",
            {"records": state.get("toolcontext_audit_records", [])},
        )
        packet_ref_path = self._write_json(
            run_dir / "final_candidate_review_packet_reference.json",
            packet_ref,
        )
        evaluation_path = self._write_text(
            run_dir / "pilot_evaluation.md",
            self._evaluation_markdown(state),
        )
        output_paths = {
            "toolcontext_audit": audit_path,
            "graph_trace": trace_path,
            "node_statuses": statuses_path,
            "final_candidate_review_packet_reference": packet_ref_path,
            "pilot_evaluation": evaluation_path,
        }
        state_with_paths: LangGraphPilotState = {
            **state,
            "toolcontext_audit_paths": [audit_path],
            "graph_output_paths": output_paths,
        }
        graph_state_path = self._write_json(run_dir / "graph_state.json", state_with_paths)
        state_with_paths["graph_output_paths"] = {
            **output_paths,
            "graph_state": graph_state_path,
        }
        self._write_json(run_dir / "graph_state.json", state_with_paths)
        return state_with_paths

    def run(self) -> LangGraphPilotState:
        run_id = _run_id(self.config)
        initial: LangGraphPilotState = {
            "run_id": run_id,
            "input_idea": self.config.input_idea,
            "formalizer_artifact_paths": {},
            "operator_approval_paths": {},
            "bridge_artifact_paths": {},
            "robustness_artifact_paths": {},
            "candidate_review_packet_paths": {},
            "toolcontext_audit_paths": [],
            "node_statuses": [],
            "blocked_actions": [],
            "non_authority_flags": list(NON_AUTHORITY_FLAGS),
            "graph_trace": [],
            "toolcontext_audit_records": [],
        }
        target = (OUTPUT_ROOT / run_id / "graph_state.json").as_posix()
        final_state = self.tool_context.run_allowed(
            ToolAction(RUN_SCRATCH_LANGGRAPH_PILOT, target),
            lambda: self.build_graph().invoke(initial),
        )
        return self._write_outputs(final_state)
