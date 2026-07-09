# WP-LABPROD-COCKPIT-REALRUN-REFRESH-08 — Cockpit refresh for real product runs

Status: READY_FOR_REVIEW

## Scope

Refresh the merged static lab product cockpit (`tools/lab_cockpit`) so it displays
the **real** end-to-end product pipeline output (product bridge prepare → product
runner adapter (PR #623) → product gates adapters (PR #624) → advisory review
packet) instead of only the legacy spine-only orchestrator placeholders. Read-only
and additive: no run/approve/execute/promote/candidate control, and existing
cockpit panels/tests are unchanged.

## Hard dependency

PR #624 is merged on `main` (HEAD `129bb28`). The gates adapter produces advisory
review packets (`product_pipeline_advisory_review_packet_v1`); runner + gates
schemas are discoverable. See `scratch/.../repo_truth_discovery.md`.

## Result

- `tools/lab_cockpit/model.py` — additive `build_product_pipeline_runs(...)`
  projection over committed real product-run fixtures, plus
  `build_product_candidate_funnel(...)`; honest state vocabulary (no run /
  awaiting approval / prepared / executed / advisory packet ready /
  blocked-failed); withheld-statistics, robustness, and candidate-review
  projection helpers that read the real advisory packet; new product non-authority
  flags; spine-only supersession note wired into `pipeline_state`; both wired into
  `build_cockpit_data`.
- `tools/lab_cockpit/render.py` — additive **Product pipeline · real runs** HTML
  panel (KPI strip, state-vocabulary legend, run cards with provenance, stage
  ladder, real-runner callout, withheld/missing statistics table, robustness
  diagnostics, advisory candidate-review, advisory surface-routing callout,
  artifact drilldown) and a **Product candidate funnel** panel; matching markdown
  sections; spine-only banner now shows the real-run supersession note. New CSS
  only — no controls.
- `tests/test_lab_cockpit_product_runs.py` — 22 focused tests, including a
  contract test that drives the **real** product chain into a temp dir and
  asserts the projection tracks the actual advisory-packet shape.
- `docs/research/LAB_PRODUCTIZATION_COCKPIT_REALRUN_REFRESH.md` — surface doc.
- `scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/**` — repo-truth discovery,
  reproducible fixture generator, committed deterministic real-run fixture,
  rendering + no-controls evidence, non-authority assertions, validation summary,
  built cockpit output.

## Required behavior satisfied

- **States distinguished.** The panel enumerates all six honest states; the
  committed run reaches the terminal `advisory_packet_ready` via a full stage
  ladder; missing directory / empty directory fail closed to `no_run`; malformed
  `run_index.json` renders a `blocked_or_failed` fail-closed card.
- **Backed by real artifacts.** Every number is read from a committed real
  advisory packet produced by the real adapters (denominator 8/8 completed,
  direct-agent reconciliation passed).
- **Missing stats shown missing, never zero.** WFO/OOS renders as a blocked /
  withheld gate; per-trade, oos-walkforward, and funding-stress sections show
  explicit statuses with `fabricated = false`.
- **Funnel implies no admission.** Product candidate funnel terminates at
  `Candidates admitted = 0`; advisory `surface_status` is labelled review-routing
  only.
- **GO-like → review-needed only.** `go_auto_admission / crossing / promotion`
  and `candidate_lifecycle_written` are surfaced as `false`; non-promotion posture
  is shown.

## Boundary

Read-only static cockpit. No controls, approval actions, notifications,
scheduler/autonomy, canonical writes, candidate lifecycle, crossing,
promotion/readiness, paper/live/runtime, provider/API, or protected-path touch.
Non-authority assertions committed at
`scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/non_authority_assertions.json`.

## Validation

See `scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/validation_summary.txt`.
