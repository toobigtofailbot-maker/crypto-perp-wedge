# Repo Truth Discovery

Package: `WP-RUNNER-PREVIOUS-BAR-HIGHLOW-REF-01`

## Base

- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\runner-previous-bar-highlow-ref-01`
- Branch: `runner/previous-bar-highlow-ref-01`
- Base commit: `c2dac11729ffdf9fc9f833ff39e64ea67eb8bed5`
- Base source: `origin/main`
- PR #606 merged: yes; base commit is merge commit `c2dac11`.

## Required Evidence Read

- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/operator_review_packet.md`
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/denominator_preservation_audit.json`
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/strategy_reading_summary.json`
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/validation_summary.txt`
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`

## Facts

- `LAB-RT-HYP-002R` was blocked before execution.
- Blocker source: unsupported `previous_bar_high_low` breakout reference in the
  current closed runner grammar.
- Frozen HYP-002R requires current breakout comparison against the immediately
  previous completed bar high/low.
- The previous batch preserved denominator: 32 frozen rows, 24 executed
  successful rows, 8 HYP-002R blocked rows, 0 dropped rows.
- The signed frozen set was not modified by this package.

## Surfaces Inspected

- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/registry/validate_strategy_specs.py`
- `tools/registry/validate_variant_sweep_artifacts.py`
- `tools/registry/validate_result_populations.py`
- `tools/registry/validate_candidate_registry.py`
- `research/schemas/strategy_spec.schema.json`
- `research/schemas/variant_manifest.schema.json`
- `research/schemas/sweep_plan.schema.json`
- `research/schemas/result_population.schema.json`
- `tests/test_spec_signal_compiler.py`
- `tests/test_validate_strategy_specs.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/`

## Decision

Implement the unblocker as a closed Strategy Spec online OHLCV primitive named
`previous_bar_refs`, not as a generic expression, formula, arbitrary lag, or
dynamic evaluation feature.
