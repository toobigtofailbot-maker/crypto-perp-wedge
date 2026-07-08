# WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01 Blocker Report

## Decision

`BLOCKED`

## Base / Branch

- Branch: `codex/wp-labprod-bridge-product-mode-implement-01`
- Base: `origin/main` at `553f0a53a1987af2f94f392d166a5d206b3d63d3`
- Local `main` was refreshed by fast-forward before branch creation.
- Open PR collision check: `gh pr list --state open --json number,title,headRefName,baseRefName,files,url --limit 100` returned `[]`.
- Local and remote package branch pre-existence checks returned no existing branch before creation.

## Repo-Truth Discovery

### Fact

- Required dependency artifacts from `WP-LABPROD-BRIDGE-CONTRACT-DECISION-01` exist on refreshed `main`, including:
  - `docs/research/LAB_PRODUCTIZATION_BRIDGE_CONTRACT_DECISION.md`
  - `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/proposed_contract_diff.md`
  - `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/approval_strictness_equivalence.md`
  - `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/prepare_execute_split_contract.md`
  - `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/legacy_byte_regression_plan.md`
  - `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/new_path_validation_plan.md`
- Current bridge module is `tools/research_agents/formalizer_runner_bridge.py`.
- Current bridge class/config names are `FormalizerRunnerBridge` and `FormalizerRunnerBridgeConfig`.
- Current legacy role is `formalizer_runner_bridge`.
- Current legacy accepted WP IDs are:
  - `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`
  - `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`
  - `WP-RESEARCH-FUNDING-CARRY-02`
- Current legacy approval parser requires:
  - approval colocated under the formalizer output directory;
  - `approved_for_noncanonical_runner_bridge = true`;
  - `approved_by = operator`;
  - `approval_scope = noncanonical_scratch_runner_bridge_only`;
  - nonempty `approval_timestamp_utc`;
  - matching `source_formalizer_run_id`;
  - `approved_funding_cost_mode = on` when bridge config requests funding mode `on`.
- Current legacy source-prefix validation accepts only:
  - `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/`
  - `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/formalizer/outputs/`
  - `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/`
- Current legacy output root is derived as `scratch/<tool_context.wp_id>/outputs`.
- Current runner invocation location is `_invoke_runner`, which calls `tools.research_runner.run_offline_sweep` through `RUN_NONCANONICAL_OFFLINE_SWEEP`.
- Current bridge-owned validators are `validate_strategy_specs` and `validate_variant_sweep_artifacts`.
- Current denominator/review outputs are:
  - `formalizer_runner_bridge_denominator_ledger_v1`
  - `formalizer_runner_bridge_human_review_packet_v1`
- Current ToolContext permission model grants `formalizer_runner_bridge` the `RUN_NONCANONICAL_OFFLINE_SWEEP` action, and that permission is path-scoped to `scratch/<wp_id>/outputs/`.
- Current lab product approval idiom uses `lab_pipeline_prereg_approval_v1`, `approved_by = Karl`, exact approval statement, packet hash binding, timestamp presence, and explicit false authority flags. It does not define a stale-approval window.

### Fact

Merged contract-decision packet requires product-mode stale approval rejection:

- `docs/research/LAB_PRODUCTIZATION_BRIDGE_CONTRACT_DECISION.md` says product mode must reject stale approvals.
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/proposed_contract_diff.md` says product mode requires a "Timestamp plus stale-window check".
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/new_path_validation_plan.md` requires a stale-approval rejection test.

### Fact

The same merged decision packet records the exact stale-window semantics as unresolved:

- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/approval_strictness_equivalence.md` lists "Exact stale-approval window is an open Karl decision."
- The same file lists "Block implementation if stale approval semantics are not specified."
- The same file lists "missing stale-window decision" under required future blockers.
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/karl_review_packet.md` lists "exact stale-approval window" as an item needing Karl review.
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/repo_truth_discovery.md` lists "Exact stale approval window" as an open question.

## Inference

Implementing product mode without stale rejection would violate the decision packet and the active WP requirement.

Implementing product mode with an invented stale window, such as same-timestamp, 24-hour, same-day, or non-expiring timestamp semantics, would create new approval policy not present in repo truth.

## Decision

Stop under the active package stop condition:

- "If the exact stale-window requirement cannot be implemented without unresolved policy, stop and report."
- "Stop and report if stale-approval semantics are required but undefined."

## Delivered Changes

- This blocker report.
- `docs/status_entries/WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01.md`

No bridge code, tests, schemas, validators, query layer, runner, lab pipeline implementation, canonical artifacts, candidate lifecycle records, runtime, paper/live, OMS, risk, reconciliation, scheduler, provider/API, dependency, config, or data files were changed.

## Validation

Implementation validation was not run because the package stopped before implementation.

Planned scope validation after writing the blocker artifacts:

- `git diff --check`
- `python tools/dev/diff_scope_summary.py`
- changed-file inspection

## Boundary

No product mode was implemented. No runner adapter was implemented. No runner execution path was changed or invoked. No protected runtime boundary was touched.

## Open Escalation

Karl/Main must define the product bridge-preparation approval stale-window semantics before this package can be safely implemented. The needed decision should specify the exact accepted timestamp relation/window and whether it is evaluated against bridge config timestamp, product packet timestamp, wall clock, or another deterministic repo-truth field.
