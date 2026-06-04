# Strategy Spec Artifact Grammar Design

## 1. Scope

WP-S2c-177 / WP-12gx is a Tier 1 documentation-only design-opening package for the future Strategy Spec artifact grammar.

It creates this design document and updates `docs/project_status.md` only. It creates no schema, validator, query view, artifact instance, Strategy Spec example, Markdown companion example, parser/compiler, executable semantics, storage path lock, code, tests, tools, runner behavior, dashboard, agent, prompt, runtime behavior, paper/live behavior, protected-path change, approval authority, readiness authority, recommendation authority, ranking/scoring authority, transition authority, or human-gate execution.

## 2. Repo-truth and Main authorization basis

Repo truth is refreshed `main` after WP-S2c-176 / WP-12gw, merged by PR #353 at merge commit `f4e49170ec4855d96c41a0fe2899ca5f0bbe346d`.

Primary basis:

- WP-S2c-151 locks `Strategy Spec` as the future human-reviewable artifact/surface and `Strategy DSL` as constrained representation discipline and design track.
- WP-S2c-166 requires future Strategy Spec / DSL representation to remain typed, declarative, non-executable, side-effect-free, host-data-bounded, auditable, and separated from runtime, paper/live, broker/exchange/order behavior.
- WP-S2c-158 locks future variant population manifest as the required pre-registration surface before sweep execution and locks complete result-population preservation.
- WP-S2c-167 defines provenance, audit, lineage, and hash-pinning posture as evidence-trail concepts only.
- WP-S2c-172 through WP-S2c-176 completed the backtest-realism implementation tranche, making fee-side, exchange-constraint disclosure, funding notional, slippage/fill/size/liquidity, liquidation/maintenance margin/mark source, and bar-path assumptions explicit in the research backtester.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces.
- Permanent human gates, D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and protected runtime boundaries remain unchanged.

The active execution prompt records Main authorization for roadmap item 3 and direct WP-S2c-177 drafting. Current merged repo truth wins over memory, summaries, external research, or generic best practice.

## 3. Design objective

The objective is to define the intended future Strategy Spec artifact grammar shape at design level before schema introduction.

This document prepares schema-shape review for Main. It does not choose exact schema fields, final enum values, exact operator vocabulary, exact nested-condition mechanics, exact storage path, exact hash rules, validator implementation, query surfaces, parser/compiler behavior, artifact instances, or executable semantics.

## 4. Non-authority boundary

Strategy Spec is a future planning and human-review surface only.

Strategy Spec is not a candidate, not evidence, not approval, not a recommendation, not ranking authority, not readiness authority, not transition authority, not paper/live authority, not runtime authority, and not human-gate execution authority.

Strategy DSL is constrained representation discipline and design track only. It is not executable code, parser/compiler authority, a runtime interface, a broker/exchange/order interface, or a trading engine.

Candidate registry is rejected as Strategy Spec storage. EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces. Permanent human gates remain unchanged.

## 5. Relationship to WP-S2c-151 DSL lock

WP-S2c-151 governs this design.

The future artifact/surface name is `Strategy Spec`. The preferred future format family is JSON-compatible canonical artifact plus optional non-canonical Markdown narrative companion. Only conceptual mandatory field groups are locked by WP-S2c-151; exact schema fields remain deferred.

This package preserves the WP-S2c-151 locks:

- non-executable declarative clauses;
- exact operator vocabulary deferred;
- exact nested-condition mechanics deferred;
- conceptual human-review status posture only;
- no `locked` status in the initial status set until locking semantics are separately designed;
- no Strategy Spec storage in `research/candidate_registry.jsonl`;
- no Strategy Spec / variant-population mapping to EXP or trial-log yet.

## 6. Relationship to WP-S2c-166 expressiveness-readiness criteria

WP-S2c-166 requires future Strategy Spec / DSL expressiveness to be typed, declarative, non-executable, side-effect-free, host-data-bounded, auditable, and suitable for human review and bounded variant derivation only after later authorization.

This design preserves MVP-critical representation families as reviewable declarations: multi-signal entries, explicit exits, sizing and risk-parameter concepts, regime filters, multi-timeframe references, trend-following, mean reversion, breakouts, funding/carry concepts, basis/spread concepts, risk overlays, cooldowns, no-trade filters, and time/session filters.

This design rejects dangerous expressiveness: arbitrary Python, shell, SQL, user-defined functions, callbacks, recursion, loops, external calls, mutable global state, self-modifying rules, imperative order routing, broker/exchange/order directives, hidden mutation, and any expression that can execute gates or update readiness.

## 7. Relationship to WP-S2c-158 variant/pre-registration discipline

WP-S2c-158 locks the future variant population manifest as the required pre-registration surface before sweep execution.

Strategy Spec sits upstream of that surface. A future Strategy Spec may define strategy intent, assumptions, parameter declarations, and invalid combinations that a later variant manifest can freeze into a tested universe. The Strategy Spec itself is not the pre-registration manifest, not a sweep plan, not a run manifest, and not execution authorization.

Spec hash-pinning may later support pre-registration discipline by making the Strategy Spec snapshot used for variant planning immutable or amendment-audited. Hash-pinning does not approve a spec, execute a sweep, create evidence, or satisfy gates.

## 8. Strategy Spec artifact grammar principles

Future Strategy Spec grammar should be:

- structured enough for schema validation after later approval;
- human-reviewable before variant planning;
- explicit about assumptions and unresolved blockers;
- constrained to declared host data and declared timeframes;
- clear about parameter bounds and search-space exposure;
- explicit about invalid combinations and exclusions;
- lineage-aware and hash-pinning-ready;
- separated from evidence, decision, and runtime surfaces;
- non-executable by construction.

The grammar should expose review questions rather than hide them behind executable expressions or opaque scores.

## 9. Proposed future canonical artifact posture

The future canonical artifact should be JSON-compatible structured content after schema authorization. An optional Markdown narrative companion may explain the spec, but it must remain non-canonical and must not supersede the structured artifact.

This package does not lock a schema file, storage path, artifact ID format, serialization convention, Markdown companion convention, example, or fixture.

Possible future schema path options for Main review include a `research/schemas/` JSON Schema path or a Strategy Lab-specific schema path under `docs/research_pipeline/` if repo convention later prefers documentation-adjacent schema definitions. No option is selected here.

## 10. Proposed conceptual schema structure

A future schema should preserve these conceptual groups:

- identity / status / non-execution posture;
- provenance / source;
- instruments / market assumptions;
- timeframe / data assumptions;
- entry logic;
- exit logic;
- risk model;
- filters;
- free-parameter declarations with type, range or allowed values, units, default, role, and rationale;
- constraints / invalid combinations / exclusions;
- review status / human approval posture;
- lineage / hash-pinning / pre-registration support.

Exact top-level field names, required/optional splits, enum values, operator objects, nested-condition mechanics, reference formats, and hash fields remain subject to Main schema-shape review before WP-S2c-178.

## 11. Identity / status / non-execution posture group

Future schema design should reserve conceptual space for:

- spec identifier placeholder;
- schema version;
- title or short name;
- status;
- non-execution declaration;
- human-review posture;
- supersession or amendment posture where needed.

The non-execution declaration should state that the artifact is a human-reviewable planning surface only. It must not authorize candidate registration, EXP creation, sweep execution, paper/live behavior, runtime behavior, recommendation, ranking, readiness, transition, or gate satisfaction.

Final status enum values are not locked. Conceptual families may include draft, review_requested, approved_for_variant_planning, rejected, and superseded.

## 12. Provenance / source group

Future schema design should reserve conceptual space for:

- source idea or concept reference;
- author or preparer metadata posture;
- created and updated timestamp posture;
- source rationale or thesis;
- source constraints;
- review notes posture;
- unresolved source claims or missing-information notes.

Source provenance is audit context only. Unsupported performance claims remain claims until tested through authorized evidence flow.

## 13. Instruments / market assumptions group

Future schema design should reserve conceptual space for:

- symbol or instrument family;
- venue or market type where needed as declared assumption;
- long/short allowed posture;
- leverage assumption as review metadata only;
- exchange-constraint references or declarations where applicable;
- instrument-specific blockers or exclusions.

This group creates no broker/exchange/order authority. Leverage and exchange-constraint declarations are review visibility only and cannot modify D-0001, runtime risk, paper/live behavior, order routing, or config.

## 14. Timeframe / data assumptions group

Future schema design should reserve conceptual space for:

- primary timeframe;
- optional confirmation timeframe or timeframes;
- data streams referenced;
- host-data-bounded references only;
- OHLCV, funding, mark, index, and premium data assumptions where applicable;
- missing-data and gap-handling assumption posture;
- unavailable-data blockers.

The group must not authorize data fetching, arbitrary file reads, external calls, silent interpolation, or data-catalog changes. It should make D2-003A gap posture and host-data availability visible for review where applicable.

## 15. Entry logic group

Future schema design should reserve conceptual space for declarative entry condition groups, including:

- signal families;
- direction;
- required versus confirming conditions;
- parameter references;
- data and timeframe references;
- review notes or assumptions.

Entry logic must remain non-executable. It should describe strategy intent and required host-provided inputs without arbitrary code, callbacks, custom functions, loops, recursion, network calls, file operations, or runtime contact.

## 16. Exit logic group

Future schema design should reserve conceptual space for:

- exit condition groups;
- invalidation rules;
- maximum holding period posture;
- stop and profit-target concepts as declarative risk or exit assumptions;
- signal reversal concepts;
- path-dependency qualifiers.

Exit logic does not create path-execution semantics, stop/limit order behavior, order-routing authority, or intrabar sequencing authority.

## 17. Risk model group

Future schema design should reserve conceptual space for:

- sizing intent;
- exposure limits as review metadata;
- stop distance and target concepts;
- leverage assumption visibility;
- liquidation and maintenance-margin sensitivity references;
- cost, funding, slippage, and liquidity assumption links where relevant.

The risk model group is not runtime risk control. It cannot alter D-0001, safe mode, OMS, reconciliation, overlay behavior, paper/live behavior, or protected runtime paths.

## 18. Filters group

Future schema design should reserve conceptual space for:

- regime filters;
- no-trade filters;
- cooldown concepts;
- time or session filters;
- funding, carry, basis, spread, volatility, or trend/range filters where host-data-bounded;
- reviewability and search-space visibility.

Filters must not become hidden post-result rescue logic. They should expose whether a filter is part of the core thesis, a blocker, a qualifier, or a potential later variant axis.

## 19. Free-parameter declaration group

Future schema design should reserve conceptual space for each free parameter:

- name;
- type;
- units;
- range or allowed values;
- default;
- role and rationale;
- whether included in later variant generation;
- constraints or invalid combinations;
- no-parameter declaration where applicable.

MVP / D2-006-style review should limit free parameters to no more than 5 unless a later explicitly authorized exception exists. A future validator may enforce this count. This document creates no exception process.

## 20. Constraint / invalid-combination / exclusion group

Future schema design should reserve conceptual space for:

- invalid parameter combinations;
- unavailable data blockers;
- deferred pattern blockers;
- rejected assumptions;
- conditions that qualify or block downstream review;
- exclusions that prevent later variant planning unless resolved.

Constraints should protect against hidden search expansion, unsupported inputs, unsafe assumptions, and post-result mutation.

## 21. Review status / human approval posture group

Future schema design should reserve conceptual space for conceptual statuses and review notes.

Conceptual status families may include draft, review_requested, approved_for_variant_planning, rejected, and superseded. Final enum values are not locked.

Approval for variant planning means only that a human reviewer found the spec clear enough to support later variant-manifest planning. It is not candidate approval, EXP approval, sweep authority, ranking, recommendation, readiness, transition, paper/live approval, runtime approval, D2-006 satisfaction, Scope 6 satisfaction, or human-gate execution.

## 22. Lineage / hash-pinning / pre-registration support

Future schema design should reserve conceptual space for:

- canonical spec hash posture;
- immutable snapshot posture for downstream variant planning;
- mutation or amendment visibility;
- parent concept or source references;
- downstream variant manifest and result-population lineage references where later authorized;
- canonical evidence references only where later mapping is approved.

Hash-pinning supports pre-registration and mutation detection. It does not create approval, evidence, execution, or decision authority. Exact hash algorithm, fields, mismatch behavior, query behavior, and tooling remain deferred.

## 23. Operator vocabulary posture

Exact operator vocabulary remains deferred under WP-S2c-151.

Future schema shape may reserve space for bounded declarative condition operators, but WP-S2c-177 does not define a full vocabulary, choose operator names, define formulas, or create executable grammar.

Operator design must preserve typed, non-executable, side-effect-free, host-data-bounded representation discipline.

## 24. Nested-condition posture

Exact nested-condition mechanics remain deferred under WP-S2c-151.

The bounded non-executable nested-condition principle remains in scope. Future schema shape may reserve design space for condition groups, required/confirming groupings, and bounded nesting, but it must not create recursion, arbitrary loops, callbacks, custom functions, or executable evaluation semantics.

Future Main schema-shape review should decide whether nested condition structure is required for WP-S2c-178 or deferred to a later schema revision.

## 25. Host-data-boundedness and data dependency boundaries

Future Strategy Specs should reference only declared host-provided data surfaces.

Specs must not fetch data, read arbitrary files, call external services, mutate data, write artifacts, or depend on undeclared data. Unavailable or unauthorized data should block, defer, or qualify review.

Host-data references should identify the intended stream, timeframe, and assumption posture clearly enough for later validator and human review, without creating query-layer behavior or data-access behavior.

## 26. Backtest-realism assumption references

Future Strategy Specs should make relevant backtest-realism assumptions visible for review, including:

- fees and fee-side assumptions;
- exchange-constraint disclosures;
- funding notional assumptions;
- slippage model;
- fill mode;
- order size;
- liquidity capacity assumption;
- liquidation mode;
- maintenance margin assumption;
- mark price source;
- bar-path assumption.

These are declaration and readiness references only. Strategy Spec must not execute or enforce these assumptions, change `lib/backtest.py`, alter research results, call a runner, or contact runtime/paper/live/protected paths.

## 27. Free-parameter-count discipline

Future Strategy Spec grammar should preserve D2-006-style search discipline by making free-parameter count visible before variant planning.

The MVP posture is no more than 5 free parameters unless Main later explicitly authorizes an exception. Countable parameters should include any value that can be varied in later search or materially selected from a set of alternatives. Fixed assumptions and no-parameter declarations should remain distinguishable from free parameters.

This discipline supports anti-overfit review and does not itself approve a spec or variant population.

## 28. Future validator surface

A future validator may enforce, after exact schema approval:

- schema/content shape;
- required conceptual groups;
- free-parameter-count <=5 unless explicitly authorized later;
- parameter type/range/default presence;
- non-executable field posture;
- forbidden expression patterns;
- host-data-bounded references;
- approved status enum values;
- lineage/hash field presence once schema locks them;
- review-status and non-execution declaration presence.

The validator must not approve, recommend, rank, execute gates, trigger transitions, run backtests, create artifacts, update readiness, mutate evidence, or contact runtime/paper/live/protected paths.

## 29. Future schema introduction surface for WP-S2c-178

WP-S2c-178 is not auto-draftable from this document alone. Main must review the schema shape after WP-S2c-177 merges.

Schema-shape items for Main review before WP-S2c-178:

- canonical schema file path;
- schema documentation path, if any;
- top-level field groups;
- required versus optional groups;
- status enum posture;
- free-parameter representation;
- no-parameter declaration representation;
- condition/operator placeholder posture;
- nested-condition placeholder posture;
- hash/lineage posture;
- host-data reference posture;
- backtest-realism assumption reference posture;
- validator boundaries;
- explicit forbidden expressiveness;
- zero-instance posture.

No exact schema file path is selected here.

## 30. Relationship to downstream variant manifest / sweep grammar

Strategy Spec grammar should make future variant-manifest and sweep-plan design easier by exposing bounded parameter axes, invalid combinations, exclusions, data assumptions, timeframe assumptions, and hash-pinned spec identity.

The downstream variant manifest remains the required pre-registration surface before sweep execution under WP-S2c-158. Sweep plan and run-manifest grammar remain downstream and are not created here.

Strategy Spec cannot silently generate variants, execute sweeps, expand trial budget, mutate a tested universe, or create result populations.

## 31. Explicit forbidden expressiveness

Future Strategy Specs must forbid:

- arbitrary Python, shell, SQL, or other executable code;
- unrestricted custom functions;
- callbacks;
- recursion;
- loops;
- external network, file, or process calls;
- runtime side effects;
- mutable global state;
- self-modifying rules;
- hidden post-result mutation;
- imperative order-routing instructions;
- broker/exchange/order API directives;
- config or dependency changes;
- live, paper, runtime, OMS, reconciliation, risk, overlay, safe-mode, or kill-switch controls;
- gate execution, readiness updates, transition triggers, approval actions, ranking/scoring authority, or recommendation authority.

Any future schema or validator that cannot preserve these bans must stop and escalate.

## 32. Deferred items

Deferred items include:

- exact schema file path;
- exact storage path;
- exact artifact ID format;
- exact fields and field names;
- final status enum values;
- exact operator vocabulary;
- exact nested-condition mechanics and depth limits;
- examples and fixtures;
- Markdown companion convention;
- hash algorithm and mismatch behavior;
- validators;
- query views;
- parser/compiler behavior;
- host interpreter behavior;
- variant-manifest mapping;
- EXP / REP / trial-log mapping;
- amendment and supersession mechanics;
- dashboard, agent, runner, and implementation behavior.

Each deferred item requires later explicit package scope.

## 33. Stop / escalation conditions

Stop and escalate if future work would:

- create schema, validator, query view, artifact instance, Strategy Spec example, parser/compiler behavior, runner behavior, code, tests, tools, dashboard, agent, prompt, runtime contact, paper/live contact, or protected-path changes without explicit authorization;
- make Strategy Specs executable;
- define arbitrary code, callbacks, loops, recursion, external calls, or hidden mutation;
- turn Strategy Spec into candidate storage, evidence, approval, recommendation, ranking, readiness, transition, paper/live, runtime, or gate authority;
- use candidate registry as Strategy Spec storage;
- replace EXP / REP, trial-log, OL, REC, or DEC;
- weaken WP-S2c-151, WP-S2c-166, WP-S2c-158, D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, or permanent human gates;
- exceed the <=5 free-parameter MVP posture without Main-approved exception authority;
- conflict with current merged repo truth.

## 34. Validation posture

This package uses T1-doc-narrow validation unless current repo truth requires broader validation.

Validation proves exact changed-file scope, forbidden-path cleanliness, query/integrity health, registry/artifact/outcome/reconciliation validator health, and scoped research-pipeline consistency. It does not create implementation authority.

Full pytest is not required for this package class unless current repo truth, validation failure, local convention, or Codex judgment indicates it is needed.

## 35. Next-package posture

After merge, Side must report back to Main with the proposed schema shape for review.

WP-S2c-178 is not auto-draftable until Main completes schema-shape review. Any WP-S2c-178 package must start from refreshed `main`, preserve this non-executable / non-authority posture, and remain zero-instance unless Main explicitly authorizes otherwise.
