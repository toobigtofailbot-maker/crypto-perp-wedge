# Lab Productization Pipeline Runner Adapter

## Summary

`WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04` adds a narrow product runner adapter over bridge product prepare-only outputs. It consumes prepared Strategy Spec / Variant Manifest / Sweep Plan artifacts, requires a separate Karl execute approval, invokes the existing offline runner, writes only package-local scratch Result Population artifacts, and reconciles adapter output against a direct runner invocation on the same inputs.

## Scope

- Implementation: `tools/lab_pipeline/runner_adapter.py`
- Registry status: `tools/lab_pipeline/adapter_contract.py` reports `noncanonical_offline_runner_execution` as implemented only for package `WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04`.
- Tests: `tests/test_lab_pipeline_runner_adapter.py`

## Execute Approval

Runner execution uses `product_runner_execute_approval_v1`, not the bridge preparation approval and not the broad lab prereg approval. The marker binds Karl approval to:

- prepared Strategy Spec path/hash;
- prepared Variant Manifest path/hash;
- prepared Sweep Plan path/hash;
- bridge preparation run id;
- product pipeline run id;
- runner adapter stage identity;
- product output root;
- explicit runner-execution authorization;
- explicit false protected-authority flags.

Timestamp is required for audit syntax only. No wall-clock expiry is introduced.

## Runner Invocation

The adapter calls `tools.research_runner.run_offline_sweep.run_offline_sweep` directly. It does not copy runner logic, reinterpret metrics, alter backtester behavior, mutate runner schemas, or narrow the result population.

The adapter audits `noncanonical_offline_sweep_run` through the existing ToolContext policy under package-local output root:

```text
scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/outputs
```

## Output

Outputs are noncanonical and product-scratch-local:

- adapter Result Population under `runner_artifacts/adapter/`;
- direct reconciliation Result Population under `runner_artifacts/direct/`;
- `runner_adapter_result.json` with source bindings, approval binding, denominator counts, reconciliation hashes, and non-authority assertions.

The adapter rejects output roots outside its package scratch output root.

## Reconciliation

The adapter runs the existing offline runner twice on the same prepared inputs:

- adapter invocation;
- direct invocation.

It compares raw file hashes first. If raw hashes differ, it uses only the existing read-only replay normalization contract in `tools/research_replay/normalization.py`. A mismatch fails closed.

## Denominator

All runner rows remain in the Result Population. Adapter status counts use:

- completed
- failed
- invalid
- blocked
- pruned

No winner-only selection, ranking authority, readiness claim, promotion claim, gate action, WFO/OOS run, robustness run, candidate-review run, canonical write, or candidate lifecycle write is added.

## Non-Authority

This adapter creates no canonical evidence and no candidate lifecycle state. It does not contact paper/live/runtime, OMS, risk, reconciliation, broker/exchange/order paths, scheduler/autonomy, notifications, provider/API/credentials, dependency/config/data-acquisition surfaces, `src/**`, `lib/**`, `configs/**`, or protected runtime paths.
