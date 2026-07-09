# Scale Budget Contract

## Contract

`product_runner_execute_approval_v1` now includes `approved_sweep_budget` with schema version `product_runner_approved_sweep_budget_v1`.

The contract is exact-content-bound to:

- prepared Strategy Spec path;
- prepared Variant Manifest path;
- prepared Sweep Plan path;
- Variant Manifest id;
- Sweep Plan id;
- `all_manifest_variants` selection mode;
- committed population count;
- selected variant count;
- variant assignment count;
- manifest population cap;
- selected variant id hash;
- Karl-approved `max_variant_count`.

## Enforcement

The runner adapter fails closed before runner invocation if:

- `approved_sweep_budget` is missing;
- `max_variant_count` is not a positive integer;
- selection mode is not `all_manifest_variants`;
- selected ids do not equal all manifest ids;
- committed/declared/selected/trial-budget/assignment counts differ;
- committed population exceeds `max_variant_count`;
- budget fields do not exactly match the prepared artifacts.

The runner adapter fails closed after runner invocation if:

- adapter or direct result row count differs from the approved denominator;
- adapter or direct result variant ids differ from the approved selected ids;
- denominator status counts do not sum to the approved denominator;
- adapter/direct denominator counts differ.

## Non-Authority

The contract grants no canonical write, candidate lifecycle, crossing, promotion/readiness, paper/live/runtime, scheduler/autonomy, notification, provider/API, dependency/config/data-acquisition, protected-path, schema, validator, query-layer, runner, or backtester authority.
