# WP-RUNNER-DATA-PATH-NONOHLCV-01 Repo-Truth Discovery

## Commands / Scope

- Preflight: `git fetch origin`; `git switch main`; `git pull --ff-only origin main`; `git log --oneline -n 20`.
- Local `main` includes merge commit `2cf40a0` for PR #558 / `WP-RESEARCH-PRICEONLY-SYNTHESIS-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\runner-data-path-nonohlcv-01`.
- Mandatory broad search was run over `docs`, `tools`, `lib`, `tests`, `research`, and `scratch` for runner, OHLCV, data_ref, taker-flow, funding, availability, and RP identifiers.

## Exact Data Path

- Offline runner entry point: `tools/research_runner/run_offline_sweep.py::run_offline_sweep`.
- Parent artifact validation: `tools/research_runner/run_offline_sweep.py::_validate_parent_inputs`.
- Canonical input loader: `tools/research_runner/run_offline_sweep.py::_load_ohlcv_input`.
- 15m wrapper: `tools/research_runner/run_offline_sweep.py::_load_15m_ohlcv_input`.
- 4h wrapper: `tools/research_runner/run_offline_sweep.py::_load_4h_ohlcv_input`.
- Signal compiler call: `tools/research_runner/run_offline_sweep.py::_run_canonical_15m_backtest`.
- Backtester input contract: `lib/backtest.py::run_backtest` requires `open`, `high`, `low`, `close`, `volume` in the supplied OHLCV frame and `funding_rate` in the funding frame.

## OHLCV Strip Point

- Previous strip point: `tools/research_runner/run_offline_sweep.py::_load_ohlcv_input` assigned `frame = frame[["open", "high", "low", "close", "volume"]].astype(float)` after timestamp selection.
- That discarded all extra CSV columns before `compile_signal(...)`.

## Current Required OHLCV Contract

- Required OHLCV columns remain: `open`, `high`, `low`, `close`, `volume`.
- Timestamp source remains one of `timestamp`, `open_time`, or `open_time_ms`, with conflict checks.
- Index must be UTC, monotonic after sort, no duplicates, minimum row count, and exactly spaced by requested timeframe.

## Compiler / data_ref Truth

- Compiler: `tools/research_runner/spec_signal_compiler.py`.
- Allowed OHLCV fields: `open`, `high`, `low`, `close`, `volume`.
- Allowed data-derived fields include `funding_rate`, `funding_mark_price`, `mark_price`, `index_price`, `premium_index`, `open_interest`, `open_interest_value`, long/short ratios, and taker-flow fields.
- Allowed timestamp-derived fields include `hour_of_day_utc`, `day_of_week_utc`, `is_weekend_utc`.
- `_resolve_data_ref(...)` already compiles non-OHLCV data refs when the field is allowed and present in the supplied frame.
- Existing compiler tests prove allowed data-derived fields compile, missing fields fail closed, unknown fields fail closed, future mutation does not alter prior bars, and nulls are preserved without fill/interpolation.

## Availability Labels

- Catalog: `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`.
- Taker-flow fields have both recent-only REST labels and conditional `FULL_HISTORY_PUBLIC_ARCHIVE` labels through `PUBLIC_TRADE_ARCHIVE_DERIVATION`.
- Open-interest and long/short ratio REST fields are recent-only or snapshot-only unless separate historical vendor/captured provenance exists.
- Result-population schema already supports optional identity-bearing `data_availability_claim`.
- Validator: `tools/registry/validate_result_populations.py::_validate_data_availability_claim` binds claim feature sources to non-OHLCV Strategy Spec `data_ref` and `host_data_refs`.

## Taker-Flow Source / Materialization Truth

- Taker-flow reconstruction tool: `tools/data_ingestion/takerflow_archive_recon.py`.
- It is offline, local-file only, accepts CSV/ZIP trade or aggTrade archives, and emits lineage with `FULL_HISTORY_PUBLIC_ARCHIVE` class when source archives cover the window.
- Tests: `tests/test_takerflow_archive_recon.py`.
- Repo/worktree committed fixtures include only small hand-calculation files under `tests/fixtures/takerflow_archive_recon/`.
- Isolated worktree has no full-history taker-flow trade or aggTrade archive files.
- Root checkout has local ignored OHLCV/funding/mark/index/premium files, but no inspected full-history taker-flow archive source files.

## Funding Source Truth

- Funding availability label supports conditional full-history public archive where aligned funding records cover the claimed evidence window.
- Root checkout has ignored local funding parquet files under `data/processed/`.
- The isolated worktree contains only `.gitkeep` under `data/processed`.
- This WP did not create a runner-consumable full-history funding materialized CSV because the authorized package objective centers first on declared-column preservation and the isolated worktree lacks promoted source material.

## Byte / Behavior Regression Candidates

- Canonical OHLCV-only RPs present: `research/result_populations/RP-2592.result_population.json`, `RP-3731.result_population.json`, `RP-7134.result_population.json`.
- Discovery found historical runner command examples in docs for canonical 15m/4h dry runs, but no repo-native committed byte-replay command for these exact three RPs that guarantees byte-identical reproduction from current local ignored data.
- Fallback regression used: targeted runner/compiler tests, unchanged default `_input_scope()`, existing result-population validator, and no mutation of canonical result populations.

## Repo-Truth Adjustments

- Compiler support already existed; runner data loading was the blocking layer.
- The safe implementation is runner-only plus tests. No `lib/backtest.py`, compiler operator semantics, schemas, validators, canonical artifacts, or runtime paths are changed.
- Full-history taker-flow materialization is blocked by absent full-history local archive inputs in the isolated worktree.
