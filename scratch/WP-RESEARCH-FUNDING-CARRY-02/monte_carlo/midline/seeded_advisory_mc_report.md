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
Output checksum: `sha256:65106df86941182232213881b9bfe2c136a0e0095f7b0644d9ea402ff117018a`

## Fixture

- Result Population: `RP-7592`
- Path: `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/runner_artifacts/RP-7592.result_population.json`
- Checksum: `sha256:18bfe97d571b3e5debf675a103e736ff29ce17287847a4b673cc4cbe68480d37`
- Rows used: `18`
- Row filter: `attempted_true_and_outcome_category_successful`
- Variant Manifest: `VM-9934`
- Sweep Plan: `SWEEP-PLAN-9934`
- Fixture validation: `passed`

## Bootstrap Confidence Intervals

| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |
|---|---:|---:|---:|---:|---:|
| drawdown | 0.9837178117673359 | 0.9841424592890557 | 0.9571486615052753 | 1.0 | 18 |
| exposure | 1.0 | 1.0 | 1.0 | 1.0 | 18 |
| fees | 9497.585776155647 | 9603.914768187016 | 4060.4403213776654 | 16859.772889544493 | 18 |
| funding | 0.0 | 0.0 | 0.0 | 0.0 | 18 |
| pnl | -4901.7435213918325 | -4954.300131463841 | -10000.0 | 3252.1212903294254 | 18 |
| return_pct | -0.49017435213918326 | -0.48526468631530706 | -1.0 | 0.3252121290329425 | 18 |
| sharpe | -0.19295855678505316 | -0.18787853709512736 | -0.5488219950108814 | 0.13229296590418027 | 18 |
| slippage | 2374.396444038912 | 2329.0275532892706 | 1037.2656068758813 | 4140.851246627575 | 18 |
| trade_count | 347.1111111111111 | 348.098611111111 | 232.3625 | 475.05833333333334 | 18 |
| win_rate | 0.4914090939332548 | 0.49150187258737604 | 0.46989342634769526 | 0.5152667536628662 | 18 |

## Missing / Queued Inputs

- Metrics skipped: `[]`
- Per-trade Monte Carlo: `QUEUE_PER_TRADE_INSTRUMENTATION`
- Parameter sensitivity: `insufficient_mapping`

## Boundary

- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.
- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.
- No per-trade data is fabricated.
