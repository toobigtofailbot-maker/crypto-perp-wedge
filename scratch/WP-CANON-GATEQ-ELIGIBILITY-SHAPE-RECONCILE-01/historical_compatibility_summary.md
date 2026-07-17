# Historical compatibility summary

- Refreshed `main` contains no `research/queue/` directory and therefore no authoritative Gate-Q approval, queue item, or admission-audit record.
- No historical queue-control byte required migration, optional-field treatment, or version branching.
- New audit records require and carry the exact three-field eligibility object.
- Synthetic historical replay re-derives and compares the exact eligibility object successfully; a schema-valid altered audit object fails closed.
- All immutable Gate-C, Strategy Spec, Gate C-VP, VM/Sweep, dataset catalog, and local Parquet bytes remain unchanged.
- No real approval, queue admission, audit append, dispatch, execution, Result Population, or candidate state was created.
