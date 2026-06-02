# Advisory Ranking Artifact Design

## 1. Scope

WP-S2c-160 / WP-12gg is a Tier 1 documentation-only substantive design
package.

It defines advisory ranking artifact design for the future Strategy Research
Lab.

It creates only this design document and one `docs/project_status.md`
branch-state entry.

It creates no advisory ranking artifact instance, ranking score, formula, DSR
calculation, schema, validator, query view, parser/compiler, code, test,
fixture, artifact, storage path, sweep, backtest, result aggregation, strategy
execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-159 designed anti-overfit / DSR population logic and handed off
WP-S2c-160.

WP-S2c-158 locked variant/storage discipline and complete result-population
preservation.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused and WP-S2c-140 onward remains deferred, not rescinded.

Implementation remains unauthorized until later explicit Karl authorization.

## 3. Design objective

The objective is to define how a future advisory ranking artifact should
present candidate or variant-family ordering for human review.

Advisory ordering should be explainable, evidence-linked, and warning-rich.

Advisory ranking must not become recommendation, promotion, paper/live
readiness, runtime authority, or gate satisfaction.

This design preserves D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6,
canonical evidence routing, and permanent human gates.

This package does not create scores or executable ranking logic.

## 4. Lifecycle placement

Advisory ranking belongs after future anti-overfit / DSR review and before
Scope 6 / R2S integration review.

It consumes future complete result populations, anti-overfit / DSR diagnostics,
and canonical evidence references.

It should feed WP-S2c-161 Scope 6 integration design.

It does not replace EXP / REP, trial-log, OL, REC, or DEC.

It does not bypass D2-006 promotion gates or Scope 6 discipline.

## 5. Advisory ranking posture

Advisory ranking is a future human-review support surface.

It may order or group variants or candidate families for review.

It may surface warnings, blockers, and evidence gaps.

It does not recommend execution.

It does not approve a candidate.

It does not promote anything.

It does not create readiness or transition authority.

It does not satisfy human gates.

It must be treated as advisory text/data only.

## 6. Non-authority boundary

Advisory ranking cannot:

- trigger paper/live activity;
- trigger runtime behavior;
- contact broker, exchange, or order systems;
- modify risk caps or overlays;
- update candidate registry;
- create EXP, REP, trial-log, OL, REC, or DEC;
- satisfy D2-006, D2-007, REC-5, Scope 6, or human gates;
- produce recommendation authority.

Any future label such as `top-ranked` means review priority only, not
approval.

## 7. Required future inputs

Future advisory ranking design should require:

- approved Strategy Spec lineage;
- variant population lineage;
- result population completeness status;
- canonical EXP / REP / trial-log references if later available;
- anti-overfit / DSR diagnostics;
- D2-006 posture;
- REC-5 exact-segment posture;
- Scope 6 / R2S posture if available;
- data/timeframe support posture;
- cost, slippage, and funding assumptions;
- human-review notes and unresolved blockers.

Exact fields remain deferred.

## 8. Full-population and completeness dependency

Advisory ranking must not run on winner-only result data.

Missing failed, invalid, errored, aborted, or filtered variants should block or
qualify advisory ranking.

Complete population status must be visible in the artifact.

A high apparent result with incomplete population is not cleanly rankable.

This package creates no result population or completeness validator.

## 9. Anti-overfit / DSR diagnostic representation

Future advisory ranking should represent DSR / multiple-testing-aware
diagnostics from WP-S2c-159.

It should show overfit flags, population denominator caveats, parameter-cliff
warnings, walk-forward divergence, regime instability, cost fragility, drawdown
concentration, sample-size concerns, and trial-budget irregularities.

It must not compute DSR or implement formulas.

It must not hide diagnostics behind a single score.

## 10. Candidate and variant grouping posture

Future advisory ranking may group by Strategy Spec, variant family, candidate
lineage, market/timeframe, or evidence segment if later authorized.

Grouping must preserve lineage and must not merge distinct evidence segments in
a way that weakens REC-5.

Near-neighbor variants cannot be treated as exact-segment evidence.

Exact grouping keys remain deferred.

## 11. Advisory ordering semantics

Ordering may be based on future weighted or rule-based design, but this package
does not choose weights, formulas, or thresholds.

Ordering should be explainable and decomposable into evidence, anti-overfit,
risk, robustness, and blocker context.

Ordering should prefer transparency over a black-box score.

Ties, uncertainty, and incomplete evidence should be explicit.

`Ranked higher` means higher review priority only.

## 12. Warning and blocker representation

Future advisory artifact design should represent:

- population incomplete;
- DSR / multiple-testing weakness;
- overfit or fragility flags;
- D2-006 not met;
- REC-5 exact-segment not met;
- Scope 6 / R2S unresolved;
- insufficient trade count or sample;
- data/timeframe unsupported;
- cost, slippage, or funding fragile;
- drawdown or tail-risk concentrated;
- runtime/protected-boundary blocker;
- human-review blocker.

Exact warning enum remains deferred.

## 13. Disqualification and exclusion posture

Future advisory ranking may show excluded or disqualified variants, but
exclusion must preserve reason and lineage.

Disqualified items must not disappear from population accounting.

Exclusion from advisory ranking is not the same as canonical rejection unless
later decision artifacts record it.

Exact exclusion status set remains deferred.

## 14. Evidence and lineage requirements

Future advisory ranking artifact design should preserve:

- Strategy Spec reference;
- variant population reference;
- sweep/run/result population references if later created;
- EXP / REP / trial-log / OL / REC / DEC references where available;
- anti-overfit / DSR diagnostic source;
- data/timeframe support references;
- human-review notes;
- unresolved blockers and deferrals.

No exact IDs, paths, schema, or links are locked here.

## 15. D2-006 composition

Advisory ranking is upstream of D2-006 and cannot relax D2-006.

Passing advisory review does not mean passing D2-006.

D2-006 remains the promotion gate.

Any future advisory artifact must clearly mark D2-006 posture.

This package modifies no D2-006 rule.

## 16. REC-5 floor preservation

REC-5 exact-segment floor discipline remains absolute.

Advisory ranking must not dilute REC-5 by sweep volume, near-neighbor variants,
or pooled segments.

Advisory ranking must mark exact-segment insufficiency as blocker or warning.

This package modifies no REC-5 rule.

## 17. Scope 6 / R2S relationship

Advisory ranking should feed future Scope 6 / R2S integration design in
WP-S2c-161.

Advisory ranking cannot itself satisfy Scope 6.

Scope 6 evidence and decision posture remains separate.

Any future R2S pathway remains human-gated and subject to locked criteria.

This package creates no Scope 6 artifact or R2S decision.

## 18. Canonical evidence relationship

EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision
surfaces.

Advisory ranking may reference canonical evidence.

Advisory ranking cannot become a parallel evidence store or decision store.

No canonical artifact is created or modified.

## 19. Human-review relationship

Advisory ranking exists to help humans review.

Human reviewers must be able to see why an item is ranked or blocked.

Human review is still required for downstream gates.

Advisory ranking cannot execute a human decision.

Future artifact should preserve reviewer notes if later authorized.

## 20. Advisory artifact mutation and amendment posture

Future advisory ranking artifacts should be reproducible or
amendment-audited.

Post-result rank manipulation must be visible.

If ranking inputs change, the artifact should record the basis for change.

Exact amendment schema is deferred.

No advisory artifact is created here.

## 21. Deferred implementation details

The following details are explicitly deferred:

- ranking formulas;
- scores and weights;
- thresholds;
- DSR computation;
- exact diagnostic fields;
- warning enums;
- blocker enums;
- grouping keys;
- storage paths;
- schema fields;
- validators;
- query views;
- examples / fixtures;
- parser/compiler;
- code / tests / tools;
- implementation.

## 22. Rejected and out-of-scope alternatives

Ranking-as-recommendation is rejected because human gates remain required.

Ranking-as-approval is rejected because advisory ordering cannot approve a
candidate.

Automatic promotion based on rank is rejected because D2-006, Scope 6, and
human-gated downstream decisions remain separate.

Paper/live readiness based on rank is rejected because ranking cannot create
paper/live or runtime authority.

Ranking on winner-only populations is rejected because it hides
multiple-testing exposure and survivorship bias.

Hiding overfit diagnostics behind a single score is rejected because humans
need visible diagnostic context.

Diluting REC-5 with near-neighbor variants is rejected because exact-segment
evidence discipline must hold.

Replacing D2-006 with an advisory score is rejected because D2-006 remains the
promotion gate.

A parallel evidence or decision store is rejected because canonical evidence
and decision surfaces remain EXP / REP, trial-log, OL, REC, and DEC.

Implementation before WP-S2c-164 authorization is rejected because the lab
design tranche has not authorized implementation.

Track 3 / AUTO reactivation is rejected because those paths remain paused or
frozen.

Paper/live bridge or runtime contact is rejected because protected boundaries
remain strict.

## 23. Handoff to WP-S2c-161

WP-S2c-161 should define how advisory ranking posture integrates with Scope 6 /
R2S review.

It should clarify how advisory outputs are consumed without becoming R2S
approval.

It should preserve D2-006, REC-5, Scope 6, Phase 9 / D2-011, and human gates.

WP-S2c-161 must remain documentation-only unless separately authorized.

## 24. Protected boundaries

This design explicitly preserves:

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
- WP-S2c-158 variant/storage lock;
- WP-S2c-159 anti-overfit / DSR design;
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

## 25. Stop conditions

Stop if any content creates ranking/scoring code, ranking formulas, DSR
calculations, schema, validator, query view, parser/compiler, fixture, storage
path, artifact instance, advisory ranking artifact, variant manifest, sweep
plan, run manifest, result population, metrics table, EXP, REP, trial-log row,
OL, REC, DEC, or implementation.

Stop if any content runs backtests, sweeps, optimizations, parameter searches,
result aggregation, DSR/statistical calculations, ranking/scoring
calculations, runner commands, local-run-registry writes, local-sweep-result
writes, or query-output packages.

Stop if any content modifies or weakens D2-006, D2-007, REC-5, Phase 9 /
D2-011, Scope 6, WP-S2c-151, WP-S2c-158, WP-S2c-159, or permanent human
gates.

Stop if any content treats advisory ranking as recommendation authority,
candidate approval, ranking authority, promotion authority, readiness
authority, transition authority, paper/live authority, runtime authority, or
automatic gate satisfaction.

Stop if any content permits runtime contact, broker/exchange/order contact,
network contact, file-writing commands, protected-path contact, Track 3
reactivation, AUTO bridge reactivation, paper bridge work,
monitoring/dashboard work, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 26. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation requires exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

No full pytest is required unless repo-local convention or validation issues
require it.

## 27. Next-package posture

After merge, the default next sequential package is WP-S2c-161 Scope 6
integration design, unless Main/Karl directs otherwise.

WP-S2c-161 is not Karl-gated.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler/query-view packages.
