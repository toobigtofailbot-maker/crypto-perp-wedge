# Memory / Status Snapshot Design

## Scope and non-authority

This document is design-only. It does not implement a memory/status snapshot helper, create or commit generated snapshot files, reduce validation, or alter repo-truth precedence.

Manual steps for this design package: none.

A future memory/status snapshot is advisory only. It must never become source of truth, validation authority, implementation authority, runtime authority, protected-boundary authority, evidence authority, or downstream decision authority.

## Problem statement

Codex and Side often need a compact reminder of current workflow state, recent package sequence, paused/resumed state, helper/tooling status, and likely next packages. A bounded snapshot could reduce context load, but a stale or overtrusted snapshot could become pseudo-truth around active work packages, branch or PR state, artifact IDs, exact-segment counts, and protected-boundary authority.

## Design goal

A future helper may summarize current workflow status for context efficiency while preserving refreshed repo inspection, active package scope, `docs/project_status.md`, direct artifact/count verification, branch/PR checks, validation commands, and Side semantic review as authoritative workflow surfaces.

## Source-of-truth boundary

Current merged repo files remain source of truth. Active package scope remains source of truth for the package. `docs/project_status.md` remains the project state anchor.

Current branch and PR state must be verified live through local git and GitHub before use. Artifact IDs and exact-segment counts must be verified from current repo files or query surfaces before use.

A future snapshot must not replace:

- refreshed-main preflight;
- `docs/project_status.md`;
- branch or PR checks;
- direct file inspection or changed-file inspection;
- direct artifact or count verification;
- integrity views, registry validators, scoped pytest, full pytest, or Side semantic review.

## Allowed future snapshot behavior

A future snapshot may summarize:

- latest known package sequence;
- paused or resumed workflow state;
- known next candidate packages;
- implemented efficiency guidance, designs, and helpers;
- future efficiency items;
- open PR summary and project-status conflict state;
- known stop triggers and protected-boundary notes;
- validation posture reminders.

The snapshot may point Codex toward likely current-state files, but Codex must still inspect current repo files directly before relying on their contents or changing them.

## Disallowed behavior

A future snapshot must not authorize implementation, runtime behavior, protected-path changes, schema changes, validator changes, query-layer changes, policy, scoring, ranking, recommendation, approval, readiness, lifecycle, promotion, demotion, or downstream authority.

It must not replace current repo truth, active package scope, refreshed-main preflight, `docs/project_status.md`, branch/PR checks, direct artifact/count verification, validators, integrity views, tests, artifact/query evidence, or Side semantic review.

It must not authorize WP-S2c-30 resumption without explicit user/Karl/Side instruction. It must not create R1/R2, H-006, Path B, runtime, paper/live, OMS, risk, safe-mode, config, dependency, data, policy, approval, readiness, lifecycle, promotion/demotion, or downstream authority.

## Suggested future snapshot inputs

Design-only possible inputs:

- `AGENTS.md`;
- `CLAUDE_START_HERE.md`;
- `docs/onboarding/WORKFLOW.md`;
- `docs/project_status.md`;
- `docs/ai/codex/`;
- `tools/dev/`;
- selected `docs/research_pipeline/` files if explicitly scoped;
- current git branch;
- current `HEAD` SHA;
- `git status --short`;
- open PR list and `docs/project_status.md` conflict check.

Future implementation should exclude or carefully gate:

- `data/`;
- `configs/`;
- `.claude/`;
- runtime and protected implementation paths;
- large artifacts;
- private files;
- secrets;
- generated trial outputs.

## Suggested future snapshot outputs

Design-only possible outputs:

- `repo_root`;
- `source_commit`;
- `branch`;
- `generated_at_utc`;
- `command`;
- `snapshot_scope`;
- `included_sources`;
- `excluded_sources`;
- `latest_recorded_wp`;
- `paused_workflow_state`;
- `next_expected_packages`;
- `implemented_efficiency_helpers`;
- `future_efficiency_items`;
- `open_pr_summary`;
- `project_status_conflict_state`;
- `staleness_rules`;
- `protected_boundary_notes`;
- `advisory_note`.

## Freshness and staleness rules

A future generated snapshot must include generation timestamp, source commit SHA, branch name, command used, included sources, excluded sources, and an advisory-only note.

A future generated snapshot must be treated stale when:

- source commit SHA differs from current `HEAD`;
- `docs/project_status.md` changed after generation;
- active branch differs from the generated branch;
- any open PR touches `docs/project_status.md`;
- active package scope differs from snapshot scope;
- artifact IDs or counts in the snapshot are relevant to the active task;
- snapshot generation command or source set is unknown.

If stale or missing, Codex must regenerate under explicit package scope or ignore the snapshot. A stale snapshot must not be used without regeneration and direct current repo verification.

## Protected-boundary handling

Protected and runtime paths must be excluded by default or marked protected and non-authoritative. A future snapshot must not include protected-path content unless a later package explicitly allows it.

A future snapshot must not include secrets, `.env` values, keys, tokens, exchange credentials, private data files, large raw data files, or protected-path content unless explicitly allowed by a later package.

The snapshot must avoid embedding full source files. It should summarize status, file paths, package sequence, helper/tooling state, and validation posture only.

## Suggested future CLI shape

Design only; any actual CLI must be approved in a later implementation work package.

```powershell
python tools/dev/status_snapshot.py --scope token-efficiency
python tools/dev/status_snapshot.py --scope active-workflow
python tools/dev/status_snapshot.py --json
python tools/dev/status_snapshot.py --check-stale
python tools/dev/status_snapshot.py --output <path>
```

## Suggested future JSON shape

Design-only JSON keys:

```json
{
  "repo_root": "",
  "source_commit": "",
  "branch": "",
  "generated_at_utc": "",
  "command": "",
  "snapshot_scope": "",
  "included_sources": [],
  "excluded_sources": [],
  "latest_recorded_wp": "",
  "paused_workflow_state": "",
  "next_expected_packages": [],
  "implemented_efficiency_helpers": [],
  "future_efficiency_items": [],
  "open_pr_summary": [],
  "project_status_conflict_state": "",
  "staleness_rules": [],
  "protected_boundary_notes": [],
  "advisory_note": ""
}
```

JSON output is advisory and must not replace direct inspection, validation evidence, branch/PR checks, or artifact/count verification.

## Suggested future tests

A future implementation must test:

- advisory output wording;
- stale-snapshot detection for source commit mismatch;
- stale-snapshot detection when `docs/project_status.md` changed after generation;
- active branch mismatch detection;
- active package scope mismatch detection;
- open PR conflict handling for `docs/project_status.md`;
- artifact/count relevance requiring direct verification;
- unknown generation command or source set handling;
- protected-path exclusion or protected non-authoritative marking;
- no file mutation outside an explicitly approved output path;
- no git mutation;
- no dependency addition;
- no external service calls;
- secret, `.env`, key, token, credential, private-file, large-data, and protected-content exclusion;
- JSON output includes required advisory metadata;
- no authority claims.

## Manual-step rule

Manual steps for this design package: none.

Manual steps may become relevant only if a later implementation package requires local setup. The default expected future implementation should be repo-local, standard-library-only, and require no manual user setup.

## Implementation prerequisites

A future implementation package must explicitly approve helper path, output path behavior, scope presets, included and excluded source rules, staleness checks, open PR checks, JSON shape, tests, and validation commands.

The default future implementation must be local-only and standard-library-only unless a later package explicitly approves dependencies. It must not send repo contents to external services.

## Stop conditions

Stop if future wording or implementation would:

- make the snapshot source of truth or authority;
- let the snapshot replace refreshed-main preflight, current repo inspection, active package scope, `docs/project_status.md`, branch/PR checks, direct artifact/count verification, validators, integrity views, tests, artifact/query evidence, or Side semantic review;
- permit using a stale snapshot without regeneration and direct current repo verification;
- reduce validation;
- authorize runtime, protected-path, schema, validator, query-layer, policy, scoring, ranking, recommendation, readiness, lifecycle, promotion, demotion, or downstream authority;
- include secrets, `.env` values, keys, tokens, exchange credentials, private data files, large raw data files, or protected-path content without later explicit authority;
- add dependencies or external service calls without later explicit authority;
- create generated snapshot files without package approval.

## Future implementation package requirements

A future implementation package must be narrow and mergeable. It must inspect current repo truth, preserve advisory-only behavior, include explicit allowed changed files, prove no protected-path authority, prove no validation reduction, prove no stale pseudo-truth behavior, run targeted helper tests, run scoped regression, run full pytest, check all discovered `v_integrity_*` views, run all registry validators, and confirm no competing `docs/project_status.md` PR exists if status is updated.
