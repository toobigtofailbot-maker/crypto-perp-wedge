# Hypothesis H-012: 15m Trend Following with Funding Filter

## Hypothesis ID
H-012

## Metadata
- Created: 2026-05-29
- Status: DRAFT
- Owner: WP-12ff / WP-S2c-126
- Source design: `docs/research_pipeline/2026-05-path_b_execution_candidate_selection_design.md`

## Main 4.0 Bounded Acceptance of `ohlcv_15m`

`ohlcv_15m` is accepted as a permitted `information_inputs` label per Main 4.0 ruling at the WP-S2c-125 stop-item resolution.

Acceptance rationale:
1. The registry's established `ohlcv_{timeframe}` convention applies to locked timeframes by construction. Prior candidates use `ohlcv_30m`, `ohlcv_1h`, `ohlcv_4h`, and `ohlcv_1d` verbatim; `ohlcv_15m` follows the same pattern applied to the locked 15m timeframe.
2. `15m` is a locked timeframe with `PLANNING` status in `research/timeframe_status.md`; it is listed verbatim in D2-013 (`docs/onboarding/PHASE2_BASELINE.md`).
3. BTCUSDT 15m OHLCV data is present in `docs/data_catalog.md` (Dataset: BTCUSDT 15m full history, range 2020-01-01 / 2026-04-11, path `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`).
4. The acceptance is convention application against locked surfaces, not taxonomy addition or reinterpretation; no new taxonomy label is introduced.
5. Locked Option B framing is preserved. This package operates under locked Option B as-written.

## Economic Rationale

BTC perpetual futures exhibit intraday directional runs — periods where price accumulates bars in one direction before reversing or pausing. At the 15m granularity, these runs are shorter in duration and noisier than 4h or 1d trends, but they may be detectable through conventional trend signals applied to 15m bars when combined with a funding-rate context filter.

The funding rate reflects the cost of holding a leveraged perpetual position and encodes whether the market is net long or net short in aggregate. When the funding direction aligns with a detected 15m price trend, the net leveraged positioning adds structural tailwind pressure in that direction. When funding opposes the detected trend, leveraged positioning may act as a headwind that increases false-signal probability.

This rationale is about observable market structure and data relationships, not a performance expectation. The 15m timeframe has not been tested in this repository, and the rationale does not guarantee that a well-designed candidate will pass any D2-006 gate.

Cost drag at 15m is a primary design risk. At higher trade frequency, fees and slippage consume a larger fraction of gross PnL than at 4h or 1d. A minimum hold period or signal persistence requirement may be needed to keep cost drag within the D2-006 Gate 5 threshold (≤ 50% of gross PnL). This is a design tension to be resolved in WP-S2c-127.

## Testable Prediction

These predictions are falsifiable and derived from the WP-S2c-125 design surface. Confirmation does not imply D2-006 pass or readiness.

1. A 15m trend signal (e.g., moving-average crossover or channel breakout on `ohlcv_15m`) produces OOS Sharpe > 0 more often than random entry over multi-year walk-forward folds, whether or not it clears the D2-006 Gate 1 threshold of ≥ 1.0.
2. The `funding_8h` directional filter reduces the false-signal rate — measured as the fraction of signals that produce negative OOS returns — compared to a pure 15m price-trend baseline using `ohlcv_15m` alone.
3. Cost drag at 15m is materially higher than 4h equivalents (H-001, H-002), consistent with the D2-006 Gate 5 structural concern for faster timeframes. Cost drag must remain within Gate 5 (≤ 50% of gross PnL) to be viable.
4. Free-parameter count remains at or below 3 for the initial baseline design (trend lookback + funding threshold + optional minimum hold), within the D2-006 Gate 7 limit of ≤ 5.

## Primary Timeframe
15m

**Justification:** The `15m` timeframe has zero concluded candidates in the locked research timeframe set (confirmed by Q05.json, `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q05.json`). It is listed verbatim in the locked timeframe set (D2-013, `docs/onboarding/PHASE2_BASELINE.md`). Its status in `research/timeframe_status.md` is `PLANNING`, the only non-cold-storage timeframe currently available. The design tests short-horizon directional behavior distinct from the 4h and 1d candidates tested in H-001 through H-010. No timeframe boundary is added or changed by this candidate.

## Confirmation Timeframes
None

`funding_8h` is an information input and context filter, not a confirmation timeframe. It is used to gate or weight the 15m trend signal at the bar level, not as a separate timeframe driving entry decisions. Per D2-015, confirmation timeframes must be coarser than the primary timeframe; the absence of a confirmation timeframe is intentional for this initial baseline. No multi-timeframe confirmation is introduced.

## Required Data

- Instrument: BTCUSDT Binance USDT-M Perpetual
- Required streams:
  - `ohlcv_15m`
  - `funding_8h`
- Required data catalog paths:
  - BTCUSDT 15m full history Parquet: `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` (confirmed in `docs/data_catalog.md`, range 2020-01-01 / 2026-04-11)
  - BTCUSDT funding rates full history Parquet: `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet` (confirmed in `docs/data_catalog.md`, range 2019-09-10 / 2026-04-12)
- No external data, paid data, Tier 4, protected-path, runtime, paper/live, broker/exchange/order, or live API contact is used or required.

## Signal Logic

Pre-registration-level description only. Exact parameter defaults and execution logic are deferred to WP-S2c-127 EXP. No backtest is run in this package.

**Inputs:**
- 15m OHLCV bars (open, high, low, close, volume).
- 8h funding rates aligned to 15m bars by forward-fill timestamp with no lookahead.

**Candidate theme:**
- Short-horizon trend-following signal on 15m OHLCV bars.
- Funding-rate directional context filter: when funding direction opposes the detected trend, the filter may attenuate or suppress the signal to reduce false entries from counter-directional leveraged positioning.

**Candidate direction:**
- The directional profile (long/short/flat) will be specified in the WP-S2c-127 EXP after review of funding filter interaction. No additional parameters beyond the three-parameter budget are introduced for direction control in the initial baseline.

**Parameters (pre-registration level):**
1. Trend lookback window (number of 15m bars for moving-average or breakout calculation).
2. Funding threshold (funding rate level above or below which the filter activates).
3. Optional minimum hold bars (minimum bars a position must be held for cost-drag control; may be fixed at 0 for the minimal baseline).

Exact parameter defaults, signal generation logic, preprocessing steps, position-change rules, and execution assumptions are deferred to WP-S2c-127 EXP. No backtest is run here.

## Success Criteria

Locked D2-006 gates from `docs/onboarding/PHASE2_BASELINE.md`:

1. OOS Sharpe ≥ 1.0 net of modeled costs.
2. DSR > 1.0 at 95% confidence given actual cumulative trial count from `research/trial_log.jsonl`.
3. Max drawdown ≤ 20% in any walk-forward fold.
4. Parameter sensitivity: ±25% parameter shift keeps Sharpe within 70% of baseline.
5. Cost drag ≤ 50% of gross PnL.
6. No single 90-day window contributes > 60% of total PnL.
7. ≤ 5 free parameters.
8. Walk-forward efficiency (OOS/IS Sharpe ratio) > 0.5.

All eight gates must pass for promotion eligibility. Gate thresholds are frozen in `docs/onboarding/PHASE2_BASELINE.md` and `lib/evaluation.py` and require a Decision Change entry to modify.

## Kill Criteria

- OOS Sharpe < 0.3 after baseline test.
- Cost drag persistently exceeds D2-006 Gate 5 threshold (≤ 50% of gross PnL) across tested parameter configurations.
- Max drawdown materially exceeds D2-006 Gate 3 threshold (≤ 20%) in multiple walk-forward folds.
- Funding filter fails to reduce false-signal rate versus pure 15m trend baseline after baseline evaluation.
- Parameter sensitivity fails D2-006 Gate 4 (min_ratio < 0.70 at ±25% parameter shift).
- Evidence indicates design requires > 5 free parameters or unapproved information inputs to achieve signal quality.

## Free Parameters

1. **Trend lookback window** — number of 15m bars for moving-average or channel calculation.
2. **Funding threshold** — funding rate level above or below which the directional filter activates.
3. **Minimum hold bars** (optional) — minimum bars a position must be held; included for cost-drag control.

Count: 2 parameters for the minimal baseline (lookback + funding threshold), expandable to 3 if minimum hold is treated as free. The registry uses `free_parameter_count: 3` as the conservative maximum for this initial candidate.

Any design requiring > 5 free parameters halts and requires Main/Karl routing before proceeding.

## Expected Trial Count

- Primary baseline run: 1
- Parameter sensitivity trials (±25% shift on up to 2 free parameters): approximately 4
- Total initial budget: approximately 5 logged trials

Every backtest run must be logged in `research/trial_log.jsonl` in WP-S2c-128. No trial-log entry is created in this package. DSR must be computed at REP creation time (WP-S2c-128) using the cumulative trial count from `research/trial_log.jsonl` including all prior H-001 through H-010 trials.

## Artefacts

- Notebook: `research/hypotheses/2026-05-29_H-012_15m-trend-following-funding-filtered/experiment.ipynb` (scaffold only; no backtest outputs; created in this package, WP-12ff / WP-S2c-126)
- Future EXP: to be created in WP-S2c-127.
- Future REP and trial-log entries: WP-S2c-128.
- Future OL/REC: WP-S2c-129.
- Future DEC: WP-S2c-130.

This package creates no EXP, REP, OL, REC, or DEC artifact.

## Decision Record

- Outcome: PENDING
- Decision record path: null; future WP-S2c-130 DEC.
- No decision is made in this package.

## Notes

- One-candidate authorization only. This package registers exactly one initial Path B candidate under locked Option B. Multiple-candidate authorization is not granted.
- No readiness, transition, recommendation, ranking, or scoring is asserted by this package.
- REC-5 exact-segment discipline remains absolute. Any future REC entry for H-012 will start at count 1 for any new exact segment (candidate_id / outcome_kind / pipeline_version / expectation_source_type), which is below the REC-5 floor of n ≥ 3. Cross-segment inference across existing candidate segments (H-001 through H-011) is not allowed. The initial REC will be below floor if later created, and cannot infer across segments.
- No backtest is run, and no trial-log entry is created in this package.
- H-011 remains unchanged (cross_asset_regime / weekly / reserved). H-012 is the next available candidate ID following direct registry inspection confirming H-011 incompatibility with the selected surface.
