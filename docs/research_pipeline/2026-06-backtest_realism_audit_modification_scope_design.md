# Backtest Realism Audit / Modification Scope Design

## 1. Scope

WP-S2c-171 / WP-12gr is a Tier 1 documentation-only read-only audit and per-edit modification-scope design package.

This package creates this document and updates `docs/project_status.md` only.

It inspects `lib/backtest.py`, `lib/evaluation.py`, and relevant tests read-only. It does not edit implementation files, tests, schemas, validators, query views, artifacts, tools, runners, configs, data, runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, safe-mode, kill-switch, `.claude/`, dashboards, agents, prompts, or protected paths.

## 2. Repo-Truth and Decision Basis

Repo truth is refreshed `main` at WP-S2c-170 / WP-12gq merge commit `8b2acd370b4100130f16c61d6e7a9b67915f20eb`.

Primary basis:

- `docs/project_status.md` records that WP-S2c-170 merged and that WP-S2c-171 may be drafted after refreshed-main preflight and no stop trigger.
- `docs/research_pipeline/2026-06-implementation_roadmap_locking_first_tranche_authorization.md` authorizes WP-S2c-171 as read-only audit and per-edit modification-scope design only.
- `docs/research_pipeline/2026-06-lab_validity_floor_backtest_realism_bounded_search_design.md` identifies the crypto-perp realism taxonomy.
- WP-S2c-164 through WP-S2c-169 preserve implementation deferral, prerequisite discipline, provenance, Strategy Spec / DSL non-execution, agent support-only posture, and human gates.
- D2-006, D2-007, REC-5, Scope 6, Phase 9 / D2-011, D-0001, D2-008, Phase 1 paper runtime protection, OMS, reconciliation, kill-switch, Tier 4 boundaries, and Track 3 paused state remain unchanged.

Current merged repo truth wins over memory, external research, summaries, or generic best practice.

## 3. Audit Objective

The objective is to inspect current research backtest/evaluation surfaces and identify exact future modification scopes for Main review before any WP-S2c-172+ implementation package is drafted.

The audit covers fees, funding timing and treatment, slippage and fills, liquidity and order-size realism, liquidation and maintenance margin, exchange constraints, mark/index assumptions, bar-path assumptions, deterministic preservation, and regression / before-after evidence.

## 4. Non-Authority Boundary

This document is not implementation authority.

WP-S2c-171 does not authorize implementation, direct edits to `lib/backtest.py`, direct edits to `lib/evaluation.py`, protected-path edits, test edits, schema changes, validator changes, query-view changes, artifact creation, runner work, sweep execution, dashboard work, agent work, runtime contact, paper/live contact, recommendation, approval, readiness, ranking/scoring authority, transition authority, or human-gate execution.

WP-S2c-172+ are not draftable automatically. They require WP-S2c-171 merge, Side report-back to Main, Main review of the exact protected-path edit scope, and explicit Main authorization of the next specific edit package or capsule set.

Proposed modifications below are proposed scopes only. They are not approved edits.

## 5. Read-Only Inspection Summary

Inspected read-only:

- `lib/backtest.py`
- `lib/evaluation.py`
- `tests/test_backtest.py`
- `tests/test_backtest_liquidation.py`
- `tests/test_evaluation.py`
- `tests/test_evaluation_cost_drag.py`

Current implementation summary:

- `run_backtest()` is a deterministic bar-by-bar research backtester.
- Signal at bar `t` fills at open of bar `t+1`.
- OHLCV and funding inputs must have UTC monotonic non-duplicated indexes.
- Irreparable D2-003A bars are skipped from a manifest.
- Fees and slippage are modeled as fixed bps costs on one-contract notional.
- Funding cashflows are applied to open positions for funding events within `(prev_bar_ts, bar_ts]`.
- Liquidation is represented as an equity floor at zero when marked equity becomes non-positive.
- Evaluation consumes `BacktestResult` to compute metrics and D2-006 gates.

## 6. Current Backtest/Evaluation Surface Map

| Surface | File | Current role | Affects | Realism relation | Future risk |
|---|---|---|---|---|---|
| `BacktestResult` | `lib/backtest.py` | Frozen result dataclass with equity, trades, PnL, costs, skips, liquidation fields | result reporting, metrics input | stores fees, slippage, funding, liquidation status | protected-path-adjacent because downstream evaluation/tests consume fields |
| `_load_irreparable_gaps()` | `lib/backtest.py` | Loads D2-003A gap manifest | deterministic gap handling | data gap realism | low implementation risk if unchanged |
| `_build_irreparable_set()` | `lib/backtest.py` | Converts gap ranges to timestamps | deterministic skip behavior | bar availability assumptions | low to moderate if gap semantics change |
| `_validate_series_index()` | `lib/backtest.py` | Enforces UTC, monotonic, no duplicates | deterministic input assumptions | funding and bar timing | moderate if expanded for new data surfaces |
| `_bps_cost()` | `lib/backtest.py` | Calculates bps cost from price and size | fees/slippage costs | fixed one-contract cost model | moderate if sizing or fee tiers are added |
| `run_backtest()` input arguments | `lib/backtest.py` | Public API for signals, OHLCV, funding, costs, execution mode | parameter handling, calculation | all audit dimensions | implementation-risky; central research engine |
| `run_backtest()` gap skip block | `lib/backtest.py` | Carries equity through irreparable bars | calculation, determinism | data gap and bar-path assumptions | moderate; affects historical reproducibility |
| `run_backtest()` funding block | `lib/backtest.py` | Applies funding events between bars | calculation | funding timing/treatment | high; affects candidate metrics |
| `run_backtest()` fill block | `lib/backtest.py` | Closes/opens at next bar open, taker fee, fixed slippage | calculation, trades | fees, slippage/fills, bar path | high; affects all backtests |
| `run_backtest()` liquidation block | `lib/backtest.py` | Floors equity at zero and stops processing | calculation, trades, reporting | liquidation / maintenance margin | high; changes can alter NO-GO evidence |
| `params_snapshot` | `lib/backtest.py` | Records run parameters | result reporting | cost/execution assumption disclosure | moderate; useful for future auditability |
| `_returns_from_equity()` | `lib/evaluation.py` | Computes per-bar returns | metrics | regression evidence | moderate if equity path changes |
| `sharpe()`, `sortino()`, `calmar()`, `max_drawdown()` | `lib/evaluation.py` | Core metrics | metrics | before/after evidence, drawdown/liquidation | moderate |
| `turnover()` | `lib/evaluation.py` | Entry-price based turnover | metrics | order-size and cost fragility proxy | moderate; one-contract assumption |
| `cost_drag()` | `lib/evaluation.py` | Costs over gross PnL | metrics, Gate 5 input | fees/slippage/funding fragility | high; D2-006 related |
| `deflated_sharpe_ratio()` | `lib/evaluation.py` | DSR probability and benchmark | Gate 2 | anti-overfit context, not direct realism | moderate |
| `parameter_sensitivity()` | `lib/evaluation.py` | Runs shifted params and Sharpe | Gate 4 support | regression evidence and robustness | moderate |
| `check_promotion_gates()` | `lib/evaluation.py` | D2-006 gate report | metrics/gates | cost drag, drawdown, WFE | high; gate semantics must not change without authority |
| `TrialEntry`, `make_trial_entry()`, `append_trial()` | `lib/evaluation.py` | Trial-log helper | evidence recording | provenance, regression evidence | implementation-risky if changed because trial-log authority is protected by package scope |

## 7. Realism Taxonomy Audit Summary

| Dimension | Current posture | Concise finding |
|---|---|---|
| Fees | partially modeled | fixed bps inputs exist; maker fee input is unused in current fill semantics |
| Funding timing / treatment | partially modeled | event timestamps are applied between bars using entry fill price not mark/notional updates |
| Slippage / fills | partially modeled | fixed one-way bps slippage and next-bar-open fills exist; no partial fills or market impact |
| Liquidity / order-size realism | absent to partially modeled | one-contract sizing and OHLCV volume presence exist; no capacity, volume share, depth, or size model |
| Liquidation / maintenance margin | partially modeled | equity floor and stop exist; no maintenance-margin schedule, leverage brackets, mark price, or exchange liquidation formula |
| Exchange constraints | absent | no tick/step/min-notional/leverage/order-type/time-in-force constraints |
| Mark/index assumptions | assumed externally | OHLCV close marks equity; funding uses entry fill price; no mark/index stream selection in engine |
| Bar-path assumptions | partially modeled | next-bar-open fill and close marking are explicit; intrabar path is not modeled |
| Deterministic preservation | explicitly modeled | UTC index assertions, no lookahead tests, frozen result dataclass, deterministic loops |
| Regression / before-after evidence | partially modeled | unit tests and WP-5b regression tests exist; future realism changes need stronger before/after evidence |

## 8. Fees Audit

Current evidence:

- `run_backtest()` accepts `fee_bps_taker` and `fee_bps_maker`.
- Entries and exits both call `_bps_cost(fill_price, 1.0, fee_bps_taker)`.
- `fee_bps_maker` is recorded in `params_snapshot` but is not used in current calculation.
- Trade rows record exit-side `fees`; entry fees are accumulated in `fees_paid` but not represented as a separate trade-row field.

Finding: fees are partially modeled as fixed taker bps on one-contract notional. Maker/taker differentiation is not operationally modeled. Fee tiers, maker fills, VIP tiers, BNB discounts, and exchange-specific fee schedules are absent.

## 9. Funding Timing / Treatment Audit

Current evidence:

- Funding input requires a `funding_rate` column and UTC funding-event index.
- Funding events are applied for open positions when `prev_bar_ts < f_ts <= bar_ts`.
- Longs pay positive funding and shorts receive positive funding through `funding_cashflow = -position * rate * abs(entry_fill_price)`.
- Funding notional is fixed to `abs(entry_fill_price)` for one-contract sizing.

Finding: funding is partially modeled with event timing and directional sign. It does not use changing mark notional, position quantity beyond one contract, funding interval metadata, missed-event diagnostics, or mark/index source selection.

## 10. Slippage / Fills Audit

Current evidence:

- Only `execution="next_bar_open"` is supported.
- Signal at bar `i - 1` fills at `open_prices[i]`.
- Slippage is a fixed bps cost rather than a price adjustment.
- Entries and exits are treated as complete fills at one open price.

Finding: slippage and fills are partially modeled. The current model is deterministic and simple but does not model spread, volume, market impact, stale fills, partial fills, limit/stop behavior, order type, queue position, latency, or fill rejection.

## 11. Liquidity and Order-Size Realism Audit

Current evidence:

- OHLCV requires a `volume` column.
- `volume` is not used in cost, fill, capacity, or trade admissibility logic.
- Position size is effectively one contract and callers are expected to scale externally.
- `turnover()` assumes entry-price notional and doubles for entry plus exit.

Finding: liquidity and order-size realism are mostly absent. There is no volume-share cap, depth model, maximum notional, minimum notional, capacity stress, or strategy-size parameter inside `run_backtest()`.

## 12. Liquidation / Maintenance Margin Audit

Current evidence:

- `BacktestResult` exposes `liquidated` and `liquidation_timestamp`.
- `run_backtest()` sets liquidation when `marked_equity <= 0.0`, floors equity to zero, appends a closing trade if needed, and stops processing future bars.
- Tests assert bounded drawdown after catastrophic paths.

Finding: liquidation is partially modeled as ruin / zero-equity semantics. It is not Binance-style maintenance margin or liquidation-price modeling. There are no leverage brackets, margin mode assumptions, maintenance margin rates, mark-price liquidation checks, insurance fund / ADL assumptions, or liquidation fees.

## 13. Exchange Constraints Audit

Current evidence:

- `run_backtest()` accepts no exchange filter metadata.
- There are no tick-size, step-size, min-notional, max-notional, leverage, order-type, time-in-force, reduce-only, position-mode, or precision checks.
- The research engine uses continuous float prices and one-contract size.

Finding: exchange constraints are absent from the current research backtester. They are also deliberately separate from protected broker/exchange/order paths and must not be imported from runtime code by implication.

## 14. Mark/Index Assumptions Audit

Current evidence:

- `stream` and `interval` are used for irreparable-gap lookup only.
- The OHLCV `close` marks open positions for equity.
- The OHLCV `open` fills trades.
- Funding uses entry fill price as notional.
- Mark, index, and premium datasets exist in repo data posture, but `run_backtest()` does not select or consume mark/index streams.

Finding: mark/index mechanics are assumed externally. Current behavior uses the provided OHLCV frame as both execution and marking source. Future packages may need explicit source declarations or optional mark/index inputs, but no such edit is authorized here.

## 15. Bar-Path Assumptions Audit

Current evidence:

- The design header states signal at bar `t` fills at open of `t+1`.
- `test_no_lookahead` verifies future close mutation does not alter past bars.
- Intrabar high/low are required but not used in current execution or liquidation logic.
- Open and close drive all current fill and marking behavior.

Finding: bar-path assumptions are explicit but simplified. The model avoids lookahead but cannot represent intrabar stop/target ordering, high/low path, gap-through behavior, stop-limit behavior, or liquidation timing inside a bar.

## 16. Determinism and Regression Preservation Audit

Current evidence:

- Inputs are UTC-indexed, monotonic, and duplicate-free.
- Execution supports one mode only.
- Results are returned in a frozen dataclass.
- Existing tests cover hand-computed SMA equity, no-lookahead behavior, D2-003A skip behavior, funding cashflow, bounded liquidation, D2-006 gate behavior, and cost-drag edge cases.

Finding: deterministic preservation is an explicit current strength. Future realism edits must retain deterministic outputs for identical inputs, document intentional metric changes, and produce before/after evidence for known fixtures and committed historical-result expectations where package scope requires it.

## 17. Proposed Per-Dimension Modification Scope

| Dimension | Future WP placeholder | Proposed edit files | Proposed sections | Proposed semantic change | Impact | Preserve | Required evidence | Forbidden adjacent changes | Split posture |
|---|---|---|---|---|---|---|---|---|---|
| Fees / exchange constraints | WP-S2c-172 | `lib/backtest.py`; tests only if authorized | `_bps_cost()`, `run_backtest()` fee inputs/fill block, `params_snapshot` | make maker/taker usage explicit; add exchange-filter assumption checks or disclosures if Main authorizes | cost metrics and Gate 5 may change | deterministic fixed assumptions; D2-006 threshold unchanged | unit tests for maker/taker paths, unchanged default regression, full pytest | no runtime broker/exchange/config dependency | bundle because fee mode and exchange constraints share fill admissibility |
| Funding timing / treatment | WP-S2c-173 | `lib/backtest.py`; tests only if authorized | funding precompute/block, result params | clarify or improve funding notional and event handling | funding_paid, equity, cost_drag may change | exact timestamp determinism | event-boundary tests, long/short tests, no missed-event ambiguity | no data fetch, no mark/index path unless separately authorized | standalone due cost impact and candidate sensitivity |
| Slippage / fills / liquidity / order size | WP-S2c-174 | `lib/backtest.py`; `lib/evaluation.py` only if turnover/cost reporting authorized; tests only if authorized | fill block, `_bps_cost()`, trade rows, `turnover()` | add explicit size/capacity/fill assumptions or conservative deterministic model | trades, costs, equity may change | no lookahead, deterministic fill rule | fill-regression matrix, capacity rejection/stress tests, no-lookahead tests | no runtime order engine, no live order semantics | standalone or split if Main wants fill model before liquidity |
| Liquidation / maintenance margin / mark-index | WP-S2c-175 | `lib/backtest.py`; tests only if authorized | liquidation block, optional marking-source inputs, params | define bounded research liquidation and marking assumptions without runtime margin authority | drawdown/equity/trades may change | bounded equity, Phase 1 runtime separation | catastrophic path tests, mark-vs-close fixture tests, historical regression | no D-0001, OMS, risk, runtime, exchange API, or config changes | standalone due protected-boundary adjacency |
| Bar-path assumptions / deterministic regression consolidation | WP-S2c-176 | `lib/backtest.py`, `lib/evaluation.py`, tests only if authorized | execution mode assertion, high/low usage if authorized, regression harness | document or add deterministic bar-path modes and consolidate before/after evidence | execution semantics may change if modes added | current default remains unchanged unless Main approves | no-lookahead, intrabar fixture, current default equivalence, full pytest | no stop/limit runtime order semantics by implication | final consolidation after prior realism dimensions |

## 18. Proposed File/Function/Section Touch Map

Potential later edit map for Main review:

- `lib/backtest.py::BacktestResult`: possible additive reporting fields only if Main authorizes result-surface changes.
- `lib/backtest.py::_bps_cost`: possible cost helper expansion for size, fee side, or explicit notional handling.
- `lib/backtest.py::run_backtest` parameters: possible additive optional parameters for execution/cost/liquidity/marking assumptions, with default-preservation requirements.
- `lib/backtest.py::run_backtest` funding block: possible funding notional and event-boundary clarification.
- `lib/backtest.py::run_backtest` fill block: possible maker/taker, fill price, slippage, size, and admissibility semantics.
- `lib/backtest.py::run_backtest` liquidation block: possible maintenance-margin or mark-price research approximation.
- `lib/backtest.py::params_snapshot`: possible assumption disclosure.
- `lib/evaluation.py::turnover`: possible size-aware turnover if size becomes internal.
- `lib/evaluation.py::cost_drag`: possible preservation tests only unless Main authorizes metric semantic changes.
- `lib/evaluation.py::check_promotion_gates`: should remain untouched unless Main explicitly authorizes D2-006 gate-reporting changes. Current proposal does not require D2-006 threshold edits.

## 19. Proposed Semantic-Change Map

Proposed semantic changes for later review, not approval:

- Make current taker-only fee behavior either explicit and tested, or add deterministic maker/taker path semantics.
- Convert `fee_bps_maker` from unused parameter to either explicitly unused/deprecated disclosure or authorized calculation input.
- Make funding notional semantics explicit, and optionally allow deterministic mark/notional funding if Main authorizes exact source and defaults.
- Add deterministic size/capacity assumptions before any lab-scale result population relies on larger order realism.
- Keep next-bar-open as the default fill rule unless Main authorizes a new mode.
- Preserve equity-floor liquidation as default unless Main authorizes maintenance-margin approximation.
- Add explicit mark/index source semantics only as research-engine inputs, not runtime or exchange behavior.
- Treat high/low intrabar use as a new bar-path mode requiring explicit Main review, not a silent default.

## 20. Proposed Validation Map

Expected validation for future implementation packages:

- Targeted unit tests for each edited behavior.
- Deterministic before/after fixture evidence with default-preservation assertions where defaults should not change.
- Intentional-change evidence where metrics are expected to change.
- `git diff --check` and staged `git diff --cached --check`.
- Exact changed-file scope check with `tools/dev/diff_scope_summary.py` where present.
- Forbidden-path diff check covering `src`, runtime, `configs`, `data`, `.claude`, broker/exchange/order, OMS, reconciliation, risk, safe-mode, kill-switch, dashboards, agents, schemas, validators, query views, and artifacts unless explicitly in package scope.
- `python -m tools.research_query.run --list-views`.
- All discovered `v_integrity_*` views clean.
- `python -m tools.registry.validate_registry`.
- `python -m tools.registry.validate_experiment_artifacts`.
- `python -m tools.registry.validate_outcome_ledger`.
- `python -m tools.registry.validate_reconciliations`.
- Targeted pytest for `tests/test_backtest.py`, `tests/test_backtest_liquidation.py`, `tests/test_evaluation.py`, and `tests/test_evaluation_cost_drag.py` when relevant.
- Repo-conventional scoped research pipeline pytest.
- Full pytest for any T3 implementation or protected-path-adjacent package.

## 21. Proposed WP-S2c-172+ Package Split

Proposed split for Main review:

1. WP-S2c-172: fees and exchange-constraint disclosure / deterministic assumptions.
2. WP-S2c-173: funding timing and treatment.
3. WP-S2c-174: slippage, fills, liquidity, and order-size realism.
4. WP-S2c-175: liquidation, maintenance-margin approximation, and mark/index assumptions.
5. WP-S2c-176: bar-path assumptions and deterministic regression consolidation.

This split is proposed because each package can alter equity, cost, trade, or gate-input metrics in a different way. Keeping them separate reduces review ambiguity and makes before/after evidence attributable.

These packages are not draftable until Main reviews this exact protected-path scope and authorizes the next specific package or capsule set.

## 22. Protected-Path Preservation Wording

Proposed wording for Main report-back:

Any future backtest-realism implementation package must preserve Phase 1 paper runtime protection, deterministic execution, D-0001, D2-008, OMS boundaries, reconciliation boundaries, kill-switch boundaries, Tier 4 boundaries, Track 3 paused state, runtime / paper-live separation, permanent human gates, and locked decisions. No broker/exchange/order behavior, OMS/reconciliation/risk/safe-mode/kill-switch behavior, config behavior, dependency behavior, data behavior, AUTO bridge behavior, A2C-003 behavior, Track 3 / WP-S2c-140 behavior, or protected-path behavior may change by implication. Any protected-path contact requires explicit Main authorization, exact package scope, stop-condition handling, targeted tests, before/after deterministic evidence, and full pytest.

## 23. Explicit No-Edit Statement

WP-S2c-171 did not edit `lib/backtest.py`, `lib/evaluation.py`, tests, schemas, validators, query views, artifacts, tools, runners, configs, data, runtime, paper/live, broker/exchange/order, OMS, reconciliation, risk, safe-mode, kill-switch, `.claude/`, dashboards, agents, prompts, or protected paths.

Read-only inspection produced proposed scopes only. Proposed modifications are not approved edits.

## 24. Main Surfacing Requirements

Side must report back to Main with:

- the current surface map;
- the realism findings by dimension;
- exact proposed files/functions/sections for future edits;
- expected semantic changes;
- expected validation profile;
- proposed WP-S2c-172+ split;
- protected-path preservation wording;
- unresolved questions about maker/taker behavior, funding notional, size/capacity, maintenance margin, mark/index source, and intrabar path modes.

## 25. Stop / Escalation Findings

No stop condition was encountered during this package.

Escalation items for Main review before implementation:

- Future edits probably touch `lib/backtest.py`, which is implementation and protected-path-adjacent research-engine code.
- Future changes may alter historical backtest metrics and D2-006 gate inputs even if D2-006 thresholds remain unchanged.
- `fee_bps_maker` currently appears as an accepted and recorded parameter but is not used in calculation.
- OHLCV `volume`, `high`, and `low` are required but mostly unused for realism.
- Liquidation currently means zero-equity ruin, not exchange maintenance-margin liquidation.

## 26. Deferred or Rejected Modifications

Deferred:

- exact formulas, thresholds, fee tiers, funding notional rules, capacity limits, maintenance margin schedules, mark/index source fields, intrabar path models, regression harness mechanics, storage paths, schemas, validators, query views, and artifact changes.

Rejected for this package:

- implementation edits;
- direct approval of any proposed edit;
- WP-S2c-172+ automatic drafting;
- importing runtime broker/exchange/order logic into the research backtester by implication;
- changing D2-006, D2-007, REC-5, Scope 6, D-0001, D2-008, Phase 1 runtime protection, OMS, reconciliation, kill-switch, Tier 4 boundaries, Track 3 paused state, permanent human gates, or locked decisions.

## 27. Future Package Dependencies

WP-S2c-172+ depend on:

- WP-S2c-171 merge;
- Side report-back to Main;
- Main review of the exact protected-path edit scope;
- explicit Main authorization of the next implementation package or capsule set;
- package-specific validation requirements;
- no stop trigger on refreshed main.

Any implementation package must inspect current `lib/backtest.py`, `lib/evaluation.py`, tests, current docs, and current changed files again. This document is not a substitute for refreshed repo truth.

## 28. Validation Posture

This package uses T1-doc-narrow validation unless current repo truth requires broader validation.

Required validation is scope and repo-consistency validation, not implementation validation:

- diff whitespace checks;
- exact changed-file scope check;
- forbidden-path diff check;
- query-view listing;
- all discovered `v_integrity_*` views clean;
- registry / experiment artifact / outcome ledger / reconciliation validators;
- scoped pytest covering research pipeline, registry, artifact, outcome, reconciliation, and integrity surfaces;
- full pytest only if current repo truth, validation failure, or package discovery requires it;
- staged diff checks;
- clean final status.

## 29. Next-Package Posture

After WP-S2c-171 merges, Side must report back to Main with the exact protected-path edit scope before any WP-S2c-172+ draft.

WP-S2c-172+ remain unauthorized until Main reviews and authorizes a specific edit package or capsule set.

Implementation edits remain unauthorized.
