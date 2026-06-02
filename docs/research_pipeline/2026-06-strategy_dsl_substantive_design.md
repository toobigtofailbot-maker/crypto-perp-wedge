# Strategy DSL Substantive Design

## 1. Scope

WP-S2c-149 / WP-12fv is a Tier 1 documentation-only package.

It creates the substantive Strategy DSL design for the Strategy Research Lab.
It creates no DSL schema, validator, parser/compiler, implementation, artifact
instance, fixture, query view, code, test, strategy execution, approval
authority, ranking authority, readiness authority, transition authority,
paper/live authority, runtime authority, or human-gate execution authority.

All design choices in this document are proposed or narrowed for WP-S2c-150
and WP-S2c-151 review. They are not implementation locks, schema locks, field
contracts, storage decisions, or execution authority.

## 2. Authorization and repo-truth basis

WP-S2c-148 opened the Strategy DSL design track and handed off WP-S2c-149 as
the next sequential lab package.

WP-S2c-147 defines the Strategy Research Lab target operating model. That model
requires a locked DSL or strategy-spec shape before lab implementation can be
requested.

Current repo truth records Track 3 as paused after WP-S2c-139. WP-S2c-140
onward remains deferred, not rescinded.

Future DSL implementation remains unauthorized until later explicit locking and
implementation authorization. This document does not authorize implementation,
schema work, validator work, query-layer work, artifact creation, or runtime
contact.

## 3. Design goal

The future DSL/spec should turn human strategy ideas into structured,
reviewable, non-executable specs.

It should support later variant population design, pre-registration, sweep
planning, anti-overfit controls, and provenance.

It should preserve separation between ideas, specs, variants, evidence, and
decisions. An idea is not a concept. A concept is not a spec. A spec is not a
candidate. A variant population is not evidence. Evidence and decisions remain
separate committed surfaces.

## 4. Recommended design direction

The recommended direction is a declarative Strategy Spec surface, not an
executable DSL.

This document prefers the phrase `Strategy Spec` for the future
human-reviewable artifact. The term `DSL` should be reserved for the constrained
representation discipline: explicit structure, limited clause vocabulary,
schema-validatable shape after later locking, and no executable payload.

The design should bias toward explicit fields and enumerated or structured
clauses rather than arbitrary expression language. A future executor, if later
authorized, would interpret a locked spec only through a separate offline
research adapter. It would not make the spec itself executable and would not
contact runtime or protected paths.

This recommendation is non-locking until the future Karl-gated WP-S2c-151
decision.

## 5. Format-family recommendation

The preferred format family is a JSON-compatible canonical artifact with an
optional Markdown narrative companion.

The JSON-compatible family is recommended because it is repo-compatible,
diff-friendly, deterministic, hashable, schema-validatable after later schema
authorization, and consistent with the existing artifact grammar direction for
registry-adjacent research surfaces. A companion Markdown narrative, if later
approved, can carry rationale and review notes without making prose the
canonical spec.

Raw executable code is rejected because it would collapse the spec into an
execution surface and create ambiguity around Python, shell, SQL, imports,
network access, broker calls, file writes, and protected-path contact.

Pure prose is insufficient because it is too ambiguous for variant population
boundaries, pre-registration, parameter limits, invalid-combination rules,
provenance checks, and later validation.

This package creates no instance, schema, storage path, or concrete field
contract.

## 6. Minimum valid spec structure

A future valid Strategy Spec should contain conceptual field families for:

- identity, version, and status;
- source and provenance;
- market universe;
- timeframe and data assumptions;
- signal logic;
- entry logic;
- exit logic;
- risk controls;
- parameter defaults and allowed ranges;
- constraints and invalid combinations;
- exclusions and unsupported interpretations;
- cost, slippage, and funding assumptions;
- trial-budget assumptions;
- review status and human approvals;
- links to concept records, variant populations, and future evidence surfaces.

These are field families, not exact field names. They do not create a schema,
validator contract, storage path, or implementation API.

## 7. Mandatory field groups

Any future valid Strategy Spec should require enough structure for human review
and future validation.

Mandatory conceptual groups should include:

- identity, version, and non-execution posture;
- provenance and source lineage;
- market, data, and timeframe assumptions;
- signal, entry, exit, and risk logic;
- parameter bounds or an explicit no-parameter declaration;
- cost, slippage, and funding assumptions when relevant to the strategy;
- constraints, invalid combinations, and exclusion rules;
- review status and required human approval posture;
- links to upstream concept context and downstream variant-planning context
  when those surfaces later exist.

Mandatory groups must make the spec inspectable before variant planning. They
must not create candidate registration, experiment authority, sweep authority,
ranking authority, paper/live authority, runtime authority, or human-gate
execution authority.

## 8. Optional field groups

Optional conceptual groups may include:

- alternate timeframe notes;
- alternate market notes;
- explanatory narrative;
- source-paper or article excerpt summaries;
- deeper economic rationale;
- diagnostic hints for later offline research;
- known failure modes;
- future evidence-link placeholders;
- reviewer notes;
- supersession notes after later revision semantics are designed.

Optional groups must remain non-authoritative. They must not create execution
authority, data-catalog changes, timeframe-status changes, candidate
registration, experiment plans, sweeps, rankings, recommendations, readiness
claims, promotion claims, or runtime contact.

## 9. Non-executable logic representation

Strategy logic should be represented as declarative clauses, condition
families, and a later locked operator vocabulary, not arbitrary code.

The design should support structured statements such as condition groups,
comparisons, time-window references, data-stream references, holding-period
constraints, and risk-control clauses. No operator vocabulary is locked here.

Future designs must prohibit arbitrary Python, shell, SQL, network calls, file
writes, dynamic imports, broker calls, exchange calls, order calls, runtime
contact, and protected-path contact. A spec must not contain payloads that can
execute, fetch, mutate, place orders, alter state, or reach outside the
approved research artifact boundary.

Any future operator vocabulary must be separately designed, reviewed, and
locked before validators or adapters can rely on it.

## 10. Provenance model

A future Strategy Spec should require provenance concepts for:

- source type;
- source identifier or citation;
- user prompt lineage when applicable;
- authoring agent or human author;
- reviewer identity or review role;
- version and revision history;
- hash or content fingerprint concept;
- data assumptions and data-catalog references.

This document does not lock a hash algorithm, schema field, storage path, or
revision implementation.

Provenance must support audit from idea to concept, from concept to spec, from
spec to variant population, and from variant population to future evidence if a
later bridge is authorized.

## 11. Data, timeframe, and input representation

Future specs must reference existing data-catalog and timeframe-status surfaces
without modifying them.

Specs must distinguish required inputs, optional inputs, and unavailable
inputs. They must record when an idea requires data not currently authorized.
They must not silently expand the data catalog, timeframe status, locked
timeframe set, taxonomy, strategy family list, or information-input posture.

When a spec depends on unavailable or unauthorized data, the spec should remain
blocked, draft, rejected, or otherwise not approved for variant planning until
a later package resolves the data authorization question.

## 12. Parameter-bound representation

Future specs must distinguish:

- fixed defaults;
- tunable parameters;
- allowed ranges;
- disallowed ranges;
- economic rationale for bounds;
- units and domains;
- expected sensitivity.

The spec should not enumerate a full variant population. Unlimited or
open-ended parameter spaces are forbidden because they weaken pre-registration
and multiple-testing discipline.

Variant enumeration belongs to later variant-population packages. A spec should
define the bounded design envelope; a future variant population should define
the concrete tested universe.

## 13. Invalid-combination and exclusion-rule representation

Future specs must support explicit invalid combinations and exclusions.

Examples include:

- data unavailable;
- timeframe unsupported;
- parameter combinations economically incoherent;
- strategy family outside authorized taxonomy;
- assumptions requiring Tier 4 or protected-path contact;
- interpretations that would require runtime, paper/live, exchange, broker, or
  order behavior;
- combinations that would exceed the intended trial budget.

Exclusions are part of anti-overfit discipline. They must survive after
results and must not be erased because a later result looked better or worse
than expected.

## 14. Human-review status model

Proposed status concepts may include draft, review requested, approved for
variant planning, rejected, superseded, and locked only after future locking.

These are design concepts, not schema enums.

Approval means clear enough for variant planning only. It does not create
candidate registration, EXP authority, sweep authority, ranking authority,
recommendation authority, paper/live authority, runtime authority, promotion
authority, readiness authority, transition authority, or human-gate execution
authority.

Novel strategy-family introduction remains human-gated.

## 15. Links to concept records and variant populations

Future specs should link backward to concept records and forward to variant
population manifests.

Until those surfaces are designed, this document defines relationship
requirements only. A spec is not a concept and not a variant population.

Concept records should preserve idea intake, source claim, economic mechanism,
assumptions, and open questions. Strategy Specs should formalize reviewed
strategy logic and bounded assumptions. Variant population manifests should
pre-register the concrete bounded variants that may later be executed after
authorization.

Variant population approval and pre-registration remain separate.

## 16. Relationship to existing evidence artifacts

The Strategy Spec is upstream of the existing evidence chain.

It must not replace the candidate registry, EXP/REP artifacts, trial log,
outcome ledgers, reconciliations, decision records, query views, or any
existing decision surface.

Future designs must decide whether specs link to candidates before or after
variant approval. No mapping is locked here.

Existing evidence artifacts remain the source of truth for results. A spec can
inform future research planning only after later authorization; it cannot
become evidence by existing in the repo.

## 17. Validation approach for later packages

After the DSL/spec shape is locked, later packages may design validation layers
for:

- syntax validation;
- schema validation after a schema exists;
- non-executable payload checks;
- data and timeframe reference checks;
- parameter-bound completeness checks;
- invalid-combination and exclusion-rule presence checks;
- provenance completeness checks;
- human-review status checks;
- no protected-path or runtime reference checks.

This document creates no validators. Validators must be designed only after DSL
lock and only inside an explicit implementation or schema package.

## 18. Implementation readiness blockers

The following blockers must be resolved before implementation:

- WP-S2c-150 consolidation;
- WP-S2c-151 Karl-gated DSL locking decision;
- decision on format family;
- decision on mandatory and optional field groups;
- decision on operator and logic representation;
- decision on data and timeframe reference rules;
- decision on parameter-bound semantics;
- decision on human-review status semantics;
- decision on future schema, validator, and query-view plan;
- protected-boundary review;
- explicit implementation authorization.

Until these are resolved, no Strategy Spec schema, parser, validator, artifact
instance, tool, query view, or implementation should be drafted.

## 19. Rejected alternatives

Pure prose only is rejected because it cannot reliably support validation,
variant-boundary review, provenance checks, invalid-combination retention,
trial budgeting, or reproducible handoff.

Raw executable code is rejected because it would create an execution surface
and invite imports, file writes, network calls, broker calls, runtime contact,
and protected-path coupling.

An arbitrary expression language is rejected because it would become a hidden
programming language before the project has locked safety, operator,
validation, and parser boundaries.

Direct `SignalProvider` or runtime mapping is rejected because the spec is a
research-planning surface, not a paper/live or runtime integration surface.

Immediate JSON schema creation is rejected because WP-S2c-149 is a
substantive design package, not a locking or implementation package.

Using `research/candidate_registry.jsonl` as DSL/spec storage is rejected
because the registry tracks candidate status and evidence links. Reusing it for
spec logic would duplicate source-of-truth responsibilities and blur candidates
with upstream specs.

Creating DSL artifacts before concept/spec approval design exists is rejected
because the lab still needs explicit concept ingestion, spec approval, variant
population, and storage decisions.

## 20. Unresolved questions for WP-S2c-150

WP-S2c-150 should consolidate unresolved questions and tradeoffs, including:

- exact format-family lock;
- whether canonical should be JSON or structured Markdown;
- how much narrative belongs in the spec versus a companion doc;
- how strict the operator vocabulary should be;
- how to represent nested conditions without executable code;
- how to represent data-catalog references before data-catalog automation
  exists;
- how to represent unavailable data;
- how to link to concept records that do not yet exist;
- how to handle spec revisions and supersession;
- what must wait for concept ingestion design in WP-S2c-152 and WP-S2c-153;
- what must wait for variant generation and storage design in WP-S2c-154
  through WP-S2c-158.

## 21. Protected boundaries

This design preserves:

- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS, reconciliation, kill-switch, and safe-mode boundaries;
- SignalProvider Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data/` protected paths;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred and A/D/E rejected status;
- Track 3 paused status;
- WP-S2c-140 deferred status;
- permanent human gates.

No Strategy Spec or DSL package may weaken these boundaries without explicit
later authorization.

## 22. Stop conditions

Stop if any content:

- creates a schema, validator, parser, compiler, fixture, artifact instance, or
  implementation;
- locks field names as an implementation contract;
- allows executable code or runtime/protected-path contact;
- treats spec approval as candidate, EXP, sweep, paper/live, promotion, or
  runtime approval;
- weakens pre-registration, D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6,
  or human gates;
- reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
  monitoring/dashboard, A2C-003, C/F, or A/D/E;
- fails validation.

## 23. Non-authority boundary

This substantive design creates no strategy authority, recommendation
authority, approval authority, runtime authority, paper/live authority,
ranking/scoring authority, promotion authority, transition authority, readiness
authority, or human-gate execution authority.

It is design structure only.

## 24. Next-package posture

After merge, the default next sequential package is WP-S2c-150 Strategy DSL
consolidation and unresolved-questions design.

Do not draft WP-S2c-151 locking until WP-S2c-150 is merged and Karl-gate
preconditions are satisfied.

Do not draft implementation packages. Do not draft Track 3 continuation
packages.
