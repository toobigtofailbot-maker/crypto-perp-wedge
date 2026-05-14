# Post-Checkpoint Stage 2 Direction Decision (WP-10v)

## Package metadata

- Package label: WP-10v.
- Package title: Post-Checkpoint Stage 2 Direction Decision.
- Package class: documentation-only direction-setting decision package.
- Effective base: refreshed `main` after merged WP-10u.
- Created artifact: this decision document only.
- Modified status surface: `docs/project_status.md` only.

WP-10v creates no research evidence artifact, implementation artifact, schema,
validator, query-layer change, test change, runtime behavior, config change,
dependency change, data change, or protected-path change.

## Context

WP-10u closed Stage 2 first sub-stage as a checkpoint and stopped before any
further Stage 2 work (per WP-10u checkpoint lock). The first sub-stage executed
exactly one Path A evidence cycle:

```text
existing EXP-0011 -> REP-0012 -> OL-0012 -> REC-0023
```

The selected exact segment remains:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

The REC-5 floor remains `n >= 3` per exact
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`
segment (per WP-10u checkpoint lock). Current repo truth records 2 REC
observations for the selected exact segment: `REC-0022` and `REC-0023` (per
REC-0022 and REC-0023 segment fields). No segment has crossed the REC-5 floor,
and all other exact segments remain below floor.

WP-10v decides direction only. It does not implement the next cycle.

## Strategic question

How does Stage 2 proceed after the WP-10u first-sub-stage checkpoint?

Legitimate options after the checkpoint include:

- continue Path A on the same segment to cross the REC-5 floor;
- continue Path A on a different segment for breadth;
- cross into Stage 2 second sub-stage or small cohort work;
- cross into Path B or first EXP scaffold work;
- stop or hold at the checkpoint.

WP-10v locks the selected direction through PC-1 through PC-4 below.

## PC-1 - Floor-crossing priority

Decision: crossing the REC-5 floor for
`H-004 / research_oos / post_wp_5b / d2_006_gates` is the immediate Stage 2
priority (per WP-10u checkpoint lock, WP-10q selected segment, and REC-0022 and
REC-0023 segment fields).

Rationale:

- A first floor crossing is architecturally meaningful.
- It creates the first exact segment for which cross-window inference is no
  longer `INSUFFICIENT_EVIDENCE` under REC-5.
- It proves floor-crossing mechanics for one exact segment.
- The WP-10q-selected segment is the natural continuation target.
- Breadth at `n = 1` or `n = 2` would keep every segment below floor.

Non-claims: PC-1 does not commit to floor crossing any other segment, policy
work, scoring, ranking/recommendation, paper/live/runtime work, or
post-floor-crossing direction.

## PC-2 - Next evidence cycle

Decision: the next evidence cycle is one more Path A cycle against
`H-004 / research_oos / post_wp_5b / d2_006_gates`, D2-only through
`d2_006_gates`, expected to produce the third REC observation for that exact
segment if all later implementation packages validate (per WP-10p Stage 2
authorization, WP-10q selected segment, and WP-10u checkpoint lock).

Cycle constraints:

- Segment: unchanged from WP-10q.
- Path: Path A per WP-10p.
- New EXP: none.
- Future REP: one new REP against existing `EXP-0011`, in a later package.
- Future OL: one new OL from that REP, in a later package.
- Future REC: one new REC against `d2_006_gates`, in a later package.
- `exp_success_criteria` reconciliation is excluded from this cycle.
- No combined artifact package is authorized.

Observation-window direction:

- The future REP package should target a next-most-recent contiguous evaluation
  period of equivalent length to the `OL-0012` evaluation window.
- The exact dates are not locked by WP-10v.
- WP-10w must determine exact dates from refreshed repo/data truth and stop if
  the window is ambiguous, non-reproducible, synthetic, cloned from the previous
  window, or requires forbidden data/config/code changes.

REC-5 outcome:

- If the future REP -> OL -> REC chain validates and commits, the selected
  exact segment should move from 2 to 3 REC observations.
- That would satisfy REC-5 for that exact segment only.
- WP-10v itself does not satisfy REC-5.

## PC-3 - Post-floor-crossing disposition

Decision: once REC-5 crosses for the selected exact segment, explicit
chat-level direction-setting is required before any further Stage 2 work. No
automatic progression is authorized (per WP-10u checkpoint lock and this
post-checkpoint decision).

Informational possibilities after crossing, not pre-committed:

- first descriptive consumer brief over the crossed segment;
- floor crossing for additional segments;
- Path B authorization;
- Stage 2 second-sub-stage authorization;
- stop or hold at the first floor crossing.

Explicit non-authorizations:

- no policy work;
- no scoring/ranking/recommendation;
- no paper/live/runtime;
- no lifecycle transition work;
- no cross-segment inference involving below-floor segments.

## PC-4 - Forbidden scope preservation and additions

Decision: all forbidden scopes from WP-10p, WP-10u, and earlier locks remain
preserved (per WP-10p Stage 2 authorization and WP-10u checkpoint lock).

Preserved forbidden scopes include:

- promotion/demotion policy implementation or schema;
- ranking/recommendation implementation or schema;
- evidence-quality scoring implementation or schema;
- paper extension implementation or schema;
- live extension implementation or schema;
- operationally consequential lifecycle transitions;
- runtime, OMS, risk, safe-mode, execution, deployment;
- configs and dependencies;
- modifications to `lib/`, `src/`, `configs/`, `.claude/`, `data/`,
  `docs/data_catalog.md`, `docs/architecture/LONG_TERM_SCOPE.md`, or
  `docs/onboarding/PHASE2_BASELINE.md`;
- schema changes;
- validator changes;
- query-layer changes;
- existing committed instance changes;
- performance-based candidate selection;
- synthetic evidence;
- H-012 or any new candidate.

Post-checkpoint additions:

1. Cross-segment inference remains forbidden for non-crossed segments.
2. EXP scaffolds remain forbidden through the next Path A cycle and the later
   post-floor-crossing direction decision.
3. Premature consumer briefs using non-`INSUFFICIENT_EVIDENCE` language over
   the floor-crossing segment remain forbidden until the third REC observation
   is actually committed.

## Implementation sequencing

Future likely labels are placeholders only:

- WP-10w likely becomes the next REP package.
- WP-10x likely becomes the next OL package.
- WP-10y likely becomes the next REC package.

These labels are placeholders until drafted. WP-10v drafts no implementation
package. Each future package must be separately scoped, preflighted, validated,
and reviewed. No combined package is authorized.

## Validation expectations for subsequent implementation packages

Later implementation packages must preserve normal validation discipline:

- applicable schema validators pass;
- all discovered `v_integrity_*` views return `[]`;
- targeted pytest passes;
- full pytest passes;
- `git diff --check` passes;
- changed-file set matches the package scope;
- no policy/scoring/ranking/recommendation/paper-live/runtime framing;
- observation window is reproducible and not cloned;
- expectation source remains `d2_006_gates` only;
- segment identity remains exactly
  `H-004 / research_oos / post_wp_5b / d2_006_gates`.

## Non-claims

WP-10v creates no:

- additional segment selection;
- artifact;
- implementation artifact;
- schema;
- validator;
- query-layer change;
- test change;
- EXP scaffold;
- Path B;
- cohort;
- H-011 inclusion;
- H-012/new candidate;
- policy;
- scoring;
- ranking/recommendation;
- paper-live;
- runtime;
- post-floor-crossing direction.

WP-10v creates no separate methodology artifact beyond this WP-10v direction
decision document.
