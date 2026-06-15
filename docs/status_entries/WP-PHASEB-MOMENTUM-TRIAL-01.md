# WP-PHASEB-MOMENTUM-TRIAL-01 Branch State

- Package: `WP-PHASEB-MOMENTUM-TRIAL-01`.
- Branch: `trial/phaseb-momentum-0004-dryrun-surface`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-MOMENTUM-TRIAL-01`.
- Base: `origin/main` after PR #475 / `1da7489`.
- Package class: Karl-gated canonical result-population write after
  deterministic dry-run review.
- Status: canonical evidence committed; screen verdict diagnostic recorded.

## Scope Summary

This package commits the valid deterministic Phase-B momentum single-slice
canonical trial result for the frozen preregistration set:

- `STRAT-SPEC-0004`
- `VM-0004`
- `SWEEP-PLAN-0004`

The canonical result population is:

- `research/result_populations/RP-2592.result_population.json`

The separate operational-screen diagnostic is:

- `docs/research_pipeline/2026-06-phaseb_momentum_trial_0004_rp2592_screen.md`

The screen diagnostic records `NO-GO` under the frozen momentum
GO-to-walk-forward screen. The result population remains evidence; the screen
verdict is not encoded as candidate promotion, readiness, ranking,
recommendation, lifecycle transition, walk-forward authorization, paper/live
authority, or runtime authority.

## Determinism And Identity

Karl authorized canonical commit after reviewing the dry-run surface.

The long-budget dry-run and repeat scratch artifacts completed successfully
and matched byte-for-byte before canonical copy.

Canonical identity facts:

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
- Structured sizing metadata: present and included in both identity-hash
  scopes.

## Population And Screen

`RP-2592` preserves the frozen denominator:

- Committed denominator: `8`
- Result row count: `8`
- Outcome count sum: `8`
- Outcome counts: `successful=8`; all other outcome categories `0`
- Denominator reconciliation: `PASS`

Frozen-screen diagnostic:

- Denominator completeness: `PASS`
- Churn: `PASS`
- Cost burden: `FAIL`
- Net performance: `PASS`
- Drawdown: `FAIL`
- Sensitivity: `PASS`
- C3 / DSR: `NOT-EVALUABLE`
- Final screen verdict: `NO-GO`

Exact screen values are recorded in
`docs/research_pipeline/2026-06-phaseb_momentum_trial_0004_rp2592_screen.md`.

## Validation

Validation scope for this package:

- Dry-run and repeat scratch files matched by content hash.
- Canonical `RP-2592` content hash matched the dry-run artifact.
- Result-population validator passed for the committed corpus.
- Result-population validator passed for scratch `RP-2592` before canonical
  copy.
- Strategy Spec, Variant Manifest, Sweep Plan, and indicator catalog validators
  passed.
- Query-layer view listing passed.
- Query tests and full pytest passed.
- Integrity views were clean.
- Diff scope passed with the explicit authorized canonical result-population
  write flag.

## Boundary Summary

- Canonical result population written: `YES`, `RP-2592`.
- Prior result populations changed: `NO`.
- `STRAT-SPEC-0004` changed: `NO`.
- `VM-0004` changed: `NO`.
- `SWEEP-PLAN-0004` changed: `NO`.
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

The Phase-B momentum single-slice trial is complete and `NO-GO` under the
frozen screen. Walk-forward is not authorized by this result.

Any future design requires a separate preregistration track and separate
authorization. The frozen 0004 artifacts and `RP-2592` evidence should remain
append-only.
