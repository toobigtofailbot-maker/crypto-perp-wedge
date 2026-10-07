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
| D2-023 | Search Policy Binding and Proposal-Wave Handoff |
| D2-024 | Extreme Hermes Autonomous Research Director |
| D2-025 | Extreme Hermes Capability Coverage and Orchestration Ownership |
| D2-026 | Scientific Autonomy Kernel Durable Authority and Storage |

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

### D2-023 — Search Policy Binding and Proposal-Wave Handoff

**Status:** LOCKED

**Decision ID:** D2-023

**Date:** 2026-10-06

**Scope:** Authoritative search-policy input and noncanonical active proposal-
wave recovery for the first V2-INTEGRATION-01B proof

**Approval:** Karl-authorized through `WP-V2-INTEGRATION-01B-ARCH-01`

**Controlling record:**
`docs/architecture/2026-10-search_policy_proposal_handoff_lock.md`

#### Decision

- A human/manual, strict CPW-owned `SearchPolicyBinding v1` supplies every
  authoritative scientific-policy field; Hermes, Prefect, and Optuna do not.
- The first 01B proof supports a brand-new campaign/search only. Parent and
  reason-for-change fields are null, and cumulative pre-search proposal and
  scientific-trial counts are fixed to zero.
- CPW alone builds the frozen `SearchContract` from the accepted intent,
  validated policy binding, and exact repo evidence, failing closed on missing
  or mismatched identity, policy, history, strategy, data, or holdout inputs.
- `ProposalWaveHandoff v1` is noncanonical active-wave state stored only under
  `.cpw/active/` through the safe CPW resolver. It is not canonical evidence,
  a Result Population, a result store, approval, or durable lineage.
- Recovery restores the exact finalized pre-wave Governor snapshot, reproduces
  exactly one recorded proposal wave, and requires equality of order, IDs,
  parameters, fingerprints, contract hash, and scientific denominator.
  Divergence fails closed.
- Prefect remains operational-only. Search Governor remains the sole
  scientific/search owner, and Optuna remains proposer-only behind it.
- 01B stops before runner execution, results, wave finalization, final holdout,
  candidate review, promotion, or canonical write.
- Durable cumulative scientific lineage remains deferred; the `.cpw` handoff
  cannot substitute for it.

#### Non-authority

D2-023 implements no code and grants no Stage 5B, autonomous scheduling,
runner, canonical-write, candidate/promotion, protected-runtime, risk,
paper/live, exchange/order, capital, or self-merge authority.

### D2-024 — Extreme Hermes Autonomous Research Director

**Status:** LOCKED

**Decision ID:** D2-024

**Date:** 2026-10-06

**Scope:** Extreme Hermes target architecture and roadmap supersession

**Approval:** Karl-approved through
`WP-EXTREME-HERMES-00-AUTONOMOUS-RESEARCH-DIRECTOR-ARCH-01`

**Controlling record:**
`docs/architecture/2026-10-extreme_hermes_autonomous_research_director.md`

#### Decision

Extreme Hermes is the owner-approved target generic intelligence/runtime,
always-on research director, and continuous-improvement brain for the
non-capital research factory. The controlling principle is broad capability
inside an externally isolated research sandbox and narrow authority at CPW,
scientific, protected-runtime, and economic gateways.

After Stage 5B is implemented, validated, explicitly activated, and bound to a
valid Karl-approved immutable envelope, Hermes may continuously direct ordinary
legal in-envelope research without separate per-job approval. CPW remains
authoritative for scientific truth, durable lineage, holdout state, Search
Governor legality, evidence, and canonical semantics. Humans retain envelope
and scientific-policy changes, candidate promotion, protected recovery/risk,
paper/live, credentials, capital allocation, and live activation.

#### Proof-only and permanent boundaries

The current 01A one-shot, fixed-14-tool, Project-Evidence-only posture and its
disabled browser/web, terminal/code/files, memory/session-search, skills,
delegation, cron, and successor-research capabilities are a safety/control
proof baseline, not the permanent architecture. They remain disabled until
separately proven and authorized.

Hermes may never unilaterally manufacture scientific truth, turn FAIL into
PASS, erase or reset scientific history, refresh a contaminated holdout,
bypass Governor budgets/legality, redefine scientific/gate policy, promote a
candidate, alter protected risk/OMS/reconciliation/safe-mode/kill-switch
authority, hold unrestricted live/capital credentials, authorize live trading,
or allocate capital.

#### Prospective supersession and roadmap

D2-019 ownership remains intact. D2-020's envelope, Stage 5B, lineage,
holdout, fail-closed, and economic boundaries remain intact, while its
sole-future-lock statement and older sequence are prospectively superseded.
D2-022/01A controls remain valid proof and fallback controls rather than the
permanent capability ceiling. D2-023's policy, contract, Governor, identity,
replay, and noncanonical-state primitives remain useful, while its manual,
new-campaign-only, zero-history constraints are temporary first-proof limits
to be replaced by the autonomy kernel.

The controlling sequence is `EXTREME-HERMES-01` isolated sandbox,
`V2-AUTONOMY-KERNEL-01`, `V2-RESEARCH-FACTORY-LOOP-01`,
`EXTREME-HERMES-02` Stage 5B/always-on activation, and later
`EXTREME-HERMES-03` non-protected lab engineering. Future work must not default
to one permission per package absent a concrete security or compatibility
dependency.

#### Version policy and non-activation

D2-024 selects no replacement Hermes version. `EXTREME-HERMES-01` must freshly
verify official releases/tags, security, compatibility, image/digest,
capabilities, isolation, and rollback immediately before selecting a canary
pin. D2-024 changes documentation and architecture only; it enables no tool,
upgrade, schedule, autonomous research, Stage 5B, code path, protected runtime,
paper/live action, credential, or capital use.

### D2-025 — Extreme Hermes Capability Coverage and Orchestration Ownership

**Status:** LOCKED

**Decision ID:** D2-025

**Date:** 2026-10-06

**Scope:** Extreme Hermes capability completeness and orchestration ownership

**Approval:** Karl-authorized through
`WP-EXTREME-HERMES-D2-025-CAPABILITY-COVERAGE-01`

**Controlling addendum:**
`docs/architecture/2026-10-extreme_hermes_capability_coverage_and_orchestration_ownership.md`

#### Decision

- The full useful Hermes capability set remains on the roadmap; omission from
  the first canary is sequencing, not silent rejection.
- Persistent Bot Mode is adopted as a research-organization primitive, with
  ephemeral flat delegation as a complementary bounded mechanism.
- Browser research is allowed, but model-written browser execution must be
  isolated from the credential-bearing director environment, director secrets,
  private/LAN/metadata/control-plane networks except an explicitly reviewed
  narrow exception, and protected repo/runtime write surfaces. Live effective
  behavior, not configuration labels, is the acceptance proof.
- Specialist Bots receive independently reviewed minimum credentials;
  automatic director-profile credential copying/cloning is disabled. Bot
  creation and delegated children cannot silently widen credential access.
- Persistent specialist Bots must operate through supported
  CLI/service/gateway profile mechanisms on the research VPS without an
  interactive Desktop session. Desktop Bot Mode is optional operator UI, not
  an autonomous-factory runtime dependency.
- Hermes cron/routines own intelligence wake-ups. Prefect owns durable
  scientific workflow execution, workers, queues, operational retries, and
  durable flow/run state.
- Plugins are privileged and must be reviewed, pinned where possible,
  allowlisted, provenance-recorded, and prevented from arbitrary self-install
  or self-update.
- MCP expands beyond Project-Evidence only through curated, reviewed servers,
  explicit tool filters, explicit credentials, and live effective-tool
  verification. Authority-bearing CPW interfaces remain narrow and fail-closed.
- Hermes, Bot, session-search, skill, and optional external memory remain
  non-authoritative. Research Memory remains a non-authoritative retrieval and
  deduplication index. CPW durable lineage remains authoritative scientific
  truth.
- Self-improving skills are adopted under isolated storage, controlled writes,
  audit, rollback, and capability-containment proof.
- Computer Use remains a conditional later capability in a dedicated reviewed
  GUI sandbox; it is not part of the first F1/F2 canary and is not forgotten.
- Deeper/nested multi-agent orchestration remains conditional on measured value
  and explicit depth, concurrency, cost, runtime, containment, visibility, and
  auditability bounds.
- Karl's later owner decision removes external independent review as a
  mandatory prerequisite for the `EXTREME-HERMES-01` F1/F2 canary. Side 21
  security review plus explicit physical canary acceptance is the controlling
  pre-implementation gate. No security control is removed.
- External independent security challenge is deferred to the pre-Stage-5B /
  `EXTREME-HERMES-02` gate, or earlier if Side 21 detects material unresolved
  security uncertainty, unless Karl explicitly changes that later gate.
- Hermes `v2026.9.24 / v0.21.5` is not acceptable unchanged because it lacks
  the required upstream tool-scope fix associated with issue `#121089` and
  commit `59559b858fb1a4578f51029112099462a431c3f1`. The selected canary release
  must include that fix or an explicitly reviewed equivalent, and final version
  selection requires a fresh upstream check in the implementation package.

#### Non-authority

D2-025 is an addendum to D2-024 and does not weaken D2-024's permanent
scientific, protected-runtime, or economic boundaries. Changing the F1/F2
review authority weakens no physical security control. D2-025 activates no
Hermes upgrade, tool, Bot, plugin, MCP, routine, Computer Use, Stage 5B,
autonomous scientific execution, code/runtime path, paper/live action,
credential, exchange/order authority, or capital use.

### D2-026 — Scientific Autonomy Kernel Durable Authority and Storage

**Status:** LOCKED

**Decision ID:** D2-026

**Date:** 2026-10-07

**Scope:** T0 docs-only scientific autonomy kernel authority/storage lock

**Approval:** Karl-approved through `WP-V2-AUTONOMY-KERNEL-ARCH-01`

**Exact base:** `200276fd4407e4a13a912a6b475ab9ab38a1de70`

**Controlling record:**
`docs/architecture/2026-10-v2_autonomy_kernel_durable_authority.md`

#### Decision

- The future production envelope is a human-owned CPW repo artifact under
  `research/autonomy/envelopes/`, with strict schema family under
  `research/schemas/`. It is versioned, immutable, content-hash bound, and binds
  exact repo identity and explicit human/Karl approval metadata. Automation
  may read/validate but cannot create, edit, expand, reinterpret, replace, or
  self-authorize it. Revocation/replacement creates explicit new human-controlled
  state. No schema or real envelope is created here; the later kernel may use
  test fixtures only. Production operation requires later Stage 5B activation.
- CPW's future autonomy kernel owns a separate logical PostgreSQL scientific-
  authority database, separate migrations, and separate write role. The same
  physical server/cluster may be reused. Recommended database/role name family
  is `cpw_research_authority`, schema family `research_authority`; deployment
  credentials/host/port remain environment configuration, not scientific
  identity. Research Memory rebuild/deletion cannot reset scientific history;
  Hermes, Prefect, and broker state cannot own scientific lineage.
- Durable state combines transactional current authority with append-only
  audit/event history, deterministic IDs/hashes, DB uniqueness/check constraints,
  atomic transitions, and fail-closed idempotency/conflicts. It covers envelope
  binding, campaign/search/trial lineage, cumulative proposal/trial accounting,
  exact evidence/result references/hashes, holdout, contamination domains/ancestry,
  and authority audit. No universal event-sourcing framework is required.
- The store is not a second performance/result warehouse. Existing/future CPW
  evidence and Result Population surfaces retain scientific payload semantics;
  no candidate or promotion authority is created.
- `.cpw/active` remains active/provisional only. In-flight recovery state must
  bind exact authoritative campaign/search/contract/lineage identity. Deletion
  or recreation of `.cpw` cannot reset history; file presence creates no authority.
- CPW alone derives a frozen `SearchContract` from accepted
  `BoundedResearchIntent`, exact valid Karl-approved envelope, exact repo/evidence
  identity, and durable authoritative lineage. It binds envelope ID/version/hash,
  contamination domain, lineage state/version/hash, and cumulative proposal/trial
  counts. Hermes/Prefect/Optuna cannot supply or override counts, remaining budget,
  holdout freshness, envelope policy, scientific retry, or search-space widening.
  Caller-supplied cumulative history is not production continuation.
- A successor requires exact campaign/parent-search/parent-lineage identity,
  reason for change, authoritative cumulative history, immutable-envelope
  revalidation, and a new frozen contract. Rename/restart/new operational ID
  cannot reset budget; domains cannot widen beyond the envelope. Search Governor
  retains search legality/proposal/accounting/scientific-trial identity; Optuna
  remains proposal-only.
- Final holdout is unavailable to adaptive search. Informative exposure is
  durable; escaped informative results consume it across influenced downstream
  lineage in the same contamination domain. New hypothesis/search/branch/session/
  run/memory IDs do not restore freshness. Exact retry avoids another exposure
  only if no informative result escaped; missing contamination edges do not
  prove isolation. The first kernel has no automatic strict-isolation declaration
  or freshness-restoration path. Any isolation exemption needs a separate
  reviewed architecture/authority decision.
- The envelope defines ceilings; the durable authority store owns atomic
  campaign usage/reservation. Search-local budgets fit remaining envelope/campaign
  budget, concurrent starts cannot oversubscribe, and same-trial software retries
  do not create independent trials. Successors/restarts/new IDs cannot reset
  totals. Expansion requires human envelope replacement/expansion.
- Ownership remains explicit: Karl-approved envelope owns scope/budget/policy;
  CPW kernel owns validation/binding, durable lineage, and holdout contamination;
  Governor owns search legality and scientific identity; Optuna proposes; Hermes
  reasons/proposes next actions; Prefect owns operational flows/runs/retries;
  Research Memory retrieves/deduplicates without authority; CPW evidence surfaces
  own payloads; humans retain promotion and existing protected owners retain
  runtime/OMS/reconciliation/hard risk.

#### Dependency and non-activation

D2-020's previously deferred storage/ownership choice is closed on accepted
merge; D2-021 identity, D2-022 ownership, D2-023 existing proof restrictions,
and D2-024/D2-025 capability/roadmap boundaries remain intact. Side 22 may draft
`V2-AUTONOMY-KERNEL-01` only after accepted merge and refreshed exact-head truth.
That implementation is not executable merely because this decision exists.

This decision implements no database, schema, production envelope, or kernel;
activates no Stage 5B; schedules no research; allows no Hermes scientific
experiment execution; calls no runner/backtester; performs no WFO/OOS,
robustness, or Monte Carlo; writes no Result Population; promotes no candidate;
changes no protected runtime/risk/OMS/reconciliation/overlay/safe-mode control;
enables no paper/live or exchange/order; and allocates no capital. No scientific
threshold or existing gate semantics change.
