# Momentum 4h Preregistration 0006

Status: draft-and-surface preregistration package for
`WP-MOMENTUM-4H-PREREG-01`.

This document surfaces `STRAT-SPEC-0006`, `VM-0006`, and
`SWEEP-PLAN-0006` plus a proposed 4h single-slice screen. It is not canonical
evidence, not a canonical trial, not a result population, not candidate or
walk-forward authority, and not paper/live/runtime/capital authority.
Freeze/finalization remains subject to explicit you/Main gate review.

## Purpose

The 4h momentum preregistration draft follows three current repo facts:

- `RP-3731` is canonical 15m evidence for `STRAT-SPEC-0005` /
  `VM-0005` / `SWEEP-PLAN-0005` and has a diagnostic `NO-GO` verdict driven by
  drawdown and cost.
- PR #489 / `WP-DATA-RESAMPLE-4H-01` landed the derived BTCUSDT 4h data
  lineage.
- `WP-MOMENTUM-4H-PROBE-01C` is scratch-only diagnostic evidence classified as
  `PREMISE-CONFIRMED`, showing materially lower trade count and cost/gross on
  the higher-timeframe premise versus `RP-3731`.

## Evidence Status

Canonical evidence:

- `research/result_populations/RP-3731.result_population.json` records the
  exact 0005 15m canonical result population and its complete eight-row
  denominator.
- `docs/research_pipeline/2026-06-momentum_v2_trial_0005_result.md` records
  the separate frozen-screen diagnostic verdict over `RP-3731`: `NO-GO`.
- PR #489 / `WP-DATA-RESAMPLE-4H-01` and the 4h catalog metadata record the
  derived 4h OHLCV slice identity and validation status.

Scratch diagnostic basis:

- `WP-MOMENTUM-4H-PROBE-01C` is scratch-only.
- It is not canonical evidence.
- It is not preregistration authority.
- It is not profitability proof.
- It is not candidate authority.

## 4h Probe Facts

`WP-MOMENTUM-4H-PROBE-01C` reported:

- classification: `PREMISE-CONFIRMED`;
- all 8 scratch rows successful;
- 4h median trade_count `60.5` versus `RP-3731` 15m median trade_count
  `1123.5`;
- 4h max trade_count `82` versus `RP-3731` 15m max trade_count `1443`;
- 4h median cost/gross `0.06199` versus `RP-3731` 15m median cost/gross
  `0.853`;
- 4h median drawdown `45.01%` versus `RP-3731` 15m median drawdown `59.70%`;
- 4h max drawdown `52.95%` versus `RP-3731` 15m max drawdown `72.21%`;
- funding modeled as synthetic zero funding.

These are scratch diagnostic facts only. They do not become canonical results
and they do not prove the exact 0006 grid.

## Frozen Draft Design

Structure:

- both-direction BTCUSDT SMA crossover trend-continuation;
- side-specific long and short entry groups;
- side-specific trend confirmation inside entry groups;
- opposite-crossover exits retained;
- fixed A6 `exit_logic.atr_stop` retained;
- fixed entry throttle retained;
- no compiler mirroring;
- no shared filter-group migration;
- no winner-only or post-hoc variant narrowing.

Grid:

- `fast_lookback_bars`: `[2, 3]`
- `slow_lookback_bars`: `[6, 12]`
- `trend_lookback_bars`: `[19, 25]`
- denominator: `8`
- every row satisfies `fast < slow < trend`

Grid rationale:

- 0005 15m fast `[20, 50]` is about `[5h, 12.5h]`, rescaled to 4h bars as
  approximately `[2, 3]`.
- 0005 15m slow `[100, 200]` is about `[25h, 50h]`, rescaled to 4h bars as
  approximately `[6, 12]`.
- 0005 15m trend `[300, 400]` is about `[75h, 100h]`, rescaled to 4h bars as
  approximately `[19, 25]`.
- No row is selected or removed using 4h probe performance.

Important caveat:

- The 4h scratch probe used the 0005 bar-count grid directly on 4h bars.
- This preregistration uses time-horizon-rescaled lookbacks.
- Therefore the scratch probe confirms the higher-timeframe cost/trade-count
  premise, but it is not canonical evidence for the exact 0006 grid.
- This is acceptable for draft-and-surface only. If later authorized, the
  eventual 0006 trial must be committed regardless of outcome.

Fixed ATR stop:

- `atr_lookback = 14`
- `atr_multiplier = 3.0`
- `entry_reference_price = next_bar_open_pre_fee_slippage`
- `evaluation_price = close`
- `evaluation_timing = bar_close`

Fixed throttle:

- `entry_logic.entry_controls.min_bars_between_entries = 16`
- On 4h bars this is a 64h bar-count throttle, not the 15m equivalent of 4h.
- This is intentional for this draft surface because the scratch premise probe
  used the same fixed throttle.

Data refs:

- primary timeframe: `4h`
- 4h catalog identity:
  `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`
- parent 15m identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- 4h CSV SHA:
  `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1`
- 4h validation status: `PASS`

Funding limitation:

- The current 4h probe and current 15m result-population path model funding as
  `0.0` / synthetic zero funding.
- This is not blocking research preregistration.
- Funding must be modeled before any momentum strategy is judged live-viable.
- No paper/live/runtime viability is claimed.

## Frozen Screen Proposal

These are draft surface criteria for a future authorized 0006 canonical
single-slice trial. They are not final freeze criteria unless this PR is
accepted/merged under explicit you/Main gate review.

1. Denominator completeness: all 8 variants accounted for, every non-success
   retained and classified, and no winner-only retention.
2. Nondegenerate: at least 2 variants with nonzero gross PnL and nonzero
   trades. Stop if the denominator cannot be assembled.
3. Net performance: median `return_pct > 0`, at least `5/8` rows with
   `return_pct > 0`, and at least `5/8` rows with `sharpe > 0`.
4. Drawdown: median drawdown `<= 0.45`, max drawdown `< 0.60`, and automatic
   `NO-GO` if any row drawdown `>= 0.75`.
5. Cost: `cost_to_gross_pnl` must be computable. Median
   `cost_to_gross_pnl` over positive-gross-PnL rows must be `<= 0.20`, and
   every otherwise core-sanity positive-gross-PnL row must be `<= 0.35`. Stop
   if the cost metric is uncomputable.
6. Churn: median `trade_count <= 250`, max `trade_count <= 500`, and any
   minimum trade-count floor is used only for nondegeneracy, not optimization.
7. Sensitivity: positive-return rows must span more than one bucket on at least
   two of the fast, slow, and trend axes. Single-row or best-row-only success
   is forbidden.
8. DSR / PSR / MinTRL: compute only if inputs exist; otherwise mark
   not-evaluable without fabrication.
9. Funding: record the current funding-zero limitation and make no live
   viability claim.

## Known Implementation Dependency

The current official offline runner is 15m/canonical-D4A-specific and cannot
consume 4h through the canonical path. The scratch probe used direct
`compile_signal` plus `run_backtest` only.

Before any canonical 4h trial, a separate narrow runner/data-path capability
package or approved execution route is required. This preregistration package
does not implement that runner capability.

## Local Sanity Probe

A scratch-only local sanity probe was run before report-back using the
gitignored 4h CSV available in the original repo worktree and direct
`compile_signal` plus `run_backtest`.

Result:

- all 8 proposed `VM-0006` variants compiled;
- all 8 rows produced nonzero trades;
- no output artifact was committed;
- no threshold, grid value, screen criterion, or variant selection was changed
  because of this probe.

Limitations:

- synthetic zero funding was used;
- the direct route is not the official canonical runner path;
- this is compile/nondegeneracy sanity only, not canonical evidence and not a
  result-population substitute.

## Boundary

No Result Population is written. No canonical trial is run. No
`STRAT-SPEC-0004`, `VM-0004`, `SWEEP-PLAN-0004`, `STRAT-SPEC-0005`,
`VM-0005`, `SWEEP-PLAN-0005`, `RP-3731`, 4h data catalog/validation/
derivation artifact, compiler, schema, validator, runner, query-layer logic,
`lib/`, data content, candidate registry, walk-forward path, paper/live/
runtime path, OMS/risk/reconciliation path, broker/exchange path, or capital
authority is changed or authorized by this artifact.
