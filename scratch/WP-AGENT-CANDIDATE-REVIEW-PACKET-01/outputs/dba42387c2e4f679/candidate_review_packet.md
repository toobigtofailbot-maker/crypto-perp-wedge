# Candidate Review Packet

- Run ID: dba42387c2e4f679
- Posture: scratch-only, advisory, human-review-required
- Strongest allowed summary: candidate may be worth human review for further evidence

## Non-Authority Flags
- not canonical
- not evidence
- not candidate authority
- not promotion authority
- not ranking authority
- not paper/live readiness
- not a trading signal
- human review required

## Sources
- Formalizer: scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/3a32f0bf02d2/formalized_idea.json (sha256:e19cd2a83c396fa16c7e8e88c2240dcc0e115ac219f70e00ccabca634d89ed60)
- Bridge packet: scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/fd63eb89897d9dc5/human_review_packet.json (sha256:bc222c21a89863d57d0139422c66389339276a74dc5688fb2a7e0832568496db)
- Denominator ledger: scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/fd63eb89897d9dc5/denominator_ledger.json (sha256:84f8199aea9b78753c8a570c26696991e0f9cc4a078cb358749aaba80059d540)
- Robustness diagnostics: scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/9309de71e35fc40f/robustness_diagnostics.json (sha256:3b47f445b447ccaa97f35dffe09d4026396953f73173cec962f093f15d8b09c4)
- Robustness packet: scratch/WP-AGENT-ROBUSTNESS-DIAGNOSTICIAN-01/outputs/9309de71e35fc40f/robustness_review_packet.json (sha256:857154c5a25a33914f96e34684b3d85882d3efcb6ea6db6cb6a5cecdd4cc6762)

## Denominator
- completed: 8
- failed: 0
- invalid: 0
- pruned: 0
- blocked: 0
- All source rows preserved: True

## Evidence Summary
- Strategy family: strat-spec-0003-sma-stddev-mean-reversion
- Idea summary: BTCUSDT 15m SMA and stddev mean revert because temporary liquidity pressure dislocates returns; center_lookback_bars from 50 to 100; vol_lookback_bars from 30 to 50; trend_lookback_bars from 100 to 200.
- Funding mode: {'default_off': True, 'effective': 'off', 'global_mode_mutated': False, 'requested': 'off'}
- Data warnings: ['none']
- Data blockers: ['none']

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

## Gaps And Follow-Ups
- Evidence gaps:
  - needs real trade rows for per-trade diagnostics
  - needs fold/OOS inputs for walk-forward diagnostics
  - needs separately authorized funding-on test before funding stress
- Blockers:
  - none
- Recommended human review questions:
  - Do the source packets preserve enough lineage for a future lifecycle review?
  - Are denominator failures, invalid rows, pruned rows, and blocked rows acceptable to investigate further?
  - Which missing diagnostics must be collected before any future canonical evidence package?
  - Does the data availability/funding posture require a separate approved package?
- Recommended next evidence steps:
  - collect real trade rows before per-trade diagnostics
  - collect fold/OOS inputs before walk-forward robustness claims
  - run funding-on evidence only under a separate approved package
  - prepare candidate lifecycle review only through a later human-gated path
