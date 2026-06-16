# WP-ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01

## Package class

Docs-only feasibility / architecture surface assessment.

Implementation posture: forbidden.

Strategy Spec posture: forbidden.

Canonical evidence posture: forbidden.

## Branch / worktree / base

- Branch: `docs/online-ohlcv-primitive-feasibility-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01`
- Base: `main` at `6f671a6` (`Merge pull request #498 from toobigtofailbot-maker/docs/probe-methodology-canonical-regrounding-01`)

## Changed files

- `docs/research_pipeline/2026-06-online_ohlcv_primitive_feasibility.md`
- `docs/status_entries/WP-ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01.md`
- `docs/research_pipeline/README.md`

## Source docs/code inspected

- `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/architecture/future_strategy_capability_matrix.md`
- `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`
- `docs/data/intraday_data_assessment.md`
- `docs/data/2026-06-binance_usdtm_15m_catalog_and_slice_identity.md`
- `docs/data/2026-06-binance_usdtm_4h_resampled_catalog_and_slice_identity.md`
- `docs/data_catalog.md`
- `research/schemas/strategy_spec.schema.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/schemas/result_population.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- `research/data_slices/binance_usdtm_btcusdt_4h/binance_usdtm_btcusdt_4h_20200101_20260411.catalog_slice.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_variant_sweep_artifacts.py`
- `tools/registry/validate_indicator_catalogs.py`
- `tools/registry/validate_result_populations.py`
- `tests/test_spec_signal_compiler.py`
- `tests/test_offline_research_runner.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_validate_variant_sweep_artifacts.py`
- `tests/test_validate_indicator_catalogs.py`
- `tests/test_validate_result_populations.py`
- `tests/test_research_query.py`

## Primitive feasibility classification

| Primitive | Classification |
|---|---|
| Deterministic session/opening-range primitive | Medium addition |
| Close-confirmed breakout primitive | Medium addition |
| Retest-window and retest-tolerance primitive | Medium addition |
| One-trade-per-session guard | Small bounded addition |
| Candle-shape/wick predicate | Small bounded addition |
| Body-ratio predicate | Small bounded addition |
| Higher-timeframe deterministic trend-bias reference | Medium addition |

Summary:

- A bounded shared primitive route is feasible.
- Session/retest state and higher-timeframe binding are not currently supported.
- No primitive requires protected runtime, paper/live, OMS/risk, broker/exchange, or capital path changes.

## Strategy feasibility classification

| Hypothesis | Classification |
|---|---|
| ORB break-and-retest | Near-term after bounded primitive package |
| No-wick trend pullback | Near-term after bounded primitive package |
| Deterministic ORB-derived bias variant | Requires larger compiler upgrade |

Summary:

- None of the three is testable now through current closed Strategy Spec / compiler semantics.
- ORB and no-wick designs are feasible after bounded closed primitives.
- Deterministic ORB-derived bias additionally needs multi-timeframe 4h bias binding.

## Recommendation

Recommendation: A. Proceed with one bounded shared primitive design package.

Exact next package:

```text
WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01
```

## Validation summary

Required validation was run after docs-only changes:

- `git status --short`
- `git diff --check`
- `git diff --cached --check`
- `python -m tools.registry.validate_strategy_specs`
- `python -m tools.registry.validate_variant_sweep_artifacts`
- `python -m tools.registry.validate_indicator_catalogs`
- `python -m tools.registry.validate_result_populations`
- `python -m tools.registry.validate_candidate_registry`
- `python -m tools.registry.validate_paper_state`
- `python -m tools.research_query.run --list-views`
- `python tools/dev/diff_scope_summary.py --check-forbidden`
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`

Full sharded pytest: NOT RUN - docs-only feasibility assessment; no code/schema/validator/query/runner changes.

## Boundary summary

- Implementation: NO.
- Strategy Spec / Variant Manifest / Sweep Plan / Result Population: NO.
- Compiler / runner / schema / query / data mutation: NO.
- Candidate / walk-forward / paper / live / runtime / capital authority: NO.
- Protected paths touched: NO.

## Exact next package

`WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01`
