# Variant Manifest / Sweep Plan Grammar Design

## 1. Scope

WP-12hc / WP-S2c-182 is a Tier 1 documentation-only design-opening package for future variant manifest and sweep plan artifact grammars.

It creates this design document and updates `docs/project_status.md` only.

It creates no schema, validator, query view, artifact instance, Strategy Spec instance, variant manifest instance, sweep plan instance, runner, sweep execution, result population, canonical evidence artifact, storage path lock, code, tests, tools, examples, approval, readiness, recommendation, transition, ranking/scoring authority, paper/live authority, runtime authority, or human-gate execution authority.

## 2. Repo-Truth and Main Authorization Basis

Repo truth is refreshed `main` after WP-12hb / WP-S2c-181, merged at `258401dc480a2e404188ad1ddc162b596514af28`.

Primary basis:

- WP-S2c-158 locks future variant population manifests as required pre-registration surfaces before sweep execution and locks complete result-population preservation.
- WP-S2c-165 defines lab validity floor, bounded-search governance, walk-forward-first MVP posture, and DSR / PSR / MinTRL prerequisite posture.
- WP-S2c-167 defines provenance, audit, lineage, parent-reference, and hash-pinning posture as evidence-trail discipline only.
- WP-S2c-178 introduced the non-executing Strategy Spec schema with closed operators, `max_condition_group_depth=3`, and a D2-006-style `<=5` free-parameter cap.
- WP-S2c-179 introduced Strategy Spec validator hard checks.
- WP-S2c-180 introduced read-only Strategy Spec query visibility.
- WP-S2c-181 closed the Strategy Spec grammar tranche and required Main direction before WP-S2c-182.

The active execution package records Main authorization for roadmap item 4 and direct WP-S2c-182 drafting. Current merged repo truth wins over memory, summaries, external research, or generic best practice.

## 3. Design Objective

The objective is to define the intended future artifact-grammar shape for:

- variant manifest: the hash-pinned bounded population of parameter variations generated from one parent Strategy Spec;
- sweep plan: the pre-registered test plan over one variant manifest.

This design prepares Main schema-shape review after WP-S2c-182 merges. It does not decide final schema files, final field names, exact enum values, hash algorithms, validator implementation, query views, artifact instances, runner behavior, or result-population storage.

## 4. Non-Authority Boundary

Variant manifests and sweep plans are future typed, declarative, non-executable, side-effect-free, host-data-bounded planning artifacts.

They are not candidates, evidence, approvals, recommendations, ranking/scoring authority, readiness, transitions, EXP authority, paper/live authority, runtime authority, or human-gate execution authority.

The existence of a manifest or sweep plan must not imply runner invocation, sweep authorization, result aggregation, artifact mutation, gate satisfaction, or any permanent human-gate execution.

## 5. Relationship to WP-S2c-158 Pre-Registration Lock

WP-S2c-158 locks the future variant population manifest as the required pre-registration surface before sweep execution.

This design preserves that lock by treating the manifest as the frozen tested-universe declaration, not as evidence or execution authority. The future grammar must make post-result variant insertion, silent population expansion, and winner-only framing structurally impossible or visible as incomplete.

## 6. Relationship to WP-S2c-165 Bounded-Search Governance

WP-S2c-165 requires bounded search, visible trial budget, complete lineage, and full result-population retention.

The future manifest grammar should support constrained manual grids and constrained random search as MVP-compatible generator postures. Bayesian optimization, Hyperband, evolutionary search, open-ended LLM strategy expansion, adaptive pruning, symbolic search, and portfolio optimizer search remain unauthorized unless a later explicit package designs and authorizes them.

## 7. Relationship to WP-S2c-167 Provenance / Audit / Lineage

WP-S2c-167 requires an auditable path from source idea to Strategy Spec, variant population, sweep/run planning, result population, anti-overfit review, advisory handoff, and later human decision records where authorized.

The future manifest and sweep plan grammars should preserve parent references, content hashes, amendment and supersession posture, stale/mismatch blocker posture, failure visibility, and links to later canonical evidence surfaces without creating authority.

## 8. Relationship to WP-S2c-178 Strategy Spec Schema

WP-S2c-178 establishes the current Strategy Spec schema posture: non-executing, human-review planning only, closed operator enum, `max_condition_group_depth=3`, and D2-006-style `<=5` free-parameter cap.

Future variant manifests must reference one parent Strategy Spec by ID, schema version, and content hash. Variant axes must derive only from declared parent free parameters or explicitly reviewed structural choices if later authorized. The manifest must not mutate the parent Strategy Spec or bypass its free-parameter discipline.

## 9. Variant Manifest Purpose

A variant manifest is the future pre-registration surface for a bounded population generated from one parent Strategy Spec before any sweep execution.

Its purpose is to freeze the planned tested universe, expose search bounds, preserve parameter-axis and exclusion rationale, record the denominator for later DSR / multiple-testing review, and make population completeness auditable.

## 10. Sweep Plan Purpose

A sweep plan is the future pre-registered test plan over one variant manifest.

Its purpose is to declare which manifest population will be tested, what validation methods and data/timeframe assumptions are intended, what result capture is expected, and what blockers or stop conditions apply before any future separately authorized offline run.

## 11. Variant Manifest Conceptual Artifact Structure

Future manifest schema-shape review should consider these conceptual groups:

- identity / status / non-execution posture;
- parent Strategy Spec reference and hash posture;
- population cap, declared count, and trial-budget posture;
- parameter axes and generator posture;
- invalid-combination and exclusion declarations;
- variant assignment rows;
- manifest hash-pinning and immutability posture;
- amendment and supersession posture;
- completeness preservation expectations;
- lineage and audit references.

These groups are design concepts only, not final schema fields.

## 12. Sweep Plan Conceptual Artifact Structure

Future sweep plan schema-shape review should consider these conceptual groups:

- identity / status / non-execution posture;
- parent variant manifest reference and hash posture;
- test selection and coverage;
- validation method declaration;
- data, timeframe, and realism assumptions;
- trial-budget and denominator references;
- result-capture expectations;
- amendment and supersession posture;
- non-execution and no-runner boundary;
- lineage and audit references.

These groups are design concepts only, not final schema fields.

## 13. Parent Strategy Spec Reference / Hash Posture

A future manifest should conceptually carry:

- parent `strategy_spec_id`;
- parent `strategy_spec_hash`;
- parent Strategy Spec schema version;
- parent review posture such as clear-for-variant-planning where applicable;
- stale, missing, mismatched, or changed-parent blocker posture.

The reference is audit context only. It creates no Strategy Spec mutation, approval, candidate registration, EXP creation, sweep authority, or gate satisfaction.

## 14. Variant Population Cap Posture

A future manifest should carry an explicit finite population-size cap, declared variant count, and trial-budget posture.

The cap is boundary-critical because it defines the tested-universe denominator for later DSR / multiple-testing interpretation and prevents unbounded or hidden search expansion.

Population cap representation is a required Main schema-shape review item before WP-S2c-183. This document does not choose final cap fields, units, or validator mechanics.

## 15. Parameter-Axis and Assignment Posture

A future manifest should describe each parameter axis conceptually with:

- parameter name;
- source reference to a parent Strategy Spec free parameter;
- type and units;
- allowed values or bounded range;
- generator posture, limited at MVP to constrained manual grid or constrained random search unless later authorized;
- invalid-combination and exclusion references;
- whether the axis counts toward the parent `<=5` free-parameter posture.

Future variant assignment rows should conceptually carry a variant identifier placeholder, parameter assignments, assignment hash, inclusion/exclusion status, invalid/excluded/not-attempted reason posture, parent axis references, and lineage/audit references.

No actual variants are created here.

## 16. Invalid-Combination and Exclusion Posture

The future manifest grammar should preserve invalid combinations and exclusions before results are known.

Invalid or excluded variants should remain visible with reason and origin. Exclusion rules must not become post-result rescue logic, silent cleanup, hidden parameter-axis insertion, or a way to erase failed or inconvenient variants.

## 17. Manifest Hash-Pinning / Immutability Posture

A future manifest should conceptually support manifest hash, hash algorithm placeholder, hash scope, population snapshot identity, frozen-at posture, pre-sweep immutability declaration, stale/mismatch handling, and amendment/supersession references.

Hash-pinning and pre-registration are boundary-critical schema-shape items for Main review before WP-S2c-183. This design does not choose a hash algorithm or final hash scope.

## 18. Amendment / Supersession Posture

Amendments and supersessions must preserve the original manifest or sweep plan, the reason for change, the timing concept, the parent-child relationship, and whether pre-registration, trial budget, data assumptions, or population membership changed.

Post-result mutation, silent refresh, and retroactive cleanup remain forbidden. Supersession should preserve historical auditability rather than overwrite it.

## 19. Sweep-Plan Test-Plan Posture

A future sweep plan should reference exactly one parent variant manifest by ID and hash, declare the manifest population count and cap it relies on, and define the planned test coverage.

The plan may cover all variants or a pre-registered subset only if the subset selection rule and exclusions are declared before results. It must not permit post-result additions outside the manifest population.

## 20. Validation Method Declaration Posture

A future sweep plan should declare intended validation methods at planning level, including where applicable:

- backtest;
- walk-forward / OOS validation;
- robustness checks;
- cost, funding, slippage, liquidity, liquidation, mark, and bar-path stress posture;
- DSR / PSR / MinTRL accounting posture;
- Monte Carlo as later or conditional strengthening, not mandatory MVP.

Exact methods, windows, formulas, thresholds, and implementation mechanics remain deferred unless already locked by repo truth.

## 21. Walk-Forward / OOS / Robustness / DSR Accounting Posture

The future sweep plan grammar should preserve walk-forward-first MVP posture from WP-S2c-165 unless Main later replaces it.

It should expose chronological separation, OOS windows, robustness families, trial-budget denominator, search lineage, and DSR / PSR / MinTRL prerequisite posture as review-support context only. These declarations cannot approve variants, satisfy D2-006, satisfy REC-5, rank with authority, or trigger transitions.

## 22. Result-Population Capture Expectations

The future sweep plan should declare expected result-population capture without creating the result population.

Complete downstream visibility should include all generated, attempted, not-attempted, invalid, excluded, errored, aborted, filtered, data-unavailable, and successful variants where applicable. Winner-only review must be structurally impossible or visible as incomplete.

The relationship to canonical EXP / REP, trial-log, OL, REC, and DEC remains deferred.

## 23. Anti-Overfit and Multiple-Testing Boundaries

The manifest and sweep plan grammars should preserve denominator context for later anti-overfit / DSR-style review.

They must not claim that smaller, faster, or more automated search is cleaner evidence. Search efficiency is not validity. Many tried variants increase evidence burden and must remain visible.

## 24. Non-Executable / No-Runner Boundary

Variant manifest and sweep plan artifacts must reject executable structure, arbitrary code, callbacks, loops, recursion, external calls, imperative control flow, broker/exchange/order directives, runtime actions, paper/live actions, readiness updates, transition triggers, approval actions, ranking scores, and recommendations.

Artifact existence must not invoke a runner, authorize a sweep, create EXP authority, create evidence, aggregate results, update readiness, or execute any gate.

## 25. Future Validator Surface

A future validator may enforce schema/content shape, required fields after schema approval, parent Strategy Spec reference format, parent Strategy Spec hash presence, finite population cap presence, declared variant count within cap, variant assignments within parent Strategy Spec ranges or allowed values, `<=5` parent free-parameter posture, no undeclared parameter axes, invalid-combination and exclusion declarations, manifest hash fields consistent with schema rules, sweep plan references to valid manifest ID/hash, no post-hoc additions outside the manifest population, and non-executable / non-authority flags.

A future validator must not approve artifacts, recommend variants, rank variants with authority, execute gates, trigger transitions, run sweeps, invoke runners, create result populations, mutate evidence, update readiness, or contact runtime/paper/live/protected paths.

## 26. Future Schema Introduction Surface for WP-S2c-183

Main schema-shape review after WP-S2c-182 should decide or direct:

- whether variant manifest and sweep plan share one schema package or split into two schema files;
- canonical schema file path options;
- top-level field groups;
- required versus optional groups;
- artifact status enum posture;
- parent Strategy Spec reference/hash posture;
- parent manifest reference/hash posture;
- population-cap representation;
- trial-budget representation;
- parameter-axis representation;
- variant-assignment representation;
- invalid-combination / exclusion representation;
- manifest hash-pinning / immutability representation;
- amendment / supersession posture;
- sweep validation-method representation;
- walk-forward/OOS/robustness/DSR accounting posture;
- result-capture expectation fields;
- validator boundaries;
- explicit forbidden structure;
- zero-instance posture.

Hash-pinning / pre-registration and population-cap representation are the boundary-critical review items. WP-S2c-183 is not auto-draftable until Main completes this schema-shape review.

## 27. Relationship to Roadmap Item 5 Runner / Result-Population Work

WP-S2c-182 opens roadmap item 4 only.

WP-S2c-183 schema work requires Main schema-shape review after this package merges. WP-S2c-184 validator work comes after schema. WP-S2c-185 read-only query views come after validator. WP-S2c-186 checkpoint closes item 4 and requires Main re-engagement for item 5.

Roadmap item 5 remains offline research runner / result-population work and is not authorized here. The user's always-on non-authoritative strategy-improvement end-state remains downstream; this package does not authorize continuous lab, candidate queue, allocator, dashboard, agent, paper bridge, live bridge, or runtime implementation.

## 28. Explicit Forbidden Structure

The future grammar must explicitly reject:

- unbounded variant populations;
- hidden parameter axes;
- undeclared variants;
- post-hoc variant addition;
- post-result manifest mutation;
- silent manifest refresh;
- winner-only population retention;
- adaptive search without future explicit authorization;
- executable variant or sweep artifacts;
- arbitrary code, callbacks, loops, recursion, external calls, imperative control flow, parser/compiler behavior, or host execution;
- runner invocation by artifact existence;
- sweep execution;
- result aggregation;
- ranking/scoring authority;
- recommendation authority;
- candidate approval;
- EXP approval;
- readiness authority;
- transition authority;
- paper/live authority;
- runtime authority;
- human-gate execution.

## 29. Deferred Items

Deferred items include exact schema files, exact fields, enum values, hash algorithms, hash scopes, status mechanics, validator implementation, query views, artifact paths, artifact IDs, examples, fixtures, Strategy Spec instances, variant manifest instances, sweep plan instances, run manifests, result populations, EXP / REP / trial-log mapping, OL / REC / DEC linkage mechanics, runner interfaces, formulas, thresholds, windows, robustness protocols, dashboards, agents, prompts, and implementation sequence.

## 30. Stop / Escalation Conditions

Stop and re-engage Main if future schema-shape or package work would require schema, validator, query-layer, code, test, artifact-instance, runner, result-population, EXP / REP / trial-log / OL / REC / DEC, ranking, recommendation, approval, readiness, transition, paper/live, runtime, protected-path, or human-gate authority beyond the active package.

Also stop if proposed grammar permits unbounded search, post-hoc variant insertion, hidden population mutation, winner-only retention, executable artifacts, or conflict with WP-S2c-158, WP-S2c-165, WP-S2c-167, WP-S2c-178, D2-006, D2-007, REC-5, Scope 6, Phase 9 / D2-011, or permanent human gates.

## 31. Validation Posture

WP-S2c-182 uses T1-doc-narrow validation.

Validation should prove exact changed-file scope, forbidden-path cleanliness, query-view and integrity health, registry/artifact/outcome/reconciliation validator health, Strategy Spec validator health, and repo-conventional scoped pytest where current repo convention expects it for this class. Full pytest is not required unless repo truth, validation failure, local convention, or execution judgment indicates it is needed.

## 32. Next-Package Posture

After WP-S2c-182 merges, Side must report back to Main with the proposed variant manifest / sweep plan schema shape before any WP-S2c-183 draft.

WP-S2c-183 is not auto-draftable until Main reviews the schema-shape items, especially hash-pinning / pre-registration structure and population-cap representation. Permanent human gates and all protected boundaries remain unchanged.
