# Overlay Diversification Production Record 01

**Date:** 2026-04-24
**Package:** WP-7q
**Scope:** Additive overlay-input fixture diversification only.
**Does not introduce:** Shadow entries, code changes, schema changes, validator changes, query-layer changes, helper changes, runtime influence, or policy inference.
**Does not encode:** Diagnostic interpretation, overlay influence, OMS influence, risk influence, runtime authority, or execution authority.

## 1. Purpose

This production record documents the second committed overlay-input fixture set now consumable by the merged paired explicit-path helper surface introduced by WP-7q-prep.

This file is a production record only. It is not a diagnostic brief and should not be interpreted as policy evidence or as a recommendation to change overlay behavior.

## 2. Baseline And New Fixture Paths

Canonical baseline paths:

- `tests/fixtures/context_snapshot_sample.json`
- `configs/fmp_macro_flags.json`

New additive fixture paths:

- `tests/fixtures/context_snapshot_sample_02.json`
- `configs/fmp_macro_flags_02.json`

## 3. Fixture Shape And Variation Lock

The new context fixture preserves the exact current canonical field shape:

- `asof_timestamp_utc`
- `events`
- `snapshot_hash`

The new macro-flag config preserves the exact current canonical field shape:

- `event_types`
- `fail_open`
- `per_event_permission`
- `per_event_window_minutes`

Independent variation was locked as honest under the current merged observer semantics. Snapshot content and macro-flag config each produce truthful overlay-side behavioral differences at the same deterministic evaluation timestamp, so the enabled combinatorial space is 4 combinations rather than a coupled-pair-only fallback.

## 4. Field-Level Contrast Introduced

Context fixture contrasts relative to `tests/fixtures/context_snapshot_sample.json`:

- `asof_timestamp_utc`: `2025-01-01T00:00:00Z` -> `2025-01-14T00:00:00Z`
- `snapshot_hash`: `samplehash` -> `samplehash02`
- `events[1].event_type`: `FOMC` at `2025-01-15T19:00:00Z` -> `CPI` at `2025-01-15T19:00:00Z`
- `events[2].event_timestamp_utc`: `2025-01-12T13:30:00Z` -> `2025-01-20T19:00:00Z`
- `events[2].event_type`: `CPI` -> `FOMC`

Config fixture contrasts relative to `configs/fmp_macro_flags.json`:

- `per_event_permission.FOMC`: `BLOCK` -> `ALLOW`
- `per_event_window_minutes.CPI.post`: `60` -> `10`
- `fail_open`: unchanged at `true`
- `event_types`: unchanged at `["CPI", "FOMC", "NFP"]`
- `per_event_permission.CPI`: unchanged at `ALLOW_REDUCED`
- `per_event_permission.NFP`: unchanged at `ALLOW_REDUCED`
- `per_event_window_minutes.FOMC`: unchanged at `{ "pre": 30, "post": 150 }`
- `per_event_window_minutes.NFP`: unchanged at `{ "pre": 30, "post": 60 }`

## 5. Non-Mutating Smoke Checks

Deterministic evaluation timestamp:

- `2025-01-15T19:15:00Z`

Observer combinations run:

| Context fixture | Config fixture | Observed overlay bucket | Reason code | context_missing |
|---|---|---|---|---|
| `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags.json` | `BLOCK` | `ACTIVE_WINDOW_MATCH` | `false` |
| `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags.json` | `ALLOW_REDUCED` | `ACTIVE_WINDOW_MATCH` | `false` |
| `tests/fixtures/context_snapshot_sample.json` | `configs/fmp_macro_flags_02.json` | `ALLOW` | `ACTIVE_WINDOW_MATCH` | `false` |
| `tests/fixtures/context_snapshot_sample_02.json` | `configs/fmp_macro_flags_02.json` | `ALLOW` | `NO_ACTIVE_WINDOW` | `false` |

Unlocked truthful overlay-side contrast:

- the new context fixture changes the active window class at the same timestamp from canonical `FOMC -> BLOCK` to `CPI -> ALLOW_REDUCED` when paired with the canonical config
- the new config changes the canonical `FOMC -> BLOCK` outcome to `ALLOW` at the same timestamp when paired with the canonical context
- the new fixture pair removes the active window entirely at that same timestamp and yields `ALLOW` with `reason_code = NO_ACTIVE_WINDOW`

## 6. Helper Dry-Run Consumption Proof

Exact helper dry-run command used:

```powershell
.\.venv\Scripts\python.exe -m tools.shadow.shadow_run_helper --advisory-source BMAP --advisory-artifact-id BMAP-0002 --context-snapshot-path tests\fixtures\context_snapshot_sample_02.json --macro-flags-path configs\fmp_macro_flags_02.json --timestamp 2025-01-15T19:15:00Z
```

Result summary:

- exit code `0`
- `Overlay input mode: explicit`
- explicit repo-resident fixture paths were echoed
- dry-run succeeded without write
- validation note reported that corpus validation is skipped because the current schema and validator still lock `observation_source.snapshot_path` and `observation_source.config_path` to the canonical fixtures

## 7. Enabled Combinatorial Space

The committed overlay-input fixture family now exposes 4 honest combinations for later packages:

- canonical context x canonical config
- canonical context x new config
- new context x canonical config
- new context x new config

## 8. Boundary Statement

No shadow entries were added in this package.

No code, schema, validator, helper, or query-layer behavior was changed in this package.

Noncanonical write mode remains out of scope in this package.
