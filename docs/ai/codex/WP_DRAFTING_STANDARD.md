# Coding-Agent WP Drafting Standard

This standard applies to Claude Code and Codex. Tool-specific notes are marked explicitly; all other rules are shared.

## 1. Purpose and Authority

This document is the repo-standard for drafting coding-agent work packages (WPs). It standardizes WP structure, delivery format, parallel execution, scope control, forbidden scope, validation, stop conditions, report-back formats, review checklists, and type-specific templates.

Repo truth, current merged state, and explicit Main/Karl authorization still override generic templates. This standard is guidance for drafting and execution discipline; it does not create implementation, evidence, runtime, policy, promotion, approval, or downstream authority.

The standard exists to prevent recurring failures:

- uncommitted files from another WP leaking into a new WP;
- a coding agent editing `main` or the root checkout during parallel work;
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
- validation tier: the T0-T4 blast-radius tier from `docs/ai/codex/VALIDATION_POLICY.md`, including mandatory focused tests, adjacent subsystem tests, relevant validators/integrity views, and whether broad/full-suite evidence is required and why;
- validation profile: environment prerequisites, known disclosures, and any reusable broad evidence with its exact base/head/scope;
- context budget: P0 must read, P1 conditional, and P2 irrelevant or forbidden;
- stop conditions: conditions that require halting and reporting;
- commit / PR instructions: branch, commit message, PR title, draft status, and body requirements;
- report-back format: required sections and evidence. Report-backs may use the compact tier-aware shape from `docs/ai/codex/WP_EXECUTION_REPORT.md` when the package is clean; expanded detail is required when validation fails, scope differs, forbidden files are touched, GitHub mergeability is not clean, or the package is T2/T3/T4 with material semantic risk;
- whether `docs/project_status.md` will be modified: state this explicitly so reviewers can anticipate parallel-PR collision risk and confirm the final rebase and mergeability gate was completed (see `docs/status_entries/README.md`);
- review checklist: how Side/Main should inspect merge readiness;
- PR status: ready for review / not draft unless explicitly authorized otherwise.

### Coherent vertical-slice rule

A WP is one coherent objective, one authority/risk boundary, and one validation
chain. It does not mean one tiny file or assertion. Prefer a larger coherent
same-risk vertical slice when splitting it would create avoidable handoffs or
leave direct consumers knowingly contradictory.

Before implementation, scan the obvious downstream consumers and tests of the
state being changed. Within an authorized objective, the package may include
same-semantic-class test rebaselines, fixture corrections, local helper
refactors, and reversible non-canonical support corrections when necessary to
complete that objective and when they remain inside the allowed files, risk
tier, and authority boundary.

Stop when architecture changes, protected or canonical authority expands, the
allowed-file or risk boundary genuinely widens, or unexpected semantics cannot
be resolved inside the authorized objective. Do not split or stop merely because
a necessary in-scope correction was not predicted line by line.

### Runway and bounded-correction rule

Main may authorize a larger runway of packages or a bounded in-scope correction
envelope. The runway must state its objective, allowed authority/risk boundary,
validation chain, stop triggers, and re-engagement points. It never authorizes a
new tier, protected boundary, or out-of-scope file implicitly.

### Context budget

Every WP must classify context as:

- P0: must read before work;
- P1: read only when dependency or contradiction analysis requires it;
- P2: irrelevant or forbidden for the package.

This keeps repo truth first while avoiding repeated broad exploration. The
budget cannot omit startup anchors, current changed files, or a file required to
resolve a real contradiction.

PR title package-label prefix rule:

- The expected PR title must begin with the package label followed by a colon and a space. Example: `WP-GUIDE-EFF-04: Close workflow-efficiency guidance gaps`.
- If a package has both a local ID and a roadmap ID, the local/package ID comes first in the PR title unless the active WP explicitly says otherwise.
- A PR title that does not begin with the package label is a review hygiene issue and should be corrected before merge-readiness unless Main/Karl explicitly authorizes a different naming convention.

## 3. Mandatory Delivery Rule

Every drafted WP delivered from Side/Main to a coding agent must be delivered as a `.txt` file. Do not deliver only in chat.

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

Two or three file-disjoint lanes of the same or lower risk may run concurrently
when their objectives and validation chains are independent. Protected or
shared-semantic overlaps must serialize. `docs/project_status.md` conflicts are
expected during parallel WP execution and may be resolved by rebase after
earlier PRs merge.

Protected/runtime/canonical/schema/tooling overlaps are stop conditions unless explicitly scoped by the active WP. Do not use parallel execution to weaken protected boundaries or to broaden a package.

## 6. Parallel Status-Entry Rule

For future parallel WPs, prefer per-WP status fragments under `docs/status_entries/<WP_ID>.md`. Use the process in `docs/status_entries/README.md` for fragment naming, required fields, update posture, and review checks.

After WP-G2, `docs/project_status.md` should be used as a milestone summary, major accepted-decision ledger, current runway pointer, and startup anchor. Update `docs/project_status.md` only for milestone summaries, major runway changes, major accepted decisions, or when the active WP explicitly requires it.

If a WP still modifies `docs/project_status.md`, conflicts may still occur. Before final push, rebase onto current `origin/main` and resolve `docs/project_status.md` by preserving:

- all already-merged status entries;
- this WP's scoped status entry;
- chronological and status-log consistency.

Do not broadly rewrite `docs/project_status.md` during conflict resolution. Do not remove another WP's merged status entry. Do not add entries for PRs that are not merged yet unless the WP explicitly owns that branch-state entry.

Allowed conflict-resolution behavior:

- preserve all merged entries;
- append or retain this WP's scoped entry;
- fix ordering or local context around the conflict only.

Forbidden during conflict resolution:

- code, schema, tool, or artifact changes;
- broad `docs/project_status.md` rewrite;
- deleting already-merged entries;
- changing another WP's meaning;
- using conflict resolution to expand package scope.

The final rebase / GitHub mergeability gate remains mandatory even when status fragments are used.

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

Use a deterministic named validation profile when a package depends on
gitignored data, local control-plane evidence, known integrity disclosures, or
other environment-specific state. Verify exact paths, file kind, byte lengths,
hashes, ignore/tracking state, and permitted hydration method before testing.
Local existence never upgrades evidence to merged repo truth.

If required local data is absent, report it against the profile before broad
validation. Do not commit gitignored local data or expand the WP to data-file
handling. T0 docs/process packages do not run pytest by default. T1-T4 packages
follow the active tier and package requirements, with environment-only failures
reported separately from semantic failures.

## 10. Usage-Efficient Validation Rule

Run validation in the readiness order locked by
`docs/ai/codex/VALIDATION_POLICY.md`. Full pytest/full-release is an integration
and protected-boundary tool, not the routine inner loop.

Universal rule:

- confirm exact branch/base/worktree, validation profile, prerequisites, known disclosures, and changed-file allowlist first;
- use focused tests first;
- use adjacent subsystem tests second;
- run package validators / registry validators next;
- run query views / integrity checks where relevant;
- run `tools/dev/diff_scope_summary.py` before full pytest where available;
- run full pytest only when the tier, blast radius, milestone/release boundary, protected gate, or active package requires it;
- run the final rebase / GitHub mergeability gate after validation.

If focused tests fail, correct and rerun the focused chain first. Do not proceed
to broad validation until focused, adjacent, and relevant validator/integrity
checks pass. After a small correction, rerun prior broad evidence only when the
correction invalidates its covered blast radius. If validation exposes a broader
architecture issue or unscoped file requirement, stop and report instead of
continuing exploratory edits.

Concise-output rule:

- prefer `pytest -q`;
- for passing commands, report command + pass/fail + short count only;
- if a command fails, report the failing command, failing test name, and relevant error only;
- do not paste full passing logs;
- do not paste large unrelated stack traces.

PR-body minimum rule:

PR bodies must include the following minimum sections and must not restate the entire WP or paste large passing logs:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / ready-for-review status
```

See `docs/ai/codex/WP_EXECUTION_REPORT.md` for the compact and expanded report-back shapes and tier-aware expectations.

Recommended T0 docs/status/comment validation profile:

```powershell
git diff --check
python tools/dev/diff_scope_summary.py --check-forbidden
git diff --cached --check
git diff --cached --name-only
# final rebase / GitHub mergeability gate
```

Run docs render/lint/link checks when the repo supports them. Run targeted
validators only when the docs diff changes artifact indexes, references,
examples, or validation-relevant generated text. Full pytest is not required
for T0 unless the active WP or stronger authority requires it. Use
`docs/ai/codex/VALIDATION_POLICY.md` to distinguish `NOT RUN - T0 docs/process
policy` from `TIMED OUT`.

Recommended T2 broad production/contract validation shape:

```powershell
python -m pytest <changed/new test file> -q
python -m pytest <adjacent subsystem tests> -q
python -m <relevant validators>
python -m tools.research_query.run --list-views
# run all discovered v_integrity_* views and confirm clean / zero rows
python tools/dev/diff_scope_summary.py
python -m pytest -q
git diff --cached --check
git diff --cached --name-only
# final rebase / GitHub mergeability gate
```

For data WPs, run focused data tests first, adjacent importer / validator / catalog tests second, invalid-data output tests where relevant, and relevant validators/integrity checks. Run full pytest only when the tier, affected dependency graph, milestone/release boundary, or active package requires it.

For compiler WPs, run focused compiler tests first, adjacent validator / compiler-probe tests second, determinism / fail-closed / no-lookahead tests where relevant, and relevant validators/integrity checks. Run full pytest when the T2 blast radius is broad or when a stronger gate requires it.

Environment-only full-pytest failures:

- if full pytest fails only because a gitignored local data file is absent in the isolated worktree, report it explicitly as environment-only;
- do not commit gitignored local data;
- do not expand the WP to data-file handling;
- for T0 docs/process packages, full pytest is not required unless explicitly required;
- for T1-T4 WPs, follow the package and tier requirements and report any environment-only full-pytest failure separately;
- do not weaken real validation failures. Any required full-suite failure remains a blocker unless the active WP or stronger authority explicitly defines a different acceptance condition.

## 11. Invalid-Data Output Rule

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

## 12. Universal WP Skeleton

```text
# <WP id> - <title>

## Coding-agent instruction
- Open the PR ready for review unless explicitly authorized as draft.
- Do not work outside this WP.

## Package identity
- WP id:
- Title:
- Suggested branch:
- Expected PR title: (must begin with the package label, e.g. `WP-EXAMPLE-ID: Title`)
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

## Coding-agent report-back format
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

## 13. Type-Specific Templates

### T0 Doc / Design WP

Use for documentation, process, architecture, or design-only packages.

Required emphasis:

- docs/status only unless the WP explicitly allows another file;
- no code, tests, schemas, tools, data artifacts, research artifacts, or runtime mutation;
- T0 validation from the package;
- full pytest not required unless repo guidance or the WP requires it;
- if full pytest is run voluntarily and fails only due to missing gitignored local data, report as environment-only and do not expand scope.

Validation should include changed-file scope, forbidden-path check, `git diff --check`, and package-required validators.

Full pytest is not required for T0 docs/design/process WPs unless explicitly
required by the WP or repo guidance. Use the T0 profile from the
Usage-Efficient Validation Rule by default. Use
`docs/ai/codex/VALIDATION_POLICY.md` for the current wording and to distinguish
`NOT RUN - T0 docs/process policy` from `TIMED OUT`.

### T1 Test / Read-Only / Exact-Persistence WP

Use for test-only changes, read-only query additions without production query
semantic changes, exact-artifact persistence, and non-canonical research
automation.

Required emphasis:

- focused and adjacent tests plus relevant validators/integrity views;
- no full suite by default;
- exact artifact bytes and identity remain unchanged for persistence packages;
- no promotion, canonical-crossing, protected-writer, or runtime authority.

### T2 Production / Contract Implementation WP

Use for scoped code/test implementation packages.

Required emphasis:

- code/tests allowed only in scoped files;
- focused tests first, adjacent tests second, then relevant validators, integrity views, and diff-scope proof;
- full pytest when the dependency graph or blast radius is broad, or when a milestone/release/package gate requires it;
- run `tools/dev/diff_scope_summary.py` where available;
- run relevant integrity views;
- no protected path drift;
- no opportunistic refactors.

### T3 Canonical Crossing / Protected Writer WP

Use for canonical crossing logic, execution writers, dispatch authorization,
and other protected writers. Require full rigor, full-release/full-suite
evidence, exact-head review, exact-content and append-only integrity proof, and
the applicable human gate.

### T4 Runtime / Capital-Boundary WP

Use for runtime, OMS, reconciliation, risk, capital, and paper/live paths.
Require maximum rigor, Karl gate, and preservation of every protected control.

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
- focused data tests first;
- adjacent importer / validator / catalog tests second;
- invalid-data output tests where relevant;
- full pytest when the T2 dependency graph/blast radius, milestone/release boundary, or active package requires it.

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
- focused compiler tests first;
- adjacent validator / compiler-probe tests second;
- determinism / fail-closed / no-lookahead tests where relevant;
- full pytest when the T2 dependency graph/blast radius, milestone/release boundary, or active package requires it.

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
- PR body stale-claim check: no GitHub template placeholders, unchecked boxes, or pending/TBD language;
- final PR readiness gate: PR title prefix, PR body placeholder scan, status-fragment PR URL and finality check, semantic audit for non-authority packages;
- follow-up prompt if not merge-ready.

## 14. Required Context Budget and Package-Class Fields

Every future WP must include:

- `Context Budget / Files to Inspect`, explicitly mapped to P0/P1/P2. P0 contains `Read first` and `Read for this package`; P1 contains `Read only if blocked` and `Search terms if paths changed`; P2 contains `Do not read / do not touch`. See `docs/ai/codex/COMPACT_WP_TEMPLATE.md` for the full Context Budget requirements.
- `Delta from defaults` when using compact WP format, stating what differs from standard guidance for validation, forbidden paths, manual steps, stop triggers, and report-back. The delta section must not skip required startup anchors, validation, or protected-boundary checks.
- Package-class classification using the single blast-radius vocabulary in `docs/ai/codex/VALIDATION_POLICY.md`: T0 (docs/status/comments), T1 (test-only/read-only query/exact persistence/non-canonical research automation), T2 (schema/validator/contract/query SQL/broad production code), T3 (canonical crossing/protected writer/dispatch authorization), or T4 (runtime/paper/live/OMS/reconciliation/risk/capital). See `docs/ai/codex/README.md` for the aligned read-path guidance.

These requirements do not reduce or replace the universal WP requirements in Section 2, the validation requirements in Sections 9–10, the isolated-worktree rule in Section 4, or any other standard in this document.

Before drafting a WP, the drafter must refresh current WP drafting guidance from:

- `docs/ai/codex/WP_DRAFTING_STANDARD.md`;
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`, when relevant.

Do not rely only on memory, prior chat summaries, stale local prompts, or older WPs when drafting execution packages.

## 15. Requirement Compatibility / Impossibility Check

Before an execution WP sends a coding agent to implement a non-trivial behavior, the drafter must verify that the behavior is compatible with current repo mechanisms and the allowed changed-file scope.

For each material behavior, identify:

- required behavior;
- controlling repo mechanism (schema, validator, collector, renderer, test, doc, etc.);
- files likely needed to deliver the behavior;
- whether those files are in the allowed scope for this WP;
- whether schema/validator/tests/contracts already permit the behavior without changes outside scope;
- action: implement / stop / split package / ask Main/Karl.

Required format:

```text
| Required behavior | Controlling repo mechanism | Files likely needed | Allowed in this WP? | Compatible? | Action |
|---|---|---:|---:|---:|---|
| <behavior> | <mechanism> | <paths> | yes/no | yes/no | implement / stop / split / ask Main |
```

If a required behavior is impossible under the allowed scope, the WP must not ask the agent to implement it. It must either:

- split a prior unblock package;
- explicitly accept the limitation as known debt;
- or define a stop condition and decision request.

This gate is mandatory for dashboard, schema, validator, collector, and renderer
packages and recommended for all T2 implementation packages.

## 16. Follow-Up / Blocker Resolution Contradiction Scan

When a follow-up WP resolves a blocker or changes earlier package scope, the coding agent must search the PR body, status fragment, and changed docs for stale claims from the prior state.

Search for:

```text
blocked, draft, decision required, pending, to be added, background run, not ready,
no schema change, no validator change, old error text, prior Option A/B language,
TBD, placeholder
```

Every hit must be removed or classified before the PR is reported ready-for-review. Classification options:

- removed (stale language deleted);
- historical note (clearly marked as past state, not current state);
- required reference (neutral, not stale).

This scan is mandatory for follow-up WPs and for any package that resolves a prior blocker. Include the scan result in the report-back under the final PR readiness gate.

## 17. Final PR Readiness Gate

Every coding agent must complete this gate before reporting a PR ready for review or asking Side/Main for merge-readiness review.

The gate requires the agent to inspect the actual GitHub PR title, PR body, and the committed status fragment and confirm:

- PR title begins with the package label followed by `:`;
- final report/status/PR body includes or references a compact Active-WP Requirement Traceability checklist with active-WP requirement, source section in active WP, evidence location, and status of satisfied / not applicable / blocked;
- validation required by the active WP ran unless the active WP explicitly says that validation is optional or not used as merge evidence;
- final console report, PR body, status fragment, and project-status pointer agree on validation, draft state, mergeability, blockers, skipped checks, and changed-file scope;
- PR body uses the required compact or expanded report shape;
- PR body contains no GitHub template placeholders;
- PR body contains no unchecked template checkboxes;
- PR body contains no `TBD`, `pending`, `to be added`, `background run`, `paste output`, or equivalent stale placeholder text;
- status fragment contains the actual PR URL (not a placeholder);
- status fragment validation summary is final;
- status fragment contains no pending/background validation language;
- skipped or unavailable validation is explicitly marked `Not run; not used as merge evidence.` or classified with exact environment-only failure details;
- changed-file scope was checked after final metadata/status updates;
- GitHub reports the PR mergeable/clean unless the package is intentionally draft/blocked.

For packages whose changed text includes non-authority, anti-ranking, no-readiness, no-promotion, no-execution, or dashboard-as-non-authority constraints, a semantic text audit is also required before ready-for-review. See `docs/ai/codex/COMPACT_WP_TEMPLATE.md` for the sample audit block.

This gate applies to every WP that opens a PR, including T0 docs-only packages.
Active WPs that include a `Final PR Readiness Gate` section must apply the gate
to their own PR before reporting ready-for-review.

If a required item is missing, the agent must report not-ready and include a paste-ready follow-up prompt.

When Side/Main review determines a follow-up is needed, the review/report-back must include:

- paste-ready follow-up prompt;
- self-diagnosis;
- whether the issue was preventable;
- what should have caught it;
- immediate process change;
- whether a durable repo/process/WP-guidance package is needed.

If the failure was preventable or likely to recur, Side/Main should draft or request a narrow improvement WP after the immediate blocker is resolved.

## 18. Architecture-transition and external-adoption rules

At an architecture transition, identify the validation, allowlist, environment,
and evidence-lifecycle support that the next packages will need. When an
obvious validation-tool gap would otherwise force repeated exceptions or broad
manual proof, surface a separate bounded tooling package before the transition.
Do not hide tooling implementation inside the package making the crossing.

When an external capability already has a committed disposition and its
adoption trigger is satisfied, use that disposition rather than reopening a
generic survey by default. Adopt or wrap the bounded capability only within its
existing authority boundary. Adoption never gives an external tool canonical,
promotion, runtime, execution, or risk authority.

## 19. Protected-core invariants

Acceleration is faster everywhere protected controls do not require
protected-level cost and unchanged where they do. No WP, runway, evidence reuse,
or validation tier may weaken exact-content canonical crossings,
irreversible-execution authorization, full-denominator accounting, append-only
integrity, protected writers, human promotion gates, runtime, paper/live, OMS,
reconciliation, hard risk, capital, or exact-head review where T3/T4 requires
it.

## 20. Future WP Reference Rule

Future WPs (for Claude Code or Codex) may say:

```text
Follow docs/ai/codex/WP_DRAFTING_STANDARD.md.
This WP uses the <type> template.
Apply the mandatory isolated-worktree rule.
Apply the final rebase / GitHub mergeability gate.
Apply the invalid-data output rule if data is involved.
```

Those references are valid only when the WP still states the package-specific identity, objective, scope, forbidden scope, validation, stop conditions, and report-back requirements.
