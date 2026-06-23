# WP-AGENT-CANDIDATE-REVIEW-PACKET-01 Repo-Truth Discovery

## Formalizer Output Contract

- Source: `tools/research_agents/idea_formalizer_agent.py`
- Primary artifact: `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/<run_id>/formalized_idea.json`
- Required shape observed: `schema_version=agent_formalized_idea_v1`, `run_id`, `status`, `research_object`, `draft_strategy_spec`, `capability_assessment`, and `non_authority`.
- Draft Strategy Spec, when produced, remains in the formalizer scratch output prefix and is draft/non-canonical.
- Repo-truth constraint: formalizer output is advisory scratch only; provider output and provider memory have no repo authority.

## Bridge Output Contract

- Source: `tools/research_agents/formalizer_runner_bridge.py`
- Human review packet: `scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/<run_id>/human_review_packet.json`
- Denominator ledger: `scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/<run_id>/denominator_ledger.json`
- Optional runner artifact: scratch Result Population-shaped artifact bound in `runner_artifact_paths`.
- Required bridge facts: `run_id`, source idea summary, derived scratch input paths, runner invocation metadata, denominator counts, manual reconciliation result, top metrics, full ledger path, data availability warnings/blockers, funding mode, and non-authority flags.
- Denominator truth is the full ledger with `completed`, `failed`, `invalid`, `pruned`, and `blocked` counts. Winner-only reporting is forbidden.

## Robustness Diagnostics Output Contract

- Source: `tools/research_agents/robustness_diagnostician_agent.py`
- Diagnostics artifact: `robustness_diagnostics.json`
- Review packet: `robustness_review_packet.json`
- Required robustness facts: source bridge run ID, source paths and hashes, approval metadata, validator status, attempted/completed/skipped diagnostics, bootstrap and sensitivity summaries, denominator integrity, missing fold/per-trade/funding inputs, warnings/blockers, follow-up gaps, and non-authority flags including `not ranking authority`.
- Missing trade rows, fold inputs, and funding-on inputs remain explicit skipped/queued states. No diagnostics may be fabricated.

## Candidate Lifecycle Helper / Packet Interfaces

- Source helper: `tools/candidate_lifecycle/lifecycle_engine.py`
- CLI wrapper: `tools/candidate_lifecycle/build_candidate_review_packet.py`
- Scratch examples: `scratch/WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01/candidate_review_packet.md` and `candidate_lifecycle_report.json`
- The lifecycle helper prepares human-gated scratch review packets and blocks auto-promotion/readiness/paper/live authority.
- This package consumes those helper files only as read-only packet-interface context. It does not call lifecycle transitions or write lifecycle registry entries.

## Canonical Candidate Lifecycle Registry Boundaries

- Source schema: `research/schemas/candidate_lifecycle_registry.schema.json`
- The registry schema is review/evidence shape only and explicitly creates no runtime, paper/live, OMS, risk, promotion, broker/exchange, or capital authority.
- Canonical registry writes remain forbidden by ToolContext path policy and package scope.

## ToolContext Action Types And Hard Prohibitions

- Source: `tools/agent_sandbox/permissions.py` and `tools/agent_sandbox/tool_context.py`
- Existing hard prohibitions cover canonical writes, candidate registration/promotion/readiness/freeze, trial-log mutation, runtime/paper/live/protected trading paths, credentials, private endpoints, network access, funding-mode mutation, evidence suppression/deletion, ToolContext bypass, and fabricated per-trade data.
- This package adds the scratch-only `build_scratch_candidate_review_packet` action, scoped to `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/`.
- The existing `candidate_review_packet_preparer` role is used. Its reads are limited to active scratch, upstream agent scratch output prefixes, and candidate-lifecycle helper/example surfaces.

## Scratch-Only Review-Packet Generation Helper

- No dedicated prior agent helper exists for synthesizing formalizer, bridge, and robustness outputs into one candidate-review packet.
- The lifecycle helper has a Markdown review-packet interface, but it is lifecycle oriented and not a substitute for this upstream-output packet.
- Decision: implement a new bounded agent under `tools/research_agents/candidate_review_packet_agent.py`.

## Safe Fields To Summarize

- Source paths and SHA-256 hashes.
- Formalizer research object summary and optional draft Strategy Spec metadata.
- Bridge run metadata, runner artifact reference, top metrics, data availability warnings/blockers, and funding mode.
- Full denominator counts and row dispositions across all five statuses.
- Robustness completed/skipped diagnostics, missing inputs, bootstrap/sensitivity summaries, and warning propagation.
- Human review questions and follow-up evidence steps.

## Advisory / Non-Authority Fields

- All packet outputs must remain scratch-only, not canonical, not evidence, not candidate authority, not promotion authority, not ranking authority, not paper/live readiness, not a trading signal, and human-review-required.
- Approval marker scope is only `noncanonical_scratch_candidate_review_only`.
- Strongest permitted recommendation language: candidate may be worth human review for further evidence.

## Stop Conditions Checked

- PR #547 is merged into local `main`.
- Robustness outputs can be generated through merged repo code.
- Required upstream contracts can be cross-checked by run IDs, paths, hashes, and denominator counts.
- No safe implementation required touching runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, schemas, validators, query-layer behavior, canonical artifacts, or `docs/project_status.md`.
