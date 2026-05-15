# Post-Floor-Crossing Stage 2 Direction Decision (WP-10z)

## Package metadata

- Package label: WP-10z.
- Package title: Post-Floor-Crossing Stage 2 Direction Decision.
- Package class: documentation-only direction-setting decision package.
- Effective base: refreshed `main` after merged WP-10y.
- Created artifact: this decision document only.
- Modified status surface: `docs/project_status.md` only.

WP-10z creates no research evidence artifact, implementation artifact,
consumer brief, schema, validator, query-layer change, test change, runtime
behavior, config change, dependency change, data change, or protected-path
change.

## Context

WP-10y crossed REC-5 for the first time in project history. The crossed exact
segment is:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

The three D2 REC observations for that exact segment are:

- `REC-0022`
- `REC-0023`
- `REC-0024`

REC-5 remains `n >= 3` per exact
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`
segment. The REC-5 crossing applies only to
`H-004 / research_oos / post_wp_5b / d2_006_gates`; all other exact REC-5
segments remain below floor under current repo truth.

WP-10v PC-3 explicitly required chat-level direction-setting once REC-5
crossed for the selected exact segment before any further Stage 2 work. WP-10z
discharges that PC-3 deferral by locking PFC-1 through PFC-4. WP-10z does not
implement the consumer brief.

This document does not characterize the floor-crossed segment's analytic
content. That work belongs to the later consumer brief if separately scoped and
validated.

## Strategic question

What is the immediate next package after WP-10y, given that REC-5 has crossed
for one exact segment and all other segments remain below floor?

Legitimate options include:

- descriptive consumer brief over the crossed segment only;
- additional Path A floor-crossing for another segment;
- Stage 2 second-sub-stage authorization;
- Path B / first EXP scaffold authorization;
- stop / hold at the first REC-5 crossing.

WP-10z locks the selected direction through PFC-1 through PFC-4 below.

## PFC-1 - Immediate next package

Decision: the immediate next package is a descriptive consumer brief over
`H-004 / research_oos / post_wp_5b / d2_006_gates` (per WP-10v PC-3 deferral,
WP-10y / REC-0024 floor-crossing state, and REC-0022, REC-0023, and REC-0024
segment fields).

The brief is scoped strictly to that exact segment and to descriptive
observations of its three committed REC observations:

- `REC-0022`
- `REC-0023`
- `REC-0024`

Rationale:

- The consumer brief is the natural first analytic output of a floor crossing.
- REC-5 existed to gate cross-window inference within a segment until floor
  was crossed.
- Single-segment scope is narrow.
- The brief creates a worked example of a floor-crossed-segment analytic
  output.
- The brief does not authorize broader scope.

Non-claims:

- PFC-1 does not draft or implement the brief.
- PFC-1 does not commit to consumer briefs for other segments.
- PFC-1 does not commit to a specific timeline.
- PFC-1 does not pre-commit post-consumer-brief direction.

## PFC-2 - Consumer-brief scope and inference boundaries

Decision: the future consumer brief is scoped strictly to
`H-004 / research_oos / post_wp_5b / d2_006_gates` (per WP-10p Stage 2
authorization, WP-10v PC-3 deferral, WP-10y / REC-0024 floor-crossing state,
and REC-0022, REC-0023, and REC-0024 segment fields).

The brief may state within-segment cross-observation patterns for this exact
segment without marking each such within-segment pattern as
`INSUFFICIENT_EVIDENCE`.

Permitted content:

- Per-observation factual content for `REC-0022`, `REC-0023`, and `REC-0024`,
  including comparison verdicts, expectation source, OL evaluation windows,
  per-metric expected and realized values, and derivation-record content.
- Three-observation factual content for the exact segment, including verdict
  distribution, per-metric patterns across the three observations, and timing
  characteristics.
- Descriptive within-segment cross-observation observations that do not extend
  beyond the exact segment.

Forbidden content:

- Cross-segment inference.
- Claims about H-004 generally.
- Claims about the H-004 pre-WP-5b segment.
- Claims about H-004 post-WP-5b `exp_success_criteria`.
- Predictive inference.
- Comparative inference involving non-floor-crossed segments.
- Policy implication.
- Ranking, scoring, recommendation, promotion, demotion, paper-live, runtime,
  lifecycle, or operational framing.

`INSUFFICIENT_EVIDENCE` marker usage:

- Required for claims that would cross the forbidden boundaries.
- Not required for within-segment cross-observation patterns inside the crossed
  exact segment.

WP-10z does not draft the brief's specific conclusions.

## PFC-3 - Post-consumer-brief disposition

Decision: once the consumer brief commits, another explicit chat-level
direction-setting decision is required before further Stage 2 work. No
automatic progression is authorized (per WP-10v PC-3 deferral and WP-10y /
REC-0024 floor-crossing state).

Informational possibilities after the consumer brief, not pre-committed:

- floor crossing for additional segments;
- Path B authorization;
- Stage 2 second-sub-stage authorization;
- stop / hold at the first consumer brief;
- stability lock declaring the first floor crossing plus first consumer brief a
  coherent committed work-set.

Explicit non-authorizations:

- no policy work;
- no scoring/ranking/recommendation;
- no paper/live/runtime;
- no lifecycle transition work;
- no cross-segment inference involving below-floor segments;
- no post-consumer-brief direction.

## PFC-4 - Forbidden scope preservation and additions

Decision: all forbidden scopes from WP-10p, WP-10u, WP-10v, and earlier locks
remain preserved (per WP-10p Stage 2 authorization, WP-10u checkpoint lock,
WP-10v PC-4, and WP-10y / REC-0024 floor-crossing state).

Preserved forbidden scopes include:

- promotion/demotion policy implementation or schema;
- ranking/recommendation implementation or schema;
- evidence-quality scoring implementation or schema;
- paper extension implementation or schema;
- live extension implementation or schema;
- forward-flow lifecycle transitions citing the crossed segment as evidence for
  operationally consequential states;
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
- Stage 2 second-sub-stage authorization.

Post-floor-crossing additions:

1. Cross-segment inference remains forbidden even though one segment has
   crossed floor.
2. Policy/ranking/scoring framing remains forbidden even for the crossed
   segment.
3. Forward-flow lifecycle transitions citing the crossed segment remain
   forbidden.

## Implementation sequencing

The next implementation package will be a descriptive consumer brief over:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

The likely label may be WP-11a or another label assigned by Main 3.0 later.
WP-10z drafts no implementation package. Each subsequent package requires its
own chat-level direction-setting, scope, preflight, validation, and review. No
automatic progression is authorized after the consumer brief, and
post-consumer-brief direction is deferred.

## Validation expectations for the next implementation package

The next implementation package is expected to validate that:

- applicable schema validators pass;
- all discovered `v_integrity_*` views return `[]`;
- targeted pytest passes;
- full pytest passes;
- `git diff --check` passes;
- changed-file set matches the package scope;
- brief scope remains exactly
  `H-004 / research_oos / post_wp_5b / d2_006_gates`;
- brief respects PFC-2 permitted and forbidden content;
- no policy/scoring/ranking/recommendation/paper-live/runtime framing is
  introduced;
- no Path B, cohort, new candidate, or lifecycle transition is authorized;
- no protected-path changes are made.

## Non-claims

WP-10z creates no:

- consumer brief;
- WP-11a or successor implementation package;
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
- methodology artifact separate from this WP-10z decision document;
- schema;
- validator;
- query-layer change;
- test change;
- Path B;
- cohort;
- H-011 inclusion;
- H-012/new candidate;
- policy;
- scoring;
- ranking/recommendation;
- paper-live;
- runtime;
- post-consumer-brief direction.
