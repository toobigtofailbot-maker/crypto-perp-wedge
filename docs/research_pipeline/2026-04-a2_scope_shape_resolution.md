# A2 Scope-Shape Resolution Surface

## Package Metadata And Scope

- Package label: WP-12ak / WP-S2c-2.
- Package title: A2 Scope-Shape Resolution Surface.
- Package class: Tier 1 documentation-only architecture/design-decision support.
- Effective base: post-WP-12aj / post-A2 design-opening.
- Committed files: this document and `docs/project_status.md` only.

This package focuses only on the A2 scope-shape question surfaced by
WP-12aj / WP-S2c-1. It enumerates explicit scope-shape options, analyzes
trade-offs and locked-constraint interactions, may include a non-binding Side
recommendation, and prepares the next chat-level decision surface for
Karl/Main.

This package has no final selection authority. It does not authorize A2
implementation, cohort implementation, EXP scaffold authoring, Path B
execution, artifact creation, schema/validator/query-layer/runtime/protected
path changes, or policy/scoring/ranking/recommendation/promotion/readiness/
lifecycle authority.

## Context

WP-12aj / WP-S2c-1 opened the A2 design surface after the A1 runway
checkpoint. It surfaced nine unresolved A2 design categories:

- scope shape;
- cohort architecture;
- Path B architecture;
- envelope;
- floor discipline interaction;
- expectation-source symmetry;
- methodology and process;
- Tier 4 distance;
- schema versioning.

Scope shape is upstream of cohort architecture, Path B architecture, envelope,
methodology/process, and most other A2 questions. WP-S2c-2 narrows the design
surface to scope shape only.

A1 runway context remains narrow:

- `H-004 / research_oos / post_wp_5b / d2_006_gates` is floor-crossed at
  `reconciliation_count = 3`.
- `H-004 / research_oos / post_wp_5b / exp_success_criteria` is floor-crossed
  at `reconciliation_count = 3`.
- This is one-candidate expectation-source symmetry.
- It is not cross-candidate comparison, cross-pipeline-version comparison,
  aggregate-corpus inference, policy authority, paper/live readiness, or
  operational authority.

This package is documentation-only. It does not authorize implementation.

## Scope-Shape Options

### SS-A: Cohort Only

Definition: A2 second sub-stage would focus on cohort scope: multiple
candidates or candidate/segment units evaluated under Path A-equivalent
canonical evidence mechanics. There is no Path B authorization, no new EXP
scaffold authoring, no H-011 first-time inclusion, and no H-012+ registration.

Later design would make substantive:

- cohort definition;
- candidate/segment eligibility;
- non-performance selection method;
- cohort size bounds;
- evidence floor expectations;
- expectation-source symmetry requirement;
- package-count envelope.

This option would defer or make moot Path B eligibility, EXP scaffold authoring
envelope, and Path B sequencing inside this A2 scope.

Primary benefits:

- Directly addresses the largest missing A1 evidence dimension:
  cross-candidate or cross-segment breadth.
- Keeps A2 close to known Path A mechanics and existing OL v1 / REC v1
  research-OOS surfaces.
- Avoids immediate EXP scaffold complexity.

Primary risks/costs:

- Requires careful non-performance cohort selection.
- Can become package-expensive if every cohort member needs both expectation
  sources floor-crossed.
- May leave Path B architecture unresolved if Karl/Main expects it soon.

Locked-constraint interactions:

- Must preserve REC-5 per exact segment and avoid cross-segment inference for
  below-floor members.
- Must not use performance-based selection, ranking, recommendation, or
  policy framing.
- Must use existing committed EXP provenance only unless a later package
  separately authorizes otherwise.

Likely next design package if selected: cohort architecture and envelope
resolution.

### SS-B: Path B Only

Definition: A2 second sub-stage would focus on Path B design: EXP scaffold
authoring against eligible pre-existing hypotheses, if later authorized. There
is no cohort scope and no Path A continuation for multiple candidates inside
this scope unless separately authorized.

This option still does not authorize EXP scaffold execution now. Later design
must decide eligible hypotheses, EXP authoring envelope, whether H-011
slot-only can be used or remains excluded, how to avoid H-012+ registration,
and sequencing and validation boundaries.

This option would defer or make moot cohort breadth work inside this A2 scope.

Primary benefits:

- Resolves the long-deferred Path B / first EXP scaffold question directly.
- Could clarify future evidence generation mechanics for eligible existing
  hypotheses.
- Avoids conflating cohort breadth with EXP authoring design.

Primary risks/costs:

- Most implementation-adjacent option short of actual execution.
- Higher chance of accidentally implying EXP scaffold authority.
- Does not address A1's missing cross-candidate breadth.

Locked-constraint interactions:

- EXP scaffold authoring remains forbidden unless a later implementation
  package separately authorizes it.
- H-011 first-time inclusion and H-012+ registration remain forbidden unless
  separately authorized.
- Must preserve D2-005 pre-registration discipline and current schema/query
  boundaries.

Likely next design package if selected: Path B eligibility and EXP scaffold
authoring envelope resolution.

### SS-C: Cohort + Path B Parallel

Definition: A2 would include both cohort and Path B design surfaces in
parallel. Later packages would need to address how the two streams interact.

This option would make both cohort architecture and Path B architecture
substantive. It would defer neither major surface, but it would likely require
splitting work into coordinated sub-tracks before any implementation package.

Primary benefits:

- Most complete A2 design scope.
- Allows Karl/Main to reason about breadth and new EXP authoring together.
- Preserves optionality across both major unresolved A2 surfaces.

Primary risks/costs:

- Broadest option and likely highest architecture/design cost.
- Highest coordination burden.
- Greater risk of scope drift, implied downstream authority, or hidden schema
  pressure.

Locked-constraint interactions:

- Both cohort and Path B boundaries must be preserved at once.
- Any interaction between streams must not create ranking, policy,
  recommendation, H-011 inclusion, H-012+ registration, schema expansion, or
  query-layer authority by implication.
- If parallelism requires changing a locked decision, that is a stop/decision
  trigger, not a WP-S2c-2 resolution.

Likely next design package if selected: parallel-track decomposition, deciding
whether cohort and Path B become separate sub-tracks before deeper design.

### SS-D: Cohort Then Path B

Definition: A2 would first resolve and, if later authorized, execute cohort
design scope, with Path B deferred until the cohort sequence completes or
reaches a checkpoint.

This option makes cohort architecture substantive first. It preserves Path B
as a staged target, but defers Path B eligibility and EXP scaffold authoring
details until after cohort-first work.

Primary benefits:

- Addresses A1's missing cross-candidate breadth first.
- Keeps immediate A2 design bounded and closer to existing Path A mechanics.
- Avoids immediately opening EXP scaffold authoring complexity.
- Preserves Path B as a later staged follow-on rather than discarding it.

Primary risks/costs:

- Path B remains unresolved during the first stage.
- Cohort work may consume multiple packages before Path B can reopen.
- Requires a clear checkpoint rule to prevent indefinite deferral.

Locked-constraint interactions:

- Cohort-first work must preserve non-performance selection and REC-5 floor
  discipline.
- Path B remains unauthorized until a later separate package.
- No EXP scaffold, H-011 first-time inclusion, H-012+ registration, or
  implementation authority follows automatically.

Likely next design package if selected: cohort architecture first-stage
resolution with Path B recorded as staged/deferred.

### SS-E: Path B Then Cohort

Definition: A2 would first resolve and, if later authorized, execute Path B
design scope, with cohort deferred until the Path B sequence completes or
reaches a checkpoint.

This option makes Path B architecture substantive first. It preserves cohort
as a later target, but defers cohort breadth, cohort selection, and
cross-candidate envelope questions.

Primary benefits:

- Prioritizes EXP scaffold architecture before evidence breadth.
- Clarifies how future new plan authoring can occur within locked evidence
  discipline.
- Could unblock a later cohort design if that cohort depends on new EXP
  scaffolds.

Primary risks/costs:

- Defers the missing cross-candidate breadth exposed by A1.
- Opens the most implementation-adjacent design surface first.
- Higher risk of accidental EXP scaffold authorization language.

Locked-constraint interactions:

- Path B remains design-only until a later implementation package separately
  authorizes EXP scaffold authoring.
- H-011 first-time inclusion and H-012+ registration remain blocked.
- Must not weaken D2-005, OL v1, REC v1, schema-versioning, or query-layer
  locks.

Likely next design package if selected: Path B architecture first-stage
resolution.

### SS-F: Both Deferred

Definition: A2 design pauses or remains open without selecting cohort or Path
B scope. Karl/Main reconsiders direction later.

This option makes neither cohort nor Path B substantive now. It defers cohort
architecture, Path B architecture, envelope, implementation sequencing, and
downstream A2 package structure.

Primary benefits:

- Valid if trade-offs remain unclear.
- Lowest immediate scope and implementation risk.
- Avoids premature commitment to either major surface.

Primary risks/costs:

- Produces no immediate architecture progress.
- Leaves A2 open after WP-12aj and WP-S2c-2.
- May require another direction-setting package before meaningful design can
  resume.

Locked-constraint interactions:

- Easiest option to keep within current locked constraints because it pauses
  substantive design selection.
- Must still avoid implying deprecation of A2, Path B, or cohort work unless
  Karl/Main explicitly chooses that later.

Likely next design package if selected: pause/reactivation conditions or
redirection to another track.

## Locked-Constraint Interaction By Option

SS-A through SS-F can be discussed within current locked constraints as design
options. Any later implementation package requires separate authorization.

All options must preserve:

- Tier 4 absolute boundaries.
- Protected paths.
- No runtime, paper-live, OMS, risk, safe-mode, execution, exchange, broker,
  or order behavior.
- No policy, promotion, demotion, fast-track, readiness, ranking,
  recommendation, evidence-quality scoring, approval, or lifecycle authority.
- No cross-segment inference under the REC-5 floor.
- No performance-based selection.
- No H-012+ registration.
- No H-011 first-time inclusion.
- No AUTO reactivation.
- No schema/validator/query-layer changes by default.
- OL v1 `research_oos` scope and REC v1 expectation-source constraints.
- EXP scaffold authoring remains forbidden unless Path B implementation is
  separately authorized later.

Constraint posture by option:

- SS-A is closest to existing Path A mechanics, but must not convert cohort
  breadth into ranking, scoring, or below-floor inference.
- SS-B is narrow but implementation-adjacent; it must keep EXP scaffold
  authoring design separate from EXP scaffold execution.
- SS-C carries the most scope pressure because it must preserve cohort and
  Path B constraints simultaneously.
- SS-D keeps immediate work close to cohort breadth while preserving Path B as
  deferred and unauthorized.
- SS-E prioritizes Path B design and therefore needs especially explicit EXP
  scaffold non-authority language.
- SS-F preserves constraints by pausing, but leaves A2 unresolved.

If any option later appears to require changing a locked decision, that is a
stop/decision trigger for Karl/Main. WP-S2c-2 does not resolve locked-decision
modification.

## Side Recommendation

Recommend SS-D: Cohort then Path B.

Rationale:

- A1 produced single-candidate expectation-source symmetry, not
  cross-candidate breadth.
- Cohort-first addresses the most important missing evidence dimension:
  cross-candidate breadth.
- Deferring Path B avoids immediately opening EXP scaffold authoring
  complexity.
- Path B remains preserved as a staged follow-on rather than discarded.
- SS-D keeps A2 bounded while still moving beyond the H-004-only evidence
  base.
- It avoids the high complexity of SS-C parallel work and the
  implementation-adjacent complexity of SS-B / SS-E Path-B-first.
- It is more productive than SS-F pause and more complete than SS-A if
  Karl/Main wants Path B preserved for later.

This recommendation is non-binding. Karl/Main resolves scope shape after
WP-S2c-2 merges. This package does not select SS-D.

## Downstream Design Implications

If SS-A is selected, the next design package likely resolves cohort
architecture and envelope: cohort definition, eligible candidate/segment units,
non-performance selection, cohort size, floor expectations, and package-count
bounds.

If SS-B is selected, the next design package likely resolves Path B
eligibility and EXP scaffold authoring envelope: eligible hypotheses, whether
H-011 remains excluded, sequencing, validation boundaries, and avoidance of
H-012+ registration.

If SS-C is selected, the next design package likely must choose whether to
split cohort and Path B into separate sub-tracks before deeper design.

If SS-D is selected, the next design package likely resolves cohort
architecture first, while recording Path B as staged/deferred and still
unauthorized.

If SS-E is selected, the next design package likely resolves Path B
architecture first, while recording cohort as staged/deferred.

If SS-F is selected, the next package likely records pause/reactivation
conditions or redirects to another track.

## Explicit Non-Claims

WP-S2c-2 does not:

- select scope shape;
- authorize cohort or Path B implementation;
- authorize EXP scaffold authoring;
- author cohorts, EXPs, REPs, OLs, RECs, LCHs, or registry artifacts;
- modify existing merged artifacts or decision docs;
- pre-commit envelope, methodology, cohort architecture, Path B architecture,
  schema versioning, or any downstream A2 design question;
- introduce schema versioning, add validators, expose central query-layer
  views, or add CLI surfaces;
- reactivate AUTO;
- unlock cross-segment inference under REC-5 floor;
- authorize H-012+ candidate registration;
- authorize H-011 first-time inclusion;
- authorize policy/scoring/ranking/recommendation/promotion/readiness/
  lifecycle authority;
- authorize an automatic follow-on package.

## Next Chat-Level Decision Surface

After WP-S2c-2 merges, Karl/Main must decide:

1. Select scope shape: SS-A, SS-B, SS-C, SS-D, SS-E, SS-F, or modify/add/remove
   options.
2. Decide whether the next A2 design package should be comprehensive for the
   selected scope, sequential, hybrid, or paused.
3. Decide whether to authorize the within-segment consumer brief for the newly
   floor-crossed `exp_success_criteria` segment, depending on WP-S2b-6
   clarification.
4. Confirm that no implementation package follows automatically from
   WP-S2c-2.

## WP-S2b-6 Clarification Note

Main asked Side to verify at report-back whether WP-S2b-6's within-segment
consumer brief covered:

- `d2_006_gates` only;
- `exp_success_criteria` only;
- both;
- neither / not applicable.

This clarification is non-blocking for WP-S2c-2. This package does not draft
an Option 4 consumer brief.

Repo-truth discovery during WP-S2c-2 found WP-12ah / S2b-6 was an OL-only
append package that added `OL-0015` for the
`exp_success_criteria` segment. The committed within-segment consumer brief
identified by Stage 2 first-sub-stage docs is WP-11a over
`H-004 / research_oos / post_wp_5b / d2_006_gates` only. No committed
WP-S2b-6 consumer brief was identified.

## Standing Boundary Statement

This document is a decision-support surface only. Research/workbench artifacts
have no execution authority unless explicitly promoted through a later
approved path. Runtime execution, OMS, reconciliation, risk caps, bounded
overlay semantics, safe mode, configs, and live-trading paths remain untouched.
