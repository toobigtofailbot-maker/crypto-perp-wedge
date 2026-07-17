# Repo-truth preflight

- Refreshed base: `ea8073b890c6aa84f1684714844a00b1a6c296ca` (`origin/main`).
- Root checkout was clean; the package uses dedicated branch `codex/wp-canon-gateq-eligibility-shape-reconcile-01` and its dedicated worktree.
- PRs #657 through #662 were merged. No open PR, local/remote branch, or worktree owned this correction. The blocked H-004 Gate-Q worktrees were not reused.
- Repo truth matched the diagnosed contradiction: Gate-Q and queue-item eligibility lineage used the generic two-field ref, while the protected writer required exact equality with Gate-C's three-field object.
- `research/queue/` was absent on refreshed `main`: zero authoritative Gate-Q approvals, queue items, or admission-audit records required migration.
- Baseline queue-control regression: `86 passed, 5 skipped`.
- Immutable H-004-R2, Gate C-VP, VM/Sweep, catalog, and local Parquet hashes matched the package pins before mutation.
- Frozen allowlist: the six expected schema/writer/test files, two directly affected synthetic fixtures, six compact evidence files, and one status fragment.

Compatibility decision: implement the Main-authorized dedicated schema shape and additive audit/replay propagation. No historical compatibility branch is required because no committed admission history exists.
