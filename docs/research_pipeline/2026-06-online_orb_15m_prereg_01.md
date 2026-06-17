# Online ORB 15m Preregistration 01

Package: `WP-ONLINE-ORB-15M-PREREG-01`

## 1. Authority Boundary

This package drafts and surfaces a freeze-ready ORB 15m preregistration surface for Main/Karl review. It is not a finalized freeze, not canonical evidence, not a canonical trial, not a Result Population, not a candidate lifecycle decision, not walk-forward/OOS authority, and not paper/live/runtime/capital authority.

No Strategy Spec, Variant Manifest, Sweep Plan, or Result Population artifact is committed by this package. Scratch artifacts were generated under `scratch/WP-ONLINE-ORB-15M-PREREG-01/` only to validate and run the exact proposed surface through the existing offline runner. Those scratch artifacts are intentionally uncommitted and have no execution authority.

## 2. Repo-Truth Discovery

Fact:

- Required online OHLCV primitive packages are merged on refreshed `main` at `8f3f9fd`.
- `WP-ONLINE-OHLCV-PRIMITIVE-IMPL-01` added session, opening-range, breakout, retest, and session trade-cap primitives.
- `WP-ONLINE-OHLCV-EXIT-PRIMITIVE-IMPL-01` added `time_exit.session_end`, `opening_range_opposite_side`, and `fixed_R_target`.
- `WP-ONLINE-OHLCV-VARIANT-BINDING-01` added closed `{"parameter_ref": "..."}` binding for the needed primitive thresholds and `fixed_R_target.r_multiple`.
- `WP-ONLINE-OHLCV-BUNDLED-SURFACE-INTEGRATION-01` drafted the ORB 15m surface but was blocked by full-slice runtime.
- `WP-ONLINE-OHLCV-RUNNER-PERF-01` removed that runtime blocker and completed a full-slice ORB dry-run with no Result Population write.
- GitHub open PR check returned no open PRs in `toobigtofailbot-maker/crypto-perp-wedge` during this package.

Current 15m data identity:

- Catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Local path used: `C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`

Decision:

- Keep draft JSON artifacts scratch-only for this package because the package is Main/Karl-gated and explicitly forbids canonical write posture.
- Commit only this preregistration surface and the package status entry.

## 3. Draft Surface

Strategy label: `ONLINE-ORB-15M-UTC00-BREAK-RETEST`

Fixed semantics:

- Symbol: BTCUSDT.
- Timeframe: 15m.
- Session: UTC daily session anchored at `00:00`.
- Opening range: first 2 x 15m bars, 30 minutes.
- Direction: both long and short.
- Entry: close-confirmed opening-range breakout plus close-confirmed bounded retest.
- Session trade cap: one trade per session.
- Exit set: `time_exit.session_end`, `opening_range_opposite_side`, and `fixed_R_target`.

Entry primitive shape:

- `session_window`: `UTC_DAILY_0000`.
- `opening_range`: `OR-UTC00-30M`, start offset 0 bars, length 2 bars.
- `opening_range_breakout`: close/bar-close confirmation, next-bar-open entry timing, ATR-multiple tolerance.
- `opening_range_retest`: min 1 bar after breakout, max bound from `retest_window_bars`, close-only retest, next-open-after-confirmation entry timing.

Exit primitive shape:

- `time_exit.session_end`: last bar close before session end, fill timing `next_bar_open`, partial-session policy `no_exit`.
- `opening_range_opposite_side`: close-confirmed opposite-side stop, not evaluated until after entry bar.
- `fixed_R_target`: close-confirmed fixed-R target using `opening_range_opposite_side` as the stop reference.

Variant axes:

| Axis | Values |
|---|---:|
| `retest_window_bars` | `2`, `4` |
| `breakout_tolerance_atr` | `0.0`, `0.1` |
| `fixed_R_target` | `1.0`, `2.0` |

Denominator:

- `2 x 2 x 2 = 8` variants.
- No parameter was narrowed or changed after seeing scratch output.

## 4. Scratch Integration Reconfirmation

Probe class: scratch feasibility check.

Canonical-equivalent: NO. The command uses the current canonical runner path and exact data lineage, but the Strategy Spec / VM / Sweep artifacts are scratch-only review inputs, not committed canonical preregistration artifacts.

Command:

```powershell
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_runner.run_offline_sweep --strategy-spec scratch\WP-ONLINE-ORB-15M-PREREG-01\orb_15m\STRAT-SPEC-9103.strategy_spec.json --variant-manifest scratch\WP-ONLINE-ORB-15M-PREREG-01\orb_15m\VM-9103.variant_manifest.json --sweep-plan scratch\WP-ONLINE-ORB-15M-PREREG-01\orb_15m\SWEEP-PLAN-9103.sweep_plan.json --canonical-15m --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --d4-catalog-slice research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json --d2-import-report research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json --run-label WP-ONLINE-ORB-15M-PREREG-01-orb-session-end --sizing-mode dynamic_equity_target_leverage --target-leverage 1.0 --max-workers 4
```

Result:

- Completed: YES.
- Wall-clock: 173.7 seconds for direct CLI summary; 172.157 seconds for row-extraction API run.
- Dry run: `true`.
- Result Population write: NO (`wrote=false`, `output_path=null`).
- In-memory dry-run result population ID: `RP-1482`.
- Denominator: 8.
- Outcome counts: 8 successful, 0 failed, 0 invalid, 0 excluded, 0 errored, 0 aborted, 0 filtered, 0 data-unavailable, 0 not-attempted.
- Integration nondegenerate: YES. All 8 rows completed with nonzero trades.

Scratch row metrics:

| Variant | retest | tolerance | target R | trades | return_pct | sharpe | drawdown | fees | slippage | funding |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 2 | 0.0 | 1.0 | 999 | -0.848720 | -2.408586 | 0.863085 | 3649.167876 | 912.291969 | 0.0 |
| VAR-000002 | 2 | 0.0 | 2.0 | 999 | -0.907570 | -2.442578 | 0.915990 | 3044.129662 | 761.032415 | 0.0 |
| VAR-000003 | 2 | 0.1 | 1.0 | 1056 | -0.876507 | -2.476977 | 0.887362 | 3592.616599 | 898.154150 | 0.0 |
| VAR-000004 | 2 | 0.1 | 2.0 | 1056 | -0.911901 | -2.324061 | 0.925420 | 3405.578180 | 851.394545 | 0.0 |
| VAR-000005 | 4 | 0.0 | 1.0 | 1298 | -0.918915 | -2.801897 | 0.928058 | 3937.988504 | 984.497126 | 0.0 |
| VAR-000006 | 4 | 0.0 | 2.0 | 1298 | -0.951480 | -2.718414 | 0.957541 | 3581.314701 | 895.328675 | 0.0 |
| VAR-000007 | 4 | 0.1 | 1.0 | 1344 | -0.935667 | -2.870006 | 0.941262 | 3680.006109 | 920.001527 | 0.0 |
| VAR-000008 | 4 | 0.1 | 2.0 | 1344 | -0.952351 | -2.566962 | 0.960920 | 3936.983058 | 984.245764 | 0.0 |

Aggregate scratch facts:

- Trade count: min 999, median 1177, max 1344.
- Return: min -0.952351, median -0.915408, max -0.848720.
- Sharpe: min -2.870006, median -2.521969, max -2.324061.
- Drawdown: min 0.863085, median 0.926739, max 0.960920.
- Fees plus slippage plus funding: min 3805.162077, median 4526.115297, max 4922.485630.

Cost/gross availability:

- The current result population metric schema exposes `pnl`, `return_pct`, `sharpe`, `drawdown`, `trade_count`, `fees`, `funding`, `slippage`, `exposure`, and `win_rate`.
- It does not expose gross PnL, gross profit/loss, turnover, average equity, or per-trade PnL distribution in the Result Population row.
- Therefore `cost/gross` is unavailable from existing committed result-population fields. This package does not fabricate it.
- Follow-up instrumentation is required before any future canonical trial can apply a cost/gross screen honestly.

## 5. Frozen Screen Draft

This screen is proposed for Main/Karl review only. It is not applied as canonical evidence in this package.

### Denominator / Completeness

PASS only if:

- denominator equals 8;
- all 8 variants complete or all non-success rows are retained with explicit category accounting;
- result row count, outcome count sum, and committed denominator agree;
- failed, invalid, excluded, errored, aborted, filtered, data-unavailable, and not-attempted rows remain visible;
- winner-only and successful-only denominator treatment are forbidden.

### Net Performance

PASS only if:

- median net return is greater than 0;
- at least 5 of 8 variants have positive net return;
- positive-return rows have nontrivial trade counts;
- Sharpe is available across the whole population and not reported winner-only.

### Drawdown

PASS only if:

- median max drawdown is less than or equal to 0.45;
- maximum max drawdown across variants is less than 0.60;
- any variant drawdown greater than or equal to 0.75 is automatic NO-GO.

### Cost / Churn

Required recording:

- trade counts and average trades per year;
- fees, slippage, funding, and total recorded cost;
- median and max available cost metric;
- cost/gross availability status.

PASS only if a compounding-aware cost metric is available and cost does not dominate gross edge. Preferred metric is cost/gross PnL on positive-gross rows. If gross PnL is unavailable from canonical row fields, classify the screen as `INCONCLUSIVE / instrumentation-required` rather than fabricating the value.

Churn must be assessed explicitly because 15m frequency is the main risk. This screen should not permit a GO based on a single low-churn winner or on cost-blind net metrics.

### Sensitivity

PASS only if:

- positive rows span more than one bucket on at least two independent axes;
- sensitivity covers `retest_window_bars`, `breakout_tolerance_atr`, and `fixed_R_target`;
- a single-cell or winner-only conclusion is forbidden.

### Statistical Screens

DSR / PSR / MinTRL may be computed only if the required formula inputs are available in the future evidence artifact. If not evaluable, record them as unavailable and identify the missing fields. Do not fabricate numeric confidence.

### Verdict Framing

Allowed future screen verdicts:

- `GO`
- `NO-GO`
- `INCONCLUSIVE / instrumentation-required`

Cost NO-GO interpretation:

- If ORB 15m NO-GOs mainly on cost/churn, interpret it as 15m cost-hostility for this archetype, not as permission to retune 15m parameters.
- The natural follow-on would be a higher-timeframe ORB surface, subject to Main/Karl direction.

## 6. Current Scratch Read

Fact:

- The scratch integration is nondegenerate mechanically: 8/8 rows complete and all rows trade.
- The scratch economic read is poor: all 8 rows have negative net return, negative Sharpe, and drawdown above the proposed automatic NO-GO drawdown threshold.
- The current Result Population row fields are insufficient for cost/gross.

Inference:

- The proposed surface is ready for Main/Karl review as a freeze candidate from an integration standpoint.
- The frozen screen should require follow-up cost/gross instrumentation before canonical trial if Main/Karl want the cost gate to be decisive rather than unavailable.

Decision:

- Do not freeze or finalize in this package.
- Do not write a canonical Result Population.
- Do not register a candidate or authorize walk-forward/paper/live/runtime work.

## 7. Boundary Recap

- Committed Strategy Spec / VM / Sweep: NO.
- Result Population write: NO.
- Canonical trial: NO.
- Candidate registration: NO.
- Walk-forward/OOS: NO.
- Paper/live/runtime/capital: NO.
- OMS/risk/reconciliation/broker/exchange paths: NO.
- Schema/compiler/runner/query/data behavior changed: NO.
- Protected paths touched: NO.

## 8. Follow-Up

Narrowest next item:

- Main/Karl review of the ORB 15m preregistration surface and frozen screen.

If Main/Karl approve finalization:

- A later package should either commit finalized Strategy Spec / VM / Sweep artifacts or explicitly choose scratch-only no-freeze closure.
- Before a canonical trial, decide whether to add Result Population cost/gross instrumentation or mark the cost gate as unavailable/instrumentation-required by design.
