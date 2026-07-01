# Repo Truth Discovery

Package: `WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01`

## Branch / Base

- Branch: `lab/real-traffic-acceptance-batch-01`
- Base commit: `0fbd7f240694045873e7b879da9c902172c59995`
- Refreshed from `origin/main`: yes
- Working tree preflight: clean except pre-existing untracked `build/`

## PR #596 Merge Evidence

- PR #596 is present in current history: `257abf5 Merge pull request #596 from toobigtofailbot-maker/lab/side12-operating-readiness-audit-01`
- Current `origin/main` is newer than #596 and includes PR #597 as well: `0fbd7f2 Merge pull request #597 from toobigtofailbot-maker/lab/visual-cockpit-static-01`

## Required Readiness Artifacts Inspected

- `docs/research/LAB_COMPLETION_MAP.md`
- `docs/research/LAB_EVENT_TAPE_CONTRACT.md`
- `docs/status_entries/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01.md`
- `scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/final_operating_readiness_state.json`
- `scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/side12_operating_readiness_map.json`
- `scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/event_tape_proof_ledger.json`

## Supported Family / Routes Discovered

Facts:

- `tools/research_runner/run_offline_sweep.py` is the build-test-only offline sweep runner.
- `tools/research_runner/spec_signal_compiler.py` exposes closed compiler support for OHLCV price-only surfaces, indicator builtins, crossovers, z-score operands, and online OHLCV session/opening-range primitives.
- `research/schemas/strategy_spec.schema.json`, `research/schemas/variant_manifest.schema.json`, and `research/schemas/sweep_plan.schema.json` define the Strategy Spec / Variant Manifest / Sweep Plan grammar.
- `docs/research_pipeline/2026-06-online_ohlcv_surface_integration_01.md` records scratch feasibility for no-wick 4h EMA-retest and ORB 15m surfaces.
- `docs/research_pipeline/2026-06-online_orb_15m_prereg_01.md` records an ORB 15m preregistration review surface and full-slice dry-run completion with no canonical write.
- `docs/research_pipeline/2026-06-phaseb_pivot_design_01.md` records a docs-only SMA crossover continuation design that current closed vocabulary can express.
- `docs/research_pipeline/2026-06-phaseb_first_hypothesis_design.md` records the z-score / volatility-normalized mean-reversion design basis.

Discovered supported proposal routes:

- `price_only_ohlcv.no_wick_ema_retest_4h`
- `price_only_ohlcv.opening_range_breakout_retest_15m`
- `price_only_ohlcv.sma_crossover_trend_continuation_15m`
- `price_only_ohlcv.zscore_regime_gated_mean_reversion_15m`

Inference:

- These routes are suitable for a sign-off proposal because they use existing documented surfaces and closed repo grammar, but they are not execution authority without Karl/Main sign-off.

## Research Runner / Query / Gate Surfaces Discovered

- Research runner: `tools/research_runner/run_offline_sweep.py`
- Signal compiler: `tools/research_runner/spec_signal_compiler.py`
- Query layer: `tools/research_query/run.py`, `tools/research_query/query_layer.py`, `tools/research_query/views.sql`
- WFO/OOS: `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md`, `tools/oos_gate/evaluate.py`, `tools/walkforward/run_walkforward_scratch.py`
- Robustness/MC: `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md`, `tools/robustness/seeded_advisory_mc.py`, `tools/robustness/robustness_depth.py`, `tools/research_runner/generate_robustness_report.py`
- Lab state / scheduler / reporting / dashboard: `tools/lab_state/`, `tools/lab_scheduler_shell/`, `tools/lab_reporting/`, `tools/lab_dashboard/`
- Validators: `tools/registry/validate_result_populations.py`, `tools/registry/validate_candidate_registry.py`, `tools/registry/validate_strategy_specs.py`, `tools/registry/validate_variant_sweep_artifacts.py`

## Protected / Forbidden Paths Observed But Left Untouched

- `research/candidate_registry.jsonl`
- `tools/candidate_lifecycle/**`
- `lib/**`
- `configs/**`
- `data/**`
- runtime / paper / live / OMS / risk / reconciliation / order / exchange / broker paths
- dependency manifests

## Signed Frozen Set Check

- Required sign-off artifact exists: no
- Required machine-readable frozen set exists: no
- Search of `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01` before package edits found no existing signed set.
- The prompt attachment did not contain Karl sign-off; it instructed Codex to stop before execution when sign-off is absent.

## Decision

Package stopped before real research execution and produced blocked-pending-signoff artifacts only.

## Files Intentionally Left Unchanged

- `research/candidate_registry.jsonl`
- `research/result_populations/**`
- `research/strategy_specs/**`
- `research/variant_manifests/**`
- `research/sweep_plans/**`
- `tools/research_runner/**`
- `tools/research_query/**`
- `tools/registry/**`
- `tools/oos_gate/**`
- `tools/walkforward/**`
- `tools/robustness/**`
- `tools/lab_state/**`
- `tools/lab_scheduler_shell/**`
- `tools/lab_reporting/**`
- `tools/lab_dashboard/**`
- `lib/**`
- `configs/**`
- `data/**`
