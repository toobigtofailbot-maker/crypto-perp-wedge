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
