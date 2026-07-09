# WP-DASH-PANELS-04 — Repo-Truth Discovery

First real dashboard data panels over the already-merged read-only operator
portal shell. Local-first, read-only, presentation only.

## Preflight state

- Base: `main` @ `a03f07f` (PR #633 / WP-DASH-FRONTEND-NEXT16-EVAL-03B merged).
- Branch: `claude/wp-dash-panels-04-c379e9` (worktree), cut from `origin/main`.
- Node `v24.18.0`, npm `11.16.0` (winget install at `C:\Program Files\nodejs`,
  not on default PATH — prepended for this session).
- Baseline BEFORE changes: `npm run typecheck` PASS, `npm run lint` PASS
  (no ESLint warnings/errors), `npm run build` PASS (all routes prerendered).

## Current frontend package versions (`operator_dashboard_frontend/package.json`)

- `next` 14.2.35 (merged baseline after #632/#633).
- `react` / `react-dom` 18.3.x, `typescript` 5.x, `tailwindcss` 3.4.x.
- No chart / plotting dependency present. **No new dependency is needed** —
  all panels use Tailwind/CSS/React primitives only.

## Route / page structure (App Router, all static/read-only)

- `/` Command Center — dashboard_summary fixture.
- `/research`, `/research/jobs`, `/research/result-populations`,
  `/research/families` (placeholder), `/research/blockers` (placeholder),
  `/research/robustness` (placeholder).
- `/strategies`, `/strategies/[strategy_id]`.
- `/candidates`.
- `/reports`, `/reports/daily`, `/reports/weekly`,
  `/reports/strategy-review` (placeholder), `/reports/main` (placeholder).
- `/system`, `/system/data`, `/system/validators`, `/system/provenance`,
  `/system/blockers` (placeholder).
- `/agent-inbox`, `/paper`, `/live` (placeholders / boundary pages).

## Available fixture / API envelope files (`src/lib/fixtures/`)

All are committed API projections generated from
`tools.operator_dashboard_api.app` via FastAPI TestClient, schema
`operator_dashboard_api_v1`. Envelope = `{schema_version, source, provenance[],
authority{}, warnings[], withheld{}, unavailable{}, data}`.

- `dashboard_summary.json` — `data.counts` (result_populations 8, strategies 6,
  registered_candidates 12, queue_runs 3, product_runs 1, candidates_admitted 0),
  `queue_summary` (by_status, approval_needed_count 2, blocked_count 1),
  `product_run_summary`, `paper_trading` / `live_trading` unavailable.
- `research_jobs.json` — `data.summary` (run_count, by_status over 8 states,
  approval/blocked/failed/advisory counts) + `data.runs[]` with per-run
  `status`, `approval_needed`, `blocked_reasons[]`, `notification_preview`
  (dry_run_only true, notification_fired false). Withholds notifications as
  dry-run preview metadata only.
- `result_populations.json` — `data.items[]` with committed_denominator,
  result_row_count, `outcome_counts` (successful/failed/errored/… + counts_sum
  and counts_sum_equals_committed_denominator), execution_mode `offline_research`,
  offline_only / no_runtime_contact / no_paper_live_contact,
  `validator_status` = `"passed"`, `review_status` = `"not_reviewed"`.
  Withholds per_trade_distributions.
- `strategies.json` — `data.items[]` with title, short_name, status
  `approved_for_variant_planning`, `source_type`, instrument_family,
  market_type, primary_timeframe, direction, `free_parameter_count` (null),
  `max_free_parameters` (5), `not_executable` true.
- `candidates_funnel.json` — `data.candidate_registry` (registered_count 12,
  by_status, by_overall_verdict, admitted_candidate_count 0, paper_live_built
  false) + `data.product_candidate_funnel` (available, winner_only_view false,
  `stages[]` runner→advisory→admitted counts, note). Withholds
  candidate_admission; paper_live_capability unavailable.
- `reports_daily.json` / `reports_weekly.json` — `data.report` with
  `non_authority_declaration`, `edge_search_hold`, `counts`
  (subjects/completed/blocked/no_gos + by_overall_state), section arrays
  (completed_runs, blocked_runs, no_gos, validation_status,
  candidate_review_readiness, artifact_links), `withheld_statistics`
  (PSR/DSR/MinTRL), `caveats[]`, `charting.enabled=false`.
- `system_data_health.json` — `data.status` PASS, `data_provenance`
  (d4_slice row_count/gap_facts/duplicate_facts/freshness, artifact_paths[]),
  `latest_data_slice`, `latest_validation`, `paper_runtime` /
  `live_mode` NOT_AVAILABLE, `warnings[]` (display-only-gates WARN).
- `agent_intake_schema.json` — `data.status` unavailable, draft_endpoint_available
  false, allowed_methods ["GET"], future_intake_fields_preview[]. Unavailable:
  agent_inbox_write (POST intentionally not implemented).

## Data fields used by each new/updated panel

- Command Center: counts, queue_summary.by_status + approval/blocked counts,
  product_run_summary, paper/live unavailable, envelope.warnings/withheld/
  unavailable (top items), provenance.
- Research / Jobs: summary.by_status distribution, per-run status chips,
  approval_needed.kind/scope, blocked_reasons, notification_preview dry-run
  disclaimer.
- Result Populations: committed_denominator vs result_row_count,
  outcome_counts distribution (CSS bars), offline/no-runtime/no-paper-live
  badges, validator/review status chips, withheld per-trade note.
- Strategies: title/id, status, source_type, instrument_family, market_type,
  primary_timeframe, direction, free_parameter_count vs max_free_parameters,
  not_executable badge.
- Candidates: registry counts, by_status, by_overall_verdict, funnel stages
  (CSS proportional bars), winner_only_view, admitted count, paper/live
  unavailable.
- Reports: counts stat tiles, by_overall_state distribution, section sizes,
  withheld_statistics, caveats, charting-withheld note, edge_search_hold,
  descriptive-only notification posture.
- System: data-health status, d4 slice facts (rows/gaps/duplicates/freshness),
  validator state, provenance artifact inventory, paper/live NOT_AVAILABLE,
  warnings.

## Current unavailable / withheld / provenance fields

Rendered by the shared `ProvenanceFooter` (source, schema, provenance artifacts,
warnings, withheld keys, unavailable keys). New panels additionally surface the
specific withheld/unavailable notes inline where relevant (per-trade
distributions, notifications dry-run, candidate_admission, paper_live_capability,
agent_inbox_write, charting).

## No-control constraints in existing shell

- `apiClient.ts` is GET-only, imported by no page; shell renders committed
  fixtures with zero network contact. No POST/PUT/PATCH/DELETE helper exists.
- Sidebar interactivity is navigation-only (`usePathname` for active
  highlight); every nav entry is a Next `<Link>`.
- `Banners.tsx` renders explicit READ-ONLY / authority-state banners on every
  page via `PageHeader`.
- Every fixture `authority` block sets `control_surface: "none"` and negates
  execution/approval/ranking/readiness/promotion/runtime/paper-live/agent-inbox/
  scheduler/notification authority.

## Observed defect to fix within display scope

- `research/result-populations/page.tsx` compared `validator_status === "PASS"`,
  but the committed value is `"passed"`, so the "good" tone never rendered.
  Fixed via a case-insensitive status→tone helper in the panel upgrade.

## New dependency decision

**No new dependency.** All visual summaries (distribution bars, funnel bars,
meters) are implemented with Tailwind utility classes and inline width styles
over React primitives. Charting libraries are explicitly out of scope and not
introduced.
