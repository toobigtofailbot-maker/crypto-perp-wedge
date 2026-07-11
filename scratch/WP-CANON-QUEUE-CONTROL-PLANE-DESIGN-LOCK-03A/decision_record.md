# Decision record

## Repo facts

Gate C is separate and non-queueing; VM/Sweep denominator semantics are locked; no canonical admission schema/path exists; no current automation watches the selected path.

## Inferred constraints

Admission must remain inert, immutable, one-file-per-item, fully hash-bound, and independently revalidated.

## New decisions

- `research/queue/admissions/` and `QI-YYYYMMDD-XXXXXXXX`: needed for deterministic append-only identity; narrowest isolated layout; later writer depends on it; dispatch remains unauthorized.
- target `offline_research`: only legitimate current domain; later dispatcher remains unauthorized.
- priorities `normal|expedited`: smallest useful bounded ordering vocabulary; no bypass semantics; scheduling remains unauthorized.
- denominator-bound `variant_attempts`: directly matches current frozen population; retries count and v1 bound equals denominator; resource/runtime expansion remains unauthorized.
- `gate_q_approval_core_v1`: necessary to break the full-file hash cycle while preserving exact queue-byte binding; later writer recomputes it; it does not replace full Gate-Q validation.

## Rejected alternatives

Scheduler/batch/run locations risk semantic conflation; JSONL complicates exclusive item identity; free-text targets/priorities are unbounded; full reciprocal file hashes are mathematically circular; priority-based budget exceptions weaken Gate Q.

## Future options

A later package may design writer/audit atomicity and, separately, operator-controlled dispatch. Neither is authorized now.
