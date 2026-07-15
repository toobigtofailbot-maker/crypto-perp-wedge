# H-004-R2 Gate C-VP exact-content approval packet

Status: **FROZEN — KARL EXACT-CONTENT APPROVAL REQUIRED**

No authoritative approval or audit write has occurred. The protected writer has not been invoked.

## Exact approval artifact

- Approval ID: `VPAPP-20260715-H004R201`
- Authoritative target: `research/strategy_spec_variant_planning_approvals/VPAPP-20260715-H004R201.variant_planning_approval.json`
- Frozen proposal: `scratch/WP-CANON-H004-VP-APPROVAL-GATED-02/frozen_variant_planning_approval.json`
- Frozen proposal bytes: `3695`
- Whole-file SHA-256: `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a`
- Contract-core SHA-256: `sha256:4b8e126870c918e88ac42336427c3ba495bcacb6433bd3741b0a01c712bf99f0`
- Proposed `approved_at`: `2026-07-15T18:08:31.172496Z`

## Canonical parent and Gate-C lineage

- Parent ID/path: `STRAT-SPEC-0007` at `research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json`
- Parent whole-file SHA-256: `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`
- Embedded status: `review_requested`
- Gate-C audit: `research/canonical_crossing_audit/strategy_spec_writes.jsonl`, 1-based line `1`
- Gate-C raw-line SHA-256 including LF: `sha256:ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2`
- Gate-C approval ID: `GATE-C-H004-R2-0001`

## Bounded future VM contract

- VM ID/path: `VM-0007` at `research/variant_manifests/VM-0007.variant_manifest.json`
- Search-family ID: `SF-H004-R2-EMA-PULLBACK-CONTINUATION-1D-0001`
- Ordered axes:
  1. `pullback_ema_bars` integer values `[10,20,30]`
  2. `trend_fast_ema_bars` integer values `[40,50,60]`
  3. `atr_multiplier` milli-values `[2000,2500,3000]`
  4. `max_holding_bars` integer values `[30,45,60]`
- Product proof: `3 × 3 × 3 × 3 = 81`
- Population cap: `81`
- Committed population: `81`
- Denominator: `committed_pre_registered_population_count`
- Adaptive search: `false`
- Post-hoc mutation forbidden: `true`
- Authority: `one_bounded_variant_manifest_preparation_only`

## Authority boundary

Only `authorizes_variant_manifest_preparation=true` and `authorizes_one_manifest_only=true`.

Every downstream authority flag is fixed `false`: strategy-Spec mutation, Gate C, Gate Q, queue admission, dispatch, research execution, result population, candidate lifecycle, ranking, recommendation, promotion readiness, scheduler autonomy, notifications, runtime, paper/live, and OMS/risk/reconciliation.

This approval creates no VM, Sweep, dataset, Gate Q, queue item, dispatch, execution, result, candidate, ranking, recommendation, runtime, paper/live, OMS, risk, or reconciliation state.

## Exact authorization required

Stage B may proceed only if Karl approves this exact ID/target, whole-file hash, contract-core hash, and the complete VM/search-family/axes/population contract above. Any changed byte, ID, path, hash, axis, value, population fact, or authority flag requires a new freeze and a new exact authorization.
