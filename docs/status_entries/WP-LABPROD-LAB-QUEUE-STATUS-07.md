# WP-LABPROD-LAB-QUEUE-STATUS-07 Status

## Decision

`FOLLOW_UP_REQUIRED`

## Summary

Adds read-only operator queue/status visibility for product pipeline runs. The surface reads existing pipeline state, runner adapter, and gates advisory packet artifacts; shows Karl approval points; distinguishes awaiting approval from blocked; and marks advisory packet availability when a completed advisory packet exists.

## Changed Files

- `tools/lab_pipeline/queue_status.py`
- `tests/test_lab_pipeline_queue_status.py`
- `docs/research/LAB_PRODUCTIZATION_LAB_QUEUE_STATUS.md`
- `docs/status_entries/WP-LABPROD-LAB-QUEUE-STATUS-07.md`
- `scratch/WP-LABPROD-LAB-QUEUE-STATUS-07/*`

## Boundary

No notification firing, autonomous dispatch, scheduler activation, job execution controls, runner invocation, gates invocation, provider/API use, credential use, canonical evidence write, candidate lifecycle write, crossing, promotion/readiness, paper/live/runtime contact, dependency/config/data-acquisition change, or protected-path touch is introduced.

## Validation

Validation details are recorded in `scratch/WP-LABPROD-LAB-QUEUE-STATUS-07/validation_summary.txt`.

Package-focused validations passed. Follow-up is required because the working tree also contains unrelated WP-LABPROD-BOUNDED-SWEEP-SCALE-06 / runner-gates adapter changes not authored in this package, and full pytest timed out before completion.
