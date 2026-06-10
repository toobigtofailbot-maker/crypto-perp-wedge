# Static Dashboard

The dashboard is a local/offline static operator view with three pages:

- Overview
- Data / Provenance
- Gates

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

## Results data (F5B collector)

When `research/result_populations/RP-4492.result_population.json` is present,
the collector populates the optional `pages.results` section of the generated
`dashboard_data.v1` contract. The Results section includes the result-population
identity, committed denominator, all seven variant rows (ordered by ascending
`variant_id` only), backtest assumptions, descriptive population-level
observations, and non-authority notes.

Results data is collector output only. The current renderer does not display a
Results page; that is F5C. The generated `dashboard_data/dashboard_data.json`
contains valid Results contract data and passes the F5A validator, but
`dashboard_build/index.html` does not yet include a Results page section.

Results data is display-only and non-authoritative. It confers no
ranking, recommendation, readiness, promotion, approval, or execution
authority. `dashboard_data/` and `dashboard_build/` remain gitignored.
