# WP-RESEARCH-PRICEONLY-SYNTHESIS-01 Repo-Truth Discovery

## Scope

This discovery records current merged repo evidence for the BTC 15m price-only research lane, recent blocked research-machine reach attempts, data-derived frontier status, canonical crossing reach, and Side 12 / operator research-lab target-state gaps.

No strategy run, backtest, canonical Result Population write, canonical crossing, promotion, registration, runtime, paper/live, OMS/risk/reconciliation/capital, provider/API, network, compiler, runner, backtester, schema, validator, or data-ingestion change was performed.

## Discovery Commands / Surfaces

- `git fetch origin`; `git switch main`; `git pull --ff-only origin main`; `git log --oneline -n 180`: local `main` includes merge commit `1e85394` for PR #557 / `WP-AGENT-ADAPTER-TAKERFLOW-FAMILY-01`.
- Mandatory broad `Select-String` search over `docs`, `research`, `scratch`, `tools`, and `tests` for NO-GO, Result Population, report, ORB, SMA/stddev, Donchian, taker-flow, funding, blocked, candidate-review, and canonical crossing terms.
- `python -m tools.research_query.run --list-views`: 124 views listed.
- Read-only query views inspected: `v_result_population_overview`, `v_concluded_candidates`, `v_candidate_overview`, `v_strategy_spec_overview`, `v_result_population_backtest_assumptions`, `v_result_population_outcome_counts`, `v_data_feature_availability`.
- Exact status entries and scratch blocker records inspected for ORB, SMA/stddev, Donchian adapter, taker-flow adapter, data-derived compiler/features, data availability, funding default-off reconciliation, candidate review, canonical crossing, walk-forward, robustness, dashboard, lifecycle, notifications, and future capability backlog.

## Concluded Price-Only Results Found

Fact:

- `research/result_populations/RP-4492.result_population.json` is canonical real-data evidence for `STRAT-SPEC-0001` / `VM-0001` / `SWEEP-PLAN-0001`, BTCUSDT 15m SMA-distance. `docs/research_pipeline/2026-06-post_d5_real_data_interpretation_checkpoint.md` records descriptive, non-authoritative observations. The artifact contains a complete 7/7 denominator and mixed row outcomes under the offline model, but it creates no candidate approval, recommendation, readiness, or runtime authority.
- `research/result_populations/RP-6688.result_population.json` is canonical real-data evidence for `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002`, BTCUSDT 15m both-direction SMA-band. `docs/research_pipeline/2026-06-rp6688_both_direction_sma_band_checkpoint.md` records a complete 10/10 denominator, with every row at `return_pct=-1.0`, `pnl=-10000.0`, and full drawdown under the fixed-size model.
- `research/result_populations/RP-7520.result_population.json` is canonical dynamic-sizing evidence for the same `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` lineage. `docs/research_pipeline/2026-06-canonical_dynamic_sizing_result_population.md` and `docs/research_pipeline/2026-06-realism_runway_conclusion.md` record that `RP-7520` does not reproduce the uniform liquidation artifact but still shows no evidence-level edge for that exact SMA-band population under dynamic 1x sizing.
- `research/result_populations/RP-7134.result_population.json` is canonical evidence for `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003`, BTCUSDT 15m z-score trend-gated mean reversion. `docs/research_pipeline/2026-06-phaseb_trial_01_screen_verdict.md` records a frozen-screen `NO-GO`: 8/8 denominator retained, 0/8 positive return rows, all rows near terminal loss/drawdown, and no walk-forward/promotion/readiness authority.
- `docs/research_pipeline/2026-06-phaseb_v1_failure_decomposition.md` classifies `RP-7134`'s dominant aggregate failure mode as fundamental gross-negative expectancy, with evidence limits around exact tail/no-stop mechanics because per-trade rows, MFE, MAE, and exit-reason fields are absent.
- `research/result_populations/RP-2592.result_population.json` is canonical evidence for BTCUSDT 15m SMA crossover momentum (`STRAT-SPEC-0004`). `docs/research_pipeline/2026-06-phaseb_momentum_trial_0004_rp2592_screen.md` records a frozen-screen `NO-GO` despite some positive rows because cost burden and drawdown gates fail and DSR/PSR/MinTRL inputs are absent.
- `research/result_populations/RP-3731.result_population.json` is canonical evidence for BTCUSDT 15m momentum v2 with ATR-stop (`STRAT-SPEC-0005`). `docs/research_pipeline/2026-06-momentum_v2_trial_0005_result.md` records a frozen-screen `NO-GO` because drawdown and cost gates fail.

Inference:

- The committed BTCUSDT 15m price-only Result Populations and their screen/checkpoint documents do not identify a candidate worth crossing. This does not prove price-only BTC 15m can never work; it only describes the current committed evidence set.

Decision:

- Classify the 15m SMA-distance, SMA-band, z-score mean-reversion, SMA-crossover momentum, and momentum-v2 artifacts as `canonical_result_population` / `canonical_report`, `NO-GO` or no-edge descriptive evidence depending on their paired screen/checkpoint, `price_only`, and `canonical_evidence`.

## Relevant Canonical Result Populations Found

Fact:

- Canonical Result Populations under `research/result_populations/`: `RP-2134`, `RP-2592`, `RP-3731`, `RP-4492`, `RP-6236`, `RP-6688`, `RP-7134`, `RP-7520`.
- Query view `v_result_population_overview` reports all eight as `offline_research`, `offline_only=true`, `status=generated`, and `review_status=not_reviewed`.
- 15m price-only lineage:
  - `RP-4492`: `STRAT-SPEC-0001`, denominator 7.
  - `RP-6688`: `STRAT-SPEC-0002`, denominator 10.
  - `RP-7520`: `STRAT-SPEC-0002`, denominator 10.
  - `RP-7134`: `STRAT-SPEC-0003`, denominator 8.
  - `RP-2592`: `STRAT-SPEC-0004`, denominator 8.
  - `RP-3731`: `STRAT-SPEC-0005`, denominator 8.
- 4h momentum lineage:
  - `RP-6236`: `STRAT-SPEC-0006`, denominator 8, frozen single-slice `NO-GO` in `docs/research_pipeline/2026-06-momentum_4h_trial_0006_result.md`.
- `RP-2134` is an earlier fixture-backed/offline population for `STRAT-SPEC-0001`; it is not the primary current real-data 15m synthesis anchor.

## Relevant Non-Canonical / Scratch Results Found

Fact:

- `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/` records an ORB exit re-spec attempt that stopped after formalizer acceptance because no validated ORB formalizer draft adapter or bridge support exists.
- `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/` records an SMA/stddev attempt that stopped before VM/Sweep and bridge execution because the machine path would duplicate `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003` and canonical `RP-7134`.
- `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/` records Donchian adapter validation only: formalizer/bridge smoke run `7f62785b9cd2a5d2`, scratch runner artifact `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/outputs/7f62785b9cd2a5d2/runner_artifacts/RP-3248.result_population.json`, two completed fixture variants, and explicit non-authority flags.
- `scratch/WP-AGENT-ADAPTER-TAKERFLOW-FAMILY-01/` records blocked taker-flow adapter discovery and blocked downstream reach reasons; no adapter was implemented and no runner smoke was run.

Decision:

- Treat these scratch outputs as `blocked_attempt` or `adapter_smoke`; they do not create canonical evidence or GO/NO-GO strategy conclusions.

## Blocked Attempts and Exact Blockers

Fact:

- ORB exit re-spec (`docs/status_entries/WP-RESEARCH-ORB-EXIT-RESPEC-01.md`): formalizer accepted the idea but produced no draft Strategy Spec because no validated ORB draft adapter exists; bridge, robustness, and candidate review were blocked. Missing diagnostics include MFE, MAE, exit reason, per-trade rows, and gross PnL/cost-gross for ORB.
- SMA/stddev fresh edge attempt (`docs/status_entries/WP-RESEARCH-EDGE-SMA-FAMILY-01.md`): formalizer produced a validator-clean scratch Strategy Spec but it was semantically identical to `STRAT-SPEC-0003`; VM/Sweep/bridge were blocked because only duplicate `VM-0003` / `SWEEP-PLAN-0003` semantics are available and `RP-7134` is already concluded `NO-GO`.
- Donchian adapter (`docs/status_entries/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01.md`): not blocked at adapter-smoke level. It is adapter-validation only, using a deterministic scratch OHLCV fixture and scratch `RP-3248`; it explicitly makes no fresh research conclusion and does not reopen H-002/REP-0003 or H-012/REP-0032.
- Taker-flow adapter/downstream reach (`docs/status_entries/WP-AGENT-ADAPTER-TAKERFLOW-FAMILY-01.md`): blocked before implementation because the current offline runner input loading strips non-OHLCV fields and the worktree has no runner-consumable full-history taker-flow dataset. Safe implementation would require runner/data-source support outside that WP.
- Candidate-review reach for the fresh ORB/SMA/taker-flow attempts is blocked because required valid bridge/robustness source packets do not exist for those attempts.
- Canonical crossing remains blocked for real use because current crossing support is fixture-only and no real candidate-review packet worth crossing exists.

## Canonical / Scratch / Docs-Only / Advisory Classification

Fact:

- Canonical Result Populations: `research/result_populations/RP-*.result_population.json`.
- Canonical reports/checkpoints: selected documents under `docs/research_pipeline/` that interpret specific RPs without changing authority.
- Scratch-only blocked/adapter artifacts: all outputs under the inspected `scratch/WP-*` prefixes.
- Docs-only design/inventory: canonical crossing design, BTC future capability backlog, expressiveness/pivot design docs.
- Infrastructure-only: compiler data-derived field allowlist, data feature availability labels, taker-flow archive reconstruction tool, funding default-off switch, walk-forward contracts, dashboard review surfaces, notification pilot.

Decision:

- Do not merge these categories. Scratch adapter smoke and docs-only designs are not canonical strategy evidence.

## Price-Only Versus Data-Derived Classification

Fact:

- Price-only/OHLCV-only 15m canonical families include `STRAT-SPEC-0001`, `STRAT-SPEC-0002`, `STRAT-SPEC-0003`, `STRAT-SPEC-0004`, and `STRAT-SPEC-0005`.
- Donchian H-002 is 4h price-only and concluded `NO-GO` via `REP-0003`.
- H-012 / `REP-0032` is hybrid: 15m Donchian breakout with funding-rate context filter plus a pure Donchian comparator. It is concluded `NO-GO`; the pure comparator also liquidated later with Sharpe `0.2884` and 201 trades.
- Taker-flow feature usage is data-derived; no committed equivalent taker-flow canonical RP/REP or GO/NO-GO strategy conclusion was found in the inspected repo truth.
- Funding/premium/mark/index data-derived features have existing historical infrastructure and older candidate evidence in non-15m contexts, but this package found no taker-flow strategy conclusion and no new data-derived frontier strategy family test after PR #557.

Decision:

- State that data-derived families such as taker-flow/funding remain untested in the recent adapter/downstream frontier where runner/data-path support is missing. Do not state that every historical funding-containing candidate in the repo is untested.

## Data-Derived Infrastructure Status

Fact:

- `docs/status_entries/WP-COMPILER-FEATURES-DATA-DERIVED-01.md` records compiler-visible data refs for funding, mark/index/premium, open interest, long/short ratios, and taker fields as direct input values only. It does not fetch, align, forward-fill, backfill, interpolate, or change funding PnL/cost semantics.
- `docs/status_entries/WP-DATA-AVAILABILITY-LABELS-01.md` records full-history conditional availability for funding, mark/index/premium, timestamp-derived fields, and taker archive derivations; recent/snapshot/vendor-only limitations remain fail-closed for other features.
- `docs/status_entries/WP-DATA-TAKERFLOW-ARCHIVE-RECON-01.md` records deterministic local public archive reconstruction for taker-flow slices, with no network/download path and no runner/backtester integration authority.
- `docs/status_entries/WP-LAB-FUNDING-BACKTEST-DEFAULT-OFF-RECONCILIATION-01.md` records explicit `funding_cost_mode`, defaulting off. It is a protected cost-model reconciliation and not a taker-flow/funding edge result.
- PR #557 discovery records that `tools/research_runner/run_offline_sweep.py` narrows input to OHLCV columns before compilation, so archive-derived taker-flow columns are not currently runner-consumable.

Inference:

- Taker-flow/funding infrastructure exists in parts, but the current runner/data path does not yet make archive-derived non-OHLCV columns generally consumable for a real taker-flow strategy run.

## Data-Derived Strategy Conclusion Status

Fact:

- No committed equivalent taker-flow canonical RP/REP or GO/NO-GO strategy conclusion was found by the bounded taker-flow adapter discovery.
- Funding-containing historical candidates exist, including H-001, H-007, H-010, and H-012, with `NO-GO` conclusions in the candidate query surface. These are not evidence that the blocked taker-flow adapter frontier has been tested.

Decision:

- For this synthesis, classify taker-flow adapter/downstream reach as `NOT_TESTED` / `BLOCKED`, not `NO-GO`.

## Canonical Crossing Status

Fact:

- `docs/status_entries/WP-AGENT-CANONICAL-CROSSING-BUILD-01.md` records a fixture-only canonical crossing builder. It writes only under scratch outputs and validates fake/test registry copies.
- First real crossing remains separately gated. It requires a real candidate-review packet selected by humans, full source content surfaced before approval, a real approval artifact, explicit real storage authorization, and fresh validation.
- Recent ORB, SMA, and taker-flow attempts did not produce the required valid bridge/robustness/candidate-review chain.

Inference:

- The first real canonical crossing remains unavailable because no candidate-review packet worth crossing exists in current repo truth.

## Side 12 / Operator Research-Lab Target-State Gaps

Fact:

- Existing partial/built surfaces include idea intake/formalization, bounded research agents, scratch candidate-review packet preparation, fixture-only canonical crossing, non-canonical walk-forward run capability, walk-forward contract, advisory robustness depth, dashboard operator-review page, and notification/approval pilot.
- Existing gaps remain in always-on scheduling, autonomous scout behavior, broad adapter coverage, generic downstream robustness/candidate-review reach across supported families, full data-derived runner support, per-trade/MFE/MAE/exit_reason diagnostics, standard candidate gates for walk-forward/OOS and Monte Carlo robustness, a real agent-produced candidate lifecycle packet, first real canonical crossing, full dashboard page breadth, daily/weekly reports, integrated operator notification/approval queue, regime/parameter advisor integration, live/paper performance monitoring, and the paper/live/runtime execution-machine phase.

Decision:

- Classify the Side 12 / operator target state as incomplete.

## Repo-Truth Corrections to Main / Operator Assumptions

- Donchian is not an unconcluded archetype. H-002/`REP-0003` is concluded `NO-GO`, and H-012/`REP-0032` includes a funded Donchian test plus pure comparator, also `NO-GO`.
- ORB +1.1R median MFE is operator context only in the inspected repo truth; no committed support for that exact claim was found.
- The recent SMA/stddev machine attempt did not produce fresh evidence because it duplicated the already-concluded `RP-7134` family.
- The taker-flow package did not fail as a strategy; it stopped before implementation because runner/data support is missing.
- The research lab has several built pieces, but the Side 12 / operator target state remains incomplete.

## Open Questions / Future Options

- Whether to build runner/data-path support for data-derived families.
- Whether to resume taker-flow/funding adapter work after runner/data-path support exists.
- Whether to add more price-only adapters despite the current synthesis.
- Whether to expand dashboards/reporting/operator surfaces before additional research execution.
- Whether to hold canonical crossing until a real candidate-review packet exists.
