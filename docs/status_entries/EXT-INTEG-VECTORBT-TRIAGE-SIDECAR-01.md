# EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01 - Non-Canonical Vectorbt Fast Triage

## Branch / PR

- Branch: `ext/integ-vectorbt-triage-sidecar-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/517`
- Base: `origin/main` at `c095c88`.
- Prerequisite: PR #513 / `EXT-SIMULATOR-PILOT-01` verified merged.

## Package Class

T3 non-canonical sidecar / research acceleration; additive, repo-governed,
dependency-isolated, non-runtime, and boundary-preserving.

## Scope Summary

This package productionizes vectorbt as a bounded fast-triage sidecar under
`tools/sidecars/`. It reads a repo Strategy Spec, Variant Manifest, Sweep Plan,
and controlled OHLCV fixture; uses the existing repo signal compiler; runs no
canonical runner or backtester; and writes deterministic, explicitly
non-canonical scratch metrics ordered by variant id rather than by metric rank.

The sidecar caps each run through `--max-variants` with a hard maximum of
`10,000`. If vectorbt is unavailable, it writes a deterministic
`DEFERRED_OPTIONAL_DEPENDENCY_UNAVAILABLE` report with decision `BLOCKED`
instead of failing ambiguously. Vectorbt remains optional and isolated from repo
dependency files.

## Changed Files

- `tools/sidecars/__init__.py`
- `tools/sidecars/vectorbt_triage_sidecar.py`
- `tests/test_vectorbt_triage_sidecar.py`
- `docs/status_entries/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01.md`
- `scratch/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01/vectorbt_triage_report.json`
- `scratch/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01/vectorbt_triage_report.md`
- `scratch/EXT-INTEG-VECTORBT-TRIAGE-SIDECAR-01/vectorbt_triage_report.sha256`

## Fixture / Output Facts

- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Data slice identity:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- OHLCV checksum:
  `sha256:c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`
- Vectorbt version in isolated environment: `1.0.0`
- Selected / processed variants: `8 / 8`
- Variant ordering: `variant_id_ascending_not_metric_ranked`
- Triage rows checksum:
  `sha256:6c7df46eb3420e5ae643ec5896ce1f3c66881d8711ddac5fb12142c99843abe3`
- Report output checksum:
  `sha256:add979d96a6d95380380e4fd84e13f72847a66135a3af706dac3cca9566a0fd4`
- Two isolated-environment runs produced the same report output checksum.
- The default repo environment exercised the explicit deferred-report path
  because vectorbt is not installed there.

## Validation Summary

- `python -m pytest tests/test_vectorbt_triage_sidecar.py -q`: `PASS`, 10 passed.
- Isolated vectorbt CLI, run twice with `--max-variants 8`: `PASS`, 8 selected
  and 8 processed each run; report checksums matched.
- Default repo-environment CLI blocked-mode smoke run: `PASS`; explicit deferred
  report written with decision `BLOCKED` and exit code 0.
- `python -m tools.research_query.run --list-views`: `PASS`.
- `python tools/dev/diff_scope_summary.py`: `PASS`; forbidden-path matches:
  none.
- `python tools/dev/verify.py --integrity-views --pytest
  tests/test_vectorbt_triage_sidecar.py` with explicit package path
  authorizations: `PASS`; result-population validator passed, query view
  listing passed, focused tests passed, and all 55 discovered integrity views
  were clean / zero rows.
- `python -m pytest -q`: `PASS`, 1690 passed, 1 skipped, 6 warnings in
  1944.60 seconds.
- `git diff --check` and staged diff checks: `PASS`.
- Ruff and Black were unavailable in the repo environment and are not used as
  merge evidence; no dependency installation or mutation was performed.

## Boundary Summary

- Runtime / paper / live touched: `NO`.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order paths touched: `NO`.
- Private APIs / credentials / account / balance / position / order methods:
  `NO`.
- Canonical Result Population mutation or write: `NO`.
- Canonical Strategy Spec / Variant Manifest / Sweep Plan mutation or write:
  `NO`.
- Runner / backtester mutation or replacement: `NO`.
- Schema / validator / query-layer mutation: `NO`.
- Dependency-file mutation: `NO`.
- Candidate ranking, screen-gate, promotion, readiness, finalist confirmation,
  or candidate-evidence authority: `NO`.
- Local absolute paths in committed outputs: `NO`.

## Merge Status

PR #517 is open as ready for review. The branch was rebased on current
`origin/main` at `c095c88`; GitHub reported `MERGEABLE` with merge state
`CLEAN` after implementation and status-fragment synchronization. Required
validation was rerun after the final rebase.

## Next Dependency / Runway Note

Decision label: `ADOPT_AS_NON_CANONICAL_TRIAGE_SIDECAR`.

Any finalist surfaced by this sidecar requires a later, separately authorized
confirmation through the repo-owned canonical runner/evidence path. This
package creates no finalist confirmation or downstream authority.
