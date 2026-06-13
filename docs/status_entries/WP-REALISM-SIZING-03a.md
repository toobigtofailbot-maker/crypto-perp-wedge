# WP-REALISM-SIZING-03a — Canonical dynamic-sizing result population

- Package class: T3 canonical result-population write, Karl-gated, append-only evidence.
- Branch: `evidence/realism-sizing-03a-dynamic-rp`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/454
- Gate: Karl authorization explicitly granted for `WP-REALISM-SIZING-03a` canonical dynamic-sizing result-population write.
- Scope summary: Creates append-only canonical result population `RP-7520` for `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` using `dynamic_equity_target_leverage` at `target_leverage=1.0` over the cleaned BTCUSDT 15m D4 lineage, and updates only authorized docs/status files.
- Authorization basis: `Karl authorizes WP-REALISM-SIZING-03a canonical dynamic-sizing result-population write.`
- Result population: `research/result_populations/RP-7520.result_population.json`, generated through `tools.research_runner.run_offline_sweep` into temp output then copied to the append-only committed path. Git stages the JSON under the repo LF normalization policy.
- Input identity hash: `sha256:761f4af20320a244b0ff966eca17f3cc3a47bc79a5672cf2b40ee183ab9c05de`.
- Result population identity hash: `sha256:698f02c6239a5d2221ababeab62850403f71d9cf6f36279b3b8dcdc05fa7403c`.
- Data lineage: D4 catalog ref `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`; D4 slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; normalized CSV SHA256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- Validation-report SHA: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- Sizing metadata: `sizing_mode=dynamic_equity_target_leverage`, `target_leverage=1.0`, `sizing_equity_basis=realized_available_equity_at_entry`, `entry_reference_price_basis=next_bar_open_pre_fee_slippage`; `sizing_metadata` appears in both identity-hash scopes.
- Denominator / outcome counts: committed denominator `10`; actual rows `10`; outcome count sum `10`; `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`.
- Per-variant comparison: all ten rows match the 02f/02g scratch references within absolute `<= 1e-9` for floating metrics and exact equality for `trade_count`; detailed table lives in `docs/research_pipeline/2026-06-canonical_dynamic_sizing_result_population.md`.
- Non-degeneracy check: `return_pct == -1.0` count `0`; `max_drawdown == 1.0` count `0`; liquidation / zero-equity terminal flag count `0`; uniform liquidation artifact reproduced: NO.
- Validation summary: runner completed with `ok=true`, `aborted=false`, `wrote=true`, `result_population_id=RP-7520`; temp artifact validation passed; committed result-population validation passed; focused identity/content checks passed; `python -m tools.research_query.run --list-views` passed with `118` views; all `55` discovered `v_integrity_*` views returned zero rows.
- Boundary / append-only proof: `RP-7520` is new; `RP-2134`, `RP-4492`, and `RP-6688` are unchanged; no D4 catalog, validation-report, data-content, Strategy Spec, variant manifest, sweep plan, code, schema, validator, test, candidate registry, dashboard implementation, generated dashboard output, runtime, paper/live, OMS/risk, broker/exchange, or protected-path mutation is included.
- Merge status: PR #454 is open as a ready-for-review, non-draft PR from refreshed `origin/main` commit `ad0161be448f8df434cd945fc05331562ae86340`; final rebase and GitHub mergeability check are recorded in the final report-back.
- Next authority: This package does not authorize candidate registration, ranking, readiness, promotion, paper/live, runtime, or trading behavior.

## Changed files

- `research/result_populations/RP-7520.result_population.json`
- `docs/project_status.md`
- `docs/research_pipeline/2026-06-canonical_dynamic_sizing_result_population.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-REALISM-SIZING-03a.md`

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 6 | `C:\GitHub\crypto-perp-wedge-realism-sizing-03a` on branch `evidence/realism-sizing-03a-dynamic-rp`, based on `ad0161b` | satisfied |
| Verify `WP-DATA-LINEAGE-FIX-01` merged | WP section 5 | Base commit is PR #453 merge `ad0161b`; FIX-01 docs/status inspected | satisfied |
| Confirm validation-report SHA `785a8d53...` | WP sections 5 and 11 | File SHA check and catalog note | satisfied |
| Confirm D4 identity `3daace53...` | WP sections 5 and 11 | Catalog identity-input recomputation | satisfied |
| Create `RP-7520` through canonical runner path | WP section 10 | Runner stdout and committed artifact path | satisfied |
| Match required identity hashes | WP sections 4 and 10 | Focused identity/content check and artifact fields | satisfied |
| Preserve denominator and all outcome counts | WP section 11 | Focused identity/content check and artifact fields | satisfied |
| Match all variant rows within tolerance | WP section 12 | Focused identity/content check and research note table | satisfied |
| Report non-degeneracy checks | WP section 13 | Research note and status fragment | satisfied |
| Commit only expected files | WP sections 8 and 18 | Changed-file list and final diff-scope checks | satisfied |
| Avoid authority drift | WP sections 14, 19, and 24 | Authority/finality audit | satisfied |

## Validation detail

- D4 validation-report file SHA256: pass; `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- D4 catalog identity-input recomputation: pass; `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- Local D4A CSV materialization from existing source: pass; normalized SHA256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`, row count `220128`, no gaps, no duplicates.
- Full dynamic 1x canonical-runner-path run: pass; retained runner output wrote temp `RP-7520.result_population.json` with `ok=true`, `aborted=false`, `wrote=true`. An earlier duplicate launch was stopped before producing an artifact and is not used as evidence.
- Temp artifact validation: pass with `python -m tools.registry.validate_result_populations --result-populations-dir C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_03a\result_populations --strategy-specs-dir research\strategy_specs --variant-manifests-dir research\variant_manifests --sweep-plans-dir research\sweep_plans`.
- Artifact byte check: pass; runner temp and working-tree `RP-7520` copies initially matched at SHA256 `382f3b609204cb7a263fc40cc4cbaed511a834fea8c2d752cba4e3a45fc2e1c5`; staged/committed JSON bytes after repo LF normalization hash to `1df066eeb15957bb0a0825b180bcded8ee971a6e9834a30fe93ac7b70810bd36`.
- Focused identity/content check: pass; ID, parent refs, denominator, row count, outcome counts, required hashes, sizing metadata scopes, D4/D3 lineage, per-variant tolerance, and non-degeneracy counts all match.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass; `118` views listed.
- All discovered `v_integrity_*` views: pass; `55` views returned zero rows.
- `python tools/dev/diff_scope_summary.py`: pass; the helper reported the expected broad `research/` match for the authorized new `research/result_populations/RP-7520.result_population.json`.
- `git diff --check`: pass.
- Forbidden no-mutation checks: pass; no prior result population, data slice, Strategy Spec, variant manifest, sweep plan, code, schema, validator, test, data-content, or protected-path diff.

## Authority/finality audit

- `canonical`, `result population`, `write`: classified as canonical evidence scope or result-population identity.
- `rank`, `ranking`, `winner`, `selected`: classified as non-authority caveat, denominator/governance metadata, or forbidden-scope statement; no variant ordering is used as a preference claim.
- `candidate`, `registry`, `readiness`, `promote`, `promotion`, `paper`, `live`, `runtime`, `trading`: classified as non-authority caveat or forbidden-scope statement.
- `edge`, `profitable`, `profitability`: classified as interpretation boundary / limitation.
- `approved`, `approval`, `recommend`, `recommendation`, `execute`: classified as non-authority flags, validator boundary, validation command/result, or source artifact/status identifier.
- `validated`: classified as validation command/result or source artifact/status identifier.
- `NO-GO`: no package-authored hits.
- Placeholder scan terms `TBD`, `pending`, `to be added`, `background run`, `paste output`, `after PR number is known`, and `will confirm`: no package-authored hits.
- No authority drift requiring rewording was found.
