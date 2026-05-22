# Code-Index Design

## Scope and non-authority

This document is design-only. It does not implement a code-index helper, create or commit generated index files, reduce validation, or alter repo-truth precedence.

Manual steps for this design package: none.

A future code index is advisory only. It must never become source of truth, semantic authority, validation authority, implementation authority, runtime authority, or downstream decision authority.

## Problem statement

Codex and Side often need to locate likely files quickly without loading unrelated repo context. A bounded code index could improve context efficiency, but an unbounded or stale index could become pseudo-truth, hide repo drift, or cause direct file inspection to be skipped.

## Design goal

A future helper may summarize repo structure and likely inspection targets for context efficiency while preserving current merged repo files, active package scope, direct file inspection, changed-file inspection, validators, integrity views, tests, artifact/query evidence, and Side semantic review as the authoritative workflow.

## Source-of-truth boundary

Current merged repo files remain source of truth. Active package scope remains source of truth for the package. `docs/project_status.md` remains the current-state anchor.

A future index must not replace:

- direct file inspection;
- changed-file inspection;
- `docs/project_status.md`;
- artifact, query, validator, or test evidence;
- integrity views, registry validators, scoped pytest, or full pytest;
- Side semantic review.

## Allowed future index behavior

A future index may help locate files, summarize stable repo structure, suggest likely inspection targets, and report coarse module, test, and documentation summaries.

It may point Codex toward relevant files for a package, but Codex must still inspect the current files directly before relying on their contents or changing them.

## Disallowed behavior

A future index must not authorize implementation, runtime behavior, protected-path changes, schema changes, validator changes, query-layer changes, policy, scoring, ranking, recommendation, readiness, lifecycle, promotion, demotion, or downstream authority.

It must not be used to skip required validation, direct inspection, changed-file inspection, `docs/project_status.md`, artifact evidence, query evidence, validator evidence, test evidence, or Side semantic review.

It must not send repo contents to external services, add dependencies without later package approval, include secrets, or embed full source files.

## Suggested future index inputs

Design-only possible inputs:

- `AGENTS.md`;
- `CLAUDE_START_HERE.md`;
- `docs/onboarding/WORKFLOW.md`;
- `docs/project_status.md`;
- `docs/ai/codex/`;
- `tools/`;
- `tests/`;
- `research/` metadata paths if explicitly scoped;
- selected `docs/research_pipeline/` files if explicitly scoped.

Future implementation should exclude or carefully gate:

- `data/`;
- `configs/`;
- `.claude/`;
- runtime and protected implementation paths;
- large artifacts;
- private files;
- secrets.

## Suggested future index outputs

Design-only possible outputs:

- `repo_root`;
- `source_commit`;
- `generated_at_utc`;
- `index_scope`;
- `excluded_paths`;
- `path_summaries`;
- `module_summaries`;
- `test_summaries`;
- `doc_summaries`;
- `protected_path_notes`;
- `staleness_rules`;
- `advisory_note`.

## Freshness and staleness rules

A future generated index must include generation timestamp, source commit SHA, command used, included path prefixes, excluded path prefixes, and an advisory-only note.

A future generated index must be treated stale when:

- source commit SHA differs from current `HEAD`;
- relevant files changed after generation;
- active package touches paths outside the indexed scope;
- index generation command or exclusions are unknown.

If stale or missing, Codex must regenerate under explicit package scope or ignore the index. A stale index must not be used without regeneration or direct current-file verification.

## Protected-boundary handling

Protected and runtime paths must be excluded by default or marked protected and non-authoritative. A future index must not include protected-path content unless a later package explicitly allows it.

The index must not authorize contact with runtime, paper/live, OMS, risk, safe-mode, config, dependency, schema, validator, query-layer, data, or protected-path behavior.

## Suggested future CLI shape

Design only; any actual CLI must be approved in a later implementation work package.

```powershell
python tools/dev/code_index.py --scope docs-ai
python tools/dev/code_index.py --scope tools-dev
python tools/dev/code_index.py --scope tests
python tools/dev/code_index.py --json
python tools/dev/code_index.py --check-stale
python tools/dev/code_index.py --output <path>
```

## Suggested future JSON shape

Design-only JSON keys:

```json
{
  "repo_root": "",
  "source_commit": "",
  "generated_at_utc": "",
  "command": "",
  "index_scope": [],
  "included_paths": [],
  "excluded_paths": [],
  "path_summaries": [],
  "module_summaries": [],
  "test_summaries": [],
  "doc_summaries": [],
  "protected_path_notes": [],
  "staleness_rules": [],
  "advisory_note": ""
}
```

JSON output is advisory and must not replace direct inspection or validation evidence.

## Suggested future tests

A future implementation must test:

- advisory output wording;
- stale-index detection for source commit mismatch;
- stale-index detection for relevant file changes after generation;
- stale-index detection for active scope outside indexed scope;
- stale-index detection for unknown command or exclusions;
- protected-path exclusion or protected non-authoritative marking;
- no file mutation outside an explicitly approved output path;
- no git mutation;
- no dependency addition;
- no external service calls;
- secret, `.env`, key, token, credential, private-file, large-data, and protected-content exclusion;
- JSON output includes required advisory metadata.

## Manual-step rule

Manual steps for this design package: none.

Manual steps may become relevant only if a later implementation package requires local setup. The default expected future implementation should be repo-local, standard-library-only, and require no manual user setup.

## Implementation prerequisites

A future implementation package must explicitly approve helper path, output path behavior, scope presets, exclusion rules, staleness checks, JSON shape, tests, and validation commands.

The default future implementation must be local-only and standard-library-only unless a later package explicitly approves dependencies. It must not send repo contents to external services.

It must avoid embedding full source files and should summarize paths, module names, docstrings or signatures where safe, and dependency hints only.

## Stop conditions

Stop if future wording or implementation would:

- make the index source of truth or semantic authority;
- let the index replace direct file inspection, changed-file inspection, `docs/project_status.md`, validators, integrity views, tests, artifact/query evidence, or Side semantic review;
- permit using a stale index without regeneration or direct current-file verification;
- reduce validation;
- authorize runtime, protected-path, schema, validator, query-layer, policy, scoring, ranking, recommendation, readiness, lifecycle, promotion, demotion, or downstream authority;
- include secrets, `.env` values, keys, tokens, exchange credentials, private data files, large raw data files, or protected-path content without later explicit authority;
- add dependencies or external service calls without later explicit authority;
- create generated index files without package approval.

## Future implementation package requirements

A future implementation package must be narrow and mergeable. It must inspect current repo truth, preserve advisory-only behavior, include explicit allowed changed files, prove no protected-path authority, prove no validation reduction, run targeted helper tests, run scoped regression, run full pytest, check all discovered `v_integrity_*` views, run all registry validators, and confirm no competing `docs/project_status.md` PR exists if status is updated.
