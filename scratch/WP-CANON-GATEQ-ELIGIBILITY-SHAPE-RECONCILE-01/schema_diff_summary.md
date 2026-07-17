# Schema diff summary

## Gate-Q

```text
Before: lineage.eligibility_report -> generic {path, sha256}
After:  lineage.eligibility_report -> dedicated closed
        {path, sha256, advisory_only: true}
```

`eligibility_report_ref` reuses the existing path and hash contracts, requires all three fields, rejects additional properties, and fixes `advisory_only` to `true`. All other generic refs and authority flags are unchanged.

## Queue item

`lineage.eligibility_report` now references `gate_q_approval.schema.json#/definitions/eligibility_report_ref`; no divergent local definition was added.

## Admission audit

Every new `queue_admission_audit_record_v1` requires `eligibility_report` through the same Gate-Q definition. The record remains closed and all no-dispatch/no-execution fields remain unchanged.

The two synthetic queue-control fixtures were updated only to carry the required field and their dependent approval-core/queue-byte hashes were recomputed. They are not production state.
