# A2 Architecture-Design Opening

## Package Metadata And Scope

- Package label: WP-12aj / WP-S2c-1.
- Package title: A2 Architecture-Design Opening.
- Package class: Tier 1 documentation-only architecture/design opening.
- Effective base: post-WP-12ai / post-A1 runway checkpoint.
- Committed files: this document and `docs/project_status.md` only.

This package opens the A2 design surface, summarizes locked constraints,
surfaces unresolved design questions, and prepares the next chat-level decision
surface for Karl/Main.

This package has no implementation authority. It does not authorize A2
implementation, cohort implementation, EXP scaffold authoring, Path B
execution, artifact creation, schema/validator/query-layer/runtime/protected
path changes, policy/scoring/ranking/recommendation, approval,
promotion/demotion, readiness, lifecycle transition, or downstream authority.

## Context

A1 runway completed cleanly after WP-12ai / S2b-7. Two exact H-004 segments are
now floor-crossed at `reconciliation_count = 3`:

- `H-004 / research_oos / post_wp_5b / d2_006_gates`
- `H-004 / research_oos / post_wp_5b / exp_success_criteria`

Both floor-crossed segments share the same candidate, outcome kind, and
pipeline version:

```text
H-004 / research_oos / post_wp_5b
```

This provides expectation-source symmetry for one candidate. It does not
provide cross-candidate comparison, cross-pipeline-version comparison,
aggregate-corpus inference, or operational authority.

A2 remained the queued preferred reassessment target from Karl's A1-with-A2
preserved framing. WP-S2b-8 selected Option 1: A2 architecture design.
WP-S2c-1 is design-opening only.

## Locked Constraints A2 Must Honor

Phase 9 decisions remain locked:

- Decision 1: lifecycle state vocabulary is additive and version-governed.
- Decision 2: lifecycle transitions follow the permitted transition graph.
- Decision 3: lifecycle changes use LCH artifacts, distinct from DCH and REL.
- Decision 4: outcome-ledger v1 granularity is one record per candidate and
  evaluation window.
- Decision 5: REC artifacts keep expected-vs-realized reconciliation auditable.
- Decision 6: approval is human-only; agents, helpers, validators, queries, and
  advisory artifacts do not approve promotion, demotion, recovery, live entry,
  or deployment.
- Decision 7: retrospective backfill remains package-scoped and auditable.
- Decision 8: advisory links are one-way lineage only and add no execution,
  ranking, approval, or runtime authority.
- Decision 9: tiered promotion evidence policy remains future policy work and
  does not permit ad hoc runtime tweaking or automatic promotion.
- Decision 10: schema evolution requires explicit versioned work.

OL constraints remain locked:

- OL v1 supports `research_oos` only.
- `pipeline_version` disclosure is required.
- Consumer inference needs `n >= 3` per
  `(candidate, outcome_kind, pipeline_version)`.
- OLs create no operational, policy, scoring, ranking, promotion, demotion, or
  paper/live authority.
- This package creates no OL schema expansion.

REC constraints remain locked:

- REC v1 reconciles `research_oos` only.
- `exp_success_criteria` and `d2_006_gates` are separate expectation sources.
- Consumer inference needs `n >= 3` per `(candidate, outcome_kind,
  pipeline_version, expectation_source_type)`.
- Expectation sources do not combine by default.
- D2 fallback for EXP-success RECs is not available unless separately
  authorized.
- RECs create no operational, policy, scoring, ranking, promotion, demotion, or
  paper/live authority.

Stage 2 constraints remain locked:

- The first sub-stage proceeded as Path A only.
- The first sub-stage was single-segment, used existing `EXP-0011`, and created
  no EXP scaffold, cohort, Path B, new candidate, H-011 inclusion, or H-012+
  registration.
- Path B and first EXP scaffold work require a future Stage 2 second-sub-stage
  authorization decision.
- Second-sub-stage scope was deferred to its own authorization.
- Stage 2 validation discipline requires exact scope, integrity health,
  changed-file checks, protected-boundary preservation, and non-performance
  selection discipline.
- No inherited authorization exists for second-sub-stage implementation.

PC / PFC / PCB locks remain active framing:

- PC-1 through PC-4 prioritized one D2 floor crossing, required later
  chat-level direction after crossing, and preserved forbidden scopes.
- PFC-1 through PFC-4 authorized one descriptive consumer brief over the crossed
  D2 segment only, preserved cross-segment boundaries, and required fresh
  direction afterward.
- PCB-1 through PCB-4 authorized the Stage 2 first-sub-stage stability lock,
  preserved A2 as deferred, and required explicit direction before further
  Stage 2 work.
- Karl's A1-with-A2-preserved framing allowed A1 safety/evidence work before A2
  reassessment; it did not authorize A2 implementation.
- A2 remains design-only unless a later package separately authorizes
  implementation.

WP-12a operating model carries forward:

- Repo truth wins over memory, handoffs, summaries, and assumptions.
- Refreshed-main preflight is mandatory.
- Narrow package scope controls execution.
- Stop triggers require report-back.
- Main/Karl re-engagement is required at checkpoints and direction decisions.

Tier 4 and protected-path boundaries are absolute:

- No runtime, paper/live, OMS, risk, safe-mode, kill-switch, execution,
  exchange, broker, or order behavior.
- No D2-008 overlay bounds or hard risk cap changes.
- No protected-path contact.

Authority locks remain in force. A2 design must not create policy, promotion,
demotion, fast-track, readiness, ranking, recommendation, evidence-quality
scoring, approval, lifecycle transition authority beyond locked OL/REC
mechanics, H-012+ registration, H-011 first-time inclusion, cross-segment
inference under the REC-5 floor, or performance-based selection.

Canonical-corpus locks remain in force. A2 design creates no schema authority,
`tools.registry` validator additions, central query-layer view exposure for new
artifact families, or modification of merged Phase 9, Stage 1, Stage 2, WP-10,
WP-11, or WP-12 artifacts.

Operations restrictions remain in force. A2 design creates no scheduler,
daemon, queue, watcher, trigger, dashboard, agent, Monte Carlo engine, or
robustness engine.

Evidence-bridge and AUTO restrictions remain in force. A2 design creates no
bridge from AUTO outputs to canonical evidence. AUTO remains paused at WP-12aa.
No AUTO successor is authorized here.

Config and dependency restrictions remain in force. A2 design creates no
`configs/`, dependency, environment, or data changes.

## Unresolved A2 Design Questions

### Scope Shape

- Is A2 cohort-only, Path B-only, cohort plus Path B, staged
  cohort-then-Path-B, staged Path-B-then-cohort, or both deferred?
- Is A2 a design sequence, a later implementation runway, or both in phases?
- What is the smallest useful A2 design scope?

### Cohort Architecture

If cohort enters A2:

- What counts as a cohort?
- How are candidates selected without performance-based ranking?
- How do locked WP-10j-like non-performance selection rules extend from one
  segment to a cohort?
- What are minimum, maximum, and default cohort sizes?
- Does each cohort member need both expectation sources floor-crossed, or is
  one source enough for breadth?
- How does REC-5 floor discipline apply across cohort members?
- How are below-floor cohort members represented without implying cross-segment
  inference?

### Path B Architecture

If Path B enters A2:

- What exactly counts as Path B in the Stage 2 second sub-stage?
- Which hypotheses are eligible?
- How does Path B selection differ from Path A segment selection?
- What is the EXP authoring envelope: one EXP, multiple EXPs, sequential,
  parallel, or gated?
- How does Path B interact with H-011 being slot-only?
- How does Path B avoid H-012+ registration unless separately authorized?
- How does Path B avoid turning design into EXP scaffold execution?

### Envelope

- What is the package-count envelope for A2 design?
- What would be the later implementation envelope if authorized?
- Is A2 fixed-size like the first sub-stage, or open-ended?
- What stop triggers end A2 design or implementation?
- What evidence or design criteria determine whether A2 continues or pauses?

### Floor Discipline Interaction

- How should A2 use the H-004 evidence now that both H-004 post-WP-5b
  expectation sources are floor-crossed?
- Should A2 prioritize additional candidates, additional pipeline versions, or
  deeper H-004 analysis?
- Does A2 seek cross-candidate breadth or expectation-source symmetry first?
- How does A2 prevent cross-segment inference from below-floor segments?
- How does A2 treat new segments that start at `n = 0` or below floor?

### Expectation-Source Symmetry

- Should A2 require both `exp_success_criteria` and `d2_006_gates`
  floor-crossing for each cohort member?
- Is one expectation source enough for breadth?
- If symmetry is desirable, what is the package-cost implication?
- How should A2 handle cases where one expectation source is cleanly available
  but the other is blocked?

### Methodology And Process

- Should A2 mirror Stage 2 first-sub-stage sequence patterns?
- Should A2 mirror the A1 REP -> OL -> REC runway pattern?
- Should A2 use a design-first sequence before implementation?
- How does A2 preserve D2-005 pre-registration discipline?
- What must be decided before any cohort or Path B implementation package is
  safe to draft?

### Tier 4 Distance

- How does A2 remain clearly distant from runtime, paper/live, OMS, risk, and
  execution?
- How does A2 avoid implying paper/live readiness while producing richer
  canonical evidence?
- What language should future A2 documents use to keep evidence production
  separate from operational authorization?

### Schema Versioning

- Can A2 work within existing OL v1 and REC v1 schemas?
- What signs would indicate A2 requires OL v2 or REC v2?
- If schema versioning is needed, what separate architecture decision would be
  required?
- How does A2 avoid silently smuggling schema expansion into implementation?

## What WP-S2c-1 Explicitly Does Not Decide

WP-S2c-1 does not select cohort size, candidate set, Path A vs Path B vs both,
or package-count envelope. It does not authorize A2 implementation, author
cohorts, EXPs, REPs, OLs, RECs, LCHs, or registry artifacts, modify existing
merged artifacts or decision docs, pre-commit answers to unresolved A2
questions, introduce schema versioning, add validators, expose central
query-layer views, add CLI surfaces, reactivate AUTO, unlock cross-segment
inference under REC-5 floor, authorize H-012+ candidate registration, authorize
H-011 first-time inclusion, or authorize policy/scoring/ranking/recommendation,
promotion/demotion, readiness, lifecycle transition, approval, or downstream
authority.

## Next Chat-Level Decision Surface

After WP-S2c-1 merges, Karl/Main should decide:

1. Proceed with further A2 design or pause A2.
2. If further design proceeds, which unresolved A2 question should be resolved
   first.
3. Whether design-package structure should be one comprehensive A2 architecture
   decision package, a sequence of smaller design-resolution packages, or a
   hybrid.
4. Whether a consumer brief for the newly floor-crossed `exp_success_criteria`
   segment should be authorized separately, depending on WP-S2b-6
   clarification.
5. Whether A2 design should prioritize cohort questions, Path B questions,
   envelope questions, or schema-v1 feasibility questions.
6. Confirm that no implementation package follows automatically from
   WP-S2c-1.

## WP-S2b-6 Clarification Note

Main asked Side to confirm at report-back whether WP-S2b-6's within-segment
consumer brief covered `d2_006_gates` only, `exp_success_criteria` only, both,
or neither / not applicable.

This clarification is non-blocking for WP-S2c-1. This package does not draft an
Option 2 consumer brief and does not resolve the clarification by guessing.

## Standing Non-Claims

- No Tier 4 contact.
- No protected-path contact.
- No canonical-corpus locks broken.
- No AUTO contact.
- No policy/scoring/ranking/recommendation authority.
- No operational consequence.
- No A2 implementation authority.
- No downstream package authority.
