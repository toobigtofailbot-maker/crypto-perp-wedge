# Runner Surface Contract

This package adds one closed runner/formalization route:
`online_ohlcv_primitives.previous_bar_refs`.

Allowed config:

- `source`: `ohlcv`
- `lag_bars`: `1`
- `fields`: exactly `["high", "low"]`
- `missing_prior_policy`: `null_output`

Allowed use:

- `primitive_ref` with `field="high"` resolves to the immediately previous
  completed bar high.
- `primitive_ref` with `field="low"` resolves to the immediately previous
  completed bar low.

Null/fail-closed behavior:

- First row has no prior bar and resolves null.
- Rows whose prior bar high/low is missing resolve null.
- Existing condition evaluation turns null operands into predicate false.

Not added:

- No arbitrary lag expression support.
- No formula, eval, code, SQL, Python, or script route.
- No future-bar reference.
- No generic previous-bar field support beyond high/low.
- No candidate, crossing, promotion/readiness, paper/live, runtime, or protected
  execution authority.
