# WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01 Repo-Truth Discovery

## Facts

- Base `fa1994d` contains PR #555 / `WP-RESEARCH-EDGE-SMA-FAMILY-01`.
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json` declares active `donchian` bound to compiler builtin `donchian_v1`.
- The sole Donchian input is OHLCV `high`/`low`. `lookback_bars` is a required integer with minimum 1 and may bind a Strategy Spec parameter.
- Supported outputs are `upper`, `lower`, `mid`, `width`, plus causal breakout fields `upper_lag1`, `lower_lag1`, `mid_lag1`, and `width_lag1`.
- `tools/research_runner/spec_signal_compiler.py` computes full-window rolling high/low and shifts the `*_lag1` outputs by one bar. Existing compiler tests cover breakout-safe comparison and future-mutation no-lookahead behavior.
- The Strategy Spec grammar supports `indicator_ref`, parameter-bound lookbacks, `gt`/`lt`, explicit long/short groups, and side-specific exits. The offline sweep runner consumes this grammar.
- The existing formalizer is a deterministic provider-shaped adapter around `STRAT-SPEC-0003`; the existing bridge copies VM-0003/SWEEP-PLAN-0003 compatibility shapes, validates scratch artifacts, invokes the real offline runner twice for reconciliation, and preserves a full outcome ledger.
- Donchian is derivable from the public OHLCV archive. No funding signal is needed. Bridge funding-cost mode remains explicit and defaults to `off` because the current runner bridge has no explicit funding-on input.
- No Donchian reference appears in canonical `research/result_populations/RP-*.result_population.json` files.
- Prior canonical Donchian research does exist: H-002 is concluded `NO-GO` with `REP-0003`, and H-012/`REP-0032` includes a 15m Donchian breakout with funding filter and a pure-Donchian comparator. Therefore this package makes no family-novelty claim.

## Decision

Proceed with a scratch-only adapter because compiler, schema, and runner support exist. Treat the brief's "not-yet-concluded archetype" premise as stale. This package proves machine reach only; it does not reopen, supersede, or reinterpret prior Donchian conclusions.

## Bounded Adapter Shape

- Family ID: `donchian_channel_breakout_v1`.
- Entry: completed-bar close greater than `upper_lag1` for long; close less than `lower_lag1` for short.
- Exit: opposite lagged channel.
- Grid: `channel_lookback_bars` in `[20, 55]`.
- No intrabar breakout, ATR stop/target, session exit, funding signal, new operator, new indicator, or post-hoc narrowing.
- Freshness requires no SMA/stddev indicator references and non-canonical IDs distinct from STRAT-SPEC-0003, VM-0003, SWEEP-PLAN-0003, and RP-7134.

## Data Caveat

The committed proof uses a deterministic scratch OHLCV fixture to exercise the real offline runner. It is adapter-validation input, not canonical evidence and not the follow-on research dataset.
