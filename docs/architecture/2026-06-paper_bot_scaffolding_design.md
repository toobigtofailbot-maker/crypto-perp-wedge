# Paper-Bot Scaffolding Design

## 1. Package Scope

WP-E4 / Engineering Block 1 designs sandbox-only paper-bot scaffolding inside
the E1 two-lane sandbox wall.

This package is design-only. It does not implement paper-runtime code,
dashboard code, alert code, scheduler or daemon behavior, broker or exchange
adapters, order lifecycle code, OMS or reconciliation behavior, risk caps,
safe-mode implementation, kill-switch implementation, credentials, configs,
schema changes, validator changes, query-layer changes, tool changes, tests,
artifact mutation, result-population mutation, or downstream authority.

Any paper-runtime implementation after E4 requires separate Main/Karl-reviewed
authorization. That authorization must review the sandbox-runtime boundary
before code lands.

## 2. Repo-Truth Basis

Facts:

- WP-E1 is merged and defines the two-lane sandbox wall.
- WP-E2 is merged and designs a read-only operator surface. It cannot trigger
  execution and may display later paper-risk status only from separately
  authorized non-authoritative sources.
- WP-E3 is merged and designs human-notification-only alert and briefing
  channels. Alerts cannot trigger execution or mutate state.
- `docs/phase1_closure_report.md` records the protected Phase 1 paper runtime
  foundation: deterministic scheduling, bounded overlay gating, simulated
  broker, ledger accounting, structured logs, persistence, idempotency, and
  offline-first behavior.
- `docs/onboarding/SYSTEM_MAP.md` records the current paper runtime flow and
  protected module boundaries.
- `docs/research_pipeline/2026-05-phase3_paper_trading_bridge_sketch.md`
  preserves D2-007 shadow mode as the sole bridge from research backtester
  toward the protected Phase 1 paper runtime.
- `research/result_populations/RP-2134.result_population.json` exists as
  fixture-based pipeline evidence only, not strategy-quality evidence from
  production exchange history and not paper/live/runtime authority.
- No current E4 paper-bot implementation surface exists in repo truth.

Inference:

- A useful future paper bot can be scaffolded as a sandbox-only lane-2 design
  without changing protected Phase 1 runtime code.
- The first safe shape is a manually selected, locally simulated paper bot that
  records provenance and paper state separately from canonical research
  artifacts.
- Existing Phase 1 paper runtime concepts can inform naming and safety posture,
  but E4 cannot redefine or modify those protected behaviors.

Decision:

- The recommended future scaffold is a simple sandbox-only paper-bot envelope
  with manual operator approval, explicit provenance, separate sandbox paper
  state, a simulated order/position model, and read-only outputs for E2/E3
  consumers.
- No research artifact, result population, dashboard, alert, digest, query
  view, validation result, score, or report can become automatic authority to
  start, stop, select, rank, approve, promote, resize, or execute a paper run.

Open questions:

- Which exact sandbox state artifact shape should a later implementation use.
- Whether the future sandbox bot should reuse protected Phase 1 runtime modules
  under explicit authorization or remain a separate lane-2 simulator first.
- Which manual approval record is sufficient before a sandbox paper run starts.
- Which later package, if any, should define read-only paper-risk snapshots for
  the E2 operator surface and E3 digest.

## 3. Sandbox-Only Goal

The future paper bot should let a human operator observe how a manually selected
strategy reference behaves in a local, non-authoritative sandbox.

Required posture:

- no live keys;
- no live orders;
- no real broker, exchange, order, or live API contact;
- no real-capital trading;
- no dashboard-triggered execution;
- no alert-triggered execution;
- no research artifact as automatic authority;
- no paper-to-live transition without a separate Karl gate;
- no mutation of canonical research artifacts.

The paper bot is not a promotion gate, readiness gate, ranking engine, research
validator, or live-trading rehearsal. It is an engineering sandbox whose output
may later help humans inspect operational behavior if separately authorized.

## 4. Two-Lane Wall Recap

Lane 1 owns canonical research and evidence artifacts: strategy specs, variant
manifests, sweep plans, result populations, robustness reports, data contracts,
validators, trial discipline, and human-gated decisions.

Lane 2 owns sandbox/paper engineering surfaces: local operator workflows,
sandbox-only state, mock or simulated broker surfaces, read-only visibility,
human-only briefing, and provenance capture.

The E4 scaffold must preserve the wall:

- Lane 2 may read Lane 1 artifacts only as operator-selected inputs.
- Lane 2 must not mutate Lane 1 artifacts.
- Lane 2 state is not canonical research evidence.
- Lane 2 output cannot approve, rank, promote, demote, or declare readiness for
  a strategy.
- Lane 2 cannot create paper/live, runtime, OMS, reconciliation, risk, overlay,
  safe-mode, kill-switch, or downstream authority.

## 5. Future Paper-Bot Components

A later implementation package could consider these components, subject to
separate authorization:

- Operator approval record: captures the human decision to start a sandbox run,
  selected strategy/spec reference, source commit, config identity, and explicit
  no-live-keys/no-real-orders declaration.
- Input reader: reads only committed repo artifacts or separately authorized
  read-only local inputs.
- Signal adapter: translates the selected sandbox strategy reference into a
  sandbox-only target-position intent. It must not modify `SignalProvider`
  protocol behavior unless separately authorized.
- Sandbox clock: advances through operator-selected local time or offline bars.
  It is not a daemon, watcher, scheduler, or live bar-close loop unless a later
  package explicitly authorizes that behavior.
- Simulated order model: creates local simulated order records only. It cannot
  route, place, cancel, amend, or test real orders.
- Simulated position model: records sandbox-only position state and fills
  derived from local simulation assumptions.
- Paper accounting model: records sandbox-only PnL, fees, and slippage
  assumptions without modifying protected paper ledger accounting truth.
- Sandbox state store: writes separate paper-bot state outside canonical
  research artifacts and with provenance attached.
- Audit log: records operator actions, input hashes, state transitions,
  warnings, and boundary declarations without secrets.
- Read-only snapshot exporter: optionally emits a non-authoritative status
  snapshot for a future E2 operator surface or E3 digest.

These component names are design placeholders only. They do not authorize
files, paths, interfaces, schemas, runtime hooks, or implementation.

## 6. Manual Operator Approval Flow

Minimum future flow:

1. Operator reviews the selected strategy/spec reference and source artifacts.
2. Operator reviews sandbox configuration, data source, simulation assumptions,
   and explicit boundary declarations.
3. Operator records an approval action for a sandbox-only run.
4. The paper bot records provenance before any sandbox state transition.
5. The paper bot runs only against authorized local inputs and simulated broker
   behavior.
6. The operator may manually pause, stop, reset sandbox state, or place the
   sandbox into a stop/safe state.
7. Outputs are reviewed as sandbox observations only.

Approval record minimum fields for later design:

- operator action timestamp;
- operator identity or local operator label;
- selected candidate, strategy, or spec reference;
- source artifact path and ID;
- source artifact hash or identity hash when available;
- source commit or branch context;
- sandbox configuration identity;
- local data or fixture identity;
- simulated broker identity;
- declaration that no live keys, real orders, or broker/exchange contact are
  used;
- declaration that the run is non-authoritative.

## 7. Allowed Input Sources

Allowed input sources for a future sandbox package:

- manually selected committed research artifacts;
- committed strategy specs, manifests, sweep plans, result populations, and
  derived reports as read-only references only;
- local offline data files only when separately authorized for the paper-bot
  package;
- operator-provided sandbox configuration after explicit review;
- later E4-defined or post-E4-defined read-only paper-risk snapshots.

Forbidden automatic authority sources:

- RP-2134 or any result population as automatic selection authority;
- robustness reports as automatic approval authority;
- dashboards or static viewers as selection or execution authority;
- alerts, digests, Telegram, email, or reminders as execution authority;
- query views or validators as ranking, readiness, or transition authority;
- advisory agents, scores, or reports as automatic paper-run authority;
- uncommitted local work as repo truth;
- live broker, exchange, order, account, or position responses.

## 8. State and Provenance Recording Concept

Paper-bot state must be separate from canonical research artifacts.

A future state model should record:

- run ID;
- source commit and dirty-state declaration;
- selected strategy/spec reference and hashes;
- operator approval record reference;
- sandbox configuration identity;
- local data identity;
- simulated broker/model assumptions;
- current simulated position;
- simulated order records;
- simulated fills;
- local PnL and accounting assumptions;
- stop/safe-state status;
- warnings and missing-input facts;
- non-authority declaration.

State recording rules:

- do not mutate strategy specs, variant manifests, sweep plans, result
  populations, robustness reports, trial logs, validators, or query surfaces;
- do not write to protected Phase 1 paper state unless a later package
  explicitly authorizes that boundary;
- do not log secrets;
- make reset sandbox-scoped only;
- make stale, missing, or inconsistent source state visible to the operator.

## 9. Paper Position and Order Simulation Concept

The future scaffold may simulate order and position behavior locally, but it
must not imply broker equivalence.

Design limits:

- simulated orders are local records only;
- fills are local deterministic assumptions, not exchange confirmations;
- simulated positions are sandbox state only;
- accounting outputs are sandbox observations only;
- the model cannot place, cancel, amend, test, or reconcile real orders;
- the model cannot poll live open orders, balances, positions, or account
  state;
- the model cannot replace protected OMS, reconciliation, paper ledger, overlay,
  safe-mode, or kill-switch truth.

Any later desire to reuse protected Phase 1 broker, ledger, scheduler, event
log, config, or runtime behavior must trigger separate Main/Karl-reviewed
implementation authorization before code changes.

## 10. Stop and Safe-State Concept

The E4 design may use stop and safe-state language only at the sandbox concept
level.

Future sandbox controls may include:

- start after manual approval;
- pause local simulation;
- stop local simulation;
- reset sandbox state;
- mark sandbox safe state;
- record boundary incident;
- export read-only status.

These controls must not redefine protected runtime safe-mode or kill-switch
semantics. They must not contact live venues, cancel real orders, flatten real
positions, mutate protected runtime state, or change D-0001, D2-008, OMS,
reconciliation, event-log, ledger, config, or overlay behavior.

## 11. Operator Surface Relationship

The E2 operator surface may later display paper-bot status only from a
separately authorized read-only paper-risk snapshot.

Allowed display concepts:

- sandbox run ID;
- selected strategy/spec reference;
- source commit and hashes;
- sandbox state timestamp;
- simulated position and order summary;
- warning and stale-state indicators;
- no-live-keys/no-real-orders declaration;
- non-authority declaration.

Forbidden display behavior:

- start, stop, pause, reset, approve, promote, rank, or select controls;
- mutation of paper-bot state or canonical research artifacts;
- display output treated as strategy approval or live readiness;
- direct runtime, broker, exchange, order, account, or credential inspection.

The dashboard may display E4 state. It may not drive E4 state.

## 12. Alert and Briefing Relationship

The E3 alert/briefing channel may later summarize paper-bot status only from
E4-authorized read-only source facts.

Allowed briefing concepts:

- latest sandbox run summary;
- provenance and selected input reference;
- missing-input or stale-state warnings;
- boundary incident suspicion;
- operator review reminder.

Forbidden briefing behavior:

- alert-triggered execution;
- alert-triggered start, stop, pause, reset, selection, approval, promotion, or
  readiness transition;
- secret handling unless separately authorized;
- broker, exchange, order, live API, OMS, reconciliation, risk, overlay, or
  protected runtime contact.

Notifications are pointers for human review only. Repo/source truth wins if a
briefing disagrees with source state.

## 13. Future Implementation Proof Requirements

Before any implementation package lands, Main/Karl must review and authorize
the sandbox-runtime boundary. A future implementation package would need to
prove at minimum:

- exact allowed files and paths;
- no live keys, real orders, or broker/exchange contact;
- no scheduler, daemon, watcher, or autonomous trigger unless explicitly
  authorized;
- no dashboard-triggered or alert-triggered execution;
- no protected Phase 1 runtime mutation unless explicitly authorized;
- no canonical research artifact mutation;
- separate sandbox paper state and provenance recording;
- deterministic local simulation assumptions;
- fail-closed behavior for missing, stale, or ambiguous inputs;
- tests or validation appropriate to any implemented code;
- read-only status export, if any, cannot mutate state or create authority;
- manual operator approval is required before any sandbox run.

## 14. Stop Conditions Before Implementation

Stop before implementation if the proposed package requires:

- live keys;
- real orders;
- broker, exchange, order, live API, account, balance, open-order, or position
  contact;
- dashboard-triggered execution;
- alert-triggered execution;
- autonomous strategy selection;
- research artifact as automatic authority;
- paper-to-live transition;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  event-log, overlay, config, dependency, schema, validator, query-layer, data,
  or protected-path changes outside explicit scope;
- mutation of canonical research artifacts;
- changing D-0001, D2-006, D2-007, D2-008, SignalProvider, paper ledger
  accounting, OMS truth, reconciliation truth, safe-mode truth, or kill-switch
  truth;
- ranking, recommendation, approval, readiness, transition, promotion,
  demotion, lifecycle, policy, or downstream authority.

## 15. What Is Not Authorized

WP-E4 does not authorize:

- paper-bot implementation;
- paper-runtime code;
- dashboard code;
- alert or digest code;
- scheduler, daemon, watcher, queue, or background process;
- broker, exchange, order, live API, account, balance, open-order, or position
  contact;
- live keys, credentials, secrets, or config changes;
- order lifecycle code;
- OMS or reconciliation implementation;
- risk caps or safe-mode implementation;
- kill-switch implementation;
- protected Phase 1 runtime changes;
- schema, validator, query-layer, tool, test, dependency, data, or config
  changes;
- strategy artifact mutation;
- result-population mutation;
- canonical evidence mutation;
- dashboard, alert, report, validator, query, result population, robustness
  report, or research artifact authority;
- paper-to-live or live transition;
- ranking, scoring, recommendation, approval, readiness, promotion, demotion,
  lifecycle, policy, gate, runtime, paper/live, or downstream authority.

## 16. Report-Back Requirement

Report-back for this package must state:

- worktree path, branch, and base;
- changed files;
- paper-bot scaffolding summary;
- manual approval and authority boundaries;
- implementation gate;
- validation results;
- boundary check;
- post-E4 authorization needs;
- final rebase and GitHub mergeability status;
- PR status.
