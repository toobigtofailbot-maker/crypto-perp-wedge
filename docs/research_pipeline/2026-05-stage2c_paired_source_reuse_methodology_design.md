# Stage 2c Paired-Source Reuse Methodology Design

## Scope

WP-12bj / WP-S2c-21b is a Tier 1 methodology-design package only.

This document designs prospective R1 paired-source reuse. It does not implement
paired-source reuse, does not authorize paired-source reuse use, does not
change H-005, does not open H-006 implementation, and does not change schemas,
validators, query-layer behavior, artifact schemas, tests, runtime behavior,
configs, protected paths, or evidence artifacts.

## Current state and motivation

Current forward-flow strict evidence packages often create separate
`REP -> OL -> REC` chains for different expectation-source types. D2-006 gate
reconciliations and EXP-success reconciliations may sometimes compare the same
underlying candidate run and outcome evidence against different expectation
sources.

When the actual source run and derived outcome evidence are identical,
duplicating REP/OL production can increase work-package count and review
burden. The R1 design goal is to document a safe future method for reducing
duplicated source-evidence production without weakening exact-segment counts,
expectation-source separation, validation, artifact lineage, or authority
boundaries.

This is an efficiency design only. It does not claim existing artifacts are
wrong or require correction.

Repo-truth observations at drafting time:

- REP artifacts identify `plan_id`, `candidate_id`, `trial_ids`, evaluation
  windows, actual bar windows where present, data source and dataset IDs,
  config and dataset hashes where present, gate results, verdict, and
  no-authority notes.
- OL artifacts derive from REP artifacts through `derivation_record`, preserve
  `candidate_id`, `outcome_kind`, `pipeline_version`, evaluation windows,
  source-data references, source-data window notes, metrics, and no-authority
  posture.
- REC artifacts identify `expectation_source_type`,
  `expectation_source_artifact_id`, `expectation_source_artifact_path`,
  source OL lineage, copied realized metrics, comparison results, and
  exact-segment interpretation.
- Current RECs keep D2-006 gate expectations and EXP success criteria as
  separate expectation sources.
- `v_reconciliation_candidate_pipeline_summary` counts exact segments by
  `candidate_id`, `outcome_kind`, `pipeline_version`, and
  `expectation_source_type`.
- Retrospective seed/backfill RECs already include cases where one source OL
  supports both `d2_006_gates` and `exp_success_criteria` RECs. Current forward
  H-001 and H-005 runway packages still use separate REP/OL/REC chains for
  added observations. No current repo document operationally authorizes R1
  paired-source reuse for future forward packages.

## Definition of paired-source reuse

Paired-source reuse is a future methodology where one eligible REP/OL source
chain may support more than one REC, provided each REC remains separate by
`expectation_source_type` and exact segment.

The intended pattern preserves:

- one actual source run;
- one source REP;
- one source OL;
- multiple separate REC artifacts only when eligibility is satisfied;
- separate expectation-source comparisons;
- separate exact-segment counts;
- no count merging.

## Current strict evidence pattern

The current strict forward evidence pattern is:

```text
REP -> OL -> REC for d2_006_gates
REP -> OL -> REC for exp_success_criteria
```

H-001 first-member completion used separate forward evidence chains for the
additional D2 and EXP-success observations. H-005 continues under this strict
pattern unless Main explicitly revises sequencing later.

## Proposed R1 design

The proposed prospective R1 pattern is:

```text
REP -> OL -> REC(d2_006_gates)
          -> REC(exp_success_criteria)
```

Schema-equivalent implementation may use different field names only if a later
approved package explicitly authorizes and validates that behavior. This
pattern is not operational after WP-S2c-21b. It remains design-only until later
approval.

## Eligibility requirements

Future paired-source reuse may be eligible only when all of the following
source-evidence fields match:

- same `candidate_id`;
- same `plan_id` and committed EXP provenance;
- same `outcome_kind`;
- same `pipeline_version`;
- same evaluation-window start and end;
- same actual bar window when present;
- same data source, dataset identifiers, and dataset hash where applicable;
- same config hash where applicable;
- same trial ID and source REP;
- same source OL;
- same no pre-window carry-in and warmup disclosure posture;
- same artifact schema version and validation status;
- no existing REC conflict;
- no package-specific prohibition;
- no active locked methodology conflict.

If any material source-evidence field differs, paired-source reuse is
ineligible.

## Required artifact lineage

Future paired-source reuse must preserve auditable lineage:

- each paired REC must identify the same source OL;
- each paired REC must identify its own `expectation_source_type`;
- each paired REC must identify its own expectation source artifact ID and
  path;
- each paired REC must record that source evidence was reused under
  paired-source methodology if and when that methodology is later approved;
- lineage must be queryable and auditable;
- artifact IDs remain unique;
- REC IDs remain unique;
- source REP/OL artifacts are not mutated in place.

This section is design guidance only. It does not add schema fields now.

## Exact-segment counting rules

Exact-segment counts remain keyed by:

- `candidate_id`;
- `outcome_kind`;
- `pipeline_version`;
- `expectation_source_type`.

A D2 REC increments only the D2 exact segment. An EXP-success REC increments
only the EXP-success exact segment. Counts are not combined across expectation
sources. The REC-5 floor remains per exact segment. Paired-source reuse cannot
create candidate-level or cohort-level authority.

## Expectation-source separation

D2-006 gate expectations and EXP success criteria remain separate expectation
sources.

Each REC must compare realized metrics only against its own expectation source.
A pass/fail result or `overall_verdict` from one expectation source cannot be
copied to another. The same source OL may be reused only as evidence input, not
as a shared conclusion. Cost-drag and unsupported-metric posture must continue
to follow expectation-source-specific REC convention.

## Candidate / window / pipeline constraints

R1 is prospective for H-006 onward only unless Main explicitly changes that
later. H-005 remains strict and unchanged.

R1 cannot bridge:

- different candidates;
- different windows;
- different pipeline versions;
- different outcome kinds;
- different EXP provenance;
- retrospective and forward-flow posture if that distinction affects source
  evidence;
- any package whose active WP forbids paired-source reuse.

## Validation and integrity requirements

Any future implementation package must preserve, at minimum:

- refreshed-main preflight;
- no open competing `docs/project_status.md` PR;
- clean integrity views;
- clean registry validators;
- clean source REP/OL validators;
- clean REC validators;
- correct exact-segment count views;
- duplicate and conflict integrity views clean, or updated only by explicit
  future schema/query package;
- scoped and full pytest unless a future repo-approved validation-tier document
  changes that rule;
- exact changed-file scope.

This design does not reduce validation.

## H-005 preservation

H-005 continues under the strict exact-segment runway. Current repo truth records:

```text
H-005 / research_oos / pre_wp_5b / d2_006_gates = 2
H-005 / research_oos / pre_wp_5b / exp_success_criteria = 1
```

WP-S2c-26 through WP-S2c-34 remain sequential unless Main explicitly revises
sequencing. No paired-source reuse may be applied to H-005 by this document.
H-005 artifacts remain valid strict-pattern precedents.

## H-006+ prospective use

R1 may be considered for H-006 or later only after:

- WP-S2c-21b merges;
- WP-S2c-21c merges;
- Main/Karl re-engages and explicitly approves R1/R2 application;
- a future implementation WP encodes exact allowed behavior.

Until those conditions are met, this document is advisory methodology design
only.

## Interaction with WP-S2c-21c batched-cycle design

WP-S2c-21b designs source reuse. WP-S2c-21c designs package batching. Either
may be approved, modified, or rejected independently.

A combined future pattern may be one batched package creating one REP, one OL,
and multiple separate RECs from the same source evidence, but only if approved
after WP-S2c-21c. WP-S2c-21b alone does not authorize batching.

## Reviewer checklist

A future reviewer deciding whether a proposed paired-source reuse package is
eligible should verify:

- source REP/OL identity;
- candidate match;
- EXP provenance match;
- window match;
- outcome kind match;
- pipeline version match;
- data/config hash match where applicable;
- expectation-source separation;
- exact count effect;
- no duplicate REC conflict;
- no H-005, H-006, Path B, or protected-path unauthorized scope;
- no policy, scoring, ranking, recommendation, readiness, lifecycle,
  approval, promotion/demotion, or downstream authority.

## Stop conditions

Stop if:

- source evidence differs materially;
- exact-segment count cannot be preserved;
- query views cannot distinguish reused source evidence;
- validator behavior would need unapproved change;
- artifact schema would need unapproved change;
- the package would imply H-005 change;
- the package would imply H-006 implementation before approval;
- the package would imply Path B or runtime authority;
- paired-source reuse would blur expectation-source-specific conclusions.

## What is not authorized

This methodology design does not authorize REP, OL, REC, EXP, LCH, schema,
validator, query-layer, implementation, config, dependency, data, runtime,
paper/live, OMS, risk, safe mode, Path B, H-006 implementation,
paired-source reuse implementation, batched-cycle implementation, AUTO
successor work, policy/scoring/ranking/recommendation, approval,
promotion/demotion, readiness, lifecycle, or downstream authority.

## Main/Karl approval gate

R1 remains design-only after this package. WP-S2c-21c must merge next for R2
design. Main/Karl must re-engage after WP-S2c-21c.

No package may apply R1 until explicit approval exists in repo truth or in a
Main/Karl instruction that is then locked into repo truth.
