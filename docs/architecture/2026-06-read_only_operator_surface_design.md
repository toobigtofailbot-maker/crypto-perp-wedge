# Read-Only Operator Surface Design

## 1. Package Scope

WP-E2 / Engineering Block 1 designs a read-only operator surface for repo
artifacts and paper-risk status visibility.

This package is design-only. It does not authorize dashboard implementation,
Streamlit code, static-site generation, CLI page generation, runtime
implementation, paper/live code, execution triggers, artifact mutation,
dependency changes, credential use, broker or exchange contact, schema changes,
validator changes, query-layer changes, or downstream authority.

## 2. Repo-Truth Basis

Facts:

- WP-E1 is merged and defines the two-lane sandbox wall.
- `docs/architecture/2026-06-two_lane_sandbox_wall.md` allows later read-only
  dashboard design only when it preserves no execution triggers, no
  dashboard-as-authority, and no ranking, scoring, recommendation, approval,
  readiness, lifecycle, runtime, paper/live, or downstream authority.
- `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md`
  already sketches dashboard visibility as derived presentation only.
- `docs/architecture/LONG_TERM_SCOPE.md` states dashboard visibility must derive
  from repo truth and must not create separate shadow truth outside the repo.
- `research/result_populations/RP-2134.result_population.json` exists as
  fixture-based pipeline evidence only, with explicit no paper/live/runtime,
  ranking, readiness, recommendation, promotion, or transition authority.
- `research/derived_reports/RP-2134.item6_robustness_report.md` exists as a
  derived non-authoritative robustness report and withholds PSR, DSR, and
  MinTRL because required inputs are absent.

Inference:

- A useful operator surface can be designed as a local read-only viewer over
  committed repo files without touching protected runtime or paper/live paths.
- RP-2134 and its derived report are suitable first display examples only
  because they demonstrate lineage, provenance, denominator posture, missing
  robustness inputs, and non-authority declarations.

Decision:

- The recommended MVP is a local/offline read-only viewer over repo artifacts,
  preferably static HTML first or Streamlit only if a later implementation
  package explicitly authorizes dependencies.
- The surface is observational only and cannot rank, select, promote, approve,
  recommend, declare readiness, or trigger execution.

Open question:

- The exact implementation form remains a future E2 implementation decision;
  this document selects the MVP posture, not code.

## 3. Operator Use Cases

Supported operator use cases:

- inspect current repo artifact status and latest branch-state context;
- view candidate/spec/result-population lineage and provenance;
- view committed-denominator and outcome-count posture for result populations;
- view derived robustness-report readiness and missing-input status;
- view non-authority declarations attached to displayed artifacts;
- view paper-risk status boundaries once a later E4 paper-risk surface exists;
- identify discrepancies for human investigation.

Unsupported use cases:

- start, stop, pause, reset, or otherwise control execution;
- mutate artifacts, configs, trial logs, result populations, reports, or paper
  state;
- rank or select strategies;
- recommend or approve candidates;
- declare paper/live readiness;
- change risk, OMS, reconciliation, overlay, safe-mode, kill-switch, or runtime
  behavior;
- contact broker, exchange, order, live API, or credential surfaces.

## 4. Read-Only Data Sources

Allowed initial display sources:

- `docs/project_status.md` for branch-state and package ledger context;
- `docs/architecture/2026-06-two_lane_sandbox_wall.md` for sandbox-wall
  boundaries;
- `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md` for
  existing dashboard discipline;
- `research/result_populations/RP-2134.result_population.json` for lineage,
  provenance, denominator, outcome-count, and non-authority display examples;
- `research/derived_reports/RP-2134.item6_robustness_report.md` for derived
  robustness posture and missing-input display examples.

Future display sources may include separately authorized paper-risk status
artifacts or runtime snapshots only after their source package defines them as
readable, non-authoritative, and safe to expose.

Forbidden data sources:

- live keys or secrets;
- broker, exchange, order, or live API responses;
- protected runtime internals unless a later package explicitly creates a
  read-only exported snapshot;
- mutable local scratch state as authority;
- uncommitted research work as repo-truth display unless visibly labeled local
  and non-authoritative.

## 5. Candidate Implementation Options

### Static HTML

Static HTML is the lowest-authority first implementation option. A future
generator could read committed repo artifacts and emit local static files.

Advantages:

- no server runtime;
- no live credentials;
- easy offline inspection;
- easy artifact provenance display;
- simple to constrain to read-only output.

Tradeoffs:

- refresh requires regeneration;
- interactivity is limited unless JavaScript is later authorized;
- future paper-risk status display needs explicit snapshot inputs.

### Streamlit

Streamlit is suitable only if a later implementation package authorizes the
dependency and constrains it to local read-only file reads.

Advantages:

- faster filtering and tabular exploration;
- useful for artifact lineage and status drill-down;
- simpler local UI iteration than hand-built HTML.

Tradeoffs:

- introduces an application runtime and likely dependency surface;
- must be tightly constrained to avoid controls that look executable;
- must not host network, credential, broker/exchange, or mutation paths.

### CLI-Generated Pages

A CLI-generated page or terminal summary can be acceptable for the narrowest
surface.

Advantages:

- minimal UI surface;
- easy to run locally;
- can produce deterministic output for review.

Tradeoffs:

- less useful for repeated operator scanning;
- easy to confuse with operational CLI commands unless command names and output
  labels are explicit about read-only status;
- does not provide a dashboard-like visual surface.

## 6. Recommended MVP Surface

Recommended MVP: local/offline static read-only viewer.

The MVP should:

- read only committed repo artifacts and separately authorized read-only status
  snapshots;
- display artifact IDs, paths, hashes where present, lineage, provenance,
  denominator posture, outcome counts, and missing-input status;
- label every displayed research output as non-authoritative unless the source
  artifact states otherwise;
- display paper-risk status only as bounded status from a future authorized
  E4/sandbox source, never by querying live services;
- include visible discrepancy labels when display data is missing, stale,
  inconsistent, or below sufficient-evidence floors;
- avoid controls that imply start, stop, reset, promotion, recommendation,
  approval, readiness, ranking, or execution.

The MVP should not introduce dependencies unless the future implementation
package explicitly chooses Streamlit or another app framework.

## 7. Artifact and Provenance Display

The operator surface should display:

- artifact ID and file path;
- schema or artifact family where available;
- parent lineage IDs;
- hashes or identity hashes where available;
- committed denominator and outcome-count posture for result populations;
- data provenance, including fixture or production-data caveats;
- validation status only when sourced from committed or freshly run validation
  output in the active package;
- non-authority declarations;
- missing-input declarations, including withheld PSR, DSR, and MinTRL for
  RP-2134's derived robustness report.

The surface must not compute new scientific conclusions, fill missing metrics,
reinterpret insufficient evidence, or turn display ordering into ranking.

## 8. Paper-Risk Status Display Boundaries

Paper-risk status display is future-dependent. Until a later E4 package creates
a bounded paper-risk status source, E2 can only design placeholder categories.

Allowed placeholder categories:

- selected sandbox strategy reference;
- source artifact path, ID, and hash where available;
- sandbox/mock broker identity;
- sandbox configuration identity;
- paper-risk status timestamp;
- safe-mode or kill-switch placeholder state as reported by a later authorized
  sandbox source;
- explicit no-live-keys and no-real-orders declaration.

Forbidden paper-risk display behavior:

- direct runtime inspection;
- broker/exchange/API calls;
- live key loading;
- open-order or position polling;
- state mutation;
- start/stop/reset controls;
- redefining protected safe-mode or kill-switch semantics;
- presenting paper-risk status as strategy approval or live readiness.

## 9. Non-Authority Declarations

Every future operator surface must declare:

- repo artifacts and protected runtime truth outrank the display;
- dashboard output is presentation only;
- the surface cannot trigger execution;
- the surface cannot mutate artifacts or state;
- the surface cannot rank, score, select, recommend, approve, promote, demote,
  archive, declare readiness, or create lifecycle authority;
- the surface cannot become risk, OMS, reconciliation, overlay, safe-mode,
  kill-switch, paper/live, runtime, policy, or downstream authority.

## 10. Security and Secrets Posture

The operator surface must:

- require no live keys;
- read no `.env` files;
- log no secrets;
- contact no broker, exchange, order, or live API endpoints;
- avoid dependency or network additions unless separately authorized;
- treat local/offline operation as the default;
- display credential absence as expected, not as a failure.

## 11. E4 / Paper-Runtime Relationship

E2 does not implement or authorize E4.

The E2 surface may later consume E4 outputs only if E4 separately defines a
read-only paper-risk status artifact or snapshot. That source must preserve
manual strategy selection, provenance capture, sandbox-only operation, no live
keys, no real orders, no protected runtime mutation, and no canonical artifact
mutation.

The dashboard may display E4 state; it may not drive E4 state.

## 12. Stop Conditions

Stop a future implementation or extension package if it requires:

- dashboard-triggered execution;
- artifact or paper-state mutation;
- live keys, broker contact, exchange contact, order contact, or live API
  contact;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  overlay, event-log, config, dependency, schema, validator, query-layer, data,
  or protected-path changes outside explicit scope;
- Streamlit or other dependency installation without explicit authorization;
- dashboard-as-authority semantics;
- ranking, scoring, recommendation, approval, readiness, promotion, demotion,
  archive, lifecycle, policy, or downstream authority;
- RP-2134 or any result population being treated as strategy-quality evidence
  beyond its committed declarations.

## 13. What Is Not Authorized

WP-E2 does not authorize:

- dashboard implementation;
- Streamlit app code;
- static HTML generator code;
- CLI generator code;
- runtime implementation;
- paper/live implementation;
- broker, exchange, order, or live API contact;
- credentials or secret handling;
- execution triggers;
- artifact mutation;
- paper-state mutation;
- dependency changes;
- schema, validator, query-layer, tool, test, config, data, runtime, or
  protected-path changes;
- ranking, scoring, recommendation, approval, readiness, promotion, demotion,
  lifecycle, policy, or downstream authority.

## 14. Next Surface

After E2 review, E3 may design human-notification-only alert and briefing
channels, or E4 may design sandbox paper-bot scaffolding, only when separately
authorized and only inside the WP-E1 wall.
