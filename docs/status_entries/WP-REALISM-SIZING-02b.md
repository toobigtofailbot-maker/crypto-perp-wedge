# WP-REALISM-SIZING-02b - Dynamic equity sizing core

- Package class: T3 protected backtest-core implementation.
- Branch: `backtest/realism-sizing-02b-dynamic-equity`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/446
- Scope summary: Implements opt-in dynamic equity-relative entry sizing in
  `lib/backtest.py` and focused backtest tests while preserving fixed
  `order_size` behavior as the default.
- Authorization basis: Main/Karl accepted `WP-REALISM-SIZING-02a`, locked the
  dynamic sizing design, verified PR #445 merged, and explicitly authorized
  protected-path 02b implementation in `lib/backtest.py`.
- Reasoning model: GPT-5.5 xhigh; protected backtest-core sizing methodology
  implementation.
- Implementation summary: Adds additive sizing-mode validation, tracks current
  open position quantity separately from direction, computes dynamic entry
  quantity only when opening a new dynamic-mode position, and routes existing
  cost, funding, PnL, maintenance-margin, liquidation, and trade-row notional
  calculations through the current open quantity.
- Modes: `fixed_order_size` remains the default and uses `order_size`;
  `dynamic_equity_target_leverage` is opt-in and uses target leverage, realized
  equity at entry, and next-bar-open reference price.
- Fixed default preservation: Focused regression compares omitted
  `sizing_mode` with explicit `fixed_order_size` and asserts identical equity
  curve, per-bar PnL, trade rows, cost totals, realized/unrealized PnL,
  liquidation flags, drawdown tuple, and params snapshot.
- Dynamic sizing formula:
  `quantity = target_leverage * sizing_equity / entry_reference_price`.
- Edge-case handling: Dynamic mode rejects invalid target leverage and fails
  closed without opening a new position for non-positive/non-finite sizing
  equity, invalid/non-finite entry reference price, or non-finite/non-positive
  computed quantity.
- Cost/funding/liquidation interaction: Dynamic quantity drives entry/exit
  fee and slippage costs, funding notional, realized and unrealized PnL,
  maintenance-margin notional, liquidation price math, and trade-row notional
  fields. Fixed mode remains on `order_size`.
- Params snapshot: Existing `BacktestResult.params` records `sizing_mode`,
  `target_leverage`, `sizing_equity_basis`,
  `entry_reference_price_basis`, and `order_size`.
- Tests: Focused `tests/test_backtest.py` coverage added for fixed default
  preservation, formula math, equity-relative scaling, long/short symmetry,
  non-positive equity fail-closed behavior, invalid reference fail-closed
  behavior, invalid target leverage, no-lookahead, determinism, cost/funding
  interaction, maintenance-margin interaction, and benign 1x dynamic
  maintenance-margin behavior.
- Validation summary:
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_backtest.py -q`:
    pass, 63 passed.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_backtest_liquidation.py -q`:
    environment-only failure in
    `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`
    because the isolated worktree lacks gitignored
    `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`;
    remaining result was 14 passed.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`:
    pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`:
    pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`:
    pass; changed-file set is expected, with the `lib/backtest.py` protected
    path match authorized by this WP.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`:
    environment-only failure in
    `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`
    because the same gitignored local parquet file is absent; remaining suite
    result was 1353 passed, 1 failed, 6 warnings.
  - `git diff --check`: pass.
  - Direct forbidden-scope checks: no status or diff for
    `research/result_populations`, `lib/evaluation.py`,
    `tools/research_runner/run_offline_sweep.py`, `research/schemas`, or
    `tools/registry`.
- No-canonical-write proof: No result-population files are modified by the
  implementation or focused tests. Direct `git status --short
  research/result_populations` and `git diff -- research/result_populations`
  checks returned no output.
- Boundary summary: No `lib/evaluation.py`, runner, schema, validator,
  Strategy Spec, variant manifest, sweep plan, result population, data,
  candidate registry, dashboard implementation, runtime, paper/live, OMS/risk,
  broker/exchange, or protected path beyond the authorized `lib/backtest.py`
  implementation is changed.
- Merge status: PR #446 is open as a ready-for-review, non-draft PR. Final
  local rebase onto `origin/main` was a no-op, local final diff checks passed,
  and GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package does not authorize runner exposure,
  schema/validator sizing metadata, canonical reruns, candidate registration,
  or paper/live/runtime work. Main/Karl review is required after merge before
  any 02c/02d/canonical rerun package.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 7 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02b` on `backtest/realism-sizing-02b-dynamic-equity` at base `7f313fc` | satisfied |
| Verify PR #445 / 02a merged and source artifacts exist | WP section 6 | Base `origin/main` merge `7f313fc`; 02a design/status files inspected | satisfied |
| Modify only allowed implementation and focused test files | WP sections 9-10 | `lib/backtest.py`, `tests/test_backtest.py` | satisfied |
| Preserve fixed default behavior | WP sections 11-12, 18 | `tests/test_backtest.py::test_fixed_order_size_default_preserved_with_explicit_mode` | satisfied |
| Implement dynamic formula and bases | WP sections 13, 16 | `lib/backtest.py`; implementation note | satisfied |
| Add edge-case handling and tests | WP sections 14, 17 | `lib/backtest.py`; focused tests in `tests/test_backtest.py` | satisfied |
| Preserve cost/funding/liquidation model while using dynamic quantity | WP section 15 | `lib/backtest.py`; focused tests in `tests/test_backtest.py` | satisfied |
| Record sizing params in existing params snapshot | WP section 16 | `lib/backtest.py`; focused tests in `tests/test_backtest.py` | satisfied |
| Add implementation note | WP section 19 | `docs/research_pipeline/2026-06-dynamic_equity_sizing_impl_note.md` | satisfied |
| Add status fragment | WP section 20 | this file | satisfied |
| Update project status compactly | WP section 21 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 22 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation | WP section 23 | validation summary | satisfied |
| Complete authority/finality audit | WP section 24 | final report-back and PR body | satisfied |
| Prove no canonical result-population changes | WP sections 10, 23 | no-canonical-write proof and final git checks | satisfied |
