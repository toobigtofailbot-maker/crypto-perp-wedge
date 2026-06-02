# Result Population / Storage Design

## 1. Scope

WP-S2c-156 / WP-12gc is a Tier 1 documentation-only substantive design
package.

It defines result population / storage design for future Strategy Research Lab
sweeps.

It creates only this design document, updates `docs/research_pipeline/README.md`
with one additive index entry, and updates `docs/project_status.md`.

It creates no result artifact, result-storage path, result population, metrics
table, schema, validator, query view, parser, compiler, code, test, fixture,
implementation, sweep, backtest, optimizer run, strategy execution, or
authority.

## 2. Authorization and repo-truth basis

WP-S2c-155 defined sweep orchestration and handed off WP-S2c-156 as the
default next sequential lab package.

WP-S2c-154 opened variant-generation design.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Result-population problem statement

The lab eventually needs to preserve the full population of outputs from an
authorized sweep.

The dangerous failure mode is retaining only winners, suppressing failures, or
losing invalid, excluded, or errored variants.

Another failure mode is creating a parallel result store that bypasses EXP /
REP, trial-log, OL, REC, and DEC.

The design problem is to define result-population and storage requirements
before any result artifact, storage path, schema, or execution implementation
exists.

## 4. Design objective

Result population means the future complete record of all variants and run
outcomes belonging to an authorized sweep or sweep-like research run.

This design defines storage questions that must be answered before artifacts
are created.

It preserves anti-overfit review, multiple-testing accounting, lineage, and
evidence-chain compatibility.

Execution, storage creation, schema creation, and result aggregation remain
unauthorized here.

## 5. Result population posture

A result population is a future evidence-adjacent or evidence-input surface.

It is not itself a recommendation.

It is not ranking authority.

It is not candidate approval.

It is not paper/live readiness.

It is not promotion or transition authority.

It becomes meaningful only through later authorized execution and canonical
evidence routing.

This package creates no result population instance.

## 6. Relationship to lab lifecycle

Result population belongs after future authorized sweep execution and before
anti-overfit / ranking review.

It consumes results from future sweep orchestration.

It must preserve lineage from idea to concept to Strategy Spec to variant
population to sweep plan or run to result population to future evidence.

It must not bypass EXP / REP, trial-log, OL, REC, DEC, D2-006, D2-007, REC-5,
Phase 9 / D2-011, Scope 6, or human gates.

## 7. Sweep-result dependency

Result population depends on a future authorized sweep or run.

Because no real sweep plan, run manifest, or result set exists, this package
must not create result artifacts or assume concrete fields.

If sweep or run manifest storage or schema remains unresolved, WP-S2c-156
records dependencies only.

## 8. Population completeness requirements

Future result population design must preserve:

- all attempted variants;
- variants not attempted and why;
- failed variants;
- invalid variants;
- excluded variants;
- errored variants;
- aborted runs;
- data-unavailable runs;
- timeout or resource-failure cases;
- variants filtered before execution and why;
- successful variants;
- all material metadata required to interpret the population.

These are design requirements only. They are not schema fields.

## 9. Failure, exclusion, invalid, and error retention

Failures must not be hidden to improve apparent performance.

Exclusions must preserve pre-result rationale.

Invalid combinations must preserve reason and origin.

Execution errors must be distinguishable from strategy underperformance.

Aborts and amendments must not erase original population membership.

Result populations must make survivorship bias visible.

## 10. Metric preservation requirements

Future result population design should preserve enough metric families for
later anti-overfit review, including:

- PnL / return metrics;
- drawdown metrics;
- risk-adjusted metrics;
- hit rate / win-loss statistics;
- trade count;
- turnover / cost / slippage / funding assumptions;
- exposure / leverage / liquidation-risk indicators where applicable;
- per-segment and aggregate metrics;
- OOS / walk-forward / fold metrics when applicable;
- uncertainty / confidence / robustness indicators where applicable.

Exact metrics and schema are deferred.

## 11. Lineage and provenance requirements

Future result population design must preserve:

- Strategy Spec lineage;
- variant population lineage;
- sweep plan / run-manifest lineage if later created;
- execution authorization reference if later created;
- data snapshot / timeframe / input references;
- code / runner / environment references if later authorized;
- trial budget reference;
- result generation timestamp concept;
- reviewer or aggregation agent concept.

Exact identifiers, hash algorithms, paths, and schemas are not locked here.

## 12. Trial-budget and multiple-testing relationship

Result population must preserve trial-budget context.

It must allow multiple-testing exposure to be calculated or audited later.

It must support DSR-aware or later multiple-testing-aware interpretation.

It must distinguish planned trials from amendments, retries, reruns, seeds,
folds, walk-forward windows, and exploratory repeats.

It must not let failed or repeated attempts disappear from the tested
population.

## 13. Anti-overfit review support

Result population storage must support population-level review, not only
best-result review.

It should enable detection of parameter sensitivity, PnL concentration,
overfitting, brittle segments, cost drag, and drawdown concentration.

It should preserve enough information for later WP-S2c-159 / WP-S2c-160
anti-overfit and advisory ranking artifact design.

It must not create ranking authority here.

## 14. Relationship to EXP / REP

EXP / REP remain canonical experiment and report artifacts.

Future result populations may feed REP or may be linked from REP only after
later design.

This package does not decide whether one sweep maps to one EXP, many EXPs, one
REP with many trials, or an intermediate layer.

No EXP or REP is created or modified.

## 15. Relationship to trial-log

Trial-log remains canonical for recorded trial evidence where applicable.

Future design must decide whether each variant, segment, seed, fold, or run
maps to trial-log rows.

This package does not lock that mapping.

No trial-log row is created or modified.

## 16. Relationship to OL / REC / DEC

OL, REC, and DEC remain canonical outcome, reconciliation, and decision
surfaces.

Result population cannot create OL / REC / DEC authority.

Any future advisory ranking or decision routing must consume canonical evidence
and gates.

No OL, REC, or DEC artifact is created or modified.

## 17. Intermediate result-surface question

Open design question: should the lab create a future intermediate
result-population artifact, or should result population be represented entirely
through EXP / REP / trial-log plus query views?

An intermediate artifact may preserve full population and failed variants
clearly.

Canonical-only representation reduces parallel-source risk.

Either option requires later storage / schema lock and protected-boundary
review.

This package does not choose a final option. This question must be consolidated
in WP-S2c-157 and locked, if authorized, in WP-S2c-158.

## 18. Storage and schema non-decisions

This package does not choose storage path.

It does not choose exact file format.

It does not choose schema fields.

It does not create validator design.

It does not create examples or fixtures.

It does not create result IDs.

It does not decide result-population to EXP / trial-log mapping.

It does not decide query-view shape.

It does not decide implementation.

## 19. Result-mutation and amendment posture

Future result populations must be immutable or amendment-audited after
creation.

Post-result deletion or winner-only filtering is forbidden.

Corrections must preserve original values or original references where
feasible.

Amendments must be explicit and explain why.

No amendment schema is locked here.

## 20. Relationship to existing local-sweep precedent

Existing local-sweep-result and local-run-registry docs may inform future
design.

They are precedent, not active authority for this package.

This package does not write local-run registry or local-sweep result data.

Future packages must decide whether and how precedent maps to the Strategy
Research Lab without bypassing evidence discipline.

## 21. What WP-S2c-157 must answer

WP-S2c-157 should consolidate variant / storage design across WP-S2c-154,
WP-S2c-155, and WP-S2c-156, including:

- whether variant populations, sweep plans / run manifests, and result
  populations need separate future artifacts;
- whether result population should be intermediate artifact, canonical EXP /
  REP / trial-log representation, or hybrid;
- what must be locked in WP-S2c-158;
- unresolved storage / schema / ID / linking decisions;
- anti-overfit and trial-budget implications;
- evidence-chain mapping options;
- protected-boundary and non-authority constraints;
- Karl decision prompts for WP-S2c-158 if locking is required.

WP-S2c-157 is still documentation-only.

## 22. Later variant/storage tranche posture

The expected later tranche posture is:

- WP-S2c-154: variant generation design opening;
- WP-S2c-155: sweep orchestration design;
- WP-S2c-156: result population / storage design;
- WP-S2c-157: variant/storage consolidation;
- WP-S2c-158: Karl-gated storage / variant lock.

No variant manifest, sweep plan, run manifest, result population, schema,
validator, parser/compiler, code, fixture, artifact instance, sweep, backtest,
runner invocation, result aggregation, or implementation should be created
before later explicit authorization.

WP-S2c-158 is expected to be Karl-gated. Do not auto-draft it before
report-back and explicit lock direction if WP-S2c-157 requires that.

## 23. Protected boundaries

This design explicitly preserves:

- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS / reconciliation / kill-switch / safe-mode;
- SignalProvider Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data/` protected paths;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred and A/D/E rejected;
- Track 3 paused;
- WP-S2c-140 deferred;
- permanent human gates;
- WP-S2c-151 Strategy DSL / Strategy Spec lock.

## 24. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation must confirm exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 25. Stop conditions

Stop if any content creates a result population, result-storage path, metrics
table, sweep result, sweep plan, run manifest, variant manifest, concept
artifact, Strategy Spec artifact, schema, validator, parser/compiler, fixture,
storage path, artifact instance, or implementation.

Stop if any content creates or ingests a real strategy idea, concept, Strategy
Spec, parameter grid, variant population, sweep plan, run manifest, result set,
metrics table, or result population as a committed artifact.

Stop if any content modifies or weakens the WP-S2c-151 Strategy Spec /
Strategy DSL lock.

Stop if any content permits executable code, runtime contact,
broker/exchange/order contact, network contact, file-writing commands, runner
invocation, local-run-registry write, local-sweep-result write, or
protected-path contact.

Stop if any content treats result population or result storage as candidate,
Strategy Spec, EXP, REP, ranking, paper/live, promotion, recommendation,
readiness, transition, or runtime approval.

Stop if any content weakens pre-registration, anti-overfit discipline, DSR /
multiple-testing posture, D2-006 / D2-007, REC-5, Phase 9 / D2-011, Scope 6,
or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 26. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, or human-gate
execution authority.

It is planning and storage-design structure only.

## 27. Next-package posture

After merge, the default next sequential package is WP-S2c-157 variant/storage
consolidation, unless Main/Karl directs a different authorized lab package.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler packages.

Do not auto-draft WP-S2c-158 before WP-S2c-157 is merged and any required
Karl-gated lock direction is resolved.
