# Post-Consumer-Brief Stage 2 Direction Decision (WP-11b)

## Package metadata

- Package label: WP-11b.
- Package title: Post-Consumer-Brief Stage 2 Direction Decision.
- Package class: documentation-only direction-setting decision package.
- Effective base: refreshed `main` after merged WP-11a.
- Created artifact: this decision document only.
- Modified status surface: `docs/project_status.md` only.

WP-11b creates no research evidence artifact, implementation artifact,
stability-lock document, consumer brief, schema, validator, query-layer change,
test change, runtime behavior, config change, dependency change, data change, or
protected-path change.

## Context

WP-11a committed the first descriptive consumer brief over a REC-5
floor-crossed exact segment (per WP-11a consumer brief completion). The segment
is:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

The source REC observations are:

- `REC-0022`
- `REC-0023`
- `REC-0024`

WP-11a used within-segment non-`INSUFFICIENT_EVIDENCE` analytic language under
WP-10z PFC-2. WP-11a did not authorize further Stage 2 work. WP-10z PFC-3
explicitly required chat-level direction-setting before any further Stage 2
work after the consumer brief (per WP-10z PFC-3 deferral).

WP-11b discharges that PFC-3 deferral by locking PCB-1 through PCB-4 (per
PCB-1 through PCB-4 chat-level confirmation). WP-11b does not draft or
implement the stability lock.

## Strategic question

What is the immediate next package after WP-11a, given that the first
floor-crossed segment consumer brief has committed and WP-10z PFC-3 requires a
fresh direction decision?

Legitimate options include:

- Stage 2 first-sub-stage stability lock;
- additional Path A floor crossing for another exact segment;
- Stage 2 second-sub-stage authorization;
- Path B / first EXP scaffold authorization;
- stop / hold after the first consumer brief.

WP-11b locks the selected direction through PCB-1 through PCB-4 below.

## PCB-1 - Immediate next package

Decision: the immediate next package after WP-11b is a Stage 2 first-sub-stage
stability lock (per WP-10z PFC-3 deferral, WP-11a consumer brief completion,
and PCB-1 through PCB-4 chat-level confirmation).

That future stability lock declares the WP-10q through WP-11a sequence as
Stage 2 first sub-stage complete-as-executed. Its structural role mirrors
WP-10o's Stage 1 checkpoint/stability-lock role (per WP-10q through WP-11a
Stage 2 first-sub-stage sequence).

Rationale:

- WP-10q through WP-11a form a coherent work-set: segment selection
  methodology, Path A evidence cycles, REC-5 floor crossing, and first
  descriptive consumer brief.
- The sequence exercised selection, evidence generation, floor crossing, and
  analytic-output mechanics against real content.
- Closing the sub-stage before opening a broader one preserves the decision
  hygiene used throughout Phase 10.
- The stability-lock package is lower-risk than scope expansion because it is
  documentation-only.

Non-claims:

- PCB-1 does not draft or implement the stability lock.
- PCB-1 does not authorize Stage 2 second-sub-stage.
- PCB-1 does not authorize additional floor crossing.
- PCB-1 does not authorize cohort, Path B, new candidate, or
  policy/scoring/ranking work.

## PCB-2 - Stability lock scope

Decision: the future stability lock scope covers WP-10q through WP-11a as
Stage 2 first sub-stage complete-as-executed (per WP-10q through WP-11a Stage 2
first-sub-stage sequence and PCB-1 through PCB-4 chat-level confirmation).
WP-11b authorizes only the stability-lock package class and scope, not the
stability-lock document itself.

At scope level, the future stability-lock package should cover:

- Stage 2 first-sub-stage completion summary.
- Constituent packages: WP-10q segment selection application; WP-10r / WP-10s /
  WP-10t first Path A evidence cycle; WP-10w / WP-10x / WP-10y subsequent Path
  A evidence cycle work culminating in REC-5 floor crossing; WP-11a first
  floor-crossed segment consumer brief.
- Constraint posture during Stage 2 first sub-stage: single-segment scope, Path
  A only, no Path B, no cohort, no EXP scaffold, no policy/ranking/scoring/
  recommendation, no paper-live/runtime, and no protected-path changes.
- REC-5 floor status after Stage 2 first sub-stage: one exact segment crossed
  floor; all other exact segments remain below floor unless refreshed repo
  truth says otherwise; floor crossing remains segment-specific.
- WP-11a consumer brief output status: first descriptive consumer brief
  committed, within-segment analytic content allowed under PFC-2, and no
  cross-segment inference unlocked.
- Stage 2 second-sub-stage transition prerequisites to be decided later.
- Stability statement: Stage 2 first-sub-stage mechanics, decisions, and
  outputs are locked as complete-as-executed; additive evolution must occur via
  new packages; no retroactive modification to WP-10q through WP-11a content
  unless a committed gap requires backward-compatible patching.
- Explicit non-claims: no Stage 2 second-sub-stage authorization; no additional
  segment selection; no resource commitment; no policy/scoring/ranking/
  recommendation/paper-live/runtime authority; no deprecation of any Stage 2
  first-sub-stage artifact.

WP-11b does not write the actual stability-lock content beyond this scope
authorization. The future stability-lock implementation package authors its
own document.

## PCB-3 - Post-stability-lock disposition

Decision: after the stability lock commits, another explicit chat-level
direction-setting decision is required before any further Stage 2 work. No
automatic progression is authorized (per WP-10z PFC-3 deferral and PCB-1
through PCB-4 chat-level confirmation).

Specifically deferred:

- whether Stage 2 second-sub-stage proceeds;
- whether additional Path A floor crossing for another segment becomes next
  priority;
- whether Path B authorization becomes next direction;
- whether cohort expansion becomes next direction;
- whether stop / hold becomes the next direction;
- whether any broader Stage 2 stability-lock concept is needed later.

WP-11b does not pre-commit any of these.

## PCB-4 - Forbidden scope preservation and additions

Decision: all forbidden scopes from prior tranches remain preserved (per
WP-10p Stage 2 authorization, WP-10u checkpoint lock, WP-10z PFC-4, WP-11a
consumer brief completion, and PCB-1 through PCB-4 chat-level confirmation).

Preserved forbidden scopes include:

- promotion/demotion policy implementation or schema;
- ranking/recommendation implementation or schema;
- evidence-quality scoring implementation or schema;
- paper extension implementation or schema;
- live extension implementation or schema;
- forward-flow lifecycle transitions citing the floor-crossed segment's REC
  content or consumer brief content as evidence for operationally consequential
  transitions;
- operationally consequential lifecycle transitions;
- runtime, OMS, risk, safe-mode, execution, deployment;
- configs and dependencies;
- modifications to `lib/`, `src/`, `configs/`, `.claude/`, `data/`,
  `docs/data_catalog.md`, `docs/architecture/LONG_TERM_SCOPE.md`, or
  `docs/onboarding/PHASE2_BASELINE.md`;
- schema changes;
- validator changes;
- query-layer changes;
- test changes;
- existing committed instance changes;
- performance-based candidate selection;
- synthetic evidence;
- H-012 or any new candidate;
- H-011 inclusion;
- cross-segment inference under REC-5 floor for non-crossed segments;
- EXP scaffolds;
- Path B authorization;
- cohort authorization;
- Stage 2 second-sub-stage authorization;
- Phase 9 / Phase 10 decision record modification unless explicitly authorized
  later.

Post-consumer-brief additions:

1. WP-11a consumer brief content does not retroactively unlock cross-segment
   inference or aggregate-corpus inference.
2. The future Stage 2 first-sub-stage stability lock does not retroactively
   unlock policy, ranking, or scoring framing for the floor-crossed segment.

## Implementation sequencing

The next implementation package will be the Stage 2 first-sub-stage stability
lock. The likely label may be WP-11c or another label assigned by Main 3.0
later.

WP-11b drafts no implementation package. Each subsequent package requires its
own scope, preflight, validation, and review. No automatic progression is
authorized after the stability lock, and post-stability-lock direction is
deferred.

## Validation expectations for the next implementation package

The next implementation package is expected to validate that:

- applicable schema validators pass;
- all discovered `v_integrity_*` views return `[]`;
- targeted pytest passes;
- full pytest passes;
- `git diff --check` passes;
- changed-file set matches the package scope;
- stability-lock scope remains within WP-10q through WP-11a;
- no additional floor crossing is authorized;
- no Path B, cohort, new candidate, or Stage 2 second-sub-stage authorization
  is introduced;
- no policy/scoring/ranking/recommendation/paper-live/runtime/lifecycle
  transition framing is introduced;
- no protected-path changes are made.

## Non-claims

WP-11b creates no:

- stability-lock document;
- WP-11c or successor implementation package;
- consumer brief;
- query directory;
- output directory;
- helper;
- research evidence artifact;
- implementation artifact;
- EXP;
- REP;
- OL;
- REC;
- LCH;
- registry artifact;
- methodology artifact separate from this WP-11b decision document;
- schema;
- validator;
- query-layer change;
- test change;
- Path B;
- cohort;
- H-011 inclusion;
- H-012/new candidate;
- additional floor crossing;
- Stage 2 second-sub-stage authorization;
- policy;
- scoring;
- ranking/recommendation;
- paper-live;
- runtime;
- lifecycle transition;
- post-stability-lock direction.
