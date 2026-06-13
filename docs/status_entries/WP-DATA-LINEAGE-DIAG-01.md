# WP-DATA-LINEAGE-DIAG-01 - D4 validation-report SHA mismatch diagnostic

- Package class: T2 read-only data-lineage diagnostic.
- Branch: `diag/data-lineage-d4-validation-report-sha`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/452
- Scope summary: Diagnoses the D4 BTCUSDT 15m validation-report SHA mismatch surfaced by `WP-REALISM-SIZING-02g`; records evidence in docs/status only; implements no reconciliation.
- Authorization basis: Main authorized `WP-DATA-LINEAGE-DIAG-01` to determine which D3 validation-report SHA is authoritative, diagnose divergence, confirm D4 data and RP-6688 provenance impact, and surface reconciliation options with no mutation.
- Observed mismatch: D4 catalog records `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`; current committed validation-report file bytes hash to `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`.
- Catalog-recorded SHA: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`; present in `validation_report.sha256` and `slice_identity.identity_inputs.validation_report_sha256`.
- Committed-file SHA: `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`; current Git blob `e6725eb38ebeb190915cc2e4219e57e27151d619` hashes to this value.
- Authoritative-SHA finding: `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46` is authoritative for the current committed validation-report file bytes. `785a8d53...` remains the existing D4 catalog identity-input value and exactly matches the CRLF byte form of the same semantic report content.
- Root-cause finding: likely line-ending byte drift. The D3 validator writes text JSON, the D4 catalog hashes working-tree report bytes, and the catalog-recorded hash is exactly reproduced by CRLF-converting the current LF report. No path mismatch or semantic report mismatch was found; no committed historical `785a8d53...` validation-report blob was found.
- Semantic validation-report finding: committed report records `ok=true`, `PASS`, `BTCUSDT`, `ohlcv`, `15m`, row count `220128`, expected row count `220128`, range `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`, duplicate rows `0`, gap count `0`, missing bars `0`, and normalized source SHA `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`.
- D4 data / slice-identity finding: committed catalog `slice_identity.identity_inputs` recomputes to `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; mismatch concerns the validation-report byte link, not observed D4 OHLCV content under the evidence recorded by 02g.
- RP-6688 provenance impact: `RP-6688` cites `d3_validation_report_sha256=785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c` and D4 slice identity `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; it therefore carries a stale upstream validation-report file-byte reference relative to current committed report bytes while retaining the D4 slice identity used by the catalog.
- Reconciliation options: Option 1 restore validation-report bytes to `785a8d53...`; Option 2 update catalog/reference to `51ceb94d...`; Option 3 regenerate D3/D4 lineage under a gated reconciliation package; Option 4 preserve both with an explicit lineage-version note if accepted by future authority. Each option requires separate authorization.
- Validation summary: Local diagnostic checks passed for SHA computation, catalog extraction, CRLF reproduction, catalog identity-input recomputation, git log/blame, historical blob search, result-population validation, query view listing, all 55 integrity views, diff-scope summary, whitespace diff check, and protected no-mutation checks.
- No-mutation proof: No D4 catalog, D3 validation report, data file, result population, tool, schema, validator, test, Strategy Spec, variant manifest, sweep plan, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, or protected-path mutation is authorized or included.
- Boundary summary: Docs/status only. No catalog mutation, validation-report mutation, data mutation, RP mutation, code edit, schema/validator edit, external/raw data acquisition, candidate registration, ranking, readiness, promotion, paper/live/runtime action, or trading authority.
- Merge status: PR #452 is open as a non-draft PR. Final local rebase onto `origin/main` was a no-op, required validation reran cleanly, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: This package does not authorize catalog, validation-report, data, or RP mutation. Any reconciliation package requires separate authorization.

## Changed files

- `docs/project_status.md`
- `docs/research_pipeline/2026-06-d4_validation_report_sha_diagnostic.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-DATA-LINEAGE-DIAG-01.md`

## Validation detail

- `python -m tools.registry.validate_result_populations`: pass; committed result-population artifacts validate.
- `python -m tools.research_query.run --list-views`: pass; query views listed successfully.
- All discovered `v_integrity_*` views: pass; 55 views run, zero rows returned.
- `git diff --check`: pass.
- `python tools/dev/diff_scope_summary.py`: pass; tracked changed files were `docs/project_status.md` and `docs/research_pipeline/README.md`, untracked allowed files were this status fragment and the diagnostic note, forbidden-path matches none.
- `git status --short research/data_slices` plus `git diff -- research/data_slices`: pass; no output.
- `git status --short research/result_populations` plus `git diff -- research/result_populations`: pass; no output.
- `git status --short tools lib tests research/schemas data` plus `git diff -- tools lib tests research/schemas data`: pass; no output.
- Final rebase / GitHub mergeability gate: pass; `git rebase origin/main` reported branch up to date, final `git status --short` had no output, final `git diff --check` passed, final `git diff --cached --check` passed with no staged files, PR title begins with `WP-DATA-LINEAGE-DIAG-01:`, GitHub reports `isDraft=false`, and GitHub reports `mergeable=MERGEABLE`.
- Full pytest: not run; package is docs/status diagnostic only and the active WP does not require full pytest for this docs-only diagnostic.

## Authority/finality audit

- Changed-line audit terms in `docs/project_status.md` and `docs/research_pipeline/README.md`: classified as data-lineage diagnostic scope, non-authority caveat, forbidden-scope statement, or source artifact/status identifier.
- New diagnostic/status audit terms: classified as data-lineage diagnostic scope, observed mismatch, evidence statement, reconciliation option, non-authority caveat, forbidden-scope statement, validation command/result, source artifact/status identifier, limitation, or next-authority statement.
- PR body audit terms: classified as data-lineage diagnostic scope, observed mismatch, evidence statement, reconciliation option, non-authority caveat, forbidden-scope statement, validation command/result, source artifact/status identifier, or PR status.
- Placeholder scan terms `TBD`, `pending`, `to be added`, `background run`, `paste output`, `after PR number is known`, and `will confirm`: no hits in added diff lines or new package files.
- PR body placeholder scan: no GitHub template placeholders, unchecked boxes, or stale placeholder text.
- No drift requiring rewording was found in the package-authored text.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 6 | `C:\GitHub\crypto-perp-wedge-data-lineage-diag-01` on branch `diag/data-lineage-d4-validation-report-sha`, based on `origin/main` at `75d3b9a` | satisfied |
| Verify 02g merged and required artifacts exist | WP section 5 | Base commit `75d3b9a`; inspected 02g docs/status, D4 catalog/import/validation report, and `RP-6688` | satisfied |
| Compute current file SHA and extract catalog SHA | WP sections 10-11 | Diagnostic note sections `Catalog-recorded SHA` and `Committed-file SHA` | satisfied |
| Inspect git history and historical blobs | WP section 11 | Diagnostic note section `Git history / blob evidence` | satisfied |
| Check semantic validation-report content | WP section 10C | Diagnostic note section `Semantic validation-report content check` | satisfied |
| Recompute D4 slice identity | WP section 10D | Diagnostic note section `D4 data and slice-identity status` | satisfied |
| Inspect RP-6688 provenance | WP section 10E | Diagnostic note section `RP-6688 provenance impact` | satisfied |
| Present reconciliation options without mutation | WP section 10F | Diagnostic note section `Reconciliation options` | satisfied |
| Modify only expected docs | WP sections 8-9 | Changed files section and final diff scope | satisfied |
| Run required validators and final checks | WP section 12 | Validation detail section | satisfied |
