# Paper-Runtime Implementation Proof Bar

## Purpose

WP-E5 defines the minimum proof bar for any future paper-runtime
implementation package after E4.

This document is a checklist for review before runtime code lands. It does not
authorize paper-runtime implementation, dashboard implementation, alert
implementation, schedulers, daemons, credentials, broker or exchange contact,
order lifecycle code, protected runtime changes, canonical artifact mutation,
or paper/live authority.

## Relationship to E1/E2/E3/E4

Facts:

- E1 defines the two-lane sandbox wall between canonical research/evidence and
  sandbox/paper engineering.
- E2 designs a read-only operator surface that may display later authorized
  sandbox state but cannot trigger execution or mutate state.
- E3 designs human-notification-only alert and briefing channels that cannot
  trigger execution or mutate state.
- E4 designs sandbox-only paper-bot scaffolding and states that any
  paper-runtime implementation requires separate Main/Karl-reviewed
  authorization of the sandbox-runtime boundary before code lands.

Decision:

- A future implementation package is reviewable only if it proves the boundary
  items in this checklist before implementation is accepted.

## Non-authority posture

Required future posture:

- paper runtime output does not rank, score, promote, approve, or recommend
  strategies;
- paper PnL does not imply live readiness;
- paper runs do not authorize live transition;
- paper-to-live remains separately Karl-gated;
- research artifacts are inputs only after manual operator selection;
- dashboards, alerts, reports, validators, query views, result populations, and
  robustness reports remain non-authoritative for execution.

## Required preconditions before implementation

A future implementation package must state and prove:

- explicit Main/Karl authorization for paper-runtime implementation;
- exact allowed files and paths;
- exact state output paths for paper-runtime state, events, simulated orders,
  simulated fills, and provenance records;
- no required change to protected Phase 1 runtime paths unless explicitly
  authorized in that package;
- no required change to OMS, reconciliation, risk caps, safe mode,
  kill-switch semantics, event-log schema, overlay semantics, live configs,
  schemas, validators, query-layer behavior, dependencies, or data artifacts
  unless explicitly authorized;
- no required broker, exchange, order, live API, account, balance, position, or
  open-order contact;
- no required credentials, secrets, or live keys;
- manual operator approval is part of the run start path;
- missing, stale, ambiguous, or unauthorized inputs fail closed.

## Sandbox boundary proof

The future implementation package must prove:

- paper runtime is sandbox-only;
- no live keys are read, required, accepted, or logged;
- no real orders can be placed, amended, canceled, tested, or reconciled;
- no broker, exchange, order, live API, account, balance, position, or
  open-order endpoint can be contacted;
- no paper-to-live transition path exists;
- paper state is separate from canonical research artifacts;
- simulated broker, order, fill, position, and accounting behavior is labeled
  as local simulation only;
- runtime behavior cannot escape into protected Phase 1 runtime or live paths
  outside explicit package authorization.

## No-live-contact proof

Review evidence must include:

- changed-file list showing no credential, live config, broker adapter, exchange
  adapter, order lifecycle, OMS, reconciliation, risk, safe-mode, kill-switch,
  or live-trading path changes outside explicit scope;
- tests or static checks proving live-contact modules are not imported by the
  sandbox paper-runtime path, where code is introduced;
- operator documentation stating that missing live credentials are expected and
  not an error;
- failure behavior showing that any attempted live-contact configuration is
  rejected before run start.

## Manual approval gate proof

The future implementation package must prove:

- an operator manually selects and approves the strategy/spec/config before a
  paper run starts;
- the approval record is written or referenced before state transition;
- research artifacts are inputs, not automatic authority;
- result populations cannot automatically promote into paper runs;
- dashboard output cannot trigger execution;
- alerts or briefings cannot trigger execution;
- query views, validators, reports, scores, or advisory outputs cannot select,
  approve, start, resize, stop, or promote a run.

Minimum approval record content:

- operator label or identity convention;
- approval timestamp;
- selected strategy/spec/config reference;
- source artifact paths and IDs;
- hashes or identity hashes where repo convention supports them;
- source commit or branch context;
- explicit no-live-keys/no-real-orders/no-broker-contact declaration;
- explicit non-authority declaration.

## Required operator controls

The future implementation package must define operator controls before code is
accepted.

Minimum required controls:

- review selected strategy/spec/config before run start;
- approve run start manually;
- start only after approval;
- stop the paper runtime;
- view stop state and stop reason;
- review paper-run provenance;
- inspect sandbox state without mutating canonical artifacts.

Required control boundaries:

- controls are local, explicit, and auditable;
- controls cannot contact broker, exchange, order, live API, account, balance,
  position, or open-order paths;
- controls cannot load or require live credentials;
- controls cannot mutate canonical research artifacts;
- controls cannot become ranking, recommendation, approval, readiness,
  promotion, transition, paper/live, or downstream authority;
- controls cannot redefine protected Phase 1 safe-mode or kill-switch
  semantics.

## Kill-switch / stop-control proof

This section is proof-bar only. WP-E5 does not implement stop or kill-switch
code.

A future implementation package must prove:

- the operator can stop the paper runtime;
- stop command or stop state is explicit and auditable;
- the paper loop halts safely after stop;
- paper order simulation stops accepting new actions after stop;
- simulated fills or state transitions after stop are either rejected or
  explicitly limited to safe shutdown bookkeeping;
- run state records stop timestamp and stop reason;
- stop controls do not redefine protected Phase 1 safe-mode or kill-switch
  semantics;
- stop controls do not contact live venues, cancel real orders, flatten real
  positions, or mutate protected runtime state.

## Paper state and provenance proof

Future paper-runtime state must record:

- paper run ID;
- selected strategy/spec/config reference;
- operator approval record;
- start timestamp;
- stop timestamp when applicable;
- stop reason when applicable;
- input artifact references;
- data slice or catalog references if relevant;
- source commit or branch context;
- dirty-state declaration if relevant;
- paper state hash or identity where repo convention supports it;
- simulated event, order, fill, position, and accounting provenance;
- sandbox broker or simulation model identity;
- no-authority declaration.

## Canonical artifact immutability proof

The future implementation package must prove that paper runtime does not mutate:

- strategy specs;
- variant manifests;
- sweep plans;
- result populations;
- robustness reports;
- trial logs;
- data catalog artifacts;
- data slice artifacts;
- schemas;
- validators;
- query-layer surfaces.

Paper runtime may write only to future authorized paper-state paths defined by
the implementation package.

## Read-only operator-surface relationship

The E2 operator surface may display paper-runtime state only from a separately
authorized read-only snapshot or state source.

Required proof:

- dashboard/operator surface cannot start, stop, pause, reset, approve, select,
  promote, rank, or execute;
- dashboard/operator surface cannot mutate paper state or canonical artifacts;
- dashboard/operator display is presentation only;
- repo/source state outranks display text.

## Alert/briefing relationship

The E3 alert and briefing channels may summarize paper-runtime state only from
authorized read-only source facts.

Required proof:

- alerts cannot start, stop, pause, reset, approve, select, promote, rank, or
  execute;
- notification delivery failure cannot mutate paper state or trigger recovery
  actions;
- notification text cannot imply ranking, readiness, recommendation, promotion,
  transition, policy, or execution authority;
- alert outputs remain prompts for human review only.

## Validation and test requirements

A future implementation package must define validation appropriate to its code
surface. Minimum expected proof includes:

- focused unit tests for approval-gate enforcement;
- focused unit tests for no-live-contact rejection;
- focused unit tests for stop-control behavior;
- focused unit tests for provenance/state recording;
- tests proving canonical artifacts are not mutated;
- tests proving dashboard and alert surfaces, if present, cannot trigger
  execution;
- registry/query/integrity validation if the package explicitly adds authorized
  artifact families or read-only views;
- `git diff --check`;
- `tools/dev/diff_scope_summary.py`;
- full pytest unless the future package's explicit validation profile and repo
  guidance define a narrower accepted profile.

Validation evidence must report command, result, and any integrity-view count.
Validation failure is a stop condition unless the failure is environment-only
and the active package explicitly permits reporting it that way.

## Implementation package allowed/forbidden scope template

Future authorization required. The following is a template, not authority.

Likely allowed scope for a first paper-runtime implementation package:

- paper runtime state model;
- manual approval file, CLI, or local input mechanism;
- simulated order state;
- simulated position state;
- simulated fill state;
- paper event log;
- stop control;
- paper-run provenance record;
- read-only paper-state snapshot, if explicitly scoped;
- focused tests and validation.

Likely forbidden scope for that package:

- live keys;
- real broker or exchange contact;
- real orders;
- live API contact;
- OMS/live reconciliation;
- live risk caps;
- protected safe-mode or kill-switch semantic changes;
- protected Phase 1 runtime mutation unless explicitly authorized;
- paper-to-live transition;
- canonical artifact mutation;
- automatic strategy promotion;
- dashboard execution triggers;
- alert execution triggers;
- credential or secret changes.

## Stop conditions

Stop the future package if implementation requires:

- live keys, credentials, or secrets;
- real orders;
- broker, exchange, order, live API, account, balance, position, or open-order
  contact;
- paper-to-live transition;
- dashboard-triggered execution;
- alert-triggered execution;
- autonomous strategy selection;
- research artifacts becoming automatic authority;
- mutation of strategy specs, variant manifests, sweep plans, result
  populations, robustness reports, trial logs, data catalog artifacts, or data
  slice artifacts;
- protected runtime, OMS, reconciliation, risk, safe-mode, kill-switch,
  event-log, overlay, config, schema, validator, query-layer, dependency, tool,
  test, or data changes outside explicit scope;
- safe implementation that needs a boundary decision not present in repo truth
  or the active package;
- validation failure that cannot be fixed inside the authorized scope.

## Minimum acceptance checklist

Before first paper-runtime implementation is accepted, reviewers must be able to
check all items:

- [ ] Explicit implementation authorization exists.
- [ ] Changed files match the authorized package.
- [ ] Sandbox-only boundary is enforced.
- [ ] No live keys are required, read, accepted, or logged.
- [ ] No real orders can be placed, amended, canceled, tested, or reconciled.
- [ ] No broker/exchange/order/live API contact exists.
- [ ] No paper-to-live path exists.
- [ ] Manual operator approval is required before run start.
- [ ] Dashboard output cannot trigger execution.
- [ ] Alerts or briefings cannot trigger execution.
- [ ] Stop control is explicit, auditable, and halts the paper loop safely.
- [ ] Simulated order handling stops accepting new actions after stop.
- [ ] Run state records stop reason.
- [ ] Provenance records selected strategy/spec/config, approval, timestamps,
  inputs, data refs where relevant, run ID, and simulated event/order/fill
  lineage.
- [ ] Paper state is separate from canonical research artifacts.
- [ ] Canonical research artifacts are not mutated.
- [ ] Paper output carries no ranking, recommendation, readiness, promotion,
  transition, paper/live, or downstream authority.
- [ ] Validation and tests passed for the implemented surface.
- [ ] Final rebase and GitHub mergeability gate passed.

## Report-back requirements

Any future implementation report-back must include:

- branch, worktree, and base;
- authorization source;
- changed files;
- sandbox/no-live-contact proof;
- manual approval proof;
- kill-switch or stop-control proof;
- provenance and state-separation proof;
- canonical immutability proof;
- read-only operator-surface and alert/briefing boundary proof;
- validation results;
- forbidden-scope check;
- final rebase and GitHub mergeability status;
- PR status.
