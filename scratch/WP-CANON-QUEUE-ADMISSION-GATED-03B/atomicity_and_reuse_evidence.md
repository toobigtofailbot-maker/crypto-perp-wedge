# Atomicity and reuse evidence

Admission is serialized by exclusive creation of `.queue_admission.lock`. Inside the lock the audit is re-read, approval/ID/path reuse is rejected, the item is opened with `xb`, exact bytes are flushed/fsynced, and one prevalidated audit line is flushed/fsynced. Audit failure truncates to the prior length and removes the new item. Rollback failure and committed lock-cleanup failure are integrity-critical and forbid automatic retry. Existing targets are never overwritten.
