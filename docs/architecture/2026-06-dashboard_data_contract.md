# Dashboard Data Contract

## Purpose

`dashboard_data.v1` is the first read-only data contract for future local static dashboard renderers. It is a validated mirror of repo facts only. The renderer must consume this contract as input and must not invent facts, reshape evidence, rank variants, hide stale state, or create execution controls.

This contract is defined by:

- JSON Schema: `research/schemas/dashboard_data.schema.json`
- Validator: `python -m tools.dashboard.validate_dashboard_data <path>`
- Minimal fixtures: `tests/fixtures/dashboard/`

## Scope

The MVP contract covers three page sections:

- `overview`
- `data_provenance`
- `gates`

No renderer, HTML generator, CSS, JavaScript UI, server, generated dashboard output, or runtime contact is included.

## Required Top-Level Fields

- `schema_version`: constant `dashboard_data.v1`
- `generated_at_utc`: UTC generation timestamp
- `source_commit`: source repo commit
- `source_branch`: source repo branch
- `dirty_state`: `clean`, `dirty`, or `unknown`
- `system_posture`: `research_only`, `paper_disabled`, `paper_sandbox_only`, `live_disabled`, or `unknown`
- `non_authority_declaration`: required true flags
- `pages`: required `overview`, `data_provenance`, and `gates`
- `warnings`: top-level warnings
- `source_refs`: canonical source-reference table used by page sections

## Status Vocabulary

Any field named `status` must use:

- `PASS`
- `WARN`
- `FAIL`
- `BLOCKED`
- `UNKNOWN`
- `NOT_AVAILABLE`

Missing facts must be represented explicitly with `UNKNOWN`, `WARN`, or `NOT_AVAILABLE`; silent omission of required sections is invalid.

## Freshness / Staleness

Freshness is explicit through:

- `staleness_status`
- `staleness_reason`
- `source_artifact_mtime_utc`

Allowed `staleness_status` values:

- `FRESH`
- `STALE`
- `UNKNOWN`
- `NOT_APPLICABLE`

The contract permits unavailable source times through `source_artifact_mtime_utc: null`, but the staleness posture and reason must still be present.

## Overview

The `overview` page supports:

- `status_cards`
- `warnings`
- `latest_data_slice`
- `latest_validation`
- `latest_result_population_empty_state`
- `paper_runtime_empty_state`
- `live_mode_empty_state`
- `open_gates_summary`

Required empty-state messages:

- `No D5 result population yet.`
- `No paper runtime yet.`
- `No live mode.`

These empty states are informational only and do not authorize result population, paper runtime, or live mode work.

## Data / Provenance

The `data_provenance` page supports D4A facts, including:

- D4 catalog ref
- D4 slice identity
- D3 validation report identity/hash/status
- D2 import/provenance report identity/hash/status
- D4 catalog artifact hash
- row count and expected row count
- timestamp range
- gap and duplicate facts
- raw source hash
- normalized hash
- source artifact paths

The first fixture demonstrates the current D4A Binance USDT-M BTCUSDT 15m slice values. Bulk OHLCV data remains gitignored and outside dashboard contract authority.

## Gates

The `gates` page supports read-only gate entries with:

- `gate_id`
- `title`
- `status`
- `why_it_matters`
- `required_human_action`
- `source_refs`
- `non_authority_note`

The first MVP supports these gate identities as data:

- `D5A_RUNNER_PROVENANCE_ALIGNMENT`
- `D5_KARL_GATE`
- `F2_REPORT_BACK_BEFORE_F3`
- `PAPER_RUNTIME_IMPLEMENTATION_AUTHORIZATION`
- `LIVE_GATE_PAPER_TO_LIVE_KARL_GATE`

Gate text may display required human action. It must not contain executable actions, commands, endpoint URLs, buttons, approval mutations, or broker/exchange/order controls.

## Non-Authority Enforcement

The validator rejects authority-like fields and values, including:

- `best_variant`
- `recommended_variant`
- `approved_strategy`
- `ready_for_live`
- `ready_for_paper`
- `promote`
- `promotion_status`
- `execute`
- `place_order`
- `cancel_order`
- `start_paper_run`
- `start_live_run`
- `approve_button`
- `promote_to_paper`
- `live_enabled`

The recursive key scan normalizes case and separators before matching. The value scan is intentionally narrower: it rejects exact authority-token string values after the same normalization, avoiding broad rejection of explanatory text.

## Source References

Top-level `source_refs` is the canonical source-reference table. Nested `source_refs` fields contain source reference IDs and must resolve to top-level entries.

Source-reference entries include:

- `ref_id`
- `ref_type`
- `path`
- `sha256`
- `description`

The validator rejects duplicate top-level `ref_id` values and nested references to unknown IDs.

## Boundary

`dashboard_data.v1` is non-executing, read-only, and local/offline. It creates no:

- renderer implementation
- runtime/paper/live contact
- broker/exchange/order action
- ranking, recommendation, readiness, promotion, transition, or approval authority
- result-population mutation
- source artifact mutation
