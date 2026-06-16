# Momentum 4h Probe / Canonical Reconcile

Package label: `WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01`

Status: read-only diagnostic.

## 1. Authority Boundary

This diagnostic has evidence-integrity authority only. It does not mutate
`RP-6236`, does not create replacement evidence, does not change runner,
compiler, schema, validator, Strategy Spec, Variant Manifest, Sweep Plan, data,
candidate, walk-forward, paper/live, runtime, OMS/risk/reconciliation,
broker/exchange, or capital paths.

This diagnostic does not mutate RP-6236. If RP-6236 requires annotation,
correction, replacement, or rerun, that must be a separate explicitly
authorized package. RP-6236 remains an honest committed artifact unless and
until a future append-only diagnostic annotation or replacement result is
authorized.

## 2. Question Being Answered

The question was why the 4h premise probe and canonical `RP-6236` diverged:

| Metric | Prior 4h probe summary | Canonical `RP-6236` |
|---|---:|---:|
| Median trades | 60.5 | 511.0 |
| Median cost/gross | 0.06199 | 1.319 on positive-gross rows |
| Median drawdown | 45.01% | 69.68% |
| Positive rows | probe summary implied positive rows | 0/8 positive returns |

The diagnostic also tested whether the `STRAT-SPEC-0006` trend-confirmation
gate is actually applied in the canonical 4h route.

## 3. Source Artifacts Inspected

- `research/result_populations/RP-6236.result_population.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `research/variant_manifests/VM-0006.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0006.sweep_plan.json`
- `docs/research_pipeline/2026-06-momentum_4h_trial_0006_result.md`
- `docs/research_pipeline/2026-06-momentum_4h_prereg_0006.md`
- `docs/status_entries/WP-MOMENTUM-4H-TRIAL-01.md`
- `docs/status_entries/WP-RUNNER-4H-CAPABILITY-01.md`
- `docs/status_entries/WP-MOMENTUM-4H-PREREG-01.md`
- `tools/research_runner/run_offline_sweep.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_spec_signal_compiler.py`

Search found no committed standalone report/status artifact for
`WP-MOMENTUM-4H-PROBE-01`, `01A`, `01B`, or `01C` beyond the preregistration
document's summary of `WP-MOMENTUM-4H-PROBE-01C`.

## 4. Probe vs Canonical Metric Table

| Dimension | Probe summary / reconstruction | Canonical `RP-6236` | Diagnostic reading |
|---|---:|---:|---|
| Grid basis | 0005 bar-count grid directly on 4h bars | 0006 rescaled 4h grid | different tested population |
| Fast bars | 20, 50 | 2, 3 | materially shorter canonical fast lookbacks |
| Slow bars | 100, 200 | 6, 12 | materially shorter canonical slow lookbacks |
| Trend bars | 300, 400 | 19, 25 | materially shorter canonical trend lookbacks |
| Median trades | 60.5 reported; 60.5 reconstructed | 511.0 | explained by shorter canonical lookbacks |
| Median drawdown | 45.01% reported; about 45.01% reconstructed | 69.68% | explained by different population and churn |
| Median cost/gross | 0.06199 reported; about 0.062 reconstructed | 1.319 positive-gross median | explained by different population and gross PnL |

The scratch reconstruction used direct `compile_signal` plus `run_backtest` over
the exact 4h CSV and the 0005-style bar-count grid. It is diagnostic only; it
does not promote the probe to canonical evidence.

## 5. Canonical `RP-6236` Per-Variant Table

| Variant | fast/slow/trend | Trades | Return | Max DD | Gross PnL | Net PnL | Cost/Gross |
|---|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 2/6/19 | 562 | -3.20% | 50.38% | 4,796.64 | -320.26 | 1.067 |
| VAR-000002 | 2/6/25 | 558 | -67.51% | 73.38% | -3,782.84 | -6,751.03 | N/A |
| VAR-000003 | 2/12/19 | 468 | -67.83% | 81.44% | -4,249.85 | -6,782.81 | N/A |
| VAR-000004 | 2/12/25 | 454 | -73.52% | 85.91% | -4,561.03 | -7,352.30 | N/A |
| VAR-000005 | 3/6/19 | 554 | -46.54% | 57.02% | -619.68 | -4,654.08 | N/A |
| VAR-000006 | 3/6/25 | 556 | -57.44% | 65.99% | -2,191.37 | -5,743.73 | N/A |
| VAR-000007 | 3/12/19 | 448 | -9.84% | 63.50% | 3,085.30 | -984.18 | 1.319 |
| VAR-000008 | 3/12/25 | 432 | -29.99% | 78.63% | 1,680.96 | -2,999.15 | 2.784 |

## 6. Probe Evidence Inventory

Committed probe evidence is summary-only:

- The preregistration document says `WP-MOMENTUM-4H-PROBE-01C` was
  scratch-only and `PREMISE-CONFIRMED`.
- It records 8 successful scratch rows, median trade count `60.5`, max trade
  count `82`, median cost/gross `0.06199`, median drawdown `45.01%`, max
  drawdown `52.95%`, and synthetic zero funding.
- It explicitly says the probe used the 0005 bar-count grid directly on 4h bars.
- It explicitly says the probe confirms the higher-timeframe premise, not the
  exact 0006 rescaled grid.
- It says the route was direct `compile_signal` plus `run_backtest`, not the
  official canonical runner route.

No committed probe output with per-variant trade timestamps was found.

Scratch reconstruction of the documented probe-like grid:

| Variant | probe-like fast/slow/trend | Trades | Return | Max DD | Cost/Gross |
|---|---:|---:|---:|---:|---:|
| VAR-000001 | 20/100/300 | 82 | 687.07% | 35.87% | 0.042 |
| VAR-000002 | 20/100/400 | 79 | 244.46% | 41.15% | 0.060 |
| VAR-000003 | 20/200/300 | 52 | 170.32% | 38.02% | 0.055 |
| VAR-000004 | 20/200/400 | 48 | 22.60% | 51.26% | 0.190 |
| VAR-000005 | 50/100/300 | 69 | 428.92% | 45.86% | 0.064 |
| VAR-000006 | 50/100/400 | 71 | 169.80% | 44.15% | 0.084 |
| VAR-000007 | 50/200/300 | 45 | 130.89% | 52.95% | 0.070 |
| VAR-000008 | 50/200/400 | 40 | 149.01% | 46.32% | 0.055 |

This reconstruction matches the reported probe trade-count range, median trade
count, max trade count, median drawdown, max drawdown, and median cost/gross
closely enough to identify the population mismatch as the dominant cause.

## 7. Execution-Path Comparison

Canonical 4h path:

1. `tools.research_runner.run_offline_sweep` validates the Strategy Spec,
   Variant Manifest, Sweep Plan, and 4h catalog lineage.
2. The `--canonical-4h` route loads the exact 4h CSV, checks catalog SHA,
   validation status, row count, range, spacing, gaps, duplicates, and lineage.
3. Each manifest row is passed to `compile_signal(...)`.
4. `compile_signal(...)` evaluates side-specific entry groups, shared filter
   groups if present, side-specific exits, fixed entry throttle, and ATR-stop.
5. The resulting signal is passed to `run_backtest(...)` with interval `4h`,
   synthetic zero funding, dynamic equity target leverage, taker fees, and
   fixed slippage.
6. Metrics are captured into `RP-6236`.

Probe path per committed summary:

1. Direct `compile_signal(...)` plus `run_backtest(...)`.
2. 4h CSV from local gitignored data.
3. 0005 bar-count grid directly on 4h bars.
4. No canonical runner output or committed result population.

`WP-RUNNER-4H-CAPABILITY-01` already recorded that the exact same-input direct
route matched the official 4h runner route for 0006. This diagnostic reproduced
the same result: direct exact-0006 metrics matched `RP-6236` trade counts and
returns for all eight rows.

## 8. Trend-Confirmation Gate Audit

Classification: `CANONICAL_GATE_APPLIED_AS_INTENDED`.

Evidence:

- `STRAT-SPEC-0006` has two side-specific entry groups. The long group requires
  `fast SMA crosses_above slow SMA` and confirming `close > SMA(trend)`. The
  short group requires `fast SMA crosses_below slow SMA` and confirming
  `close < SMA(trend)`.
- `compile_signal(...)` collects `entry_logic.groups`, splits both-direction
  root entry groups by side, and calls `_entry_allowed(...)` separately for
  long and short groups.
- `_entry_allowed(...)` accepts group roles including `required`,
  `confirming`, and `filter`; `_evaluate_condition(...)` rejects incompatible
  roles and evaluates `gt`, `lt`, and crossover operators.
- In scratch exact-0006 direct checks, canonical direct trade counts and
  returns matched `RP-6236` for all eight variants.
- Removing the confirming trend conditions in memory changed thousands of
  signal bars and changed trade counts for six variants; two variants failed
  closed with `exit_logic.atr_stop ATR is not available at entry signal bar`.

Trend-gate isolation summary:

| Variant | Canonical trades | No-trend result |
|---|---:|---|
| VAR-000001 | 562 | 668 trades, return changed |
| VAR-000002 | 558 | 668 trades, return changed |
| VAR-000003 | 468 | 548 trades, return changed |
| VAR-000004 | 454 | 548 trades, return changed |
| VAR-000005 | 554 | fail-closed before ATR available |
| VAR-000006 | 556 | fail-closed before ATR available |
| VAR-000007 | 448 | 521 trades, return changed |
| VAR-000008 | 432 | 521 trades, return changed |

The trend gate is not inert or bypassed. It is applied and materially affects
signal generation. The divergence is not caused by a missing trend gate.

## 9. Trade Timestamp Comparison

Committed probe trade timestamps are unavailable because the probe artifact was
not committed.

Scratch representative comparison for `VAR-000001`:

| Sequence | Canonical exact-0006 first entries | Probe-like 0005-grid first entries |
|---:|---|---|
| 1 | 2020-01-05 00:00:00+00:00 | 2020-04-15 20:00:00+00:00 |
| 2 | 2020-01-10 16:00:00+00:00 | 2020-04-24 00:00:00+00:00 |
| 3 | 2020-01-14 00:00:00+00:00 | 2020-05-14 08:00:00+00:00 |
| 4 | 2020-01-17 00:00:00+00:00 | 2020-05-30 12:00:00+00:00 |
| 5 | 2020-01-21 12:00:00+00:00 | 2020-06-24 04:00:00+00:00 |
| 6 | 2020-01-25 04:00:00+00:00 | 2020-07-08 16:00:00+00:00 |
| 7 | 2020-01-29 00:00:00+00:00 | 2020-07-16 20:00:00+00:00 |
| 8 | 2020-02-01 04:00:00+00:00 | 2020-07-22 12:00:00+00:00 |
| 9 | 2020-02-08 12:00:00+00:00 | 2020-09-01 20:00:00+00:00 |
| 10 | 2020-02-11 16:00:00+00:00 | 2020-09-24 00:00:00+00:00 |

The divergence starts at entry filtering / signal frequency, not at result
capture. The much shorter canonical 0006 lookbacks create far earlier and far
more frequent crossovers.

## 10. Root Cause

Root cause: the premise probe and canonical `RP-6236` did not test the same
population.

The probe used the 0005 bar-count grid directly on 4h bars:

- fast `[20, 50]`
- slow `[100, 200]`
- trend `[300, 400]`

Canonical `RP-6236` used the frozen 0006 horizon-rescaled 4h grid:

- fast `[2, 3]`
- slow `[6, 12]`
- trend `[19, 25]`

That grid change compresses the effective SMA horizons by about an order of
magnitude, materially increasing crossover frequency and cost exposure. The
canonical route itself is reproducible, and exact same-input direct route
execution matches `RP-6236`.

## 11. Classification

- Canonical runner: `sound for this diagnostic`. The dry-run reproduced
  `RP-6236`, and direct exact-0006 metrics matched the committed result rows.
- Trend gate: `CANONICAL_GATE_APPLIED_AS_INTENDED`.
- Probe methodology: `PROBE_METHODOLOGY_NEEDS_CANONICAL_REGROUNDING`.
- Probe logic classification:
  `PROBE_USED_NONCANONICAL_OR_UNRELIABLE_LOGIC` for use as a premise gate
  against the exact 0006 canonical population.
- `RP-6236` status: interpretable as valid canonical evidence for the exact
  frozen 0006 population. It does not need correction or replacement based on
  this diagnostic.

## 12. Required Follow-Up

Recommended next package: probe-methodology correction / canonical-regrounding
guidance.

Required content for that future package:

- premise probes that are intended to gate a future canonical run must use the
  same Strategy Spec semantics, same exact grid, same canonical runner path when
  available, and same data lineage;
- if a probe intentionally uses a different grid or route, it must be labeled
  as qualitative premise evidence only and must not be compared as if it were
  a forecast of canonical row metrics;
- optional future instrumentation may export trade timestamps for canonical and
  probe runs, but no instrumentation is required to interpret `RP-6236`.

No fix package, `RP-6236` replacement, or fresh 0006 rerun is supported by the
evidence in this diagnostic.

## 13. Forbidden Authority Reminder

This diagnostic creates no signal-definition, policy, promotion, readiness,
paper/live, runtime, capital, OMS/risk/reconciliation, broker/exchange, or
candidate authority. Research/workbench artifacts remain non-executable unless
explicitly promoted through a later approved path.
