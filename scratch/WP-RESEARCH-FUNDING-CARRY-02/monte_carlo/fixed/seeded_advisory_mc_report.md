# EXT-INTEG-ROBUSTNESS-MC-01 Seeded Advisory Robustness Report

- ADVISORY ROBUSTNESS / SEEDED MONTE CARLO OUTPUT
- NON-CANONICAL REPORT
- NOT A RESULT POPULATION
- NOT SCREEN-GATE AUTHORITY
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT CANDIDATE EVIDENCE AUTHORITY
- NOT PROMOTION / READINESS AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- PER-TRADE MONTE CARLO USES ONLY REAL PER-TRADE DATA IF AVAILABLE
- MISSING PER-TRADE DATA MUST BE REPORTED, NOT FABRICATED

Decision label: `ADOPT_AS_ROBUSTNESS_LAYER`
Seed: `20260624`
Bootstrap samples: `1000`
Confidence level: `0.95`
Output checksum: `sha256:3803071a6752a65835caee258c6ec3712cb79b92e81078a8b81cdf3b59598f8a`

## Fixture

- Result Population: `RP-2009`
- Path: `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/runner_artifacts/RP-2009.result_population.json`
- Checksum: `sha256:d6e5e6c46c38208b308b2c5aaa34b3a65176831b61b5026229c857ba08914076`
- Rows used: `18`
- Row filter: `attempted_true_and_outcome_category_successful`
- Variant Manifest: `VM-9933`
- Sweep Plan: `SWEEP-PLAN-9933`
- Fixture validation: `passed`

## Bootstrap Confidence Intervals

| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |
|---|---:|---:|---:|---:|---:|
| drawdown | 0.9920421483488876 | 0.9923286310083368 | 0.9761264450466628 | 1.0 | 18 |
| exposure | 1.0 | 1.0 | 1.0 | 1.0 | 18 |
| fees | 9020.659346661232 | 9107.08651322102 | 4126.224944505722 | 15733.239175072915 | 18 |
| funding | 0.0 | 0.0 | 0.0 | 0.0 | 18 |
| pnl | -6614.049010916809 | -6627.592814873078 | -10000.0 | 157.85296724957394 | 18 |
| return_pct | -0.6614049010916809 | -0.6532786187178794 | -1.0 | 0.01578529672495736 | 18 |
| sharpe | -0.5047856832056071 | -0.49449683482645207 | -1.0969163557430623 | 0.03851940208666206 | 18 |
| slippage | 2255.164836665308 | 2215.0376605760125 | 1044.8652226775973 | 3867.196655765634 | 18 |
| trade_count | 340.3888888888889 | 341.39383333333365 | 230.88333333333333 | 460.3902777777778 | 18 |
| win_rate | 0.49191584406338074 | 0.4919451086707302 | 0.4717105889429022 | 0.5139512377472575 | 18 |

## Missing / Queued Inputs

- Metrics skipped: `[]`
- Per-trade Monte Carlo: `QUEUE_PER_TRADE_INSTRUMENTATION`
- Parameter sensitivity: `insufficient_mapping`

## Boundary

- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.
- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.
- No per-trade data is fabricated.
