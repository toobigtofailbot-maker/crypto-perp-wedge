# WP-LAB-DOCS-COMPLETION-MAP-01 — Document research-lab completion map and deferred boundaries

## Decision

**Complete.** Docs-only. No implementation files.

## Summary

Created the authoritative committed completion map for the research lab:
`docs/research/LAB_COMPLETION_MAP.md`. The map documents, for the current
human-driven / no-edge-search phase:

- **Built and complete** — research engine / primitives + deterministic runner,
  Result Populations + validators, query layer, replay-normalization contract,
  walk-forward / OOS gate, robustness / candidate-review reach, coordinator
  state model (#568), results dashboard (#569), daily brief / weekly report
  (#570), approval / gate queue (#572), default-off scheduler shell (#571), and
  the funding `H-FUNDING-RATE-POSITIONING-FADE-01 = NO-GO` conclusion.
- **Inert / default-off** — scheduler shell (no executor, no-op only) and the
  read-only approval queue.
- **Deferred-B** — autonomous scheduling / run triggering, research scout,
  notification firing, approval-queue writes, candidate lifecycle writes,
  coordinator transition execution, first real canonical crossing, and all live
  candidate-flow-dependent behavior — each with its exact deferral reason, all
  requiring separate operator authorization **and** real candidate flow.
- **GO-gated execution-machine bucket** — paper / shadow / live, runtime
  monitoring, execution machine, broker / exchange / order paths, OMS / risk /
  reconciliation / capital, safe-mode / kill-switch operational authority.
- **Edge-search hold**, **what remains buildable now** (read-only legibility
  only), **what is not buildable without edge-search / live candidate flow**,
  **what is not authorized**, the **definition of done** for the no-edge-search
  scope, and **drift guardrails**.

The document does not recommend resuming edge-search and adds no new
architecture decision.

## Boundary

- Edge-search: not resumed; explicitly held.
- Implementation: none — docs-only.
- Strategy recommendation: none; no strategy-family prioritization.
- Runtime / paper / live: untouched; classified GO-gated only.
- Protected paths (OMS, risk, reconciliation, capital, broker, exchange,
  candidate registry, canonical Result Populations, trial logs): untouched.

## Validation

- `python -m tools.research_query.run --list-views` — ran, lists views.
- `python tools/dev/diff_scope_summary.py` — only the two allowed new files
  (`docs/research/LAB_COMPLETION_MAP.md`,
  `scratch/WP-LAB-DOCS-COMPLETION-MAP-01/...`); no forbidden-path matches.
- `git diff --check` — clean (exit 0).
- Full pytest: not run (docs-only change; no code touched).

## Files

- `docs/research/LAB_COMPLETION_MAP.md` (new)
- `docs/status_entries/WP-LAB-DOCS-COMPLETION-MAP-01.md` (new)
- `scratch/WP-LAB-DOCS-COMPLETION-MAP-01/repo_truth_discovery.md` (new)
- `scratch/WP-LAB-DOCS-COMPLETION-MAP-01/completion_map_summary.json` (new)
- `scratch/WP-LAB-DOCS-COMPLETION-MAP-01/validation_summary.txt` (new)
- `scratch/WP-LAB-DOCS-COMPLETION-MAP-01/main_report_back_guardrail.txt` (new)
