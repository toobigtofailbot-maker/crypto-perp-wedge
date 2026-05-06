# Forward-Flow Evidence Plan (WP-10h)

## Purpose

WP-10h is a documentation-only plan after the WP-10g `REC-0012` correction.
It defines how future packages may generate new evidence toward REC-5
satisfaction without mutating the current retrospective corpus.

WP-10h does not generate evidence, create experiments, create EXP, REP, OL, or
REC artifacts, implement policy, score evidence quality, rank or recommend
candidates, create paper/live semantics, or touch runtime, deployment, OMS,
risk, safe-mode, execution, configs, dependencies, or protected paths.

## Locked Inputs

WP-10h consumes these locked descriptive inputs:

- WP-10g `REC-0012` correction.
- WP-10f Phase 9 -> Phase 10 transition decision.
- WP-10e REC-5 floor-gap stability lock.
- WP-10d REC cross-expectation-source consumer.
- REC v1 stability lock.
- Outcome-ledger v1 stability lock.
- Lifecycle stability lock.

These inputs are planning inputs only. They create no implementation,
promotion, demotion, ranking, recommendation, policy, paper/live,
evidence-scoring, runtime, or protected-path authority.

## Current Evidence State

Current repo truth records:

- REC corpus: 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11
  `d2_006_gates` rows.
- REC-5 state: every current `candidate_id / outcome_kind / pipeline_version /
  expectation_source_type` segment has `reconciliation_count = 1`, below the
  `n >= 3` floor.
- Outcome ledger: 11 rows, `OL-0001` through `OL-0011`.
- Lifecycle changes: 30 rows, with transition counts 10 / 10 / 10 for
  `proposed -> in_research`, `in_research -> research_concluded`, and
  `research_concluded -> archived`.
- H-004 remains structurally split under both expectation sources:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

`REC-0012` correction is complete. `REC-0012`, `REC-0017`, and `REC-0019`
all preserve the extracted D2-006 cost-drag gate and skip deterministic
cost-drag pass/fail comparison when `gross_pnl <= 0`. No open D2
non-positive-gross-PnL cost-drag anomaly remains.

## REC-5 Evidence Target

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

New evidence means:

- a new forward-flow observation with its own experiment/report provenance;
- a new outcome-ledger entry grounded in a future valid REP/EXP path;
- a new REC entry derived from a future OL row and one expectation source;
- append-only evidence unless an explicit correction package is approved.

Retrospective duplicate splitting does not count. Combining expectation
sources does not count. Combining pipeline versions does not count. Combining
H-004 pre/post rows does not count.

## Evidence Unit Definition

A future REC-5 evidence unit is the complete, validator-clean chain:

```text
candidate_id
outcome_kind
pipeline_version
expectation_source_type
experiment/report provenance
outcome-ledger artifact
reconciliation artifact
validation evidence
```

Required properties:

- unique future observation, not a clone of existing backfill;
- clear evaluation window or explicitly documented no-window convention;
- linked EXP and REP artifacts;
- OL artifact derived from actual future evidence;
- REC artifact derived from OL plus one expectation source;
- validator-clean and query-visible;
- no policy, paper/live, ranking, recommendation, scoring, runtime, or
  protected-path authority.

## Minimum Evidence Gap By Segment

Every current REC-5 segment has count 1. The REC-5 target is 3. The minimum
additional observations needed per current segment is therefore 2.

This does not mean every candidate should be expanded immediately. Candidate
selection for future evidence generation requires a later architecture or
planning decision. WP-10h does not select candidates for execution.

## Forward-Flow Package Sequence

Future evidence generation should follow this sequence unless a later Main 3.0
decision replaces it.

### Stage 1 - Evidence-Generation Architecture

Decide candidate selection rules, whether to prioritize one candidate, a small
cohort, or all candidates, expectation-source priority, evaluation-window
conventions, and whether H-004 pre/post remains separate.

Output: documentation-only architecture package.

### Stage 2 - Future Experiment Plan Package(s)

Create future EXP plan(s), define success criteria, define D2-006 gate linkage
if used, and define data requirements. No execution occurs unless separately
authorized.

### Stage 3 - Future Report/Artifact Package(s)

Create REP artifacts only after valid future evidence exists. Preserve actual
metrics and provenance. Do not create synthetic evidence.

### Stage 4 - Outcome-Ledger Append Package(s)

Append new OL rows from valid REP/EXP evidence. Do not mutate locked OL v1
rows. Preserve pipeline-version and evaluation-window semantics.

### Stage 5 - Reconciliation Append Package(s)

Append new REC rows from new OL rows and one expectation source per REC. Do
not combine expectation sources, pipeline versions, or H-004 split rows.

### Stage 6 - Consumer/Stability Update Package(s)

Only after new artifacts are validator-clean, update consumers and stability
locks descriptively. Policy still requires separate Main 3.0 authorization.

## Candidate-Selection Policy Is Not Decided

WP-10h does not choose which candidates receive forward-flow evidence. It does
not rank candidates, recommend strategies, promote or demote anything, or
select a source-type priority. Candidate-selection rules must be decided by a
later architecture package or Main 3.0.

## Expectation-Source Handling

`exp_success_criteria` and `d2_006_gates` remain separate source types.
Evidence counts do not combine across expectation sources. New evidence can
target one or both source types, but WP-10h does not choose a source-type
priority.

Any future expectation source type requires a schema and architecture decision
before implementation.

## Pipeline-Version And H-004 Handling

Pipeline versions remain separate for REC-5. H-004 pre/post remains a
structural split. Future H-004 evidence must specify pipeline version.

The current corpus supports no pre/post comparison and no improvement or
degradation inference. Any future comparison requires later explicit design and
sufficient evidence.

## Data/Evaluation-Window Planning Requirements

Future evidence packages must define:

- observation period;
- evaluation window start/end or explicit no-window convention;
- data source and data version;
- cost, slippage, and funding assumptions;
- walk-forward or holdout convention;
- reproducibility path;
- artifact provenance;
- validator path.

These requirements do not prescribe runtime or live execution implementation.

## Validation Requirements For Future Evidence

Future evidence packages must pass:

- relevant EXP/REP validators;
- outcome-ledger validator;
- REC validator;
- integrity views;
- lifecycle, OL, and REC regressions;
- targeted or full pytest as applicable;
- changed-file scope inspection;
- protected-path preservation checks.

## Stop Conditions For Future Evidence Packages

Future packages must stop if:

- evidence would be synthetic;
- evidence would clone existing retrospective rows;
- schema or validator changes are required without an architecture decision;
- policy, ranking, scoring, paper/live, or runtime scope is introduced;
- REC-5 counts would be satisfied by combining forbidden dimensions;
- protected paths are touched;
- integrity views become non-empty;
- tests fail.

## Supported Uses Of WP-10h

WP-10h supports:

- planning future evidence generation;
- estimating REC-5 evidence gaps;
- informing WP-10i Phase 10 architecture planning;
- defining sequencing constraints;
- preventing accidental policy, ranking, scoring, paper/live, or runtime drift.

## Unsupported Claims

WP-10h does not support claims of:

- REC-5 satisfaction;
- policy readiness;
- promotion or demotion;
- candidate ranking or recommendation;
- paper/live readiness;
- evidence-quality scoring;
- strategy-family performance conclusion;
- pipeline-version performance comparison;
- cross-window inference;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.

## Next Package Boundary

WP-10i should be the Phase 10 architecture plan. WP-10i should consume WP-10h
and decide the architecture sequence.

WP-10i should not implement experiments, policy, paper/live, scoring, ranking,
recommendation, or runtime. Policy and runtime packages remain forbidden unless
Main 3.0 later authorizes them.

## Validation Snapshot

WP-10h validation records:

- REC validator: PASS.
- `v_reconciliation_overview`: 22 rows.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11
  `d2_006_gates` rows.
- `v_reconciliation_candidate_pipeline_summary`: every current segment has
  `reconciliation_count = 1`.
- REC integrity views: `[]`.
- all discovered `v_integrity_*` views: `[]`.
- outcome-ledger validator: PASS.
- `v_outcome_ledger_overview`: 11 rows.
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved.
- lifecycle validator: PASS.
- `v_lifecycle_change_overview`: 30 rows.
- `v_lifecycle_state_transitions`: 10 / 10 / 10.
- targeted tests: PASS.
- full pytest: PASS.
- `git diff --check`: PASS.

## Non-Claims

WP-10h creates no:

- new EXP, REP, OL, or REC artifacts;
- REC-5 satisfaction;
- candidate selection;
- policy;
- promotion or demotion;
- ranking or recommendation;
- paper/live semantics;
- evidence-quality scoring;
- schema;
- validator;
- query-layer view;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.
