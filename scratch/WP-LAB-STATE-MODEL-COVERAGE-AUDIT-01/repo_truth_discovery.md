# Repo-truth discovery — WP-LAB-STATE-MODEL-COVERAGE-AUDIT-01

Read-only discovery for the coordinator state-model / operator-surface coverage
audit. No artifact was mutated. Counts are over **git-tracked** files only.

## Dependencies (all merged into base `9e8ed40`)

| PR | Package | Present |
| --- | --- | --- |
| #568 | coordinator state model (`tools/lab_state/`) | yes |
| #569 | results dashboard (`tools/lab_dashboard/`) | yes |
| #570 | brief/report surface (`tools/lab_reporting/`) | yes |
| #571 | scheduler shell (`tools/lab_scheduler_shell/`) | yes |
| #572 | approval queue (`tools/lab_approval_queue/`) | yes |

`git merge-base --is-ancestor 4a3d734 HEAD` → true (PR #572 in base). Not blocked.

## How the operator view is wired

All four operator surfaces resolve state from **one** source: the
`SUBJECTS` dict in `tools/lab_state/run.py`.

- `tools/lab_dashboard/data_model.py` imports `SUBJECTS` and builds a view per subject.
- `tools/lab_reporting/report_model.py` consumes `build_dashboard_data` (same subjects).
- `tools/lab_approval_queue/queue_model.py` imports `SUBJECTS`.
- `tools/lab_scheduler_shell/shell.py` validates run-queue `subject_id`s against
  `frozenset(s["subject_id"] for s in SUBJECTS.values())`.

So **operator-visible coverage == the set of subjects bound in `SUBJECTS`**.
There are exactly two:

1. `funding_positioning_fade_no_go` — `H-FUNDING-RATE-POSITIONING-FADE-01`, overall `no_go`.
2. `oos_gate_fail_demo` — `OOS-GATE-FIXTURE-RP-2592`, exercises `oos_gate_fail`.

### Coordinator-referenced artifact paths (8, derived from `SUBJECTS`)

Surface-rendered (shown as content in dashboard/report/approval):
- `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` (reporting)
- `docs/research/WALKFORWARD_OOS_GATE_CONTRACT.md` (reporting)
- `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json` (experiment/robustness)
- `scratch/WP-LAB-GENERIC-ROBUSTNESS-REVIEW-REACH-01/generic_review_contract.json` (candidate_review_reach)

Consulted for state only (presence/parse drives a stage state, not rendered as content):
- `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md` (formalization)
- `docs/status_entries/WP-LAB-WALKFORWARD-OOS-GATE-01.md` (formalization, subject 2)
- `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/replay_fixture_summary.json` (replay)
- `scratch/WP-LAB-WALKFORWARD-OOS-GATE-01/fixture_gate_summary.json` (oos gate, subject 2)

The coordinator is **deliberately narrow** (`LAB_COORDINATOR_STATE_MODEL.md`):
one end-to-end NO-GO binding plus one OOS-fail fixture, with edge-search held.

## Committed-artifact universe (git-tracked)

| Root | Files |
| --- | --- |
| `docs/research` | 10 |
| `docs/status_entries` | 170 |
| `research` | 745 |
| `scratch` | 356 |
| **total (audited roots)** | **1281** |

`research/` breakdown (top dirs): briefs 441, reconciliations 51, experiments 44,
outcome_ledgers 32, schemas 32, lifecycle_changes 30, hypotheses 23, decisions 12,
audits 11, overlay_shadow_logs 10, result_populations 8, sweep_plans 6,
strategy_specs 6, variant_manifests 6, data_slices 6, plus singletons
(`candidate_registry.jsonl`, `trial_log.jsonl`, etc.).

## Silent-evidence candidates (concluded research not bound to the coordinator)

These are committed *conclusions* (not edge-search process scratch) that the
operator view does not represent because `SUBJECTS` binds only two subjects:

- `scratch/WP-RESEARCH-FUNDING-CARRY-01/` — `no_candidate_review_packet_reason.json` (concluded, unbound)
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/` — `no_candidate_review_packet_reason.json`, `human_review_packet.json`, RP-2009/RP-7592 (concluded, unbound)
- `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/` — `sma_family_result_packet.json`, blocked reasons (concluded, unbound)
- `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/` — `orb_exit_respec_result_packet.json`, blocked reasons (concluded, unbound)
- `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/` + `docs/research/PRICEONLY_SYNTHESIS_2026-06.md` — synthesis, unbound
- `research/result_populations/**` (8) and `research/candidate_registry.jsonl` — canonical, unbound

Only `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`
is bound (subject 1). The rest are the audit's coverage-gap findings.

## Validators available

`python -m tools.research_query.run --list-views` → OK (20+ views).
Registry validators present under `tools/registry/` incl.
`validate_result_populations.py`, `validate_candidate_registry.py`.
