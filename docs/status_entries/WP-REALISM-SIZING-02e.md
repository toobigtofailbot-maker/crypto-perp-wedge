# WP-REALISM-SIZING-02e — Dynamic sizing pre-rerun audit

- Package class: T3 readiness audit, scratch/read-only, non-protected.
- Branch: `audit/realism-sizing-02e-pre-rerun`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/449
- Scope summary: Produces scratch/read-only STRAT-SPEC-0002 dynamic 1x full-D4 population evidence, validates sizing metadata and identity-hash scope on a non-committed scratch artifact, and records docs/status evidence only.
- Authorization basis: Main/Karl accepted `WP-REALISM-SIZING-02d` and authorized `WP-REALISM-SIZING-02e` scratch/read-only pre-rerun audit evidence before any Karl-gated canonical dynamic-sizing result-population write.
- Reasoning model: GPT-5.5 high; scratch readiness audit before Karl-gated canonical write.
- Scratch run configuration: `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002`, `dynamic_equity_target_leverage`, `target_leverage=1.0`, deterministic seed `190`, D4 provenance mode, dry-run/no canonical write. Scratch result id `RP-0469`.
- Data provenance: D4 catalog ref `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`; slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; row count `220128`; range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`; provenance class `canonical_real_data`; D3 validation SHA256 `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- Sizing metadata: scratch artifact includes `sizing_mode=dynamic_equity_target_leverage`, `target_leverage=1.0`, `sizing_equity_basis=realized_available_equity_at_entry`, and `entry_reference_price_basis=next_bar_open_pre_fee_slippage`; no `max_leverage_cap` is present. Current runner exposes sizing controls but does not emit top-level `sizing_metadata`; this scratch audit populated the schema-supported block only in non-committed scratch output and recomputed hashes.
- Identity-hash proof: input identity hash `sha256:15438f68d38c925a80b6ed001be34b0d75707f17c1111aff62c0fcd90933ab3b`; result population identity hash `sha256:bc57f752fc969a4fc3f5e7b5c79ece8b682ea19257c64dbdeaac4bff2d03cf82`; both hash scopes include `sizing_metadata`; two repeated identity reconstructions from the scratch artifact produced the same hashes.
- Per-variant population summary: denominator `10`; actual rows `10`; outcome sum `10`; outcome counts `10 successful / 0 failed / 0 errored / 0 invalid / 0 excluded / 0 filtered / 0 data_unavailable / 0 not_attempted / 0 aborted`; all ten per-variant metrics are recorded in `docs/research_pipeline/2026-06-dynamic_sizing_prererun_audit.md`.
- Non-degeneracy check: `return_pct == -1.0` count `0`; `max_drawdown == 1.0` count `0`; liquidation / zero-equity terminal flag count `0`; uniform liquidation artifact reproduced: NO.
- Validation summary: Scratch artifact validation passed with `0` errors from `tools.registry.validate_result_populations.validate_result_populations(...)` and `python -m tools.registry.validate_result_populations --result-populations-dir C:\Users\dersu\AppData\Local\Temp\crypto_perp_wedge_02e\result_populations --strategy-specs-dir research\strategy_specs --variant-manifests-dir research\variant_manifests --sweep-plans-dir research\sweep_plans`; `python -m tools.registry.validate_result_populations` passed for committed RPs; `python -m tools.research_query.run --list-views` passed; all 55 discovered `v_integrity_*` views returned zero rows; `python tools/dev/diff_scope_summary.py` passed with expected docs-only scope and no forbidden-path matches; `git diff --check` passed; no result-population/code/schema/validator/test status or diff was present. Full pytest was not run because this package makes docs-only committed changes and the scratch exercise used existing runner/backtest paths without code edits; full pytest is not used as merge evidence.
- No-canonical-write proof: `git status --short research/result_populations`, `git diff -- research/result_populations`, `git status --short lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests`, and `git diff -- lib tools/research_runner/run_offline_sweep.py research/schemas tools/registry tests` returned no output before docs edits.
- Boundary summary: Committed scope is docs only. No lib, runner, schema, validator, test, Strategy Spec, variant manifest, sweep plan, data, result population, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected path is changed.
- Merge status: PR #449 is open for review; final rebase and GitHub mergeability gate are recorded in the PR body and final report-back.
- Next authority: This package does not authorize a canonical dynamic-sizing result population. Main/Karl review is required before any canonical write.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 7 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02e` on `audit/realism-sizing-02e-pre-rerun` from `origin/main` merge `da71fef` | satisfied |
| Verify `WP-REALISM-SIZING-02d` merged and required artifacts exist | WP section 6 | PR #448 merge is base commit; 02b/02c/02d docs, runner, schema, validator, parent artifacts, and `RP-6688` inspected | satisfied |
| Produce full D4 scratch population for all 10 STRAT-SPEC-0002 variants | WP sections 11-12 | `docs/research_pipeline/2026-06-dynamic_sizing_prererun_audit.md` per-variant table | satisfied |
| Preserve denominator and D4 provenance | WP sections 16-17 | scratch artifact `RP-0469`; audit note data provenance section | satisfied |
| Include and validate sizing metadata | WP sections 14-15 | scratch artifact top-level `sizing_metadata`; audit note sizing metadata and identity sections | satisfied |
| Prove non-degeneracy | WP section 13 | audit note non-degeneracy section | satisfied |
| Prove no canonical result-population write | WP sections 18 and 23 | no-canonical-write proof in audit note and final checks | satisfied |
| Modify only expected docs | WP sections 9-10 | final changed-file list | satisfied |
| Complete authority/finality text audit | WP section 24 | final report-back and PR body | satisfied |
