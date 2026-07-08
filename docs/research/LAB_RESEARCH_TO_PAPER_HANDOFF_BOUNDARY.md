# Research Lab to Paper Handoff Boundary

## 1. Purpose

This document defines the boundary between productized research-lab output and
any future paper, shadow, live, runtime, or protected execution work.

The productized research lab may surface advisory outputs, evidence packets,
blocked states, candidate-review prompts, and human-review questions. Those
outputs are review inputs only. Paper, shadow, live, runtime, OMS,
reconciliation, risk, broker/exchange/order, credential, scheduler/autonomy, and
protected execution paths remain outside this milestone.

This document is a boundary definition. It does not build or authorize
paper/shadow/live, candidate admission, canonical crossing,
promotion/readiness, runtime contact, scheduler behavior, provider/API use,
credential handling, implementation work, schema changes, validator changes,
query-layer changes, or protected-path changes.

## 2. Definitions

**Research lab output** means a lab-produced or lab-surfaced research artifact,
operator surface row, report, diagnostic, advisory ranking context, robustness
review, OOS gate result, blocked-state explanation, or candidate-review packet.
It may help a human understand research evidence. It is not an approval,
candidate registration, crossing event, transition, readiness declaration,
paper/shadow/live start, or runtime instruction.

**GO-like research signal** means a research-side observation suggesting that a
strategy or strategy family might deserve human review. A GO-like signal is not
a repo decision, not D2-006 satisfaction by itself, not REC-5 satisfaction by
itself, not candidate admission, not canonical crossing, not promotion, and not
paper/shadow/live readiness.

**Candidate-worthy evidence** means a complete, reviewable evidence set that
appears strong enough for Karl/Main to decide whether a separate candidate or
crossing package should be considered. It must preserve full denominator,
lineage, costs, failures, blockers, robustness posture, unsupported statistics,
and human-review questions. It does not itself register a candidate.

**Candidate admission** means an explicit future human-gated decision and
authorized write path that admits a strategy into a canonical candidate
lifecycle surface. Current lab outputs cannot perform this action.

**Canonical crossing** means an explicitly authorized future append-only move
from noncanonical or advisory research packet material into a canonical
candidate lifecycle record or event. Current repo truth requires explicit human
approval, source content review, hash validation, denominator preservation,
validator/integrity preflight, append-only write semantics, post-write
validation, and audit reporting before any such future crossing.

**Promotion/readiness** means a later human-gated determination that a candidate
has satisfied the governing evidence and approval criteria for a downstream
state such as research-to-shadow, shadow-to-paper, or live review.
Readiness criteria cannot self-execute and cannot replace human approval.

**Paper/shadow/live** means any work involving shadow observation, paper
simulation/runtime, live operation, broker/exchange/order paths, account or
position observation, OMS/reconciliation, live credentials, capital, or
protected execution integration. D2-007 preserves shadow as the sole bridge from
research backtester to paper runtime, and later paper/live work remains
separately gated.

**Protected runtime paths** means the execution-critical boundaries protected
by repo truth, including OMS truth, reconciliation truth, kill-switch and
safe-mode semantics, D-0001 hard caps, D2-008 overlay output semantics,
paper-ledger accounting math, event-log discipline, SignalProvider boundaries,
configs, live-trading paths, and related `src/`, `lib/`, `configs/`, `.claude/`,
and `data/` protected areas where active package scope does not explicitly
authorize changes.

## 3. Required Evidence Packet Before Any Future Paper Discussion

A future paper, shadow, or live discussion may begin only after a separate
authorized review path assembles an evidence packet that is explicit enough for
Karl/Main to inspect. The minimum packet must include:

- exact strategy, Strategy Spec, Variant Manifest, Sweep Plan, candidate, and
  result-population lineage where those surfaces exist;
- full denominator result population, including completed, failed, invalid,
  excluded, aborted, blocked, pruned, data-unavailable, errored, and successful
  variants;
- all failed, invalid, blocked, excluded, and unavailable variants preserved,
  not filtered into a winners-only view;
- D2-006 posture and direct D2-006 pass evidence reference or attestation
  before any research-to-shadow review;
- walk-forward / OOS evidence with split method, chronology, purge/embargo
  posture, denominator mapping, and pass/fail/blocked/advisory-only status;
- robustness, Monte Carlo, bootstrap, DSR, PSR, and MinTRL posture where
  supported by current evidence and method contracts;
- explicit withheld-statistics list where statistics are unsupported, including
  missing return series, missing trial context, missing per-trade rows, missing
  OOS folds, unavailable funding stress, or absent method contracts;
- cost, fee, slippage, funding, leverage, liquidation, fill, data freshness,
  and simulator realism assumptions;
- data availability caveats, irreparable or unavailable-input caveats, and
  whether evidence uses canonical, scratch, fixture, or advisory sources;
- artifact lineage, file paths, source commits, IDs, hashes, and validation
  posture for every evidence input;
- advisory ranking caveats, including that ranking/order can only prioritize
  review and cannot recommend trading, approve gates, or create readiness;
- human-review questions for Karl/Main, including unresolved choices,
  unsupported assumptions, blockers, and required separate authorization.

If any required evidence is absent, the packet must say so plainly and classify
the paper/shadow/live discussion as blocked or premature.

## 4. Non-Authority Boundary

Research lab output cannot auto-register a candidate.

Research lab output cannot execute canonical crossing.

Research lab output cannot promote, demote, approve, reject, retire, reopen, or
declare readiness for a candidate.

Research lab output cannot create paper, shadow, live, runtime, capital,
broker/exchange/order, credential, scheduler/autonomy, notification, or
protected-path authority.

Research lab output cannot contact or mutate runtime, paper/live, OMS,
reconciliation, risk, overlay, safe-mode, kill-switch, config, provider/API,
data, schema, validator, query-layer, runner, compiler, or protected execution
paths unless a later package explicitly authorizes that exact change.

Research lab output cannot convert a D2-006 pass, D2-007 parity result, REC-5
floor crossing, OOS gate pass, robustness diagnostic, dashboard row, queue row,
agent output, advisory rank, notification, or report into automatic approval.

## 5. Human Decision Path

Karl/Main must see explicit decision points before any candidate admission,
canonical crossing, research-to-shadow, shadow-to-paper, paper/live, runtime, or
protected-path work.

Main must surface unclear choices to Karl instead of silently turning a
research signal into a lifecycle, paper, shadow, live, or runtime action.

Any future paper/shadow/live package requires separate explicit authorization
with its own allowed files, forbidden scope, validation, boundary checks,
approval records, and stop conditions.

Automation may prepare evidence only when separately authorized. It may not
approve gates, replace human review, satisfy D2-006, satisfy D2-007, satisfy
REC-5, execute lifecycle transitions, invoke paper/runtime, or change risk.

## 6. Relationship to Future Productization WPs

The lab orchestrator may stop at candidate-surface or
candidate-ready-for-human-review state. It may not execute candidate admission,
crossing, promotion, readiness, paper/shadow/live, runtime, scheduler, or
notification actions without separate authorization.

The cockpit or dashboard may visualize evidence, blockers, readiness context,
paper-risk context, or human-review queues only as read-only operator
visibility. It cannot execute, approve, rank as authority, promote, select,
start paper, start shadow, contact providers, send orders, or mutate state.

Gate actions may record explicit Karl/Main decisions only when a later package
authorizes the exact artifact, schema, validator, and write path. A gate action
cannot bypass D2-006, D2-007, REC-5 exact-segment discipline, Phase 9 / D2-011
human approval semantics, Scope 6 approval-record requirements, or permanent
human gates.

Future paper/shadow/productization work must remain split into narrow packages.
Evidence-packet preparation, candidate crossing, research-to-shadow approval,
shadow evidence retention, shadow-to-paper approval, paper-bot scaffolding,
runtime integration, provider/API work, and live readiness are distinct
authorization problems.

## 7. Stop Conditions

Stop and escalate if evidence is incomplete, inconsistent, unvalidated,
winner-only, missing denominator rows, missing lineage, or below the governing
evidence floor.

Stop and escalate if the denominator is not preserved across planned,
attempted, completed, failed, invalid, excluded, blocked, unavailable, errored,
and successful variants.

Stop and escalate if robustness, DSR, PSR, MinTRL, Monte Carlo, bootstrap,
OOS/fold, per-trade, funding-stress, or simulator-realism support is missing
but hidden, implied, or converted into a pass.

Stop and escalate if backtest realism, cost/fill assumptions, data availability,
funding/liquidation handling, or signal-equivalence evidence is below a future
locked threshold or cannot be stated honestly.

Stop and escalate if candidate admission, canonical crossing,
promotion/readiness, paper/shadow/live, runtime, OMS, reconciliation, risk,
broker/exchange/order, credential, provider/API, scheduler/autonomy,
notification firing, schema, validator, query-layer, runner, compiler, data, or
protected-path contact would be needed.

Stop and escalate if a future package would treat lab output, dashboard
visibility, advisory ranking, agent output, D2-006 evidence, D2-007 evidence,
REC-5 evidence, OOS evidence, or robustness evidence as automatic authority.

## 8. Current Boundary Decision

The current decision is to define the handoff line only.

This document creates no candidate, crossing, approval, readiness, paper,
shadow, live, runtime, scheduler, notification, provider/API, credential,
dependency, schema, validator, query, implementation, result-population, data,
or protected-path authority.
