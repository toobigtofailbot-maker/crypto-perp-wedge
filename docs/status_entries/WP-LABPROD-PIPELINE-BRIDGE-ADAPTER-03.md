# WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03

## Status

Outcome B. The bridge adapter is precisely blocked by current repo truth; no
unsafe bridge invocation path was merged.

## Changed Files

- `tools/lab_pipeline/adapter_contract.py`
- `tests/test_lab_pipeline_bridge_adapter.py`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_BRIDGE_ADAPTER.md`
- `docs/status_entries/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03.md`
- `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/`

## Repo-Truth Discovery

The existing formalizer-runner bridge requires its own ToolContext WP allowlist,
formalizer source-prefix contract, output-root contract, and legacy operator
approval marker. Those constraints conflict with this package's required
package-local scratch output and Karl-signed exact-content bridge approval
marker.

## Boundary

No `src/`, `lib/`, `configs/`, `.claude/`, `data/`, dependency, provider/API,
credential, scheduler/autonomy, notification, runtime, paper/live, OMS, risk,
reconciliation, broker/exchange, canonical Result Population, candidate
lifecycle, Strategy Spec, Variant Manifest, Sweep Plan, WFO/OOS, robustness, or
candidate-review path was changed.

## Next Package

Before `WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04`, a narrower bridge-contract
expansion decision is required if the lab pipeline should invoke the existing
bridge with package-local scratch outputs and a no-runner bridge-preparation
mode.
