# WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01

Package class: docs-only primitive design / architecture decision surface.

Branch/worktree/base:

- Branch: `docs/online-ohlcv-primitive-design-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01`
- Base: `main` at `1c0c686` after PR #499 merge.

Changed files:

- `docs/architecture/online_ohlcv_primitive_design.md`
- `docs/status_entries/WP-ONLINE-OHLCV-PRIMITIVE-DESIGN-01.md`
- `docs/research_pipeline/README.md`

Source docs/code inspected:

- `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
- `docs/research_pipeline/2026-06-online_ohlcv_primitive_feasibility.md`
- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/architecture/future_strategy_capability_matrix.md`
- `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`
- `research/schemas/strategy_spec.schema.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/schemas/result_population.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/strategy_specs/STRAT-SPEC-0006.strategy_spec.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- relevant compiler, runner, schema, validator, and query tests.

First-tranche decision:

- Split implementation into two bounded packages.
- Session/ORB package: `session_window`, `opening_range`, close-confirmed breakout, close-confirmed retest window/tolerance, and `entry_controls.max_trades_per_session`.
- Candle-shape package: upper/lower wick and body-ratio predicates with side-specific and fail-closed behavior.

Deferred scope:

- Higher-timeframe deterministic trend-bias binding.
- Intrabar stop/target ordering and simulator realism.
- Fixed-R target unless close-only conservative semantics are separately authorized.
- Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, probes, candidates, and canonical evidence.
- Runtime, paper/live, OMS/risk, broker/exchange, capital, and autonomous authority.

Recommendation:

- B. Split implementation into session/ORB and candle-shape packages.

Exact next packages:

- `WP-ONLINE-OHLCV-SESSION-ORB-IMPL-01`
- `WP-ONLINE-OHLCV-CANDLE-SHAPE-IMPL-01`

Validation summary:

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `tools.registry.validate_strategy_specs`: PASS.
- `tools.registry.validate_variant_sweep_artifacts`: PASS.
- `tools.registry.validate_indicator_catalogs`: PASS.
- `tools.registry.validate_result_populations`: PASS.
- `tools.registry.validate_candidate_registry`: PASS.
- `tools.registry.validate_paper_state`: PASS.
- `tools.research_query.run --list-views`: PASS.
- `tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no forbidden-path matches.
- `tools/dev/verify.py --integrity-views --integrity-max-workers 4 --timeout-seconds 300 --max-output-chars 6000 --json`: PASS; integrity views clean.
- Full sharded pytest: NOT RUN - docs-only primitive design; no code/schema/validator/query/runner changes.

Boundary summary:

- Implementation: NO.
- Strategy Spec / Variant Manifest / Sweep Plan / Result Population: NO.
- Compiler / runner / schema / query / data mutation: NO.
- Candidate / walk-forward / paper / live / runtime / capital authority: NO.
- Protected paths touched: NO.
