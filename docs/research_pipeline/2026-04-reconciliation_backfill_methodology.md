# REC v1 Retrospective Backfill Methodology (WP-9w)

## Purpose

This methodology governs deriving REC v1 artifacts from locked OL v1 outcomes
and committed expectation sources.

WP-9w seeds exactly one real REC artifact, `REC-0001`. Full retrospective REC
backfill remains deferred to WP-9x. WP-9w introduces no helper or automation.

## Inputs

REC v1 backfill may use:

- committed OL artifacts
- OL-linked EXP plans
- EXP `success_criteria`
- D2-006 fallback source at `docs/onboarding/PHASE2_BASELINE.md`
- REC schema
- REC validator and query-layer surfaces

## Source Selection Order

1. Use OL-linked EXP `success_criteria` when present and candidate-consistent.
2. Use `d2_006_gates` only when EXP success criteria are missing or explicitly
   not usable.
3. Do not use DEC, HYPOTHESIS markdown, REP `gate_results`, advisory artifacts,
   policy artifacts, paper/live sources, or runtime outputs in REC v1.

## Expectation Extraction Rules

Extract only from committed source fields. Preserve source field paths and
source text/value.

Do not invent thresholds. Numeric comparisons require an explicit numeric
threshold and a deterministic metric mapping to the referenced OL metrics.
Qualitative or gate-reference expectations become `insufficient_evidence`
unless deterministic comparison is defined by the source.

## Realized Metrics Rules

Copy realized metrics exactly from the referenced OL entry. The REC validator
enforces copied-value consistency.

Do not recompute metrics from REP, EXP, runtime data, or other sources. Do not
change OL artifacts during REC backfill.

## Verdict Derivation Rules

For clear REC v1 cases:

- all metric comparisons `met` -> `all_met`
- all metric comparisons `not_met` -> `none_met`
- mixed `met` / `not_met` -> `partially_met`
- all metric comparisons `insufficient_evidence` -> `insufficient_evidence`

Nuanced decisive-required-metric handling remains deferred because REC v1 does
not define decisiveness.

## Retrospective Disclosure Rules

All current backfill entries are retrospective. Each entry must set
`retrospective_flag = true`, include a non-empty disclosure, and state source
selection and limitations.

## ID Allocation

`REC-0001` is allocated to the WP-9w seed. WP-9x full backfill must append from
`REC-0002`.

Never rewrite committed REC IDs without an explicitly scoped package.

## Seed Artifact Summary

`REC-0001` reconciles `OL-0001` for `H-001` under `pre_wp_5b` pipeline
semantics. The expectation source is `exp_success_criteria` from `EXP-0002` at
`research/experiments/EXP-0002.plan.json`.

The seed extracts all committed `EXP-0002.success_criteria` values. It compares
only criteria with deterministic OL metric mappings: Sharpe, DSR, max drawdown,
cost drag, and walk-forward efficiency. All mapped comparisons are `not_met`,
so `overall_verdict` is `none_met`. Gate-reference and unmapped criteria are
preserved in extraction and do not create additional verdict authority.

## Full Backfill Plan For WP-9x

WP-9x should backfill remaining eligible OL entries. Preserve one REC per
selected OL/expectation-source pair unless Main 3.0 decides otherwise.

WP-9x must preserve the H-004 `pre_wp_5b` / `post_wp_5b` split and REC-5
segmentation by `candidate_id / outcome_kind / pipeline_version /
expectation_source_type`. Do not infer consumer-floor conclusions until a later
consumer package.

## WP-9x Completion

WP-9x completes the retrospective REC v1 backfill over the locked OL v1 corpus.
It preserves `REC-0001` and appends:

| REC | OL | Candidate | Pipeline | Expectation source | Verdict |
|---|---|---|---|---|---|
| `REC-0002` | `OL-0002` | `H-005` | `pre_wp_5b` | `EXP-0001` | `partially_met` |
| `REC-0003` | `OL-0003` | `H-002` | `pre_wp_5b` | `EXP-0003` | `partially_met` |
| `REC-0004` | `OL-0004` | `H-003` | `pre_wp_5b` | `EXP-0004` | `partially_met` |
| `REC-0005` | `OL-0005` | `H-004` | `pre_wp_5b` | `EXP-0005` | `partially_met` |
| `REC-0006` | `OL-0006` | `H-006` | `pre_wp_5b` | `EXP-0006` | `partially_met` |
| `REC-0007` | `OL-0007` | `H-007` | `pre_wp_5b` | `EXP-0007` | `none_met` |
| `REC-0008` | `OL-0008` | `H-008` | `pre_wp_5b` | `EXP-0008` | `partially_met` |
| `REC-0009` | `OL-0009` | `H-009` | `pre_wp_5b` | `EXP-0009` | `none_met` |
| `REC-0010` | `OL-0010` | `H-010` | `pre_wp_5b` | `EXP-0010` | `partially_met` |
| `REC-0011` | `OL-0011` | `H-004` | `post_wp_5b` | `EXP-0011` | `insufficient_evidence` |

Expectation-source distribution is 11 `exp_success_criteria` rows and 0
`d2_006_gates` fallback rows. Verdict distribution is 3 `none_met`, 7
`partially_met`, and 1 `insufficient_evidence`.

For `REC-0002` through `REC-0010`, deterministic comparison is limited to
Sharpe, DSR, max drawdown, cost drag, and walk-forward efficiency because those
criteria have explicit numeric thresholds and OL metric mappings. Gate
references, sensitivity, PnL concentration, free-parameter count, and
qualitative kill criteria are preserved but unmapped.

`REC-0011` preserves the committed `EXP-0011` success criteria and records
`insufficient_evidence` because those criteria are operational/qualitative and
do not provide deterministic numeric thresholds mapped to OL metrics.

The H-004 split remains separate:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b
REC-0011 / OL-0011 / H-004 / post_wp_5b
```

WP-9x does not compare those rows against each other and does not infer
improvement, degradation, promotion, demotion, paper/live readiness, policy,
consumer, helper, evidence-scoring, runtime, deployment, config, OMS, risk,
overlay, safe-mode, or live-trading authority.

## Non-Claims

REC backfill creates no:

- promotion/demotion policy
- paper/live semantics
- evidence-quality scoring
- REC helper
- REC consumer
- candidate recommendation
- runtime, deployment, OMS, risk, safe-mode, execution, config, or
  protected-path authority
