# Optional Command-Output Compression Guidance

## Scope and non-authority

This document is guidance-only for optional manual command-output compression in Codex/Side workflows. It creates no implementation authority, validation authority, evidence authority, runtime authority, or downstream decision authority.

It does not require, install, configure, vendor, wrap, or depend on RTK, RTX, TRS, or any other command-output compression tool. It creates no repo dependency and no user manual setup requirement for this package.

Manual steps for this guidance package: none.

Manual steps become relevant only if a later package explicitly proposes actual setup or required use of a compression tool. Until then, users do not need to install RTK, RTX, TRS, or any other external compression tool for repo workflow.

## Preferred optional tool posture

RTK is the preferred optional manual/local command-output compression candidate for this repo's Codex / Claude Code reporting workflow when long successful shell outputs would otherwise waste tokens.

RTK remains optional. It is not a repo dependency, is not required for Codex execution, and is not validation authority.

RTK does not replace raw logs, command execution, changed-file inspection, integrity views, registry validators, scoped pytest, full pytest, or Side semantic review.

If RTK is unavailable, Codex must use the existing no-RTK fallback: direct command execution, precise manual summaries, `tools/dev/diff_scope_summary.py`, and `tools/dev/validation_summary.py` where applicable.

## Where RTK may help

RTK may be useful for long successful output from:

- `git status`
- `git diff`
- `git diff --cached`
- `git ls-files --others --exclude-standard`
- `git log` / PR metadata
- pytest successful output
- registry validator successful output
- query/integrity successful output
- repetitive successful command logs

RTK is reporting support only. It does not decide whether commands passed.

## Where raw output is required

Raw output must be preserved or retrieved for:

- failures
- nonzero exit codes
- timeouts
- stack traces
- assertion diffs
- failing test names
- validator names/errors
- integrity rows
- changed-file paths
- forbidden path matches
- allowed-file violations
- trial-log diffs
- protected-boundary evidence
- schema/validator/query-layer diagnostics
- anything needed for semantic review

## Windows / WSL / no-RTK fallback

Karl is on Windows. Do not assume shell hooks work reliably in native PowerShell.

The preferred Windows posture is explicit/manual RTK command use if Karl installs it locally and confirms it works. WSL/Linux/macOS may use normal shell command patterns if Karl chooses that route.

Follow current official RTK installation instructions outside the repo if you choose to trial RTK manually.

The no-RTK fallback remains fully valid and requires no setup. Codex must not block, fail, or refuse a WP merely because RTK is unavailable unless a future WP explicitly makes it required.

Native Windows hook-based integration must not be assumed or required by repo guidance.

## Manual trial rule

Manual RTK setup/trial is optional and outside this package. Manual trial should happen after this docs-only WP merges, if Karl chooses.

Manual trial should not modify repo files, add dependencies, or install hooks into the repo.

Manual trial should compare:

- raw output vs RTK-compressed output for successful long commands;
- whether failures remain visible enough to diagnose;
- whether Windows/PowerShell or WSL behavior is reliable.

If manual trial is successful, a later WP may decide whether to document exact local command patterns or build no-code usage examples.

If manual trial is not useful, no repo behavior changes.

## Allowed reporting pattern

Safe example pattern:

```text
Raw command executed: <exact command>
Output reported: RTK-compressed summary, advisory only
Status: pass/fail/timeout with exact count
Raw output: retained locally when failure or diagnostic detail is needed
```

## Disallowed patterns

RTK must not be used to:

- hide failures;
- hide changed files;
- hide forbidden-scope hits;
- compress away integrity rows;
- compress away failing test names;
- replace PR changed-file inspection;
- replace raw failure output;
- claim validation passed when only compressed output was inspected;
- send secrets/private/protected content to external services;
- create a mandatory setup requirement;
- create dependency, hook, wrapper, CI, config, runtime, or protected-path changes.

## Allowed use

Optional compression is allowed only to reduce copied or pasted output noise in reports, PR bodies, or chat summaries.

Compressed output may support readability, but it is not repo truth, validation authority, or evidence authority.

Local-only compression is preferred if compression is used. External services require explicit user/Karl approval and are out of scope for this package.

## Required safeguards

Compression cannot replace actual command execution, direct changed-file inspection, integrity views, registry validators, scoped pytest, full pytest unless a future repo-approved validation-tier document changes that, or semantic review.

Compression cannot hide failures, stack traces, exception messages, assertion diffs, failing test names, changed-file paths, integrity rows, validator errors, or nonzero exit codes.

## What compression must not replace

Compressed or summarized output must not replace:

- actual command execution;
- direct changed-file inspection;
- integrity views;
- registry validators;
- scoped pytest;
- full pytest unless a future repo-approved validation-tier document changes that;
- Side semantic review;
- repo truth or active package scope.

## Failure-output rule

If a command fails, Codex must preserve or retrieve enough raw output for review. Failure summaries must include the command, nonzero exit code or timeout, failing test or validator names when available, and the material raw failure details needed to diagnose the problem.

## Validation-output rule

Validation commands must still run exactly as required by the active package. If compressed output is used in a PR body or report-back, Codex must label it as compressed or summarized and include exact pass/fail counts.

`v_integrity_*: clean (N)` is allowed only if all discovered integrity views actually ran with JSON output and returned `[]`.

## Privacy and secret-safety rule

Compression must not send private repo contents, secrets, credentials, `.env` values, keys, tokens, config secrets, exchange credentials, data files, or protected-path content to any external service.

External compression services require explicit user/Karl approval and are out of scope for this package.

## How to report compressed output

When compressed output is reported, label it as compressed or summarized. Include the exact command class, exact pass/fail count, and enough context to show the underlying command actually ran.

Do not present compressed output as raw logs. Do not let compressed output obscure changed-file paths, validator names, integrity-view names, test names, failures, warnings that affect scope, or nonzero exit codes.

## When to use raw output instead

Use raw output when a command fails, times out, reports integrity rows, reports validator errors, reports assertion diffs, shows unexpected changed files, touches forbidden scope, or contains security-sensitive context that should not be sent through any compressor.

Use raw output when a reviewer needs exact failure text, exact stack traces, exact changed-file paths, exact integrity rows, exact validator diagnostics, or exact test failure details.

## Future adoption path

Any future package that makes a compression tool required must:

- identify the tool;
- verify current installation instructions;
- state manual steps;
- state whether setup is optional or required;
- state whether it creates repo dependency;
- state fallback behavior when the tool is unavailable;
- keep validation unchanged;
- be approved before implementation.

Such a package must not reduce validation, replace raw failure output, create hidden dependencies, add external service calls without approval, or weaken repo-truth precedence.

## Stop conditions

Stop and report if compression wording or use would:

- require installing RTK, RTX, TRS, or any external compression tool for current workflow;
- create repo dependency, scripts, hooks, wrappers, configs, binaries, dependencies, or external service calls without approved scope;
- replace command execution;
- replace direct changed-file inspection;
- replace integrity views, registry validators, scoped pytest, full pytest, or semantic review;
- hide failures, stack traces, exception messages, assertion diffs, failing test names, changed-file paths, integrity rows, validator errors, or nonzero exit codes;
- send secrets, credentials, `.env` values, keys, tokens, exchange credentials, private data files, or protected-path content to an external service;
- resume evidence-runway work, apply R1/R2, create H-006 or Path B authority, touch runtime/protected paths, or create policy, readiness, lifecycle, promotion/demotion, or downstream authority.
