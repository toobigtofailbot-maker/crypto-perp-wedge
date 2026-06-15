# Paper / Shadow Chassis Design

## 1. Package Scope

WP-CHASSIS-PAPER-DESIGN-01 designs a disconnected paper/shadow chassis and
live-readiness decomposition for future BTCUSDT USDT-M perpetual work.

This package is architecture design only. It does not implement paper runtime,
shadow runtime, OMS behavior, reconciliation behavior, risk caps, safe mode,
kill-switch behavior, exchange connectivity, broker connectivity, credentials,
deployment, dashboards, alerts, schemas, validators, query-layer behavior, or
any live-trading path.

The design is non-authoritative. It can inform later packages, but every
implementation, promotion, runtime integration, or live-readiness step requires
a separately scoped and reviewed package.

## 2. Repo-Truth Basis

Facts:

- The repo has a protected deterministic Phase 1 paper/runtime foundation.
- Current Phase 2 work is research-first and candidate-agnostic.
- Existing architecture docs define protected OMS state-machine,
  reconciliation-loop, execution-policy, safe-mode/flatten, paper-scaffolding,
  operator-surface, alert/briefing, and paper-runtime proof-bar concepts.
- The two-lane sandbox wall separates canonical research/evidence artifacts
  from sandbox and paper engineering surfaces.
- Existing research, result-population, advisory, dashboard, and alert
  artifacts have no execution, promotion, or live-trading authority.

Inference:

- A future paper/shadow chassis needs its own architecture surface before any
  implementation can be reviewed safely.
- The chassis must be disconnected from the research engine: research artifacts
  may be selected and read as inputs, but research code and artifacts must not
  own runtime state, OMS state, risk state, reconciliation state, or promotion.
- Paper and shadow modes should share operator, provenance, observability, and
  fail-closed concepts, while keeping their state separate from canonical
  research evidence.

Decision:

- The future chassis should be designed as a boundary layer between approved
  candidate specifications and any later paper/live execution surfaces.
- Strategies produce signal or position intent only. They never contact an
  exchange and never place, cancel, replace, or reconcile orders.
- OMS, reconciliation, risk caps, safe mode, kill switch, operator controls,
  data-feed gating, secrets, release, observability, and runbooks are required
  live-readiness domains, not optional polish.

Open questions:

- Which concrete artifact family should record future paper/shadow evidence.
- Whether the first paper implementation should reuse protected Phase 1 runtime
  modules or remain a separate sandbox chassis until parity evidence exists.
- Which exchange-specific constraints must be represented before first shadow
  mode versus before first live mode.
- Which operator dashboard surface should be implemented first after a
  read-only state snapshot exists.

## 3. Architecture Boundary

The chassis has four conceptual layers:

1. Research evidence layer: candidate specs, variant manifests, sweep plans,
   result populations, reports, advisory outputs, and human decisions.
2. Chassis intake layer: manually selected candidate/spec references, config
   identity, signal-equivalence checks, operator approval, and provenance.
3. Paper/shadow operations layer: bar ingestion, signal generation, paper or
   shadow mode, simulated or observed order state, position/account model,
   risk/safe-mode evaluation, event logging, observability, and operator
   controls.
4. Future venue boundary: OMS abstraction, exchange constraints, reconciliation,
   secrets, release controls, and live-readiness gates.

Required boundary rules:

- Research artifacts are inputs only after explicit human selection.
- The chassis does not mutate canonical research artifacts.
- Paper/shadow evidence is not promotion authority.
- Shadow observation is not live authorization.
- Paper PnL is not live readiness.
- Dashboard and alert output are presentation only.
- Missing, stale, ambiguous, unauthorized, or inconsistent inputs fail closed.

## 4. Paper / Shadow Engine

Signal intake from approved candidate specs:

- The engine may read only committed, approved, and manually selected candidate
  or Strategy Spec references from the research layer.
- Intake must record artifact IDs, file paths, source commit, identity hashes
  where available, config identity, operator approval, and run ID.
- Intake must reject uncommitted, stale, ambiguous, or unsupported candidate
  references unless a later package explicitly defines a local scratch mode.
- Intake must not infer promotion, ranking, or readiness from result
  populations or reports.

Recent/live bar processing:

- The engine consumes recent bars from a separately authorized feed component.
- Signal generation runs on closed bars only unless a later package explicitly
  authorizes intrabar semantics.
- Bar timestamps, feed source, data freshness, and gap handling decisions must
  be recorded with the signal event.
- If the bar stream is missing, stale, duplicated, out of order, or not aligned
  to the candidate timeframe, the engine must enter a no-new-intent state.

Paper mode:

- Paper mode produces local simulated orders, fills, positions, account state,
  PnL, fees, funding, and risk state.
- It does not contact an exchange.
- It does not create exchange orders.
- It does not reconcile against live venue state.
- Its output is sandbox evidence only.

Shadow mode:

- Shadow mode observes live or recent market/account facts only after future
  authorization for the exact read paths.
- Shadow mode must not submit, amend, cancel, test, or flatten orders.
- If account or order observation is authorized later, observed state must be
  read-only and separated from paper simulation state.
- Shadow output is operational parity evidence only, not execution authority.

Replay/simulation mode:

- Replay mode consumes historical or recorded bars deterministically.
- Replay uses the same signal semantics and timing as paper/shadow mode.
- Replay may be used to debug bar-close timing, fill assumptions, and operator
  display without live contact.
- Replay output must be labeled as replay and cannot be mixed with paper or
  shadow evidence without source labels.

Paper evidence storage:

- Future paper/shadow evidence should be stored in a dedicated artifact family
  or state path defined by a separate package.
- Minimum evidence fields: run ID, selected candidate/spec, source commit,
  config identity, operator approval reference, data-feed identity, mode,
  signal events, order-intent events, simulated fills, position/account state,
  risk state, safe-mode state, observability summary, and non-authority
  declaration.
- Evidence storage must not mutate Strategy Specs, Variant Manifests, Sweep
  Plans, result populations, trial logs, schemas, validators, or query views
  unless a later package explicitly authorizes additive read-only surfaces.

Non-authority boundary:

- The paper/shadow engine cannot approve a candidate, promote to live, resize
  capital, alter risk parameters, change overlays, or select strategies
  automatically.

## 5. OMS Abstraction

Strategy boundary:

- Strategies produce signal or target-position intent only.
- Strategies never import exchange clients, broker clients, credential code,
  order APIs, account APIs, OMS state, or reconciliation state.
- Strategies do not encode exchange filters as trading logic.

OMS responsibility:

- Only the OMS abstraction can express order intent.
- OMS transforms desired position into place/cancel/replace intent after
  applying reconciliation state, exchange constraints, risk gates, and safe-mode
  state.
- OMS owns order lifecycle vocabulary and idempotency, but this document does
  not implement it.

Conceptual order-intent schema:

```text
OrderIntent:
  run_id
  decision_id
  client_order_id
  symbol
  mode: paper | shadow_observation | future_live
  action: place | cancel | replace | cancel_all | flatten
  side: buy | sell
  position_side: long | short | both | one_way
  order_type: market | limit
  quantity
  price
  time_in_force
  reduce_only
  post_only
  intent_reason
  risk_gate_snapshot
  exchange_filter_snapshot
  created_at_utc
```

Idempotent client order IDs:

- Client order IDs must be deterministic within run, decision, symbol, side,
  action, and sequence scope.
- Re-submitting the same intent after a retry must not create accidental
  duplicate exposure.
- Cancel and cancel-all intent must be safe to retry.

Order lifecycle:

- Conceptual states: planned, submitted, acknowledged, working, partially
  filled, filled, cancel requested, canceled, rejected, expired, terminal
  unknown, reconciled.
- Unknown states must be resolved by reconciliation or fail closed.
- Every lifecycle event must link back to `decision_id` and `client_order_id`.

Reduce-only, post-only, market, and limit handling:

- Reduce-only is required for any order intended only to reduce exposure.
- Post-only is a maker-liquidity constraint, not a risk control.
- Market orders are emergency or explicit-taker behavior and must be visible in
  operator and observability output.
- Limit orders must satisfy tick size, price band, time-in-force, and
  post-only constraints where applicable.

Cancel/replace:

- Replace should be modeled as cancel old intent plus place new intent unless
  a future package explicitly supports atomic amend semantics.
- Mismatched price, quantity, side, reduce-only, or post-only state requires a
  deterministic cancel/replace decision.

Rate-limit handling:

- OMS must classify rate-limit responses separately from permanent rejects.
- Bounded retry with backoff is allowed at design level.
- Retry exhaustion must halt new risk-increasing intent and trigger
  reconciliation or safe mode depending on risk.

Exchange error taxonomy:

- Transient transport failure.
- Rate limit or throttling.
- Authentication or permission failure.
- Invalid order parameters or filters.
- Insufficient margin.
- Reduce-only rejection.
- Post-only rejection.
- Order not found.
- Unknown order status.
- Exchange maintenance or degraded service.
- Symbol or instrument status change.

No implementation:

- This document defines vocabulary only. No OMS code, connector code, live API
  call, or test-order path is authorized.

## 6. Reconciliation

Reconciliation compares expected internal state against observed state. In
paper mode, observed state is the local simulation ledger. In any future
shadow/live mode, observed state may include authorized read-only or live venue
state. The reconciliation design must preserve the existing repo principle that
reconciliation is the only deterministic path for resolving uncertainty.

Required comparisons:

- Expected position versus observed position.
- Expected open orders versus observed open orders.
- Expected fills versus observed fills.
- Expected equity versus observed equity.
- Expected margin versus observed margin.
- Expected unrealized PnL versus observed unrealized PnL.
- Expected realized PnL versus observed realized PnL.
- Expected funding payments versus observed funding payments.

Drift classifications:

- No drift: expected and observed match within defined tolerance.
- Timing drift: explainable by feed, fill, or report latency within tolerance.
- Fill gap: observed fill is missing from internal state.
- Open-order drift: order missing, extra, mismatched, or terminal unknown.
- Position drift: position quantity or side differs beyond tolerance.
- PnL drift: realized or unrealized PnL differs beyond tolerance.
- Equity/margin drift: account equity or margin differs beyond tolerance.
- Funding drift: funding payment timing or value differs.
- Filter drift: exchange constraints changed since intent planning.
- Unknown live risk: state cannot prove order and position safety.

Stop/halt behavior:

- Timing drift within tolerance may continue in reduced observation mode.
- Fill gaps must be ingested and reconciled before new risk-increasing intent.
- Open-order drift defaults to cancel unknown orders in future live-capable
  designs, subject to the existing OMS/reconciliation specs.
- Unexplained position, equity, margin, or PnL drift must halt new
  risk-increasing intent.
- Unknown live risk must trigger safe mode or frozen state according to later
  implementation authority.

## 7. Risk Caps / Safe Mode / Kill Switch

Risk caps are hard gates. They are evaluated before order intent and during
reconciliation. They are not strategy preferences.

Required cap families:

- Position cap: maximum absolute position per symbol and mode.
- Leverage cap: maximum effective leverage versus equity or margin basis.
- Daily loss cap: maximum realized plus unrealized loss for the UTC/session day.
- Per-order size cap: maximum notional or quantity per order intent.
- Max drawdown cap: maximum drawdown for paper or future live mode.
- Max stale data age: maximum age for bars, market data, account data, and
  signal data before no-new-intent.

Safe-mode triggers:

- Manual operator safe-mode action.
- Risk cap breach or unavailable risk-cap calculation.
- Stale data beyond configured tolerance.
- Unknown live order risk.
- Unexplained position, order, equity, margin, PnL, or funding drift.
- Reconciliation failure.
- Exchange permission/authentication failure.
- Repeated rate-limit or transport failure that prevents state certainty.
- Invalid or missing runtime configuration.
- Clock skew beyond tolerance.
- Operator dashboard or observability reports a boundary incident.

Kill-switch semantics:

- Kill switch is an operator or safety-dominant state that blocks new
  risk-increasing intent.
- In paper mode, kill switch halts the paper loop and freezes simulated order
  generation.
- In future live-capable mode, kill switch must cancel open orders, flatten
  according to authorized policy, verify zero open orders and zero position,
  and enter frozen state.
- This document does not redefine existing protected kill-switch semantics.

Manual halt/resume:

- Halt is always allowed to reduce or freeze activity.
- Resume requires operator action, fresh configuration validation, fresh
  reconciliation, healthy feeds, healthy risk-cap state, and a recorded reason.
- Resume cannot happen automatically after a severe mismatch.

Fail-safe default:

- If the system cannot prove it is safe to generate new intent, it generates no
  new risk-increasing intent.

## 8. Operator Controls And Dashboard

Required before paper/shadow:

- Selected candidate/spec reference and source commit.
- Mode: replay, paper, or shadow.
- Run ID and current run state.
- Operator approval record.
- Data freshness and latest accepted closed bar.
- Signal freshness and latest signal event.
- Current simulated or observed position summary.
- Current simulated or observed order summary.
- Risk cap state.
- Safe-mode or kill-switch state.
- Heartbeat and last event timestamp.
- Boundary declaration: no live orders in paper/shadow unless later explicitly
  authorized.

Can wait until live:

- Full exchange account detail panels.
- Multi-account or cross-venue views.
- Advanced latency histograms by exchange endpoint.
- Automated incident routing beyond human notification.
- Live credential health beyond explicit environment checks.
- Capital-allocation views.

Manual controls:

- Halt.
- Resume after preconditions.
- Enter safe mode.
- Acknowledge incident.
- Mark run reviewed.
- Export read-only evidence snapshot.

Controls that require later authorization before implementation:

- Start paper run.
- Stop paper run.
- Reset paper state.
- Manual flatten.
- Live credential enablement.
- Live deployment promotion.

Dashboard status indicators:

- Data freshness.
- Signal freshness.
- Order lifecycle.
- Position drift.
- PnL drift.
- Risk cap state.
- Safe-mode state.
- Kill-switch state.
- Heartbeat.
- Reconciliation status.
- Feed status.
- Release/config identity.

Dashboard boundary:

- The dashboard cannot be source of truth, cannot mutate canonical research
  artifacts, cannot trigger live orders, and cannot promote or approve
  candidates.

## 9. Data Feed Architecture

Websocket versus REST polling decision points:

- Websocket is preferred for low-latency market updates, account updates, order
  updates, and heartbeat-sensitive streams when future implementation authority
  exists.
- REST polling is acceptable for low-frequency bootstrap, periodic snapshots,
  reconciliation checks, and fallback when websocket health is degraded.
- Paper mode can begin with deterministic local or REST-like bar snapshots if
  later scoped; shadow/live requires explicit feed-health and reconciliation
  contracts.

Bar builder:

- The bar builder must define source stream, interval, close-time convention,
  timezone, completeness rule, duplicate handling, and out-of-order handling.
- Signals consume only accepted closed bars.
- Bar-builder output must include source metadata and freshness timestamp.

Clock/time sync:

- All runtime timestamps are UTC.
- System clock skew must be measured against a trusted source or exchange time
  before live-capable operation.
- Excessive clock skew blocks new intent.

Missing-bar handling:

- Missing bars are never silently interpolated.
- Missing bars produce a visible feed state and no-new-intent until the policy
  defines replay, gap skip, or halt behavior.
- Gap decisions must be recorded with the run evidence.

Replay mode:

- Replay uses committed or recorded bars with deterministic iteration.
- Replay must preserve the same bar-close timing used by paper/shadow signal
  generation.
- Replay cannot contact live feeds.

Stale feed detection:

- Feed freshness must be evaluated separately for market bars, account state,
  order state, fills, funding, and exchange filters where applicable.
- Stale feed state blocks new risk-increasing intent.

Feed failover:

- Failover can switch between authorized sources only when source precedence,
  data identity, and gap handling are defined.
- Failover must be visible in logs and dashboard state.
- A failover that changes data semantics requires no-new-intent until reviewed.

Live feed gating:

- Live-capable operation requires healthy market feed, order/account feed,
  reconciliation snapshots, exchange filters, and clock sync.
- Any absent required live feed blocks live operation.

## 10. Order Model / Exchange Constraints

Required exchange-constraint inputs before live:

- Symbol status.
- Price tick size.
- Quantity step size.
- Minimum and maximum quantity.
- Minimum notional.
- Price bands or percent-price filters.
- Leverage and margin mode constraints.
- Position mode: one-way or hedge.
- Reduce-only support and restrictions.
- Post-only or maker-only support.
- Time-in-force support.
- Trigger/protection rules if stop or conditional orders are ever introduced.
- Rate limits and order-count limits.
- Exchange maintenance/degraded status.

Design rules:

- Order planning must validate constraints before intent is emitted.
- Constraint snapshots must be included in intent evidence.
- Constraint drift invalidates pending plans and requires re-planning.
- If constraints are missing or invalid, no new order intent is allowed.

## 11. Position / Account State Model

Minimum position fields:

- Symbol.
- Mode.
- Position side.
- Quantity.
- Entry price.
- Mark price.
- Notional.
- Unrealized PnL.
- Realized PnL.
- Funding accrued or paid.
- Last fill timestamp.
- Last reconcile timestamp.

Minimum account fields:

- Equity.
- Available balance.
- Initial margin.
- Maintenance margin.
- Margin ratio.
- Effective leverage.
- Daily realized PnL.
- Daily unrealized PnL.
- Drawdown from session or run high-water mark.
- Fee and funding totals.

State rules:

- Paper state is derived from simulation.
- Shadow observed state, if authorized later, is read-only and labeled observed.
- Expected state and observed state must remain distinct until reconciled.
- Account state cannot be inferred from price alone in live-capable designs.

## 12. Backtest-To-Paper Signal Equivalence

Proof requirements:

- Same spec: paper/shadow generation references the exact committed candidate or
  Strategy Spec selected by the operator.
- Same signal semantics: indicator definitions, side labels, entries, exits,
  throttles, and flat behavior match the backtest/compiler semantics.
- Same bar-close timing: no intrabar information is used when the backtest used
  closed bars.
- Same position intent: long, short, flat, and side-specific transitions match
  the backtest signal stream.
- Same throttle/exit semantics: holding periods, cooldowns, exits, and
  mutually exclusive side behavior match the compiled or documented semantics.
- No lookahead: signal generation cannot use future bars, unfinished bars, or
  post-close information unavailable at decision time.
- Reproducibility: replay of the paper/shadow signal generator over the same
  historical bars must reproduce the offline signal sequence within documented
  tolerances.

Required evidence before paper/shadow:

- Spec artifact identity.
- Data/bar identity.
- Signal generator version.
- Equivalence test or replay result.
- Differences, if any, explicitly classified and reviewed.

## 13. Paper Fill / Simulation Model

Fill timing options:

- Mark-price fill: useful for simple mark-to-market approximation, but not
  sufficient for exchange-executable order behavior.
- Next-bar open fill: closer to current backtest-style bar-close decisions when
  decisions are made after a closed bar.
- Quote-aware fill: requires bid/ask or book data and is a later upgrade.

Recommended first paper default:

- Use next accepted bar open for market-like simulated fills when operating from
  closed-bar signals, with explicit fee, slippage, and latency assumptions.

Spread/slippage model:

- Minimum first model: fixed bps spread/slippage assumption by order type.
- Upgrade path: time-varying spread model from quote data.
- Every fill must record the model and parameter values used.

Latency model:

- Minimum first model: deterministic one-decision-cycle latency or configured
  milliseconds applied consistently.
- Upgrade path: empirical latency distribution from measured feed and order
  timestamps.

Partial-fill simulation:

- Minimum first model may assume all-or-none fills if labeled.
- Partial fills are required before live-like order lifecycle testing.
- Partial-fill state must support remaining quantity, average fill price,
  cancel after partial, and PnL/account updates.

Fees and funding:

- Fees must be recorded by maker/taker assumption.
- Funding must be applied using the appropriate funding timestamp and position
  exposure convention.
- Funding gaps must be visible and fail closed if they materially affect the
  model.

Liquidation:

- First paper mode may use a liquidation-risk flag if exact liquidation
  mechanics are not modeled.
- Live-readiness requires stronger liquidation and margin-risk modeling or an
  explicit reason why leverage/risk caps make liquidation unreachable under
  configured bounds.

Model limitations:

- Bar-based fills do not prove fillability.
- Fixed slippage does not prove live execution quality.
- Paper fills do not validate exchange queue position.
- Paper PnL does not prove live profitability.

Upgrade triggers:

- Candidate reaches paper/shadow review.
- Fill assumptions dominate PnL or risk conclusions.
- Partial fills, maker orders, reduce-only behavior, or post-only behavior
  materially affect lifecycle evidence.
- Live-readiness review begins.

## 14. Secrets / Key Management

Hard rules:

- No secrets in repo.
- No API keys, secret keys, tokens, chat IDs, private endpoints, or credential
  examples that look real.
- Paper mode does not require live credentials.
- Missing live credentials are expected in design and paper-only contexts.

Environment separation:

- Replay, paper, shadow-read-only, and future live environments must have
  separate configuration and credential scope.
- Live credentials cannot be accepted by replay or paper-only commands.
- Shadow-read-only credentials, if ever authorized, must be permission-limited.

Withdrawal-disabled keys:

- Any future exchange key must be withdrawal-disabled.
- Trade-enabled keys require explicit live authorization and operator approval.
- Read-only keys are preferred for shadow observation.

Key storage model:

- Local environment variables, OS secret store, or external secret manager can
  be considered later.
- `.env` files remain local and uncommitted.
- Logs and error output must redact credential material.

Key rotation and revocation:

- Rotation procedure must be documented before live credentials.
- Emergency revocation must be an operator runbook.
- Suspected leak requires immediate revocation and incident record.

Operator approval:

- Live credentials cannot be added, used, or tested without explicit operator
  approval and separate package authorization.

## 15. Release / Deployment

Versioned release artifact:

- Any future paper/shadow runtime must identify source commit, package version,
  config identity, selected candidate/spec identity, data-feed identity, and
  simulation model identity.

Deployment checklist:

- Clean worktree or declared dirty state.
- Config freeze.
- Runtime config validation.
- Candidate/spec identity validation.
- Feed validation.
- Risk-cap validation.
- Secrets absence or authorized secret-scope validation.
- Dry-run startup check.
- Operator approval.
- Rollback plan.

Rollback:

- Rollback returns to the prior approved release/config pair.
- Rollback must preserve evidence and incident records.
- Rollback cannot mutate canonical research artifacts.

Config freeze:

- Runtime config must be immutable for a run except through explicit operator
  change records.
- Config changes during a run require halt, review, and restart unless a later
  package defines safe live reload semantics.

Dry-run startup check:

- Validate config, candidate/spec identity, feed availability, risk caps,
  clock sync, state paths, secrets posture, and dashboard/alert output paths.
- Dry-run cannot place, cancel, test, or reconcile real orders.

Migration procedure:

- State migrations must be explicit, versioned, reversible where practical,
  and validated on copies before production state.
- Migration failures fail closed.

Environment promotion:

- Replay to paper requires equivalence proof and operator approval.
- Paper to shadow requires feed, observability, and non-trading read-path
  authorization.
- Shadow to live requires separate live-readiness review and human approval.

## 16. Runbooks / Incident Response

Required runbooks before paper/shadow:

- Halt.
- Restart.
- Stale feed.
- Bad data.
- Safe-mode entry.
- Safe-mode exit.
- Position mismatch in paper state.
- PnL drift in paper state.
- Evidence export and review.

Required runbooks before live:

- Exchange disconnect.
- Open-order mismatch.
- Position mismatch.
- Daily loss breach.
- Manual flatten.
- Cancel-all failure.
- Unknown live order status.
- Credential compromise.
- Exchange maintenance.
- Rate-limit exhaustion.
- Failed rollback.

Runbook rules:

- Runbooks must name preconditions, exact operator action, expected state,
  verification step, evidence to retain, and escalation path.
- No runbook may instruct committing secrets.
- No runbook may rely on dashboard state as the only source of truth.

## 17. Observability

Required telemetry:

- Heartbeat.
- Feed latency.
- Bar freshness.
- Signal freshness.
- Order lifecycle state.
- Position drift.
- PnL drift.
- Equity/margin drift.
- Risk cap state.
- Safe-mode state.
- Kill-switch state.
- Reconciliation result.
- Error taxonomy counts.
- Config/release identity.

Alert routing:

- Alerts notify humans only.
- Alerts cannot trigger execution, recovery, cancel, flatten, restart, config
  change, promotion, or readiness transition.
- Routing channels require separate authorization when networked.

Alert severity:

- Info: routine state, run start/stop, evidence export.
- Warning: stale feed, missing optional data, degraded latency, nearing caps.
- Critical: risk cap breach, unknown order state, unexplained drift, safe mode,
  kill switch, credential incident.

Log retention:

- Retain run evidence, operator actions, state transitions, risk events,
  reconciliation summaries, and incident records long enough for post-mortem
  and review.
- Logs must exclude secrets and raw signed payloads.
- Retention policy is a live-readiness requirement before production use.

## 18. Live-Readiness Classification

| Component | Classification | Rationale |
|---|---|---|
| Candidate/spec manual selection | Required before candidate | Prevents automatic research-artifact authority. |
| Backtest-to-paper signal equivalence proof | Required before paper/shadow | Paper/shadow evidence is meaningless if signal semantics drift. |
| Replay mode | Required before paper/shadow | Provides deterministic timing and equivalence debug path. |
| Paper/shadow state artifact family | Required before paper/shadow | Evidence must be separate, auditable, and non-authoritative. |
| Paper fill/simulation model v1 | Required before paper/shadow | Paper mode needs explicit deterministic fill/accounting assumptions. |
| Data-feed freshness gate | Required before paper/shadow | Stale or malformed bars must block new intent. |
| Operator approval record | Required before paper/shadow | Human selection and run start must be auditable. |
| Operator halt control | Required before paper/shadow | Operator must be able to stop a paper/shadow run. |
| Read-only operator status surface | Required before paper/shadow | Operator needs state visibility before running the chassis. |
| Heartbeat and freshness observability | Required before paper/shadow | Missing runtime health must be visible. |
| OMS order-intent abstraction | Required before live | Live execution must route through OMS intent, not strategies. |
| Exchange constraint model | Required before live | Orders must satisfy filters, modes, and rate limits before submission. |
| Reconciliation against venue state | Required before live | Live state uncertainty must be resolved deterministically. |
| Risk caps | Required before live | Position, leverage, loss, order-size, drawdown, and stale-data caps are hard gates. |
| Safe-mode and kill-switch implementation | Required before live | Live operation needs deterministic risk-reduction and frozen-state behavior. |
| Secrets/key-management procedure | Required before live | Live or read-only credentials require storage, rotation, and revocation controls. |
| Deployment/release checklist | Required before live | Release identity, rollback, dry-run, and config freeze are production prerequisites. |
| Live incident runbooks | Required before live | Human operators need tested procedures for venue and risk incidents. |
| Alert routing beyond local output | Required before live | Critical live incidents need routed human notification, without execution authority. |
| Partial-fill simulation | Required before live | Live-like lifecycle evidence needs partial-fill behavior. |
| Quote-aware fill model | Required before live | Maker/post-only and spread-sensitive behavior need better fill realism. |
| Account/margin/liquidation model | Required before live | Leverage and margin risks cannot be approximated loosely for live review. |
| Cross-venue support | Deferred / explicitly blocked | Out of current single-venue scope. |
| Multi-instrument scaling | Deferred / explicitly blocked | BTCUSDT single-instrument scope remains the design basis. |
| Capital scaling | Deferred / explicitly blocked | No capital authority is created. |
| Any autonomy over capital | Deferred / explicitly blocked | Human gates remain mandatory. |
| Self-modifying risk params | Deferred / explicitly blocked | Risk caps cannot be changed autonomously. |
| Unsupervised live promotion | Deferred / explicitly blocked | Live promotion remains human-gated and separately authorized. |

## 19. Future Package Split

Future option, not authority:

1. Paper/shadow artifact and state model design.
2. Signal-equivalence harness design and no-live replay proof.
3. Paper fill/accounting model implementation in a sandbox path.
4. Read-only operator status snapshot and dashboard surface.
5. Shadow read-only feed and account observation design.
6. OMS/reconciliation live-readiness impact map.
7. Secrets and deployment readiness design.
8. Live-readiness review package.

Each package must restate allowed files, forbidden scope, validation, and
boundary checks.

## 20. What Is Not Authorized

This design does not authorize:

- paper runtime implementation;
- shadow runtime implementation;
- OMS implementation;
- reconciliation implementation;
- exchange connector implementation;
- broker connector implementation;
- live data feed implementation;
- credentials or secrets;
- deployment;
- dashboard implementation;
- alert implementation;
- schema, validator, compiler, runner, query-layer, or `lib` changes;
- Strategy Spec, Variant Manifest, Sweep Plan, result-population, or research
  artifact mutation;
- candidate promotion or readiness authority;
- paper-to-live or live-trading authority;
- capital authority;
- autonomous risk changes;
- real orders, test orders, cancels, flattening, or exchange contact.
