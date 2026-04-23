# Shadow Batch 01 Production Record

**Date:** 2026-04-22
**Package:** WP-7l
**Scope:** First committed helper-produced overlay shadow batch created through the manual shadow-run helper.
**Does not introduce:** Helper redesign, schema changes, validator changes, query-layer changes, scheduler/trigger infrastructure, new fixtures, or diagnostic interpretation.
**Does not encode:** Policy inference, overlay influence, OMS influence, risk influence, or runtime authority.

## 1. Purpose

This record documents the first committed post-WP-7k batch of helper-produced `overlay_shadow_log` artifacts. It records the helper inputs, the locked production rules, the discovered helper-accepted combination set, the selected batch size, and the exact commands used to create the new committed artifacts.

This file is a production record only. It is not a diagnostic brief and should not be interpreted as policy evidence or as a recommendation to change overlay behavior.

## 2. Locked Production Rules Applied

- Distinctness for batch selection is defined by advisory source, advisory artifact id, and helper-accepted overlay-input fixture pair.
- Timestamp differences do not create distinct combinations.
- Batch size is `min(4, available_count)` with a floor of 2.
- If both source families are available, the batch must include at least one `BMAP` entry and one `PGAS` entry.
- The helper accepts only the canonical fixture pair:
  - `tests/fixtures/context_snapshot_sample.json`
  - `configs/fmp_macro_flags.json`
- Batch timestamps follow the stable drafting convention selected for WP-7l:
  - first selected entry: `2026-04-22T00:00:00Z`
  - second selected entry: `2026-04-22T01:00:00Z`

## 3. Discovered Available Distinct Combinations

The current helper-accepted combination set at production time was:

| Advisory source | Advisory artifact id | Snapshot path | Config path | Helper-accepted |
|---|---|---|---|---|
| `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` | Yes |
| `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` | Yes |

The fixture set remained a single canonical pair only.

`PGAS-0001` was not part of the helper-accepted set for this batch because its `combined_bucket` is null under current repo truth, so it is not a valid helper input for committed PGAS-source shadow production.

## 4. Selected Batch Size

The locked batch target is 4 when enough distinct combinations exist. Current repo truth exposed only 2 distinct helper-accepted combinations, so the fallback rule reduced the committed batch size from 4 to 2.

The selected batch preserved source balance:

- one `BMAP` entry
- one `PGAS` entry

## 5. Helper Commands Used

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source BMAP --advisory-artifact-id BMAP-0001 --snapshot tests\fixtures\context_snapshot_sample.json --config configs\fmp_macro_flags.json --timestamp 2026-04-22T00:00:00Z --out research\overlay_shadow_logs\OSH-0003.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0003.overlay_shadow_log.json`

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source PGAS --advisory-artifact-id PGAS-0002 --snapshot tests\fixtures\context_snapshot_sample.json --config configs\fmp_macro_flags.json --timestamp 2026-04-22T01:00:00Z --out research\overlay_shadow_logs\OSH-0004.overlay_shadow_log.json --write
```

Result:
`Wrote validated overlay shadow log: research/overlay_shadow_logs/OSH-0004.overlay_shadow_log.json`

## 6. Produced Batch Mapping

| OSH id | Advisory source | Advisory artifact id | Fixture pair | Timestamp |
|---|---|---|---|---|
| `OSH-0003` | `BMAP` | `BMAP-0001` | `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json` | `2026-04-22T00:00:00Z` |
| `OSH-0004` | `PGAS` | `PGAS-0002` | `tests/fixtures/context_snapshot_sample.json` + `configs/fmp_macro_flags.json` | `2026-04-22T01:00:00Z` |

## 7. Boundary Statement

This production record documents committed artifact creation only. It does not diagnose agreement quality, does not infer policy from `MATCH` or `MISMATCH`, does not recommend overlay changes, and does not recommend automated cadence or runtime integration.
