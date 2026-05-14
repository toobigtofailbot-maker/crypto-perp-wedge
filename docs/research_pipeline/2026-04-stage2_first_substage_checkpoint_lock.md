# Stage 2 First-Sub-Stage Checkpoint Lock (WP-10u)

## Purpose

WP-10u is a documentation-only checkpoint lock after the completed Stage 2
first-sub-stage sequence. It records the state reached by WP-10q, WP-10r,
WP-10s, and WP-10t, and stops before any further Stage 2 work.

WP-10u creates no evidence artifact, selects no new segment, creates no cohort,
and authorizes no continuation package.

## Locked inputs

WP-10u consumes these locked inputs:

- WP-10p Stage 2 authorization decision:
  `docs/research_pipeline/2026-04-stage2_authorization_decision.md`.
- WP-10q Stage 2 candidate-selection application:
  `docs/research_pipeline/2026-04-stage2_candidate_selection_application.md`.
- WP-10r Stage 2 Path A report:
  `research/experiments/REP-0012.report.json`.
- WP-10s Stage 2 Path A outcome ledger:
  `research/outcome_ledgers/OL-0012.outcome_ledger.json`.
- WP-10t Stage 2 Path A reconciliation:
  `research/reconciliations/REC-0023.reconciliation.json`.
- Current project-status, REC, OL, EXP/REP, lifecycle, and registry repo truth.

These inputs are descriptive controls only. They create no EXP scaffold, EXP
plan, artifact, policy, scoring, ranking/recommendation, paper-live, runtime,
config, dependency, data, or protected-path authority.

## Stage 2 first-sub-stage completed sequence

Stage 2 first sub-stage is complete as executed through this sequence:

1. WP-10q selected exactly one real exact segment.
2. WP-10r added one REP from existing `EXP-0011`.
3. WP-10s added one OL from `REP-0012`.
4. WP-10t added one REC from `OL-0012` against D2-006.

This sequence used Path A only. It did not create a new EXP scaffold or EXP
plan, and it did not authorize Path B.

## Selected exact segment

The locked selected exact segment is:

```text
candidate_id: H-004
outcome_kind: research_oos
pipeline_version: post_wp_5b
expectation_source_type: d2_006_gates
```

In compact form:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

This selection remains a Stage 2 first-sub-stage methodology result. It is not
a cohort, policy decision, performance quality claim, ranking, recommendation,
paper-live readiness claim, runtime claim, promotion, or demotion.

## Artifact chain

The completed Path A artifact chain is:

```text
EXP-0011 -> REP-0012 -> OL-0012 -> REC-0023
```

`EXP-0011` already existed before WP-10r. WP-10r created `REP-0012`, WP-10s
created `OL-0012`, and WP-10t created `REC-0023`.

WP-10u creates no EXP, REP, OL, REC, LCH, registry, or trial-log artifact.

## REC-5 accounting

REC-5 remains unsatisfied.

The REC-5 floor remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

The selected exact segment now has 2 REC observations:

```text
REC-0022 / OL-0011 / H-004 / research_oos / post_wp_5b / d2_006_gates
REC-0023 / OL-0012 / H-004 / research_oos / post_wp_5b / d2_006_gates
```

Because `2 < 3`, the selected exact segment remains below the REC-5 floor.
Sources, pipeline versions, and expectation-source types remain separate and
do not combine for REC-5.

## Cost-drag non-positive-gross-PnL posture

`OL-0012.metrics.gross_pnl <= 0`. `REC-0023` preserves the D2-006
cost-drag expectation but skips deterministic cost-drag pass/fail comparison
because `cost_drag_fraction` is not semantically interpretable as a fraction of
positive gross PnL in this case.

`REC-0023` does not treat negative cost drag as a pass. This is a descriptive
comparison-surface posture only and creates no policy, scoring,
ranking/recommendation, paper-live, runtime, promotion, or demotion authority.

## H-004 split handling

H-004 pre/post rows remain structurally separate. WP-10u makes no H-004
pre/post comparison, improvement claim, degradation claim, or special-case
policy claim.

The Stage 2 first sub-stage targeted only:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

Historical H-004 rows under other pipeline versions or expectation-source types
remain unchanged and separate.

## H-011 exclusion / no-current-target posture

H-011 remains registry-present with no current OL/REC target segment. H-011
was not included in WP-10q, WP-10r, WP-10s, WP-10t, or WP-10u.

WP-10u does not demote H-011, replace H-011 by comparison, register H-012 or
beyond, or authorize a new-candidate evidence path.

## Path A boundary confirmation

The completed first sub-stage stayed within Path A:

- one selected exact segment;
- one new REP against existing committed `EXP-0011`;
- one new OL from that REP;
- one new REC from that OL against D2-006;
- no new EXP.

Path B was not authorized. No EXP scaffold, EXP plan, small cohort, H-011
inclusion, H-012/new-candidate path, LCH artifact, or registry artifact was
created.

## What the first sub-stage did not do

The Stage 2 first sub-stage did not:

- satisfy REC-5;
- create synthetic evidence for REC-5;
- combine expectation sources, pipeline versions, or H-004 split rows;
- create a cohort;
- include H-011;
- create H-012 or any new candidate;
- create an EXP scaffold or EXP plan;
- create a new EXP;
- create an LCH or registry artifact;
- change schemas, validators, query-layer behavior, tests, runtime, configs,
  dependencies, data, or protected paths;
- create policy, scoring, ranking/recommendation, paper-live, runtime,
  promotion, or demotion authority.

## Checkpoint lock statement

Stage 2 first sub-stage is locked complete as executed through WP-10q, WP-10r,
WP-10s, and WP-10t.

This lock records the completed Path A chain and the remaining below-floor
REC-5 posture. It does not authorize another Path A cycle, a Stage 2
second-sub-stage package, Path B, an EXP scaffold, a small cohort, a new
candidate path, policy, scoring, ranking/recommendation, paper-live, runtime,
promotion, or demotion.

## Non-authorized future options

Main 3.0 may later decide to:

- stop at this checkpoint;
- authorize another Path A evidence cycle;
- authorize a Stage 2 second-sub-stage decision package;
- authorize or continue blocking Path B / EXP scaffold work;
- redirect to a different stability or architecture package.

None of those options is authorized by WP-10u. WP-10u does not draft WP-10v,
WP-10w, or any later package.

## Required Main 3.0 decision before further work

Further Stage 2 work requires a new Main 3.0 capsule. That future capsule must
explicitly choose the next package class, scope, changed-file limits,
validation requirements, and protected-boundary constraints before work begins.

This checkpoint alone is not execution authority for any further Stage 2
package.

## Validation snapshot

WP-10u validation is expected to cover:

- all available `tools.registry.validate_*` validators;
- all discovered `v_integrity_*` views, expected `[]`;
- targeted registry, research-query, reconciliation, outcome-ledger,
  lifecycle, and experiment tests;
- full pytest;
- semantic scans for forbidden authority language;
- `git diff --check`;
- changed-file inspection.

The expected changed-file set is exactly:

```text
docs/project_status.md
docs/research_pipeline/2026-04-stage2_first_substage_checkpoint_lock.md
```

## Non-claims

WP-10u creates no:

- new segment selection;
- cohort;
- EXP scaffold or EXP plan;
- EXP, REP, OL, REC, LCH, registry, or trial-log artifact;
- H-011 inclusion;
- H-012 or new candidate;
- REC-5 satisfaction;
- source, pipeline-version, or expectation-source combining;
- H-004 pre/post comparison claim;
- schema change;
- validator change;
- query-layer change;
- test change;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- config, dependency, data, or protected-path change;
- policy;
- scoring;
- ranking or recommendation;
- promotion or demotion;
- paper-live semantics.
