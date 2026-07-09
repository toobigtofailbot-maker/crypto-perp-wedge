# Denominator Preservation Evidence

## Verdict

The runner adapter preserves the full runner denominator and records adapter status counts without winner narrowing.

## Status Mapping

Runner outcome categories are mapped to the package-required status vocabulary:

- `successful` -> `completed`
- `failed` -> `failed`
- `invalid` -> `invalid`
- `excluded` / `filtered` -> `pruned`
- `errored` / `aborted` / `data_unavailable` / `not_attempted` -> `blocked`

Allowed adapter denominator statuses:

- `completed`
- `failed`
- `invalid`
- `blocked`
- `pruned`

## Preservation Rules

- The adapter does not remove Result Population rows.
- The adapter does not select winners.
- The adapter records counts across all rows present in the runner Result Population.
- Adapter and direct denominator counts must match or the adapter fails closed.

## Focused Evidence

Command:

```text
.\.venv\Scripts\python.exe -m pytest tests/test_lab_pipeline_runner_adapter.py -q
```

Result:

```text
29 passed
```

Covered cases include:

- full denominator retained from real runner output;
- explicit fixture covering `completed`, `failed`, `invalid`, `pruned`, and `blocked`;
- no winner narrowing;
- no canonical Result Population write.

## Boundary

The denominator evidence is product-scratch/non-authoritative. It does not create candidate, promotion, readiness, WFO/OOS, robustness, candidate-review, paper/live/runtime, scheduler, provider/API, dependency/config/data, or protected-path authority.
