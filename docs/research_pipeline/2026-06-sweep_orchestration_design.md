# Sweep Orchestration Design

## 1. Scope

WP-S2c-155 / WP-12gb is a Tier 1 documentation-only substantive design
package.

It defines sweep-orchestration design for the Strategy Research Lab.

It creates only this design document, updates `docs/research_pipeline/README.md`
with one additive index entry, and updates `docs/project_status.md`.

It creates no sweep plan artifact, run manifest, result population, variant
manifest, schema, validator, query view, parser, compiler, code, test, fixture,
storage path, implementation, sweep, backtest, optimizer run, strategy
execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-154 opened variant-generation design and handed off WP-S2c-155 as the
default next sequential lab package.

WP-S2c-153 defined concept-to-Strategy-Spec authoring and approval discipline.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake through
advisory ranked output.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Sweep-orchestration problem statement

The lab needs a controlled way to take a future pre-registered variant
population and plan an offline research sweep without bypassing gates.

The dangerous failure mode is treating variant generation as permission to run
unlimited sweeps.

Another failure mode is bypassing EXP / REP, trial-log, OL, REC, and DEC by
creating a parallel results channel.

The design problem is to define orchestration boundaries before any runner,
storage, or execution implementation exists.

## 4. Design objective

This design defines how a future pre-registered variant population should be
handed to sweep planning.

Future sweep planning must carry lineage, pre-registration reference, trial
budget, allowed execution context, planned result capture, and stop conditions.

Execution authorization remains separate from sweep planning.

The design preserves the evidence chain and anti-overfit discipline.

## 5. Orchestration posture

Sweep orchestration is future planning and coordination for offline research
only.

It is not runtime trading.

It is not paper/live bridge work.

It is not permission to call a runner.

It is not approval, recommendation, ranking, readiness, promotion, or
transition authority.

It may later coordinate authorized offline backtest or sweep execution only
after separate implementation authorization.

## 6. Relationship to lab lifecycle

Sweep orchestration belongs after variant generation / pre-registration and
before result population / storage.

It consumes a future pre-registered variant population.

Later packages only may produce enough structure for controlled run execution
and result capture.

Sweep orchestration must preserve lineage from idea to concept to Strategy Spec
to variant population to future sweep to future evidence.

## 7. Pre-registered variant population dependency

Sweep planning depends on a pre-registered variant population.

Because no real variant population manifest exists yet, this package must not
create run plans or assume concrete fields.

The future handoff should require a frozen or explicitly amendable tested
universe before execution.

If variant manifest storage or schema remains unresolved, WP-S2c-155 records
dependencies only.

## 8. Execution-authorization surface

Future sweep execution requires explicit authorization beyond sweep planning.

Initial lab maturity should keep execution authorization human-gated.

Execution authorization must verify variant pre-registration, trial budget,
data/timeframe availability, protected-boundary safety, and evidence-chain
routing.

No automatic authorization may be inferred from concept review, Strategy Spec
approval, variant generation, or sweep planning.

## 9. Sweep-planning boundary

Future sweep planning may define intended datasets, timeframe, variant
population reference, budget, runner family, result-capture expectation, and
stop conditions.

This package does not choose exact fields, schema, storage path, or runner
interface.

Sweep planning must not mutate the variant population after results are known.

Sweep planning must not silently expand trial budget or variant universe.

## 10. Trial-budget posture

Trial budget must be visible before execution.

Trial budget must account for the number of variants, segments, seeds, folds,
walk-forward windows, and repeated attempts where applicable.

Trial budget must support DSR and multiple-testing-aware interpretation.

Trial-budget expansion after results are known is forbidden unless later
amendment semantics explicitly allow and audit it.

## 11. Run-manifest posture

A future run manifest may be needed, but this package does not create one.

Future run-manifest design should preserve lineage, variant population
reference, environment assumptions, data slice references, runner
configuration, execution authorization reference, and result destination.

Exact run IDs, fields, storage, and schema are deferred.

## 12. Result-collection posture

Future result collection must route to canonical evidence artifacts or later
explicitly designed intermediate result surfaces.

Result collection must preserve all attempted variants, failed variants,
invalid variants, excluded variants, and execution errors where applicable.

Result collection must not retain only winners.

Result collection must support future anti-overfit and population-level review.

## 13. Evidence-chain relationship

EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision
surfaces.

Sweep orchestration must not create a parallel evidence chain.

Future design must decide how sweep runs map to EXP and trial-log rows.

No mapping is locked here.

No EXP, REP, trial-log, OL, REC, or DEC artifact is created here.

## 14. Runtime and protected-path boundary

Sweep orchestration is offline research design only.

It must not touch paper runtime, OMS, reconciliation, kill-switch, safe-mode,
overlay, SignalProvider, broker/exchange/order APIs, Tier 4, or protected
paths.

It must not write to `lib/`, `src/`, `configs/`, `.claude/`, or `data/`.

It must not modify local runners or automation code.

## 15. Relationship to existing batch-runner / local-run precedent

Existing parameter-sweep, batch-runner, local-run-registry, and
local-sweep-result docs are precedent only.

They may inform future design vocabulary but do not authorize runner invocation
or implementation.

This package does not reactivate AUTO bridge or any previous automation
implementation path.

Future packages must decide what precedent can be reused under the new Strategy
Lab discipline.

## 16. Failure, abort, and amendment posture

Future sweep orchestration must define how failed runs, invalid variants,
aborted sweeps, data unavailability, and budget breaches are recorded.

Aborts and amendments must be auditable.

Amendments after pre-registration must not erase the original registered
universe.

Failures must not be hidden to improve apparent performance.

## 17. Storage and schema non-decisions

This package does not choose storage path.

It does not choose exact file format.

It does not choose schema fields.

It does not create validator design.

It does not create examples or fixtures.

It does not create run IDs.

It does not decide sweep-plan to EXP/trial-log mapping.

It does not decide result-population storage semantics.

It does not decide implementation.

## 18. What WP-S2c-156 must answer

WP-S2c-156 should define result population / storage design, including:

- what result population means after a future sweep;
- how all variants, failures, exclusions, and errors are retained;
- what metrics and lineage must be preserved for anti-overfit review;
- how result storage relates to EXP / REP, trial-log, OL, REC, and DEC;
- what storage/schema decisions remain for WP-S2c-157/158;
- stop conditions before any result artifact or storage path is created.

## 19. Later variant/storage tranche posture

The expected later tranche posture is:

- WP-S2c-154: variant generation design opening;
- WP-S2c-155: sweep orchestration design;
- WP-S2c-156: result population / storage design;
- WP-S2c-157: variant/storage consolidation;
- WP-S2c-158: Karl-gated storage / variant lock.

No variant manifest, sweep plan, run manifest, result population, schema,
validator, parser/compiler, code, fixture, artifact instance, sweep, backtest,
runner invocation, or implementation should be created before later explicit
authorization.

WP-S2c-158 is expected to be Karl-gated. Do not auto-draft it before
report-back and explicit lock direction if the preceding package requires that.

## 20. Protected boundaries

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

## 21. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation must confirm exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 22. Stop conditions

Stop if any content creates a sweep plan, run manifest, result population,
variant manifest, concept artifact, Strategy Spec artifact, schema, validator,
parser/compiler, fixture, storage path, artifact instance, or implementation.

Stop if any content creates or ingests a real strategy idea, concept, Strategy
Spec, parameter grid, variant population, sweep plan, run manifest, or result
set as a committed artifact.

Stop if any content modifies or weakens the WP-S2c-151 Strategy Spec /
Strategy DSL lock.

Stop if any content permits executable code, runtime contact,
broker/exchange/order contact, network contact, file-writing commands, runner
invocation, local-run-registry write, local-sweep-result write, or
protected-path contact.

Stop if any content treats sweep planning as candidate, Strategy Spec, EXP,
sweep execution, ranking, paper/live, promotion, recommendation, readiness, or
runtime approval.

Stop if any content weakens pre-registration, anti-overfit discipline, D2-006,
D2-007, REC-5, Phase 9 / D2-011, Scope 6, or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 23. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, or human-gate
execution authority.

It is planning and orchestration-boundary structure only.

## 24. Next-package posture

After merge, the default next sequential package is WP-S2c-156 result
population / storage design, unless Main/Karl directs a different authorized
lab package.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler packages.
