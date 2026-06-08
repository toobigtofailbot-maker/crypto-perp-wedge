# Post-D5 Real-Data Interpretation Checkpoint

## 1. Scope

This is a T1 documentation-only descriptive checkpoint over result population
`RP-4492` (`research/result_populations/RP-4492.result_population.json`).

This checkpoint is evidence-not-authority. It creates no artifact mutation, no
result-population replacement, no strategy approval, no recommendation, no
paper/live/runtime authority, and no F5 implementation.

Specifically:

- Evidence-not-authority: observations describe what the artifact records, not
  what should be done next.
- No artifact mutation: `RP-4492` is consumed read-only. No result-population
  artifact is written, replaced, or renamed.
- No strategy approval: no strategy, variant, parameter set, or configuration
  is approved or selected.
- No recommendation: no variant is recommended over another.
- No paper/live/runtime authority: this checkpoint creates no authority over
  paper or live execution, the OMS, reconciliation, risk, safe-mode,
  broker/exchange contact, or execution controls.
- No F5 implementation: the F5 Results dashboard remains a separate package
  gated after this checkpoint.

## 2. Evidence Basis

- Result population ID / path: `RP-4492` /
  `research/result_populations/RP-4492.result_population.json`
- Provenance class: `canonical_real_data`
- Strategy Spec: `STRAT-SPEC-0001`
- Variant Manifest: `VM-0001`
- Sweep Plan: `SWEEP-PLAN-0001`
- Result population identity hash:
  `sha256:2a9cee1b1ba32d9f98f879aa4c1ef95e2f5b75b7348e1084e66afe80f77bb32c`
- Input identity hash:
  `sha256:8fca9c6f6238f4fd5712420921faa649a1a182866adb22f1d5f3680b850a535c`

## 3. D4 Provenance / Data Integrity Context

The following provenance and integrity facts are recorded in `RP-4492` and are
preserved here without modification.

- D4 catalog ref:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation identity:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- Row count / expected row count: `220128 / 220128`
- Timestamp range: `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`
- Gap facts: `gap_count=0`, `missing_bar_count=0`, `gaps=[]`
- Duplicate facts: `duplicate_group_count=0`, `duplicate_row_count=0`,
  `duplicates=[]`
- Raw source SHA256:
  `343b639e35ce79824d26bddf6d70af2641c9d76003301e303f83cdf61d4feab4`
- Normalized CSV SHA256:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

The D4 provenance chain was validated before the D5 sweep ran. The data slice
is offline only; no exchange or API contact occurred at sweep time.

## 4. Complete-Population / Denominator Context

- Committed denominator: `7`
- Variant result rows: `7`
- Outcome counts sum: `7`
- Represented variants: `VAR-000001` through `VAR-000007`
- No dropped, executed-only, successful-only, or winner-only denominator is
  encoded.

All observations below are population observations over the complete committed
7/7 denominator, not winner selection.

The denominator was committed before the sweep ran and is preserved in the
artifact. No post-hoc cleanup, filtering, or retention of only successful rows
occurred.

## 5. Descriptive Result Table

The table below is presented in variant ID order only. It is not sorted by any
performance metric. No row is ranked, emphasized, selected, or singled out. No recommendation is made.

Values are taken directly from `RP-4492.variant_result_rows[*].metrics` and
`outcome_category` fields. Reasonable rounding is applied for readability; the
canonical values remain in the artifact.

| variant_id  | return_pct | pnl ($)    | drawdown | sharpe  | trade_count | win_rate | fees ($)  | slippage ($) | outcome_category |
|-------------|------------|------------|----------|---------|-------------|----------|-----------|--------------|------------------|
| VAR-000001  | -1.0000    | -10000.00  | 1.0000   |  0.6404 | 970         | 0.7010   | 17915.00  |  4478.75     | successful       |
| VAR-000002  | -1.0000    | -10000.00  | 1.0000   | -0.1400 | 935         | 0.6492   | 25367.51  |  6341.88     | successful       |
| VAR-000003  | -1.0000    | -10000.00  | 1.0000   | -0.2800 | 888         | 0.6306   | 24590.50  |  6147.63     | successful       |
| VAR-000004  |  0.6125    |   6125.29  | 0.7731   |  0.5568 | 624         | 0.6170   | 21218.51  |  5304.63     | successful       |
| VAR-000005  |  4.2244    |  42244.30  | 0.4630   |  0.7859 | 243         | 0.6337   |  7462.78  |  1865.70     | successful       |
| VAR-000006  |  3.6849    |  36849.17  | 0.2905   |  0.8565 | 113         | 0.6372   |  3159.50  |   789.88     | successful       |
| VAR-000007  |  5.0472    |  50472.11  | 0.2690   |  1.2477 |  64         | 0.7500   |  1773.11  |   443.28     | successful       |

## 6. Descriptive Observations

The following observations describe what the artifact records. They do not rank
variants, select a preferred configuration, make a recommendation, or claim
readiness of any kind.

- Under this offline runner assumption set, all seven variants completed with
  `outcome_category=successful`. No aborted, errored, failed, excluded,
  filtered, invalid, not-attempted, or data-unavailable rows were recorded.
- The population spans both negative and positive `return_pct` values. Three
  variants show `return_pct = -1.0` in this result population; four show
  positive `return_pct` values.
- Trade count decreases across the variant ID sequence in this result
  population: from 970 trades for VAR-000001 to 64 trades for VAR-000007.
- Fee and slippage values are notably higher for variants with higher trade
  counts, as would be expected under a fixed-bps slippage model and taker-only
  fee assumption.
- Drawdown values vary across the population: three variants show drawdown of
  1.0 (full drawdown under the model); four show drawdown values below 1.0,
  ranging from approximately 0.27 to 0.77.
- Win rate across all seven variants falls in the range of approximately 0.63
  to 0.75 under this assumption set.
- Sharpe values range from approximately -0.28 to 1.25 across the population
  under this backtest assumption set.
- All seven variants were executed against the same D4A slice (220,128
  15-minute bars, `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`) with
  no gaps or duplicates recorded.
- The runner recorded `exposure=1.0` for all seven variants, consistent with
  always-in-market behavior under this assumption set.
- `funding=0.0` is recorded for all seven variants; funding cost is not
  captured under this runner assumption set.

## 7. Backtest Assumption Context

The following assumptions are recorded in `RP-4492.backtest_assumption_summary`
and constrain interpretation of all observations above.

| assumption field          | recorded value                                          |
|---------------------------|---------------------------------------------------------|
| `fill_mode`               | `complete`                                              |
| `bar_path_assumption`     | `next_open_close_mark`                                  |
| `fee_side_assumption`     | `taker_entry_taker_exit`                                |
| `slippage_model`          | `fixed_bps`                                             |
| `mark_price_source`       | `close`                                                 |
| `liquidation_mode`        | `zero_equity`                                           |
| `order_size_assumption`   | `future offline runner assumption only; no execution here` |
| `funding_notional`        | `entry_price`                                           |
| `liquidity_capacity_assumption` | `null`                                          |
| `maintenance_margin_assumption` | `null`                                          |

These assumptions constrain interpretation. `fill_mode=complete` assumes every
order fills in full at the modeled price. `fixed_bps` slippage does not model
liquidity depth, market impact, or realistic execution variability.
`taker_entry_taker_exit` applies taker fees on both sides. The
`order_size_assumption` field records that no actual order sizing was executed.

These assumption values do not represent live or paper readiness. They record
what the offline runner assumed for this sweep.

## 8. Caveats / Non-Authority Boundary

This checkpoint explicitly does not:

- Approve paper or live trading of any variant or configuration.
- Recommend a strategy.
- Rank variants as authority.
- Satisfy any gate.
- Create promotion, transition, readiness, runtime, paper/live, OMS,
  reconciliation, risk, safe-mode, broker/exchange, or execution authority.

D5 evidence is not a substitute for future review packages, additional data
slices, robustness checks, out-of-sample evaluation, slippage and liquidity
realism review, execution-risk review, or human-gated decisions. The
observations above reflect a single offline backtest under one assumption set
over one data slice. They do not generalize beyond what the artifact directly
records.

The `non_authority_declaration` block in `RP-4492` records that this result
population is not decision authority, ranking authority, recommendation
authority, readiness authority, runtime authority, paper/live authority,
candidate approval, gate authority, or a replacement for any canonical evidence,
reconciliation, or outcome-ledger artifact.

## 9. Dashboard Implication for F5

F5 Results dashboard can follow only after this checkpoint is accepted.

F5 should consume validated `dashboard_data` only, not raw result-population
JSON directly.

F5 should display:

- descriptive framing consistent with this checkpoint;
- complete-population context (7/7 denominator);
- provenance context (D4 catalog ref, D4 slice identity, D3 validation
  identity);
- non-authority warnings visible to any operator reading the dashboard.

F5 must not display ranking-as-authority, readiness claims, promotion cues,
recommendation language, or execution controls of any kind.

F5 is a separate package and remains gated until after this checkpoint is
accepted.

## 10. What Is Locked

This checkpoint locks only:

- RP-4492 descriptive interpretation checkpoint exists and is part of the repo
  record.
- D4 provenance and validation context from the artifact were preserved without
  modification.
- The 7/7 denominator context was preserved; all variants are included in
  observations.
- All observations were descriptive and non-authoritative.
- F5 Results dashboard remains a separate display-only package.

## 11. What Is Not Authorized

This checkpoint does not authorize:

- F5 implementation in this package.
- Paper, live, or runtime implementation of any kind.
- Strategy promotion of any variant.
- Readiness approval.
- Variant selection or ranking-as-authority.
- Creation of a new result population or replacement of `RP-4492`.
- Mutation of any result artifact, data artifact, or canonical artifact.
- Schema, validator, query-layer, or dashboard implementation changes.
- Protected-path changes.

## 12. Required Next Authority

After this package merges, Side reports back to Main and asks Main to confirm
F5 Results dashboard package authorization and constraints before F5 is drafted
or executed.

No F5 work should begin until Main provides explicit confirmation and, ideally,
a capsule or package brief for F5.
