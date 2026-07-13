# Repository truth discovery

- Base: `bfc15567850dd143dd064f688a0fa99fbeec9eff` (`origin/main`).
- Branch: `codex/wp-lab-state-supplemental-role-contract-reconcile-01` in the package-isolated worktree.
- Open PR overlap: none at preflight.
- Producer: `SUBJECTS["funding_fade_riskmanaged_no_go"]` emits the exact supplemental role `riskmanaged_conclusion_evidence` over 15 sorted paths: the funding-fade risk-managed conclusion/status/synthesis records and the Stage-1 triage denominator/slice/verdict records.
- Resolver: `build_snapshot()` carries every supplemental item through unchanged as an `ArtifactRef`; it does not validate or reinterpret the role and remains read-only.
- Auditor before change: supplemental roles are accepted only when prefixed `supplemental_`, `legacy_`, `canonical_`, or `bundle_`; there is no exact-role allowlist.
- Exact exception: `AuditError: unknown supplemental artifact role: riskmanaged_conclusion_evidence`.
- Focused reproduction: `3 failed, 2 passed, 12 errors`; all 15 affected nodes fail/error at the same supplemental-role predicate before coverage classification.
- Prior full-suite inventory: the remaining six non-lab nodes are one external-simulator missing-local-data node, one stale operator-surface exact-count node, and four stale research-query expectation nodes.
- Decision: the mismatch is one product defect. An exact allowlist containing only `riskmanaged_conclusion_evidence` resolves it without changing coordinator/operator output, existing prefixes, classification rules, or authority boundaries.
- Expansion: `tests/fixtures/**` was included only in the preservation hash manifest to prove committed fixtures remain unchanged. No fixture was inspected for semantic changes.

The complete 15 producer paths are asserted from live `SUBJECTS` by the package tests. Read-only production and fixture hashes are recorded in `read_only_hashes_before.json`.
