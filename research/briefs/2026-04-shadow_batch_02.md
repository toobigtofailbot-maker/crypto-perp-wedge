# Shadow Batch 02 Production Record

**Date:** 2026-04-22
**Package:** WP-7o
**Scope:** Second committed helper-produced overlay shadow batch over the diversified advisory state introduced by WP-7n.
**Does not introduce:** Helper redesign, schema changes, validator changes, query-layer changes, scheduler/trigger infrastructure, new advisory artifacts, new overlay-input fixtures, or diagnostic interpretation.
**Does not encode:** Policy inference, overlay influence, OMS influence, risk influence, runtime authority, or execution authority.

## 1. Purpose

This record documents the second committed post-WP-7k batch of helper-produced `overlay_shadow_log` artifacts. It records the helper inputs, the locked production rules, the represented combinations already present before the batch, the newly available distinct combinations discovered after WP-7n advisory-input diversification, and the exact commands used to create the new committed artifacts.

This file is a production record only. It is not a diagnostic brief and should not be interpreted as policy evidence or as a recommendation to change overlay behavior.

## 2. Locked Production Rules Applied

- Distinctness for batch selection is defined by advisory source, advisory artifact id, and helper-accepted overlay-input fixture pair.
- Timestamp differences do not create distinct combinations.
- Batch size is the full count of currently available distinct combinations not yet represented in committed `OSH-0001` through `OSH-0004`.
- The minimum floor remains `N >= 2`.
- If both source families are available, the batch must include at least one `BMAP` entry and one `PGAS` entry.
- The helper accepts only the canonical fixture pair:
  - `tests/fixtures/context_snapshot_sample.json`
  - `configs/fmp_macro_flags.json`
- Batch timestamps follow the stable drafting convention selected for WP-7o:
  - first selected entry: `2026-04-22T03:00:00Z`
  - second selected entry: `2026-04-22T04:00:00Z`

## 3. Represented Combinations Already Present Before The Batch

Committed `OSH-0001` through `OSH-0004` already represented these distinct combinations:

| Advisory source | Advisory artifact id | Snapshot path | Config path |
|---|---|---|---|
| `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |
| `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` |

The fixture set remained a single canonical pair only.

## 4. Newly Available Distinct Combinations Discovered At Phase 1

Current repo truth after WP-7n advisory-input diversification exposed these helper-accepted combinations not yet represented in committed `OSH-0001` through `OSH-0004`:

| Advisory source | Advisory artifact id | Snapshot path | Config path | Helper-accepted |
|---|---|---|---|---|
| `BMAP` | `BMAP-0002` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` | Yes |
| `PGAS` | `PGAS-0003` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` | Yes |

## 5. Selected Batch Size

Current repo truth exposed exactly 2 distinct helper-accepted combinations not yet represented in committed `OSH-0001` through `OSH-0004`, so the selected batch size resolved to `N = 2`.

The selected batch preserved source balance:

- one `BMAP` entry
- one `PGAS` entry

## 6. Helper Commands Used

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source BMAP --advisory-artifact-id BMAP-0002 --snapshot tests\fixtures\context_snapshot_sample.json --config configs\fmp_macro_flags.json --timestamp 2026-04-22T03:00:00Z --out research\overlay_shadow_logs\OSH-0005.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0005.overlay_shadow_log.json`

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source PGAS --advisory-artifact-id PGAS-0003 --snapshot tests\fixtures\context_snapshot_sample.json --config configs\fmp_macro_flags.json --timestamp 2026-04-22T04:00:00Z --out research\overlay_shadow_logs\OSH-0006.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0006.overlay_shadow_log.json`

## 7. Produced Batch Mapping

| OSH id | Advisory source | Advisory artifact id | Fixture pair | Timestamp |
|---|---|---|---|---|
| `OSH-0005` | `BMAP` | `BMAP-0002` | `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json` | `2026-04-22T03:00:00Z` |
| `OSH-0006` | `PGAS` | `PGAS-0003` | `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json` | `2026-04-22T04:00:00Z` |

## 8. Boundary Statement

Overlay-input fixture diversification remains deferred and is not part of this batch.

This production record documents committed artifact creation only. It does not diagnose agreement quality, does not infer policy from `MATCH` or `MISMATCH`, does not recommend overlay changes, does not recommend automated cadence or runtime integration, and encodes no policy inference.
