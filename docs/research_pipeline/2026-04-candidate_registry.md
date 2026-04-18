# Candidate Registry

## Purpose

`research/candidate_registry.jsonl` is the structured index of strategy
candidates. Each line is one candidate entry validated by
`research/schemas/candidate_registry.schema.json`.

The registry exists so candidate comparison, filtering, and status tracking can
be done from structured data instead of prose-only decision records. It does not
replace the source artifacts:

- `HYPOTHESIS.md` remains the source of truth for signal logic and
  pre-registration.
- `research/trial_log.jsonl` remains the append-only source of truth for trial
  metrics.
- `research/decisions/DEC-*.md` remains the human-readable decision record.

## Field Conventions

- `candidate_id`: stable `H-NNN` identifier.
- `name`: hypothesis title from `HYPOTHESIS.md`, or reserved-slot name.
- `status`: current lifecycle state. Existing completed candidates are
  `CONCLUDED`; H-011 is `DRAFT` because it is reserved only.
- `overall_verdict`: decision outcome. Existing candidates are `NO-GO`; H-011 is
  `PENDING`.
- `strategy_family`: conservative normalized family label derived from the
  title and rationale. The v1 schema keeps this soft rather than enum-locked.
- `timeframe`: declared primary timeframe, taken from `HYPOTHESIS.md` when
  present.
- `information_inputs`: normalized data streams derived from Required Data /
  INPUTS sections. Reserved slots may use an empty list.
- `free_parameter_count`: declared parameter count, or `null` when not cleanly
  available. H-011 uses `null` because it is not pre-registered.
- `hypothesis_md_path`: path to the source hypothesis, or `null` for reserved
  slots.
- `decision_record_path`: path to the decision record, or `null` before a
  decision exists.
- `trial_ids`: references to `research/trial_log.jsonl`.
- `pipeline_stage`: current pipeline stage. `reserved` means a slot exists but
  is not pre-registered.
- `created_at` / `updated_at`: ISO dates derived from repo artifacts when
  available. Reserved-slot dates are the WP-6a backfill date.

Optional fields such as `direction_profile`, `notes`, and
`differentiation_summary` are intentionally non-core. The v1 schema avoids
hardening fields that are not consistently represented in H-001 through H-010.

## Current Backfill

H-001 through H-010 are backfilled from current repo truth:

- Candidate titles, created dates, status, primary timeframe, required streams,
  free-parameter counts, and decision-record paths come from each
  `HYPOTHESIS.md`.
- Trial IDs come from `research/trial_log.jsonl`.
- Decision outcomes come from the associated DEC files.
- H-009 is recorded as `30m`, matching current repo truth.

H-011 is a reserved slot only:

- `pipeline_stage = "reserved"`
- `status = "DRAFT"`
- `overall_verdict = "PENDING"`
- `information_inputs = []`
- `free_parameter_count = null`
- `hypothesis_md_path = null`
- `decision_record_path = null`
- `trial_ids = []`

The H-011 slot does not procure data, does not create a hypothesis file, and
does not commit to testing the candidate.

## Adding A Candidate

1. Pre-register the candidate in `research/hypotheses/H-NNN/HYPOTHESIS.md`.
2. Add a registry row with fields directly derived from the hypothesis.
3. Keep `decision_record_path = null`, `trial_ids = []`, and
   `overall_verdict = "PENDING"` until evidence exists.
4. Run:

```powershell
.venv\Scripts\python.exe tools\registry\validate_registry.py
```

5. Commit the hypothesis and registry row together.

## Updating Candidate Status

After a baseline or later experiment creates a trial-log row and decision
record:

1. Add the new `trial_id`.
2. Set `decision_record_path`.
3. Update `status`, `overall_verdict`, `pipeline_stage`, and `updated_at`.
4. Re-run the registry validator.

The registry should point to evidence. It should not duplicate full metrics from
`trial_log.jsonl` or DEC tables.

## Out Of Scope

- No candidate auto-generation.
- No agent in the loop.
- No DuckDB query layer.
- No Monte Carlo infrastructure.
- No gold data procurement.
- No H-011 pre-registration.
- No execution-core changes.
