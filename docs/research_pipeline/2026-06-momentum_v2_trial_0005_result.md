# Momentum v2 Trial 0005 RP-3731 Screen Verdict

## Status / Authority Boundary

Status: `diagnostic verdict over committed canonical evidence`.

This document records the frozen operational-screen diagnostic for `RP-3731`,
the canonical momentum v2 single-slice result for `STRAT-SPEC-0005` /
`VM-0005` / `SWEEP-PLAN-0005`.

`RP-3731` is canonical evidence. This screen verdict is a separate diagnostic
over that evidence. It is not candidate promotion, not walk-forward
authorization, not candidate registration, not ranking or recommendation, not
paper/live readiness, and not runtime, capital, or recommendation authority.

The valid unfavorable result is committed as evidence. No result is withheld
because it is unfavorable, and the frozen-screen verdict remains `NO-GO`.

No paper/live/runtime path, OMS/risk/reconciliation path, broker/exchange path,
compiler, schema, catalog, runner, `lib/`, Strategy Spec, Variant Manifest,
Sweep Plan, prior result population, trial log, or candidate registry behavior
is changed or authorized by this diagnostic.

## Identity And Provenance

- Result population id: `RP-3731`
- Input identity hash:
  `sha256:9f28ec89a08dcacebe22e7de68c3b5be72af312cf1f060b74bdde41e85881051`
- Result population identity hash:
  `sha256:8e5f1381a860284ffa6ceb9f496fdf2d9ee127541a02e3a97abb013ba68e5aa1`
- Source scratch file hash:
  `e8d6bc5c48a80c32f9495a0d63d05be0cf8513b8f3912d6b81c6dbca715672c2`
- Source scratch path:
  `C:\GitHub\crypto-perp-wedge-WP-MOMENTUM-V2-TRIAL-01-scratch\run1\RP-3731.result_population.json`
- Canonical evidence path:
  `research/result_populations/RP-3731.result_population.json`
- Data path used:
  `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- Data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Runner posture: `--canonical-15m`,
  `--sizing-mode dynamic_equity_target_leverage`, `--target-leverage 1.0`,
  `--max-workers 4`

## Frozen Artifacts

- Strategy Spec: `STRAT-SPEC-0005`
- Strategy Spec hash:
  `sha256:9a20e64f83e6cbe2360e3be715ad273f2c851aacb6da99fa27d802ee29588141`
- Variant Manifest: `VM-0005`
- Variant Manifest hash:
  `sha256:db901fa9e3fcf6c0aac6905f175afb2eab3283d1cc8c41d6f8ee28f9887971c1`
- Sweep Plan: `SWEEP-PLAN-0005`
- Sweep Plan identity hash:
  `sha256:e985f0da214aa93dbe341258e874eabf218298f4219da67c851ab81784682a12`
- Denominator: `8`
- ATR literals:
  - `atr_lookback=14`
  - `atr_multiplier=3.0`
  - `entry_reference_price=next_bar_open_pre_fee_slippage`
  - `evaluation_price=close`
  - `evaluation_timing=bar_close`

## Determinism

- Run 1 elapsed: `517.2s`
- Run 2 elapsed: `517.9s`
- Byte-identical repeat: `YES`
- Same input/result identities: `YES`

The canonical result preserves the same content, input identity, and result
identity hashes as the reviewed deterministic scratch artifact.

## Population Summary

`RP-3731` preserves the frozen `VM-0005` denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

All rows are successful runner completions. Successful means the backtests ran
to completion; it does not mean profitable, recommended, approved, ready, or
promoted.

## Cost Computability

`cost_to_gross_pnl` is computable for all rows from committed RP fields.

Fields:

- `metrics.pnl`
- `metrics.fees`
- `metrics.slippage`
- `metrics.funding`

Formula:

- `total_cost = fees + slippage + funding`
- `gross_pnl = pnl + total_cost`
- `cost_to_gross_pnl = total_cost / gross_pnl`

All rows have positive gross PnL. The funding field is present and `0.0` in all
rows because the current D4 OHLCV path supplies no funding.

## Per-Variant Surface

| Variant | Params fast/slow/trend | Return | Sharpe | Drawdown | Trades | Cost/Gross |
|---|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20/100/300 | -10.19% | 0.166 | 60.93% | 1442 | 1.061 |
| VAR-000002 | 20/100/400 | 6.77% | 0.232 | 61.26% | 1443 | 0.965 |
| VAR-000003 | 20/200/300 | 68.88% | 0.409 | 57.15% | 1008 | 0.742 |
| VAR-000004 | 20/200/400 | 105.24% | 0.482 | 50.84% | 959 | 0.683 |
| VAR-000005 | 50/100/300 | 163.89% | 0.577 | 49.09% | 1264 | 0.685 |
| VAR-000006 | 50/100/400 | 125.40% | 0.518 | 58.48% | 1239 | 0.724 |
| VAR-000007 | 50/200/300 | -46.21% | -0.035 | 67.79% | 819 | 2.864 |
| VAR-000008 | 50/200/400 | -53.97% | -0.116 | 72.21% | 773 | 5.443 |

## Frozen Screen Evaluation

Final screen verdict: `NO-GO`.

The verdict is a diagnostic over the committed evidence. It must not be baked
into the result population as a promotion or lifecycle decision.

| Rule | Verdict | Exact values |
|---|---|---|
| Denominator completeness | PASS | denominator `8`; result rows `8`; outcome count sum `8` |
| Net performance | PASS | median return `37.83%`; positive return rows `5/8`; positive Sharpe rows `6/8` |
| Drawdown | FAIL | median drawdown `59.70%`, above `<=45%` gate; max drawdown `72.21%`, not `<60%`; no row hit automatic `>=75%` NO-GO rule |
| Cost | FAIL | median cost/gross `0.853`, above `<=0.55` gate |
| Churn | PASS | median trades `1123.5`; max trades `1443` |
| Sensitivity | PASS | positive rows span more than one bucket on all three axes |
| DSR / PSR / MinTRL | NOT-EVALUABLE | required inputs are absent from available RP fields; no fabricated DSR, PSR, or MinTRL |

## Interpretation

`RP-3731` is valid `NO-GO` evidence for this exact frozen momentum v2
single-slice trial. The valid unfavorable result is retained as canonical
evidence under pre-registration discipline.

The frozen momentum v2 population does not advance to walk-forward under the
declared screen. This result does not prove the broad economic idea impossible,
but it does reject this exact frozen single-slice population under the frozen
operational screen.

Do not mutate `STRAT-SPEC-0005`, `VM-0005`, or `SWEEP-PLAN-0005` in response to
this result. Any future v3, 4h, ATR-parameter, candidate, or walk-forward work
requires a separate preregistration track and separate authorization.

## Boundary Summary

- Canonical evidence committed: `RP-3731`
- Valid unfavorable evidence committed: `YES`
- Result withheld because unfavorable: `NO`
- Screen verdict: `NO-GO`
- Walk-forward authorized: `NO`
- Candidate created or registered: `NO`
- Candidate promotion/readiness authorized: `NO`
- Candidate ranking or recommendation authorized: `NO`
- Paper/live/runtime authority created: `NO`
- Runtime or capital authority created: `NO`
- OMS/risk/reconciliation/broker/exchange authority created: `NO`
- Frozen Strategy Spec / Variant Manifest / Sweep Plan mutation authorized:
  `NO`
