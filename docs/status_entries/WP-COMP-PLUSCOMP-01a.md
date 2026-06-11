# WP-COMP-PLUSCOMP-01a — Lock plus-parameter composition design

- Package class: T1 docs-only design / decision
- Branch: `docs/comp-pluscomp-01a-design`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/430
- Scope summary: Locks the docs-only design for `scale_by_one_plus_parameter` as the closed symmetric sibling of existing `scale_by_one_minus_parameter`.
- Authorization basis: Main 5 accepted `WP-COMP-XOVER-01` as complete and selected Direction A, a closed plus-parameter composition design, with the conditional runway `WP-COMP-PLUSCOMP-01a -> clean merge -> WP-COMP-PLUSCOMP-01b -> clean merge -> WP-COMP-PLUSCOMP-01c -> report back`.
- Changed files:
  - `docs/research_pipeline/2026-06-plus_parameter_composition_design.md`
  - `docs/status_entries/WP-COMP-PLUSCOMP-01a.md`
  - `docs/research_pipeline/README.md`
  - `docs/project_status.md`
- Design summary: Docs-only design lock for the closed plus-parameter composed operand; no implementation files are changed.
- Locked semantics: `composition_type=scale_by_one_plus_parameter`; formula `base * (1 + p)`; base operand restricted to `data_ref` or `indicator_ref`; parameter operand restricted to `parameter_ref`; bound parameter range `0 < p < 1`; nesting forbidden; depth-neutral; closed grammar only.
- Validation summary:
  - `git diff --check`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows, via single-process query-layer check after the per-view subprocess loop exceeded the tool timeout.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
  - `git diff --cached --check`: pass.
  - `git diff --cached --name-only`: no staged files after final commit; pre-commit staged scope was the expected four files.
- Boundary summary: No schema, validator, compiler, catalog, Strategy Spec, variant manifest, sweep plan, result population, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change. No ranking, recommendation, readiness, promotion, canonical-use, or execution authority is created.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| plus composition design doc created | `docs/research_pipeline/2026-06-plus_parameter_composition_design.md` | satisfied |
| status fragment created | `docs/status_entries/WP-COMP-PLUSCOMP-01a.md` | satisfied |
| README index entry added | `docs/research_pipeline/README.md` | satisfied |
| project-status pointer added | `docs/project_status.md` | satisfied |
| id locked as `scale_by_one_plus_parameter` | design doc locked form | satisfied |
| semantics locked as `base * (1 + p)` | design doc locked form | satisfied |
| base operand restriction locked | design doc locked form | satisfied |
| parameter operand restriction locked | design doc locked form | satisfied |
| `(0, 1)` exclusive bound locked | design doc locked form | satisfied |
| nesting forbidden | design doc locked form | satisfied |
| expression language forbidden | design doc grammar and stop rules | satisfied |
| later 01b/01c sequence documented | design doc required later package sequence | satisfied |
| no implementation files changed | diff scope and changed-file list | satisfied |
| T1 validation run | validation summary | satisfied |
| PR body/status finality clean | final PR readiness gate | satisfied |
| no forbidden paths touched | diff scope and changed-file list | satisfied |

- Merge status: PR #430 is open and non-draft; GitHub reports `mergeable=MERGEABLE`; final readiness checks are recorded in the PR body and report-back.
- Next authority: After this PR merges cleanly, Side may draft `WP-COMP-PLUSCOMP-01b` only from refreshed `origin/main` and only if no competing `docs/project_status.md` PR is open. This fragment does not authorize 01b execution before 01a merges.
