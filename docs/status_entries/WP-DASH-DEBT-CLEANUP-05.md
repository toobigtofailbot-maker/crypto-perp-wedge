# WP-DASH-DEBT-CLEANUP-05 — Narrow dashboard UI debt cleanup

- Package class: narrow frontend UI-debt cleanup (no new capability)
- Execution mode: local-first, read-only, presentation only
- Base: `main` @ `1969251` (PRs #636 and #639 merged)
- Branch: `claude/wp-dash-debt-cleanup-05`
- Decision: **READY_FOR_REVIEW**

## What this package delivers

A narrow cleanup pass over known operator-dashboard UI debt. No new architecture,
routes, data fetching, endpoints, dependencies, or controls. 8 source files
changed, all under `operator_dashboard_frontend/src/**` (+24 / -47).

### Cleanup items (all four completed)

1. **Redundant Agent Inbox error copy — done.** `IntakeForm.tsx` appended
   "No draft packet was created, and nothing is shown in its place." to every
   submit-error `reason`, on top of an `UnavailableState` title that already
   says "Draft not created" / "Intake service unreachable" and passthrough
   messages that already end with "No draft was created." Reduced to
   `reason={submission.message}`. No service error meaning changed — the
   passthrough (`route.ts`) and the isolated service are untouched.

2. **Dead `Funnel` / `FunnelStageRow` removed — done.** After Charts 05 the
   candidates funnel is drawn by the ECharts `CategoricalCountChart`; the CSS
   `Funnel` primitive had **zero importers** on `main` (verified by
   word-boundary search — remaining "Funnel" hits are string literals and
   unrelated `candidatesFunnel` / `FunnelStage` identifiers). Removed the
   component and its interface from `viz.tsx`; corrected the module docstring.
   Kept the still-used `BAR_CLASS`, `DOT_CLASS`, `pct`, `CountBars`,
   `StackedBar` (build/lint green confirms they are live).

3. **Mobile / narrow-viewport shell overflow — done.** At 375px the shell's
   fixed 240px `shrink-0` sidebar left the content column **135px** wide and the
   outer `overflow-hidden` clipped the overflowing content with no way to reach
   it. `AppShell.tsx` + `Sidebar.tsx` now stack vertically below `md` (full-width
   nav block above full-width content) and restore the persistent side-by-side
   sidebar from `md` up. Top-level nav links wrap horizontally on mobile
   (`flex-row flex-wrap` → `md:flex-col`), cutting mobile nav height ~440px→~322px
   while preserving every link and the active group's sub-nav. Desktop layout is
   unchanged (240px vertical sidebar). Fix stays within the existing sidebar
   layout intent — no drawer, no toggle, no new component/route/control.

4. **Small operator-facing clarity fixes (directly related to #3) — done.**
   Long unbreakable `font-mono` identifiers still clipped the content column at
   full width. Added `break-all` (and one `min-w-0`) at the four shared spots
   that render them so they wrap: `ProvenanceFooter` artifact paths,
   `ChartProvenanceNote` source path, `UnavailableChartState` "Declared by"
   source, and `EvidencePanel` reconciliation check ids.

## Boundary

Frontend cleanup only. No route, data fetch, API endpoint, or dependency added.
No new form, button, or mutation path — the Agent Inbox still exposes exactly one
form and one submit (plus its existing Clear button), verified in-browser. No
chart semantics changed and no data fabricated; the removed `Funnel` had no
renderer role left. `tools/**`, the read-only dashboard API, and all
runtime/OMS/risk/reconciliation/safe-mode paths are untouched.

## Intentionally not changed

Wide explorer data tables on `/strategies/{id}` overflow the viewport but already
sit in `overflow-x-auto` scroll containers (the intended pattern for wide
tables); verified scrollable, not clipped — left as-is.

## Validation

| Check | Result |
| --- | --- |
| `npm run typecheck` | PASS (no errors) |
| `npm run lint` | PASS (no warnings or errors) |
| `npm run build` | PASS (all routes compiled) |
| `pytest tests/test_operator_dashboard_api.py` | PASS |
| `pytest tests/test_agent_inbox_intake.py` | PASS (19 passed together) |
| `python tools/dev/diff_scope_summary.py` | ok — all changes under allowed prefix |
| `git diff --check` / `--cached --check` | OK (no whitespace errors) |
| Browser, 375px: `/`, `/agent-inbox`, `/candidates`, `/strategies`, `/strategies/STRAT-SPEC-0001`, `/research/result-populations` | No horizontal overflow, 0 clipped-in-`main` elements, no console errors, charts render |

Note: a transient Next dev cache error ("Cannot find module './276.js'") appeared
once when `npm run build` ran against the same `.next` dir as the live dev
server; cleared by `rm -rf .next` + restart. The production build passed cleanly
and all browser results were re-confirmed on the clean server — not a code
defect.

## Report-back

- Item 1 (redundant error copy): **done**.
- Item 2 (dead `Funnel`/`FunnelStageRow`): **done** (zero importers, evidence recorded).
- Item 3 (mobile shell overflow): **done** (content no longer clipped; desktop unchanged).
- Item 4 (related clarity fixes): **done** (mono identifiers wrap).
- Intentionally deferred: wide explorer tables (already correctly in
  `overflow-x-auto` scroll wrappers — no change needed).
- No new product capability was introduced.
