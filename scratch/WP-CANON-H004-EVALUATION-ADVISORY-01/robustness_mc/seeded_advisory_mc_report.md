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
Output checksum: `sha256:e9d9547235a1a901b501df441b10a408ec4ce05c2c7189065b0015a21da92341`

## Fixture

- Result Population: `RP-0007`
- Path: `research/result_populations/RP-0007.result_population.json`
- Checksum: `sha256:ff1104cebcb2775f3f64d2e5bec72b3aaaeeb4187740978e79a26a4819ee2308`
- Rows used: `81`
- Row filter: `attempted_true_and_outcome_category_successful`
- Variant Manifest: `VM-0007`
- Sweep Plan: `SWEEP-PLAN-0007`
- Fixture validation: `passed`

## Bootstrap Confidence Intervals

| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |
|---|---:|---:|---:|---:|---:|
| drawdown | 0.787851493868377 | 0.7875492492901403 | 0.755796531046143 | 0.820938024351035 | 81 |
| exposure | 1.0 | 1.0 | 1.0 | 1.0 | 81 |
| fees | 3510.123016706466 | 3508.206273211823 | 2979.5496814141566 | 4045.3149202817176 | 81 |
| funding | 12960.08287255466 | 12960.17543651805 | 11766.681611884522 | 14162.023911522085 | 81 |
| pnl | 43036.80346834689 | 42986.69433775243 | 34892.1209329424 | 51282.61245385194 | 81 |
| return_pct | 4.303680346834686 | 4.307558677976175 | 3.4787575939577016 | 5.125361475213646 | 81 |
| sharpe | 0.3715442667932788 | 0.369058814297004 | 0.23156430099939462 | 0.5119911451805494 | 81 |
| slippage | 877.5307541766165 | 879.1569567342891 | 751.043353782507 | 1007.5233910308621 | 81 |
| trade_count | 60.333333333333336 | 60.268987654320966 | 51.690123456790126 | 68.23641975308642 | 81 |
| win_rate | 0.31579766779577695 | 0.3157891404405074 | 0.31278678724416015 | 0.3189068296866663 | 81 |

## Missing / Queued Inputs

- Metrics skipped: `[]`
- Per-trade Monte Carlo: `QUEUE_PER_TRADE_INSTRUMENTATION`
- Parameter sensitivity: `performed`

## Boundary

- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.
- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.
- No per-trade data is fabricated.
