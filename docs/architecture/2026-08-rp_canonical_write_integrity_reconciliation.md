# Result Population Canonical-Write Integrity Reconciliation

## Decision

`v_integrity_result_population_canonical_write_violation` continues to detect
canonical Result Population output references across the complete Result
Population payload. One exact administrative provenance record is exempted so
that protected persistence can name its proposed canonical target without that
non-authorizing record becoming a canonical-write integrity finding.

## Previous invariant and exposed conflict

The previous invariant rejected any payload text containing a canonical Result
Population output reference. That broad protection correctly prevented
scientific, execution, review, validation, ledger, non-authority, and other
payload content from implying a canonical write.

Protected Result Population persistence exposed one narrow conflict: its
administrative lineage must preserve the proposed Result Population identity
and target path before a canonical write is authorized. The provenance text is
therefore expected to name the canonical target even though it grants no write
authority.

## Revised invariant

Canonical-output detection remains field-aware across payload keys and scalar
values. A canonical reference is not a finding only when all of the following
are true:

- it is a string element directly inside
  `audit_envelope.administrative_lineage`;
- exactly one copy of the permitted string exists;
- its complete value is
  `PROPOSED_RESULT_POPULATION|id=<ENCLOSING_RP_ID>|canonical_target_path=research/result_populations/<ENCLOSING_RP_ID>.result_population.json|classification=canonical write not yet authorized`;
- both identifiers are derived from and exactly match the enclosing
  `result_population_id`; and
- the classification is exactly `canonical write not yet authorized`.

Administrative provenance records the intended destination for auditability.
It is outside the scientific identity hashes and does not approve, execute, or
authorize the canonical write. The provenance record cannot authorize itself.

## Forbidden broadening

The exemption does not apply to the rest of `audit_envelope`, to arbitrary
`administrative_lineage` content, to reordered or extended records, to wrong or
malformed identifiers and paths, to alternate classifications, or to a second
canonical reference elsewhere in the payload. Duplicate copies of the exact
record are also findings. Canonical references in scientific, execution,
validation, review, non-authority, ledger, and all other fields remain findings.

This decision makes no schema or registry-validator change, changes no
scientific hash scope or append-only semantic, changes no canonical crossing
gate, and grants no candidate, GO, promotion, runtime, paper/live, OMS,
reconciliation, risk, or capital authority.
