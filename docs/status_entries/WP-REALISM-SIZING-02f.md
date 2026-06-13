# WP-REALISM-SIZING-02f - Canonical dynamic sizing runner readiness

- Package class: T3 runner readiness, build-test/scratch only, non-protected.
- Branch: `runner/realism-sizing-02f-canonical-readiness`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/450
- Scope summary: Makes the offline runner emit top-level dynamic `sizing_metadata` directly, includes it in both runner-produced identity-hash scopes, preserves fixed/default runner output shape without top-level `sizing_metadata`, and records full-D4 STRAT-SPEC-0002 dynamic 1x scratch evidence through the canonical runner path.
- Authorization basis: Main accepted `WP-REALISM-SIZING-02e` and authorized `WP-REALISM-SIZING-02f` as canonical-runner readiness for dynamic sizing evidence with no canonical result-population write.
- Runner change: `tools/research_runner/run_offline_sweep.py` now derives structured top-level `sizing_metadata` for `dynamic_equity_target_leverage`, emits it before identity hashing, and adds `sizing_metadata` to both `input_identity_hash.hash_scope` and `result_population_identity_hash.hash_scope` only when dynamic sizing metadata is present.
- Default/fixed preservation: Default and explicit `fixed_order_size` outputs do not emit top-level `sizing_metadata` and do not include `sizing_metadata` in either identity-hash scope. Existing fixed-mode order-size resolution and backtest argument pass-through remain covered by focused tests.
- Full-D4 dry-run configuration: `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002`, `dynamic_equity_target_leverage`, `target_leverage=1.0`, deterministic seed `190`, D4 catalog/import provenance mode, scratch output under `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations`, artifact `RP-7520.result_population.json`, no canonical output directory.
- Runtime characterization: Full canonical-runner-path scratch run completed successfully in `01:22:51.1896865`; runner stdout reported `ok=true`, `aborted=false`, `wrote=true`, `output_path=C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations\RP-7520.result_population.json`; stderr was empty.
- Data provenance: The catalog-referenced normalized CSV path was not locally present, so the run used the existing 02e full-D4 scratch CSV fallback `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv` with SHA256 `ec69b3a5ba3a00b0f2937c9c7b3aba04c4aaecd88762b699092c5b26656cc014`; the runner-generated artifact records D4 catalog ref `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`, D4 slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`, row count `220128`, range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`, D3 validation SHA256 `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`, and `execution_provenance_class=canonical_real_data`.
- Sizing metadata: Runner-generated top-level `sizing_metadata` is `sizing_mode=dynamic_equity_target_leverage`, `target_leverage=1.0`, `sizing_equity_basis=realized_available_equity_at_entry`, and `entry_reference_price_basis=next_bar_open_pre_fee_slippage`; no `max_leverage_cap` is present.
- Identity-hash proof: Runner-generated input identity hash `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de`; runner-generated result population identity hash `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c`; both hash scopes include `sizing_metadata`. Focused tests prove dynamic target-leverage changes alter both identity hash values and repeated identical dynamic runs keep identical identity hashes and rows.
- Per-variant population summary: Denominator `10`; actual variant rows `10`; outcome count sum `10`; outcome counts `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`. All ten per-variant rows are recorded in `docs/research_pipeline/2026-06-canonical_dynamic_sizing_runner_readiness.md`.
- Comparison to 02e: Absolute tolerance `<= 1e-9` for floating metrics and exact equality for trade counts; all 10 canonical-path runner rows match the 02e scratch reference within tolerance; mismatch table is empty.
- Non-degeneracy check: `return_pct == -1.0` count `0`; `max_drawdown == 1.0` count `0`; liquidation / zero-equity terminal flag count `0`; uniform liquidation artifact reproduced: NO.
- Validation summary:
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`: pass, `73 passed`, 2 existing timestamp parsing warnings.
  - Full-D4 runner command: pass, artifact `RP-7520.result_population.json`, elapsed `01:22:51.1896865`.
  - Scratch artifact validation with `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations --result-populations-dir C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations --strategy-specs-dir research\strategy_specs --variant-manifests-dir research\variant_manifests --sweep-plans-dir research\sweep_plans`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches at the time run.
  - `git diff --check`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: environment-only failure in `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` because the isolated worktree lacks gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`; remaining suite result was `1375 passed, 1 failed, 6 warnings`.
- No-canonical-write proof: The full-D4 scratch artifact was written only under `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02f\result_populations`. Final git checks showed no status or diff under `research/result_populations`.
- Boundary summary: No `lib/`, `research/schemas/`, `tools/registry/`, Strategy Spec, variant manifest, sweep plan, result population, data, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected-path changes are included.
- Merge status: PR #450 is open as a ready-for-review, non-draft PR. Final local rebase onto `origin/main` was a no-op, local final diff checks passed, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package does not authorize a canonical dynamic-sizing result population. Main review and Karl gate are required before any canonical write.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 6 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02f` on `runner/realism-sizing-02f-canonical-readiness` from PR #449 merge `2c7b6df` | satisfied |
| Verify 02e merged and required prior artifacts exist | WP section 5 | Base commit is PR #449 merge; required 02b/02c/02d/02e docs, runner, schema/validator support, parent artifacts, and `RP-6688` inspected | satisfied |
| Modify only allowed files | WP sections 8-9 | final changed-file list and scope checks | satisfied |
| Emit top-level dynamic `sizing_metadata` directly from runner | WP sections 10 and 16 | `tools/research_runner/run_offline_sweep.py`; focused tests; scratch artifact `RP-7520` | satisfied |
| Include `sizing_metadata` in both identity scopes | WP sections 10 and 15 | scratch artifact identity-hash scopes; focused hash tests | satisfied |
| Preserve default/fixed behavior | WP sections 10 and 16 | fixed/default focused tests | satisfied |
| Complete full-D4 canonical-runner-path scratch run | WP section 11 | implementation note and status runtime evidence | satisfied |
| Compare all 10 rows to 02e scratch within tolerance | WP section 12 | implementation note comparison table | satisfied |
| Report per-variant table without ranking | WP section 13 | implementation note per-variant canonical-path population section | satisfied |
| Report non-degeneracy checks | WP section 14 | implementation note and status non-degeneracy sections | satisfied |
| Record identity/provenance proof | WP section 15 | implementation note data provenance and identity-hash sections | satisfied |
| Run required validation | WP section 21 | validation summary | satisfied with one environment-only full-pytest failure |
| Prove no canonical result-population write | WP sections 10, 15, and 21 | scratch output path plus final git checks | satisfied |
| Complete authority/finality semantic text audit | WP section 22 | final report-back and PR body | satisfied |
