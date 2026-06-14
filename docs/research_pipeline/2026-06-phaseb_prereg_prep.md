# Phase-B Pre-Registration Prep

## Status / Authority Boundary

Status: `pre-freeze prep`.

This note is not a freeze, not a Strategy Spec, not a Variant Manifest, not a
Sweep Plan, not a canonical result population, not a trial-log entry, not
canonical evidence, and not candidate authority.

It authorizes no compiler, schema, validator, catalog, runner, backtester,
library, result-population, data-acquisition, candidate lifecycle, ranking,
readiness, promotion, paper/live/runtime, OMS/risk/reconciliation,
broker/exchange, collateral, dependency, CI, or autonomous behavior change.

The real-data probe below was read-only and in-memory. It used a locally
available D4 normalized CSV whose byte hash matched the committed D4 catalog
`normalized.sha256`. It wrote no scratch artifact and did not copy data into
this package worktree.

## Repo-Truth Basis

Fact: `docs/research_pipeline/2026-06-phaseb_hypothesis_reconciliation.md`
defines the non-frozen Phase-B probe shape as both-direction BTCUSDT 15m
z-score mean reversion with A1 z-score entries, shared A2 `trend` and `regime`
gates through `filters.groups`, A3 `min_bars_between_entries`, and centerline
exits.

Fact: the fixed regime candidate in that reconciliation is:

```text
STDDEV(close, vol_lookback_bars) > 1.0
```

Fact: current closed compiler grammar supports OHLCV data refs, `sma`, `ema`,
`atr`, `stddev`, constants, parameter refs, A1 `z_score`, closed comparison
operators, side-labeled both-direction entries/exits, and
`min_bars_between_entries`.

Fact: current closed compiler grammar does not expose a division/ratio
operator, percentile/rank operator, arbitrary expression language, normalized
volatility primitive, or cross-stream regime primitive.

Fact: `RP-7520` is the current comparable dynamic-equity 1x evidence family for
`STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` over the same BTCUSDT 15m D4
slice.

## Blocker A: Real-Data Gate Behavior

### Probe Method

The probe loaded the committed D4 catalog slice:

- catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- catalog normalized path:
  `data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- expected normalized SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

The package worktree did not contain the gitignored normalized CSV. The probe
used the read-only local file at:

```text
C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv
```

The file hash matched the committed catalog normalized SHA256 exactly.

Data shape:

- row count: `220128`
- start: `2020-01-01T00:00:00+00:00`
- end: `2026-04-11T23:45:00+00:00`

Parameter values checked:

- `center_lookback_bars`: `50`, `100`
- `vol_lookback_bars`: `30`, `50`
- `trend_lookback_bars`: `100`, `200`
- z-score thresholds: long `< -1.5`, short `> 1.5`
- current regime candidate: `STDDEV(close, vol_lookback_bars) > 1.0`

Degeneracy threshold used: true-rate `<= 1%` or `>= 99%` after warmup. This is
a design judgment for pre-freeze review, not a repo-wide validator rule.

### Gate True-Rates

| Gate | Parameters | True rate | True / valid | Degenerate? |
|---|---:|---:|---:|---|
| Current regime: `STDDEV(close, 30) > 1.0` | `vol=30` | `100.000000%` | `220099 / 220099` | YES |
| Current regime: `STDDEV(close, 50) > 1.0` | `vol=50` | `100.000000%` | `220079 / 220079` | YES |
| Trend: `close > SMA(close, 100)` | `trend=100` | `52.270383%` | `115010 / 220029` | NO |
| Trend: `close > SMA(close, 200)` | `trend=200` | `52.664269%` | `115824 / 219929` | NO |

Because the current regime gate is always true after warmup for both proposed
volatility lookbacks, the combined `trend AND current_regime` rate equals the
trend-gate rate exactly. The current fixed-minimum regime gate is inert on the
real BTCUSDT 15m D4 close-price series.

### Entry Opportunity Counts

These are possible bar-level entry-condition counts before applying
`min_bars_between_entries` state. They are not backtest trades and are not
evidence of profitability.

| center | vol | trend | valid rows | raw long | raw short | gated long | gated short | gated either |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 30 | 100 | 220029 | 45313 | 51534 | 2495 | 49280 | 51775 |
| 50 | 30 | 200 | 219929 | 45253 | 51534 | 7946 | 43676 | 51622 |
| 50 | 50 | 100 | 220029 | 30034 | 32083 | 1229 | 31139 | 32368 |
| 50 | 50 | 200 | 219929 | 29988 | 32083 | 5157 | 27551 | 32708 |
| 100 | 30 | 100 | 220029 | 64515 | 74214 | 0 | 74214 | 74214 |
| 100 | 30 | 200 | 219929 | 64420 | 74214 | 4703 | 68943 | 73646 |
| 100 | 50 | 100 | 220029 | 52656 | 61350 | 0 | 61350 | 61350 |
| 100 | 50 | 200 | 219929 | 52573 | 61350 | 2876 | 58014 | 60890 |

Inference: the shared one-sided trend gate `close > SMA(trend)` is not globally
degenerate, but it is strongly directional for a mean-reversion shape. When
`center_lookback_bars` and `trend_lookback_bars` are both `100`, long entries
are impossible because long dislocation requires close below the same SMA that
the trend gate requires close above. This is a pre-freeze review issue, not a
compiler or schema issue.

### Closed Regime Alternatives Checked

The current grammar cannot express price-normalized volatility directly.
However, it can express same-unit volatility expansion comparisons with no
schema/compiler/catalog change:

```text
STDDEV(close, vol_lookback_bars) > STDDEV(close, trend_lookback_bars)
```

This is scale-meaningful because both operands are price-unit rolling
volatility over the same close series. It is equivalent to asking whether
shorter-window volatility exceeds longer-window volatility, without needing a
division operator. It uses the existing `vol_lookback_bars` and
`trend_lookback_bars` axes and adds no free parameter.

Observed true-rates:

| Alternative regime form | True rate | True / valid | Degenerate? |
|---|---:|---:|---|
| `STDDEV(close, 30) > STDDEV(close, 100)` | `13.241436%` | `29135 / 220029` | NO |
| `STDDEV(close, 30) > STDDEV(close, 200)` | `6.827658%` | `15016 / 219929` | NO |
| `STDDEV(close, 50) > STDDEV(close, 100)` | `22.227979%` | `48908 / 220029` | NO |
| `STDDEV(close, 50) > STDDEV(close, 200)` | `11.535541%` | `25370 / 219929` | NO |

The probe also checked same-lookback `STDDEV > ATR` as a closed same-unit form:

| Alternative regime form | True rate | True / valid | Degenerate? |
|---|---:|---:|---|
| `STDDEV(close, 30) > ATR(30)` | `52.186970%` | `114863 / 220099` | NO |
| `STDDEV(close, 50) > ATR(50)` | `73.878471%` | `162591 / 220079` | NO |

Decision surface: the fixed `STDDEV(close, vol_lookback_bars) > 1.0` gate
should not be frozen. A closed scale-meaningful replacement exists:
`STDDEV(close, vol_lookback_bars) > STDDEV(close, trend_lookback_bars)`.
If Main does not want that coupled volatility-expansion interpretation in v1,
the fallback is to drop the regime gate and keep z-score entries, trend gate,
and throttle. Adding normalized volatility, percentile/rank, or richer regime
primitives routes back to a future compiler/schema track.

## Blocker B: Operational Success Criteria

### RP-7520 Comparison Basis

RP-7520 fields used for the comparison are result-population row metrics under
`variant_result_rows[].metrics`.

RP-7520 complete-population summary:

| Metric | Min | Median | Max | Mean |
|---|---:|---:|---:|---:|
| `trade_count` | `1212` | `3506.5` | `12962` | `4850.2` |
| `return_pct` | `-0.999998` | `-0.981508` | `-0.616501` | `-0.912189` |
| `sharpe` | `-3.169619` | `-0.922568` | `-0.174432` | `-1.198252` |
| `drawdown` | `0.726300` | `0.983166` | `0.999998` | `0.935495` |
| `fees + slippage + funding` | `7141.387269` | `8073.023601` | `16751.362811` | `9052.834177` |
| `(fees + slippage + funding) / 10000` | `0.714139` | `0.807302` | `1.675136` | `0.905283` |

RP-7520 funding is `0.0` for every row because the canonical 15m runner used
zero funding for this OHLCV-only input. Future comparison should still use the
same explicit total-cost formula:

```text
total_cost = metrics.fees + metrics.slippage + metrics.funding
cost_to_initial_equity = total_cost / 10000
```

If a future result-population artifact records `initial_equity` explicitly in
a different location, that recorded value should replace the hard-coded
`10000` denominator for this derived comparison.

### Proposed Primary Screen

This is a proposed operational threshold set for Main review. It is a
GO-to-walk-forward versus NO-GO single-slice screen only. It is not promotion,
readiness, ranking, paper/live authority, or D2-006 gate satisfaction.

The future single-slice Phase-B population should be marked GO-to-walk-forward
only if all of the following are true:

1. Population completeness:
   - `committed_denominator_snapshot.committed_denominator` equals the frozen
     Cartesian denominator plus all retained non-success rows.
   - `result_row_count`, `outcome_counts_sum`, and committed denominator agree.
   - Failed, invalid, excluded, errored, aborted, filtered,
     data-unavailable, and not-attempted rows remain visible.
   - No winner-only, successful-only, executed-only, or post-hoc-cleaned
     denominator is used.

2. Cost-drag and turnover:
   - median `trade_count` is below RP-7520's minimum `trade_count` of `1212`.
   - no more than 25% of rows exceed RP-7520's median `trade_count` of
     `3506.5`.
   - median `cost_to_initial_equity` is `<= 0.50`, materially below RP-7520's
     median `0.807302`.
   - every variant counted as a core sanity pass has
     `cost_to_initial_equity <= 0.50` and `trade_count <= 1212`.

3. Net performance:
   - median `return_pct` is greater than `-0.25`, materially above RP-7520's
     best row at `-0.616501`.
   - at least 25% of the committed denominator has `return_pct > 0` and
     `sharpe > 0`.
   - the best row must have `return_pct > 0` and `sharpe > 0`, but a best row
     alone cannot create GO status.

4. Max drawdown floor:
   - median `drawdown` is `<= 0.50`, materially below RP-7520's median
     `0.983166`.
   - no core-sanity-pass row may have `drawdown > 0.35`.
   - no row may hit terminal-like drawdown `>= 0.95`; if a future package wants
     to tolerate failed variants, it must preserve them in the denominator and
     state why they do not block the screen.

5. Sensitivity / robustness:
   - at least 25% of the committed denominator, and at least four variants if
     the denominator is `16`, must pass the core sanity screen:
     `return_pct > 0`, `sharpe > 0`, `drawdown <= 0.35`,
     `cost_to_initial_equity <= 0.50`, and `trade_count <= 1212`.
   - the passing rows must span more than one value of at least two frozen
     variant axes. A single isolated cell or one-axis-only pocket is NO-GO for
     walk-forward.

6. DSR / C3 posture:
   - numeric PSR, DSR, and MinTRL remain withheld unless the future evidence
     artifact exposes the required formula inputs.
   - the result-population denominator is the frozen family denominator for
     this single-slice screen.
   - trial-log DSR posture must use the full valid trial-log row count
     available at the later evaluation time; do not fabricate a smaller
     winner-only or Phase-B-only denominator.

If any item fails, the single-slice decision is NO-GO for walk-forward. A
NO-GO result does not prove the broad economic idea impossible; it means the
pre-registered v1 population did not meet the declared single-slice screen.

## Final Pre-Freeze Surface

Recommended v1 design shape after this gate check:

- primary timeframe: BTCUSDT 15m D4 OHLCV;
- direction: both;
- entry: A1 z-score long below `-1.5`, short above `1.5`;
- exits: side-specific centerline exits;
- trend gate: keep under Main review, with the observed directional-bias note
  above;
- regime gate: do not freeze `STDDEV(close, vol_lookback_bars) > 1.0`;
- replacement regime candidate: freeze-consider
  `STDDEV(close, vol_lookback_bars) > STDDEV(close, trend_lookback_bars)`;
- trade-frequency control: keep A3 `min_bars_between_entries`;
- free parameter count: `4`;
- draft grid: `center_lookback_bars in {50, 100}`,
  `vol_lookback_bars in {30, 50}`,
  `trend_lookback_bars in {100, 200}`,
  `min_bars_between_entries in {8, 24}`;
- denominator implication if frozen unchanged: `16` declared variants, plus
  retained non-success rows if any.

If Main drops the regime gate instead of accepting the replacement, the free
parameter count remains `4` because the prior regime minimum was fixed and not
swept. The denominator remains `16` if the four-axis grid is otherwise
unchanged.

## Stop / Follow-Up Surface

Open pre-freeze decisions:

- Decide whether to replace the inert fixed-minimum regime gate with the closed
  volatility-expansion form, or drop regime from v1.
- Review whether the shared one-sided trend gate is intended despite the
  observed long-entry suppression for `center=100, trend=100`.
- If Main wants normalized volatility, percentile/rank regime, volatility
  ratios as first-class operators, or side-specific trend polarity, route that
  through a future compiler/schema design or implementation package.

This note does not draft the freeze package and does not authorize the trial.
