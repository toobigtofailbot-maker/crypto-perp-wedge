# Reconciliation Artifact (REC v1)

## Purpose

The reconciliation artifact compares realized outcome-ledger outcomes against
committed expectation sources.

REC v1 is the first schema/documentation foundation for expected-vs-realized
research reconciliation. It records what was expected, what the outcome ledger
recorded, how each metric compared, and a derived `overall_verdict`.

REC artifacts are evidence artifacts only. They do not approve promotion,
demotion, paper trading, live trading, deployment, runtime changes, or policy
changes.

## Scope of REC v1

REC v1 supports `research_oos` outcome-ledger entries only.

REC v1 includes:

- required `schema_version: "v1"`
- `REC-NNNN` artifact identifiers
- one reconciled `OL-NNNN` outcome
- candidate, outcome kind, and pipeline-version segmentation fields copied
  from the reconciled outcome-ledger entry
- exactly one committed expectation source per REC artifact
- per-metric comparison
- a derived `overall_verdict`
- derivation and retrospective disclosure fields

WP-9u creates no REC instances, validator, query-layer relation, query-layer
view, helper, tests, consumers, policy, runtime authority, paper/live
semantics, or evidence-quality scoring.

## Relationship to Outcome Ledger

The outcome ledger records what happened. REC records how that outcome compares
against expectations that were committed elsewhere.

REC v1 reconciles only committed OL v1 `research_oos` entries. The REC schema
keeps the following segmentation fields because later consumers need them for
floor discipline:

- `candidate_id`
- `outcome_kind`
- `pipeline_version`
- `expectation_source_type`

The REC schema mirrors the OL v1 realized metric surface and does not introduce
new realized metric semantics. Later validator work is expected to enforce that
REC `realized_metrics` values match the cited OL entry.

## Expectation Sources

REC v1 supports exactly two expectation source types:

- `exp_success_criteria`
- `d2_006_gates`

For `exp_success_criteria`, the expectation source artifact id is an
`EXP-NNNN` plan and the source path is the committed EXP plan artifact.

For `d2_006_gates`, the expectation source artifact id is `D2-006` and the
source path is:

```text
docs/onboarding/PHASE2_BASELINE.md
```

The canonical source section is `D2-006 - Promotion gates are objective,
numeric, and shared across all candidates`.

DEC, HYPOTHESIS, REP `gate_results`, advisory artifacts, paper/live artifacts,
and policy artifacts are excluded from REC v1 expectation sources.

## Comparison Semantics

REC v1 supports per-metric comparison through
`comparison.metric_comparisons[]`.

Each comparison records:

- the metric name
- the extracted expected value
- the realized OL metric value
- numeric deltas when meaningful
- a metric-level verdict of `met`, `not_met`, or `insufficient_evidence`
- comparison notes

Deltas may be null when a criterion is qualitative or a gate reference does not
support a numeric delta without later extraction logic.

The intended `overall_verdict` derivation is:

- all comparable metrics met -> `all_met`
- mixed met/not_met -> `partially_met`
- all comparable required metrics not_met -> `none_met`
- all or decisive required metrics insufficient evidence ->
  `insufficient_evidence`

WP-9u documents this rule only. Validator enforcement belongs to a later
scoped package.

## REC-5 Consumer Floor

REC consumers must use a floor of at least `n >= 3` reconciliations per:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Below that floor, consumers must treat inference as insufficient evidence.

WP-9u documents the fields needed for that segmentation only. It creates no REC
consumer and no query-layer behavior.

## Retrospective Posture

Retrospective REC backfill for `OL-0001` through `OL-0011` is principle-locked
for later packages.

WP-9u creates no retrospective REC instances. If a later package creates
retrospective REC entries, each entry must set `retrospective_flag` and include
`retrospective_disclosure`.

## Forward-Compatibility Boundaries

REC v1 preserves narrow forward-compatible references for advisory and
lifecycle artifacts, but those references are lineage only.

REC v1 does not include:

- paper or live outcome reconciliation
- evidence-quality scoring
- policy fields
- promotion or demotion flags
- runtime authority
- deployment authority
- REC validator behavior
- REC query-layer behavior
- REC helper behavior

Paper/live reconciliation, evidence scoring, and promotion/demotion policy
require later explicitly scoped work.

## Validation Plan

WP-9u validates only the schema/documentation foundation:

- JSON Schema draft-07 self-check
- existing registry validators
- existing outcome-ledger validator
- existing query-layer integrity views
- existing lifecycle query regressions
- existing pytest regression suites
- `git diff --check`

Path existence checks, copied OL metric consistency, expectation-source
reference resolution, and `overall_verdict` derivation enforcement are deferred
to later validator work.

## Non-Claims

REC v1 does not claim:

- any candidate is promotable
- any candidate should be demoted
- any paper/live behavior is authorized
- any advisory artifact has execution or policy authority
- any policy threshold has changed
- any runtime, OMS, risk, overlay, safe-mode, deployment, config, or
  live-trading behavior has changed

REC v1 is an artifact contract only.
