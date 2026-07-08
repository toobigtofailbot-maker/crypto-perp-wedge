# Karl Review Packet

## 1. Decision Subject

Whether to approve, reject, or request changes to the proposed additive bridge product-mode contract plus explicit bridge-preparation / runner-execution split.

This packet does not implement the change.

## 2. Why This Is Karl-Gated

The bridge is an evidence-integrity boundary. Product bridge invocation would change approval semantics, source path binding, output-root binding, validation ownership, and runner reachability. The current repo already rejected adapter plumbing around this collision. A protected contract decision is required before code moves.

## 3. Current Bridge Contract Facts

- Bridge module: `tools/research_agents/formalizer_runner_bridge.py`.
- Current role: `formalizer_runner_bridge`.
- Current accepted WPs: `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`, `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`, `WP-RESEARCH-FUNDING-CARRY-02`.
- Current output root: `scratch/<tool_context.wp_id>/outputs`.
- Current source prefixes: legacy formalizer / Donchian / funding scratch prefixes.
- Current approval: `approved_by = operator`, `approval_scope = noncanonical_scratch_runner_bridge_only`, timestamp, matching source formalizer run id, and bridge approval boolean.
- Current unblocked behavior: derive and validate scratch Strategy Spec / Variant Manifest / Sweep Plan, write denominator ledger and human review packet, then invoke the offline runner twice for bridged and direct manual-equivalent reconciliation.
- Current product collision is proven by tests that reject the lab product WP ToolContext, product-local source prefix, product output-root expectation, and Karl hash-bound approval shape.

## 4. Proposed Additive Product-Mode Contract

Add a first-class product mode while preserving legacy default behavior unchanged.

Product mode would require:

- explicit mode value: `product_bridge_prepare_only`;
- product-specific ToolContext/WP allowlist;
- source product packet path/hash binding;
- product-local source formalizer output path/hash binding;
- product-local approval marker path/hash binding;
- Karl exact-content bridge-preparation approval;
- output under product package-local scratch;
- bridge-owned validation of formalizer, draft Strategy Spec, derived Strategy Spec, Variant Manifest, Sweep Plan, denominator, and review packet;
- explicit false flags for runner, canonical, candidate, paper/live/runtime, scheduler, notification, provider/API/credential, dependency/config/data, and protected authority;
- no runner invocation.

## 5. Proof Obligation: Product Approval As Strict As Legacy Approval

Verdict from this packet: `as_strict_or_stricter_if_implemented_as_specified`.

Reason: product mode preserves actor, scope, path, source run, and timestamp checks while adding Karl identity, exact statement, source and approval hash binding, product/pipeline run binding, bridge stage binding, stale rejection, output-root binding, non-inferability from broad prereg approval, and explicit false authority flags.

Open strictness items for Karl:

- exact product bridge-preparation approval scope string;
- exact approval statement text;
- exact stale-approval window;
- exact product-mode WP allowlist.

## 6. Prepare/Execute Split

The proposed split is:

- `legacy_bridge_run`: current behavior unchanged.
- `product_bridge_prepare_only`: bridge preparation only, no runner.
- `future_runner_adapter_execution`: separate later authority surface, not approved here.

Runner boundary begins at `_invoke_runner`, `run_offline_sweep`, or `RUN_NONCANONICAL_OFFLINE_SWEEP`. Product mode must not reach that boundary.

## 7. Legacy Byte-Regression Plan

A future implementation must run deterministic legacy bridge invocations before and after the change and compare derived Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, review packet, runner artifacts where deterministic, returned paths, and audit records. If byte-for-byte comparison is impossible due to volatility and no repo-truth deterministic mode exists, implementation must stop for Karl decision.

## 8. New-Path Validation Plan

Future product-mode validation must prove:

- product ToolContext allowlist;
- rejection of unsupported WPs;
- Karl exact-content bridge marker required;
- legacy operator approval rejected;
- broad prereg approval rejected;
- stale/hash/path/output-root/authority mismatches rejected;
- bridge validators run;
- output stays product-local scratch;
- denominator and review packet preserved;
- runner not invoked and runner permission not requested.

## 9. Risks

Main risks:

- weaker approval side door;
- accidental legacy bridge drift;
- ToolContext or scratch-prefix bypass;
- broad prereg approval used as bridge approval;
- fabricated bridge-shaped outputs;
- runner invoked during preparation;
- bridge validators bypassed;
- denominator/review-packet drift;
- partial artifact leakage;
- canonical/candidate/runtime/scheduler/provider/protected authority leakage;
- this packet misread as implementation authorization.

The packet mitigates these through exact approval, mode separation, hash/path binding, bridge-owned validation, byte-regression, non-authority assertions, and fail-closed tests.

## 10. Exact Decision Needed From Karl

Karl is asked to decide whether the surfaced contract direction is acceptable as a future implementation target:

- additive bridge product mode;
- bridge-specific Karl exact-content preparation approval;
- product-local scratch;
- bridge-owned validation;
- product bridge preparation only;
- runner execution separated into a later approval surface;
- legacy behavior byte-regressed unchanged.

## 11. What Remains Forbidden Until Karl Approves

- bridge code changes;
- adapter code changes for bridge invocation;
- runner adapter execution;
- approval parser broadening;
- product-side bridge reimplementation;
- fake legacy operator approval;
- scratch-prefix spoofing;
- monkeypatch or fake-blocker runner suppression;
- canonical evidence;
- candidate lifecycle;
- crossing;
- promotion/readiness;
- paper/live/runtime;
- scheduler/autonomy;
- notifications;
- provider/API/credential use;
- dependency/config/data acquisition;
- protected-path touch.
