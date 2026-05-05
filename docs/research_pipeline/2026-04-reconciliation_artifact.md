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

WP-9u creates no REC instances, helper, consumers, policy, runtime authority,
paper/live semantics, or evidence-quality scoring. WP-9v adds validator and
query-layer support only.

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

WP-9v adds path/reference checks, copied OL metric consistency, and clear
`overall_verdict` derivation enforcement. Nuanced enforcement for "decisive
required metrics" remains deferred because REC v1 does not identify decisive
metrics in schema shape.

## WP-9v Validator And Query Layer

WP-9v makes REC v1 operationally checkable and queryable while keeping the REC
corpus empty.

The validator is:

```powershell
.\.venv\Scripts\python.exe -m tools.registry.validate_reconciliations
```

Future REC artifacts use this directory and filename convention:

```text
research/reconciliations/REC-0001.reconciliation.json
```

Missing `research/reconciliations/` and an existing directory with no
`*.reconciliation.json` files are healthy empty states. WP-9v does not create
the directory and does not create any REC instances.

The validator checks JSON shape against
`research/schemas/reconciliation.schema.json`, duplicate IDs, filename/ID
consistency, candidate and outcome-ledger references, REC/OL copied
segmentation fields, EXP and D2-006 expectation-source references,
top-level-vs-extracted expectation source consistency, derivation-record
consistency, linked advisory/lifecycle references, deterministic copied
`realized_metrics` values, retrospective disclosure, and clear
`overall_verdict` derivations.

The query layer exposes:

- `reconciliations`
- `v_reconciliation_overview`
- `v_reconciliation_candidate_pipeline_summary`
- `v_integrity_reconciliation_refs`
- `v_integrity_reconciliation_scope`
- `v_integrity_reconciliation_expectation_source`
- `v_integrity_reconciliation_derivation`
- `v_integrity_reconciliation_realized_metrics`

All REC overview, summary, and integrity views return empty results in the
current no-instance state.

WP-9v explicitly defers:

- REC instances
- REC methodology
- retrospective REC backfill
- REC helper or artifact-generation tooling
- REC consumers and consumer-floor views
- promotion/demotion policy
- paper/live reconciliation semantics
- evidence-quality scoring
- runtime, deployment, config, OMS, risk, overlay, safe-mode, or live-trading
  behavior

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
