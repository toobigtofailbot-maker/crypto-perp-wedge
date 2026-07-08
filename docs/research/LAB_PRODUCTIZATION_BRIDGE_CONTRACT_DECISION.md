# Lab Productization Bridge Contract Decision

## 1. Executive Summary

This packet surfaces a protected bridge-contract proposal for Karl review. It does not implement the proposal.

The recommended contract change is an additive product-mode path inside the existing formalizer-runner bridge, paired with an explicit bridge-preparation / runner-execution split. Legacy bridge behavior must remain unchanged by default. Product mode must require a Karl exact-content bridge-preparation approval marker, product-local scratch paths, bridge-owned validation, denominator and review packet preservation, and no runner invocation.

## 2. Current Merged-State Context

Current `main` contains the WP03 blocker evidence, the bridge-invocation design, and the cockpit syntax fix status entry. The live bridge module is `tools/research_agents/formalizer_runner_bridge.py`. The live product adapter registry keeps `bridge_spec_variant_sweep_preparation` blocked because current bridge contracts cannot safely satisfy product package-local scratch, Karl product approval, and no-runner requirements.

Base inspected for this packet: `7435debccdd970018e4d2f8d3d88f605c12181e9`.

## 3. WP03 Outcome B Blocker Recap

WP03 recorded Outcome B: the product pipeline cannot safely invoke the existing bridge as adapter plumbing. The blockers are current contracts, not incidental wiring gaps:

- The bridge accepts only its existing ToolContext role and WP allowlist.
- The bridge accepts only scoped legacy formalizer scratch prefixes.
- The bridge writes under `scratch/<tool_context.wp_id>/outputs`, not product package-local scratch.
- The bridge approval gate expects legacy `approved_by = operator` approval.
- The unblocked bridge path invokes the offline runner.

## 4. Merged Bridge-Invocation Design Conclusion

`docs/research/LAB_PRODUCTIZATION_BRIDGE_INVOCATION_DESIGN.md` recommends preserving the legacy bridge path and adding a deliberate product invocation mode only after protected-surface authorization. It rejects fake legacy approvals, scratch-prefix spoofing, adapter-side bridge-output fabrication, runner monkeypatching, and product-side bridge reimplementation.

## 5. Why This Is A Protected-Surface Contract Decision

The bridge sits on the evidence-integrity boundary. It derives Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, review packet, and runner/reconciliation evidence. A product invocation path changes approval semantics, source binding, scratch roots, validation ownership, and runner reachability. That makes this a Karl-gated contract decision before any code change.

## 6. Current Bridge Contract Map

Facts from `tools/research_agents/formalizer_runner_bridge.py`:

- `ROLE = "formalizer_runner_bridge"`.
- Accepted WPs are `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`, `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`, and `WP-RESEARCH-FUNDING-CARRY-02`.
- `FormalizerRunnerBridge.__init__` rejects other ToolContext role/WP combinations.
- `self.output_root` is `scratch/<tool_context.wp_id>/outputs`.
- `_validate_formalizer_contract` accepts only legacy formalizer output prefixes.
- `_require_approval` expects colocated legacy approval with `approved_for_noncanonical_runner_bridge = true`, `approved_by = operator`, `approval_scope = noncanonical_scratch_runner_bridge_only`, timestamp, and matching `source_formalizer_run_id`.
- `_validate_draft` and `_validate_derived_inputs` run bridge-owned registry validators.
- `_invoke_runner` calls `tools.research_runner.run_offline_sweep`.
- `run()` invokes the runner twice when unblocked: bridged and direct manual-equivalent.
- `run()` writes `formalizer_runner_bridge_denominator_ledger_v1` and `formalizer_runner_bridge_human_review_packet_v1`.

## 7. Proposed Additive Product-Mode Contract

Decision proposal:

- Add a closed `bridge_invocation_mode` with legacy default unchanged.
- Add product mode only for bridge preparation.
- Require product-mode ToolContext role/WP allowlist distinct from legacy.
- Require product-local source paths and output root under the active product package scratch root.
- Require a bridge-specific Karl exact-content approval marker.
- Require source artifact path/hash binding, approval artifact path/hash binding, source run identity, bridge stage identity, output-root binding, and explicit false authority flags.
- Reject broad pipeline prereg approval when bridge-specific approval is absent.
- Reuse bridge-owned validation for accepted formalizer output, draft Strategy Spec, derived Strategy Spec, Variant Manifest, Sweep Plan, denominator, and review packet semantics.
- Forbid runner invocation in product mode.

## 8. Karl Exact-Content Approval Path

Product mode must require an approval shape at least as strict as legacy:

- `approved_by = Karl`.
- A bridge-specific approval scope such as `noncanonical_product_bridge_preparation_only`.
- An exact approval statement for the frozen bridge-preparation packet.
- Hash binding to the source product packet, source formalizer output, and approval marker content.
- Explicit `authorizes_bridge_preparation = true`.
- Explicit false flags for runner execution, canonical writes, candidate lifecycle, paper/live/runtime, scheduler/autonomy, notification, provider/API/credential use, dependency/config/data acquisition, and protected-path touch.
- Rejection of stale, mismatched, broad, legacy, or inferred approvals.

The strictness verdict is recorded as `as_strict_or_stricter_if_implemented_as_specified`.

## 9. Approval Strictness-Equivalence Argument

Legacy approval is narrow but content-light: it requires the operator actor, legacy scope, timestamp, colocated path prefix, source run id, and a boolean noncanonical bridge flag.

The product proposal is at least as strict because it preserves explicit actor, scope, path, source run, and timestamp checks while adding Karl identity, exact statement, source and approval hash binding, pipeline run identity, bridge stage identity, output-root binding, non-inferability from broad prereg approval, stale-approval rejection, and explicit false authority flags.

This verdict holds only if a future implementation preserves these requirements fail-closed and proves legacy byte-regression unchanged.

## 10. Product-Local Scratch Contract

Product mode must write only under the active product package scratch root. It must reject legacy formalizer prefixes for product mode unless those paths are explicitly product-local and hash-bound through the product approval marker. It must not move product artifacts into bridge-owned scratch and call that product-local.

## 11. Bridge-Owned Validation Requirement

The bridge must remain the owner of bridge-preparation validation. Product code must not emit bridge-shaped Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, or review packet artifacts without bridge validation. Future implementation must validate all new-path artifacts through bridge-owned validator calls and fail closed on any validation error.

## 12. Prepare / Execute Split

Required callable distinctions:

- `legacy_bridge_run`: current behavior, unchanged by default, including runner invocation when unblocked.
- `product_bridge_prepare_only`: new proposed behavior, validates and writes bridge-preparation artifacts but cannot invoke the runner.
- `future_runner_adapter_execution`: not authorized by this packet and requires separate approval.

The runner boundary begins at `_invoke_runner` / `RUN_NONCANONICAL_OFFLINE_SWEEP` / `run_offline_sweep`. Product mode must have no path to that permission or call.

## 13. Legacy Byte-Regression Plan

A future implementation must prove legacy behavior is unchanged with direct before/after legacy invocations and byte-for-byte comparisons where deterministic. Required artifacts include derived Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, human review packet, runner artifact path behavior, audit records, ToolContext allowlist behavior, legacy approval behavior, source-prefix behavior, and output-root behavior.

If volatile fields prevent byte comparison and no repo-truth deterministic mode exists, the implementation must stop for Karl decision instead of silently normalizing.

## 14. New-Path Validation Plan

Future product-mode validation must test:

- product-specific ToolContext/WP allowlist;
- rejection of unsupported WPs;
- Karl exact-content bridge-preparation marker requirement;
- rejection of legacy operator approval and broad prereg approval;
- rejection of stale approval, hash mismatch, runner authorization, canonical/candidate/runtime/scheduler/provider/dependency authority;
- product-local scratch writes only;
- bridge-owned validator execution;
- denominator and review packet preservation;
- no runner invocation and no `RUN_NONCANONICAL_OFFLINE_SWEEP` access.

## 15. Risks And Mitigations

Major risks are weaker product approval side door, accidental legacy behavior drift, ToolContext bypass, scratch-prefix bypass, inferred approval from broad prereg, fabricated bridge-shaped outputs, runner invocation during prepare-only, validator bypass, denominator/review-packet drift, partial artifact leakage, authority leakage, and future misuse of this packet as implementation authorization.

Mitigations are mode separation, exact approval schema, path/hash binding, bridge-owned validation, byte-regression proof, explicit false authority flags, fail-closed tests, and non-authority assertions.

## 16. Stop / Escalation Criteria

Future implementation must stop if:

- strictness equivalence cannot be preserved;
- legacy byte-regression is not demonstrable;
- product mode needs fake approvals, spoofed prefixes, monkeypatches, fake blockers, or copied bridge output;
- product preparation cannot be separated from runner execution;
- implementation would require protected runtime, paper/live, OMS, risk, reconciliation, scheduler, provider/API, dependency, config, or data authority.

## 17. What This Package Does Not Authorize

This package authorizes no bridge code change, adapter code change, runner execution, WFO/OOS execution, robustness execution, candidate-review execution, canonical evidence write, Strategy Spec write, Variant Manifest write, Sweep Plan write, candidate lifecycle record, crossing, promotion/readiness, paper/live/runtime contact, scheduler/autonomy, notification, provider/API/credential use, dependency/config/data acquisition, schema/validator/query-layer behavior change, or protected-path touch.

## 18. Karl Decision Packet Location

Karl-facing packet:

- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/karl_review_packet.md`

Supporting artifacts:

- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/proposed_contract_diff.md`
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/approval_strictness_equivalence.md`
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/prepare_execute_split_contract.md`
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/legacy_byte_regression_plan.md`
- `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/new_path_validation_plan.md`

## 19. Validation Summary

Validation is recorded in `scratch/WP-LABPROD-BRIDGE-CONTRACT-DECISION-01/validation_summary.txt`.
