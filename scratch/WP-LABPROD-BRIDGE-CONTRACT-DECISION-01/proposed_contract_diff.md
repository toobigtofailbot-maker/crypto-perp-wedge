# Proposed Contract Diff

This is a contract-level diff. It is not an applied patch and is not apply-ready code.

## 1. Existing Legacy Bridge Contract

| Contract element | Current legacy behavior |
|---|---|
| Module | `tools/research_agents/formalizer_runner_bridge.py` |
| Public class | `FormalizerRunnerBridge` |
| Config | `FormalizerRunnerBridgeConfig` |
| Role | `ROLE = "formalizer_runner_bridge"` |
| WP allowlist | `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`, `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`, `WP-RESEARCH-FUNDING-CARRY-02` |
| Output root | `scratch/<tool_context.wp_id>/outputs` |
| Formalizer source prefixes | Legacy formalizer / Donchian / funding prefixes only |
| Approval actor | `operator` |
| Approval scope | `noncanonical_scratch_runner_bridge_only` |
| Validation | Bridge calls Strategy Spec and Variant/Sweep validators |
| Runner | `_invoke_runner` calls `run_offline_sweep` when unblocked |
| Review outputs | denominator ledger and human review packet |

Legacy behavior requirement: byte-stable by default after any future implementation.

## 2. Proposed Additive Product-Mode Contract

Add a closed invocation mode with legacy default unchanged:

- `bridge_invocation_mode = legacy_bridge_run` by default.
- `bridge_invocation_mode = product_bridge_prepare_only` for the product path.

Product mode requirements:

- ToolContext role/WP accepted only through an explicit product-mode allowlist.
- Source product packet path and source formalizer output path must be under the active product package scratch root.
- Source formalizer output hash must match the approval marker.
- Product approval marker must be Karl-signed, exact-content, bridge-specific, hash-bound, and scoped to preparation only.
- Output root must be product package-local scratch.
- Runner policy must be `prepare_only`.
- Derived artifacts must be bridge-validated.
- Product mode must never invoke `_invoke_runner` or request `RUN_NONCANONICAL_OFFLINE_SWEEP`.

## 3. Approval Contract Diff

| Current contract element | Proposed product-mode element | Legacy unchanged? | Product validation / rejection |
|---|---|---:|---|
| `approved_by = operator` | `approved_by = Karl` | Yes | Reject non-Karl in product mode |
| `approval_scope = noncanonical_scratch_runner_bridge_only` | bridge-specific preparation-only scope | Yes | Reject broad prereg scope and legacy scope in product mode |
| Timestamp required | Timestamp plus stale-window check | Yes | Reject missing/stale approval |
| Source formalizer run id | Source formalizer run id plus pipeline/product run id | Yes | Reject source/run mismatch |
| No source hash binding | Source formalizer path/hash binding | Yes | Reject hash mismatch |
| No approval hash binding | Approval marker path/hash binding | Yes | Reject hash mismatch |
| Runner allowed by bridge path when unblocked | `authorizes_runner_execution = false` | Yes | Reject true/missing false flag |
| No broad false flags | Explicit false flags for canonical/candidate/runtime/scheduler/provider/dependency/protected authority | Yes | Reject broad authority |

## 4. ToolContext/WP Allowlist Diff

Current: `FormalizerRunnerBridge.__init__` accepts only the three legacy WPs.

Proposed: keep legacy allowlist unchanged for legacy mode. Product mode must define a separate allowlist that accepts only the product bridge-preparation package identity or a Karl-approved closed set. Product mode must not be reachable by adding product WPs to the legacy branch.

Test/regression proof required:

- legacy accepted WPs still accepted;
- legacy rejected WPs still rejected;
- product mode rejects unsupported WPs;
- product mode rejects legacy WPs unless explicitly authorized for product mode;
- ToolContext bypass remains blocked.

## 5. Source-Path Validation Diff

Current: `_validate_formalizer_contract` requires legacy formalizer prefixes.

Proposed: product mode requires product-local formalizer output under the active product package scratch root and hash binding to the product bridge approval marker. Legacy source-prefix behavior remains unchanged.

Fail-closed behavior:

- reject product paths outside active product scratch;
- reject legacy formalizer prefix spoofing in product mode;
- reject path traversal or absolute paths outside repo;
- reject missing or mismatched source hash.

## 6. Output-Root Contract Diff

Current: `self.output_root = scratch/<tool_context.wp_id>/outputs`.

Proposed: legacy mode keeps that derivation. Product mode must set output root to the active product package-local scratch output root and reject any in-repo output root outside it.

Required proof:

- legacy output paths remain byte/path-stable;
- product output paths begin with the active product scratch prefix;
- product mode writes no canonical paths.

## 7. Runner-Coupling / Prepare-Only Diff

Current: `run()` invokes `_invoke_runner` when no blockers exist.

Proposed:

- `legacy_bridge_run` keeps current behavior.
- `product_bridge_prepare_only` ends after bridge-preparation artifacts, denominator ledger, review packet, and validation summary are produced.
- `future_runner_adapter_execution` remains outside this decision packet.

Fail-closed behavior:

- product mode cannot call `_invoke_runner`;
- product mode cannot request `RUN_NONCANONICAL_OFFLINE_SWEEP`;
- product mode rejects approval markers with runner authorization;
- no fake data blockers, monkeypatches, or suppression flags are used to avoid runner invocation.

## 8. Artifact Validation Diff

Current: bridge validates draft Strategy Spec and derived Strategy Spec / Variant Manifest / Sweep Plan.

Proposed: product mode must use bridge-owned validators for the same artifact families. Product code must not fabricate bridge-shaped outputs.

Validation requirement:

- Strategy Spec validation passes;
- Variant Manifest / Sweep Plan validation passes;
- formalizer contract validation passes;
- denominator ledger status set is closed;
- non-authority fields are present.

## 9. Denominator/Review-Packet Diff

Current: bridge writes `formalizer_runner_bridge_denominator_ledger_v1` and `formalizer_runner_bridge_human_review_packet_v1`.

Proposed: product mode must preserve denominator honesty and review packet non-authority. It may either reuse the current schemas with additive product-mode fields or introduce explicit additive product-mode schema versions after Karl approval.

Required fields:

- source product packet path/hash;
- source formalizer output path/hash;
- approval marker path/hash;
- product bridge-preparation mode;
- runner invoked false;
- canonical/candidate/runtime/scheduler/provider/dependency authority false.

## 10. Audit/Permission Diff

Current: ToolContext audits allowed and blocked actions; hard-blocked actions include approval bypass, data availability bypass, evidence suppression, protected runtime actions, provider/API calls, and canonical/candidate actions.

Proposed: product mode must emit or preserve audit evidence showing:

- product-mode ToolContext accepted only through explicit allowlist;
- bridge-owned validators ran;
- runner permission was not requested;
- any rejected broad approval or path mismatch was audited/fail-closed.

## 11. Required Future Implementation Files

If Karl approves implementation, expected touched files would be limited to a bridge-contract implementation package, likely:

- `tools/research_agents/formalizer_runner_bridge.py`
- focused bridge/product tests
- minimal documentation/status/scratch evidence

This packet does not authorize those edits.

## 12. Required Future Tests

- Legacy byte-regression fixture before/after comparison.
- Legacy ToolContext allowlist unchanged.
- Legacy approval shape unchanged.
- Legacy source-prefix validation unchanged.
- Legacy output-root behavior unchanged.
- Legacy runner invocation behavior unchanged.
- Product mode requires product ToolContext allowlist.
- Product mode requires Karl bridge-preparation approval.
- Product mode rejects legacy operator approval.
- Product mode rejects broad prereg approval.
- Product mode rejects stale approval and hash mismatch.
- Product mode rejects runner/canonical/candidate/runtime/scheduler/provider/dependency authority.
- Product mode writes only product scratch outputs.
- Product mode validates derived artifacts.
- Product mode never invokes runner.

## 13. Explicitly Unchanged Legacy Paths

The proposal requires no change to:

- legacy default invocation semantics;
- legacy approval schema;
- legacy accepted WP list in legacy mode;
- legacy formalizer prefixes in legacy mode;
- legacy output root in legacy mode;
- legacy validator calls;
- legacy runner/reconciliation behavior;
- legacy denominator and review packet behavior.
