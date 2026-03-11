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

