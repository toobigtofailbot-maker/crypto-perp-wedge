# EXT-ROBUSTNESS-MC-PILOT-01 Scratch Robustness Report

- NON-CANONICAL ROBUSTNESS / MONTE CARLO PILOT OUTPUT
- NOT A RESULT POPULATION
- NOT SCREEN-GATE AUTHORITY
- NOT STRATEGY / VM / SWEEP AUTHORITY
- NOT CANDIDATE EVIDENCE AUTHORITY
- NOT PROMOTION / READINESS AUTHORITY
- NOT PAPER / LIVE / RUNTIME AUTHORITY
- PER-TRADE MONTE CARLO USES ONLY REAL PER-TRADE DATA IF AVAILABLE
- MISSING PER-TRADE DATA MUST BE REPORTED, NOT FABRICATED

Recommendation: `ADOPT_AS_ROBUSTNESS_LAYER`
Seed: `20260618`
Bootstrap samples: `1000`
Confidence level: `0.95`
Output checksum: `sha256:5c08c31bdf5130c75be573923b3280a1e60e947a6bef2d13fdbdb21adfdfef30`

## Fixture

- Result Population: `RP-2592`
- Path: `research/result_populations/RP-2592.result_population.json`
- Checksum: `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
- Rows used: `8`
- VM: `VM-0004`
- Sweep: `SWEEP-PLAN-0004`

## Bootstrap Confidence Intervals

| metric | observed mean | bootstrap mean | ci lower | ci upper | rows |
|---|---:|---:|---:|---:|---:|
| drawdown | 0.6396255106984028 | 0.6391246618226054 | 0.6039042267534553 | 0.671806351909639 | 8 |
| fees | 11407.455777723917 | 11341.457581133773 | 8472.263352262817 | 13851.81356496969 | 8 |
| funding | 0.0 | 0.0 | 0.0 | 0.0 | 8 |
| return_pct | 0.29981331782578785 | 0.2966269031242293 | -0.035842344218068714 | 0.6201552575064193 | 8 |
| sharpe | 0.2771542548171937 | 0.27668639138759676 | 0.1584772859891341 | 0.3728077602107834 | 8 |
| slippage | 2851.8639444309792 | 2841.7657400334856 | 2172.8725960581924 | 3509.662961568191 | 8 |
| trade_count | 929.5 | 928.643 | 753.871875 | 1110.403125 | 8 |
| win_rate | 0.3149938303694375 | 0.31468887049857464 | 0.293201763495469 | 0.3341329677729225 | 8 |

## Missing / Skipped Inputs

- Metrics skipped: `[]`
- Trade-order resampling: `PER_TRADE_DATA_MISSING`
- Parameter sensitivity: `performed`
- Empyrical: `unavailable`
- Jesse concept inspection: `not_inspected`

## Boundary

- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, runner, backtester, runtime, paper, or live artifact is written.
- This report is advisory only and creates no screen-gate, promotion, readiness, ranking, or candidate-evidence authority.
