# Coding-Agent Token Efficiency and Context Hygiene

This guidance applies to Claude Code and Codex. File name is retained for historical reference; Codex-specific notes inside remain Codex-specific.

## Scope and non-authority

This document is guidance-only for coding-agent token efficiency, prompt size, and context hygiene. It does not create implementation authority, validation-tier authority, evidence authority, runtime authority, or downstream decision authority.

Token efficiency cannot justify skipping repo-truth inspection, refreshed-main preflight, changed-file inspection, integrity views, registry validators, full pytest, package-specific validation, or package-specific stop conditions. It also cannot justify protected-path, runtime, paper/live, OMS, risk, safe-mode, config, dependency, schema, validator, query-layer, data, or implementation drift.

## Source-of-truth hierarchy

Use the active package's precedence order when one is provided. Otherwise:

1. Current merged repo truth, including actual changed files and live merged state.
2. Active work package scope and constraints.
3. `AGENTS.md`.
4. Supporting coding-agent workflow docs under `docs/ai/codex/`.
5. Chat memory, prior summaries, Agent Mode research, and generic best practice.

Repo truth and active WP scope always win. Cached status, memory, summaries, or compressed notes never replace current repo inspection.

## Read-Path Router and Context Budget

The package-class read-path router in `docs/ai/codex/README.md` provides T1/T2/T3/T4 class-specific file-reading guidance. Apply it after required startup anchors and after the active WP instructions.

Every WP should include a `Context Budget / Files to Inspect` section with the five required fields (`Read first`, `Read for this package`, `Read only if blocked`, `Do not read / do not touch`, `Search terms if paths changed`). See `docs/ai/codex/COMPACT_WP_TEMPLATE.md` for the full requirements.

The read-path router and Context Budget reduce wrong-file reading. They do not reduce startup-anchor obligations, repo-truth inspection, validation, changed-file inspection, or stop-condition investigation.

## Context hygiene rules

Read required startup anchors first, then read only task-relevant files or slices. Prefer targeted searches, exact file reads, and current diffs over broad context ingestion.

Do not paste or restate long guidance blocks when a canonical repo document can be referenced. Do not rely on older handoffs or chat memory for current branch, artifact, test, or PR state.

## Prompt-efficiency rules

Future Codex prompts may reference this document to reduce repeated boilerplate, but every WP must still include package-specific objective, dependencies, allowed files, forbidden scope, validation, stop conditions, and report-back requirements.

Prompt compression must preserve scope control. It must not omit protected boundaries, validation gates, dependency checks, or package-specific stop triggers.

## Targeted repo inspection

Codex should inspect the startup anchors and the files that are material to the package. Use `rg` or exact-path reads for repo-local discovery where practical.

Targeted inspection does not mean shallow inspection. If a package changes a file, inspect that file directly. If a package depends on current branch, PR, artifact, or validation state, verify it against current repo truth.

## Concise project-status entries

`docs/project_status.md` entries should stay concise when full detail exists in the package artifact, guidance document, or PR body. The entry must still include package identity, created or modified files, core boundary, and next-step authority.

Brevity must not omit material authority facts, stop-trigger facts, protected-boundary facts, validation posture, or downstream non-authority.

## Concise report-backs

Default concise report-backs should use the compact tier-aware shape from `docs/ai/codex/WP_EXECUTION_REPORT.md`:

```text
A. Scope
B. Changed files
C. Validation
D. Boundary check
E. PR status / decision
```

Longer report-backs remain required for T2/T3/T4 packages, artifact packages, stop triggers, validation failures, nontrivial semantics, package-specific report formats, or any case where compression would hide a failed command, skipped required validation, unexpected changed file, forbidden-scope touch, mergeability failure, or unresolved escalation. See `docs/ai/codex/WP_EXECUTION_REPORT.md` for the full expanded shape, tier-aware expectations, and failure evidence rule.

PR bodies must use the compact minimum shape. They must not restate the entire WP or paste large passing logs.

## Validation-output summarization

Prefer concise passing-output summaries: command + pass/fail + short count. Do not paste full passing logs.

For integrity views, summarize clean results as count + clean/no rows where repo convention allows. `v_integrity_*: clean (N)` is allowed only if all discovered integrity views actually ran with JSON output and returned `[]`. Integrity views must still be discovered and executed.

Registry validators and pytest results may be summarized by exact command class and pass count when the underlying commands actually ran. Summaries do not replace command execution.

For failures, include the failing command, failing test or view name, and relevant error only. Compression must never hide a failed command, skipped required validation, unexpected changed file, forbidden-scope touch, mergeability failure, or unresolved escalation.

Token efficiency cannot skip validation, changed-file inspection, final rebase, GitHub mergeability, or stop conditions.

Do not add or endorse validation wrappers, RTK integration, generated summaries, generated current-state files, or generated code indexes.

## Optional manual command-output compression

RTK is now the preferred optional manual/local command-output compression candidate for long successful Codex / Claude Code command output.

Actual RTK/RTX/TRS tooling remains unimplemented. RTK is not required, is not a repo dependency, and requires no setup for normal Codex execution.

Compressed output may support reporting only. It cannot replace running the required commands or inspecting the actual diff.

Follow `docs/ai/codex/OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md` for safeguards, raw-output requirements, and Windows / WSL / no-RTK fallback posture.

## Future helper/tooling sequence

Future efficiency ideas are sequenced. Compact WP template guidance is now implemented as guidance at `docs/ai/codex/COMPACT_WP_TEMPLATE.md`; the local diff/scope summary helper is now implemented as a repo-local advisory helper at `tools/dev/diff_scope_summary.py`; optional RTK command-output compression guidance is now implemented as guidance only at `docs/ai/codex/OPTIONAL_COMMAND_OUTPUT_COMPRESSION.md`, identifying RTK as the preferred optional manual/local compression candidate while leaving RTK/RTX/TRS tooling unimplemented; validation-summary helper/wrapper design is now implemented as design only at `docs/ai/codex/VALIDATION_SUMMARY_HELPER_DESIGN.md`; the validation-summary log helper is now implemented as a repo-local advisory helper at `tools/dev/validation_summary.py` for summarizing existing local logs only; code-index design is now implemented as design only at `docs/ai/codex/CODE_INDEX_DESIGN.md`; code-index implementation is now implemented as a repo-local advisory helper at `tools/dev/code_index.py`; memory/status snapshot design is now implemented as design only at `docs/ai/codex/MEMORY_STATUS_SNAPSHOT_DESIGN.md`; memory/status snapshot implementation is now implemented as a repo-local advisory helper at `tools/dev/status_snapshot.py`. Generated code-index files and generated memory/status snapshot files are not committed by default and are not repo truth. The remaining helper/tooling items below are not implemented here:

- compact WP templates: implemented guidance only in `docs/ai/codex/COMPACT_WP_TEMPLATE.md`;
- local diff/scope summary helper: implemented repo-local advisory helper only at `tools/dev/diff_scope_summary.py`;
- optional RTK/RTX/TRS/manual compression tooling: not implemented;
- validation-summary helper or wrapper design: implemented design only in `docs/ai/codex/VALIDATION_SUMMARY_HELPER_DESIGN.md`;
- validation-summary log helper: implemented repo-local advisory helper only at `tools/dev/validation_summary.py`;
- validation-summary command-running wrapper modes: not implemented; deferred / not implemented for now;
- code-index design: implemented design only in `docs/ai/codex/CODE_INDEX_DESIGN.md`;
- code-index implementation: implemented repo-local advisory helper only at `tools/dev/code_index.py`;
- memory/status snapshot design: implemented design only in `docs/ai/codex/MEMORY_STATUS_SNAPSHOT_DESIGN.md`;
- memory/status snapshot implementation: implemented repo-local advisory helper only at `tools/dev/status_snapshot.py`.

Validation command-running wrapper modes are deferred / not implemented for now. The current approved workflow continues to execute required commands directly and may summarize existing local logs through `tools/dev/validation_summary.py`. The helper remains a log-summary helper only, and its command-running wrapper modes remain intentionally unimplemented / fail-closed. Wrapper modes may be reopened only by a future explicit package if repeated validation-reporting bottlenecks justify the added risk; any such package must fail closed, preserve raw failure output, preserve exit codes and timeouts, and keep actual commands as validation authority.

The current efficiency/tooling tranche is complete enough to resume project work after explicit user/Karl instruction. Each future helper or tooling idea still requires its own package scope and validation. The implemented guidance, helper, and design surfaces are advisory only and do not replace package scope, raw logs, command execution, direct changed-file inspection, integrity views, registry validators, scoped pytest, full pytest, repo-truth file inspection, `docs/project_status.md`, branch/PR checks, artifact/count verification, or semantic review. This document does not implement RTK/RTX/TRS/manual compression tooling, command-running validation wrappers, generated committed indexes, generated committed memory/status snapshots, memory files, automation, schemas, validators, query-layer changes, or runtime behavior.

## Workflow-Efficiency Guidance Closure

This workflow-efficiency guidance cleanup is complete enough to return to project work. Future helper or tooling ideas still require their own explicit WP scope and validation.

Advisory posture of helper outputs:

- `diff_scope_summary.py`, `validation_summary.py`, `code_index.py`, and `status_snapshot.py` outputs are advisory only.
- These helpers do not replace repo truth, raw logs, command execution, direct changed-file inspection, validators, integrity views, tests, `docs/project_status.md`, branch/PR checks, artifact/count verification, or semantic review.
- Generated helper outputs are not committed unless the active WP explicitly scopes that commit.

Deferred items — not implemented here:

- Current-state capsule creation is deferred / not implemented here.
- No `docs/current_state.md` or truth-replacement summary is created by this closure package.
- Startup/runbook conditionality is deferred and requires a future explicit design package before any change to the hard startup sequence or `docs/runbook.md` can be made.
- `docs/runbook.md` remains part of the hard startup sequence unless a future authorized package changes that.
- Historical `docs/project_status.md` cleanup is not authorized by this closure package.
- This closure does not implement RTK/RTX/TRS tooling, validation-summary command-running wrappers, generated committed indexes or snapshots, memory files, automation, schemas, validators, query-layer changes, or runtime behavior.

## R1/R2 and H-005 boundaries

R1 paired-source reuse and R2 batched-cycle methodology remain design-only unless later approved and locked into repo truth. This guidance does not apply R1 or R2.

H-005 remains under the strict exact-segment runway. WP-S2c-30 remains paused only because the user paused the workflow to insert this token-efficiency guidance sequence. This document does not complete, supersede, authorize, or resume WP-S2c-30.

## What not to do

Do not use token efficiency to:

- skip refreshed-main preflight;
- skip required startup anchors;
- skip changed-file inspection;
- skip integrity views;
- skip registry validators;
- skip full pytest unless a future repo-approved validation-tier document changes that;
- weaken forbidden-scope handling or protected boundaries;
- treat compressed summaries, memory, or cached status as repo truth;
- implement RTK, validation wrappers, broader or authority-bearing code indexes, broader or authority-bearing memory/status snapshots, R1/R2, H-006, Path B, runtime, paper/live, OMS, risk, safe-mode, config, dependency, schema, validator, query-layer, data, policy, scoring, ranking, recommendation, approval, readiness, lifecycle, promotion/demotion, or downstream authority.

## Codex stop conditions

Stop and report if efficiency wording or tooling would require touching protected paths, runtime behavior, paper/live paths, OMS, risk, safe mode, configs, dependencies, schemas, validators, query-layer behavior, data, implementation code, or forbidden package paths without explicit authority.

Stop and report if a package cannot preserve repo truth, active scope, validation discipline, changed-file inspection, project-status overlap guardrails, H-005 strict sequencing, R1/R2 non-application, or WP-S2c-30 pause status.
