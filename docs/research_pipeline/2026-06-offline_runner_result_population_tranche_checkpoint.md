# Offline Runner / Result-Population Tranche Checkpoint

## 1. Scope of Item 5

WP-12hm / WP-S2c-192 is a documentation/checkpoint package only.

It closes roadmap item 5, the offline runner / result-population tranche, as complete-as-built through WP-S2c-191 and surfaces the next Main-owned gate: item 6 robustness support plus the first canonical sweep-run question.

Item 5 now provides the repo with:

- a design surface for offline runner / result-population posture;
- a result-population schema;
- a result-population validator;
- a build-and-test-only offline runner;
- read-only result-population query visibility;
- no canonical result-population corpus.

This checkpoint creates this document and updates `docs/project_status.md` only. It does not implement item 6, authorize item 6, run the offline runner, run a canonical sweep, create result-population instances, or create authority.

## 2. Repo-Truth Basis

Pre-edit repo-truth discovery confirmed:

- PR #368 / WP-12hl / WP-S2c-191 is merged.
- `docs/project_status.md` on refreshed `main` records the WP-S2c-191 handoff.
- No open PRs existed before this package branch was created.
- No open WP-S2c-192 / WP-12hm PR existed before this package branch was created.
- The expected item 5 surfaces exist on `main`.
- No `research/result_populations/` canonical corpus exists.
- No active Main/Karl redirect for this package was present in the WP-S2c-191 handoff.

## 3. Completed Packages

The completed item 5 chain is:

- WP-S2c-187: design opening.
- WP-S2c-188: result-population schema.
- WP-S2c-189: result-population validator.
- WP-S2c-190: build-and-test-only offline runner.
- WP-S2c-191: read-only result-population query views.
- WP-S2c-192: this checkpoint.

## 4. What Now Exists In Repo

Concrete repo surfaces now present:

- `docs/research_pipeline/2026-06-offline_runner_result_population_design.md`
- `research/schemas/result_population.schema.json`
- `tools/registry/validate_result_populations.py`
- `tests/test_validate_result_populations.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/research_runner/__init__.py`
- `tests/test_offline_research_runner.py`
- result-population relation registration in `tools/research_query/query_layer.py`
- result-population read-only descriptive and integrity views in `tools/research_query/views.sql`
- query-layer tests in `tests/test_research_query.py`

## 5. WP-S2c-190 Runner Facts To Preserve For Main

Facts to preserve for the next Main report-back:

- runner uses existing `lib.backtest.run_backtest(...)` read-only;
- `lib/backtest.py` and `lib/evaluation.py` remained unchanged;
- runner defaults to dry-run/no-write;
- writes require explicit write flag plus caller-supplied non-canonical output directory;
- canonical `research/result_populations/` writes are disabled/rejected;
- tests use fixture/synthetic data only;
- result-population IDs and identity-hash-scoped output are deterministic for identical inputs;
- output validates through `tools.registry.validate_result_populations`;
- complete population and committed denominator are preserved;
- per-variant errors continue as rows;
- infrastructure abort emits `not_attempted` rows for unattempted committed variants;
- no first canonical sweep was run or authorized.

## 6. WP-S2c-191 Query-Layer Facts To Preserve For Main

Facts to preserve for the next Main report-back:

- read-only result-population relation registration exists;
- absent/empty result-population corpus compiles through a typed empty relation;
- descriptive views exist for overview, parent lineage, denominator, outcome counts, variant rows, errors, data coverage, backtest assumptions, identity/audit split, append-only ledger, non-authority, and execution context;
- integrity views exist for denominator, outcome counts, missing rows, unknown outcome categories, audit envelope in identity scope, non-authority, canonical evidence, append-only posture, offline boundary, canonical write indication, authority-key markers, and parent hash-chain mismatch;
- tests use temporary result-population fixtures only;
- query views do not run the offline runner and do not create artifacts.

## 7. What Remains Unauthorized

All of the following remain unauthorized:

- first canonical sweep run;
- canonical result-population output;
- real repo-data result-population corpus;
- item 6 robustness computation;
- DSR / PSR / MinTRL computation;
- Monte Carlo / bootstrap computation;
- parameter sensitivity / stability maps;
- cost / funding / slippage stress computation;
- dashboard/advisory ranking logic;
- paper trading behavior;
- live trading behavior;
- runtime/protected-path behavior;
- multi-strategy allocator;
- always-on lab execution;
- approval/recommendation/ranking/readiness/transition/gate authority.

## 8. Boundary Confirmations

This checkpoint confirms:

- no paper/live contact;
- no broker/exchange/order contact;
- no runtime/protected-path change;
- no OMS/reconciliation/risk/safe-mode/kill-switch change;
- no canonical evidence replacement;
- no EXP / REP / trial-log / OL / REC / DEC replacement;
- no authority was created.

## 9. Known Next Main Decisions

The next gate is Main-owned, not Side-owned.

Known Main decisions include:

- item 6 sequencing;
- first canonical sweep-run authorization or deferral;
- whether robustness/DSR/PSR/MinTRL starts next;
- whether Monte Carlo/bootstrap starts next;
- whether parameter sensitivity/stability maps start next;
- whether cost/funding/slippage stress support starts next;
- whether always-on lab / candidate queue / multi-strategy end-state should be locked now or deferred.

These options are not ranked here. This checkpoint does not recommend a preferred sequence.

## 10. Required Post-Merge Posture

After WP-S2c-192 merges, Side must report back to Main before drafting WP-S2c-193 or any item 6 implementation package.

First canonical sweep authorization remains separate and Main-owned.

## 11. Non-Authority Statement

Result-population schema, validator, runner, and query surfaces remain research/workbench surfaces only.

They do not approve, recommend, rank, create readiness, transition strategy state, satisfy gates, replace canonical evidence, or create paper/live/runtime/protected-path authority.

## 12. Validation Profile

This package is documentation/checkpoint-only. Validation should prove exact changed-file scope, no forbidden-scope changes, query-view listing health, clean integrity views, registry/artifact/outcome/reconciliation validator health, diff hygiene, and staged diff hygiene.

Full pytest is not required for this doc-only checkpoint unless repo convention, local preflight, or a changed-file side effect indicates it.
