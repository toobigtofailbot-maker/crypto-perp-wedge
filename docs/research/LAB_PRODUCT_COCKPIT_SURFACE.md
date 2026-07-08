# Lab Product Cockpit Surface

Static, read-only, product-grade operator cockpit over concluded lab evidence.
Implemented by `tools/lab_cockpit` (`model.py` / `render.py` / `run.py`).

## Purpose

Make the existing lab evidence usable and inspectable at a glance for an
operator, without adding any execution authority. The cockpit is deliberately
richer than the existing text/table results dashboard
(`docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`): it adds inline SVG chart
visualizations, a strategy explorer, a candidate funnel, and an evidence
timeline, while remaining a pure static projection.

It is a **beautiful read-only cockpit**. It builds no approval, run, promote,
candidate, or scheduler control. Approval actions belong to a later gate-actions
package after the orchestrator state contract exists.

## Data sources (read-only)

- Merged **coordinator state model** (`tools/lab_state`), reused via the existing
  `tools/lab_dashboard` data model, for lab-wide state, the subjects-by-state
  summary, and the held-boundary / deferred-B map.
- Concluded **real-traffic four-hypothesis batch** (PR #606 / #608 / #609):
  - `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/revised_batch_final_rollup.json`
    (authoritative per-hypothesis metrics),
  - `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`
    (frozen-set metadata, GO/NO-GO definitions, pass-with-caution context),
  - the batch-execute and HYP-002R-completion strategy readings, walk-forward,
    robustness, denominator-audit and non-authority artifacts,
  - `docs/research/LAB_REAL_TRAFFIC_BATCH_SYNTHESIS_2026-07.md`.

Every number rendered is read from a committed artifact. Missing artifacts fail
closed to an explicit `withheld` / `unavailable` state; nothing is fabricated.

## Panels

1. **Lab overview** — KPI strip (frozen rows, preserved, executed, positive
   median-PnL hypotheses, GO-like = 0, candidate-ready = 0) and top blockers.
2. **Candidate funnel** — full denominator (`frozen → executed → positive median
   PnL → GO-like → candidate-ready`); narrows honestly to zero candidate-ready.
3. **Strategy / hypothesis explorer** — one card per frozen hypothesis with a
   status pill, drawdown meter, positive-row pips, WFO/MC chips, and the
   committed strategy reading.
4. **Visual result panels** — inline SVG: median-PnL diverging bars, drawdown
   severity bars, positive-row bars, and the non-promoting-reason callout.
5. **Robustness · WFO / OOS** — withheld statistics (Monte-Carlo / bootstrap /
   PSR / DSR / MinTRL) shown explicitly; dry-run walk-forward flagged as **not a
   rigorous OOS gate pass**.
6. **Activity / evidence timeline** — committed PR #600 → #606 → #608 → #609
   sequence, no live refresh.
7. **Coordinator state · held boundary** — subjects-by-state, subject list, and
   the deferred-B / GO-gated boundary.
8. **Artifact drilldown** — repo-relative paths with present/missing indicators
   and source-category labels.
9. **Boundary · non-authority** — committed batch assertions plus the cockpit's
   own non-authority declaration.

## Reading of the current evidence

- Full denominator: 32 rows (4 hypotheses × 8 variants); all preserved, none
  dropped/blocked; no winner-only pruning.
- No hypothesis is GO-like or candidate-worthy. HYP-001 / HYP-002R / HYP-004R
  show positive PnL surfaces but fail the primary drawdown screen (~77%);
  HYP-003R is a clean NO-GO (0/8 positive, ~99% drawdown).
- No canonical Result Population was written; evidence is dry-run / package-local.
- Monte-Carlo / bootstrap withheld; PSR / DSR / MinTRL not computed.

## CLI

```powershell
python -m tools.lab_cockpit.run --out-dir build/lab_cockpit   # data + html + md
python -m tools.lab_cockpit.run --html
python -m tools.lab_cockpit.run --data-json
python -m tools.lab_cockpit.run --markdown
```

The `--out-dir` form writes `cockpit_data.json`, `cockpit.html`, and
`cockpit.md`; the page is usable directly from a local file or static output
directory.

## Static / no-control guarantees

- Static only: no server, live fetch, network, background daemon, auto-refresh,
  form submission, or JavaScript.
- The rendered HTML contains no `<script>`, `<button>`, `<form>`, `<input>`,
  `onclick`, meta refresh, or external network reference.
- Deterministic: two builds over the same checkout are byte-identical.

## Non-authority

Static read-only visualization only. This surface grants no run, approval,
promotion, candidate, crossing, paper/live/runtime, scheduler, notification,
provider/API, credential, dependency, data, or protected-path authority. Any real
transition or approval requires separate human action through the candidate
lifecycle engine; this cockpit cannot grant it.
