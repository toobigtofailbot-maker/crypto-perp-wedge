# Exact-equality preservation

The protected order and equality semantics remain intact:

- Gate-Q schema validation precedes queue-item schema validation (`queue_admission.py` lines 325-326).
- Gate-Q-to-queue-item eligibility lineage still uses `_equal` with the complete objects (lines 349-351).
- Gate-Q eligibility lineage still uses direct Python object inequality against the complete Gate-C record (lines 359-362).
- `_equal` itself is unchanged (line 138).
- Preflight validation, in-lock revalidation, path/symlink checks, exact-byte hashing, reuse checks, exclusive creation, append-only audit, rollback, integrity-critical handling, and terminal non-dispatch posture are unchanged.

The only writer additions are:

- emit the already schema-validated and exact-equality-validated Gate-Q eligibility object in the derived audit record (line 425);
- compare that derived object during historical replay (lines 264-276).

Proofs cover schema-valid Gate-Q/item mismatch, schema-valid Gate-Q/Gate-C mismatch, and schema-valid audit replay mismatch. No projection, normalization, subset comparison, field stripping, or hash-only comparison was introduced.
