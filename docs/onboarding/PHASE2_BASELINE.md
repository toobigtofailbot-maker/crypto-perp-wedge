# Phase 2 Locked Baseline

**Status:** LOCKED
**Authority:** Main Architecture chat
**Supersedes:** `docs/onboarding/PHASE2_MANDATE.md` (kept for history)
**Change protocol:** Any modification requires a new Decision Change entry in `docs/decisions.md` approved by Karl or Santi. This document is the authoritative Phase 2 reference. When any other document contradicts this one, this one wins and the other must be updated.

---

## Current V2 bounded-autonomy clarification (D2-020 / V2-00)

`D2-020` and
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`
are the controlling future research-authorization and roadmap authority where
earlier wording conflicts. V2 prospectively replaces per-hypothesis approval
with Karl-approved bounded-envelope authority for legal in-envelope research.
D2-011 and D2-016 are superseded only to that extent; D2-005
preregistration, D2-006 promotion gates, D2-007 shadow/parity, D2-014
timeframe-at-hypothesis discipline, and D2-019 adoption-first ownership remain
intact.

This is not operational on merge. Per-hypothesis approval and all current
default-off/autonomy restrictions remain effective until Stage 5B is
implemented, validated, explicitly activated, and a valid Karl-approved
bounded research envelope exists. Humans permanently retain envelope changes,
scientific-policy changes, candidate promotion, protected execution, risk,
paper/live, capital, and live-activation authority. CPW owns authoritative
scientific lineage and contamination-aware final-holdout state; Research
Memory is indexing/retrieval only.

---

## Current adoption-first clarification (D2-019 / CPW-MIG-00)

D2-019 and
`docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`
are the current controlling architecture where earlier Phase 2 wording
conflicts. Infrastructure buildability is not candidate-gated; economic
activation is.

Separately authorized Phase 2 migration packages may conduct bounded,
non-capital Nautilus N1 research/simulation proof, N2
paper/accounting/restart proof, and N3 Binance USD-M/order/reconnect proof
before genuine edge or GO exists. This creates no candidate-performance claim,
candidate-specific paper/shadow conclusion, promotion, live-readiness
conclusion, live deployment, or capital authority. Generic ownership follows
the CPW-MIG-00 map: Hermes for generic agent/reasoning runtime, Prefect for
generic orchestration, Nautilus for generic trading mechanics after proof, CPW
for differentiated scientific/canonical/safety semantics, and humans for
economic authority.

---

## Phase 2 Direction Update (Locked clarification)

Phase 2 remains research-first, but the accepted path is no longer forced to be candidate-first with research infrastructure deferred until after Strategy v1. Phase 2 now explicitly includes a candidate-agnostic research machine foundation tranche for systematic BTCUSDT candidate discovery, testing, comparison, and later human-gated promotion.

This clarification does not weaken the protected deterministic execution core, does not lock Strategy v1 now, and does not convert the project into agentic execution. OMS truth, reconciliation truth, kill-switch semantics, D-0001 hard caps, overlay bounds, paper ledger accounting, and runtime decision paths remain protected.

The immediate next architecture work may include bounded research-process foundations such as a candidate registry, experiment artifact schemas, evidence/report conventions, pipeline foundation work, and later bounded research-agent interfaces. Candidate execution resumes through that broader research machine rather than being the only organizing principle of the phase.

H-011 and future hypotheses remain valid backlog candidates, but no single candidate is automatically the central next move. Strategy v1 lock-in is deferred until structured evidence supports selection, ranking, shadow readiness, and human approval.

---

## Purpose

This document locks the Phase 2 architecture, operating model, and execution direction for the BTCUSDT USDT-M perpetual futures trading system. It defines what Phase 2 is, what it is not, what changed relative to Phase 1, and what remains protected.

Phase 2 is a **research program**, not a runtime-infrastructure expansion program. Its job is to answer one question: *is there a tradeable edge in BTCUSDT perpetual futures at the locked timeframes, net of realistic costs, passing objective promotion gates?* Candidate-agnostic research machine foundations are in scope when they directly improve disciplined candidate discovery, evidence collection, comparison, or human-gated promotion without touching protected execution.

---

## Scope summary

- **Research-first, infrastructure-second.**
- **Lightweight pandas/numpy backtester as primary research engine.** Phase 1 paper runtime remains untouched and is used only for shadow mode.
- **Full free Binance history** as the authoritative Phase 2 dataset. No paid data sources in Phase 2.
- **Deflated Sharpe Ratio + trial log + pre-registered hypotheses** as the overfitting firewall.
- **Shadow mode** as the sole bridge from research backtester to paper runtime.
- **OpenClaw reduced to a thin orchestration layer** (skills, workflows, agent definitions under `.claude/`).
- **Stronger agent involvement** in research, evaluation, and monitoring. No agent touches execution or risk parameters.
- **Broadened timeframe set:** 15m, 30m, 1h, 4h, 1d.

---

## Locked Decisions D2-001 through D2-017

Each decision below is structured as: **What changes / Why / Trade-offs / What remains protected / Implementation impact.**

---

### D2-001 — Research-first, infrastructure-second

- **What changes:** Phase 2 is an alpha research program, not a runtime-infrastructure program. Engineering effort is gated on "does this improve disciplined BTC candidate research, evidence quality, comparison, or promotion readiness?" If the answer is no, it is deferred. Candidate-agnostic research machine foundations are allowed under that gate.
- **Why:** Phase 1 built sound infrastructure with zero validated strategies. Continuing to refine plumbing before testing alpha inverts the professional quant workflow and burns the scarcest resource (team attention).
- **Trade-offs:** Less architectural elegance in the protected runtime in the short term; some Phase 1 polish work is deliberately left undone. In exchange, we get validated or killed hypotheses and reusable research evidence flow without prematurely locking Strategy v1.
- **What remains protected:** D-0001 hard risk caps, OMS state machine semantics, reconciliation truth rules, kill-switch, overlay bounds {ALLOW, ALLOW_REDUCED=0.5, BLOCK} + fail-open, event log schema.
- **Implementation impact:** Work packages are measured by research evidence quality, candidate throughput, and promotion-readiness clarity, not "files written per week" or runtime polish.

---

### D2-002 — Lightweight pandas/numpy backtester as the primary research engine

- **What changes:** We do NOT extend the Phase 1 paper runtime into a historical replay engine as the primary research path. Instead, we build a ~300-line pandas/numpy backtester in `lib/backtest.py` that takes `(signal_series, ohlcv, funding) → equity_curve + metrics`. The paper runtime remains the live/shadow execution path; the research backtester is a separate, simpler tool.
- **Why:** Replay-through-paper-runtime was architecturally correct but the wrong tradeoff for our stage. A pandas backtester runs 1000× faster, is trivially parallelizable for parameter sweeps, and fits hypothesis-notebook workflow. Parity is re-established at shadow-deployment time (D2-007), not at research time.
- **Trade-offs:** Two execution surfaces for a window (research vs shadow); parity must be explicitly verified before promotion rather than guaranteed by construction. Accepted because research velocity matters more than parity during hypothesis testing.
- **What remains protected:** Paper runtime, ledger math, overlay evaluator — untouched.
- **Implementation impact:** WP-1b builds `lib/backtest.py`; no refactor of `paper_trader.run_once`; no `replay_runner.py` in Phase 2.

---

### D2-003 — Free Binance data as the authoritative dataset (Tier 0 only for Phase 2)

- **What changes:** Historical data comes from `data.binance.vision` monthly/daily archives (OHLCV, mark, index, premium index klines with SHA256 checksums) plus Binance REST `/fapi/v1/fundingRate` for funding history. Target window: full history since BTCUSDT perp listing (Sep 2019 → present, ~6.5 years). No paid data sources in Phase 2.
- **Why:** Tier 0 covers 100% of what 1h/4h/15m/30m/1d bar strategies need. Tardis.dev and order book data become relevant only when live-deployment slippage modeling matters — that is Phase 3.
- **Trade-offs:** No tick-level order book history, so slippage models in backtests are parametric (assumed bps), not empirical. Documented limitation.
- **What remains protected:** Existing fetch scripts, `docs/data_catalog.md` format, gitignored data directories.
- **Implementation impact:** WP-1a extends existing `scripts/fetch_btcusdt_*` to cover full history via `data.binance.vision` bulk downloads. No raw data committed. Parquet files + SHA256 entries in `docs/data_catalog.md` remain the provenance mechanism.

---

### D2-004 — Deflated Sharpe Ratio + trial log as the overfitting firewall

- **What changes:** Every backtest run — successful, failed, exploratory — is logged as a JSONL line in `research/trial_log.jsonl` with config hash, dataset hash, parameters, Sharpe, and timestamp. The Deflated Sharpe Ratio (Bailey & López de Prado) is computed on every candidate before promotion, using the trial count from the log.
- **Why:** The dominant failure mode of retail quant projects is overfitting. DSR with a trial count is the single statistical correction that catches it. Free to implement, catastrophic to omit.
- **Trade-offs:** Adds friction to "just try another parameter" — but that's the point. Forces intentional hypothesis testing.
- **What remains protected:** Nothing is touched; this is purely additive.
- **Implementation impact:** WP-1b deliverable: `lib/evaluation.py` with DSR function and trial log append helper.

---

### D2-005 — Hypothesis pre-registration is the entry gate for any backtest

- **What changes:** No backtest is logged to `trial_log.jsonl` without a corresponding `HYPOTHESIS.md` file in `research/hypotheses/<id>/` containing: economic rationale, testable prediction, success criteria, and kill criteria — written *before* parameters are swept. Exploratory EDA lives in scratch notebooks and does not enter the trial log.
- **Why:** Separates "I'm learning the data" (fine) from "I'm testing an edge" (must be pre-registered). Without this split, p-hacking becomes the default.
- **Trade-offs:** Slight friction on starting a new test; huge clarity gain on what counts as evidence.
- **What remains protected:** All existing architectural docs.
- **Implementation impact:** WP-0 ships the `HYPOTHESIS.md` template in `research/templates/`; WP-2 is the first real use.

---

### D2-006 — Promotion gates are objective, numeric, and shared across all candidates

- **What changes:** Locked promotion gates for any strategy candidate going from research to shadow:
  1. Out-of-sample Sharpe ≥ 1.0 net of modeled costs.
  2. DSR > 1.0 at 95% confidence given actual trial count.
  3. Max drawdown ≤ 20% in any walk-forward fold.
  4. Parameter sensitivity: ±25% parameter shift keeps Sharpe within 70% of baseline.
  5. Cost drag ≤ 50% of gross PnL.
  6. No single 90-day window contributes > 60% of total PnL.
  7. ≤ 5 free parameters.
  8. Walk-forward efficiency (OOS/IS Sharpe ratio) > 0.5.
- **Why:** All eight gates are computable from the trial log and backtest output. They encode the specific failure modes that kill retail quant systems: overfitting, regime concentration, fragility, cost blindness.
- **Trade-offs:** Gates are strict enough that most candidates will fail. That is the intended behavior.
- **What remains protected:** D-0001 caps remain the live-trading ceiling on top of these research gates.
- **Implementation impact:** WP-1b ships a `check_promotion_gates(candidate) → pass/fail report` function. Gate thresholds are frozen in code and require a Decision Change entry to modify.

---

### D2-007 — Shadow mode is the sole bridge from research backtester to paper runtime

- **What changes:** A promoted candidate is implemented as a module conforming to the existing `SignalProvider` Protocol and plugged into the Phase 1 paper runtime in shadow mode — signals are generated and logged but not acted upon. Shadow runs for ≥ 14 calendar days. Parity check: during the shadow window, replay the same bars through the research backtester and require PnL deviation ≤ 10%, trade count deviation ≤ 5%. Only after shadow + parity passes does a candidate become eligible for Phase 3.
- **Why:** This is where research-backtester parity is verified — once per candidate, at the moment it matters — instead of being an architectural constraint we pay for continuously.
- **Trade-offs:** A candidate can pass research gates and still fail shadow parity; that rework cost is accepted.
- **What remains protected:** Paper runtime, SignalProvider Protocol (additive changes only and only via Decision Change entry), overlay, D-0001.
- **Implementation impact:** WP-3 defines the shadow adapter and parity report.

---

### D2-008 — Overlay-vs-existing-position semantics (P1-A addendum)

- **What changes:** BLOCK gates *new entries and risk-increasing deltas* only; existing positions are not auto-flattened. ALLOW_REDUCED(0.5) scales only the *increase component* of the target delta; reductions are always allowed at full size. Formalized as:
  ```
  effective_delta = delta_risk_increasing * multiplier
                  + delta_risk_reducing * 1.0
  ```
- **Why:** Auto-flattening on BLOCK turns the overlay into an execution actor, violating its role as a gate on new risk. The proposed semantics are the simplest to test, reason about, and audit.
- **Trade-offs:** During a BLOCK window, a losing existing position keeps running until the strategy itself exits. Acceptable because exits are always allowed.
- **What remains protected:** Overlay output set {ALLOW, ALLOW_REDUCED=0.5, BLOCK}, fail-open default, CPI/FOMC/NFP-only scope.
- **Implementation impact:** P1-A addendum entry in `docs/decisions.md` (landed in WP-0); unit test covering the four delta quadrants (increase-long, reduce-long, increase-short, reduce-short) under each overlay state, to be added when overlay logic is next touched.

---

### D2-009 — Token efficiency operating model

- **What changes:** Claude Pro subscription for interactive work; Anthropic API with prompt caching for automated queries; Advisor Strategy (Opus advisor + Sonnet executor) for architecture decisions and strategy evaluations; Haiku for log parsing and classification; API Batch for overnight analysis. No third-party routers (RouteLLM, LiteLLM, Ruflo) in Phase 2. Total monthly AI+data spend capped at ~$80.
- **Why:** Anthropic-native caching + Advisor Strategy delivers the cost savings third-party routers promise, without lock-in, configuration overhead, or the fraud risk confirmed in Ruflo's independent audit. Third-party routers become relevant only above ~$100/mo spend.
- **Trade-offs:** Claude-centric stack; no automatic multi-provider arbitrage. Accepted because the architectural cleanliness is worth more than marginal routing savings at our scale.
- **What remains protected:** Nothing touched; this is an operating model, not code.
- **Implementation impact:** Pinned `.claude/` config with Advisor Strategy enabled; prompt templates under `prompts/` with token counts measured weekly.

---

### D2-010 — Tool adoption locks

- **What changes:**
  - **ADOPT:** Graphify (repo knowledge graph for agent context), Superpowers/Obra (development methodology via Claude Code plugin), `SKILL.md` pattern for repeatable workflows, DuckDB for Parquet analytical queries, Polars for heavy DataFrame work, CCXT for exchange abstraction.
  - **REJECT:** Ruflo (audit-confirmed non-functional), Backtrader (abandoned), Qlib (no crypto), zipline-reloaded (no futures), LangGraph and CrewAI (overkill for Claude-only stack).
  - **DEFER:** NautilusTrader (Phase 3 if research-to-live parity becomes worth the migration), Jesse (if pandas backtester outgrows itself), Anthropic Managed Agents (wait for GA), Claude Code Router (only if spend crosses $100/mo).
- **Prospective D2-019 supersession:** the NautilusTrader `DEFER` clause above
  is retained as the historical D2-010 decision at the time. It no longer gates
  bounded non-capital N1/N2/N3 engineering/adoption proof on Phase 3, edge, GO,
  or paper/shadow. Proof and every ownership transfer still require separately
  authorized migration packages; economic activation remains candidate- and
  human-gated.
- **Why:** Each adoption has a direct, measurable impact on velocity or token cost. Each rejection either has no ROI or active negative ROI. Each deferral has a clear trigger condition.
- **Trade-offs:** Committing to a Claude-centric stack creates moderate Anthropic dependency. Accepted under D2-009's reasoning.
- **What remains protected:** No protected-boundary files are modified by any adopted tool.
- **Implementation impact:** Graphify and Superpowers enter at WP-1c. DuckDB and Polars enter at WP-1b alongside the backtester. CCXT optional.

---

### D2-011 — Agent roster and autonomy levels

- **What changes:** Four agent roles with explicit autonomy levels.
  - **Research Agent — "The Analyst":** HIGH autonomy. Independently researches papers, explores data, drafts `HYPOTHESIS.md` files. Never runs backtests autonomously, never touches exchange APIs, never modifies strategy code.
  - **Code Agent — "The Engineer":** MODERATE autonomy. Writes and tests code in feature branches. All merges require human review. Never modifies risk parameters, never pushes to main, never changes execution-layer code without explicit approval.
  - **Evaluation Agent — "The Auditor":** HIGH computational autonomy, ZERO decision authority. Runs the evaluation suite, computes DSR, checks gates, writes reports. Never overrides gate thresholds, never approves its own evaluations, never accesses live trading systems.
  - **Monitor Agent — "The Watchdog":** HIGH monitoring autonomy. Generates dashboards, sends alerts on threshold breaches. Never modifies positions, never changes strategy parameters, never disables the macro overlay.
- **Why:** Research hypothesis generation and evaluation are exactly the tasks where agent speed + human judgment composes well. Execution and risk parameters remain human-controlled because that is where mistakes are irrecoverable.
- **Trade-offs:** More agent output to review; more potential for agent-generated noise in `research/`. Mitigated by the pre-registration gate (D2-005) and the rule that agent PRs go into `draft/` subdirectories until a human promotes them.
- **What remains protected:** No agent ever modifies files under `src/overlay/`, `src/paper/ledger_state.py`, `docs/decisions.md`, `src/execution/interfaces.py`, or D-0001 parameters. Enforced by CODEOWNERS and PR review.
- **Implementation impact:** WP-1c ships `.claude/agents/` definitions for all four roles with their allowed-paths lists.

---

### D2-012 — OpenClaw reframed as a thin orchestration layer, not a meta-OS

- **What changes:** OpenClaw is no longer the central architecture concept. It becomes a thin layer: a set of `SKILL.md` files + Superpowers workflows + agent definitions that orchestrate the Continuous Improvement Cycle. It does not own state, does not mediate execution, and does not introduce new protocols. If removed tomorrow, the repo still functions — agents just run manually via Claude Code.
- **Why:** The "Maximum OpenClaw meta-OS" framing implied a large orchestration surface to build and maintain. Under research-first, that surface has no customers. A minimal orchestration layer delivers 90% of the value at 10% of the complexity.
- **Trade-offs:** Less impressive architectural story; less lock-in of workflow knowledge into a custom framework. Both accepted.
- **What remains protected:** All Phase 1 architecture docs and protected boundaries.
- **Implementation impact:** No new `src/orchestration/` tree, no new protocols, no new event types. OpenClaw's artifacts live in `.claude/skills/` and `.claude/workflows/` only.

---

### D2-013 — Supported timeframe set (locked)

- **What changes:** Locked timeframe set for Phase 2 research: **15m, 30m, 1h, 4h, 1d.** No sub-15m timeframes in Phase 2 (infrastructure costs outweigh research value for bar strategies; tick-level is Phase 3+).
- **Why:** 15m and 30m cover short-horizon mean-reversion and intraday momentum; 1h and 4h cover the strategies already in mind; 1d enables regime filters and walk-forward folds that need more history per fold. Each timeframe has a distinct, defensible use case.
- **Trade-offs:** Explicitly excluding sub-15m leaves microstructure strategies out of Phase 2. Accepted.
- **What remains protected:** Phase 1 paper runtime scheduler (1h bar-close). Additional timeframes become research-only inputs until a candidate is promoted to shadow.
- **Implementation impact:** Storage convention — one Parquet file per `(symbol, timeframe)`, same schema, UTC-aligned bar-close convention preserved. Catalog entries gain a `timeframe` field.

---

### D2-014 — Timeframe is a hypothesis-level choice, not an evaluation sweep

- **What changes:** Each `HYPOTHESIS.md` declares its primary timeframe and any confirmation timeframes *before* testing, as part of pre-registration. The evaluation pipeline does NOT automatically sweep a strategy across all timeframes looking for the best one.
- **Why:** Timeframe-as-free-parameter is the most common source of spurious backtest results in crypto. Locking timeframe at hypothesis-declaration time forces the researcher to state an economic reason for the choice and avoids the exact multiple-testing problem DSR is designed to punish.
- **Trade-offs:** A real edge that only manifests on an unexplored timeframe gets missed on the first pass. Acceptable — it can always be proposed as a separate, newly pre-registered hypothesis.
- **What remains protected:** DSR integrity, trial log integrity.
- **Implementation impact:** The `HYPOTHESIS.md` template has required `primary_timeframe` and optional `confirmation_timeframes` fields with required justification for each.

---

### D2-015 — Multi-timeframe confirmation pattern (when allowed)

- **What changes:** A strategy may use one **primary timeframe** (where signals are generated and trades executed) and up to two **confirmation timeframes** (where conditions must be true for the signal to fire). Confirmation timeframes must be **coarser** than the primary (e.g., 1h primary + 4h confirmation, never 1h primary + 15m confirmation). Finer timeframes used as inputs are feature engineering, not confirmation.
- **Why:** Using finer-grained timeframes for confirmation is a lookahead-bias trap — it imports information not available at the primary-timeframe bar close. Restricting confirmation to coarser bars eliminates this failure mode structurally.
- **Trade-offs:** Some valid multi-resolution feature designs require extra care to express as feature engineering rather than confirmation. Accepted.
- **What remains protected:** Bar-close determinism, UTC alignment, no lookahead.
- **Implementation impact:** Execution remains on the primary timeframe bar close. The Phase 1 paper runtime already supports this via the 1h bar-close scheduler; multi-timeframe extensions use the same scheduler with the primary timeframe as the trigger.

---

### D2-016 — Timeframe suitability is advisory output, not automatic gating

- **What changes:** The Research Agent may produce a timeframe-suitability brief for a strategy family — based on EDA of the historical dataset — that feeds hypothesis drafting. This brief is advisory. It does not pre-select timeframes and does not bypass the D2-014 pre-registration requirement.
- **Why:** Lets agents accelerate the expensive thinking step (which timeframe *might* carry signal for this strategy family) while keeping the decision in human hands.
- **Trade-offs:** Researchers still read and evaluate advisory briefs; not a zero-effort shortcut.
- **What remains protected:** D2-014 (hypothesis-level timeframe lock), D2-011 agent boundaries.
- **Implementation impact:** Research Agent outputs land under `research/briefs/` (advisory, not in trial log).

---

### D2-017 — Timeframe retirement rule

- **What changes:** If after two hypothesis cycles no candidate on a given timeframe survives the D2-006 promotion gates, that timeframe enters **cold storage** — still fetchable, not routinely tested — until a new hypothesis with explicit economic rationale proposes its return.
- **Why:** Prevents the team from burning cycles on timeframes that have empirically failed. Keeps attention focused on productive parts of the timeframe space.
- **Trade-offs:** A real edge at a cold-storage timeframe requires new justification to revisit; slight friction for a meaningful reason.
- **What remains protected:** Trial log integrity, DSR correctness (cold-storage trials still count in the cumulative trial count if revisited).
- **Implementation impact:** Cold-storage state tracked in `research/timeframe_status.md` with last-evaluated date and reason for cold storage.

---

## Protected boundaries (non-negotiable)

The following are never modified without an explicit Decision Change entry in `docs/decisions.md` locked by the Main Architecture chat:

1. OMS state machine semantics (`docs/architecture/oms_state_machine.md`).
2. Reconciliation truth rules (`docs/architecture/reconciliation_loop.md`).
3. Safe-mode flatten procedure (`docs/architecture/safe_mode_flatten.md`).
4. Kill-switch semantics.
5. D-0001 hard caps (risk per trade, daily/weekly loss, drawdown, turnover, leverage, margin reserve).
6. Overlay output set `{ALLOW, ALLOW_REDUCED=0.5, BLOCK}`, fail-open default, CPI/FOMC/NFP-only scope.
7. Paper ledger accounting math (`src/paper/ledger_state.py`).
8. Event log schema (`docs/architecture/event_log_schema.md`) — additive only.
9. Decision Change Protocol in `docs/decisions.md`.
10. No agent in the decision path — `compute_desired_position` and `evaluate_overlay` remain pure, deterministic, network-free at runtime.

---

## Operating model — chats

- **Main Architecture chat:** sole authority to lock or unlock decisions, approve baselines, issue execution briefs, accept report-backs. Outputs become repo commits via PR.
- **Architecture Karl:** Karl's implementation coordinator. Turns locked architecture into execution-ready work. Reviews and refines execution briefs. Coordinates Claude Code involvement. Cannot lock decisions.
- **Architecture Santi:** Santi's mirror role.
- **Execution chats:** one per work package. Receive a copy-paste brief from Main (or a brief refined by an Architect chat), implement in the repo via Claude Code, report back with evidence. No architectural decisions. Escalate to Main on any blocker requiring a decision.
- **Claude Code:** the implementation tool invoked inside Execution chats. Never invoked directly from Main.

**Rule:** a decision is only "locked" when it appears in the repo — in `docs/decisions.md`, this document, or equivalent. Chat agreement without a repo commit is not a decision.

---

## Execution sequence — Phase 2

1. **WP-0 — Baseline lock (docs only, no code).** Lands this document, the D2-008 addendum in `docs/decisions.md`, the `HYPOTHESIS.md` and `DECISION_RECORD.md` templates, and the Phase 2 pointers in onboarding docs. Tag: `phase2-baseline-locked`.
2. **WP-1a — Data foundation.** Full BTCUSDT history from `data.binance.vision` plus funding from Binance REST. Split into batches: Batch 1 (1h/4h OHLCV + funding), Batch 2 (15m, 30m, 1d + mark/index/premium index).
3. **WP-1b — Research workbench.** `lib/backtest.py`, `lib/evaluation.py` (with DSR and promotion-gate checker), `research/trial_log.jsonl` initialized. DuckDB and Polars added as dependencies.
4. **WP-1c — Agent and tooling setup.** Graphify index, Superpowers plugin, `.claude/agents/` definitions for the four roles, `.claude/skills/` scaffolding, Advisor Strategy configured, `prompts/` templates.
5. **WP-2 through WP-5b — Baseline hypothesis execution, audit, and bounded pipeline fixes.** H-001 through H-010 were tested and concluded NO-GO; the research pipeline was audited and bounded fixes were applied without changing existing overall NO-GO verdicts.
6. **PRE-WP-6a / WP-6a onward — Research machine foundations before Strategy v1 lock-in.** Candidate registry, experiment artifact schemas, bounded research-process infrastructure, and later bounded research-agent interfaces may be built before the next candidate-specific execution package.
7. **Later Phase 2 — Multi-candidate evaluation and promotion path.** Candidate discovery, testing, comparison, ranking, and human-gated promotion feed eventual Strategy v1 selection and shadow work when evidence justifies it.

**Phase 2 exit condition:** either a candidate has passed shadow and is ready for Phase 3 staged-live, or the candidate-agnostic research machine has produced enough structured evidence to support deliberate Strategy v1 selection, revision, discard, or pivot.

---

## What Phase 2 is NOT

- Not a protected-runtime infrastructure refinement program.
- Not immediate Strategy v1 lock-in.
- Not an uncontrolled platform migration or real-capital activation. Bounded
  adoption/proof of Prefect, Hermes, and Nautilus is allowed through separately
  authorized migration work packages. Nautilus N1/N2/N3 engineering proof may
  occur before edge/GO; economic activation remains candidate- and human-gated.
- Not a multi-venue effort.
- Not an agentic execution effort. Execution remains deterministic and human-controlled.
- Not scoped to paid data sources.
- Not scoped to sub-15m timeframes.

---

## Change log

- **Initial lock** — WP-0 baseline lock PR. Decisions D2-001 through D2-017 locked. D2-008 overlay addendum locked in `docs/decisions.md` in the same PR.
- **PRE-WP-6a direction clarification (D2-018)** — Candidate-agnostic research machine foundation work is explicitly in scope before Strategy v1 lock-in; protected deterministic execution core remains unchanged.
- **CPW-MIG-00 adoption-first clarification (D2-019)** — Prospectively
  supersedes the historical Nautilus Phase 3/GO/paper trigger for bounded
  non-capital N1/N2/N3 proof, without rewriting prior evidence or weakening any
  scientific, protected, human, live, or capital gate.
- **V2-00 bounded autonomous research clarification (D2-020)** — Prospectively
  replaces per-hypothesis approval with bounded-envelope authority only after
  Stage 5B activation and a valid Karl-approved envelope; V2-00 itself
  activates nothing and preserves scientific, candidate, protected, economic,
  live, and capital gates.

Any future change to this document requires a new Decision Change entry in `docs/decisions.md` and an updated change log line here.
