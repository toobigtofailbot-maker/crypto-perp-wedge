# Fixture matrix

All fixtures are non-production package artifacts under this directory. Invalid case fixtures name a valid base plus deterministic mutations so each rejection remains narrow and reviewable.

## Valid

| Fixture | Contract proved |
| --- | --- |
| `valid/dispatch_record.json` | immutable dispatch identity, exact authority/input/output binding, no retry, no RP authority |
| `valid/run_start.json` | sequence-1 invocation start and exact dispatch binding |
| `valid/attempt_successful.json` | successful terminal attempt |
| `valid/attempt_failed.json` | failed terminal attempt retained in denominator |
| `valid/attempt_errored.json` | errored terminal attempt retained in denominator |
| `valid/terminal_completed.json` | all 81 attempts and outcomes accounted |
| `valid/terminal_process_start_failure.json` | zero attempts; 81 explicitly not attempted |
| `valid/terminal_midrun_failure.json` | 20 attempts retained; 61 explicitly not attempted |
| `valid/terminal_blocked.json` | fail-closed terminal with partial progress retained |

Tests synthesize complete ordered JSONL streams from these line fixtures without writing any production stream.

## Invalid

| Case | Intended rejection |
| --- | --- |
| `bad_hash.case.json` | malformed tagged SHA-256 |
| `missing_queue_binding.case.json` | required exact queue binding absent |
| `free_form_executable_command.case.json` | arbitrary command surface forbidden |
| `unknown_event_state.case.json` | event vocabulary closed |
| `unknown_terminal_state.case.json` | terminal vocabulary closed |
| `not_attempted_attempt_outcome.case.json` | `not_attempted` is terminal denominator accounting only, never an attempt outcome |
| `go_readiness_vocabulary.case.json` | GO/readiness field forbidden by closed object |
| `completed_denominator_mismatch.case.json` | completed actual does not equal denominator |
| `midrun_claiming_full_completion.case.json` | midrun state falsely claims full completion |
| `retry_allowance_inconsistent.case.json` | v1 retry allowance must be zero |
| `mutable_progress_in_dispatch.case.json` | dispatch cannot own progress |
| `canonical_rp_authority_claim.case.json` | canonical RP write remains forbidden |
