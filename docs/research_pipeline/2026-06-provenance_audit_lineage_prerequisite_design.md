# Provenance / Audit / Lineage Prerequisite Design

## 1. Scope

WP-S2c-167 / WP-12gn is a Tier 1 documentation-only prerequisite design package.

It defines provenance, audit, and lineage discipline for the future Strategy Research Lab chain from idea intake through human-review handoff.

This package creates only this document and updates `docs/project_status.md`.

It creates no implementation authorization and no authority to create schemas, validators, query views, artifacts, code, tests, tools, runners, sweeps, dashboards, agents, prompts, storage paths, runtime behavior, paper/live behavior, protected-path changes, recommendation authority, approval authority, readiness authority, transition authority, ranking/scoring authority, or human-gate execution.

## 2. Repo-Truth And Decision Basis

Repo truth for this design is refreshed `main` after WP-S2c-166 / WP-12gm.

Primary basis:

- WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to advisory ranked output.
- WP-S2c-151 locks Strategy Spec as the future human-reviewable surface and Strategy DSL as constrained, declarative, non-executable representation discipline.
- WP-S2c-153 defines concept-to-Strategy-Spec authoring and approval discipline.
- WP-S2c-158 locks future variant population manifests as pre-registration surfaces and locks complete result-population preservation.
- WP-S2c-159 through WP-S2c-162 preserve anti-overfit review, advisory ranking, Scope 6 / R2S, and agent roles as support-only.
- WP-S2c-164 defers implementation and requires prerequisite design before any lab implementation tranche.
- WP-S2c-165 defines validity-floor, backtest-realism, bounded-search, walk-forward-first, and DSR / PSR / MinTRL prerequisite posture.
- WP-S2c-166 defines Strategy Spec / DSL expressiveness-readiness prerequisites.
- EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision surfaces.
- D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and permanent human gates remain preserved.

Current merged repo truth wins over external research, memory, summaries, handoffs, or generic best practice.

## 3. Design Objective

The objective is to define what future lab artifacts and support outputs must preserve so the chain from source idea to human-review handoff remains auditable.

The design covers provenance, audit, and lineage as evidence trail only.

It does not define exact field names, schemas, IDs, validators, query views, storage paths, hash algorithms, runner mechanics, agent workflows, formulas, thresholds, split mechanics, artifact instances, or implementation sequence.

## 4. Non-Authority Boundary

Provenance is not authority.

Auditability does not approve candidates.

Lineage does not create recommendation, ranking authority, readiness, transition, promotion, demotion, policy action, paper/live authority, runtime authority, or gate execution.

Human gates remain human gates.

Advisory ranking remains human-review support only.

Scope 6 / R2S remains human-gated.

Implementation remains unauthorized.

## 5. Relationship To WP-S2c-164, WP-S2c-165, And WP-S2c-166

WP-S2c-164 deferred lab implementation and required prerequisite design before implementation can be reconsidered.

WP-S2c-165 requires visible validity-floor, backtest-realism, bounded-search, walk-forward, and DSR / PSR / MinTRL context. Provenance supports that posture by requiring future artifacts to carry enough source, assumption, search, result-population, and evidence references for later diagnostic review.

WP-S2c-166 requires Strategy Spec / DSL expressiveness to remain reviewable, declarative, and host-data-bounded. Provenance supports that posture by preserving source assumptions, Strategy Spec references, variant axes, and lineage anchors without making the Strategy Spec executable.

WP-S2c-168 is expected to address future agent orchestration readiness. This document supplies the audit prerequisite: any future agent action must be traceable, non-authoritative, and human-reviewable.

## 6. Provenance / Audit / Lineage Definition

Provenance is the recorded origin and derivation context for a lab item.

Audit is the ability to inspect whether the item followed the required chain, preserved references, and disclosed missing, stale, failed, invalid, excluded, aborted, filtered, data-unavailable, or superseded branches where repo-truth designs require preservation.

Lineage is the parent-child relationship among idea, concept, Strategy Spec, variant population, sweep or run planning, result population, anti-overfit review, advisory ranking, Scope 6 / R2S handoff, and later human decision records where authorized.

These are evidence-trail concepts only.

## 7. End-To-End Provenance Chain

The future provenance chain is:

```text
source idea / concept intake
-> concept-to-Strategy-Spec drafting and approval discipline
-> Strategy Spec
-> variant population manifest
-> sweep plan / run manifest
-> result population
-> anti-overfit / DSR review
-> advisory ranking
-> Scope 6 / R2S human-review packet
-> later human decision record where authorized
```

The chain must remain auditable across successful, failed, invalid, excluded, errored, aborted, filtered, data-unavailable, incomplete, retried, amended, and superseded branches where current lab designs require preservation.

No chain position creates execution authority by existing.

## 8. Idea / Concept Lineage

Future idea and concept lineage should preserve source context, source claims, market mechanism assumptions, data and timeframe assumptions, unresolved questions, unsafe interpretations, and human-review disposition where later authorized.

A source idea is not a candidate, not evidence, not pre-registration, not approval, and not a Strategy Spec.

Unsupported performance claims must remain claims until tested through authorized evidence flow.

Concept lineage should make it possible to audit why a source idea was rejected, deferred, split, merged, or allowed for draft Strategy Spec authoring.

## 9. Strategy Spec Lineage

Future Strategy Spec lineage should preserve the parent concept or source idea context, the human-review posture that allowed drafting, material assumptions, declared data and timeframe dependencies, parameter-bound posture, exclusions, and supersession or amendment context where later authorized.

Strategy Spec lineage must preserve the WP-S2c-151 lock: Strategy Specs are human-reviewable, declarative, non-executable planning surfaces.

Strategy Spec approval, where later designed, means clear enough for variant planning only. It does not create candidate approval, EXP authority, sweep authority, paper/live approval, runtime authority, or gate satisfaction.

## 10. Variant Population Lineage

Future variant population lineage should preserve the parent Strategy Spec reference, bounded parameter or structural derivation context, invalid combinations, exclusions, trial-budget posture, pre-registration posture, and amendment or supersession context.

Variant population manifests are required future pre-registration surfaces before sweep execution under WP-S2c-158.

Lineage must not allow hidden post-result variant insertion, silent search expansion, survivor-only framing, or retroactive cleanup of failed, invalid, excluded, or errored branches.

## 11. Sweep Plan / Run Manifest Lineage

Future sweep plan or run manifest lineage should preserve the parent variant population reference, intended offline-research context, data and timeframe assumptions, trial-budget accounting, result-capture expectations, failure/abort handling posture, and execution-authorization reference where later authorized.

Sweep planning is not runner invocation.

A run manifest, if later designed, must not infer authority from file existence, agent request, dashboard action, scheduler action, or stored plan.

Exact sweep-plan and run-manifest split, storage, fields, IDs, validators, and runner behavior remain deferred.

## 12. Result Population Lineage

Future result population lineage should preserve the parent sweep or run context and the complete tested universe.

The lineage must include attempted, not-attempted, failed, invalid, excluded, errored, aborted, filtered, data-unavailable, timeout/resource-failure, retried, amended, and successful variants where repo-truth result-population design requires preservation.

Result population is evidence input or index only if later authorized. It cannot become ranking, recommendation, approval, promotion, readiness, transition, paper/live, runtime, or decision authority.

## 13. Advisory Ranking Lineage

Future advisory ranking lineage should preserve source Strategy Spec, variant population, sweep/run, result population, anti-overfit / DSR diagnostic source, canonical evidence references, warnings, blockers, and incomplete-evidence posture where later authorized.

Advisory ranking must remain human-review support only.

`Ranked higher` can mean higher review priority only. It cannot mean recommendation, approval, promotion, readiness, transition, D2-006 satisfaction, REC-5 satisfaction, paper/live authority, runtime authority, or human-gate execution.

## 14. Scope 6 / R2S Human-Review Handoff Lineage

Future Scope 6 / R2S handoff lineage may carry evidence references into human-review packet context.

The handoff should expose missing, stale, incomplete, mismatched, below-floor, or unresolved references as warnings or blockers where later authorized.

The handoff should preserve D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6, WP-S2c-100, WP-S2c-113, and permanent human-gate context where applicable.

Provenance cannot create or update R2S approval records in this package and cannot approve or transition anything by completeness alone.

## 15. Parent References And Hash-Pinning Posture

Future parent references should support auditability and reproducibility across the lab chain.

Future hash-pinning or immutable content references may be used where later design authorizes them to preserve locked pre-registration posture and content identity.

Hash-pinning must not become a mechanism for mutating, replacing, or silently refreshing locked Strategy Specs, variant populations, sweep plans, result populations, or canonical evidence after the fact.

Stale or mismatched hashes should later qualify or block review rather than be silently ignored.

Exact hash algorithm, storage fields, validation behavior, mismatch behavior, and query behavior remain deferred.

## 16. Pre-Registration Preservation

Provenance design must preserve WP-S2c-158 and Phase 9 / D2-011 pre-registration discipline.

Future lineage must show whether variants, search families, trial budgets, data assumptions, and exclusion rules were declared before sweep execution.

Lineage must not allow hidden post-result variant insertion, post-result search expansion, post-hoc filter insertion, winner-only survival, or retroactive cleanup of failed, invalid, excluded, errored, aborted, filtered, or data-unavailable attempts.

Amendments and supersessions must be explicit and audit-preserving where later authorized.

## 17. Trial-Log Linkage

Future trial-log linkage should connect attempted and completed trial-level events to the relevant Strategy Spec, variant population, sweep/run context, and result population where repo truth later authorizes that mapping.

Trial-log linkage is reference context only.

It does not create trial evidence, mutate trial rows, replace EXP / REP, or authorize sweeps.

Exact variant/seed/fold/window/run mapping to trial-log rows remains deferred.

## 18. EXP / REP / OL / REC / DEC Linkage

Future provenance should relate to canonical surfaces as references only:

- EXP / REP linkage for experiment planning and result-report evidence where applicable.
- OL linkage for structured outcome-ledger interpretation.
- REC linkage for expected-vs-realized reconciliation.
- DEC and human decision record linkage for decisions where repo truth defines them.

These linkages do not create new canonical evidence, mutate existing evidence, replace human decisions, satisfy gates, or create a parallel evidence or decision store.

Exact reference mechanics remain deferred.

## 19. Agent Operation Provenance

Future agent-operation provenance is a prerequisite for WP-S2c-168.

Future agent support should be auditable enough to show which support role acted, what input it used, what output it prepared, which repo-truth sources it cited or summarized, whether it completed, partially completed, failed, or escalated, and what human review was required afterward.

Agents must not approve, promote, reject canonically, execute gates, alter readiness, mutate canonical evidence, create artifact instances without explicit package scope, run sweeps, contact runtime, or touch paper/live/protected paths.

Agent provenance is support context only.

## 20. Partial-Completion And Failure-Recovery Provenance

Future provenance should make partial completion visible.

Failure reasons should be visible where they affect lineage interpretation.

Retries, reruns, amendments, supersessions, and abandoned branches should be linkable where later design authorizes them.

Abandoned or failed paths should not disappear if they affect result-population completeness, search-lineage interpretation, trial-budget accounting, anti-overfit review, advisory ranking, or human-review packet context.

Failures must not be rewritten into clean success.

Implementation mechanics remain deferred.

## 21. Amendment And Supersession Posture

Future amendments and supersessions should preserve the original referenced item, the reason for change, the parent-child relationship, and the review posture affected by the change.

Amendment may qualify or block clean review if it changes pre-registration, trial budget, data assumptions, variant universe, result population, advisory ranking input, or human-review packet context after results are known.

Supersession should not erase historical evidence or failed paths.

No amendment schema, status set, ID pattern, storage path, validator behavior, or query behavior is locked here.

## 22. Auditability Requirements

Future lab auditability should allow a reviewer to answer:

- where the idea came from;
- how it became a concept;
- why Strategy Spec drafting was allowed or blocked;
- which Strategy Spec governed variant derivation;
- which variant population was pre-registered;
- which sweep/run context generated results;
- whether the full result population is preserved;
- which canonical EXP / REP / trial-log / OL / REC / DEC surfaces are referenced;
- which advisory warnings, blockers, and insufficiency labels apply;
- which Scope 6 / R2S packet references are missing, stale, incomplete, or mismatched;
- which human decision record, if any, later acted on the evidence.

Auditability requirements are future design expectations only, not validator contracts.

## 23. Integrity And Consistency Expectations

Future provenance should surface parent-reference gaps, missing source context, stale hashes, mismatched references, incomplete population retention, post-result amendments, unresolved failure branches, below-floor REC-5 posture, and inconsistencies between advisory text and canonical evidence.

Integrity and consistency expectations may later become warnings, blockers, validators, or query views only through explicit future package authorization.

This package creates no such implementation.

## 24. Relationship To Validity Floor And Backtest-Realism Design

Provenance supports WP-S2c-165 by preserving the source and assumption trail needed for validity-floor and backtest-realism review.

Future lineage should make data, timeframe, fees, funding, slippage, liquidity, mark/index, liquidation, exchange-constraint, bar-path, walk-forward, OOS, trial-budget, DSR / PSR / MinTRL, and robustness context traceable where later artifacts carry it.

Traceability does not make evidence sufficient.

Validity-floor states remain review-support concepts only and cannot approve candidates or execute gates.

## 25. Relationship To Strategy Spec / DSL Expressiveness Design

Provenance supports WP-S2c-166 by preserving assumptions, source references, variant axes, invalid combinations, exclusions, and host-data dependencies needed to interpret future Strategy Specs.

Lineage must preserve typed, declarative, non-executable, side-effect-free, host-data-bounded representation discipline.

Provenance must not make Strategy Specs executable, expand DSL expressiveness, authorize parser/compiler behavior, or create exact schema fields.

## 26. Relationship To Future Agent Orchestration Design

Future agent orchestration design should use this provenance posture as a prerequisite.

Any later agent workflow should be auditable, bounded by role, explicit about input and output, clear about partial failure, and fail-closed around missing repo truth, protected boundaries, canonical evidence, schemas, validators, query views, artifacts, runners, dashboards, runtime, and paper/live paths unless exact package scope authorizes the surface.

Agent outputs remain support-only and must hand off to humans where repo truth requires human review.

## 27. Deferred Implementation Details

Deferred details include exact schema fields, field names, enum values, IDs, storage paths, file names, hash algorithms, validators, query views, integrity views, examples, fixtures, artifact instances, parser/compiler behavior, runner behavior, agent prompts, agent orchestration, dashboard surfaces, warning/blocker labels, formulas, thresholds, split mechanics, amendment mechanics, reference-resolution behavior, and implementation sequence.

Any future implementation requires explicit Main/Karl direction and a scoped package.

## 28. Rejected Alternatives

Rejected alternatives:

- provenance as approval authority;
- lineage as readiness, transition, promotion, or demotion authority;
- audit completeness as candidate approval;
- hash-pinning as artifact mutation or replacement mechanism;
- audit logs that hide failed, invalid, excluded, errored, aborted, filtered, or data-unavailable variants;
- winner-only lineage;
- post-result insertion of variants, filters, or search families;
- unbounded search hidden behind lineage labels;
- advisory ranking by lineage score;
- Scope 6 / R2S approval by provenance completeness alone;
- agent-created provenance that bypasses human review;
- agent consensus as approval;
- runtime, paper/live, broker/exchange/order, OMS, risk, overlay, safe-mode, config, dependency, data, or protected-path contact from provenance surfaces;
- implementation authorization from this prerequisite design.

## 29. Future Package Dependencies

Future packages may need to design or lock:

- exact concept and Strategy Spec lineage references;
- exact Strategy Spec hash-pinning posture;
- exact variant population manifest reference and hash posture;
- exact sweep plan / run manifest lineage posture;
- exact result-population lineage and failure-retention mechanics;
- exact EXP / REP / trial-log / OL / REC / DEC linkage mechanics;
- exact advisory ranking and Scope 6 / R2S handoff references;
- exact agent operation provenance for WP-S2c-168;
- exact amendment and supersession behavior;
- exact validation, query, dashboard, or packet-preparation behavior if later authorized.

Each future package must start from refreshed repo truth and preserve protected boundaries.

## 30. Validation Posture

This package uses CS12 T1-doc-narrow validation unless current repo truth requires a broader profile.

Validation proves changed-file scope and repo consistency only. It does not create implementation authority.

Expected validation includes refreshed-main preflight, exact changed-file scope checks, forbidden-path diff checks, query-view listing, all discovered `v_integrity_*` views, registry/artifact/outcome/reconciliation validators, repo-conventional scoped pytest for research pipeline and integrity surfaces, full pytest where current repo truth requires it, staged diff checks, and clean final status.

## 31. Next-Package Posture

After merge, Side may draft WP-S2c-168 as the agent orchestration readiness prerequisite after refreshed-main preflight and no stop trigger, unless Main/Karl redirects.

Implementation remains unauthorized.

WP-S2c-170 remains gated and must not be drafted automatically.

No schema, validator, query view, artifact, parser/compiler, code, test, tool, runner, sweep, dashboard, agent, prompt, storage path, runtime/paper/live, protected-path, approval, readiness, transition, recommendation, ranking/scoring, or human-gate execution package is authorized by WP-S2c-167.
