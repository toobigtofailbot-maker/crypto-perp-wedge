# WP-V2-INTEGRATION-01B-ARCH-01

- Branch: `codex/wp-v2-integration-01b-arch-01`
- Exact base: `f2dbcb73a25d5ce271a29915b54ae6647aee5570`
- Decision: `D2-023`
- Package class: T0 documentation-only architecture lock
- Pull request: pending publication; to be replaced before the final commit
- Substantive head: to be recorded after the validated substantive commit
- Review state: held for Side exact-head review
- Self-merge: no

## Scope

This package locks `SearchPolicyBinding v1`, the first-proof
new-campaign-only restriction, CPW intent-to-`SearchContract` ownership,
noncanonical `ProposalWaveHandoff v1` storage under `.cpw/active/`, and exact
active-wave recovery from a finalized pre-wave Governor snapshot.

It implements nothing. It adds no runner, result submission, wave
finalization, canonical write, Stage 5B, autonomous scheduling, runtime/risk,
paper/live, exchange/order, or capital authority.

## Exact changed files

1. `docs/architecture/2026-10-search_policy_proposal_handoff_lock.md`
2. `docs/decisions.md`
3. `docs/project_status.md`
4. `docs/status_entries/WP-V2-INTEGRATION-01B-ARCH-01.md`

No Python, dependency, config, schema, validator, query, data, `.cpw`, scratch,
canonical, runner, candidate-lifecycle, runtime, OMS, reconciliation, risk,
overlay, safe-mode, paper/live, exchange/order, credential, or capital file is
changed.

## Validation

- `git diff --check`: PASS.
- `tools/dev/verify.py --validation-preset docs-only --json`: PASS using the
  existing main-checkout virtual-environment interpreter because this managed
  worktree has no local `.venv`; every required command passed and the
  forbidden-path check found no match.
- Exact four-file changed-set check: PASS.
- Worktree state before commit: only the exact four authorized Markdown files
  changed; no unrelated tracked or untracked file was present.

The branch must remain unmerged for Side exact-head review.
