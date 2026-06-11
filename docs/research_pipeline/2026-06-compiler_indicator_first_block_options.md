# Compiler / Indicator First-Block Options

## Scope And Non-Authority

`WP-COMP-SURFACE-01` is docs-only and decision-surface only. It implements nothing.

This document does not authorize compiler implementation, schema or validator changes, indicator-catalog changes, Strategy Specs, variant manifests, sweep plans, result populations, backtests, ranking, recommendation, readiness, promotion, paper/live work, runtime work, data acquisition, simulator implementation, or protected-path work.

Main 5 must choose the next block after reviewing this surface. This document surfaces options; it does not select or authorize one.

## Repo-Truth Basis

Inspected local branch and commit:

- Branch: `docs/comp-surface-01-first-block-options`
- Starting commit inspected: `f13472da96943f50544aa319ab0903aa6b3c9020`
- GitHub dependency check: PR #427 / `WP-STRAT-CAP-01` is merged.
- Open PR check at start: `gh pr list --state open --json number,title,headRefName,files,url --limit 100` returned `[]`.
- Direct `git fetch origin` failed twice during startup with a network connection error; local work started from the merged PR #427 head after GitHub confirmed the merge.

Key files inspected:

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `docs/research_pipeline/2026-06-compiler_extension_tranche_plan.md`
- `docs/research_pipeline/2026-06-strategy_lab_capability_delta_map.md`
- `docs/research_pipeline/2026-06-lookback_parameter_binding_design.md`
- `docs/status_entries/WP-STRAT-CAP-01.md`
- `research/schemas/strategy_spec.schema.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `tools/registry/validate_strategy_specs.py`
- `tests/test_validate_strategy_specs.py`
- `tools/research_runner/spec_signal_compiler.py`
- `tests/test_spec_signal_compiler.py`

Current repo truth wins over S2c-213 where S2c-213 is stale. The main delta is that S2c-213 listed lookback parameter binding as the first future extension, while current schema, validator, compiler, and tests already support `bars_parameter_ref` in approved `indicator_ref.lookback` contexts, including inside `composed_operand.base_operand`.

## Reconciled S2c-213 Ordering

| S2c-213 step | Extension | Original posture | Current repo-truth delta | Keep / revise / done |
|---|---|---|---|---|
| E1 | Lookback parameter binding | First block | `strategy_spec.schema.json`, `validate_strategy_specs.py`, `spec_signal_compiler.py`, and tests support `bars_parameter_ref` in approved `indicator_ref.lookback` contexts. | Done / no implementation WP |
| E2 | `crosses_above` / `crosses_below` | Compiler/operator implementation | Schema enum exists; validator accepts the closed operator enum; compiler lists both in `UNSUPPORTED_OPERATORS` and fails closed. | Candidate first implementation block |
| E3 | `scale_by_one_plus_parameter` | Closed composed form | Schema and validator currently close `composition_type` to `scale_by_one_minus_parameter`; compiler supports only the minus form and tests reject plus. | Candidate, but schema + validator + compiler |
| E4 | `both` direction | Design first | Schema entry direction permits `both`; compiler explicitly raises `UnsupportedSpecSignalCompilerFeature`; semantics remain ambiguous. | Design first |
| E5 | `z_score` | Design first | No current schema grammar, validator semantics, catalog builtin, or compiler support verified for a closed z-score composition. | Design first |
| E6 | RSI / RVOL / Donchian | Catalog/compiler builtins | Indicator catalog and compiler approved builtins are `sma`, `ema`, `atr`, and `stddev` only. | Catalog/builtin design or implementation candidate after Main choice |
| E7+ | Offsets / VWAP / session / MTF / ATR-stop | Design/defer | Offset and VWAP need unit/session semantics; session needs UTC filter design; MTF needs runner/data alignment; ATR-stop needs runner/backtester consumption design. | Defer/design/Karl-gated where relevant |

## Per-Extension Compatibility Matrix

| Extension | Current schema support | Current compiler support | Current catalog support | Data stream needed | Likely package class | Gate / blocker | First-block suitability |
|---|---|---|---|---|---|---|---|
| Lookback parameter binding | Supported for approved `indicator_ref.lookback` contexts | Supported through variant `parameter_values` resolution | Existing SMA/EMA/ATR/StdDev entries permit strategy parameter binding for lookback | No new stream | No implementation package | Already merged | Done |
| `crosses_above` / `crosses_below` | Operator enum includes both | Fails closed via `UNSUPPORTED_OPERATORS` | Not catalog-dependent | No new stream | T3 compiler/operator + tests | Exact prior-bar/null/no-lookahead semantics | Implementation-ready candidate if Main accepts compiler-only scope |
| `scale_by_one_plus_parameter` | Not supported; current composition const is minus only | Fails closed as unsupported composition type | Not catalog-dependent | No new stream | T3 schema + validator + compiler + tests | Must mirror minus-form constraints without widening expression grammar | Good second candidate, broader than `crosses_*` |
| `both` direction | `entry_logic.direction` enum includes `both` | Fails closed explicitly | Not catalog-dependent | No new stream | T1 design first | Ambiguous long/short condition semantics and flip behavior | Not suitable as first implementation |
| `z_score` | No closed grammar verified | No support | No current z-score builtin | No new stream if based on OHLCV/indicator operands | T1 design first, then T3 | Fixed arity, denominator/null handling, no expression-language posture | Not suitable as first implementation |
| RSI | Not a Strategy Spec grammar issue if represented as indicator_ref after catalog support | No builtin | Not present | No new stream if OHLCV close-based | T1/T3 catalog + compiler + tests | Formula convention and warmup must be locked | Possible after indicator design |
| RVOL | Not a Strategy Spec grammar issue if represented as indicator_ref after catalog support | No builtin | Not present | No new stream if OHLCV volume-based | T1/T3 catalog + compiler + tests | Denominator, zero-volume, and baseline convention | Possible after indicator design |
| Donchian | Not a Strategy Spec grammar issue if represented as indicator_ref after catalog support | No builtin | Not present | No new stream if OHLCV high/low-based | T1/T3 catalog + compiler + tests | Current-bar inclusion and output fields must be locked; pairs well with `crosses_*` | Good design candidate; implementation after formula close |
| VWAP | Not present | No builtin | Not present | OHLCV volume may support rolling VWAP; anchored/session VWAP needs session semantics | T1 design first | Rolling vs anchored/session semantics | Not first implementation |
| Session/time filters | No dedicated closed predicate grammar verified | No support | Not catalog-dependent | No new stream, but UTC/session convention required | T1 design first | Timezone/session model and no runtime clock dependence | Not first implementation |
| Multi-timeframe | Timeframe fields exist, but non-empty operand timeframes fail closed | Resampling/alignment unsupported | Catalog-independent | Existing OHLCV frames may be used only after runner/data contract design | T1 design before T3 | No-lookahead alignment, gap handling, runner input contract | Deferred |
| ATR-stop consumption | ATR builtin exists as an indicator value | Compiler emits position-intent signal only; stop consumption not supported | ATR catalog entry exists | No new stream for ATR itself | T1 runner/backtester design first | Runner/backtester/protected-adjacent semantics | Deferred / protected-adjacent design |
| OI/L2/trade-flow dependent extensions | Not present | Not present | Not present | New data stream required | T1 feasibility/data contract first | Karl-gated acquisition/vendor/data scope | Out of scope for first block |

## Candidate First Implementation Blocks

The options below are sorted by repo-compatibility class, not by strategy quality. None is authorized by this document.

### `WP-COMP-XOVER-01` - Implement `crosses_above` / `crosses_below`

- Objective: Implement compiler support for the two schema-valid closed crossover operators and add focused compiler tests.
- Likely changed files: `tools/research_runner/spec_signal_compiler.py`, `tests/test_spec_signal_compiler.py`, and `docs/project_status.md` / status fragment if the WP requires status updates.
- Validation profile: focused compiler tests for prior/current evaluation, null-never-true behavior, warmup, series/scalar combinations, deterministic repeatability, no-lookahead mutation checks, no-write behavior, `git diff --check`, result-population validator, query views/integrity checks, diff scope summary, and full pytest if the implementation WP requires it.
- Safety: Narrowest implementation candidate because schema and validator already admit the operator enum and the change can remain compiler/test-only.
- Dependencies: Main 5 must accept exact crossover semantics before implementation.
- Non-authority posture: no Strategy Specs, variants, sweeps, result populations, canonical runs, ranking, recommendation, readiness, promotion, runtime, paper/live, data acquisition, or protected-path work.

### `WP-COMP-PLUS-01` - Add `scale_by_one_plus_parameter`

- Objective: Add the symmetric closed composed form `scale_by_one_plus_parameter` using the existing minus-form pattern.
- Likely changed files: `research/schemas/strategy_spec.schema.json`, `tools/registry/validate_strategy_specs.py`, `tests/test_validate_strategy_specs.py`, `tools/research_runner/spec_signal_compiler.py`, `tests/test_spec_signal_compiler.py`, and status docs if scoped.
- Validation profile: schema meta-validation, strategy-spec validator tests, compiler tests, fail-closed tests for unsupported composition types, parameter range tests, no-lookahead/null/determinism tests, result-population validator, query views/integrity checks, diff scope summary, and full pytest if the implementation WP requires it.
- Safety: Closed and small, but broader than `crosses_*` because it requires schema, validator, compiler, and tests.
- Dependencies: Main 5 must confirm the plus form should keep the existing numeric parameter `(0, 1)` constraint and not widen composition into arbitrary arithmetic.
- Non-authority posture: no artifact mutation, canonical use, ranking, recommendation, readiness, promotion, runtime, paper/live, data acquisition, or protected-path work.

### `WP-IND-DONCHIAN-DESIGN-01` - Close a small indicator-catalog formula block

- Objective: Design the closed formula and interface posture for one small indicator family, with Donchian as the clearest candidate if Main wants breakout expressiveness after `crosses_*`.
- Likely changed files: a new docs/research_pipeline design document, status fragment, and compact project-status pointer.
- Validation profile: docs validation, result-population validator, query views/integrity checks, diff scope summary, final text audit, and no code tests unless a later implementation WP is authorized.
- Safety: Safer as design first because Donchian needs current-bar inclusion/exclusion and output-field conventions before catalog/compiler changes. RSI/RVOL are similar design candidates but require their own formula/warmup/zero-denominator conventions.
- Dependencies: Main 5 must decide whether indicator-catalog expansion should precede or follow `crosses_*` and plus composition.
- Non-authority posture: no catalog edit, compiler edit, Strategy Spec, variants, sweeps, result populations, canonical use, ranking, recommendation, readiness, promotion, runtime, paper/live, data acquisition, or protected-path work.

## Recommended Next Decision For Main 5

Main 5 should choose one:

A. Authorize `crosses_*` compiler implementation if the prior-bar/null/no-lookahead compatibility is accepted as clean.

B. Authorize `scale_by_one_plus_parameter` as a closed schema/validator/compiler package.

C. Authorize a small indicator-catalog design package before new indicators.

D. Request a narrower implementation WP only after resolving any compatibility blocker.

## Boundary Statement

This surface creates no new Strategy Specs, variant manifests, sweep plans, result populations, canonical artifacts, backtests, ranking, recommendation, readiness, promotion, data acquisition, simulator implementation, runtime work, paper/live work, OMS/risk work, broker/exchange work, or protected-path change.

It does not authorize use of any option in canonical artifacts. It does not authorize changes to `lib/backtest.py`, `lib/evaluation.py`, runtime, paper/live, protected execution, schemas, validators, catalog, compiler, tools, tests, data, dashboard implementation, or generated dashboard output. Those remain outside this WP unless a later explicit package scopes them.
