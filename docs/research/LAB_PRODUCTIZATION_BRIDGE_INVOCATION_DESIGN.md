# Lab Productization Bridge Invocation Design

## 1. Executive Summary

WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03 surfaced an architecture collision, not a minor wiring gap. The lab-productization flow needs bridge-preparation functionality inside a product-local, Karl-approved, no-runner stage. The existing formalizer-runner bridge is stricter and older: it accepts only its own ToolContext WP allowlist, legacy scoped formalizer paths, legacy operator bridge approval, and on the unblocked path it invokes the offline runner.

Recommendation: do not reimplement the bridge in the product pipeline and do not weaken the current bridge validations to make adapter wiring convenient. The preferred architecture is a deliberate additive bridge-contract extension that preserves existing legacy behavior unchanged by default while adding a first-class product invocation mode with exact-content Karl approval, package-local scratch output, explicit source-prefix validation, and a bridge-preparation-only path that cannot invoke the runner. A future implementation package must be authorized as a bridge-contract change, not as adapter plumbing.

## 2. Current Repo Facts

- The existing bridge is `tools/research_agents/formalizer_runner_bridge.py`.
- `FormalizerRunnerBridge.__init__` accepts only role `formalizer_runner_bridge` and the WP IDs `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`, `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`, and `WP-RESEARCH-FUNDING-CARRY-02`.
- The bridge derives output root as `scratch/<tool_context.wp_id>/outputs`.
- The bridge validates formalizer source paths against scoped legacy prefixes:
  `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/`,
  `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/formalizer/outputs/`, or
  `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/`.
- The bridge approval contract expects an approval artifact colocated with the formalizer output, with `approved_for_noncanonical_runner_bridge = true`, `approved_by = operator`, `approval_scope = noncanonical_scratch_runner_bridge_only`, timestamp, and matching `source_formalizer_run_id`.
- The bridge validates draft Strategy Specs and derived Strategy Spec / Variant Manifest / Sweep Plan inputs through registry validators before runner invocation.
- The bridge preserves denominator ledgers and writes a `formalizer_runner_bridge_human_review_packet_v1` packet.
- If no blocker exists, the bridge invokes `tools.research_runner.run_offline_sweep` twice: a bridged run with `write_result_population=True` and a direct manual-equivalent reconciliation run with `write_result_population=False`.
- ToolContext permissions include `RUN_NONCANONICAL_OFFLINE_SWEEP` for the bridge role and require noncanonical offline sweep targets under the active WP output prefix.
- The lab pipeline model uses a different exact-content approval contract: `lab_pipeline_prereg_approval_v1`, `approved_by = Karl`, `approval_scope = noncanonical_offline_research_execution_only`, exact approval statement, packet hash binding, and explicit false flags for canonical/candidate/runtime/scheduler/notification authority.
- The lab adapter registry records `bridge_spec_variant_sweep_preparation` as blocked because the existing bridge cannot safely satisfy lab product package-local scratch, product approval, and no-runner requirements.
- The lab pipeline has a CLI through `python -m tools.lab_pipeline.run`, including an opt-in `--run-adapters` path. No separate bridge CLI exists for `FormalizerRunnerBridge`; current bridge use is direct module invocation in tests and agent flows.

## 3. WP03 Blocker Recap

WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03 recorded Outcome B:

- Existing bridge rejects the lab-pipeline bridge adapter WP ID at ToolContext construction.
- Existing bridge rejects package-local formalizer source paths.
- Existing bridge outputs under the bridge or adapter-agent WP output root, not under the lab pipeline bridge adapter package root.
- Existing bridge expects legacy operator approval, while the product flow requires a Karl-signed exact-content approval marker.
- Existing bridge invokes the offline runner when unblocked, while the adapter package forbids runner execution.

The WP03 tests and blocker scratch artifacts prove these are active repo contracts. The product flow therefore cannot call the existing bridge without changing bridge contract semantics, faking approval shape, moving outputs outside package-local scratch, or accidentally executing the runner.

## 4. Design Collision

The collision is between two valid safety models:

- Existing bridge model: a bounded research-agent bridge converts accepted formalizer outputs and legacy operator bridge approval into scratch inputs, denominator ledger, human review packet, and optionally runner/reconciliation evidence under bridge-owned scratch.
- Lab product model: a productized operator flow produces package-local noncanonical packets after Karl exact-content prereg approval, with downstream bridge/runner/WFO/OOS/robustness/candidate-review stages gap-registered until their own contracts are safely satisfied.

The product model needs bridge-preparation functionality. The bridge model currently combines bridge preparation with possible runner execution and legacy approval assumptions. Treating this as simple adapter wiring would create approval drift and runner-coupling risk.

## 5. Option A: Product Adapts To Bridge

Description: the product flow would produce bridge-conformant inputs and approval artifacts while the existing bridge contract remains byte-unchanged.

Facts:

- The product would need accepted formalizer output under a legacy formalizer scratch prefix.
- The product would need an `operator` bridge approval with `noncanonical_scratch_runner_bridge_only` scope.
- The product would need to instantiate ToolContext with one of the bridge-accepted WP IDs.
- Bridge outputs would land under the accepted bridge WP output root, not under the product package local output root.
- If unblocked, the bridge would invoke the offline runner.

Inference:

This is not safe as a product invocation model unless Main/Karl explicitly decide that the product flow may leave package-local output discipline, may rely on legacy operator approval separate from the product prereg marker, and may permit runner execution. Those decisions are not present in repo truth or this package.

Decision:

Do not recommend Option A for the product flow. It can remain the legacy bridge path for legacy research-agent flows, but it is not the correct productization path.

## 6. Option B: Additive Bridge Product-Mode Contract

Description: the bridge gains a first-class explicit product mode. Existing behavior remains unchanged by default. Product mode has its own strict contract rather than an adapter-side compatibility shim.

Required contract fields:

- `bridge_invocation_mode`: closed enum, default legacy behavior unchanged; new value for product preparation mode.
- `source_product_packet_path`: prereg or adapter packet path under the active product package scratch.
- `source_formalizer_output_path`: accepted product-side formalizer output path under the active product package scratch.
- `source_formalizer_output_sha256`: exact-content hash of the formalizer output.
- `product_approval_path`: Karl-signed exact-content product bridge approval marker.
- `product_approval_sha256`: exact-content hash of the approval marker.
- `approved_by`: must be `Karl` for product mode.
- `approval_scope`: a new bridge-specific product-preparation scope, distinct from both legacy bridge approval and broad pipeline prereg approval.
- `authorizes_bridge_preparation`: true.
- `authorizes_runner_execution`: false.
- `authorizes_canonical_write`: false.
- `authorizes_candidate_lifecycle`: false.
- `authorizes_paper_live_runtime`: false.
- `output_root`: must be package-local product scratch for product mode.
- `runner_policy`: closed enum requiring `prepare_only` in product mode.
- `bridge_version`: version identifying the product-mode contract.

Required validation boundaries:

- Reject product mode unless ToolContext role and WP ID are explicitly allowlisted for that mode.
- Reject product mode unless all source paths are inside the active product scratch prefix.
- Reject approval markers that are broad, stale, unsigned by Karl, hash-mismatched, missing exact statement, or authorizing runner/canonical/candidate/runtime paths.
- Keep all legacy bridge input validation for accepted formalizer output, draft Strategy Spec, derived artifacts, denominator integrity, and non-authority flags.
- In product mode, write only bridge-preparation artifacts and never call `_invoke_runner`.
- Preserve no provider/API/network/credential behavior.
- Preserve closed-default ToolContext behavior and audit hard-blocks.

Tests required in a future implementation:

- Legacy default behavior unchanged.
- Product mode rejects legacy operator approval.
- Product mode rejects broad pipeline prereg approval unless a bridge-specific exact approval is present.
- Product mode rejects non-product scratch paths.
- Product mode rejects unsupported ToolContext WP IDs.
- Product mode writes only product package-local scratch outputs.
- Product mode validates derived Strategy Spec / Variant Manifest / Sweep Plan inputs without invoking the runner.
- Product mode cannot set `RUN_NONCANONICAL_OFFLINE_SWEEP`.
- Product mode rejects `authorizes_runner_execution = true`.
- Product mode preserves denominator and review-packet non-authority fields.

Inference:

This option changes the bridge contract, but it does not require weakening existing legacy safety. It creates a parallel strict path with explicit field-level approval, scratch, and no-runner semantics.

Decision:

Recommend Option B, combined with the preparation/execution split from Option C.

## 7. Option C: Bridge Preparation / Runner Execution Split

Facts:

- Current bridge has internal preparation functions: it validates formalizer input, validates draft Strategy Spec, derives scratch Strategy Spec / Variant Manifest / Sweep Plan artifacts, validates derived inputs, builds denominator rows, and writes a human review packet.
- Current `run()` method proceeds into runner invocation when no blockers exist.
- No public no-runner bridge-preparation mode exists in current repo truth.

Inference:

The code has separable preparation concepts, but the supported contract does not expose a safe preparation-only mode. A future implementation would need an explicit mode or method whose contract ends after validated bridge-preparation artifacts and denominator/review packet creation, with runner invocation impossible under that mode.

Decision:

Recommend treating preparation/execution separation as part of the additive bridge product-mode contract. Do not suppress runner execution through monkeypatching, fake blockers, fake data unavailability, or adapter-side wrappers.

## 8. Option D: Product-Side Reimplementation, Rejected Unless Explicitly Authorized

Description: copy or recreate bridge behavior inside `tools/lab_pipeline` or adjacent product code.

Risks:

- Dual-maintenance drift against Strategy Spec / Variant Manifest / Sweep Plan derivation.
- Validator mismatch and future schema drift.
- Approval bypass by translating product prereg approval into bridge approval without bridge owning the semantics.
- Evidence fabrication risk if product code emits bridge-shaped outputs without invoking bridge validation.
- Denominator suppression or hidden failure risk if copied logic misses bridge ledger checks.
- Runner coupling risk if reimplementation later calls runner without inheriting bridge safety gates.

Decision:

Reject Option D for this architecture. It should be considered only if Main/Karl explicitly accept the safety and maintenance tradeoff after proving Options B/C impossible.

## 9. Decision Matrix

| Option | Safety | Drift Risk | Approval Integrity | Runner Separation | Implementation Class | Recommendation |
|---|---:|---:|---:|---:|---|---|
| A. Product adapts to bridge | Low for product flow | Medium | Weak for product approval | None | Product workarounds | Reject for product flow |
| B. Additive product-mode bridge contract | High if strict | Low | Strong | Requires C | Bridge contract change | Recommend |
| C. Preparation / runner split | High if explicit | Low | Strong if paired with B | Strong | Bridge contract change | Recommend with B |
| D. Product-side reimplementation | Low | High | Weak | Unknown | Product duplication | Reject |

## 10. Recommended Path

Preferred architecture:

1. Preserve the existing bridge legacy path unchanged by default.
2. Add a first-class product invocation mode inside the bridge contract only after Main/Karl authorization.
3. Make product mode bridge-preparation-only: validate accepted formalizer output, approval, source paths, draft Strategy Spec, derived Strategy Spec / Variant Manifest / Sweep Plan artifacts, denominator integrity, and non-authority flags, then stop before runner execution.
4. Require a bridge-specific Karl exact-content approval marker for product bridge preparation. Do not reuse the broad lab pipeline prereg approval as bridge approval.
5. Require product-mode output under package-local product scratch.
6. Keep runner execution as a separate later authorization surface that consumes validated bridge-preparation artifacts only if separately approved.

## 11. Required Future Authorization

A future package must be authorized as a bridge-contract implementation package. It should be allowed to touch only the bridge module, the minimum related tests, and product documentation needed to describe the new contract. It should not be authorized as adapter plumbing.

Required Main/Karl decisions:

- Whether a bridge-specific Karl approval marker is required in addition to the pipeline prereg marker. Recommendation: yes.
- Whether product mode may be added to the existing bridge module while preserving legacy behavior unchanged. Recommendation: yes.
- Whether bridge preparation and runner execution must be separate callable/contract modes. Recommendation: yes.
- Whether product-mode output must remain package-local to the product invocation package. Recommendation: yes.

## 12. Forbidden Implementation Shortcuts

- Do not fake legacy `operator` bridge approval from Karl prereg approval.
- Do not broaden the existing bridge approval parser to accept multiple shapes without explicit mode separation.
- Do not add the product WP ID to the legacy bridge allowlist without product-specific validation.
- Do not route product formalizer output through legacy scratch prefixes just to satisfy path checks.
- Do not move product outputs into bridge-owned scratch and call that product-local.
- Do not monkeypatch or flag-disable runner invocation from adapter code.
- Do not create fake bridge blockers to avoid runner execution.
- Do not emit bridge-shaped outputs from the product pipeline without bridge validation.
- Do not write canonical Result Populations, candidate lifecycle records, crossing, promotion/readiness, paper/live/runtime, scheduler/autonomy, notifications, provider/API calls, dependencies/configs/data, or protected paths.

## 13. Risk Register

| Risk | Severity | Design Response |
|---|---:|---|
| Weakening bridge validation | High | Product mode must be explicit and equally strict; legacy default unchanged. |
| Approval-shape drift | High | Require bridge-specific Karl exact-content approval; reject broad prereg substitution. |
| ToolContext bypass | High | Add explicit mode allowlist and tests; never instantiate bridge under fake WP identity. |
| Scratch-prefix bypass | High | Validate product-mode paths against active product scratch prefix. |
| Bridge/runner coupling | High | Product mode must be preparation-only and unable to call runner. |
| Dual-maintenance drift | High | Reject product-side reimplementation. |
| Fabricated bridge outputs | High | Bridge module must own bridge output generation and validation. |
| Canonical/candidate/runtime leakage | Critical | Preserve non-authority fields and hard false approval flags; no canonical, candidate, runtime, paper/live contact. |

## 14. Validation / Evidence References

Evidence inspected:

- `tools/research_agents/formalizer_runner_bridge.py`
- `tools/agent_sandbox/permissions.py`
- `tools/lab_pipeline/model.py`
- `tools/lab_pipeline/orchestrator.py`
- `tools/lab_pipeline/adapters.py`
- `tools/lab_pipeline/adapter_contract.py`
- `tests/test_agent_formalizer_runner_bridge.py`
- `tests/test_lab_pipeline_bridge_adapter.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_ORCHESTRATOR.md`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_AGENT_ADAPTERS.md`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_BRIDGE_ADAPTER.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/repo_truth_discovery.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/bridge_blocker_report.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/adapter_gap_register.md`

Validation results for this package are recorded in
`scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/validation_summary.txt`.

## 15. Open Questions For Main/Karl

- Should product bridge preparation require a bridge-specific Karl approval marker separate from the broad pipeline prereg marker?
- Should product mode be added to `FormalizerRunnerBridge`, or should a narrow bridge module facade own product mode while delegating to the same bridge internals?
- What exact product package WP IDs should be accepted by a future product-mode ToolContext?
- Should product-mode bridge outputs preserve the exact legacy `formalizer_runner_bridge_human_review_packet_v1` schema or use an additive product-mode schema version?
- When runner execution is later authorized, should it consume product-mode bridge-preparation artifacts directly or require an additional runner-specific approval marker?
