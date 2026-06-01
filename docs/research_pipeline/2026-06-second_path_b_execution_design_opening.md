# Second Path B Execution Design Opening

## 1. Scope

WP-S2c-138 / WP-12fp is a Tier 1 documentation-only package. It opens the
second Path B execution tranche under locked Option B.

This package creates only this design-opening document and updates
`docs/project_status.md`.

This package does not select a candidate surface. It creates no candidate
registration, hypothesis pre-registration, EXP, REP, trial-log entry, OL, REC,
DEC, canonical artifact, code, test, schema, validator, query-view, runtime, or
protected-path change.

## 2. Authorization basis

Main 4.0 authorized WP-S2c-138 as AUTHORIZED NOW.

WP-S2c-139 is auto-draft after WP-S2c-138 merges, subject to refreshed-main
preflight and no stop trigger.

C-shape and F-shape remain deferred. A/D/E remain rejected. This package does
not reopen any rejected or deferred route.

## 3. Repo-truth basis

The third cross-candidate diagnostic brief records eleven concluded NO-GO
candidates and one H-011 reserved draft row.

H-012 is `CONCLUDED` / `NO-GO` / `baseline_tested`. H-012 used
`trend_following`, `15m`, and `["ohlcv_15m", "funding_8h"]` with free
parameter count 3.

H-012 evidence records liquidation to zero equity, negative OOS Sharpe
`-0.8317508855081367`, max drawdown `1.0`, final equity `0.0`, 160 trades, and
1 of 8 D2-006 gates passed.

H-012's REC-5 exact segment is:

`H-012 / research_oos / post_wp_5b / d2_006_gates = 1`

That exact segment is below the REC-5 floor.

Scope 6 remains zero-instance. The third brief records zero rows in Scope 6
base/link surfaces and zero Scope 6 integrity issues.

Integrity views are clean in the third brief. Q09 records 32 discovered
`v_integrity_*` views with issue count zero, including
`v_integrity_plan_report_pairs`.

## 4. H-012 lesson boundary

H-012 is negative evidence for its exact candidate surface:

`15m / trend_following / ["ohlcv_15m", "funding_8h"]`

Do not infer that all 15m designs are invalid.

Do not infer that all funding-context designs are invalid.

Do not repeat H-012's exact surface without material differentiation.

Cost and liquidation risk are design concerns for future candidate selection,
especially for fast or high-turnover designs.

## 5. Locked route and boundaries

The second tranche remains under locked Path B Option B.

Locked taxonomy discipline remains unchanged. Locked timeframe_status discipline
remains unchanged. Data-catalog discipline remains unchanged.

D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, and permanent human gates
remain unchanged and absolute.

This package creates no paper, live, runtime, broker, exchange, order API, Tier
4, or protected-path authority.

## 6. Material-differentiation requirement

WP-S2c-139 must select a candidate surface that is materially different from
H-012 by at least one of:

- different timeframe;
- different strategy_family;
- different information_inputs combination.

If a proposed candidate is effectively H-012 with superficial parameter changes,
WP-S2c-139 must stop or redesign.

If a proposed input requires taxonomy expansion or unsupported convention
application, WP-S2c-139 must stop and report.

## 7. Current coverage observations

The current strategy-family/timeframe coverage matrix in Q05 is descriptive
only. It records:

- `trend_following` coverage at `4h`, `1d`, and `15m`;
- `momentum` coverage at `1h`;
- `breakout` coverage at `30m`;
- `basis_mean_reversion` coverage at `4h`;
- `cross_asset_regime` / `weekly` as the reserved H-011 row.

The current information-input coverage in Q06 is also descriptive only. It
records:

- `funding_8h` on six candidates, including H-012;
- `ohlcv_15m` only on H-012;
- `ohlcv_4h` on four candidates;
- `ohlcv_1h` on three candidates;
- `ohlcv_1d` and `ohlcv_30m` on two candidates each;
- mark, index, and premium inputs on one candidate each for the returned labels.

These observations do not rank, score, recommend, or select a next candidate.

## 8. Under-covered surfaces for WP-S2c-139 consideration

WP-S2c-139 may consider design spaces, not preselected outcomes, including:

- a non-15m timeframe inside locked timeframe_status discipline;
- a non-`trend_following` strategy family;
- an information-input mix not identical to H-012;
- a lower-turnover design to address H-012 cost and liquidation risk;
- a candidate using locked data sources already present in `docs/data_catalog.md`.

These examples are consideration surfaces only. This package does not select
one.

## 9. Forbidden selection surfaces

WP-S2c-139 and later tranche packages must not select:

- an H-012 clone;
- any surface requiring taxonomy, timeframe_status, or data-catalog changes;
- any surface requiring Tier 4, external, protected-path, paper/live, broker,
  exchange, or order API contact;
- any C/F reopening or A/D/E route;
- multiple candidates.

Candidate ranking, scoring, recommendation, readiness, transition, promotion,
or human-gate execution language is forbidden.

## 10. Candidate-ID sequencing note

H-011 remains the reserved-slot track in current repo truth and may affect the
future candidate ID.

If H-011 is released before WP-S2c-140 preflight and registry convention
supports using it, WP-S2c-140 may use H-011.

If H-011 remains reserved or unresolved, WP-S2c-140 uses the next available
candidate ID, likely H-013.

WP-S2c-138 does not resolve H-011 and does not select a candidate ID.

## 11. WP-S2c-139 objective

WP-S2c-139 should select the specific second Path B candidate surface.

It must confirm locked taxonomy, timeframe_status, and data-catalog
compatibility by direct repo-file inspection.

It must provide economic rationale, testable predictions, success/failure
criteria, expected free-parameter count within the D2-006 cap, and an estimated
trial budget.

It must stop if the selected surface needs taxonomy, timeframe_status, or
data-catalog modifications.

## 12. WP-S2c-140+ tranche shape

The expected later tranche shape is:

- WP-S2c-140: registration and hypothesis pre-registration.
- WP-S2c-141: EXP creation.
- WP-S2c-142: backtest, trial-log entry, and REP.
- WP-S2c-143: OL and REC.
- WP-S2c-144: DEC.
- WP-S2c-145: checkpoint only after Main re-engagement post-DEC.

Each later package depends on refreshed merged repo truth and its own explicit
scope.

## 13. Validation posture

Validation profile: CS12 T1-doc-narrow.

Changed-file scope is exact:

- `docs/research_pipeline/2026-06-second_path_b_execution_design_opening.md`
- `docs/project_status.md`

Integrity views and validators should be run per repo-local doc-narrow
convention. Any non-empty integrity view, validator failure, or diff-scope
breach is a stop condition.

## 14. Stop conditions

Stop if this opening or a later draft:

- surfaces tension with WP-S2c-123 locked Option B;
- requires taxonomy, timeframe_status, or data-catalog changes;
- selects a concrete candidate surface in this package;
- uses C/F or rejected A/D/E framing;
- implies readiness, transition, recommendation, ranking, scoring, approval, or
  human-gate execution;
- requires schema, validator, query-view, tool, code, test, runtime, or
  protected-path changes;
- fails validation.

## 15. Non-authority boundary

This package selects no candidate.

This package creates no pre-registration and no evidence.

This package creates no recommendation, ranking, scoring, readiness,
transition, approval, promotion, or human-gate execution.

This package creates no runtime, protected-path, Tier 4, paper, live, broker,
exchange, order API, monitoring/dashboard, paper bridge, AUTO bridge, or
A2C-003 authority.

## 16. Next-package posture

After merge, Side may auto-draft WP-S2c-139 after refreshed-main preflight and
no stop trigger.

WP-S2c-139 remains design/selection work only. It must not register a
candidate, pre-register a hypothesis, run a backtest, create evidence artifacts,
or execute gates unless a later package explicitly authorizes those actions.
