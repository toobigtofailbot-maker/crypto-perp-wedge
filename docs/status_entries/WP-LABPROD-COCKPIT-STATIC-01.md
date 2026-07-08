# WP-LABPROD-COCKPIT-STATIC-01 — Static lab product cockpit

Status: READY_FOR_REVIEW

## Scope

Build the first product-grade, visually polished, read-only lab cockpit
(`tools/lab_cockpit`). It projects committed lab evidence — the merged
coordinator state model and the concluded real-traffic four-hypothesis batch —
into a single deterministic static page with inline SVG chart visualizations.

## Result

- New module `tools/lab_cockpit/` (`model.py`, `render.py`, `run.py`,
  `__init__.py`) with a deterministic `lab_product_cockpit_v1` data model and an
  operator-grade static HTML/CSS/SVG renderer plus a markdown renderer.
- CLI: `python -m tools.lab_cockpit.run --out-dir build/lab_cockpit` (and
  `--html` / `--data-json` / `--markdown`).
- New surface doc `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md`.
- Focused tests `tests/test_lab_cockpit.py` (22 tests).

## Visual panels delivered

Lab overview (KPI strip + blockers); candidate funnel (full denominator,
narrows to zero candidate-ready); strategy / hypothesis explorer (per-hypothesis
cards with drawdown meters, positive-row pips, WFO/MC chips, readings); visual
result panels (SVG median-PnL diverging bars, drawdown severity bars,
positive-row bars); robustness · WFO/OOS (withheld statistics explicit; dry-run
walk-forward flagged as not a rigorous gate pass); activity/evidence timeline
(PR #600 → #609); coordinator state · held boundary; artifact drilldown;
boundary · non-authority.

## Static / no-control boundary

Static only — no server, live fetch, network, background daemon, auto-refresh,
form submission, or JavaScript. The rendered HTML contains no `<script>`,
`<button>`, `<form>`, `<input>`, `onclick`, meta refresh, or external network
reference. Output is byte-deterministic for the same checkout. Withheld
statistics are labelled; candidate-ready stays zero; no canonical Result
Population is claimed; the full 32-row / four-hypothesis denominator is always
shown.

## Parallel safety

Only package-allowed paths were touched (`tools/lab_cockpit/**`,
`tests/test_lab_cockpit.py`, `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md`,
this status entry, `scratch/WP-LABPROD-COCKPIT-STATIC-01/**`). No orchestrator,
readiness-display, paper-handoff, scheduler/queue, approval-action, candidate
lifecycle, canonical evidence, or protected paths were touched. The existing
`tools/lab_dashboard` and `tools/lab_state` modules are reused read-only and
unmodified. `docs/project_status.md` and `docs/research/LAB_COMPLETION_MAP.md`
are intentionally not updated by this package.

## Validation

- `python -m pytest tests/test_lab_cockpit.py -q` → 22 passed.
- No regression: `tests/test_lab_dashboard.py`,
  `tests/test_lab_state_model.py`, `tests/test_lab_state_resolver.py` → 48
  passed.
- `python -m tools.lab_cockpit.run --out-dir build/lab_cockpit` → writes data /
  html / md.
- `python -m tools.research_query.run --list-views`,
  `python -m tools.registry.validate_result_populations`,
  `python -m tools.registry.validate_candidate_registry` → OK.
- `git diff --check` → clean.
- Pre-existing/unrelated: `tests/test_lab_state_coverage_audit.py` shows the same
  3 failed / 12 errors on pristine main (126d9aa) as on this branch — an existing
  `unknown supplemental artifact role: riskmanaged_conclusion_evidence` in
  `tools/lab_state/run.py`, untouched by this package.

## Non-authority

Claude Code cockpit package; static read-only visualization only; no run,
approval, promotion, candidate, crossing, paper/live/runtime, scheduler,
notification, provider/API, credential, dependency, data, or protected-path
authority.
