# Validation-Summary Helper / Wrapper Design

## Scope and non-authority

This document is design-only. It does not implement a validation-summary helper or wrapper, reduce validation, change which commands must run, or make summarized output validation authority.

Manual steps for this design package: none.

## Problem statement

Validation output can be long enough to make PR bodies and report-backs noisy. A future helper could make reporting easier, but only if it remains bounded: summaries must not hide failures, replace command execution, or create false confidence.

## Design goal

A future helper or wrapper may summarize validation command results only after the underlying commands actually run. It should make successful validation easier to report while preserving command names, exit codes, pass/fail counts, timeout status, and material failure details.

## Allowed future helper behavior

A future helper may summarize these command classes after they run:

- `git diff --check`
- `git diff --name-only`
- `git status --short`
- `git ls-files --others --exclude-standard`
- `tools/dev/diff_scope_summary.py`
- `python -m tools.research_query.run --list-views`
- `v_integrity_*` views
- `tools/registry/validate_*.py` modules
- targeted pytest tests
- scoped pytest regression
- full pytest suite

The helper may count passed commands, list clean integrity views, collect validator names, group pytest results, and point to raw local logs. It must not decide that any required command class is unnecessary.

## Disallowed behavior

A future helper or wrapper must not:

- hide failing test names, validator names, integrity-view rows, assertion diffs, stack traces, changed-file paths, forbidden-scope hits, warnings that affect scope, timeouts, or nonzero exit codes;
- replace direct changed-file inspection, integrity views, registry validators, scoped pytest, full pytest, or Side semantic review;
- become the only validation evidence in a PR body;
- mutate files, stage, commit, reset, checkout, or modify git state;
- call runtime, paper/live, OMS, risk, safe-mode, or protected-path code;
- add dependencies unless separately approved;
- send output to external services.

## Required command coverage

Any future implementation package must cover the command classes listed above and preserve whether each command ran, its exact command string, exit code, timeout status, and summary result. Coverage can summarize these commands, but cannot weaken or skip package-specific validation requirements.

## Output model

The default output should be advisory text suitable for PR/report-back use. PR/report-back summaries may be compact, but failure details must remain accessible and cited or summarized accurately.

Summary output must distinguish:

- command executed;
- pass, fail, skipped by package scope, or timeout;
- exit code;
- pass/fail counts;
- relevant changed-file paths;
- material diagnostics;
- raw log location when available.

## Failure handling

A future helper must fail closed if any underlying command fails or times out. Failure summaries must include the failing command, nonzero exit code or timeout, failing pytest names, failing validator names, integrity-view rows, assertion diffs, stack traces, forbidden-scope hits, changed-file paths, and other material details when present.

## Exit-code handling

A future wrapper must preserve original command exit codes if it executes commands. If multiple commands run, the wrapper must return nonzero when any underlying command returns nonzero or times out.

## Raw-output preservation

A future wrapper must make raw logs available locally when failures occur. JSON or text summaries are advisory and do not replace raw output for failures. The wrapper must not delete, redact away, or overwrite material failure output needed for review.

## Validation authority boundary

Validation authority remains with the actual commands, direct changed-file inspection, integrity views, registry validators, scoped pytest, full pytest, and semantic review. Summary output is reporting support only. It does not create validation-tier authority, evidence authority, implementation authority, runtime authority, or downstream decision authority.

## Suggested future CLI shape

Design only; any actual CLI must be approved in a later implementation work package.

```powershell
python tools/dev/validation_summary.py --from-log <path>
python tools/dev/validation_summary.py --run-docs-standard
python tools/dev/validation_summary.py --run-artifact-standard
python tools/dev/validation_summary.py --json
python tools/dev/validation_summary.py --fail-on-error
```

`--from-log` would summarize an existing local log. `--run-*` modes would execute approved command bundles only if later package scope authorizes them.

## Suggested future JSON shape

Design-only JSON keys:

```json
{
  "commands": [],
  "overall_status": "",
  "query_views": [],
  "integrity_views": [],
  "registry_validators": [],
  "pytest": {},
  "diff_scope": {},
  "failures": [],
  "timeouts": [],
  "warnings": [],
  "raw_log_paths": [],
  "advisory_note": ""
}
```

JSON summaries are advisory and do not replace raw output for failures.

## Suggested future tests

A future implementation must test:

- successful all-green summary;
- failed command preserves nonzero exit code;
- timeout is surfaced;
- failing pytest name is surfaced;
- failing registry validator name is surfaced;
- integrity-view rows are surfaced;
- raw-log path is recorded for failure cases;
- JSON output includes required keys;
- helper does not mutate files or git state;
- helper uses standard library only unless later approved;
- helper fails closed on command failure.

## Manual-step rule

Manual steps for this design package: none.

Manual steps may become relevant only if a later implementation package requires local setup. The default expected future implementation should be repo-local, standard-library-only, and require no manual user setup.

## Implementation prerequisites

A future implementation package must explicitly approve any helper or wrapper file, tests, CLI behavior, command bundles, raw-log storage location, timeout handling, and report-back format. It must be standard-library-only unless a later work package explicitly approves dependencies.

## Stop conditions

Stop if future wording or implementation would:

- reduce validation or change required commands;
- let summaries replace command execution or direct changed-file inspection;
- let summaries replace integrity views, registry validators, scoped pytest, full pytest, or Side semantic review;
- ignore nonzero exit codes or timeouts;
- hide failures, stack traces, assertion diffs, integrity rows, validator names, failing test names, changed-file paths, forbidden-scope hits, or material warnings;
- mutate files or git state;
- touch runtime, paper/live, OMS, risk, safe-mode, protected paths, configs, dependencies, schemas, validators, query-layer code, data, or external services without explicit authority;
- create RTK, RTX, TRS, code-index, memory/status snapshot, R1/R2, H-006, Path B, policy, readiness, lifecycle, promotion/demotion, or downstream authority.

## Future implementation package requirements

A future package must be narrow and mergeable. It must inspect current repo truth, keep the helper advisory by default, preserve raw failure output, prove no file or git mutation, run targeted helper tests, run scoped regression, run full pytest, check all discovered `v_integrity_*` views, run all registry validators, and confirm no competing `docs/project_status.md` PR exists if status is updated.
