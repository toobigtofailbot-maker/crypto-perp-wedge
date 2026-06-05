# First Canonical Strategy Spec Design

## 1. Scope And Non-Authority

WP-12hn / WP-S2c-193 is a Tier 1 documentation-only design and selection package for the first canonical Strategy Spec candidate.

This package selects and describes the first canonical Strategy Spec concept only. It creates no Strategy Spec JSON instance, variant manifest, sweep plan, result population, canonical evidence, runner output, schema change, validator change, query-layer change, parser/compiler change, runtime change, or paper/live/protected-path change.

This document is not approval, ranking, recommendation, readiness, transition, promotion, or gate authority. The selected design is a review input for Main before WP-S2c-194.

## 2. Repo-Truth Basis

Pre-edit repo-truth discovery confirmed:

- PR #369 / WP-12hm / WP-S2c-192 is merged.
- Refreshed `main` records the WP-S2c-192 handoff in `docs/project_status.md`.
- No open PRs existed before this branch was created.
- No existing WP-S2c-193 / WP-12hn PR existed before this branch was created.
- The active package brief authorizes WP-S2c-193 as the first canonical Strategy Spec design and selection package.
- `research/schemas/strategy_spec.schema.json` exists.
- `tools/registry/validate_strategy_specs.py` exists.
- The current Strategy Spec storage path state is absent: no `research/strategy_specs/` directory exists.
- `docs/data_catalog.md` exists and records BTCUSDT 15m full-history OHLCV data.
- `research/timeframe_status.md` exists and records `15m` as `PLANNING`.
- `1h`, `30m`, `4h`, and `1d` are in Cold Storage.
- Result-population item 5 surfaces exist: `tools/research_runner/run_offline_sweep.py`, `tools/registry/validate_result_populations.py`, `tools/research_query/query_layer.py`, and `tools/research_query/views.sql`.
- No `research/result_populations/` canonical corpus exists.
- No Main/Karl redirect for this package was present in `docs/project_status.md`.

## 3. Selected Concept

Selected concept: Dynamic Volatility Mean Reversion.

This is option #5 from the user-provided strategy list.

Plain-language design:

- compute a volatility-standardized distance between close and a rolling EMA centerline;
- enter long when price is stretched below the centerline;
- enter short when price is stretched above the centerline;
- exit when the standardized distance returns toward the centerline;
- bound risk with an ATR-based hard stop, optional maximum holding period, and optional cooldown.

Concept formula:

```text
Z = (close - EMA(close, lookback_n)) / StdDev(close, lookback_n)
```

## 4. Selection Rationale

Dynamic Volatility Mean Reversion is selected as a simple pipeline-validation baseline, not because this package claims alpha confidence.

Reasons:

- it uses standard OHLCV inputs already represented in repo data posture;
- it can be described with bounded entry, exit, and risk conditions;
- it does not require order book, liquidation, open-interest, paid, tick-level, external-network, or new catalog data;
- it keeps free parameters at or below the Strategy Spec cap of 5;
- it gives WP-S2c-194 a small, reviewable first instance target and bounded variant-manifest surface;
- it avoids cold-storage timeframe selection by using the currently PLANNING `15m` timeframe.

The economic rationale is a hypothesis only: price may mean-revert after volatility-standardized overextension from a rolling centerline. This is not evidence and does not create a recommendation.

## 5. Deferred Alternatives

Deferred for later testing, not part of WP-S2c-193:

- #2 Channels With NVI: possible later, but more indicator complexity than needed for the first canonical baseline.
- #3 Q-ORB: later candidate; requires session, VWAP, RVOL, and multi-timeframe details.
- #4 Order Book Imbalance: later candidate; requires order book / microstructure data and is not suitable for the first canonical sweep.
- #6 Liquidation Cluster Hunting: later candidate; requires liquidation/open-interest data and is not suitable for the first canonical sweep.

No files, specs, concepts, candidates, or artifacts are created for these deferred ideas.

## 6. Proposed Instrument, Timeframe, And Data

Proposed instrument: BTCUSDT Binance USDT-M perpetual.

Proposed primary timeframe: `15m`.

Data refs:

- `close` for EMA, StdDev, and Z-score construction;
- `high`, `low`, and `close` for ATR stop design;
- `open` only if WP-S2c-194 needs a conventional OHLCV data-ref declaration for backtest assumptions.

No confirmation timeframe is proposed for the first canonical baseline. No external filter, order book, liquidation, open-interest, funding, mark/index/premium, paid data, or new data source is proposed.

## 7. Proposed Condition Structure

The intended Strategy Spec posture is `entry_logic.direction = both`, with condition groups no deeper than schema depth 3.

Entry logic:

- long entry required condition: `z_score <= -entry_z_threshold`;
- short entry required condition: `z_score >= entry_z_threshold`;
- `z_score` is the derived indicator `(close - EMA(close, lookback_n)) / StdDev(close, lookback_n)`.

Exit logic:

- long exit condition: `z_score crosses_above 0` or `z_score >= 0`;
- short exit condition: `z_score crosses_below 0` or `z_score <= 0`;
- exact use of `crosses_above` / `crosses_below` versus threshold comparison is left for WP-S2c-194 structure review.

Risk logic:

- ATR hard stop using `atr_stop_multiplier`;
- optional `max_holding_bars` time stop.

Filter/cooldown logic:

- no external filter required;
- optional `cooldown_bars` after exit or stop, if it can be represented cleanly as a review-only Strategy Spec condition without runner or DSL work.

Expressiveness note: the current schema supports `indicator_ref`, `parameter_ref`, closed comparison/cross operators, `direction = both`, and condition-group depth up to 3. WP-S2c-194 must confirm whether the derived `z_score` indicator can be represented as an `indicator_ref` with parameterized metadata under the existing schema/DSL posture. If it cannot, the package must stop for Main review rather than modify the schema, DSL, parser/compiler, runner, or query layer.

## 8. Proposed Free Parameters

The design uses no more than 5 free parameters. Ranges below are preliminary design ranges only; WP-S2c-194 must create the actual canonical instance and bounded variant manifest.

| Parameter | Role | Type | Preliminary range / allowed values |
|---|---|---|---|
| `lookback_n` | entry | integer | 20 to 100, step 10 |
| `entry_z_threshold` | entry | number | 1.5 to 3.0, step 0.25 or discrete bounded values |
| `atr_stop_multiplier` | risk | number | 1.0 to 3.0, step 0.25 or discrete bounded values |
| `max_holding_bars` | exit | integer | 16 to 96 on 15m bars, coarse bounded steps |
| `cooldown_bars` | filter/risk | integer | 0 to 16 on 15m bars, coarse bounded steps |

Population-size constraints for WP-S2c-194:

- the variant population must remain finite, bounded, and pre-registered;
- exact parameter grid choices belong in the WP-S2c-194 variant manifest;
- no adaptive search, post-hoc expansion, or result-conditioned population growth is allowed;
- the complete committed denominator must be preserved.

## 9. Success / Failure Review Targets

Success/failure criteria are descriptive test targets only, not promotion gates.

Review target families for the later sweep package:

- the Strategy Spec, variant manifest, sweep plan, and result population validate under existing validators;
- complete population denominator is preserved from pre-registration through result population;
- enough trades are present for basic sanity review, if applicable;
- gross behavior directionally matches the concept, with long entries after downside overextension and short entries after upside overextension;
- costs, funding, slippage, and backtest-realism assumptions are recorded;
- failed, skipped, and not-attempted variants remain visible in the complete result population;
- no ranking, recommendation, readiness, transition, approval, promotion, or gate authority is created.

## 10. Known Constraints And Open Questions

Facts:

- `15m` is the only timeframe currently in PLANNING.
- BTCUSDT 15m full-history OHLCV is present in `docs/data_catalog.md`.
- Strategy Spec schema and validator exist.
- There is no canonical Strategy Spec corpus and no canonical result-population corpus.

Inferences:

- Dynamic Volatility Mean Reversion appears suitable as a first clean baseline because it can be designed from existing OHLCV data and bounded parameters.
- Both long and short posture appears schema-compatible through `entry_logic.direction = both`.

Open questions for Main / WP-S2c-194 structure review:

- whether `z_score` as a derived indicator can be represented cleanly through the existing `indicator_ref` posture without parser/compiler or runner changes;
- whether both long and short should remain in the first instance if the exact condition encoding becomes awkward;
- whether exit should use cross operators or threshold comparisons around zero;
- how coarsely to discretize parameter ranges to keep the variant count bounded;
- whether `cooldown_bars` should remain a free parameter or be fixed/omitted for a smaller first baseline.

Decision:

- select Dynamic Volatility Mean Reversion as the first canonical Strategy Spec design candidate for Main review.

Future option:

- WP-S2c-194 may choose fewer than 5 free parameters if Main prefers a smaller first variant grid.

## 11. Handoff

After merge, Side must report back to Main with the selected condition structure and parameter declarations before WP-S2c-194.

Do not auto-draft WP-S2c-194 until Main clears the spec-structure review.

The first canonical sweep remains unauthorized until Karl explicitly authorizes WP-S2c-195 later.
