# WP-DASH-PANELS-04 — Panel Inventory

First real data-panel pass over the read-only operator dashboard shell. All
panels are CSS/React/Tailwind only; no chart dependency; read-only.

## Shared additions

- `components/viz.tsx` — `Meter`, `CountBars`, `StackedBar`, `Funnel`
  (CSS-only proportional bars / distributions / funnel).
- `components/BoundaryNotes.tsx` — inline warnings / withheld / unavailable panel.
- `lib/status.ts` — `toneForStatus` (status→cockpit tone), `humanize`,
  `sumCounts`.
- `lib/types.ts` — added `QueueSummary`, `ProductRunSummary`,
  `CandidateRegistryRollup`, `FunnelStage`, `ProductCandidateFunnel`,
  `CandidatesFunnelData`; enriched `StrategySummary` (source_type,
  max_free_parameters) and `ResultPopulationSummary` (path, offline flags,
  richer outcome_counts).
- `lib/fixtures.ts` — typed `candidatesFunnel` accessor.

## Per-route panels

### `/` Command Center
- Six headline stat tiles (unchanged set, kept).
- **New:** Queue-by-status distribution bar + approval/blocked/failed badges,
  with "View jobs →" navigation.
- **New:** Product-runs card (run count, advisory packets, blocked/failed,
  real-runner runs) with advisory-only disclaimer.
- Paper/Live cards now tone-mapped via `toneForStatus`.
- **New:** `BoundaryNotes` panel (warnings/withheld/unavailable) + provenance footer.

### `/research` Research Lab
- **New:** Stat tiles (queue/product/populations/strategies).
- **New:** Pipeline-state distribution bar + approval/blocked/advisory badges.
- Section navigation cards (kept).

### `/research/jobs`
- **New:** Queue summary as status distribution bar + count badges.
- **New:** Per-run cards — status chip, source idea, symbol/timeframe/requested-by,
  approval-needed (kind + scope, visibility-only), blocked reasons,
  dry-run notification-preview disclaimer.
- **New:** `BoundaryNotes` + explicit "status only, no controls" note.

### `/research/result-populations`
- **New:** Stat tiles — populations, total committed denominator, total result
  rows (with match hint).
- **New:** Aggregate outcome distribution (StackedBar across all populations).
- **New:** Per-population cards — validator/review status chips (fixes prior
  `"PASS"` vs `"passed"` tone bug via `toneForStatus`), rows-vs-committed badge,
  execution-mode + offline/no-runtime/no-paper-live badges, per-RP outcome bar.
- Withheld per-trade note + `BoundaryNotes`.

### `/strategies`
- **New:** Stat tiles — total, not-executable, executable.
- **New:** Richer cards — status chip, not-executable badge, source_type,
  instrument_family, market_type, primary_timeframe, direction,
  free-parameter count / max. Navigation to detail preserved.
- `BoundaryNotes`.

### `/strategies/[strategy_id]`
- **Enriched:** status + not-executable badges in header; added short_name,
  source_type, max_free_parameters rows. Deferred deep panels kept as placeholders.

### `/candidates`
- **New:** Stat tiles — registered, admitted, winner-only-view, paper/live built.
- **New:** Product candidate funnel (CSS funnel bars) with routing note.
- **New:** Registry by-status and by-overall-verdict distribution bars.
- **New:** Explicit paper/live unavailable + no-authority card. `BoundaryNotes`.

### `/reports/*` (via `ReportView`)
- **Enriched:** headline stat tiles kept; nested count groups (by_overall_state)
  now rendered as distribution bars; **new** edge-search-hold card, withheld-
  statistics badges, caveats list, charting-withheld note, descriptive-only
  posture badge. `BoundaryNotes` added.

### `/system`
- **New:** Health summary card (status/posture badges, slice status, rows,
  gaps, duplicate rows, paper/live status). Section cards kept.

### `/system/data`
- **New:** Status/posture/freshness badges; committed data-slice facts
  (dataset, venue/symbol, market type, timeframe, rows/expected, range);
  rows-match / gaps / duplicates badges; paper-runtime & live-mode cards;
  warnings.

### `/system/validators`
- **New:** Latest-validation status + freshness badges, report ref + sha;
  D3 validation / D2 import report rows with status chips.

### `/system/provenance`
- **New:** Provenance status + freshness + source-ref badges; source artifact
  inventory list (artifact id/type/path/sha256).

### `/agent-inbox`, `/paper`, `/live`
- Unchanged — already honest placeholders with unavailable / GO-gated /
  read-only status, boundary text, and future-runway notes. Left intact to
  avoid churn; they already meet the placeholder requirements.

## Deferred panels (kept as scaffolds, no fabricated data)
- `/research/families`, `/research/blockers`, `/research/robustness`,
  `/reports/strategy-review`, `/reports/main`, `/system/blockers`, and the
  strategy-detail deep panels (Variants / WFO / Robustness / Artifacts).
