# D4 Validation-Report SHA Diagnostic

## Status / authority boundary

This is a read-only lineage diagnostic. It does not mutate catalogs, validation reports, data, result populations, code, schemas, validators, Strategy Specs, variant manifests, sweep plans, candidate registry, runtime, paper/live, or trading artifacts.

Package `WP-DATA-LINEAGE-DIAG-01` diagnoses the D4 validation-report SHA mismatch surfaced by `WP-REALISM-SIZING-02g`. It records evidence only and does not implement reconciliation.

## Observed mismatch

The committed D4 catalog slice records the D3 validation-report SHA as:

```text
785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c
```

The current committed validation-report file bytes hash to:

```text
51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46
```

The catalog path points to the same committed report path:

```text
research\data_slices\binance_usdtm_btcusdt_15m\binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json
```

## Files inspected

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`
- `docs/research_pipeline/2026-06-canonical_data_path_provenance_cleanup.md`
- `docs/status_entries/WP-REALISM-SIZING-02g.md`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.import_report.json`
- `research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json`
- `research/result_populations/RP-6688.result_population.json`
- `tools/data/import_binance_usdtm_15m.py`
- `tools/data/validate_binance_usdtm_15m.py`
- `tools/data/catalog_binance_usdtm_15m.py`
- `tools/registry/validate_result_populations.py`
- `tools/research_query/run.py`

## Catalog-recorded SHA

The catalog records `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c` in both:

- `validation_report.sha256`
- `slice_identity.identity_inputs.validation_report_sha256`

The catalog generator supports that this value was intended to be a byte hash. `tools/data/catalog_binance_usdtm_15m.py` hashes the validation report with `Path.read_bytes()` through `_hash_file(...)` before placing the value in the catalog and identity input.

The catalog and validation report were both introduced by commit `2d3a5e3` (`D4A: add real-data 15m catalog slice artifacts`) on `2026-06-06`.

## Committed-file SHA

The current committed validation-report file byte SHA is:

```text
51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46
```

The current Git blob for that file is `e6725eb38ebeb190915cc2e4219e57e27151d619`, and `git cat-file` over that blob also hashes to `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`.

Authoritative-SHA classification:

```text
authoritative = committed-file SHA 51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46 for the current committed validation-report bytes
```

The catalog-recorded `785a8d53...` remains the authoritative D4 catalog identity-input value for the existing catalog slice, but it does not describe the current committed validation-report file bytes.

## Git history / blob evidence

Read-only history checks found:

- `git log --oneline -- <catalog_slice_path>`: only `2d3a5e3 D4A: add real-data 15m catalog slice artifacts`.
- `git log --oneline -- <validation_report_path>`: only `2d3a5e3 D4A: add real-data 15m catalog slice artifacts`.
- `git log --oneline -- tools/data/catalog_binance_usdtm_15m.py`: `ba71e00 D4: Add Binance 15m data catalog and slice identity`.
- `git log --oneline -- research/result_populations/RP-6688.result_population.json`: `d8ced99 WP-SPEC-BOTHDIR-01c: run both-direction canonical sweep`.
- `git blame` for both the catalog and validation report attributes all lines to `2d3a5e3`.
- `git rev-list --all --objects` reports one historical blob for the validation-report path: `e6725eb38ebeb190915cc2e4219e57e27151d619`.
- Hashing that historical blob produces `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`.

No committed historical validation-report blob with byte SHA `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c` was found.

The `785a8d53...` value is exactly reproduced by converting the current committed LF validation-report bytes to CRLF line endings. Common JSON formatting variants did not reproduce the hash; the CRLF conversion did.

Relevant local Git newline facts:

- `.gitattributes` sets `*.json text eol=lf`.
- `git ls-files --eol` reports the validation report as `i/lf w/lf attr/text eol=lf` in the current checkout.
- Local Git config reports `core.autocrlf=true`, but `.gitattributes` currently forces LF for JSON in this checkout.

## Semantic validation-report content check

The committed validation report is semantically valid for the D4 slice facts. It records:

- `ok`: `true`
- validation status: `PASS`
- symbol: `BTCUSDT`
- stream: `ohlcv`
- timeframe: `15m`
- row count: `220128`
- expected row count: `220128`
- start: `2020-01-01T00:00:00Z`
- end: `2026-04-11T23:45:00Z`
- duplicate groups: `0`
- duplicate rows: `0`
- gap count: `0`
- missing bars: `0`
- normalized source SHA: `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab`

The exact 15-minute spacing conclusion is supported by the D3 validator behavior and the report facts together: the validator computes expected count from 15-minute cadence over sorted unique timestamps, records zero duplicate rows, records zero gaps, and records row count equal to expected row count over the stated range.

## D4 data and slice-identity status

The committed catalog `slice_identity.identity_inputs` recomputes to:

```text
3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

That matches the catalog-declared D4 slice identity:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

The mismatch concerns the validation-report byte link. It does not by itself change the observed D4 OHLCV content facts. `WP-REALISM-SIZING-02g` separately recorded that the materialized D4 normalized CSV had `220128` rows, the same range, no duplicates, zero gaps or missing bars, exact 15-minute spacing, and runner-consumed OHLCV equality against the 02e/02f fallback CSV.

## RP-6688 provenance impact

`RP-6688` cites the catalog-recorded D3 validation-report SHA in `data_coverage_summary.data_coverage_notes`:

```text
d3_validation_report_sha256=785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c
```

`RP-6688` also cites the D4 slice identity:

```text
binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

Every `RP-6688` result row inspected also carries that same data slice identity.

Therefore `RP-6688` carries a stale upstream validation-report file-byte reference relative to the current committed validation-report file bytes. Its D4 slice identity reference remains aligned with the committed catalog identity.

Search also found `RP-4492` carrying the same D3 validation-report SHA. This diagnostic did not mutate or reinterpret either result population.

## Root-cause assessment

Likely cause classification:

```text
validation-report file drifted after cataloging
validation-report generator is nondeterministic in bytes but semantically equivalent
```

Support:

- The D3 validation report and D4 catalog were added in the same commit.
- The catalog generator hashes validation-report working-tree bytes with `Path.read_bytes()`.
- The D3 validator writes JSON with `Path.write_text(json.dumps(...)+ "\n", encoding="utf-8")`, which is platform newline-sensitive in text mode.
- The catalog-recorded hash is exactly the current report content with CRLF line endings.
- The committed Git blob is LF-normalized and hashes to `51ceb94d...`.
- The committed semantic JSON content matches the catalog facts.
- No path mismatch was found; the catalog path points to the committed report path.
- No committed historical report blob with byte SHA `785a8d53...` was found.

Fact: `785a8d53...` is truthful for the CRLF byte form of the current report content.

Fact: `51ceb94d...` is truthful for the current committed LF validation-report file bytes.

Inference: the catalog was likely built from CRLF working-tree bytes before Git normalized the JSON file to LF in the committed blob, or from an equivalent CRLF copy of the report content. This is byte-level lineage drift, not observed semantic report drift.

## Reconciliation options

Option 1: restore validation-report file bytes to the catalog-recorded SHA `785a8d53...`.

- Later mutations: validation-report file bytes, and possibly `.gitattributes` or path-specific treatment if CRLF must be preserved in Git despite LF text rules.
- Retrospective/backfill implication: existing catalog, D4 slice identity, `RP-4492`, and `RP-6688` validation-report references would align with the file-byte hash after restoration.
- Identity-hash implication: D4 slice identity can remain unchanged if the catalog is not regenerated.
- Canonical dynamic-sizing write implication: can proceed only after a separately authorized package makes the link coherent and records the reconciliation.
- Risk: preserving CRLF JSON bytes conflicts with current LF normalization policy unless the future package explicitly handles it.

Option 2: update catalog/reference to committed-file SHA `51ceb94d...`.

- Later mutations: D4 catalog slice and any downstream references that cite the validation-report SHA; likely status/docs for affected result populations.
- Retrospective/backfill implication: `RP-4492` and `RP-6688` would carry stale upstream validation-report references unless backfilled or explicitly documented.
- Identity-hash implication: the D4 slice identity changes because `validation_report_sha256` is part of `slice_identity.identity_inputs`.
- Canonical dynamic-sizing write implication: can proceed only after downstream lineage expectations are updated or explicitly versioned.
- Risk: changing the catalog hash re-keys a D4 identity whose data content otherwise remains sound.

Option 3: regenerate D3/D4 lineage canonically and update downstream references under a gated reconciliation package.

- Later mutations: D3 validation report, D4 catalog slice, docs/status, and downstream references as authorized by that package.
- Retrospective/backfill implication: older result populations need explicit documentation preserving their original lineage while identifying any superseding lineage version.
- Identity-hash implication: identity may change if LF committed bytes become the canonical D3 report hash.
- Canonical dynamic-sizing write implication: can proceed after the regenerated lineage and downstream reference policy are settled.
- Risk: broader than required if the only observed issue is line-ending byte drift.

Option 4: preserve both via explicit lineage-version note if both are semantically equivalent but byte-different.

- Later mutations: documentation/status or a separately authorized lineage note; catalog mutation only if the future package chooses to embed the note in an artifact.
- Retrospective/backfill implication: old result populations can remain under their recorded D4 identity while the note explains the CRLF/LF byte distinction.
- Identity-hash implication: no identity change if limited to docs/status; identity changes if embedded in the catalog identity inputs.
- Canonical dynamic-sizing write implication: can proceed only if the future authority accepts explicit dual-byte lineage documentation as sufficient.
- Risk: preserves a byte mismatch rather than making the file link mechanically equal.

Evidence-supported direction: the evidence supports treating this as line-ending-only byte drift. A future reconciliation package should explicitly decide whether preserving the existing D4 identity is more important than aligning the catalog to the current committed LF file bytes. This diagnostic does not choose or implement that decision.

## Validation

Read-only diagnostic evidence collected:

- `git log --oneline -- <catalog_slice_path>`: pass; one commit found.
- `git log --oneline -- <validation_report_path>`: pass; one commit found.
- `git blame -- <catalog_slice_path>`: pass; all catalog lines attributed to `2d3a5e3`.
- `git blame -- <validation_report_path>`: pass; all report lines attributed to `2d3a5e3`.
- Historical validation-report blob hash scan: pass; no committed `785a8d53...` report blob found.
- Current file SHA computation: pass; validation report hashes to `51ceb94d...`.
- CRLF variant hash computation: pass; CRLF variant hashes to `785a8d53...`.
- Catalog identity-input recomputation: pass; recomputes to `3daace53...`.

Package validation command results are summarized in `docs/status_entries/WP-DATA-LINEAGE-DIAG-01.md`.

Summary:

- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- All discovered `v_integrity_*` views: pass; 55 views, zero rows.
- `git diff --check`: pass.
- `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
- Protected no-mutation checks for `research/data_slices`, `research/result_populations`, `tools`, `lib`, `tests`, `research/schemas`, and `data`: pass; no output.
- Full pytest: not run; package is docs/status diagnostic only and the active WP does not require full pytest for this docs-only diagnostic.

## No-mutation proof

This package does not mutate:

- `research/data_slices/*`
- `research/result_populations/*`
- `research/schemas/*`
- `tools/*`
- `lib/*`
- `tests/*`
- `data/*`
- `research/strategy_specs/*`
- `research/variant_manifests/*`
- `research/sweep_plans/*`
- `configs/*`
- `src/*`
- candidate registry files
- dashboard implementation files
- generated dashboard output
- runtime, paper/live, OMS/risk, broker/exchange, or protected paths

Final no-mutation command results are summarized in `docs/status_entries/WP-DATA-LINEAGE-DIAG-01.md`.

## Limitations

- The read-only search did not find a committed historical validation-report blob with byte SHA `785a8d53...`.
- The CRLF byte form was reproduced locally from the current committed JSON content; no separate committed CRLF artifact exists in Git history.
- This package does not inspect external/raw data or acquire data.
- This package does not repair the catalog, validation report, data slice, result populations, or runner behavior.

## Next authority

This package does not authorize catalog, validation-report, data, or RP mutation. Any reconciliation package requires separate authorization.

No result-population write, candidate registration, ranking, readiness, promotion, paper/live action, runtime action, or trading authority is authorized by this diagnostic.
