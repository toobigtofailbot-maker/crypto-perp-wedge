# WP-LABPROD-PIPELINE-GATES-ADAPTERS-05 Repo Truth Discovery

## Branch / Base

- Branch: `codex/wp-labprod-pipeline-gates-adapters-05`
- Base: `origin/main`
- Base SHA: `c3ca2c093c7d8be0b3642f04fb521189839b2ad3`
- Dependency merge: PR #623 is present on `main` as merge commit `c3ca2c0`.
- Open PR collision check: `gh pr list --state open --json number,title,headRefName,baseRefName,files,url --limit 100` returned `[]`.
- Suggested branch collision check: no local or remote `codex/wp-labprod-pipeline-gates-adapters-05` branch existed before branch creation.

## Runner Adapter Output Shape

- Runner adapter implementation: `tools/lab_pipeline/runner_adapter.py`.
- Entry point: `run_product_runner_adapter(...)`.
- Result metadata schema: `product_runner_adapter_result_v1`.
- Result metadata path produced by the runner package: `scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs/<LRUN>/runner_adapter_result.json`.
- Required downstream fields in `runner_adapter_result.json`:
  - `runner_adapter_run_id`;
  - `adapter_status`;
  - `noncanonical_status = noncanonical_product_scratch_only`;
  - `source_bindings.prepared_strategy_spec_path`;
  - `source_bindings.prepared_variant_manifest_path`;
  - `source_bindings.prepared_sweep_plan_path`;
  - `source_bindings.bridge_preparation_run_id`;
  - `source_bindings.product_pipeline_run_id`;
  - `source_bindings.execute_approval_path`;
  - `source_bindings.execute_approval_sha256`;
  - `runner_outputs.adapter_result_population_path`;
  - `runner_outputs.adapter_result_population_sha256`;
  - `runner_outputs.direct_result_population_path`;
  - `runner_outputs.direct_result_population_sha256`;
  - `denominator_counts`;
  - `runner_outcome_category_counts`;
  - `full_denominator_preserved = true`;
  - `winner_narrowing = false`;
  - `direct_runner_reconciliation.verdict = passed`.
- Product runner Result Population rows use aggregate metrics only in the current fixture path. Completed rows expose `metrics` such as Sharpe, drawdown, PnL, fees, funding, trade count, and win rate. They do not expose committed per-trade rows. Current rows do not expose fold/OOS window fields in this product runner path.
- Result population paths and metadata available to downstream adapters:
  - adapter Result Population path/hash;
  - direct Result Population path/hash;
  - runner adapter run id;
  - product pipeline run id;
  - bridge preparation run id;
  - execute approval path/hash;
  - denominator counts in vocabulary `completed`, `failed`, `invalid`, `blocked`, `pruned`;
  - noncanonical status.

## Product Bridge Facts Needed By Evaluation Adapters

- Product bridge prepare-only implementation lives in `tools/research_agents/formalizer_runner_bridge.py`.
- Product bridge package id: `WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B`.
- Product bridge mode: `product_bridge_prepare_only`.
- Product bridge output root: `scratch/WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B/outputs`.
- The prepared input paths in runner adapter `source_bindings` are under the bridge run directory and allow locating:
  - sibling `human_review_packet.json`;
  - sibling `denominator_ledger.json`;
  - sibling source formalizer output from `human_review_packet.product_bridge_preparation_metadata.source_formalizer_output_path`.
- Product bridge prepare-only review has `runner_artifact_paths = []`, `runner_invocation_metadata.runner_invoked = false`, `validation_status = prepared`, and all trials initially blocked because runner execution was not requested.
- For evaluation over product runner output, the adapter must construct a compatibility copy of the bridge review and denominator ledger that binds the product runner Result Population path, reconciled runner metrics, and updated denominator counts. This is product adapter glue only; it must not mutate source bridge or runner artifacts.

## Existing WFO/OOS Gate

- Module: `tools/oos_gate/evaluate.py`.
- Entry points:
  - `validate_oos_gate_artifact(payload)`;
  - `evaluate_candidate_review_gate(candidate_payload, gate_artifact)`.
- Required artifact schema: `oos_gate_contract.v1`.
- Allowed gate decisions: `pass`, `fail`, `blocked`, `advisory_only`.
- Canonical status must be `non_canonical`; `separately_crossed` is rejected by current validator.
- Required non-authority declaration flags are all true:
  - `not_candidate_approval`;
  - `not_promotion_authority`;
  - `not_readiness_authority`;
  - `not_ranking_authority`;
  - `not_recommendation_authority`;
  - `not_runtime_authority`;
  - `not_paper_live_authority`;
  - `not_result_population_write_authority`;
  - `not_candidate_lifecycle_write_authority`.
- Existing tests: `tests/test_oos_gate.py`.
- Withheld-statistics behavior: the validator currently requires finite `oos_metrics` values. Because current product runner output does not include real fold/OOS windows, the product adapter must not fabricate OOS metrics. It can only produce an advisory packet that marks real WFO/OOS statistics as withheld and uses the existing gate validator/evaluator over a valid blocked/advisory compatibility artifact where finite metrics are explicitly neutral placeholders and the packet preserves the withheld caveat separately.

## Existing Robustness Diagnostician

- Module: `tools/research_agents/robustness_diagnostician_agent.py`.
- Entry point: `RobustnessDiagnosticianAgent.run(...)`.
- Required inputs:
  - bridge review packet;
  - bridge Result Population artifact;
  - bridge denominator ledger;
  - operator robustness approval marker.
- Required approval scope: `noncanonical_scratch_robustness_only`.
- Existing tests: `tests/test_agent_robustness_diagnostician.py`.
- Outputs:
  - `robustness_diagnostics.json`;
  - `robustness_review_packet.json`.
- Caveats and withheld/missing behavior:
  - missing fold/OOS inputs become `oos_walkforward_status.status = missing_fold_inputs`;
  - missing per-trade rows become `per_trade_status.status = QUEUE_PER_TRADE_INSTRUMENTATION` with `fabricated_per_trade_data = false`;
  - funding stress is explicit as not applicable/missing/performed based on visible inputs.
- Contract constraint: the agent's current read allowlist and result-validation path checks expect legacy bridge-shaped paths under `scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/`. Direct product scratch paths are not accepted by the agent without changing core agent or permission contracts, which this package forbids. Decision: invoke the existing agent inside a temporary repo-shaped compatibility sandbox and write only derived advisory packet artifacts under this package's product scratch.

## Existing Candidate-Review Packet Agent

- Module: `tools/research_agents/candidate_review_packet_agent.py`.
- Entry point: `CandidateReviewPacketAgent.run(...)`.
- Required inputs:
  - formalizer research object;
  - optional draft Strategy Spec;
  - bridge review packet;
  - optional bridge Result Population artifact;
  - bridge denominator ledger;
  - robustness diagnostics;
  - robustness review packet;
  - operator candidate-review approval marker.
- Required approval scope: `noncanonical_scratch_candidate_review_only`.
- Existing tests: `tests/test_agent_candidate_review_packet.py`.
- Outputs:
  - `candidate_review_packet.json`;
  - `candidate_review_packet.md`.
- Caveats and withheld/missing behavior:
  - denominator rows and all status counts are preserved;
  - missing per-trade, fold/OOS, and funding-stress inputs remain visible in `missing_data_limitations` and `evidence_gaps`;
  - non-authority flags include `not candidate authority`, `not promotion authority`, `not ranking authority`, `not paper/live readiness`, and `human review required`.
- Contract constraint: the agent's current read allowlist expects legacy formalizer, bridge, and robustness scratch prefixes or its own package scratch. Direct product scratch paths are not accepted without core agent/permission changes. Decision: use the same temporary compatibility sandbox as the robustness invocation and copy resulting payloads into the product advisory packet.

## Candidate Surface Scaffold

- Module: `tools/lab_pipeline/gate_actions.py`.
- Entry point: `record_candidate_surface_decision(...)`.
- Allowed candidate-surface decisions exactly:
  - `hold_for_review`;
  - `needs_more_evidence`;
  - `do_not_escalate`.
- Forbidden decisions include candidate admission, crossing, promotion, paper/shadow/live start, and related runtime/scheduler/provider terms.
- Existing tests: `tests/test_lab_pipeline_gate_actions.py`.
- A GO-like result must route only to this scaffold. No candidate lifecycle, registry, crossing, promotion/readiness, canonical evidence, paper/live/runtime, scheduler, notification, provider/API, dependency/config/data-acquisition, or protected-path action is authorized.

## Deterministic / Volatile Fields For Reconciliation

- Runner adapter direct reconciliation is already recorded in `runner_adapter_result.json`.
- The WFO/OOS helper functions are pure over JSON payloads and deterministic.
- Robustness and candidate-review agents compute run ids and hashes from source payloads plus deterministic config timestamps/seeds.
- Temporary sandbox paths can affect source-path fields and hashes. Direct-agent reconciliation for this product adapter must therefore compare adapter-stage outputs against direct invocation over the same compatibility inputs and require byte-wise equality of the selected deterministic JSON payloads.
- No new normalization exists for these agent outputs. If byte-wise equality fails, the adapter must fail closed.

## Files That Must Remain Untouched

- Offline runner implementation: `tools/research_runner/**`.
- Bridge implementation: `tools/research_agents/formalizer_runner_bridge.py`.
- WFO/OOS core gate logic: `tools/oos_gate/**`.
- Robustness core agent logic: `tools/research_agents/robustness_diagnostician_agent.py`.
- Candidate-review core agent logic: `tools/research_agents/candidate_review_packet_agent.py`.
- Candidate-surface scaffold semantics: `tools/lab_pipeline/gate_actions.py` except read-only use unless a narrow test/import touch is required.
- Result Population validators, schemas, registry validators, and query layer.
- Canonical `research/result_populations/**`, Strategy Specs, Variant Manifests, Sweep Plans, candidate lifecycle/registry, crossing/promotion/readiness artifacts.
- Paper/shadow/live/runtime, OMS, risk, reconciliation, orders, exchange/broker, safe-mode/kill-switch, scheduler/autonomy, notifications, provider/API/credentials, dependency/config/data acquisition.
- `src/**`, `lib/**`, `configs/**`, `.claude/**`, `data/**`, generated build outputs.
