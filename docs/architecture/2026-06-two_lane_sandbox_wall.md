# Two-Lane Sandbox Wall Definition

## 1. Package Scope

WP-E1 / Engineering Block 1 defines the hard wall between the canonical
research/evidence lane and the paper-risk/sandbox engineering lane.

This package is design-only. It does not authorize paper-runtime
implementation, dashboard implementation, alert implementation, live keys,
broker or exchange contact, order placement, runtime modification, schema
changes, validator changes, query-layer changes, or downstream authority.

This wall is the required report-back gate before any paper-runtime
implementation package.

## 2. Repo-Truth Basis

Facts:

- PR #391 / WP-S2c-213 is merged.
- PR #392 / WP-D1 is merged before this package branch.
- `docs/project_status.md` records WP-D1 as the latest branch-state before
  this package.
- `research/result_populations/RP-2134.result_population.json` exists as the
  first fixture-based canonical 15m result population. It declares no
  paper/live/runtime authority.
- `research/derived_reports/RP-2134.item6_robustness_report.md` exists as a
  derived non-authoritative robustness report. It withholds rigorous PSR, DSR,
  and MinTRL values because required inputs are absent.
- Existing Phase 3 sketches preserve read-only dashboard discipline,
  paper-bridge non-implementation, and live-trading prohibition.
- Existing architecture docs preserve OMS truth, reconciliation truth,
  safe-mode semantics, kill-switch discipline, event-log discipline, D-0001
  hard risk caps, D2-008 overlay bounds, paper ledger accounting truth, and the
  protected Phase 1 paper runtime baseline.

Inference:

- The current repo contains enough design context to define a sandbox wall
  without modifying protected runtime paths.
- RP-2134 can be referenced only as pipeline evidence and never as strategy
  approval, ranking, readiness, paper/live, runtime, or transition authority.

Decision:

- Lane 2 may move faster only inside a sandbox-only engineering envelope.
- Lane 2 speed does not weaken Lane 1 canonical evidence rules and does not
  create live, paper, dashboard, alert, OMS, reconciliation, risk, or promotion
  authority.

Open question:

- Which later E2, E3, or E4 design package should define the first concrete
  non-authoritative interface shape remains outside WP-E1.

## 3. Lane Definitions

### Lane 1 - Canonical Research / Evidence

Lane 1 owns canonical research truth:

- strategy specs;
- variant manifests;
- sweep plans;
- result populations;
- robustness reports;
- data contracts;
- validators;
- pre-registration;
- committed evidence lineage;
- complete-denominator discipline;
- human-gated decisions.

Lane 1 artifacts may support research, comparison, review, and later
human-gated promotion discussions. They do not execute trades, select paper
runs automatically, mutate paper state, trigger dashboards or alerts, or
authorize runtime behavior.

### Lane 2 - Sandbox / Paper Engineering

Lane 2 is the sandbox-only engineering lane:

- simulated or sandbox-only runtime design;
- read-only dashboard design;
- alert and briefing design;
- operator workflow design;
- paper state design;
- mock or simulated broker design;
- local operator controls;
- audit and provenance capture for sandbox work.

Lane 2 may use engineering shortcuts only where they remain sandbox-only,
observable, reversible, and non-authoritative. Lane 2 does not own canonical
research truth and must not mutate Lane 1 artifacts.

## 4. Hard Wall Rules

Non-negotiables:

- no live keys;
- no live orders;
- no real broker, exchange, order, or live API contact;
- no OMS or reconciliation live authority;
- no paper-to-live transition without Karl/Main gate;
- no research artifact as automatic trading authority;
- no result population, robustness report, dashboard, alert, report, validator,
  score, or query view as authority;
- no dashboard or alert trigger may cause execution;
- manual operator approval is required for any strategy used in paper mode;
- paper-risk/sandbox work must record provenance for selected inputs;
- paper-risk/sandbox work must not promote artifacts;
- paper-risk/sandbox work must not mutate canonical research artifacts.

If a future safe implementation appears to require runtime, paper/live, OMS,
reconciliation, risk, safe mode, kill switch, event-log schema, overlay,
config, dependency, schema, validator, query-layer, data, credential, broker,
exchange, dashboard, alert, or protected-path modification outside its explicit
scope, that package must stop and return to Karl/Main/user for authority.

## 5. Allowed Paper-Risk Speedups

Allowed within later explicitly scoped packages:

- docs-in-PR work for design and operator workflows;
- conditional runways that are visibly blocked on wall review or human gates;
- off-the-shelf tooling for read-only visibility when separately authorized;
- read-only dashboards that cannot trigger execution;
- sandbox-only mock or simulated broker surfaces;
- manual strategy selection by an operator;
- basic alerts that notify humans only;
- basic daily summaries that summarize sandbox state only.

These speedups are future options, not implementation authority in WP-E1.

## 6. Interface Contracts Between Lanes

Safe interface contracts:

- Lane 2 may read Lane 1 research artifacts as inputs only.
- Lane 2 may consume manually selected strategy/spec/signal references only
  after operator action.
- Lane 2 must record provenance for selected references, including artifact
  IDs, hashes where available, branch or commit context, operator action, and
  run timestamp.
- Lane 2 must treat RP-2134 and its robustness report as pipeline evidence
  only, not strategy-quality evidence or paper selection authority.
- Lane 2 must never mutate strategy specs, manifests, sweep plans, result
  populations, robustness reports, validators, query surfaces, trial logs, or
  canonical research artifacts.
- Lane 2 must not promote, demote, rank, score, recommend, approve, or declare
  readiness for any strategy.
- Lane 2 outputs may be reviewed by humans but cannot become promotion,
  runtime, paper/live, risk, OMS, reconciliation, or downstream authority.

Minimum provenance boundary for any later paper-risk run design:

- operator-selected candidate or strategy reference;
- source artifact path and ID;
- source artifact hash or identity hash when present;
- source commit or branch context;
- sandbox configuration identity;
- selected sandbox/mock broker identity;
- explicit declaration that no live keys or real orders are used.

## 7. Operator Controls

Minimum paper controls for later E4 design:

- start;
- stop;
- pause;
- reset paper state;
- safe mode;
- kill-switch placeholder;
- configuration review before run start;
- audit log.

Design constraints:

- Controls must be operator-facing and auditable.
- Controls must not contact live venues in sandbox packages.
- Safe mode and kill-switch placeholders must not redefine protected runtime
  safe-mode or kill-switch semantics.
- Reset must be scoped to sandbox paper state only and must not alter canonical
  research artifacts.
- Audit logs must not contain secrets.

## 8. E2 / E3 / E4 Readiness

### E2 - Read-Only Operator Surface Design

E2 may proceed only as design unless separately authorized otherwise. It must
preserve:

- read-only dashboard/operator posture;
- no execution triggers;
- no dashboard-as-authority;
- repo and runtime truth dominance over presentation;
- no ranking, scoring, recommendation, approval, readiness, or lifecycle
  authority.

### E3 - Alert / Briefing Channel Design

E3 may proceed only as design unless separately authorized otherwise. It must
preserve:

- human-notification-only alerts;
- no alert-triggered execution;
- no autonomous scheduling, queue, daemon, or watcher authority unless later
  explicitly scoped;
- no risk, kill, promotion, readiness, ranking, scoring, or recommendation
  authority.

### E4 - Paper-Bot Scaffolding Design

E4 may proceed only as design unless separately authorized otherwise. It must
preserve:

- sandbox-only or mock/sim broker posture;
- no live keys;
- no real orders;
- no broker/exchange live contact;
- manual strategy selection;
- provenance capture;
- operator controls;
- no mutation of canonical research artifacts;
- no modification of protected runtime, OMS, reconciliation, risk, safe-mode,
  kill-switch, event-log, overlay, config, dependency, schema, validator, or
  query-layer behavior.

## 9. Stop Conditions

Stop if any future E2/E3/E4 or paper-risk package requires:

- live keys;
- real orders;
- broker, exchange, order, live API, or Tier 4 contact;
- dashboard-triggered execution;
- alert-triggered execution;
- research artifacts becoming automatic authority;
- paper implementation before E1 wall review;
- paper-to-live transition authority;
- protected runtime modification without explicit authorization;
- OMS, reconciliation, risk, safe-mode, kill-switch, event-log, overlay,
  schema, validator, query-layer, config, dependency, data, or credential
  changes outside the active package;
- changed files exceeding the allowed scope;
- validation failure that cannot be fixed inside the active package scope.

## 10. What Is Not Authorized

WP-E1 does not authorize:

- paper-runtime implementation;
- dashboard implementation;
- alert implementation;
- broker, exchange, order, live API, or Tier 4 contact;
- live keys or live orders;
- real-capital trading;
- paper-to-live transition;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  event-log, overlay, config, dependency, schema, validator, query-layer, data,
  tool, test, or protected-path changes;
- strategy artifact mutation;
- result-population mutation;
- canonical evidence mutation;
- approval, readiness, recommendation, ranking, scoring, promotion, demotion,
  lifecycle, policy, or downstream authority.

## 11. Report-Back Requirement

This wall must be reviewed before any paper-runtime implementation package.

Report-back must state:

- branch and base;
- changed files;
- sandbox wall summary;
- allowed speedups;
- hard stops;
- E2/E3/E4 readiness;
- validation results;
- boundary check;
- PR status.
