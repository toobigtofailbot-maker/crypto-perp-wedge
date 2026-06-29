# Funding Positioning Fade Synthesis - 2026-06

## Scope

This document records the completed scratch-only research result for `H-FUNDING-RATE-POSITIONING-FADE-01` and the later bounded risk-managed Stage-1 triage conclusion for `H-FUNDING-FADE-RISKMANAGED-01`. It does not run new research, create canonical evidence, register a candidate, execute crossing, or authorize paper/live/runtime work.

## Hypothesis

Prior unhardened hypothesis: `H-FUNDING-RATE-POSITIONING-FADE-01`

Extreme positive funding was interpreted as long-side crowding and a contrarian short entry. Extreme negative funding was interpreted as short-side crowding and a contrarian long entry. The frozen family used 30/90/180-day rolling empirical funding percentiles, symmetric 0.10/0.90 and 0.05/0.95 entry tails, two exit modes, and 16/32/96-bar maximum holds.

Risk-managed follow-up hypothesis: `H-FUNDING-FADE-RISKMANAGED-01`

The risk-managed follow-up kept the funding positioning-fade signal family fixed and tested whether an a-priori ATR risk layer could rescue the already isolated drawdown failure during a frozen 2024 Stage-1 triage. It did not authorize retuning, alternate funding lookbacks, alternate entry percentiles, alternate windows, Stage-2 execution, canonical evidence, candidate lifecycle writes, or paper/live/runtime work.

## Conclusion

`H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO under the tested price-P&L funding-rate signal interpretation.`

`H-FUNDING-FADE-RISKMANAGED-01 = NO-GO under the frozen 2024 Stage-1 risk-managed triage criteria.`

Evidence class: scratch-only, non-canonical, not crossed, not candidate authority, not paper-ready, not live-ready.

The funding positioning-fade signal failed both the prior unhardened evidence path and the risk-managed Stage-1 triage. The risk-control test did not reveal a signal worth protecting. The Stage-1 result is triage-only but decisive for this hypothesis under the frozen criteria.

No retuning loop is authorized. No Stage-2 prereg or execution is authorized. No candidate claim exists.

## Data

- Market: BTCUSDT perpetual.
- Timeframe: 15m.
- Bar count: 220,128 bars.
- Feature: `funding_rate` column staged from PR #560 local ignored data.
- Input data SHA256 recorded by the upstream scratch replay report: `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`.

## Result Populations

| Exit mode | Result population | Rows | Status |
| --- | --- | ---: | --- |
| `fixed_max_hold_only` | `RP-2009` | 18 | scratch-only complete |
| `midline_reversion_or_max_hold` | `RP-7592` | 18 | scratch-only complete |

Combined denominator:

- 36 planned.
- 36 complete.
- 0 failed.
- 0 invalid.
- 0 blocked.
- 0 pruned.

## Primary Failure

All 36 completed rows failed the primary 20% drawdown screen.

Drawdown ranges:

- `fixed_max_hold_only`: 85.68% to 100%.
- `midline_reversion_or_max_hold`: 80.72% to 100%.

Top return and Sharpe outliers do not override the drawdown failure because every full-history row exceeded the primary drawdown screen.

## Risk-Managed Stage-1 Follow-Up

Source package: `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01`, PR #581.

The Stage-1 2024 triage for `H-FUNDING-FADE-RISKMANAGED-01` planned 108 rows and accounted for all 108 rows. There were no blocked, errored, invalid, or data-unavailable rows, and winner-only reporting did not occur.

| Risk state | Rows | Median drawdown | Worst drawdown | Median net return | Positive-return rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `no_atr` | 36 | 0.497721 | 0.737582 | -0.459715 | 0 |
| `atr_20` | 36 | 0.481411 | 0.729638 | -0.440943 | 0 |
| `atr_30` | 36 | 0.507059 | 0.716278 | -0.464067 | 0 |

All three risk-control states were gross-negative. ATR stops did not produce a viable return/drawdown tradeoff: `atr_20` barely improved median drawdown while retaining negative median net return and zero positive-return rows, and `atr_30` did not improve median drawdown. The frozen stop/go criteria therefore conclude `NO-GO`.

## OOS

The upstream package ran a dry-run-only one-window OOS hook. It did not rescue the result:

- `fixed_max_hold_only` OOS drawdown range: 25.93% to 100%.
- `midline_reversion_or_max_hold` OOS drawdown range: 29.26% to 100%.
- 7 of 36 OOS rows had positive P&L.
- No canonical walk-forward artifact was written.

## Robustness

Descriptive robustness reports were produced. PSR, DSR, and MinTRL were withheld where required inputs were unavailable. Seeded advisory bootstrap reports showed mean drawdown near 98% to 99%. Per-trade Monte Carlo was blocked because real per-trade rows are not available; none were fabricated.

## Interpretation Caveats

- This was a price-P&L funding-rate signal test.
- Funding payments were not wired.
- `funding_cost_mode` was off.
- This was not a complete funding-carry-P&L test.
- Existing fees and slippage were enabled.
- Top return outliers do not override the drawdown failure.
- This is not a general verdict on funding-signal families.
- This is not a broad predictive-value judgment about funding.
- This is not a funding-payment or carry-P&L test.
- This does not imply canonical crossing or candidate authority.
- The risk-managed Stage-1 conclusion does not claim all funding strategies are dead.
- The risk-managed Stage-1 conclusion does not claim all BTC perp data-derived strategies are dead.
- The risk-managed Stage-1 conclusion does not claim paper/live implications.
- The risk-managed Stage-1 conclusion is not a canonical full-history candidate test.
- The risk-managed Stage-1 conclusion does not decide future unrelated taker-flow or OI hypotheses.

## Candidate And Crossing Status

No candidate-review packet was generated because all 36 completed full-history rows exceeded the 20% primary drawdown screen. No candidate was registered. No canonical crossing occurred.

For `H-FUNDING-FADE-RISKMANAGED-01`, no candidate claim exists because the 108-row Stage-1 triage concluded `NO-GO` under the frozen criteria. No Stage-2 prereg or execution is authorized.

## Drift Guardrail

This NO-GO does not automatically authorize another edge-search cycle. Additional data-derived families or funding variants require separate Main/operator authorization. Near-term lab-completion work is separate from new hypothesis search.

## Traceability

Primary upstream evidence:

- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/runner_result_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/metrics_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/walk_forward_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/no_candidate_review_packet_reason.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/rp_replay_harness_report.json`

Risk-managed Stage-1 evidence:

- `docs/status_entries/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01.md`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.md`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stop_go_evaluation.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/row_accounting.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/complete_108_row_denominator.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/complete_108_row_denominator.csv`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/atr_vs_no_atr_comparison_summary.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/no_atr_slice_summary.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/atr_20_slice_summary.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/atr_30_slice_summary.json`
- `scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/conclusion_summary.json`
