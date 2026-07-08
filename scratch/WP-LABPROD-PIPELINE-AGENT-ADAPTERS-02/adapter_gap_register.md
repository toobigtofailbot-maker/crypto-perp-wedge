# Adapter Gap Register

## Current Gap-Registered Stages

| Stage | Reason |
|---|---|
| `bridge_spec_variant_sweep_preparation` | Existing bridge requires its own operator approval marker and package-specific scratch/source-prefix contract. |
| `noncanonical_offline_runner_execution` | No safe bridge-produced validated Strategy Spec / Variant Manifest / Sweep Plan input set exists without bridge approval. |
| `wfo_oos_gate_review` | No safe upstream walk-forward/OOS gate artifact exists in the adapter packet. |
| `robustness_diagnostics` | Requires bridge outputs and a separate robustness approval marker. |
| `candidate_review_packet_preparation` | Requires complete bridge and robustness packets plus its own candidate-review approval marker. |

## Fixture Note

The committed fixture packet is `awaiting_prereg_approval`, so its JSON gap
register has zero gaps because no adapter stage was allowed to run far enough to
classify downstream gaps. The gap list above is the package-level adapter
registry truth for approved adapter runs.
