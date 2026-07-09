# Product Pipeline Advisory Review Packet

- Gates adapter run ID: LGATE-ad8b6d62f772e9d8
- Runner adapter run ID: LRUN-cbbdb839a2a7badf
- Posture: advisory_only_noncanonical_product_scratch
- Candidate-surface status: needs_more_evidence

## Denominator
- completed: 8
- failed: 0
- invalid: 0
- blocked: 0
- pruned: 0

## WFO/OOS
- Status: blocked
- Withheld: withheld_missing_walkforward_oos_inputs

## Robustness
- Completed: seeded_variant_metric_bootstrap
- Completed: metric_confidence_intervals
- Completed: parameter_sensitivity
- Completed: denominator_integrity
- Completed: source_lineage_hash_preservation
- Completed: funding_mode_visibility
- Completed: data_availability_propagation
- Skipped diagnostics:
  - {'diagnostic': 'oos_walkforward_status', 'reason': 'missing_fold_inputs'}
  - {'diagnostic': 'per_trade_status', 'reason': 'QUEUE_PER_TRADE_INSTRUMENTATION'}
  - {'diagnostic': 'funding_stress_status', 'reason': 'not_applicable_funding_mode_off'}

## Candidate Review
- Status: completed
- Non-promotion posture: true

## Non-Authority
- canonical_evidence_written: false
- candidate_lifecycle_written: false
- candidate_registry_written: false
- candidate_admission: false
- crossing: false
- promotion_or_readiness: false
- paper_live_runtime_contact: false
- scheduler_autonomous_dispatch: false
- notification_firing: false
- provider_api_credential_use: false
- dependency_config_data_acquisition: false
- protected_path_touch: false
