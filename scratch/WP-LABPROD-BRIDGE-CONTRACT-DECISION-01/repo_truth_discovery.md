# Repo Truth Discovery

## Package

`WP-LABPROD-BRIDGE-CONTRACT-DECISION-01`

## Base And Preflight

- Refreshed `main` equals `origin/main` at `7435debccdd970018e4d2f8d3d88f605c12181e9`.
- Open PR check returned no open PRs.
- Suggested branch did not exist locally or remotely before creation.
- No equivalent `LAB_PRODUCTIZATION_BRIDGE_CONTRACT_DECISION` artifact existed before this package.

## Files Inspected

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/README.md`
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`
- `docs/ai/codex/VALIDATION_POLICY.md`
- `docs/ai/codex/VALIDATION_MATRIX.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `tools/research_agents/formalizer_runner_bridge.py`
- `tests/test_agent_formalizer_runner_bridge.py`
- `tests/test_lab_pipeline_bridge_adapter.py`
- `tools/agent_sandbox/permissions.py`
- `tools/agent_sandbox/__init__.py`
- `tools/lab_pipeline/model.py`
- `tools/lab_pipeline/orchestrator.py`
- `tools/lab_pipeline/adapters.py`
- `tools/lab_pipeline/adapter_contract.py`
- `tools/lab_pipeline/gate_actions.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_BRIDGE_ADAPTER.md`
- `docs/research/LAB_PRODUCTIZATION_BRIDGE_INVOCATION_DESIGN.md`
- `docs/status_entries/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03.md`
- `docs/status_entries/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01.md`
- `docs/status_entries/WP-LABPROD-COCKPIT-SYNTAXFIX-01.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/repo_truth_discovery.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/bridge_blocker_report.md`
- `scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/repo_truth_discovery.md`
- `scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/design_option_matrix.json`

## Existing Bridge Contract Facts

### Code Facts

- Bridge module path: `tools/research_agents/formalizer_runner_bridge.py`.
- Constants:
  - `WP_ID = "WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01"`.
  - `DONCHIAN_ADAPTER_WP_ID = "WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01"`.
  - `FUNDING_RESEARCH_WP_ID = "WP-RESEARCH-FUNDING-CARRY-02"`.
  - `ROLE = "formalizer_runner_bridge"`.
  - `APPROVAL_SCOPE = "noncanonical_scratch_runner_bridge_only"`.
  - `BRIDGE_VERSION = "formalizer-runner-bridge-v1"`.
- `FormalizerRunnerBridge.__init__` requires `tool_context.role == ROLE` and `tool_context.wp_id` in the three legacy WP IDs.
- `FormalizerRunnerBridge.__init__` derives `self.output_root = Path("scratch") / tool_context.wp_id / "outputs"`.
- `_validate_formalizer_contract` selects one of the legacy formalizer output prefixes and requires the path to end with `/formalized_idea.json`.
- `_validate_formalizer_contract` requires `schema_version = agent_formalized_idea_v1`, `status = accepted`, nonempty `run_id`, BTCUSDT 15m, a supported family, a produced draft Strategy Spec path, and scratch-only non-authority.
- `_require_approval` requires approval colocated under the formalizer run prefix, `approved_for_noncanonical_runner_bridge = true`, `approved_by = operator`, `approval_scope = noncanonical_scratch_runner_bridge_only`, nonempty timestamp, and matching `source_formalizer_run_id`; funding-on also requires `approved_funding_cost_mode = on`.
- `_validate_draft` reads the draft Strategy Spec from the expected formalizer prefix and calls `validate_strategy_specs`.
- `_derive_inputs` creates scratch Strategy Spec, Variant Manifest, Sweep Plan, and lineage/approval metadata.
- `_validate_derived_inputs` calls `validate_strategy_specs` and `validate_variant_sweep_artifacts`.
- `_invoke_runner` calls `run_offline_sweep` through `RUN_NONCANONICAL_OFFLINE_SWEEP`.
- `run()` reads formalizer and approval JSON, validates contract and approval, validates drafts, derives inputs, validates derived inputs, and, when not blocked, calls `_invoke_runner` twice with `write_result_population=True` and `write_result_population=False`.
- `run()` writes `denominator_ledger.json` with schema `formalizer_runner_bridge_denominator_ledger_v1`.
- `run()` writes `human_review_packet.json` with schema `formalizer_runner_bridge_human_review_packet_v1`.
- `_assert_denominator` hard-blocks denominator suppression via `ToolAction("evidence_suppression", ...)`.

### Test Facts

- `tests/test_agent_formalizer_runner_bridge.py::test_approved_bridge_runs_real_runner_and_reconciles` proves the approved legacy bridge invokes the runner and writes valid derived inputs, denominator ledger, and human review packet.
- `tests/test_agent_formalizer_runner_bridge.py::test_missing_bridge_approval_is_blocked_and_audited` proves missing/false legacy approval is blocked via `approval_gate_bypass`.
- `tests/test_agent_formalizer_runner_bridge.py::test_constrained_full_history_data_is_blocked_before_runner` proves data blockers prevent runner invocation and audit `data_availability_bypass`.
- `tests/test_agent_formalizer_runner_bridge.py::test_runner_outcomes_map_to_complete_denominator_statuses` proves denominator status preservation and evidence-suppression blocking.
- `tests/test_agent_formalizer_runner_bridge.py::test_adversarial_actions_are_blocked_and_audited` proves protected/canonical/runtime/adversarial actions are blocked.
- `tests/test_lab_pipeline_bridge_adapter.py::test_bridge_adapter_registry_records_hard_blocker` proves `bridge_spec_variant_sweep_preparation` is blocked in the adapter registry.
- `tests/test_lab_pipeline_bridge_adapter.py::test_existing_bridge_rejects_lab_pipeline_package_toolcontext` proves the lab pipeline package WP ID is rejected by bridge construction.
- `tests/test_lab_pipeline_bridge_adapter.py::test_existing_bridge_output_root_is_not_package_local` proves the bridge output root is not the product package root.
- `tests/test_lab_pipeline_bridge_adapter.py::test_existing_bridge_rejects_package_local_formalizer_prefix` proves product-local formalizer prefixes are rejected by the existing bridge.
- `tests/test_lab_pipeline_bridge_adapter.py::test_existing_bridge_rejects_karl_hash_bound_approval_shape` proves a Karl hash-bound approval shape is rejected by the existing legacy approval gate.

### ToolContext / Permission Facts

- `tools/agent_sandbox/permissions.py` grants role `formalizer_runner_bridge` `READ_NON_SECRET`, `WRITE_SCRATCH`, `RUN_READ_ONLY_VALIDATION`, and `RUN_NONCANONICAL_OFFLINE_SWEEP`.
- The same policy scopes `WRITE_SCRATCH` and `RUN_NONCANONICAL_OFFLINE_SWEEP` to `scratch/<wp_id>/...` under the active WP.
- `approval_gate_bypass`, `data_availability_bypass`, `evidence_suppression`, `toolcontext_bypass`, protected runtime actions, provider/API calls, credential access, and canonical/candidate actions are hard-blocked.

## Lab Productization Contract Facts

### Code Facts

- `tools/lab_pipeline/model.py` defines `APPROVAL_SCHEMA_VERSION = lab_pipeline_prereg_approval_v1`.
- Product prereg approval uses `APPROVAL_SCOPE = noncanonical_offline_research_execution_only`.
- Product prereg approval uses an exact statement: "Authorizes only non-canonical offline research execution for the exact frozen preregistration packet content."
- Product non-authority flags set canonical evidence, candidate lifecycle, canonical crossing, promotion/readiness, paper/live/runtime, scheduler/autonomy, notifications, and provider/API/credential use to false.
- `tools/lab_pipeline/orchestrator.py::_approval_requirement` requires Karl approval fields and packet hash binding.
- `tools/lab_pipeline/orchestrator.py::_validate_approval` rejects non-Karl actors, wrong scope, wrong statement, missing noncanonical flag, hash mismatch, missing timestamp, and true broad authority flags.
- `tools/lab_pipeline/orchestrator.py::_validate_output_root` limits in-repo pipeline output roots to the pipeline package scratch root.
- `tools/lab_pipeline/adapters.py::_validate_adapter_output_root` limits in-repo adapter output roots to the adapter package scratch root.
- `tools/lab_pipeline/adapter_contract.py::build_adapter_registry` records the bridge stage as `implementation_status = blocked`, with blocker reason naming ToolContext WP allowlist, source formalizer scratch prefixes, bridge output root, and legacy operator approval shape.

### Docs And Scratch Facts

- `docs/research/LAB_PRODUCTIZATION_PIPELINE_BRIDGE_ADAPTER.md` records WP03 Outcome B.
- `docs/research/LAB_PRODUCTIZATION_BRIDGE_INVOCATION_DESIGN.md` recommends additive product-mode bridge contract plus prepare/execute split, rejects product-side reimplementation, and forbids fake approvals or runner suppression.
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/bridge_blocker_report.md` lists exact blockers: ToolContext WP, source-prefix, output-root, approval contract, runner boundary.
- `scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/design_option_matrix.json` recommends Option B plus Option C and rejects Options A and D for product flow.

## Current Validation Idiom

- Package-specific validation requires JSON parsing for the new JSON artifacts.
- Standard commands required by this package are:
  - `python -m tools.research_query.run --list-views`
  - `python -m tools.registry.validate_result_populations`
  - `python -m tools.registry.validate_candidate_registry`
  - `python tools/dev/diff_scope_summary.py`
  - `git diff --check`
  - `git diff --cached --check`
  - `git status --short`
- Repo guidance says docs-only packages do not run full pytest by default, but this package's command list wins for the named validators and diff checks.

## Fact / Inference / Decision / Open Question

### Fact

The existing bridge cannot be product-invoked from current lab productization code without changing at least one bridge contract: ToolContext WP allowlist, source-prefix validation, output-root derivation, approval shape, or runner coupling.

### Inference

An additive product-mode contract can preserve legacy behavior if it is mode-explicit, fail-closed, and byte-regressed against legacy fixtures. A product-mode approval path can be at least as strict as legacy if it retains actor/scope/path/source-run/timestamp checks and adds Karl identity, exact statement, source and approval hashes, output-root binding, stale rejection, explicit false authority flags, and non-inferability from broad prereg approval.

### Decision Proposed

Recommend Karl review of additive product mode plus prepare/execute split. Do not implement in this package.

### Open Questions

- Exact final product-mode WP allowlist.
- Exact product-mode approval schema name and approval statement text.
- Whether product-mode review packet reuses `formalizer_runner_bridge_human_review_packet_v1` or adds an additive schema version.
- Exact stale approval window.
- Later runner-consumption approval shape.
