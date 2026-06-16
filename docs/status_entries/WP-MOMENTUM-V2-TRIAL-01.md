# WP-MOMENTUM-V2-TRIAL-01 Branch State

- Package: `WP-MOMENTUM-V2-TRIAL-01`.
- Commit phase package: `WP-MOMENTUM-V2-TRIAL-01-COMMIT`.
- Branch: `trial/momentum-v2-0005-commit-rp3731`.
- Worktree:
  `C:\GitHub\crypto-perp-wedge-WP-MOMENTUM-V2-TRIAL-01-COMMIT`.
- Base: `origin/main` after PR #487 / `9c34777`.
- Package class: user-authorized canonical result-population write after
  deterministic dry-run review.
- Status: canonical evidence committed; screen verdict diagnostic recorded.

## Scope Summary

This package commits the valid deterministic momentum v2 single-slice canonical
trial result for the frozen preregistration set:

- `STRAT-SPEC-0005`
- `VM-0005`
- `SWEEP-PLAN-0005`

The canonical result population is:

- `research/result_populations/RP-3731.result_population.json`

The separate operational-screen diagnostic is:

- `docs/research_pipeline/2026-06-momentum_v2_trial_0005_result.md`

The screen diagnostic records `NO-GO` under the frozen momentum v2
GO-to-walk-forward screen. The result population remains evidence; the screen
verdict is not encoded as candidate promotion, readiness, ranking,
recommendation, lifecycle transition, walk-forward authorization, paper/live
authority, runtime authority, or capital authority.

## Determinism And Identity

The user authorized canonical commit after reviewing the deterministic RP-3731
dry-run surface.

The dry-run and repeat scratch artifacts completed successfully and matched
byte-for-byte before canonical copy.

Canonical identity facts:

- Result population id: `RP-3731`
- Input identity hash:
  `sha256:9f28ec89a08dcacebe22e7de68c3b5be72af312cf1f060b74bdde41e85881051`
- Result population identity hash:
  `sha256:8e5f1381a860284ffa6ceb9f496fdf2d9ee127541a02e3a97abb013ba68e5aa1`
- Source scratch file hash:
  `e8d6bc5c48a80c32f9495a0d63d05be0cf8513b8f3912d6b81c6dbca715672c2`
- Strategy Spec hash:
  `sha256:9a20e64f83e6cbe2360e3be715ad273f2c851aacb6da99fa27d802ee29588141`
- Variant Manifest hash:
  `sha256:db901fa9e3fcf6c0aac6905f175afb2eab3283d1cc8c41d6f8ee28f9887971c1`
- Sweep Plan identity hash:
  `sha256:e985f0da214aa93dbe341258e874eabf218298f4219da67c851ab81784682a12`
- Data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Structured sizing metadata: present and included in both identity-hash
  scopes.

## Population And Screen

`RP-3731` preserves the frozen denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

Frozen-screen diagnostic:

- Denominator completeness: `PASS`
- Net performance: `PASS`
- Drawdown: `FAIL`
- Cost: `FAIL`
- Churn: `PASS`
- Sensitivity: `PASS`
- DSR / PSR / MinTRL: `NOT-EVALUABLE`
- Final screen verdict: `NO-GO`

Exact screen values are recorded in
`docs/research_pipeline/2026-06-momentum_v2_trial_0005_result.md`.

## Validation

Validation scope for this package:

- Source scratch `RP-3731` file hash matched the surfaced dry-run hash before
  canonical copy.
- Canonical `RP-3731` content hash matched the dry-run artifact.
- Result-population validator passed for the committed corpus.
- Strategy Spec, Variant Manifest, Sweep Plan, and indicator catalog validators
  passed.
- Candidate registry and paper-state validators passed.
- Query-layer view listing passed.
- Query tests and full pytest were run.
- Integrity views were checked.
- Diff scope passed with the explicit authorized canonical result-population
  write flag.

## Boundary Summary

- Canonical result population written: `YES`, `RP-3731`.
- Prior result populations changed: `NO`.
- `STRAT-SPEC-0005` changed: `NO`.
- `VM-0005` changed: `NO`.
- `SWEEP-PLAN-0005` changed: `NO`.
- Trial log changed: `NO`.
- Candidate registry changed: `NO`.
- Compiler/schema/catalog changed: `NO`.
- `lib/` or runner changed: `NO`.
- Dashboard implementation changed: `NO`.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange, or protected
  path changed: `NO`.
- Candidate, readiness, promotion, ranking, recommendation, walk-forward,
  capital, or runtime authority created: `NO`.
- Result withheld because unfavorable: `NO`.

## Next State

The momentum v2 single-slice trial is complete and `NO-GO` under the frozen
screen. Walk-forward is not authorized by this result.

Any future design requires a separate preregistration track and separate
authorization. The frozen 0005 artifacts and `RP-3731` evidence should remain
append-only.
