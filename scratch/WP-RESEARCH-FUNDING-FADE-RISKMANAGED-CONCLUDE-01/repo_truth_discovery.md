# Repo Truth Discovery

Package: `WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01`

## Base

- Base branch: `main`
- Base commit: `788f46c90498f6179d1d875ab9155b16e80505c7`
- PR #581 merge observed: yes
- PR #581 merge commit observed by `gh pr view 581`: `788f46c90498f6179d1d875ab9155b16e80505c7`
- PR #581 title: `WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01 stage1 triage`
- PR #581 merged at: `2026-06-29T16:33:05Z`

## Stage-1 Verdict Source

- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.json`
- `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.md`
- Verdict: `no_go`
- Planned denominator rows: 108
- Executed rows: 108
- Blocked / errored / invalid / data-unavailable rows: 0 / 0 / 0 / 0

## Existing Funding-Fade Synthesis And Conclusion Locations

- Existing synthesis document: `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
- Existing prior conclusion status entry: `docs/status_entries/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01.md`
- Prior scratch conclusion traceability: `scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json`
- Prior funding-fade result populations remain scratch-only: `RP-2009`, `RP-7592`
- Current risk-managed Stage-1 triage status entry: `docs/status_entries/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01.md`

## Existing Operator / Coordinator Visibility Binding Mechanism

- `tools/lab_state/run.py` defines static read-only subject bundles consumed by `tools/lab_state`, `tools/lab_dashboard`, and `tools/lab_reporting`.
- Existing surfaces consume `tools.lab_state.run.SUBJECTS`; no runtime, paper/live, OMS, risk, exchange, order, or reconciliation path is involved.
- Existing dashboard/reporting tests exercise this path through `tests/test_lab_state_resolver.py`, `tests/test_lab_dashboard.py`, and `tests/test_lab_reporting.py`.

## Files Selected For Update

- `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md`
- `docs/status_entries/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01.md`
- `scratch/WP-RESEARCH-FUNDING-FADE-RISKMANAGED-CONCLUDE-01/*`
- `tools/lab_state/run.py`
- `tests/test_lab_state_resolver.py`
- `tests/test_lab_dashboard.py`
- `tests/test_lab_reporting.py`

## Files Intentionally Left Unchanged

- `research/result_populations/**`
- `research/candidate_registry.jsonl`
- `configs/**`
- `data/**`
- `lib/**`
- Runtime, paper/live, OMS, risk, reconciliation, broker, exchange, and order paths
- Stage-1 source artifacts under `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/**`

## Naming / Path Adjustments

- The existing synthesis document covers the prior funding positioning-fade family, so it was updated instead of creating a second competing synthesis document.
- The operator/coordinator subject key uses `funding_fade_riskmanaged_no_go` to distinguish this concluded risk-managed triage from the prior `funding_positioning_fade_no_go` subject.
