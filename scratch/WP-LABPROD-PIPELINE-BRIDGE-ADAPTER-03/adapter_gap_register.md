# Adapter Gap Register

## Still Gap-Registered

| Stage | Reason |
|---|---|
| `bridge_spec_variant_sweep_preparation` | Existing bridge ToolContext, source-prefix, output-root, approval, and runner contracts conflict with this package's safe adapter requirements. |
| `noncanonical_offline_runner_execution` | No safe bridge-produced Strategy Spec / Variant Manifest / Sweep Plan input set exists, and runner execution is forbidden in this package. |
| `wfo_oos_gate_review` | No safe upstream runner or OOS gate artifact exists in this package. |
| `robustness_diagnostics` | Requires bridge/runner evidence and separate approval not available here. |
| `candidate_review_packet_preparation` | Requires complete bridge, runner, WFO/OOS, and robustness inputs not available here. |

## Adapter Status

The adapter run status must remain `complete_with_gaps` for approved adapter
flows because downstream stages remain gap-registered.
