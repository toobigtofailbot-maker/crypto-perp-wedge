# EXT-INTEG-ROBUSTNESS-MC-01 - Productionized Seeded Advisory Robustness MC

## Branch / PR

- Branch: `ext/integ-robustness-mc-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/515`
- Base: `origin/main` at `893fdb4` when the dedicated worktree was created.

## Package Class

T3 advisory robustness tooling; repo-owned, additive, deterministic,
non-runtime, non-canonical, and boundary-preserving.

## Scope Summary

This package productionizes the seeded robustness / Monte Carlo pilot into
repo-owned advisory tooling under `tools/robustness/`. The tool reads an
existing Result Population JSON and, where available, the linked Variant
Manifest. It performs seeded row-level bootstrap diagnostics over finite
per-variant row metrics, reports parameter-sensitivity summaries from existing
parameter mappings, writes advisory scratch reports only, and clearly reports
that full per-trade Monte Carlo remains queued because committed Result
Populations do not contain per-trade rows.

The tool does not mutate canonical Result Populations, Strategy Specs, Variant
Manifests, Sweep Plans, runner/backtester code, trial logs, query surfaces,
schemas, validators, runtime, paper/live, OMS/risk, broker/exchange, or
promotion/readiness logic.

## Changed Files

- `tools/robustness/__init__.py`
- `tools/robustness/seeded_advisory_mc.py`
- `tests/test_seeded_advisory_mc.py`
- `docs/status_entries/EXT-INTEG-ROBUSTNESS-MC-01.md`
- `scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.json`
- `scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.md`
- `scratch/EXT-INTEG-ROBUSTNESS-MC-01/bootstrap_samples.sha256`

## Fixture / Output Facts

- Result Population: `RP-2592`
- Input path: `research/result_populations/RP-2592.result_population.json`
- Input checksum:
  `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
- Rows used: `8` successful attempted variant rows
- Seed: `20260619`
- Bootstrap samples: `1000`
- Confidence level: `0.95`
- Metrics used: `drawdown`, `exposure`, `fees`, `funding`, `pnl`,
  `return_pct`, `sharpe`, `slippage`, `trade_count`, `win_rate`
- Parameter sensitivity: `performed` from
  `research/variant_manifests/VM-0004.variant_manifest.json`
- Parameter count: `3`
- Per-trade Monte Carlo: `QUEUE_PER_TRADE_INSTRUMENTATION`
- Bootstrap sample checksum:
  `sha256:6c7434602cc8235fadec0b75f13548e77cb7f7684e40e8884f52eef286a52121`
- Report output checksum:
  `sha256:5a400437ed6df521184dc372a42ad640baeb5c42e79190f10704634174c4f672`

## Validation Summary

- `python -m pytest tests/test_seeded_advisory_mc.py -q`:
  `PASS`, 15 passed.
- Deterministic CLI rerun:
  `PASS`; same seed/input produced identical report checksum
  `sha256:5a400437ed6df521184dc372a42ad640baeb5c42e79190f10704634174c4f672`
  and identical bootstrap sample checksum
  `sha256:6c7434602cc8235fadec0b75f13548e77cb7f7684e40e8884f52eef286a52121`.
- `python -m tools.research_query.run --list-views`: `PASS`.
- `python tools/dev/diff_scope_summary.py`: `PASS`; forbidden-path matches:
  none.
- `python tools/dev/verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 1800`:
  `PASS`; result-population validator passed, query view listing passed, all
  discovered integrity views were clean / zero rows, and all four pytest shards
  passed.
- `python -m pytest -q`: `PASS`, 1658 passed, 1 skipped, 6 warnings in
  2048.92 seconds.

Earlier validation context not used as merge evidence:

- An initial `python -m pytest -q` attempt timed out at the 20-minute command
  timeout before producing a result.
- The first sharded verification attempt failed because the isolated worktree
  lacked the gitignored D4A normalized CSV expected by
  `tests/test_external_simulator_pilot.py`; the same file existed in the root
  checkout and was copied locally into the worktree under ignored
  `data/processed/d4a/`.
- After that local-only ignored data copy, the previously failing shard passed
  with 280 passed, 1 skipped, and final sharded verification plus exact
  unsharded pytest both passed.

## Boundary Summary

- Runtime / paper / live touched: `NO`.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order paths touched: `NO`.
- Private APIs / credentials / account / balance / position / order methods:
  `NO`.
- Canonical Result Population mutation: `NO`.
- Canonical Strategy Spec / Variant Manifest / Sweep Plan mutation: `NO`.
- Runner / backtester mutation: `NO`.
- Schema / validator / query-layer mutation: `NO`.
- External dependency change: `NO`.
- Screen-gate / promotion / readiness / ranking / candidate-evidence authority:
  `NO`.
- Fabricated per-trade data: `NO`.

## Active-WP Requirement Traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Seeded MC / robustness diagnostics | Authorization / Objective | `tools/robustness/seeded_advisory_mc.py`; scratch report | satisfied |
| Fixture-validated deterministic output | Implementation requirements / Validation | `fixture_validation` in scratch JSON; focused tests; checksum rerun | satisfied |
| Advisory, non-canonical labeling | Objective / Implementation requirements | `labels`, `boundary_statement`, scratch Markdown | satisfied |
| Row-level bootstrap over RP rows | Implementation requirements | `bootstrap_ci` in scratch JSON | satisfied |
| Parameter-sensitivity summary where available | Implementation requirements | `parameter_sensitivity` in scratch JSON | satisfied |
| Missing per-trade instrumentation flagged, not fabricated | Authorization / Implementation requirements | `per_trade_monte_carlo.status=QUEUE_PER_TRADE_INSTRUMENTATION` | satisfied |
| No screen gate, promotion, ranking, or readiness authority | Non-authority posture / Forbidden scope | status boundary summary; tool labels | satisfied |
| No canonical RP/spec/VM/sweep mutation | Forbidden scope | changed-file list and git diff | satisfied |
| No runner/backtester/runtime/protected path changes | Global forbidden scope | changed-file list and source guard tests | satisfied |
| Focused tests and deterministic command run | Validation | validation summary | satisfied |

## Merge Status

PR #515 is open as ready for review. Final rebase and GitHub mergeability
facts are recorded in the PR body after the final synchronization step.

## Next Dependency / Runway Note

Decision label: `ADOPT_AS_ROBUSTNESS_LAYER`.

Follow-up option: `QUEUE_PER_TRADE_INSTRUMENTATION` remains a possible later
package if Main authorizes real per-trade instrumentation. This package does
not implement that instrumentation.
