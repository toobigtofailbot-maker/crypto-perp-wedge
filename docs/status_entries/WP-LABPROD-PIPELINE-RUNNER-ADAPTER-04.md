# WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04 Status

## Decision

`READY_FOR_REVIEW`

## Summary

Adds a product runner adapter over bridge product prepare-only outputs. The adapter requires a separate Karl execute approval, invokes the existing offline runner, writes noncanonical package-local scratch Result Population artifacts, reconciles adapter output against a direct runner invocation, and preserves the full denominator status vocabulary.

## Changed Files

- `tools/lab_pipeline/runner_adapter.py`
- `tools/lab_pipeline/adapter_contract.py`
- `tests/test_lab_pipeline_runner_adapter.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_RUNNER_ADAPTER.md`
- `docs/status_entries/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04.md`
- `scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/*`

## Execute Approval

Runner execution requires `product_runner_execute_approval_v1`, approved by Karl, bound to the prepared Strategy Spec / Variant Manifest / Sweep Plan path+hash set, bridge preparation run id, product pipeline run id, runner adapter stage identity, and product output root.

Bridge preparation approval and broad pipeline prereg approval fail closed as runner execute approvals.

## Runner / Reconciliation

The adapter invokes `tools.research_runner.run_offline_sweep.run_offline_sweep`. It does not reimplement runner behavior. It writes adapter and direct runner outputs under package scratch and requires raw or repo-normalized reconciliation to pass.

## Boundary

No bridge implementation, runner implementation, backtester logic, schemas, validators, query layer, canonical Result Population, candidate lifecycle record, crossing, promotion/readiness, WFO/OOS, robustness, candidate review, paper/live/runtime, OMS, risk, reconciliation, scheduler, notification, provider/API, dependency/config/data, `src/`, `lib/`, `configs/`, or protected path is changed.

## Validation

Initial focused validation:

- `.\.venv\Scripts\python.exe -m py_compile tools\lab_pipeline\runner_adapter.py tools\lab_pipeline\adapter_contract.py`
- `.\.venv\Scripts\python.exe -m pytest tests/test_lab_pipeline_runner_adapter.py -q` -> 29 passed
- `.\.venv\Scripts\python.exe -m pytest tests/test_agent_formalizer_runner_bridge.py tests/test_lab_pipeline_bridge_adapter.py -q` -> 71 passed
- `.\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q` -> 101 passed, 2 warnings
- PowerShell-expanded `tests/test_lab_pipeline*.py` -> 86 passed

Full validation details are recorded in `scratch/WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04/validation_summary.txt`.
