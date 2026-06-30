# WP-LAB-QUEUE-SCHEDULER-REPLAY-01 Repo Truth Discovery

## Base

- Base branch: `main`
- Base commit: `77f1a98420a3b87fd207f7291efcc2aafaa8fbb2`
- Working branch: `lab/queue-scheduler-replay-01`
- Pre-existing untracked local artifact observed before package work: `build/`

## PR #592 artifacts observed

- `docs/research/LAB_EVENT_TAPE_CONTRACT.md`
- `docs/status_entries/WP-LAB-EVENT-TAPE-CONTRACT-01.md`
- `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/event_tape_schema.json`
- `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json`
- `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_tape_summary.json`
- `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/non_authority_assertions.json`
- `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/validator_result.json`
- `tools/lab_event_tape/validate.py`

## Surfaces discovered

- Queue surface discovered: `tools/lab_approval_queue/**`
- Scheduler shell surface discovered: `tools/lab_scheduler_shell/**`
- Event tape surface discovered: `tools/lab_event_tape/**`
- Tests surface discovered: `tests/**`
- Scratch evidence surface discovered: `scratch/**`
- Status-entry surface discovered: `docs/status_entries/**`

## Replay route selected

Decision: use a package-local replay interpreter in `tools/lab_event_tape/replay_queue_scheduler.py`.

Fact: the scheduler shell exposes safe inert dry-run planning for scheduler queue fixtures, while the approval queue projects committed lab-state subjects. The reference event tape is a different contract shape: it carries per-event `expected_operating_outcome.queue_action` and `expected_operating_outcome.scheduler_action`.

Inference: direct coupling to `tools/lab_approval_queue/**` or `tools/lab_scheduler_shell/**` would require adapter semantics not already exported by those packages.

Decision: do not modify queue or scheduler shell shared behavior. Interpret the event tape locally, validate it first with `tools.lab_event_tape.validate`, derive dry-run queue/scheduler actions by event type and state transition, and compare derived observations to the event-tape expected outcomes.

## Files intentionally left unchanged

- `tools/lab_approval_queue/**`
- `tools/lab_scheduler_shell/**`
- `tools/lab_dashboard/**`
- `tools/lab_reporting/**`
- `tools/lab_state/**`
- `tools/registry/**`
- `tools/research_runner/**`
- `tools/candidate_lifecycle/**`
- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `lib/**`
- `configs/**`
- `data/**`
- dependency files
- runtime, paper/live, OMS, risk, reconciliation, broker, exchange, and order paths

## Boundary statements

- No autonomous scheduler was activated.
- Replay outputs are operating-test evidence only.
- No live dispatch was performed.
- No strategy run, edge search, real research job, candidate write, crossing, promotion, readiness, canonical Result Population write, notification send, report/dashboard replay, or agent-loop replay was performed.
