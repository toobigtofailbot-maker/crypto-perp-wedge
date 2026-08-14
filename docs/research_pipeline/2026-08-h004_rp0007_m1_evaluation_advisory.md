# H004 / RP-0007 M1 evaluation advisory

Date: 2026-08-14

Package: `WP-CANON-H004-EVALUATION-ADVISORY-01`

Source base: `6994e9000aa6dcf56a7f1a4a08712ba778ea8bbe`

## Decision

The Lane 0 scientific evaluation is complete as advisory work. The scientific
reading is **FAIL / insufficient / withheld as applicable**, and the strategy
does not advance. M1 integration is **not merge-ready** because the required
full-release validation is not green: two current-base tests still assert that
canonical `RP-0007` is absent even though its persistence is merged repo truth.
This package does not widen into those control-plane/persistence tests.

H004 remains the designated engineering dummy: non-winning, non-promotable,
GO-forbidden, and `reject_by_construction`. No favorable aggregate statistic in
this package can override that classification. This report creates no candidate
admission, winner selection, promotion/readiness, paper/live, runtime, OMS,
risk, reconciliation, order, exchange, capital, or autonomous-dispatch
authority.

## Fixed source and denominator

- Canonical source: `research/result_populations/RP-0007.result_population.json`
- Whole-file SHA-256:
  `ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308`
- Scientific Result Population identity:
  `7a0663f899586e036328937de8f17c53281f8de2a2feec4ba00e71b6b6b70a90`
- Committed denominator: 81; result rows: 81; recorded successful runner
  completions: 81. Successful means completed, not profitable.
- All 81 variants were retained in the aggregate robustness inputs and in each
  WFO window. No winner-only, profitable-only, or executed-subset denominator
  was substituted.
- The source Result Population was read only and was not rewritten.

Full-period aggregate results are not a clean success surface. Twenty-seven of
81 rows record `drawdown = 1`, `return_pct = -1`, and `pnl = -10000`: zero-equity
outcomes. Across all 81 rows, Sharpe ranges from -0.590141 to 0.911429, return
from -1.000000 to 8.472414, and drawdown from 0.623339 to 1.000000.

## WFO / OOS advisory

The existing offline runner was reused in dry-run mode with the canonical 1d
input, funding enabled, deterministic seed 7, fixed-order-size semantics, and
1x target leverage. The protocol carries all 81 variants into two disjoint,
non-overlapping windows, each with 730 IS bars followed by 365 OOS bars and a
1,095-bar step. Boundaries are start-inclusive/end-exclusive. There is no
selection or ranking step: every included variant is reported.

The reused tool describes this as a build-test protocol and does not implement
purge or embargo. These results are therefore descriptive advisory evidence,
not a rigorous promotion gate. The replay produced an ephemeral dry-run ID
`RP-5942`, wrote no Result Population, and must not be confused with canonical
`RP-0007`.

| Window | IS interval (UTC, end exclusive) | OOS interval (UTC, end exclusive) | Mean IS Sharpe | Mean OOS Sharpe | Positive OOS Sharpe / return | Mean OOS return | Mean / max OOS drawdown | OOS/IS efficiency |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| WF-0001 | 2020-01-01 to 2021-12-31 | 2021-12-31 to 2022-12-31 | 0.4739 | -0.1835 | 54 / 81 | -0.3814% | 5.9919% / 6.7515% | 54 available; mean -0.4013 |
| WF-0002 | 2022-12-31 to 2024-12-30 | 2024-12-30 to 2025-12-30 | 1.2319 | -0.5863 | 0 / 81 | -9.5915% | 17.0754% / 17.2864% | 81 available; mean -0.5612 |

Across 162 window rows, 54 have positive OOS Sharpe and return. OOS/IS Sharpe
efficiency is computable for 135 rows and absent for 27 rows with a non-positive
IS Sharpe denominator. Its mean is -0.4972, its range is -1.3435 to 0.3439, and
no row exceeds 0.5. Both folds have negative mean OOS Sharpe; the later fold is
negative for all 81 variants. The WFO/OOS advisory therefore fails.

A preliminary replay used dynamic-equity sizing before the current canonical
execution context was reconciled. It was rejected, overwritten, and is not used
as evidence. The accepted artifact is the fixed-order-size, seed-7 replay
described above.

## Anti-overfit metrics and withholding

The existing item-6 robustness report preserves all 81 rows and reports no
numeric PSR, DSR, or MinTRL:

- PSR: `withheld_missing_inputs`
- DSR: `withheld_missing_inputs`
- MinTRL: `withheld_missing_inputs`

RP-0007 does not contain the per-period return series, effective observation
count, skew, kurtosis, explicit benchmark Sharpe, annualization assumptions,
declared selection rule, or effective independent-trial count required for
rigorous values. The current valid trial-log denominator of 32 is accounting
context only and is not a defensible independent-trial count. No statistic was
invented from the 81 aggregate rows.

The item-6 CLI artifact itself records OOS/IS efficiency as withheld because it
does not bind the separate WFO replay rows. The actual WFO efficiency readings
are reported in the preceding section without altering that artifact.

## Seeded aggregate-row Monte Carlo advisory

The existing seeded advisory tool bootstrapped the 81 aggregate variant rows
for 1,000 samples at seed 20260619 and 95% confidence. The output checksum is
`e9d9547235a1a901b501df441b10a408ec4ce05c2c7189065b0015a21da92341`.

Selected observed means and bootstrap intervals are:

| Metric | Observed mean | 95% aggregate-row bootstrap interval |
| --- | ---: | ---: |
| Sharpe | 0.3715 | [0.2316, 0.5120] |
| Return | 4.3037 | [3.4788, 5.1254] |
| Drawdown | 0.7879 | [0.7558, 0.8209] |
| Trade count | 60.3333 | [51.6901, 68.2364] |

This is a bootstrap across correlated aggregate parameter variants. It is not a
chronological return-path confidence interval and not per-trade Monte Carlo.
Per-trade resampling is `QUEUE_PER_TRADE_INSTRUMENTATION` because RP-0007 has no
per-trade rows; fabricated per-trade data is false.

Parameter sensitivity preserves all three values of four registered dimensions.
The strongest instability is the pullback-EMA dimension: the 10 / 20 / 30 groups
have mean Sharpe 0.812 / 0.888 / -0.590 and mean return 6.277 / 7.634 / -1.000,
with the 30 group containing the 27 zero-equity outcomes. The ATR-multiplier
groups have identical aggregate means, making that axis non-discriminating in
this population. These are descriptive findings, not a ranking or a winner.

## Robustness depth advisory

The existing robustness-depth tool ran at seed 1729 and produced checksum
`64db0c29a5feca94163ba685dbeb28e2b3ae79f3d691a6f649c66d5cf291a4ea`.
At separate 2x aggregate cost stresses, mean stressed return is 3.9527 for fees,
3.0077 for funding, and 4.2159 for slippage.

The method subtracts one additional observed absolute aggregate cost from each
row's aggregate PnL; it is not a chronological backtest rerun. Regime robustness
is blocked because no real regime labels exist, and per-trade robustness is
`unavailable_missing_per_trade_rows`. The favorable aggregate full-period mean
does not override the zero-equity rows, failed WFO/OOS reading, missing
scientific inputs, or H004's construction-level rejection.

## Validation, integrity, and M1 conclusion

- RP-0007 remains 81 / 81 rows at its fixed whole-file hash.
- WFO preserves 81 variants in each of two windows; the aggregate-row bootstrap
  and each stress dimension preserve 81 rows.
- No Strategy Spec, Variant Manifest, Sweep Plan, trial log, schema, validator,
  query layer, runner/backtester code, data artifact, canonical evidence,
  candidate lifecycle, runtime, paper/live, OMS/risk, reconciliation, broker,
  exchange, config, dependency, or protected writer is changed.
- The required local canonical data inputs were hydrated as exact ignored
  worktree prerequisites and remain untracked and unstaged.

Focused validation is green: 72 tests passed and one environment-dependent test
was skipped across the item-6, aggregate Monte Carlo, robustness-depth,
canonical-1d, and funding-input surfaces; all five walk-forward-selected runner
tests passed. The accepted 162-row WFO payload reproduced exactly. The item-6
and seeded-MC files reproduced at exact SHA-256, robustness-depth reproduced its
declared checksum, every package JSON file parsed, the result-population corpus
validated, the forbidden-path check found no match, and RP-0007 retained its
fixed hash and 81 rows.

The required `full-release-balanced-v1` run assigned all 162 tracked test files
uniquely across 48 shards with no timeout. Forty-six shards passed. Shard 30 and
shard 34 failed, and both failures reproduce serially:

- `tests/test_dispatch_authorization.py` expects no `RP-0007*` file after the
  KDAUTH boundary.
- `tests/test_scratch_persistence.py` applies the same obsolete absence guard
  to its session and therefore errors when the merged canonical file exists.

Those assertions contradict this branch's exact base, where
`WP-CANON-H004-RP0007-PERSIST-01` is already merged. They are outside this
evaluation/advisory package and are not altered here. This is an open validation
escalation, not a green full-suite result.

All 62 discovered integrity views ran: 60 are clean and the two non-clean views
each return one already-known runbook disclosure:

- `v_integrity_execution_streams`: `execution_stream_missing` for
  `RUN-20260804-H004R2A1`, non-authoritative and operator-inspection-required.
- `v_integrity_strategy_spec_legacy_hash_scope_reproducibility`: the known
  unresolved historical hash-scope row for `STRAT-SPEC-0007`.

No additional integrity finding exists, and neither known finding is
reclassified as corruption by this package.

The advisory evidence proves that the existing evaluation machinery can
exercise canonical RP-0007 inputs end to end while withholding unsupported
claims. It does not prove strategy readiness. H004 remains
`reject_by_construction`, no downstream work is authorized by this report, and
M1 closure must wait for a separately scoped reconciliation of the stale
RP-0007-absence tests followed by green full-release evidence.

Detailed machine-readable evidence is under
`scratch/WP-CANON-H004-EVALUATION-ADVISORY-01/`.
