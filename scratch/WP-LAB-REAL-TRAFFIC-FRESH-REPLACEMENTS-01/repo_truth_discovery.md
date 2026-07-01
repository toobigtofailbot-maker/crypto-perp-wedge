# Repo Truth Discovery

Package: `WP-LAB-REAL-TRAFFIC-FRESH-REPLACEMENTS-01`

## Base And PR State

- Base commit inspected: `360cd5be05d5e1458e518ed3c65b2d0b25be11a0`.
- `origin/main` was refreshed before creating the package worktree.
- PR #598 is merged: yes. GitHub reports merge commit `360cd5be05d5e1458e518ed3c65b2d0b25be11a0`, merged 2026-07-01.
- Worktree branch: `lab/real-traffic-fresh-replacements-01`.

## Merged PR #598 Packet

- Source proposal: `scratch/WP-LAB-REAL-TRAFFIC-ACCEPTANCE-BATCH-01/frozen_hypothesis_set_proposal.json`.
- Packet status: `blocked_pending_karl_signoff`.
- `LAB-RT-HYP-001` is present and retained unchanged in this package.
- Rejected replacement targets from the merged packet:
  - `LAB-RT-HYP-002`: 15m UTC opening-range breakout retest.
  - `LAB-RT-HYP-003`: 15m SMA crossover trend continuation.
  - `LAB-RT-HYP-004`: 15m volatility-normalized regime-gated mean reversion.
- Required signed frozen-set artifacts remain outside this package's authority and were not created.

## Concluded Evidence Surfaces Inspected

- `research/candidate_registry.jsonl` lists concluded NO-GO candidates `H-001` through `H-010` and `H-012`; `H-011` remains reserved/pending.
- `research/experiments/REP-0003.report.json` records `H-002` Donchian 4h NO-GO and constrains Donchian freshness.
- `research/experiments/REP-0032.report.json` records `H-012` 15m Donchian breakout with funding filter NO-GO and constrains Donchian/funding-filtered trend freshness.
- Committed canonical result populations inspected: `RP-2134`, `RP-2592`, `RP-3731`, `RP-4492`, `RP-6236`, `RP-6688`, `RP-7134`, `RP-7520`.
- Strategy Specs inspected by metadata: `STRAT-SPEC-0001` through `STRAT-SPEC-0006`.
- Prior blocked freshness evidence inspected: `docs/status_entries/WP-RESEARCH-EDGE-SMA-FAMILY-01.md`.
- ORB prior surface inspected: `docs/status_entries/WP-ONLINE-ORB-15M-PREREG-01.md`.
- Supported primitive surfaces inspected: indicator catalog and compiler status entries for RSI, Donchian, MA-distance, RVOL, rolling VWAP, EMA, ATR, and UTC session/time fields.

## Supported-Family Routes Discovered

- Closed indicator catalog includes `sma`, `ema`, `atr`, `stddev`, `rsi`, `donchian`, `ma_distance`, `rvol`, and `rolling_vwap`.
- Session/time fields are supported through timestamp-derived `data_ref` fields: `hour_of_day_utc`, `day_of_week_utc`, and `is_weekend_utc`.
- This package treats catalog/compiler support as a proposal route only. It does not assert that a final Strategy Spec/VM/Sweep can be written without a later authorized package proving validation.

## Decisions For This Packet

- Retain `LAB-RT-HYP-001` unchanged.
- Reject ORB, SMA crossover, z-score/SMA-band fade, funding, and Donchian retunes as replacement choices.
- Propose three replacements that are supported-family and economically distinct: RVOL-gated range-expansion breakout, rolling VWAP distance reversion, and session-filtered EMA impulse continuation.

## Boundary

No research execution, frozen set, Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate lifecycle artifact, crossing, promotion/readiness, paper/live/runtime contact, protected-path change, dependency change, provider/API call, or notification/scheduler activation occurred.
