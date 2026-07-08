# WP-LABPROD-PIPELINE-ORCHESTRATOR-01 Branch State

## Scope Summary

Adds the first repo-native lab-productization pipeline spine under
`tools/lab_pipeline`. The CLI accepts an operator request, writes a deterministic
scratch pipeline packet, halts at exact-content prereg approval, and continues
only when the Karl file-based approval marker is scoped to non-canonical offline
research execution for the frozen preregistration packet hash.

This branch is scoped as the Wave 1 pipeline state spine / prereg approval
contract. It does not yet invoke the existing idea formalizer,
formalizer-runner bridge, robustness diagnostician, candidate-review packet
agent, WFO/OOS gate, or real offline runner as an end-to-end product flow.
Approved runs produce deterministic non-canonical spine proof only, with
`noncanonical_execution_summary.json` recording `runner_invoked=false`.

## Authority

This package grants only non-canonical, scratch-only, offline research-lab
state-spine / approval-contract authority. It grants no candidate, crossing,
promotion/readiness, paper/live/runtime, scheduler/autonomy, notification,
provider/API, credential, dependency, data, or protected-path authority.

## Repo-Truth Discovery

Current `tools/lab_state` remains the canonical read-only coordinator state
model. Existing agent packages are scratch-only and bind approval semantics to
their own package-specific ToolContext roles and scratch prefixes. This package
therefore adds a new pipeline spine without modifying existing agent semantics
or invoking those agents.

Detailed discovery is recorded in
`scratch/WP-LABPROD-PIPELINE-ORCHESTRATOR-01/repo_truth_discovery.md`.

## Implementation

New files:

- `tools/lab_pipeline/__init__.py`
- `tools/lab_pipeline/model.py`
- `tools/lab_pipeline/state.py`
- `tools/lab_pipeline/orchestrator.py`
- `tools/lab_pipeline/run.py`
- `tests/test_lab_pipeline_orchestrator.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_ORCHESTRATOR.md`
- package scratch notes and validation artifacts

## Validation Status

Final validation summary is recorded in
`scratch/WP-LABPROD-PIPELINE-ORCHESTRATOR-01/validation_summary.txt`.

## Boundary Summary

No `src/`, `lib/`, `configs/`, `.claude/`, `data/`, scheduler implementation,
dashboard/cockpit, candidate registry, canonical Result Population, Strategy
Spec, Variant Manifest, Sweep Plan, trial log, dependency, provider/API,
credential, paper/live/runtime, OMS/risk/reconciliation, or protected path was
changed.

## Non-Authority Statement

Non-canonical lab-productization orchestration only; no canonical evidence,
candidate, crossing, promotion, paper/live/runtime, scheduler/autonomy,
notification, provider/API, credential, dependency, data, or protected-path
authority.

This package does not remove the need for future Codex/Main-approved work
packages to run a full hypothesis test. The required follow-up adapter package
is `WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02`, whose high-level goal is to safely
bind this state spine to existing formalizer / bridge / runner / robustness /
candidate-review packet modules without weakening ToolContext, approval,
scratch-prefix, non-authority, or protected-boundary guarantees.
