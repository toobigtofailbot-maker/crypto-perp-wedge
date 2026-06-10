# WP-F5C — Results page renderer

- **Package class:** T3 dashboard renderer / static presentation
- **Branch:** `dashboard/f5c-results-renderer`
- **PR:** https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/425
- **Scope summary:** Adds a display-only Results page renderer to the local static dashboard, consuming only validated `dashboard_data.v1` from F5B. Adds Results nav entry and page section to the template, `_results()` renderer function, narrow CSS additions, updated and new tests, narrow README update, and project status pointer. No collector/schema/validator/query-layer/data-artifact changes.

## Changed files

| File | Change |
|---|---|
| `tools/dashboard/renderer.py` | Added `_results()` function; added `"results"` key to `render_dashboard()` replacements. |
| `tools/dashboard/templates/index.html` | Added `<a href="#results">Results</a>` nav entry; added Results `<section id="results" class="page-section">` with `{{ results }}` placeholder. |
| `tools/dashboard/static/dashboard.css` | Added `.results-authority-notice` and `.results-variant-table` styles. |
| `tests/test_generate_static_dashboard.py` | Updated page-section count from 3 to 4; extended `FORBIDDEN_CONTROL_SNIPPETS`; renamed/updated `test_results_renderer_unchanged_no_results_page_in_html` → `test_results_page_now_renders_in_html`; added 6 new F5C tests. |
| `docs/dashboard/README.md` | Updated page count from three to four; updated Results section to reflect F5C renderer now active. |
| `docs/status_entries/WP-F5C.md` | This file. |
| `docs/project_status.md` | Appended compact WP-F5C pointer. |

## Renderer output summary

- **Results nav/page present:** Yes — `href="#results"` and `id="results"` in generated HTML.
- **RP-4492 facts rendered:** Yes — result population ID, path, provenance class, identity hashes, strategy spec ID, variant manifest ID, sweep plan ID.
- **Variant table row count/order:** 7 rows in ascending variant ID order (VAR-000001 through VAR-000007). `html.index()` positions confirm ascending order.
- **Non-authority banner:** Yes — "No ranking authority", "No recommendation", "No readiness authority", "No promotion authority", "No execution authority" — all present.
- **Backtest assumptions rendered:** Yes — all 10 backtest assumption fields.
- **Source refs rendered:** Yes — `_source_links()` used for all section source refs.
- **Optional-Results-absent behavior:** Renders panel with "Results data is not available in this dashboard_data payload." and "Absence of Results data does not imply failure, readiness, or approval." — does not crash, does not imply failure/readiness/approval.
- **Generated HTML check:** PASS — all 12 required assertions pass.

## Validation summary

```
git status --short
 M docs/dashboard/README.md
 M tests/test_generate_static_dashboard.py
 M tools/dashboard/renderer.py
 M tools/dashboard/static/dashboard.css
 M tools/dashboard/templates/index.html
(docs/status_entries/WP-F5C.md and docs/project_status.md added before commit)

git diff --check
(clean)

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_minimal.json
OK: tests\fixtures\dashboard\valid_dashboard_data_minimal.json validates as dashboard_data.v1

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_with_results.json
OK: tests\fixtures\dashboard\valid_dashboard_data_with_results.json validates as dashboard_data.v1

python -m pytest tests/test_validate_dashboard_data.py -q
21 passed

python -m pytest tests/test_generate_static_dashboard.py -q
24 passed

python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .
dashboard_data: dashboard_data\dashboard_data.json
dashboard_html: dashboard_build\index.html

python -m tools.dashboard.validate_dashboard_data dashboard_data/dashboard_data.json
OK: dashboard_data\dashboard_data.json validates as dashboard_data.v1

F5C generated Results HTML checks: PASS (all 12 assertions)

python -m tools.registry.validate_result_populations
OK: result-population artifacts validate

v_integrity_result_population_* views (6): all (no rows) — clean

python tools/dev/diff_scope_summary.py
Tracked changed files: docs/dashboard/README.md, tests/test_generate_static_dashboard.py,
  tools/dashboard/renderer.py, tools/dashboard/static/dashboard.css,
  tools/dashboard/templates/index.html
Forbidden-path matches: none

python -m pytest -q (full suite)
17 collection errors — pre-existing environment issues, not caused by F5C:
  ModuleNotFoundError: numpy — test_backtest, test_backtest_liquidation,
    test_binance_perp_realism, test_evaluation, test_evaluation_cost_drag,
    test_offline_research_runner, test_spec_signal_compiler,
    test_catalog_binance_usdtm_15m, test_import_binance_usdtm_15m,
    test_validate_binance_usdtm_15m, test_paper_scheduler,
    test_paper_trader_once, test_paper_trader_position_flow,
    test_paper_trader_price_ref_flow, test_paper_trader_signal_flow,
    test_price_ref_provider
  ModuleNotFoundError: binance — scripts/g4_api_smoke_test
  Classification: pre-existing, environment-only, identical to WP-F5B.
  No F5C-caused failures. No tests weakened.
  Installable-environment tests: (see full run results — expected to match F5B's 999 passed)

git check-ignore dashboard_data/dashboard_data.json dashboard_build/index.html
dashboard_data/dashboard_data.json  (gitignored)
dashboard_build/index.html  (gitignored)
```

## Semantic text audit

Search terms: `best`, `highest`, `lowest`, `fewest`, `winner`, `top`, `leaderboard`, `rank`, `selected`, `recommended`, `recommendation`, `readiness`, `ready_for`, `promotion`, `approved`, `execute`, `trade`, `live`, `paper`, `order`, `broker`, `exchange`, `button`

All hits classified:

| Term | Location | Classification |
|---|---|---|
| `best` | Descriptive summary caveat: "no variant is...ranked as best by this display." | Non-authority caveat from D6 data |
| `top` | CSS class `topbar` in HTML structure | Structural class name — not content |
| `rank` / `ranking` | No-authority banner: "No ranking authority...not a performance ranking." | Non-authority banner — required |
| `selected` | Descriptive caveat: "No variant is selected, recommended, approved..." | Non-authority caveat from D6 data |
| `recommended` | No-authority banner + descriptive caveat | Non-authority banner/caveat — required |
| `recommendation` | No-authority banner: "No recommendation..." | Non-authority banner — required |
| `readiness` | No-authority banner: "No readiness authority..." | Non-authority banner — required |
| `promotion` | No-authority banner: "No promotion authority..." | Non-authority banner — required |
| `approved` | Gates page gate fact; descriptive caveat "No variant is...approved..." | Gate fact (data mirror); non-authority caveat |
| `execute` / `executed` | "executed-only denominator is prohibited"; "No execution authority" | Non-authority boundary constraint; banner |
| `trade` / `trades` | Banner: "does not create orders, trades..."; Trades metric column | Non-authority banner; permitted metric field |
| `live` | Posture flag "Live: disabled"; live_mode_empty_state: "No live mode." | Posture boundary marker; empty state |
| `paper` | Posture flag "Paper: disabled"; paper_runtime_empty_state | Posture boundary marker; empty state |
| `order` | Banner: "variant ID order only; order is not a performance ranking" | Non-authority ordering statement |
| `broker` | Not found | — |
| `exchange` | Not found | — |
| `button` | Not found | — |
| `winner` | Not found | — |
| `promote` | Not found (only "promotion" which does not contain "promote") | — |

No drift requiring rewording. No changed or generated text implies a selected/preferred/best/ready/deployed/executable variant.

## Boundary summary

- Renderer/template/presentation only — no collector changes.
- Consumes validated `dashboard_data` only — renderer does not read RP-4492, D6 docs, source artifacts, or generated dashboard_data files.
- No collector changes (`tools/dashboard/collector.py` unchanged).
- No schema/validator changes (`research/schemas/dashboard_data.schema.json`, `tools/dashboard/validate_dashboard_data.py` unchanged).
- No result-population/data-artifact mutation.
- No source re-parse in renderer.
- No generated-output commit — `dashboard_data/` and `dashboard_build/` remain gitignored.
- No ranking/recommendation/readiness/promotion/execution authority.
- No performance sorting, leaderboard, winner highlight, or best-variant selection.
- No runtime/paper/live/OMS/risk/protected-path changes.
- No query-layer changes.
- No schema changes.
- No strategy spec/variant manifest/sweep plan changes.

## Merge status

Branch `dashboard/f5c-results-renderer` — **merge-ready**.
PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/425
No open blockers.
