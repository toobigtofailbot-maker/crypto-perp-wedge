# WP-V2-AUTONOMY-KERNEL-ARCH-01 — Durable authority architecture lock

- Package class: T0 docs/process-policy architecture lock.
- Branch: `codex/wp-v2-autonomy-kernel-arch-01`.
- Exact base: `200276fd4407e4a13a912a6b475ab9ab38a1de70`.
- Approval: Karl, 2026-10-07; proposed D2-026, pending accepted merge.
- Controlling record:
  `docs/architecture/2026-10-v2_autonomy_kernel_durable_authority.md`.

## Repo-truth basis

Refreshed `origin/main` exactly matches the required base. PR #733 is merged
there; F1/F2 capability proof is complete without Stage 5B activation. Preflight
found a clean worktree, no existing local/remote package branch, no open PRs,
no prior D2-026, and neither planned new file. D2-020 leaves backend/schema/path/
writer open; D2-023 retains temporary manual/new-campaign-only/zero-history
proof and noncanonical handoff controls. D2-024/D2-025 preserve CPW scientific
truth and human protected/economic gates. Existing frozen contracts, caller-side
successor proof, Governor ownership, proposal-only Optuna, `.cpw` workspace,
rebuildable Research Memory, and checksum-locked PostgreSQL migration idioms
were inspected read-only.

The relevant current-state text now reflects merged PRs #732/#733 instead of
stale pending-review wording. Unrelated historical status is preserved.

## Exact four-file closure

Created:

- `docs/architecture/2026-10-v2_autonomy_kernel_durable_authority.md`.
- `docs/status_entries/WP-V2-AUTONOMY-KERNEL-ARCH-01.md`.

Modified:

- `docs/decisions.md`.
- `docs/project_status.md`.

No other tracked changes are authorized. Zero code and zero runtime changes.

## Architecture semantics locked

The future immutable/hash-bound repo envelope remains human/Karl-owned; it
binds exact repo identity and approval. Future artifact/schema families are
`research/autonomy/envelopes/` and `research/schemas/`; automation cannot author
or expand envelopes, and replacement/revocation creates explicit new human
state. Later kernel work uses test fixtures only, not production envelopes.

CPW owns a separate logical PostgreSQL authority database, migrations, and
write role, with transactional current state, append-only audit, deterministic
IDs/hashes, constraints, atomic campaign budget reservation/usage, and
fail-closed conflict/idempotency. It preserves durable envelope/campaign/search/
trial lineage, cumulative history, evidence references/hashes, and holdout/
contamination ancestry; it is not a second result warehouse.

CPW derives frozen contracts from accepted intent, valid approved envelope,
exact repo/evidence, and durable lineage. Successors preserve campaign/parent
identity and full cumulative accounting; retries and operational IDs cannot
reset history. Governor retains legality/accounting/scientific-trial meaning;
Optuna proposes only. Informative holdout escape consumes the holdout across
influenced downstream lineage in the contamination domain. The first kernel
cannot automatically declare strict isolation and restore freshness; any
future isolation exemption needs a separate reviewed decision.

`.cpw/active` remains provisional; Research Memory remains rebuildable retrieval/
dedup context; Hermes remains reasoning/proposed action; Prefect remains
operational flow/run/retry. None can define or reset scientific authority.
Existing CPW evidence surfaces retain payload semantics, humans retain
promotion, and protected owners retain runtime/OMS/reconciliation/hard risk.

## Validation and preservation

`git diff --check`: PASS. Docs-only verifier
(`python tools/dev/verify.py --validation-preset docs-only --json`): PASS,
all six command results, zero failures. Rerun after the final tracked semantic
edit is required before commit. Exact four Markdown files (two creates/two
modifies): PASS. One new D2-026 decision entry (one heading, one Decision ID,
one index row), all 20 architecture sections, D2-020 through D2-025 references,
and direct changed-file/authority wording review: PASS.

Forbidden code/config/schema/test/dependency paths are unchanged,
including Search Governor/Optuna, Research Memory, research storage, Prefect,
Hermes/broker, schemas, requirements, and every protected runtime path. The
exact allowlist proves preservation of all other tracked files. No scientific
thresholds or existing gate semantics changed. Clean worktree after commit
and remote exact-head/PR state are checked at report-back, not inferred here.

full pytest: NOT RUN - T0 docs/process policy; not used as merge evidence.

## Authority and next dependency

Only architecture/process authority is gained on accepted merge. No database,
schema, production envelope, or kernel is implemented. No Stage 5B, scientific
execution, Governor call, autonomous scheduling, final-holdout access, runner/
backtest, WFO/OOS, robustness/Monte Carlo, Result Population/canonical write,
candidate/promotion, protected runtime/risk/OMS/reconciliation/overlay/safe-mode,
paper/live, exchange/order, credential, or capital authority is gained.

Hold for Side 22 exact-head review; do not self-merge. After accepted merge and
refreshed repo truth, Side 22 may draft executable `V2-AUTONOMY-KERNEL-01`.
That implementation WP is not already executable through this docs package.
