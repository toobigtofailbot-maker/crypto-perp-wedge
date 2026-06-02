# Strategy DSL Design Opening

## 1. Scope

WP-S2c-148 / WP-12fu is a Tier 1 documentation-only design-opening package.

It opens the Strategy DSL design track for the Strategy Research Lab. It
creates only this document, updates `docs/research_pipeline/README.md` with one
additive index entry, and updates `docs/project_status.md`.

It creates no DSL, schema, validator, query view, parser, compiler, code, test,
artifact instance, strategy execution, strategy authority, ranking authority,
recommendation authority, approval authority, paper/live authority, runtime
authority, or human-gate execution authority.

## 2. Authorization and repo-truth basis

WP-S2c-147 / WP-12ft is merged. It defines the Strategy Research Lab target
operating model and identifies WP-S2c-148 as the default next sequential lab
package.

The target operating model requires a locked Strategy DSL or spec shape before
lab implementation can be requested. It also records that lab implementation,
artifact surfaces, query views, schemas, validators, ranking formulas, and
runtime paths remain unauthorized until later explicit locking and
implementation authorization.

Current repo truth records Track 3 as paused after WP-S2c-139. WP-S2c-140
onward remains deferred, not rescinded.

Future Strategy DSL implementation remains unauthorized until later packages
lock the DSL/spec shape and receive explicit implementation authority.

## 3. DSL problem statement

The Strategy Research Lab needs a structured way to convert user ideas,
research papers, articles, strategy notes, and observed online strategies into
precise, reviewable strategy specs.

Free prose alone is too ambiguous for variant generation, pre-registration,
sweep planning, and anti-overfit accounting.

Raw executable code is too dangerous and too coupled to runtime and protected
paths.

A future DSL or spec format should sit between prose concepts and executable
research code. It should make strategy intent reviewable without becoming an
execution surface.

## 4. Design objective

The future Strategy DSL should be a constrained, auditable, non-executable
strategy-spec representation.

It should express enough structure for human review, variant-boundary
definition, and later offline research orchestration if separately authorized.

It should not be a trading engine, runtime plug-in, code generator, broker
interface, order interface, promotion surface, readiness surface, or approval
authority.

It should preserve separation between ideas, specs, variants, evidence, and
decisions.

## 5. DSL posture

The DSL is a future spec surface. It is not created by this package.

The future format may be JSON, YAML, Markdown with structured blocks, or another
repo-compatible representation. This package does not decide the format.

A future DSL should be deterministic, diff-friendly, schema-validatable in
later packages, hashable, and provenance-preserving.

It must be non-executable by default. It should describe strategy logic, not run
strategy logic.

## 6. Relationship to lab lifecycle

The future DSL belongs between Stage 1 concept record and Stage 3 variant
population.

A concept may become a draft DSL/spec after human review. A spec may feed
variant population planning only after approval.

A DSL/spec is not a candidate, not evidence, and not approval.

A DSL/spec may later feed EXP, REP, trial-log, OL, REC, or DEC surfaces only
through separately authorized bridge design. Existing evidence and decision
surfaces remain canonical until repo truth explicitly changes that posture.

## 7. Candidate expression domains

The future DSL may need to express the following domains:

- identity and provenance;
- source idea, citation, or user prompt lineage;
- market universe and instrument assumptions;
- timeframe and data stream assumptions;
- signal logic;
- entry conditions;
- exit conditions;
- risk-control logic;
- position direction and exposure constraints;
- cost, slippage, and funding assumptions;
- parameter names, ranges, and defaults;
- constraints and invalid combinations;
- exclusion rules;
- failure and invalidation rules;
- trial-budget assumptions;
- evidence-link placeholders;
- human approval metadata.

These are candidate domains only. They are not a schema, not field names, not a
validator contract, and not a storage decision.

## 8. Field-family questions for WP-S2c-149

WP-S2c-149 must decide or narrow:

- Which minimum fields are mandatory for a valid strategy spec?
- Which fields are optional?
- Which fields are human-authored versus agent-proposed?
- How should provenance be represented?
- How should data availability be represented without changing the data
  catalog?
- How should entry, exit, and risk logic be represented without executable
  code?
- How should parameter bounds be represented for later variant population
  generation?
- How should invalid combinations and exclusion rules be represented?
- How should uncertainty and open questions survive into review?
- How should DSL specs link to future concept records and later variant
  manifests?

This opening does not answer those questions.

## 9. Parameter and variant-boundary questions

The future DSL must distinguish default parameters from parameter ranges.

It must distinguish a single strategy spec from a variant population.

It must not allow unlimited sweep spaces by default. Parameter ranges should
require economic rationale and explicit bounds.

Variant generation belongs to later packages. This package does not define
generation mechanics, parameter-grid enumeration, storage shape, or execution
path.

The future DSL must make overfit controls easier, not harder.

## 10. Safety and non-executability requirements

The future DSL must not allow embedded arbitrary Python, shell, SQL, network
calls, broker calls, runtime calls, file-writing commands, dynamic imports, or
other executable payloads.

It must not contain references that imply live, paper, runtime, exchange,
broker, or order execution.

It must not automatically contact orders, OMS, reconciliation, kill-switch,
safe-mode, overlay, `SignalProvider`, paper runtime, live runtime, or protected
paths.

It must not automatically satisfy D2-006, D2-007, REC-5, Phase 9 / D2-011,
Scope 6, or human gates.

Any future executable mapping must be a separate, explicitly authorized offline
research implementation.

## 11. Human review and approval relationship

A draft DSL/spec may be agent-authored after later authorization.

Approval remains human-gated at initial maturity.

Approval means "clear enough for variant planning." It does not mean "good
strategy."

Approval does not create candidate registration, EXP authority, sweep
authority, paper/live authority, promotion authority, ranking authority,
recommendation authority, or runtime authority.

Novel strategy-family introduction remains human-gated.

## 12. Relationship to existing artifacts

DSL/spec is upstream of EXP, REP, trial-log, OL, REC, and DEC. It is not a
replacement for them.

Future designs must decide whether a strategy spec links to candidate registry
before or after variant population approval.

The future DSL must not duplicate candidate registry truth. It must not create
parallel decision records.

It must preserve artifact lineage into future EXP, REP, and trial-log surfaces
if later authorized.

## 13. Parser / schema / validator non-decisions

This package does not pick JSON, YAML, Markdown, or another format.

It does not define concrete field names.

It does not create a schema, validator, parser, compiler, query view, fixture
instance, concept record, strategy spec, variant manifest, sweep artifact, or
ranking artifact.

Those remain WP-S2c-149, WP-S2c-150, and WP-S2c-151 design-lock questions.

## 14. Protected boundaries

This opening explicitly preserves:

- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS, reconciliation, kill-switch, and safe-mode boundaries;
- `SignalProvider` Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data/` protected paths;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred and A/D/E rejected status;
- Track 3 paused status;
- WP-S2c-140 deferred status;
- permanent human gates.

No future DSL package may weaken these boundaries without explicit later
authorization.

## 15. What WP-S2c-149 must answer

WP-S2c-149 should draft the substantive Strategy DSL design and answer:

- proposed format family;
- minimum valid spec structure;
- mandatory and optional field groups;
- non-executable logic representation;
- provenance model;
- data, timeframe, and input representation;
- parameter-bound representation;
- invalid-combination and exclusion-rule representation;
- human-review status model;
- links to concept records and variant populations;
- validation approach for later packages;
- implementation readiness blockers.

If WP-S2c-149 discovers that the DSL should not be a separate surface, it must
report that option instead of forcing a DSL.

## 16. Later DSL tranche posture

The expected later DSL tranche posture is:

- WP-S2c-149: substantive DSL design.
- WP-S2c-150: DSL design consolidation and unresolved questions.
- WP-S2c-151: Karl-gated DSL locking decision.

No schema, validator, parser, compiler, code implementation, fixture instance,
or query view may be created before locking.

## 17. Validation posture

Validation profile: CS12 T1-doc-narrow.

Validation should confirm exact changed-file scope, README index scope, project
status scope, integrity views, validators per doc-narrow convention, and no DSL
implementation or authority creation.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 18. Stop conditions

Stop if any content:

- creates a DSL schema or field lock;
- implies implementation;
- requires schema, code, test, validator, query-view, or tool changes;
- creates artifacts or artifact instances;
- allows executable code, runtime contact, broker/exchange/order contact, or
  protected-path contact;
- makes DSL approval equivalent to candidate, paper, live, promotion, or
  runtime approval;
- weakens pre-registration, D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6,
  or human gates;
- reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
  monitoring/dashboard, or A2C-003;
- fails validation.

## 19. Non-authority boundary

This design opening creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority, ranking/scoring
authority, promotion authority, or human-gate execution authority.

It is planning structure only.

## 20. Next-package posture

After merge, the default next sequential package is WP-S2c-149 Strategy DSL
substantive design unless Main directs a different authorized lab package.

Do not draft implementation packages. Do not draft Track 3 continuation
packages. Do not draft WP-S2c-151 locking until the preceding DSL design and
consolidation packages and Karl-gate preconditions are satisfied.
