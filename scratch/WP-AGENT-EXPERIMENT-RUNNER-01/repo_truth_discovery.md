# WP-AGENT-EXPERIMENT-RUNNER-01 Repo-Truth Discovery

## Base and dependency

- Fresh base: `origin/main` at `7cf813a`, the merge commit for PR #544.
- PR #544 adds the formalizer implementation, tests, provider seam, package status, and a narrow ToolContext extension.
- The formalizer contract is present and compatible with a scratch-only runner contract.

## Formalizer output contract

- Output root: `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/<run_id>/`.
- Primary artifact: `formalized_idea.json`, schema `agent_formalized_idea_v1`.
- Review artifact: `human_review_packet.json` with the same formalizer result shape.
- Relevant fields: `run_id`, `status`, `input`, `capability_assessment`, `research_object`, `draft_strategy_spec`, and `non_authority`.
- An optional validator-clean draft Strategy Spec is written beside the formalized idea and remains scratch-only.
- PR #544 does not define an experiment approval marker. This package therefore requires a separate operator marker in the same formalizer run directory with the exact non-canonical scope and matching source run ID.

## Runner and denominator surfaces

- `tools/research_runner/run_offline_sweep.py` requires a schema-valid Strategy Spec, frozen Variant Manifest, and Sweep Plan with matching canonical lineage. It cannot consume the PR #544 output directly.
- The offline runner can write a Result Population to a caller-supplied non-canonical directory, but doing so still requires the frozen parent artifacts that the formalizer does not create.
- The canonical Result Population schema preserves a committed denominator across `successful`, `failed`, `invalid`, `excluded`, `errored`, `aborted`, `filtered`, `data_unavailable`, and `not_attempted` outcomes.
- The active package requires a different scratch review vocabulary: `completed`, `failed`, `invalid`, `pruned`, and `blocked`. A package-local result-population-like artifact is therefore appropriate; it is not submitted to or presented as the canonical Result Population schema.
- Safe integration choice: implement the contract and fixture-only deterministic executor now. Keep real `run_offline_sweep` integration blocked pending a later approved contract that supplies compatible Variant Manifest and Sweep Plan inputs.

## ToolContext policy

- Existing roles include `non_canonical_runner`, but `backtest_execution` and `sweep_execution` are hard prohibited for every role.
- Existing scratch writes are limited to the active WP prefix; canonical research paths, trial log, candidate registry, `docs/project_status.md`, dependencies, protected trading paths, credentials, private endpoints, network, funding-mode mutation, evidence suppression/deletion, and ToolContext bypass are hard blocked.
- Existing non-secret reads cover `research/` and `tests/fixtures/`; PR #544 separately allows the formalizer to read its own scratch prefix.
- This package needs a distinct `experiment_runner` role, reads of the formalizer scratch prefix, writes only below its active scratch prefix, and one `noncanonical_experiment_run` action restricted to its active `outputs/` prefix.

## Data availability and fixtures

- The formalizer exposes availability rows through `capability_assessment.feature_assessments`.
- Taker-flow archive derivation is conditional on verified trade or aggregate-trade archive coverage and deterministic reconstruction. Safe committed fixtures exist under `tests/fixtures/takerflow_archive_recon/` and `tests/fixtures/data_ingestion/perp_public_data/`.
- Open interest is snapshot/recent-only in public repo truth and cannot be reconstructed from trades.
- Long/short ratio history is recent-only public REST.
- Liquidation history is vendor-only and not compiler-visible in the merged catalog.

## Funding behavior

- After PR #543, `lib.backtest.run_backtest` defaults `funding_cost_mode` to `off`; `on` is explicit opt-in.
- The current offline sweep runner does not expose or pass a funding-mode parameter, so it inherits the backtest default-off behavior and cannot express explicit-on metadata through its public call.
- This package defaults to `off`, records explicit `on` in scratch metadata when requested, and makes no global funding-mode mutation.

## Authority conclusion

The safe mergeable scope is a ToolContext-routed, fixture-only experiment contract that reads approved PR #544 scratch outputs, preserves every declared trial in a scratch denominator ledger, writes scratch review packets, and blocks incompatible real sweep execution. No canonical artifact, schema, validator, query layer, runner semantics, backtester, runtime, or candidate lifecycle surface needs modification.
