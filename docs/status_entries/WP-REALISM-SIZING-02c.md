# WP-REALISM-SIZING-02c — Dynamic sizing runner exposure

- Package class: T3 runner integration, build-test only, non-protected.
- Branch: `runner/realism-sizing-02c-dynamic-exposure`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/447
- Scope summary: Exposes opt-in dynamic equity target-leverage sizing through
  the offline runner while preserving fixed sizing as the default.
- Authorization basis: Main/Karl accepted `WP-REALISM-SIZING-02b` and
  authorized runner exposure for `sizing_mode` / `target_leverage`, scratch
  dynamic 1x dry-run evidence, and read-only identity-hash scope observation.
- Reasoning model: GPT-5.5 high; runner exposure for methodology-sensitive
  dynamic sizing with no canonical write.
- Implementation summary: Adds a closed `sizing_mode` runner API/CLI surface,
  passes `sizing_mode`, `target_leverage`, and the existing resolved
  `order_size` into `run_backtest()`, and records sizing provenance in the
  existing `backtest_assumption_summary.order_size_assumption` field.
- Runner controls: `--sizing-mode fixed_order_size`,
  `--sizing-mode dynamic_equity_target_leverage`, and `--target-leverage`.
- Default preservation: `fixed_order_size` remains the default; omitted
  `--sizing-mode` keeps the runner on the pre-existing fixed order-size
  resolution path.
- Dry-run evidence: A full local 15m scratch CSV was created from the offline
  parquet, but the full-slice run exceeded a 20-minute local command timeout.
  The completed evidence uses a documented real-data sub-window from the same
  local offline parquet: 17,472 rows, `2024-01-01T00:00:00Z` through
  `2024-06-30T23:45:00Z`, dry-run true, wrote false, output path null,
  scratch result id `RP-4217`, committed denominator 10, and 10 successful
  rows.
- Dynamic payoff check: 0 of 10 variants hit `return_pct=-1.0` or drawdown
  `1.0` in the scratch sub-window dry-run. Dynamic 1x sizing does not reproduce
  the `RP-6688` uniform liquidation artifact in this build-test evidence.
- Identity-hash scope observation: Sizing fields surfaced by runner assumption
  text are identity-bearing because `backtest_assumption_summary` is in both
  `input_identity_hash` and `result_population_identity_hash` scope. Raw
  `BacktestResult.params` is not copied wholesale into result populations; when
  reflected in assumption text or row metrics, sizing behavior affects identity
  scope.
- Tests:
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
    pass, 68 passed, 2 existing timestamp parsing warnings.
- Validation summary:
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
    pass, 68 passed, 2 existing timestamp parsing warnings.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
    pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
    pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`:
    pass; changed-file set is expected and there are no forbidden-path
    matches.
  - `git diff --check`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
    environment-only failure in
    `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`
    because the isolated worktree lacks gitignored
    `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`;
    remaining suite result was 1359 passed, 1 failed, 6 warnings.
  - Direct final forbidden-scope checks: no status or diff for
    `research/result_populations`, `lib/backtest.py`, `lib/evaluation.py`,
    `research/schemas`, or `tools/registry`.
- No-canonical-write proof: Dynamic dry-run returned `dry_run=true`,
  `wrote=false`, and `output_path=null`; no file was written under
  `research/result_populations`.
- Boundary summary: No `lib/`, schema, validator, Strategy Spec, variant
  manifest, sweep plan, result population, data, candidate registry, dashboard
  implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected
  path changes.
- Merge status: PR #447 is open for review; final rebase and GitHub
  mergeability gate are recorded in the final report-back.
- Auto-progression condition: If this package is clean, dynamic dry-run
  evidence is non-degenerate, no canonical write occurred, and identity-hash
  scope is observed without committed-RP integrity issues, Side may draft
  `WP-REALISM-SIZING-02d` after merge under Main's conditional rule. Otherwise
  stop and report.
- Next authority: No canonical dynamic-sizing rerun is authorized. No result
  population write is authorized. No candidate lifecycle action is authorized.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 8 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02c` on `runner/realism-sizing-02c-dynamic-exposure` from `origin/main` merge `55825a6` | satisfied |
| Verify WP-REALISM-SIZING-02b merged and artifacts exist | WP sections 4 and 7 | `origin/main` includes PR #446 merge; 02b implementation note, status fragment, `RP-6688`, and required parent artifacts inspected | satisfied |
| Modify only allowed files | WP sections 10-11 | changed-file list and final scope checks | satisfied |
| Expose `sizing_mode` and `target_leverage` through runner | WP section 12 | `tools/research_runner/run_offline_sweep.py`; focused pass-through tests | satisfied |
| Preserve fixed default behavior | WP section 12 | default runner test and fixed-mode pass-through test | satisfied |
| Record sizing provenance in existing fields | WP section 13 | `backtest_assumption_summary.order_size_assumption`; provenance tests | satisfied |
| Produce scratch/no-write dynamic 1x evidence | WP sections 14-15 | implementation note dry-run evidence section; no-canonical-write proof | satisfied |
| Observe identity-hash scope read-only | WP section 16 | implementation note identity section; identity-scope test | satisfied |
| Add focused runner tests | WP section 17 | `tests/test_offline_research_runner.py` | satisfied |
| Add implementation note | WP section 18 | `docs/research_pipeline/2026-06-dynamic_sizing_runner_exposure_impl_note.md` | satisfied |
| Add status fragment | WP section 19 | this file | satisfied |
| Update project status compactly | WP section 20 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 21 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation and final checks | WP section 22 | validation summary | satisfied |
| Complete authority/finality text audit | WP section 23 | final report-back and PR body | satisfied |
| Push and open PR with required title | WP sections 25-26 | PR #447 | satisfied |
