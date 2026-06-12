# Sizing Realism Implementation Impact Map

## Status / Authority Boundary

This is a docs-only implementation-readiness map for the sizing-realism design
selected in `WP-REALISM-SIZING-01a`. It inspects implementation surfaces
read-only and does not change code, schemas, validators, tests, Strategy Specs,
Variant Manifests, sweep plans, result populations, data, dashboard
implementation, candidate registry files, runtime, paper/live, OMS/risk,
broker/exchange, or protected paths.

This document does not authorize `WP-REALISM-SIZING-01c`, rerun `RP-6688`,
register a candidate, rank variants, claim readiness, promote a strategy, or
create paper/live/runtime authority.

## Source Design And Repo Facts

Source design:

- `docs/research_pipeline/2026-06-realism_sizing_leverage_design.md`
- `docs/status_entries/WP-REALISM-SIZING-01a.md`

Relevant source diagnostic:

- `docs/research_pipeline/2026-06-rp6688_sizing_leverage_diagnostic.md`
- `docs/status_entries/WP-RP6688-SIZING-DIAG-01.md`
- `research/result_populations/RP-6688.result_population.json`

Repo-truth facts inspected for this map:

- `WP-REALISM-SIZING-01a` selected Option 1, runner-side
  fixed-but-equity-aware sizing, for further planning only.
- Option 1 resolves a fixed order size before calling the current backtester:
  `resolved_order_size = target_leverage * initial_equity / reference_price`.
- `tools/research_runner/run_offline_sweep.py` currently calls
  `run_backtest()` with `initial_equity=10_000.0` and `order_size=1.0` in the
  synthetic and canonical 15m paths.
- `lib/backtest.py` already accepts `order_size` and applies it consistently
  to PnL, fee cost, slippage cost, funding notional, trade notional, and
  liquidation checks.
- `lib/evaluation.py` consumes backtest outputs and trade notionals; it does
  not own the current fixed-size runner input.
- `research/schemas/result_population.schema.json` currently allows
  assumption-string disclosure through `backtest_assumption_summary`, but it
  does not define structured fields such as `sizing_model_id`,
  `target_leverage`, `reference_price`, `resolved_order_size`, or
  cost-to-equity ratios.
- Current result-population identity scopes include
  `backtest_assumption_summary`, so structured sizing metadata would need to
  be included in identity-bearing scope if it changes scientific meaning.

## Implementation Readiness Answers

1. Files likely touched for a runner/spec-side implementation of Option 1:
   `tools/research_runner/run_offline_sweep.py` and
   `tests/test_offline_research_runner.py` for the smallest runner-only
   resolution slice. Strategy Spec or sweep-plan schema/validator files may be
   needed only if target leverage is declared in parent artifacts rather than
   a runner argument or closed runner configuration. Result-population schema,
   validator, query, dashboard, and tests are likely needed only when
   structured sizing metadata is stored or surfaced.

2. Files that remain untouched for runner/spec-side Option 1:
   `lib/backtest.py` and `lib/evaluation.py` are not required for the first
   fixed-size resolution slice. Runtime, paper/live, OMS/risk, broker/exchange,
   data acquisition, and protected execution paths remain untouched.

3. Option 1 without `lib/backtest.py`:
   Yes. The current backtester already accepts a positive fixed `order_size`.
   A runner can resolve that value before invoking `run_backtest()`.

4. Option 1 without `lib/evaluation.py`:
   Yes for the first runner/spec-side slice. Existing evaluation functions
   consume backtest outputs and trade notionals after sizing is resolved.

5. Schema changes:
   Runner-only calculation can be prototyped without schema changes if no
   canonical structured sizing metadata is written. Canonical result
   populations that record `sizing_model_id`, `target_leverage`,
   `reference_price`, `resolved_order_size`, or cost-to-equity ratios require
   result-population schema changes. Strategy Spec or sweep-plan schema changes
   are required only if target leverage or sizing basis becomes an artifact
   declaration instead of a runner input.

6. Validator changes:
   Runner-only calculation can be tested without validator changes. Any new
   structured Strategy Spec, sweep-plan, or result-population fields require
   validator changes and accept/reject tests.

7. Runner changes:
   Yes. Option 1's first implementation slice is primarily a runner change:
   derive `reference_price`, validate target leverage and price, calculate
   `resolved_order_size`, pass it to `run_backtest()`, and preserve
   deterministic identity behavior.

8. Identity-hash changes:
   Yes for any new canonical result population generated under the new sizing
   model. Sizing model and resolved sizing facts must affect identity-bearing
   payload. Existing result populations and old identity hashes remain
   unchanged.

9. Query/view/dashboard changes:
   Not required for the first runner-only resolution slice if no structured
   fields are stored. Required later if sizing metadata is added to result
   populations and must be visible in query surfaces or display-only dashboard
   Results data.

10. Old result-population validation:
    Existing result populations must remain valid. No old result population is
    reinterpreted under a new sizing model.

11. Tests for first implementation slice:
    See the test plan below. The smallest slice needs runner-focused tests for
    leverage-to-size resolution, reference-price selection/fallback, invalid
    inputs, deterministic output, identity inclusion, no canonical artifact
    mutation, and unchanged old result-population validation.

12. Smallest safe implementation split:
    Implement runner/spec-side sizing resolution first, then structured
    result/reporting metadata separately, then consider lib-core dynamic sizing
    only if Main/Karl explicitly reviews that protected backtest-core
    methodology change.

13. Protected-path risk:
    Present around `lib/backtest.py` and `lib/evaluation.py` only if future
    work moves from fixed runner-resolved sizing to dynamic compounding
    equity-relative sizing or changes core cost/turnover/evaluation semantics.

14. Backward-compatibility risk:
    Present in identity scope, result-population schema evolution, query or
    dashboard display of mixed sizing models, and any regeneration of
    STRAT-SPEC-0002 / VM-0002 / SWEEP-PLAN-0002 under new sizing.

15. Main/Karl review before 01c:
    Main/Karl should review the exact declaration surface for target leverage,
    reference-price basis, whether structured metadata is part of the first
    implementation slice, identity-scope changes, query/dashboard surfacing
    timing, and confirmation that `lib/` remains untouched for 01c.

## File-Level Impact Map

| File / surface | Expected touch | Why | Risk class | Authorized now | Candidate future package | Validation needed |
|---|---:|---|---|---|---|---|
| `tools/research_runner/run_offline_sweep.py` | yes | Resolve `target_leverage * initial_equity / reference_price`, pass resolved `order_size`, and include sizing facts in identity-bearing output if scoped. | runner/spec-side | no | 01c runner/spec-side sizing resolution; possibly 01d metadata | Focused runner tests, determinism, fail-closed invalid inputs, no canonical artifact mutation |
| `lib/backtest.py` | no | Current contract already accepts fixed positive `order_size` and applies it to PnL, costs, funding notional, and liquidation checks. | backtest-core protected | no | Future lib-core package only if dynamic compounding sizing is chosen | Backtest-core regression, no-lookahead, liquidation, cost, funding, compatibility |
| `lib/evaluation.py` | no | Evaluation consumes trades and equity after backtest; first Option 1 slice does not require metric semantics changes. | backtest-core protected | no | Future lib-core or metric package only if turnover/cost metrics change | Evaluation regression and compatibility tests |
| `research/schemas/strategy_spec.schema.json` | maybe | Needed only if target leverage or sizing basis is declared in Strategy Spec instead of runner configuration. Current `risk_model` and `backtest_realism_assumptions` are not enough for structured sizing resolution. | schema/validator | no | Future declaration-surface package if artifact-declared sizing is chosen | Schema meta-validation and accept/reject tests |
| `research/schemas/result_population.schema.json` | maybe | Needed if canonical outputs store structured `sizing_model_id`, target leverage, reference price, resolved size, or cost-to-equity fields rather than assumption strings. | schema/validator | no | 01d result/reporting metadata | Schema meta-validation, old corpus validation, new fixture validation |
| `tools/registry/validate_strategy_specs.py` | maybe | Needed only if Strategy Spec grammar gains structured sizing declarations. | schema/validator | no | Future declaration-surface package if needed | Accept/reject tests, non-authority checks |
| `tools/registry/validate_result_populations.py` | maybe | Needed if result-population schema gains structured sizing metadata or new identity-scope rules. | schema/validator | no | 01d result/reporting metadata | Corpus validator, old result populations valid, new fixture reject/accept cases |
| `tests/test_offline_research_runner.py` | yes | Primary test home for runner-side resolution, reference price, determinism, write gates, and canonical directory immutability. | runner/spec-side | no | 01c runner/spec-side sizing resolution | Focused pytest for runner |
| `tests/test_research_query.py` | maybe | Needed if query surfaces expose sizing metadata or integrity views validate sizing context. | query/dashboard | no | 01d or later query visibility package | Query unit tests and integrity views |
| `docs/project_status.md` | yes | Compact branch-state pointer for this docs-only map and future packages. | docs-only | no for implementation; yes in this WP | This WP; future package pointers | Diff scope and final rebase |
| `docs/research_pipeline/*` | yes | This impact map and README index are docs-only package outputs. | docs-only | no for implementation; yes in this WP | This WP; future design/status docs | Diff check and semantic audit |
| `research/result_populations/*` | no | Existing result populations, including `RP-6688`, remain valid and unchanged; future new sizing runs require new RP IDs and hashes. | canonical artifact | no | Future separately gated regeneration package | Corpus validation, denominator preservation, append-only proof |
| Dashboard data / collector files | maybe | Required only if structured sizing metadata should appear in display-only Results pages. Current dashboard consumes validated `dashboard_data.v1` and currently targets RP-4492 facts. | query/dashboard | no | Later dashboard surfacing package if Main authorizes | Dashboard schema/validator/generator/renderer tests |
| Runtime / paper-live / OMS / risk / broker / exchange paths | no | Option 1 is offline research-runner sizing realism only and must not contact execution paths. | runtime/protected | no | None in this runway | Forbidden-scope proof |

## Protected-Path Classification

`lib/backtest.py`: not required for Option 1 implementation.

`lib/evaluation.py`: not required for Option 1 implementation.

Rationale:

- Option 1 preserves the current fixed-size backtester contract.
- The runner can calculate a different fixed `order_size` before calling
  `run_backtest()`.
- `lib/backtest.py` already validates positive `order_size` and uses it in the
  exact places that Option 1 needs.
- `lib/evaluation.py` can continue consuming the resulting equity and trade
  outputs for the first slice.

Protected-path risk becomes active only if a future package changes the
backtester from fixed runner-resolved sizing to dynamic current-equity sizing,
changes core cost mechanics, or changes evaluation semantics.

## Proposed Future Implementation Split

This split is a future option set, not authorization.

### Future 01c Candidate - Runner/Spec-Side Sizing Resolution

Purpose:

Add a runner-side sizing resolution surface that converts target leverage,
initial equity, and reference price into fixed `order_size` before calling the
current backtester.

Potential files if Main later authorizes:

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- possibly Strategy Spec or sweep-plan schema/validator files if target
  leverage is artifact-declared
- possibly result-population schema/validator files if sizing metadata is
  stored in the same slice
- docs/status pointers

Boundary:

No `lib/backtest.py` or `lib/evaluation.py` change is needed for this slice if
it remains fixed runner-resolved sizing.

### Future 01d Candidate - Result/Reporting Metadata

Purpose:

Record sizing model, reference price, resolved order size, and cost-to-equity
fields in result populations.

Potential files if Main later authorizes:

- `research/schemas/result_population.schema.json`
- `tools/registry/validate_result_populations.py`
- `tools/research_runner/run_offline_sweep.py`
- `tests/test_research_query.py`
- `tests/test_offline_research_runner.py`
- dashboard collector/contract/renderer files only if Main authorizes
  display-only dashboard surfacing

Boundary:

This package should preserve old result-population validation and avoid
retroactive reinterpretation.

### Future Lib-Core Package, Only If Needed

Purpose:

Dynamic compounding equity-relative sizing inside the backtest core.

Classification:

Protected backtest-core methodology change. It requires explicit Main/Karl
review before drafting.

Potential files:

- `lib/backtest.py`
- `lib/evaluation.py`
- backtest/evaluation tests
- schema/result contract changes if needed

Boundary:

This path is not part of the smallest Option 1 implementation split.

## Future Test Plan

Future code-touching packages should include tests for:

- target leverage resolution into fixed order size;
- first executable bar reference-price selection;
- first valid close fallback for no-trade or no-executable-bar contexts;
- invalid target leverage rejection;
- zero, negative, missing, or non-finite reference price rejection;
- deterministic resolved order size for identical inputs;
- identity-hash inclusion of sizing model and resolved sizing fields whenever
  those fields affect canonical result-population meaning;
- old result populations remain valid;
- `RP-6688` remains unchanged;
- no synthetic fixture fallback in canonical real-data mode;
- no hidden mutation of `research/result_populations/`;
- denominator preservation;
- cost-to-equity, fee-to-equity, slippage-to-equity, and funding-to-equity
  fields if added;
- full code-touching regression commands for the package class, including
  focused pytest, result-population validation, query list/integrity views,
  diff-scope summary, and final full pytest if the future package class
  requires it.

## Migration / Backward Compatibility Plan

Existing result populations remain valid.

No old result population is reinterpreted.

New sizing model uses new result populations and new identity hashes.

Comparisons across old and new sizing models require visible sizing-model
context.

Any regenerated STRAT-SPEC-0002 / VM-0002 / SWEEP-PLAN-0002 run under new
sizing must produce a new RP ID and preserve original `RP-6688`.

Old fixed-order-size populations may remain queryable beside future
equity-aware populations only when model context is visible enough to prevent
cross-model confusion.

## Main / Karl Review Items Before 01c

Review items:

- exact source of `target_leverage`: runner flag/config, Strategy Spec,
  sweep plan, or another closed artifact surface;
- exact `reference_price` basis and fallback order;
- whether 01c should store structured result-population sizing metadata or
  leave that to 01d;
- identity-scope treatment for sizing model and resolved sizing facts;
- whether query/dashboard visibility is deferred or included in a later
  display-only package;
- confirmation that 01c remains runner/spec-side and does not touch
  `lib/backtest.py` or `lib/evaluation.py`;
- validation profile for a code-touching runner package.

## Authority / Finality Audit Notes

This document uses terms such as implementation, validation, candidate,
readiness, promotion, paper, live, `lib/backtest.py`, and `lib/evaluation.py`
only for impact-map classification, forbidden-scope statements, future
not-authorized split planning, source artifact references, validation command
names, or non-authority caveats.

No wording in this document authorizes 01c, result regeneration, ranking,
readiness, promotion, paper/live/runtime behavior, or protected-path changes.
