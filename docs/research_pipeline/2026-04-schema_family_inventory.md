# Schema Family Inventory (WP-9c)

## Purpose

This inventory records the repo-truth evidence supporting WP-9c schema
versioning discipline.

It is a current-state snapshot only. It has no behavioral authority and does
not authorize schema, validator, artifact, query-layer, helper, test, runtime,
policy, deployment, OMS, risk, overlay, safe-mode, or live-trading changes.

## Inventory Method

Schema files were enumerated with:

```powershell
Get-ChildItem research/schemas -Filter *.schema.json
```

For each schema, WP-9c inspected `$schema`, `$id`, `title`, required top-level
fields, `schema_version` posture, and possible equivalent top-level markers.

Validator modules were inspected under:

```text
tools/registry/
```

Query-layer coverage was inspected in:

```text
tools/research_query/query_layer.py
tools/research_query/views.sql
```

Committed instance paths were checked under `research/` by artifact-family
directory. WP-9c did not modify any inspected file.

## Inventory Table

| Schema path | Family / artifact type | Explicit schema_version? | Version marker / equivalent marker | Validator module | Committed instance path(s) | Query-layer relation/view exposure | Classification | Retrofit priority | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `research/schemas/agent_output.schema.json` | Advisory agent output / AOUT | No | `agent_type` identifies `REGIME_SCORING`, but is not a schema version marker | `tools/registry/validate_agent_outputs.py` | `research/agent_outputs/*.agent_output.json` | `agent_outputs`, `v_agent_outputs_overview`, `v_agent_outputs_latest`, `v_integrity_agent_output_refs` | `retrofit-candidate` | Medium | Active advisory/query family without explicit version marker. |
| `research/schemas/bucket_mapping.schema.json` | Advisory bucket mapping / BMAP | No | `agent_type` identifies source advisory family, but is not a schema version marker | `tools/registry/validate_bucket_mappings.py` | `research/bucket_mappings/*.bucket_mapping.json` | `bucket_mappings`, `v_bucket_mappings_overview`, `v_bucket_mappings_latest`, `v_integrity_bucket_mapping_refs` | `retrofit-candidate` | Medium | Active advisory/query family without explicit version marker. |
| `research/schemas/candidate_registry.schema.json` | Candidate registry | No | `pipeline_stage` is a status vocabulary, not a schema version marker | `tools/registry/validate_registry.py` | `research/candidate_registry.jsonl` | `candidates`, `v_candidate_overview`, `v_concluded_candidates`, `v_candidate_by_family`, `v_information_inputs` | `retrofit-candidate` | High | Decision 10 identifies this as a schema-version-posture candidate. |
| `research/schemas/decision_change.schema.json` | Decision Change / DCH | No | No equivalent schema version marker | `tools/registry/validate_decision_changes.py` | `research/decision_changes/*.decision_change.json` | `decision_changes`, `v_decision_changes_overview`, `v_stage_transitions`, `v_integrity_decision_refs` | `retrofit-candidate` | High | DCH pipeline-stage vocabulary differs from Phase 9 lifecycle vocabulary. |
| `research/schemas/experiment_plan.schema.json` | Experiment Plan / EXP | No | No equivalent schema version marker | `tools/registry/validate_experiment_artifacts.py` | `research/experiments/*.experiment_plan.json` | `exp_plans`, `v_experiment_instances`, `v_integrity_plan_report_pairs`, `v_integrity_candidate_refs` | `retrofit-candidate` | Medium | Legacy research evidence family without explicit version marker. |
| `research/schemas/experiment_report.schema.json` | Experiment Report / REP | No | No equivalent schema version marker | `tools/registry/validate_experiment_artifacts.py` | `research/experiments/*.experiment_report.json` | `exp_reports`, `v_experiment_instances`, metric/gate views, integrity views | `retrofit-candidate` | Medium | Legacy research evidence family without explicit version marker. |
| `research/schemas/lifecycle_change.schema.json` | Lifecycle Change / LCH | Yes, required | `schema_version` const `v1` | `tools/registry/validate_lifecycle_changes.py` | None currently; missing `research/lifecycle_changes/` is healthy empty state | `lifecycle_changes`, `v_lifecycle_change_overview`, `v_lifecycle_state_transitions`, LCH integrity views | `phase9-explicit-v1` | None | First Phase 9 schema follows Decision 10 from v1. |
| `research/schemas/macro_window_agent_output.schema.json` | Macro window advisory output / MOUT | No | No equivalent schema version marker | `tools/registry/validate_macro_window_agent_outputs.py` | `research/macro_window_agent_outputs/*.macro_window_agent_output.json` | `macro_window_agent_outputs`, overview/latest views, fixture-check integrity view | `retrofit-candidate` | Medium | Active advisory/query family without explicit version marker. |
| `research/schemas/outcome_ledger.schema.json` | Outcome Ledger / OL | Yes, required | `schema_version` const `v1` | `tools/registry/validate_outcome_ledger.py` | `research/outcome_ledgers/OL-*.outcome_ledger.json` | `outcome_ledgers`, `v_outcome_ledger_overview`, `v_outcome_ledger_candidate_pipeline_summary`, outcome-ledger integrity views | `phase9-explicit-v1` | None | Outcome ledger v1 supports research OOS outcomes only; WP-9m added the seed instance and methodology, and WP-9n completed the retrospective REP-derived corpus through `OL-0011` while preserving the H-004 `REP-0005` / `REP-0011` split. Validator and query-layer support exists. WP-9o adds the offline artifact-generation helper at `tools/outcome_ledger/build_from_rep.py`; it has no auto-ID allocation and no runtime authority. Paper/live outcome kinds, per-trade granularity, evidence-quality scoring, incompatible evolution, REC/reconciliation, policy, runtime, and deployment behavior require explicit later work. |
| `research/schemas/overlay_shadow_log.schema.json` | Overlay shadow log / OSH | No | No equivalent schema version marker | `tools/registry/validate_overlay_shadow_logs.py` | `research/overlay_shadow_logs/*.overlay_shadow_log.json` | `overlay_shadow_logs`, overview/latest/agreement/override views, `v_integrity_overlay_shadow_refs` | `retrofit-candidate` | Medium | Active shadow-evidence family without explicit version marker. |
| `research/schemas/pre_gate_advisory_snapshot.schema.json` | Pre-gate advisory snapshot / PGAS | No | `combination_rule_applied` records applied rule state, but is not a schema version marker | `tools/registry/validate_pre_gate_advisory_snapshots.py` | `research/pre_gate_advisory_snapshots/*.pre_gate_advisory_snapshot.json` | `pre_gate_advisory_snapshots`, overview/latest views, `v_integrity_pre_gate_advisory_snapshot_refs` | `retrofit-candidate` | Medium | Active advisory/query family without explicit version marker. |
| `research/schemas/reconciliation.schema.json` | Reconciliation / REC | Yes, required | `schema_version` const `v1` | `tools/registry/validate_reconciliations.py` | `research/reconciliations/REC-*.reconciliation.json` | `reconciliations`, `v_reconciliation_overview`, `v_reconciliation_candidate_pipeline_summary`, REC integrity views | `phase9-explicit-v1` | None | REC v1 supports research_oos reconciliation only against `exp_success_criteria` and `d2_006_gates`; schema, validator, and query-layer support are unchanged. The committed `exp_success_criteria` corpus remains 11 rows through `REC-0011`; the `d2_006_gates` corpus is now backfilled across the locked OL v1 corpus from `REC-0012` through `REC-0022`. Helper tooling, consumers, paper/live, evidence-quality scoring, policy fields, promotion/demotion flags, runtime, and deployment behavior remain deferred. |
| `research/schemas/release_notes.schema.json` | Release Notes / REL | No | No equivalent schema version marker | `tools/registry/validate_release_notes.py` | `research/release_notes/*.release_notes.json` | `release_notes`, `v_release_notes_overview`, `v_stage_transitions`, `v_integrity_release_refs` | `retrofit-candidate` | High | Legacy release/approval companion to DCH. |
| `research/schemas/shadow_signal_summary.schema.json` | Shadow Signal Summary v1 / SSS | No | Top-level `derivation_method` const `shadow_signal_summary_option_a_floor_10_v1` | `tools/registry/validate_shadow_signal_summaries.py` | `research/shadow_signal_summaries/*.shadow_signal_summary.json` | `shadow_signal_summaries`, `v_shadow_signal_summaries_overview`, `v_integrity_shadow_signal_summary_derivation` | `equivalent-marker-locked` | None | SSS v1 stability lock treats derivation method as equivalent version marker; do not retrofit. |
| `research/schemas/shadow_signal_summary_v2.schema.json` | Shadow Signal Summary v2 / SSS v2 | Yes, required | `schema_version` const `v2`; derivation method remains `shadow_signal_summary_option_a_floor_10_v1` | `tools/registry/validate_shadow_signal_summary_v2.py` | `research/shadow_signal_summaries_v2/*.shadow_signal_summary.json` | `shadow_signal_summaries_v2`, `v_shadow_signal_summaries_v2_overview`, `v_integrity_shadow_signal_summary_v2_derivation` | `explicit-versioned-current` | None | SSS v2 stability lock records explicit versioned posture. |

## Classification Legend

- `phase9-explicit-v1`: Phase 9 family with required top-level
  `schema_version` fixed to `v1`.
- `explicit-versioned-current`: current family with an explicit required
  top-level `schema_version`, but not necessarily a Phase 9 v1 family.
- `equivalent-marker-locked`: current family without `schema_version` where a
  documented top-level marker is already locked as the practical version marker.
- `legacy-unversioned-stable`: current family without a version marker and with
  no likely near-term mutation path.
- `retrofit-candidate`: current family without explicit schema version where a
  later scoped package may need to add version posture.
- `ambiguous-needs-follow-up`: current repo truth is insufficient to classify
  the family honestly without further investigation.

## Current Known Retrofit Candidates

- Candidate registry lacks explicit top-level `schema_version`.
- DCH `pipeline_stage` vocabulary differs from Phase 9 lifecycle vocabulary.
- REL is a legacy release/approval companion to DCH and lacks explicit
  `schema_version`.
- EXP and REP are legacy research evidence families without explicit
  `schema_version`.
- AOUT, MOUT, BMAP, PGAS, and OSH are active advisory/shadow query-layer
  families without explicit `schema_version`.

These are candidates only. WP-9c does not patch them.

## Current Non-Retrofit Families

- SSS v1 must not be retrofitted by WP-9c. Its documented equivalent marker is
  top-level `derivation_method = shadow_signal_summary_option_a_floor_10_v1`.
- SSS v2 is already explicitly versioned with required
  `schema_version: "v2"`.
- LCH v1 is explicitly versioned as the first Phase 9 schema with required
  `schema_version: "v1"`.
- Outcome ledger v1 is explicitly versioned with required
  `schema_version: "v1"` and has no WP-9k committed instances, validator, or
  query-layer exposure.
- REC v1 is explicitly versioned with required `schema_version: "v1"` and has
  unchanged validator/query-layer support plus committed `exp_success_criteria`
  coverage from `REC-0001` through `REC-0011` and committed `d2_006_gates`
  coverage from `REC-0012` through `REC-0022` across the locked OL v1 corpus.
  Helper tooling, consumers, policy, paper/live semantics, evidence scoring,
  runtime, and deployment behavior remain deferred.

## Follow-Up Boundaries

This inventory does not authorize patches.

Future packages must choose from the inventory and scope one schema family at a
time unless a strong repo-truth reason justifies bundling multiple families.

Any future retrofit package must state why the retrofit is needed now, how
existing committed artifacts remain valid or are migrated, which validators and
query-layer surfaces change, and which protected paths remain untouched.
