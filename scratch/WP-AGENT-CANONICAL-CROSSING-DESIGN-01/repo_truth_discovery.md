# WP-AGENT-CANONICAL-CROSSING-DESIGN-01 Repo-Truth Discovery

## Scope

This discovery supports a docs-only design package for a future human-gated
canonical crossing from an approved scratch candidate-review packet to a
canonical candidate lifecycle registry entry or event.

This package does not implement the crossing, write canonical candidate
lifecycle registry entries, change schemas, change validators, change
ToolContext permissions, or touch runtime, paper/live, OMS, risk,
reconciliation, capital, broker/exchange, credentials, configs, data,
Strategy Specs, Variant Manifests, Sweep Plans, Result Populations, or trial
logs.

## Branch / Base

- Branch: `agent/canonical-crossing-design-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\agent-canonical-crossing-design-01`
- Base: `origin/main` at `485ecef`, the PR #548 merge commit for
  `WP-AGENT-CANDIDATE-REVIEW-PACKET-01`.

## Candidate-Review Packet Output Fields

Fact:

- `tools/research_agents/candidate_review_packet_agent.py` writes only
  scratch JSON and Markdown under
  `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/<run_id>/`.
- The JSON packet uses `schema_version=candidate_review_packet_v1`.
- The output includes:
  - `source_formalizer.path`, `source_formalizer.sha256`,
    `source_formalizer.run_id`, optional draft Strategy Spec path/hash;
  - `source_bridge.review_packet_path`, `source_bridge.review_packet_sha256`,
    `source_bridge.run_id`, optional runner artifact path/hash;
  - `source_robustness.diagnostics_path`,
    `source_robustness.diagnostics_sha256`,
    `source_robustness.review_packet_path`,
    `source_robustness.review_packet_sha256`,
    `source_robustness.run_id`;
  - `operator_approval.path`, `operator_approval.sha256`, and copied
    metadata for the noncanonical candidate-review approval marker;
  - `lineage_consistency`, including source run IDs and denominator counts;
  - `candidate_lifecycle_context_refs`, read-only helper/example refs;
  - `strategy_summary`;
  - `data_and_funding_summary`;
  - `denominator_snapshot`, including ledger path/hash, counts, declared
    trial count, all-source-rows-preserved flag, and row disposition;
  - `runner_metrics_summary`;
  - `robustness_summary`, including completed/skipped diagnostics,
    missing diagnostic inputs, bootstrap and sensitivity summaries;
  - `missing_data_limitations`, `evidence_gaps`, `blockers`;
  - recommended human-review questions and next evidence steps;
  - `allowed_summary_language`;
  - `non_authority_flags`.

Decision:

- The future crossing must require the full candidate-review packet JSON and
  its content hash, not only the Markdown packet or a summary.
- The packet's non-authority flags must remain preserved through crossing and
  cannot be treated as candidate approval, promotion, readiness, or paper/live
  authority.

## Candidate Lifecycle Registry Schema Fields

Fact:

- `research/schemas/candidate_lifecycle_registry.schema.json` defines a
  lifecycle registry object with:
  - `schema_version`;
  - `registry_id`;
  - `registry_status`;
  - `non_authority_declaration`;
  - `transition_rules`;
  - `candidates`;
  - `append_only_ledger`;
  - `validation_summary`.
- Candidate entries include:
  - `candidate_id`;
  - `candidate_status`;
  - `display_name`;
  - `strategy_family`;
  - `description`;
  - `market`;
  - `instrument`;
  - `primary_timeframe`;
  - `allowed_confirmation_timeframes`;
  - `source_refs`;
  - `evidence_links`;
  - `lifecycle_event_refs`;
  - `review_metadata`;
  - optional `blocking_reason` and `required_next_review`;
  - `non_authority_declaration`.
- Registry audit events include:
  - `event_id`;
  - `event_sequence`;
  - `candidate_id`;
  - `event_type`;
  - `timestamp_utc`;
  - `actor`;
  - `gate`;
  - `from_status`;
  - `to_status`;
  - `reason`;
  - `related_evidence_links`;
  - `blocking_or_exception_refs`;
  - `non_authority_declaration`.
- The committed schema has no explicit fields for:
  - candidate-review packet hash;
  - approval artifact hash;
  - denominator counts;
  - denominator ledger hash;
  - skipped diagnostics;
  - data availability warnings;
  - funding mode;
  - missing-data limitations;
  - runner metric summary;
  - human-review questions.
- `tests/test_validate_candidate_registry.py` asserts there is no real
  candidate lifecycle registry artifact committed under `research/`.

Inference:

- Existing `artifact_ref` structures can reference packet, approval, source,
  and evidence artifacts where the schema's enum allows an appropriate
  `artifact_type`.
- Detailed denominator, skipped diagnostic, funding, and warning content
  cannot be silently inserted into non-existent schema fields.

Decision:

- The design must mark unmapped detailed fields as `needs schema decision`.
- Any future build must decide whether to extend the lifecycle registry schema,
  use lifecycle-change artifacts, or introduce a separate crossing-audit
  artifact before canonical writes are allowed.

## Candidate Lifecycle Helper Behavior

Fact:

- `tools/candidate_lifecycle/lifecycle_engine.py` is a scratch-only lifecycle
  report and review-packet helper.
- It uses current lifecycle states:
  `proposed`, `in_research`, `research_concluded`, `paper_eligible`,
  `paper_active`, `paper_concluded`, `live_eligible`, `live_active`, `halted`,
  and `archived`.
- It blocks auto-promotion, readiness marking, paper/live starts, live-active
  targets, and evidence mutation requests.
- It writes scratch outputs under
  `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/`.
- The helper's scratch packet is not a canonical registry write path.

Repo-truth adjustment:

- The lifecycle helper and committed `lifecycle_change` artifacts use a state
  vocabulary that differs from the fixture-only
  `candidate_lifecycle_registry.schema.json` vocabulary
  (`proposed`, `validated_research`, `paper_candidate`, `paper_running`,
  `promoted_live`, `rejected`, `demoted`, `retired`).

Decision:

- A future canonical crossing build cannot assume these vocabularies are
  interchangeable. It needs an explicit schema/state decision before writes.

## Existing Human-Review Packet Shape

Fact:

- The candidate-review packet Markdown surfaces:
  - non-authority flags;
  - source paths and hashes;
  - denominator counts;
  - strategy/evidence summary;
  - funding mode;
  - data warnings and blockers;
  - completed and skipped robustness diagnostics;
  - evidence gaps, blockers, human-review questions, and next evidence steps.
- The JSON packet is the authoritative scratch packet for future crossing
  design because it preserves structured fields and hashes.
- The packet's strongest allowed summary is:
  `candidate may be worth human review for further evidence`.

Decision:

- Future crossing approval must require full content review of the structured
  JSON packet and linked sources before any lock or canonical write.
- Label-only approval, PR merge, comment, file presence, or agent
  recommendation alone is insufficient.

## Existing Validators / Integrity Views

Fact:

- `tools/registry/validate_result_populations.py` validates canonical
  Result Populations, including denominator integrity, append-only ledger
  posture, identity hashes, non-authority declarations, data-availability
  claims, and forbidden authority/executable keys.
- `tools/registry/validate_data_feature_availability.py` validates the
  data-derived feature availability catalog and preserves coverage classes
  such as full-history public archive, recent-only public REST, streaming-only,
  vendor-only, snapshot-only, and unknown/blocked.
- `tools/registry/validate_registry.py` validates the older
  `research/candidate_registry.jsonl` H-### registry against
  `research/schemas/candidate_registry.schema.json` and trial-log refs.
- `tools/registry/validate_candidate_registry.py` validates
  candidate-lifecycle-registry fixture artifacts and checks duplicate
  candidates/events, event order, status history, non-authority flags, and
  paper/live promotion evidence requirements.
- `tools/registry/validate_lifecycle_changes.py` validates committed
  `research/lifecycle_changes/*.lifecycle_change.json` artifacts, including
  schema shape, candidate refs, transition shape, evidence refs, supersession
  refs, operational transition evidence, fast-track requirements, and
  retrospective disclosure.
- `tools/research_query/run.py --list-views` lists read-only query views.
- Current lifecycle query surfaces include:
  - `v_lifecycle_change_overview`;
  - `v_lifecycle_state_transitions`;
  - `v_integrity_lifecycle_change_refs`;
  - `v_integrity_lifecycle_transition_graph`;
  - `v_integrity_lifecycle_approval_completeness`;
  - `v_integrity_lifecycle_fast_track_completeness`.
- Existing Result Population integrity views include denominator, outcome,
  append-only, non-authority, offline-boundary, canonical-write, authority-key,
  and parent-hash-chain checks.

Decision:

- Future pre-write checks must run packet/source validation, approval artifact
  validation, source hash checks, denominator consistency checks, non-authority
  flag checks, data/funding caveat checks, and ToolContext gate checks before
  any canonical write.
- Future post-write checks must run the lifecycle/candidate registry
  validators selected by the future storage decision, existing relevant
  registry validators, query view discovery, and integrity views that can find
  the new event or entry.

## Existing ToolContext Roles / Actions

Fact:

- `tools/agent_sandbox/permissions.py` is closed by default.
- Current roles include `candidate_review_packet_preparer`.
- Current hard-blocked actions include:
  `canonical_write`, `candidate_registration`, `candidate_promotion`,
  `candidate_readiness`, `candidate_freeze`,
  `candidate_lifecycle_transition`, `trial_log_mutation`,
  `overlay_control`, `execution_control`, `runtime_control`, `paper_control`,
  `live_control`, `oms_access`, `risk_control`, `reconciliation_control`,
  `safe_mode_control`, `kill_switch_control`, `broker_access`,
  `exchange_access`, `order_access`, `capital_access`, `credential_access`,
  `private_endpoint_access`, `dependency_mutation`,
  `project_status_mutation`, `network_access`, `backtest_execution`,
  `sweep_execution`, `funding_mode_mutation`, `evidence_suppression`,
  `evidence_deletion`, `toolcontext_bypass`,
  `provider_memory_as_truth`, `gate_bypass`, `approval_gate_bypass`,
  `data_availability_bypass`, `fabricated_per_trade_data`,
  `fabricated_robustness_diagnostic`, `ranking_as_promotion_ready`, and
  `provider_api_call`.
- `BUILD_SCRATCH_CANDIDATE_REVIEW_PACKET` is scoped only to the active
  candidate-review packet scratch outputs.
- `ToolContext` normalizes repo-relative paths and audits every allowed or
  blocked decision before execution.
- `AuditRecord` carries a non-authority statement and records timestamp, WP,
  role, action type, target path, decision, reason, and policy ID.

Decision:

- This package must not change ToolContext.
- The future design may propose the action
  `human_approved_canonical_candidate_crossing`, but implementation requires a
  later Karl-gated build package.

## Canonical Write Boundaries

Fact:

- ToolContext currently blocks generic canonical writes and candidate
  lifecycle transitions for bounded research agents.
- Protected runtime, paper/live, OMS, risk, reconciliation, safe mode, kill
  switch, broker/exchange, order, capital, credentials, network, dependency,
  config, and live-trading paths are outside this package.
- The candidate-review packet package specifically blocks canonical candidate
  registry, Result Population, Strategy Spec, Variant Manifest, Sweep Plan,
  trial-log writes, candidate registration/freeze/promotion/readiness, and
  paper/live/runtime actions.

Decision:

- A future crossing build must be append-only and narrow. It may create only a
  new candidate lifecycle entry or new event under explicit approval, never a
  promotion/readiness/paper/live state or overwrite of prior evidence.

## Unknowns And Required Future Implementation Gates

Open questions:

- Whether the future canonical target is:
  - a real `research/candidate_lifecycle_registry/*.candidate_lifecycle_registry.json`;
  - the existing `research/lifecycle_changes/*.lifecycle_change.json` family;
  - the older `research/candidate_registry.jsonl`;
  - or a new crossing-audit artifact paired with one of the above.
- Which lifecycle state vocabulary wins for new real candidate lifecycle
  records.
- Whether approval artifacts become committed canonical artifacts, scratch
  attachments, PR-reviewed documents, or separate audit records.
- How approval artifact IDs and storage paths are allocated.
- Whether detailed denominator, skipped diagnostic, data-warning, and funding
  caveat fields require schema additions.
- Which query views must be added or extended after the storage target is
  selected.

Future option:

- A later Karl-gated build package can implement a narrow crossing only after
  resolving schema/storage vocabulary, adding or selecting validators, defining
  ToolContext permission changes, and proving post-write query integrity.
