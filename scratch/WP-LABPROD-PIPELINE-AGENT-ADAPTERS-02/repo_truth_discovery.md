# Repo Truth Discovery

## Fact

- `tools/lab_pipeline` on `origin/main` is a deterministic state spine and
  exact-content prereg approval contract.
- Missing or invalid prereg approval halts at `awaiting_prereg_approval`.
- The existing pipeline docs explicitly named this adapter package as the
  follow-up before the spine could become a true product flow.
- Existing research agents are ToolContext-routed and preserve package/role
  boundaries.
- `tools.lab_readiness` is read-only and does not call providers, runners, or
  protected paths.

## Inference

- The idea formalizer can be safely called only in fake-offline mode through
  ToolContext, writing package scratch.
- Readiness classification can be safely called as a read-only projection.
- Bridge, robustness, and candidate-review agents cannot be safely invoked from
  the pipeline approval alone because they require distinct approval markers and
  source artifact contracts.
- Runner and WFO/OOS stages cannot be honestly invoked without bridge-produced
  validated inputs or a real gate artifact.

## Decision

Implement a closed adapter registry, execute only the safe stages after valid
pipeline prereg approval, and gap-register every unavailable or unsafe stage.

## Open Question

Whether a later gate-action package should create a unified approval artifact
that can satisfy bridge, robustness, and candidate-review contracts without
weakening their existing ToolContext controls.
