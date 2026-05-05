# Post-REC Main 3.0 Architecture Checkpoint (WP-10a)

## Purpose

WP-10a is a documentation-only decision-support checkpoint after the REC v1
stability lock.

It prepares a clean Main 3.0 architecture decision point. It does not choose or
implement the next architecture tranche.

WP-10a creates no promotion/demotion policy, paper/live semantics,
evidence-quality scoring, ranking, recommendation, runtime, deployment, OMS,
risk, safe-mode, execution, or protected-path authority.

## Locked Inputs

The checkpoint consumes these locked descriptive baselines:

- Lifecycle v1 / LCH stability baseline from WP-9a through WP-9j.
- Outcome-ledger v1 stability baseline from WP-9k through WP-9t.
- REC v1 stability baseline from WP-9u through WP-9z.
- WP-9u: REC v1 schema and REC-1 through REC-6 decisions.
- WP-9v: REC validator, central query-layer relation, overview views, and
  integrity views.
- WP-9w: `REC-0001` seed and retrospective backfill methodology.
- WP-9x: retrospective backfill to `REC-0002` through `REC-0011`.
- WP-9y: REC consumer synthesis over the completed REC v1 corpus.
- WP-9z: REC v1 stability lock.

These inputs are descriptive research surfaces only. They do not authorize
promotion policy, paper/live semantics, evidence scoring, ranking,
recommendation, or runtime behavior.

## Current Research Machine State

At checkpoint time, repo truth records:

- LCH: 30 rows, 10 candidates, and 3 transition edges with counts 10 / 10 / 10.
- OL: 11 rows, 10 candidates, H-004 split across `pre_wp_5b` and
  `post_wp_5b`, with 10 `pre_wp_5b` rows and 1 `post_wp_5b` row.
- REC: 11 rows, 10 candidates, 11 source OL rows, 11
  `exp_success_criteria` expectation-source rows, and 0 `d2_006_gates`
  expectation-source rows.
- REC verdict distribution: 3 `none_met`, 7 `partially_met`, and 1
  `insufficient_evidence`.
- H-004 remains structurally split:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
```

The H-004 split is structural only. It creates no improvement, degradation,
pipeline-performance, policy, promotion, demotion, ranking, paper/live, or
recommendation claim.

REC-5 remains locked:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

All current REC-5 segments have `reconciliation_count = 1`. All current
segments remain below floor. All current cross-reconciliation inference remains
`INSUFFICIENT_EVIDENCE`.

All integrity views were empty at checkpoint time. Targeted and full tests pass.

## What Is Now Supported

The locked research machine now supports descriptive Main 3.0 decision support
only:

- lifecycle path inspection
- outcome-ledger inventory and source lineage inspection
- REC-to-OL mapping inspection
- REC verdict distribution inspection
- expectation-source distribution inspection
- H-004 split inspection
- REC-5 floor marking
- descriptive Main 3.0 decision support

These supported uses remain research-side and descriptive. They create no policy
or runtime authority.

## What Is Not Yet Supported

The current repo does not support:

- promotion/demotion policy
- candidate recommendation
- ranking
- paper/live readiness
- evidence-quality scoring
- strategy-family performance conclusions
- pipeline-version performance comparison
- cross-window inference below REC-5
- runtime/deployment authority
- OMS/risk/safe-mode/execution authority
- protected-path authority

These require explicit later architecture decisions and scoped implementation
packages where applicable.

## Main 3.0 Decision Options

The following are plausible next architecture tranches. WP-10a does not select
among them.

### Option A - Promotion/demotion Policy Architecture

Purpose:

- Define a policy schema and decision process that consumes locked REC, OL, and
  LCH surfaces.

Required decisions before Codex:

- Whether policy can proceed while every REC-5 segment is below floor.
- Whether policy is descriptive advisory only or can ever create promotion
  flags.
- Required source artifacts.
- Explicit non-runtime boundary.
- Whether policy needs more REC evidence first.

Risks:

- Converting descriptive verdicts into authority too early.
- Bypassing REC-5.
- Accidental paper/live implication.

### Option B - Paper/live REC/outcome Extension

Purpose:

- Define a future schema/version extension for paper/live outcomes and
  reconciliation.

Required decisions before Codex:

- Whether this is OL v2, REC v2, lifecycle v2, or a separate artifact family.
- Paper/live outcome kinds and required source artifacts.
- Validator/query-layer extension boundaries.
- Runtime/protected path firewall.

Risks:

- Touching execution semantics.
- Mixing `research_oos` and paper/live in v1.
- Premature deployment interpretation.

### Option C - Evidence-quality Scoring

Purpose:

- Define a separate evidence-quality methodology without altering REC verdicts.

Required decisions before Codex:

- Scoring object and scale.
- Source artifact families.
- Whether scoring is per-REC, per-OL, per-candidate, or per-evidence item.
- Whether scores affect policy or remain descriptive.

Risks:

- Conflating REC verdicts with evidence quality.
- Adding hidden recommendation logic.
- Subjective scoring without methodology.

### Option D - Ranking/recommendation Architecture

Purpose:

- Define whether ranking/recommendation should exist and under what floors.

Required decisions before Codex:

- Required evidence floor.
- Whether ranking is allowed while REC-5 segments are below floor.
- Tie-breaking and uncertainty posture.
- Explicit non-runtime status.

Risks:

- Unsupported candidate recommendation.
- Policy leakage.
- Overfitting retrospective data.

### Option E - Sufficient-evidence Expansion

Purpose:

- Generate or plan additional research/REC evidence to satisfy floors before
  policy.

Required decisions before Codex:

- Whether new experiments are in scope.
- How many additional OL/REC rows per segment are required.
- Whether H-004 post-WP-5b needs special handling.
- Whether this belongs to research planning, not artifact backfill.

Risks:

- Creating fake evidence by splitting artifacts.
- Lowering REC-5 implicitly.
- Expanding experiment scope prematurely.

## Recommended Sequencing Discipline

No Codex implementation package for Options A-E should begin until Main 3.0
selects a direction and resolves the required decisions for that direction.

If Main 3.0 does not decide, the default next action is no repo change.

If a repo package is required before a decision, it should only be another
decision-support brief, not policy implementation.

## Questions For Main 3.0

1. Which next tranche should proceed: policy, paper/live extension, evidence
   scoring, ranking/recommendation, sufficient-evidence expansion, or another
   direction?
2. Is any policy work allowed while all REC-5 segments are below floor?
3. Should downstream outputs be descriptive-only until REC-5 is satisfied?
4. Should paper/live semantics be versioned as OL v2, REC v2, lifecycle v2, or
   a separate family?
5. Should evidence-quality scoring be independent from REC verdicts?
6. What are the forbidden paths for the next tranche?
7. What package sequence should Codex execute after the decision?

## Validation Snapshot

WP-10a validation records:

- REC validator: PASS
- `v_reconciliation_overview`: 11 rows
- `v_reconciliation_candidate_pipeline_summary`: H-004 split preserved
- `v_integrity_reconciliation_refs`: `[]`
- `v_integrity_reconciliation_scope`: `[]`
- `v_integrity_reconciliation_expectation_source`: `[]`
- `v_integrity_reconciliation_derivation`: `[]`
- `v_integrity_reconciliation_realized_metrics`: `[]`
- all discovered `v_integrity_*` views: `[]`
- outcome-ledger validator: PASS
- `v_outcome_ledger_overview`: 11 rows
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved
- lifecycle validator: PASS
- `v_lifecycle_change_overview`: 30 rows
- `v_lifecycle_state_transitions`: 10 / 10 / 10
- existing validators: PASS
- targeted tests: PASS
- full pytest: PASS
- `git diff --check`: PASS

## Non-claims

WP-10a does not create:

- architecture decision
- promotion/demotion policy
- candidate recommendation
- ranking
- paper/live semantics
- evidence-quality scoring
- new schema
- new validator
- new query-layer view
- new artifact instance
- runtime/deployment/OMS/risk/safe-mode/execution authority
- protected-path authority
