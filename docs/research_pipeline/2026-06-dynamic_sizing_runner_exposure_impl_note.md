# Dynamic Sizing Runner Exposure Implementation Note

## Status / authority boundary

This package exposes dynamic sizing to the offline runner for build-test dry
runs only. It does not write a canonical result population, mutate any RP, add
schema fields, register candidates, rank variants, mark readiness, promote
strategies, or authorize paper/live/runtime behavior.

## Source implementation

Source implementation:

- `lib/backtest.py` from `WP-REALISM-SIZING-02b`
- `docs/research_pipeline/2026-06-dynamic_equity_sizing_impl_note.md`
- `docs/status_entries/WP-REALISM-SIZING-02b.md`

`WP-REALISM-SIZING-02b` added the opt-in backtest-core
`dynamic_equity_target_leverage` mode and preserved `fixed_order_size` as the
default. This package does not edit `lib/backtest.py` or `lib/evaluation.py`.

## Runner controls

The offline runner now accepts:

```text
--sizing-mode fixed_order_size
--sizing-mode dynamic_equity_target_leverage
--target-leverage 1.0
```

The Python API mirrors the CLI with `sizing_mode` and `target_leverage`
arguments to `run_offline_sweep()`.

Closed sizing modes:

- `fixed_order_size`
- `dynamic_equity_target_leverage`

Unknown sizing modes fail closed through the API and CLI.

## Default preservation

`fixed_order_size` remains the default sizing mode. If no `--sizing-mode` is
provided, the runner continues resolving a fixed `order_size` from target
leverage, initial equity, and the first in-sample open price, then passes that
fixed quantity to `run_backtest()`.

In both fixed and dynamic modes, the runner passes the resolved `order_size`
argument for compatibility with the backtest-core signature. Dynamic mode is
activated only by passing `sizing_mode="dynamic_equity_target_leverage"` to the
backtest core.

## Sizing provenance in existing fields

No schema fields are added. Sizing provenance is recorded in the existing
identity-scoped field:

```text
backtest_assumption_summary.order_size_assumption
```

Recorded facts include:

- `sizing_mode`
- `sizing_model`
- `target_leverage`
- `initial_equity`
- fixed-mode first-open reference price basis and resolved `order_size`
- dynamic-mode realized-equity basis
- dynamic-mode next-bar-open entry reference basis
- opt-in requirement for dynamic mode
- current lack of structured sizing schema fields

## Dry-run evidence

The full local 15m parquet exists at:

```text
C:\GitHub\crypto-perp-wedge\data\processed\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet
```

A scratch full-slice CSV was created outside the repo at:

```text
C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02c\btc_usdt_15m_full_slice_scratch.csv
```

The full-slice dry-run did not complete within a 20-minute command timeout, so
the package fallback used a documented real-data sub-window from the same local
offline parquet:

```text
C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02c\btc_usdt_15m_2024H1_subwindow_scratch.csv
```

Sub-window basis:

- source: local offline BTCUSDT 15m parquet listed above
- rows: 17,472
- start: `2024-01-01T00:00:00Z`
- end: `2024-06-30T23:45:00Z`
- output mode: dry-run / no write
- result-population output path: `null`
- scratch result id: `RP-4217`
- committed denominator: 10
- outcome counts: 10 successful / 0 failed / 0 errored / 0 invalid / 0
  excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted

Per-variant dynamic 1x sub-window evidence:

| Variant | Return pct | Drawdown | Zero-equity style terminal |
|---|---:|---:|---|
| VAR-000001 | -0.659812 | 0.665553 | false |
| VAR-000002 | -0.491642 | 0.502152 | false |
| VAR-000003 | -0.201249 | 0.247574 | false |
| VAR-000004 | -0.046472 | 0.200277 | false |
| VAR-000005 | 0.140960 | 0.172773 | false |
| VAR-000006 | -0.619496 | 0.632288 | false |
| VAR-000007 | -0.557173 | 0.583482 | false |
| VAR-000008 | -0.480094 | 0.494613 | false |
| VAR-000009 | -0.266203 | 0.329177 | false |
| VAR-000010 | -0.171329 | 0.266969 | false |

Dynamic payoff check:

```text
0 of 10 variants hit return_pct=-1.0 or drawdown=1.0.
```

Dynamic 1x sizing no longer reproduces the `RP-6688` uniform liquidation
artifact in this scratch sub-window dry-run evidence.

This statement is build-test evidence only. It is not strategy-quality
evidence, not canonical evidence, and not a profitability, ranking, readiness,
promotion, or trading claim.

## Identity-hash scope observation

Result-population identity construction includes
`backtest_assumption_summary` in both `input_identity_hash.hash_scope` and
`result_population_identity_hash.hash_scope`.

Classification:

```text
params sizing fields surfaced by runner assumption text are identity-bearing.
```

The raw `BacktestResult.params` dictionary is not copied wholesale into the
result population. Sizing fields affect identity when the runner records them
in `backtest_assumption_summary.order_size_assumption`; dynamic sizing can
also affect `variant_result_rows`, which are in the result-population identity
hash scope.

Implication for 02d:

- A future structured sizing metadata package should treat sizing mode,
  target leverage, equity basis, and entry reference basis as identity-bearing.
- Fixed-mode reruns after this package may produce new scratch identity hashes
  because sizing-mode provenance is now present in the identity-scoped
  assumption string.
- Committed result populations remain immutable historical artifacts and are
  not rehashed or mutated by this package.

## Limitations

- Full-slice dynamic 1x dry-run evidence was attempted but exceeded a
  20-minute local command timeout.
- The completed payoff check uses a documented real-data sub-window, not the
  full D4 slice.
- The sub-window scratch run omits D4 full-slice catalog arguments to avoid
  falsely claiming full-slice coverage in the generated dry-run payload.
- No structured sizing schema fields exist yet.
- No canonical result population is written.

## Tests and validation

Focused validation completed:

```text
C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q
```

Result:

```text
68 passed, 2 existing timestamp parsing warnings.
```

Additional validation:

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
  pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
  pass.
- All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`:
  pass; changed-file set is expected and there are no forbidden-path matches.
- `git diff --check`: pass.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
  environment-only failure in
  `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`
  because the isolated worktree lacks gitignored
  `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`;
  remaining suite result was 1359 passed, 1 failed, 6 warnings.

Direct forbidden-scope checks showed no status or diff for
`research/result_populations`, `lib/backtest.py`, `lib/evaluation.py`,
`research/schemas`, or `tools/registry`.

## What this package does not authorize

This package does not authorize `lib/backtest.py` edits, `lib/evaluation.py`
edits, schema or validator changes, Strategy Spec mutation, variant manifest
mutation, sweep plan mutation, result-population mutation, canonical result
population writes, data acquisition, candidate registration, ranking,
readiness, promotion, paper/live/runtime behavior, OMS/risk behavior,
broker/exchange behavior, or protected-path behavior.

## Next authority

If this package is clean, dynamic dry-run evidence is non-degenerate, no
canonical write occurred, and identity-hash scope is observed without
committed-RP integrity issues, Side may draft `WP-REALISM-SIZING-02d` after
merge under Main's conditional rule.

No canonical dynamic-sizing rerun is authorized by this package.
