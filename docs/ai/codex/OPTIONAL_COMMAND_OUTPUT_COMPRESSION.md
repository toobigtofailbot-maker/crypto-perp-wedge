# Optional Command-Output Compression Guidance

## Scope and non-authority

This document is guidance-only for optional manual command-output compression in Codex/Side workflows. It creates no implementation authority, validation authority, evidence authority, runtime authority, or downstream decision authority.

It does not require, install, configure, vendor, wrap, or depend on RTK, RTX, TRS, or any other command-output compression tool. It creates no repo dependency and no user manual setup requirement for this package.

Manual steps for this guidance package: none.

Manual steps become relevant only if a later package explicitly proposes actual setup or required use of a compression tool. Until then, users do not need to install RTK, RTX, TRS, or any other external compression tool for repo workflow.

## When optional compression may help

Optional compression may help reduce copied or pasted terminal-output noise when a command succeeds and produces long repetitive output.

For now, Codex may manually summarize long successful outputs, but must not summarize away failures.

## Manual-step rule

For current repo operation, no user action is required.

Any future package that proposes setup or required use of a compression tool must state exactly what the user must do, when to do it, whether setup is optional or required, whether it creates a repo dependency, and what fallback Codex must use when the tool is unavailable.

## Tool-agnostic posture

Repo guidance is tool-agnostic. RTK, RTX, TRS, and manual compression remain optional and unimplemented until a future approved package identifies a tool and creates explicit setup or use authority.

Local-only compression is preferred if compression is used. External services require explicit user/Karl approval and are out of scope for this package.

## Allowed use

Optional compression is allowed only to reduce copied or pasted output noise in reports, PR bodies, or chat summaries.

Compressed output may support readability, but it is not repo truth, validation authority, or evidence authority.

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
- resume WP-S2c-30, apply R1/R2, create H-006 or Path B authority, touch runtime/protected paths, or create policy, readiness, lifecycle, promotion/demotion, or downstream authority.
