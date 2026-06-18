# EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01 Scratch Report

- NON-CANONICAL EXTERNAL SIDECAR OUTPUT
- NOT A RESULT POPULATION
- NOT STRATEGY AUTHORITY
- NOT VM/SWEEP AUTHORITY
- NOT CANDIDATE EVIDENCE
- NOT PAPER/LIVE/RUNTIME AUTHORITY

Recommendation: `EXPLORATION_ONLY`
Determinism match: `True`
Vectorbt wall-clock seconds: `37.476852`
Repo runner wall-clock seconds: `222.926646`
Speed ratio vectorbt/repo: `0.1681129335108992`

## Fixture

- Strategy: `STRAT-SPEC-0004`
- VM: `VM-0004`
- Sweep: `SWEEP-PLAN-0004`
- RP comparator: `RP-2592`
- Data slice: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`

## Variant Deltas

| variant | repo trades | vectorbt trades | return delta | drawdown delta | sharpe delta | status |
|---|---:|---:|---:|---:|---:|---|
| VAR-000001 | 1273 | 1274 | 9.209162017115302e-05 | -0.00012399980727384463 | -9.437933287172184e-05 | explained_difference |
| VAR-000002 | 1300 | 1301 | -0.00011688714146129708 | -0.00016387756273616993 | -9.349727803592556e-05 | explained_difference |
| VAR-000003 | 818 | 819 | -0.00022910668615716556 | -0.00013198415699033905 | -7.970318996741721e-05 | explained_difference |
| VAR-000004 | 800 | 801 | -0.00036721954653839983 | -0.00013696210845282053 | -9.107787807544065e-05 | explained_difference |
| VAR-000005 | 1025 | 1026 | -0.0005303951758597325 | -0.00015300876696966448 | -0.00010377887057294588 | explained_difference |
| VAR-000006 | 1042 | 1043 | -0.0005476804238186972 | -0.0001549215749386823 | -8.86965720968691e-05 | explained_difference |
| VAR-000007 | 601 | 602 | 8.409392288558082e-05 | -0.00015615427154669348 | -6.933977384473988e-05 | explained_difference |
| VAR-000008 | 577 | 578 | -8.424212936189446e-06 | -0.00012626300933249457 | -8.861664425097171e-05 | explained_difference |

## Notes

- Differences are expected unless explicitly marked matched.
- This sidecar uses repo compiler signals, but vectorbt accounting is not the canonical repo backtester.
- No canonical Result Population is written by this report.
