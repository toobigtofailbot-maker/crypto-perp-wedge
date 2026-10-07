# WP-EXTREME-HERMES-01 — Revision 2 in progress

Exact base: `11214acfb6d8af44586c50089eb9965063a505ee`.
Branch: `codex/wp-extreme-hermes-01-f1f2-canary-01`.
Exact authorized closure: 16 created + 8 modified files.

Implementation, pinned security backport, F0 preservation, sandbox and canaries
are authored. Preliminary focused checks passed 45 tests, adjacent checks 175,
and upstream patch checks 9. Sandbox terminal/file/Python, canary plugin/MCP,
and external skill/memory rollback observations are recorded in
`docs/architecture/2026-10-extreme_hermes_f1f2_canary_implementation.md`.

Browserbase variables are now PRESENT in the current process. A real session
passed navigation/snapshot and private-address rejection, ran no local Chromium,
and was released (provider status COMPLETED). Same branch/worktree retained.
Hermes-managed openai-codex OAuth is READY in the isolated home. Live native
search sent `web_search` and received a completed provider search call. Both
fresh specialists passed headless OAuth access with only memory/session search,
no copied auth state, stripped director credentials, and denied out-of-scope calls.
One bounded delegation completed with a leaf child at depth 1, no inherited MCP,
and a denied nested spawn. Karl authorized environment-only provisioning with
the existing official PostgreSQL 17.10 Windows binaries. The isolated external
cluster listens only on 127.0.0.1:60619, with separate research_memory_test and
research_memory databases, SCRAM authentication and DPAPI-protected local DSNs.
Repo migrations/bootstrap and the fixed reader-role script were applied.
Read-only identity/default/SELECT/DML denial and container connectivity passed;
the three Research Memory PostgreSQL integration tests passed unskipped.
The same WP resumed from its database gate. Preliminary full-release
was interrupted across restart and left no result; it is not a pass.
All final Cases A–K, exact-head verification,
physical HERMES-02 and rollback evidence remain required before publication.

No PR, final acceptance, review readiness or merge readiness is claimed.
Self-merge is forbidden; hold the eventual PR for Side 22 exact-head review.
No Stage 5B, autonomous scientific, canonical write, promotion, protected
runtime/risk, paper/live, exchange/order or capital authority is gained.
