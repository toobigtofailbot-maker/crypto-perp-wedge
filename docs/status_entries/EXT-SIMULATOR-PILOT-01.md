# EXT-SIMULATOR-PILOT-01 - Isolated External Simulator Pilot

## Branch / PR

- Branch: `ext/simulator-pilot-01`
- PR: #513

## Package Class

External-repo adoption pilot / simulator fidelity / non-canonical comparator.

## Precondition

- `EXT-WORKFLOW-HYPEROPT-PILOT-01` is merged on refreshed `main`.
- Verification evidence: refreshed `main` includes merge commit `48891a2` for
  PR #512 and package commit `be84cbb`.

## Scope Summary

This package adds a narrow NautilusTrader simulator-candidate feasibility
harness for the committed `RP-2592` fixture. The pilot reads the canonical RP,
Strategy Spec, Variant Manifest, Sweep Plan, and D4A data-slice metadata
read-only, installs NautilusTrader only in an isolated temp venv outside repo
dependency files, probes whether its offline backtest API can load, source-reads
local Nautilus backtest config concepts, and writes non-canonical scratch
reports only.

NautilusTrader installed in isolation and its backtest config import became
available during final report generation, but this package did not produce a
safe repo-specific Nautilus offline backtest mapping or any simulator metrics.
The pilot therefore reports `BLOCKED`; no reconciliation parity or determinism
evidence was produced.

## Changed Files

- `tools/external_pilots/simulator_pilot.py`
- `tests/test_external_simulator_pilot.py`
- `docs/status_entries/EXT-SIMULATOR-PILOT-01.md`
- `scratch/EXT-SIMULATOR-PILOT-01/simulator_pilot_report.json`
- `scratch/EXT-SIMULATOR-PILOT-01/simulator_pilot_report.md`
- `scratch/EXT-SIMULATOR-PILOT-01/simulator_pilot_report.sha256`

## Fixture Used

- Result Population: `RP-2592`
- Path: `research/result_populations/RP-2592.result_population.json`
- Fixture checksum:
  `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Rows used: `8`
- Selected variants: `8`
- Data slice:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Normalized local data path:
  `data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`
- Normalized local data exists: `true`
- Fee assumption: `taker_entry_taker_exit`
- Slippage assumption: `fixed_bps`
- Fill assumption: `complete`
- Bar timing assumption: `next_open_close_mark`
- Liquidation assumption: `zero_equity`
- Sizing assumption: `dynamic_equity_target_leverage` at `target_leverage=1.0`
  per the recorded sweep assumption text.

## Simulator Probe

- Candidate: NautilusTrader.
- Isolated environment used: `YES`.
- Install command: `python -m pip install nautilus_trader`.
- Installed version: `1.228.0`.
- Python used for isolated probe: `3.14.3`.
- Platform class: `Windows`.
- Repo dependency files changed: `NO`.
- Nautilus backtest API importable: `YES`.
- Import error: `null`.
- Nautilus offline backtest executed: `NO`.
- Jesse installed/executed: `NO`.
- Jesse concept source used: `NO`, deferred after Nautilus execution was blocked.

## Source-Extraction Finding

Local NautilusTrader source inspection of
`external:nautilus_trader/backtest/config.py` was performed without importing
exchange adapters. The inspected backtest config source exposes relevant
concept knobs:

- `bar_execution`
- `bar_adaptive_high_low_ordering`
- `fill_model`
- `fee_model`
- `margin_model`
- `default_leverage`
- `liquidation_enabled`
- `liquidation_trigger_ratio`
- `liquidity_consumption`
- `queue_position`

This source extraction is advisory only and creates no repo simulator,
canonical-runner, runtime, or policy authority.

## Reconciliation Result

- Variants attempted in NautilusTrader: `0`.
- Variants expressible in NautilusTrader: `0`.
- RP variants available: `8`.
- Trade count comparison: `not_performed`.
- Final equity / return comparison: `not_performed`.
- Cost model comparison: source-inspection only; no fee parity established.
- Fill model comparison: source-inspection only; no next-open parity established.
- Margin/liquidation comparison: source-inspection only; no zero-equity parity
  established.
- Funding comparison: not performed; `RP-2592` funding metrics are `0.0` for
  all rows and no Nautilus funding cashflow mapping executed.
- Unexplained differences: simulator metrics absent because Nautilus backtest
  did not execute.
- Integration burden:
  `unmeasured_until_safe_offline_backtest_mapping_is_implemented`.

## Determinism

- Repeated Nautilus runs: `NO`.
- Byte-identical: `NO`.
- Normalized-identical: `NO`.
- Checksum: `null`.
- Result: `not_established`.
- Reason: NautilusTrader offline backtest did not execute.

## Generated Artifact

- Report JSON: `scratch/EXT-SIMULATOR-PILOT-01/simulator_pilot_report.json`
- Report Markdown: `scratch/EXT-SIMULATOR-PILOT-01/simulator_pilot_report.md`
- Report checksum:
  `sha256:6f3eff7bfb26ca57c792813a56e4847b3011b3161b371836be300c8f15c3b4e0`

## Validation Summary

- `.\.venv\Scripts\python.exe -m pytest tests/test_external_simulator_pilot.py -q`:
  `PASS`, 7 passed.
- Isolated pilot command:
  `python -m tools.external_pilots.simulator_pilot --isolated-environment-used --isolated-install-command "python -m pip install nautilus_trader"`:
  `PASS`; regenerated checksum
  `sha256:6f3eff7bfb26ca57c792813a56e4847b3011b3161b371836be300c8f15c3b4e0`.
- `.\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  `PASS`, 64 passed in 495.01 seconds.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; diff checks, forbidden-scope check, result-population validator,
  query view listing, 4 pytest shards over 75 test files, and all discovered
  integrity views passed/clean.

## Boundary Summary

- External dependency added to repo: `NO`.
- Exchange/sandbox/live connection used: `NO`.
- Credentials used: `NO`.
- Private/order/account methods used: `NO`.
- Canonical Result Population write: `NO`.
- Strategy Spec mutation: `NO`.
- Variant Manifest mutation: `NO`.
- Sweep Plan mutation: `NO`.
- Runner/backtester changed: `NO`.
- OMS/risk/reconciliation changed: `NO`.
- Runtime/paper/live touched: `NO`.
- Screen-gate authority created: `NO`.
- Promotion/readiness authority created: `NO`.
- Candidate-evidence authority created: `NO`.
- Protected paths touched: `NO`.
- Machine-local absolute paths in committed outputs: `NO`.

## Recommendation

`BLOCKED`.

Rationale: NautilusTrader installed in isolation and source inspection found
relevant simulator concepts, but no offline backtest produced simulator metrics
in this package. Offline-only execution, simulator reconciliation, and
determinism are therefore not established.

Broader adoption taxonomy: `blocked`.

Next gated WP suggestion: narrow environment-compatibility and minimal
Nautilus offline backtest spike on a machine where the optional binary modules
are allowed to load; no repo dependency mutation.
