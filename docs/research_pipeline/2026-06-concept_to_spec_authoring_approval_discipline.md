# Concept-To-Strategy-Spec Authoring And Approval Discipline

## 1. Scope

WP-S2c-153 / WP-12fz is a Tier 1 documentation-only substantive design package.

It defines the concept-to-Strategy-Spec authoring and approval discipline after
concept ingestion and before draft Strategy Spec authoring.

It creates only this design document, updates `docs/research_pipeline/README.md`
with one additive index entry, and updates `docs/project_status.md`.

It creates no concept artifact, Strategy Spec artifact, schema, validator,
parser/compiler, query view, code, test, fixture, storage path, implementation,
strategy execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-152 opened the concept-ingestion design track and handed off WP-S2c-153
as the default next sequential lab package.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake through
advisory ranked output.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Discipline objective

This discipline decides when a raw idea or future concept record is clear enough
to support draft Strategy Spec authoring.

It prevents raw source claims from becoming Strategy Specs without review.

It preserves source provenance, unsupported claims, missing data, invalid
assumptions, and human-review disposition.

It keeps the boundary between concept, Strategy Spec, variant population,
evidence, and decision surfaces explicit.

## 4. Lifecycle placement

This discipline sits after concept ingestion and before draft Strategy Spec
authoring.

It does not replace Strategy Spec approval, variant population
pre-registration, EXP / REP, trial-log, OL, REC, DEC, Scope 6 gates, or existing
human-gate discipline.

It is a control point that can reject, defer, split, merge-lineage, or allow
draft Strategy Spec authoring.

## 5. Concept reviewability minimums

A concept can be reviewable only when these information families are present or
explicitly marked unresolved:

- source or provenance is known or explicitly marked unknown;
- claimed economic mechanism is stated;
- market or instrument assumption is stated or flagged as unresolved;
- timeframe assumption is stated or flagged as unresolved;
- required data or input assumptions are stated or flagged as unresolved;
- entry, exit, and risk concept is clear enough for review or flagged as
  incomplete;
- parameter hints or no-parameter posture is stated when present;
- performance claims are separated from evidence;
- known missing information is recorded;
- unsafe or prohibited interpretations are recorded.

These are information families only. They are not schema fields, exact field
names, validator contracts, storage requirements, or implementation APIs.

## 6. Concept review outcomes

Future concept-review outcomes may include:

- reject;
- defer pending clarification;
- defer pending data or timeframe authorization;
- allow draft Strategy Spec authoring;
- split into multiple concepts;
- merge with an existing concept lineage if later storage supports it.

No status enum is locked here.

## 7. Human gates before Strategy Spec drafting

Human review is required before draft Strategy Spec authoring at initial lab
maturity.

The reviewer may be Karl, Main, user, or another later-defined human role. This
package does not lock role names or responsibility routing.

Approval to draft a Strategy Spec means only that the concept is clear enough to
draft a Strategy Spec.

It does not mean candidate approval, EXP authority, sweep authority, paper/live
approval, ranking authority, recommendation authority, promotion authority,
runtime authority, or human-gate execution authority.

## 8. Draft Strategy Spec authoring boundary

A draft Strategy Spec must remain governed by WP-S2c-151:

- future artifact/surface is Strategy Spec;
- Strategy DSL is constrained representation discipline;
- JSON-compatible canonical artifact family plus optional non-canonical
  Markdown narrative companion is locked;
- conceptual mandatory field groups are locked only at group level;
- non-executable declarative posture is locked.

This package does not create any draft Strategy Spec.

It does not decide exact fields, schema, storage path, examples,
parser/compiler, validators, or implementation behavior.

## 9. Unsupported-claim handling

Performance claims from papers, videos, online notes, screenshots, user
prompts, or other source material remain claims until tested through an
authorized evidence flow.

Claims must not be promoted to evidence, ranking, recommendation, expected
performance, or approval posture.

Source quality may influence review caution but cannot create ranking authority.

Unsupported claims may be carried forward as assumptions or test targets only if
human review allows draft Strategy Spec authoring.

## 10. Missing-data and unavailable-input handling

Missing data or unresolved timeframe assumptions block progression unless they
are explicitly marked unresolved and deferred.

Concepts needing unavailable inputs, new data procurement, or timeframe-status
changes cannot proceed to draft Strategy Spec authoring until authorization is
resolved.

`docs/data_catalog.md` and `research/timeframe_status.md` remain source-of-truth
surfaces for available inputs and timeframe posture.

This package creates no data-catalog or timeframe-status change.

## 11. Unsafe or forbidden-assumption handling

Concepts requiring runtime or protected-path contact, broker/exchange/order
contact, paper/live bridge, AUTO bridge reactivation, A2C-003, C/F reopening,
A/D/E reopening, or Track 3 reactivation must be rejected or deferred.

Concepts requiring executable code, arbitrary shell/Python/SQL/network calls,
file-writing commands, or protected-path references cannot progress.

Concepts that imply automatic gate satisfaction, promotion, ranking authority,
recommendation authority, transition authority, or readiness authority cannot
progress.

## 12. Provenance flow into Strategy Spec

Future draft Strategy Specs should inherit concept provenance, including source
type, source locator/citation/filename, user prompt lineage where applicable,
source summary, extraction or review timestamp concept, reviewing agent or human
reviewer concept, and revision/supersession context.

Provenance must allow audit from idea to concept to Strategy Spec to variant
population to future evidence.

No hash algorithm, file path, schema field, or storage convention is locked
here.

## 13. Concept-to-Strategy-Spec linking requirements

Future concept records should link forward to draft Strategy Specs.

Future Strategy Specs should link backward to source concept records.

Links must preserve lineage and prevent orphan Strategy Specs.

Exact link fields, IDs, paths, storage, and schema are deferred.

A concept-to-spec link is not evidence and is not approval beyond draft-authoring
permission.

## 14. Relationship to WP-S2c-151 Strategy Spec lock

This discipline must not modify or weaken the WP-S2c-151 lock.

It must not add exact schema fields to the Strategy Spec.

It must not introduce `locked` as a Strategy Spec status.

It must not use `research/candidate_registry.jsonl` as Strategy Spec storage.

It must not decide Strategy Spec / variant-population mapping to EXP or
trial-log.

## 15. Relationship to existing evidence artifacts

Candidate registry, EXP, REP, trial-log, OL, REC, DEC, query views, data
catalog, and timeframe status remain existing source-of-truth surfaces.

Concept/spec discipline is upstream of evidence.

No concept review outcome is evidence.

No draft Strategy Spec is evidence.

The existing artifact chain remains untouched.

## 16. Review-status posture

Review status remains conceptual only.

Suggested future status concepts may include:

- draft concept;
- clarification required;
- data blocked;
- rejected;
- allowed for draft Strategy Spec authoring.

These are not enum locks. The final status set is deferred.

## 17. Deferrals to later storage/schema packages

The following are explicitly deferred:

- concept schema;
- concept storage path;
- concept IDs;
- concept validator;
- Strategy Spec schema;
- Strategy Spec storage path;
- Strategy Spec validator;
- examples/fixtures;
- parser/compiler;
- concept-to-spec link field names;
- revision/supersession mechanics;
- evidence bridge;
- implementation.

## 18. Stop conditions before artifact creation

Before any future package creates concept or Strategy Spec artifacts, it must
have:

- explicit authorization for artifact creation;
- locked or approved storage path;
- schema or schema-design authorization;
- validator plan or validator authorization;
- protected-boundary review;
- clear separation from candidate registry and evidence artifacts;
- confirmation that no runtime/protected-path work is introduced.

## 19. Handoff to WP-S2c-154

WP-S2c-154 is expected to begin variant generation design after concept/spec
approval discipline.

WP-S2c-154 must not assume real concept or Strategy Spec artifacts exist.

It should design how approved Strategy Specs could later produce bounded
variant populations while preserving pre-registration and anti-overfit controls.

If WP-S2c-154 requires unresolved concept/spec storage details, it should record
dependencies, not implement storage.

## 20. Protected boundaries

This discipline explicitly preserves:

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

Validation should confirm exact changed-file scope, integrity views and
validators per doc-narrow convention, and no implementation or authority
creation.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 22. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, or human-gate
execution authority.

It is planning and review-discipline structure only.

## 23. Next-package posture

After merge, the default next sequential package is WP-S2c-154 variant
generation design opening, unless Main/Karl directs a different authorized lab
package.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler packages.
