# Strategy Spec Grammar Tranche Checkpoint

## 1. Scope

WP-12hb / WP-S2c-181 is a Tier 1 documentation-only tranche checkpoint and report-back preparation package.

It closes the WP-S2c-177 through WP-S2c-180 Strategy Spec grammar tranche as complete-as-built and prepares concise repo-grounded facts for Side to report back after merge.

This package creates this checkpoint document and updates `docs/project_status.md` only.

It does not implement anything and does not authorize any post-tranche work.

## 2. Repo-truth basis

Repo truth for this checkpoint is refreshed `main` at `391a192c788781fcf001b64cc76c43871c3a5561`, the PR #357 / WP-12ha / WP-S2c-180 merge commit.

Pre-edit checks confirmed:

- WP-S2c-180 is merged on refreshed `main`.
- `docs/project_status.md` records the WP-12ha / WP-S2c-180 branch-state entry.
- No open PR was reported before this package branch was created.
- No WP-S2c-181 branch or PR was found before this package branch was created.
- This checkpoint document did not exist before this package.
- The WP-S2c-177 design doc, WP-S2c-178 schema, WP-S2c-179 validator, and WP-S2c-180 query-layer surfaces exist.
- The current repo contains no canonical Strategy Spec instances.

## 3. Completed tranche surfaces

The completed tranche consists of:

- WP-S2c-177 / WP-12gx: Strategy Spec artifact grammar design.
- WP-S2c-178 / WP-12gy: Strategy Spec schema.
- WP-S2c-179 / WP-12gz: Strategy Spec validator.
- WP-S2c-180 / WP-12ha: read-only Strategy Spec query visibility.

## 4. Tranche output summary

WP-S2c-177 created the Strategy Spec grammar design under the WP-S2c-151 Strategy Spec / DSL lock and WP-S2c-166 expressiveness-readiness posture.

WP-S2c-178 created `research/schemas/strategy_spec.schema.json` as a non-executing Strategy Spec schema for human-review planning only.

WP-S2c-179 created `tools/registry/validate_strategy_specs.py` and focused validator tests for future Strategy Spec artifacts.

WP-S2c-180 extended the read-only research query layer so future `research/strategy_specs/*.strategy_spec.json` files are visible when present, and absent/empty Strategy Spec corpus state is represented as an empty typed relation.

## 5. What is now available

The repo now has:

- a non-executing Strategy Spec design;
- a JSON Schema with a closed operator enum: `gt`, `gte`, `lt`, `lte`, `eq`, `neq`, `crosses_above`, `crosses_below`, `in_set`, `is_true`, and `is_false`;
- a schema-enforced condition depth bound, `max_condition_group_depth=3`;
- a D2-006-style `<=5` free-parameter cap;
- validator hard checks for the future Strategy Spec corpus;
- read-only query visibility for overview, parameter, condition-group, backtest-assumption, and integrity inspection.

## 6. Zero-instance / non-execution posture

The tranche remained zero-instance and non-executing.

It created no Strategy Spec instances, examples, committed repo-data fixtures, variant manifests, sweep plans, runners, result populations, advisory packets, dashboards, agents, paper/live bridges, runtime changes, or candidates created from Strategy Specs.

Tests use temporary Strategy Spec fixtures only.

## 7. Locked non-authority boundaries

Strategy Spec remains a typed, declarative, non-executable, side-effect-free, host-data-bounded, human-review planning surface.

Strategy Spec is not a candidate, evidence, approval, recommendation, ranking, scoring, readiness, transition, sweep, paper/live, runtime, or human-gate execution authority.

Approval for variant planning, where the schema can represent it as a status/review posture, is descriptive human-review planning scope only. It does not approve a candidate, EXP, sweep, ranking, recommendation, paper/live path, runtime path, or gate satisfaction.

## 8. Strategy Spec grammar semantics now established

The schema now establishes the current Strategy Spec shape:

- identity, status, and non-execution declaration;
- provenance and source references;
- instruments and market assumptions;
- timeframe and host-data references;
- entry logic, exit logic, risk model, and filters;
- bounded condition groups and declarative conditions;
- free-parameter declarations with the current `<=5` cap;
- constraints, review posture, lineage, hash-pinning, pre-registration support, and backtest-realism assumptions.

The grammar remains declarative. It creates no parser, compiler, host interpreter, executable expression language, runner contract, or storage authority beyond future optional Strategy Spec files being readable by the existing query layer.

## 9. Validator and query visibility now established

The Strategy Spec validator hard-checks:

- schema validity;
- closed operators;
- exact current `max_condition_group_depth=3`;
- actual condition-group depth `<=3`;
- D2-006-style `<=5` free-parameter cap;
- non-executable and non-authority flags;
- forbidden executable key names;
- filename / ID consistency;
- duplicate Strategy Spec IDs;
- unsafe host-data URL or path-like references.

The query layer provides read-only visibility and integrity views only. It does not validate, approve, recommend, rank, score, transition, satisfy gates, create readiness, create variants or sweeps, or authorize paper/live/runtime behavior.

## 10. What remains unimplemented

The following remain unimplemented and require later explicit authorization if pursued:

- variant manifest and sweep grammar;
- Strategy Spec instance policy, if Main later authorizes any instances;
- candidate generation and paper-candidate queue design;
- offline runner and result-population implementation;
- robustness, DSR, PSR, MinTRL, and Monte Carlo design or implementation;
- advisory packet and dashboard surfaces;
- agent-assist boundaries and any agent implementation;
- multi-strategy portfolio and allocator architecture;
- paper/live bridges, separately authorized later.

## 11. User end-state requirement for Main consideration

The user wants the Strategy Research Lab to become an always-on, non-authoritative strategy-improvement system. Automated means automated self-assessment, candidate generation, testing, comparison, and briefing, not automatic promotion or live deployment.

Desired future capabilities to keep visible for roadmap integration:

- periodically assess research, paper, and eventually live strategy performance;
- detect weak, strong, degrading, and improving strategies;
- generate bounded Strategy Spec variants and parameter-range changes;
- test candidates through backtests, walk-forward/OOS validation, robustness checks, Monte Carlo where appropriate, and later paper trading;
- maintain a continuous queue of paper candidates;
- support multiple strategies running in parallel after proper architecture exists;
- preserve per-strategy and per-variant lineage from idea to Strategy Spec to variant to test to result to review to paper/live decision;
- log per-strategy PnL, fees, funding, slippage, drawdown, exposure, trade count, win rate, risk-adjusted metrics, robustness, Monte Carlo outputs, and rejected or failed variants;
- produce dashboard and briefing views showing parameter sensitivity, robustness, cost/funding/slippage sensitivity, timeframe sensitivity, stable regions, and fragile regions;
- eventually support a central allocator / portfolio layer so multiple strategies do not conflict or exceed account/risk limits;
- keep all promotion, risk-change, paper/live, and live-deployment decisions human-approved.

This is an end-state roadmap requirement for Main consideration. It is not implementation authorization and is not a request to implement all of it immediately.

## 12. Descriptive next-roadmap options

Unranked descriptive options after this checkpoint include:

- proceed to variant manifest / sweep grammar;
- add Strategy Spec instance policy / first manually reviewed spec posture, if Main wants it before variants;
- define continuous lab self-assessment / candidate queue design;
- define multi-strategy portfolio / allocator architecture;
- proceed to offline runner / result-population implementation planning;
- proceed to robustness / DSR / PSR / MinTRL / Monte Carlo design;
- proceed to dashboard / briefing design;
- defer and ask for consolidation;
- hold.

No option is selected, ranked, recommended, or authorized by this checkpoint.

## 13. What is not authorized

WP-S2c-181 does not authorize schema changes, validator changes, query-view changes, code changes, test changes, tools, fixtures, Strategy Spec instances, examples, variant manifests, sweeps, runners, result populations, advisory packets, dashboards, agents, prompts, `.claude/`, runtime behavior, paper/live behavior, protected-path work, approval, readiness, recommendation, transition, ranking/scoring, candidate creation, EXP creation, or human-gate execution.

## 14. Required next authority

Side must report back to Main after this checkpoint merges.

No WP-S2c-182 or next roadmap package may be drafted until Main provides direction.

The Main report-back should ask Main to choose the next direction and provide as many exact WP capsules as possible.

The Main report-back should include the user's always-on non-authoritative strategy-improvement end-state requirement for roadmap consideration.

Any implementation, schema, validator, query, artifact, runner, dashboard, agent, paper/live, runtime, protected-path, or authority-changing work requires explicit future authorization.

## 15. Validation profile

This package uses T1-doc-major-checkpoint validation because it closes a completed Strategy Spec grammar tranche and updates `docs/project_status.md`.

Full pytest is required unless repo convention or local environment makes it impossible.

Validation must prove exact changed-file scope, forbidden-path cleanliness, query-view and integrity health, registry/artifact/outcome/reconciliation validator health, Strategy Spec validator health, scoped pytest health, full pytest health, and clean final status.

## 16. Validation

Pre-edit validation and repo-truth discovery confirmed the package could proceed from refreshed `main`:

- refreshed `main` at `391a192c788781fcf001b64cc76c43871c3a5561`;
- WP-S2c-180 merged and recorded in `docs/project_status.md`;
- no open PR reported;
- no WP-S2c-181 branch or PR found before branch creation;
- checkpoint target absent before branch creation;
- required Strategy Spec tranche surfaces present;
- current repo has no canonical Strategy Spec instances.

Package validation results are recorded in the execution report-back and PR.
