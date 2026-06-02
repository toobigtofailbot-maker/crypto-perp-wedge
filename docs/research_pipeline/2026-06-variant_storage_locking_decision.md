# Variant / Storage Locking Decision

## 1. Scope

WP-S2c-158 / WP-12ge is a Tier 1 documentation-only Karl-gated
major-decision package.

It records the variant/storage lock direction from the post-WP-S2c-157
Main/Karl resolution.

It creates only this decision document and one `docs/project_status.md`
branch-state entry.

It creates no variant manifest, sweep plan, run manifest, result population,
result-storage path, metrics table, schema, validator, query view,
parser/compiler, code, test, fixture, implementation, sweep, backtest,
optimizer run, result aggregation, strategy execution, ranking authority,
recommendation authority, paper/live authority, runtime authority, or
human-gate execution authority.

## 2. Authorization and repo-truth basis

WP-S2c-154 opened variant-generation design.

WP-S2c-155 defined sweep-orchestration design.

WP-S2c-156 defined result population / storage design.

WP-S2c-157 consolidated the tranche and produced WP-S2c-158 prompts.

External Main/Karl lock direction approved all seven prompts as YES.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused and WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Locked decisions

1. Future variant population manifest is required as the pre-registration
   surface before sweep execution.
2. Complete result-population preservation is required across attempted,
   failed, invalid, excluded, errored, aborted, filtered, data-unavailable, and
   successful variants.
3. EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and
   decision surfaces with no parallel decision authority.
4. Hybrid result model is locked: canonical evidence remains authoritative;
   any future intermediate result-population surface may only be evidence
   input / index with no authority.
5. Exact storage paths, schemas, validators, query views, examples, IDs,
   parser/compiler, runner integration, and implementation are deferred.
6. Sweep execution, result aggregation, ranking authority, paper/live
   authority, runtime contact, protected-path contact, and Track 3 / AUTO
   reactivation are explicitly forbidden.
7. Side correctly stopped after WP-S2c-157 and obtained explicit Karl lock
   direction before WP-S2c-158 drafting; future similarly gated lock packages
   must follow the same surfacing-before-locking discipline.

## 4. Decision 1 — Variant population manifest

A future variant population manifest is locked as the required
pre-registration surface before sweep execution.

This preserves Phase 9 / D2-011 pre-registration discipline at variant scale.

It prevents post-hoc cherry-picking and hidden variant-universe expansion.

Exact storage path, schema, fields, IDs, examples, validators, and
implementation remain deferred.

No variant population manifest is created here.

## 5. Decision 2 — Complete result-population preservation

Complete result-population preservation is locked.

Required future preservation includes attempted, failed, invalid, excluded,
errored, aborted, filtered, data-unavailable, and successful variants.

Preservation must include enough lineage and trial-budget context for
anti-overfit review.

Winner-only retention is forbidden.

No result population artifact is created here.

## 6. Decision 3 — Canonical evidence and decision surfaces

EXP / REP, trial-log, OL, REC, and DEC are locked as canonical evidence and
decision surfaces.

No parallel decision authority is allowed.

Any future intermediate surface must link into the canonical chain and cannot
replace it.

No EXP, REP, trial-log, OL, REC, or DEC file is created or modified.

## 7. Decision 4 — Hybrid result model

The hybrid model is locked at design-discipline level:

- canonical evidence remains authoritative;
- a future intermediate result-population surface may be designed only as
  evidence input / index;
- any intermediate surface has no ranking, recommendation, promotion,
  paper/live, runtime, approval, or decision authority.

Exact intermediate artifact shape, index shape, storage path, schema, links,
and query views remain deferred.

The hybrid model is chosen to support full-population retention without
weakening canonical evidence authority.

## 8. Decision 5 — Deferred implementation details

Exact storage paths, schemas, validators, query views, examples, fixtures, IDs,
parser/compiler, runner integration, implementation, and exact EXP/trial-log
mapping are deferred.

Downstream packages may design these only after later explicit authorization.

This package creates no schema or implementation authority.

## 9. Decision 6 — Execution and runtime prohibitions

Sweep execution, result aggregation, ranking authority, paper/live authority,
runtime contact, protected-path contact, broker/exchange/order contact, runner
invocation, local-run-registry writes, local-sweep-result writes, Track 3
reactivation, and AUTO bridge reactivation are explicitly forbidden.

No execution or implementation is authorized by this lock.

## 10. Decision 7 — Karl-gated drafting discipline

WP-S2c-158 was drafted only after WP-S2c-157 merged and explicit lock direction
was received.

This surfacing-before-locking pattern remains required for future Karl-gated
packages.

WP-S2c-164 is later Karl-gated and must not be drafted until WP-S2c-163
report-back and explicit Karl resolution.

## 11. Preservation of pre-registration discipline

The variant manifest lock preserves pre-registration discipline at scale.

Post-result mutation, silent expansion, and cherry-picking are forbidden.

Amendments must be explicitly designed later and must preserve auditability.

No amendment schema is locked here.

## 12. Preservation of DSR / multiple-testing discipline

Complete result-population preservation is required for honest DSR /
multiple-testing-aware review.

All trials, including failures and excluded/invalid/error cases where
applicable, must remain visible.

Lab anti-overfit review cannot be based only on surviving winners.

WP-S2c-159 should design the anti-overfit / DSR population logic using this
lock.

## 13. Relationship to EXP / REP

EXP and REP remain canonical planning/result artifacts.

Future variant populations and result populations may link to or feed EXP/REP
only after later design.

Exact mapping is deferred.

No EXP or REP is created or modified.

## 14. Relationship to trial-log

Trial-log remains canonical trial evidence where applicable.

Exact mapping from variant/seed/fold/run to trial-log rows remains deferred.

No trial-log row is created or modified.

## 15. Relationship to OL / REC / DEC

OL, REC, and DEC remain canonical outcome, reconciliation, and decision
surfaces.

Result populations and advisory artifacts cannot create OL/REC/DEC authority.

No OL, REC, or DEC artifact is created or modified.

## 16. Intermediate result-population boundary

A future intermediate result-population surface is permitted only as evidence
input / index.

It cannot be a parallel source of truth for decisions.

It cannot rank, recommend, approve, promote, or transition anything.

It must link to canonical evidence if later designed.

Exact shape remains deferred.

## 17. Explicit deferrals

The following items are deferred:

- storage paths;
- file formats;
- schema fields;
- validators;
- query views;
- examples;
- fixtures;
- IDs;
- parser/compiler;
- runner integration;
- local-run-registry mapping;
- local-sweep-result mapping;
- exact EXP/REP/trial-log mapping;
- amendment schema;
- result-population artifact shape;
- implementation.

## 18. Implementation prohibition

No implementation is authorized here.

Implementation remains blocked until the lab design tranche is consolidated,
the required locks are in repo truth, protected-boundary review is complete,
and explicit Karl implementation authorization is recorded.

WP-S2c-164 is expected to decide implementation tranche authorization after
WP-S2c-163 report-back.

## 19. Relationship to later WP-S2c-159 / WP-S2c-160

WP-S2c-159 should design anti-overfit / DSR population logic using the locked
full-population and trial-budget discipline.

WP-S2c-160 should design advisory ranking artifact semantics after
WP-S2c-159.

Neither package may create ranking authority, recommendation authority,
promotion authority, paper/live authority, runtime authority, or automatic gate
satisfaction.

Advisory ranking remains advisory and human-reviewed.

## 20. Relationship to later WP-S2c-163 / WP-S2c-164

WP-S2c-163 should consolidate the lab design tranche and surface
implementation-roadmap options.

WP-S2c-164 is Karl-gated and must not be drafted until WP-S2c-163 is merged,
Side reports consolidated lock candidates / implementation options, and Karl
resolves the lab design locking and implementation tranche authorization.

WP-S2c-164 remains documentation-only major decision; implementation packages
come later only if explicitly authorized.

## 21. Protected boundaries

This decision explicitly preserves:

- permanent human gates;
- WP-S2c-100 locked criteria;
- D2-006;
- D2-007;
- REC-5 floor discipline;
- Phase 9 / D2-011 pre-registration discipline;
- Scope 6 discipline;
- WP-S2c-113 Scope 6 lock;
- WP-S2c-114 schemas;
- WP-S2c-115 validators;
- WP-S2c-117 query views;
- WP-S2c-151 Strategy DSL / Strategy Spec lock;
- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS / reconciliation / kill-switch / safe-mode;
- SignalProvider Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data` protected paths;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred and A/D/E rejected;
- Track 3 paused;
- WP-S2c-140 onward deferred, not rescinded.

## 22. Stop conditions

Stop if any content creates a variant manifest, sweep plan, run manifest,
result population, result-storage path, metrics table, concept artifact,
Strategy Spec artifact, schema, validator, parser/compiler, fixture, storage
path, artifact instance, query view, or implementation.

Stop if any content creates or ingests a real strategy idea, concept, Strategy
Spec, parameter grid, variant population, sweep plan, run manifest, result
set, metrics table, or result population as a committed artifact.

Stop if any content modifies or weakens the WP-S2c-151 Strategy Spec /
Strategy DSL lock.

Stop if any content permits executable code, runtime contact,
broker/exchange/order contact, network contact, file-writing commands, runner
invocation, local-run-registry write, local-sweep-result write, result
aggregation, or protected-path contact.

Stop if any content treats variant/storage/result design as candidate,
Strategy Spec, EXP, REP, ranking, paper/live, promotion, recommendation,
readiness, transition, or runtime approval.

Stop if any content weakens pre-registration, anti-overfit discipline, DSR /
multiple-testing posture, D2-006 / D2-007, REC-5, Phase 9 / D2-011, Scope 6,
or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper
bridge, monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

Stop if full pytest fails.

## 23. Validation posture

Validation profile is CS12 T1-doc-major-decision.

Full pytest is required.

Exact changed-file scope is required.

All integrity views and validators are required.

## 24. Non-authority boundary

This locking decision creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority,
ranking/scoring authority, promotion authority, transition authority,
readiness authority, implementation authority, or human-gate execution
authority.

It locks design discipline only.

## 25. Next-package posture

After merge, the default next sequential package is WP-S2c-159 anti-overfit /
DSR-population logic design, unless Main/Karl directs otherwise.

WP-S2c-159 is not Karl-gated.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler/query-view packages.
