# Scope 6 Query-Layer Extension Design

## 1. Scope

WP-S2c-116 / WP-12ev is a Tier 1 documentation-only design package.

It designs additive read-only query-layer coverage for the three Scope 6 artifact families:

- R2S approval records;
- shadow-evidence retention records;
- S2P approval records.

It creates only this document and updates `docs/project_status.md`.

Validation profile: CS12 T1-doc-narrow.

This package changes no SQL, tests, query-layer code, schemas, validators, artifact instances, runtime paths, protected paths, or existing canonical artifacts.

## 2. Repo-truth basis

WP-S2c-113 locked the three Scope 6 artifact families at artifact-family and required-content level.

WP-S2c-114 introduced:

- `research/schemas/r2s_approval_record.schema.json`;
- `research/schemas/shadow_evidence_retention.schema.json`;
- `research/schemas/s2p_approval_record.schema.json`.

WP-S2c-115 is merged and completed the Scope 6 schema plus validator surface by adding additive validators and tests for those families.

The existing research query layer is read-only and in-memory. It inspects committed repo artifacts and creates no research evidence.

The current Scope 6 artifact families have no required committed instances. Future query-layer views must tolerate zero instances cleanly. Missing future artifact directories are a healthy empty state.

Permanent human gates, Tier 4 boundaries, D2-006, D2-007, REC-5, Phase 9, WP-S2c-100 locked criteria, WP-S2c-113 Scope 6 locks, WP-S2c-114 schemas, WP-S2c-115 validators, SignalProvider Protocol, and Phase 1 paper runtime protection remain unchanged.

## 3. Existing query-layer context

`docs/research_pipeline/2026-04-query_layer.md` defines the query layer as a read-only, in-memory inspection surface over registry, experiment, trial-log, lifecycle, advisory, reconciliation, outcome, and shadow-signal artifacts. It must not create evidence or write to research artifacts.

Representative existing views include:

- `v_candidate_overview`;
- `v_oos_metrics_by_candidate`;
- `v_gate_results_flat`;
- `v_integrity_candidate_refs`;
- `v_shadow_signal_summaries_v2_overview`;
- `v_integrity_shadow_signal_summary_v2_derivation`.

WP-S2c-117 should extend that pattern additively by loading the Scope 6 families as additional read-only relations and exposing proposed base, cross-family, and integrity views.

## 4. New artifact families

R2S approval records:

- schema: `research/schemas/r2s_approval_record.schema.json`;
- expected future artifact directory: `research/r2s_approval_records`;
- expected filename pattern: `*.r2s_approval_record.json`.

Shadow-evidence retention records:

- schema: `research/schemas/shadow_evidence_retention.schema.json`;
- expected future artifact directory: `research/shadow_evidence_retention`;
- expected filename pattern: `*.shadow_evidence_retention.json`.

S2P approval records:

- schema: `research/schemas/s2p_approval_record.schema.json`;
- expected future artifact directory: `research/s2p_approval_records`;
- expected filename pattern: `*.s2p_approval_record.json`.

These directories may be absent. Absence means no committed instances exist and should result in empty relations or empty views, not query-layer failure.

## 5. Design principles

- Read-only inspection only.
- Additive views only.
- Zero-instance safe.
- No artifact creation.
- No validator or schema modifications.
- No mutation of existing views.
- No readiness, transition, approval, gate-execution, ranking, scoring, recommendation, promotion, or policy authority.
- Views may expose records, lineage, references, preservation fields, non-authority flags, and consistency checks.
- Integrity views may detect missing or inconsistent references. They do not approve or reject candidates.

## 6. Proposed relation loading

WP-S2c-117 should add query-layer loading for the three future artifact directories:

- `r2s_approval_records`;
- `shadow_evidence_retention`;
- `s2p_approval_records`.

Missing directories should load as empty relations or otherwise result in empty views without failure, consistent with the existing query-layer idiom for optional artifact families.

Relation loading must not create files. It must not validate beyond query-read requirements. Schema and content validation remain owned by `tools/registry/validate_scope6_packaging.py`.

WP-S2c-117 should decide the exact implementation form from current `tools/research_query` idiom.

## 7. Proposed base views

`v_r2s_approval_records`:

- one row per R2S approval record;
- exposes `approval_record_id`, `candidate_id`, `strategy_or_candidate_family`, `decision_outcome`, `approval_timestamp_utc`, authority flags, preservation fields, and core evidence references in query-friendly form;
- may expose REC-5 segment fields from `rec5_exact_segment_evidence` for inspection only.

`v_shadow_evidence_retention`:

- one row per shadow-evidence retention record;
- exposes `shadow_evidence_id`, `candidate_id`, shadow-window start/end/days, D2-007 threshold constants, observed parity values, disclosure counts, mismatch diagnostic non-authority flags, and `evidence_retention_reference`;
- must not classify parity as readiness or transition sufficiency.

`v_s2p_approval_records`:

- one row per S2P approval record;
- exposes `approval_record_id`, `candidate_id`, `shadow_evidence_id` reference, `decision_outcome`, `approval_timestamp_utc`, `paper_runtime_protection_confirmation`, authority flags, and preservation fields;
- must not authorize or imply paper transition.

Exact column lists may be refined in WP-S2c-117 from schema and query-layer idiom, but column names and view descriptions must avoid readiness, transition, ranking, scoring, recommendation, policy, or promotion semantics.

## 8. Proposed cross-family views

`v_scope6_candidate_packaging_overview`:

- candidate-level inventory overview showing whether records exist in each Scope 6 family;
- may join to `v_candidate_overview` or the base `candidates` relation for registry metadata;
- inventory-only and not readiness;
- must not classify candidates as ready, approved, or transitionable.

`v_s2p_shadow_evidence_links`:

- joins S2P approval records to referenced shadow-evidence retention records where available;
- exposes S2P `approval_record_id`, referenced `shadow_evidence_id`, S2P candidate ID, shadow-evidence candidate ID, and candidate-ID consistency;
- must not authorize paper transition.

Optional additive views if repo idiom supports them:

- `v_r2s_approval_record_refs`, to flatten nested R2S evidence references;
- `v_scope6_artifact_inventory`, if a generic artifact inventory view is cleaner than a candidate overview.

Any optional view must remain read-only and non-authoritative.

## 9. Proposed integrity views

Integrity views are expected to return zero rows in healthy state.

Proposed coverage:

- `v_integrity_r2s_approval_candidate_refs`: R2S candidate IDs must exist in the candidate registry.
- `v_integrity_shadow_evidence_candidate_refs`: shadow-evidence candidate IDs must exist in the candidate registry.
- `v_integrity_s2p_approval_candidate_refs`: S2P candidate IDs must exist in the candidate registry.
- `v_integrity_r2s_rec5_candidate_consistency`: R2S nested REC-5 candidate ID must match top-level candidate ID.
- `v_integrity_s2p_shadow_evidence_refs`: S2P referenced `shadow_evidence_id` should resolve when corresponding shadow-evidence records exist.
- `v_integrity_s2p_shadow_evidence_candidate_consistency`: S2P candidate ID and referenced shadow-evidence candidate ID should match when the referenced record exists.
- `v_integrity_scope6_authority_flags`: records with any forbidden authority flag not false, or any required non-authority true field not true, should surface.
- `v_integrity_scope6_preservation_flags`: records missing required preservation booleans or with non-preserved values should surface.

WP-S2c-117 may combine or split integrity views if repo idiom suggests a cleaner count, but it must preserve this coverage.

## 10. Existing-view integration posture

Existing views must remain unchanged in WP-S2c-117 unless repo truth proves an additive change is unavoidable. If an existing-view mutation is unavoidable, WP-S2c-117 must stop and report because Main authorized additive views only.

New views may join to existing `v_candidate_overview` or the base `candidates` relation for registry metadata.

New views must not alter `v_candidate_overview`, `v_oos_metrics_by_candidate`, gate views, existing integrity views, or query semantics for existing consumers.

## 11. Query-layer documentation update for WP-S2c-117

WP-S2c-117 should update `docs/research_pipeline/2026-04-query_layer.md` if the implementation adds Scope 6 relations or views.

That update should be additive and list the new Scope 6 relations and views. It should state that Scope 6 query-layer support is read-only, tolerates zero instances, creates no artifacts, and grants no approval, readiness, transition, promotion, ranking, scoring, recommendation, policy, runtime, or human-gate execution authority.

Existing query-layer documentation should be preserved.

## 12. Test design for WP-S2c-117

WP-S2c-117 tests should cover:

- zero-instance healthy state;
- view listing includes the new Scope 6 views;
- synthetic temporary fixture instances, not committed canonical artifacts;
- base views return expected rows for valid synthetic R2S, shadow-evidence retention, and S2P payloads;
- cross-family join behavior;
- integrity views return rows for invalid synthetic references or mismatched candidate IDs;
- no committed Scope 6 artifacts are created in `research/`;
- existing query-layer tests continue to pass.

WP-S2c-117 is a T3 implementation package and requires full pytest.

## 13. Non-authority and human-gate preservation

Query views are inspection surfaces only.

View presence, record presence, valid schema shape, validator success, and clean integrity views do not approve, promote, transition, or determine readiness.

Permanent human gates remain absolute.

Approval records document human decisions but do not execute transition machinery.

Shadow-evidence retention supports human review only.

No query-layer view may automate, bypass, weaken, replace, reinterpret, or execute a permanent human gate.

## 14. Explicitly forbidden view shapes

Forbidden examples include:

- `v_candidate_readiness`;
- `v_transition_ready_candidates`;
- `v_gate_approved_candidates`;
- `v_shadow_to_paper_ready`;
- `v_research_to_shadow_ready`;
- `v_candidate_rankings`;
- `v_candidate_scores`;
- `v_candidate_recommendations`;
- any equivalent readiness, transition, approval, ranking, scoring, recommendation, policy, or promotion surface.

## 15. WP-S2c-117 implementation boundary

WP-S2c-117 may modify `tools/research_query/views.sql`, add tests, and update query-layer documentation if this design indicates it.

WP-S2c-117 must be additive.

WP-S2c-117 must not modify schemas or validators.

WP-S2c-117 must not create artifact instances under `research/`.

WP-S2c-117 is T3 implementation with full pytest required.

WP-S2c-117 must stop if implementation needs existing-view mutation, schema changes, validator changes, artifact instances, or any authority surface.

## 16. What this design does not authorize

This design does not authorize:

- SQL or view implementation in this package;
- query-layer code changes in this package;
- tests in this package;
- WP-S2c-117 changes beyond additive read-only views and tests;
- artifact instances;
- schema or validator changes;
- candidate readiness;
- transition authorization;
- human-gate execution;
- Tier 4 contact;
- runtime or protected-path changes;
- monitoring, dashboard, or paper bridge implementation;
- AUTO bridge, A2C-003, or Path B.

## 17. Validation / next-package posture

WP-S2c-116 uses CS12 T1-doc-narrow.

After merge, Side may draft WP-S2c-117 after refreshed-main preflight and no stop trigger.

WP-S2c-117 is T3 implementation with full pytest required.

After WP-S2c-117 merges, Side must stop and report back to Main 4.0 for post-tranche direction.
