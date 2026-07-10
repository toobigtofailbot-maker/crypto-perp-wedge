# WP-DASH-DEBT-CLEANUP-05 — No-scope-drift evidence

This pass is presentational cleanup only. Evidence that no forbidden scope was
entered:

## Files changed (8, all allowed)
All under `operator_dashboard_frontend/src/**`:

```
operator_dashboard_frontend/src/components/AppShell.tsx
operator_dashboard_frontend/src/components/Sidebar.tsx
operator_dashboard_frontend/src/components/ProvenanceFooter.tsx
operator_dashboard_frontend/src/components/charts/ChartProvenanceNote.tsx
operator_dashboard_frontend/src/components/charts/UnavailableChartState.tsx
operator_dashboard_frontend/src/components/explorer/EvidencePanel.tsx
operator_dashboard_frontend/src/components/agent-inbox/IntakeForm.tsx
operator_dashboard_frontend/src/components/viz.tsx
```

Plus package-local docs/evidence:
`docs/status_entries/WP-DASH-DEBT-CLEANUP-05.md`,
`scratch/WP-DASH-DEBT-CLEANUP-05/*`.

`tools/dev/diff_scope_summary.py` classified every changed source file under the
allowed `operator_dashboard_frontend/src/**` prefix.

## Forbidden scope — confirmed untouched
- **No new routes.** `git diff` adds no files under `src/app/**/page.tsx` or
  `route.ts`; nav model `lib/nav.ts` unchanged.
- **No new data fetching.** No new `apiClient`/`fixtures` calls; no `fetch`
  added. `IntakeForm` change deletes copy only.
- **No new API endpoints.** `route.ts` passthrough untouched; read-only
  dashboard API untouched.
- **No dependencies.** `package.json` / lockfile unchanged.
- **`tools/**` untouched.** No file under `tools/` in the diff.
- **No history/review/canonicalization feature.** Deletions + CSS class + copy
  only.
- **No new controls.** Agent Inbox still has exactly 1 `<form>`, 1
  `type="submit"`, 2 buttons total (submit + clear) — verified in-browser. No
  run / approve / execute / promote / cross / trade control anywhere.
- **No chart semantics changed / no fabricated data.** `CategoricalCountChart`,
  `ChartProvenanceNote` field/derived/drawn/missing logic unchanged; only a
  `break-all` class added to a source-path span. The removed `Funnel` had zero
  importers, so no chart lost a renderer.
- **No auth/hosting/Grafana/paper/live/monitoring**, and **no runtime / OMS /
  risk / reconciliation / safe-mode path** — none are in this package.

## Nature of each change
- `viz.tsx`: delete dead `Funnel` + `FunnelStageRow`; docstring wording.
- `IntakeForm.tsx`: remove one redundant trailing sentence from an error
  `reason` string (no logic, no service-meaning change).
- `AppShell.tsx` / `Sidebar.tsx`: responsive Tailwind classes so the existing
  sidebar layout stacks on mobile instead of clipping content. Same components,
  same nav, same links.
- `ProvenanceFooter.tsx`, `ChartProvenanceNote.tsx`, `UnavailableChartState.tsx`,
  `EvidencePanel.tsx`: add `break-all` (+ one `min-w-0`) so long mono
  identifiers wrap instead of being clipped.

Every change is CSS-class or copy or dead-code-deletion. No behavior, data
flow, or capability was added.
