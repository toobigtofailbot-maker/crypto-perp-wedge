# WP-AGENT-LANGGRAPH-PILOT-01 Branch State

## Scope Summary

Adds a scratch-only LangGraph orchestration pilot for the existing four-agent research flow: idea formalizer, formalizer-runner bridge, robustness diagnostician, and candidate-review packet preparer. The pilot records graph state, trace, node statuses, ToolContext audit decisions, final packet reference, and a non-authoritative pilot evaluation.

## Main Authorization

Main authorized a LangGraph pilot now that the four-agent non-canonical flow exists. This branch starts from refreshed `origin/main` at PR #548 merge commit `485ecef`.

## Pilot Boundary

LangGraph is used only as an orchestration layer. It receives no authority to write canonical candidate lifecycle entries, canonical Result Populations, Strategy Specs, Variant Manifests, Sweep Plans, trial logs, approvals, freezes, promotions, rankings, paper/live readiness, runtime controls, provider/API/network calls, scheduling, or private/credential paths.

## Dependency Posture

`langgraph` was added to `requirements.txt`. `requirements.lock.txt` records `langgraph==1.2.6` plus the resolver-required transitive dependencies, including LangChain core/protocol packages required by LangGraph. No OpenAI, Anthropic, LangChain provider/model, exchange/API provider, credential, scheduler, Prefect, Temporal, or Hermes dependency was added.

## Repo-Truth Discovery

Discovery is recorded in `scratch/WP-AGENT-LANGGRAPH-PILOT-01/repo_truth_discovery.md`. Current repo truth shows older docs deferred or rejected LangGraph, but the active package explicitly reopens a Main-authorized scratch-only pilot. The current four agent APIs are reusable without granting new authority.

## Graph Shape

The graph is:

```text
idea_formalizer_node
-> formalizer_runner_bridge_node
-> robustness_diagnostician_node
-> candidate_review_packet_node
```

The graph state tracks run ID, fixed input idea, artifact paths, approval marker paths, node statuses, blocked actions, non-authority flags, graph trace, and audit artifact paths.

## ToolContext Preservation

Each graph node instantiates the existing role-specific ToolContext for the existing agent it calls. The pilot adds only `langgraph_pilot_orchestrator` plus `run_scratch_langgraph_pilot`, scoped to `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/`. Prohibited probes remain blocked by the relevant existing ToolContext and are recorded as blocked node state.

## Determinism

The pilot uses a fixed idea, fixed timestamp, deterministic fake-offline formalizer mode, deterministic local 15m OHLCV fixture generation, fixed bridge seed, and fixed robustness bootstrap sample count. Tests assert repeated runs preserve selected stable fields and final packet hash.

## Scratch Outputs

The materialized pilot run writes:

- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/graph_state.json`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/graph_trace.json`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/node_statuses.json`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/final_candidate_review_packet_reference.json`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/pilot_evaluation.md`
- `scratch/WP-AGENT-LANGGRAPH-PILOT-01/outputs/85eaed766d4aa5a2/toolcontext_audit.json`

The graph also generated upstream scratch-only artifacts through existing agent modules; those artifacts remain non-canonical and carry no evidence, lifecycle, ranking, promotion, or paper/live authority.

## Pilot Evaluation

The pilot evaluation finding is `defer`: LangGraph made state transitions and failure capture clearer, but adoption should wait for human review of dependency weight and authority clarity. The finding is advisory only and creates no future adoption authority.

## Adversarial Boundary Tests

Tests prove canonical writes, candidate registration/freeze/promotion/readiness, ranking-as-promotion-ready, paper/live/runtime, OMS/risk/reconciliation/capital, private endpoints, credentials, provider/API/network calls, out-of-prefix graph outputs, and blocked node probes remain blocked and audited.

## Validation Status

- LangGraph pilot, candidate-review, robustness, bridge, and ToolContext focused tests: PASS, 202 tests.
- Result Population and data-availability validator tests: PASS, 69 tests.
- Result Population registry validator: PASS.
- Data feature availability registry validator: PASS.
- Query view discovery: PASS, 124 views listed.
- Diff-scope summary: PASS; dependency files are the only forbidden-pattern matches and are explicitly authorized by the package.
- `git diff --check`: PASS.
- Full pytest initial run completed with 2,174 passed, 1 skipped, 1 failed, and 6 warnings. The sole failure was the known isolated-worktree baseline `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because the gitignored D4A normalized CSV fixture was absent.
- After copying the existing local gitignored D4A normalized fixture from the root checkout into the same worktree path for validation only, full pytest passed: 2,175 passed, 1 skipped, 6 warnings.

## Boundary Summary

Changed implementation is limited to `tools/research_agents/`, the narrow ToolContext permission extension, tests, dependency files, this status entry, and scratch pilot artifacts. No canonical artifact, schema, validator behavior, query behavior, runner/backtester/compiler behavior, data, configs, project-status, runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, private endpoint, credential, scheduler, Prefect, Temporal, or Hermes surface is modified.

## Non-Authority Statement

All pilot graph outputs, upstream generated scratch artifacts, packet references, node statuses, traces, audit records, and evaluation text are scratch-only, non-canonical, non-evidence, not candidate authority, not ranking authority, not promotion authority, not paper/live readiness, not a trading signal, and human-review-required.

## Adoption / Defer / Reject Finding

Finding: defer.

Reason: LangGraph improves graph-state clarity and blocked-node reporting for the four-agent chain, but the dependency weight and authority-boundary clarity should be reviewed before any adoption package. Friction or authority blur remains sufficient reason to stay repo-native.
