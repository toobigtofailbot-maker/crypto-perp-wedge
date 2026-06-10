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
- E. State branch, PR number/URL, GitHub mergeability status, and whether the PR is ready for review.

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
- G. State branch, PR number/URL, push result, and GitHub mergeability status.
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

Minimum PR body:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / ready-for-review status
```

## Failure Evidence Rule

Compression must never hide:

- a failed command;
- a skipped required validation;
- an unexpected changed file;
- a forbidden-scope touch;
- a mergeability failure;
- an unresolved escalation.

When any of these exist, expand the relevant section with the failing command, test or view name, error output, and disposition.
