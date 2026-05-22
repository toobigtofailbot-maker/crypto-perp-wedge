# H-006 R1/R2 Approval + Implementation-Use Decision Lock

## Scope

WP-12cg / WP-S2c-39 is a Tier 1 documentation-only approval and implementation-use decision lock.

This document locks approval and use of R1/R2 methodologies for H-006 onward. It creates no evidence artifacts and changes no runtime, implementation, query-layer, validator, schema, configuration, dependency, data, paper/live, OMS, risk, safe-mode, exchange, broker, execution, or protected-path behavior.

This package does not modify the R1 or R2 design documents. It does not create H-006 REP, OL, REC, LCH, EXP, trial-log, registry, schema, validator, query-layer, implementation, config, dependency, data, Path B, runtime, paper/live, OMS, risk, safe-mode, policy, scoring, ranking, recommendation, approval, readiness, lifecycle, promotion, demotion, or downstream-authority material.

This package does not create candidate-level approval, cohort-level approval, A2C-001 completion, Path B authority, runtime/paper/live authority, policy/scoring/ranking/recommendation authority, readiness/lifecycle authority, or downstream authority.

## Approval basis

This document locks the user/Karl-approved Main output into repo truth.

Approval basis, paraphrased:

```text
Main/Karl approved R1 paired-source reuse as designed, R2 batched REP+OL+REC cycles as designed, and combined R1×R2 use. Methodologies apply from H-006 onward, remain opt-in per cycle, and preserve H-005 strict runway history.
```

## R1 approval

R1 paired-source reuse is approved as designed in `docs/research_pipeline/2026-05-stage2c_paired_source_reuse_methodology_design.md`.

R1 applies from H-006 onward. It is opt-in per cycle, not mandatory.

R1 allows one eligible REP/OL source chain to support separate REC artifacts for different expectation-source types.

R1 must preserve:

- separate REC artifacts;
- separate `expectation_source_type`;
- separate expectation-source comparisons;
- separate exact-segment counts;
- source REP/OL lineage;
- REC-5 per exact segment;
- no candidate/cohort/downstream authority.

## R2 approval

R2 batched REP+OL+REC cycles are approved as designed in `docs/research_pipeline/2026-05-stage2c_batched_cycle_methodology_design.md`.

R2 applies from H-006 onward. It is opt-in per cycle, not mandatory.

R2 allows one explicitly scoped package to create a complete internally ordered evidence cycle.

Artifact semantics remain separate:

- REP remains source experiment report;
- OL remains derived outcome ledger;
- REC remains expectation-source reconciliation;
- artifact IDs remain unique;
- validators still run;
- query surfaces and exact-segment counts remain correct.

R2 compresses package count only and does not reduce validation.

## Combined R1×R2 approval

Combined R1×R2 use is approved when eligibility holds.

Approved combined H-006 cycle pattern:

```text
one WP creates:
1. REP
2. trial_log row append
3. OL derived from the REP
4. REC(d2_006_gates) derived from the OL
5. REC(exp_success_criteria) derived from the OL
6. docs/project_status.md update
```

Two separate REC artifacts must be created. Each REC must have its own expectation-source comparison. Exact-segment counts remain separate.

The package is atomic: all artifacts validate or none commit. Partial chains must not be pushed as completed evidence. If a REC cannot be validly produced, stop and do not commit a partial evidence chain unless a future active WP explicitly authorizes reduced scope.

## H-006 procedure

H-006 is the next intended A2C-001 cohort member after the H-005 checkpoint, subject to no stop trigger.

H-006 source EXP is expected to be `EXP-0006`, but future H-006 execution packages must recompute and verify this from refreshed repo truth.

H-006 should use combined R1+R2 by default when eligibility is verified.

Expected H-006 size if eligibility holds:

- cycle 1 combined evidence package;
- cycle 2 combined evidence package;
- H-006 checkpoint package.

This is expected to reduce H-006 from the old strict pattern of about 13 packages to about 3 H-006 runway packages after this approval lock.

Exact cycle windows, artifact IDs, source metrics, and exact REC count movements must be recomputed in the execution WPs from refreshed repo truth.

## Eligibility and fallback rules

Combined R1+R2 may be used only when all R1 and R2 eligibility requirements are satisfied.

At minimum, future H-006 execution WPs must verify:

```text
same candidate_id
same plan_id / EXP provenance
same outcome_kind
same pipeline_version
same evaluation window
same actual bar window when present
same data source and dataset identifiers
same config hash where applicable
same trial ID and source REP
same source OL
no existing REC conflict
no schema/validator/query-layer changes required
exact count movement deterministic
changed-file set reviewable
no active package prohibition
no protected path / runtime / config / dependency contact
```

Fallback rules:

- If R1 paired-source reuse eligibility fails but R2 batching remains eligible, stop and report; do not silently fall back unless a follow-up package explicitly authorizes R2-only.
- If R2 batching eligibility fails but strict evidence remains possible, stop and report; do not silently split into REP/OL/REC WPs unless a follow-up package explicitly authorizes strict mode.
- If both R1 and R2 eligibility hold, use combined R1+R2.
- If any artifact in a combined package fails validation, the package halts and commits nothing.

## Efficiency patterns additionally approved

E10 checkpoint-plus-direction record may be used at future runway boundaries when checkpoint and direction-setting are genuinely simultaneous and no ambiguity is surfaced. Do not use it when the checkpoint reveals unresolved state or the next direction is not clearly approved.

E11 runway-internal `docs/project_status.md` entries may be minimal-form when a tight batched runway package already carries canonical detail in the artifact files, PR body, and report-back. Final checkpoint entries must summarize the complete runway state. Status-entry simplification must not remove dependency, authority, boundary, or validation-critical facts.

E10 and E11 are safe opt-in efficiency patterns, not mandatory procedures.

E12-E16 implementation is not authorized here. They remain future design candidates unless separately scoped.

## Validation and atomicity requirements

No validation reduction is authorized.

Required commands still run directly. Integrity views must be clean. Registry validators must pass. Source REP/OL/REC validators must pass as applicable. Exact-segment query views must verify expected count movement. Scoped and full pytest must pass unless future repo-approved validation-tier rules change. The diff/scope helper must pass or report only known allowed false positives.

In a combined package, internal validation gates must prove:

- REP validity before OL derivation;
- OL validity before REC derivation;
- both RECs valid and exact-segment counts correct before commit;
- no partial evidence chain is committed.

## What is authorized

This document authorizes only:

- R1 methodology use for H-006 onward when eligible.
- R2 methodology use for H-006 onward when eligible.
- Combined R1×R2 use for H-006 when eligible.
- First H-006 combined R1+R2 cycle package may be drafted after this approval-lock merges, from refreshed `main`, if no stop trigger fires and no competing `docs/project_status.md` PR exists.
- E10/E11 safe-adoption patterns may be used when their stated conditions hold.

## What is not authorized

This package does not authorize:

- creating H-006 evidence artifacts inside this package;
- H-006 candidate approval;
- cohort-level approval;
- A2C-001 completion;
- Path B;
- runtime;
- paper/live;
- OMS;
- risk;
- safe mode;
- exchange/broker/execution behavior;
- config/dependency/data changes;
- schema/validator/query-layer changes;
- AUTO successor work;
- policy/scoring/ranking/recommendation;
- approval/promotion/demotion/readiness/lifecycle authority;
- downstream authority;
- E12-E16 implementation;
- validation command-running wrappers;
- RTK/RTX/TRS tooling implementation.

## Next package boundary

After merge, Side may draft:

```text
WP-12ch / WP-S2c-40 — H-006 combined R1+R2 cycle 1 evidence package
```

from refreshed `main`, if no stop trigger fires and no competing `docs/project_status.md` PR exists.

The next package must perform repo-truth discovery before assuming:

- EXP ID;
- existing H-006 counts;
- next REP/OL/REC IDs;
- evaluation window;
- data availability;
- R1 eligibility;
- R2 eligibility;
- changed-file set;
- tests requiring stale committed-state refresh.

## Validation

Validation results for WP-12cg / WP-S2c-39 are recorded in the PR and execution report-back. This document itself creates no evidence artifacts and changes no validation authority.
