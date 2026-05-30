# Cross-Candidate Diagnostic Brief Design

## 1. Scope

WP-S2c-118 / WP-12ex is a Tier 1 documentation-only design package.

It designs the second cross-candidate diagnostic brief. It creates only this design document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package changes no SQL, query outputs, brief, helper, tests, tools, schemas, validators, query views, canonical artifacts, runtime paths, or protected paths.

## 2. Repo-truth basis

WP-S2c-117 is merged and completed the Scope 6 query-layer extension.

The Scope 6 surface is complete at schema, validator, and read-only query-layer level:

- WP-S2c-113 locked the Scope 6 artifact-family and required-content decisions.
- WP-S2c-114 introduced `research/schemas/r2s_approval_record.schema.json`, `research/schemas/shadow_evidence_retention.schema.json`, and `research/schemas/s2p_approval_record.schema.json`.
- WP-S2c-115 introduced `tools/registry/validate_scope6_packaging.py`.
- WP-S2c-117 introduced Scope 6 query-layer relations, base views, link/inventory views, integrity views, documentation, and tests.

Related current repo-truth anchors:

- WP-S2c-100 locked refined approval/readiness criteria.
- WP-S2c-104 locked the implementation authorization decision.
- WP-S2c-105 through WP-S2c-110 completed the bounded shadow adapter plus parity tooling tranche.
- The first cross-candidate diagnostic brief exists at `research/briefs/2026-04-cross_candidate_diagnostic.md`.
- Existing briefs are historical records and must not be modified.

## 3. WP-6e precedent

WP-6e established the first cross-candidate diagnostic pattern:

- authored synthesis file under `research/briefs/`;
- committed `queries/Q*.sql`;
- committed `outputs/Q*.json`;
- package-local rerun helper;
- factual claims cite committed query outputs;
- no candidate recommendation;
- no candidate introduction;
- no backtest rerun;
- before/after checksum posture over existing research artifacts and query-layer files.

Repo-truth tension: the current package brief mentions `run_all_queries.sh`, while the WP-6e precedent uses `run_all_queries.py`. WP-S2c-119 should preserve `run_all_queries.py` unless refreshed repo truth or explicit cross-platform constraints justify a shell helper. This design chooses `run_all_queries.py` as the default because it matches the existing precedent and the repo-local Python query CLI.

## 4. Diagnostic objective

The second brief should describe the current cross-candidate state after query-layer expansion.

It should be diagnostic and descriptive only. It should update cross-candidate context since WP-6e, exercise existing pre-Scope 6 views plus the new Scope 6 views, and verify that Scope 6 views answer cleanly under the current zero-instance state.

It should produce durable analytical evidence in `research/briefs/` for future bounded self-improvement consumers.

It must not recommend, rank, score, select, approve, or determine readiness for any candidate.

## 5. Differences from WP-6e

WP-S2c-119 should be diff-focused rather than a broad system recap.

Material repo changes since WP-6e include:

- locked approval/readiness criteria expanded in WP-S2c-100;
- implementation authorization locked in WP-S2c-104;
- bounded shadow adapter and parity tooling tranche completed in WP-S2c-105 through WP-S2c-110;
- Scope 6 schema, validator, and query surfaces landed in WP-S2c-114, WP-S2c-115, and WP-S2c-117;
- query-layer integrity coverage grew beyond the first WP-6e surface.

The second brief should preserve WP-6e evidence discipline while staying shorter and more focused on what changed.

## 6. Evidence layout for WP-S2c-119

WP-S2c-119 should use this dated package layout unless refreshed repo truth requires a narrow adjustment:

- `research/briefs/2026-05-cross_candidate_diagnostic_brief.md`
- `research/briefs/2026-05-cross_candidate_diagnostic_brief/queries/Q01.sql` through `QNN.sql`
- `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q01.json` through `QNN.json`
- `research/briefs/2026-05-cross_candidate_diagnostic_brief/run_all_queries.py`

The README pointer, if added in WP-S2c-119, should point to this brief and its adjacent query/output directory.

## 7. Helper convention

WP-S2c-119 should use `run_all_queries.py`.

The helper should:

- run every `queries/Q*.sql` file through `tools.research_query.run` or the current repo-local read-only query CLI;
- regenerate matching `outputs/Q*.json` files deterministically;
- write only inside the brief package `outputs/` directory;
- create or modify no canonical artifacts;
- remain a simple reviewer convenience, not a new framework.

## 8. Proposed query set

The WP-S2c-119 query set should be concise. Twelve queries are sufficient unless refreshed repo truth requires a small adjustment.

| Query | Purpose | Expected named views used | Output | Brief section supported | Non-authority note |
|---|---|---|---|---|---|
| Q01 | Candidate inventory and current status distribution | `v_candidate_overview` | `outputs/Q01.json` | Current candidate population / status distribution | Inventory only; no selection. |
| Q02 | Concluded candidate distribution and comparison posture to WP-6e | `v_concluded_candidates` | `outputs/Q02.json` | What changed since WP-6e; outcome snapshot | Descriptive only; no re-verdict. |
| Q03 | Outcome and verdict distribution | `v_concluded_candidates`, `v_outcome_ledger_candidate_pipeline_summary` where useful | `outputs/Q03.json` | Outcome and gate-pattern snapshot | No recommendation or ranking. |
| Q04 | Gate failure and gate pattern snapshot comparable to WP-6e | `v_gate_results_flat` | `outputs/Q04.json` | Outcome and gate-pattern snapshot | Gate counts do not imply readiness. |
| Q05 | Search-space coverage by strategy family and timeframe | `v_candidate_by_family`, `v_candidate_overview` | `outputs/Q05.json` | Search-space and information-input coverage | Coverage is not a priority queue. |
| Q06 | Information-input coverage | `v_information_inputs` | `outputs/Q06.json` | Search-space and information-input coverage | No scoring by input type. |
| Q07 | Query-layer view inventory and count, including Scope 6 views | query-layer metadata/listing or `information_schema` over registered views | `outputs/Q07.json` | Query-layer observations | View presence grants no authority. |
| Q08 | Integrity sweep over all discovered `v_integrity_*` views | all `v_integrity_*` views | `outputs/Q08.json` | Data integrity / read-only checks | Clean integrity is not approval. |
| Q09 | Scope 6 base views zero-instance rows | `v_r2s_approval_records`, `v_shadow_evidence_retention`, `v_s2p_approval_records` | `outputs/Q09.json` | Scope 6 query-layer exercise | Empty state is healthy unless repo truth changes. |
| Q10 | Scope 6 inventory and link views zero-instance behavior | `v_scope6_candidate_packaging_overview`, `v_s2p_shadow_evidence_links` | `outputs/Q10.json` | Scope 6 query-layer exercise | Inventory/link checks are not transition checks. |
| Q11 | Scope 6 integrity views zero rows | `v_integrity_r2s_approval_candidate_refs`, `v_integrity_shadow_evidence_candidate_refs`, `v_integrity_s2p_approval_candidate_refs`, `v_integrity_r2s_rec5_candidate_consistency`, `v_integrity_s2p_shadow_evidence_refs`, `v_integrity_s2p_shadow_evidence_candidate_consistency`, `v_integrity_scope6_authority_flags`, `v_integrity_scope6_preservation_flags` | `outputs/Q11.json` | Scope 6 query-layer exercise; data integrity | Clean Scope 6 integrity grants no readiness. |
| Q12 | Optional diff-focused current view/integrity footprint summary | query-layer metadata/listing plus grouped view-name patterns | `outputs/Q12.json` | What changed since WP-6e; query-layer observations | Do not hardcode historical conclusions as current facts. |

Query constraints:

- No hardcoded candidate identifiers unless unavoidable for a clearly bounded historical-artifact lookup; default to no hardcoded IDs.
- Candidate IDs should come from query results.
- No query should compute readiness, promotion, transitionability, ranking, scoring, recommendation, or candidate selection.
- No query should mutate anything.
- No query should use external data or file-reading functions through ad-hoc SQL.
- Queries should be executable through the read-only query layer.

## 9. Scope 6 zero-instance exercise

Zero Scope 6 instances are expected and healthy unless repo truth changes before WP-S2c-119.

WP-S2c-119 should document the empty Scope 6 state as a query-layer discipline check, not as a negative finding about candidates. Clean Scope 6 integrity views do not imply readiness or transition authority.

Scope 6 artifact absence means no R2S approval records, S2P approval records, or retained shadow-evidence records exist yet. It does not score, rank, approve, reject, or select candidates.

## 10. Brief structure for WP-S2c-119

The second brief should use this structure:

1. Methodology
2. What changed since WP-6e
3. Current candidate population / status distribution
4. Outcome and gate-pattern snapshot
5. Search-space and information-input coverage
6. Scope 6 query-layer exercise
7. Data integrity / read-only checks
8. Query-layer observations
9. Scope-explicit non-findings
10. Artifacts in this directory
11. What this brief enables for future packages

The brief should be concise and diff-focused. Every factual claim should cite a committed `Q*.json` output.

## 11. Claim-grounding rules

Every factual claim in the WP-S2c-119 brief must cite a specific committed query output.

Prior repo docs may be cited for context, but not as substitutes for current query results. If a current-state claim cannot be grounded in a `Q*.json` output, WP-S2c-119 should remove the claim or add a query.

No empty Scope 6 view may be interpreted as candidate readiness. No unsupported causal claim should be included.

## 12. Read-only / checksum posture

WP-S2c-119 validation should include:

- before/after checksums for existing research artifacts and query-layer files, excluding newly created brief package files and intended README/project-status updates;
- explicit confirmation that no existing canonical research artifacts changed;
- `git diff --check`;
- `.venv\Scripts\python.exe -m tools.research_query.run --list-views`;
- all discovered `v_integrity_*` views return `[]` before final brief claims are accepted;
- `run_all_queries.py` regenerates outputs deterministically;
- committed outputs match helper output;
- T1-doc-narrow validation, not full pytest unless repo guidance or a stop trigger requires it.

## 13. Non-prescriptive boundary

The brief is diagnostic only.

It does not recommend a candidate. It does not rank or score candidates. It does not determine readiness. It does not authorize research-to-shadow, shadow-to-paper, paper-to-live, or live transition.

It does not execute or replace human gates. It does not modify locked criteria or decisions.

It may inform future Main/Karl routing only after report-back.

## 14. Explicitly forbidden query and brief shapes

WP-S2c-119 must not create queries, outputs, helper names, sections, or narrative frames such as:

- candidate readiness query;
- transition-ready query;
- gate-approved candidate query;
- top candidate query;
- recommended next candidate query;
- candidate ranking query;
- candidate score query;
- paper bridge readiness query;
- recommendation section;
- selection section;
- approval section;
- readiness section;
- transition authorization section;
- promotion queue.

Equivalent readiness, transition, approval, ranking, scoring, recommendation, promotion, or policy surfaces are also forbidden.

## 15. WP-S2c-119 implementation boundary

WP-S2c-119 may:

- create the brief markdown file;
- create the dated brief subdirectory with query SQL files, output JSON files, and helper;
- update `docs/research_pipeline/README.md` with a single additive pointer;
- update `docs/project_status.md`;
- run read-only query-layer commands and commit outputs.

WP-S2c-119 must not:

- modify `tools/research_query`;
- modify views;
- modify tests;
- modify schemas or validators;
- modify existing briefs;
- modify existing canonical artifacts;
- create Scope 6 artifact instances;
- recommend, rank, score, or select candidates;
- authorize readiness or transitions.

## 16. What this design does not authorize

This design does not authorize:

- query execution in this package;
- query SQL creation in this package;
- output JSON creation in this package;
- brief authoring in this package;
- helper creation in this package;
- README update in this package;
- artifact creation in this package;
- tool, test, schema, validator, or view changes;
- candidate recommendation;
- readiness determination;
- transition authorization;
- human-gate execution;
- Tier 4 contact;
- runtime/protected-path work;
- monitoring, dashboard, or paper bridge implementation;
- AUTO bridge;
- A2C-003;
- Path B.

## 17. Validation / next-package posture

WP-S2c-118 uses CS12 T1-doc-narrow.

After merge, Side may draft WP-S2c-119 after refreshed-main preflight and no stop trigger.

WP-S2c-119 uses CS12 T1-doc-narrow with before/after checksum verification and deterministic output regeneration.

After WP-S2c-119 merges, Side must stop and report back to Main 4.0 for post-tranche direction.
