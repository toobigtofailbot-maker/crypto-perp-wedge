# WP-AGENT-ADAPTER-TAKERFLOW-FAMILY-01 Repo-Truth Discovery

## Decision

BLOCKED before adapter implementation.

## Facts

- PR #556 is merged into local main: f7d39c6 / WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01.
- Taker-flow feature availability entries exist in research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json.
- Available taker-flow feature names found: taker_buy_sell_ratio, taker_buy_volume, taker_sell_volume.
- tools/research_runner/spec_signal_compiler.py allows taker_buy_sell_ratio, taker_buy_volume, and taker_sell_volume as data-derived data_ref fields.
- tools/research_runner/run_offline_sweep.py currently loads OHLCV CSV input and then narrows the frame to open, high, low, close, volume.
- The committed data/processed tree in this worktree contains no full-history taker-flow dataset; only .gitkeep is present.
- Taker-flow archive reconstruction support exists in tools/data_ingestion/takerflow_archive_recon.py, but using it to create/promote a runner-consumable dataset or altering runner data loading is outside this WP.
- Funding mode must remain explicit/default-off; no funding mode change is authorized.

## Inferences

- Strategy Spec grammar can reference taker-flow fields via existing data_ref support.
- Current real offline runner smoke cannot honestly consume taker-flow fields because the runner input loader strips all non-OHLCV columns before compilation.
- A taker-flow formalizer/bridge adapter that pretends to run through the existing runner would either silently substitute price/OHLCV proxy data or require runner/data-source changes; both are forbidden by the package.

## Prior conclusion check

- No committed equivalent taker-flow canonical RP/REP or GO/NO-GO strategy conclusion was found by bounded search.
- Taker-flow data infrastructure/status artifacts exist; they are not edge conclusions.

## Adapter pattern

- Formalizer currently supports hard-coded SMA/stddev and Donchian family detection/body generation.
- Bridge currently dispatches SMA/stddev and Donchian, creates scratch VM/Sweep inputs, then invokes run_offline_sweep when blockers are absent.
- Bridge already has a taker-flow availability blocker in the non-taker adapter path because OHLCV-only runner fixtures are insufficient.

## Downstream limitation

- Robustness diagnostician currently requires bridge-derived input paths under scratch/WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01/outputs/, so adapter-specific bridge prefixes such as Donchian/taker-flow are not family-generic.
- Candidate-review packet currently hard-codes the strategy family summary to strat-spec-0003-sma-stddev-mean-reversion, so non-SMA bridge/robustness packets lose family identity even when required fields exist.

## Repo-truth adjustment

The package is blocked before implementation because safe implementation would require either:
1. modifying runner/data loading to preserve taker-flow fields, or
2. creating/promoting a taker-flow dataset/input source for runner use.

Both are outside the package's authorized boundaries.
