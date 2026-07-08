# WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02 Branch State

## Scope Summary

Adds a closed adapter registry and opt-in adapter-backed packet flow for
`tools/lab_pipeline`. The flow consumes the existing exact-content prereg
approval marker, writes package-local adapter packets, invokes only safe existing
modules where current contracts allow it, and gap-registers every stage that
cannot yet be safely bound.

## Adapter Truth

Actually adapter-backed:

- idea formalization through the existing fake-offline
  `IdeaFormalizerAgent.run` path under ToolContext;
- read-only availability/readiness classification through
  `build_readiness_projection`.

Gap-registered:

- bridge / spec-variant-sweep preparation;
- non-canonical offline runner execution;
- WFO/OOS gate review;
- robustness diagnostics;
- candidate-review packet preparation.

The blocked stages require separate stage-specific approvals and/or missing
upstream artifacts. The pipeline prereg approval is not treated as a substitute.

## Implementation

New files:

- `tools/lab_pipeline/adapter_contract.py`
- `tools/lab_pipeline/adapters.py`
- `tests/test_lab_pipeline_agent_adapters.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_AGENT_ADAPTERS.md`
- package scratch discovery / fixture / validation artifacts

Modified files:

- `tools/lab_pipeline/orchestrator.py`
- `tools/lab_pipeline/run.py`

## Validation Status

Validation summary is recorded in:

- `scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/validation_summary.txt`

## Boundary Summary

No `src/`, `lib/`, `configs/`, `.claude/`, `data/`, cockpit, scheduler,
notification, candidate registry, canonical Result Population, Strategy Spec,
Variant Manifest, Sweep Plan, trial log, dependency, provider/API, credential,
paper/live/runtime, OMS/risk/reconciliation, or protected path was changed.

## Non-Authority Statement

Non-canonical lab-productization adapter flow only. No canonical evidence,
candidate, crossing, promotion/readiness, paper/live/runtime,
scheduler/autonomy, notification, provider/API, credential, dependency, data,
or protected-path authority is created.
