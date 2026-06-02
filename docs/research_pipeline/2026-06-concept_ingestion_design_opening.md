# Concept Ingestion Design Opening

## 1. Scope

WP-S2c-152 / WP-12fy is a Tier 1 documentation-only design-opening package.

It opens the concept-ingestion design track for the Strategy Research Lab. It
creates only this opening document, updates `docs/research_pipeline/README.md`
with one additive index entry, and updates `docs/project_status.md`.

It creates no concept artifact, concept schema, Strategy Spec artifact,
Strategy Spec schema, validator, query view, parser, compiler, code, test,
implementation, strategy execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-147 defined the Strategy Research Lab target operating model.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-151 identifies WP-S2c-152 concept ingestion design opening as the next
sequential package unless Main/Karl directs otherwise.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Concept-ingestion problem statement

The lab needs a controlled way to turn raw strategy ideas into reviewable
concept records.

Raw ideas may come from user prompts, research papers, articles, videos, online
strategy notes, prior repo docs, or manual observations.

Raw ideas are often ambiguous, incomplete, overfit, unsupported,
data-dependent, or unsafe to translate directly into Strategy Specs.

Without a concept-ingestion layer, the lab risks confusing source claims with
testable specs, losing provenance, creating implicit execution authority, or
smuggling unsupported assumptions into later sweeps.

## 4. Design objective

Concept ingestion is the future process that captures idea source, claims,
assumptions, economic mechanism, required data, missing information, ambiguity,
exclusions, and review posture before Strategy Spec drafting.

This package keeps the topic at opening-design level only.

It creates no concept-record schema, storage, validator, or instances.

## 5. Concept posture

A concept is a future upstream planning surface.

A concept is not a Strategy Spec.

A concept is not a candidate.

A concept is not evidence.

A concept is not pre-registration.

A concept is not approval.

A concept is not strategy recommendation, ranking, paper/live readiness, or
runtime authority.

A concept may be rejected before spec authoring.

## 6. Relationship to lab lifecycle

Concept ingestion belongs between Stage 0 idea intake and Stage 2 Strategy Spec
authoring in the Strategy Research Lab target operating model.

It should feed future Strategy Spec drafting only after human review.

It should preserve enough source and assumption context to support later
provenance and anti-overfit discipline.

It must not bypass Strategy Spec approval, variant-population pre-registration,
EXP / REP, trial-log, OL, REC, DEC, or gates.

## 7. Input-source categories

Future concept ingestion should design for these source categories:

- direct user idea;
- research paper;
- article, blog, or newsletter;
- video or transcript-derived strategy note;
- online forum or social strategy description;
- existing repo research note;
- manual observation from charts or data;
- imported strategy library or pseudo-code, as concept input only;
- hybrid or multiple-source idea.

This package does not ingest any real source.

## 8. Intake information to preserve

Future concept intake should preserve these information families without
creating a schema here:

- source type;
- source locator, citation, or filename where applicable;
- user prompt lineage where applicable;
- source summary;
- claimed edge or economic mechanism;
- market and instrument assumptions;
- timeframe assumptions;
- data and input requirements;
- entry, exit, and risk idea summary;
- parameter hints;
- risk/reward claims;
- performance claims;
- costs, slippage, and funding assumptions;
- unsupported assumptions;
- missing information;
- invalid or unsafe interpretations;
- human-review notes.

## 9. Ambiguity and unsupported-claim handling

Ambiguous ideas become concept questions, not Strategy Specs.

Unsupported performance claims must be recorded as claims, not evidence.

Missing data or timeframe assumptions must block direct Strategy Spec approval
until resolved.

Concepts requiring unavailable data, protected-path contact, paper/live bridge,
broker/exchange contact, or runtime changes must be marked blocked or deferred
at concept level.

Source enthusiasm or online popularity must not become ranking authority.

## 10. Source and provenance requirements

Concept ingestion must preserve source provenance enough to audit from idea to
concept to Strategy Spec to variant population to future evidence.

Future design should include source type, source identifier, author or context
where available, extraction timestamp or package timestamp concept, reviewing
agent, human reviewer, and revision or supersession concept.

No hash algorithm, file path, schema, or storage convention is locked here.

## 11. Concept-to-Strategy-Spec boundary

A concept may become a draft Strategy Spec only through future WP-S2c-153
approval discipline.

The WP-S2c-151 lock remains in force:

- Strategy Spec is the future human-reviewable artifact/surface;
- Strategy DSL is constrained representation discipline;
- JSON-compatible canonical artifact family plus optional non-canonical
  Markdown companion is the locked format family;
- conceptual mandatory groups are locked only at group level;
- non-executable declarative posture is locked.

Concept ingestion must not create Strategy Spec artifacts or decide exact
schema fields.

## 12. Human review relationship

Human review is required before a concept can become approved-for-spec-authoring
or a similar future status.

This package does not lock final status names.

Human review may reject, defer, request clarification, or allow draft Strategy
Spec authoring.

Human concept review is not strategy approval, candidate approval, EXP
authority, sweep authority, ranking authority, paper/live authority, or runtime
authority.

## 13. Safety and non-executability requirements

Concepts and future concept records must be non-executable.

They must not embed arbitrary Python, shell, SQL, network calls, file writes,
dynamic imports, broker/exchange/order calls, runtime contact, or
protected-path contact.

They must not automatically satisfy D2-006, D2-007, REC-5, Phase 9 / D2-011,
Scope 6, or human gates.

They must not create direct Strategy Spec execution or adapter mapping.

## 14. Relationship to existing artifacts

Concept records are future upstream surfaces and must not replace candidate
registry, EXP / REP, trial log, OL, REC, DEC, query views, or decision records.

Candidate registry remains candidate status and evidence-link truth.

EXP / REP, trial-log, OL, REC, and DEC remain the canonical evidence and
decision chain.

Data catalog and timeframe status remain source of truth for available inputs
and timeframe posture.

This package creates no artifact bridge.

## 15. Concept-record non-decisions

This package does not choose storage path.

It does not choose exact file format.

It does not choose schema fields.

It does not create validator design.

It does not create examples or fixtures.

It does not create a concept status enum.

It does not decide revision or supersession mechanics.

It does not decide concept-to-spec approval implementation.

It does not decide mapping to Strategy Spec artifacts.

It does not decide artifact IDs.

## 16. What WP-S2c-153 must answer

WP-S2c-153 should define the substantive concept-to-spec authoring and approval
discipline, including:

- minimum information needed before a concept can be considered reviewable;
- human-review gates before Strategy Spec drafting;
- draft Strategy Spec authoring boundary;
- concept acceptance, rejection, or defer posture;
- how unsupported claims and missing data block progression;
- how concept provenance flows into Strategy Spec provenance;
- how future concept records link to future Strategy Specs;
- what remains deferred to storage/schema packages;
- stop conditions before any concept/spec artifact creation.

## 17. Later concept/spec tranche posture

The expected later concept/spec tranche posture is:

- WP-S2c-152: concept ingestion design opening;
- WP-S2c-153: concept-to-spec authoring and approval discipline;
- WP-S2c-154 through WP-S2c-158: variant generation, sweep orchestration,
  storage design, consolidation, and storage locking.

No concept schema, Strategy Spec schema, validator, parser/compiler, code,
fixture, or artifact instance should be created before later explicit
authorization.

If WP-S2c-153 determines concept ingestion requires a separate schema/storage
lock, it must report that as a later decision, not implement it.

## 18. Protected boundaries

This opening explicitly preserves:

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

## 19. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation should confirm exact changed-file scope, integrity views and
validators per doc-narrow convention, and no implementation or authority
creation.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 20. Stop conditions

Stop if any content creates a concept schema, Strategy Spec schema, validator,
parser/compiler, fixture, artifact instance, or implementation.

Stop if any content creates or ingests a real strategy idea as a committed
artifact.

Stop if any content modifies the WP-S2c-151 Strategy Spec / Strategy DSL lock.

Stop if any content permits executable code, runtime contact,
broker/exchange/order contact, network contact, file-writing commands, or
protected-path contact.

Stop if any content treats concept review as candidate, Strategy Spec, EXP,
sweep, ranking, paper/live, promotion, or runtime approval.

Stop if any content weakens pre-registration, D2-006/D2-007, REC-5, Phase 9 /
D2-011, Scope 6, or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 21. Non-authority boundary

This design opening creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority,
ranking/scoring authority, promotion authority, transition authority,
readiness authority, or human-gate execution authority.

It is planning structure only.

## 22. Next-package posture

After merge, the default next sequential package is WP-S2c-153 concept-to-spec
authoring and approval discipline, unless Main/Karl directs a different
authorized lab package.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler packages.
