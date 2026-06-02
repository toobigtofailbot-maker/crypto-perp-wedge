# Variant / Storage Consolidation

## 1. Scope

WP-S2c-157 / WP-12gd is a Tier 1 documentation-only consolidation and
decision-prep package.

It consolidates variant/storage design across WP-S2c-154 variant generation,
WP-S2c-155 sweep orchestration, and WP-S2c-156 result population / storage
design. It prepares WP-S2c-158 as the expected Karl-gated storage / variant
lock.

It creates only this consolidation document, updates
`docs/research_pipeline/README.md` with one additive index entry, and updates
`docs/project_status.md`.

It creates no variant manifest, sweep plan, run manifest, result population,
result-storage path, metrics table, schema, validator, query view, parser,
compiler, code, test, fixture, implementation, sweep, backtest, optimizer run,
result aggregation, strategy execution, or authority.

It does not itself lock storage or artifact decisions. WP-S2c-158 is the
expected Karl-gated lock.

## 2. Authorization and repo-truth basis

WP-S2c-154 opened variant-generation design after concept-to-Strategy-Spec
discipline and under the WP-S2c-151 Strategy Spec / Strategy DSL lock.

WP-S2c-155 defined sweep-orchestration design for future pre-registered
variant populations.

WP-S2c-156 defined result population / storage design and handed off
WP-S2c-157 as the default next sequential lab package.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction: `Strategy Spec`
is the future human-reviewable artifact/surface, `Strategy DSL` is constrained
representation discipline, and implementation remains forbidden until later
explicit authorization.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.
Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Consolidation objective

This package consolidates the variant/storage tranche into a decision-ready
shape for WP-S2c-158.

It identifies which future surfaces are likely needed, which can remain
conceptual, and which decisions must remain deferred.

It prevents premature schema, storage, ID, query-view, or implementation
decisions while giving WP-S2c-158 explicit lock prompts.

It preserves canonical evidence discipline and avoids parallel authority.

## 4. Consolidated lifecycle position

The consolidated future path is:

1. approved Strategy Spec;
2. bounded pre-registered variant population;
3. sweep planning and possible run manifest;
4. future authorized offline sweep execution;
5. complete result population;
6. anti-overfit / advisory ranking review;
7. canonical evidence and gate routing.

All of these are future surfaces unless already canonical repo artifacts. This
package creates no real artifacts, instances, paths, schemas, or executable
steps.

The separation remains: idea, concept, Strategy Spec, variant, sweep, result,
evidence, and decision are distinct surfaces.

## 5. Consolidated surface map

| Surface | Purpose | Likely future status | Canonical or intermediate | Main open question | WP-S2c-158 lock relevance |
|---|---|---|---|---|---|
| Strategy Spec | Human-reviewable strategy logic and bounded assumptions | Already high-level locked by WP-S2c-151; no instance exists | Upstream planning surface | Exact schema, storage, status, and links remain deferred | Preserve lock; do not modify |
| Variant population manifest | Freeze concrete tested universe before execution | Likely required future surface | Intermediate pre-registration surface | Exact path, ID, schema, amendment, and EXP/trial-log mapping | High |
| Sweep plan | Coordinate intended offline research run | Likely future planning surface | Intermediate planning surface | Whether distinct from run manifest | Medium/high |
| Run manifest | Record execution authorization, environment, data slices, runner config, destination, and lineage | Possibly required future surface | Intermediate execution-accounting surface | Whether separate from sweep plan or merged | Medium/high |
| Result population | Preserve complete sweep output population | Required conceptually; representation undecided | Intermediate evidence input or canonical-only representation | Separate artifact, canonical-only, or hybrid | High |
| EXP | Pre-execution experiment plan grammar | Existing canonical artifact family | Canonical evidence-planning surface | One EXP per population or many EXPs by segment/family | High |
| REP | Executed experiment report grammar | Existing canonical artifact family | Canonical evidence-result surface | How full populations feed or link to REP | High |
| Trial-log | Append-only trial metrics | Existing canonical evidence surface | Canonical trial surface | Variant/seed/fold/run row mapping | High |
| OL / REC / DEC | Outcome, reconciliation, and decision surfaces | Existing canonical decision/evidence chain | Canonical downstream surfaces | How population evidence routes without bypass | Medium |
| Query/read-model views | Inspect artifacts and integrity | Possible future read-only surfaces | Read model only | Shape waits for locked storage semantics | Medium |
| Advisory ranking artifact | Order robust research outputs for human review | Future design in WP-S2c-159/160 | Advisory-only surface | Anti-overfit and ranking semantics | Low for storage lock; dependency only |

## 6. Variant population surface assessment

WP-S2c-154 frames variant generation as future controlled derivation of a
bounded, pre-registered population from an approved Strategy Spec.

A future variant population manifest is likely needed to freeze the tested
universe before sweep execution. It should preserve parameter bounds, invalid
combinations, exclusions, trial budget, lineage, and pre-registration posture.

The manifest should not be evidence, approval, candidate registration,
ranking, paper/live readiness, promotion, transition, recommendation, or
runtime authority.

Exact schema, storage path, ID, amendment shape, and EXP/trial-log mapping
remain open.

## 7. Sweep plan / run manifest surface assessment

WP-S2c-155 frames sweep orchestration as future planning and coordination for
offline research only.

Sweep planning is likely needed to coordinate authorized future research
without creating execution authority. It should preserve variant population
reference, data/timeframe assumptions, trial budget, allowed execution context,
result capture expectations, and stop conditions.

A run manifest may be needed to connect execution authorization, environment
assumptions, runner configuration, data slices, result destination, and
lineage.

Separate sweep plan and run manifest surfaces may or may not both be necessary.
The exact split remains open for WP-S2c-158 or later storage/schema design.

## 8. Result population surface assessment

WP-S2c-156 frames result population as the future complete record of all
variants and run outcomes from an authorized sweep.

Result population is needed conceptually to prevent winner-only retention and
support population-level anti-overfit review.

It must preserve attempted, failed, invalid, excluded, errored, aborted,
data-unavailable, timeout/resource-failure, filtered, and successful variants.

It should preserve metric families, lineage, trial-budget context, and
multiple-testing exposure.

Whether this should be a separate intermediate artifact, be represented
entirely through EXP / REP / trial-log plus query views, or use a hybrid model
remains open.

## 9. Recommended storage model for WP-S2c-158 consideration

Non-locking recommendation for WP-S2c-158 consideration:

- lock the need for a future variant population manifest as a separate
  pre-registration surface;
- lock the need for a future run-manifest or sweep-plan surface, while
  deferring the exact split if it remains too early;
- lock the need to preserve complete result populations;
- prefer a hybrid result model:
  - canonical evidence remains EXP / REP / trial-log / OL / REC / DEC;
  - a future intermediate result-population surface may exist only if it links
    into canonical evidence and does not become a parallel decision source;
- defer exact storage paths, schemas, field names, validators, examples, query
  views, IDs, and implementation.

This direction is recommended because variant-population pre-registration needs
a durable surface; result-population completeness may be difficult to preserve
through only summary reports; the canonical evidence chain must remain source
of truth; and a hybrid model reduces winner-only risk while preserving
canonical authority.

This package does not lock that recommendation.

## 10. Evidence-chain mapping options

Option A: one variant population maps to one EXP and one REP with many trials.
This is simple and keeps the population together, but it may stress REP detail
and trial-log granularity.

Option B: one variant population maps to many EXPs / REPs by segment, family,
or other bounded partition. This can improve readability, but it risks
fragmenting trial-budget and population context.

Option C: one variant population maps to a future intermediate
result-population surface that feeds REP and trial-log. This may preserve
complete population detail, but it must not become a parallel evidence or
decision source.

Option D: no intermediate result-population surface; EXP / REP / trial-log
carry all result-population detail. This minimizes parallel-source risk but may
make full-population retention and queryability harder.

WP-S2c-158 should lock the high-level principle that canonical evidence remains
EXP / REP / trial-log / OL / REC / DEC, while keeping the exact mapping open.
It may also lock that any intermediate surface must be evidence input only and
must link to canonical evidence.

## 11. Intermediate result-surface decision options

Option A: no intermediate result-population artifact; canonical EXP / REP /
trial-log only.

Option B: intermediate result-population artifact with canonical links and no
decision authority.

Option C: hybrid: small intermediate population index plus canonical EXP / REP
/ trial-log detail.

Non-locking preferred option for WP-S2c-158 consideration: Option C, or Option
B if a full intermediate surface proves necessary. Option C keeps full
population retention and queryability visible while reducing parallel-source
risk and implementation burden.

Tradeoffs:

- parallel-source risk is lowest under Option A and highest under Option B if
  boundaries are weak;
- full-population retention is strongest under Option B and C;
- queryability is strongest under Option B and C;
- implementation burden is lowest under Option A and highest under Option B;
- evidence-chain clarity depends on explicit links and non-authority language.

No final option is chosen here.

## 12. Trial-budget and multiple-testing consolidation

Trial budget must be visible before execution and amendment-audited.

It must account for variants, segments, seeds, folds, walk-forward windows,
retries, reruns, and exploratory repeats.

Multiple-testing exposure must remain visible to later DSR or
multiple-testing-aware logic.

Trial budget must connect variant population, sweep/run manifest, result
population, and future evidence. Many tried variants are evidence burden, not
permission to claim a headline winner.

## 13. Pre-registration and amendment consolidation

Variant population pre-registration should freeze the intended tested universe
before execution.

Amendments must be explicit, timestamped conceptually, reasoned, and
audit-preserving.

Post-result deletion, winner-only filtering, silent trial-budget expansion, or
silent variant-universe changes are forbidden.

Exact amendment schema, storage, status, and supersession mechanics remain
deferred.

## 14. Anti-overfit support consolidation

Future variant/storage design must support:

- full population retention;
- failed, invalid, excluded, errored, aborted, filtered, timeout, and
  data-unavailable visibility;
- parameter sensitivity review;
- PnL concentration review;
- segment brittleness review;
- drawdown and cost-drag review;
- trial-budget and multiple-testing exposure;
- no hidden hand-selection;
- no post-hoc unrecorded pruning.

WP-S2c-159 / WP-S2c-160 should later design anti-overfit / DSR population logic
and advisory ranking artifact semantics after the storage/variant lock.

## 15. ID, linking, and provenance questions

Open questions:

- How should Strategy Spec IDs link to variant populations?
- How should variant population IDs link to sweep plans / run manifests?
- How should result populations link back to sweep/run surfaces and forward to
  EXP / REP / trial-log?
- Should IDs be human-readable, hash-based, sequential, or hybrid?
- What provenance must be content-fingerprinted?
- How should revisions and supersession work?
- How should amendments preserve original versions?
- How should data, runner, environment, and package references be represented
  without creating implementation authority?

All exact ID/link mechanics remain deferred unless WP-S2c-158 locks high-level
principles.

## 16. Storage and schema questions

Open questions:

- Where should future variant population manifests live?
- Where should future sweep/run manifests live?
- Where should future result population surfaces live, if used?
- Which future schemas are needed?
- Which validators are needed?
- Which examples/fixtures are safe and when?
- Which fields are mandatory versus optional?
- Which fields are implementation details?
- Which surfaces are canonical, intermediate, advisory, or read-only?

No storage path, schema, validator, field, fixture, or example decision is made
here.

## 17. Query-view and read-model questions

Future query/read-model surfaces may be needed to inspect variant populations,
sweep/run status, result populations, trial budget, and anti-overfit evidence.

Query views must not become authority. Current query-layer posture remains
read-only and in-memory.

Query-layer changes are not authorized here. Any query-view design must wait
until artifacts and storage semantics are locked.

## 18. Rejected and out-of-scope alternatives

Unbounded parameter search is rejected because it weakens pre-registration,
DSR, and multiple-testing discipline.

Winner-only result retention is rejected because it creates survivorship bias
and hides failed, invalid, excluded, errored, or aborted attempts.

Direct runner invocation from variant generation is rejected because variant
generation is not execution authority.

Result population as ranking authority is rejected because result population is
evidence input or canonical evidence support only.

Candidate registry as variant/result storage is rejected because the registry
tracks candidates and evidence links, not upstream Strategy Specs or sweep
populations.

EXP / REP / trial-log bypass through a parallel evidence store is rejected
because it would duplicate source-of-truth responsibilities.

Immediate schema, validator, query-view, parser/compiler, code, or
implementation work is rejected as premature and out of scope.

Paper/live bridge or runtime coupling is rejected because protected runtime
boundaries remain strict.

Track 3 / AUTO reactivation is rejected as outside this lab storage/variant
decision-prep package.

## 19. Recommended WP-S2c-158 lock packet

| Proposed lock item | Recommended option | Deferred details | Rejected alternatives | Dependencies | Risks | Stop conditions |
|---|---|---|---|---|---|---|
| Future variant population manifest | Lock as required pre-registration surface | Path, schema, ID, fields, examples, validators | No durable pre-registration, candidate registry storage | WP-S2c-151, WP-S2c-154 | Premature schema pressure | Any artifact/schema creation |
| Complete result-population preservation | Lock as required | Representation, storage, metric schema | Winner-only retention | WP-S2c-156 | Parallel-source risk if stored badly | Any result artifact creation |
| Canonical evidence chain | Lock EXP / REP / trial-log / OL / REC / DEC as authoritative | Exact mapping from population to canonical surfaces | Parallel evidence store | Existing artifact grammar | Mapping ambiguity | Any bypass of canonical evidence |
| Intermediate result-population boundary | Lock no decision authority if later created | Artifact/index choice, links, fields | Result surface as ranking or approval | WP-S2c-156, WP-S2c-157 | Source-of-truth confusion | Any ranking/approval authority |
| Deferred implementation details | Lock deferral of paths, schemas, validators, query views, IDs, examples, parser/compiler, implementation | All exact mechanics | Immediate implementation | Later storage/schema packages | Too little precision for implementers | Any exact schema/path lock here |
| Execution non-authorization | Lock no sweep execution, runner invocation, result aggregation, or implementation | Future implementation authorization | Execution-by-manifest or execution-by-plan | Protected-boundary docs | Authority leakage | Any runner/runtime/protected contact |

## 20. Karl decision prompts for WP-S2c-158

1. Should WP-S2c-158 lock a future variant population manifest as the required
   pre-registration surface before sweep execution?
2. Should WP-S2c-158 lock complete result-population preservation, including
   attempted, failed, invalid, excluded, errored, aborted, filtered,
   data-unavailable, and successful variants?
3. Should WP-S2c-158 lock EXP / REP, trial-log, OL, REC, and DEC as canonical
   evidence/decision surfaces, with no parallel decision authority?
4. Should WP-S2c-158 prefer a hybrid result model: canonical evidence remains
   authoritative, while a future intermediate result-population surface may be
   designed only as evidence input / index with no authority?
5. Should WP-S2c-158 defer exact storage paths, schemas, validators, query
   views, examples, IDs, parser/compiler, runner integration, and
   implementation?
6. Should WP-S2c-158 explicitly forbid sweep execution, result aggregation,
   ranking authority, paper/live authority, runtime contact, protected-path
   contact, and Track 3 / AUTO reactivation?
7. Should Side stop after WP-S2c-157 merge and request explicit Karl lock
   direction before drafting WP-S2c-158?

Recommended answer for all prompts: yes, subject to any changes Main/Karl
provides.

## 21. Open questions classification

| Question | Recommended disposition | Reason | Destination |
|---|---|---|---|
| Variant manifest requiredness | Lock required future surface | Pre-registration needs durable population freeze | WP-S2c-158 lock |
| Sweep plan versus run manifest split | Lock need for future planning/run-accounting surface, defer exact split | Split depends on later implementation and storage semantics | WP-S2c-158 lock / later schema-storage design |
| Result population representation option | Prefer hybrid non-locking; lock complete preservation | Full retention and canonical authority both matter | WP-S2c-158 lock |
| EXP / REP / trial-log mapping | Lock canonical chain, defer mapping | Exact row/report shape is premature | Later schema/storage design |
| Trial-budget accounting | Lock high-level accounting obligation | Multiple-testing exposure must be visible before execution | WP-S2c-158 lock |
| Amendment semantics | Lock audit-preserving principle, defer schema | Needed to prevent silent post-result mutation | Later schema/storage design |
| ID/linking model | Defer exact mechanics | IDs depend on storage and schema | Later schema/storage design |
| Storage path | Defer | Path choice would create premature artifact authority | Later schema/storage design |
| Schema/validator plan | Defer | Validators require locked surfaces | Later implementation authorization |
| Query-view/read-model plan | Defer | Query views depend on locked storage semantics | Later schema/storage design |
| Examples/fixtures | Defer | Examples can accidentally create artifact precedent | Later schema/storage design |
| Runner integration | Reject here; defer until explicit implementation authorization | Execution remains unauthorized | Later implementation authorization |
| Implementation authorization | Reject here | WP-S2c-157 and WP-S2c-158 are decision-prep/lock only | Later implementation authorization |
| Advisory ranking semantics | Defer | Ranking artifact is later design and advisory-only | WP-S2c-159/160 anti-overfit / advisory ranking |
| Candidate registry as storage | Reject | Blurs candidate status with upstream populations/results | Rejected / out of scope |

## 22. Relationship to later WP-S2c-159 / WP-S2c-160

WP-S2c-159 / WP-S2c-160 should design anti-overfit / DSR population logic and
the advisory ranking artifact after the storage/variant lock.

They must consume the locked variant/storage posture from WP-S2c-158.

They must not create ranking authority or recommendation authority unless
explicitly authorized.

Result-population design should preserve enough context for those packages but
does not implement them.

## 23. Protected boundaries

This consolidation explicitly preserves:

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

Validation must confirm exact changed-file scope:

- `docs/research_pipeline/2026-06-variant_storage_consolidation.md`;
- `docs/research_pipeline/README.md`;
- `docs/project_status.md`.

Integrity views and validators should run per doc-narrow convention.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 25. Stop conditions

Stop if any content creates a variant manifest, sweep plan, run manifest,
result population, result-storage path, metrics table, concept artifact,
Strategy Spec artifact, schema, validator, parser/compiler, fixture, storage
path, artifact instance, query view, or implementation.

Stop if any content creates or ingests a real strategy idea, concept, Strategy
Spec, parameter grid, variant population, sweep plan, run manifest, result set,
metrics table, or result population as a committed artifact.

Stop if any content makes the WP-S2c-158 lock decision instead of preparing
prompts.

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

## 26. Non-authority boundary

This consolidation creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority, ranking/scoring
authority, promotion authority, transition authority, readiness authority, or
human-gate execution authority.

It is design consolidation and decision preparation only.

## 27. Next-package posture

After merge, do not automatically draft WP-S2c-158.

Side must report the WP-S2c-158 Karl decision prompts and get explicit lock
direction.

WP-S2c-158 is Karl-gated.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler/query-view packages.
