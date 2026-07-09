# Lab Productization Bounded Sweep Scale

## Summary

`WP-LABPROD-BOUNDED-SWEEP-SCALE-06` enables approved large bounded sweeps inside the completed product pipeline without changing runner or backtester semantics.

The implementation adds an exact-content `approved_sweep_budget` contract to the product runner execute approval. The contract is derived from the prepared Variant Manifest and Sweep Plan, and it must prove:

- `selection_mode = all_manifest_variants`;
- selected ids equal all manifest variant ids;
- committed, declared, selected, trial-budget, assignment, and parent-manifest counts match;
- `committed_population_count <= max_variant_count`;
- product output remains noncanonical scratch only.

## Product Pipeline Behavior

The product bridge still prepares Strategy Spec / Variant Manifest / Sweep Plan artifacts and stops before runner execution.

The product runner adapter now fails closed before invoking `run_offline_sweep` unless Karl's runner execute approval includes the exact budget contract for those prepared artifacts.

After execution, both adapter and direct runner result populations must contain exactly the approved variant ids and approved row count. Any row shrinkage, missing variant, unexpected variant, budget excess, unsupported outcome, or adapter/direct denominator mismatch fails closed.

The product gates adapter carries the same scale budget into the advisory packet with caveats. The advisory packet remains noncanonical and advisory-only.

## Denominator Vocabulary

The adapter preserves the runner outcome categories currently exposed by repo truth:

- `successful` -> `completed`
- `failed` -> `failed`
- `invalid` -> `invalid`
- `excluded` / `filtered` -> `pruned`
- `errored` / `aborted` / `data_unavailable` / `not_attempted` -> `blocked`

No native product runner `no_trade` outcome category exists in the current runner result-population vocabulary. If a future runner vocabulary adds no-trade or non-trading rows, this scale layer must keep them denominator-visible before claiming support.

## Non-Authority

This package writes no canonical Result Population, candidate registry row, candidate lifecycle record, crossing, promotion/readiness marker, scheduler/autonomy hook, notification, provider/API call, dependency/config/data-acquisition change, paper/live/runtime change, OMS/risk/reconciliation/order/broker/exchange change, schema change, validator change, query-layer change, runner semantics change, or backtester change.

## Validation Evidence

Focused tests cover:

- default 8-row product runner path;
- explicit 5-row denominator status mapping;
- 1000-row synthetic bounded sweep with completed/failed/invalid/pruned/blocked visibility;
- budget-exceeded fail-closed behavior before runner invocation;
- row-shrinkage fail-closed behavior after runner output;
- advisory-packet propagation of scale budget and caveats.
