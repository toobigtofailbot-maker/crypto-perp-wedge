# WP-AGENT-CANDIDATE-REVIEW-PACKET-01 Branch State

## Scope Summary

Adds a deterministic, ToolContext-routed candidate-review packet agent that consumes formalizer, bridge, and robustness scratch outputs plus an explicit operator candidate-review approval marker. It writes only scratch JSON and Markdown review packets under the active package prefix.

## Main Authorization

Main authorized this fourth bounded research-agent package after the robustness diagnostician. The package creates no canonical artifact, evidence, candidate lifecycle, ranking, readiness, promotion, paper/live, runtime, risk, capital, broker/exchange, credential, private endpoint, network, or execution authority.

## Dependency on WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01

The branch is based on `2dd8673`, the PR #547 merge. Focused tests generate deterministic upstream bridge and robustness artifacts through merged code rather than requiring pre-existing untracked scratch outputs.

## Repo-Truth Discovery

Discovery recorded the formalizer artifact contract, bridge packet and denominator ledger contract, robustness diagnostics/review-packet contract, lifecycle helper packet surfaces, canonical lifecycle registry boundaries, and ToolContext path/action policy. Details are in `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/repo_truth_discovery.md`.

## ToolContext Integration

The existing `candidate_review_packet_preparer` role is used. The package adds one action, `build_scratch_candidate_review_packet`, scoped to `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/`. Reads are limited to active package scratch, the formalizer/bridge/robustness upstream scratch output prefixes, and read-only candidate-lifecycle helper/example files. Writes remain limited to active package scratch.

## Input Contract

Required runtime inputs are formalizer research object path, bridge review packet path, bridge denominator ledger path, robustness diagnostics path, robustness review packet path, and operator candidate-review approval path. Optional inputs are formalizer draft Strategy Spec path and bridge Result Population-shaped scratch artifact path. Source IDs, paths, and hashes are preserved where available.

## Human Approval Requirement

The approval marker must set `approved_for_noncanonical_candidate_review_packet=true`, identify `approved_by=operator`, use `approval_scope=noncanonical_scratch_candidate_review_only`, include a timestamp, and match both source bridge and robustness run IDs. Missing, false, wrong-scope, or mismatched approval is blocked and audited before packet outputs are created.

## Candidate Lifecycle Integration

The agent reads candidate-lifecycle helper files and scratch packet examples as interface context only. It does not write candidate lifecycle registry entries, lifecycle-change artifacts, or lifecycle transition outputs.

## Evidence / Denominator Preservation

The agent requires equality across bridge review counts, ledger counts, computed ledger row counts, robustness diagnostics denominator integrity, and robustness review denominator integrity. It preserves all `completed`, `failed`, `invalid`, `pruned`, and `blocked` counts and row dispositions. Shrinkage routes through an audited `evidence_suppression` block.

## Robustness Summary Handling

The packet summarizes completed and skipped robustness diagnostics, bootstrap/sensitivity summaries, missing OOS/fold inputs, missing real trade rows, and funding-off stress limitations. It does not claim robustness when diagnostics were skipped.

## Missing-Data Handling

Missing per-trade rows, missing fold/OOS inputs, and funding-off status remain explicit evidence gaps. Data availability warnings and blockers propagate from the bridge and robustness packets without reinterpretation.

## Data Availability and Funding Handling

Bridge data warnings/blockers and funding mode are copied into the packet. Funding stress remains marked as not performed when bridge truth is funding-off. No global funding mode is mutated.

## Review Packet Outputs

The agent writes:

- `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/<run_id>/candidate_review_packet.json`
- `scratch/WP-AGENT-CANDIDATE-REVIEW-PACKET-01/outputs/<run_id>/candidate_review_packet.md`

The packet includes source metadata and hashes, approval metadata, strategy summary, optional draft Strategy Spec summary, data/funding posture, denominator snapshot, runner metrics summary, robustness summary, skipped diagnostics, missing-data limitations, evidence gaps, blockers, human-review questions, next evidence steps, and full non-authority flags.

## Adversarial Boundary Tests

Tests cover approval bypass, lineage mismatch, denominator shrinkage, canonical candidate registry/Result Population/Strategy Spec/Variant Manifest/Sweep Plan/trial-log writes, registration/freeze/promotion/readiness, ranking-as-promotion-ready, paper/live/runtime, OMS/risk/reconciliation/capital, private endpoints, credentials, global funding mutation, evidence suppression/deletion, ToolContext bypass, fabricated robustness diagnostics, provider/API/network calls, and out-of-prefix packet builds.

## Validation Status

- Candidate-review packet, robustness, bridge, experiment-runner, formalizer, and ToolContext regressions: PASS, 241 tests.
- Result Population and data-availability validator tests: PASS, 69 tests.
- Candidate lifecycle helper tests: PASS, 5 tests.
- Result Population registry validator: PASS.
- Data feature availability registry validator: PASS.
- Query view discovery: PASS, 124 views listed.
- Diff-scope summary: PASS; intended files only and no forbidden-path match.
- `git diff --check`: PASS.
- Full pytest initially completed with 2,142 passed, 1 skipped, 1 failed, and 6 warnings. The sole failure was the documented isolated-worktree baseline `test_default_fixture_mapping_uses_rp_2592_lineage`, because its gitignored D4A normalized CSV was absent (`normalized_data_local_exists` was false).
- After copying the existing local gitignored D4A normalized fixture from the root checkout into the same worktree path for validation only, the final full run passed: 2,143 passed, 1 skipped, 6 warnings.

## Boundary Summary

Changed implementation is limited to `tools/research_agents/`, the narrow ToolContext permission extension, tests, this status entry, and the package scratch discovery note. No canonical artifact, schema, validator behavior, query-layer behavior, runner, backtester, compiler, config, dependency, data, project-status, runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, credential, private endpoint, or existing canonical artifact is modified.

## Non-Authority Statement

All candidate-review packet outputs are scratch-only, non-canonical, non-evidence, not candidate authority, not promotion authority, not ranking authority, not paper/live readiness, not a trading signal, and human-review-required.
