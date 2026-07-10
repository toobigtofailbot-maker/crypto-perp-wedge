# WP-DASH-STRATEGY-EXPLORER-06 — Read-only operator Strategy Explorer

- Package class: bounded frontend drilldown / visualization implementation
- Execution mode: local-first, read-only, strategy inspection only
- Base: `main` @ `9c0fb08` (merge of `WP-DASH-CHARTS-PANELS-05`)
- Branch: `claude/strategy-explorer-drilldown-28dbb6`
- Decision: **READY_FOR_REVIEW**

## What this package delivers

A read-only Strategy Explorer that lets an operator open one committed strategy spec and inspect the
evidence behind it. `/strategies/[strategy_id]` gains ten anchored sections:

1. **Identity** — id, names, lifecycle status, source type, approval scope, instrument/market/timeframe/direction, free-parameter cap, not-executable posture.
2. **Evidence & result-population linkage** — every committed result population whose lineage names the spec, with committed denominator, row counts, outcome distribution, validator/review status, manifest and sweep-plan ids, identity hashes, and four denominator reconciliation checks.
3. **Variant grid** — every committed variant result row with all ten committed metrics, printed as committed.
4. **Performance visuals** — outcome distribution, per-variant return histogram, per-variant max-drawdown histogram, and drawdown-vs-return scatter, drawn from real scalars only.
5. **Walk-forward / OOS / robustness / Monte Carlo** — all rendered as explicit absences.
6. **Declared logic** — entry, exit, and filter conditions transcribed from the spec's committed operand tree.
7. **Free parameters** — declared parameter space with defaults, ranges, and allowed values.
8. **Data requirements & backtest assumptions** — host data refs, gap handling, and one assumption column per linked population.
9. **Provenance & source artifacts** — spec path, sha256 digests, cited design docs, source constraints, unresolved claims.
10. **Boundary & non-authority** — the artifacts' own declaration flags, not prose this dashboard invented.

`/strategies` gains evidence indicators per spec (linked population count, variant-row count, or an
explicit "no linked result population" badge), two new stat cards, static facet tallies, and the spec
artifact path.

## Key repo truth established

- **No new API endpoint was needed.** `GET /api/strategies/{id}` already existed and already projected the spec body (`provenance`, `non_execution_declaration`, `timeframe_and_data`, `entry_logic`, `exit_logic`, `filters`, `free_parameters`, `review`). Only a committed fixture for it was missing; six were captured verbatim from the unchanged API via FastAPI `TestClient`, the same provenance path as every other dashboard fixture.
- **The read-only API projects no time series at all.** No equity curve, no drawdown curve, no return series, no walk-forward folds, no Monte Carlo. Robustness statistics (PSR/DSR/MinTRL) are named as withheld in the committed report artifacts. Every one of these renders an honest `deferred` / `withheld` card. Nothing is fabricated, zero-filled, or interpolated.
- **Per-variant parameter values do not exist on this surface.** The API projects only `assignment_hash`; the values live in the parent variant manifest, which no read-only endpoint exposes. The variant grid says so and does not reconstruct them from the spec's declared `allowed_values`.
- Three API projection quirks were **observed and worked around, not fixed** (fixing them is a backend change, out of scope):
  - the detail endpoint overwrites `data.status` with the envelope status, so lifecycle status is read from `GET /api/strategies`;
  - `approval_scope` reads `review.review_scope`, which specs do not carry, so it projects `null` — the real value is read from `review.approval_scope`;
  - `free_parameter_count` reads `free_parameters.count`, which specs do not carry, so it projects `null` — the count shown is derived from `free_parameters.parameters[]` and labelled as derived.
- All 6 committed specs have at least one linked result population, so no spec renders an empty drilldown. 8 populations, 66 committed variant rows.

## Boundary

Frontend Strategy Explorer only. Read-only presentation. No controls, no forms, no state, no writes.
No fabricated metrics. No API, backend, dependency, runtime, paper/live, or protected-path changes.
No candidate, gate, promotion, readiness, ranking, or recommendation semantics are created or implied.
Every Explorer component is a server component; navigation is `next/link` and in-page fragment
anchors only.

## Validation

| Check | Result |
|---|---|
| `npm run typecheck` | PASS |
| `npm run lint` | PASS — no warnings or errors |
| `npm run build` | PASS — 31 static pages; the 6 spec routes now prerender (SSG) |
| `pytest tests/test_operator_dashboard_api.py -q` | PASS — 11 passed |
| `tools.research_query.run --list-views` | PASS — 124 views |
| `tools.registry.validate_result_populations` | OK |
| `tools.registry.validate_candidate_registry` | OK |
| `tools/dev/diff_scope_summary.py` | no forbidden-path matches; exit reason `ok` |
| `git diff --check` / `--cached --check` | clean |
| No-control scan | 0 mutation methods, 0 forms, 0 buttons, 0 handlers, 0 state hooks, 0 controls in served HTML |
| Visual verification | all 6 routes HTTP 200; derived counts match fixtures; unknown ids render the honest unavailable page |

Browser console was **not** checked: the Chrome extension was not connected in this session, and
`preview_start` requires `.claude/launch.json`, a forbidden path for this package. The client-side
chart components are reused unmodified from `WP-DASH-CHARTS-PANELS-05` with the same prop shapes.

## Evidence

- `scratch/WP-DASH-STRATEGY-EXPLORER-06/repo_truth_discovery.md`
- `scratch/WP-DASH-STRATEGY-EXPLORER-06/explorer_inventory.md`
- `scratch/WP-DASH-STRATEGY-EXPLORER-06/no_control_evidence.md`
- `scratch/WP-DASH-STRATEGY-EXPLORER-06/non_authority_assertions.json`
- `scratch/WP-DASH-STRATEGY-EXPLORER-06/validation_summary.txt`
- `scratch/WP-DASH-STRATEGY-EXPLORER-06/generate_strategy_detail_fixtures.py`
