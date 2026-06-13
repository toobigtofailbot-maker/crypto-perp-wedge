# WP-REALISM-SIZING-02g - Canonical data-path provenance cleanup

- Package class: T3 data-path readiness, build-test/scratch, non-protected.
- Branch: `audit/realism-sizing-02g-data-path-provenance`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/451
- Scope summary: Materializes the documented D4A normalized CSV locally at the catalog-referenced gitignored path from existing local D4A source, compares it to the 02e/02f fallback, reruns STRAT-SPEC-0002 dynamic 1x through the canonical runner path in a temp scratch output directory, and records docs/status evidence only.
- Authorization basis: Main accepted `WP-REALISM-SIZING-02f` and authorized `WP-REALISM-SIZING-02g` to close the data-path provenance gap before any future Karl-gated canonical dynamic-sizing result-population write.
- Materialized CSV path: `C:\GitHub\crypto-perp-wedge-realism-sizing-02g\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv`.
- Materialization method: `tools.data.import_binance_usdtm_15m` over existing local D4A source CSV `C:\GitHub\crypto-perp-wedge-d4a\data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_source_from_repo_catalog_parquet.csv`; no external/raw data acquisition.
- Materialized CSV identity: raw CSV SHA256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`; row count `220128`; range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`; duplicate timestamp count `0`; gap/missing bar count `0`; exact 15m spacing yes; committed catalog identity-input recomputation equals D4 slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Fallback relationship: 02e/02f fallback CSV `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\btc_usdt_15m_full_d4_lineage_scratch.csv` has SHA256 `ec69b3a5ba3a00b0f2937c9c7b3aba04c4aaecd88762b699092c5b26656cc014`; bytes differ from the materialized normalized CSV, but runner-consumed timestamp/OHLCV content is equivalent over all `220128` rows.
- Canonical-path dry-run: Full STRAT-SPEC-0002 / VM-0002 / SWEEP-PLAN-0002 dynamic 1x run completed through `tools.research_runner.run_offline_sweep` using the materialized documented CSV plus committed D4 catalog slice and D2 import report; temp scratch artifact `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations\RP-7520.result_population.json`; no canonical output directory used.
- Runtime characterization: elapsed `01:23:43.6720158`; scratch artifact `RP-7520`; denominator `10`; rows `10`; outcome counts `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`.
- Data provenance: D4 catalog ref `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`; D4 slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; execution provenance class `canonical_real_data`.
- Sizing metadata: runner-emitted top-level `sizing_metadata` is `sizing_mode=dynamic_equity_target_leverage`, `target_leverage=1.0`, `sizing_equity_basis=realized_available_equity_at_entry`, and `entry_reference_price_basis=next_bar_open_pre_fee_slippage`; both input and result identity-hash scopes include `sizing_metadata`.
- Identity-hash comparison to 02f: input identity hash `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de`, exact 02f match; result population identity hash `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c`, exact 02f match.
- Per-variant comparison to 02f: all 10 variants match 02f within absolute `<= 1e-9` for floating metrics and exact equality for `trade_count`; detailed rows live in `docs/research_pipeline/2026-06-canonical_data_path_provenance_cleanup.md`.
- Non-degeneracy check: `return_pct == -1.0` count `0`; `max_drawdown == 1.0` count `0`; liquidation / zero-equity terminal flag count `0`; uniform liquidation artifact reproduced: NO.
- Validation summary: D2 materialization pass; D3 materialized CSV validation pass; committed D4 catalog identity-input recomputation pass; fallback runner-content comparison pass; full dynamic runner scratch run pass; scratch artifact validation pass; `python -m tools.registry.validate_result_populations` pass; `python -m tools.research_query.run --list-views` pass; all 55 discovered `v_integrity_*` views clean / zero rows; `python tools/dev/diff_scope_summary.py` pass with no forbidden-path matches; `git diff --check` pass. Full pytest not run because committed changes are docs-only and no code/schema/tool/test files changed.
- No-canonical-write proof: Scratch output was written only under `C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02g\result_populations`; `research/result_populations` has no status or diff after the scratch run.
- Boundary summary: Committed scope is docs only. No lib, runner, schema, validator, test, Strategy Spec, variant manifest, sweep plan, result population, committed data, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected path change is included.
- Merge status: PR #451 is open as a ready-for-review, non-draft PR. Final local rebase onto `origin/main` was a no-op, local final diff checks passed, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package does not authorize a canonical dynamic-sizing result population. Main review and Karl gate are required before any canonical write.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 6 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02g` on `audit/realism-sizing-02g-data-path-provenance` from PR #450 merge `23abbd5` | satisfied |
| Verify `WP-REALISM-SIZING-02f` merged and prior artifacts exist | WP section 5 | base commit is PR #450 merge; 02f docs/status, runner, parent artifacts, and `RP-6688` inspected | satisfied |
| Materialize documented normalized D4 CSV locally | WP sections 10-11 | audit note materialization and identity sections | satisfied |
| Prove relationship to 02e/02f fallback | WP section 11 | audit note fallback section | satisfied |
| Rerun full dynamic 1x canonical runner path over documented CSV | WP section 12 | audit note dry-run section; scratch artifact `RP-7520` | satisfied |
| Compare rows and hashes to 02f | WP sections 12-13 | audit note identity and per-variant sections | satisfied |
| Report non-degeneracy checks | WP section 14 | audit note non-degeneracy section | satisfied |
| Prove no canonical result-population write | WP section 15 | audit note no-canonical-write section and git checks | satisfied |
| Modify only expected docs | WP sections 8-9 | changed-file list | satisfied |
| Run required validation and final checks | WP section 20 | validation summary | satisfied |
| Complete authority/finality text audit | WP section 21 | final report-back and PR body | satisfied |
