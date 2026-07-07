# WP-RUNNER-PREVIOUS-BAR-HIGHLOW-REF-01 Status

## Scope

Runner/formalization support unblocker for the frozen `LAB-RT-HYP-002R`
previous-bar high/low breakout reference. The package adds a closed
`previous_bar_refs` Strategy Spec primitive and compiler route for OHLCV
`high[t-1]` and `low[t-1]` references.

Changed files:

- `research/schemas/strategy_spec.schema.json`
- `tools/registry/validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `docs/status_entries/WP-RUNNER-PREVIOUS-BAR-HIGHLOW-REF-01.md`
- `scratch/WP-RUNNER-PREVIOUS-BAR-HIGHLOW-REF-01/*`

## Capability

`online_ohlcv_primitives.previous_bar_refs[]` is additive and closed. It accepts
only `source="ohlcv"`, `lag_bars=1`, `fields=["high", "low"]`, and
`missing_prior_policy="null_output"`. `primitive_ref` operands may then read
only `field="high"` or `field="low"` from the declared primitive.

The compiler resolves those fields as `ohlcv["high"].shift(1)` and
`ohlcv["low"].shift(1)`. Existing condition evaluation treats null operands as
false, so the first row and rows whose prior bar high/low is missing fail
closed. No arbitrary lag expression, formula, eval, code, SQL, Python, or future
bar reference route is added.

## Boundary

- Research execution performed: `NO`
- Signed frozen set modified: `NO`
- Strategy Spec, Variant Manifest, or Sweep Plan written: `NO`
- Result Population written: `NO`
- Candidate admission, crossing, promotion/readiness, paper/live, runtime, OMS,
  risk, reconciliation, broker/exchange, credential, or private API authority
  created: `NO`
- Dependency changes: `NO`

## Validation

Validation details are recorded in
`scratch/WP-RUNNER-PREVIOUS-BAR-HIGHLOW-REF-01/validation_summary.txt`.
