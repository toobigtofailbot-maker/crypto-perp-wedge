# Static Dashboard

The dashboard is a local/offline static operator view with five pages:

- Overview
- Data / Provenance
- Gates
- Operator Review
- Results

Generate it from the repo root:

```powershell
python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .
```

The command writes `dashboard_data/dashboard_data.json`, validates it with
`tools.dashboard.validate_dashboard_data`, then renders `dashboard_build/index.html`
from the validated contract data.

`dashboard_build/` and `dashboard_data/` are generated local outputs and remain
gitignored. The dashboard is display-only: it mirrors validated repo facts,
shows empty states for missing D5, paper runtime, and live mode, and cannot
satisfy gates or mutate artifacts.

The polished static UI keeps the same contract boundary. Search fields on the
Data / Provenance and Gates pages are local browser filters only. They do not
sort by quality, call a server, fetch network resources, write artifacts, or
change any gate state.

## Results page (F5B collector + F5C renderer + lab registry)

When `research/result_populations/RP-4492.result_population.json` is present,
the collector (F5B) populates the optional `pages.results` section of the
generated `dashboard_data.v1` contract. The renderer (F5C) displays that
payload as a Results page in `dashboard_build/index.html`.

The Results page renders from validated `dashboard_data.v1` only. The renderer
does not read RP-4492 or D6 docs directly; all data comes from the collector
output already embedded in the validated contract.

The Results page includes:
- Result population identity (RP-4492)
- Complete population facts (denominator, row count, variant range)
- Descriptive summary (observations and caveats from D6 checkpoint evidence)
- Variant table — seven rows in ascending variant ID order only
- Lab run / result registry — committed Result Populations in run ID order only
- Adopted advisory report links where source data exists
- Backtest assumptions
- Source refs
- Explicit no-authority framing

The Results page is display-only and non-authoritative. It confers no
ranking, recommendation, readiness, promotion, approval, or execution
authority. Rows are displayed in variant ID order only; order is not a
performance ranking. The dashboard does not rank, recommend, approve,
deploy, or execute variants.

`dashboard_data/` and `dashboard_build/` are generated local outputs and
remain gitignored.

The lab registry surface is built from committed Result Populations and adopted
advisory reports only. It is read-only and display-only. It does not rank,
recommend, approve, promote, declare readiness, or create paper/live or
execution authority.

## Operator Review page

The Operator Review page expands the validated dashboard contract without
creating a control surface. It displays:

- active-job availability and committed recent-job records;
- population completeness and explicit successful, failed, invalid, excluded,
  errored, aborted, data-unavailable, and unknown counts;
- candidate review rows with strategy / variant / sweep lineage, caveats, and
  evidence links;
- walk-forward / OOS, robustness, and funding-realism evidence coverage;
- candidate-lifecycle and pending-human-approval posture;
- blockers, missing prerequisites, warnings, and uncertainty.

Current repo truth has no canonical active-job snapshot, no canonical
walk-forward manifest instance, and no real candidate-lifecycle registry
instance. The page therefore shows those states as unavailable or blocked. It
does not infer favorable evidence from absence. Committed job rows use timestamp
and stable-ID ordering, while candidate review rows use stable IDs; neither is a
quality ranking.

Manual approval remains required outside the dashboard. The page has no
executable controls and grants no ranking, recommendation, readiness,
promotion, approval, paper/live, capital, risk, or execution authority.
