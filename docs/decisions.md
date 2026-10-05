# Decisions Log

## Template (copy for each decision)

* Date (UTC):
* Decision:
* Options considered:
* Why:
* What would change my mind:





\# Decisions Log



\## Decision Change Protocol (Binding)

A decision in this file is binding once marked \*\*LOCKED\*\*. Any change requires:

\- New entry: \*\*Decision Change\*\* referencing the original Decision ID

\- What changed (old → new)

\- Why (evidence / risk / operational reason)

\- Trigger conditions (what must happen for change to be allowed)

\- Effective date

\- Backtest/Paper validation plan if it impacts risk/execution



---
## P1-A — Context Overlay Decision (LOCKED)

**Status:** LOCKED  
**Scope:** Phase-1 Paper (deterministic, non-agentic)  
**Decision ID:** P1-A-OVERLAY-LOCK  
**Date:** 2026-03-09  

### Output Contract (binding)
The overlay MUST emit exactly one of:
- `ALLOW` (size_multiplier = 1.0)
- `ALLOW_REDUCED` (size_multiplier = 0.5)   <-- binding
- `BLOCK` (size_multiplier = 0.0)

**Binding rule:** `ALLOW_REDUCED` is ALWAYS exactly **0.5x**. No other reduced levels are permitted.

### Eligible macro triggers (only)
- CPI
- FOMC
- NFP

### Macro windows (binding)
- Only macro windows based on the events above are allowed.
- No additional event types and no dynamic/learned widening.

### Fail-open (non-negotiable)
If macro context is missing, stale, or API fails:
- overlay MUST return `ALLOW` (size_multiplier = 1.0)
- and set `context_missing = true` in the emitted audit record.

### Change protocol
Any modification to overlay semantics requires:
- a new decision entry in this file
- explicit review/approval by Main Architecture Chat
- version bump of overlay rules (no silent changes)
---

\## D-0001 — Phase-1 Defaults (LOCKED)

\*\*Date:\*\* 2026-03-01  

\*\*Status:\*\* LOCKED  

\*\*Owner:\*\* Karl  

\*\*Scope:\*\* Phase-1 (BTC-only wedge) — applies to all backtests, paper, and live runs unless explicitly changed via Decision Change Protocol.



\### Decision

Lock the Phase-1 default risk/execution policies and parameters (percent-based).



\### Locked Defaults (all % unless noted)

\*\*Capital / Margin\*\*

\- \*\*Equity Reserve:\*\* 40% (not used as margin)

\- \*\*Max Margin Usage:\*\* Target 30% Equity, Hard Cap 40% Equity



\*\*Leverage / Notional Exposure (Policy)\*\*

\- \*\*Target Notional/Equity:\*\* 1.5x–3.0x

\- \*\*Hard Notional/Equity Cap:\*\* 4.0x

\- \*\*Note:\*\* Leverage capability remains flexible in code; policy caps are binding.



\*\*Risk per Trade\*\*

\- \*\*Risk per Trade (loss at stop, incl. conservative fees + slippage):\*\*

&nbsp; - Target 0.75% Equity

&nbsp; - Hard Cap 1.25% Equity



\*\*Loss Limits / Kill-Switch\*\*

\- \*\*Daily Loss Limit (Hard Kill):\*\* 2.5% Equity

\- \*\*Weekly Loss Limit (Halt + Review):\*\* 6% Equity

\- \*\*Peak-to-Trough Drawdown (Hard Kill):\*\* 7% Equity



\*\*Turnover Caps\*\*

\- \*\*Daily Notional Turnover:\*\* ≤ 150% Equity

\- \*\*Hard Cap:\*\* 250% Equity



\*\*Execution Timing\*\*

\- \*\*Signal evaluation:\*\* strictly on \*\*1h bar close\*\*

\- \*\*4h timeframe:\*\* regime filter only

\- \*\*Intra-bar:\*\* protective orders only (no intra-bar signal trading)



\*\*Order Policy\*\*

\- \*\*Default:\*\* marketable limit orders + defined retry / cancel-if-stale policy

\- \*\*Emergency:\*\* reduce-only + aggressive marketable limit; market allowed as last resort



\*\*Universe\*\*

\- \*\*BTC only\*\* (Binance USDT-M Perpetual)



\*\*Funding in Backtests\*\*

\- Funding PnL is booked as \*\*realized cashflow at exact funding event timestamps\*\* (not bar-aggregated).



\### Rationale (short)

\- Small-cap survival first; prevent liquidation/fee-drag via tight policy caps.

\- Deterministic bar-close workflow reduces noise/turnover and operational fragility.

\- Funding modeled conservatively and timestamp-correct to avoid backtest fantasy.



\### Change Triggers (examples)

Changes allowed only if one of these is met and validated:

\- Paper trading shows stable performance for multiple weeks with clean ops logs.

\- Verified evidence that policy caps materially prevent fills/execution under normal conditions.

\- Data fidelity upgrade enables safer intra-bar logic (e.g., reliable 1m/tick + fill model).


## P1-C — Macro Window Policy v1 (LOCKED) (Addendum to P1-A)

**Status:** LOCKED  
**Decision ID:** P1-C-MACRO-POLICY-V1  
**Date:** 2026-03-10  

### Per-event permission (binding)
- FOMC: `BLOCK`
- CPI: `ALLOW_REDUCED`
- NFP: `ALLOW_REDUCED`

### Windows (UTC relative)
- FOMC: pre `30` minutes, post `150` minutes
- CPI: pre `30` minutes, post `60` minutes
- NFP: pre `30` minutes, post `60` minutes

### Merge rule (binding)
When windows overlap, apply strict severity ordering: `BLOCK` > `ALLOW_REDUCED` > `ALLOW`; merge/sort behavior MUST be deterministic.

### Fail-open (binding)
If calendar/snapshot context is missing, empty, or invalid, emit exactly one full-range `ALLOW` window with `context_missing=true`. Change protocol: new Decision Change entry required.

---

## D2-008 — Overlay Semantics Addendum (LOCKED)

**Status:** LOCKED  
**Decision ID:** D2-008  
**Date:** 2026-04-11  
**Scope:** Phase 2 (addendum to P1-A)

### Semantics (binding)

BLOCK gates only new entries and risk-increasing deltas. ALLOW_REDUCED(0.5) scales only the increase component. Reductions always allowed at full size.

**Formula:**
```
effective_delta = delta_risk_increasing * multiplier + delta_risk_reducing * 1.0
```

### Change protocol

Any modification requires a new decision entry in this file with explicit Main Architecture chat approval.

---

## Phase 2 Locked Decisions

The following decisions are locked for Phase 2. Full details in `docs/onboarding/PHASE2_BASELINE.md`.

| ID | Summary |
|----|---------|
| D2-001 | Research-first, infrastructure-second |
| D2-002 | Lightweight pandas/numpy backtester (~300 lines) |
| D2-003 | Free Binance data only |
| D2-004 | DSR + trial_log.jsonl overfitting firewall |
| D2-005 | Hypothesis pre-registration mandatory |
| D2-006 | Promotion gates locked |
| D2-007 | Shadow mode bridge (≥14 days + parity check) |
| D2-008 | Overlay semantics addendum (see above) |
| D2-009 | Token efficiency operating model |
| D2-010 | Tool adoption/rejection list |
| D2-011 | Agent roster with autonomy levels |
| D2-012 | OpenClaw reframed as thin layer |
| D2-013 | Supported timeframes (15m, 30m, 1h, 4h, 1d) |
| D2-014 | Timeframe is hypothesis-level choice |
| D2-015 | Multi-timeframe confirmation rules |
| D2-016 | Research Agent advisory briefs only |
| D2-017 | Cold storage for failed timeframes |
| D2-018 | Decision Change: Phase 2 research machine direction clarification |
| D2-019 | Decision Change: Adoption-first infrastructure buildability and Nautilus proof sequencing |
| D2-020 | Decision Change: Bounded Autonomous Research Envelope and V2 Operating Roadmap |
| D2-021 | Five-Timeframe Canonical Base and Feature Parent Identity |
| D2-022 | Hermes Bounded Research Handoff and SearchContract Ownership |

### D2-003A — Irreparable official-source gap policy

A bar is classified 'irreparable' if it is missing from all three of:
(a) data.binance.vision monthly archive, (b) data.binance.vision historical
daily archive, (c) Binance REST official endpoint. Irreparable bars are
recorded in data/irreparable_gaps.json with stream, interval, UTC range,
bar count, and the UTC date of the verification pass. Produced Parquet
files remain gap-flagged (a boolean column or sidecar manifest) but are
accepted by the validator provided all of the following bounded tolerances
hold per (stream, interval) file:

* total irreparable bars <= 0.01% of expected bars in the declared range
* no single contiguous irreparable window exceeds 8 bars
* no irreparable window falls within the most recent 90 days of the
  declared range
  Files breaching any tolerance FAIL the validator and block the PR.
  Downstream research code (WP-1b onward) MUST consult the gap manifest and
  either skip affected bars or explicitly handle them; silent interpolation
  is forbidden.
  Rationale: preserves D2-003 (free sources only) while preventing indefinite
  blockage on a category of gaps that is structurally bounded and documented.
  Change protocol: modifying thresholds requires a new Decision Change
  entry.

### D2-018 — Decision Change: Phase 2 research machine direction clarification

**Status:** LOCKED
**Decision ID:** D2-018
**Date:** 2026-04-17
**Scope:** Phase 2 direction clarification; updates `docs/onboarding/PHASE2_BASELINE.md`
**References:** D2-001, D2-004, D2-005, D2-006, D2-007, D2-011, D2-012, D2-017

#### What changed (old -> new)

Old: Phase 2 could be read as candidate-first, with research infrastructure deferred until after Strategy v1 selection.

New: Phase 2 remains research-first, but candidate-agnostic research machine foundation work is explicitly in scope before Strategy v1 lock-in when it improves disciplined candidate discovery, evidence collection, testing, comparison, ranking, or human-gated promotion.

#### Authorized by this change

- Candidate registry foundation work.
- Experiment artifact schemas for plans, reports, evidence, and decisions.
- Bounded research-process foundation work for systematic multi-candidate research.
- Later bounded research automation above the protected deterministic execution core.

#### What remains protected

- OMS truth.
- Reconciliation truth.
- Kill-switch semantics.
- D-0001 hard caps.
- Bounded overlay semantics.
- Paper ledger accounting and execution-critical runtime behavior.
- No agentic execution, autonomous risk changes, or automated promotion authority.

#### What this does not authorize

- Strategy v1 lock-in now.
- H-011 execution or pre-registration now.
- Runtime, OMS, reconciliation, overlay, or risk-cap changes.
- Automatic promotion from research to shadow or live.
- Changes to D2-006 promotion gate thresholds.

#### Why

H-001 through H-010 produced no promotable candidate, and WP-5a/WP-5b established an audited and bounded research instrument. The repo now needs reusable structure for candidate discovery, evidence capture, comparison, and later human-gated promotion before more candidate-specific execution work becomes the default next step.

#### Trigger conditions

This change applies only to docs and later explicitly scoped research-machine foundation packages. Any package that touches protected execution, risk, OMS, reconciliation, overlay semantics, promotion thresholds, trial logs, hypotheses, decisions, or runtime behavior still requires its own explicit authorization.

#### Effective date

2026-04-17

#### Backtest / paper validation plan

None. This is a docs-only Phase 2 direction clarification and does not affect risk, execution, backtest results, paper runtime behavior, or live behavior.

### D2-019 — Decision Change: Adoption-first infrastructure buildability and Nautilus proof sequencing

**Status:** LOCKED
**Decision ID:** D2-019
**Date:** 2026-09-23
**Scope:** Phase 2 adoption-first architecture clarification; updates
`docs/onboarding/PHASE2_BASELINE.md`
**Approval:** Karl/Main-approved through CPW-MIG-00
**References:** D2-001, D2-002, D2-007, D2-010, D2-018;
`docs/decisions/ENGINEERING_VS_STRATEGY_READINESS.md`;
`docs/architecture/2026-09-adoption_first_migration_architecture_freeze.md`

#### What changed (old -> new)

Old: Phase 2 deferred NautilusTrader until Phase 3 or until research-to-live,
GO, or paper/shadow conditions were met. That wording could be read as
prohibiting simulator, paper, or execution-infrastructure adoption proof before
a genuine strategy candidate existed.

New: infrastructure buildability is not candidate-gated; economic activation
is. Separately scoped packages may conduct bounded non-capital Nautilus N1
research/simulation proof, N2 paper/accounting/restart proof, and N3 Binance
USD-M/order/reconnect proof before genuine edge or GO exists. Proof may use
approved fixtures, synthetic or designated non-winning engineering material,
and authorized offline, demo, testnet, or other non-capital environments.

Nautilus gains no canonical research, paper/accounting, exchange, or execution
authority merely from this decision. Each ownership transfer requires its
bounded proof and a later authorized migration package. Genuine candidate
performance claims, candidate-specific paper/shadow conclusions, promotion,
candidate live-readiness conclusions, live deployment, and real capital remain
subject to existing scientific and human authority.

#### Boundaries retained

- The accepted CPW/Nautilus reconciliation split remains unchanged: Nautilus
  may own ordinary mechanics after proof; CPW retains trust, ambiguity,
  fail-closed escalation, safe-flatten, duplicate-economic-effect, and required
  human recovery policy.
- Canonical authority remains engine-neutral and CPW-controlled.
- Hard risk, bounded overlay semantics, OMS truth, reconciliation safety and
  economic policy, paper ledger math, human approvals, live gates, and capital
  gates are unchanged.
- No runtime, paper/live, code, dependency, schema, query, data, or canonical
  artifact change occurs in D2-019, and no framework is installed.

#### Why

Karl/Main approved the adoption-first migration architecture in CPW-MIG-00.
This entry reconciles that approved direction with the locked Phase 2 baseline
through its binding Decision Change protocol while preserving the historical
D2-010 decision text and every economic/protected boundary.

#### Trigger conditions

D2-019 changes planning eligibility only. N1, N2, N3, ownership transfer,
retirement, and activation each require a separately authorized package and
their applicable proof and human gates.

#### Effective date

2026-09-23

#### Backtest / paper validation plan

None for this decision record. It is documentation/process architecture only.
Later N1/N2/N3 packages carry their own bounded validation.

### D2-020 — Bounded Autonomous Research Envelope and V2 Operating Roadmap

**Status:** LOCKED

**Decision ID:** D2-020

**Date:** 2026-10-03

**Scope:** V2 bounded autonomous research architecture and future roadmap

**Approval:** Karl/Main-approved through V2-00

**Controlling record:**
`docs/architecture/2026-10-bounded_autonomous_research_v2_architecture.md`

#### What changed (old -> new)

Old: current authority required per-hypothesis human approval, made Research
Agent/lab roles advisory-only, held initial Spec/variant/sweep execution behind
separate human authorization, and kept edge-search and autonomous scheduling
off. Broad HG-1/HG-4/HG-5 and permanent-human-gate wording could be read as
forbidding all autonomous research lifecycle decisions.

New: Karl approves a versioned, immutable, hash-bound bounded research
envelope. After Stage 5B is implemented, validated, explicitly activated, and
a valid Karl-approved envelope exists, the factory may create, run, evaluate,
stop, disposition, and follow up legal in-envelope research without separate
per-hypothesis approval. CPW deterministic machinery remains scientific
authority, and humans retain promotion, economic, protected-runtime, live, and
capital authority.

#### Effective date and default-off rule

This is an architecture authority change, not an autonomy activation event.
Per-hypothesis approval and all current autonomy restrictions remain
operationally effective until Stage 5B is implemented, validated, explicitly
activated, and a valid Karl-approved bounded research envelope exists. Merging
V2-00 does not activate Hermes research execution, Prefect autonomous
scheduling, edge-search, or any factory runtime behavior.

#### Prospectively superseded only where conflicting

- D2-011 agent-autonomy restrictions;
- D2-016 human-choice wording where it conflicts with legal in-envelope
  timeframe selection under D2-014 preregistration;
- permanent per-hypothesis approval and generic research go/no-go wording;
- HG-1/HG-4/HG-5 only insofar as they prohibit autonomous research lifecycle
  behavior inside a valid envelope after Stage 5B activation;
- initial-maturity per-Spec, per-variant, and per-sweep authorization;
- no-edge-search and autonomous scheduler/scout default-off posture only after
  Stage 5B activation and while a valid Karl-approved envelope exists.

#### Explicitly preserved

D2-005 preregistration, D2-006 scientific promotion gates, D2-007
shadow/parity, D2-014 timeframe discipline, denominator/trial accounting,
WFO/OOS/leakage, robustness and multiple-testing, candidate promotion,
paper/live gates, OMS/reconciliation/safe-mode/kill-switch truth, D-0001 hard
risk caps, overlay bounds, paper accounting, canonical evidence/writers,
exchange/order/runtime authority, and capital authority remain unchanged.
D2-019 and CPW-MIG-00 continue to control generic ownership and adoption-first
migration.

#### Scientific lineage, holdout, and disposition boundary

CPW must own the future durable authoritative scientific lineage, cumulative
trial/search history, final-holdout state, and information-contamination
ancestry. Research Memory may mirror and index that history but cannot define,
erase, or reset it. An exposed final holdout is consumed across every influenced
downstream lineage in its information-contamination domain unless strict
information isolation is proven; renaming or creating another operational ID
does not restore freshness. Automated research dispositions remain distinct
from candidate rejection, promotion, readiness, or economic decisions.

#### Stop and recovery boundary

The factory owns automatic fail-closed research stop. Only envelope-approved,
bounded exact-input/same-trial recovery may proceed automatically. Envelope,
budget, scientific-policy, protected-boundary, risk, paper/live, exchange, and
capital recovery or expansion remains human-controlled where existing policy
requires it.

#### Roadmap effect

V2-00 is the sole Stage-5A-equivalent authority lock. The next implementation
lane after merge is five-timeframe/data-feature completion, followed by Prefect
consumer orchestration, Hermes/Research Memory/Search Governor integration,
product integration, Stage 5B activation, and VPS acceptance. After always-on
acceptance, serialized Stage 8A+ engineering and Stage 8R continuous
non-capital research operate in parallel.

#### Backtest / paper validation plan

None. V2-00 is documentation/governance only and changes no implementation,
runtime, paper/live, risk, or capital behavior.

### D2-021 — Five-Timeframe Canonical Base and Feature Parent Identity

**Status:** LOCKED

**Decision ID:** D2-021

**Date:** 2026-10-04

**Scope:** Canonical primary-timeframe source identity and future row-local
feature parent identity

**Approval:** Karl/Main-approved through
`WP-FT-01-CANONICAL-30M-1H-LINEAGE-RUNNER-ROUTES-01`

#### Decision

- `15m` uses the existing canonical D4 base.
- `30m` uses a deterministic canonical base derived from the exact canonical
  D4 15m parent.
- `1h` uses a deterministic canonical base derived from the exact canonical D4
  15m parent.
- `4h` uses the existing D4-derived canonical base.
- `1d` keeps the existing direct canonical 1d base unchanged.
- Future taker features derive row-locally from the exact canonical base
  selected as the primary timeframe.
- Feature parent identity equals execution-base identity.
- Existing direct 30m and 1h Parquets are diagnostic reconciliation evidence
  only and never a second authority.
- Diagnostic disagreement does not create dual authority. No tolerance,
  repair, splicing, averaging, or source switching is authorized.
- Child ratios are never averaged.
- The existing canonical 1d route is not replaced.

#### Non-authority and package boundary

D2-021 does not implement FT-02, activate autonomy, change promotion or
timeframe policy, or create runtime, paper, live, risk, capital, or economic
authority. It changes no protected execution boundary.

### D2-022 — Hermes Bounded Research Handoff and SearchContract Ownership

**Status:** LOCKED

**Decision ID:** D2-022

**Date:** 2026-10-05

**Scope:** Hermes operational handoff and CPW `SearchContract` ownership

**Approval:** Karl-authorized through
`WP-V2-INTEGRATION-01-ARCHITECTURE-LOCK-01`

**Controlling record:**
`docs/architecture/2026-10-hermes_research_integration_handoff_lock.md`

#### Decision

- The first proof uses a CPW-owned fixed-command host-side invocation adapter,
  under Prefect operational control, to one non-interactive turn in the
  existing pinned Hermes container. The adapter is narrow: it grants no
  caller-selectable command, generic Docker/subprocess authority, repository
  mount, Docker socket, or new Hermes API.
- `BoundedResearchIntent v1` is the strict, non-authoritative typed handoff.
  Hermes supplies untrusted reasoning; Project-Evidence / CPW re-resolves
  evidence, validates the envelope, normalizes the exact `hypothesis-v1`
  fingerprint, and performs read-only exact Research Memory deduplication.
- CPW alone may deterministically convert an accepted intent plus explicit
  scientific policy, evidence, and lineage into a frozen `SearchContract`.
- Search Governor alone owns search legality, scientific IDs and denominator,
  proposal/trial budgets, duplicate policy, final-holdout isolation, retry
  meaning, and bounded snapshot/restore. Optuna remains proposer-only behind
  the Governor; Prefect remains operational-only.
- H2/H2.5 proposal and prepared-payload surfaces remain inert and cannot become
  integration inputs or automatic consumer messages.
- V2-INTEGRATION-01A and 01B are separate future implementation packages. 01A
  stops before Governor/Optuna; 01B remains separately gated and stops before
  real product-runner execution.

#### Non-authority

D2-022 implements no code and activates no Stage 5B, autonomous research,
schedule/trigger, runner, canonical write, promotion, protected runtime,
paper/live, exchange/order, or capital authority.
