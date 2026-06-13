# WP-DATA-LINEAGE-FIX-01 - Validation-report byte reconciliation

- Package class: T2 lineage reconciliation, committed-lineage mutation, content-preserving.
- Branch: `fix/data-lineage-validation-report-crlf`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/453
- Gate: Karl authorization explicitly granted for `WP-DATA-LINEAGE-FIX-01 - validation-report byte reconciliation, Option 1`.
- Scope summary: Restores the BTCUSDT 15m D4 validation-report working-tree bytes to the catalog-attested CRLF byte form and adds a narrow path-specific line-ending pin.
- Authorization basis: Restore the D4 validation-report file to SHA256 `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`, add only the narrow `.gitattributes` pin, and update only authorized docs/status files.
- Restored file: `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json`.
- Prior file-byte SHA: `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`.
- Restored file-byte SHA: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- Catalog-attested SHA: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- Line-ending pin: `.gitattributes` path-specific exact-byte rule `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol`.
- Catalog identity verification: D4 catalog identity-input recomputes to `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`; catalog object unchanged.
- RP validation: `RP-2134`, `RP-4492`, and `RP-6688` validate through the committed result-population validator.
- RP-6688 citation status: `RP-6688` remains unchanged; its existing `d3_validation_report_sha256=785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c` citation now matches the restored validation-report file bytes.
- Validation summary: Required validation passed for SHA verification, catalog identity recomputation, committed result-population validation, query view listing, all discovered integrity views, diff-scope summary, whitespace checks, and forbidden-path no-mutation checks.
- Boundary / no-mutation proof: No D4 catalog object, result population, data content, code, schema, validator, test, Strategy Spec, variant manifest, sweep plan, candidate registry, dashboard implementation, runtime, paper/live, OMS/risk, broker/exchange, protected path, or canonical result population was changed or written.
- Merge status: PR #453 is open as a non-draft PR. Final rebase, validation rerun, and GitHub mergeability check completed cleanly before ready-for-review report-back.
- Next authority: This package does not authorize a canonical dynamic-sizing result population. Any canonical write requires separate authorization.

## Changed files

- `.gitattributes`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json`
- `docs/project_status.md`
- `docs/research_pipeline/2026-06-validation_report_crlf_reconciliation.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-DATA-LINEAGE-FIX-01.md`

## Validation detail

- Validation-report file byte SHA256: pass; `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`.
- Catalog identity-input recomputation: pass; `3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`.
- RP-6688 citation check: pass; citation equals restored validation-report SHA and `RP-6688` is unchanged.
- `python -m tools.registry.validate_result_populations`: pass; committed result-population artifacts validate.
- `python -m tools.research_query.run --list-views`: pass; query views listed successfully.
- All discovered `v_integrity_*` views: pass; zero rows returned.
- `python tools/dev/diff_scope_summary.py`: pass; changed-file scope limited to allowed files. The helper's broad `research/` pattern matched the exact validation-report artifact authorized by this package.
- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- Forbidden no-mutation checks: pass; no result-population, catalog-object, data-content, code, schema, validator, test, Strategy Spec, variant manifest, or sweep plan changes.
- Full pytest: not run; active package does not require full pytest when committed changes are limited to lineage artifact bytes, `.gitattributes`, and docs.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP section 6 | `C:\GitHub\crypto-perp-wedge-data-lineage-fix-01` on branch `fix/data-lineage-validation-report-crlf`, based on `origin/main` at `1adf88e` | satisfied |
| Verify `WP-DATA-LINEAGE-DIAG-01` merged and source artifacts exist | WP section 5 | Diagnostic note, status fragment, D4 catalog, validation report, and `RP-6688` inspected | satisfied |
| Restore validation-report bytes to `785a8d53...` | WP sections 4 and 10A | Restored file SHA verification | satisfied |
| Add narrow line-ending pin | WP section 10B | `.gitattributes` path-specific rule | satisfied |
| Preserve D4 catalog identity `3daace53...` | WP sections 10C and 11 | Catalog identity recomputation | satisfied |
| Do not mutate result populations | WP sections 9 and 11 | `git diff -- research/result_populations` has no output | satisfied |
| Validate committed result populations | WP sections 11 and 12 | Result-population validator output | satisfied |
| Run and clear integrity views | WP section 12 | Integrity-view validation output | satisfied |
| Limit diff scope to allowed files | WP sections 8, 9, and 12 | Diff-scope summary and changed-file checks | satisfied |
| Record reconciliation note and status | WP sections 13 and 14 | This status fragment and reconciliation note | satisfied |

## Authority/finality audit

- Authority terms in changed files are classified as line-ending reconciliation scope, integrity/provenance evidence, validation command/result, future canonical-write gate statement, non-authority caveat, forbidden-scope statement, source artifact/status identifier, limitation, or quoted audit terms.
- Placeholder scan terms `TBD`, `pending`, `to be added`, `background run`, `paste output`, `after PR number is known`, and `will confirm`: no unclassified hits in final package-authored text.
- No ranking, readiness, promotion, trading, paper/live, runtime, candidate, or canonical-write authority is introduced.
