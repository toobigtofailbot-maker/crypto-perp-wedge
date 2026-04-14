# Execution Brief Template

Copy this template for each work package. Keep it repo-first, scoped, and testable.

## Package

- **ID:** `[WP-X]`
- **Title:** `[Short name]`
- **Base branch:** `main`
- **Working branch:** `[branch-name]`
- **PR title:** `[PR title]`

## Repo-First Startup

Before editing:

1. Read `docs/project_status.md`.
2. Read only the additional files needed for this package.
3. If repo truth conflicts with stale chat wording, stop and report the conflict.
4. Do not improvise outside this brief.

## Objective

[One paragraph describing what this package accomplishes and what it intentionally does not do.]

## Allowed Scope

Create or update only:

| Path | Allowed action | Purpose |
|---|---|---|
| `[path]` | `[create/update]` | `[why]` |

## Forbidden Scope

Do not modify:

- `[specific files/directories]`

Do not:

- Add dependencies unless explicitly listed.
- Change runtime behavior unless explicitly listed.
- Touch generated data/artifacts unless explicitly listed.
- Make architecture decisions.

## File Specifications

### `[path]`

- **Required change:** `[content or behavior required]`
- **Must preserve:** `[constraints]`
- **Must not do:** `[negative constraints]`

## Validation Gates

All gates must pass before reporting complete:

| Gate | Command / check | Expected |
|---|---|---|
| 1 | `[exact command]` | `[expected result]` |
| 2 | `[manual check]` | `[expected result]` |

## Stop Conditions

Stop and escalate if:

- Repo truth contradicts this brief in a way that affects scope, locked decisions, or validation.
- Required work would touch forbidden files.
- Baseline validation fails before edits.
- Any uncertainty remains about current repo truth versus outdated wording.

## Done Criteria

- All required files updated.
- All validation gates pass.
- Only allowed files changed.
- No forbidden runtime/data/test/config/dependency drift.
- PR is ready for review or blocker is reported clearly.

## Manual Tasks

[None / list any required human-only checks or follow-up actions.]

## Report-Back Format

Use `prompts/report_back.md` unless this package supplies a stricter format.
