# Prepare / Execute Split Contract

## Definition: Bridge Preparation

Bridge preparation means the bridge-owned conversion of an accepted formalizer output and bridge-specific approval into validated scratch-only Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, and human review packet artifacts.

Preparation may:

- read the approved source formalizer output;
- read the product bridge-preparation approval marker;
- validate source path, content, hashes, schema, family, and non-authority;
- validate draft Strategy Spec;
- derive scratch Strategy Spec / Variant Manifest / Sweep Plan artifacts;
- run bridge-owned validators;
- produce denominator ledger and human review packet;
- write only approved scratch outputs;
- record audit/non-authority evidence.

Preparation must not:

- call `_invoke_runner`;
- call `run_offline_sweep`;
- request `RUN_NONCANONICAL_OFFLINE_SWEEP`;
- write canonical Result Populations;
- write Strategy Specs, Variant Manifests, or Sweep Plans outside package scratch;
- mutate candidate lifecycle, trial log, project status, schemas, validators, query layer, data, config, dependencies, runtime, paper/live, OMS, risk, reconciliation, scheduler, notifications, provider/API, credentials, or protected paths.

## Runner Boundary

The runner boundary begins at any of the following:

- `_invoke_runner`;
- `run_offline_sweep`;
- `RUN_NONCANONICAL_OFFLINE_SWEEP`;
- any creation of runner artifacts or Result Population-shaped outputs from runner execution.

Product bridge preparation must terminate before this boundary.

## Required Distinctions

### `legacy_bridge_run`

Current behavior. It must remain unchanged by default. It may invoke the runner when the legacy contract is approved and no blockers exist.

### `product_bridge_prepare_only`

New proposed behavior. It may produce bridge-preparation artifacts only. It must have no call path to runner execution and no permission to request runner execution.

### `future_runner_adapter_execution`

Not authorized here. A later authority surface would be required to consume validated product bridge-preparation artifacts and run a noncanonical offline runner path.

## How Runner Execution Remains Separately Gated

- Product approval marker must set `authorizes_runner_execution = false`.
- Product mode must reject any marker that authorizes runner execution.
- Product ToolContext must not include or request `RUN_NONCANONICAL_OFFLINE_SWEEP`.
- Product mode must expose no argument that flips preparation into execution.
- A future runner path must require a separate exact-content runner approval marker.

## Proof Product Mode Cannot Invoke Runner

Required future proof:

- static test or spy proving `_invoke_runner` is not called in product mode;
- ToolContext audit showing no `RUN_NONCANONICAL_OFFLINE_SWEEP` action requested;
- approval tests rejecting runner authorization;
- output tree inspection showing no `runner_artifacts` directory from product preparation;
- direct product-mode invocation with unblocked data still stops before runner boundary.

## Proof Legacy Behavior Remains Unchanged

Required future proof:

- direct legacy invocation before/after implementation;
- byte-for-byte comparison for deterministic outputs;
- same runner invocation count and targets in legacy mode;
- same ToolContext allowed/blocked audit behavior;
- same approval, source-prefix, output-root, validation, denominator, and review-packet behavior.

## Escalation Condition

If bridge preparation cannot be separated without altering legacy runner-coupled behavior, stop. Do not design monkeypatch, fake-blocker, suppression, or adapter-side workaround behavior.

## Verdict

`prepare_execute_split_verdict`: `separable_as_contract_proposal_requires_future_bridge_implementation_and_legacy_byte_regression`
