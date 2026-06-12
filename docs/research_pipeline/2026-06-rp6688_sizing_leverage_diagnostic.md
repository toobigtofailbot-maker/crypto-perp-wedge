# RP-6688 Sizing / Leverage / Cost Diagnostic

## Status / authority boundary

This is a read-only diagnostic. It does not mutate RP-6688, rerun a
backtest, change sizing logic, change cost logic, change assumptions, register
a candidate, rank variants, assert readiness, promote a strategy, or authorize
paper/live/runtime behavior.

The diagnostic consumes committed repo artifacts and code read-only. It is a
classification over the observed `RP-6688` terminal-zero pattern, not an
implementation package.

## Source artifacts

- Result population:
  `research/result_populations/RP-6688.result_population.json`
- Strategy Spec:
  `research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json`
- Variant Manifest:
  `research/variant_manifests/VM-0002.variant_manifest.json`
- Sweep Plan:
  `research/sweep_plans/SWEEP-PLAN-0002.sweep_plan.json`
- Prior checkpoint:
  `docs/research_pipeline/2026-06-rp6688_both_direction_sma_band_checkpoint.md`
- Prior status fragments:
  `docs/status_entries/WP-SPEC-BOTHDIR-01c.md` and
  `docs/status_entries/WP-SPEC-BOTHDIR-01d.md`
- Backtest and evaluation code, inspected read-only:
  `lib/backtest.py`, `lib/evaluation.py`, and the recorded runner reference
  `tools/research_runner/run_offline_sweep.py`

Prior-state checks on refreshed `origin/main`:

- PR #440 is merged at base commit `244f465`.
- `docs/research_pipeline/2026-06-rp6688_both_direction_sma_band_checkpoint.md`
  exists.
- `docs/status_entries/WP-SPEC-BOTHDIR-01d.md` exists.
- `research/result_populations/RP-6688.result_population.json` exists.
- `research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json` exists.
- `research/variant_manifests/VM-0002.variant_manifest.json` exists.
- `research/sweep_plans/SWEEP-PLAN-0002.sweep_plan.json` exists.
- `RP-6688` remains a 10-row complete population with committed denominator
  10 and outcome counts sum 10.
- `RP-6688` records `canonical_real_data` in the runner environment summary.
- `input_identity_hash` remains
  `sha256:ea9ea760ef7a5d30956a4573fc4ca0c39b43a533803667370219f5e3f7ffe386`.
- `result_population_identity_hash` remains
  `sha256:7ee08cc1f30e26c318b39d571b90d25406072329ce4a67bd7c94ec35f98fcdbc`.

## Contradiction being diagnosed

Every `RP-6688` row records:

- `return_pct = -1.0`
- `pnl = -10000.0`
- `drawdown = 1.0`

At the same time, the same rows record win rates from about 61% to 76%, six
positive Sharpe values, and one Sharpe value near +1.0. That combination is
not a clean signal-quality statement by itself. It is consistent with a path
where many individual closed trades can be positive, while fixed-size
BTC-denominated exposure and notional-scaled costs eventually reduce marked
equity to zero.

## Backtest sizing model observed from code

`lib.backtest.run_backtest()` uses a deterministic fixed `order_size` argument,
defaulting to `1.0`. The canonical 15m runner path calls it with:

- `initial_equity=10_000.0`
- `order_size=1.0`
- `fee_bps_taker=4.0`
- `fee_bps_maker=2.0`
- `entry_fee_side="taker"`
- `exit_fee_side="taker"`
- `slippage_bps=1.0`
- `funding_notional_mode="entry_price"`
- `liquidation_mode="zero_equity"`

The position state is directional only: `+1`, `-1`, or `0`. PnL is calculated
as:

```text
+/- (price change) * order_size
```

Therefore, for BTCUSDT with `order_size=1.0`, each open position is one BTC of
notional exposure. The sizing model is fixed contracts/units, not
equity-relative, not fixed USD notional, and not capped as a leverage fraction
of current equity.

`STRAT-SPEC-0002`, `VM-0002`, and `SWEEP-PLAN-0002` do not define an
equity-relative sizing rule. Their realism fields disclose the locked
assumption surface and leave actual order sizing to the offline runner/backtest
path.

## Cost model observed from code

`lib.backtest._bps_cost(price, size, bps)` computes:

```text
abs(price * size) * bps / 10000
```

Fees and slippage are therefore not scaled to starting equity. They are scaled
to trade notional. For the canonical 15m runner:

- entry fee = `4 bps * fill_price * 1.0`
- exit fee = `4 bps * fill_price * 1.0`
- entry slippage = `1 bps * fill_price * 1.0`
- exit slippage = `1 bps * fill_price * 1.0`

Funding is configured with `funding_notional_mode="entry_price"`, but
`RP-6688` records `funding = 0.0` for all rows because the canonical 15m runner
constructs zero funding for the OHLCV-only input.

Equity and zero-equity behavior:

- Marked equity is `cash equity + unrealized PnL`.
- In `zero_equity` mode, if marked equity is `<= 0.0`, the backtester records
  liquidation-style zeroing, sets equity to `0.0`, writes the rest of the
  equity curve as zero, and breaks the loop.
- `RP-6688` rows do not expose `liquidated` or `liquidation_timestamp`.
  However, `return_pct = -1.0`, `pnl = -10000.0`, and `drawdown = 1.0` are
  exactly consistent with final equity being zero under that code path.

## RP-6688 row-level evidence

The table uses pre-registered variant ID order. It is not sorted by
performance and does not identify a favored variant.

Derived fields use only repo-visible facts:

- Estimated position quantity: `1.0` contract/unit for every row, from runner
  and backtest code.
- Cost/equity: `(fees + slippage + funding) / 10000`.
- Average costed fill notional: inferred from `fees / 0.0004`, then divided by
  estimated costed fills. Because each row terminal-zeros and liquidation exits
  do not charge exit cost in `lib/backtest.py`, the estimate uses
  `2 * trade_count - 1` costed fills.
- Implied leverage: average costed fill notional / `10000`.

| variant_id | sma_lookback_bars | band_threshold | return_pct | pnl | drawdown | trade_count | win_rate | sharpe | fees | slippage | funding | estimated quantity | avg costed fill notional | implied leverage | cost/equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20 | 0.0025 | -1.0000 | -10000.00 | 1.0000 | 747 | 0.7068 | -3.3185 | 4712.34 | 1178.08 | 0.00 | 1.0 | 7890.72 | 0.7891 | 0.5890 |
| VAR-000002 | 20 | 0.0050 | -1.0000 | -10000.00 | 1.0000 | 1037 | 0.6683 | -0.0941 | 7695.88 | 1923.97 | 0.00 | 1.0 | 9281.09 | 0.9281 | 0.9620 |
| VAR-000003 | 20 | 0.0100 | -1.0000 | -10000.00 | 1.0000 | 854 | 0.6230 | 0.7334 | 12895.14 | 3223.78 | 0.00 | 1.0 | 18885.68 | 1.8886 | 1.6119 |
| VAR-000004 | 20 | 0.0150 | -1.0000 | -10000.00 | 1.0000 | 1466 | 0.6132 | 0.8303 | 37332.33 | 9333.08 | 0.00 | 1.0 | 31842.66 | 3.1843 | 4.6665 |
| VAR-000005 | 20 | 0.0200 | -1.0000 | -10000.00 | 1.0000 | 555 | 0.6216 | -0.1537 | 13633.02 | 3408.25 | 0.00 | 1.0 | 30732.69 | 3.0733 | 1.7041 |
| VAR-000006 | 50 | 0.0025 | -1.0000 | -10000.00 | 1.0000 | 1096 | 0.7600 | 0.5901 | 8173.68 | 2043.42 | 0.00 | 1.0 | 9326.43 | 0.9326 | 1.0217 |
| VAR-000007 | 50 | 0.0050 | -1.0000 | -10000.00 | 1.0000 | 794 | 0.7179 | -1.0654 | 6355.36 | 1588.84 | 0.00 | 1.0 | 10011.60 | 1.0012 | 0.7944 |
| VAR-000008 | 50 | 0.0100 | -1.0000 | -10000.00 | 1.0000 | 543 | 0.6814 | 0.6157 | 5619.58 | 1404.89 | 0.00 | 1.0 | 12948.33 | 1.2948 | 0.7024 |
| VAR-000009 | 50 | 0.0150 | -1.0000 | -10000.00 | 1.0000 | 360 | 0.6611 | 0.0346 | 3897.31 | 974.33 | 0.00 | 1.0 | 13551.16 | 1.3551 | 0.4872 |
| VAR-000010 | 50 | 0.0200 | -1.0000 | -10000.00 | 1.0000 | 308 | 0.6494 | 0.9972 | 4697.42 | 1174.35 | 0.00 | 1.0 | 19095.20 | 1.9095 | 0.5872 |

`max_drawdown` is not present in `RP-6688`; the row metric field is
`drawdown`.

`fee_cost`, `total_fees`, `slippage_cost`, and `slippage_cost_total` are not
present in `RP-6688`; the row metric fields are `fees` and `slippage`.

## Implied notional and leverage analysis

The fixed quantity is one BTC-equivalent unit. Notional per open position is
therefore approximately:

```text
BTCUSDT fill price * 1.0
```

Relative to `initial_equity=10000`, the implied leverage at any fill is:

```text
BTCUSDT fill price / 10000
```

The committed result population does not include raw candle high/low or
per-trade fill rows, so this diagnostic does not claim an exact full-slice
price high/low from the result artifact. The cost totals do allow a
read-only, formula-based estimate of the realized cost-bearing fill basis.
Across the ten rows, inferred average costed fill notional ranges from about
`7890.72` to `31842.66`, implying about `0.79x` to `3.18x` average costed-fill
exposure versus starting equity.

That is enough to classify the population as materially affected by fixed
unit sizing. A one-contract model changes leverage mechanically as BTC price
changes. It is not normalized to equity, and it can expose a USD 10,000 account
to one BTC of directional PnL during higher-price periods.

## Cost-scale analysis

Fees and slippage are plausible under the configured cost model because they
scale with notional and trade count:

- Fees use 4 bps per costed side.
- Slippage uses 1 bps per costed side.
- In every row, `fees` is exactly 4x `slippage` within rounding, consistent
  with the 4 bps versus 1 bps settings.
- Total direct cost ranges from `4871.64` to `46665.42`, or about `48.72%` to
  `466.65%` of starting equity.
- Funding is zero in all rows and is not the driver.

Costs are therefore large enough to matter. They are not the primary
classification by themselves because the large cost totals arise from the same
fixed one-BTC quantity and notional-scaled bps model. Cost drag is a secondary
mechanism attached to the sizing/leverage setup.

## Classification

Primary classification: **(b) sizing / leverage artifact**.

Rationale:

- The runner uses fixed `order_size=1.0` BTC-equivalent unit against
  `initial_equity=10000`.
- Position notional is price-relative, not equity-relative.
- Costs are charged against notional, not against equity.
- Rows with high win rates and positive Sharpe values still end at exact zero
  equity because a fixed one-BTC position can make losses and costs large
  relative to account equity.
- The uniform `-100%` terminal return across all ten rows is better explained
  as the backtest realism/sizing setup zeroing equity than as proof that the
  symmetric SMA-band signal has no signal-quality value.

Secondary note: direct cost drag is severe in several rows and contributes to
the zeroing path. It is not the primary classification because the fee and
slippage totals are themselves a consequence of notional-scaled costs on a
fixed one-BTC position.

## Integrity concerns, if any

No integrity stop condition is identified from read-only inspection.

Observed constraints and limitations:

- `RP-6688` does not include per-trade rows, raw candle extrema, liquidated
  flag, or liquidation timestamp fields.
- The result schema reports terminal `return_pct`, `pnl`, `drawdown`, cost
  totals, win rate, and Sharpe only.
- The exact terminal-zero timestamp cannot be diagnosed from `RP-6688` alone.
- The row values are consistent with the inspected runner and backtest code:
  fixed size, notional costs, zero-funding OHLCV input, and zero-equity
  terminal behavior.

This diagnostic found no denominator mismatch, no wrong parent lineage, no
wrong data provenance, no validator/code contradiction, and no material
code/result inconsistency.

## Recommendation for future package

Future package option, not authorized here: a separate design-first
backtest-realism assumptions package for equity-relative sizing, leverage caps,
and cost-model reporting.

That future package would be protected/backtest-core-adjacent. It should be
design-first, separately authorized, and explicitly non-runtime unless a later
approved package changes that boundary. This diagnostic does not authorize
implementation, artifact mutation, reruns, candidate registration, ranking,
readiness, promotion, or paper/live/runtime use.

## What this diagnostic does not change

This diagnostic changes no:

- result population;
- Strategy Spec;
- Variant Manifest;
- Sweep Plan;
- schema;
- validator;
- compiler;
- runner;
- query-layer behavior;
- data artifact;
- candidate registry;
- dashboard implementation;
- runtime, paper/live, OMS, risk, broker, exchange, or protected path.

It does not rerun `RP-6688`, recalculate results, create a new result
population, select a variant, or assert paper/live readiness.

## Stop / escalation notes

No stop condition fired.

Smallest viable next package if Main wants to proceed from this classification:
a design-only realism-assumptions package covering equity-relative sizing,
leverage caps, direct-cost reporting, and how future canonical result
populations should disclose sizing and terminal-zero mechanics. That package
would be separate from this diagnostic and would require explicit authorization
before any implementation or rerun.
