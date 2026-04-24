# Shadow Batch 03 Production Record

**Date:** 2026-04-24
**Package:** WP-7r
**Scope:** Third committed helper-produced overlay shadow batch over the currently write-valid noncanonical overlay-input frontier.
**Does not introduce:** Helper changes, schema changes, validator changes, query-layer changes, runtime contact, new fixtures, new advisory artifacts, or diagnostic interpretation.
**Does not encode:** Policy inference, overlay influence, OMS influence, risk influence, runtime authority, or execution authority.

## 1. Purpose

This record documents the first committed noncanonical-overlay-input shadow batch after WP-7q, WP-7r-prep, and WP-7r-helper aligned the helper write path and widened the shadow-log contract for explicit paired noncanonical overlay-input references.

This file is a batch-production record only. It is not a diagnostic brief and should not be interpreted as policy evidence or as a recommendation to change overlay behavior.

## 2. Phase-1 Represented Set Before The Batch

Committed `OSH-0001` through `OSH-0006` already represented these distinct combinations:

| Advisory source | Advisory artifact id | Snapshot path | Config path |
|---|---|---|---|
| `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |
| `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |
| `BMAP` | `BMAP-0002` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |
| `PGAS` | `PGAS-0003` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |

## 3. Phase-1 Write-Valid Unrepresented Set

Under current merged repo truth, the commit-valid overlay-input identities were:

- canonical pair:
  - `tests/fixtures/context_snapshot_sample.json`
  - `configs/fmp_macro_flags.json`
- explicit noncanonical pair:
  - `tests/fixtures/context_snapshot_sample_02.json`
  - `configs/fmp_macro_flags_02.json`

Mixed canonical/noncanonical combinations remained helper-observable but were not commit-valid because the current schema and validator require paired overlay-input references to move together.

The write-valid unrepresented set therefore resolved exactly to:

| Advisory source | Advisory artifact id | Snapshot path | Config path | Write-valid |
|---|---|---|---|---|
| `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags_02.json` | Yes |
| `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags_02.json` | Yes |
| `BMAP` | `BMAP-0002` | `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags_02.json` | Yes |
| `PGAS` | `PGAS-0003` | `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags_02.json` | Yes |

The exact computed batch size was `N = 4`.

## 4. Helper Commands Used

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source BMAP --advisory-artifact-id BMAP-0001 --context-snapshot-path tests\fixtures\context_snapshot_sample_02.json --macro-flags-path configs\fmp_macro_flags_02.json --timestamp 2026-04-22T05:00:00Z --out research\overlay_shadow_logs\OSH-0007.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0007.overlay_shadow_log.json`

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source PGAS --advisory-artifact-id PGAS-0002 --context-snapshot-path tests\fixtures\context_snapshot_sample_02.json --macro-flags-path configs\fmp_macro_flags_02.json --timestamp 2026-04-22T06:00:00Z --out research\overlay_shadow_logs\OSH-0008.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0008.overlay_shadow_log.json`

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source BMAP --advisory-artifact-id BMAP-0002 --context-snapshot-path tests\fixtures\context_snapshot_sample_02.json --macro-flags-path configs\fmp_macro_flags_02.json --timestamp 2026-04-22T07:00:00Z --out research\overlay_shadow_logs\OSH-0009.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0009.overlay_shadow_log.json`

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source PGAS --advisory-artifact-id PGAS-0003 --context-snapshot-path tests\fixtures\context_snapshot_sample_02.json --macro-flags-path configs\fmp_macro_flags_02.json --timestamp 2026-04-22T08:00:00Z --out research\overlay_shadow_logs\OSH-0010.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0010.overlay_shadow_log.json`

## 5. Produced Batch Mapping

| OSH id | Advisory source | Advisory artifact id | Fixture pair | Timestamp |
|---|---|---|---|---|
| `OSH-0007` | `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json` | `2026-04-22T05:00:00Z` |
| `OSH-0008` | `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json` | `2026-04-22T06:00:00Z` |
| `OSH-0009` | `BMAP` | `BMAP-0002` | `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json` | `2026-04-22T07:00:00Z` |
| `OSH-0010` | `PGAS` | `PGAS-0003` | `tests/fixtures/context_snapshot_sample_02.json` + `configs/fmp_macro_flags_02.json` | `2026-04-22T08:00:00Z` |

Advisory-source coverage obtained:

- `BMAP`: `OSH-0007`, `OSH-0009`
- `PGAS`: `OSH-0008`, `OSH-0010`

Overlay-input fixture identities used for every committed row:

- `tests/fixtures/context_snapshot_sample_02.json`
- `configs/fmp_macro_flags_02.json`

## 6. Boundary Statement

This is the first committed noncanonical-overlay-input shadow batch.

No helper, schema, validator, query-layer, or runtime behavior changed in this package.

Diagnostic interpretation is deferred to the next brief package.
