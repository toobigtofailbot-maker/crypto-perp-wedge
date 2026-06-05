# Strategy Spec Computable Surface Audit

## 1. Scope And Non-Authority

WP-12ho / WP-S2c-194-BLOCKER is a documentation-only blocker-surfacing audit.

This package creates no Strategy Spec instance, variant manifest, sweep plan, result population, runner execution, canonical sweep, EXP, REP, trial-log entry, OL, REC, DEC, schema change, validator change, query-layer change, runner change, backtester change, data-catalog change, timeframe-status change, taxonomy change, runtime change, paper/live change, or protected-path change.

This audit is not approval, recommendation, ranking, readiness, transition, gate, paper/live, runtime, promotion, or human-gate execution authority.

## 2. Main Gate Being Answered

Main's gate:

```text
Before WP-S2c-194 can create canonical instances, Side must surface what the locked grammar + runner/backtester actually compute from a Strategy Spec today.
```

This audit answers that gate from current repo truth only.

## 3. Repo-Truth Preflight

Pre-edit repo-truth discovery confirmed:

- PR #370 / WP-12hn / WP-S2c-193 is merged.
- `docs/project_status.md` records the WP-S2c-193 handoff at `docs/project_status.md:496`.
- No open PRs existed before this branch was created.
- No existing computable-surface, indicator-catalog, or computation-binding PR existed before this branch was created.
- Main's latest direction is that WP-S2c-194 must not auto-draft until Main responds to the Strategy Spec structure review; WP-12hn also specifically left `z_score` representation as an open question at `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:116`.
- Strategy Spec surfaces exist: `research/schemas/strategy_spec.schema.json` and `tools/registry/validate_strategy_specs.py`.
- Offline runner / backtester surfaces exist: `tools/research_runner/run_offline_sweep.py`, `lib/backtest.py`, and `lib/evaluation.py`.
- Result-population and query surfaces exist: `tools/registry/validate_result_populations.py`, `tools/research_query/query_layer.py`, and `tools/research_query/views.sql`.
- No canonical `research/strategy_specs/` corpus exists.
- No canonical `research/result_populations/` corpus exists.

## 4. Strategy Spec Grammar Facts

Facts:

- Operand types are `data_ref`, `indicator_ref`, `parameter_ref`, and `constant`; see `research/schemas/strategy_spec.schema.json:366`.
- Operators are closed to `gt`, `gte`, `lt`, `lte`, `eq`, `neq`, `crosses_above`, `crosses_below`, `in_set`, `is_true`, and `is_false`; see `research/schemas/strategy_spec.schema.json:313` and `tools/registry/validate_strategy_specs.py:160`.
- Condition-group depth is schema-capped at 3; see `research/schemas/strategy_spec.schema.json:102`, `research/schemas/strategy_spec.schema.json:503`, and `tools/registry/validate_strategy_specs.py:168`.
- Host data refs can name streams including `ohlcv`, `funding`, `mark`, `index`, `premium`, and `indicator_catalog`; see `research/schemas/strategy_spec.schema.json:299`.
- The schema can carry `indicator_ref` operands and compare them through closed operators, but it does not define how named indicators are computed.
- The validator enforces schema shape, closed operators, group depth, free-parameter limits, forbidden executable keys, non-authority flags, and host-data-reference safety. It does not define or enforce a concrete indicator catalog.
- The schema/validator do not map `indicator_ref.ref` values such as `ema`, `atr`, `vwap`, `rvol`, or `z_score` to computations.

Decision:

- The Strategy Spec grammar is currently a non-executing review grammar, not a computation grammar.

## 5. Backtester Facts

Facts:

- `lib.backtest.run_backtest(...)` requires a precomputed `signal: pd.Series`, `ohlcv: pd.DataFrame`, and `funding: pd.DataFrame`; see `lib/backtest.py:248`.
- The signal is expected to carry position intent values where bar `t` fills at open of bar `t+1`; see `lib/backtest.py:280`.
- The OHLCV frame must contain `open`, `high`, `low`, `close`, and `volume`; see `lib/backtest.py:388`.
- The funding frame must contain `funding_rate`; see `lib/backtest.py:392`.
- The backtester uses OHLCV `open` for fills, `close` for marking, `volume` for optional liquidity-cap checks, and funding events from `funding_rate`; see `lib/backtest.py:419`, `lib/backtest.py:427`, `lib/backtest.py:428`, `lib/backtest.py:429`, `lib/backtest.py:493`, and `lib/backtest.py:551`.
- The backtester explicitly rejects external mark/index sources in this path and supports only `mark_price_source = "close"`; see `lib/backtest.py:222`.
- `run_backtest(...)` does not consume Strategy Spec JSON directly.
- `run_backtest(...)` does not compute indicators from Strategy Spec operands.
- `run_backtest(...)` does not translate Strategy Spec conditions into signals.

Inference:

- Any strategy-specific signal computation must happen before `run_backtest(...)` is called. That binding is not present in `lib/backtest.py`.

## 6. Offline Runner Facts

Facts:

- `tools/research_runner/run_offline_sweep.py` validates a Strategy Spec, variant manifest, and sweep plan as parent inputs; see `tools/research_runner/run_offline_sweep.py:110`.
- The runner blocks canonical `research/result_populations` writes; see `tools/research_runner/run_offline_sweep.py:223`.
- The runner detects fixture modes from `variant.assignment_status` / `status_reason` strings beginning with `runner_fixture:`; see `tools/research_runner/run_offline_sweep.py:229`.
- The runner builds synthetic OHLCV, funding, and a synthetic signal in `_synthetic_inputs(...)`; see `tools/research_runner/run_offline_sweep.py:234`.
- The runner calls `run_backtest(...)` only through `_run_synthetic_backtest(...)` using those synthetic inputs; see `tools/research_runner/run_offline_sweep.py:254` and `tools/research_runner/run_offline_sweep.py:256`.
- Runner result rows record `synthetic_fixture_only` data identity; see `tools/research_runner/run_offline_sweep.py:346`, `tools/research_runner/run_offline_sweep.py:632`, and `tools/research_runner/run_offline_sweep.py:718`.
- Runner tests exercise fixture statuses such as `runner_fixture:errored`, `runner_fixture:data_unavailable`, and `runner_fixture:infra_abort`; see `tests/test_offline_research_runner.py:247`, `tests/test_offline_research_runner.py:261`, and `tests/test_offline_research_runner.py:277`.
- Runner tests confirm the backtester is called through the read-only adapter for successful variants; see `tests/test_offline_research_runner.py:516`.

Determination:

- The offline runner consumes Strategy Spec artifacts as validated parent lineage, but it does not translate Strategy Spec conditions into backtest signals.
- The current runner path is fixture/synthetic only.
- The current runner path is build-and-test-only and is not canonical Strategy Spec evidence.

## 7. Result-Population And Query Surface Facts

Facts:

- The query layer registers empty-safe Strategy Spec and result-population relations when canonical corpora are absent; see `tools/research_query/query_layer.py:1038` and `tools/research_query/query_layer.py:1665`.
- Query views expose Strategy Spec overview/parameter/condition/backtest-assumption views and result-population overview/lineage/denominator/outcome/error/data/backtest-assumption views; see `tools/research_query/views.sql:4081` through `tools/research_query/views.sql:4882`.
- These surfaces observe artifacts and integrity. They do not compute indicators, signals, or Strategy Spec-to-backtest bindings.

## 8. Actual Computable Surface Today

| Surface | Genuinely computable today? | Evidence | Notes |
|---|---:|---|---|
| raw OHLCV close | Partial | `lib/backtest.py:428`, `lib/backtest.py:551` | Backtester can consume `close` for marking once a signal already exists. No Strategy Spec-to-signal binding. |
| raw OHLCV open/high/low | Partial | `lib/backtest.py:388`, `lib/backtest.py:427`, `lib/backtest.py:493` | `open` is used for fills. `high`/`low` are required columns but not indicator-computed from Strategy Spec. |
| volume | Partial | `lib/backtest.py:388`, `lib/backtest.py:429`, `lib/backtest.py:497` | Available to the backtester for optional liquidity-cap checks. No RVOL computation binding. |
| funding | Partial | `lib/backtest.py:392`, `lib/backtest.py:419` | Funding cashflows are supported once a signal exists. No Strategy Spec funding-condition compiler. |
| EMA | No | Search found design mentions only, including `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:38` | No committed indicator computation mapping from `indicator_ref`. |
| SMA | No | Search found examples outside canonical runner, including `docs/runbook.md` | A manual runbook example can compute SMA in ad hoc code; it is not Strategy Spec binding. |
| StdDev | No | Design mention at `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:47` | No locked computation mapping. |
| ATR | No | Design mention at `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:108` | No locked computation mapping or Strategy Spec risk-stop compiler. |
| VWAP | No | Repo search found no Strategy Spec computation binding | Unsupported today. |
| RVOL | No | Repo search found no Strategy Spec computation binding | Unsupported today. |
| z_score | No | Open question at `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:116` and `docs/research_pipeline/2026-06-first_canonical_strategy_spec_design.md:167` | Specifically not cleared for canonical instance use as hidden computation. |
| Donchian high/low | No | Repo search found no Strategy Spec computation binding | Unsupported today. |
| order book imbalance | No | No order-book data/binding in inspected runner/backtester surfaces | Unsupported today. |
| liquidation volume | No | No liquidation-volume data/binding in inspected runner/backtester surfaces | Unsupported today. |
| open interest | No | No open-interest data/binding in inspected runner/backtester surfaces | Unsupported today. |
| custom indicator_ref names | No | `research/schemas/strategy_spec.schema.json:366` accepts the operand type; validator does not map names | Representable as labels only, not computable. |

## 9. Strategy Spec To Backtest Binding Determination

Finding C:

```text
No Strategy Spec -> backtest signal computation binding exists today.
```

The current state supports:

- schema validation of non-executing Strategy Spec artifacts;
- validation of variant/sweep/result-population artifact shapes;
- query visibility over those artifact families;
- a fixture/synthetic offline runner path that can call `run_backtest(...)` with synthetic signals.

The current state does not support:

- translating Strategy Spec entry/exit/filter/risk conditions into a signal series;
- computing `indicator_ref` values from Strategy Spec JSON;
- running a canonical Strategy Spec against real BTCUSDT data through the offline runner;
- producing canonical Strategy Spec-derived result-population evidence.

## 10. Implication For The First Canonical Spec

Outcome 2:

```text
No canonical Strategy Spec can be swept yet because there is no spec->signal computation binding.
```

Facts:

- A Strategy Spec instance could be created and validated as a non-executing review artifact if Main authorizes that narrow artifact-only package.
- A genuinely runnable Strategy Spec cannot be created and swept today without adding or clarifying a computation-binding / indicator-catalog path.
- The current fixture-backed runner path is useful for build-and-test proof, but it is not suitable for canonical Strategy Spec evidence because it creates synthetic signals independent of Strategy Spec conditions.

Decision:

- Do not create the first canonical Strategy Spec instance in WP-12ho.
- Do not draft canonical-instance WP-S2c-194 until Main responds to this audit.

## 11. Recommended Next Direction For Main

Recommendation:

- Main should capsule a narrow computation-binding / indicator-catalog clarification package before canonical Strategy Spec instances if the next objective is genuinely runnable evidence.
- That package should decide whether the first binding is design-only or implementation, which indicators/operands are in the first locked catalog, how `indicator_ref.ref` values map to computations, and how Strategy Spec conditions compile into the `signal` series required by `lib.backtest.run_backtest(...)`.

Future option:

- If Main wants an artifact-only canonical Strategy Spec first, it should explicitly scope that package as non-runnable and non-evidence-producing. That would not satisfy the runnable first-sweep path.

## 12. Relationship To Karl's Future Lab Requirement

Karl's downstream lab intent includes broad BTC strategy families:

- candle/statistical;
- session/multi-timeframe;
- derivatives-data;
- microstructure/order-book;
- execution-simulation-heavy;
- calendar/time-anchor;
- regime-routing.

This audit is foundational because those families require explicit data, indicator, simulator, and signal-binding definitions. They should not hide computation inside `notes`, arbitrary `indicator_ref` names, or unreviewed runner assumptions.

This package does not implement capability-map work.

## 13. Final Audit Finding

Fact:

- The Strategy Spec grammar can describe non-executing strategy logic and carry `data_ref`, `indicator_ref`, `parameter_ref`, and `constant` operands.

Fact:

- The backtester can compute backtest accounting from a precomputed signal, OHLCV, and funding inputs.

Fact:

- The offline runner can validate parent artifacts and exercise synthetic fixture backtests.

Decision:

- The actual computable Strategy Spec surface today is empty for Strategy Spec-derived signals and named indicators.

Open question:

- Main must decide whether the next package is a non-runnable canonical Strategy Spec instance package or a computation-binding / indicator-catalog clarification package.
