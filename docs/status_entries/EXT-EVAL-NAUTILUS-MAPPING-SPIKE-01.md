# EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01 — Status Fragment

## Final synchronized facts

- Branch: ext/eval-nautilus-mapping-spike-01
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/519
- Base: current origin/main commit after final rebase, `0434ce273c45085b99d0ff30a4b085f422785a28`
- Prerequisite: PR #513 merged
- Package class: bounded offline Nautilus mapping spike
- Decision label: VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE
- Nautilus version: 1.221.0
- Fixture: STRAT-SPEC-0004 / VM-0004 / SWEEP-PLAN-0004 / RP-2592
- Data slice: binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
- Rows: 220128
- Variants attempted: 8
- Variants expressible: 8
- Repeated runs: true
- Normalized identical: true
- Run checksum: d5a42698d41d45b6f138a29b348321805636f09b4016bd9801525426b00c6ce5
- Report checksum: 4c3d84f639c4da9e20c064cc5e6b6f15cbe4110693d23aa6e48f11c1739772a5
- Exact trade counts: true
- Max absolute return delta: 0.004382623128073526

## Unsupported semantics

Nautilus 1.221.0 does not expose the RP zero-equity liquidation rule through this low-level bounded mapping; no RP-2592 variant liquidated.

Continuous canonical quantities are rounded to 8 decimal places by the synthetic offline instrument.

## Boundary summary

- No runtime/paper/live touch.
- No OMS/risk/reconciliation touch.
- No private API/credentials/order/account methods.
- No canonical RP/spec/VM/sweep mutation.
- No runner/backtester mutation or replacement.
- No dependency-file mutation.
- No promotion/readiness/screen-gate authority.
- Nautilus installed only in an isolated temp venv.

## Authority label

NON-CANONICAL NAUTILUS MAPPING SPIKE

NOT CANONICAL EVIDENCE

NOT RUNNER REPLACEMENT

NOT PAPER/LIVE/RUNTIME AUTHORITY

CANONICAL USE REQUIRES SEPARATE MAPPING, VALIDATION, DETERMINISM, AUDITABILITY, PROVENANCE, AND MAIN APPROVAL

## Changed files in PR scope

- tools/simulators/nautilus_mapping_spike.py
- tests/test_nautilus_mapping_spike.py
- scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.json
- scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.md
- scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.sha256
- docs/status_entries/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01.md

## Validation receipt

- python -m pytest tests/test_nautilus_mapping_spike.py -q
- python -m tools.research_query.run --list-views
- python tools/dev/diff_scope_summary.py
- git diff --check
