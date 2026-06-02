# Variant Generation Design Opening

## 1. Scope

WP-S2c-154 / WP-12ga is a Tier 1 documentation-only design-opening package.

It opens the variant-generation design track for the Strategy Research Lab.

It creates only this opening document, updates `docs/research_pipeline/README.md`
with one additive index entry, and updates `docs/project_status.md`.

It creates no variant manifest, concept artifact, Strategy Spec artifact,
schema, validator, query view, parser, compiler, code, test, fixture, storage
path, implementation, sweep, backtest, strategy execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-153 defined concept-to-Strategy-Spec authoring and approval discipline
and handed off WP-S2c-154 as the next sequential lab package.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake through
advisory ranked output.

Track 3 remains paused. WP-S2c-140 onward remains deferred, not rescinded.

Future implementation remains unauthorized until later explicit locking and
implementation authorization.

## 3. Variant-generation problem statement

The lab's research-throughput goal requires converting approved Strategy Specs
into bounded populations of testable variants.

Unbounded parameter search is overfit-prone and incompatible with DSR and
multiple-testing discipline.

Single hand-picked variants are too narrow to characterize robustness.

The design problem is to define how future approved Strategy Specs could
produce pre-registered, bounded, auditable variant populations without creating
execution authority.

## 4. Design objective

Variant generation is the future derivation of a bounded variant population
from an approved Strategy Spec.

The design must preserve the distinction between parameter bounds in a
Strategy Spec and enumerated variants in a future variant population.

The design must prevent unlimited search, hidden hand-selection, and
post-result variant manipulation.

This package remains at design-opening level only.

## 5. Variant posture

A variant is a future testable parameterization or structural choice derived
from an approved Strategy Spec.

A variant is not a Strategy Spec.

A variant is not a concept.

A variant is not a candidate.

A variant is not evidence until tested through an authorized evidence flow.

A variant population is not approval, recommendation, ranking, paper/live
readiness, or runtime authority.

Variants may be rejected before sweep execution.

## 6. Relationship to lab lifecycle

Variant generation belongs after concept-to-spec approval and before sweep
orchestration.

It should feed future sweep planning only after pre-registration and
human-gated approval at initial maturity.

It should preserve source/spec lineage and anti-overfit accounting.

It must not bypass EXP / REP, trial-log, OL, REC, DEC, D2-006, D2-007, REC-5,
Phase 9 / D2-011, Scope 6, or human gates.

## 7. Approved Strategy Spec dependency

Future variant generation depends on an approved Strategy Spec.

Because no real Strategy Spec artifacts exist yet, this package must not create
variants or assume concrete fields.

Variant generation must obey the WP-S2c-151 lock:

- Strategy Spec is the future human-reviewable artifact/surface;
- Strategy DSL is constrained representation discipline;
- JSON-compatible canonical artifact family plus optional non-canonical
  Markdown companion is locked;
- conceptual mandatory groups are locked only at group level;
- non-executable declarative posture is locked.

If Strategy Spec storage or schema remains unresolved, WP-S2c-154 records
dependencies only.

## 8. Variant population versus single variant

A single variant is one concrete future parameterization or allowed structural
setting.

A variant population is the bounded, pre-registered universe of variants
derived from a Strategy Spec for a future sweep.

Future design must forbid selecting only the best-looking variant after
exploration.

Future design must preserve failed, excluded, and invalid variants for audit
where applicable.

## 9. Parameter-bound source posture

Parameter bounds originate from future approved Strategy Specs and
human-reviewed economic rationale.

Bounds must include units/domains, allowed ranges, disallowed ranges, and
sensitivity expectations when available.

Open-ended or unlimited ranges are forbidden.

Parameter hints from concepts cannot directly become variant ranges without
Strategy Spec approval.

## 10. Variant-boundary controls

Future variant populations should define these information families:

- allowed parameters;
- allowed ranges;
- discrete choices;
- invalid combinations;
- exclusion rules;
- maximum population size or trial budget;
- randomization or grid posture if later authorized;
- seed/reproducibility posture if later relevant;
- lineage to Strategy Spec;
- reason for each included parameter family.

This package does not create exact fields or schema.

## 11. Pre-registration relationship

Variant populations must be pre-registered before sweep execution.

Pre-registration must freeze the intended tested universe or clearly record any
allowed adaptive rule before results are known.

Post-result changes must not silently alter the registered variant universe.

Any future change after pre-registration requires explicit amendment semantics
in later design.

## 12. Anti-overfit relationship

Variant generation is an anti-overfit control surface.

It should make multiple-testing exposure visible.

It should support DSR-aware or later multiple-testing-aware evaluation.

It should prevent hidden hand-selection and survivorship bias.

It should preserve invalid or excluded variant rationale before results.

It should not optimize by trying everything until something works.

## 13. Sweep-orchestration boundary

WP-S2c-154 does not execute sweeps.

Future sweep orchestration is a later design topic.

Variant generation should hand a bounded population to future sweep planning,
not call batch runners directly.

No backtest, optimizer, execution runner, local-run registry write,
local-sweep result write, or query-output generation is authorized here.

## 14. Trial-budget and evidence-chain relationship

Future variant populations must carry or link to a trial-budget posture.

Trial-budget posture must be compatible with DSR and trial-log accounting.

Evidence will remain canonical in EXP / REP, trial-log, OL, REC, and DEC after
later authorized execution.

Variant generation does not itself create evidence.

The mapping from variant populations to EXP and trial-log remains deferred.

## 15. Relationship to existing parameter-sweep and batch-runner precedent

Existing parameter-sweep, batch-runner, local-run-registry, and
local-sweep-result docs may inform future design.

They are precedent, not active authority for this package.

This package does not reactivate or modify any automation implementation.

Future designs must decide how much of that precedent is reused without
bypassing Strategy Spec approval, pre-registration, or evidence discipline.

## 16. Storage and manifest non-decisions

This package does not choose storage path.

It does not choose exact file format.

It does not choose schema fields.

It does not create validator design.

It does not create examples or fixtures.

It does not create variant IDs.

It does not decide variant-manifest to EXP/trial-log mapping.

It does not decide sweep-run manifest semantics.

It does not decide implementation.

## 17. What WP-S2c-155 must answer

WP-S2c-155 should define sweep orchestration design opening or substantive
sweep-planning boundary.

It should answer:

- how a future pre-registered variant population would be handed to sweep
  planning;
- which surfaces are responsible for execution authorization;
- how trial budget, run manifests, and result collection should relate;
- how to avoid direct runtime/protected-path contact;
- how to preserve EXP / REP, trial-log, OL, REC, and DEC evidence chain;
- what remains deferred to storage/schema packages and WP-S2c-158 storage
  locking;
- stop conditions before any sweep execution or runner contact.

## 18. Later variant/storage tranche posture

The expected later tranche posture is:

- WP-S2c-154: variant generation design opening;
- WP-S2c-155: sweep orchestration design;
- WP-S2c-156: result population / storage design;
- WP-S2c-157: variant/storage consolidation;
- WP-S2c-158: Karl-gated storage / variant lock.

No variant manifest, schema, validator, parser/compiler, code, fixture,
artifact instance, sweep, backtest, or implementation should be created before
later explicit authorization.

WP-S2c-158 is expected to be a Karl-gated lock. Do not auto-draft it before
report-back and explicit lock direction if the preceding package requires
that.

## 19. Protected boundaries

This design explicitly preserves:

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

## 20. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation must confirm exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

Full pytest is not required unless repo-local convention or validation issues
require it.

## 21. Stop conditions

Stop if any content creates a variant manifest, concept artifact, Strategy Spec
artifact, schema, validator, parser/compiler, fixture, storage path, artifact
instance, or implementation.

Stop if any content creates or ingests a real strategy idea, concept, Strategy
Spec, parameter grid, or variant population as a committed artifact.

Stop if any content modifies or weakens the WP-S2c-151 Strategy Spec /
Strategy DSL lock.

Stop if any content permits executable code, runtime contact,
broker/exchange/order contact, network contact, file-writing commands, or
protected-path contact.

Stop if any content treats variant generation as candidate, Strategy Spec, EXP,
sweep, ranking, paper/live, promotion, recommendation, readiness, or runtime
approval.

Stop if any content weakens pre-registration, anti-overfit discipline, D2-006,
D2-007, REC-5, Phase 9 / D2-011, Scope 6, or human gates.

Stop if any content reactivates Track 3, WP-S2c-140, AUTO bridge, paper bridge,
monitoring/dashboard, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 22. Non-authority boundary

This design opening creates no strategy authority, recommendation authority,
approval authority, runtime authority, paper/live authority, ranking/scoring
authority, promotion authority, transition authority, readiness authority, or
human-gate execution authority.

It is planning structure only.

## 23. Next-package posture

After merge, the default next sequential package is WP-S2c-155 sweep
orchestration design, unless Main/Karl directs a different authorized lab
package.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema, validator, parser, or compiler packages.
