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
