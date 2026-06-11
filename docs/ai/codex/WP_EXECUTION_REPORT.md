# Work Package Execution Report

Use this report-back structure for coding-agent execution packages (Claude Code or Codex).

## Default Compact Report-Back Shape

Use the compact shape by default for clean T1 packages:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / decision
```

Each section must be concrete and audit-friendly:

- A. State what changed and what did not change.
- B. List exact created and modified files.
- C. State commands run, pass/fail result, and short counts. Do not paste full passing logs.
- D. Confirm protected paths remained untouched and that no forbidden-scope files were touched.
- E. State branch, PR number/URL, actual PR title, GitHub mergeability status, and whether the PR is ready for review. For normal WPs the PR title should begin with the package label; if it does not, correct it or explain why a package-specific exception applies. Include an explicit final PR readiness gate result: PR body placeholder scan (no GitHub template placeholders, unchecked boxes, stale pending/TBD text), status-fragment PR URL finality, status-fragment validation finality, and Active-WP Requirement Traceability checklist or reference.

## Expanded Report-Back Shape

Use the expanded shape when required (see trigger conditions below):

```text
A. Branch / base
B. Repo-truth discovery
C. Delivered changes
D. Validation results
E. Failed or skipped validation detail
F. Forbidden-scope check
G. PR / push status
H. Open escalations
I. Ready for review
```

Each expanded section must be concrete and audit-friendly:

- A. Identify the actual branch and base commit.
- B. State what repo facts were verified before editing.
- C. List created and modified files.
- D. Report exact validation run status or explicit non-run reasoning.
- E. For each failed or skipped validation, include the failing command, failing test or view name, and relevant error.
- F. Confirm protected paths remained untouched when required.
- G. State branch, PR number/URL, actual PR title, push result, and GitHub mergeability status. If the PR title does not begin with the package label, correct it or report the exception reason. Include an explicit final PR readiness gate result: PR body placeholder scan, status-fragment PR URL and validation finality, Active-WP Requirement Traceability checklist or reference, and semantic audit result for non-authority packages.
- H. List any open escalations or stop-condition triggers.
- I. State YES or NO.

## When Expanded Detail Is Required

Expanded detail is required when any of the following apply:

- validation failed or was skipped;
- GitHub mergeability is not clean (`mergeable=false` or conflicts reported);
- scope differs from the expected changed-file list;
- forbidden or protected files were touched;
- repo truth changed the package scope;
- manual recovery, rebase, detached HEAD, or conflict resolution occurred;
- the package is T2, T3, or T4 and has material semantic risk.

## Tier-Aware Report-Back Expectations

```text
T1 docs/guidance/design:
- Compact by default if clean.
- Include exact changed files, validation commands and results, boundary check, PR/mergeability status.
- Do not paste full passing logs.

T2 research artifacts/query/evidence:
- Include artifact IDs, parent lineage, denominators, hashes where applicable.
- Include validator, query, and integrity results.
- Compact passing logs; expand failed evidence.

T3 implementation/tooling/dashboard/schema/validator:
- Include changed modules, tests, validators, integration or dry-run evidence where relevant.
- Include adjacent subsystem checks and protected-path scan.
- Compact passing logs; expand failures.

T4 runtime/paper/live/OMS/risk/protected:
- Do not use compact-only report-back unless the active WP explicitly authorizes it.
- Include full safety and protected-boundary evidence required by the package.
```

## PR Body Is Not a Mini-WP

PR bodies must summarize what changed, the changed-file list, validation results, boundary check, and review status. They must not restate the entire WP or paste large passing logs.

The PR body is part of the review evidence surface and cannot be left as a template. Before reporting ready-for-review, the coding agent must inspect the actual rendered GitHub PR body and confirm it contains no GitHub template placeholders, unchecked template checkboxes, or stale pending/TBD language.

Minimum PR body:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / ready-for-review status
```

## Draft-State Consistency Rule

Final readiness evidence must include the actual GitHub `isDraft` value (from `gh pr view --json isDraft`).

- Blocked or draft PRs must be consistent across GitHub state, PR body, and status fragment: if GitHub `isDraft=true`, the PR body and status fragment must not say ready for review or complete.
- Non-draft, mergeable PRs must not have PR body or status fragment language that says draft, blocked, or not ready.
- Do not call a PR merge-ready if GitHub state and PR body/status fragment contradict each other.

## Active-WP Requirement Traceability Gate

Before reporting ready-for-review, reconcile the final PR against the active WP.

The final report/status/PR body must include or reference a compact checklist with:

- active-WP requirement;
- source section in the active WP;
- evidence location;
- status: satisfied / not applicable / blocked.

Required validation from the active WP cannot be skipped or downgraded to "Not run; not used as merge evidence" unless the active WP explicitly says that validation is optional or not used as merge evidence.

If final console report, PR body, status fragment, or project-status pointer disagree on validation, draft state, mergeability, blockers, skipped checks, or changed-file scope, the PR is not ready.

If a required item is missing, report not-ready and include a paste-ready follow-up prompt.

## Follow-Up / Blocker Resolution Contradiction Scan

When a follow-up WP resolves a blocker or changes earlier package scope, the report-back must include a contradiction scan result.

Scan the PR body, status fragment, and changed docs for stale claims from the prior blocked/draft state:

```text
blocked, draft, decision required, pending, to be added, background run, not ready,
no schema change, no validator change, old error text, prior Option A/B language,
TBD, placeholder
```

Report the scan result in the final PR readiness gate section of the report-back:

- terms searched;
- hits found;
- disposition of each hit (removed / historical note / required reference).

If any hit remains without classification, the PR is not merge-ready.

## If Not Merge-Ready

If a PR is not merge-ready, the report-back must include:

- exact reason the PR is not ready;
- a paste-ready follow-up prompt that resolves the blocker;
- self-diagnosis;
- whether the issue was preventable;
- what should have caught it;
- immediate process change;
- whether a durable repo/process/WP-guidance package is needed.

If the failure was preventable or likely to recur, Side/Main should draft or request a narrow improvement WP after the immediate blocker is resolved.

## Failure Evidence Rule

Compression must never hide:

- a failed command;
- a skipped required validation;
- an unexpected changed file;
- a forbidden-scope touch;
- a mergeability failure;
- an unresolved escalation.

When any of these exist, expand the relevant section with the failing command, test or view name, error output, and disposition.
