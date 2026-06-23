# WP-AGENT-LANGGRAPH-PILOT-01 Repo-Truth Discovery

## Existing Agent Module Entry Points

- `tools.research_agents.idea_formalizer_agent.IdeaFormalizerAgent.run()` accepts a bounded BTCUSDT idea, uses `fake_offline` deterministically by default, and writes `formalized_idea.json`, optional scratch draft Strategy Spec, and `human_review_packet.json` under `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/<run_id>/`.
- `tools.research_agents.formalizer_runner_bridge.FormalizerRunnerBridge.run()` consumes an accepted formalizer artifact plus colocated bridge approval, derives scratch Strategy Spec / VM / Sweep copies, invokes the real offline runner on a local 15m fixture, and writes bridge packet, denominator ledger, and scratch Result Population-shaped output under `scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/<run_id>/`.
- `tools.research_agents.robustness_diagnostician_agent.RobustnessDiagnosticianAgent.run()` consumes bridge packet, bridge Result Population-shaped artifact, bridge denominator ledger, and explicit robustness approval, then writes deterministic advisory diagnostics and review packet under `scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/<run_id>/`.
- `tools.research_agents.candidate_review_packet_agent.CandidateReviewPacketAgent.run()` consumes formalizer, bridge, robustness, and explicit candidate-review approval paths, validates lineage and denominator preservation, and writes scratch packet JSON/Markdown under `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/<run_id>/`.

## Graph Node Input / Output Contracts

- `idea_formalizer_node` input is the fixed pilot idea. Output paths are formalized idea, human-review packet, and draft Strategy Spec.
- `formalizer_runner_bridge_node` input is the formalizer output and an operator bridge approval marker generated through the formalizer ToolContext. Output paths are the bridge denominator ledger, human-review packet, derived scratch inputs, and Result Population-shaped runner artifact.
- `robustness_diagnostician_node` input is the bridge packet, bridge runner artifact, bridge denominator ledger, and robustness approval marker. Output paths are robustness diagnostics and robustness review packet.
- `candidate_review_packet_node` input is the formalizer, bridge, robustness, and candidate-review approval bundle. Output paths are candidate-review packet JSON and Markdown.
- The graph state records `run_id`, `input_idea`, all artifact path groups, operator approval paths, `node_statuses`, `blocked_actions`, `graph_trace`, `toolcontext_audit_paths`, and non-authority flags.

## ToolContext Action Boundaries

- Existing node actions stay routed through their existing roles and package IDs.
- The pilot adds one graph-level role, `langgraph_pilot_orchestrator`, and one action, `run_scratch_langgraph_pilot`, scoped to `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/`.
- Existing hard prohibitions still block canonical writes, candidate registration/freeze/promotion/readiness, ranking-as-promotion-ready, paper/live/runtime, OMS/risk/reconciliation/capital, private endpoints, credentials, provider/API/network calls, dependency mutation outside the package, evidence suppression/deletion, ToolContext bypass, and out-of-prefix outputs.
- Prohibited node probes route through the relevant existing node ToolContext and halt the graph with blocked node state.

## Dependency Convention

- `pyproject.toml` contains minimal project metadata and Ruff configuration only.
- `requirements.txt` lists unpinned top-level runtime dependencies.
- `requirements.lock.txt` is UTF-16 LE and records pinned resolved dependencies.
- LangGraph was not present before this package. The safe addition path is `langgraph` in `requirements.txt` plus pinned `langgraph==1.2.6` and required transitive dependencies in `requirements.lock.txt`.
- The resolver installed LangChain core/protocol packages required by LangGraph, but no OpenAI, Anthropic, LangChain provider/model, credential, or exchange/API provider package was added.

## Existing LangGraph / Orchestration Truth

- Older repo docs rejected or deferred LangGraph as overkill for the earlier Claude-only stack.
- The active execution package explicitly reopens a Main-authorized scratch-only LangGraph pilot after the four-agent flow exists.
- The current decision remains pilot-only: LangGraph may orchestrate, but ToolContext remains the authority boundary.

## Test Fixture Strategy

- The pilot uses one fixed input idea, fixed timestamp, deterministic fake-offline formalizer provider, deterministic generated 15m OHLCV CSV fixture, fixed bridge seed, and fixed robustness bootstrap sample count.
- The fixed idea avoids extra detected features so the merged bridge remains within its existing SMA/stddev adapter contract.
- Tests copy only required repo templates and lifecycle reference files into a temp repo root, then run the real existing agent modules.

## Known Blockers

- None for a scratch-only pilot.
- Adoption is not automatic because the dependency set is materially larger than the repo-native orchestrator and requires human review of dependency weight and authority clarity.
