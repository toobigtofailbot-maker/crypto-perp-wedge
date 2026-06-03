# Scope 6 / R2S Integration Design

## 1. Scope

WP-S2c-161 / WP-12gh is a Tier 1 documentation-only substantive design
package.

It defines Scope 6 / R2S integration design for future Strategy Research Lab
advisory outputs.

It creates only this design document and one `docs/project_status.md`
branch-state entry.

It creates no Scope 6 artifact instance, R2S approval record,
shadow-evidence retention artifact, S2P approval record, advisory ranking
artifact, ranking score, formula, DSR calculation, schema, validator, query
view, parser/compiler, code, test, fixture, artifact, storage path, sweep,
backtest, result aggregation, transition machinery, strategy execution, or
authority.

## 2. Authorization and repo-truth basis

WP-S2c-160 designed advisory ranking artifact semantics and handed off
WP-S2c-161.

WP-S2c-159 designed anti-overfit / DSR population logic.

WP-S2c-158 locked variant/storage discipline and complete result-population
preservation.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-113 locked Scope 6 packaging decisions for the future R2S approval
record, shadow-evidence retention artifact, and S2P approval record.

WP-S2c-100 locked approval/readiness criteria and remains unchanged.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused and WP-S2c-140 onward remains deferred, not rescinded.

Implementation remains unauthorized until later explicit Karl authorization.

## 3. Design objective

The objective is to define how future advisory ranking output can be consumed
by Scope 6 / R2S human review.

Advisory ranking must remain review-support only.

Advisory ranking must not become R2S approval, candidate promotion, transition
machinery, paper/live readiness, runtime authority, or gate execution.

This design preserves D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6,
WP-S2c-100 locked criteria, canonical evidence routing, and permanent human
gates.

This package does not create artifacts, schemas, validators, query views, or
implementation.

## 4. Lifecycle placement

This design sits after future advisory ranking and before any future R2S
approval-record creation.

It consumes future advisory ranking context, canonical evidence references,
and gate posture.

It prepares WP-S2c-162 to define agent roles around this boundary.

It does not replace EXP / REP, trial-log, OL, REC, or DEC.

It does not execute or satisfy D2-006, REC-5, Scope 6, or human gates.

## 5. Scope 6 / R2S posture

Scope 6 / R2S remains a human-gated review and decision pathway.

Advisory outputs may prioritize review and surface blockers, but they cannot
decide.

R2S approval-record artifacts remain separate future artifacts under the
WP-S2c-113 lock.

R2S transition machinery remains unauthorized.

Any future R2S approval record documents a human decision only and does not
itself implement transition machinery.

## 6. Advisory ranking input boundary

Future advisory ranking can supply:

- review-priority ordering;
- evidence-linked rationale;
- warnings;
- blockers;
- overfit / DSR diagnostics;
- population-completeness status;
- D2-006 posture;
- REC-5 posture;
- Scope 6 unresolved-status posture;
- data/timeframe support notes;
- cost, slippage, and funding assumption notes;
- unresolved human-review notes.

These inputs are advisory context only.

Exact fields, enums, schema, query views, and storage paths remain deferred.

## 7. R2S non-approval boundary

Advisory ranking cannot:

- approve R2S;
- reject R2S as a canonical decision;
- promote a candidate;
- create readiness;
- create transition authority;
- satisfy human gates;
- create or update R2S approval records;
- update the candidate registry;
- trigger a shadow adapter or paper runtime;
- contact runtime or protected paths.

Any label such as `ready for R2S review` means ready for human review only, not
approved for transition.

## 8. Required future review inputs

Future R2S review should be able to see, where available:

- candidate or Strategy Spec lineage;
- variant population lineage;
- result population completeness;
- advisory ranking rationale;
- anti-overfit / DSR diagnostics;
- canonical EXP / REP / trial-log references;
- OL / REC / DEC references where applicable;
- D2-006 pass / fail / unknown posture;
- REC-5 exact-segment evidence list or insufficiency;
- Phase 9 / D2-011 pre-registration posture;
- Scope 6 criteria checklist posture;
- data/timeframe support posture;
- cost, slippage, and funding assumption posture;
- unresolved blockers and deferrals;
- reviewer notes.

Exact field shape remains deferred.

## 9. Warning and blocker propagation

Advisory warnings should propagate into R2S review as visible warnings or
blockers.

Blockers may prevent a human reviewer from proceeding, but only through later
authorized criteria / artifact design.

Warnings must not be hidden by ranking order.

Blockers must preserve reason and lineage.

Exact blocker enum and validator behavior remain deferred.

## 10. D2-006 composition

D2-006 remains the research promotion gate.

Advisory ranking cannot relax D2-006.

Scope 6 / R2S review cannot treat advisory rank as a D2-006 substitute.

Any future R2S review surface must show D2-006 posture explicitly.

This package modifies no D2-006 rule.

## 11. REC-5 exact-segment preservation

REC-5 exact-segment floor discipline remains absolute.

Advisory ranking cannot dilute REC-5 by sweep volume, near-neighbor variants,
pooled segments, or Strategy Spec family similarity.

R2S review must preserve exact evidence-segment requirements.

Near-neighbor or family-level evidence may be context only if later authorized,
not REC-5 satisfaction.

This package modifies no REC-5 rule.

## 12. Phase 9 / D2-011 pre-registration relationship

R2S review should preserve the future pre-registration chain from Strategy Spec
to variant population to sweep / result population where applicable.

Unregistered or amended-after-result variant universes should be warning or
blocker context.

This package does not define amendment schema or artifact fields.

Phase 9 / D2-011 is not modified.

## 13. WP-S2c-100 locked-criteria relationship

WP-S2c-100 locked approval/readiness criteria remain unchanged.

Advisory ranking and Scope 6 integration must not reinterpret those criteria.

If future advisory output conflicts with locked criteria, locked criteria win.

This package creates no readiness determination.

## 14. R2S approval-record relationship

WP-S2c-113 locks the future R2S approval-record artifact family and
required-content posture.

Advisory ranking may be referenced as decision-support context only if later
artifact design permits it.

R2S approval records remain human-decision records.

R2S approval records do not implement transition machinery.

This package creates no approval record and no approval-record schema.

## 15. Shadow-evidence and S2P boundary

Shadow-evidence retention and S2P approval records are downstream Scope 6 /
paper-related surfaces.

WP-S2c-161 does not design S2P integration beyond preserving the boundary.

Advisory ranking for the research lab does not authorize shadow-evidence
retention, paper bridge, paper runtime, or S2P transition.

D2-007 and Phase 1 paper runtime protections remain unchanged.

## 16. Canonical evidence relationship

EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision
surfaces.

Advisory ranking and Scope 6 integration may reference canonical evidence but
cannot replace it.

No parallel evidence store or decision store is created.

No canonical artifact is created or modified.

## 17. Human-review and permanent-gate relationship

Human review remains required at all locked human-gate points.

Advisory output can help humans see what to review, why, and with which
blockers.

Advisory output cannot execute a human decision.

R2S review cannot be automated by rank, score, warning state, or agent output.

Permanent human gates are unchanged.

## 18. Decision record versus advisory surface

Advisory ranking surfaces are not decision records.

R2S approval records are future human-decision records.

Canonical decision artifacts remain separate.

A ranked advisory item can be discussed in review without becoming approved.

Rejection or exclusion in advisory context is not canonical rejection unless
later decision artifacts record it.

## 19. Data/timeframe and cost-assumption posture

Future R2S review should preserve data/timeframe support posture and cost,
slippage, and funding assumptions surfaced by advisory ranking.

Unsupported data/timeframes or unrealistic cost assumptions should remain
visible warnings or blockers.

No data catalog or timeframe-status file is modified.

## 20. Incomplete evidence posture

Incomplete result populations, missing failed variants, missing invalid /
error / aborted / filtered variants, missing DSR / anti-overfit diagnostics,
or missing exact-segment REC-5 evidence should qualify or block review.

Winner-only or incomplete advisory output is insufficient for clean R2S
review.

Exact blocker handling remains deferred.

## 21. Agent-consumption boundary for WP-S2c-162

WP-S2c-162 should define lab agent roles around this boundary.

Agents may draft, summarize, check completeness, or prepare human-review
packets if later authorized.

Agents must not approve R2S, execute gates, update candidate readiness, trigger
transitions, or contact runtime / protected paths.

This package creates no agent implementation.

## 22. Artifact, schema, validator, and query non-decisions

The following are explicitly deferred:

- advisory ranking artifact schema;
- R2S integration schema;
- warning / blocker enum;
- Scope 6 integration validator;
- query-view changes;
- artifact examples;
- storage paths;
- IDs;
- exact canonical evidence links;
- exact R2S approval-record reference fields;
- mutation / amendment schema;
- implementation.

## 23. Deferred implementation details

The following implementation details are explicitly deferred:

- ranking formulas;
- scoring;
- DSR computation;
- R2S approval-record creation;
- transition machinery;
- shadow adapter integration;
- paper bridge integration;
- dashboard integration;
- agent implementation;
- code / tests / tools;
- parser / compiler;
- validator implementation;
- query implementation;
- any runtime integration.

## 24. Rejected and out-of-scope alternatives

Advisory ranking as R2S approval is rejected because human-gated Scope 6
approval records remain separate.

Advisory rank as D2-006 replacement is rejected because D2-006 remains the
research promotion gate.

Advisory rank as REC-5 satisfaction is rejected because exact-segment evidence
discipline must hold.

Advisory rank as Scope 6 satisfaction is rejected because Scope 6 review and
human decisions remain separate.

Automatic R2S promotion is rejected because permanent human gates and locked
criteria remain required.

Human-gate execution by agent or score is rejected because human review cannot
be automated by advisory output.

Candidate registry updates from advisory output are rejected because advisory
context is not candidate-state authority.

R2S approval-record creation in this package is rejected because this package
is documentation-only integration design.

S2P / paper bridge work is rejected because downstream paper-related surfaces
remain outside this package.

Runtime or protected-path contact is rejected because Tier 4 and protected
runtime boundaries remain strict.

Track 3 / AUTO reactivation is rejected because those paths remain paused or
frozen.

Implementation before WP-S2c-164 authorization is rejected because the lab
design tranche has not authorized implementation.

## 25. Protected boundaries

This design explicitly preserves:

- permanent human gates;
- WP-S2c-100 locked criteria;
- D2-006;
- D2-007;
- REC-5 floor discipline;
- Phase 9 / D2-011 pre-registration discipline;
- Scope 6 discipline;
- WP-S2c-113 Scope 6 packaging lock;
- WP-S2c-114 schemas;
- WP-S2c-115 validators;
- WP-S2c-117 query views;
- WP-S2c-151 Strategy DSL / Strategy Spec lock;
- WP-S2c-158 variant/storage lock;
- WP-S2c-159 anti-overfit / DSR design;
- WP-S2c-160 advisory ranking design;
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

## 26. Stop conditions

Stop if any content creates ranking/scoring code, ranking formulas, DSR
calculations, schema, validator, query view, parser/compiler, fixture, storage
path, artifact instance, advisory ranking artifact, Scope 6 artifact, R2S
approval record, shadow-evidence retention artifact, S2P approval record,
variant manifest, sweep plan, run manifest, result population, metrics table,
EXP, REP, trial-log row, OL, REC, DEC, or implementation.

Stop if any content runs backtests, sweeps, optimizations, parameter searches,
result aggregation, DSR/statistical calculations, ranking/scoring
calculations, transition simulation, runner commands, local-run-registry
writes, local-sweep-result writes, or query-output packages.

Stop if any content modifies or weakens D2-006, D2-007, REC-5, Phase 9 /
D2-011, Scope 6, WP-S2c-100, WP-S2c-113, WP-S2c-151, WP-S2c-158,
WP-S2c-159, WP-S2c-160, or permanent human gates.

Stop if any content treats advisory ranking or Scope 6 integration as
recommendation authority, candidate approval, ranking authority, promotion
authority, readiness authority, transition authority, paper/live authority,
runtime authority, or automatic gate satisfaction.

Stop if any content permits runtime contact, broker/exchange/order contact,
network contact, file-writing commands beyond scoped docs/status edit,
protected-path contact, Track 3 reactivation, AUTO bridge reactivation, paper
bridge work, monitoring/dashboard work, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 27. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation requires exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

No full pytest is required unless repo-local convention or validation issues
require it.

## 28. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, implementation
authority, or human-gate execution authority.

It is Scope 6 / R2S integration design only.

## 29. Next-package posture

After merge, the default next sequential package is WP-S2c-162 lab agent roles
/ operating boundaries, unless Main/Karl directs otherwise.

WP-S2c-162 is not Karl-gated unless Main/Karl directs otherwise.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler/query-view packages.
