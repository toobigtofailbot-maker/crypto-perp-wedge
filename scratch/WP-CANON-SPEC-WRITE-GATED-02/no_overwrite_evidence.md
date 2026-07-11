# No-overwrite evidence

The writer creates the canonical target with OS-level exclusive binary create (`xb`) inside a narrow local crossing lock. Existing targets and simulated concurrent-create collisions fail closed without audit append. The audit permanently rejects reused targets, Strategy Spec IDs, or Gate C approval IDs even if a prior target was removed. Audit-open and partial-write failures restore the audit's prior bytes and remove the newly created target; rollback failure is integrity-critical. Stale locks are never auto-cleared and require explicit operator inspection.
