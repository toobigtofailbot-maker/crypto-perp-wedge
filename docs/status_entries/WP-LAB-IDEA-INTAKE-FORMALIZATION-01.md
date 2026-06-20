# WP-LAB-IDEA-INTAKE-FORMALIZATION-01 - Structured idea intake and draft formalization

## WP id / title

- WP id: `WP-LAB-IDEA-INTAKE-FORMALIZATION-01`
- Title: Add structured idea intake and draft formalization path.
- Decision: `COMPLETE`.

## Branch / PR

- Branch: `lab/idea-intake-formalization-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-idea-intake-formalization-01`
- Base: `origin/main` at `fcb8a8f`.
- Rebase result: branch was already current with `origin/main`; no conflicts.
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/523`

## Package class

Tier 3 schema / workflow tooling / draft formalization; additive,
scratch-only, and non-canonical.

## Repo-truth discovery

- The merged workflow generator is deterministic, scratch-only, and tied to a
  fixed Strategy Spec / parameter family.
- Current repo capability includes locked OHLCV/funding/mark/index/premium data
  streams and the `sma`, `ema`, `atr`, and `stddev` indicator catalog entries.
- No repo-owned live LLM/API client abstraction or safe model test adapter
  exists. The only LLM-related code paths found are non-live agent stubs.
- Therefore the formalizer is deterministic and local. Workflow generation is
  eligible only for an exact match to the merged generator family. Live LLM
  integration remains a separately gated future option.

## Scope summary

The package adds a closed structured research-idea contract and deterministic
formalization path for JSON and sufficiently explicit plain text. It performs
early rejection for ambiguous, unbounded, non-causal, leakage-bearing,
executable-code, trading-instruction, or capital-instruction input; classifies
current-lab versus upgrade-dependent ideas; maps known data/features; and can
prepare or optionally invoke the existing scratch workflow generator for its
exact bounded family.

All outputs carry draft/non-authority flags. Draft-to-preregistration remains a
human-gated future action.

## Changed files

- `research/schemas/research_idea.schema.json`
- `tools/research_workflow/validate_research_idea.py`
- `tools/research_workflow/formalize_research_idea.py`
- `tests/test_research_idea_validator.py`
- `tests/test_formalize_research_idea.py`
- `tests/fixtures/research_ideas/valid_research_idea_current_lab.json`
- `tests/fixtures/research_ideas/valid_research_idea_upgrade_dependent.json`
- `tests/fixtures/research_ideas/invalid_research_idea_unbounded_search.json`
- `tests/fixtures/research_ideas/invalid_research_idea_non_causal.json`
- `scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01/README.md`
- `scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01/example_research_idea.json`
- `scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01/example_formalization_report.json`
- `scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01/draft_workflow_parameter_space.json`
- `docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md`

## Validation summary

Validation was rerun after the final rebase check using the repo root Python
3.11 virtualenv unless otherwise stated.

- `python -m pytest tests/test_research_idea_validator.py tests/test_formalize_research_idea.py tests/test_draft_grid_generator.py -q`: PASS, 26 tests.
- `python -m tools.research_workflow.validate_research_idea tests/fixtures/research_ideas/valid_research_idea_current_lab.json`: PASS.
- `python -m tools.research_workflow.validate_research_idea tests/fixtures/research_ideas/valid_research_idea_upgrade_dependent.json`: PASS.
- `python -m tools.research_workflow.formalize_research_idea --input tests/fixtures/research_ideas/valid_research_idea_current_lab.json --output-dir scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01`: PASS; classified `current_lab_testable`, wrote validated scratch example and eligible draft workflow input, and did not invoke workflow generation.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS as an advisory check; before commit it listed only the 13 scoped implementation/example files. Its generic `research/` match was the explicitly authorized new schema. After commit the helper correctly reported no local working-tree changes.
- `git diff origin/main...HEAD --check` and `git diff --check`: PASS.
- Python syntax compilation for both new tool modules: PASS.
- Direct changed-file inspection: complete for every changed file.

Full-suite disclosure:

- Ambient Python 3.14 `python -m pytest -q`: collection blocked by 23 missing-dependency errors (`binance`, `pandas`, and `numpy`); this is not counted as a pass.
- Repo Python 3.11 virtualenv `python -m pytest -q`: did not finish within the 1,200-second command bound and emitted no failure output before termination; this is not counted as a pass.

## Boundary summary

- Canonical Strategy Spec / Variant Manifest / Sweep Plan writes: none.
- Canonical Result Population, candidate, trial-log, preregistration, evidence,
  ranking, recommendation, screen-gate, readiness, or promotion changes: none.
- `lib/backtest.py`, `lib/evaluation.py`, runner/backtester, query-layer, and
  dashboard changes: none.
- Runtime, paper/live, OMS, risk, reconciliation, safe mode, kill switch,
  broker, exchange, order, capital, credential, or API-config changes: none.
- Live LLM/model/network calls and credentials: none.
- Dependency changes: none.
- `docs/project_status.md`: not modified.

## Merge status

- PR #523 is ready for review.
- Focused, adjacent, validator, demo, query-discovery, syntax, scope, and diff
  checks pass. Full-suite limitations are disclosed above and are not claimed
  as passing evidence.

## Next dependency / runway note

A live LLM adapter or any draft-to-preregistration path requires a separate
approved package with a safe mocked adapter, deterministic post-model
validation, and an explicit human gate. This package grants no such authority.
