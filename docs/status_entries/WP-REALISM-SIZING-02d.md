# WP-REALISM-SIZING-02d - Sizing metadata schema

- Package class: T3 schema/validator/result-metadata package.
- Branch: `schema/realism-sizing-02d-result-metadata`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/448
- Scope summary: Adds optional structured sizing metadata to the
  result-population schema and validator for future result populations, while
  preserving old-shape result populations without backfill.
- Authorization basis: Main authorized `WP-REALISM-SIZING-02d` after
  `WP-REALISM-SIZING-02c` exposed dynamic sizing to the offline runner, produced
  non-degenerate dry-run evidence, wrote no canonical result population, and
  observed sizing provenance inside existing identity-hash scope.
- Reasoning model: GPT-5.5 high; additive result-population schema/validator
  metadata with identity and reproducibility implications.
- Source runway: `WP-REALISM-SIZING-02b` implemented opt-in dynamic
  equity-relative sizing in `lib/backtest.py`; `WP-REALISM-SIZING-02c` exposed
  `sizing_mode` / `target_leverage` to the offline runner for build-test dry
  runs and recorded identity-hash scope observations.
- Schema summary: Adds optional top-level `sizing_metadata` with closed
  `sizing_mode` values `fixed_order_size` and
  `dynamic_equity_target_leverage`, basis fields for sizing equity and entry
  reference price, optional positive `target_leverage` for fixed mode, required
  positive `target_leverage` for dynamic mode, and optional positive
  `max_leverage_cap`.
- Validator behavior: Accepts old result populations with no
  `sizing_metadata`; validates structured metadata when present; rejects
  unknown modes, missing dynamic fields, unsupported basis strings,
  non-positive or non-finite leverage values, and missing identity-hash scope
  inclusion when structured sizing metadata is present.
- Identity-bearing posture: `sizing_metadata` is identity-bearing for future
  result populations that include it. Both `input_identity_hash.hash_scope` and
  `result_population_identity_hash.hash_scope` must include `sizing_metadata`
  when the object is present.
- Prior-RP compatibility: `RP-2134`, `RP-4492`, and `RP-6688` remain valid and
  immutable. Old result populations are not backfilled and remain valid under
  their recorded assumption text and pipeline version.
- Tests: Focused result-population validator tests cover committed-RP
  compatibility, old-shape fixture compatibility, accepted fixed/dynamic
  metadata, invalid modes, invalid leverage values, missing dynamic fields,
  invalid basis strings, optional max leverage cap behavior, identity-scope
  requirements, and identity-hash change behavior.
- Validation summary:
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_validate_result_populations.py -q`: pass, 53 tests.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`: pass; changed files are expected, with the advisory `research/schemas/result_population.schema.json` path match authorized by this WP.
  - `git diff --check` and `git diff --cached --check`: pass.
  - `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: environment-only failure in `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` because the isolated worktree lacks gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`; remaining suite result was 1370 passed, 1 failed, 6 warnings.
- No-canonical-write proof: No files under `research/result_populations/` are
  modified by this package.
- Boundary summary: No `lib/`, runner, Strategy Spec schema, Strategy Spec,
  variant manifest, sweep plan, result population, data, candidate registry,
  dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or
  protected path changes are included.
- Merge status: PR #448 is open as a ready-for-review, non-draft PR. Final local rebase onto `origin/main` was a no-op, local final diff checks passed, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package does not authorize a canonical dynamic-sizing
  rerun, result-population creation, runner/lib changes, candidate registration,
  or paper/live/runtime work. Main/Karl review is required before any canonical
  result-population write.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 8 | `C:\GitHub\crypto-perp-wedge-realism-sizing-02d` on `schema/realism-sizing-02d-result-metadata` from `origin/main` merge `0623540` | satisfied |
| Verify `WP-REALISM-SIZING-02c` merged and required artifacts exist | WP sections 4 and 7 | `origin/main` includes PR #447 merge and required 02c docs, runner exposure, and RP files | satisfied |
| Modify only allowed files | WP sections 10-11 | changed-file list and final scope checks | satisfied |
| Add optional structured sizing metadata schema fields | WP sections 12-13 | `research/schemas/result_population.schema.json` | satisfied |
| Treat structured sizing metadata as identity-bearing | WP section 14 | schema hash-scope enum and validator identity-scope enforcement | satisfied |
| Add focused validator behavior | WP section 15 | `tools/registry/validate_result_populations.py` | satisfied |
| Add required tests | WP section 16 | `tests/test_validate_result_populations.py` | satisfied |
| Document sizing metadata schema and pipeline-versioning posture | WP section 17 | `docs/research_pipeline/2026-06-sizing_metadata_schema_note.md` | satisfied |
| Add this status fragment | WP section 18 | this file | satisfied |
| Update project status compactly | WP section 19 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 20 | `docs/research_pipeline/README.md` | satisfied |
| Run required validation and final checks | WP section 21 | validation summary and final report-back | satisfied |
| Complete authority/finality text audit | WP section 22 | final report-back and PR body | satisfied |
| Push and open PR with required title | WP section 24 | PR #448 | satisfied |
