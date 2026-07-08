# Lab Productization Pipeline Agent Adapters

## Status And Authority

`WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02` adds the first closed adapter registry
and adapter-backed packet flow for `tools/lab_pipeline`.

The adapter flow is package-local, scratch-only, non-canonical, offline
research-lab material. It grants no canonical evidence, candidate lifecycle,
candidate admission, crossing, promotion/readiness, paper/live/runtime,
scheduler/autonomy, notification, provider/API, credential, dependency/config,
data-acquisition, or protected-path authority.

The flow is entered only after the existing exact-content prereg approval marker
validates. Missing, broad, stale, or mismatched prereg approval keeps the adapter
packet in `awaiting_prereg_approval` and invokes no real modules.

## CLI

The Wave 1 pipeline behavior remains available:

```powershell
python -m tools.lab_pipeline.run --request <request.json> --json
python -m tools.lab_pipeline.run --request <request.json> --approval <approval.json> --json
```

The adapter-backed flow is opt-in after approval:

```powershell
python -m tools.lab_pipeline.run --request <request.json> --approval <approval.json> --run-adapters --json
```

Adapter packets write under:

```text
scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/outputs/<adapter_run_id>/
```

Required packet files are:

- `pipeline_adapter_request.json`
- `pipeline_adapter_state.json`
- `adapter_trace.json`
- `adapter_artifact_index.json`
- `adapter_gap_register.json`
- `non_authority_assertions.json`
- `operator_review_packet.md`

## Closed Registry

The adapter registry is closed and deterministic in
`tools/lab_pipeline/adapter_contract.py`.

Actually adapter-backed now:

- `idea_formalization`: invokes
  `tools.research_agents.idea_formalizer_agent.IdeaFormalizerAgent.run` in
  fake-offline provider mode through ToolContext role `idea_formalizer`, writing
  only package scratch.
- `availability_readiness_classification`: invokes the read-only
  `tools.lab_readiness.readiness.build_readiness_projection` and stores the
  projection in the adapter packet.

Gap-registered now:

- `bridge_spec_variant_sweep_preparation`
- `noncanonical_offline_runner_execution`
- `wfo_oos_gate_review`
- `robustness_diagnostics`
- `candidate_review_packet_preparation`

Those stages remain blocked because current repo truth requires separate
stage-specific approval markers, complete upstream artifacts, or both. The
pipeline prereg approval cannot be substituted for the bridge, robustness, or
candidate-review approvals without weakening the existing ToolContext and
approval contracts. Missing bridge outputs also mean the runner, WFO/OOS gate,
robustness diagnostics, and candidate-review packet cannot be honestly invoked.

## Status Semantics

Adapter stage statuses are closed:

- `adapter_complete`
- `adapter_blocked`
- `adapter_skipped`
- `adapter_failed`
- `awaiting_prereg_approval`
- `blocked_unsafe_to_adapt`

Adapter run statuses are closed:

- `awaiting_prereg_approval`
- `complete_with_gaps`
- `complete_without_gaps`
- `adapter_failed`

The adapter flow does not emit `complete` alone. If any required stage remains
gap-registered, the run status is `complete_with_gaps`.

## Fixture

Committed fixture input:

- `scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/adapter_run_fixture.json`

Committed adapter packet:

- `scratch/WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02/outputs/LADAPT-8f3015b055116a87/`

That fixture intentionally has no approval marker and therefore records
`awaiting_prereg_approval`, zero invoked real modules, and zero gaps. It proves
the adapter packet fails closed before module invocation. A committed approved
adapter run is not included because this package cannot self-author a Karl
approval marker.

## Boundary

The adapter flow preserves:

- exact-content prereg approval discipline;
- ToolContext role and scratch-prefix controls;
- no provider/API/credential use;
- no canonical Result Population writes;
- no Strategy Spec / Variant Manifest / Sweep Plan canonical mutation;
- no candidate lifecycle, admission, crossing, promotion, or readiness;
- no paper/live/runtime, scheduler/autonomy, notification, dependency/config,
  data-acquisition, or protected-path contact.

Any package that wants the bridge/runner/robustness/candidate-review stages to
move from gap-registered to adapter-backed must provide the exact missing
stage-specific approval/input contract without weakening these boundaries.
