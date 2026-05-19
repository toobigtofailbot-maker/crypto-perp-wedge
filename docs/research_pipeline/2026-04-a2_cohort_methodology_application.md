# A2 Cohort Methodology Application

## Package Metadata And Scope

- Package label: WP-12ao / WP-S2c-6.
- Package title: A2 Cohort Methodology Application.
- Package class: Tier 1 documentation-only methodology-application package.
- Effective base: post-WP-12an / post-cohort-selection-methodology.
- Committed files: this document and `docs/project_status.md` only.
- Optional package-local query/output bundle: not used.

This package applies the committed WP-S2c-5 methodology mechanically against
current repo truth. It produces the actual A2 cohort definition, reports
pre-cohort REC-5 floor state, estimates per-member REP -> OL -> REC chains if
later implementation is authorized, estimates the cohort-phase package count,
and prepares the Main/Karl checkpoint.

This package has no implementation authority. It creates no EXP, REP, OL, REC,
LCH, registry, schema, validator, central query-layer, runtime, protected-path,
config, dependency, or data artifact. It does not modify the candidate
registry, does not open Path B design, does not author EXP scaffolds, does not
authorize H-011 first-time inclusion or H-012+ registration, does not use
performance-based selection, does not create policy/scoring/ranking/
recommendation/promotion/readiness/lifecycle authority, and does not authorize
an automatic next package.

## Context

WP-S2c-3 locked SS-D:

```text
Cohort then Path B
```

WP-S2c-4 designed the first A2 cohort architecture:

- cohort envelope: minimum 2, default 3, maximum first phase 4;
- exact REC-5 segment authority remains
  `(candidate_id, outcome_kind, pipeline_version, expectation_source_type)`;
- expectation-source symmetry is preferred;
- methodology was deferred to WP-S2c-5.

WP-S2c-5 designed the methodology applied here:

- eligibility hard filters;
- non-performance selection criteria;
- composition rules;
- deterministic tie-breaking;
- output shape.

WP-S2c-6 applies those already-committed rules. Cohort implementation remains
future work and requires separate Main/Karl authorization. Path B remains
deferred. The within-segment `exp_success_criteria` consumer brief remains a
real gap but is outside this package.

## Source Snapshot

- Refreshed `main` commit SHA:
  `6846bd1c7e6d934ce5342007e2e2f51b8e86a41d`.
- Query views listed: 55.
- Integrity views checked: 24.
- Integrity result: every discovered `v_integrity_*` view returned `[]`.
- Candidate registry source: `research/candidate_registry.jsonl` and
  `v_candidate_overview`.
- EXP corpus sources: `research/experiments/*.plan.json`,
  `research/experiments/*.report.json`, and `v_experiment_instances`.
- OL corpus sources: `research/outcome_ledgers/*.outcome_ledger.json` and
  `v_outcome_ledger_candidate_pipeline_summary`.
- REC corpus sources: `research/reconciliations/*.reconciliation.json` and
  `v_reconciliation_candidate_pipeline_summary`.
- REC corpus current count: 26 reconciliation artifacts, `REC-0001` through
  `REC-0026`.
- Package-local output bundle paths: none.

## Methodology References

WP-S2c-6 applies WP-S2c-5 as written. It does not replace or revise the
methodology.

The applied WP-S2c-5 surfaces are:

- eligibility hard filter;
- non-performance selection dimensions;
- forbidden performance and authority criteria;
- composition rules;
- deterministic tie-breaking;
- output shape.

No performance metric, realized metric strength, verdict favorability, policy
posture, paper/live posture, or operational attractiveness is used as a
selection input.

## Eligibility Filter Result

The unit considered is candidate plus pipeline version, with expectation-source
targets recorded separately. Exact REC-5 floor state remains per
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`.

| candidate_id | candidate registry source | candidate/segment unit considered | outcome_kind | pipeline_version | committed EXP provenance present | H-011 first-time inclusion required | H-012+ registration required | OL v1 / REC v1 representable | Path B required | eligibility verdict | reason if excluded |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H-001 | `research/candidate_registry.jsonl` | H-001 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0002` / `research/experiments/EXP-0002.plan.json` | no | no | yes | no | eligible | n/a |
| H-002 | `research/candidate_registry.jsonl` | H-002 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0003` / `research/experiments/EXP-0003.plan.json` | no | no | yes | no | eligible | n/a |
| H-003 | `research/candidate_registry.jsonl` | H-003 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0004` / `research/experiments/EXP-0004.plan.json` | no | no | yes | no | eligible | n/a |
| H-004 | `research/candidate_registry.jsonl` | H-004 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0005` / `research/experiments/EXP-0005.plan.json` | no | no | yes | no | eligible | n/a |
| H-004 | `research/candidate_registry.jsonl` | H-004 / research_oos / post_wp_5b | research_oos | post_wp_5b | yes: `EXP-0011` / `research/experiments/EXP-0011.plan.json` | no | no | yes | no | eligible | n/a |
| H-005 | `research/candidate_registry.jsonl` | H-005 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0001` / `research/experiments/EXP-0001.plan.json` | no | no | yes | no | eligible | n/a |
| H-006 | `research/candidate_registry.jsonl` | H-006 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0006` / `research/experiments/EXP-0006.plan.json` | no | no | yes | no | eligible | n/a |
| H-007 | `research/candidate_registry.jsonl` | H-007 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0007` / `research/experiments/EXP-0007.plan.json` | no | no | yes | no | eligible | n/a |
| H-008 | `research/candidate_registry.jsonl` | H-008 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0008` / `research/experiments/EXP-0008.plan.json` | no | no | yes | no | eligible | n/a |
| H-009 | `research/candidate_registry.jsonl` | H-009 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0009` / `research/experiments/EXP-0009.plan.json` | no | no | yes | no | eligible | n/a |
| H-010 | `research/candidate_registry.jsonl` | H-010 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | yes: `EXP-0010` / `research/experiments/EXP-0010.plan.json` | no | no | yes | no | eligible | n/a |
| H-011 | `research/candidate_registry.jsonl` | no current OL/REC target segment | n/a | n/a | no committed EXP plan for current target segment | yes | no | no current target segment | yes for first-time inclusion path | excluded | Reserved registry slot with no current OL/REC target segment; inclusion would require H-011 first-time inclusion and new EXP scaffold authority. |

Eligibility does not equal selection. The selected cohort is derived below.

## Selection Criteria Application

Evidence-breadth contribution:

- H-004 / post_wp_5b has both exact segments already at
  `reconciliation_count = 3`.
- All pre-WP-5b eligible units for H-001 through H-010 have paired exact
  segments at `reconciliation_count = 1`.
- The methodology therefore favors below-floor pre-WP-5b units for breadth.

Structural coverage:

- Repo metadata exposes `strategy_family`, `timeframe`, `information_inputs`,
  and `pipeline_stage`.
- The selected members broaden candidate/timeframe/family coverage outside the
  already floor-crossed H-004 post-WP-5b single-candidate reference point.
- The selected set covers:
  - H-001: `funding_directional`, `4h`, `ohlcv_4h` plus `funding_8h`;
  - H-005: `momentum`, `1h`, `ohlcv_1h`;
  - H-006: `breakout`, `30m`, `ohlcv_30m`.

EXP provenance readiness:

- Each selected member has committed EXP provenance:
  `EXP-0002`, `EXP-0001`, and `EXP-0006`.
- No selected member requires Path B or new EXP scaffold authoring.

Expectation-source feasibility:

- Each selected member has current REC v1 evidence under both
  `d2_006_gates` and `exp_success_criteria`.
- The future target is paired-source coverage for both source types.
- The `exp_success_criteria` consumer brief gap remains disclosed and is not
  resolved by this package.

Pipeline-version comparability:

- All selected members use `pre_wp_5b`.
- Pipeline versions are recorded explicitly and are not collapsed.

REC-count clarity:

- Current counts are grounded in `v_reconciliation_candidate_pipeline_summary`
  and the committed `research/reconciliations/*.reconciliation.json` corpus.
- Each selected exact segment currently has `reconciliation_count = 1`, below
  the REC-5 floor of `n >= 3`.

## Deterministic Tie-Break Result

Tie-breaking was needed because more than three eligible units exist.

The applied sequence:

1. H-011 was excluded because it lacks a current target segment and would
   require first-time inclusion and EXP scaffold authority.
2. Units without committed EXP provenance, requiring Path B, or requiring
   schema/query/runtime/protected-path work: none among H-001 through H-010.
3. H-004 post-WP-5b was not selected because its paired exact segments are
   already floor-crossed; the package objective is breadth definition, not
   adding more work to a floor-crossed single-candidate reference point.
4. Remaining below-floor pre-WP-5b units were filtered for broader structural
   coverage outside H-004's already represented 1d trend-following reference.
5. The cohort target of 3 was filled with one 4h funding/funding-directional
   unit, one 1h momentum unit, and one 30m breakout unit.
6. Lexical candidate-ID fallback was used only inside structurally comparable
   buckets:
   - 4h funding-aware candidates: H-001 before H-007 and H-010;
   - 1h candidates: H-005 before H-008;
   - 30m candidates: H-006 before H-009.

Lexical ordering is deterministic only. It is not a quality rank.

## Composition Validation

The selected cohort satisfies the WP-S2c-4 envelope:

- total cohort size: 3;
- size is between 2 and 4;
- default target 3 is used;
- all members are eligible;
- each member has exact segment state recorded;
- expectation-source targets are recorded;
- no below-floor aggregation creates a cohort-level claim;
- no selected member requires Path B;
- no selected member requires EXP scaffold authoring;
- no selected member requires H-011 first-time inclusion;
- no selected member requires H-012+ registration.

## Cohort Definition

```text
cohort_id: A2C-001
cohort_label: A2 SS-D first cohort
package_label: WP-12ao / WP-S2c-6
total_cohort_size: 3
```

This cohort definition has no implementation authority.

| candidate_id | candidate/segment unit | outcome_kind | pipeline_version | committed EXP provenance | selected expectation_source_type targets | current reconciliation_count by exact segment | current floor status by exact segment | reason selected under non-performance methodology | partial-source disclosure |
|---|---|---|---|---|---|---|---|---|---|
| H-001 | H-001 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | `EXP-0002` / `research/experiments/EXP-0002.plan.json` | `d2_006_gates`; `exp_success_criteria` | `d2_006_gates`: 1 (`REC-0012`); `exp_success_criteria`: 1 (`REC-0001`) | both below REC-5; each needs 2 additional observations to reach `n = 3` | Adds 4h funding-aware structural coverage with committed EXP provenance and paired current source representation. | none; both current source types are present |
| H-005 | H-005 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | `EXP-0001` / `research/experiments/EXP-0001.plan.json` | `d2_006_gates`; `exp_success_criteria` | `d2_006_gates`: 1 (`REC-0013`); `exp_success_criteria`: 1 (`REC-0002`) | both below REC-5; each needs 2 additional observations to reach `n = 3` | Adds 1h momentum structural coverage with committed EXP provenance and paired current source representation. | none; both current source types are present |
| H-006 | H-006 / research_oos / pre_wp_5b | research_oos | pre_wp_5b | `EXP-0006` / `research/experiments/EXP-0006.plan.json` | `d2_006_gates`; `exp_success_criteria` | `d2_006_gates`: 1 (`REC-0017`); `exp_success_criteria`: 1 (`REC-0006`) | both below REC-5; each needs 2 additional observations to reach `n = 3` | Adds 30m breakout structural coverage with committed EXP provenance and paired current source representation. | none; both current source types are present |

No cohort-level floor status is claimed. Every floor statement above is exact
segment-local.

## Expected Per-Member REP / OL / REC Chain Plan

This section is provisional and non-authoritative. It creates no artifacts and
does not authorize any chain.

If later implementation is separately authorized, each selected member would
follow Path A-style evidence production where the existing committed EXP
supports a future REP -> OL -> REC chain:

| candidate_id | future exact segments | expectation sources targeted | additional observations needed | provisional chain shape |
|---|---|---|---|---|
| H-001 | H-001 / research_oos / pre_wp_5b / `d2_006_gates`; H-001 / research_oos / pre_wp_5b / `exp_success_criteria` | both | 2 per exact segment | Future observation chains would reference existing `EXP-0002`, produce REP evidence, derive OL evidence, and reconcile each targeted source separately. |
| H-005 | H-005 / research_oos / pre_wp_5b / `d2_006_gates`; H-005 / research_oos / pre_wp_5b / `exp_success_criteria` | both | 2 per exact segment | Future observation chains would reference existing `EXP-0001`, produce REP evidence, derive OL evidence, and reconcile each targeted source separately. |
| H-006 | H-006 / research_oos / pre_wp_5b / `d2_006_gates`; H-006 / research_oos / pre_wp_5b / `exp_success_criteria` | both | 2 per exact segment | Future observation chains would reference existing `EXP-0006`, produce REP evidence, derive OL evidence, and reconcile each targeted source separately. |

Package-count estimate:

- strict exact-segment chain estimate: 3 members * 2 expectation-source
  segments * 2 additional observations * 3 packages per REP/OL/REC chain =
  36 packages;
- paired-source reuse estimate, if later explicitly authorized to share a REP
  and OL before separate REC packages: 3 members * 2 additional observations *
  4 packages per paired-source observation set = 24 packages;
- total cohort-phase implementation estimate range: 24 to 36 later packages.

This package does not authorize that runway.

## Checkpoint Decision Surface

After WP-S2c-6 merges, Karl/Main must decide among at least:

1. authorize a bounded cohort implementation runway sized by this cohort
   definition;
2. authorize a cohort implementation runway plus a small parallel or
   sequential WP-S2c-7 `exp_success_criteria` consumer brief;
3. authorize WP-S2c-7 consumer brief first and defer cohort implementation;
4. pause A2 cohort work;
5. request refinement or correction of this cohort definition;
6. redirect to another track;
7. later authorize Path B architecture design only after the cohort-phase
   checkpoint.

No package follows automatically from WP-S2c-6.

## Explicit Non-Claims

WP-S2c-6 does not:

- authorize cohort implementation;
- create REP, OL, REC, EXP, LCH, registry, or canonical artifact files;
- modify the candidate registry;
- modify existing merged artifacts;
- authorize Path B design or execution;
- authorize EXP scaffold authoring;
- authorize H-011 first-time inclusion;
- authorize H-012+ registration;
- change schemas, validators, central query-layer behavior, implementation,
  configs, dependencies, data, runtime, or protected paths;
- use performance-based selection;
- authorize policy/scoring/ranking/recommendation/promotion/readiness/
  lifecycle authority;
- authorize an automatic next package.
