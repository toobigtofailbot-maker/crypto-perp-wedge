# WP-CANON-VARIANT-PLANNING-VM-QUEUE-LINEAGE-01B

Status: **READY FOR PR REVIEW**.

Adds backward-compatible external Variant Manifest planning-approval evidence and independently replays the merged 01A approval, parent, Gate-C, audit, permanent-use, and exact contract-core lineage. Legacy embedded-approved manifests remain unchanged and reject external evidence; review-requested canonical manifests require the external append-only approval. Gate-Q, queue-item, and admission-audit contracts carry the four approval lineage facts only in external mode, and queue admission plus historical replay revalidate them before preserving the sole inert `admitted_non_dispatched` state.

Validation completed with 221 focused contract tests passing and five pre-existing Windows symlink skips; 367 adjacent read-only contract tests passing; and a deterministic 2,955-node inventory executing exactly once with 2,948 passing, the seven authorized environment skips, zero failures/errors/internal errors, and zero timeouts. Both collection runs were identical. Strategy Spec, VM/Sweep, and Result Population validators pass, as do the package-relevant research-query integrity checks. An optional sweep of every live integrity view reproduced the existing STRAT-SPEC-0007 hash-readiness row identically on untouched `origin/main`; this package does not alter that canonical/query state.

All six existing canonical VM/Sweep pairs, their hashes, and every production/read-only lineage input remain byte-identical. This package creates no real planning approval or audit line, VM, Sweep, Gate-Q approval, queue item, admission record, dispatch, execution, Result Population, candidate, runtime, paper/live, OMS, risk, reconciliation, dependency, or configuration state.
