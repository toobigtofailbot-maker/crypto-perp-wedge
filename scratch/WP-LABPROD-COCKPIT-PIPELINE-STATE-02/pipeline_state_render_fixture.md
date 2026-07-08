# Lab Product Cockpit (read-only)

_schema: `lab_product_cockpit_v1` — read_only_operator_cockpit_

> Static read-only cockpit. No run / approve / promote / retry / candidate / scheduler / live-fetch control.

> No further edge-search is authorized by the coordinator state model. Strategy generation/search remains held until separate operator authorization.

## Lab overview

- Real-traffic operating-layer acceptance evidence concluded; lab held at edge-search with no candidate produced.
- Real-traffic batch: decision `complete`, 32/32 rows preserved, 32 executed successful, GO-like evidence: False, canonical RP written: False.
- Top blockers:
  - No hypothesis produced GO-like or candidate-worthy evidence (0 GO-like of 4 frozen).
  - No canonical Result Population written; evidence is dry-run / package-local.
  - Monte-Carlo / bootstrap withheld; PSR / DSR / MinTRL not computed.
  - Walk-forward evidence is bounded dry-run only, not a rigorous OOS gate pass.
  - Edge-search remains held pending separate operator authorization.

## Pipeline runs / run-state

- Runs: 3 (awaiting approval: 1, blocked/invalid: 1, complete spine-only: 1, complete real-runner: 0).
- Honest labeling: State spine / prereg approval contract only; real agent/runner adapter flow not yet complete.

| run | status | current stage | runner_invoked | blocker |
| --- | --- | --- | --- | --- |
| `LPIPE-0508a68667a87ce9` | COMPLETE · SPINE ONLY | `complete` | False | — |
| `LPIPE-2201304f65ac6f79` | AWAITING PREREG APPROVAL | `awaiting_prereg_approval` | None | prereg_approval_blocked:missing_prereg_approval |
| `LPIPE-e7d1a256221a28aa` | BLOCKED | `blocked` | None | availability_blocked:unsupported_timeframe |

## Candidate funnel (full denominator)

| stage | count |
| --- | ---: |
| Frozen hypotheses | 4 |
| Executed (denominator preserved) | 4 |
| Positive median PnL surface | 3 |
| GO-like evidence | 0 |
| Candidate-ready for human review | 0 |

## Strategy / hypothesis explorer

| hypothesis | status | positive rows | median PnL | max drawdown | RP |
| --- | --- | ---: | ---: | ---: | --- |
| `LAB-RT-HYP-001` | NON-PROMOTING | 6/8 | 19,190.54 | 77.09% | RP-3523 |
| `LAB-RT-HYP-002R` | NON-PROMOTING | 8/8 | 56,170.01 | 77.28% | RP-1413 |
| `LAB-RT-HYP-003R` | NO-GO | 0/8 | -9,800.99 | 99.00% | RP-2231 |
| `LAB-RT-HYP-004R` | NON-PROMOTING | 8/8 | 57,714.73 | 77.28% | RP-6877 |

### `LAB-RT-HYP-001` — BTCUSDT 4h no-wick EMA retest continuation

- route: `price_only_ohlcv.no_wick_ema_retest_4h`
- non-promoting: fails primary drawdown screen; WFO 24/24 dry-run; Monte-Carlo withheld.
- reading: NO-GO / not candidate-worthy despite positive median return because max drawdown is about 77.1% and sensitivity includes negative rows.

### `LAB-RT-HYP-002R` — BTCUSDT 15m RVOL-gated range-expansion breakout

- route: `price_only_ohlcv.rvol_range_expansion_breakout_15m`
- non-promoting: fails primary drawdown screen; WFO 24/24 dry-run; Monte-Carlo withheld.
- reading: RVOL-gated immediately previous-bar high/low range-expansion breakout; not Donchian, not ORB, not session-anchor substitution. Positive PnL rows are offset by drawdown around 77.28%, so the frozen GO screen is not met.

### `LAB-RT-HYP-003R` — BTCUSDT 15m rolling VWAP distance reversion

- route: `price_only_ohlcv.rolling_vwap_distance_reversion_15m`
- non-promoting: negative population and severe drawdown; WFO 24/24 dry-run; Monte-Carlo withheld.
- reading: NO-GO. 0/8 positive rows, median return about -98.0%, high churn and severe drawdown. Pass-with-caution context against RP-7134 / STRAT-SPEC-0003 retained.
- context: pass_with_caution
- context: future result records must carry pass_with_caution context

### `LAB-RT-HYP-004R` — BTCUSDT 15m session-filtered EMA impulse continuation

- route: `price_only_ohlcv.session_ema_impulse_continuation_15m`
- non-promoting: fails primary drawdown screen; WFO 24/24 dry-run; Monte-Carlo withheld.
- reading: NO-GO / not candidate-worthy despite 8/8 positive full-slice rows because max drawdown is about 77.3%; session filter is load-bearing but evidence fails drawdown screen. Pass-with-caution context against RP-2592 / RP-3731 / RP-6236 retained.
- context: pass_with_caution
- context: future result records must carry pass_with_caution context

## Robustness / WFO / OOS

- Walk-forward is bounded dry-run only; not a rigorous OOS gate pass.
- Monte-Carlo run: False — No package-local MC runner surface was used; no new dependency or runner change authorized.
- Withheld statistics: MonteCarlo, Bootstrap, PSR, DSR, MinTRL.

## Activity / evidence timeline

- PR #600 — Revised four-hypothesis set signed off and frozen (`scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`)
- PR #606 — Revised batch executed (HYP-002R blocked pending runner support) (`scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/real_traffic_batch_manifest.json`)
- PR #608 — HYP-002R completed; final revised-batch rollup (`scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/revised_batch_final_rollup.json`)
- PR #609 — Real-traffic batch synthesis concluded (`docs/research/LAB_REAL_TRAFFIC_BATCH_SYNTHESIS_2026-07.md`)

## Coordinator state

| overall state | count |
| --- | ---: |
| `not_started` | 0 |
| `formalized` | 0 |
| `experiment_complete` | 1 |
| `replay_checked` | 0 |
| `oos_gate_fail` | 1 |
| `oos_gate_blocked` | 0 |
| `candidate_review_blocked` | 0 |
| `robustness_advisory` | 0 |
| `no_go` | 4 |
| `blocked` | 2 |
| `candidate_ready_for_human_review` | 0 |
| `operator_gate_pending` | 0 |
| `reported` | 1 |

## Artifact drilldown

- [conclusion_doc] `docs/research/LAB_REAL_TRAFFIC_BATCH_SYNTHESIS_2026-07.md` (present)
- [batch_rollup] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/revised_batch_final_rollup.json` (present)
- [frozen_set] `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json` (present)
- [batch_manifest] `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/real_traffic_batch_manifest.json` (present)
- [strategy_reading] `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/strategy_reading_summary.json` (present)
- [strategy_reading] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_strategy_reading.json` (present)
- [walkforward_oos] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_wfo_oos_summary.json` (present)
- [robustness_mc] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_robustness_mc_summary.json` (present)
- [denominator_audit] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_denominator_audit.json` (present)
- [boundary] `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/non_authority_assertions.json` (present)

## Boundary / non-authority

- autonomous_scheduler_activated: False
- bounded_real_research_traffic: True
- candidate_admission_authorized: False
- candidate_admitted: False
- canonical_crossing_authorized: False
- canonical_crossing_performed: False
- dependency_changes: False
- karl_signoff_present: True
- main_verification_present: True
- non_promotion_posture: True
- paper_live_authority_created: False
- parameter_expansion_after_results_performed: False
- private_provider_api_used: False
- promotion_readiness_authorized: False
- promotion_readiness_created: False
- protected_paths_touched: False
- real_notification_sending_authorized: False
- retuning_after_results_performed: False
- runtime_contact_performed: False
- signed_frozen_set_modified: False
- signed_revised_frozen_set_present: True
- winner_only_pruning_performed: False

> This cockpit shows the full denominator (every hypothesis and row), not winners only.
> All real-traffic evidence is dry-run / package-local and non-canonical; nothing here is crossed, candidate-registered, paper-ready, or live-ready.
> Positive PnL surfaces that fail the primary drawdown screen are shown as non-promoting, not as edges.
> Withheld statistics (Monte-Carlo / bootstrap / PSR / DSR / MinTRL) are labelled explicitly rather than fabricated.
> Display ordering is deterministic and confers no ranking, recommendation, readiness, or promotion authority.
> Any real transition, candidate admission, crossing, or approval requires separate human action; this cockpit cannot grant it.
