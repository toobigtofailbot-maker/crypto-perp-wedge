# WP-LAB-WALKFORWARD-OOS-GATE-01 Repo-Truth Discovery

## Search Command

The required broad discovery command was run from the package worktree:

`Select-String -Path docs\**\*.md,tools\**\*.py,tests\**\*.py,research\**\*.json,scratch\**\*.json,scratch\**\*.md -Pattern "walk-forward|walk_forward|OOS|out-of-sample|purge|embargo|candidate gate|candidate-review|Result Population|dry-run|WP-RESEARCH-FUNDING-CARRY-02" -CaseSensitive:$false`

An `rg` equivalent was also run to identify exact files for targeted reads.

## Current Walk-Forward / OOS Scripts and Hooks

- `tools/walkforward/run_walkforward_scratch.py` executes explicit fold
  manifests through the existing offline runner and writes scratch-only
  reports.
- `tools/walkforward/purged_folds.py` builds repo-native purged/embargoed
  fold manifests using explicit bar counts.
- `tools/registry/validate_walkforward_fold_manifest.py` validates existing
  fold-manifest chronology, lineage, denominator posture, gap posture, and
  non-authority fields.
- `tools/registry/validate_walkforward_run_report.py` validates scratch
  walk-forward run reports and rejects authority-like fields.

## PR #563 / Funding Dry-Run OOS Summary

- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md` records that the
  funding-carry package ran one dry-run-only non-overlapping OOS window and
  wrote no canonical walk-forward artifact.
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/walk_forward_summary.json` records
  `status=completed_dry_run_only`, `purge_embargo=not_implemented_deferred_by_design`,
  `classification=NO-GO`, and `canonical_result_population_written=false`.
- Because purge/embargo is explicitly not implemented in that dry-run summary,
  it is not sufficient for a rigorous standard OOS gate pass.

## Purged Walk-Forward Evidence

- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_manifest.json`
  records `purge.bars=96`, `embargo.bars=32`, `window_count=2`, and
  full-population carry-forward semantics.
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_walkforward_run_report.json`
  records run `WF-RUN-40BB0B209274054B`, 2 successful folds, 16 comparable
  variant pairs, and preserved denominator posture.
- Current OOS evidence is non-canonical scratch evidence only.

## Candidate-Review Gate Logic

- `tools/candidate_lifecycle/lifecycle_engine.py` is scratch-only and requires
  `walkforward_run_ref` for `research_concluded -> paper_eligible` review
  packets.
- Missing `walkforward_run_ref` already blocks paper-eligibility packet
  preparation.
- No existing standard OOS gate artifact or OOS gate decision field exists in
  the lifecycle engine. This package therefore adds read-only evaluation in
  owned `tools/oos_gate/**` files instead of mutating lifecycle code.

## Result Population Validator

- `tools/registry/validate_result_populations.py` validates committed Result
  Populations under `research/result_populations`.
- Result Populations explicitly carry non-authority declarations and do not
  grant gate, recommendation, ranking, readiness, transition, runtime, or
  paper/live authority.
- This package does not modify Result Population schemas, validators, or
  artifacts.

## Data Availability Validator

- `tools/registry/validate_data_feature_availability.py` is invoked by the
  Result Population validator when data-availability claims are present.
- This package does not alter data availability catalogs, validators, source
  data, or data lineage.

## Research Query Views

- `tools/research_query/run.py` and `tools/research_query/views.sql` expose
  descriptive read-only query surfaces, including result population integrity
  views.
- This package does not add or modify query-layer behavior.

## Decision

Continue. The required work can be completed inside owned files with no
overlap against forbidden parallel areas and no need to touch conditional
files.
