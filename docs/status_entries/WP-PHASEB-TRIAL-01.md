# WP-PHASEB-TRIAL-01 Branch State

- Package: `WP-PHASEB-TRIAL-01`.
- Branch: `trial/phaseb-0003-dryrun-surface`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-TRIAL-01`.
- Base: `origin/main` after PR #469 / `df5c326`.
- Package class: Karl-gated canonical result-population write after
  deterministic dry-run review.
- Status: canonical evidence committed; screen verdict diagnostic recorded.

## Scope Summary

This package commits the valid deterministic Phase-B v1 single-slice canonical
trial result for the frozen preregistration set:

- `STRAT-SPEC-0003`
- `VM-0003`
- `SWEEP-PLAN-0003`

The canonical result population is:

- `research/result_populations/RP-7134.result_population.json`

The separate operational-screen diagnostic is:

- `docs/research_pipeline/2026-06-phaseb_trial_01_screen_verdict.md`

The screen diagnostic records `NO-GO` under the frozen single-slice
GO-to-walk-forward screen. The result population remains evidence; the screen
verdict is not encoded as candidate promotion, readiness, ranking,
recommendation, lifecycle transition, walk-forward authorization, paper/live
authority, or runtime authority.

## Determinism And Identity

Karl authorized canonical commit after reviewing the dry-run surface.

The long-budget dry-run and repeat scratch artifacts completed successfully
and matched byte-for-byte before canonical copy.

Canonical identity facts:

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
- Structured sizing metadata: present and included in both identity-hash
  scopes.

## Population And Screen

`RP-7134` preserves the frozen denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

Frozen-screen diagnostic:

- Denominator completeness: `PASS`
- Churn: `FAIL`
- Cost burden: `PASS`
- Net performance: `FAIL`
- Drawdown: `FAIL`
- Sensitivity: `FAIL`
- C3 / DSR: `NOT-EVALUABLE`
- Final screen verdict: `NO-GO`

Exact screen values are recorded in
`docs/research_pipeline/2026-06-phaseb_trial_01_screen_verdict.md`.

## Validation

Validation scope for this package:

- Dry-run and repeat scratch files matched by content hash.
- Canonical `RP-7134` content hash matched the dry-run artifact.
- Result-population validator passed for the committed corpus.
- Result-population validator passed for scratch `RP-7134` before canonical
  copy.
- Strategy Spec, Variant Manifest, Sweep Plan, and indicator catalog validators
  passed.
- Query-layer view listing passed.
- Diff scope showed only the expected evidence/documentation files.

## Boundary Summary

- Canonical result population written: `YES`, `RP-7134`.
- Prior result populations changed: `NO`.
- `STRAT-SPEC-0003` changed: `NO`.
- `VM-0003` changed: `NO`.
- `SWEEP-PLAN-0003` changed: `NO`.
- Trial log changed: `NO`.
- Candidate registry changed: `NO`.
- Compiler/schema/catalog changed: `NO`.
- `lib/` or runner changed: `NO`.
- Dashboard implementation changed: `NO`.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange, or protected
  path changed: `NO`.
- Candidate, readiness, promotion, ranking, recommendation, walk-forward, or
  runtime authority created: `NO`.

## Next State

The Phase-B v1 single-slice trial is complete and `NO-GO` under the frozen
screen. Walk-forward is not authorized by this result.

Any future v2 design requires a separate preregistration track and separate
authorization. The v1 frozen artifacts and `RP-7134` evidence should remain
append-only.
