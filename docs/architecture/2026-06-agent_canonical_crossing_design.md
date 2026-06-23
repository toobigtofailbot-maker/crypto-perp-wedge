# Agent Canonical Crossing Design

## Purpose

This document designs a future human-gated canonical crossing from an approved
scratch candidate-review packet to a canonical candidate lifecycle registry
entry or event.

Fact: the source packet is produced by
`tools/research_agents/candidate_review_packet_agent.py` as scratch-only,
non-canonical JSON and Markdown.

Decision: a future crossing may only happen after full source content review,
explicit human approval, source-hash validation, denominator preservation,
validator/integrity preflight, append-only canonical write, post-write
validation, and audit reporting.

## Current Non-Canonical Pipeline

Current scratch pipeline:

```text
idea formalizer scratch artifact
-> formalizer-runner bridge scratch packet, denominator ledger, runner artifact
-> robustness diagnostician scratch diagnostics and review packet
-> candidate-review packet JSON and Markdown
```

Current candidate-review packet fields include source paths and SHA-256 hashes,
approval metadata, strategy summary, data/funding posture, denominator counts,
row dispositions, runner metrics summary, robustness completed/skipped
diagnostics, missing-data limitations, evidence gaps, blockers, human-review
questions, next evidence steps, and non-authority flags.

The packet's strongest allowed conclusion is: candidate may be worth human
review for further evidence.

## Design Scope

This design covers:

- the proposed crossing contract;
- the required human approval artifact shape;
- content-before-lock review discipline;
- source packet requirements;
- field-level mapping from scratch packet to existing canonical lifecycle
  schema surfaces;
- provenance, lineage, denominator, data-availability, funding, and missing
  diagnostic preservation;
- append-only/no-overwrite semantics;
- validator and integrity gates;
- future ToolContext permission shape;
- audit requirements;
- stop conditions;
- the Karl-gated build boundary.

## Explicit Non-Scope

This package does not:

- implement the crossing;
- write canonical candidate lifecycle registry entries;
- modify canonical candidate registry data;
- modify canonical Result Populations, Strategy Specs, Variant Manifests,
  Sweep Plans, trial logs, or lifecycle changes;
- create promotion, readiness, registration, freeze, paper/live, runtime, OMS,
  risk, reconciliation, capital, broker/exchange, credential, provider/API, or
  network behavior;
- change schemas, validators, query-layer behavior, ToolContext permissions,
  configs, dependencies, data, runner, backtester, compiler, or protected
  runtime paths.

## Authority Model

Fact:

- Scratch candidate-review packets have no canonical authority.
- Existing ToolContext policy hard-blocks canonical writes, candidate
  registration, lifecycle transition, promotion, readiness, paper/live,
  runtime, OMS, risk, reconciliation, capital, credentials, network, provider
  memory as truth, gate bypass, and evidence suppression/deletion.
- `research/schemas/candidate_lifecycle_registry.schema.json` is
  real-capable but currently fixture-only under committed repo truth.
- `research/lifecycle_changes/*.lifecycle_change.json` are committed canonical
  lifecycle-change artifacts for H-001 through H-010 and use a different
  lifecycle vocabulary.

Decision:

- Human approval authorizes only the narrow crossing write described by the
  approval artifact.
- Approval does not imply promotion, readiness, paper/live qualification,
  ranking, recommendation, execution, risk, capital, or broker/exchange
  authority.
- Provider memory, agent memory, chat summaries, labels, comments, and PR merge
  state are not repo truth.

## Human Approval Artifact

The future approval artifact must be structured data, committed or otherwise
stored under a later approved canonical/audit path. It must include at least:

| Field | Required meaning |
|---|---|
| `approval_id` | Stable approval identifier. |
| `approved_by` | Human approver identity or gate owner. |
| `approval_timestamp_utc` | UTC timestamp of explicit approval. |
| `approval_scope` | Must identify canonical candidate crossing only. |
| `source_candidate_review_packet_path` | Repo-relative path to the reviewed packet JSON. |
| `source_candidate_review_packet_hash` | SHA-256 of the reviewed packet JSON. |
| `source_formalizer_artifact_path` / `source_formalizer_artifact_hash` | Source formalizer artifact binding. |
| `source_bridge_artifact_path` / `source_bridge_artifact_hash` | Source bridge review packet binding. |
| `source_robustness_artifact_path` / `source_robustness_artifact_hash` | Source robustness packet or diagnostics binding. |
| `source_denominator_ledger_path` / `source_denominator_ledger_hash` | Source denominator ledger binding. |
| `source_bridge_result_artifact_path` / `source_bridge_result_artifact_hash` | Optional scratch Result Population-shaped source binding when present. |
| `content_reviewed` | Must be `true`; affirms full content was reviewed. |
| `canonical_crossing_allowed` | Must be `true`; authorizes only the crossing scope. |
| `canonical_write_scope` | Exact target family and allowed operation. |
| `append_only` | Must be `true`. |
| `no_promotion` | Must be `true`. |
| `no_readiness` | Must be `true`. |
| `operator_acknowledges_missing_diagnostics` | Must be `true` when packet records skipped or missing diagnostics. |
| `operator_acknowledges_data_availability_warnings` | Must be `true` when packet records warnings/blockers. |
| `operator_acknowledges_funding_mode` | Must be `true` and name the packet funding mode. |

The approval cannot be inferred from file presence, PR merge, label, comment,
status entry, agent recommendation, packet summary, or prior operator approval
for noncanonical scratch packet generation.

## Content-Before-Lock Review Discipline

The crossing sequence is:

```text
scratch candidate-review packet
-> full content surfaced to human
-> explicit human approval artifact
-> validator/integrity preflight
-> append-only canonical candidate lifecycle write
-> post-write validation/query integrity check
-> audit record / report packet
```

Required discipline:

- surface the full candidate-review packet JSON and Markdown to the human;
- surface linked source paths/hashes, denominator ledger, robustness summary,
  skipped diagnostics, data warnings, funding mode, blockers, and open
  questions before approval;
- verify source hashes after approval and before write;
- freeze only the reviewed source content, not a summary;
- reject approval artifacts that do not state `content_reviewed=true`.

Explicit prohibitions:

- no label-only approval;
- no silent canonical creation;
- no canonical write from packet summary without source content;
- no using provider memory as repo truth;
- no dropping denominator counts or skipped diagnostics;
- no mutation of prior evidence;
- no candidate promotion without a separate gate;
- no paper/live readiness implication.

## Source Packet Requirements

The source packet must:

- be the structured JSON candidate-review packet, not only Markdown;
- have `schema_version=candidate_review_packet_v1`;
- include source formalizer, bridge, robustness, approval, and denominator
  references with SHA-256 hashes;
- include full denominator counts and row dispositions;
- preserve all completed, failed, invalid, pruned, and blocked rows;
- include non-authority flags;
- include data availability warnings/blockers and funding mode;
- include completed/skipped robustness diagnostics and missing-input states;
- include human-review questions and next evidence steps;
- pass a future packet contract validator before crossing.

## Field-Level Crossing Map

The future build must not invent schema fields. Where the current canonical
schema has no target field, the target is marked `needs schema decision`.

| Candidate-review packet field | Canonical candidate lifecycle registry field | Required transformation | Validator/gate | Preserved caveat | Source hash/path |
|---|---|---|---|---|---|
| `strategy_summary.strategy_family` | `candidates[].strategy_family` | Copy normalized family text if human-approved. | Packet schema and lifecycle registry schema. | Scratch summary is not strategy approval. | Packet hash plus formalizer path/hash. |
| `strategy_summary.idea_summary` | `candidates[].description` | Human-reviewed description; do not copy provider memory. | Content-reviewed approval. | Summary remains source-derived and non-authoritative. | Packet hash plus formalizer path/hash. |
| `strategy_summary.timeframe` | `candidates[].primary_timeframe` | Map only if within locked timeframe enum. | Lifecycle registry schema enum. | Missing or unsupported timeframe stops. | Packet hash. |
| `strategy_summary.symbols` | `candidates[].instrument` / `market` | Require BTCUSDT / crypto perpetual match. | Lifecycle registry schema consts. | Any cross-asset or weekly mismatch needs schema decision. | Packet hash. |
| `source_formalizer.path/hash` | `candidates[].source_refs.source_design_refs` or `approval_note_refs` | Record as `artifact_ref` if artifact type/relationship fits. | Source hash verification. | Formalizer artifact is scratch source, not canonical evidence. | Formalizer path/hash. |
| `source_formalizer.draft_strategy_spec_path/hash` | `source_refs.strategy_spec_refs` | Reference as review/source lineage only when present. | Source hash verification. | Draft Strategy Spec is scratch and not canonical. | Draft path/hash. |
| `source_bridge.review_packet_path/hash` | `evidence_links` or `source_refs.source_design_refs` | Reference as context/source lineage if schema type permits; otherwise needs schema decision. | Source hash verification. | Bridge packet is scratch, not evidence. | Bridge packet path/hash. |
| `source_bridge.runner_artifact_path/hash` | `evidence_links` with `artifact_type=result_population` only if future gate accepts scratch-shaped source refs; otherwise needs schema decision. | Preserve as source reference, not canonical RP. | Result Population-shaped scratch artifact validation and hash check. | Scratch Result Population-shaped artifact is not canonical evidence. | Runner artifact path/hash. |
| `source_robustness.diagnostics_path/hash` | `evidence_links` with `artifact_type=robustness_report` if accepted; otherwise needs schema decision. | Record diagnostics reference. | Source hash verification. | Diagnostics are scratch and skipped inputs stay visible. | Diagnostics path/hash. |
| `source_robustness.review_packet_path/hash` | `evidence_links` or `source_refs.source_design_refs` | Record robustness packet reference. | Source hash verification. | Packet is advisory, not robustness approval. | Robustness packet path/hash. |
| `operator_approval.path/hash` | `source_refs.approval_note_refs` or event `blocking_or_exception_refs` | Link explicit approval artifact after validating fields. | Approval artifact validator. | Noncanonical packet approval is not crossing approval. | Approval path/hash. |
| Future crossing approval artifact | `source_refs.approval_note_refs`, event `related_evidence_links`, or needs schema decision | Link the actual crossing approval artifact. | Approval artifact validator and content-reviewed check. | Approval grants only append-only crossing. | Approval path/hash. |
| `denominator_snapshot.counts` | needs schema decision | Preserve completed/failed/invalid/pruned/blocked counts exactly. | Denominator equality across packet/ledger/robustness. | No winner-only, successful-only, or executed-only denominator. | Packet hash plus ledger path/hash. |
| `denominator_snapshot.row_disposition` | needs schema decision | Preserve every row disposition or link ledger. | Ledger row count and status count check. | Failed, invalid, pruned, and blocked rows remain visible. | Ledger path/hash. |
| `lineage_consistency.denominator_counts` | needs schema decision | Cross-check against packet and ledger counts. | Pre-write denominator gate. | Any mismatch stops. | Packet hash plus ledger path/hash. |
| `runner_metrics_summary.top_metrics` | needs schema decision | Reference or summarize only if schema allows; avoid parallel metric truth. | Human content review and source hash. | Metrics remain in source packet/artifact. | Packet hash plus bridge result path/hash. |
| `runner_metrics_summary.manual_reconciliation_result` | needs schema decision | Preserve reconciliation summary or link source packet. | Source hash verification. | Manual reconciliation does not approve candidate. | Packet hash. |
| `robustness_summary.diagnostics_completed` | needs schema decision | Preserve completed diagnostic names or source link. | Robustness source hash check. | Completed diagnostics are scratch advisory. | Robustness path/hash. |
| `robustness_summary.diagnostics_skipped` | needs schema decision | Preserve skipped diagnostics explicitly. | Missing-diagnostic acknowledgment required. | Skipped diagnostics cannot be hidden. | Packet hash plus robustness path/hash. |
| `missing_data_limitations` | needs schema decision | Preserve per-trade, fold/OOS, and funding-stress missing-input states. | Missing diagnostic/data gate. | No fabricated trade rows or folds. | Packet hash. |
| `data_and_funding_summary.data_availability_warnings` | needs schema decision | Preserve warnings verbatim or reference packet. | Data availability acknowledgment required. | Recent-only/vendor-only warnings remain visible. | Packet hash plus bridge packet hash. |
| `data_and_funding_summary.data_availability_blockers` | `candidates[].blocking_reason` only for summary; detailed blockers need schema decision | Human-reviewed blocker summary. | Data availability gate. | Blockers cannot be reinterpreted as pass. | Packet hash. |
| `data_and_funding_summary.funding_mode` | needs schema decision | Preserve requested/effective funding mode. | Funding acknowledgment required. | Funding-off or unsupported funding-on must remain explicit. | Packet hash. |
| `evidence_gaps` | `review_metadata.unresolved_questions`, `blocking_reason`, or needs schema decision | Preserve as review/gap text without creating authority. | Human content review. | Gaps are not approvals. | Packet hash. |
| `blockers` | `blocking_reason` or needs schema decision | Preserve blocking reason summary. | Human content review. | Blockers must stop if unresolved and required. | Packet hash. |
| `recommended_human_review_questions` | `review_metadata.unresolved_questions` | Copy or curate questions. | Content-reviewed approval. | Questions remain open review prompts. | Packet hash. |
| `recommended_next_evidence_steps` | `required_next_review` or needs schema decision | Summarize next review/evidence requirement. | Human approval artifact. | Next steps are not readiness. | Packet hash. |
| `non_authority_flags` | `non_authority_declaration` | Map to required true non-authority declarations. | Lifecycle registry validator. | No promotion/readiness/paper/live/trading authority. | Packet hash. |

## Provenance / Lineage Requirements

The future crossing must preserve:

- packet path and hash;
- formalizer path and hash;
- draft Strategy Spec path and hash if present;
- bridge packet path and hash;
- bridge scratch runner artifact path and hash if present;
- denominator ledger path and hash;
- robustness diagnostics path and hash;
- robustness review packet path and hash;
- crossing approval artifact path and hash;
- source run IDs;
- target candidate/event ID;
- ToolContext audit record IDs or paths if implemented;
- post-write validation report path and hash.

All hashes must be recomputed immediately before write. A mismatch stops.

## Denominator Preservation Requirements

The crossing must preserve the complete denominator:

- completed;
- failed;
- invalid;
- pruned;
- blocked;
- declared trial count;
- ledger row count;
- every row disposition.

No crossing may use successful-only, executed-only, winner-only, or cleaned-up
denominators. If the target schema cannot hold the counts directly, the
canonical record must preserve a hash-bound link to the ledger and mark the
detailed mapping as `needs schema decision` until extended.

## Data Availability and Funding Caveat Preservation

The crossing must preserve:

- data availability warnings and blockers from the bridge packet;
- open-interest recent-only or non-reconstructable caveats;
- liquidation/vendor/captured-history caveats;
- public archive or recent-only feature distinctions;
- requested and effective funding mode;
- funding-off stress limitation;
- any funding-on unsupported/blocking state.

The approval artifact must include explicit operator acknowledgments for data
availability warnings and funding mode.

## Missing-Diagnostic Preservation

The crossing must preserve:

- skipped robustness diagnostics;
- missing per-trade rows;
- missing fold/OOS inputs;
- funding-stress not performed or not applicable;
- any unavailable metric diagnostic;
- follow-up evidence steps required before stronger claims.

Missing diagnostics cannot be hidden, converted to pass, or treated as
candidate readiness.

## Append-Only / No-Overwrite Semantics

Future crossing writes must obey:

- new candidate lifecycle entry or new lifecycle event only;
- no overwrite of existing canonical entries;
- no deletion;
- no silent replacement of packet contents;
- corrections require explicit correction or supersession event;
- all source hashes remain preserved;
- prior evidence remains immutable and visible;
- any collision on candidate ID, event ID, event sequence, or source hash stops.

## Validator and Integrity Gates

Pre-write gates:

- candidate-review packet contract valid;
- packet and all source hashes match approval artifact;
- approval artifact valid, explicit, content-reviewed, append-only, no
  promotion, and no readiness;
- denominator counts match across packet, ledger, robustness diagnostics, and
  robustness review packet;
- non-authority flags present and true;
- skipped diagnostics, data warnings, and funding mode visible and
  acknowledged;
- target schema/storage decision exists;
- ToolContext allows only the explicit crossing action under approval;
- no paper/live/readiness/promotion/runtime fields are set;
- no source path escapes repo-relative allowed locations;
- no provider memory or summary-only source is used.

Post-write gates:

- selected lifecycle registry or lifecycle-change validator passes;
- older candidate registry validator passes if touched by a future package;
- Result Population and data-availability validators still pass;
- query views list successfully;
- integrity views can find the new candidate event or entry;
- source packet hash is retained;
- denominator link or counts are retained;
- no promotion/readiness/paper/live state is created;
- audit record/report packet exists;
- `git diff --check` passes.

## ToolContext / Permission Design

Future action shape:

```text
human_approved_canonical_candidate_crossing
```

Required constraints:

- requires valid approval artifact;
- requires `content_reviewed=true`;
- requires source candidate-review packet path and hash;
- requires approval artifact path and hash;
- requires source formalizer, bridge, robustness, and denominator ledger
  hashes;
- allows only append-only candidate lifecycle entry/event write selected by the
  future storage design;
- forbids promotion, readiness, ranking, recommendation, paper/live, runtime,
  OMS, risk, reconciliation, capital, credentials, private endpoints, network,
  provider memory, and evidence deletion/suppression;
- audits every allow/block decision before execution.

This package does not implement that action or change ToolContext.

## Audit Requirements

The future crossing report must record:

- package ID and git commit;
- target storage path;
- target candidate/event ID;
- approval artifact path/hash;
- packet path/hash;
- all source paths/hashes;
- denominator counts and row count;
- missing diagnostic acknowledgments;
- data/funding acknowledgments;
- pre-write validation command results;
- ToolContext allow/block audit records;
- post-write validation command results;
- changed-file list;
- explicit non-authority statement.

## Stop Conditions

The future build must stop if:

- approval artifact is missing or label-only;
- `content_reviewed` is missing or false;
- `canonical_crossing_allowed` is missing or false;
- packet source hash mismatch;
- formalizer, bridge, robustness, runner, or ledger hash mismatch;
- denominator mismatch;
- missing diagnostics are hidden;
- data availability warnings are missing;
- funding mode is missing;
- canonical write would overwrite an existing entry;
- correction would mutate prior evidence instead of appending an event;
- candidate promotion/readiness/paper/live status would be implied;
- ToolContext cannot enforce the gate;
- target schema/storage decision is unresolved;
- validators or integrity views fail;
- implementation requires touching protected runtime, OMS, reconciliation,
  risk, safe mode, configs, live-trading paths, credentials, dependencies, or
  private endpoints.

## Karl-Gated Build Boundary

Implementation is Karl-gated and out of scope here.

A future build package must separately authorize:

- target canonical storage path;
- lifecycle state vocabulary;
- approval artifact storage and schema;
- packet/source contract validator;
- any candidate lifecycle registry schema changes;
- any lifecycle-change schema or validator changes;
- ToolContext permission changes;
- post-write query/integrity view changes;
- exact tests and validation commands.

## Open Questions

- Which target is canonical for this crossing:
  `research/candidate_lifecycle_registry/`,
  `research/lifecycle_changes/`, `research/candidate_registry.jsonl`, or a new
  crossing-audit artifact?
- Which lifecycle state vocabulary wins for new candidate lifecycle records?
- Should denominator counts and skipped diagnostics become first-class schema
  fields or remain hash-bound source references?
- Where should approval artifacts live?
- What ID allocator owns `approval_id`, candidate IDs, and event IDs?
- Which query views must be added to prove a new crossing is discoverable?
- Should a future crossing be allowed to create a new candidate only, append an
  event to an existing candidate only, or both under separate scopes?

## Future Implementation WP Shape

Recommended split:

1. Storage/schema decision lock for target artifact family and state
   vocabulary.
2. Approval artifact schema/validator design and fixture-only tests.
3. Packet/source contract validator and denominator/hash preflight tests.
4. ToolContext action implementation with blocked-action tests.
5. Append-only crossing writer implementation against fixtures only.
6. Query/integrity surfaces for discoverability and post-write checks.
7. Separately approved first real crossing package, if Main/Karl authorize it.

Each package must start from refreshed `main`, inspect changed files, validate
exact scope, and stop on protected-boundary conflict.
