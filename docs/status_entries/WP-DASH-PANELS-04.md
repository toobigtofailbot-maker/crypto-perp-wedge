# WP-DASH-PANELS-04 Status Entry

## Scope

First real data-panel pass over the already-merged, isolated
`operator_dashboard_frontend/` read-only operator dashboard shell. Presentation
only: the shell renders committed API-shaped fixtures and is turned from a
navigational scaffold into an informative operator cockpit without gaining any
control, write, or runtime authority.

## Decision

Delivered. Real panels were added across Command Center, Research (overview +
jobs), Result Populations, Strategies (list + detail), Candidates, Reports, and
System (overview + data + validators + provenance), plus reusable CSS-only
visual primitives. Agent Inbox / Paper / Live remain honest placeholders.

## What changed

- Added CSS-only visual primitives (`components/viz.tsx`): `Meter`, `CountBars`,
  `StackedBar`, `Funnel` — proportional bars / distributions / funnel built from
  Tailwind + inline widths. No chart dependency.
- Added `components/BoundaryNotes.tsx` (inline warnings/withheld/unavailable) and
  `lib/status.ts` (status→tone mapping + display aggregations).
- Upgraded panels: queue/pipeline distributions, product-run summary, per-run
  job cards (approval-needed + blocked reasons + dry-run notification preview,
  all visibility-only), result-population outcome distributions with committed-
  denominator-vs-rows reconciliation, enriched strategy cards, candidate funnel
  with registry breakdowns, report readability (state distribution, withheld
  statistics, caveats, edge-search hold), and system data-health / validator /
  provenance detail.
- Fixed a display bug: result-population validator tone compared against `"PASS"`
  while the committed value is `"passed"`; now handled by a case-insensitive
  status→tone helper.

## Files Created

- `docs/status_entries/WP-DASH-PANELS-04.md`
- `operator_dashboard_frontend/src/components/viz.tsx`
- `operator_dashboard_frontend/src/components/BoundaryNotes.tsx`
- `operator_dashboard_frontend/src/lib/status.ts`
- `scratch/WP-DASH-PANELS-04/repo_truth_discovery.md`
- `scratch/WP-DASH-PANELS-04/panel_inventory.md`
- `scratch/WP-DASH-PANELS-04/no_control_evidence.md`
- `scratch/WP-DASH-PANELS-04/non_authority_assertions.json`
- `scratch/WP-DASH-PANELS-04/validation_summary.txt`

## Boundary

Frontend panel/presentation work only. Read-only. No new dependency, no chart
library, no API/backend change, no fixture regeneration, no POST/mutation, no
Agent Inbox write, no execution/approval/promotion/crossing/paper-live/
notification/scheduler controls, no hosted deployment, no auth, no Grafana, no
runtime or paper/live contact, no canonical/candidate-lifecycle/crossing/
promotion/readiness writes, no protected-path changes. Navigation-only `<Link>`
elements are the sole interactivity; no control-looking buttons were added.

## Validation

typecheck / lint / build PASS; `tests/test_operator_dashboard_api.py` 11 passed;
`research_query --list-views`, `validate_result_populations`,
`validate_candidate_registry` OK; `diff_scope_summary.py` exit `ok` with no
forbidden-path matches; `git diff --check` clean; no-control scan clean; visual
render verified via `next dev`. Full detail in
`scratch/WP-DASH-PANELS-04/validation_summary.txt`.
