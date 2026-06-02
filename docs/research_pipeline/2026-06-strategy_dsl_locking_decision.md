# Strategy DSL Locking Decision

## 1. Scope

WP-S2c-151 / WP-12fx is a Tier 1 documentation-only Karl-gated locking
decision package.

It creates the Strategy DSL / Strategy Spec locking decision. It creates no
schema, validator, parser/compiler, implementation, artifact instance, fixture,
query view, code, test, Strategy Spec artifact, approval authority, ranking
authority, readiness authority, transition authority, paper/live authority,
runtime authority, or human-gate execution authority.

## 2. Authorization and repo-truth basis

WP-S2c-148 opened the Strategy DSL design track under the Strategy Research
Lab tranche.

WP-S2c-149 produced the substantive non-locking Strategy DSL / Strategy Spec
design.

WP-S2c-150 consolidated unresolved questions and produced the Karl decision
prompts for WP-S2c-151.

External Karl-gated lock direction approved all six main WP-S2c-151 prompts
and the additional lock details recorded here.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later lab-design
consolidation and explicit Karl implementation authorization.

## 3. Locked decisions

- Future artifact/surface is `Strategy Spec`.
- `Strategy DSL` means constrained representation discipline and design track.
- Preferred format family is JSON-compatible canonical artifact plus optional
  non-canonical Markdown narrative companion.
- Only conceptual mandatory field groups are locked; exact schema fields are
  not locked.
- Non-executable declarative clauses are locked.
- Exact operator vocabulary is deferred.
- Exact nested-condition mechanics are deferred.
- Human-review status posture is conceptual only; final enum values are not
  locked.
- `locked` status is not part of the initial status set until locking
  semantics are separately designed.
- `research/candidate_registry.jsonl` is rejected as Strategy Spec storage.
- Strategy Spec / variant-population mapping to EXP and trial-log is deferred.
- Implementation is forbidden until later lab-design consolidation and
  explicit Karl implementation authorization.

## 4. Decision 1 — Strategy Spec terminology

`Strategy Spec` is locked as the future human-reviewable artifact/surface.

No artifact path, file naming convention, schema name, or storage path is
locked here.

Strategy Spec is not a candidate, not evidence, not approval, and not
execution authority.

## 5. Decision 2 — DSL terminology

`Strategy DSL` is locked as constrained representation discipline and design
track.

DSL is not executable code, a parser/compiler, runtime interface, or trading
engine.

This terminology reduces execution-authority confusion by separating the
future human-reviewable Strategy Spec surface from any implication that the
representation itself executes.

## 6. Decision 3 — Format family

The preferred format family is a JSON-compatible canonical artifact plus an
optional Markdown narrative companion.

Canonical structured content is the future source of truth after later schema
authorization.

The Markdown companion, if later used, is explanatory and non-canonical. It
must not supersede canonical content.

Exact serialization, path, file naming, schema, examples, and companion
convention remain deferred.

## 7. Decision 4 — Conceptual mandatory field groups

Only these conceptual mandatory groups are locked:

- identity/status/non-execution posture;
- provenance/source;
- market/data/timeframe assumptions;
- signal/entry/exit/risk logic;
- parameter bounds or no-parameter declaration;
- constraints/invalid combinations/exclusions;
- review status/human approval posture.

Exact field names are not locked. Schema is not created. Validators are not
created. Implementation API is not created.

## 8. Decision 5 — Non-executable declarative posture

Strategy Spec logic is locked as declarative clauses only.

Future specs must forbid arbitrary Python, shell, SQL, network calls, file
writes, dynamic imports, broker/exchange/order calls, runtime contact,
protected-path contact, and implicit execution.

Future adapters may interpret locked specs only after separate offline-research
implementation authorization.

## 9. Decision 6 — Operator vocabulary deferral

Only non-executable declarative posture is locked.

Exact operator vocabulary is deferred. This decision does not choose a minimal
or moderate operator set.

Operator details are deferred to later schema/design work after concept/spec
approval and variant/storage designs.

## 10. Decision 7 — Nested-condition deferral

The bounded and non-executable nested-condition principle is locked.

Exact nesting mechanics and depth limits are deferred.

This decision creates no syntax and no examples.

## 11. Decision 8 — Human-review status posture

Human-review status posture is locked conceptually only.

Potential future status concepts may include:

- draft;
- review_requested;
- approved_for_variant_planning;
- rejected;
- superseded.

Final enum values are not locked.

`locked` is not included in the initial status set until locking semantics are
separately designed.

Approval means clear enough for variant planning only. Approval does not create
candidate, EXP, sweep, ranking, recommendation, paper/live, runtime,
promotion, readiness, transition, or human-gate execution authority.

## 12. Decision 9 — Candidate-registry storage rejection

`research/candidate_registry.jsonl` is explicitly rejected as Strategy Spec
storage.

The candidate registry tracks candidate status and evidence links. Strategy
Specs are upstream research-planning surfaces.

Using the registry as spec storage would blur candidates with specs and
duplicate source-of-truth responsibilities.

This package does not select a storage path.

## 13. Decision 10 — Evidence-bridge deferral

Strategy Spec / variant-population mapping to EXP and trial-log is deferred
until later variant/storage design.

Existing EXP/REP/trial-log/OL/REC/DEC remain canonical evidence and decision
chain surfaces.

Strategy Spec is upstream and cannot become evidence by existing.

## 14. Explicit deferrals

The following items are deferred:

- exact field names;
- schema;
- validators;
- query views;
- examples/fixtures;
- parser/compiler;
- storage path;
- artifact naming;
- exact serialization;
- companion-doc convention;
- exact operator vocabulary;
- exact nested-condition mechanics;
- final human-review status enum;
- concept/spec approval mechanics;
- variant generation/storage mechanics;
- evidence bridge to EXP/trial-log;
- implementation.

## 15. Implementation prohibition

No implementation is authorized until later lab-design consolidation and
explicit Karl implementation authorization.

Implementation is also blocked until concept/spec approval design, variant
generation/storage design, anti-overfit/ranking design, Scope 6 integration,
and protected-boundary review are complete.

WP-S2c-151 creates no implementation authority.

## 16. Relationship to existing research/evidence artifacts

The existing evidence chain remains source of truth.

Candidate registry is not spec storage.

EXP/REP/trial-log/OL/REC/DEC remain canonical for evidence, results, and
decisions.

Query views remain read-only consumption surfaces.

No registry/artifact/query change is created.

## 17. Relationship to later lab-tranche packages

Later package relationships are:

- WP-S2c-152/153: concept ingestion and spec approval discipline.
- WP-S2c-154/158: variant generation, sweep orchestration, storage, and
  storage locking.
- WP-S2c-159/160: anti-overfit/DSR population logic and advisory ranking
  artifact.
- WP-S2c-161/162: Scope 6 integration and lab agent roles.
- WP-S2c-163/164: lab design consolidation and implementation authorization
  decision.

WP-S2c-152 is the next sequential package after WP-S2c-151 unless Main/Karl
directs otherwise.

## 18. Protected boundaries

This decision explicitly preserves:

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
- permanent human gates.

## 19. Stop conditions

Stop if any content creates a schema, validator, parser, compiler, fixture,
artifact instance, or implementation.

Stop if any content locks exact field names as implementation contract.

Stop if any content allows executable code or runtime/protected-path contact.

Stop if any content treats spec approval as candidate, EXP, sweep, paper/live,
promotion, or runtime approval.

Stop if any content weakens pre-registration, D2-006/D2-007, REC-5,
Phase 9/D2-011, Scope 6, or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper
bridge, monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 20. Validation posture

Validation profile is CS12 T1-doc-major-decision.

Full pytest is required.

Exact changed-file scope is required.

All integrity views and validators are required.

## 21. Non-authority boundary

This locking decision creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority,
ranking/scoring authority, promotion authority, transition authority,
readiness authority, or human-gate execution authority.

It locks design direction only.

## 22. Next-package posture

After merge, the default next sequential package is WP-S2c-152 concept
ingestion design opening, unless Main/Karl directs otherwise.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler packages.
