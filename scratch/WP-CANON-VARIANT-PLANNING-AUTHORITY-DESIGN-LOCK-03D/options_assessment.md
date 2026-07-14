# Options assessment

1. **Mutate STRAT-SPEC-0007 — rejected.** Overwrite is forbidden; bytes are Gate-C hash-bound; the audit and queue replay require the original identity. Rewriting or rollback would bypass exclusive-create history.
2. **Treat Gate C as implicit planning approval — rejected.** Its exact scope is one canonical write and its downstream flags are false. Canonicalization and planning are distinct gates.
3. **Relax VM review evidence — rejected.** A review-requested parent without separate approval removes human authorization and permits a schema-valid false claim.
4. **External append-only approval — selected.** It binds one immutable parent and one exact bounded VM contract, is Karl-reviewed and independently replayable, preserves legacy VMs, and precedes but does not grant Gate Q.

No materially equivalent alternative authority model exists in merged repo truth.

## Open naming and placement choice

Merged truth does not select between these governance presentations:

1. **Standalone Gate C-VP.** Presents the approval as a separate named gate adjacent to Gate C.
2. **Documented variant-planning sub-gate under Gate C.** Presents the approval within Gate-C governance while preserving Gate C's existing exact canonical-write scope.

The artifact, protected writer, audit, single-use contract core, validation, replay, backward compatibility, and all no-downstream-authority semantics are identical under either presentation. Karl/Main must select one before implementation; this design does not select by implication.
