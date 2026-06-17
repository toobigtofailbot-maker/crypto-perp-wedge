# WP-ONLINE-ORB-15M-PREREG-01

## Package Class

Strategy preregistration draft / freeze surface / scratch integration reconfirmation.

## Branch / Worktree / Base

- Branch: `prereg/online-orb-15m-prereg-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-ORB-15M-PREREG-01`
- Base: refreshed `main` at `8f3f9fd` (`Merge pull request #506 from toobigtofailbot-maker/perf/online-ohlcv-runner-perf-01`)

## Changed Files

- `docs/research_pipeline/2026-06-online_orb_15m_prereg_01.md`
- `docs/status_entries/WP-ONLINE-ORB-15M-PREREG-01.md`

Scratch artifacts under `scratch/WP-ONLINE-ORB-15M-PREREG-01/` were generated for validation and dry-run extraction only and are not committed.

## Surface

- Strategy label: `ONLINE-ORB-15M-UTC00-BREAK-RETEST`
- Symbol/timeframe: BTCUSDT 15m.
- Session/opening range: UTC 00:00 daily session, first 2 x 15m bars.
- Entry: both-direction close-confirmed opening-range breakout plus bounded close-confirmed retest.
- Exits: `time_exit.session_end`, `opening_range_opposite_side`, `fixed_R_target`.
- Axes: `retest_window_bars {2,4}` x `breakout_tolerance_atr {0.0,0.1}` x `fixed_R_target {1.0,2.0}`.
- Denominator: 8.

## Scratch Integration

PASS for mechanical integration.

- Scratch Strategy Spec validation: PASS.
- Scratch VM/Sweep validation: PASS.
- Full-slice runner dry-run completed: YES.
- Wall-clock: 173.7 seconds for CLI summary; 172.157 seconds for row-extraction API run.
- Dry run: `true`.
- Result Population write: NO (`wrote=false`, `output_path=null`).
- In-memory result population ID: `RP-1482`.
- Denominator: 8.
- Outcome counts: 8 successful, 0 failed/errored/invalid/excluded/aborted/filtered/data-unavailable/not-attempted.
- Trade counts: `[999, 999, 1056, 1056, 1298, 1298, 1344, 1344]`.
- Median return: `-0.915408`.
- Median Sharpe: `-2.521969`.
- Median drawdown: `0.926739`.
- Cost/gross availability: unavailable from current Result Population row fields; gross PnL is not exposed.

## Frozen Screen Draft

Drafted only, not applied as canonical evidence.

- Denominator completeness: require 8/8 accounting with retained non-success rows.
- Net performance: median net return > 0 and at least 5/8 positive net-return variants.
- Drawdown: median drawdown <= 0.45, max drawdown < 0.60, automatic NO-GO if any row drawdown >= 0.75.
- Cost/churn: record trade counts, average trades/year, fees, slippage, funding, total cost, and cost/gross availability; require follow-up instrumentation if cost/gross remains unavailable.
- Sensitivity: positive rows must span more than one bucket on at least two independent axes.
- DSR/PSR/MinTRL: compute only if required inputs exist; otherwise mark unavailable without fabrication.
- Verdict framing: `GO`, `NO-GO`, or `INCONCLUSIVE / instrumentation-required`.

## Freeze Status

Main/Karl-gated and not finalized. This package surfaces the review package only.

## Boundary Summary

- Committed Strategy Spec / VM / Sweep: NO.
- Canonical Result Population: NO.
- Canonical trial: NO.
- Candidate / walk-forward / paper / live / runtime / capital: NO.
- Protected runtime, OMS, risk, reconciliation, broker, exchange, credentials, or capital path touched: NO.
- Schema/compiler/runner/query/data behavior changed: NO.

## Exact Next Item

Main/Karl review of the ORB 15m preregistration surface and frozen screen. If finalization is approved, decide in the next package whether to add cost/gross instrumentation before any canonical trial or explicitly preserve cost/gross as instrumentation-required.
