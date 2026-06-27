# ATR Parent-Spec Denominator Route Plan
## Package: WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01

### Problem

In the current Strategy Spec schema, `exit_logic.atr_stop` is a **parent-spec-level**
field. It cannot be varied across variants within a single sweep. The frozen Stage-1
denominator requires three risk-control states:

| State label     | atr_stop_enabled | atr_lookback_bars | atr_multiplier | Rows |
|-----------------|------------------|-------------------|----------------|------|
| no_atr          | false            | —                 | —              | 36   |
| atr_20          | true             | 14                | 2.0            | 36   |
| atr_30          | true             | 14                | 3.0            | 36   |
| **Total**       |                  |                   |                | **108** |

The 36 rows per state share the same signal grid (3 funding lookbacks × 2 entry tail
pairs × 2 exit modes × 3 max-hold bars = 36).

---

### Route: Three scratch parent Strategy Specs + denominator bundler

**Step 1 (next authorized package):** Create three scratch parent Strategy Specs:

```
scratch/<NEXT-WP>/specs/H_FUNDING_FADE_RISKMANAGED_NO_ATR.strategy_spec.json
scratch/<NEXT-WP>/specs/H_FUNDING_FADE_RISKMANAGED_ATR_20.strategy_spec.json
scratch/<NEXT-WP>/specs/H_FUNDING_FADE_RISKMANAGED_ATR_30.strategy_spec.json
```

Each spec is identical to the frozen signal spec except for `exit_logic.atr_stop`.

**Step 2 (next authorized package):** For each parent spec, create:
- A 36-variant Variant Manifest frozen for sweep planning.
- A Sweep Plan referencing the manifest.

The 36 variant IDs within each spec are assigned independently:
`<spec_prefix>-V001` through `<spec_prefix>-V036`.

**Step 3 (next authorized package):** Run each spec separately through
`run_offline_sweep --canonical-15m --evaluation-start 2024-01-01T00:00:00Z
--evaluation-end 2025-01-01T00:00:00Z`.

Each run produces a 36-row result population (scratch, not canonical).

**Step 4 (next authorized package):** Call `bundle_atr_denominator` from
`tools/research_runner/atr_denominator_bundler.py` with the three 36-row slices:

```python
from tools.research_runner.atr_denominator_bundler import bundle_atr_denominator

bundle = bundle_atr_denominator(
    no_atr_rows=no_atr_result_population["variant_result_rows"],
    atr_20_rows=atr_20_result_population["variant_result_rows"],
    atr_30_rows=atr_30_result_population["variant_result_rows"],
)
```

The bundler assigns:
- `risk_control_state`: one of `"no_atr"`, `"atr_20"`, `"atr_30"`
- `composite_row_id`: `f"{risk_control_state}:{variant_id}"`

Output: 108-row list with unique composite_row_ids. No rows are dropped; all
failure/error/data_unavailable rows are preserved in the denominator.

---

### Denominator integrity guarantees

- `validate_bundle_denominator_integrity(bundle)` confirms:
  - 108 total rows
  - 36 rows per state
  - All composite_row_ids unique
  - No unexpected states

- `winner_only_reporting_forbidden = true` (inherited from sweep plan governance)
- All 108 planned rows accounted for in the combined table

---

### Why no schema change is needed now

The route above uses only:
1. Multiple scratch Strategy Specs (each valid under current schema)
2. Standard `run_offline_sweep` with the new `--evaluation-start`/`--evaluation-end` params
3. `bundle_atr_denominator` (new offline-only utility, no schema dependency)

No modifications to `validate_strategy_specs.py` or any schema file are required.

---

### Status in this package

This plan is documented and the bundler utility is implemented and tested.
The three scratch parent Strategy Specs, manifests, and sweep plans are
**NOT** created in this package (that is the Stage-1 retry package's job).

`atr_parent_spec_route_ready: true` — the bundler exists and tests pass,
and the route is fully planned. The next package can follow this plan without
further architectural decisions.
