# WP-DATA-MATERIALIZE-FUNDING-FEATURE-01 Branch State

## Scope Summary

Additive local-data materialization of a runner-consumable BTCUSDT 15m `funding_rate` feature, plus lineage, availability, fail-closed tests, and declared-column smoke evidence.

## Main / Operator Authorization

Main identified funding-carry as the first data-derived frontier. The operator selected the bounded funding-data foundation package. No strategy hypothesis or edge-discovery authority is included.

## Repo-Truth Discovery

PR #559 is merged. Local ignored full-history funding and D4A OHLCV inputs exist. The compiler already accepts `funding_rate`; the runner already preserves declared non-OHLCV columns. Exact RP replay commands do not exist.

## Funding Source Inventory

The local funding parquet has 7,220 rows from `2019-09-10T08:00:00Z` through `2026-04-12T16:00:00Z`, SHA256 `5f0da7478ccf3514af41dff9958b579cd2f797a2716001b0fa10a11059912798`. It is gitignored local data cataloged in `docs/data_catalog.md`.

## Funding Materialization Contract

`tools/data/materialize_funding_feature.py` accepts local CSV/Parquet only, requires the approved full-history availability label and source identity, validates timestamps/symbol/coverage, and writes a deterministic runner CSV plus manifest.

## Materialized Dataset Status

The ignored output contains 220,128 D4A bars from `2020-01-01T00:00:00Z` through `2026-04-11T23:45:00Z`, with `funding_rate`, SHA256 `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`, size 15,450,598 bytes. The full dataset is not committed.

## Alignment / No-Lookahead Rule

Each bar receives the latest funding event timestamp at or before bar close. Values carry forward only after observation. Coverage has zero uncovered rows, zero lookahead violations, and zero gaps over an 8-hour plus 1-minute timestamp-jitter threshold.

## Declared-Column Runner Smoke

Passed. The funding-specific smoke proves `funding_rate` reaches the backtester through the PR #559 declared-column path and preserves `PUBLIC_FUNDING_ARCHIVE` in `data_availability_claim`. It makes no strategy or edge conclusion.

## Funding P&L Status

Funding P&L remains separate and default-off. No funding cost, P&L, fill, position, or accounting semantics changed.

## RP Replay / Determinism Harness

Exact replay for `RP-2592`, `RP-3731`, and `RP-7134` remains blocked because no committed repo-native reconstruction command or canonical normalization contract exists. No broader harness was invented. Materialized CSV byte determinism is tested.

## Availability Label Preservation

The manifest and runner claim preserve `FULL_HISTORY_PUBLIC_ARCHIVE`, `PUBLIC_FUNDING_ARCHIVE`, and the catalog condition. Tests prove recent-only, missing identity, and incomplete coverage fail closed.

## Validation Status

Focused materialization and offline-runner tests pass (`106 passed`). Result-population / availability / candidate-registry tests pass (`88 passed`); all three registry validators pass; 124 query views list successfully; diff scope reports no forbidden matches; and `git diff --check` passes. Initial full pytest had `2226 passed, 1 skipped, 1 failed` solely because the isolated worktree lacked the ignored D4A file. After copying the root-local D4A into its ignored conventional worktree path, the failing test passed and the repo full-pytest sharded verifier passed all 4 shards / 106 test files.

## Boundary Summary

No network, API, credential, private endpoint, vendor source, synthetic-as-real data, large committed dataset, strategy research, canonical artifact, crossing, promotion, runtime, paper/live, OMS, risk, reconciliation, or capital path is used or changed.

## Non-Authority Statement

These research/workbench artifacts have no execution, evidence, candidate, promotion, readiness, paper/live, or runtime authority.

## Research-Lab Completion Note

This WP is research-lab data foundation work.

It does not complete the Side 12 / operator target-state lab.

It does not run edge discovery.

It does not produce a candidate.

It does not authorize paper/live/runtime.

It only attempts to materialize one data-derived feature path required before funding-family strategies can be tested honestly.

## Open Decision Surfaces

- Whether a later package defines a canonical exact RP replay and normalization contract.
- Whether a separately authorized package defines and runs a funding-family hypothesis using this feature path.
