# Second Path B Candidate-Selection Design

## 1. Scope

WP-S2c-139 / WP-12fr is a Tier 1 documentation-only candidate-surface
selection package. It selects one design-only second Path B candidate surface
under locked Option B.

This package creates only this document and updates `docs/project_status.md`.
It creates no candidate registration, no hypothesis pre-registration, no
candidate ID assignment for execution, and no evidence.

## 2. Authorization basis

WP-S2c-138 opened the second Path B tranche and authorized WP-S2c-139 to select
a specific second Path B candidate surface. The active package instruction also
records Main's Strategy Research Lab pivot: Track 3 pauses after WP-S2c-139
merge, and WP-S2c-140 onward is deferred, not rescinded.

This design record may be reused later only after refreshed-main preflight,
direct repo-truth inspection, and explicit Main reactivation of Track 3.

## 3. Repo-truth basis

Direct inspection confirms:

- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/outputs/Q01.json`
  records eleven `CONCLUDED` / `NO-GO` / `baseline_tested` candidates:
  H-001 through H-010 plus H-012.
- Q01 and `research/candidate_registry.jsonl` record H-011 as `DRAFT` /
  `PENDING` / `reserved`, with `strategy_family=cross_asset_regime`,
  `timeframe=weekly`, `information_inputs=[]`, and no trial IDs.
- H-012 is `CONCLUDED` / `NO-GO` / `baseline_tested` with
  `strategy_family=trend_following`, `timeframe=15m`,
  `information_inputs=["ohlcv_15m", "funding_8h"]`, and
  `free_parameter_count=3`.
- The committed third brief records H-012 liquidation to zero equity, OOS
  Sharpe `-0.8317508855081367`, max drawdown `1.0`, final equity `0.0`, 160
  trades, and 1 of 8 D2-006 gates passed.
- Q05 records current strategy-family/timeframe coverage, including H-012 as
  the only `trend_following` / `15m` row and H-011 as the only
  `cross_asset_regime` / `weekly` non-concluded row.
- Q06 records `funding_8h` on six candidates including H-012, `ohlcv_15m` only
  on H-012, and mark/index/premium inputs only on H-010/H-008 labels returned
  by the current candidate corpus.
- `research/timeframe_status.md` records `15m` as `PLANNING`; `30m`, `1h`,
  `4h`, and `1d` are in Cold Storage.
- `docs/data_catalog.md` records 15m mark price, index price, and premium
  index full-history Parquet datasets.

## 4. Track 3 pause posture

Track 3 pauses after WP-S2c-139 merges. Do not draft WP-S2c-140
automatically.

WP-S2c-140 through WP-S2c-145 are deferred, not rescinded. The next main
project direction after this merge is the Strategy Research Lab tranche, unless
Main later explicitly reactivates Track 3.

## 5. Candidate surface selection

Selected design-only surface:

| Field | Selected value |
|---|---|
| Provisional candidate name | `15m-basis-premium-dislocation-mean-reversion` |
| `strategy_family` | `basis_mean_reversion` |
| Primary timeframe | `15m` |
| `information_inputs` | `["mark_price_15m", "index_price_15m", "premium_index_15m"]` |
| `direction_profile` | `long_flat_short` |
| Proposed economic edge | Fade short-horizon mark/index and premium-index dislocations when the perp price appears stretched versus index reference rather than joining trend continuation. |

Entry/exit concept: compute a 15m premium/basis dislocation measure from
mark-price, index-price, and premium-index bars. Enter short when positive
dislocation exceeds a high threshold and begins to mean revert; enter long when
negative dislocation exceeds the symmetric threshold and begins to mean revert.
Exit to flat when dislocation normalizes, a maximum hold is reached, or a
cooldown/risk condition applies.

Risk-control concept: no pyramiding, flat default, fixed notional in any future
research test, maximum hold bars, cooldown after exit, and no trading through
known unrepaired data gaps. These are design concepts only and do not authorize
implementation.

## 6. Material differentiation from H-012

H-012 surface:

- timeframe: `15m`;
- strategy_family: `trend_following`;
- information_inputs: `["ohlcv_15m", "funding_8h"]`;
- expected turnover: trend-breakout entries with funding filter, 160 trades in
  committed baseline evidence;
- cost/liquidation posture: liquidated to zero equity, negative OOS Sharpe,
  100% max drawdown, and 1/8 D2-006 gates.

Selected surface:

- timeframe: `15m`;
- strategy_family: `basis_mean_reversion`;
- information_inputs: `["mark_price_15m", "index_price_15m",
  "premium_index_15m"]`;
- expected turnover: lower than a generic 15m continuation strategy because
  entries require an extreme dislocation plus normalization trigger;
- cost/liquidation posture: designed to reduce continuous trend exposure and
  avoid H-012's trend-continuation liquidation path, while still carrying
  intraday cost risk.

The selected surface differs from H-012 by strategy family and information
input combination. It is not an H-012 parameter variant.

## 7. Locked compatibility check

Candidate-registry schema compatibility: direct inspection of
`research/schemas/candidate_registry.schema.json` shows `strategy_family`,
`timeframe`, and `information_inputs` are string fields without closed enums;
`direction_profile` accepts `long_flat_short`; `free_parameter_count` accepts a
non-negative integer. The selected surface is compatible with the schema if a
future package registers it, but this package creates no registry row.

Timeframe compatibility: `15m` exists in `research/timeframe_status.md` and is
`PLANNING`, not Cold Storage.

Data-catalog compatibility: `docs/data_catalog.md` contains:

- `data/processed/binance_um_perp_BTCUSDT_mark_price_15m_2019-12-23_2026-04-11_2026-04-12T2316Z.parquet`;
- `data/processed/binance_um_perp_BTCUSDT_index_price_15m_2019-12-23_2026-04-11_2026-04-13T0010Z.parquet`;
- `data/processed/binance_um_perp_BTCUSDT_premium_index_15m_2019-12-24_2026-04-11_2026-04-13T0107Z.parquet`.

The labels `mark_price_15m`, `index_price_15m`, and `premium_index_15m` follow
the existing registry/data-catalog stream-plus-timeframe convention already
used by H-010 at `4h`, applied to cataloged 15m streams. No taxonomy,
timeframe_status, data-catalog, schema, validator, query-view, tool, code,
test, runtime, or protected-path change is needed.

The selected surface does not use C/F framing and does not reopen rejected
A/D/E routes.

## 8. Economic rationale

Perpetual futures can temporarily diverge from index reference pricing when
leverage demand, liquidation pressure, and short-horizon order imbalance push
the mark/premium complex away from fair-value reference. A mean-reversion
design that acts only on large dislocations tests whether those short-horizon
stretches normalize often enough to cover modeled costs.

This is materially different from H-012. H-012 joined 15m trend continuation
using OHLCV and funding context. The selected surface instead fades
cross-stream dislocation using mark/index/premium data and explicitly avoids
being a funding-filtered trend variant.

The rationale is falsifiable: if dislocations do not normalize reliably, if
cost drag consumes gross PnL, or if drawdowns remain liquidation-like, the
surface fails under future D2-006 criteria. It does not rely on trying many
parameters until something works.

## 9. Testable predictions

1. Trade frequency should be lower than H-012 because entries require
   thresholded dislocation rather than every qualifying trend continuation.
2. Cost drag as a share of gross PnL should be lower than a high-turnover 15m
   trend continuation design if the threshold/cooldown concepts work; if gross
   PnL is non-positive, the cost-drag ratio is semantically caveated.
3. Max drawdown and liquidation behavior should improve versus H-012 if
   exposure is shorter, flat default is enforced, and maximum hold bars prevent
   trend-fade persistence.
4. Parameter perturbation should be fragile if the edge is an artifact of a
   narrow premium threshold; a robust surface should keep sensitivity min ratio
   >= 0.70 under future D2-006 semantics.
5. Walk-forward efficiency should be strongest in high-dislocation regimes and
   weaker in calm regimes; failure to preserve OOS/IS efficiency > 0.5 would
   falsify the design.

## 10. Proposed success / failure criteria

These are future execution criteria only. They do not create readiness,
transition, approval, or execution authority.

Future registration/execution packages must preserve D2-006 gates without
modifying them:

- OOS Sharpe >= 1.0;
- DSR > 0.95 under repo evaluator semantics;
- max drawdown <= 20%;
- sensitivity min ratio >= 0.70;
- cost drag <= 50% of gross PnL, with the repo's non-positive-gross-PnL caveat;
- no single 90-day window > 60% of total PnL;
- <= 5 free parameters;
- walk-forward efficiency > 0.5.

Failure criteria include negative OOS Sharpe, liquidation or 100% drawdown,
cost drag structurally above threshold when gross PnL is positive, sensitivity
collapse below 0.70, or concentrated PnL that violates the 90-day rule.

## 11. Expected free-parameter count

Expected free-parameter count: 5 maximum.

Proposed free parameters:

- dislocation lookback bars;
- entry z-score or percentile threshold;
- exit normalization threshold;
- maximum hold bars;
- cooldown bars after exit.

No parameter grid is created here. If a future registration package cannot keep
the design at <= 5 free parameters, it must simplify or stop.

## 12. Estimated trial budget

Estimated future budget for a single baseline plus sensitivity package: 11
logged trials maximum.

Bounded sketch:

- one primary baseline run;
- two one-at-a-time perturbations for each of five free parameters, if all five
  are retained;
- no variant sweep;
- no extra timeframe sweep.

This estimate is for future trial-log accounting and DSR discipline only. It
does not authorize execution.

## 13. Candidate-ID posture

H-011 is preserved as a reserved `cross_asset_regime` / `weekly` slot. A future
WP-S2c-140 registration, if Main later reactivates Track 3, would use the
next-available slot, likely H-013, subject to direct registry inspection at
that time.

This document does not assign H-013 or any other ID as execution truth and
creates no registry row.

## 14. Why not the nearest alternatives

H-012 clone: rejected because repeating `trend_following` / `15m` /
`["ohlcv_15m", "funding_8h"]` would be a parameter variant of a concluded
NO-GO surface.

H-011 cross-asset/weekly direction: rejected because H-011 is preserved as a
reserved historical slot, weekly is outside the locked Phase 2 timeframe set,
and cross-asset/gold data procurement is not authorized.

High-turnover 15m continuation: rejected because H-012 already exposed cost and
liquidation weakness in a 15m continuation-like design. The selected surface
instead requires extreme dislocation and flat default behavior.

4h basis/premium clone: rejected because H-010 already tested a 4h
`basis_mean_reversion` surface and 4h is in Cold Storage. The selected design
uses the same broad family but a materially different 15m dislocation surface
inside current `15m` PLANNING status.

## 15. Forbidden interpretations

This is not candidate registration. This is not hypothesis pre-registration.
This is not evidence. This is not a recommendation to trade.

This is not readiness, transition, ranking, scoring, promotion, approval,
Path B continuation/termination authority, or human-gate execution.

This does not reopen C/F or A/D/E. This does not authorize WP-S2c-140.

## 16. Stop conditions for any future registration package

Stop if future repo truth changes materially before registration.

Stop if the selected surface requires taxonomy, timeframe_status,
data-catalog, schema, validator, query-view, tool, code, test, runtime, or
protected-path modifications.

Stop if H-011 status changes and candidate-ID sequencing changes.

Stop if Main's lab pivot supersedes manual registration.

Stop if the candidate would require new data procurement, Tier 4 contact,
runtime/protected-path contact, paper/live bridge, monitoring/dashboard, AUTO
bridge, or A2C-003 contact.

## 17. Non-authority boundary

No runtime, protected-path, Tier 4, paper, live, broker, exchange, order API,
monitoring/dashboard, paper bridge, AUTO bridge, A2C-003, or human-gate
execution authority is created.

No D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, permanent human gate, or
protected runtime boundary is modified.

## 18. Next-package posture

After merge, Track 3 pauses. Do not draft WP-S2c-140 automatically.

The next recommended package is Strategy Research Lab tranche WP-S2c-146 unless
Main directs otherwise. WP-S2c-140 onward remains deferred and may resume only
under future Main direction after refreshed-main preflight and direct repo-truth
inspection.
