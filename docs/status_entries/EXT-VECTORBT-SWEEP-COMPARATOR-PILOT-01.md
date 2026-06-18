# EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01 - Vectorbt Sweep Comparator Pilot

## Branch / PR

- Branch: `ext/vectorbt-sweep-comparator-pilot-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/508`

## Package Class

External-repo adoption pilot / non-canonical comparator / scratch evidence.

## Scope Summary

This package adds an isolated vectorbt sidecar comparator for the current
`STRAT-SPEC-0004` / `VM-0004` / `SWEEP-PLAN-0004` / `RP-2592` fixture. The
sidecar uses repo compiler output, runs vectorbt twice for determinism, runs a
repo dry-run baseline, and writes only non-canonical scratch comparison reports
under the requested scratch output directory.

## Changed Files

- `tools/external_pilots/__init__.py`
- `tools/external_pilots/vectorbt_sweep_comparator.py`
- `tests/test_vectorbt_sweep_comparator.py`
- `docs/status_entries/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01.md`
- `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/vectorbt_run_1.json`
- `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/vectorbt_run_2.json`
- `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/runner_baseline.json`
- `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/comparison_report.json`
- `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/comparison_report.md`

## Dependency Scope

No repo dependency file is changed. Current repo truth has a single broad
`requirements.txt` / `requirements.lock.txt` dependency surface and no sidecar,
research-only, or dev-only dependency group. `vectorbt==1.0.0` requires
`pandas<3`, while the repo lock pins `pandas==3.0.1`, so adding vectorbt to the
current broad dependency file would contaminate the shared environment. The
pilot was run from an isolated local venv outside the repo.

Future option: add an explicit external-pilot or research-side dependency group
before committing vectorbt as a repo dependency.

## Fixture Used

- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- RP comparator: `RP-2592`
- Data slice: BTCUSDT 15m D4 catalog slice,
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`

## Pilot Result

- Command:
  `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_vectorbt_pilot_venv\Scripts\python.exe -m tools.external_pilots.vectorbt_sweep_comparator --repo-max-workers 4`
- Output directory:
  `scratch/EXT-VECTORBT-SWEEP-COMPARATOR-PILOT-01/`
- Vectorbt wall-clock: `37.47685239999555` seconds.
- Repo runner dry-run wall-clock: `222.9266459000064` seconds.
- Speed ratio, vectorbt / repo: `0.1681129335108992`.
- Determinism run 1 hash:
  `sha256:afe22d9fbc2aa7889370f57b6268132c50a29d98cd0b73c194c0ddeb060cb6dd`
- Determinism run 2 hash:
  `sha256:afe22d9fbc2aa7889370f57b6268132c50a29d98cd0b73c194c0ddeb060cb6dd`
- Determinism match: `true`.
- Matched variants: none.
- Explained-difference variants:
  `VAR-000001`, `VAR-000002`, `VAR-000003`, `VAR-000004`,
  `VAR-000005`, `VAR-000006`, `VAR-000007`, `VAR-000008`.
- Unexplained-difference variants: none.

Per-variant trade-count deltas were `+1` for all eight variants. Return deltas
were small but non-zero; the report records them as explained by non-canonical
vectorbt accounting, percent-sizing approximation, and missing repo-equivalent
zero-equity liquidation / funding semantics.

## Validation Summary

- `.\.venv\Scripts\python.exe -m pytest tests/test_vectorbt_sweep_comparator.py -q`:
  `PASS`, 7 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_spec_signal_compiler.py -q`:
  `PASS`, 196 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
  `PASS`, 94 passed, 2 existing timestamp parsing warnings.
- `.\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  `PASS`, 64 passed.
- Read-only `RP-6236` API dry-run byte regression:
  `PASS`; generated `RP-6236`, denominator `8`, successful `8`, `dry_run=true`,
  `wrote=false`, and generated payload equaled committed
  `research/result_populations/RP-6236.result_population.json`.
- Direct integrity-view sweep through query-layer API:
  `PASS`; 55 discovered `v_integrity_*` views run, 0 nonempty.
- `.\.venv\Scripts\python.exe tools\dev\verify.py`:
  `PASS`; standard commands, result-population validator, and view listing passed.
- `.\.venv\Scripts\python.exe -m pytest -q`:
  attempted serial full pytest; timed out after 20 minutes with no material
  failure output.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; 4 deterministic pytest file shards over 70 test files passed, and all
  discovered integrity views were clean.

## Boundary Summary

- Canonical Result Population write: `NO`.
- Canonical Strategy Spec / VM / Sweep Plan mutation: `NO`.
- `lib/backtest.py` canonical behavior change: `NO`.
- Offline runner behavior change: `NO`.
- Runtime / paper / live / OMS / risk / broker / exchange / credential paths touched: `NO`.
- Vectorbt output authority: non-canonical scratch comparator only.

## Recommendation

`EXPLORATION_ONLY`.

Vectorbt was materially faster and deterministic in this pilot, but it did not
match canonical runner accounting exactly. The observed differences are
explained and documented, but the sidecar is not suitable as canonical evidence
or as a runner replacement from this package.

## Merge Status

Validation complete on branch. Draft PR #508 opened. GitHub connector reported
`mergeable=false` immediately after creation; this may be transient, but it is
not called ready-to-merge from this fragment.

## Next Dependency / Runway Note

If vectorbt remains useful after this pilot, the next package should design a
proper external-pilot dependency group rather than adding vectorbt to the current
broad requirements surface.
