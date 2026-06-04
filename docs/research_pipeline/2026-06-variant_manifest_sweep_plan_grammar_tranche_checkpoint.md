# Variant Manifest / Sweep Plan Grammar Tranche Checkpoint

## 1. Scope

WP-12hg / WP-S2c-186 is a Tier 1 documentation-only tranche checkpoint.

It closes roadmap item 4, the variant manifest / sweep plan artifact grammar tranche, as complete-as-built through WP-S2c-185.

This package creates this checkpoint document and updates `docs/project_status.md` only. It creates no schema, validator, query view, code, test, artifact instance, Strategy Spec instance, variant manifest instance, sweep plan instance, result population, runner, sweep execution, canonical sweep run, result computation, runtime behavior, paper/live behavior, protected-path change, approval, readiness, recommendation, transition, ranking/scoring, or human-gate execution authority.

## 2. Main Authorization Basis

Main reviewed the WP-S2c-185 merge/report-back and directed Side to close item 4 with WP-S2c-186 as planned.

Main also authorized WP-S2c-187 directly after WP-S2c-186 merge as the item 5 design-opening package for offline runner / result-population architecture, subject to refreshed-main preflight and no stop trigger.

The completed Side Research finding is included here only as concise supporting evidence for item 5 and item 6 design, not as repo truth or implementation authorization.

## 3. Completed Item 4 Package Chain

The completed item 4 chain is:

- WP-S2c-182 / WP-12hc: variant manifest / sweep plan grammar design opening.
- WP-S2c-183 / WP-12hd: variant manifest and sweep plan schemas.
- WP-S2c-184 / WP-12he: variant/sweep validator.
- WP-S2c-185 / WP-12hf: read-only variant/sweep query-layer visibility.

## 4. Complete-As-Built Summary

Item 4 is complete through WP-S2c-185.

The repo now contains design, schema, validator, and read-only query visibility for future variant manifests and sweep plans. These surfaces are declarative planning and inspection surfaces only. They do not create artifacts, execute anything, compute results, approve candidates, rank variants, satisfy gates, or reach runtime/paper/live/protected paths.

## 5. Variant Manifest Surface Now Present

The variant manifest is the future hash-pinned bounded population pre-registration surface generated from one parent Strategy Spec.

The schema records one parent Strategy Spec reference and hash posture, finite population cap, declared committed population, parameter axes, variant assignments, invalid/exclusion declarations, manifest hash-pinning, immutable supersession posture, lineage, review posture, and non-execution / non-authority declarations.

The validator hard-checks schema validity, filename/ID consistency, duplicate IDs, parent Strategy Spec hash mismatch when the parent is available, manifest hash mismatch, finite population and count reconciliation, parameter-axis / assignment integrity, committed-denominator posture, supersession posture, non-authority flags, and forbidden executable keys.

## 6. Sweep Plan Surface Now Present

The sweep plan is the future pre-registered test plan over exactly one variant manifest.

The schema records parent manifest ID/hash posture, selected population coverage, validation-method declarations, data/timeframe and backtest-realism assumptions, result-capture expectations, trial accounting, lineage, review posture, amendment/supersession posture, and non-execution / non-authority declarations.

The validator hard-checks parent manifest reference/hash posture, selected variants remaining inside the manifest, committed denominator preservation, no-runner/no-computation flags, winner-only-retention rejection, non-authority flags, and forbidden executable keys.

## 7. Main Adjustment 1: Immutable Supersession / No Supersession After Results / Fresh Denominator

The tranche preserves Main Adjustment 1.

Variant manifests and sweep plans may preserve append-only supersession lineage before associated results exist. After associated results exist, supersession is not allowed; the artifact posture is close-only after results.

For a new manifest, a fresh committed denominator is required. Old manifest results are not inherited or absorbed into a new manifest.

## 8. Main Adjustment 2: Committed-Population Denominator

The tranche preserves Main Adjustment 2.

The multiple-testing / DSR-style denominator is the committed pre-registered population count, not the executed count or successful count.

Failed, excluded, invalid, errored, aborted, filtered, data-unavailable, and not-attempted variants remain visible and counted. Executed-only and successful-only denominators are rejected.

## 9. Side Research Finding As Non-Authoritative Supporting Evidence

Completed Side Research covered pre-registration and multiple-testing denominator accounting in systematic quant research, hash-pinning hypothesis/variant populations, prevention of post-hoc expansion, and honest trial-count denominators for DSR-style correction.

The finding supports prospective full-population pre-registration, immutable population identity, canonical hash-pinning, append-only amendment/supersession history, no supersession after results for confirmatory populations, fresh denominators for new manifests, committed-population denominators, and keeping failed/invalid/errored/aborted/filtered/data-unavailable/not-attempted variants visible and counted.

This research is not repo truth, not implementation authorization, and not committed as a standalone item 4 brief. Per Main direction, item 5 should incorporate the identity-hash versus audit-envelope split and append-only population/result ledger pattern. Item 6 should incorporate confirmatory-vs-exploratory labels plus raw committed denominator and later effective-trial diagnostics.

## 10. Zero-Instance Posture

Current repo truth remains zero-instance for this grammar family.

There are no canonical Strategy Spec instances, variant manifest instances, sweep plan instances, result-population instances, run manifests, canonical sweep runs, runner-created results, or item 4 artifact instances.

Tests use temporary fixtures only.

## 11. Non-Execution / Non-Authority Boundary

Variant manifest and sweep plan artifacts remain typed, declarative, non-executable, side-effect-free, host-data-bounded planning artifacts only.

Query views are descriptive visibility only. Validators hard-check posture but do not approve artifacts.

No ranking, recommendation, approval, readiness, transition, human-gate execution, EXP authority, paper/live authority, runtime authority, runner authority, sweep authority, result authority, or protected-path authority exists.

## 12. Validation Posture Across The Tranche

WP-S2c-182 used Tier 1 documentation validation for the design opening.

WP-S2c-183 introduced schemas with implementation validation and full pytest.

WP-S2c-184 introduced the variant/sweep validator with implementation validation and full pytest.

WP-S2c-185 introduced read-only query-layer visibility with implementation validation and full pytest.

WP-S2c-186 itself is T1-doc-narrow and validates exact changed-file scope, query/integrity health, validators, and scoped tests without changing implementation surfaces.

## 13. Remaining Unimplemented Surfaces

Item 4 did not implement:

- any artifact instances;
- result-population schemas or instances;
- offline runner behavior;
- runner invocation;
- result computation;
- canonical sweep runs;
- canonical EXP / REP / trial-log mapping for variant populations;
- dashboards, agents, prompts, continuous lab, candidate queue, allocator, paper bridge, live bridge, or runtime behavior.

Each remains future work requiring explicit package authority.

## 14. Roadmap Item 5 Handoff

Roadmap item 5 is the offline research runner / result-population tranche.

It is the first roadmap direction that may eventually execute at population scale, but only after later packages authorize and implement that surface. It remains offline research only.

The future runner is expected to call the realism-corrected backtester without modifying the backtester or protected paths. It must preserve deterministic execution, complete-population output, committed-population denominator accounting, and offline-only posture.

Item 5 does not authorize runtime, paper/live, OMS, reconciliation, kill-switch, broker, exchange, order, or Tier 4 contact. First canonical sweep run remains separately unauthorized.

## 15. Authorized Next WP Sequence

Main-authorized item 5 sequence:

- WP-S2c-187: Offline runner / result-population design opening.
- WP-S2c-188: Result-population schema introduction.
- WP-S2c-189: Result-population validator implementation.
- WP-S2c-190: Offline runner implementation.
- WP-S2c-191: Result-population query-layer extension.
- WP-S2c-192: Item 5 tranche checkpoint.

WP-S2c-187 is authorized directly after WP-S2c-186 merge, refreshed-main preflight, and no stop trigger. WP-S2c-188 is gated by Main review of result-population schema shape after WP-S2c-187.

## 16. Mandatory Stop / Review Points

After WP-S2c-187 merge, Main must review result-population schema shape before WP-S2c-188. Focus: complete-population / denominator-preservation structure, identity-hash / audit-envelope split, and append-only ledger posture.

After WP-S2c-189 merge, Main must review runner execution-surface scope before WP-S2c-190. Focus: what the runner calls, what it reads, where it writes, how offline-only posture is enforced, how determinism is enforced, and how complete-population output is enforced.

After WP-S2c-192, Main must re-engage for roadmap item 6 and the first-sweep-run question.

Any protected-boundary tension or scope expansion requires immediate halt and report-back.

## 17. User End-State Visibility

The user end-state remains visible and downstream: an always-on, non-authoritative Strategy Research Lab with automated self-assessment, candidate generation, testing, comparison, and briefing; multiple paper candidates continuously tested; eventually multiple approved live strategies in parallel; and central allocation/risk coordination before multi-strategy operation.

All promotion, risk-change, paper/live, and live-deployment decisions remain human-approved.

These end-state capabilities remain visible and unranked. They are downstream of core pipeline dependencies and are not authorized by WP-S2c-186 or item 5. No continuous lab, candidate queue, allocator, paper-live bridge, or live deployment work is pulled forward by this checkpoint.

## 18. Forbidden Implications

This checkpoint explicitly rejects these implications:

- item 4 authorizes runner execution;
- item 4 authorizes result computation;
- item 4 authorizes canonical sweep runs;
- WP-S2c-186 authorizes item 5 implementation beyond Main's explicit capsule sequence;
- Side Research changes repo truth by itself;
- query views are approval, readiness, ranking, or recommendation surfaces;
- validators approve or promote artifacts;
- result populations already exist;
- first canonical sweep run is authorized;
- paper/live/runtime paths are reachable;
- protected paths may be modified;
- human gates are weakened.

## 19. Next-Package Posture

After WP-S2c-186 merges, Side may draft WP-S2c-187 from refreshed `main` if no stop trigger fires and Main does not redirect.

WP-S2c-187 is documentation-only design opening for offline runner / result-population architecture. WP-S2c-188 remains gated by Main schema-shape review after WP-S2c-187.

No first canonical sweep run is authorized in item 5 until a separate future authorized moment, surfaced after WP-S2c-192.

## 20. Report-Back Posture

The WP-S2c-186 report-back should state branch/base, repo-truth discovery, delivered changes, checkpoint summary, Side Research handling, item 5 handoff, boundary check, validation results, open issues, manual steps, PR/push status, and ready-for-review status.

Manual steps: none.
