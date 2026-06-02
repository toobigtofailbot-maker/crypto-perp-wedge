# Strategy DSL Consolidation And Unresolved Questions

## 1. Scope

WP-S2c-150 / WP-12fw is a Tier 1 documentation-only consolidation and
decision-prep package.

It consolidates the Strategy DSL / Strategy Spec design opened in WP-S2c-148
and substantively narrowed in WP-S2c-149. It prepares the Karl-gated
WP-S2c-151 locking decision.

This package creates no schema, validator, parser, compiler, implementation,
artifact instance, fixture, query view, code, test, Strategy Spec artifact,
approval authority, ranking authority, readiness authority, transition
authority, paper/live authority, runtime authority, or human-gate execution
authority.

This package does not lock the DSL/spec as final. WP-S2c-151 is the
Karl-gated locking decision.

## 2. Authorization and repo-truth basis

WP-S2c-148 opened the Strategy DSL design track under the Strategy Research
Lab tranche.

WP-S2c-149 produced substantive non-locking Strategy DSL / Strategy Spec design
and handed off WP-S2c-150 as the consolidation and unresolved-questions
package.

WP-S2c-147 defines the Strategy Research Lab target operating model and
requires a locked DSL/spec shape before lab implementation can be requested.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future DSL implementation remains unauthorized until explicit DSL/spec locking
and later implementation authorization.

## 3. Consolidated design posture

The preferred design remains a declarative `Strategy Spec` surface, not an
executable DSL.

`DSL` should mean constrained representation discipline: explicit structure,
limited representation choices, non-executable clauses, provenance discipline,
and later schema-validatable form after separate authorization.

The future Strategy Spec should be structured, reviewable, non-executable,
diff-friendly, hashable, provenance-preserving, and later
schema-validatable.

Strategy Spec sits between concept records and variant population manifests. A
Strategy Spec is not a candidate, not evidence, not approval, and not execution
authority.

## 4. Decision packet for WP-S2c-151

Proposed lock item: lock the high-level Strategy Spec shape and representation
discipline needed before later concept/spec approval and variant-storage design
can proceed.

Recommended option: lock `Strategy Spec` as the future human-reviewable
artifact/surface and `Strategy DSL` as the constrained representation
discipline; lock a JSON-compatible canonical format family plus optional
Markdown narrative companion; lock conceptual mandatory field groups and
non-executable declarative posture; defer exact fields, storage paths, schema,
validators, examples, parser/compiler, and implementation.

Rejected alternatives: pure prose only, raw executable code, arbitrary
expression language, immediate schema creation before lock, direct runtime or
`SignalProvider` mapping, and candidate registry as spec storage.

Dependencies: WP-S2c-147 target operating model, WP-S2c-148 design opening,
WP-S2c-149 substantive design, locked D2-006/D2-007/REC-5/Phase 9/D2-011/
Scope 6 discipline, and permanent human gates.

Deferrals: concept ingestion and spec approval mechanics to WP-S2c-152/153;
variant generation and storage mechanics to WP-S2c-154/158; anti-overfit and
ranking surfaces to WP-S2c-159/160; implementation roadmap and authorization
to WP-S2c-163/164 or later explicit authority.

Risks: locking too much could create premature schema or implementation
pressure; locking too little could leave later packages without a stable design
boundary.

Stop conditions: any WP-S2c-151 draft that creates implementation authority,
schema, validator, parser/compiler, artifact instance, executable logic,
paper/live authority, ranking/recommendation authority, or protected-path
contact must stop.

## 5. Format-family consolidation

Recommended WP-S2c-151 lock option: JSON-compatible canonical artifact plus
optional Markdown narrative companion.

The JSON-compatible canonical surface should hold structured strategy-spec
content after later schema authorization. It should be deterministic,
diff-friendly, hashable, provenance-preserving, and compatible with later
validation.

The optional Markdown companion, if allowed, should hold rationale, review
narrative, and explanatory notes. It must not supersede canonical structured
content.

Rejected alternatives:

- pure prose only;
- raw executable code;
- arbitrary expression language;
- immediate schema creation before lock;
- candidate registry as spec storage.

Open decision for WP-S2c-151: exact serialization and companion-document
convention.

## 6. Strategy Spec versus DSL terminology

Recommended WP-S2c-151 terminology:

- `Strategy Spec`: the future human-reviewable artifact/surface.
- `Strategy DSL`: the constrained representation discipline and design track.

This reduces execution-authority confusion by avoiding a framing where "DSL"
sounds like executable code. The future surface should describe strategy
intent and bounded assumptions; it should not run strategy logic.

No artifact path, artifact name, schema name, or storage convention is locked
by this package.

## 7. Field-family consolidation

WP-S2c-149's conceptual field families consolidate into these clusters:

- identity/status/non-execution;
- source/provenance/revision;
- market/universe/timeframe/data;
- signal/entry/exit/risk logic;
- parameters/bounds/sensitivity;
- costs/slippage/funding;
- constraints/invalid combinations/exclusions;
- review/approval posture;
- concept/variant/evidence links.

These clusters are candidate lock content for WP-S2c-151. They are not exact
field names, schema fields, validator contracts, storage paths, or
implementation APIs.

## 8. Mandatory versus optional groups

Recommended mandatory conceptual groups:

- identity/status/non-execution posture;
- provenance/source;
- market/data/timeframe assumptions;
- signal/entry/exit/risk logic;
- parameter bounds or no-parameter declaration;
- constraints/invalid combinations/exclusions;
- review status/human approval posture.

Recommended optional conceptual groups:

- explanatory narrative;
- alternate markets/timeframes;
- economic rationale detail;
- source excerpt summary;
- known failure modes;
- diagnostic hints;
- future evidence placeholders;
- reviewer/supersession notes.

Exact fields remain later schema work after lock.

## 9. Non-executable logic consolidation

The future Strategy Spec should use declarative clauses with a later locked
operator vocabulary.

It must not permit arbitrary code, implicit execution, file/network contact,
runtime contact, broker/exchange/order contact, or protected-path contact.

Future adapters may interpret locked specs only under later offline-research
implementation authorization. A spec's existence must not make the spec
executable.

## 10. Operator-vocabulary decision options

Option A: lock a minimal operator vocabulary for simple comparisons,
thresholds, logical AND/OR, and time-window references.

Option B: lock a moderate operator vocabulary that adds common rolling-window
or statistical transforms while remaining declarative.

Option C: defer exact operator vocabulary and lock only the principle of
non-executable declarative clauses.

Recommendation for Karl: Option C. It preserves non-executability and
representation discipline without prematurely designing schema/operator
semantics before concept/spec approval and variant-storage design.

Tradeoff: Option A is safer than Option B but may still be too early. Option B
risks premature implementation. Option C is narrowest for WP-S2c-151, with
operator details deferred to later schema or implementation-design packages.

## 11. Nested-condition representation options

Option A: flat condition groups only.

Option B: bounded nested groups with a depth cap and no arbitrary expressions.

Option C: defer exact nesting shape to later schema design.

Recommendation for Karl: Option C. WP-S2c-151 can lock non-executable
declarative posture while leaving exact nesting mechanics for later schema
design. If Karl wants more specificity, Option B is safer than arbitrary
expressions because it can preserve boundedness, but it should still avoid
syntax creation in the locking decision.

This package creates no syntax.

## 12. Provenance and revision posture

Provenance should be a mandatory conceptual cluster.

It should include source type, source identifier or citation, user prompt
lineage where applicable, author/reviewer role, version/revision concept,
content fingerprint concept, and data assumptions/catalog references.

Revisions and supersession should be explicit and auditable. This package does
not lock a hash algorithm, revision schema, exact field, or file path.

## 13. Data, timeframe, and unavailable-input posture

Future specs must reference existing `docs/data_catalog.md` and
`research/timeframe_status.md` surfaces without modifying them.

Specs must distinguish required, optional, unavailable, and unauthorized
inputs. A spec depending on unavailable or unauthorized input cannot be
approved for variant planning until data authorization is resolved.

Specs must not silently expand taxonomy, data, locked timeframe, or
information-input posture.

## 14. Parameter-bound and variant-boundary posture

Specs define the bounded design envelope. Variant population manifests define
the tested universe later.

Unlimited or open-ended parameter spaces are rejected.

Parameter bounds should require economic rationale, units/domains, disallowed
ranges, and expected sensitivity. Full enumeration waits for WP-S2c-154/158.

## 15. Invalid-combination and exclusion posture

Invalid combinations and exclusions are required anti-overfit surfaces.

They must survive after results. Exclusions must not be erased based on
observed outcomes.

They should cover unavailable data, unsupported timeframe, incoherent
parameter combinations, taxonomy conflicts, protected-path assumptions, and
trial-budget violations.

## 16. Human-review status posture

Candidate status concepts remain design-only.

Recommended later status concepts:

- draft;
- review_requested;
- approved_for_variant_planning;
- rejected;
- superseded.

`locked` should either be omitted from the initial status set or used only
after future locking semantics are defined.

Approval means clear enough for variant planning only. Approval does not create
candidate authority, EXP authority, sweep authority, ranking or recommendation
authority, paper/live authority, runtime authority, or human-gate execution
authority.

## 17. Concept-record and variant-population dependencies

Strategy Spec depends on future concept ingestion and spec approval design in
WP-S2c-152/153.

The forward link to variant population manifests depends on WP-S2c-154/158.

WP-S2c-151 can lock high-level shape while deferring exact relationship
mechanics.

This package creates no concept, spec, variant, sweep, or ranking artifacts.

## 18. Existing evidence artifact relationship

Specs are upstream of EXP, REP, trial-log, OL, REC, and DEC.

The existing evidence chain remains canonical.

Future mapping from specs and variant populations to EXPs and trial-log rows
remains unresolved. No mapping is locked in WP-S2c-150.

## 19. Validation and implementation-readiness posture

After WP-S2c-151 lock, later packages may design syntax validation, schema
validation, non-executable checks, data/timeframe reference checks,
parameter-bound checks, provenance checks, status checks, and
protected-reference checks.

This package creates no validators.

Implementation remains blocked until the WP-S2c-151 lock, concept/spec
approval design, variant generation/storage design, anti-overfit/ranking
artifact design, Scope 6 integration, protected-boundary review, and explicit
implementation authorization are complete.

## 20. Rejected and out-of-scope alternatives

Pure prose only remains rejected because it cannot reliably support validation,
variant-boundary review, provenance checks, invalid-combination retention,
trial budgeting, or reproducible handoff.

Raw executable code remains rejected because it would create an execution
surface and invite imports, file writes, network calls, broker calls, runtime
contact, and protected-path coupling.

Arbitrary expression language remains rejected because it would become a
hidden programming language before operator, validation, and parser boundaries
are locked.

Direct runtime or `SignalProvider` mapping remains rejected because Strategy
Spec is a research-planning surface, not a paper/live or runtime integration
surface.

Immediate schema creation remains rejected because the DSL/spec is not locked.

Candidate registry as spec storage remains rejected because the registry tracks
candidate status and evidence links. Using it for spec logic would blur
upstream specs with candidates and duplicate source-of-truth responsibilities.

Creating artifacts before concept/spec/variant/storage designs exist remains
rejected because it would create premature artifact authority.

Automatic paper/live/ranking/promotion authority remains rejected because it
would violate safety, source-of-truth clarity, overfit control, and
implementation sequencing.

## 21. Open questions classification

| Question | Recommended disposition | Reason | Destination |
|---|---|---|---|
| Exact canonical format | Lock format family, defer exact serialization | Stable direction is needed, but schema detail is premature | WP-S2c-151 lock |
| Narrative companion rule | Lock optional companion as non-canonical | Preserves rationale without weakening canonical structure | WP-S2c-151 lock |
| Operator vocabulary strictness | Defer exact vocabulary; lock non-executable posture | Avoids premature schema/operator design | WP-S2c-151 lock |
| Nested-condition depth | Defer exact shape | Needs schema design to avoid accidental syntax creation | WP-S2c-152/153 concept/spec approval |
| Unavailable data representation | Require distinction between required, optional, unavailable, and unauthorized | Blocks silent data/taxonomy expansion | WP-S2c-152/153 concept/spec approval |
| Concept-record links | Defer mechanics | Concept record surface is not designed yet | WP-S2c-152/153 concept/spec approval |
| Variant-manifest links | Defer mechanics | Variant storage and manifests are later tranche work | WP-S2c-154/158 variant/storage |
| Revision/supersession semantics | Lock auditable posture, defer exact mechanics | Needs storage and status design | WP-S2c-152/153 concept/spec approval |
| Schema/validator plan | Defer implementation plan until lock and approval design | Validators require locked shape | WP-S2c-163/164 implementation roadmap/authorization |
| Storage path | Defer | Storage should not be picked before concept/spec and variant surfaces are designed | WP-S2c-154/158 variant/storage |
| Evidence bridge to EXP/trial-log | Defer | Existing evidence chain remains canonical and bridge design is unresolved | WP-S2c-154/158 variant/storage |
| Artifact naming | Defer | Names depend on storage and schema decisions | WP-S2c-154/158 variant/storage |
| Human status set | Lock conceptual direction only | Status semantics depend on approval design | WP-S2c-152/153 concept/spec approval |
| Protected-reference checks | Defer validator mechanics; lock boundary principle | Checks require later schema/validator work | WP-S2c-163/164 implementation roadmap/authorization |
| Anti-overfit relationship | Defer specific ranking/filter mechanics | Population-level robustness is later lab-tranche work | WP-S2c-159/160 anti-overfit/ranking |
| Executable code in specs | Reject | Would create implementation/runtime authority | Out of scope / rejected |
| Candidate registry as spec storage | Reject | Blurs candidates with upstream specs | Out of scope / rejected |

## 22. Karl decision prompts for WP-S2c-151

1. Should WP-S2c-151 lock the future artifact as `Strategy Spec` with `DSL` as
   representation discipline?
2. Should WP-S2c-151 lock JSON-compatible canonical artifact plus optional
   Markdown narrative companion as the preferred format family?
3. Should WP-S2c-151 lock the conceptual mandatory field groups without exact
   schema fields?
4. Should WP-S2c-151 lock non-executable declarative clauses while deferring
   exact operator vocabulary?
5. Should WP-S2c-151 defer exact storage path, schema, validators, and examples
   until after concept/spec approval and variant/storage designs?
6. Should WP-S2c-151 explicitly forbid implementation until later lab-design
   consolidation and Karl implementation authorization?

Side must report these prompts after WP-S2c-150 merge and must not draft
WP-S2c-151 until Karl resolves the lock direction.

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
- permanent human gates.

## 24. Stop conditions

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

## 25. Non-authority boundary

This consolidation creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority, ranking/scoring
authority, promotion authority, transition authority, readiness authority, or
human-gate execution authority.

It is design consolidation and decision preparation only.

## 26. Next-package posture

After merge, do not automatically draft WP-S2c-151.

Side must report the WP-S2c-151 Karl decision prompts and get explicit lock
direction.

WP-S2c-151 remains Karl-gated.

Do not draft implementation packages. Do not draft Track 3 continuation
packages.
