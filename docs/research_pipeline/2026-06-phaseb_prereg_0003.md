# Phase-B Pre-Registration 0003 Draft Surface

## Status / Authority Boundary

Status: `Karl-approved Option A freeze-candidate surface for PR review`.

This document surfaces the exact uncommitted candidate artifacts drafted by
`WP-PHASEB-PREREG-01` for review. It is not a finalized freeze, not canonical
evidence, not a result population, not a trial-log entry, not candidate
approval, not readiness, and not paper/live/runtime authority.

The drafted JSON artifacts use the schema-required frozen-for-sweep-planning
fields so the hash-pinned candidate chain can validate. Karl approved the
Option A fixed-throttle shape for commit and PR review. Merge remains required
before this surface is repo-canonical.

Follow-up revision: Option A fixes
`entry_logic.entry_controls.min_bars_between_entries = 8` in the Strategy Spec
and does not treat it as a Variant Manifest axis or free parameter.

## Draft Artifact Set

- Strategy Spec: `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- Variant Manifest: `research/variant_manifests/VM-0003.variant_manifest.json`
- Sweep Plan: `research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json`

No commit, PR, canonical sweep, canonical result population, trial, candidate
registry entry, promotion, paper/live/runtime path, OMS/risk/reconciliation
path, broker/exchange path, schema, validator, compiler, runner, `lib/`, `src/`,
data catalog, or data-content change is authorized by this draft.

## Candidate Semantics

`STRAT-SPEC-0003` is a BTCUSDT Binance USDT-M perpetual 15m both-direction
mean-reversion design.

Included:

- A1 z-score entry operand:
  `z_score(close, SMA(center_lookback_bars), STDDEV(vol_lookback_bars))`.
- Long entry when z-score is `< -1.5`.
- Short entry when z-score is `> 1.5`.
- `zero_scale_policy: "null_output"`.
- Shared A2 trend gate through `filters.groups`:
  `close > SMA(trend_lookback_bars)`.
- Shared A3 throttle fixed in the Strategy Spec:
  `entry_logic.entry_controls.min_bars_between_entries = 8`.
- Long exit when `close >= SMA(center_lookback_bars)`.
- Short exit when `close <= SMA(center_lookback_bars)`.
- Dynamic-equity 1x sizing posture for future comparable offline measurement,
  inherited from the RP-7520 realism surface.

Excluded:

- No regime group.
- No `STDDEV(close, vol_lookback_bars) > 1.0`.
- No volatility-expansion substitute.
- No throttle sweep axis.
- No open expression language or free-form formula.
- No runtime, paper/live, OMS, risk, reconciliation, broker, or exchange field.

## Variant Grid

`VM-0003` declares a full Cartesian 8-cell manual grid:

| Axis | Values |
|---|---:|
| `center_lookback_bars` | `50`, `100` |
| `vol_lookback_bars` | `30`, `50` |
| `trend_lookback_bars` | `100`, `200` |

Free-parameter count: `3`.

Committed denominator if finalized unchanged: `8`, plus any retained
non-success rows required by future result-population rules.

Repo-truth follow-up decision for Karl review: current
`entry_logic.entry_controls.min_bars_between_entries` is a Strategy Spec
literal, so Option A keeps it fixed at `8` and removes it from the VM grid. No
implementation, schema, compiler, runner, or materialization change is included
or authorized by this draft.

The manifest contains all 8 variants in deterministic manual-grid order:

| Variant | center | vol | trend |
|---|---:|---:|---:|
| `VAR-000001` | 50 | 30 | 100 |
| `VAR-000002` | 50 | 30 | 200 |
| `VAR-000003` | 50 | 50 | 100 |
| `VAR-000004` | 50 | 50 | 200 |
| `VAR-000005` | 100 | 30 | 100 |
| `VAR-000006` | 100 | 30 | 200 |
| `VAR-000007` | 100 | 50 | 100 |
| `VAR-000008` | 100 | 50 | 200 |

## Sweep Plan

`SWEEP-PLAN-0003` references `VM-0003`, selects all 8 manifest variants, and
records zero executed variants and 8 not-attempted variants. It declares a
future single-slice BTCUSDT 15m D4/D4A OHLCV trial target only.

Future comparable measurement assumptions, if separately authorized:

- `dynamic_equity_target_leverage`
- `target_leverage = 1.0`
- taker-entry / taker-exit fees
- fixed-bps slippage
- funding-notional mode `entry_price`
- zero-equity liquidation mode
- `close` mark source
- `next_open_close_mark` bar-path assumption

This package does not run the trial and does not write a canonical result
population.

## Operational Screen

The future single-slice Phase-B population is GO-to-walk-forward only if every
rule below passes. This is not promotion, readiness, candidate approval, or
paper/live authority.

1. Denominator completeness:
   - `committed_denominator_snapshot.committed_denominator` must equal the
     frozen VM Cartesian denominator plus all retained non-success rows.
   - For the current draft grid, the frozen VM Cartesian denominator is `8`.
   - `result_row_count`, `outcome_counts_sum`, and committed denominator must
     agree.
   - Successful, failed, invalid, excluded, errored, aborted, filtered,
     data-unavailable, and not-attempted rows must remain visible.
   - Winner-only, successful-only, executed-only, or post-hoc-cleaned
     denominator treatment is NO-GO.

2. RP-7520 comparison basis:
   - `trade_count`: min `1212`, median `3506.5`, max `12962`, mean `4850.2`.
   - `return_pct`: min `-0.999998`, median `-0.981508`, max `-0.616501`,
     mean `-0.912189`.
   - `sharpe`: min `-3.169619`, median `-0.922568`, max `-0.174432`,
     mean `-1.198252`.
   - `drawdown`: min `0.726300`, median `0.983166`, max `0.999998`,
     mean `0.935495`.
   - `fees + slippage + funding`: min `7141.387269`, median `8073.023601`,
     max `16751.362811`, mean `9052.834177`.
   - `(fees + slippage + funding) / 10000`: min `0.714139`,
     median `0.807302`, max `1.675136`, mean `0.905283`.

3. Trade-count / churn:
   - Population median `metrics.trade_count` must be `< 1212`.
   - No more than 25% of denominator rows may have
     `metrics.trade_count > 3506.5`.
   - Every core-sanity-pass row must have `metrics.trade_count <= 1212`.

4. Cost burden:
   - `total_cost = metrics.fees + metrics.slippage + metrics.funding`.
   - `cost_to_initial_equity = total_cost / 10000`, unless a future result
     population records a different `initial_equity`, in which case use that
     recorded value.
   - Population median `cost_to_initial_equity` must be `<= 0.50`.
   - Every core-sanity-pass row must have `cost_to_initial_equity <= 0.50`.

5. Net performance:
   - Population median `metrics.return_pct` must be `> -0.25`.
   - At least 25% of the committed denominator, at least 2 of 8 for this
     draft grid before retained non-success rows, must have
     `metrics.return_pct > 0` and `metrics.sharpe > 0`.
   - The best row must have `metrics.return_pct > 0` and
     `metrics.sharpe > 0`, but the best row alone cannot create GO status.

6. Max drawdown:
   - Use artifact field `metrics.drawdown`, where positive fraction means
     drawdown; `0.35` means 35%.
   - Population median `metrics.drawdown` must be `<= 0.50`.
   - No core-sanity-pass row may have `metrics.drawdown > 0.35`.
   - Any row with `metrics.drawdown >= 0.95` is NO-GO unless a future package
     explicitly preserves the row in the denominator and states why it does not
     block the screen.

7. Sensitivity / non-isolated variant:
   - At least 25% of the committed denominator, at least 2 variants for the
     current 8-variant draft grid before retained non-success rows, must pass
     the core sanity screen: `return_pct > 0`, `sharpe > 0`,
     `drawdown <= 0.35`, `cost_to_initial_equity <= 0.50`, and
     `trade_count <= 1212`.
   - Passing rows must span more than one value of at least two of the three
     frozen variant axes. This is a strict but coherent sensitivity screen for
     an 8-variant, three-binary-axis grid. A single isolated cell or
     one-axis-only pocket is NO-GO.

8. C3 / DSR posture:
   - Numeric PSR, DSR, and MinTRL remain withheld unless the future evidence
     artifact exposes required formula inputs.
   - The result-population denominator is the frozen family denominator for
     this single-slice screen.
   - Trial-log DSR posture must use the full valid trial-log row count
     available at future evaluation time.
   - Winner-only or Phase-B-only denominator shrinkage is forbidden.

If any item fails, the single-slice decision is NO-GO for walk-forward. A NO-GO
does not reject the broad economic idea; it rejects this exact frozen v1
population under the declared screen.

## Review Stop

Karl approved the Option A fixed-throttle surface for commit and PR review.
No canonical run, result-population write, candidate promotion, paper/live
readiness, or runtime authority is created by this artifact.
