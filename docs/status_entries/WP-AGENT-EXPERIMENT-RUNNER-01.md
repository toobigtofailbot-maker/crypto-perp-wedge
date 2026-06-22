# WP-AGENT-EXPERIMENT-RUNNER-01 Branch State

## Scope Summary

Adds a bounded, deterministic experiment-runner agent that consumes an explicitly operator-approved PR #544 formalizer output and writes only non-canonical scratch experiment packets, a complete denominator ledger, scratch results, and a human-review packet.

Branch: `agent/experiment-runner-01`.
Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\agent-experiment-runner-01`.
Base: refreshed `origin/main` at `7cf813a` after PR #544 merged.

## Main Authorization

Main authorized this second research-agent package after the idea formalizer. Scope is limited to ToolContext-routed scratch reads, bounded fixture execution, scratch writes, denominator preservation, review packets, availability guards, funding metadata, tests, discovery notes, and this status entry.

## Dependency on WP-AGENT-IDEA-FORMALIZER-01

The agent consumes `agent_formalized_idea_v1` from `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/<run_id>/formalized_idea.json`. It can read an optional scratch draft Strategy Spec but never mutates or promotes it. Unsupported, rejected, malformed, or non-scratch formalizer inputs fail closed.

## ToolContext Integration

The distinct `experiment_runner` role can read non-secret research/test fixtures, its own scratch prefix, and the formalizer scratch prefix. It can write only beneath `scratch/WP-AGENT-EXPERIMENT-RUNNER-01/` and execute only `noncanonical_experiment_run` targeted beneath that WP's `outputs/` prefix. Approval bypass, canonical writes, sweep/backtest actions, lifecycle actions, protected trading actions, credentials, private endpoints, network, funding mutation, evidence suppression/deletion, and ToolContext bypass remain blocked and audited.

## Input Contract

Inputs are a scoped formalizer artifact path, a matching approval marker in the same formalizer run directory, bounded trial declarations, and `ExperimentRunnerConfig`. Trial declarations require strategy family, variant ID, unique trial ID, and parameter object. The package-local executor is deterministic and fixture-only.

## Human Approval Requirement

Execution requires `approved_for_noncanonical_experiment: true`, `approved_by: operator`, `approval_scope: noncanonical_scratch_only`, a non-empty UTC approval timestamp, and the matching formalizer run ID. Invalid or missing approval triggers an audited `approval_gate_bypass` block before execution or output writes.

## Runner Integration

The merged offline sweep runner requires a schema-valid Strategy Spec, frozen Variant Manifest, and Sweep Plan. PR #544 supplies none of the latter two and its Strategy Spec is scratch draft only. Real runner integration therefore remains explicitly blocked. This package uses the authorized fallback: contract implementation plus a local fixture executor, with a documented later-contract blocker in every run/review packet.

## Denominator Preservation

Every declared trial receives exactly one ledger row with one of `completed`, `failed`, `invalid`, `pruned`, or `blocked`. Rows include source lineage, approval scope, identifiers, params, input/output hashes, metrics or null, deterministic timestamps, reasons, and non-authority flags. An invariant rejects missing, duplicate, winner-only, or unsupported-status ledgers before artifacts are written.

## Funding Mode Handling

Experiment configuration defaults `funding_cost_mode` to `off`. Explicit `on` is visible in run and review metadata. The fixture executor performs no funding calculation, and the agent does not mutate config or global funding behavior.

## Data Availability Guard Handling

Availability checks reuse formalizer feature assessments. Full-history public experiments block recent-only, snapshot-only, streaming-only, vendor-only, and otherwise constrained features. Public archive taker flow proceeds only with a configured present local fixture/source. Open interest is never treated as reconstructable from trades, and liquidation history requires vendor/captured fixture data.

## Review Packet

Each approved run writes `experiment_run_packet.json`, `denominator_ledger.json`, `scratch_results.json`, and `human_review_packet.json` beneath the package output root. Review packets include source summary, approval metadata, runner configuration, all five counts, top metrics if any, full ledger and artifact paths, validation status, data and integration blockers, and explicit non-authority flags.

## Adversarial Boundary Tests

Tests prove blocked and audited behavior for missing approval; canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, and trial-log writes; candidate registration/promotion/freeze; paper/live/runtime; OMS/risk/reconciliation/capital; private endpoints and credentials; global funding mutation; evidence suppression/deletion; ToolContext bypass; real sweep execution; output-prefix escape; denominator dropping; and constrained-data full-history claims. Blocked operations do not mutate their sentinel target.

## Validation Status

- Ruff check for changed Python: PASS.
- Focused experiment-runner, formalizer, and ToolContext tests: PASS, 135 tests.
- Strategy Spec, Result Population, and data-availability regression tests: PASS, 171 tests.
- Strategy Spec validator: PASS.
- Result Population validator: PASS.
- Data feature availability validator: PASS.
- Query-view discovery: PASS, 124 views listed.
- Repo-venv Python 3.11 full pytest: baseline-limited, 2,036 passed, 1 skipped, 1 failed, and 6 warnings in 1,428.78 seconds. The sole failure is `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because the known gitignored isolated-worktree D4A normalized-data fixture is absent (`normalized_data_local_exists` is false). It is unrelated to this package diff.
- Diff-scope summary: PASS; seven intended files and no forbidden-path match.
- `git diff --check`: PASS.

## Boundary Summary

Changed implementation is limited to `tools/research_agents/`, the narrow ToolContext permissions extension, and tests. Package artifacts are limited to this status entry and package scratch discovery note. No canonical artifact, schema, validator behavior, query layer, dependency, existing runner/backtester, config, runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, credential, private endpoint, candidate lifecycle, or `docs/project_status.md` file changes.

## Non-Authority Statement

The agent, fixture outcomes, ledgers, scratch results, and review packets are not canonical, evidence, candidate authority, promotion authority, or paper/live readiness. They require human review and create no registration, freeze, approval, ranking, recommendation, readiness, runtime, risk, capital, or execution authority.
