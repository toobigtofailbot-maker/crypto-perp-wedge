# Canonical Dispatch and Execution Control Plane

Status: locked Option-C design and schema contract for `WP-CANON-DISPATCH-CONTROL-PLANE-DESIGN-LOCK-01`.

This contract defines durable state for a one-shot offline-research dispatch. It creates no writer, dispatcher, runner adapter, scheduler, production dispatch, production execution event, or Result Population. Capitalized requirement words are normative.

## Decision and boundary

Option C is selected:

1. one immutable dispatch JSON record owns dispatch identity, exact authorization, and exact input/output bindings;
2. one append-only JSONL stream per run owns invocation start, every attempt outcome, and one terminal execution event;
3. the admitted queue item and admission audit remain immutable admission history;
4. provisional runner outputs remain scratch detail;
5. only a later separately gated Result Population package may create canonical scientific evidence.

Option A, mutating the queue item through execution states, is rejected because admission history is permanently `admitted_non_dispatched` and has no execution authority. Option B, a mutable execution-state document, is rejected because it would erase prior progress and failure transitions. Option C preserves the exact dispatch decision and every later execution fact without rewriting either history.

Dispatch and execution records are authoritative control-plane history only. They MUST NOT replace or claim authority for a Result Population, EXP, REP, outcome ledger, recommendation, decision, ranking, readiness, promotion, candidate lifecycle, scheduler, runtime, paper, or live surface. They MUST NOT contain GO, NO-GO, winner, candidate-worthy, readiness, or recommendation semantics.

## Directories and identities

| Artifact | Authoritative path | Identity |
| --- | --- | --- |
| Dispatch record | `research/queue/dispatch_records/<dispatch_id>.dispatch_record.json` | `DSP-YYYYMMDD-XXXXXXXX` |
| Execution stream | `research/queue/execution_events/<run_id>.execution_events.jsonl` | `RUN-YYYYMMDD-XXXXXXXX` |
| Execution event | one JSON object plus LF in the run stream | `EXEC-EVENT-<run_id>-NNNNNN` |
| Exact Karl authority reference | durable repo-relative source bound by the dispatch record | `KDAUTH-YYYYMMDD-XXXXXXXX` |

`XXXXXXXX` is eight uppercase alphanumeric characters. The dispatch date MUST equal the UTC date of `created_at`. Event sequence numbers start at 1, are contiguous and strictly increasing, and are rendered as six digits in the event ID. Paths are repo-relative POSIX paths with no traversal, backslashes, empty components, or symlink escape.

IDs, exact target paths, run IDs, event IDs, and queue-item/authorization pairs are permanently single-use. Removal of a file does not free an identity. A future writer MUST scan all current dispatch records, every execution line, durable Karl authorization sources, and retained repository history before crossing. An identity found in any one source is consumed. Missing or ambiguous history fails closed.

No production directory or instance is created by this design package.

## Immutable dispatch record

Normative schema: `research/schemas/canon_dispatch_record.schema.json`.

The record MUST bind:

- its derived dispatch ID/path, creation timestamp, and the sole state `dispatched`;
- one exact admitted queue item ID/path and raw-file SHA-256;
- the exact Gate-Q ID/path, full-file SHA-256, core SHA-256, core scope, and canonicalization;
- one fresh exact Karl authorization, including its ID, source path/hash, actor, time, scope, queue item, dispatch ID, and run ID;
- one run ID and derived execution-stream path;
- structured runner module, source path, version, and source SHA-256, never a command string;
- exact Strategy Spec, Variant Manifest, Sweep Plan, and dataset identities and hashes;
- denominator, budget, seed, workers, one-shot/no-retry posture, and exact scratch/event output targets;
- immutable/single-use posture and the complete non-authority declaration.

The record MUST NOT contain progress, attempt outcomes, counts, a terminal state, a mutable status, a retry instruction, a canonical Result Population target, or a free-form executable command. `dispatch_state="dispatched"` records only that the durable one-shot dispatch crossing occurred; it does not mean a process started or finished.

## Append-only execution stream

Normative schema: `research/schemas/canon_execution_event.schema.json`.

Every LF-terminated line MUST decode as one UTF-8 JSON object and MUST validate independently. Every line binds the exact dispatch ID/path/raw hash, run ID, queue-item ID, stream path, timestamp, stable event ID/sequence, and actor/tool identity. All lines in a stream MUST share those bindings.

The closed event vocabulary is:

| Event | Required payload | Ordering rule |
| --- | --- | --- |
| `run_start` | invocation start, whether the runner process started, planned denominator, budget, seed, workers, no-auto-retry | exactly once at sequence 1 |
| `attempt_outcome` | contiguous attempt number, unique variant ID, retry ordinal 0, closed outcome/reason, budget and denominator counting truth | zero or more after start and before terminal |
| `run_terminal` | closed terminal state/reason, process-start truth, full denominator accounting, actual budget | exactly once and last |

An `attempt_outcome` is terminal for that one planned attempt. Because v1 admits no retry allowance, `retry_ordinal` MUST be 0 and a variant ID MUST NOT recur in the run. `not_attempted` is retained in the closed outcome vocabulary for terminal denominator accounting; a future semantic validator MUST reject an emitted attempt event that falsely consumes budget while claiming no attempt occurred.

The stream MUST never rewrite, truncate, reorder, or delete an earlier line. A partial or malformed tail is crash-visible integrity evidence and MUST NOT be silently repaired. Corrections require a separately authorized future protocol; none is defined here.

## Execution states

| From | Event | To | Required truth |
| --- | --- | --- | --- |
| no stream | `run_start` | invocation recorded | sequence 1; exact dispatch binding |
| invocation recorded | `attempt_outcome` | invocation in progress | process started; next sequence/attempt; unique variant |
| invocation recorded or in progress | `run_terminal` | terminal | exactly one closed terminal; all denominator members visible |
| terminal | any event | invalid | no event may follow terminal |

The closed terminal vocabulary is:

- `run_completed`: the process started; attempts, budget actual, and all non-`not_attempted` outcome counts equal the planned denominator; `not_attempted=0`.
- `run_failed_process_start`: the runner process did not start; actual attempts are 0; every planned member is `not_attempted`.
- `run_failed_midrun`: the process started and stopped before the denominator completed; actual attempts are strictly less than planned; the remainder is explicitly `not_attempted`.
- `run_blocked`: a fail-closed condition prevented or halted progress; completed attempt outcomes remain and every remainder is explicitly `not_attempted`.

`success`, `pass`, GO, candidate, ranking, recommendation, and readiness are not terminal states.

## Budget and denominator accounting

The denominator basis is `committed_pre_registered_population_count`. It MUST equal the Variant Manifest value, Sweep Plan value, dispatch planned count, and budget upper bound. The sole budget metric is `variant_attempts`; unit is `attempts`; every actual attempt counts; and `actual <= upper_bound` MUST hold.

V1 fixes `retry_allowance=0`. Since the upper bound equals the denominator, no retry fits inside the admitted budget. A recovery invocation is not a retry: it requires a fresh dispatch ID, run ID, target paths, and exact Karl authorization.

Every terminal event MUST account for the full planned population. The sum of all nine outcome counts MUST equal `population_accounted_total`, which MUST equal `planned`. The sum excluding `not_attempted` MUST equal `attempts_recorded` and budget `actual`. `not_attempted` MUST equal the unattempted remainder. These cross-field equations are semantic-validator requirements because Draft 7 cannot compare or sum sibling values.

The closed outcome categories are `successful`, `failed`, `invalid`, `excluded`, `errored`, `aborted`, `filtered`, `data_unavailable`, and `not_attempted`. Failed, invalid, excluded, errored, aborted, filtered, unavailable, and unattempted members MUST remain visible; winner-only retention and silent drops are forbidden.

## Single-use, locking, and crossing requirements

A future dispatch writer MUST:

1. resolve the repository root and reject symlinked path components or escapes;
2. parse and validate the queue item, Gate-Q, authorization, runner, artifacts, dataset, denominator, budget, and proposed dispatch bytes;
3. scan dispatch IDs, run IDs, queue-item/authorization pairs, target paths, authorization history, execution events, and retained history for reuse;
4. acquire one repository-wide transient exclusive dispatch-crossing lock using an atomic `O_CREAT|O_EXCL`-equivalent primitive;
5. repeat every validation and reuse scan inside the lock immediately before creation;
6. exclusive-create the exact dispatch target, write the already validated bytes completely, flush, and fsync;
7. preserve any post-crossing file or failure evidence and release the lock without invoking a runner automatically.

The exclusive-create call is the dispatch crossing. A collision, partial write, fsync uncertainty, or lock-cleanup failure consumes the proposed identities and requires operator inspection. The writer MUST NOT delete, overwrite, truncate, reuse, or repair the target in place.

A future execution-event writer MUST use a per-run exclusive append lock. Under that lock it MUST reread and validate the entire existing stream, verify exact dispatch binding, enforce next sequence/event ID and legal ordering, append one complete canonical JSON line plus LF, flush, and fsync. It MUST NOT append after a terminal event or truncate a failed append.

## Failure and recovery matrix

| Failure point | Durable history | Required response | Forbidden response |
| --- | --- | --- | --- |
| validation/reuse check before crossing | no new dispatch | fix inputs and obtain fresh authority if content/identity changes | bypass validation |
| lock/collision/uncertain exclusive create | collision or uncertain target | fail closed; preserve evidence; new identities and fresh Karl authority | reuse or overwrite |
| after dispatch, before stream start | immutable dispatch only | operator inspection; append a non-running start and blocked/process-start terminal only when facts are provable | delete dispatch or auto-fire |
| runner process cannot start | dispatch, start, process-start terminal | stop | automatic second invocation |
| process fails midrun | dispatch, start, completed attempt lines, midrun terminal | preserve partial counts and remainder | resume silently or drop failures |
| fail-closed condition | existing lines plus blocked terminal when safely appendable | stop and preserve cause outside canonical evidence | mutate prior lines |
| crash leaves no terminal | incomplete stream remains visible | operator inspection; append a blocking terminal only if sequence/count facts are trustworthy, otherwise leave incomplete | infer completion or repair tail |
| completed run | completed terminal | later separately gated RP handoff may read scratch and control history | write canonical RP from this authority |

Any recovery run for the same queue item MUST use a new dispatch ID, run ID, paths, and fresh narrow Karl authority. The original dispatch and stream remain permanent. No scheduler, watcher, recurring worker, automatic retry, or automatic recovery is authorized.

## Scratch outputs and Result Population handoff

Runner output targets in the dispatch record MUST remain under package/run-specific scratch paths and are provisional detail. Scratch may contain metrics or diagnostics but has no canonical authority. Dispatch/execution history may prove which inputs ran and how attempts terminated; it does not itself prove strategy performance.

A later separately authorized Result Population package MAY read the immutable dispatch, complete execution stream, and scratch outputs. It MUST independently validate scientific evidence, denominator, lineage, and the Result Population schema/validator. It MUST NOT mutate queue, admission, dispatch, or execution history. This contract neither creates nor authorizes `RP-0007`.

## Future packages

Separate Karl/Main-authorized packages are required for:

- an exact dispatch-authorization artifact/schema if Main chooses to canonicalize that source;
- a dispatch writer and execution-event writer implementing every lock, reuse, path, and failure rule above;
- read-only integrity/query views and a replay validator;
- a runner adapter or runner capability package, including the separately tracked 1d real-data gap;
- the one-shot H-004-R2 dispatch and any later canonical Result Population handoff.

None may be inferred from this contract lock.

## Traceability

`WP-CANON-H004-DISPATCH-GATED-01` Stage A stopped at base `1c22edf602f748ed03d9304c66b4b40cd6f0d601` because the repo had no durable dispatch/execution-state contract. Its twelve preserved uncommitted evidence files remain read-only and identify the same independent 1d runner gap. This Option-C lock resolves only the missing representation and semantics. It does not unblock execution by itself.
