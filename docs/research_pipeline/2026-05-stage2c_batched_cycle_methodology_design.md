# Stage 2c Batched REP+OL+REC Cycle Methodology Design

## Scope

WP-12bk / WP-S2c-21c is a Tier 1 methodology-design package only.

This document designs prospective R2 batched REP+OL+REC cycle methodology. It
does not implement batched cycles, does not authorize batched-cycle use, does
not apply R1 or R2, does not change H-005, does not open H-006 implementation,
and does not change schemas, validators, query-layer behavior, artifact
schemas, tests, runtime behavior, configs, protected paths, or evidence
artifacts.

This document is advisory methodology design only until Main/Karl explicitly
approve later implementation use and that approval is locked into repo truth.

## Current state and motivation

The current strict evidence pattern often splits a single logical observation
into multiple work packages:

- one REP package;
- one OL package;
- one REC package.

This has preserved safety and reviewability. It also increases work-package
count, repeated `docs/project_status.md` edits, repeated report-back burden,
and repeated validation overhead.

The goal of R2 is to design a safe future method to batch a complete evidence
cycle without weakening artifact integrity, validation, exact-segment counts,
expectation-source separation, reviewability, or protected boundaries. This is
an efficiency design, not a correction. Current artifacts remain valid repo
truth.

Repo-truth observations at drafting time:

- REP artifacts identify the source experiment report, including `plan_id`,
  `candidate_id`, trial IDs, evaluation windows, data references, metrics,
  gate results, verdict, and no-authority posture.
- OL artifacts derive from REP artifacts through `derivation_record`, preserve
  source REP lineage, candidate identity, outcome kind, pipeline version,
  windows, metrics, and no-authority posture.
- REC artifacts derive from OL artifacts, identify their own
  `expectation_source_type`, expectation source artifact, copied realized
  metrics, comparisons, exact-segment interpretation, and no-authority posture.
- Current forward H-001 and H-005 strict runway packages create REP, OL, and
  REC artifacts in separate packages.
- Current reconciliation counts are surfaced by exact segment in
  `v_reconciliation_candidate_pipeline_summary`.

## Definition of batched cycle

A batched cycle is a future methodology where one explicitly approved package
may create a full internally ordered evidence cycle:

```text
REP -> OL -> REC
```

The package is batched, but artifact semantics stay separate:

- REP remains the source experiment report.
- OL remains the derived outcome ledger.
- REC remains the expectation-source reconciliation.
- Artifact IDs remain unique.
- Validators still run.
- Query surfaces and exact-segment counts must remain correct.
- The PR remains reviewable.

Batching compresses package count only. It does not merge artifact families or
reduce validation.

## Current strict evidence pattern

The current strict forward evidence pattern is:

```text
WP-A: create REP
WP-B: create OL from REP
WP-C: create REC from OL
```

H-001 first-member completion and the H-005 strict runway use this pattern for
forward evidence production. H-005 continues under the strict pattern unless
Main explicitly revises sequencing later.

## Proposed R2 design

The proposed prospective R2 pattern is:

```text
one WP creates:
1. REP
2. OL derived from that REP
3. REC derived from that OL
```

When combined with approved R1, a future pattern may be:

```text
one WP creates:
1. REP
2. OL derived from that REP
3. REC(d2_006_gates) derived from that OL
4. REC(exp_success_criteria) derived from that OL
```

This combined pattern is not operational until Main/Karl approves it after
WP-S2c-21c. R2 alone designs package batching. R1 designs source reuse. Neither
is implementation-authorized by this document.

## Package eligibility requirements

Future batched-cycle packages may be eligible only when all of the following
are true:

- the EXP or source plan already exists and validates;
- no EXP scaffold authoring is needed;
- evaluation-window methodology is locked and unambiguous;
- the target source evidence is a new observation, not a rewrite of existing
  evidence;
- artifact IDs can be recomputed safely at execution time;
- the REP can be created without schema, validator, or query-layer changes;
- the OL can be derived from the REP without schema, validator, or query-layer
  changes;
- the REC can be derived from the OL without schema, validator, or query-layer
  changes;
- exact-segment count movement is known and deterministic;
- expected changed-file set is reviewable;
- no protected path, runtime, config, dependency, Path B, or H-006
  implementation boundary is crossed;
- package-specific scope permits batching.

If any step requires redesign, forbidden scope, schema change, validator
change, query-layer change, runtime contact, or protected-path contact,
batching is ineligible.

## Required artifact ordering

A future batched package must preserve this internal order:

1. refresh `main` and verify dependencies;
2. compute next artifact IDs;
3. produce REP first;
4. validate REP and registry state as appropriate;
5. produce OL derived from the REP;
6. validate OL and registry state as appropriate;
7. produce REC or RECs derived from the OL;
8. validate REC or RECs, exact-segment counts, and integrity views;
9. update `docs/project_status.md`;
10. run scoped and full validation;
11. stage exact changed-file set.

No REC may be authored before its source OL exists. No OL may be authored before
its source REP exists. A batched PR must show this ordering in the changed files,
validation notes, and report-back.

## Validation gates inside a batched package

Even when batched, validation must preserve logical stage gates:

- after REP creation: report, schema, and registry checks sufficient to prove
  the REP is valid;
- after OL creation: outcome-ledger checks sufficient to prove OL lineage and
  metrics are valid;
- after REC creation: reconciliation checks sufficient to prove
  expectation-source comparison and exact-segment counts are valid;
- after all changes: integrity views, registry validators, scoped pytest, full
  pytest, diff checks, and untracked-file checks.

The design does not reduce validation. It compresses package count only.

## Partial-failure and rollback rules

If REP creation succeeds but OL derivation fails, stop without committing and
either remove uncommitted artifacts or leave them uncommitted with explicit
report-back.

If REP and OL creation succeed but REC derivation fails, stop without
committing and report exactly which artifact stage failed.

If any validation fails, stop without committing.

A batched package may not commit a partial evidence chain unless the active WP
explicitly permits a reduced-scope commit. Partial artifacts must not be pushed
as completed evidence.

## Exact-segment counting rules

REP and OL do not increase reconciliation count. Only REC artifacts increase
exact-segment counts.

Exact-segment counts remain keyed by:

- `candidate_id`;
- `outcome_kind`;
- `pipeline_version`;
- `expectation_source_type`.

One batched package may create one or more RECs only if each REC's expectation
source and count movement is explicit. A D2 REC increments only the
`d2_006_gates` exact segment. An EXP-success REC increments only the
`exp_success_criteria` exact segment. Counts are not combined.

The REC-5 floor remains per exact segment. Batched cycles cannot create
candidate-level, cohort-level, policy, ranking, approval, readiness, lifecycle,
runtime, or downstream authority.

## Interaction with R1 paired-source reuse

R1 designs source reuse. R2 designs package batching. They are separable.

R2 alone may support one REP/OL/REC chain in one package. R1 plus R2 combined
may support one REP/OL with multiple separate RECs in one package.

R1 plus R2 cannot be used until Main/Karl approves after WP-S2c-21c. Combined
use must preserve R1 eligibility, lineage, expectation-source separation,
unique REC IDs, separate expectation-source comparisons, and exact-segment
count preservation.

## Candidate / window / pipeline constraints

R2 is prospective for H-006 onward only unless Main explicitly changes that
later. H-005 remains strict and unchanged.

R2 cannot be used when:

- the evaluation window is ambiguous;
- artifact derivation requires manual interpretation beyond the package scope;
- the package is protected runtime, paper, live, OMS, risk, safe-mode, config,
  dependency, or implementation work;
- schema, query, or validator changes are required but not explicitly
  authorized;
- the active WP forbids batching;
- candidate, outcome kind, pipeline version, or expectation source would be
  blurred or combined.

## H-005 preservation

H-005 continues under the strict exact-segment runway.

Current repo truth records:

```text
H-005 / research_oos / pre_wp_5b / d2_006_gates = 2
H-005 / research_oos / pre_wp_5b / exp_success_criteria = 1
```

WP-S2c-26 through WP-S2c-34 remain sequential unless Main explicitly revises
sequencing. No batched-cycle implementation may be applied to H-005 by this
document. H-005 artifacts remain valid strict-pattern precedents.

## H-006+ prospective use

R2 may be considered for H-006 or later only after:

- WP-S2c-21b merges;
- WP-S2c-21c merges;
- Main/Karl re-engages and explicitly approves R1/R2 application;
- a future implementation WP encodes exact allowed behavior.

Until that happens, this document is advisory methodology design only.

## Reviewer checklist

A future reviewer deciding whether a proposed batched package is eligible
should verify:

- source EXP exists and validates;
- evaluation window is locked;
- artifact IDs are available;
- REP can be produced without forbidden scope;
- OL can be derived directly from REP;
- REC can be derived directly from OL;
- exact count movement is explicit;
- expectation-source separation is preserved;
- R1 eligibility is checked if multiple RECs share one source OL;
- changed-file set remains reviewable;
- validation gates are all run;
- no H-005, H-006, Path B, or protected-path unauthorized scope is present;
- no policy, scoring, ranking, recommendation, readiness, lifecycle,
  approval, promotion/demotion, or downstream authority is created.

## Stop conditions

Stop if:

- source EXP is missing or invalid;
- evaluation window is ambiguous;
- artifact ID sequencing is ambiguous;
- REP creation requires schema, validator, or query-layer changes;
- OL derivation requires schema, validator, or query-layer changes;
- REC derivation requires schema, validator, or query-layer changes;
- exact-segment count movement cannot be deterministically stated;
- batching would make changed-file review too broad;
- partial failure cannot be cleanly reported;
- the package would imply H-005 change;
- the package would imply H-006 implementation before approval;
- the package would imply Path B or runtime authority;
- the package would blur expectation-source-specific conclusions;
- the package would weaken validation.

## Additional efficiency scan for Main

Main should continue looking for other areas where the project can reduce WP
count, execution time, repeated review burden, or unnecessary process overhead
without weakening bot performance, repo truth, validation, protected
boundaries, or safety.

Main has freedom to propose, design, or recommend solutions, including changes
to workflow, package structure, batching, report-back format, validation tiers,
architecture sequencing, automation helpers, evidence production, review
process, handoff structure, or operating model.

Future ideas should be classified as:

1. Safe to adopt now
2. Needs Tier 1 design package first
3. Risky / not recommended

For each idea, report:

- expected WP/time savings;
- affected project area;
- risk level;
- whether it changes validation;
- whether it touches protected paths;
- whether Main/Karl approval or a repo-truth lock is required.

If an idea is safe to adopt immediately, say so. If it requires a repo-truth
design lock or implementation WP, specify the narrowest package needed.

This scan should focus especially on areas beyond R1/R2 where the project may
still be over-splitting work or repeating effort unnecessarily.

This section is a prompt to Main and future reviewers. It is not implementation
authority for Codex.

## What is not authorized

This methodology design does not authorize REP, OL, REC, EXP, LCH, schema,
validator, query-layer, implementation, config, dependency, data, runtime,
paper/live, OMS, risk, safe mode, Path B, H-006 implementation,
paired-source reuse implementation, batched-cycle implementation, AUTO
successor work, policy/scoring/ranking/recommendation, approval,
promotion/demotion, readiness, lifecycle, or downstream authority.

## Main/Karl approval gate

R2 remains design-only after this package. R1 remains design-only after this
package. Main/Karl must re-engage after WP-S2c-21c.

No package may apply R1 or R2 until explicit approval exists in repo truth or
in a Main/Karl instruction that is then locked into repo truth.

Report-back after this package should explicitly request Main/Karl's decision
on whether to approve, modify, defer, or reject R1/R2 for H-006+.
