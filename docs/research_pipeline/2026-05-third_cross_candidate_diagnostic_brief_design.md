# Third Cross-Candidate Diagnostic Brief Design

## 1. Scope

WP-S2c-132 / WP-12fl is a Tier 1 documentation-only design package.

It designs the third cross-candidate diagnostic brief against the current eleven-concluded-candidate state with H-012 included. This package creates only this design document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package changes no SQL, query outputs, brief, helper, tests, tools, schemas, validators, query views, canonical artifacts, runtime paths, or protected paths.

## 2. Authorization basis

Main 4.0 authorized a third cross-candidate diagnostic brief tranche after WP-S2c-131 / WP-12fk.

The authorized tranche is:

- WP-S2c-132 / WP-12fl: design only.
- WP-S2c-133: query execution and brief authoring.

Mandatory Main/Karl re-engagement occurs after WP-S2c-133 report-back. WP-S2c-132 selects no post-brief direction.

## 3. Repo-truth basis

Current repo truth records eleven concluded candidates: H-001 through H-010 plus H-012. All eleven concluded candidates are `NO-GO`.

H-011 remains a reserved draft slot in `research/candidate_registry.jsonl`: `status=DRAFT`, `overall_verdict=PENDING`, `pipeline_stage=reserved`, and `decision_record_path=null`.

H-012 is the first concluded candidate added after the WP-S2c-119 ten-candidate state. It is also the first post-WP-S2c-100-locks candidate and the first concluded candidate under canonical locked Option B framing.

H-012 artifacts include:

- `research/experiments/EXP-0012.plan.json`
- `research/experiments/REP-0032.report.json`
- `research/outcome_ledgers/OL-0032.outcome_ledger.json`
- `research/reconciliations/REC-0051.reconciliation.json`
- `research/decisions/DEC-0011.md`

H-012 evidence records 1/8 D2-006 gates passed, liquidation to zero equity, negative OOS Sharpe, 100% max drawdown, and REC-0051 `none_met`.

WP-S2c-127b refined `v_integrity_plan_report_pairs` to allow bounded pre-execution EXP-without-REP state only for known pending pre-registered candidates with no trial evidence or decision record. H-012 later moved beyond that interval through REP, OL, REC, and DEC artifacts.

Existing briefs are historical records and must not be modified.

## 4. Prior brief precedent

WP-6e established the first cross-candidate diagnostic brief pattern:

- brief under `research/briefs/`;
- committed `queries/Q*.sql`;
- committed `outputs/Q*.json`;
- package-local `run_all_queries.py`;
- factual claims grounded in committed query outputs;
- before/after checksum posture over existing research artifacts and query-layer files;
- no candidate recommendation.

WP-S2c-118 and WP-S2c-119 established the design-plus-execution split for the second brief. WP-S2c-119 used committed Q*.sql, Q*.json, and `run_all_queries.py`, and used a diff-focused structure against WP-6e.

WP-S2c-133 should preserve that evidence discipline and use a diff-focused structure against WP-S2c-119.

## 5. Diagnostic objective

WP-S2c-133 should describe the current cross-candidate state with H-012 included.

It should exercise existing pre-Scope 6 views, Scope 6 views from WP-S2c-117, and the WP-S2c-127b integrity refinement through committed query outputs.

It should compare current state to WP-S2c-119 without modifying WP-S2c-119.

It should produce durable analytical evidence for future Main/Karl routing.

It must not recommend, rank, score, select, approve, transition, or determine readiness for any candidate. It must not recommend Path B continuation or termination.

## 6. Differences from WP-S2c-119

Material differences since WP-S2c-119:

- H-012 was added and concluded `NO-GO`.
- The concluded candidate count moves from 10 to 11.
- H-012 introduces `ohlcv_15m` plus `funding_8h` under locked Option B.
- H-012 adds post-WP-S2c-100-locks and post-WP-S2c-123 Option B evidence.
- H-012 adds EXP-0012, REP-0032, OL-0032, REC-0051, and DEC-0011.
- WP-S2c-127a/b integrity refinement landed mid-tranche.
- Scope 6 remains zero-instance; H-012 did not create shadow evidence or approval records.
- C/F remain deferred; monitoring/dashboard deferred; paper bridge unauthorized.

The third brief should be shorter and diff-focused, not a full system re-explanation.

## 7. Evidence layout for WP-S2c-133

WP-S2c-133 should use this dated layout unless refreshed repo truth requires a narrow adjustment:

- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief.md`
- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/queries/Q01.sql` through `QNN.sql`
- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/outputs/Q01.json` through `QNN.json`
- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief/run_all_queries.py`
- `docs/research_pipeline/README.md` additive pointer in WP-S2c-133 only.
- `docs/project_status.md` entry in WP-S2c-133.

If refreshed repo convention strongly prefers `2026-05` because this design artifact is May-dated, WP-S2c-133 may use `2026-05-third_cross_candidate_diagnostic_brief`. Otherwise, prefer `2026-06` because the current package date and H-012 DEC/checkpoint completion are June 2026. WP-S2c-133 must verify existing directory names before choosing.

## 8. Helper convention

WP-S2c-133 should use `run_all_queries.py`.

The helper must:

- run all package-local `queries/Q*.sql` files through the existing read-only query CLI;
- write only into the package-local `outputs/` directory;
- regenerate outputs deterministically;
- create or modify no canonical artifacts;
- remain a package-local reviewer convenience, not a general framework.

## 9. Proposed query set

WP-S2c-133 should use a concise query set. It may adapt the WP-S2c-119 Q01-Q12 pattern and add H-012/diff-specific coverage. The initial design is Q01-Q14:

| Query | Purpose | Expected source | Output | Brief section | Non-authority note |
|---|---|---|---|---|---|
| Q01 | Candidate inventory/status distribution with H-012 included | `v_candidate_overview` | `outputs/Q01.json` | population/status | inventory only |
| Q02 | Concluded candidate distribution by verdict/family/timeframe | `v_concluded_candidates` | `outputs/Q02.json` | outcome distribution | descriptive only |
| Q03 | Diff snapshot versus WP-S2c-119-era state using current artifact identifiers and counts | registry/query outputs; no historical mutation | `outputs/Q03.json` | what changed | no recommendation |
| Q04 | D2-006 gate failure/pass pattern across experiment reports including REP-0032 | `v_gate_results_flat` or current gate view | `outputs/Q04.json` | gate patterns | gate counts do not imply readiness |
| Q05 | Strategy-family/timeframe coverage matrix including H-012 15m trend_following | current candidate views | `outputs/Q05.json` | search-space coverage | not a priority queue |
| Q06 | Information-input coverage including `ohlcv_15m` and `funding_8h` | `v_information_inputs` or current input view | `outputs/Q06.json` | input coverage | not scoring |
| Q07 | H-012 artifact chain summary from registry/EXP/REP/OL/REC/DEC references where exposed | current query layer views | `outputs/Q07.json` | H-012 delta | not re-verdicting |
| Q08 | Outcome-ledger / reconciliation distribution including H-012 segment count | OL/REC views | `outputs/Q08.json` | REC posture | no cross-segment inference |
| Q09 | Full discovered `v_integrity_*` sweep | all integrity views | `outputs/Q09.json` | integrity | clean integrity is not approval |
| Q10 | Scope 6 base views zero-instance rows | Scope 6 base views | `outputs/Q10.json` | Scope 6 exercise | empty state is not candidate finding |
| Q11 | Scope 6 inventory/link views zero-instance behavior | Scope 6 inventory/link views | `outputs/Q11.json` | Scope 6 exercise | no transition check |
| Q12 | Scope 6 integrity views zero rows | Scope 6 integrity views | `outputs/Q12.json` | Scope 6 integrity | no readiness authority |
| Q13 | Query-layer footprint/current view count including WP-S2c-127b-refined integrity surface | query metadata/list-views or information_schema | `outputs/Q13.json` | query-layer observations | view presence grants no authority |
| Q14 | REC-5 exact segment counts for H-012 and broader current REC corpus | REC/query views | `outputs/Q14.json` | REC-5 posture | no cross-segment inference |

If current query views cannot support one query cleanly without modifying views, WP-S2c-133 must either narrow the query to available views or stop and report. It must not modify query views.

## 10. Query constraints

Queries must obey these constraints:

- No hardcoded candidate IDs except where explicitly bounded to the H-012 delta section or fixed known artifact references required by this design.
- Default to deriving identifiers from query results.
- No candidate-ranking, scoring, selection, readiness, approval, promotion, transitionability, or recommendation queries.
- No query may compute a next-candidate recommendation.
- No mutation.
- No external data.
- No ad-hoc file-reading functions outside the read-only query layer.
- Queries must be executable through the repo-local read-only query CLI.
- Queries must not automate or weaken human gates.
- Queries must not create a Path B continuation/termination recommendation.

## 11. Scope 6 zero-instance exercise

WP-S2c-133 should verify that Scope 6 base, link, inventory, and integrity views remain clean and zero-instance unless repo truth changes.

Empty Scope 6 state is a query-layer discipline check, not a candidate finding.

H-012 did not create shadow evidence, R2S approval, S2P approval, or retained shadow evidence.

Clean Scope 6 integrity grants no readiness or transition authority.

## 12. WP-S2c-127b integrity-refinement exercise

WP-S2c-133 should include an integrity sweep that covers `v_integrity_plan_report_pairs`.

The brief should note that H-012 moved through the pre-execution EXP-without-REP interval and now has REP/OL/REC/DEC evidence.

The refinement is not an approval mechanism; it is integrity semantics only.

## 13. Brief structure for WP-S2c-133

WP-S2c-133 should use a diff-focused structure:

1. Methodology
2. What changed since WP-S2c-119
3. Current candidate population / status distribution
4. H-012 delta and artifact chain
5. Outcome and D2-006 gate-pattern snapshot
6. Search-space and information-input coverage
7. Outcome-ledger / reconciliation / REC-5 posture
8. Scope 6 query-layer exercise
9. Data integrity / read-only checks
10. Query-layer observations
11. Deferred items unchanged
12. Scope-explicit non-findings
13. Artifacts in this directory
14. What this brief enables for Main/Karl routing

Every factual claim must cite a committed query output.

## 14. Claim-grounding rules

Every current-state factual claim in the WP-S2c-133 brief must cite a specific committed `Q*.json` output.

Prior docs can be cited for context, but not as substitutes for current query results.

If a claim cannot be grounded in query output, remove the claim or add a query in WP-S2c-133.

Do not infer from prior prose where query output is available.

No empty Scope 6 result may be interpreted as readiness.

No unsupported causal claim is allowed.

## 15. Read-only / checksum posture

WP-S2c-133 validation should include:

- before/after checksums for existing research artifacts and query-layer files, excluding newly created brief package files and intended README/project-status updates;
- confirmation that no existing canonical research artifacts changed;
- `git diff --check`;
- read-only query CLI list-views;
- all discovered `v_integrity_*` views return `[]`;
- `run_all_queries.py` regenerates outputs deterministically;
- committed outputs match helper output;
- T1-doc-narrow validation, not full pytest unless repo guidance or a stop trigger requires it.

## 16. Non-prescriptive boundary

The brief is diagnostic only.

It does not recommend a candidate. It does not rank or score candidates. It does not determine readiness.

It does not authorize research-to-shadow, shadow-to-paper, paper-to-live, or live transition.

It does not recommend Path B continuation or termination.

It does not execute or replace human gates.

It may inform future Main/Karl routing only after report-back.

## 17. Explicitly forbidden query and brief shapes

WP-S2c-133 must not create query names, output names, sections, or narrative frames such as:

- candidate readiness query;
- transition-ready query;
- gate-approved candidate query;
- top candidate query;
- recommended next candidate query;
- candidate ranking query;
- candidate score query;
- paper bridge readiness query;
- continue Path B query;
- stop Path B query;
- recommendation section;
- selection section;
- approval section;
- readiness section;
- transition authorization section;
- promotion queue.

Equivalent readiness, transition, approval, ranking, scoring, recommendation, promotion, policy, or route-selection surfaces are also forbidden.

## 18. WP-S2c-133 implementation boundary

WP-S2c-133 may:

- create the brief markdown file;
- create the dated brief subdirectory with query SQL files, output JSON files, and helper;
- update `docs/research_pipeline/README.md` with a single additive pointer;
- update `docs/project_status.md`;
- run read-only query-layer commands and commit outputs.

WP-S2c-133 must not:

- modify `tools/research_query`;
- modify views;
- modify tests;
- modify schemas or validators;
- modify existing briefs;
- modify existing canonical artifacts;
- create Scope 6 artifact instances;
- run backtests;
- pre-register candidates;
- recommend, rank, score, select, continue, or terminate Path B.

## 19. Stop conditions for WP-S2c-133

WP-S2c-133 must stop and report if:

- any integrity view returns non-empty rows;
- a query result requires modification of an existing canonical artifact to interpret;
- query execution requires modifying views, tools, schemas, validators, or tests;
- the brief cannot be coherent without recommending a specific next candidate or recommending Path B continuation/termination;
- any factual claim cannot be grounded in committed query output;
- the brief surfaces tension with locked criteria or locked decisions;
- Scope 6 zero-instance interpretation risks becoming readiness/transition language;
- Main/Karl/Karl override or standing boundary halt applies.

## 20. Report-back requirement

After WP-S2c-133 merges, Side must stop and report to Main/Karl.

No post-brief direction is authorized by WP-S2c-132 or WP-S2c-133.

Main/Karl will route post-brief direction from the surfaced diagnostic evidence.
