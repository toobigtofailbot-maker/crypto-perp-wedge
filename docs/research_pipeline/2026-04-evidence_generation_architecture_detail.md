# Evidence-Generation Architecture Detail (WP-10l)

## 9.1 Purpose

WP-10l is a documentation-only architecture-detail package. It defines future mechanics for generating evidence from a segment that a WP-10k-style eligibility matrix marks as `eligible_for_future_evidence_planning`.

WP-10l is candidate-agnostic and uses placeholder worked-example mechanics only. It does not create EXP, REP, OL, or REC artifacts; does not create EXP scaffolds; does not choose candidates, cohorts, or target strategy; and does not implement policy, scoring, ranking, recommendation, paper/live, runtime, or protected-path behavior.

## 9.2 Locked Inputs

- Main 3.0 WP-10l direction decision: evidence-generation architecture detail is the immediate next package and remains documentation-only.
- WP-10k candidate-selection eligibility matrix: `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- WP-10j candidate-selection rule design: `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10i Phase 10 architecture plan: `docs/research_pipeline/2026-04-phase10_architecture_plan.md`.
- WP-10h forward-flow evidence plan: `docs/research_pipeline/2026-04-forward_flow_evidence_plan.md`.
- WP-10g REC-0012 correction.
- REC v1 stability and current 22-row corpus.
- OL v1 stability and current 11-row corpus.
- Lifecycle stability and current 30-row corpus.

## 9.3 Current Machine State

- REC corpus is 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution is 11 `exp_success_criteria` rows and 11 `d2_006_gates` rows.
- REC-5 segment count is 1 for every current `candidate_id / outcome_kind / pipeline_version / expectation_source_type` segment, below the floor.
- OL corpus is 11 rows, `OL-0001` through `OL-0011`.
- LCH corpus is 30 rows, with transition counts 10 / 10 / 10 across `proposed->in_research`, `in_research->research_concluded`, and `research_concluded->archived`.
- Candidate registry exposes `H-001` through `H-011`.
- WP-10k eligibility posture marks current OL/REC target segments for `H-001` through `H-010` as eligible for future evidence planning and marks `H-011` as registry-present with no current OL/REC target segment.
- H-004 remains structurally split under both expectation sources by `pre_wp_5b` and `post_wp_5b` pipeline versions.
- REC-0012 correction is complete; `REC-0012`, `REC-0017`, and `REC-0019` preserve the D2 cost-drag expectation while skipping deterministic cost-drag comparison when `gross_pnl <= 0`.
- No open D2 non-positive-gross-PnL anomaly remains.

## 9.4 Architecture Goal

WP-10l defines mechanics from eligibility matrix output to future evidence artifacts while deferring candidate selection and target strategy to WP-10m. The design makes future EXP, REP, OL, and REC packages narrow and validator-backed, and prevents implicit policy, ranking, scoring, paper/live, runtime, or protected-path drift.

## 9.5 Placeholder Worked-Example Convention

Placeholder notation:

```text
<eligible_segment_X>
<candidate_id_X>
<outcome_kind_X>
<pipeline_version_X>
<expectation_source_type_X>
<future_exp_id_X>
<future_rep_id_X>
<future_ol_id_X>
<future_rec_id_X>
<observation_window_X>
```

Rules:

- Placeholders are not real candidate IDs.
- Placeholders do not imply candidate choice.
- Placeholders do not create fixture artifacts.
- Placeholders are inline narrative only.
- No committed synthetic EXP, REP, OL, or REC instances are created by WP-10l.

## 9.6 Application Flow Overview

```text
Eligibility matrix entry
-> planning gate
-> EXP authoring gate
-> future research/backtest execution gate
-> REP artifact gate
-> OL append gate
-> REC append gate
-> validation and consumer/stability gate
```

| Gate | Input | Output | Future artifact family touched | Future validators required | Forbidden scope | Stop conditions |
|---|---|---|---|---|---|---|
| Planning | WP-10k-style eligibility entry | planning-ready segment descriptor | none | registry, REC, OL, lifecycle, integrity views | candidate choice, ranking, scoring, policy, runtime | eligibility is missing, ambiguous, synthetic, or requires forbidden combining |
| EXP authoring | planning-ready segment descriptor | future EXP artifact | EXP | EXP/schema validators, registry checks | real EXP creation in WP-10l, execution results | missing candidate/outcome/pipeline/source/window binding |
| Research execution | validated future EXP | validated future result set | none or future run evidence | package-specific reproducibility checks | runtime/protected paths, configs, dependencies, metrics in WP-10l | execution package cannot preserve protected boundaries |
| REP artifact | validated result set | future REP artifact | REP | REP/schema validators | synthetic evidence, ranking, policy language | source EXP/result chain incomplete |
| OL append | validated EXP + REP pair | future OL artifact | OL | OL validator and OL integrity views | mutating locked OL rows, policy authority | OL semantics or window provenance ambiguous |
| REC append | validated OL + expectation source | future REC artifact | REC | REC validator and REC integrity views | combining sources, pipelines, H-004 rows, REC policy authority | mapped expectation source or realized metrics are incomplete |
| Validation/consumer stability | validated future EXP/REP/OL/REC artifacts | validation record and optional descriptive consumer/stability update | read-only consumers/stability docs only | all applicable validators, integrity views, pytest, diff checks | policy, ranking, paper/live, runtime authority | tests fail, integrity rows appear, or changed-file scope expands |

## 9.7 Gate 1 - Planning Gate

Input:

```text
<eligible_segment_X> from WP-10k-style eligibility matrix
```

Required checks:

- Eligibility status is descriptive and not a recommendation.
- Segment dimensions are explicit: candidate_id, outcome_kind, pipeline_version, expectation_source_type.
- REC-5 gap is below floor.
- No forbidden dimension combining is needed.
- No selected cohort is implied.

Output:

```text
planning-ready segment descriptor
```

Forbidden scope:

- Candidate recommendation.
- Rank or score.
- EXP plan creation.
- Policy implication.
- Paper/live/runtime implication.

Stop if any segment dimension is missing, if the segment requires combining expectation sources or pipeline versions, or if the descriptor would choose a candidate or cohort.

## 9.8 Gate 2 - EXP Authoring Gate

Input:

```text
planning-ready segment descriptor
```

Future EXP must specify:

- candidate binding;
- outcome_kind;
- pipeline_version;
- expectation_source_type;
- success_criteria;
- D2-006 linkage if used;
- observation window convention;
- data source/version;
- reproducibility path;
- cost/slippage/funding assumptions;
- no execution results.

Output:

```text
future EXP artifact
```

Forbidden in WP-10l:

- Creating an actual EXP file.
- Choosing a real candidate.
- Creating a scaffold.
- Running a backtest.

Stop if an EXP would need schema, validator, runtime, config, or dependency changes not authorized by a later architecture decision.

## 9.9 Gate 3 - Future Research/Backtest Execution Gate

Input:

```text
validated future EXP artifact
```

Future execution package must define:

- run environment;
- data window;
- data version;
- parameter freeze;
- metric computation method;
- cost/slippage/funding treatment;
- reproducibility evidence;
- run logs or equivalent provenance.

Output:

```text
validated future research/backtest result set
```

Forbidden in WP-10l:

- Executing runs.
- Touching runtime/protected paths.
- Modifying configs/dependencies.
- Producing metrics.

Stop if the future execution package would cross runtime, OMS, reconciliation, risk, overlay, safe-mode, live-trading, config, dependency, or protected-path boundaries without explicit authorization.

## 9.10 Gate 4 - REP Artifact Gate

Input:

```text
validated future research/backtest result set
```

Future REP must include:

- source EXP ID;
- candidate ID;
- pipeline version;
- observation/evaluation window;
- realized metrics;
- derivation record;
- limitations;
- no policy or promotion language.

Output:

```text
future REP artifact
```

Forbidden in WP-10l:

- Creating a REP artifact.
- Creating synthetic evidence.
- Performance ranking.

Stop if the result set is not reproducible, the source EXP linkage is missing, or the report would create promotion, demotion, ranking, scoring, recommendation, paper/live, or policy claims.

## 9.11 Gate 5 - OL Append Gate

Input:

```text
validated future EXP + REP pair
```

Future OL append must:

- create a new OL row;
- preserve locked OL v1 rows;
- include candidate, outcome_kind, pipeline_version, and source REP/EXP IDs;
- copy realized metrics according to locked OL semantics;
- preserve observation/evaluation-window semantics;
- pass OL validator and integrity views.

Output:

```text
future OL artifact
```

Forbidden in WP-10l:

- Creating OL artifacts.
- Mutating existing OL rows.
- Using OL as policy authority.

Stop if the OL row would overwrite retrospective windows, duplicate existing evidence, or rely on unmapped metrics.

## 9.12 Gate 6 - REC Append Gate

Input:

```text
validated future OL artifact + expectation source
```

Future REC append must:

- create a new REC row;
- preserve locked REC v1 rows;
- identify expectation_source_type;
- extract expectations from an approved source;
- compare only mapped metrics;
- preserve source, pipeline, and H-004 separation;
- update segment count toward REC-5;
- pass REC validator and integrity views.

Output:

```text
future REC artifact
```

Forbidden in WP-10l:

- Creating REC artifacts.
- Mutating existing REC rows.
- Combining expectation sources.
- Combining pipeline versions.
- Combining H-004 pre/post rows.
- Treating REC as policy authority.

Stop if the future REC append would satisfy REC-5 through forbidden combining, use synthetic evidence, or compare a metric where locked semantics require non-comparison.

## 9.13 Gate 7 - Validation and Consumer/Stability Gate

Input:

```text
validated future EXP/REP/OL/REC artifacts
```

Future validation package must run:

- registry validators;
- EXP/REP validators;
- OL validator;
- REC validator;
- lifecycle regressions;
- all discovered `v_integrity_*` views;
- targeted pytest;
- full pytest where appropriate;
- `git diff --check`;
- changed-file and preservation checks.

Future descriptive consumer/stability package may:

- update read-only consumers;
- update stability locks;
- report REC-5 count deltas;
- report no-policy posture.

Forbidden scope:

- policy;
- ranking;
- scoring;
- recommendation;
- paper/live;
- runtime/protected-path authority.

Stop if any validator fails, any integrity view returns rows, or the package would grant policy, ranking, scoring, recommendation, paper/live, runtime, or protected-path authority.

## 9.14 Observation-Window Mechanics

Every future evidence unit must declare an observation/evaluation window or an explicit no-window convention if the active schema still supports that posture. Future windows must not silently overwrite locked retrospective windows.

Multiple windows for the same segment are separate observations only if:

- data periods are distinct or explicitly justified;
- provenance is distinct;
- the EXP/REP/OL/REC chain is distinct;
- no clone or split of an existing retrospective artifact occurs.

Sequential windows are later, distinct observation periods for the same exact segment. Parallel windows are separately planned observation periods that may run under the same package only when each chain remains independently identified. Overlapping windows require explicit justification because they may reuse market data; they cannot be counted as independent evidence by default.

Rules:

- Overlapping windows require explicit justification.
- No double-counting under REC-5.
- No cross-window performance inference without later design.
- No policy claim from window count alone.

## 9.15 EXP/REP Planning Mechanics

Future EXP requirements:

- success criteria mirroring the existing EXP idiom;
- expectation source mapping;
- candidate binding;
- pipeline version;
- data requirements;
- observation window;
- validation path.

Future REP requirements:

- metric realization;
- source EXP linkage;
- derivation record;
- limitations and non-claims;
- reproducibility references;
- no ranking or policy language.

## 9.16 OL/REC Append Mechanics

- OL append consumes future REP/EXP only.
- REC append consumes future OL plus expectation source only.
- Each append is validator-backed.
- Each append is append-only by default.
- Corrections require explicit correction packages.
- Synthetic OL/REC rows are forbidden.
- Retrospective duplicate rows cannot be created to satisfy REC-5.

## 9.17 Cohort Application Mechanics

If a later package targets more than one segment, each segment has independent gate state. Shared observation windows are allowed only when explicitly documented. A cohort package must report per-segment status and must not aggregate into rankings or recommendations.

Cohort-level validation must include per-segment REC-5 deltas. No cross-segment inference is supported under the REC-5 floor. No strategy-family conclusion is supported unless later design and evidence floors authorize it.

WP-10l names no cohort.

## 9.18 REC-5 Accounting Mechanics

REC-5 floor:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

- Current count is 1 for every current segment.
- A future valid REC append increments only its exact segment.
- Sources do not combine.
- Pipeline versions do not combine.
- H-004 pre/post rows do not combine.
- Consumers do not count as evidence.
- Eligibility does not count as evidence.
- EXP plans do not count as evidence.
- REP without OL/REC append does not count as REC-5 satisfaction.
- REC-5 review requires query verification after append.

## 9.19 H-004 Mechanics

H-004 pre/post remains structural. Future H-004 evidence must specify pipeline version. The current corpus does not support pre/post comparison. Future comparison requires explicit design and sufficient evidence. H-004 cannot be special-cased in WP-10l.

## 9.20 Validation Package Architecture

Future validation package contents:

- pre-edit repo truth;
- changed-file scope;
- schema validation;
- registry validation;
- OL validation;
- REC validation;
- integrity views;
- query regressions;
- REC-5 segment delta check;
- H-004 separation check;
- forbidden-field scan;
- no-policy/no-runtime check;
- pytest;
- diff check;
- preservation hashes.

## 9.21 Stop Conditions for Future Evidence-Generation Packages

Future packages must stop if:

- selected target is not authorized by a prior target-strategy decision;
- evidence is synthetic or cloned;
- source artifact chain is incomplete;
- observation window is ambiguous;
- schema/validator changes are needed without architecture decision;
- REC-5 would be satisfied by forbidden combining;
- policy/ranking/scoring/paper-live/runtime language appears;
- protected paths are touched;
- integrity views become non-empty;
- tests fail.

## 9.22 Forbidden Scope Per Gate

Every gate forbids policy implication, promotion/demotion, ranking/recommendation, evidence-quality scoring, paper/live readiness, runtime/OMS/risk/safe-mode/execution/deployment, configs/dependencies/protected paths, synthetic evidence, and REC-5 dimension combining.

| Gate | Additional forbidden scope |
|---|---|
| Planning | candidate selection, cohort selection, EXP plan creation |
| EXP authoring | actual EXP file creation in WP-10l, scaffolds, real candidate choice |
| Research/backtest execution | run execution, metric production, runtime or config mutation |
| REP artifact | REP creation in WP-10l, synthetic evidence, promotion language |
| OL append | OL creation in WP-10l, mutation of existing OL rows, OL as policy authority |
| REC append | REC creation in WP-10l, source/pipeline/H-004 combining, REC as policy authority |
| Validation and consumer/stability | policy consumers, ranking/scoring consumers, paper/live or runtime authority |

## 9.23 Next Package Boundary

The next package should be WP-10m target-strategy decision, documentation-only. WP-10m should decide candidate-agnostic vs single-candidate vs small-cohort vs staged-cohort strategy.

Preliminary Main 3.0 direction suggests a staged cohort strategy with candidate-agnostic first stage, but WP-10l does not decide it. EXP scaffolds remain forbidden until WP-10m merges and explicitly authorizes moving beyond architecture. WP-10n is the earliest plausible first EXP scaffold, and only if scoped after WP-10m.

## 9.24 Supported Uses

- Future evidence architecture.
- Gate design.
- Observation-window planning.
- EXP/REP/OL/REC transition planning.
- Validation package planning.
- Cohort mechanics planning.
- WP-10m decision support.

## 9.25 Unsupported Claims

- Candidate selection.
- Target strategy decision.
- EXP scaffold creation.
- New evidence creation.
- EXP/REP/OL/REC artifact creation.
- REC-5 satisfaction.
- Policy readiness.
- Promotion/demotion.
- Ranking/recommendation.
- Paper/live readiness.
- Evidence-quality scoring.
- Strategy-family performance conclusion.
- Pipeline-version performance comparison.
- Cross-window inference.
- Runtime/deployment/OMS/risk/safe-mode/execution authority.
- Protected-path authority.

## 9.26 Validation Snapshot

WP-10l package validation results:

- REC validator: PASS.
- REC overview: PASS, 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: PASS, 11 `exp_success_criteria` / 11 `d2_006_gates`.
- REC-5 segment counts: PASS, every current segment count is 1.
- REC integrity views: PASS, `[]`.
- All discovered integrity views: PASS, `[]`.
- OL validator/overview: PASS, 11 rows, `OL-0001` through `OL-0011`.
- Candidate registry validator/overview: PASS, `H-001` through `H-011`.
- Lifecycle validator/overview: PASS, 30 rows and transitions 10 / 10 / 10.
- Targeted tests: PASS, 200 passed and 213 deselected.
- Full pytest: PASS, 413 passed with 4 Pandas deprecation warnings.
- `git diff --check`: PASS.

## 9.27 Non-Claims

WP-10l does not create:

- selected candidate or cohort;
- target-strategy decision;
- EXP scaffold;
- EXP/REP/OL/REC artifact;
- synthetic fixture artifact;
- schema change;
- validator change;
- query-layer view;
- REC-5 satisfaction;
- policy;
- scoring;
- ranking/recommendation;
- paper/live semantics;
- runtime/deployment/OMS/risk/safe-mode/execution authority;
- protected-path authority.
