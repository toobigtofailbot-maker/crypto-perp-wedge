# WP-RESEARCH-EDGE-SMA-FAMILY-01 Repo-Truth Discovery

## Facts

- The current idea formalizer accepts BTCUSDT ideas on locked timeframes and has one draft adapter: a scratch copy of `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`.
- The current bridge accepts only BTCUSDT 15m formalizer outputs containing `sma` and `stddev`, requires the draft to declare the `STRAT-SPEC-0003 capability family`, and copies `VM-0003` and `SWEEP-PLAN-0003` semantics.
- The formalizer does not bind idea-specific z-score thresholds, exit thresholds, volatility stops, holding limits, or session limits into the draft. Its supported draft retains fixed +/-1.5 z-score entries, SMA-centerline exits, no stop distance, no max holding period, one trend gate, and an 8-bar entry throttle.
- `VM-0003` is the complete 2 x 2 x 2 grid over center lookback `{50,100}`, volatility lookback `{30,50}`, and trend lookback `{100,200}`. `SWEEP-PLAN-0003` selects all eight variants.
- That exact Strategy Spec / Variant Manifest / Sweep Plan family has already been executed canonically over the BTCUSDT 15m D4A slice as `RP-7134`, preserving denominator 8/8. The frozen screen verdict is `NO-GO`.
- All `RP-7134` rows completed, but returns range from about -98.60% to -99.77%, Sharpe values are all negative, and drawdowns range from about 98.66% to 99.79%.
- The earlier raw SMA-band family is represented by `STRAT-SPEC-0002` / `RP-7520`; it also records no evidence-level edge. A raw SMA crossover pivot exists as design work and must not be rerun here.
- The committed D4A data identity is `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`. The bridge itself uses a repo-local 15m fixture path rather than the D4A canonical real-data path.
- Bridge funding mode defaults to explicit `off`. Funding-on blocks because the current bridge/runner contract has no explicit funding input.
- The robustness diagnostician supports completed-row aggregate seeded bootstrap intervals, aggregate parameter sensitivity, denominator integrity, lineage/hash preservation, and warning propagation. Real per-trade, MFE/MAE, fold/OOS, and funding-stress diagnostics are unavailable from the bridge output.
- The candidate-review packet agent can summarize valid formalizer, bridge, and robustness packets after a separate scoped operator marker. It cannot operate without bridge and robustness artifacts.

## Inference

The package hypothesis is economically consistent with the broad SMA/stddev family, but it is not a fresh executable hypothesis under the current agent adapter. Running the bridge would reproduce the already-concluded `STRAT-SPEC-0003` body and eight parameter assignments while changing only scratch IDs, lineage, and fixture execution context.

## Decision

Run the bounded formalizer once to preserve the requested machine-path evidence, then stop before bridge execution. Do not relabel a duplicate of the concluded `RP-7134` hypothesis as fresh edge discovery, and do not add the adapter or primitives forbidden by this package.

## Repo-Truth Adjustment

The pre-registered wording is narrowed to the adapter-supported fixed shape for capability assessment only: BTCUSDT 15m, both-direction +/-1.5 z-score entry, SMA-centerline exit, shared SMA trend gate, fixed 8-bar entry throttle, and the existing three-lookback grid. Volatility-scaled stop, configurable exit threshold, holding limit, and session conditions are unsupported by this adapter and therefore were not claimed or run.

## Open Question / Future Option

A genuinely fresh SMA/stddev attempt requires a separately approved preregistration and adapter/bridge path whose semantic degrees of freedom differ from `STRAT-SPEC-0003`. That work is outside this package.
