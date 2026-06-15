# Phase-B Momentum Trial 0004 RP-2592 Screen Verdict

## Status / Authority Boundary

Status: `diagnostic verdict over committed canonical evidence`.

This document records the frozen operational-screen diagnostic for `RP-2592`,
the canonical Phase-B momentum single-slice result for `STRAT-SPEC-0004` /
`VM-0004` / `SWEEP-PLAN-0004`.

`RP-2592` is canonical evidence. This screen verdict is a separate diagnostic
over that evidence. It is not candidate promotion, not walk-forward
authorization, not candidate registration, not ranking or recommendation, not
paper/live readiness, and not runtime authority.

The result is valid and committed regardless of the unfavorable `NO-GO`
diagnostic verdict. The verdict must not be baked into the result population as
a promotion, lifecycle, readiness, or runtime decision.

No paper/live/runtime path, OMS/risk/reconciliation path, broker/exchange path,
compiler, schema, catalog, runner, `lib/`, Strategy Spec, Variant Manifest,
Sweep Plan, prior result population, trial log, or candidate registry behavior
is changed or authorized by this diagnostic.

## Evidence Inputs

- Strategy Spec: `research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json`
- Variant Manifest: `research/variant_manifests/VM-0004.variant_manifest.json`
- Sweep Plan: `research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json`
- Result Population: `research/result_populations/RP-2592.result_population.json`

Canonical evidence facts:

- Result population id: `RP-2592`
- Input identity hash:
  `sha256:d6df0801bdff4cd3b63e747677c0bd458ec65c7fbd9ce45dcf363bddcb739080`
- Result population identity hash:
  `sha256:c146d7880687f363ab2fa258a3b205b63f6ce45ba88c7641d63636186656a0e7`
- Content hash:
  `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
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

Dry-run and repeat scratch artifacts were byte-identical before canonical copy.
The canonical result preserves the same content, input identity, and result
identity hashes.

## Population Summary

`RP-2592` preserves the frozen `VM-0004` denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

All rows are successful runner completions. Successful means the backtests ran
to completion; it does not mean profitable, recommended, approved, ready, or
promoted.

## Per-Variant Surface

| Variant | fast | slow | trend | return_pct | drawdown | win_rate | sharpe | trades | fees | slippage | funding |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VAR-000001 | 20 | 100 | 300 | -0.429746 | 0.712333 | 0.304006 | -0.019888 | 1273 | 7954.73 | 1988.68 | 0 |
| VAR-000002 | 20 | 100 | 400 | 0.169923 | 0.628921 | 0.308462 | 0.266760 | 1300 | 14164.01 | 3541.00 | 0 |
| VAR-000003 | 20 | 200 | 300 | 0.483694 | 0.692489 | 0.278729 | 0.358209 | 818 | 14054.28 | 3513.57 | 0 |
| VAR-000004 | 20 | 200 | 400 | 0.644372 | 0.565444 | 0.270000 | 0.397940 | 800 | 13729.89 | 3432.47 | 0 |
| VAR-000005 | 50 | 100 | 300 | 0.811322 | 0.657392 | 0.333659 | 0.435555 | 1025 | 12900.23 | 3225.06 | 0 |
| VAR-000006 | 50 | 100 | 400 | 0.954728 | 0.614364 | 0.327255 | 0.464502 | 1042 | 16776.41 | 4194.10 | 0 |
| VAR-000007 | 50 | 200 | 300 | -0.179286 | 0.675760 | 0.347754 | 0.134306 | 601 | 5604.61 | 1401.15 | 0 |
| VAR-000008 | 50 | 200 | 400 | -0.056500 | 0.570302 | 0.350087 | 0.179851 | 577 | 6075.48 | 1518.87 | 0 |

## Frozen Screen Evaluation

Final screen verdict: `NO-GO`.

The verdict is a diagnostic over the committed evidence. It must not be baked
into the result population as a promotion or lifecycle decision.

| Rule | Verdict | Exact values |
|---|---|---|
| Denominator completeness | PASS | denominator `8`; result rows `8`; outcome count sum `8` |
| Churn | PASS | median `trade_count=921.5`; max `1300`; min `577` |
| Cost burden | FAIL | median cost/equity `1.6644`; max cost/equity `2.0971` |
| Net performance | PASS | median `return_pct=0.3268`; positive return rows `5/8`; positive Sharpe rows `7/8` |
| Drawdown | FAIL | median drawdown `0.6432`; max drawdown `0.7123` |
| Sensitivity | PASS | positive rows span both fast and slow axes; trend-bucket medians: `300=0.1522`, `400=0.4071` |
| C3 / DSR | NOT-EVALUABLE | numeric PSR / DSR / MinTRL withheld because required inputs are absent; no fabricated DSR |

## Interpretation

`RP-2592` is valid `NO-GO` evidence for this exact frozen Phase-B momentum
single-slice trial. The valid unfavorable result is retained as canonical
evidence under pre-registration discipline.

The frozen momentum population does not advance to walk-forward under the
declared screen. This result does not prove the broad economic idea impossible,
but it does reject this exact frozen single-slice population under the frozen
operational screen.

Do not mutate `STRAT-SPEC-0004`, `VM-0004`, or `SWEEP-PLAN-0004` in response to
this result. If a future design is pursued, it requires a separate
pre-registration track with new scoped authorization.

## Boundary Summary

- Canonical evidence committed: `RP-2592`
- Screen verdict: `NO-GO`
- Walk-forward authorized: `NO`
- Candidate promotion/readiness authorized: `NO`
- Candidate registry mutation authorized: `NO`
- Paper/live/runtime authority created: `NO`
- OMS/risk/reconciliation/broker/exchange authority created: `NO`
- Frozen Strategy Spec / Variant Manifest / Sweep Plan mutation authorized:
  `NO`
