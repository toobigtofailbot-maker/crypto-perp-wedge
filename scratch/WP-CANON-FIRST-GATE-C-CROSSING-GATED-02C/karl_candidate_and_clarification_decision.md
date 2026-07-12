# Karl candidate and clarification decision — Phase A

## Current candidate inventory

| Draft | Title | Submitter / provenance | Sample status | Blocker | Review | Eligibility | Duplicate posture | Recommendation |
|---|---|---|---|---|---|---|---|---|
| `AIDRAFT-8DEEE634E62CD560` | EMA momentum continuation | `codex-sample`; `fake-rule-v1`; `fake_offline`; `deterministic_fake` | Explicit deterministic fake/sample despite `fabricated=false` | No validated draft adapter exists for this exact primitive family | Unreviewed; 0 events | `needs_clarification` (advisory only) | No normalized match, but material differentiation from existing momentum/trend work is unresolved | Not usable unless explicitly authorized as a canonical canary and fully clarified |

## Existing-only sample warning

`AIDRAFT-8DEEE634E62CD560` remains fake-offline, sample-labeled, unreviewed, blocked, scratch-only, and unsuitable for silent production canonicalization. Selecting it requires an explicit acknowledgement that deterministic fake/sample provenance will become part of canonical repo truth.

## Required decision

Choose exactly one:

1. Select an existing genuine draft ID and answer every clarification below. Current discovery found no such committed draft.
2. Supply a new genuine research idea for Agent Inbox intake and answer every clarification below.
3. Explicitly authorize `AIDRAFT-8DEEE634E62CD560` as a deliberate canonical canary, acknowledge its fake/sample provenance, and answer every clarification below.
4. Reject or defer all candidates.

Record the choice here:

- Choice (1/2/3/4):
- Selected draft ID, or proposed new title:
- If choice 3: “I acknowledge and accept that fake-offline/sample provenance will be preserved in canonical repo truth” (yes/no):

## One-pass material clarification record

Answer every line. Use `none` only when that absence is an intentional rule; use `unknown/block` when the item must prevent Phase B. Unsupported expected-performance statements will be treated as hypotheses, never evidence.

### Hypothesis and market posture

- Exact economic hypothesis and causal rationale:
- Falsifiable prediction, including the observable outcome that would contradict it:
- Direction: long, short, or both:
- Confirm all unsupported performance/causal claims are hypotheses rather than evidence (yes/no):

### Completed-bar signal and entry

- Exact indicator/feature definitions, including price field, formula/convention, and lookbacks:
- Exact completed-bar signal semantics; identify bar `t` inputs and forbid/allow intrabar inputs:
- Exact long entry condition (or `not applicable`):
- Exact short entry condition (or `not applicable`):
- Cross/event semantics versus persistent-state semantics:
- Entry timing and assumed fill price after a signal:
- Same-bar, repeated-signal, pyramiding, and existing-position behavior:

### Exit, reversal, holding, and risk

- Exact long exit and reversal conditions:
- Exact short exit and reversal conditions:
- Exit timing and assumed fill price:
- Maximum holding rule: enabled/disabled; if enabled, exact bars and counting convention:
- Position-sizing concept and fixed/parameterized/review-only posture:
- Exposure, leverage, and concurrent-position assumptions:
- Stop-loss posture: exact stop or explicit no-stop; include evaluation timing and fill behavior:
- Profit target/trailing exit posture, if any:
- Priority/tie policy when entry, exit, reversal, stop, and target coincide:

### Costs and realism

- Maker/taker assumption and fee values or exact repo-default reference:
- Slippage model and value or exact repo-default reference:
- Funding treatment, source, alignment, and notional basis:
- Fill model and bar-path assumption:
- Liquidity/capacity, exchange-constraint, liquidation, and maintenance-margin assumptions:

### Timeframes and data

- Primary timeframe (must be one of `15m`, `30m`, `1h`, `4h`, `1d`):
- Confirmation timeframes and exact completed-bar alignment, or none:
- Exact symbol/instrument confirmation (`BTCUSDT` Binance USDT-M perpetual):
- Exact raw data streams and fields:
- Exact derived features and definitions:
- Warm-up requirement, including maximum lookback and first eligible signal bar:
- Missing-bar, irreparable-gap, stale-data, and cross-timeframe gap policy:
- Identified repo-supported dataset/catalog/feature references:
- Known data coverage limitations:

### Parameters and constraints (maximum five free parameters)

For each free parameter provide name, role, type, units, allowed set or inclusive min/max/step, default, and rationale:

1. Parameter 1:
2. Parameter 2:
3. Parameter 3:
4. Parameter 4:
5. Parameter 5:

- Fixed literals that are deliberately not free parameters, with rationale:
- Invalid parameter combinations and ordering constraints:
- Confirm total free-parameter count is at most five (yes/no):

### Disconfirmation, stop conditions, and differentiation

- Preregistered disconfirmation criteria, including costs and out-of-sample posture:
- Thesis stop conditions distinct from a trade-level stop-loss:
- Exact duplicate scan comparison set and why this is not an exact duplicate:
- Material differentiation from `STRAT-SPEC-0001` through `0006`:
- Material differentiation from concluded H-001 through H-010 and H-012, especially momentum/trend families H-005, H-008, and H-012:
- If near-duplicate: explicitly confirm it may proceed and state the research reason (yes/no + reason):
- Unsupported claims or promotional language to omit from canonical content:
- Known compiler/adapter/runner/data limitations:
- Resolution for every current blocker, including who/what establishes that resolution:
- Any remaining open question (must be `none` to enter Phase B):

## Mandatory stop

No review event, eligibility overwrite, frozen Strategy Spec, Gate-C approval record, or canonical write is authorized by this packet.

**AWAITING KARL CANDIDATE/CLARIFICATION DECISION**

