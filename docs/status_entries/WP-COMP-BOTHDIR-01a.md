# WP-COMP-BOTHDIR-01a - Design both-direction semantics

- Package class: T1 docs-only design / semantics decision surface
- Branch: `docs/comp-bothdir-01a-semantics`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/433
- Scope summary: Creates a docs-only design surface for closed `direction: "both"` Strategy Spec semantics.
- Authorization basis: Main 5 accepted the completed PLUSCOMP runway and selected Direction A, both-direction semantics design first, authorizing exactly WP-COMP-BOTHDIR-01a for docs-only design, project-status pointer, README index entry, and status fragment.
- Changed files:
  - `docs/research_pipeline/2026-06-both_direction_semantics_design.md`
  - `docs/status_entries/WP-COMP-BOTHDIR-01a.md`
  - `docs/research_pipeline/README.md`
  - `docs/project_status.md`
- Design summary: The design evaluates compiler mirroring, explicit side-labeled long/short groups, and side-tagged groups within the current structure for `direction: "both"`. It preserves single-stream position intent, deterministic no-lookahead evaluation, closed grammar, condition-group depth no greater than 3, and no expression-language posture.
- Recommended candidate semantics: Use explicit side-labeled long and short entry groups, with side-specific exits and one mutually exclusive compiled signal stream. When flat, long-only fire emits `1.0`, short-only fire emits `-1.0`, simultaneous long/short fire emits `0.0`, and no fire emits `0.0`.
- Validation summary:
  - `git diff --check`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
  - `git diff --cached --check`: pass.
  - `git diff --cached --name-only`: pass, expected four files.
- Boundary summary: Docs/status only. No schema, validator, compiler, test, Strategy Spec, variant manifest, sweep plan, result population, catalog, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| both-direction design doc created | `docs/research_pipeline/2026-06-both_direction_semantics_design.md` | satisfied |
| three representation options evaluated | design doc options matrix | satisfied |
| candidate semantics recommended for Main lock | design doc recommended candidate semantics | satisfied |
| simultaneous-fire conflict rule designed | design doc simultaneous-fire section | satisfied |
| mutual exclusivity addressed | design doc position mutual exclusivity section | satisfied |
| per-side exits addressed | design doc exit interaction section | satisfied |
| determinism/no-lookahead addressed | design doc determinism section | satisfied |
| closed grammar and depth <= 3 addressed | design doc options and determinism sections | satisfied |
| downstream 01b/01c implications described without authorization | design doc downstream implementation implications | satisfied |
| status fragment created | this file | satisfied |
| README index entry added | `docs/research_pipeline/README.md` | satisfied |
| project-status pointer added | `docs/project_status.md` | satisfied |
| no implementation files changed | final changed-file list | satisfied |
| T1 validation run | validation summary in this fragment | satisfied |
| PR body/status finality clean | PR body, status fragment, and final readiness gate | satisfied |
| no forbidden paths touched | final diff scope | satisfied |

- Merge status: PR #433 is open, non-draft, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: After this PR merges, report the design result to Main 5 and wait for Main 5's locked representation and next capsule. Do not draft WP-COMP-BOTHDIR-01b automatically.
