# WP-F2 / Dashboard Track - dashboard_data Contract, Validator, and Fixtures

## WP Id / Title

WP-F2 / Dashboard Track - `dashboard_data` contract, validator, and fixtures.

## Branch / PR

- Branch: `codex/dashboard-f2-data-contract-validator`
- PR: pending

## Package Class

T3 schema/validator/tests.

## Scope Summary

Adds the first versioned `dashboard_data.v1` contract for future local static dashboard renderers. The contract covers Overview, Data / Provenance, and Gates; requires explicit freshness/staleness and source-reference structure; and preserves a read-only, non-authoritative posture.

F1 dashboard design files are not present on the refreshed `origin/main` base used by this package, so F2 follows the Main-approved constraints embedded in the package brief and does not create or edit F1 files.

## Changed Files

- `docs/architecture/2026-06-dashboard_data_contract.md`
- `docs/status_entries/WP-F2.md`
- `research/schemas/dashboard_data.schema.json`
- `tools/dashboard/__init__.py`
- `tools/dashboard/validate_dashboard_data.py`
- `tests/test_validate_dashboard_data.py`
- `tests/fixtures/dashboard/valid_dashboard_data_minimal.json`
- `tests/fixtures/dashboard/invalid_dashboard_data_authority_field.json`
- `tests/fixtures/dashboard/invalid_dashboard_data_missing_status.json`
- `tests/fixtures/dashboard/invalid_dashboard_data_bad_gate_action.json`
- `.gitignore`

## Contract Summary

`dashboard_data.v1` requires:

- source repo identity: `generated_at_utc`, `source_commit`, `source_branch`, `dirty_state`
- posture: `system_posture`
- non-authority declaration
- required pages: `overview`, `data_provenance`, `gates`
- explicit top-level and nested warnings
- top-level source-reference table with nested reference IDs

Required status vocabulary is `PASS`, `WARN`, `FAIL`, `BLOCKED`, `UNKNOWN`, and `NOT_AVAILABLE`.

Required staleness vocabulary is `FRESH`, `STALE`, `UNKNOWN`, and `NOT_APPLICABLE`.

## Validator Behavior

`python -m tools.dashboard.validate_dashboard_data <path>` validates one JSON file. It exits `0` for valid contract data and nonzero for invalid data, prints concise deterministic errors, performs no network access, and mutates no artifacts.

The validator layers semantic checks over JSON Schema:

- recursive forbidden key scan
- exact forbidden value scan for authority tokens
- required non-authority true flags
- status and staleness vocabulary checks
- source-reference resolution
- gate action text rejection for commands or endpoint URLs

## Fixtures

Committed fixtures are tiny synthetic dashboard-data examples under `tests/fixtures/dashboard/`:

- valid minimal dashboard_data with compact D4A provenance facts
- invalid authority field
- invalid missing status
- invalid gate action / execution control

No generated dashboard output or production-scale data is committed.

## Non-Authority Enforcement

The schema and validator reject authority-like fields or obvious equivalents such as `best_variant`, `recommended_variant`, `approved_strategy`, `ready_for_live`, `ready_for_paper`, `promote`, `promotion_status`, `execute`, `place_order`, `cancel_order`, `start_paper_run`, `start_live_run`, `approve_button`, `promote_to_paper`, and `live_enabled`.

The contract permits explanatory text but does not permit execution controls, commands, endpoint URLs, approval buttons, ranking, readiness, recommendation, promotion, transition, order, broker, exchange, paper, or live authority.

## Freshness / Staleness Behavior

Freshness is represented through `freshness.staleness_status`, `freshness.staleness_reason`, and `freshness.source_artifact_mtime_utc`. Missing source times are allowed as `null`, but the staleness status and reason fields remain required.

## D4A Provenance Support

The valid fixture represents the current D4A facts:

- D4 catalog ref: `binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b`
- D4 slice identity: `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- D3 validation report hash: `785a8d53797155dcc80e646e8610db8d510825b9fa3dbccd21e79aa2700a6c1c`
- D2 import report hash: `553c320d6639ceca4422f0f08620550c558e05162eb16aff30854db76a7246d3`
- D4 catalog artifact hash: `80a080336853ca96c81e2033a381527caec3737c1a817c111fc61d4e8c685327`
- row count / expected row count: `220128` / `220128`
- timestamp range: `2020-01-01T00:00:00Z` to `2026-04-11T23:45:00Z`
- gap and duplicate counts: zero
- raw and normalized hashes

## Validation Summary

- `git diff --check`: pass.
- `python -m pytest tests/test_validate_dashboard_data.py -q`: pass, 15 tests.
- `python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_minimal.json`: pass.
- Invalid fixture CLI checks: authority field, missing status, and bad gate action fixtures all rejected with nonzero validator behavior covered by focused tests.
- `python -m tools.registry.validate_result_populations`: pass.
- `python -m tools.research_query.run --list-views`: pass.
- `v_integrity_*`: clean, 55 views.
- `python tools/dev/diff_scope_summary.py`: pass; default advisory forbidden-prefix output flags `research/schemas/dashboard_data.schema.json` under `research/`, which is expected and authorized for this T3 schema/validator package.
- `python -m pytest -q`: environment-only failure after 1,199 passed tests because the isolated worktree lacks gitignored local fixture `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` required by `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`. No data file is committed or pulled into scope.

## Boundary Summary

No renderer, HTML generator, CSS/JS UI, server, generated dashboard output, production-scale data, data artifact mutation, result population mutation, runner/compiler/backtester/lib change, query-layer change, runtime/paper/live path, broker/exchange/order path, credentials, dependencies, CI, ranking, readiness, recommendation, promotion, transition, approval, or execution authority is included.

## Merge Status

Pending PR at package execution time.

## Next Dependency / Runway Note

F2 must report back to Main after merge before any F3 renderer implementation. F3 should consume only contract-valid dashboard facts.
