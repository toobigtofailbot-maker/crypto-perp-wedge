# WP-LAB-DASHBOARD-GAP-COMPLETE-01 — Repo Truth Discovery

## Base commit

`cbbca34fa62dabcb17c81bbf25c264f0dcb64b56` (Merge pull request #587)

## PR #583-#587 artifacts observed

All hard-dependency artifacts confirmed present on `main`:

| Artifact | Path | Present |
| --- | --- | --- |
| baseline_payload_catalog.json | scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json | yes |
| baseline_gate_expectations.json | scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json | yes |
| guard_validation_summary.json | scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_validation_summary.json | yes |
| baseline_loop_result.json | scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/baseline_loop_result.json | yes |
| no_candidate_review_result.json | scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/no_candidate_review_result.json | yes |
| crossing_rejection_result.json | scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/crossing_rejection_result.json | yes |
| completion_state_update.json | scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/completion_state_update.json | yes |
| held_boundary_map.json | scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json | yes |
| LAB_COMPLETION_MAP.md | docs/research/LAB_COMPLETION_MAP.md | yes |
| WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01.md | docs/status_entries/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01.md | yes |

## Current dashboard outputs and commands

- Dashboard command: `python -m tools.lab_dashboard.run --out-dir build/lab_dashboard`
- Alternate modes: `--data-json`, `--html`, `--markdown`
- Reporting command: `python -m tools.lab_reporting.run --out-dir build/lab_reporting --as-of 2026-06-29 --period 2026-W26`

Current output (pre-change): 9 subjects, 41 tests passing.

## Existing panels/views

1. **Denominator summary** — full population by overall state, completed/no-go/blocked/candidate-ready/operator-gate counts
2. **Trial denominator** — planned/complete/failed/invalid/blocked/pruned over distinct Result Population sets
3. **Caveats** — global non-authority caveats (6 items)
4. **Per-subject views** — evidence class, denominator, replay, OOS gate, robustness, candidate review, reporting, operator gate, result populations, NO-GO caveats, artifact drill-down

## Actual missing Side 12 dashboard views

| View | Status |
| --- | --- |
| Strategy detail drill-down | MISSING — baseline construction payloads not surfaced |
| Sweep-grid / population table | MISSING — no aggregate baseline grid with gate expectations |
| WFO/OOS gate posture (aggregate) | MISSING — per-subject only, no baseline posture panel |
| MC/robustness posture (aggregate) | MISSING — per-subject only, no baseline posture panel |
| Blockers / withheld (aggregate) | PARTIAL — per-subject withheld; no aggregate baseline view |
| Agent activity / baseline-loop | MISSING — PR #586 loop results not surfaced |
| Data/provenance (baseline PRs) | MISSING — PR #583-#587 provenance trace absent |
| Candidate/no-candidate state | MISSING — per-subject only; no explicit no-candidate authority panel |
| Non-authority caveats | PRESENT — 6 global caveats already in caveats array |
| Held-boundary / deferred-B | MISSING — held_boundary_map.json not surfaced |
| Completion proof summary | MISSING — completion_state_update.json not surfaced |

## Selected files for update

- `tools/lab_dashboard/data_model.py` — add baseline_proof_panel, held_boundary_panel
- `tools/lab_dashboard/render.py` — add rendering for new panels
- `tests/test_lab_dashboard.py` — add tests for new panels

## Files intentionally left unchanged

- `tools/lab_state/**` — state model is authoritative; no changes needed
- `tools/lab_reporting/**` — reporting shaping layer; no changes needed
- `tools/lab_approval_queue/**` — approval queue surface; no changes needed
- `research/**`, `lib/**`, `configs/**`, `data/**` — forbidden
- `requirements*.txt`, `pyproject.toml` — no dependency changes

## Non-authority confirmation

This dashboard remains read-only and non-authoritative. All new panels are
descriptive-only projections of committed scratch artifacts. No panel:
- executes a strategy, backtest, or sweep
- creates candidate or canonical evidence
- ranks, recommends, or declares readiness
- touches paper/live/runtime paths
- adds dependencies
