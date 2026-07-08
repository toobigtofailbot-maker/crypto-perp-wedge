# Repo Truth Discovery

## Fact

- Current main SHA at package start: `126d9aaeaad2e5bd67e5163548f1223e6e78df13`.
- Open PR collision check returned `[]`.
- `docs/research/LAB_COORDINATOR_STATE_MODEL.md` defines a read-only
  coordinator state vocabulary implemented by `tools/lab_state`.
- `docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md` defines an inert scheduler
  shell with no executor and no autonomous dispatch.
- Existing bounded research-agent modules live under `tools/research_agents`.
- The formalizer-runner bridge, robustness diagnostician, and candidate review
  packet agents validate exact package-specific ToolContext roles and WP IDs.
- Existing research-agent modules remain package-specific and scratch-prefix
  specific; their approval and ToolContext semantics are not generic pipeline
  adapter interfaces in this PR.

## Inference

The first lab-productization pipeline should not modify existing agent modules
to relax their package-specific guards. A new `tools/lab_pipeline` surface can
provide the operator-invocable state spine and exact prereg approval pause while
preserving those prior agent boundaries.

The current branch should therefore be described as a deterministic state spine
and approval contract, not as proof that the existing idea formalizer,
formalizer-runner bridge, robustness diagnostician, candidate-review packet
agent, WFO/OOS gate, or real offline runner are already chained into one product
flow.

## Decision

Use the preferred new package path `tools/lab_pipeline`. Keep pipeline run-stage
names local to that package and document that they do not alter
`tools/lab_state`. Keep approved execution as deterministic non-canonical spine
proof with `runner_invoked=false`.

## Open Question

Future adapter packages can decide how, or whether, to route approved pipeline
runs into existing bounded agent modules without weakening their ToolContext
roles, approval scopes, and scratch-prefix guarantees.

Named follow-up dependency: `WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02`.

## Future Option

A later package could add adapters for real formalizer/runner/robustness packet
families after the exact cross-WP approval and scratch-prefix contract is
locked.
