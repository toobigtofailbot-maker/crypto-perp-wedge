# WP-CANON-GATE-C-LINEAGE-BYTE-RESTORATION-01

Status: **READY FOR PR REVIEW**.

- Base: `de758a5a886b2729384efb1873966b6fccb2fdc7` (`origin/main`).
- Restoration: the H-004-R2 source draft and eligibility report were restored by LF-to-CRLF byte transformation only. Their raw hashes now exactly match immutable Gate-C evidence: `sha256:7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a` and `sha256:76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9`.
- Prevention: `.gitattributes` adds exact-path `-text` rules with the repository's CR-at-EOL whitespace allowance; the global LF policy is unchanged.
- Proof: current and crossing-commit blobs were identical before restoration; both files were pure LF with no stray CRs; parsed JSON and canonical semantic digests are unchanged; Git index and fresh detached checkout retain the exact CRLF hashes.
- Lineage: Gate-C approval/audit and review trail replay; eligibility internally binds the restored source; `STRAT-SPEC-0007`, Gate C-VP, `VM-0007`, `SWEEP-PLAN-0007`, denominator 81, and dataset lineage validate. The current read-only queue lineage preflight passes every available upstream check; no authoritative Gate-Q exists and no proposal or write was created.
- Validation: 24 registry validators pass; data validation passes; 58 integrity views reproduce 57 clean plus the accepted pre-existing `STRAT-SPEC-0007` hash-readiness row; two identical collections found 2,965 nodes across 160 files; exact non-overlapping execution produced 2,958 passed and the refreshed-main seven skips, with zero failures, errors, internal errors, or timeouts.
- Boundary: no approval/audit mutation, recross, Strategy Spec/VM/Sweep/dataset mutation, Gate Q, queue, dispatch, execution, Result Population, candidate, runtime, paper/live, OMS, risk, or reconciliation change or authority.
