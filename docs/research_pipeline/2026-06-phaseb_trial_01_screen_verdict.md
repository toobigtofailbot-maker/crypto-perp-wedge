# Phase-B Trial 01 Screen Verdict

## Status / Authority Boundary

Status: `diagnostic verdict over committed canonical evidence`.

This document records the frozen operational-screen diagnostic for
`RP-7134`, the first canonical Phase-B single-slice trial result for
`STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003`.

`RP-7134` is canonical evidence. This screen verdict is a separate diagnostic
over that evidence. It is not candidate promotion, not walk-forward
authorization, not candidate registration, not ranking or recommendation, not
paper/live readiness, and not runtime authority.

No paper/live/runtime path, OMS/risk/reconciliation path, broker/exchange path,
compiler, schema, catalog, runner, `lib/`, Strategy Spec, Variant Manifest,
Sweep Plan, prior result population, trial log, or candidate registry behavior
is changed or authorized by this diagnostic.

## Evidence Inputs

- Strategy Spec: `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- Variant Manifest: `research/variant_manifests/VM-0003.variant_manifest.json`
- Sweep Plan: `research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json`
- Result Population: `research/result_populations/RP-7134.result_population.json`

Canonical evidence facts:

- Result population id: `RP-7134`
- Input identity hash:
  `sha256:9b77a2ba4b12ee11645d73357b3146903922296703eb82926d62b1d9da777794`
- Result population identity hash:
  `sha256:2be44e307726f280f62123147db92afba20c520e5f14f59b470ea52d8ba6f27e`
- Content hash:
  `sha256:9813afd65c946ceaac23804fd485b4452d2451bec31a726eb86667926741e524`
- D4A normalized SHA:
  `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation report SHA:
  `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report SHA:
  `543c944f727b2b9a7ad06742946ecefc91aa8b94723f46509e4041f622ef57ad`
- Sizing metadata:
  `dynamic_equity_target_leverage`, `target_leverage=1.0`, included in both
  input and result identity-hash scopes.

Validity classification: `valid deterministic canonical evidence`.

Dry-run and repeat scratch artifacts were byte-identical before canonical
copy. The canonical result preserves the same content, input identity, and
result identity hashes.

## Population Summary

`RP-7134` preserves the frozen `VM-0003` denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

All rows are successful runner completions. Successful means the backtests ran
to completion; it does not mean profitable, recommended, approved, ready, or
promoted.

## Frozen Screen Evaluation

Final screen verdict: `NO-GO`.

The verdict is a diagnostic over the committed evidence. It must not be baked
into the result population as a promotion or lifecycle decision.

| Rule | Verdict | Exact values |
|---|---|---|
| Denominator completeness | PASS | denominator `8`; result rows `8`; outcome count sum `8` |
| Churn | FAIL | median `trade_count=2695.5`, not `< 1212`; rows above `3506.5` are `2/8 = 25%` |
| Cost burden | PASS | median cost/equity `0.390507`, which is `<= 0.50` |
| Net performance | FAIL | median `return_pct=-0.992704`; positive return and positive Sharpe rows `0/8` |
| Drawdown | FAIL | median drawdown `0.993063`; drawdown `>= 0.95` rows `8/8` |
| Sensitivity | FAIL | core sanity pass rows `0/8`; no passing axis span |
| C3 / DSR | NOT-EVALUABLE | numeric PSR / DSR / MinTRL withheld because required inputs are absent; no fabricated DSR |

## Interpretation

`RP-7134` is valid NO-GO evidence for this exact frozen Phase-B v1
single-slice trial. The valid unfavorable result is retained as canonical
evidence under pre-registration discipline.

The frozen v1 population does not advance to walk-forward under the declared
screen. This result does not prove the broad economic idea impossible, but it
does reject this exact frozen single-slice population under the frozen
operational screen.

Do not mutate `STRAT-SPEC-0003`, `VM-0003`, or `SWEEP-PLAN-0003` in response
to this result. If a future v2 design is pursued, it requires a separate
pre-registration track with new scoped authorization.

## Boundary Summary

- Canonical evidence committed: `RP-7134`
- Screen verdict: `NO-GO`
- Walk-forward authorized: `NO`
- Candidate promotion/readiness authorized: `NO`
- Candidate registry mutation authorized: `NO`
- Paper/live/runtime authority created: `NO`
- OMS/risk/reconciliation/broker/exchange authority created: `NO`
- Frozen Strategy Spec / Variant Manifest / Sweep Plan mutation authorized:
  `NO`
