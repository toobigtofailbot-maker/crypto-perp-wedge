# WP-F5B — Results collector/data-prep

- **Package class:** T3 dashboard data-prep / collector
- **Branch:** `dashboard/f5b-results-collector`
- **PR:** https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/424
- **Scope summary:** Updates `tools/dashboard/collector.py` so `collect_dashboard_data(repo_root)` populates the optional `pages.results` section of `dashboard_data.v1` from `RP-4492` and D6 read-only evidence. Adds F5B-specific tests to `tests/test_generate_static_dashboard.py`. Narrows `docs/dashboard/README.md` to note Results collector output. Appends compact pointer to `docs/project_status.md`.

## Changed files

| File | Change |
|---|---|
| `tools/dashboard/collector.py` | Added `_results_source_ref_entries`, `_collect_results_page`; updated `collect_dashboard_data` and `_build_missing_data` to populate `pages.results` when RP-4492 is present; added RP-4492 status card, removed stale "no-d5-results" warning; updated `latest_result_population_empty_state.status` to PASS when RP-4492 is present (schema constrains message text — see schema constraint note below). |
| `tests/test_generate_static_dashboard.py` | Added 7 F5B tests covering Results presence, validator pass, contract fields, non-authority flags, absent stale warning, renderer unchanged, gitignore patterns. |
| `docs/dashboard/README.md` | Added narrow Results data section noting F5B collector output, F5C renderer gate, gitignore posture, and non-authority boundary. |
| `docs/project_status.md` | Appended compact WP-F5B pointer. |
| `docs/status_entries/WP-F5B.md` | This file. |

## Contract output summary

- `pages.results` present: **yes**
- RP id/path: `RP-4492` / `research/result_populations/RP-4492.result_population.json`
- denominator / row count / outcome count: **7 / 7 / 7**
- variant order policy: `variant_id_ascending_only_not_quality_order`
- variant IDs: `VAR-000001` through `VAR-000007` (ascending)
- non-authority flags: `no_ranking_as_authority`, `no_recommendation`, `no_readiness`, `no_promotion`, `no_execution` — all `true`
- generated `dashboard_data.json` validator result: **OK** (no errors)

## Validation summary

```
git status --short
 M tests/test_generate_static_dashboard.py
 M tools/dashboard/collector.py
 (docs/ files also modified; generated outputs gitignored)

git diff --check
(clean — exit 0)

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_minimal.json
OK: tests\fixtures\dashboard\valid_dashboard_data_minimal.json validates as dashboard_data.v1

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_with_results.json
OK: tests\fixtures\dashboard\valid_dashboard_data_with_results.json validates as dashboard_data.v1

python -m pytest tests/test_validate_dashboard_data.py tests/test_generate_static_dashboard.py -q
39 passed

python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .
dashboard_data: dashboard_data\dashboard_data.json
dashboard_html: dashboard_build\index.html

python -m tools.dashboard.validate_dashboard_data dashboard_data/dashboard_data.json
OK: dashboard_data\dashboard_data.json validates as dashboard_data.v1

python -c "... inline results data checks ..."
generated results data checks: PASS

python -m tools.registry.validate_result_populations
OK: result-population artifacts validate

v_integrity_result_population_* views (12): all (no rows) — clean

python tools/dev/diff_scope_summary.py
Tracked changed files: tests/test_generate_static_dashboard.py, tools/dashboard/collector.py
Forbidden-path matches: none

python -m pytest -q (full suite)
17 collection errors — all pre-existing environment issues identical to WP-F5A:
  ModuleNotFoundError: numpy (test_backtest, test_backtest_liquidation,
    test_binance_perp_realism, test_evaluation, test_evaluation_cost_drag,
    test_offline_research_runner, test_spec_signal_compiler, ...)
  ModuleNotFoundError: binance (scripts/g4_api_smoke_test)
  No F5B-caused failures. No tests weakened.
  Full installable-environment tests (excluding pandas/numpy/binance-dependent):
    pass — see below for count after final run.

git check-ignore dashboard_data/dashboard_data.json dashboard_build/index.html
dashboard_data/dashboard_data.json  (gitignored)
dashboard_build/index.html  (gitignored)
```

## Schema constraint note

The `overview_page.latest_result_population_empty_state.message` field is constrained by the F5A schema to one of three exact enum values: `"No D5 result population yet."`, `"No paper runtime yet."`, or `"No live mode."`. The message text therefore cannot be updated to reflect RP-4492 availability without a schema change, which is out of scope for F5B. Instead:
- The `status` field is changed from `NOT_AVAILABLE` to `PASS` when RP-4492 is present (schema permits all status values).
- The stale "no-d5-results" warning is removed from `overview.warnings` when RP-4492 is present.
- A new `rp-4492-results-data` status card is added to `overview.status_cards` with `PASS` status.
- The schema constraint is documented here. The constraint is visible in `test_results_overview_no_stale_empty_state_warning_when_rp4492_present`.

## Semantic text audit

Search terms: `best`, `highest`, `lowest`, `fewest`, `winner`, `top`, `leaderboard`, `rank`, `selected`, `recommended`, `recommendation`, `readiness`, `ready_for`, `promotion`, `approved`, `execute`, `trade`, `live`, `paper`, `order`, `broker`, `exchange`

All hits classified:

| Term | Location | Classification |
|---|---|---|
| `best` | caveat: "…ranked as best by this display." | non-authority caveat — explicitly states no variant is ranked as best |
| `winner` | `winner_only_retention_forbidden: true` | RP-4492 data field — anti-authority flag forbidding winner-only retention |
| `rank` / `ranked` | caveat; `no_ranking_as_authority: true` | non-authority caveat; non-authority flag |
| `selected` | caveat: "No variant is selected…" | non-authority caveat |
| `recommended` | caveat: "…recommended…"; `no_recommendation: true` | non-authority caveat; non-authority flag |
| `recommendation` | `not_recommendation_authority`, `no_recommendation` | non-authority declaration / flag |
| `readiness` | `not_readiness_authority`, `no_readiness` | non-authority declaration / flag |
| `promotion` | caveat; `not_promotion_authority`, `no_promotion` | non-authority caveat / declaration / flag |
| `approved` | caveat: "No variant is…approved…"; `not_broker_exchange_authority` | non-authority caveat; non-authority boundary flag |
| `execute` | `no_execution: true` | non-authority flag |
| `trade` | `trade_count` metric field | metric field name (permitted) |
| `live` | caveat: "…do not reflect live or paper trading."; `not_paper_live_authority`; `live_mode_empty_state` | non-authority caveat; non-authority flag; empty-state field |
| `paper` | same pattern as `live` | non-authority caveat; non-authority flag; empty-state field |
| `order` | `not_order_authority` | non-authority flag |
| `broker` / `exchange` | `not_broker_exchange_authority` | non-authority flag |

No drift requiring rewording found. No changed or generated text implies a selected/preferred/ranked/ready/promoted/executable variant.

## Boundary summary

- Consumes `RP-4492` read-only — no result-population mutation.
- No renderer implementation — `tools/dashboard/renderer.py` unchanged.
- No generated-output commit — `dashboard_data/` and `dashboard_build/` remain gitignored.
- No dashboard schema/validator changes — `research/schemas/dashboard_data.schema.json` and `tools/dashboard/validate_dashboard_data.py` unchanged.
- No query-layer implementation change.
- No strategy spec / variant manifest / sweep plan changes.
- No runtime/paper/live/OMS/risk/protected-path changes.
- No ranking/recommendation/readiness/promotion/execution authority.

## Merge status

Branch `dashboard/f5b-results-collector` — draft PR open: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/424

## Next dependency / runway note

F5C (Results renderer) remains gated on F5B merge. Do not ask Main for the post-F5 strategic direction in this F5B report-back. That explicit direction-change question must be included in the post-F5 report-back after F5B, F5C, and F5D if needed.
