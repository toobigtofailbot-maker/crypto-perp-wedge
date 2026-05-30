# Path B Reassessment Design Substance

## 1. Scope

WP-S2c-121 / WP-12fa is a Tier 1 documentation-only design-substance package.
It creates only this substance document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package produces Path B reassessment options and trade-offs only. It does
not select, lock, approve, reject, defer, or authorize any option. It does not
authorize Path B execution.

## 2. Repo-truth basis

WP-S2c-120 is merged and opened the Path B reassessment design tranche.
WP-S2c-119 is merged and closed the second cross-candidate diagnostic brief
tranche.

The diagnostic brief is diagnostic only. It does not recommend, rank, score,
select, approve, transition, or determine readiness.

Current Scope 6 surface is complete at schema, validator, and query-layer
level:

- WP-S2c-113 locked Scope 6 artifact families.
- WP-S2c-114 introduced Scope 6 schemas.
- WP-S2c-115 introduced Scope 6 validators.
- WP-S2c-117 introduced Scope 6 query-layer views.

Related locked repo-truth anchors remain in force:

- WP-S2c-100 locked refined approval/readiness criteria.
- WP-S2c-104 locked implementation authorization and deferred monitoring,
  dashboard, and paper bridge work.
- WP-S2c-105 through WP-S2c-110 completed the bounded shadow adapter plus
  parity tooling tranche.

Existing canonical artifacts and existing briefs are historical records and are
not modified by this package.

## 3. Current diagnostic baseline

WP-S2c-119 records the current diagnostic baseline:

- ten concluded baseline-tested candidates;
- one reserved draft row;
- no active research candidate flowing through R2S/S2P approval surfaces;
- all concluded groups remain NO-GO in the diagnostic brief's described
  current state;
- search-space coverage remains sparse by strategy-family/timeframe;
- information-input coverage is concentrated in existing crypto-perp internal
  streams;
- Scope 6 base views return zero rows;
- Scope 6 inventory/link views operate under zero-instance state;
- Q08 full integrity sweep and Q11 Scope 6 integrity subset returned `[]`.

None of these facts determine readiness, recommend a candidate, rank a
candidate, score a candidate, approve a transition, or authorize Path B
execution.

## 4. Design objective

This document produces evidence-kind expansion options for Main/Karl review.
All options are framed inside locked boundaries. The package makes downstream
package shape and cost legible while preserving the distinction between design,
locking, execution authorization, and execution.

WP-S2c-122 may consume this substance and consolidate it into lock-candidate
wording. This document itself does not provide final lock-candidate wording.

## 5. Evidence-kind expansion dimensions

The design dimensions from WP-S2c-120 are:

- strategy-family expansion;
- timeframe expansion within locked timeframe-status discipline;
- information-input combinations within locked taxonomy;
- candidate-instance dimensions;
- data/evidence-type expansion that remains inside approved non-runtime
  research boundaries;
- narrower versus broader Path B variants;
- hold / do-nothing alternative.

These are design dimensions only. They are not authorizations to create
candidates, pre-register hypotheses, run backtests, create research artifacts,
change taxonomy, change timeframe discipline, or modify schemas, validators, or
query views.

## 6. Option A — hold / no Path B execution

Design summary: do not execute Path B now. Maintain current infrastructure and
wait for other evidence or Main/Karl direction.

Diagnostic trace: current infrastructure is healthy but empty for Scope 6
instances. WP-S2c-119 records no active research candidate flowing through
R2S/S2P surfaces.

Evidence-kind expansion involved: none.

Expected downstream work package shape/cost: zero Path B execution WPs. If the
hold persists, a future routing or report-back package may be useful to refresh
state, but that is not required by this option.

Schema/validator/query-layer implication: no schema, validator, or query-layer
changes.

Preservation note: all gates, locks, human gates, Phase 1 paper runtime
protection, Tier 4 boundaries, and Path B non-authorization remain unchanged.

Trade-offs: this is the lowest-risk and lowest-work option. It does not
re-prime the research pipeline and leaves the empty active-candidate state
unchanged.

Stop/decision triggers: stop if maintaining the hold would be reframed as
candidate rejection, readiness determination, or Path B option selection.

## 7. Option B — narrow Path B within current taxonomy and timeframe discipline

Design summary: reassess a narrow Path B execution shape that expands only
within already-locked or known strategy-family, timeframe, and information-input
disciplines.

Diagnostic trace: WP-S2c-119 shows sparse strategy-family/timeframe coverage
and concentrated information-input coverage. This option would use that
coverage view to identify under-exercised combinations without selecting any
candidate in this tranche.

Evidence-kind expansion involved: limited new research evidence around
under-covered family/timeframe/input combinations, without new taxonomy,
runtime contact, Tier 4 contact, or protected-path contact.

Expected downstream work package shape/cost: likely a small design/locking
package plus a limited execution tranche if later authorized. Rough cost range:
low single-digit to low-teens WPs, depending on the exact later lock.

Schema/validator/query-layer implication: existing experiment artifacts are
likely sufficient if later execution fits current grammar. Validators and query
surfaces should remain unchanged unless a later package proves an explicit gap.

Preservation note: D2-006, D2-007, REC-5, permanent human gates, and Path B
execution non-authorization remain unchanged.

Trade-offs: this is the safest active re-prime route, but it may be too narrow
to address the observed failure distribution.

Stop/decision triggers: stop if the narrow route requires taxonomy changes,
timeframe-status changes, candidate registration, hypothesis pre-registration,
backtest execution, or option selection in the design tranche.

## 8. Option C — information-input combination expansion within locked taxonomy

Design summary: focus Path B on new combinations of already-allowed information
inputs, without adding new information-input taxonomy labels.

Diagnostic trace: WP-S2c-119 information-input coverage shows existing inputs
are concentrated in a limited set of crypto-perp internal streams:
`funding_8h`, OHLCV labels, and mark/index/premium labels. Several labels occur
for only one candidate.

Evidence-kind expansion involved: new combinations of OHLCV, funding, mark,
index, and premium-style inputs only where those labels are already inside
locked taxonomy and current repo truth.

Expected downstream work package shape/cost: moderate. Later work may need one
or more packages to design and lock exact input-combination grammar before any
execution if current artifact grammar proves insufficient.

Schema/validator/query-layer implication: likely no schema changes if existing
`information_inputs` fields support combinations. If taxonomy extension is
needed, that is a stop condition for this design path, not an implementation
detail.

Preservation note: locked information-input taxonomy remains unchanged. No
external data, Tier 4 contact, runtime contact, or protected-path contact is
introduced.

Trade-offs: this targets a clear diagnostic coverage gap, but it risks taxonomy
drift if later packages do not tightly bound allowed labels and combinations.

Stop/decision triggers: stop if a later route needs a new information-input
label, external data source, paid data path, or reinterpretation of existing
input labels without explicit Main/Karl lock.

## 9. Option D — candidate-instance dimension expansion

Design summary: reassess whether Path B should expand candidate-instance
dimensions such as parameter families, market-condition slices, or evidence
segmentation around existing approved research lanes.

Diagnostic trace: current concluded candidates are all NO-GO. Current
candidate-instance coverage may be too sparse to distinguish whether failures
are family-level, timeframe-level, input-level, or instance-design-level.

Evidence-kind expansion involved: more structured candidate-instance evidence
without registering a candidate in this tranche.

Expected downstream work package shape/cost: moderate to high if later
authorized. Execution would need clear pre-registration, experiment-plan,
report, trial-log, and outcome-ledger discipline.

Schema/validator/query-layer implication: existing experiment artifact grammar
may be sufficient for bounded instance dimensions. Later query-layer additions
may be needed only if new instance dimensions are not inspectable through
current views, and that would require separate authorization.

Preservation note: REC-5 exact-segment discipline remains absolute. No pooled
cross-segment inference below floor is permitted.

Trade-offs: this improves diagnostic resolution but can expand work quickly if
instance axes are not tightly bounded.

Stop/decision triggers: stop if this option drifts into candidate ranking,
candidate recommendation, candidate readiness, pooled REC-5 inference, or
unbounded parameter search.

## 10. Option E — broader Path B evidence-kind expansion, bounded by current locks

Design summary: explore a broader Path B design that could include new strategy
families, new timeframe coverage within locked timeframe-status discipline, and
new data/evidence-type categories that remain non-runtime and non-Tier-4.

Diagnostic trace: the search-space matrix remains sparse, including the
reserved/non-concluded coverage. Broader expansion could address structural
coverage gaps across strategy family, timeframe, and evidence type.

Evidence-kind expansion involved: multi-axis expansion across strategy family,
timeframe, and evidence type while preserving all locked boundaries.

Expected downstream work package shape/cost: high and variable. A later
authorized path would likely require multiple tranches. Rough cost range: high
single-digit to 25 WPs depending on option lock and validation burden.

Schema/validator/query-layer implication: this option has a higher chance of
needing schema or query-layer design before execution. Any locked taxonomy or
timeframe-status change is a stop condition.

Preservation note: no runtime/protected contact, Tier 4 contact, gate
weakening, readiness shortcut, ranking, scoring, or recommendation authority is
introduced.

Trade-offs: this offers the largest coverage gain but has the highest scope,
validation, and semantic-drift risk.

Stop/decision triggers: stop if broader expansion requires locked taxonomy
change, timeframe-status change, protected-path work, Tier 4 contact, candidate
generation authority, or candidate recommendation/ranking/scoring.

## 11. Option F — mixed phased Path B

Design summary: stage Path B reassessment into a narrow first execution slice
and a later optional broader slice if Main/Karl later authorizes it.

Diagnostic trace: the empty active pipeline argues for a small re-prime, while
sparse coverage suggests a broader backlog may exist.

Evidence-kind expansion involved: phased evidence-kind expansion, starting with
the most bounded expansion and deferring broader evidence kinds.

Expected downstream work package shape/cost: medium. The first slice may be low
single-digit to low-teens WPs, with a later optional tranche gated by evidence
and Main/Karl review.

Schema/validator/query-layer implication: this likely minimizes immediate
schema, validator, and query-layer changes. Later slices may require design
refresh if they expose gaps.

Preservation note: each phase must separately preserve locked gates, human
authority, timeframe discipline, information-input discipline, Phase 1 paper
runtime protection, and Tier 4 boundaries.

Trade-offs: this balances momentum and safety, but adds sequencing complexity
and later re-engagement overhead.

Stop/decision triggers: stop if phasing is used to imply automatic continuation
from a narrow slice into broader execution, or if later phases are treated as
pre-authorized.

## 12. Cross-option comparison

All rows below are DESIGN OPTIONS / NOT SELECTED / NOT LOCKED.

| Option | Scope size | Execution risk if later authorized | Likely WP cost range | Schema/validator/query-layer implication | Candidate/artifact impact if later authorized | Preservation confidence | Main risk | Main benefit |
|---|---|---|---|---|---|---|---|---|
| A - hold | None | None | 0 Path B execution WPs | None | None | High | Pipeline remains inactive | Lowest risk and work |
| B - narrow current-taxonomy route | Small | Low to moderate | Low single-digit to low-teens | Likely none | Limited new plans/reports only if later authorized | High | Too narrow to address failures | Safest active re-prime |
| C - input-combination route | Medium | Moderate | Moderate, exact range depends on grammar | Likely none unless grammar gap appears | New input-combination evidence only if later authorized | Medium-high | Taxonomy drift | Targets concentrated input coverage |
| D - candidate-instance route | Medium to high | Moderate to high | Moderate to high | Possible later query additions | More structured instance evidence only if later authorized | Medium | Unbounded search risk | Better failure diagnosis |
| E - broader evidence-kind route | Large | High | High single-digit to 25 | Higher chance of later schema/query design | Multi-axis evidence only if later authorized | Medium | Scope and semantic drift | Largest coverage expansion |
| F - mixed phased route | Medium | Moderate | First slice low single-digit to low-teens; later tranche optional | Low immediate, possible later refresh | Phased evidence only if later authorized | Medium-high | Implied automatic continuation | Balances momentum and safety |

## 13. Downstream package-shape / cost estimate

Cost ranges are rough planning estimates, not commitments. Actual package count
depends on later Karl resolution.

Possible downstream phases include:

- Karl-gated locking decision package after WP-S2c-122;
- optional execution authorization package if locking resolves toward action;
- possible execution tranche or tranches;
- possible schema, validator, or query-layer design package if a later
  authorized Path B route requires new surfaces.

Path B execution may also remain zero WPs if all options are deferred or
rejected.

## 14. Schema / validator / query-layer implication assessment

Option A has no schema, validator, or query-layer implications.

Option B likely fits existing experiment artifacts if later execution remains
narrow and current-taxonomy. Any schema or query-layer gap would require a
separate later design/authorization package.

Option C likely fits existing `information_inputs` fields if combinations use
already-allowed labels. Any need to modify locked information-input taxonomy is
a stop condition.

Option D likely uses existing experiment artifact grammar for bounded
candidate-instance dimensions, but later query-layer additions may be required
if those dimensions are not inspectable.

Option E has the highest chance of needing schema, validator, or query-layer
design before execution. Any change to WP-S2c-114 schemas, WP-S2c-115
validators, WP-S2c-117 query views, locked information-input taxonomy, or
timeframe-status discipline requires separate later authorization.

Option F minimizes immediate implications by sequencing a narrow slice first
and deferring broader surface changes until after evidence and Main/Karl review.

Existing experiment artifacts may be sufficient for narrow options. Any need to
modify WP-S2c-114 schemas, WP-S2c-115 validators, or WP-S2c-117 query views
requires a separate later design/authorization package. Any need to change
locked information-input taxonomy or timeframe-status discipline is a stop
condition, not an implementation detail.

## 15. Locked-boundary preservation matrix

| Option | Permanent human gates | D2-006 | D2-007 | REC-5 | Phase 9 Decision 9 | WP-S2c-100 locked criteria | WP-S2c-104 authorization | Scope 6 locks/schemas/validators/views | Information-input taxonomy | Timeframe-status discipline | Phase 1 paper runtime | Tier 4/protected paths |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Preserved | Unchanged | Unchanged | Unchanged | Unchanged | Preserved | Unchanged | Unchanged | Unchanged | Unchanged | Preserved | Preserved |
| B | Preserved | Unchanged | Unchanged | Unchanged | Unchanged | Preserved | Unchanged | Unchanged | Stop-if-change-needed | Stop-if-change-needed | Preserved | Preserved |
| C | Preserved | Unchanged | Unchanged | Unchanged | Unchanged | Preserved | Unchanged | Unchanged | Stop-if-change-needed | Unchanged | Preserved | Preserved |
| D | Preserved | Unchanged | Unchanged | Stop-if-change-needed | Unchanged | Preserved | Unchanged | Unchanged unless separately authorized | Unchanged | Stop-if-change-needed | Preserved | Preserved |
| E | Preserved | Unchanged | Unchanged | Stop-if-change-needed | Unchanged | Preserved | Unchanged | Stop-if-change-needed | Stop-if-change-needed | Stop-if-change-needed | Preserved | Preserved |
| F | Preserved phase-by-phase | Unchanged | Unchanged | Stop-if-change-needed | Unchanged | Preserved | Unchanged | Stop-if-change-needed for later slices | Stop-if-change-needed | Stop-if-change-needed | Preserved | Preserved |

## 16. Risks, tensions, and open points

- Exact historical Karl Path B intent may need confirmation before any later
  execution if repo docs do not explicitly resolve it.
- Locked information-input taxonomy source may need confirmation before any
  later execution.
- Timeframe-status discipline may need confirmation before any later execution.
- Broader Path B can drift into candidate generation or ranking if not tightly
  bounded.
- No active candidate means design must not force approval surfaces.
- Execution cost remains uncertain until options are consolidated and resolved.

These risks do not block WP-S2c-121 substance. They are surfaced for
WP-S2c-122/Karl review.

## 17. What this substance does not authorize

This substance does not authorize:

- Path B execution;
- option locking or selection;
- candidate registration;
- hypothesis pre-registration;
- backtest execution;
- research artifact creation;
- schema, validator, or query-layer changes;
- tools or tests changes;
- canonical artifact modification;
- transition authorization;
- candidate readiness determination;
- recommendation, ranking, or scoring;
- human-gate execution;
- Tier 4 contact;
- runtime or protected-path work;
- monitoring or dashboard implementation;
- paper bridge implementation;
- AUTO bridge work;
- A2C-003.

## 18. WP-S2c-122 consolidation posture

WP-S2c-122 should consume this substance. It should consolidate only the
options present in this document. It must not add options and must not
materially change option intent.

WP-S2c-122 should convert each option into lock-candidate wording with
preservation notes. It should prepare Main/Karl resolution prompts where each
option can be marked LOCK / MODIFY / DEFER / REJECT.

WP-S2c-122 must not lock, select, or authorize execution.

## 19. Validation / next-package posture

WP-S2c-121 uses CS12 T1-doc-narrow.

After merge, Side may draft WP-S2c-122 after refreshed-main preflight and no
stop trigger. WP-S2c-122 is T1-doc-narrow and consolidation-only.

After WP-S2c-122 merges, Side must stop and report back to Main 4.0 with
consolidated lock-candidate content. No locking package may be drafted until
Main/Karl resolves each option.
