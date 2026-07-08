# Readiness Surface Contract

## Purpose

The readiness display is an operator-facing, read-only routing surface for lab
idea intake. It answers:

- Can this family / feature / data requirement be tested now?
- If not, why not?
- Is the blocker data availability, compiler support, runner support, simulator
  realism, vendor/capture dependency, or protected phase gating?
- What is the next prerequisite category without authorizing it?

## Required Fields

Each item carries:

- `subject_id`
- `label`
- `feature_or_family`
- `status`
- `reason_code`
- `required_source_evidence`
- `current_repo_support`
- `blocker_detail`
- `next_prerequisite_category`
- `non_authority_flags`

## Status Vocabulary

- `testable_now_with_current_public_history`
- `testable_now_with_current_caveats`
- `needs_local_full_history_materialization`
- `needs_vendor_or_captured_history`
- `needs_runner_or_compiler_support`
- `needs_simulator_realism_upgrade`
- `go_gated_or_paper_phase_only`
- `protected_or_out_of_scope`
- `unknown_needs_review`

## Non-Authority Rules

The display must not:

- acquire data;
- contact providers, vendors, public/private APIs, or credentials;
- change runner, compiler, backtester, schema, validator, query-layer, data
  catalog, dependency, or config behavior;
- write canonical evidence, candidate lifecycle records, Strategy Specs, Variant
  Manifests, Sweep Plans, Result Populations, or trial-log entries;
- authorize blocked ideas, edge-search, crossing, promotion, paper/live/runtime,
  scheduler/autonomy, or protected-path work.

## Output Contract

- `python -m tools.lab_readiness.run --json` prints deterministic JSON.
- `python -m tools.lab_readiness.run --markdown` prints deterministic Markdown.
- `python -m tools.lab_readiness.run --out-dir <path>` writes only
  `readiness.json` and `readiness.md` under `<path>`.
