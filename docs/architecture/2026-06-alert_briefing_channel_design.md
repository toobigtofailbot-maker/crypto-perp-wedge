# Alert / Briefing Channel Design

## 1. Package Scope

WP-E3 / Engineering Block 1 designs human-notification-only alert and briefing
channels for repo and paper-risk status.

This package is design-only. It does not implement alert code, scheduler code,
daemon code, Telegram or email integrations, credentials, secrets, dashboard
code, paper/runtime/live code, broker or exchange contact, schema changes,
validator changes, query-layer changes, artifact mutation, dependencies, or
execution triggers.

## 2. Repo-Truth Basis

Facts:

- WP-E1 is merged and defines the two-lane sandbox wall.
- The sandbox wall permits later alert and briefing design only when alerts
  notify humans and do not trigger execution.
- `RP-2134` exists as fixture-based pipeline evidence with no paper/live/runtime
  authority.
- `RP-2134.item6_robustness_report.md` exists as a derived non-authoritative
  report and withholds PSR, DSR, and MinTRL values because required inputs are
  absent.
- No existing alert or briefing implementation is present in the current
  architecture docs.

Inference:

- The repo can define alert/briefing channel boundaries without touching
  runtime, paper/live, broker/exchange, dashboard, schema, validator, or
  query-layer paths.
- Any first implementation should favor local, operator-initiated digest
  generation before networked notification channels.

Decision:

- The MVP channel should be a local/offline, human-readable daily digest design.
- Telegram and email should remain later optional channels until an explicit
  secret-handling and delivery-failure design is authorized.
- No daemon, autonomous watcher, alert-triggered queue, or scheduler authority is
  created here.

Open questions:

- Which exact paper-risk status fields E4 will expose for a future digest.
- Whether E2 will define a read-only operator surface before any digest
  implementation.
- Whether Telegram or email is worth adding after local digest behavior is
  proven useful.

## 3. Goals

Alert and briefing channels should help a human operator notice repo and
paper-risk state without creating any trading authority.

Goals:

- summarize sandbox-only paper-risk status for operator review;
- surface validation, provenance, and boundary warnings in plain text;
- distinguish normal daily briefing, warning, and incident messages;
- preserve repo truth over notification text;
- keep secrets out of the repository;
- avoid alert noise that trains operators to ignore messages;
- fail closed when required source state is missing or ambiguous.

Non-goals:

- executing trades;
- placing, canceling, or modifying orders;
- starting or stopping paper or live systems;
- selecting, ranking, approving, or promoting strategies;
- mutating research artifacts, result populations, robustness reports, paper
  state, configs, logs, or runtime state;
- contacting broker, exchange, order, OMS, reconciliation, risk, overlay, or
  protected runtime paths.

## 4. Candidate Channels

### Local / Offline Digest

Description:

- Operator runs a local command in a later implementation package.
- Output is a human-readable text or Markdown digest.
- The digest reads only authorized repo or sandbox status inputs.
- The digest does not send network traffic.

Use fit:

- best first MVP because it avoids credentials, network delivery, daemon
  behavior, and autonomous notification infrastructure;
- easy to review in PRs and local logs;
- compatible with E1 sandbox wall and E4 paper scaffolding design.

Boundary:

- a local digest cannot become strategy approval, ranking, readiness, promotion,
  paper/live, runtime, OMS, reconciliation, or risk authority.

### Scheduled Summary

Description:

- A later package may design or implement operator-controlled scheduling for a
  local digest.
- Scheduling must be explicitly authorized before implementation.

Use fit:

- useful after the digest content is stable;
- not required for MVP.

Boundary:

- a schedule may generate a notification only; it cannot trigger execution,
  paper actions, live actions, artifact mutation, or state transitions.

### Telegram

Description:

- A later package may send the digest or incident text to a Telegram chat.

Use fit:

- useful for mobile visibility once the message model is stable.

Boundary:

- bot tokens, chat IDs, and routing secrets must be runtime-local or secret-store
  backed and never committed;
- Telegram delivery failure cannot cause trading actions or state mutation;
- Telegram commands must not be accepted as execution controls unless a future
  package explicitly designs a separate non-trading operator-control surface.

### Email

Description:

- A later package may send digest or incident text by email.

Use fit:

- useful for slower daily summaries, audit-style review, and broad operator
  visibility.

Boundary:

- SMTP/API credentials, recipients, and routing secrets must not be committed;
- email delivery failure cannot cause trading actions or state mutation;
- email replies must not be parsed as commands.

## 5. Recommended MVP

The recommended MVP is a local/offline daily digest only.

Required posture:

- manually invoked by an operator;
- human-readable text or Markdown output;
- no network delivery;
- no daemon, watcher, queue, scheduler, or background process;
- no credentials or secrets;
- read-only inputs only;
- no mutation of research artifacts, paper state, configs, logs, or runtime
  state unless a later package explicitly scopes a local output file;
- explicit non-authority banner in the generated content.

Minimum future digest sections:

- source repo/commit context;
- selected sandbox or paper-risk context, if E4 later defines one;
- latest validation or health facts that are authorized as read-only inputs;
- provenance of manually selected strategy/spec references, if any;
- warnings for missing inputs or stale local state;
- boundary statement: notification only, no execution authority.

## 6. Message Types

Daily summary:

- low-urgency operator briefing;
- includes status, provenance, missing-input warnings, and next manual review
  items;
- should be compact enough to scan.

Warning:

- human attention requested for stale state, validation failure, missing
  provenance, unavailable input, failed digest generation, or sandbox status
  inconsistency;
- cannot execute a fix and cannot mutate state.

Incident notification:

- human attention requested for severe sandbox-only issues such as paper-risk
  process failure, impossible provenance, or boundary violation suspicion;
- must direct the operator to inspect repo truth and logs;
- cannot place orders, cancel orders, flatten positions, invoke a kill switch,
  or contact broker/exchange paths.

Review reminder:

- a non-urgent reminder to inspect a report, digest, or status file;
- cannot promote, rank, or select strategy candidates.

## 7. Manual Review Posture

Alerts and briefings are prompts for human review only.

The operator must treat alert text as a pointer to repo or sandbox truth, not as
truth itself. If a notification disagrees with repo artifacts, committed
evidence, local sandbox logs, or E4-defined paper state, the underlying source
state wins until the discrepancy is investigated.

Any human action after an alert must occur through separately authorized
operator workflows. Alert delivery itself cannot be the action.

## 8. Secrets Handling

Hard policy:

- no committed tokens, API keys, chat IDs, SMTP credentials, routing secrets, or
  recipient lists;
- no secrets in examples that look real;
- no secrets in generated digest output or logs;
- no dependency on live broker/exchange credentials;
- missing notification secrets must fail closed with a human-readable local
  error in any later implementation.

Later Telegram or email implementation must define:

- local environment variable names or external secret-store references;
- redaction rules for logs and errors;
- dry-run behavior that proves message rendering without delivery;
- delivery test posture that does not contact broker/exchange/order paths;
- operator-owned rotation procedure outside the repository.

## 9. Rate / Noise Policy

Default policy:

- daily summary: at most once per operator-invoked run or authorized schedule;
- warnings: aggregate repeated warnings into one section where practical;
- incidents: emit one concise incident message per detected incident class;
- repeated identical failures should include first-seen and latest-seen context
  when available, not repeated message spam.

Noise controls:

- distinguish missing data, stale data, validation failure, and boundary
  violation suspicion;
- avoid strategy-performance language that implies ranking, approval, readiness,
  or recommendation;
- avoid urgency labels unless operator action is actually required.

## 10. Failure / Incident Design

Notification failures:

- record or print a local human-readable failure only in a later authorized
  implementation;
- do not retry indefinitely;
- do not trigger execution, state mutation, broker/exchange contact, or
  artifact changes;
- do not hide source validation failures behind delivery failures.

Source-state failures:

- missing required inputs should produce a warning or fail-closed digest;
- stale local state should be named explicitly;
- validation failures should be summarized only as facts and should point to
  source validation output where available.

Boundary incidents:

- suspected alert-triggered execution, secret leakage, broker/exchange contact,
  artifact mutation, or authority-bearing wording is a stop condition for the
  relevant future package.

## 11. Relationship To E2

E2 is expected to define a read-only operator surface if separately authorized.

E3 should align with E2 by treating notifications as summaries of the same
read-only source facts, not as a parallel source of truth. If E2 and a digest
disagree, repo/source truth wins. E3 does not require E2 to exist before the
local digest design is valid, but a future implementation should reuse E2 source
definitions if E2 lands first.

## 12. Relationship To E4

E4 is expected to design paper-bot scaffolding if separately authorized.

E3 should align with E4 by summarizing only E4-authorized sandbox or paper-risk
state. E3 does not define paper state, paper controls, broker mocks, strategy
selection, or provenance fields. E4 remains design-only unless separately
authorized, and E3 cannot convert E4 outputs into trading, ranking, readiness,
promotion, paper/live, or runtime authority.

## 13. Hard Rules

Alerts and briefings:

- cannot trigger execution;
- cannot mutate artifacts;
- cannot mutate paper, runtime, config, or live state;
- cannot rank, select, approve, recommend, promote, demote, or declare readiness
  for strategies;
- cannot become paper/live authority;
- cannot become runtime, OMS, reconciliation, risk, safe-mode, kill-switch, or
  overlay authority;
- cannot require committed secrets;
- cannot contact broker, exchange, order, live API, OMS, reconciliation, risk,
  overlay, or protected runtime paths;
- cannot override repo truth or committed source artifacts.

## 14. Stop Conditions

Stop any future alert/briefing package if it requires:

- alert implementation outside explicit scope;
- scheduler, daemon, watcher, queue, or autonomous trigger without explicit
  authorization;
- credentials or secrets committed to the repository;
- broker, exchange, order, live API, OMS, reconciliation, risk, overlay, or
  protected runtime contact;
- paper/live/runtime code changes outside explicit scope;
- schema, validator, query-layer, dependency, dashboard, or artifact mutation
  outside explicit scope;
- notification text that implies approval, readiness, recommendation, ranking,
  promotion, transition, policy, gate, paper/live, runtime, or downstream
  authority;
- any alert-triggered execution or state mutation.

## 15. What Is Not Authorized

WP-E3 does not authorize:

- alert code;
- digest generator code;
- Telegram integration;
- email integration;
- scheduler, daemon, watcher, queue, or background process;
- credentials, secrets, or config;
- dashboard implementation;
- paper-bot implementation;
- broker, exchange, order, or live API contact;
- runtime, paper/live, OMS, reconciliation, risk, safe-mode, kill-switch,
  event-log, overlay, config, dependency, schema, validator, query-layer, data,
  tool, test, or protected-path changes;
- research artifact mutation;
- result-population mutation;
- approval, readiness, recommendation, ranking, scoring, promotion, demotion,
  lifecycle, policy, gate, transition, or downstream authority.

## 16. Report-Back Requirement

Report-back for this package must state:

- worktree path, branch, and base;
- changed files;
- alert/briefing design summary;
- recommended MVP;
- boundaries;
- validation results;
- PR status.
