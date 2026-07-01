# Repo-Truth Discovery

## Package

`WP-LAB-REAL-TRAFFIC-DISTINCTNESS-CHECKS-01`

## Base And PR State

- Base commit: `ba5bf7e97201332a18a18a1e10eb3d877706c834`
- Base source: refreshed `origin/main`
- PR #599 state: merged at `2026-07-01T18:36:34Z`
- PR #599 merge commit: `ba5bf7e97201332a18a18a1e10eb3d877706c834`

## Required Sources Found

- `scratch/WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01/revised_hypothesis_set_proposal.json`
- `scratch/WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01/freshness_check_matrix.json`
- `scratch/WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01/concluded_family_inventory.json`
- `research/experiments/REP-0003.report.json`
- `research/experiments/REP-0032.report.json`
- `research/result_populations/RP-7134.result_population.json`
- `research/result_populations/RP-2592.result_population.json`
- `research/result_populations/RP-3731.result_population.json`
- `research/result_populations/RP-6236.result_population.json`
- `docs/status_entries/WP-RESEARCH-EDGE-SMA-FAMILY-01.md`
- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0005.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `research/variant_manifests/VM-0003.variant_manifest.json`
- `research/variant_manifests/VM-0004.variant_manifest.json`
- `research/variant_manifests/VM-0005.variant_manifest.json`
- `research/variant_manifests/VM-0006.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json`
- `research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json`
- `research/sweep_plans/SWEEP-PLAN-0005.sweep_plan.json`
- `research/sweep_plans/SWEEP-PLAN-0006.sweep_plan.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `tools/research_runner/spec_signal_compiler.py`

## Closest Substitutes / Notes

- The package asked for indicator catalog / compiler status entries for RVOL, rolling VWAP, EMA, ATR, RSI, and timestamp-derived session fields. Repo truth contains `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json` and `tools/research_runner/spec_signal_compiler.py` as the most direct current sources. The compiler file lists `hour_of_day_utc`, `day_of_week_utc`, `session`, `ema`, `atr`, `rsi`, `donchian`, `rvol`, and `rolling_vwap`; it was inspected read-only.
- No separate Strategy Spec, Variant Manifest, Sweep Plan, or Result Population was created for the revised hypotheses.
- No required comparison target was missing.

## Facts

- The revised proposal retains `LAB-RT-HYP-001` and introduces `LAB-RT-HYP-002R`, `LAB-RT-HYP-003R`, and `LAB-RT-HYP-004R` as replacements requiring verification.
- `REP-0003` records H-002 as 4h Donchian channel trend-following with `NO-GO`.
- `REP-0032` records H-012 as a 15m Donchian breakout using prior-bar rolling high/low plus a funding context filter, with both filtered and pure Donchian comparator paths liquidating.
- `STRAT-SPEC-0003` records RP-7134's body as SMA/stddev z-score mean reversion with shared SMA trend gate, fixed 8-bar entry throttle, and SMA-centerline exits.
- `WP-RESEARCH-EDGE-SMA-FAMILY-01` records that a fresh SMA/stddev attempt collapsed into the `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003` semantics and was blocked.
- `STRAT-SPEC-0004`, `STRAT-SPEC-0005`, and `STRAT-SPEC-0006` record fast/slow SMA crossover entries with side-specific trend SMA confirmation. `STRAT-SPEC-0005` and `STRAT-SPEC-0006` add a fixed ATR stop while preserving crossover entries.
- `IND-CATALOG-0001` declares SMA, EMA, ATR, StdDev, RSI, Donchian, SMA-distance, RVOL, and rolling candle-VWAP interfaces. It also states rolling VWAP is an OHLCV candle approximation, not true trade-level VWAP.

## Inferences

- HYP-002R is distinct from Donchian only if later formalization preserves previous-bar high/low plus RVOL plus range-expansion semantics and does not substitute rolling-channel breakout.
- HYP-003R is distinct from RP-7134 only if later formalization preserves rolling VWAP, ATR-distance scaling, RSI confirmation, and VWAP/RSI exits.
- HYP-004R is distinct from the SMA crossover family only if later formalization preserves no-fast/slow-crossover mechanics and keeps session/body-ATR/RVOL as load-bearing.

## Decision

- HYP-002R: `pass`
- HYP-003R: `pass_with_caution`
- HYP-004R: `pass_with_caution`
- Kept set: `LAB-RT-HYP-001`, `LAB-RT-HYP-002R`, `LAB-RT-HYP-003R`, `LAB-RT-HYP-004R`
- Dropped set: none
- Reduced batch: false

## Open Questions

- Main must verify whether caution-level distinctness for HYP-003R and HYP-004R is acceptable before any freeze.
- Karl signoff remains absent.
- Future formalization must be rechecked against these mechanics before execution authority is inferred.
