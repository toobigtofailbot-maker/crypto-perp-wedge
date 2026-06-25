# WP-LAB-DOCS-COMPLETION-MAP-01 — Repo-truth discovery

Docs-only package. This file records the committed repo truth inspected to write
`docs/research/LAB_COMPLETION_MAP.md`. No implementation files were read for
modification; nothing was executed against research artifacts.

## Effective base

Branch `claude/stupefied-driscoll-dbcd22` off `main` at commit `9e8ed40`
(Merge PR #571). Recent merges in base:

- #568 — `WP-LAB-COORDINATOR-STATE-MODEL-01` (read-only coordinator state model)
- #569 — `WP-LAB-RESULTS-DASHBOARD-01` (read-only results dashboard)
- #570 — `WP-LAB-OPERATOR-BRIEF-REPORT-01` (read-only brief / weekly report)
- #571 — `WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01` (inert default-off scheduler shell)
- #572 — `WP-LAB-APPROVAL-QUEUE-SURFACE-01` (read-only approval / gate queue)

`WP-LAB-OPERATOR-SURFACE-INTEGRATION-01` (#573) and
`WP-LAB-STATE-MODEL-COVERAGE-AUDIT-01` (#574) are open at time of writing and are
**not** in this base; they are noted as in-flight, not claimed as built here.

## Research docs inspected

| Doc | Repo truth captured |
| --- | --- |
| `docs/research/LAB_COORDINATOR_STATE_MODEL.md` | Read-only pipeline stage model (`idea_intake → … → operator_gate`), state vocabulary (no new names), reason codes, artifact-ref model, resolver precedence, `H-FUNDING-RATE-POSITIONING-FADE-01` binding, non-authority + edge-search hold. Impl: `tools/lab_state/`. |
| `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md` | Read-only projection of state model; full denominator (not winners-only); no executable controls; deterministic; `tools/lab_dashboard/`. |
| `docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md` | Read-only daily brief / weekly report shaping the dashboard projection; descriptive-only; charting deferred; `tools/lab_reporting/`. |
| `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md` | Read-only approval/gate queue; displays gates, does not execute them; honest NO-GO/blocked state; `tools/lab_approval_queue/`. |
| `docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md` | Inert default-off control-plane shell; no executor; only output is a planned no-op; every autonomy flag defaults False; `tools/lab_scheduler_shell/`. |
| `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` | `H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO`; 36/36 rows fail 20% drawdown screen; scratch-only/non-canonical; no candidate registered; explicit drift guardrail (NO-GO does not authorize new edge-search). |
| `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md` | Non-canonical OOS gate input; `gate_decision ∈ {pass,fail,blocked,advisory_only}`; no approval/promotion authority. `tools/oos_gate/`, `tools/walkforward/`. |
| `docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md` | Family-agnostic Result Population replay normalization; `tools/research_replay`. |
| `docs/research/GENERIC_ROBUSTNESS_REVIEW_REACH_CONTRACT.md` | Robustness review reach + `NO_GO_*` / `BLOCKED_*` reason codes consumed by surfaces. |
| `docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md` | "Side 12" / target operating model: lifecycle, L0–L5 autonomy levels, anti-overfit controls, protected boundaries, human gates. Documentation-only; no implementation authority. |

## Status entries inspected

`docs/status_entries/WP-LAB-COORDINATOR-STATE-MODEL-01.md`,
`WP-LAB-RESULTS-DASHBOARD-01.md`, `WP-LAB-OPERATOR-BRIEF-REPORT-01.md`,
`WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01.md`, `WP-LAB-APPROVAL-QUEUE-SURFACE-01.md`,
plus walk-forward / OOS / replay / robustness / candidate-lifecycle entries for
the evaluation-rigor and artifact lineage.

## Tooling present (read-only inventory, not modified)

`tools/lab_state`, `tools/lab_dashboard`, `tools/lab_reporting`,
`tools/lab_approval_queue`, `tools/lab_scheduler_shell`, `tools/oos_gate`,
`tools/walkforward`, `tools/research_replay`, `tools/robustness`,
`tools/research_query` (query layer + `views.sql`), `tools/candidate_lifecycle`
(`lifecycle_engine.py`, `build_candidate_review_packet.py`,
`canonical_crossing_build.py`), `tools/research_runner`,
`tools/research_automation`.

## Key boundary facts extracted

- Every lab surface (state model, dashboard, brief/report, approval queue,
  scheduler shell) is **read-only / descriptive** and carries a
  `non_authority_declaration` + `edge_search_hold` note.
- The only "action" anywhere in the surface stack is the scheduler shell's
  planned **no-op** (`executed: false`).
- The candidate-lifecycle engine exists but is **human-gated**; no candidate is
  registered and no canonical crossing has occurred (`nothing_candidate_ready`).
- The single end-to-end research conclusion to date is a **NO-GO**.
- No new edge-search is authorized by any committed surface or conclusion.
