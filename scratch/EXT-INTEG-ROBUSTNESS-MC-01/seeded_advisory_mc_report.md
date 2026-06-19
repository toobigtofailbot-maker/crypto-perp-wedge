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
Seed: `20260619`
Bootstrap samples: `1000`
Confidence level: `0.95`
Output checksum: `sha256:5a400437ed6df521184dc372a42ad640baeb5c42e79190f10704634174c4f672`

## Fixture

- Result Population: `RP-2592`
- Path: `research/result_populations/RP-2592.result_population.json`
- Checksum: `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
- Rows used: `8`
- Row filter: `attempted_true_and_outcome_category_successful`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Fixture validation: `passed`

## Bootstrap Confidence Intervals

| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |
|---|---:|---:|---:|---:|---:|
| drawdown | 0.6396255106984028 | 0.6398843941516353 | 0.6048597429260648 | 0.6726167974730358 | 8 |
| exposure | 1.0 | 1.0 | 1.0 | 1.0 | 8 |
| fees | 11407.455777723917 | 11430.876014197538 | 8526.300997597984 | 14012.12492335079 | 8 |
| funding | 0.0 | 0.0 | 0.0 | 0.0 | 8 |
| pnl | 2998.133178257878 | 3013.226643928187 | -382.0206479433184 | 6223.171444929774 | 8 |
| return_pct | 0.29981331782578785 | 0.3099893028479074 | -0.01241983410590339 | 0.6130195217702804 | 8 |
| sharpe | 0.2771542548171937 | 0.2785580942071443 | 0.15439503079711975 | 0.37941753734026207 | 8 |
| slippage | 2851.8639444309792 | 2832.346766349415 | 2123.0916355749896 | 3462.6804309018253 | 8 |
| trade_count | 929.5 | 932.801375 | 763.3468750000001 | 1103.8875 | 8 |
| win_rate | 0.3149938303694375 | 0.31510196214772884 | 0.2955022468779247 | 0.3339298478391354 | 8 |

## Missing / Queued Inputs

- Metrics skipped: `[]`
- Per-trade Monte Carlo: `QUEUE_PER_TRADE_INSTRUMENTATION`
- Parameter sensitivity: `performed`

## Boundary

- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.
- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.
- No per-trade data is fabricated.
