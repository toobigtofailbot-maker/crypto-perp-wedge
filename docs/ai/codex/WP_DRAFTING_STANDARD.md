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

## 2. Minimum-Complete WP Requirements

Draft for implementation, using `docs/ai/codex/COMPACT_WP_TEMPLATE.md` by
default when stable guidance can be referenced. Refresh this standard and the
compact guidance before drafting; memory, older WPs, and chat summaries are not
current repo truth. State the package-specific requirements once:

- Identity and authorization: WP id/title, branch, effective base, execution mode,
  T0-T4 class from `VALIDATION_POLICY.md`, expected PR title prefixed with the
  package label plus `: ` (local ID first unless the WP says otherwise), authorizer,
  authorized scope, and non-authority posture.
- Objective and why now: exact deliverable, dependencies, required prior merges,
  and repo-truth/absence checks.
- Context: P0 startup anchors and package files, P1 conditional reads and search
  terms, P2 irrelevant/forbidden paths. Use the five Context Budget fields in
  `COMPACT_WP_TEMPLATE.md`; real contradictions and changed-file inspection
  cannot be omitted to meet a context budget.
- Interfaces and scope: required inputs, outputs, contracts/direct consumers,
  exact created/modified files, and whether `docs/project_status.md` is touched.
- Behavior: concrete implementation requirements and acceptance outcomes;
  disclose manual steps as `None` or specify what, when, required/optional,
  dependency effect, and what must wait. State next-step authority.
- Forbidden scope: excluded paths, behavior, authority, and protected controls.
- Risk-based validation: smallest sufficient focused, adjacent, affected-contract,
  validator/integrity checks, commands and expected evidence; explain broad/full
  validation need or non-run under `VALIDATION_POLICY.md`. Name environment
  prerequisites, known disclosures, and exact reusable evidence where applicable.
- Stop conditions: dependency failure, genuine scope/architecture/risk expansion,
  economic/security/protected boundary change, or unapproved behavior.
- Delivery and review: commit message/push, PR title/body, ready-for-review
  non-draft posture unless explicitly authorized otherwise, exact-head review,
  Karl-only merge authorization, and report-back under `WP_EXECUTION_REPORT.md`.
  State `Delta from defaults` for compact packages; references never waive gates.

### Coherent objective and bounded corrections

One WP is one coherent objective, one authority/risk boundary, and one validation
chain, in one dedicated worktree/branch. Inspect obvious direct consumers and
tests before implementation. Normal fixes, fixture/test rebaselines, and local
support corrections may proceed without renewed permission when they stay within
already-authorized files, objective, risk, and authority. Do not stop merely
because an in-scope correction was not predicted line by line.

Escalate genuine scope or architecture expansion, economic/security/protected
boundary changes, or behavior not approved by the objective. A runway or bounded
correction envelope must name its objective, boundary, validation, stop triggers,
and re-engagement points; it implicitly authorizes no new file, tier, or authority.

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

Use `docs/ai/codex/VALIDATION_POLICY.md` for tiers, test selection, protected
floors, full-release triggers, and evidence reuse. Validate in this order:

1. Verify branch/base/worktree, scope allowlist, profile prerequisites and known
   disclosures before testing.
2. Run the smallest sufficient focused and adjacent checks, affected contracts,
   and relevant validators/integrity views. Correct failures in that chain first.
3. Inspect the actual diff and run `tools/dev/diff_scope_summary.py` where available.
4. Run broad/full validation only when policy or the active gate requires it;
   prefer one stable-candidate run and repeat only for invalidated evidence.
5. Complete final base/mergeability and exact-head checks, rerunning required
   validation when changed semantics invalidate it.

T0 default checks (plus directly applicable supported docs guards):

```powershell
git diff --check
python tools/dev/diff_scope_summary.py --check-forbidden
git diff --cached --check
git diff --cached --name-only
```

Report passing commands with outcomes/counts; failures with the command and
relevant error. Never call a timeout a policy skip or weaken a required failure.
Missing ignored data is an environment finding under the named profile, not
permission to commit data or expand scope. Use the policy's explicit non-run
and timeout wording and `WP_EXECUTION_REPORT.md` for PR/report formats.

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

## 12. Compact Drafting Reference

Use the existing skeleton and Context Budget in
`docs/ai/codex/COMPACT_WP_TEMPLATE.md`, satisfying the single requirement list in
Section 2. Add only package-specific detail and deltas needed for implementation;
do not repeat standard guidance or duplicate requirements across sections.

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

## 16. Reporting and Final PR Readiness

Apply `docs/ai/codex/WP_EXECUTION_REPORT.md` for compact/expanded reporting,
Active-WP Requirement Traceability, draft-state consistency, follow-up
contradiction scans, and failure/follow-up evidence. For non-authority text,
apply the semantic audit in `COMPACT_WP_TEMPLATE.md`; classify hits rather than
silently removing required boundary references.

Before reporting ready for review, inspect actual changed files and re-fetch the
GitHub PR title, body, base/head, `isDraft`, and mergeability. Confirm the package
prefix, no stale claims/placeholders or unchecked template boxes, final scope
and validation, traceability, and agreement across report/status/PR surfaces.
Check the committed fragment's actual PR URL and validation finality under the
report guidance. Missing required evidence means not-ready with a concrete
follow-up; summaries never replace actual GitHub state or changed-file review.

Review must cover the exact PR head; new commits invalidate earlier head approval.
Preserve the final base/mergeability gate in Section 7. Ready for review is not
merge authorization: Karl alone authorizes merge; coding agents do not self-merge.

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
