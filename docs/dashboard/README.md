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
