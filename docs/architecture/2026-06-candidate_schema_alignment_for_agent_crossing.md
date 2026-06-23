# Candidate Schema Alignment For Agent Crossing

## Purpose

This document records the schema/vocabulary decision that resolves the
candidate-review packet fields previously marked `needs schema decision` by
the canonical crossing design.

Decision: the canonical candidate lifecycle registry schema can preserve an
approved scratch candidate-review packet by appending a new event type,
`candidate_review_packet_crossed`, whose `crossing_evidence` object carries
the packet's source lineage, denominator snapshot, diagnostics, data
availability, funding posture, non-authority flags, and append-only semantics.

Non-decision: this does not implement a crossing, write a real candidate
lifecycle registry instance, create a crossing approval artifact, register a
candidate, freeze/promote/rank a candidate, or create paper/live readiness.

## Event Shape

`research/schemas/candidate_lifecycle_registry.schema.json` now allows:

```json
{
  "event_type": "candidate_review_packet_crossed",
  "from_status": null,
  "to_status": "proposed",
  "crossing_evidence": {
    "source_lineage": {},
    "denominator_snapshot": {},
    "diagnostics_summary": {},
    "data_availability": {},
    "funding": {},
    "non_authority_flags": {},
    "append_only_semantics": {}
  }
}
```

Rules:

- `crossing_evidence` is optional for existing event types.
- `crossing_evidence` is required for
  `event_type=candidate_review_packet_crossed`.
- Any event with `crossing_evidence` must use
  `event_type=candidate_review_packet_crossed`.
- The crossing event is new-event-shaped and first-entry-shaped:
  `from_status=null`, `to_status=proposed`.
- A crossing event cannot imply `validated_research`, `paper_candidate`,
  `paper_running`, `promoted_live`, ranking, evidence authority, or readiness.

## Schema Additions

### Artifact References

New `artifact_ref.artifact_type` enum values:

- `candidate_review_packet`
- `formalizer_artifact`
- `bridge_review_packet`
- `denominator_ledger`
- `robustness_diagnostics`
- `robustness_review_packet`
- `operator_approval`
- `crossing_approval`

### Source Lineage

Required fields:

| Field | Type | Required |
|---|---|---|
| `candidate_review_packet_path` | string | yes |
| `candidate_review_packet_hash` | `sha256:<64 hex>` | yes |
| `formalizer_artifact_path` | string | yes |
| `formalizer_artifact_hash` | `sha256:<64 hex>` | yes |
| `bridge_artifact_path` | string | yes |
| `bridge_artifact_hash` | `sha256:<64 hex>` | yes |
| `robustness_artifact_path` | string | yes |
| `robustness_artifact_hash` | `sha256:<64 hex>` | yes |
| `denominator_ledger_path` | string | yes |
| `denominator_ledger_hash` | `sha256:<64 hex>` | yes |

Optional paired fields are provided for the formalizer draft Strategy Spec,
bridge runner artifact, robustness review packet, operator approval, and
future crossing approval.

### Denominator Snapshot

Required fields:

| Field | Type | Required |
|---|---|---|
| `completed_count` | integer >= 0 | yes |
| `failed_count` | integer >= 0 | yes |
| `invalid_count` | integer >= 0 | yes |
| `pruned_count` | integer >= 0 | yes |
| `blocked_count` | integer >= 0 | yes |
| `declared_trial_count` | integer >= 0 | yes |
| `all_source_rows_preserved` | boolean, `true` | yes |
| `full_ledger_path` | string | yes |
| `full_ledger_hash` | `sha256:<64 hex>` | yes |
| `row_disposition` | array of row objects | yes |

Row dispositions require `variant_id`, `trial_status`, and `status_reason`.
`trial_status` is closed to `completed`, `failed`, `invalid`, `pruned`, and
`blocked`.

### Diagnostics Summary

Required fields:

| Field | Type | Required |
|---|---|---|
| `completed_diagnostics` | unique string array | yes |
| `skipped_diagnostics` | array of `{diagnostic, reason}` objects | yes |
| `skipped_reasons` | unique string array | yes |
| `missing_diagnostics.per_trade` | object | yes |
| `missing_diagnostics.oos_walkforward` | object | yes |
| `missing_diagnostics.funding_stress` | object | yes |
| `unsupported_diagnostics` | unique string array | yes |

Missing-diagnostic states require `status` and `performed`. They may carry
`reason`, `queued_follow_up`, and `fabricated_per_trade_data=false`.

### Data Availability

Required fields:

| Field | Type | Required |
|---|---|---|
| `warnings` | string array | yes |
| `blockers` | string array | yes |
| `coverage_classes` | unique string array | yes |
| `constraint_classes` | unique string array | yes |
| `caveats` | unique string array | yes |

This covers warning/blocker text plus vendor, capture, recent-only, and
streaming-only caveats where the packet or upstream diagnostics surface them.

### Funding

Required fields:

| Field | Type | Required |
|---|---|---|
| `funding_cost_mode` | enum: `off`, `on`, `not_run`, `unknown` | yes |
| `funding_stress_status.status` | string | yes |
| `funding_stress_status.performed` | boolean | yes |
| `funding_stress_status.skipped_reason` | string or null | optional |

### Non-Authority Flags

Required true fields:

- `not_evidence`
- `not_candidate_authority`
- `not_promotion_authority`
- `not_ranking_authority`
- `not_paper_live_readiness`
- `not_trading_signal`
- `human_review_required`

### Append-Only Semantics

Required true fields:

- `append_only`
- `new_event_only`
- `no_overwrite`
- `correction_requires_supersession_event`
- `source_hashes_preserved`
- `denominator_snapshot_preserved`
- `caveats_preserved`
- `missing_diagnostics_preserved`

## Field-Level Mapping

| Scratch packet field | Canonical home after this package | Rule |
|---|---|---|
| `source_formalizer.path` / `sha256` | `crossing_evidence.source_lineage.formalizer_artifact_path/hash` | Preserve exact path/hash. |
| `source_formalizer.draft_strategy_spec_path` / `sha256` | optional source-lineage draft fields and/or `source_refs.strategy_spec_refs` | Reference only; not canonical Strategy Spec evidence. |
| `source_bridge.review_packet_path` / `sha256` | `crossing_evidence.source_lineage.bridge_artifact_path/hash` | Preserve exact path/hash. |
| `source_bridge.runner_artifact_path` / `sha256` | optional source-lineage runner fields | Scratch Result Population-shaped source only. |
| `source_robustness.diagnostics_path` / `sha256` | `crossing_evidence.source_lineage.robustness_artifact_path/hash` | Preserve exact path/hash. |
| `source_robustness.review_packet_path` / `sha256` | optional source-lineage robustness review fields | Preserve packet link when present. |
| `operator_approval.path` / `sha256` | optional source-lineage operator approval fields | Noncanonical packet approval only; not crossing approval. |
| future crossing approval path/hash | optional source-lineage crossing approval fields | Required by future build policy, not created here. |
| `denominator_snapshot.counts.completed` | `denominator_snapshot.completed_count` | Integer count. |
| `denominator_snapshot.counts.failed` | `denominator_snapshot.failed_count` | Integer count. |
| `denominator_snapshot.counts.invalid` | `denominator_snapshot.invalid_count` | Integer count. |
| `denominator_snapshot.counts.pruned` | `denominator_snapshot.pruned_count` | Integer count. |
| `denominator_snapshot.counts.blocked` | `denominator_snapshot.blocked_count` | Integer count. |
| `denominator_snapshot.ledger_path/hash` | `denominator_snapshot.full_ledger_path/hash` plus source lineage ledger fields | Preserve hash-bound ledger. |
| `denominator_snapshot.row_disposition` | `denominator_snapshot.row_disposition[]` | Preserve row status and reason. |
| `robustness_summary.diagnostics_completed` | `diagnostics_summary.completed_diagnostics[]` | Preserve diagnostic names. |
| `robustness_summary.diagnostics_skipped` | `diagnostics_summary.skipped_diagnostics[]` and `skipped_reasons[]` | Preserve skip reasons. |
| `missing_data_limitations.per_trade` | `diagnostics_summary.missing_diagnostics.per_trade` | Preserve unavailable per-trade state and `fabricated_per_trade_data=false`. |
| `missing_data_limitations.oos_walkforward` | `diagnostics_summary.missing_diagnostics.oos_walkforward` | Preserve missing fold/OOS state. |
| `missing_data_limitations.funding_stress` | `diagnostics_summary.missing_diagnostics.funding_stress` | Preserve funding-stress-not-run state. |
| `data_and_funding_summary.data_availability_warnings` | `data_availability.warnings[]` | Preserve warnings. |
| `data_and_funding_summary.data_availability_blockers` | `data_availability.blockers[]` | Preserve blockers. |
| vendor/capture/recent-only caveats | `data_availability.coverage_classes[]`, `constraint_classes[]`, and `caveats[]` | Preserve caveat classes where surfaced. |
| `data_and_funding_summary.funding_mode.requested/effective` | `funding.funding_cost_mode` | Preserve selected funding mode. |
| `data_and_funding_summary.funding_stress_status` | `funding.funding_stress_status` | Preserve performed/skipped state. |
| `non_authority_flags` | `crossing_evidence.non_authority_flags` and event/candidate non-authority declarations | Required true; crossing does not create authority. |
| `recommended_human_review_questions` | `review_metadata.unresolved_questions` | Human-review prompts only. |
| `recommended_next_evidence_steps` | `required_next_review` and/or event reason | Next evidence, not readiness. |
| `runner_metrics_summary.*` | source packet/bridge source refs and hashes | No parallel canonical metric truth in this package. |

## Validator Expectations

Existing `tools.registry.validate_candidate_registry` remains the validator
entrypoint. The validator now observes the extended JSON schema without
changing `tools/registry` behavior.

Focused tests prove:

- a valid fake crossing event with denominator snapshot passes;
- skipped diagnostics and skipped reasons are representable;
- data availability warnings/blockers and caveats are representable;
- `funding_cost_mode=off` with funding stress not run is representable;
- missing per-trade and OOS diagnostics are representable;
- incomplete denominator snapshot is invalid;
- missing crossing non-authority flags are invalid;
- promotion/readiness implication is invalid for a crossing event; and
- crossing evidence without the crossing event type is invalid.

## Integrity / Query Expectations

No query-layer behavior is changed here because no real
`research/candidate_lifecycle_registry/` artifact exists and this package is
not authorized to create one.

Future real crossing package must add or select the minimum query/integrity
surface after the storage target is authorized. At minimum, the future
post-write check must prove that the appended crossing event is discoverable,
that packet hash and denominator snapshot are retained, and that no
promotion/readiness/paper/live state is created.

## Fake Fixture

Fixture:

```text
tests/fixtures/candidate_lifecycle_registry/valid_candidate_review_packet_crossing.candidate_lifecycle_registry.json
```

It records a fake `CANDIDATE-FIXTURE-0002` with one
`CLE-FIXTURE-0001` crossing event. The fixture is test-only and creates no real
candidate lifecycle registry artifact under `research/`.

## Stop Conditions For Later Crossing Build

A future crossing build must stop if:

- candidate-review packet path/hash is missing or mismatched;
- formalizer, bridge, robustness, or denominator ledger path/hash is missing
  or mismatched;
- denominator snapshot is incomplete or mismatched;
- row dispositions are missing;
- skipped diagnostics or missing diagnostic states are hidden;
- data availability warnings/blockers/caveats are missing;
- funding mode or funding stress status is missing;
- crossing event would overwrite an existing entry;
- event ID, event sequence, candidate ID, or source hash collides;
- crossing would imply validation, ranking, promotion, paper/live readiness,
  runtime action, or trading authority;
- correction would mutate prior evidence instead of appending a correction or
  supersession event; or
- validators/query integrity fail.

## LangGraph Dependency Note

LangGraph dependency cleanup is a separate housekeeping decision or should be
folded into a future infra/dependency cleanup work package. This
schema-alignment package does not touch LangGraph dependencies.
