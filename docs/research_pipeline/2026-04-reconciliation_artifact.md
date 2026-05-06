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

## WP-9w Seed And Methodology

WP-9w commits the first real REC v1 artifact:

```text
research/reconciliations/REC-0001.reconciliation.json
```

The seed reconciles `OL-0001` for `H-001` under `pre_wp_5b` pipeline semantics
against `EXP-0002` success criteria at:

```text
research/experiments/EXP-0002.plan.json
```

The retrospective backfill methodology is documented at:

```text
docs/research_pipeline/2026-04-reconciliation_backfill_methodology.md
```

The REC validator and query-layer now operate over one committed REC row.
REC-0001 extracts the committed EXP success criteria, compares only
deterministically mapped OL metrics, and preserves unmapped gate-reference or
qualitative criteria without inventing thresholds or authority.

WP-9w defers full REC backfill, helper tooling, consumers, promotion/demotion
policy, paper/live semantics, evidence-quality scoring, and runtime,
deployment, config, OMS, risk, overlay, safe-mode, or live-trading behavior.

## WP-9x Retrospective Backfill

WP-9x completes the REC v1 retrospective artifact backfill over the locked OL
v1 corpus. The committed REC corpus now covers:

```text
REC-0001 through REC-0011
```

Each locked OL v1 row has exactly one REC v1 artifact. `REC-0001` remains the
WP-9w seed; WP-9x appends `REC-0002` through `REC-0011` without rewriting the
seed.

Source selection follows the WP-9w methodology: use the OL-linked committed
EXP success criteria when present and candidate-consistent, and use D2-006 only
as a fallback. The WP-9x corpus uses committed EXP success criteria for every
new REC row. Realized metrics are copied from the referenced OL artifacts
without recomputation.

The H-004 split is preserved as two distinct REC rows:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b
REC-0011 / OL-0011 / H-004 / post_wp_5b
```

The REC validator and query layer now operate over 11 committed REC rows.
Helper tooling, REC consumers, promotion/demotion policy, paper/live
semantics, evidence-quality scoring, and runtime, deployment, config, OMS,
risk, overlay, safe-mode, or live-trading behavior remain deferred.

## WP-10b D2-006 Gates Seed

WP-10b commits the first real `d2_006_gates` REC v1 artifact:

```text
research/reconciliations/REC-0012.reconciliation.json
```

The seed reconciles `OL-0001` for `H-001` under `pre_wp_5b` pipeline
semantics against the committed D2-006 source at:

```text
docs/onboarding/PHASE2_BASELINE.md
```

The methodology for deriving `d2_006_gates` REC entries is documented at:

```text
docs/research_pipeline/2026-04-rec_d2_006_gates_methodology.md
```

The committed REC corpus now has 12 rows: 11 `exp_success_criteria` rows and
one `d2_006_gates` row. The new segment is:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates -> reconciliation_count = 1
```

That segment remains below the REC-5 floor. WP-10c bulk `d2_006_gates`
backfill remains deferred.

WP-10b changes no REC schema, validator, query-layer code, policy surface,
paper/live semantics, evidence-quality scoring, runtime, deployment, config,
OMS, risk, overlay, safe-mode, or live-trading behavior.

## WP-10c D2-006 Gates Backfill

WP-10c completes the `d2_006_gates` REC v1 retrospective backfill over the
locked OL v1 corpus. The committed REC corpus now has 22 rows:

```text
REC-0001 through REC-0022
```

The expectation-source distribution is now 11 `exp_success_criteria` rows and
11 `d2_006_gates` rows. D2-006 coverage spans:

```text
REC-0012 through REC-0022
```

Those D2-006 rows cover source OL outcomes `OL-0001` through `OL-0011` exactly
once each. The H-004 split remains preserved across both expectation sources:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

REC-5 remains below floor for every current segment. WP-10c is descriptive
only and leaves the WP-10d cross-expectation-source descriptive brief as the
downstream consumer package. WP-10c changes no REC schema, validator,
query-layer code, policy surface, paper/live semantics, evidence-quality
scoring, ranking/recommendation logic, runtime, deployment, config, OMS, risk,
overlay, safe-mode, or live-trading behavior.

## WP-10g REC-0012 Cost-Drag Correction

WP-10g corrects the `REC-0012` D2-006 cost-drag comparison posture after WP-10d
surfaced the pre-WP-10c seed anomaly. `REC-0012` now preserves the D2-006
cost-drag gate in `expectation_extracted` but omits `cost_drag_fraction` from
deterministic pass/fail comparison because `OL-0001.metrics.gross_pnl <= 0`
makes the ratio semantically uninterpretable.

The correction makes non-positive-gross-PnL cost-drag handling consistent
across `REC-0012`, `REC-0017`, and `REC-0019`. It changes no REC schema, REC
validator, query-layer code, OL artifacts, EXP/REP artifacts, policy surface,
paper/live semantics, evidence-quality scoring, ranking/recommendation logic,
runtime, deployment, config, OMS, risk, overlay, safe-mode, or live-trading
behavior. REC-5 remains below floor for every current segment.

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
