# Local Static Dashboard Design

## Purpose

WP-F1 locks the architecture, constraints, and visual design standard for a
future local/offline static dashboard. It does not implement a dashboard,
choose a renderer, add a schema, add a validator, add dependencies, create
templates, create generated output, or authorize paper/live/runtime behavior.

The dashboard goal is operator visibility over repo truth. It is an honest
mirror of committed and separately authorized read-only artifacts, not an
interpretation layer and not a control surface.

## Non-authority posture

Dashboard output is presentation only. Repo artifacts, validation reports,
protected runtime truth, and human-gated decisions outrank dashboard display.

The dashboard may show:

- facts;
- status;
- warnings;
- staleness;
- gates;
- hashes;
- links;
- validation summaries;
- read-only paper state later, if a separate package creates safe snapshots.

The dashboard must not:

- approve, promote, demote, archive, or declare readiness;
- rank as authority or imply strategy quality from ordering;
- recommend execution;
- trigger execution;
- start, stop, pause, reset, select, or resize paper/live runs;
- satisfy gates;
- mutate artifacts, configs, state, data, or logs;
- hide uncertainty, stale state, missing data, or insufficient evidence.

No chart, table, card, badge, sort order, or page position may imply quality
ranking unless a later non-authoritative interpretation design explicitly
authorizes descriptive ordering and labels it as non-authority.

## Why local/offline static-first

The first dashboard should be static and local because that shape minimizes
authority and dependency risk:

- no application server is needed for the MVP;
- no runtime service, daemon, scheduler, watcher, or hosted surface is needed;
- no live credentials or `.env` files are needed;
- no broker, exchange, order, account, position, or live API contact is needed;
- output can be regenerated and inspected from repo artifacts;
- stale or missing input can be displayed explicitly rather than masked by a
  live fetch.

Static-first also matches existing repo posture: E2 permits a read-only
operator surface that cannot trigger execution, E4 states that a dashboard may
display sandbox state but may not drive it, and E5 requires any future
paper-runtime implementation to prove dashboard output cannot trigger
execution.

## Architecture: collector -> dashboard_data contract -> renderer

F1 locks this future structure:

```text
repo artifacts
-> dashboard collector
-> validated dashboard_data JSON
-> static renderer
-> local dashboard build directory
-> open index.html locally
```

Artifact readers are not the dashboard renderer.

The collector reads committed repo artifacts and separately authorized
read-only local snapshots. The collector produces `dashboard_data` JSON only.
After F2 exists, the renderer must consume only F2-contract-valid
`dashboard_data`; it must not re-read repo artifacts directly.

The separation is required because the dashboard must be an honest mirror of
repo truth, not an interpretation layer. Artifact-reading rules, source
normalization, missing-input handling, identity hashes, and validation status
belong in the collector and contract. Layout, navigation, visual hierarchy, and
static assets belong in the renderer.

## Hard constraints

The dashboard must be:

- local/offline first;
- static output;
- read-only;
- non-authoritative;
- no server for MVP;
- no JavaScript build pipeline for MVP;
- no CDN;
- no network fetch at render time;
- no network fetch at view time;
- vendored-assets only;
- openable as a local file;
- reproducible and regenerable from source inputs.

Permanently forbidden unless separately authorized:

- broker, exchange, order, account, balance, position, open-order, or live API
  contact;
- credentials, secrets, `.env` reads, or live keys;
- execution controls;
- dashboard-triggered paper/live action;
- artifact mutation;
- automatic ranking, promotion, readiness, approval, selection, or lifecycle
  transition;
- dashboard-as-authority semantics;
- paper/live gate satisfaction.

## Renderer decision posture

F1 locks constraints, not a renderer tool. F3 must choose and prove a renderer
that satisfies the F1 constraints after F2 reports back the `dashboard_data`
contract.

Allowed renderer/dependency classes for MVP:

- Python static generation;
- templating such as Jinja2 if already acceptable under repo dependency policy
  or explicitly added in F3;
- vendored CSS;
- optional vanilla JavaScript for local search, sort, tabs, or disclosure
  controls.

Deferred until justified:

- charting libraries such as Plotly or Lightweight Charts;
- Panel or StaticDash if a plain static renderer cannot meet requirements.

Forbidden for MVP:

- Streamlit, Dash, or another server app;
- React, Vite, or another JavaScript build pipeline;
- CDN dependencies;
- runtime service;
- hosted server;
- authentication layer;
- live data feed.

## MVP page scope

The MVP is three real-data pages only:

- Overview;
- Data / Provenance;
- Gates.

Reason: D5 does not exist yet, and paper runtime does not exist yet. The MVP
should render pages with real available data and explicit empty states instead
of many thin or empty pages.

## Overview page

The Overview page is the daily operator view. It should show:

- system posture: research-only, paper disabled, live disabled;
- latest data slice status if available;
- latest validation status if available;
- open gates and blockers;
- staleness and warnings;
- links to relevant status fragments and repo artifacts.

The Overview should use four to six critical cards. Cards should be factual
and status-oriented, not promotional. Missing data must be visible as an empty
state or warning instead of omitted.

## Data / Provenance page

The Data / Provenance page reads available D4A, D3, and D2 artifacts when
present. It should display:

- D4 catalog ref;
- D4 slice identity;
- D3 validation report identity;
- row count;
- timestamp range;
- gap facts;
- duplicate facts;
- raw hash;
- normalized hash;
- D3 PASS / D4 PASS status.

The page must distinguish committed artifact identity from local regenerated
output. It must not silently promote gitignored local data into repo truth.

## Gates page

The Gates page shows:

- current hard gates;
- stop conditions;
- required Main/Karl report-backs;
- known blockers;
- next manual review required.

Dashboard displays gates; dashboard does not satisfy gates.

The page must avoid approve, promote, ready, launch, start, stop, pause, reset,
or execution-like controls. It should link to source gate artifacts or status
fragments where useful.

## Future page expansion

Target pages after data exists:

- Results page after D5;
- Validation / integrity detail page after F3/F4 or when useful;
- Strategy / sweep inventory page after MVP;
- Audit page after MVP if not already covered;
- Paper page after paper runtime and paper-state snapshots exist.

F5 Results page waits for D5. F6 Paper page waits for paper runtime plus
paper-state snapshots.

Future pages remain display-only and must preserve the non-authority posture.

## Dashboard information model

The future `dashboard_data` contract should separate at least these concepts:

- build metadata: source commit, generation timestamp, dirty-state declaration,
  contract version, collector version, and renderer-compatible version;
- system posture: research-only, paper disabled/enabled status from authorized
  source facts, live disabled status, and protected-boundary declarations;
- artifact links: repo-relative paths, artifact IDs, artifact families, source
  hashes, and status-fragment links;
- data provenance: D2/D3/D4 identities, row counts, timestamp ranges, gaps,
  duplicates, raw hashes, normalized hashes, and validation statuses;
- gates and blockers: gate ID, gate label, source path, status, required human
  owner when known, and stop condition text;
- staleness: source timestamp, generated timestamp, age classification, and
  stale/missing reason;
- empty states: expected-but-missing source, reason, and next manual action;
- warnings: severity, source path, and evidence link.

F1 does not define exact field names. F2 owns the dashboard_data schema,
validator, fixtures, and exact contract.

## Visual design standard

The dashboard must look like a restrained operational surface, not a raw HTML
dump and not a marketing page.

Required visual traits:

- dark-first;
- left sidebar navigation;
- sticky top status bar;
- card-based Overview with four to six critical cards;
- semantic badges: PASS / WARN / FAIL / BLOCKED;
- semantic colors reserved for status and warnings only;
- neutral background;
- subtle borders and shadows;
- generous whitespace;
- compact tables;
- monospace only for hashes and IDs;
- responsive single-column collapse;
- explicit empty states;
- useful links to repo artifacts and status fragments.

Forbidden visual and UX patterns:

- execution buttons;
- approve, promote, launch, start, stop, pause, or reset buttons;
- traffic-light simplification that hides uncertainty;
- ranking as quality;
- best-variant language;
- silent omission of stale or missing data;
- raw log dump as the primary UI.

Status labels must make uncertainty visible. PASS means source validation says
PASS. WARN means source facts require operator attention. FAIL means source
validation or integrity facts failed. BLOCKED means a gate, missing input, or
stop condition prevents continuation.

## Dependency policy

Allowed for MVP:

- standard-library Python static generation;
- a Python templating dependency only if F3 explicitly authorizes it or it is
  already acceptable under repo dependency policy;
- vendored CSS committed with the renderer implementation package;
- optional local vanilla JavaScript committed with the renderer implementation
  package for search, sort, tabs, or disclosure controls.

Deferred:

- charting libraries;
- richer static dashboard frameworks;
- app-like local server frameworks.

Forbidden for MVP:

- CDN dependency;
- JS build pipeline;
- hosted service;
- live data feed;
- authentication system;
- secrets or credential handling.

F1 creates no dependency change.

## Generated output policy

Generated dashboard output should be local and regenerable:

- `dashboard_build/` is generated and should be gitignored;
- `dashboard_data/` is generated and should be gitignored;
- full dashboard output should not be committed by default;
- production-scale data or local dashboard outputs should not be committed;
- only tiny test fixtures under `tests/fixtures/` should be committed when
  needed by F2/F3.

Current repo truth: `.gitignore` does not yet cover `dashboard_build/` or
`dashboard_data/`. F1 does not edit `.gitignore`; F2/F3 should add the ignore
rules when code or output paths are introduced.

## Dashboard namespace policy

F1 proposes these future namespaces without creating implementation
directories:

```text
tools/dashboard/
docs/dashboard/
dashboard_build/
dashboard_data/
tests/fixtures/dashboard/
```

`tools/dashboard/` should contain future collector/renderer code only when an
implementation package authorizes it. `docs/dashboard/` may contain user-facing
dashboard documentation after implementation. `dashboard_build/` and
`dashboard_data/` are generated local output. `tests/fixtures/dashboard/` may
hold tiny committed fixtures for schema and renderer tests.

## Read-only artifact sources

Allowed read-only source classes for MVP:

- `docs/project_status.md` and `docs/status_entries/*.md` for repo status and
  package fragments;
- D2 import/provenance reports when present;
- D3 validation reports when present;
- D4 catalog/slice artifacts when present;
- committed gate, architecture, or proof-bar documents;
- separately authorized read-only status snapshots if a later package creates
  them.

Forbidden source classes:

- secrets and `.env` files;
- broker/exchange/order/live API responses;
- live account, balance, position, or open-order state;
- mutable local scratch state as authority;
- uncommitted files as repo truth unless visibly labeled local and
  non-authoritative;
- protected runtime internals unless a later package creates an authorized
  read-only snapshot.

## Freshness/staleness posture

The dashboard must show when facts were generated and what source timestamp or
artifact identity supports them.

Required handling:

- display source timestamp where present;
- display dashboard generation timestamp;
- display source commit and dirty-state declaration when available;
- label missing freshness metadata as unknown;
- label stale or possibly stale inputs as WARN or BLOCKED according to the
  future contract;
- never refresh through network fetch at render or view time.

Freshness display is informational. It does not satisfy any gate and does not
authorize paper/live action.

## Empty-state posture

Empty states are first-class dashboard content.

Expected MVP empty states include:

- D5 unavailable, so Results page is not part of MVP;
- paper runtime unavailable, so Paper page is not part of MVP;
- paper-state snapshots unavailable unless a later package creates them;
- validation report absent or stale;
- data catalog slice absent;
- gate source absent or not yet promoted to dashboard input.

The dashboard should state what is missing, why that absence is expected or
blocking, and where the operator should inspect repo truth next. It must not
hide a missing source by dropping the card, row, or page.

## Start-before-D5 posture

The dashboard may start before D5 because the MVP is scoped to pages that can
display real current data:

- Overview;
- Data / Provenance;
- Gates.

The MVP must not fabricate Results content before D5. The Results page waits
for D5 and should be added in F5 only after D5 exists. Paper views wait for
paper runtime and read-only paper-state snapshots and should be added in F6
only after those sources exist.

## WP sequence and gates

Locked sequence:

```text
F1 - architecture + constraints + design standard [T1]
F2 - dashboard_data schema + validator + tests [T3; report-back before F3]
F3 - static dashboard MVP generator, 3 pages [T3]
F4 - polished UI pass [T3]
F5 - Results page after D5 [T3; gated]
F6 - Paper page after paper runtime + snapshots [T3; gated]
```

F2 must surface the dashboard_data contract before F3 renderer implementation.
F3 must prove the chosen renderer satisfies F1 constraints. F4 may polish the
UI but must not add new authority. F5 waits for D5. F6 waits for paper runtime
and paper-state snapshots.

## Stop conditions

Stop a future dashboard package if safe implementation requires:

- implementation during a docs/design-only package;
- schema, validator, or test changes outside explicit authorization;
- dependency decision beyond the allowed package scope;
- named renderer lock before F3;
- dashboard-as-authority wording;
- execution, promotion, readiness, approval, selection, ranking, or policy
  controls;
- source artifact mutation;
- credential, secret, broker, exchange, order, live API, account, position, or
  open-order contact;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  overlay, config, schema, validator, query-layer, dependency, data, or
  protected-path changes outside explicit scope;
- `docs/project_status.md` rewrite to complete a parallel package;
- validation failure that cannot be fixed inside authorized scope.

## What to avoid

Avoid:

- building a dashboard before F2 defines and validates `dashboard_data`;
- letting renderer code read repo artifacts directly after F2 exists;
- making the dashboard a separate truth source;
- using live refreshes to hide missing committed artifacts;
- adding a server, app framework, or JS build pipeline to the MVP;
- committing generated dashboard output by default;
- turning gate display into gate satisfaction;
- using rank, best, ready, approve, promote, launch, or execute language;
- creating broad pages with thin or fabricated content.
