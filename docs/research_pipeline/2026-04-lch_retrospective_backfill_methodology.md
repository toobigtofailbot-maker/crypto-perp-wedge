# LCH Retrospective Backfill Methodology (WP-9d)

## Purpose

This document defines the methodology for retrospective Lifecycle Change (LCH)
backfill.

WP-9d applies the method first to H-001. WP-9e is expected to apply this same
method to H-002 through H-010 unless current repo truth requires a later
revision.

This record has no runtime, policy, promotion, paper/live, deployment, OMS,
reconciliation, risk, overlay, safe-mode, or live-trading authority.

## Scope

WP-9d creates H-001 lifecycle changes only.

WP-9e is expected to apply the same method to H-002 through H-010 in a later
package. H-011 and future candidates are out of scope.

This methodology does not create outcome-ledger artifacts, REC artifacts, new
research results, or candidate promotion authority.

## Candidate Lifecycle Path

Historical concluded / NO-GO candidates map to:

```text
proposed -> in_research -> research_concluded -> archived
```

No paper, live, halted, or fast-track state is used for H-001 through H-010
retrospective backfill unless repo truth proves otherwise.

This state mapping is retrospective disclosure only. It does not rewrite the
candidate registry status, verdict, pipeline stage, or any cited evidence
artifact.

## Per-Transition Evidence Convention

Use one evidence convention per transition:

- `proposed -> in_research`: cite the candidate `HYPOTHESIS.md` repo-relative
  path.
- `in_research -> research_concluded`: cite the candidate REP artifact ID.
- `research_concluded -> archived`: cite the DEC markdown repo-relative path.
  The LCH validator does not treat bare `DEC-*` as a known reference prefix in
  current repo truth, so DEC evidence must be represented as an existing
  repo-relative path unless a later package changes validator behavior.

For WP-9e, H-005 is expected to cite its DEC path plus `DCH-0001` and
`REL-0001` on the third transition if those artifacts remain committed and
relevant.

## Timestamp Convention

Use the first commit timestamp that introduced the evidence artifact when that
source is unambiguous.

Command pattern:

```powershell
git log --follow --reverse --format=%cI -- <evidence-path> | Select-Object -First 1
```

If artifact-introduction timestamp evidence is unavailable, ambiguous, or
misleading, inspect whether the artifact has an internal date field. Use an
internal date only when it is clearly repo truth, and disclose that fallback in
`retrospective_disclosure`.

Do not invent timestamps.

## `decided_by` Convention

WP-9d uses:

```text
retrospective_backfill_wp_9d
```

WP-9e should use:

```text
retrospective_backfill_wp_9e
```

This is the identity of the backfill recorder. It is not a claim about the
historical human author of the original hypothesis, experiment report, or
decision record.

## `risk_acknowledgment` Convention

Use this uniform statement:

```text
Retrospective backfill of historical lifecycle transition; no operational risk implication. Original decision risk was acknowledged in cited evidence artifacts.
```

## `retrospective_disclosure` Template

Use this template and replace bracketed terms with the specific transition
facts:

```text
Retrospective backfill of [TRANSITION_EDGE] for [CANDIDATE_ID]. The historical transition is evidenced by [EVIDENCE_REF] with decided_at sourced from [TIMESTAMP_SOURCE]. This LCH was authored post hoc in WP-9d to populate the Phase 9 lifecycle layer under Decision 7; it does not modify the candidate, the cited evidence artifact, any historical decision, or any runtime behavior.
```

## ID Allocation Strategy

WP-9d allocates:

- `LCH-0001` through `LCH-0003` for H-001.

WP-9e is expected to allocate:

- `LCH-0004` through `LCH-0030` for H-002 through H-010 in candidate order.

All retrospective backfill instances set `retrospective_flag` to `true`.

All `supersedes_lch_id` values are `null`.

## H-001 Instances Created by WP-9d

WP-9d creates:

- `LCH-0001`: H-001 `proposed -> in_research`, evidenced by
  `research/hypotheses/H-001/HYPOTHESIS.md`.
- `LCH-0002`: H-001 `in_research -> research_concluded`, evidenced by
  `REP-0002`.
- `LCH-0003`: H-001 `research_concluded -> archived`, evidenced by
  `research/decisions/DEC-0001.md`.

Each `decided_at` value is sourced from the first commit timestamp introducing
the transition evidence artifact.

## Validation Expectations

After WP-9d:

- the LCH validator passes
- `v_lifecycle_change_overview` shows three rows
- `v_lifecycle_state_transitions` shows one count for each H-001 transition
  edge
- all LCH integrity views return `[]`
- all existing non-LCH integrity views remain `[]`

## Non-Claims

WP-9d does not create:

- a new research result
- a candidate status mutation
- paper or live eligibility
- outcome-ledger evidence
- REC evidence
- promotion or demotion policy
- deployment artifacts
- fast-track decisions
- runtime, policy, OMS, reconciliation, risk, overlay, safe-mode, live-trading,
  or protected-path behavior

## WP-9e Handoff

WP-9e must use this methodology unchanged unless repo truth reveals a blocker.

Any methodology change in WP-9e requires escalation rather than silent drift.
