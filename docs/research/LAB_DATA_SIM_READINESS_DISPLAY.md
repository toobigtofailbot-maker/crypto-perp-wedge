# Lab Data / Simulator Readiness Display

This document describes the read-only data and simulator readiness display added
by `WP-LABPROD-DATA-SIM-READINESS-DISPLAY-01`.

The display answers whether a feature, family, or data requirement can be tested
now on the offline research path, and if not, which prerequisite category blocks
it. It separates unavailable data from strategy failure and avoids treating a
missing source as a NO-GO result.

## CLI

```powershell
python -m tools.lab_readiness.run --json
python -m tools.lab_readiness.run --markdown
python -m tools.lab_readiness.run --out-dir build/lab_readiness
```

`--json` and `--markdown` write to stdout only. `--out-dir` writes
`readiness.json` and `readiness.md` to the requested directory.

## Taxonomy

- `testable_now_with_current_public_history`
- `testable_now_with_current_caveats`
- `needs_local_full_history_materialization`
- `needs_vendor_or_captured_history`
- `needs_runner_or_compiler_support`
- `needs_simulator_realism_upgrade`
- `go_gated_or_paper_phase_only`
- `protected_or_out_of_scope`
- `unknown_needs_review`

The taxonomy is closed in `tools/lab_readiness/model.py`. Unknown or missing
evidence fails closed to `unknown_needs_review` where no safer specific blocker
exists.

## Current Display Coverage

The first display projection covers:

- OHLCV-only indicators;
- funding-rate feature history;
- funding PnL / cost realism;
- taker-flow archive-derived support;
- open interest;
- long/short ratio;
- liquidation volume/history;
- L2 / order-book features;
- mark / index / premium index fields;
- UTC/session/time-derived fields;
- Donchian / breakout family support;
- SMA / StdDev mean-reversion support;
- EMA / RVOL / rolling VWAP / session-family support;
- simulator realism / paper-shadow phase boundary.

The display reads committed repo files only. It does not inspect local ignored
data dumps, call providers, acquire archives, or run a strategy.

## Key Boundaries

- Read-only readiness display only.
- No data acquisition, vendor integration, provider/API call, credential use, or
  dependency/config change.
- No runner, compiler, backtester, schema, validator, or query-layer behavior
  change.
- No Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate
  registry, crossing, promotion, paper/live/runtime, OMS, risk, reconciliation,
  broker/exchange/order, scheduler, or autonomy authority.

Readiness means operator-facing routing information for idea intake. It is not
candidate approval, evidence sufficiency, ranking, recommendation, or permission
to run blocked ideas.
