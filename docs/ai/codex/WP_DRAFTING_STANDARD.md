# Codex WP Drafting Standard

## 1. Purpose and Authority

This document is the repo-standard for drafting Codex work packages (WPs). It standardizes WP structure, delivery format, parallel execution, scope control, forbidden scope, validation, stop conditions, report-back formats, review checklists, and type-specific templates.

Repo truth, current merged state, and explicit Main/Karl authorization still override generic templates. This standard is guidance for drafting and execution discipline; it does not create implementation, evidence, runtime, policy, promotion, approval, or downstream authority.

The standard exists to prevent recurring failures:

- uncommitted files from another WP leaking into a new WP;
- Codex editing `main` or the root checkout during parallel work;
- parallel WPs colliding on `docs/project_status.md`;
- PRs being called merge-ready while GitHub reports `mergeable=false`;
- detached-HEAD confusion after manual or rebase conflict resolution;
- invalid data producing normalized files that downstream code can consume;
- validation failures caused only by missing gitignored local data in isolated worktrees.

## 2. Universal WP Requirements

Every WP must include:

- package identity: WP id, title, suggested branch, package class, execution mode, expected PR title;
- authorization source: who authorized the package and what was authorized;
- objective: the exact deliverable and non-authority posture;
- why now / dependency: required prior merges, report-backs, decisions, or runway state;
- operating context: repo files to read before work;
- scope: exact allowed created or modified files;
- forbidden scope: paths, artifacts, authority changes, and protected boundaries outside the package;
- validation: exact commands and expected evidence;
- stop conditions: conditions that require halting and reporting;
- commit / PR instructions: branch, commit message, PR title, draft status, and body requirements;
- report-back format: required sections and evidence;
- review checklist: how Side/Main should inspect merge readiness;
- PR status: ready for review / not draft unless explicitly authorized otherwise.

## 3. Mandatory Delivery Rule

Every drafted WP delivered from Side/Main to Codex must be delivered as a `.txt` file. Do not deliver only in chat.

The filename must include the WP id and a short title, for example:

```text
WP-D2_Data_Block_1_binance_usdtm_15m_offline_ingestion.txt
```

## 4. Mandatory Isolated-Worktree Rule

Permanent standard:

- one WP = one dedicated worktree = one branch;
- branch-only isolation is not enough for parallel execution;
- never work from the root checkout during parallel execution;
- never make package edits on `main`;
- stop if the dedicated worktree is dirty before starting;
- do not stash, reset, clean, delete, or overwrite silently.

Reusable command template:

```powershell
Set-Location "C:\GitHub\crypto-perp-wedge"
git fetch origin
git worktree add -b <branch> <worktree-path> origin/main
Set-Location "<worktree-path>"
git branch --show-current
git status --short
```

Required start state:

```text
current path is the dedicated WP worktree
current branch is the intended WP branch
git status --short returns no output
```

Stop if:

- current branch is `main`;
- current path is the root checkout;
- the worktree is dirty;
- the branch or path already exists unexpectedly;
- untracked files from another WP exist.

If dirty, stop and report the file list. Do not stash silently, overwrite, clean, reset, delete files, or mix those files into the package.

## 5. Parallel PR Rule

Parallel PRs are allowed when primary scopes do not overlap. `docs/project_status.md` conflicts are expected during parallel WP execution and may be resolved by rebase after earlier PRs merge.

Protected/runtime/canonical/schema/tooling overlaps are stop conditions unless explicitly scoped by the active WP. Do not use parallel execution to weaken protected boundaries or to broaden a package.

## 6. Parallel Status-Entry Rule

If multiple parallel WPs are running, `docs/project_status.md` conflicts are expected. Before final push, rebase onto current `origin/main` and resolve `docs/project_status.md` by preserving:

- all already-merged status entries;
- this WP's status entry;
- chronological and status-log consistency.

Do not broadly rewrite `docs/project_status.md` during conflict resolution. Do not remove another WP's merged status entry. Do not add entries for PRs that are not merged yet unless the WP explicitly owns that branch-state entry.

Allowed conflict-resolution behavior:

- preserve all merged entries;
- append or retain this WP's entry;
- fix ordering or local context around the conflict only.

Forbidden during conflict resolution:

- code, schema, tool, or artifact changes;
- broad `docs/project_status.md` rewrite;
- deleting already-merged entries;
- changing another WP's meaning;
- using conflict resolution to expand package scope.

Future option, not the current default: if `docs/project_status.md` conflicts become repeated friction, propose a separate repo-process WP to move per-WP status fragments into separate files such as `docs/status_entries/<WP_ID>.md`, while keeping `docs/project_status.md` as a milestone summary only.

## 7. Final Rebase / GitHub Mergeability Gate

Every WP that opens or updates a PR must complete this gate before reporting "ready for merge":

```powershell
git fetch origin
git rebase origin/main
# resolve docs/project_status.md conflicts if any
git status --short
git diff --check
# rerun required validation for the package
git diff --cached --check
git diff --cached --name-only
```

If the rebase rewrites history, push safely:

```powershell
git push --force-with-lease
```

After pushing, check the PR on GitHub. GitHub must report `mergeable=true` before Side is asked to review it as merge-ready. A PR is not merge-ready if GitHub reports conflicts or `mergeable=false`.

If GitHub reports `mergeable=false`, do not call the PR merge-ready. Report the blocker and provide a narrow rebase / conflict-resolution follow-up.

## 8. Rebase Editor / Detached-HEAD Caution

During `git rebase --continue`, Git may open an editor for the commit message. If Vim opens, save and quit with:

```text
Esc
:wq
Enter
```

Do not close the terminal window as a substitute for saving the editor.

If detached HEAD happens, do not reset or clean. If the correct changes are present on detached HEAD, either push detached HEAD explicitly to the PR branch:

```powershell
git push --force-with-lease origin HEAD:<branch>
```

or stop and report for manual recovery. Do not continue editing from detached HEAD unless explicitly instructed.

## 9. Validation Environment From Isolated Worktrees

If the dedicated worktree lacks `.venv`, use the root checkout virtualenv by absolute path:

```powershell
& "C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe" -m <module>
```

or create/use the repo-standard environment if that is the established convention. Do not treat missing `.venv` inside a worktree as a package failure.

If full pytest fails only because a gitignored local data file is absent in the isolated worktree, report it explicitly. Do not commit gitignored local data and do not expand the WP to data-file handling.

For T1 docs-only WPs, full pytest is not required unless the package or repo guidance explicitly requires it. For T3/code WPs, follow the package validation requirements and report environment-only failures separately.

## 10. Invalid-Data Output Rule

Permanent data rule: invalid data may write validation/provenance reports only. Invalid data must not write normalized downstream-consumable outputs. Report-only means report-only.

Required behavior:

- valid source + output path: write normalized output + report, return 0;
- invalid source without report-only flag: write report only, no normalized output, return nonzero;
- invalid source with report-only flag: write report only, no normalized output, return 0.

Forbidden:

- normalized output for invalid data;
- best-effort normalized file;
- silent fill, interpolation, or deduplication;
- synthetic-as-real candles;
- invalid data artifact that downstream code might consume as valid.

Required tests for data WPs:

- invalid input does not create normalized output;
- report-only invalid input still does not create normalized output;
- report records validation failure/errors;
- downstream-consumable data files exist only for valid input.

Review question:

```text
Can invalid data produce a file that downstream code might consume as valid?
```

If yes, the PR is not merge-ready.

## 11. Universal WP Skeleton

```text
# <WP id> - <title>

## Codex instruction
- Open the PR ready for review unless explicitly authorized as draft.
- Do not work outside this WP.

## Package identity
- WP id:
- Title:
- Suggested branch:
- Expected PR title:
- Package class:
- Execution mode:

## Authorization
- Source:
- Authorized scope:

## Objective
- Exact deliverable:
- Non-authority posture:

## Operating context
- Read startup anchors:
- Read package-specific files:

## Dependencies
- Required prior merges:
- Required absence checks:
- Why now:

## Mandatory worktree rule
- One WP = one dedicated worktree = one branch.
- Required commands:
- Required clean start state:

## Scope
- Allowed created files:
- Allowed modified files:

## Forbidden scope
- Forbidden files/paths:
- Forbidden behavior/authority:

## Required behavior/content
- Required document/artifact/code behavior:
- Required wording or fields:

## Validation
- Commands:
- Expected results:

## Stop conditions
- Dependency failures:
- Scope expansion:
- Validation failure:
- Protected-boundary tension:

## Final rebase / GitHub mergeability gate
- Rebase onto origin/main:
- Rerun validation:
- Confirm GitHub mergeable=true:

## PR body requirements
- Scope:
- Changed files:
- Validation:
- Boundary check:
- Ready-for-review status:

## Codex report-back format
- Branch/base:
- Repo-truth discovery:
- Delivered changes:
- Validation:
- Boundary check:
- PR/push status:
- Open escalations:

## Side review checklist
- Changed-file scope:
- Semantic fit:
- Validation evidence:
- Boundary and authority check:
- Mergeability:
```

## 12. Type-Specific Templates

### T1 Doc / Design WP

Use for documentation, process, architecture, or design-only packages.

Required emphasis:

- docs/status only unless the WP explicitly allows another file;
- no code, tests, schemas, tools, data artifacts, research artifacts, or runtime mutation;
- T1 validation from the package;
- full pytest not required unless repo guidance or the WP requires it;
- if full pytest is run voluntarily and fails only due to missing gitignored local data, report as environment-only and do not expand scope.

Validation should include changed-file scope, forbidden-path check, `git diff --check`, and package-required validators.

### T3 Implementation WP

Use for scoped code/test implementation packages.

Required emphasis:

- code/tests allowed only in scoped files;
- full pytest unless the WP explicitly defines a stricter or narrower approved profile;
- run `tools/dev/diff_scope_summary.py` where available;
- run relevant integrity views;
- no protected path drift;
- no opportunistic refactors.

### Data Contract WP

Use for design-only data policy and contract packages.

Required content:

- source policy;
- timestamp semantics;
- gap policy;
- duplicate policy;
- hash/provenance policy;
- storage/catalog expectations;
- no implementation.

### Data Ingestion WP

Use for offline data ingestion implementation.

Required content:

- offline-only source;
- no live API or keys;
- invalid-data output rule;
- deterministic normalization;
- source and output hashes;
- gap and duplicate tests;
- full pytest unless a stricter WP-specific validation profile applies.

### Schema / Validator WP

Use for schema grammar or validator work.

Required content:

- closed grammar;
- `additionalProperties: false` where applicable;
- accept/reject tests;
- no compiler implementation unless explicitly scoped;
- no artifact mutation unless explicitly scoped.

### Compiler Implementation WP

Use for closed compiler additions.

Required content:

- closed forms only;
- no expression language;
- no `eval`, `exec`, or `lambda`;
- determinism;
- no-lookahead behavior;
- null/warmup behavior;
- full pytest.

### Runner / Canonical-Artifact WP

Use for runner output and canonical artifact packages.

Required content:

- frozen parents;
- committed denominator;
- complete population;
- determinism rerun;
- canonical write gate;
- no denominator shrinkage;
- Karl gate where applicable.

### Query / Test Transition WP

Use when current repo state requires transitioning query/test expectations.

Required content:

- state transition, not test weakening;
- exact stale assertions;
- result/query implementation change is halt unless scoped;
- no broad relaxation.

### Engineering / Operator-Surface WP

Use for dashboards, briefings, alerts, or operator-facing surfaces.

Required content:

- read-only / non-authoritative posture;
- no execution triggers;
- no artifact mutation;
- no credentials;
- no broker/exchange contact.

### Paper-Risk Design WP

Use for sandbox paper-risk design only.

Required content:

- sandbox-only;
- manual operator approval;
- no live keys or orders;
- paper-to-live gate remains hard;
- no research artifact as automatic authority.

### Follow-Up / Correction WP

Use to repair a precise blocker.

Required content:

- exact blocker;
- minimal correction;
- changed files allowed;
- validation rerun;
- forbidden scope unchanged;
- no opportunistic cleanup.

### Main Report-Back Template

Report-backs to Main should include:

- merged PRs / repo state;
- changed files;
- semantic summary;
- validation;
- boundary summary;
- decision request;
- next capsules;
- mandatory stop points.

Report-backs to Main should be delivered as Markdown files, not only in chat.

### Merge-Readiness Review Checklist

Reviewers should verify:

- scope check: changed files match the WP;
- file-change check: no unapproved files or untracked package leakage;
- semantic check: content matches the objective and does not redesign outside scope;
- validation check: package-required commands ran and passed or failures are correctly classified;
- boundary check: protected paths and runtime/paper/live boundaries stayed untouched;
- authority check: no artifact, report, doc, or tool gained unauthorized downstream authority;
- mergeability check: final branch is rebased and GitHub reports `mergeable=true`;
- invalid-data downstream-consumption check where relevant;
- PR body stale-claim check;
- follow-up prompt if not merge-ready.

## 13. Future WP Reference Rule

Future WPs may say:

```text
Follow docs/ai/codex/WP_DRAFTING_STANDARD.md.
This WP uses the <type> template.
Apply the mandatory isolated-worktree rule.
Apply the final rebase / GitHub mergeability gate.
Apply the invalid-data output rule if data is involved.
```

Those references are valid only when the WP still states the package-specific identity, objective, scope, forbidden scope, validation, stop conditions, and report-back requirements.
