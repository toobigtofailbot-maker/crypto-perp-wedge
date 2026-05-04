# Phase 9 Decision Record

## Purpose

This record anchors Phase 9 architecture direction after WP-8i.

Phase 9 is named `Outcome-Ingesting Research Lifecycle Foundation`.

This document records research-pipeline architecture decisions only. It has no
runtime authority, no policy authority, no deployment authority, and no effect
on OMS, reconciliation, risk, overlay, safe-mode, or live-trading behavior.

## Lock Status Summary

Hard-locked now:

- Decision 1: Lifecycle State Vocabulary
- Decision 2: Permitted Lifecycle Transitions
- Decision 3: Lifecycle Transition Artifact Form
- Decision 4: Outcome Ledger Granularity
- Decision 5: Expected-vs-Realized Reconciliation Discipline
- Decision 6: Human Approval Semantics
- Decision 8: Advisory-to-Candidate Coupling

Principle-locked now, implemented by later scoped packages:

- Decision 7: Retrospective Backfill Discipline
- Decision 9: Tiered Promotion Evidence Policy
- Decision 10: Schema Versioning Discipline

## Decision 1 - Lifecycle State Vocabulary

Phase 9 lifecycle state vocabulary v1 contains ten states:

- `proposed`: a candidate or lifecycle object has been identified but research
  work has not started.
- `in_research`: research work is active.
- `research_concluded`: research work has reached a documented conclusion.
- `paper_eligible`: evidence is sufficient for a later human-gated paper start
  decision.
- `paper_active`: paper evaluation is active.
- `paper_concluded`: paper evaluation has completed and is ready for review.
- `live_eligible`: evidence is sufficient for a later human-gated live start
  decision.
- `live_active`: live evaluation is active under separately governed runtime
  and risk controls.
- `halted`: lifecycle progress is paused by a governed halt decision.
- `archived`: lifecycle progress is terminally closed.

The vocabulary evolves additively only. Future removals, renames, or semantic
rewrites require explicit later versioned schema work.

## Decision 2 - Permitted Lifecycle Transitions

Phase 9 lifecycle transitions are governed by the v1 transition graph.

All unlisted edges are forbidden. `archived` is terminal. `halted` recovery is
allowed only to the immediately preceding non-halted state, and validating that
history requires validator or integrity logic in WP-9b or later. Graph
evolution requires versioned schema work.

## Decision 3 - Lifecycle Transition Artifact Form

Lifecycle transitions are recorded by Lifecycle Change artifacts using the
`LCH-NNNN` identifier family.

LCH is distinct from Decision Change (`DCH-NNNN`) and Release Notes
(`REL-NNNN`). DCH records human approval-gate decisions in the existing
pipeline-stage vocabulary. REL records release and monitoring details for an
already approved stage transition. LCH records Phase 9 lifecycle state
transitions.

LCH artifacts may cite DCH, REP, REC, outcome, advisory, and other evidence
artifacts. WP-9a creates no LCH instances.

## Decision 4 - Outcome Ledger Granularity

Outcome-ledger v1 granularity is one record per candidate and evaluation
window.

Per-trade outcome ingestion is deferred to outcome-ledger v2 or later.

## Decision 5 - Expected-vs-Realized Reconciliation Discipline

Expected-vs-realized reconciliation uses the `REC-NNNN` artifact family.

Expected metrics must be extracted from cited committed artifacts rather than
reconstructed from memory or chat summaries. REC artifacts are separate from the
outcome ledger so expected-vs-realized comparison remains auditable.

WP-9a does not create a REC schema or REC instance.

## Decision 6 - Human Approval Semantics

Phase 9 approval fields are embedded in LCH artifacts.

There is no separate approval artifact in Phase 9 v1. Approval is human-only:
agents, helpers, validators, query views, and advisory artifacts do not approve
promotion, demotion, recovery, live entry, or deployment.

## Decision 7 - Retrospective Backfill Discipline

Retrospective lifecycle backfill for H-001 through H-010 is approved in
principle.

No retrospective LCH instances are created in WP-9a. Backfill belongs in a
dedicated later package and may be split if needed for reviewability.

## Decision 8 - Advisory-to-Candidate Coupling

Phase 9 artifacts may include optional one-way lineage references to advisory
artifacts.

Those references do not modify PGAS, SSS, AOUT, MOUT, or BMAP schemas and do
not grant advisory artifacts execution, ranking, approval, or runtime
authority.

## Decision 9 - Tiered Promotion Evidence Policy

Outcome ingestion cadence is manual and on-demand in Phase 9 v1. An
outcome-ingestion helper is a mid-tranche package, not WP-9a.

The standard promotion path requires:

- at least 3 completed paper evaluation windows
- at least 90 calendar days of paper trading coverage

The fast-track promotion path is for exceptional candidates only and requires:

- at least 1 completed paper evaluation window
- at least 30 calendar days of paper trading coverage
- stronger pre-paper evidence
- explicit human approval through LCH
- explicit risk acknowledgment
- limited-risk initial live exposure only
- predefined reduction, halt, or demotion criteria before live entry

Strong-candidate criteria include:

- strong OOS or forward-flow evidence
- realistic cost and slippage assumptions
- no leakage concerns
- acceptable drawdown profile
- sufficient trades or observations
- reproducible implementation
- clean lineage to EXP, REP, and REC evidence
- explicit risk acknowledgment
- no unresolved integrity issues

Live underperformance may trigger governed reduction, halt, demotion, or a new
research/change package. It must not trigger ad hoc runtime tweaking,
autonomous self-modification, automatic promotion, automatic scaling, or
full-risk live deployment from fast-track by default.

Exact thresholds, capital caps, monitoring cadence, and halt/reduction
mechanics belong in later promotion/demotion policy and deployment artifacts.

## Decision 10 - Schema Versioning Discipline

All Phase 9 schemas declare explicit `schema_version` from v1.

Cross-family schema-version discipline belongs in a later package. WP-9a does
not retrofit SSS v1 or SSS v2. SSS v1 remains governed by its top-level
`derivation_method` marker, and SSS v2 already has explicit
`schema_version: "v2"`.

## OL-1 - Outcome Ledger v1 Outcome Kind

Outcome-ledger v1 supports `research_oos` only.

Paper and live outcome kinds are v2 or later future work. WP-9k creates no
paper/live outcome semantics.

## OL-2 - Retrospective REP Backfill

Retrospective outcome-ledger backfill from REP artifacts is accepted after the
outcome-ledger schema and validator support are merged.

WP-9n or an equivalent later scoped package executes this backfill. WP-9k
creates no outcome-ledger instances.

## OL-3 - Derivation And Pipeline Disclosure

Outcome-ledger entries require `derivation_record`.

Outcome-ledger entries require `pipeline_version`.

Reproducibility is interpreted under the disclosed pipeline semantics and the
available committed source artifacts.

## OL-4 - Consumer Inference Floor

Outcome-ledger consumers must use an insufficient-evidence floor of at least 3
evaluation windows per candidate / outcome_kind / pipeline_version before
cross-window inference.

Below that floor, consumers must mark the inference state as
`INSUFFICIENT_EVIDENCE`.

This is a consumer-time rule for later packages. It is not WP-9k runtime,
validator, query-layer, or policy behavior.

## OL-5 - Outcome Ledger v1 Schema Scope

Outcome-ledger v1 includes:

- `research_oos` only
- required `pipeline_version`
- optional `linked_advisory_artifacts`
- no paper/live outcome kinds
- no per-trade granularity
- no evidence-quality scoring

## OL-6 - Outcome Ingestion Helper Sequencing

The outcome-ingestion helper is a mid-tranche package after schema,
validator/query-layer, methodology/synthetic instance, and retrospective
backfill.

WP-9k creates no outcome-ingestion helper.

## Non-Claims / Forbidden Implications

WP-9a does not imply:

- runtime influence
- automated promotion
- self-modifying agents
- portfolio or multi-asset architecture
- deployment authority
- modification to protected execution boundaries
- OMS, reconciliation, risk, overlay, safe-mode, or live-trading behavior

## Current Known Retrofit Candidates

- DCH `pipeline_stage` vocabulary differs from the Phase 9 lifecycle
  vocabulary. This is a Decision 10 / schema-versioning-discipline retrofit
  candidate, not WP-9a scope.
- Candidate-registry schema-version posture is a Decision 10 candidate because
  the current registry schema has no explicit top-level `schema_version`.
- Existing schema families without explicit schema-version fields are Decision
  10 candidates when and only when a later package explicitly scopes that
  cross-family discipline.
