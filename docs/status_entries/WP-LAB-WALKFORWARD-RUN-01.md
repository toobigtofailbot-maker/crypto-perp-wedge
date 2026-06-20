# WP-LAB-WALKFORWARD-RUN-01 - Non-canonical walk-forward run capability

## Package

- Package: `WP-LAB-WALKFORWARD-RUN-01`
- Follow-up: `WP-LAB-WALKFORWARD-RUN-01-FOLLOWUP-02`
- Decision: `COMPLETE`
- Package class: Tier 3 run-path / non-canonical evidence tooling

## Branch / PR

- Branch: `lab/walkforward-run-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-walkforward-run-01`
- Base before continuation: `fcb8a8f`; observed behind `origin/main` by 3 commits.
- Base after rebase: `da62902`
- Rebase result: clean; no conflicts.
- Dirty work preserved: yes.
- Snapshot path: `C:\Users\dersu\AppData\Local\Temp\WP-LAB-WALKFORWARD-RUN-01_followup02_20260620_090855`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/525

## Scope Summary

This package adds a deterministic scratch-only walk-forward run helper over the
merged fold-manifest contract. It validates a scratch fold manifest, carries all
included variants through declared IS/OOS fold windows via the existing offline
runner path, writes per-fold metrics and descriptive degradation comparisons,
and emits a display-only dashboard fragment for later dashboard work.

The scratch demonstration targets `STRAT-SPEC-0004` / `VM-0004` /
`SWEEP-PLAN-0004` over the D4 BTCUSDT 15m slice. The output is not canonical
evidence, not promotion evidence, not ranking authority, not readiness
authority, not paper/live authority, and not candidate registration. The first
canonical walk-forward run still requires explicit GO / Karl gate.

## Changed Files

- `tools/walkforward/__init__.py`
- `tools/walkforward/run_walkforward_scratch.py`
- `research/schemas/walkforward_run_report.schema.json`
- `tools/registry/validate_walkforward_run_report.py`
- `tests/test_walkforward_run_report_validator.py`
- `tests/test_run_walkforward_scratch.py`
- `tests/fixtures/walkforward_run/valid_walkforward_run_report.json`
- `tests/fixtures/walkforward_run/invalid_walkforward_run_report_authority.json`
- `tests/fixtures/walkforward_run/invalid_walkforward_run_report_counts.json`
- `scratch/WP-LAB-WALKFORWARD-RUN-01/README.md`
- `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_fold_manifest.input.json`
- `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json`
- `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_dashboard_fragment.json`
- `docs/status_entries/WP-LAB-WALKFORWARD-RUN-01.md`

## Validation Summary

Commands run from the dedicated worktree after rebase onto `da62902`.

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_walkforward_run_report_validator.py tests/test_run_walkforward_scratch.py -q`: PASS, 8 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_walkforward_run_report tests/fixtures/walkforward_run/valid_walkforward_run_report.json`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_walkforward_run_report scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_walkforward_fold_manifest scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_fold_manifest.input.json`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_walkforward_fold_manifest`: PASS; canonical manifest directory absent, nothing to validate.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_walkforward_fold_manifest_validator.py tests/test_research_query_walkforward_views.py -q`: PASS, 7 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: PASS.
- Scratch demonstration regeneration with `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.walkforward.run_walkforward_scratch --walkforward-manifest scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_fold_manifest.input.json --ohlcv-input C:\GitHub\crypto-perp-wedge\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --created-at-utc 2026-06-20T12:00:00Z`: PASS; rewrote only the scratch report and dashboard fragment.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`: PASS; no forbidden-path matches.
- `git diff --check`: PASS; Git reported line-ending normalization warnings on regenerated scratch JSON files only.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --integrity-views --timeout-seconds 120 --max-output-chars 12000`: PASS; all discovered `v_integrity_*` views clean.

## Full Pytest / Verify Disclosure

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: TIMED OUT after approximately 902 seconds. The partial log reached 53% and showed one failure before timeout.
- The surfaced failure was `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`, where `fixture["normalized_data_local_exists"]` was `False` instead of `True`. This is a local data-file availability expectation outside this package, not a walk-forward-run failure.
- A sharded `verify.py --full-pytest-sharded --pytest-shards 6 --pytest-shard-workers 3 --full-pytest-timeout-seconds 900 --max-output-chars 12000` fallback was observed running in this worktree; it exceeded its timeout and remained hung after an additional wait, so it was stopped and is not used as merge evidence.
- Full pytest is not counted as a pass. No package-specific failure surfaced.

## Boundary Summary

- No canonical writes.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, trial log, candidate record, or canonical fold manifest mutation.
- No `docs/project_status.md` edit.
- No `lib/backtest.py` change.
- No `lib/evaluation.py` change.
- No `tools/research_runner/run_offline_sweep.py` semantic change.
- No funding-into-backtest wiring.
- No dashboard implementation or results-surface change.
- No runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order, dependency, credential, or API config path touched.

## Active-WP Requirement Traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Continue existing dirty branch without discarding untracked work | Follow-up sections 1-8 | Snapshot path, preservation commit, changed files above | satisfied |
| Consume merged fold-manifest contract | Original WP sections 3, 7 | `tools/walkforward/run_walkforward_scratch.py`, scratch fold manifest validation | satisfied |
| Produce per-fold IS/OOS metrics and degradation comparison | Original WP section 7 | `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json`, schema/tests | satisfied |
| Emit dashboard-consumable scratch fragment only | Original WP sections 7, 9 | `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_dashboard_fragment.json` | satisfied |
| Validate non-canonically against STRAT-SPEC-0004 | Original WP section 8 | Scratch regeneration command and report lineage | satisfied |
| Preserve non-authority posture | Original WP sections 7, 11 | schema consts, validator semantic checks, report flags | satisfied |
| Avoid forbidden paths and canonical writes | Original WP sections 6, 8, global forbidden scope | boundary summary and diff-scope check | satisfied |

## Merge Status

- Ready for review.
- Full pytest timeout / unrelated local-data failure disclosed and not counted as a pass.

## Next Dependency / Runway Note

This package proves the scratch walk-forward run path only. The first canonical
walk-forward run waits for explicit GO and Karl gate. Funding-into-backtest
remains serialized outside this package.
