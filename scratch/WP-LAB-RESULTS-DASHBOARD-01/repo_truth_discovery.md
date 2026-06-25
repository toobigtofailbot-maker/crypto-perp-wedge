# WP-LAB-RESULTS-DASHBOARD-01 — Repo-truth discovery

## Dependency check

`WP-LAB-COORDINATOR-STATE-MODEL-01` is **merged** (PR #568, merged
2026-06-25T18:28:35Z, merge commit `5107b86` on `origin/main`). The worktree was
rebased onto the post-merge `origin/main` before any work began, so the
dependency is present:

- `docs/research/LAB_COORDINATOR_STATE_MODEL.md`
- `tools/lab_state/{model,resolver,run}.py`
- `tests/test_lab_state_model.py`, `tests/test_lab_state_resolver.py`

Dependency satisfied — not blocked.

## Existing dashboard / report / state surfaces found

Discovery command (package §4) plus directory inspection surfaced:

| Surface | Location | Scope | Relevance |
| --- | --- | --- | --- |
| F-series static dashboard MVP | `tools/dashboard/**` | data-slice / gates / operator-review over `dashboard_data.v1` contract | adjacent but different contract |
| Lab run registry | `tools/lab_registry/**` | builds a registry of canonical lab runs | feeds `tools/dashboard` operator_review |
| Coordinator state model | `tools/lab_state/**` | read-only per-stage + overall coordinator state snapshots | **the surface this package must visualize** |
| Research query views | `tools/research_query` (`--list-views`) | SQL-style read-only views | unrelated query surface |
| OOS gate / robustness / replay contracts | `tools/oos_gate`, `tools/robustness`, `docs/research/*CONTRACT.md` | upstream evidence contracts | consumed transitively via `tools/lab_state` |

## Why a new `tools/lab_dashboard/` and not folding into `tools/dashboard/`

Package §5 allows `tools/lab_dashboard/**` and also says to prefer the
repo-native location "if the repo already has a dashboard directory/tool ...
after discovery and document why." After inspecting `tools/dashboard`, a new
focused module is the correct, lower-risk choice:

1. **Different data contract.** `tools/dashboard` emits and strictly validates
   `dashboard_data.v1` (`tools/dashboard/validate_dashboard_data.py`). It models
   data slices, gates, and an operator-review page built from
   `tools/lab_registry`. It does **not** consume the new coordinator state model
   (`tools/lab_state`). Bending its frozen contract to carry coordinator-state
   stages would be invasive and risk that validator/contract.
2. **Different subject.** This package's objective is a coordinator-state
   results surface: completed runs, NO-GO / blocked / candidate-ready states,
   OOS gate status, replay status, robustness status, candidate-review reason
   status, and denominator caveats — exactly the `tools/lab_state` vocabulary,
   not the data-slice/gates vocabulary `tools/dashboard` already owns.
3. **Determinism.** `tools/dashboard` output is intentionally non-deterministic
   (`generated_at_utc`, `git rev-parse`/`branch`/`status` subprocess calls). The
   package requires a deterministic static artifact across two runs. The new
   surface is a pure projection of committed artifacts with no clock and no git,
   so two runs are byte-identical.

The new module **reuses** `tools/lab_state` as its single source of state truth
(it never re-derives state) and reads the same committed artifacts the resolver
already consults for display facts (denominator breakdown, Result Population
IDs, withheld statistics). It introduces no new state vocabulary.

## Created location

```
tools/lab_dashboard/__init__.py
tools/lab_dashboard/data_model.py   # deterministic read-only projection
tools/lab_dashboard/render.py       # static HTML + markdown renderers (no controls)
tools/lab_dashboard/run.py          # CLI: emit data JSON / HTML / markdown
tests/test_lab_dashboard.py
```

## Read-only / non-authority confirmation

The surface executes no transition, runs no strategy, resumes no edge-search,
writes no canonical or candidate-lifecycle evidence, fetches no data, and
renders no executable control (no run/approve/promote/retry button, no scheduler
toggle, no auto-refresh). It is a read-only projection of already-committed
repo truth.
