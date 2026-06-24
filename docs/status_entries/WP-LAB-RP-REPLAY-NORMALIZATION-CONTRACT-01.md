# WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01 Branch State

## Scope Summary

Define and implement a reusable Result Population replay and normalization contract for deterministic, family-agnostic replay comparison.

## Base / Branch

- Base: refreshed `origin/main` at PR #563 merge `2b2c3d8`
- Branch: `lab/rp-replay-normalization-contract-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-rp-replay-normalization-contract-01`

## Parallel Forecast

The required forecast is recorded at `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/parallel_touched_file_forecast.md`.

- Owned files only were forecast and used.
- Conditional files were avoided.
- No overlap with candidate-review, walk-forward/OOS gate, robustness diagnostician, canonical crossing, runtime, or funding-accounting work was detected.

## Repo-Truth Discovery

Discovery is recorded at `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/repo_truth_discovery.md`.

Current repo truth showed package-specific replay proof from `WP-RESEARCH-FUNDING-CARRY-02` / PR #563 for `RP-2009` and `RP-7592`, but no reusable replay-normalization contract or owned helper existed.

## Delivered Changes

- Added `docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md`.
- Added read-only helper package under `tools/research_replay/`.
- Added `tools/research_replay/replay_normalization_contract.schema.json`.
- Added focused tests in `tests/test_research_replay_normalization.py`.
- Added required scratch artifacts:
  - `contract_summary.json`
  - `replay_fixture_summary.json`
  - `validation_summary.txt`
  - `main_report_back_guardrail.txt`

## Contract Behavior

The normalized stable payload includes parent hashes, runner identity, data identity, declared RP identity hashes, trial count, variant IDs, status counts, denominator counts, metric set, backtest assumptions, optional sizing metadata, and row metrics/outcomes.

Allowed normalization is limited to administrative timestamps, repo-local absolute path spellings, path separators, and JSON object key order. Metrics, variant IDs, outcomes, row counts, denominator counts, failure reasons, data identity, parent hashes, candidate state, and runtime/risk/capital state remain hash-bearing.

## PR #563 Fixture Evidence

Both PR #563 scratch Result Populations normalize successfully:

- `RP-2009`: normalized stable hash `sha256:9b3efb61a77f59fdb8bb830b233594fa48c2aaab9e880e67424ff0d7e7c1963a`
- `RP-7592`: normalized stable hash `sha256:630cd5eb6a411d20c09d81ce2936eaf24de33543aec7055c6e3ef15e47acbac0`

They intentionally do not match each other because they represent different exit-mode populations with different parent identities, variant IDs, row identities, and metrics.

## FOLLOWUP-01 Hardening (PR #565 review)

After review, replay normalization was hardened to fail closed on two unsafe paths. The branch was rebased onto `origin/main` after the sibling PR #566/#567 merges (clean, no conflicts).

- `_normalize_portable_path` now raises `ReplayNormalizationError` for absolute paths outside the repo root instead of collapsing them to a shared `<absolute-path-outside-repo>` placeholder, which previously hid identity-bearing differences between distinct external paths. Absolute paths under the repo root and relative paths are unchanged.
- `normalized_payload` now raises `ReplayNormalizationError` for any non-object entry in `variant_result_rows` instead of silently skipping it, which previously could corrupt the trial count.
- Added tests `test_repo_root_absolute_path_matches_relative_path`, `test_external_absolute_paths_fail_closed`, and `test_non_object_variant_result_row_fails_closed`.
- Contract doc gained a "Fail-Closed Behavior" section.
- PR #563 scratch populations (`RP-2009`, `RP-7592`) still normalize.

Follow-up validation is recorded in `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/followup_01_review_fix_summary.json` and appended to `validation_summary.txt`.

## Boundary Summary

No strategy run, edge search, funding-with-stops rerun, canonical crossing, candidate lifecycle write, canonical Result Population write, runtime/paper/live, OMS, risk, reconciliation, capital, funding P&L/accounting, provider/API/network fetch, dashboard/scheduler/scout/coordinator implementation, external adoption PoC, or large tracked data change was made.

## Validation Status

Validation commands and outcomes are recorded in `scratch/WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01/validation_summary.txt`.
