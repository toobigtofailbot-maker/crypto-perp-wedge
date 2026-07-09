# WP-LABPROD-BOUNDED-SWEEP-SCALE-06 Status

## Decision

`READY_FOR_REVIEW`

## Summary

Adds bounded-sweep scale enforcement to the completed product pipeline. Product runner execute approvals now require an exact `approved_sweep_budget` contract derived from the prepared Variant Manifest / Sweep Plan. The runner adapter fails closed on missing budget, budget excess, non-all-manifest selection, count mismatch, row shrinkage, or unexpected rows, while preserving product scratch-only output and existing runner semantics.

## Changed Files

- `tools/lab_pipeline/runner_adapter.py`
- `tools/lab_pipeline/gates_adapter.py`
- `tests/test_lab_pipeline_runner_adapter.py`
- `tests/test_lab_pipeline_gates_adapter.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_RUNNER_ADAPTER.md`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_GATES_ADAPTERS.md`
- `docs/research/LAB_PRODUCTIZATION_BOUNDED_SWEEP_SCALE.md`
- `docs/status_entries/WP-LABPROD-BOUNDED-SWEEP-SCALE-06.md`
- `scratch/WP-LABPROD-BOUNDED-SWEEP-SCALE-06/*`

## Scale

Largest focused tested denominator is `1000` synthetic rows. The approval contract supports larger approved counts by exact `max_variant_count`, but does not add unbounded execution, winner narrowing, canonical writes, or candidate authority.

## Boundary

No runner/backtester semantics, result-population schema, validators, query layer, canonical Result Population, candidate lifecycle, crossing, promotion/readiness, paper/live/runtime, OMS, risk, reconciliation, scheduler, notification, provider/API, dependency/config/data-acquisition, `src/`, `lib/`, `configs/`, or protected path is changed.

## Validation

Validation details are recorded in `scratch/WP-LABPROD-BOUNDED-SWEEP-SCALE-06/validation_summary.txt`.
