# Validation-Report CRLF Reconciliation

## Status / authority boundary

This package performs a narrow content-preserving lineage reconciliation of one validation-report file's byte representation. It does not mutate catalogs, result populations, data content, code, schemas, validators, Strategy Specs, variant manifests, sweep plans, candidate registry, runtime, paper/live, or trading artifacts. It does not authorize a canonical result-population write.

## Prior diagnostic finding

`WP-DATA-LINEAGE-DIAG-01` found that the BTCUSDT 15m D4 catalog records validation-report SHA256 `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`, while the then-current committed validation-report working-tree bytes hashed to `51ceb94dc43c4e63f704bde86585f94bb800c2da21aa516f492d897a5bfc2a46`.

The diagnostic reproduced the catalog-recorded SHA by converting the same semantic validation report content from LF to CRLF. It found no path mismatch and no semantic validation-report mismatch.

## Reconciliation decision

Karl authorization selected Option 1: restore the validation-report file to its catalog-attested CRLF byte representation and pin that artifact path against future line-ending drift.

The D4 catalog object remains unchanged. The D4 slice identity remains unchanged.

## File restored

Restored file:

```text
research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json
```

The only content change in the validation-report artifact is LF-to-CRLF line-ending representation. JSON keys, values, order, timestamps, and validation facts are preserved.

## Line-ending pin

`.gitattributes` now includes a narrow path-specific exact-byte preservation rule after the broad `*.json text eol=lf` rule:

```text
research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.validation_report.json -text whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol
```

This scoped pin keeps the catalog-attested CRLF byte representation for this artifact path without changing the repository's general JSON LF policy.

## Post-change SHA verification

Target validation-report file byte SHA256:

```text
785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c
```

Post-change verification computed this exact SHA256 over the restored validation-report working-tree bytes.

## Catalog identity verification

The catalog identity-input object in:

```text
research/data_slices/binance_usdtm_btcusdt_15m/binance_usdtm_btcusdt_15m_20200101_20260411.catalog_slice.json
```

still recomputes to:

```text
3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664
```

The catalog file itself is unchanged.

## RP-6688 citation healing

`RP-6688` already cites:

```text
d3_validation_report_sha256=785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c
```

After restoring the validation-report bytes, that existing citation matches the restored file-byte SHA without mutating `RP-6688`.

`RP-2134`, `RP-4492`, and `RP-6688` remain unchanged.

## Validation

Package validation completed with:

- `python -m tools.registry.validate_result_populations`
- `python -m tools.research_query.run --list-views`
- all discovered `v_integrity_*` views
- `python tools/dev/diff_scope_summary.py`
- whitespace and changed-file checks
- forbidden-path no-mutation checks

All committed result populations validated, all integrity views returned zero rows, and diff scope stayed within the package.

## Boundary / no-mutation proof

This reconciliation did not modify:

- the D4 catalog object
- any result population
- data content
- `lib/`
- `tools/`
- `tests/`
- `research/schemas/`
- `data/`
- `research/strategy_specs/`
- `research/variant_manifests/`
- `research/sweep_plans/`
- `configs/`
- `src/`
- candidate registry files
- dashboard implementation files
- generated dashboard output
- runtime, paper/live, OMS/risk, broker/exchange, or protected paths

No canonical result population was written.

## Remaining limitations

This package reconciles only one validation-report byte link. It does not regenerate D3 or D4 artifacts, reinterpret any result population, alter strategy-quality evidence, or create downstream authority.

## Next authority

This package does not authorize a canonical dynamic-sizing result population. Any canonical write requires separate authorization.
