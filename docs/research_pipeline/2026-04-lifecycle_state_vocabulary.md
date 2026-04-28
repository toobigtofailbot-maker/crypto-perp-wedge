# Lifecycle State Vocabulary v1

## Purpose

This document defines the Phase 9 lifecycle-state vocabulary used by Lifecycle
Change artifacts.

The vocabulary is an architectural language for research lifecycle state. It is
not the same vocabulary as the existing DCH and candidate-registry
`pipeline_stage` enum.

## States

`proposed`

- Entry meaning: a candidate or lifecycle object has been identified.
- Exit meaning: research work starts through `proposed -> in_research`.

`in_research`

- Entry meaning: active research is underway.
- Exit meaning: research reaches a documented conclusion.

`research_concluded`

- Entry meaning: research has concluded with evidence.
- Exit meaning: the lifecycle moves to paper eligibility or archival.

`paper_eligible`

- Entry meaning: a human has recorded that paper evaluation may be considered.
- Exit meaning: paper evaluation starts or the lifecycle is archived.

`paper_active`

- Entry meaning: paper evaluation is active.
- Exit meaning: paper evaluation concludes, the lifecycle is halted, or the
  lifecycle is archived.

`paper_concluded`

- Entry meaning: paper evaluation has completed and is ready for review.
- Exit meaning: the lifecycle moves to live eligibility or archival.

`live_eligible`

- Entry meaning: a human has recorded that live evaluation may be considered.
- Exit meaning: live evaluation starts or the lifecycle is archived.

`live_active`

- Entry meaning: live evaluation is active under separately governed runtime
  and risk controls.
- Exit meaning: the lifecycle returns to paper-concluded review, is halted, or
  is archived.

`halted`

- Entry meaning: lifecycle progress is paused by a governed halt decision.
- Exit meaning: recovery occurs only through LCH to the immediately preceding
  non-halted state, or the lifecycle is archived.

`archived`

- Entry meaning: lifecycle progress is terminally closed.
- Exit meaning: none.

## Terminal Classification

Terminal:

- `archived`

Non-terminal:

- `proposed`
- `in_research`
- `research_concluded`
- `paper_eligible`
- `paper_active`
- `paper_concluded`
- `live_eligible`
- `live_active`
- `halted`

`halted` is recoverable, but only through LCH and only subject to later
validator or integrity checks that can inspect lifecycle history.

## Relationship To DCH Pipeline Stage

The existing DCH and candidate-registry `pipeline_stage` vocabulary is:

- `reserved`
- `pre_registered`
- `baseline_tested`
- `sensitivity_tested`
- `monte_carlo_tested`
- `paper_validated`
- `shadow_live`
- `production_live`
- `archived`

That vocabulary is adjacent to, not identical with, Phase 9 lifecycle state. It
remains unchanged in WP-9a. Any retrofit or mapping belongs to later Decision
10 schema-versioning work.

## Non-Claims

This vocabulary does not:

- authorize runtime deployment
- mutate the candidate registry
- approve any candidate
- create paper execution
- create live execution
- change OMS, reconciliation, risk, overlay, safe-mode, or live-trading behavior
