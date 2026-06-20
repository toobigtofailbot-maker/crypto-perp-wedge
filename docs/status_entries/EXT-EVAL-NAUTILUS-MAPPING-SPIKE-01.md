# EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01 - Bounded Nautilus Offline Mapping and Determinism Spike

## Branch / PR

- Branch: `ext/eval-nautilus-mapping-spike-01`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/519
- Base: refreshed `origin/main` at `0434ce273c45085b99d0ff30a4b085f422785a28`
- Prerequisite: PR #513 / `EXT-SIMULATOR-PILOT-01` verified merged.

## Package Class

T3 isolated simulator evaluation / bounded mapping spike.

## Scope Summary

The package maps the frozen `STRAT-SPEC-0004` signal surface into an isolated
NautilusTrader 1.221.0 offline backtest over the checksum-verified 220,128-row
BTCUSDT 15m D4A slice. It attempts all eight `VM-0004` / `SWEEP-PLAN-0004`
variants, reconciles available fields against `RP-2592`, and repeats the full
run for normalized determinism evidence.

Decision label: `VIABLE_CANONICAL_GRADE_SIMULATOR_CANDIDATE`.

This label is non-canonical evaluation evidence only. It does not grant
Nautilus canonical, runner, backtester, paper/live, runtime, promotion,
readiness, or screen-gate authority.

## Changed Files

- `tools/simulators/nautilus_mapping_spike.py`
- `tests/test_nautilus_mapping_spike.py`
- `scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.json`
- `scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.md`
- `scratch/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01/nautilus_mapping_report.sha256`
- `docs/status_entries/EXT-EVAL-NAUTILUS-MAPPING-SPIKE-01.md`

`docs/project_status.md` is unchanged.

## Observed Result

- Variants available / attempted / expressible: `8 / 8 / 8`.
- RP trade counts match Nautilus-derived closed trade counts for all variants.
- Maximum absolute return delta versus `RP-2592`: `0.004382623128073526`.
- The `0.005` bounded-spike tolerance is explicitly not a canonical acceptance
  threshold.
- Run 1 normalized checksum:
  `sha256:d5a42698d41d45b6f138a29b348321805636f09b4016bd9801525426b00c6ce5`.
- Run 2 normalized checksum:
  `sha256:d5a42698d41d45b6f138a29b348321805636f09b4016bd9801525426b00c6ce5`.
- Report checksum:
  `sha256:4c3d84f639c4da9e20c064cc5e6b6f15cbe4110693d23aa6e48f11c1739772a5`.
- Normalized deterministic repeat result: `true`.

The mapping uses the repo signal compiler read-only, next-open market fills,
dynamic realized-equity 1x sizing, and zero funding. The canonical runner's
separate 4 bps taker fee plus 1 bps additive slippage cash costs are represented
as an equivalent 5 bps Nautilus taker commission and allocated 80/20 for field
comparison.

Unsupported semantics remain explicit: Nautilus 1.221.0 does not expose the
RP zero-equity liquidation rule through this bounded low-level mapping, though
no RP-2592 variant liquidated; canonical continuous quantities are rounded to
eight decimal places by the synthetic offline instrument.

## Validation Summary

- `python -m pytest tests/test_nautilus_mapping_spike.py -q`: PASS, 4 passed.
- `python -m pytest tests/test_nautilus_mapping_spike.py tests/test_external_simulator_pilot.py -q`:
  PASS, 11 passed after rebase. An earlier isolated-worktree attempt exposed the
  expected absent gitignored D4A file; validation reruns used a validation-only
  junction to the existing checksum-matching local data directory. No data was
  committed.
- Isolated `python -m tools.simulators.nautilus_mapping_spike --ohlcv-input data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`:
  PASS after rebase; 8 variants attempted, 8 expressible, two
  normalized-identical runs.
- `python -m tools.research_query.run --list-views`: PASS after rebase.
- `python tools/dev/diff_scope_summary.py`: PASS after rebase; no forbidden-path
  matches.
- `python -m pytest -q`: PASS after rebase, 1,684 passed, 1 skipped, 6 warnings.
- `git diff --check`: PASS after rebase.

## Boundary Summary

- Runtime / paper / live touched: `NO`.
- OMS / risk / reconciliation / safe-mode touched: `NO`.
- Private APIs / credentials / exchange / sandbox / orders / accounts used:
  `NO`.
- Canonical RP / Strategy Spec / Variant Manifest / Sweep Plan mutated: `NO`.
- Canonical runner / `lib/backtest.py` mutated: `NO`.
- Repo dependency files mutated: `NO`; Nautilus used only in an isolated temp
  virtual environment.
- Promotion / readiness / screen-gate / candidate-evidence authority created:
  `NO`.
- Machine-local absolute paths in committed outputs: `NO`.

## Merge Status

- PR #519 is open and ready for review.
- Final branch rebase, validation receipt check, push, and GitHub mergeability
  confirmation are recorded in the PR body against base `0434ce2`.

## Next Dependency / Runway Note

Any canonical use requires a separate Main-approved package covering mapping,
validation, determinism, auditability, provenance, and explicit promotion of
authority. This spike does not authorize that follow-up.
