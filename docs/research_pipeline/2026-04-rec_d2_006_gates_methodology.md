# REC d2_006_gates Methodology (WP-10b)

## Purpose

This methodology governs deriving REC v1 entries from the committed D2-006
promotion-gate source text and existing locked outcome-ledger outcomes.

WP-10b seeds exactly one real `d2_006_gates` REC artifact, `REC-0012`, against
`OL-0001`. It exercises the REC v1 `d2_006_gates` expectation-source path
without creating policy, promotion, ranking, paper/live, scoring, runtime, or
protected-path authority.

## Source Inputs

Allowed inputs for `d2_006_gates` REC derivation are:

- committed OL artifacts under `research/outcome_ledgers/`
- the D2-006 source at `docs/onboarding/PHASE2_BASELINE.md`
- the REC v1 schema and validator
- central query-layer REC views and integrity views

Do not use EXP success criteria, REP gate results, DEC, DCH, REL, HYPOTHESIS,
advisory artifacts, paper/live artifacts, policy artifacts, runtime outputs, or
data files as expectation sources for `d2_006_gates` REC entries.

## D2-006 Extraction Rules

Extract only from the committed D2-006 source text in:

```text
docs/onboarding/PHASE2_BASELINE.md
```

The canonical source section is:

```text
### D2-006 - Promotion gates are objective, numeric, and shared across all candidates
```

Preserve source section, path, field path, and source text. Do not invent
thresholds, restate thresholds from later evaluator behavior, or strengthen
qualitative language into numeric requirements.

## Deterministic Mapping Rules

Numeric gates can produce deterministic REC comparisons only when the D2-006
source provides an explicit numeric threshold and the referenced OL metrics
contain a directly corresponding metric.

For `REC-0012 -> OL-0001`, the deterministic mappings are:

| D2 gate | OL metric | REC comparison |
|---|---|---|
| Out-of-sample Sharpe >= 1.0 net of modeled costs | `sharpe` | numeric |
| DSR > 1.0 at 95% confidence given actual trial count | `dsr` | numeric |
| Max drawdown <= 20% in any walk-forward fold | `max_drawdown` | numeric |
| Cost drag <= 50% of gross PnL | `cost_drag_fraction` | extracted-only when `gross_pnl <= 0` |
| Walk-forward efficiency (OOS/IS Sharpe ratio) > 0.5 | `walk_forward_efficiency` | numeric |

The following gates are preserved in `expectation_extracted` but are not
compared for `REC-0012` because the referenced OL row either lacks a directly
mapped realized value or makes the ratio semantically uninterpretable:

- parameter sensitivity
- cost drag, because `OL-0001.metrics.gross_pnl <= 0` makes
  `cost_drag_fraction` semantically uninterpretable as a pass/fail ratio
- 90-day PnL concentration
- free parameter count

## Realized Metrics Rules

Copy `realized_metrics` exactly from the referenced OL `metrics` object.

Do not recompute metrics from REP, EXP, backtests, runtime, data files, or any
other source. Do not modify OL artifacts during REC derivation.

## Verdict Rules

For clear REC v1 cases:

- all metric comparisons `met` -> `all_met`
- all metric comparisons `not_met` -> `none_met`
- mixed `met` / `not_met` -> `partially_met`
- all metric comparisons `insufficient_evidence` -> `insufficient_evidence`

If no deterministic mappings exist, set all required comparison verdicts to
`insufficient_evidence` and set `overall_verdict` to
`insufficient_evidence`.

Unmapped qualitative or missing-metric gates do not create pass/fail authority.

## Retrospective Disclosure

All WP-10b and planned WP-10c `d2_006_gates` entries are retrospective because
they reconcile already committed OL outcomes against the already committed
D2-006 source text.

Each entry must set `retrospective_flag = true` and include a non-empty
`retrospective_disclosure` that states the source posture and non-authority
boundaries.

## ID Allocation

`REC-0012` is allocated to the WP-10b seed.

WP-10c bulk backfill should append from `REC-0013`. Do not rewrite committed
REC IDs without a later explicitly scoped package.

## REC-5 Floor Posture

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

`REC-0012` creates one new segment:

```text
H-001 / research_oos / pre_wp_5b / d2_006_gates -> reconciliation_count = 1
```

That segment remains below floor. WP-10b does not satisfy REC-5 and does not
support cross-segment inference.

## WP-10c Bulk Backfill Posture

WP-10c may append additional real `d2_006_gates` REC entries from locked OL
outcomes and the same D2-006 source text.

WP-10c must preserve append-only artifact discipline, deterministic mapping
rules, copied realized metrics, REC-5 floor discipline, and the same
non-authority boundaries. It must not create synthetic production evidence.

## WP-10c Completion

WP-10c appends `REC-0013` through `REC-0022`, completing the bounded
`d2_006_gates` backfill over the locked OL v1 corpus. The complete
`d2_006_gates` coverage is now:

```text
REC-0012 through REC-0022
```

Each locked OL v1 row from `OL-0001` through `OL-0011` now has exactly one
`d2_006_gates` REC entry. The prior `REC-0012 -> OL-0001` seed remains
unchanged, and WP-10c adds one append-only entry for each remaining OL row.

The H-004 split remains preserved under the D2-006 expectation source:

```text
REC-0016 / OL-0005 / H-004 / pre_wp_5b
REC-0022 / OL-0011 / H-004 / post_wp_5b
```

REC-5 remains below floor for every current segment because each
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`
segment has `reconciliation_count = 1`. WP-10c creates no policy,
promotion/demotion, ranking/recommendation, paper/live, evidence-scoring,
runtime, deployment, config, OMS, risk, safe-mode, overlay, or protected-path
authority.

## WP-10g REC-0012 Cost-Drag Correction

WP-10g corrects the original `REC-0012` seed so non-positive-gross-PnL
cost-drag comparison posture is consistent across D2 rows. `REC-0012`,
`REC-0017`, and `REC-0019` now preserve the D2-006 cost-drag expectation in
`expectation_extracted` but skip deterministic pass/fail comparison because
the referenced OL rows have `gross_pnl <= 0`.

WP-10g changes no REC schema, REC validator, query-layer code, OL artifacts,
EXP/REP artifacts, candidate registry, lifecycle artifacts, policy surface,
paper/live semantics, evidence scoring, ranking/recommendation logic, runtime,
deployment, config, dependency, OMS, risk, safe-mode, overlay, or
protected-path behavior. REC-5 remains below floor for every current segment.

## Non-Claims

This methodology and the committed `d2_006_gates` REC corpus create no:

- promotion or demotion policy
- candidate recommendation
- ranking
- paper/live readiness claim
- evidence-quality score
- REC-5 satisfaction claim
- cross-segment inference
- EXP, REP, OL, REC schema, validator, or query-layer authority change
- runtime, deployment, OMS, risk, safe-mode, execution, config, or
  protected-path authority
