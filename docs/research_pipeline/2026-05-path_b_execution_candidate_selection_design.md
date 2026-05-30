# Path B Execution Candidate-Selection Design

## 1. Scope

WP-S2c-125 / WP-12fe is a Tier 1 documentation-only candidate-selection design
package. Validation profile: CS12 T1-doc-narrow.

This package creates only this candidate-selection design document and updates
`docs/project_status.md`. No other file is created or modified.

This package selects the initial Path B candidate design surface only. It does
not register a candidate, pre-register a hypothesis, create an experiment, run a
backtest, create trial-log entries, create OL/REC/DEC, modify canonical
artifacts, or authorize readiness/transition.

## 2. Repo-truth basis

- WP-S2c-124 (WP-12fd) opened the bounded Path B execution tranche. Its merged
  document `docs/research_pipeline/2026-05-path_b_execution_design_opening.md`
  deferred specific candidate-selection questions to WP-S2c-125.
- WP-S2c-123 (WP-12fc) locked Option B as-written. Locked wording:
  "Path B may be prepared as a narrow current-taxonomy/current-timeframe
  discipline route that examines under-covered strategy-family, timeframe, and
  information-input combinations already permitted by repo truth."
- Main 4.0 approved bounded Path B execution under locked Option B. Initial
  authorization covers one candidate only.
- WP-S2c-119 (WP-12ey) is the diagnostic evidence source for this design.
  Source: `research/briefs/2026-05-cross_candidate_diagnostic_brief.md` and
  its Q01–Q12 committed outputs.
- Locked taxonomy, timeframe_status, and data catalog are read-only sources.
  They are not modified by this package.
- Existing canonical artifacts and existing briefs remain historical records
  and are not modified.

## 3. Source-verification method

Every selection in this document is sourced from a specific repo file.
No memory-based taxonomy or timeframe assertion is used. If any selected
label/value were not directly supported by repo truth, this package would stop
rather than invent.

| Selection dimension | Source file | Exact label / value found |
|---|---|---|
| Information_inputs taxonomy | `research/candidate_registry.jsonl` | `ohlcv_30m`, `ohlcv_1h`, `ohlcv_4h`, `ohlcv_1d`, `funding_8h`, `mark_price_4h`, `index_price_4h`, `premium_index_1h`, `premium_index_4h` |
| Information_inputs taxonomy | `docs/data_catalog.md` | Dataset: BTCUSDT 15m full history; Dataset: funding rates full history |
| Timeframe taxonomy | `docs/onboarding/PHASE2_BASELINE.md` D2-013 | `15m, 30m, 1h, 4h, 1d` |
| Timeframe status | `research/timeframe_status.md` | `15m` status: `PLANNING` |
| Data catalog source (15m) | `docs/data_catalog.md` | `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` |
| Data catalog source (funding) | `docs/data_catalog.md` | `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet` |
| D2-006 free-parameter gate | `docs/onboarding/PHASE2_BASELINE.md` D2-006 | Gate 7: ≤ 5 free parameters |
| D2-006 DSR gate | `docs/onboarding/PHASE2_BASELINE.md` D2-006 | Gate 2: DSR > 1.0 at 95% CI |
| DSR trial-count discipline | `docs/onboarding/PHASE2_BASELINE.md` D2-004 | Trial count from `research/trial_log.jsonl` |
| Diagnostic coverage | `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q05.json` | `15m` has zero concluded candidates |
| Diagnostic coverage | `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q06.json` | No `ohlcv_15m` label appears; confirms zero 15m OHLCV coverage |
| Candidate registry reserved slot | `research/candidate_registry.jsonl` | H-011 `status: DRAFT`, `pipeline_stage: reserved` |
| Strategy-family coverage | `research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q02.json` | `trend_following` tested at `4h` and `1d` only; never at `15m` |

## 4. Diagnostic-selection basis

WP-S2c-119 Q05 (`research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q05.json`)
returns the strategy-family / timeframe coverage matrix for the current ten
concluded candidates plus the reserved H-011 row.

Q05 shows:
- `15m` has zero candidates in the concluded population. It does not appear in
  any Q05 row for concluded candidates.
- `30m` has two candidates (`breakout` / H-006; `multi_tf_alignment` / H-009).
- `1h` has two candidates (both `momentum`).
- `4h` has four candidates across three families.
- `1d` has two candidates.
- `weekly` (H-011 reserved slot) is outside the locked timeframe set.

Search-space coverage at `15m` is zero. This is the clearest under-covered
case in the locked timeframe set.

WP-S2c-119 Q06 (`research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q06.json`)
returns information-input label coverage. No `ohlcv_15m` label appears anywhere
in Q06. `funding_8h` appears for five candidates. This confirms that a 15m
OHLCV-based combination is under-covered in both the timeframe dimension and the
information-input dimension simultaneously.

This selection responds to sparse search-space coverage at 15m and concentrated
information-input coverage at 4h/1h. The selected combination is not described
as best, most promising, or ranked over alternatives. It is the selected initial
bounded Path B design surface under current constraints.

## 5. Selected strategy-family

**Selected:** `trend_following`

Source evidence from Q02
(`research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q02.json`):
`trend_following` appears for `H-002` at `4h` and `H-004` at `1d`. It has
never been tested at `15m`.

The `trend_following` family is established in the registry with two concluded
entries. It has the clearest prior-art naming convention in the existing
candidates and requires no new family label. At 15m it examines whether
short-horizon directional signals — intraday runs and bar-level momentum
accumulation — carry predictive content distinct from the multi-day trend
dynamics of the 4h and 1d candidates.

This is not a ranking or preference over all strategy families. It is the
initial bounded design choice. Other under-covered families (e.g., `breakout`
at 15m, `mean_reversion` at 15m) remain untested and may be considered in later
packages with separate Main/Karl authorization.

## 6. Selected timeframe

**Selected:** `15m`

Source: `research/timeframe_status.md`, row for `15m`, Status column:
`PLANNING`. This is the verbatim entry in the locked timeframe-status file.

The `15m` timeframe is also listed verbatim in D2-013
(`docs/onboarding/PHASE2_BASELINE.md`): "Locked timeframe set for Phase 2
research: 15m, 30m, 1h, 4h, 1d."

`15m` is the only timeframe in the locked set currently in `PLANNING` status
with zero tested candidates. All other locked timeframes (`30m`, `1h`, `4h`,
`1d`) are in `Cold Storage` per `research/timeframe_status.md`.

No timeframe boundary is added, modified, or reinterpreted. The `15m`
timeframe is accepted as-found in locked repo truth.

## 7. Selected information_inputs

**Selected:** `["ohlcv_15m", "funding_8h"]`

**`funding_8h`:** This label appears verbatim in five concluded candidate
entries in `research/candidate_registry.jsonl` (H-001, H-007, H-008, H-009,
H-010). It is fully established in the locked taxonomy. As an 8h funding event
stream it is cross-timeframe and may be used alongside any OHLCV timeframe.

**`ohlcv_15m` — CONDITIONAL, pending Main/Karl interpretation confirmation:**
This label has not appeared verbatim as a registered candidate `information_input`
in any prior candidate entry. Q06
(`research/briefs/2026-05-cross_candidate_diagnostic_brief/outputs/Q06.json`)
confirms no `ohlcv_15m` label exists in the current committed registry. No repo
file explicitly states that `ohlcv_15m` is an authorized locked-taxonomy label.

Repo evidence supporting the label as a plausible extension:
- The pattern `ohlcv_{timeframe}` appears verbatim across `ohlcv_30m` (H-006,
  H-009), `ohlcv_1h` (H-005, H-008, H-009), `ohlcv_4h` (H-001, H-002, H-007,
  H-009), and `ohlcv_1d` (H-003, H-004) in `research/candidate_registry.jsonl`.
- The 15m OHLCV dataset exists in `docs/data_catalog.md` under "Dataset:
  BTCUSDT 15m full history (Binance USDT-M Perp) – Parquet", range
  2020-01-01 / 2026-04-11.
- D2-013 (`docs/onboarding/PHASE2_BASELINE.md`) lists `15m` in the locked
  timeframe set: "15m, 30m, 1h, 4h, 1d."

However, no repo file explicitly authorizes `ohlcv_15m` as a locked-taxonomy
label. The label is inferred from the naming convention applied to the locked
15m timeframe. Whether this inference constitutes a permitted label under locked
Option B, or constitutes "adding" a new taxonomy label, is an interpretation
question that requires Main/Karl confirmation before WP-S2c-126 may be drafted.

This design selects `ohlcv_15m` as the intended primary information_input
conditional on that confirmation. If Main/Karl rejects this interpretation, the
design surface must be revised before WP-S2c-126 proceeds.

No taxonomy label is added, modified, reinterpreted, or combined through new
grammar as an action of this package. The combination does not introduce C-shape
grammar work. The selection remains inside Option B, pending confirmation.

## 8. Selected data source(s)

**Selected:**
1. BTCUSDT 15m full history (Binance USDT-M Perp) – Parquet
   - Source: `data.binance.vision` bulk archives + Binance Futures API
   - Range: 2020-01-01 / 2026-04-11
   - Storage path: `data/processed/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`
   - Confirmed in: `docs/data_catalog.md`

2. BTCUSDT funding rates full history (Binance USDT-M Perp) – Parquet
   - Source: Binance Futures API `/fapi/v1/fundingRate`
   - Range: 2019-09-10 / 2026-04-12
   - Storage path: `data/processed/binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_2026-04-12T1655Z.parquet`
   - Confirmed in: `docs/data_catalog.md`

Both data sources are present in the locked data catalog. No external data,
paid data, Tier 4, protected-path, runtime, or paper/live data source is used.
No data source is added, modified, reinterpreted, or extended by this package.

## 9. Initial Path B candidate design surface

**Design name / descriptive slug (for later candidate):**
`15m-trend-following-funding-filtered`

This slug is descriptive and does not constitute a registry mutation. No
candidate ID is assigned in this package.

| Field | Selected value |
|---|---|
| Strategy-family | `trend_following` |
| Timeframe | `15m` |
| Information_inputs | `["ohlcv_15m", "funding_8h"]` |
| Primary data source | BTCUSDT 15m full history Parquet |
| Secondary data source | BTCUSDT funding rates full history Parquet |
| Expected hypothesis theme | Short-horizon directional bias using 15m price bars, gated by funding rate direction to reduce false signals from counter-directional leverage positioning |

**Expected candidate artifact lineage if later authorized:**
- WP-S2c-126: candidate registry row + `HYPOTHESIS.md` + initial
  `experiment.ipynb`
- WP-S2c-127: EXP creation
- WP-S2c-128: backtest + trial-log entry + REP artifact
- WP-S2c-129: OL + REC
- WP-S2c-130: DEC

Candidate ID assignment is deferred to WP-S2c-126 pre-draft verification.
H-011 is only a likely/reserved slot if direct registry inspection confirms it
remains available and matches the intended candidate shape.

## 10. Economic rationale

BTC perpetual futures exhibit intraday directional runs — periods where price
accumulates bars in one direction before reversing or pausing. At the 15m
granularity these runs are shorter in duration and noisier than 4h or 1d trends,
but they may be detectable through conventional trend signals applied to 15m
bars when combined with a funding-rate context filter.

The funding rate reflects the cost of holding a leveraged perpetual position
and encodes whether the market is net long or net short in aggregate. When
funding direction aligns with a detected 15m price trend, the net leveraged
positioning adds structural tailwind pressure in that direction. When funding
opposes the detected trend, leveraged positioning may act as a headwind that
increases false-signal probability.

This rationale is about observable market behavior and data relationships, not
a performance expectation. The 15m timeframe has not been tested, and the
rationale does not guarantee that a well-designed candidate will pass any D2-006
gate.

Cost drag at 15m is a primary design concern. A minimum hold period or signal
persistence requirement may be needed to keep cost drag within the D2-006
Gate 5 threshold (≤ 50% of gross PnL). This is a design tension, not a
resolved question.

## 11. Testable predictions

These predictions are falsifiable and tied to the selected timeframe, strategy
family, and information_inputs. They do not imply readiness if they are
confirmed.

1. A 15m trend signal (e.g., moving-average crossover or channel breakout on
   `ohlcv_15m`) produces OOS Sharpe > 0 more often than random entry over
   multi-year walk-forward folds, whether or not it clears the D2-006 Gate 1
   threshold of ≥ 1.0.

2. The `funding_8h` directional filter reduces the false-signal rate — measured
   as the fraction of signals that produce negative OOS returns — compared to a
   pure 15m price-trend baseline using `ohlcv_15m` alone.

3. Cost drag as a fraction of gross PnL increases materially at 15m compared to
   4h equivalents (H-001, H-002), consistent with the D2-006 Gate 5 structural
   concern for faster timeframes.

4. Walk-forward efficiency (OOS/IS Sharpe ratio) exceeds 0.5 in fewer than
   half the tested walk-forward folds, given the higher noise-to-signal ratio
   at 15m compared to 4h or 1d timeframes.

5. The free-parameter count stays at or below 3 for the initial baseline
   design (trend lookback + funding threshold + optional minimum hold), within
   the D2-006 Gate 7 limit of ≤ 5.

## 12. Success / failure criteria

These are design-level criteria. Final exact gate values must be copied from
locked D2-006 in `docs/onboarding/PHASE2_BASELINE.md` by WP-S2c-127 when
authoring the EXP artifact. No gate values are redefined or loosened here.

| Gate | D2-006 source threshold | Design-level expectation |
|---|---|---|
| Gate 1: OOS Sharpe | ≥ 1.0 | Primary quantitative pass/fail; cost drag and noise may make this the binding constraint |
| Gate 2: DSR | > 1.0 at 95% CI | Trial-count-corrected; all prior H-001 through H-010 trials count toward cumulative trial budget |
| Gate 3: Max DD per fold | ≤ 20% | 15m noise may produce elevated per-fold drawdown |
| Gate 4: Parameter sensitivity | min_ratio ≥ 0.70 | 2-3 parameter design limits sensitivity surface |
| Gate 5: Cost drag | ≤ 50% gross PnL | Primary design risk for 15m; may require minimum hold constraint |
| Gate 6: PnL concentration | no 90-day window > 60% | To be verified empirically; 15m data spans 2020-2026 |
| Gate 7: Free parameters | ≤ 5 | Expected 2-3 free parameters; within limit |
| Gate 8: Walk-forward efficiency | OOS/IS Sharpe > 0.5 | Uncertain at 15m; noise may suppress OOS/IS ratio |

Design-level failure condition: if cost drag at 15m structurally and
consistently exceeds the Gate 5 threshold in preliminary testing before full
pre-registration, this indicates the 15m timeframe may be cost-structurally
unsuitable and the design surface requires reassessment before WP-S2c-126.

This failure condition is a WP-S2c-126 stop trigger, not a decision made in
this package.

## 13. Expected free-parameter count under D2-006

D2-006 Gate 7 (source: `docs/onboarding/PHASE2_BASELINE.md`): ≤ 5 free
parameters.

Expected free parameters for the initial baseline design:

| Parameter | Description | Fixed or free |
|---|---|---|
| Trend lookback window | Number of 15m bars for moving-average or channel calculation | Free |
| Funding threshold | Funding rate level above / below which the filter activates | Free |
| Minimum hold bars | Minimum bars a position must be held (cost-drag control) | Free (optional, may be fixed at 0 for initial baseline) |

Expected total: 2 free parameters for the minimal baseline (lookback + funding
threshold), expandable to 3 if minimum hold is treated as free. This is well
below the D2-006 Gate 7 limit of 5.

Constants treated as fixed (not free parameters): bar size (15m), instrument
(BTCUSDT), cost model (locked parametric from backtester), walk-forward fold
boundaries, and UTC bar-close convention.

If the design would require more than 5 free parameters, this package would
stop and report. Based on the current design surface, no stop condition is
triggered.

## 14. DSR-aware trial-count budget

DSR discipline source: `docs/onboarding/PHASE2_BASELINE.md` D2-004.

The Deflated Sharpe Ratio must be computed using the cumulative trial count from
`research/trial_log.jsonl`, which currently records trials for H-001 through
H-010 (10 candidates, multiple runs each). All future trials for the Path B
candidate add to this cumulative count.

Expected trial-count budget for the initial Path B baseline experiment:

| Trial type | Count |
|---|---|
| Primary baseline run | 1 |
| Parameter sensitivity trials (±25% shift on 2 params) | 4 |
| Walk-forward fold runs (included in primary) | N/A (part of primary) |
| Total initial budget | ~5 logged trials |

All backtest runs must be logged in `research/trial_log.jsonl` in WP-S2c-128.
No trial-log entries are created in this package.

DSR must be computed at the time of REP artifact creation (WP-S2c-128) using
the trial count as of that moment. The design surface is narrow enough (2-3
free parameters) that DSR correction at 5 additional trials on top of the
existing 10+ trials is expected to be manageable, but the exact DSR value is
not pre-computed here.

## 15. REC-5 and segment-discipline posture

REC-5 exact-segment discipline (source: `docs/research_pipeline/2026-04-rec_v1_stability.md`
and `docs/research_pipeline/2026-04-rec5_floor_gap_stability.md`) remains
absolute.

No pooled cross-segment inference below the REC-5 floor is allowed. Future
REC entries for the Path B candidate must respect the four-dimension segment:
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`.

The initial REC for a new candidate starts at count 1 for any new exact segment
and is below the REC-5 floor of n ≥ 3. Cross-segment inference across existing
candidate segments is not allowed.

REC-5 posture for the Path B candidate:
- Any new OL/REC artifacts created in WP-S2c-129 will produce initial
  per-segment REC counts of 1 — below floor.
- This is expected. Below-floor posture is the healthy starting state for a new
  candidate.
- The WP-S2c-130 DEC must record the floor posture without claiming sufficient
  evidence for promotion decisions.

## 16. Candidate ID / registry posture

This package does not assign or modify a candidate ID.

H-011 is noted as a likely/reserved slot in `research/candidate_registry.jsonl`
(current entry: `candidate_id: "H-011"`, `pipeline_stage: "reserved"`,
`status: "DRAFT"`). However, H-011's current reserved content is
`cross_asset_regime / weekly` — a design surface incompatible with the selected
15m / trend_following surface. WP-S2c-126 must verify by direct registry
inspection whether H-011 can be repurposed for the selected design surface or
whether a new candidate ID beyond H-011 is the correct path. No assumption is
made here.

WP-S2c-126 pre-draft verification must inspect `research/candidate_registry.jsonl`
directly and confirm the appropriate candidate slot before drafting any registry
row.

If H-011 is unavailable, has been repurposed, or the registry pattern requires
a different ID, WP-S2c-126 must halt and report back to Main/Karl before
proceeding.

## 17. WP-S2c-126 pre-draft verification requirements

**Mandatory stop after WP-S2c-125 merge.** Side must report back to Main/Karl
for explicit interpretation confirmation before WP-S2c-126 may be drafted.
The specific confirmation required is stated in item 2 below. WP-S2c-126 may
not proceed from refreshed-main preflight alone; it requires the explicit
Main/Karl confirmation described here.

Once Main/Karl has confirmed, Side/Claude must also verify directly by reading
current repo files before drafting WP-S2c-126:

1. An appropriate candidate registry slot exists (H-011 or next available)
   and is compatible with the selected 15m / trend_following /
   `ohlcv_15m` + `funding_8h` design surface.

2. **`ohlcv_15m` label interpretation confirmed by Main/Karl.** No repo file
   explicitly authorizes `ohlcv_15m` as a locked-taxonomy label. The label is
   inferred from the `ohlcv_{timeframe}` naming convention applied to the locked
   15m timeframe. Main/Karl must explicitly state whether `ohlcv_15m` is
   accepted as a permitted label under the locked information_inputs taxonomy, or
   whether a different information_input selection is required. This confirmation
   must be obtained before WP-S2c-126 drafts. If rejected, the design surface
   must be revised before any WP-S2c-126 work begins.

3. `funding_8h` label exists verbatim in `research/candidate_registry.jsonl`
   (confirmed in this package; reconfirm at WP-S2c-126 preflight).

4. The `15m` timeframe exists verbatim in `research/timeframe_status.md` as
   `PLANNING` (confirmed in this package; reconfirm at WP-S2c-126 preflight).

5. Both selected data sources exist in `docs/data_catalog.md` (confirmed in
   this package; reconfirm at WP-S2c-126 preflight).

6. The selected design surface still matches this WP-S2c-125 document without
   material drift.

7. No open PR has modified `research/candidate_registry.jsonl`,
   `research/timeframe_status.md`, or `docs/data_catalog.md` since this
   package's merge.

Failure to verify any item, or absence of the item 2 Main/Karl confirmation,
halts WP-S2c-126 and requires a report back to Main/Karl.

## 18. Non-authority and forbidden surfaces

This package explicitly creates none of the following:

- candidate registration
- hypothesis pre-registration
- experiment plan or `experiment.ipynb`
- backtest execution or results
- trial-log entry
- OL artifact
- REC artifact
- DEC artifact
- approval record (R2S or S2P)
- shadow-evidence retention artifact
- readiness determination
- transition authorization
- recommendation, ranking, or scoring
- human-gate execution
- Tier 4 or protected-path contact
- taxonomy change
- timeframe_status change
- data catalog change
- schema change
- validator change
- query-layer change
- tools or tests change
- existing canonical artifact modification
- existing brief modification
- multiple-candidate authorization
- C/F deferred-shape work
- A/D/E reopening

## 19. Stop conditions carried forward

The following stop conditions are inherited from WP-S2c-124 and applied to
this and subsequent packages:

- Selected information_inputs label not present in locked taxonomy or not
  permitted by naming convention applied to locked timeframe.
- Selected timeframe missing from `research/timeframe_status.md` verbatim.
- Selected data source missing from `docs/data_catalog.md`.
- Free-parameter count would exceed D2-006 Gate 7 (≤ 5).
- D2-006 threshold cannot be confirmed from repo truth.
- Economic rationale is insufficient or relies on unsupported claims.
- Design requires candidate registration, hypothesis pre-registration, backtest
  execution, research artifact creation, query SQL/output creation,
  tools/query-layer changes, tests, schemas, validators, query views, existing
  canonical artifact changes, or existing brief changes.
- Design selects multiple candidates or assigns/promotes a candidate ID.
- Design requires or implies candidate recommendation, ranking, scoring,
  readiness, approval, promotion, transition authorization, policy authority,
  or human-gate execution.
- Design treats this package as executing Path B rather than selecting the
  design surface.
- Design weakens, automates, bypasses, replaces, reinterprets, or executes a
  permanent human gate.
- Design requires Tier 4 contact, paper/live contact, broker/exchange/order/
  live API contact, monitoring/dashboard implementation, paper bridge
  implementation, AUTO bridge, A2C-003, or runtime/protected-path work.
- Ranking/scoring/recommendation framing appears.
- Cross-segment inference below REC-5 floor.
- C-shape or F-shape framing pressure.
- Multiple-candidate pressure.
- Need to modify locked source files.
- Karl/user override.

## 20. Validation / next-package posture

WP-S2c-125 uses CS12 T1-doc-narrow.

After merge, Side must stop and report back to Main/Karl. WP-S2c-126 may not
be drafted until Main/Karl provides explicit confirmation of the `ohlcv_15m`
label interpretation (Section 17, item 2). Refreshed-main preflight alone does
not authorize WP-S2c-126 to proceed.

Once Main/Karl confirms and the Section 17 pre-draft verification gate passes
in full:
- Reconfirm the full Section 17 checklist against current repo files.
- Confirm no open stop condition from Section 19 applies.
- Only then draft WP-S2c-126.

WP-S2c-126 is a T3-implementation package with full pytest required. It must
not be auto-drafted from this merge.
