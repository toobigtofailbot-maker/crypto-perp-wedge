# WP-AGENT-CANDIDATE-SCHEMA-ALIGNMENT-01 Repo-Truth Discovery

## Scope

This package resolves the schema-alignment items surfaced by the prior
canonical crossing design. It is additive schema/fixture/test work only.

Forbidden scope remained untouched: no real canonical candidate lifecycle
registry instance, no canonical crossing, no registration, no freeze, no
promotion, no paper/live readiness, no Result Population, Strategy Spec,
Variant Manifest, Sweep Plan, trial-log, runtime, paper/live, OMS, risk,
reconciliation, capital, private endpoint, provider/API/network, dependency,
or LangGraph cleanup change.

## Branch / Base

- Branch: `agent/candidate-schema-alignment-01`
- Worktree:
  `C:\GitHub\crypto-perp-wedge-worktrees\agent-candidate-schema-alignment-01`
- Base: refreshed `origin/main` at `6218416`, the PR #550 merge commit.

## PR #549 Needs-Schema-Decision Items

The merged canonical crossing design marked these packet fields as needing a
schema decision before a canonical crossing build:

- `denominator_snapshot.counts`
- `denominator_snapshot.row_disposition`
- `lineage_consistency.denominator_counts`
- `runner_metrics_summary.top_metrics`
- `runner_metrics_summary.manual_reconciliation_result`
- `robustness_summary.diagnostics_completed`
- `robustness_summary.diagnostics_skipped`
- `missing_data_limitations`
- `data_and_funding_summary.data_availability_warnings`
- `data_and_funding_summary.data_availability_blockers`
- `data_and_funding_summary.funding_mode`
- `evidence_gaps`
- `blockers`
- `recommended_next_evidence_steps`

This package resolves the required preservation subset by adding a
`candidate_review_packet_crossed` event type and a required nested
`crossing_evidence` object for that event. Runner metrics remain hash-bound to
the source packet/bridge artifacts; they are not promoted into parallel
canonical metric truth.

## Candidate-Review Packet Fields

Current scratch packet:

- Path:
  `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/dba42387c2e4f679/candidate_review_packet.json`
- Schema version: `candidate_review_packet_v1`
- Source lineage:
  `source_formalizer`, `source_bridge`, `source_robustness`,
  `operator_approval`, and `candidate_lifecycle_context_refs`, each with paths
  and hashes where applicable.
- Denominator:
  `denominator_snapshot.counts` has `completed`, `failed`, `invalid`,
  `pruned`, and `blocked`; `declared_trial_count`; `ledger_path`;
  `ledger_sha256`; `all_source_rows_preserved`; and `row_disposition`.
- Robustness:
  `robustness_summary.diagnostics_completed`,
  `robustness_summary.diagnostics_skipped`,
  `missing_diagnostic_inputs`, bootstrap and sensitivity summaries.
- Missing diagnostics:
  per-trade data unavailable, OOS/walk-forward fold inputs unavailable, and
  funding stress not applicable because funding mode is off.
- Data/funding:
  `data_and_funding_summary.data_availability_warnings`,
  `data_availability_blockers`, `funding_mode`, and
  `funding_stress_status`.
- Authority:
  `non_authority_flags` includes not canonical, not evidence, not candidate
  authority, not promotion authority, not ranking authority, not paper/live
  readiness, not a trading signal, and human review required.

## Robustness Diagnostic Fields

`tools/research_agents/robustness_diagnostician_agent.py` and
`scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/9309de71e35fc40f/robustness_review_packet.json`
preserve:

- attempted, completed, and skipped diagnostics;
- `denominator_integrity_status.source_status_counts`;
- per-trade status with `fabricated_per_trade_data=false`;
- OOS/walk-forward `missing_fold_inputs`;
- funding stress `not_applicable_funding_mode_off`;
- data availability warnings/blockers; and
- non-authority flags including not ranking authority.

## Bridge Denominator Ledger Fields

`tools/research_agents/formalizer_runner_bridge.py` and
`scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/fd63eb89897d9dc5/denominator_ledger.json`
preserve:

- `declared_trial_count`;
- `denominator_preserved=true`;
- `trial_status_counts` over `completed`, `failed`, `invalid`, `pruned`, and
  `blocked`;
- every row's `variant_id`, `trial_status`, `status_reason`,
  `runner_outcome_category`, parameters, funding mode, source formalizer path,
  input/output hashes, and runner artifact path.

## Current Candidate Lifecycle Registry Schema

Before this package, `research/schemas/candidate_lifecycle_registry.schema.json`
defined:

- registry metadata and non-authority declaration;
- candidates with source refs, evidence links, event refs, review metadata,
  optional blocking/next-review fields, and non-authority declaration;
- append-only audit events with event ID, sequence, candidate ID, event type,
  timestamp, gate, statuses, evidence refs, exception refs, and
  non-authority declaration.

Missing before this package:

- first-class candidate-review packet path/hash;
- first-class denominator status counts and row dispositions;
- first-class skipped diagnostics and missing diagnostic states;
- first-class data availability warnings/blockers/caveats;
- first-class funding cost mode and funding stress status;
- first-class crossing non-authority flags; and
- event-specific append-only correction/supersession semantics.

## Schema Extension Decision

Decision: add event-shaped evidence under `append_only_ledger[]`, not candidate
top-level fields.

New schema content:

- `event_type`: new enum value `candidate_review_packet_crossed`.
- `crossing_evidence`: optional for ordinary events, required when
  `event_type == candidate_review_packet_crossed`.
- For crossing evidence, `event_type` must be
  `candidate_review_packet_crossed`; the event must be first-event-shaped
  `from_status=null` and `to_status=proposed`.
- `source_lineage`: required paths/hashes for candidate-review packet,
  formalizer artifact, bridge artifact, robustness artifact, and denominator
  ledger; optional paired hashes for draft spec, runner artifact, robustness
  review packet, operator approval, and future crossing approval.
- `denominator_snapshot`: required integer counts for completed, failed,
  invalid, pruned, and blocked; `declared_trial_count`;
  `all_source_rows_preserved=true`; full ledger path/hash; and row
  dispositions.
- `diagnostics_summary`: completed diagnostics, skipped diagnostics,
  skipped reasons, missing diagnostics for per-trade, OOS/walk-forward, and
  funding stress, plus unsupported diagnostics.
- `data_availability`: warnings, blockers, coverage classes, constraint
  classes, and caveats.
- `funding`: `funding_cost_mode` enum of `off`, `on`, `not_run`, or
  `unknown`; funding stress status with performed flag and skipped reason.
- `non_authority_flags`: required true flags for not evidence, not candidate
  authority, not promotion authority, not ranking authority, not paper/live
  readiness, not trading signal, and human review required.
- `append_only_semantics`: required true flags for append-only, new event
  only, no overwrite, correction requires supersession event, source hashes
  preserved, denominator snapshot preserved, caveats preserved, and missing
  diagnostics preserved.

Inference: this is additive for existing registry events because
`crossing_evidence` is optional unless the new event type is used. Existing
fake fixtures remain valid.

## Validators And Integrity / Query Surfaces

Repo truth:

- `tools/registry/validate_candidate_registry.py` validates schema and existing
  semantic rules for candidate/event identity, append-only event ordering,
  status history, non-authority declarations, and promotion evidence.
- `tools/registry/AGENTS.override.md` says this package must not modify
  validator behavior there.
- `tools/research_query/` currently exposes lifecycle-change views, not
  candidate lifecycle registry crossing-event views.

Decision:

- Do not modify `tools/registry` behavior in this package.
- Prove the alignment through JSON schema additions, fake fixture coverage, and
  tests that call the existing validator.
- Do not add query-layer behavior because no real
  `research/candidate_lifecycle_registry/` artifact exists and the package is
  not authorized to write one.

## Fake Fixture Coverage

Added:

- `tests/fixtures/candidate_lifecycle_registry/valid_candidate_review_packet_crossing.candidate_lifecycle_registry.json`

The fixture is `registry_status=test_fixture`, uses
`CANDIDATE-FIXTURE-0002`, has one append-only
`candidate_review_packet_crossed` event, and preserves denominator counts,
full row dispositions, source hashes, skipped diagnostics, data warnings and
blockers, funding mode off, missing per-trade/OOS/funding-stress states,
non-authority flags, and append-only semantics.

## Candidate Lifecycle Helper Alignment

Fact: `tools/candidate_lifecycle/lifecycle_engine.py` remains scratch-only and
uses a different lifecycle vocabulary (`research_concluded`,
`paper_eligible`, etc.) from the candidate lifecycle registry fixture schema
(`proposed`, `validated_research`, etc.).

Decision: do not update helper output in this package. The helper mismatch is a
future crossing-build prerequisite; changing it here would risk crossing
implementation by implication.

## Stop Conditions / Open Questions

No package stop condition fired.

Open future questions remain:

- where a real crossing approval artifact will live;
- which ID allocator owns real candidate and event IDs;
- whether a future crossing creates only a new candidate, appends to an
  existing candidate, or supports both under separate scopes;
- which query/integrity views should expose real crossing events after a real
  storage target is authorized; and
- whether runner metric summaries should remain source-hash-bound only or gain
  separate first-class canonical summary fields in a later package.
