# WP-LAB-EVENT-TAPE-CONTRACT-01 Repo Truth Discovery

## Base

- Base commit: `114857be663085bfdbda264cc881ab252121b7b5`
- PR #591 merged on refreshed main: yes
- Pre-existing dirty state before package work: untracked `build/` directory observed; left unchanged.

## Required Artifacts Observed

- PR #583-#591 lab artifacts observed through refreshed `docs/project_status.md`, `docs/research/LAB_COMPLETION_MAP.md`, status entries, and required scratch artifacts.
- `docs/research/LAB_COMPLETION_MAP.md`: present
- `docs/status_entries/WP-LAB-SIDE12-COMPLETION-FINAL-MAP-01.md`: present
- `scratch/WP-LAB-SIDE12-COMPLETION-FINAL-MAP-01/final_decision_state.json`: present
- `scratch/WP-LAB-SIDE12-COMPLETION-FINAL-MAP-01/final_capability_map.json`: present
- `scratch/WP-LAB-SIDE12-COMPLETION-FINAL-MAP-01/known_payload_proof_boundary.json`: present
- `scratch/WP-LAB-SIDE12-COMPLETION-FINAL-MAP-01/held_b_structural_reasons.json`: present
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/synthetic_population_manifest.json`: present, `sha256:c653f61feb4a5dfee60c7031df3073c9f1beedf33725ae1175919e64e0de7c5e`
- `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/factorytest_result.json`: present

## Surfaces Discovered

- Queue surface: `tools/lab_approval_queue/**`
- Scheduler surface: `tools/lab_scheduler_shell/**`; exact `tools/lab_scheduler/**` path was not present
- Reporting surface: `tools/lab_reporting/**`
- Dashboard surface: `tools/lab_dashboard/**`
- Agent/lab-state surface: `tools/lab_state/**` and lab status artifacts; no replay integration selected
- Registry surfaces: `tools/lab_registry/**` and `tools/registry/**`

## Selected Routes

- Contract location: `docs/research/LAB_EVENT_TAPE_CONTRACT.md`
- Schema location: `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/event_tape_schema.json`
- Fixture location: `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json`
- Validator route: `tools/lab_event_tape/validate.py`
- Focused tests: `tests/test_lab_event_tape_contract.py`
- Source-reference validation mode: strict row-reference validation against the #588 synthetic population manifest

## Files Intentionally Left Unchanged

- `tools/lab_state/**`
- `tools/lab_dashboard/**`
- `tools/lab_reporting/**`
- `tools/lab_approval_queue/**`
- `tools/lab_scheduler_shell/**`
- `tools/lab_registry/**`
- `tools/registry/**`
- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `lib/**`
- `configs/**`
- `data/**`
- runtime, paper/live, OMS, risk, reconciliation, order, exchange, and broker paths

## Authority Statement

This package creates no replay behavior. It does not run queue/scheduler, notification/reporting, dashboard, agent-loop, registry replay, strategy execution, backtest, sweep, WFO/OOS, MC, crossing, promotion, paper/live, or runtime paths. Event-tape artifacts are operating-test evidence only; they are not strategy evidence, candidate evidence, edge evidence, crossing authority, promotion authority, or paper/live authority.
