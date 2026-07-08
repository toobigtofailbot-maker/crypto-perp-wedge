# Repo-truth discovery — WP-LABPROD-COCKPIT-STATIC-01

Read-only inspection performed before building the static lab product cockpit.

## Preflight

- Current main SHA (worktree base): `126d9aa` (merge of PR #609,
  `lab/real-traffic-batch-conclude-01`).
- Branch: `claude/labprod-cockpit-static-5c8915` (harness-provisioned worktree at
  `.claude/worktrees/hungry-hermann-b0a7ce`).
- `gh pr list --state open` → `[]` (no open PRs; no collision on
  `tools/lab_cockpit/**`, `tests/test_lab_cockpit*.py`,
  `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md`,
  `docs/status_entries/WP-LABPROD-COCKPIT-STATIC-01.md`,
  `scratch/WP-LABPROD-COCKPIT-STATIC-01/**`).
- `tools/lab_cockpit/**` does not exist yet → building the preferred new module.

## Files inspected

Existing dashboard / state surfaces (reused read-only, not modified):

- `tools/lab_dashboard/data_model.py` — deterministic dashboard data model; reuses
  `tools/lab_state`. Exposes `build_dashboard_data`, `build_subject_view`,
  `DASHBOARD_NON_AUTHORITY`, held-boundary + baseline-proof panels.
- `tools/lab_dashboard/render.py` — static HTML/markdown renderers (tables only,
  no `<script>`/`<button>`/`<form>`).
- `tools/lab_dashboard/run.py` — CLI (`--data-json`/`--html`/`--markdown`/`--out-dir`).
- `tools/lab_state/model.py` — canonical state vocabulary, `OVERALL_STATES`,
  `NON_AUTHORITY_DECLARATION`, `EDGE_SEARCH_HOLD_NOTE`.
- `tools/lab_state/resolver.py` — read-only resolver → `build_snapshot`.
- `tools/lab_state/run.py` — `SUBJECTS` bindings over committed artifacts.
- `tests/test_lab_dashboard.py` — determinism / no-control / full-denominator
  test patterns (mirrored for the cockpit).

Real-traffic batch evidence (the cockpit's central new data — read-only):

- `docs/research/LAB_REAL_TRAFFIC_BATCH_SYNTHESIS_2026-07.md` — batch conclusion
  (PR #609): 32 frozen rows, 32 preserved, 0 dropped/blocked, 32 executed
  successful, canonical RP written = false, GO-like = false.
- `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/revised_batch_final_rollup.json`
  — authoritative final rollup after PR #608; per-hypothesis median PnL /
  drawdown / positive rows / trade counts / walk-forward for the four frozen
  hypotheses (HYP-001, HYP-002R, HYP-003R, HYP-004R).
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-SIGNOFF-FREEZE-01/revised_frozen_hypothesis_set.json`
  — frozen set: hypothesis names, family routes, economic rationale, GO/NO-GO
  definitions, `pass_with_caution` context, freeze conditions (PR #600).
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/strategy_reading_summary.json`
  — per-hypothesis strategy readings (PR #606; HYP-002R blocked there).
- `scratch/WP-LAB-REAL-TRAFFIC-REVISED-BATCH-EXECUTE-01/real_traffic_batch_manifest.json`
  — batch execute manifest (PR #606).
- `scratch/WP-LAB-REAL-TRAFFIC-HYP002R-COMPLETION-01/hyp002r_strategy_reading.json`,
  `hyp002r_wfo_oos_summary.json`, `hyp002r_robustness_mc_summary.json`,
  `hyp002r_denominator_audit.json`, `non_authority_assertions.json`,
  `operator_review_packet.md` — HYP-002R completion evidence (PR #608).

## Key facts carried into the cockpit (no fabrication)

- Full denominator = 32 rows (4 hypotheses x 8 variants); all preserved, none
  dropped/blocked; no winner-only pruning.
- No hypothesis produces GO-like or candidate-worthy evidence; candidate-ready = 0.
- No canonical Result Population written; evidence is dry-run / package-local.
- Monte-Carlo / bootstrap withheld (no package-local MC runner surface used);
  PSR / DSR / MinTRL not computed — surfaced as explicit withheld labels.
- Walk-forward is bounded dry-run (24 rows/hyp, 3 windows) — not a rigorous OOS
  gate pass.
- Per-hypothesis: HYP-001 6/8 positive, dd ~77.1%; HYP-002R 8/8 positive, median
  PnL ~56170, dd ~77.3%; HYP-003R 0/8 positive, median PnL ~-9801, dd ~99.0%;
  HYP-004R 8/8 positive, median PnL ~57715, dd ~77.3%. All non-promoting under
  the primary drawdown screen; HYP-003R is a clean NO-GO.

## Design decision

Create the preferred new module `tools/lab_cockpit/` (model / render / run) rather
than extending `tools/lab_dashboard`. The cockpit reuses
`tools.lab_dashboard.data_model.build_dashboard_data` read-only for the coordinator
state + held-boundary projection, and adds a richer real-traffic batch model plus
an SVG/CSS operator-grade static renderer. No orchestrator / readiness / scheduler
/ approval paths are touched.
