# Strategy-Lab Capability Delta Map

## Scope And Non-Authority

`WP-STRAT-CAP-01` is design-only and roadmap-only. It implements nothing.

This document does not authorize Strategy Specs, candidates, variant manifests,
sweep plans, result populations, backtests, paper/live behavior, runtime
behavior, data acquisition, vendor spend, simulator implementation, dashboard
authority, ranking, recommendation, readiness, promotion, execution authority,
or protected-path changes.

Strategy-research handoff remains planning input only. Repo truth, current
merged files, and actual artifact contents win over Main 4 text, onboarding,
memory, external research, or summaries if they conflict.

## Repo-Truth Basis

Inspected base:

- Branch: `docs/strat-cap-01-capability-delta-map`
- Base commit: `3dc45815395384ecb5c6049dd8940e1e8fe2f8bb`
- Base source: refreshed `origin/main`
- Open PRs at start: none returned by `gh pr list --state open`

Key files inspected:

- `AGENTS.md`
- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/ai/codex/WP_DRAFTING_STANDARD.md`
- `docs/ai/codex/COMPACT_WP_TEMPLATE.md`
- `docs/ai/codex/WP_EXECUTION_REPORT.md`
- `docs/status_entries/README.md`
- `docs/status_entries/WP-F5A.md`
- `docs/status_entries/WP-F5B.md`
- `docs/status_entries/WP-F5C.md`
- `docs/status_entries/WP-GUIDE-EFF-05.md`
- `docs/status_entries/WP-GUIDE-CLAUDE-ALIGN-01.md`
- `docs/status_entries/WP-D5.md`
- `docs/status_entries/WP-D6.md`
- `docs/status_entries/WP-E4.md`
- `docs/research_pipeline/2026-06-compiler_extension_tranche_plan.md`
- `docs/research_pipeline/2026-06-lookback_parameter_binding_design.md`
- `docs/research_pipeline/2026-06-strategy_research_lab_design_consolidation_roadmap.md`
- `docs/research_pipeline/README.md`
- `docs/architecture/2026-06-two_lane_sandbox_wall.md`
- `docs/architecture/2026-06-read_only_operator_surface_design.md`
- `docs/architecture/2026-06-alert_briefing_channel_design.md`
- `docs/architecture/2026-06-paper_bot_scaffolding_design.md`
- `docs/dashboard/README.md`
- `research/schemas/strategy_spec.schema.json`
- `research/schemas/dashboard_data.schema.json`
- `research/result_populations/RP-4492.result_population.json`

Presence checks also found current artifact surfaces under
`research/strategy_specs/`, `research/variant_manifests/`,
`research/sweep_plans/`, `research/indicator_catalogs/`,
`research/result_populations/`, `research/derived_reports/`, and
`research/data_slices/`.

## Main 4 Authorization Basis

Main 4 authorized the F5 runway as F5B, then F5C, then F5D only if needed,
followed by a report-back checkpoint. Main 4 then authorized the first post-F5
design-only lane as `WP-STRAT-CAP-01`, before committing to FLOW, indicator,
open-interest, simulator, or other implementation ordering.

The named post-F5 tracks to inventory are STRAT-BRIEF, STRAT-CAP,
INDICATOR/CATALOG, PERP-FEATURES, CALENDAR, WFO, DASHBOARD-REVIEW, FLOW-FEAS,
OI-DATA, TRADE/L2-DATA, SIMULATOR, and PROTECTED-PAPER/LIVE.

The authorization is design-only. Data acquisition, vendor spend, simulator
implementation, paper/live work, OMS/risk/protected runtime changes, and
protected-path contact remain Karl-gated or forbidden unless later explicitly
authorized.

## F5 Runway Closeout

| Item | Repo-truth status | Evidence | Closeout classification |
|---|---|---|---|
| F5A | Merged | `docs/status_entries/WP-F5A.md`, project-status pointer, PR #422 | Complete |
| GUIDE-EFF-05 | Merged | `docs/status_entries/WP-GUIDE-EFF-05.md`, project-status pointer, PR #423 | Complete process correction |
| F5B | Merged | `docs/status_entries/WP-F5B.md`, project-status pointer, PR #424 | Complete |
| F5C | Merged | `docs/status_entries/WP-F5C.md`, project-status pointer, PR #425 | Complete |
| F5D | Not needed | F5C status reports non-draft mergeable PR, display-only renderer complete, no collector/schema/validator/result-population mutation, no generated-output commit, no authority drift, and no open PRs or live F5 defect found at package start | Conditional-not-needed |
| GUIDE-CLAUDE-ALIGN-01 | Merged | `docs/status_entries/WP-GUIDE-CLAUDE-ALIGN-01.md`, project-status pointer, PR #426 | Process follow-up complete |

F5D is classified as conditional-not-needed because no remaining F5C blocker
requiring validation or polish was found, no authority drift requiring an F5
correction was found, F5C committed no generated dashboard output, and F5C
status records explicit no-authority and no-forbidden-scope boundaries.

## Current Capability Inventory

| Capability area | Current repo-truth capability | Evidence source | Limitation / gap |
|---|---|---|---|
| Strategy Spec grammar | `strategy_spec.schema.json` exists with non-executing Strategy Spec shape, status vocabulary, condition groups, operator enum, backtest assumptions, closed lookback binding support, and explicit non-authority declarations | `research/schemas/strategy_spec.schema.json`; project-status WP-R2/WP-R3 entries | Exact future candidate flow and broader expressiveness remain Main/Karl decisions |
| Indicator catalog | `IND-CATALOG-0001.indicator_catalog.json` and `indicator_catalog.schema.json` exist; catalog remains interface-only | `research/indicator_catalogs/`; `research/schemas/indicator_catalog.schema.json`; compiler tranche plan | Additional indicators such as RSI, RVOL, Donchian, VWAP are not implemented here |
| Compiler operators | Compiler plan records support for `gt`, `gte`, `lt`, `lte`, `eq`, `neq`; schema also enumerates additional operators that fail closed unless implemented | `2026-06-compiler_extension_tranche_plan.md` | `crosses_above`, `crosses_below`, `in_set`, `is_true`, `is_false` are not current compiler capability per inspected plan |
| Compiler operands/composition | Data, indicator, parameter, constant, and one closed composed form are represented; `scale_by_one_minus_parameter` is the existing composed form | `strategy_spec.schema.json`; compiler tranche plan | Plus/offset/z-score composition remains future work |
| Lookback binding | Closed `bars_parameter_ref` schema/validator support and compiler resolution are merged for approved indicator-ref contexts | project-status WP-R2/WP-R3 entries; `strategy_spec.schema.json` | No Strategy Spec mutation or new canonical artifact is authorized by this map |
| Variant manifests | `VM-0001.variant_manifest.json` exists and is linked to result populations | artifact inventory; `RP-4492` lineage | Future variant-generation process and amendment policy remain bounded by later packages |
| Sweep plans | `SWEEP-PLAN-0001.sweep_plan.json` exists and is linked to result populations | artifact inventory; `RP-4492` lineage | No new sweep or run is authorized here |
| Offline runner | Build-and-test-only offline runner has produced fixture and canonical-real-data populations with D4 provenance after D5A-D5C alignment | WP-D5 status; `RP-4492` execution context | Runner changes are outside this package and not authorized |
| Result populations | `RP-2134` fixture-backed and `RP-4492` canonical-real-data result populations exist; both preserve committed denominator posture | `research/result_populations/`; `WP-D5.md`; `RP-4492` | Result populations remain evidence/reference only and do not rank or promote |
| Real-data slice/catalog | D4A artifact chain exists for Binance USDT-M BTCUSDT 15m with PASS validation, catalog ref, slice identity, row/range/gap/duplicate/source facts | `research/data_slices/...`; WP-D4A evidence in project/status entries; `RP-4492` data coverage | Bulk OHLCV remains local/gitignored; acquisition expansion is not authorized |
| Robustness / PSR / DSR / MinTRL | Derived robustness report exists for `RP-2134`; numeric PSR/DSR/MinTRL were withheld when required inputs were absent | `research/derived_reports/RP-2134.item6_robustness_report.md`; project-status WP-12ih | Full robustness formulas and return-path storage remain future design/implementation decisions |
| Dashboard / Results page | Static local dashboard has Overview, Data/Provenance, Gates, and display-only Results page from validated `dashboard_data.v1` | `docs/dashboard/README.md`; `WP-F5B.md`; `WP-F5C.md`; `dashboard_data.schema.json` | Generated output remains local/gitignored; no dashboard authority or controls |
| Data ingestion/validation/catalog | Offline 15m D1-D4/D4A path is built for local CSV/ZIP normalization, validation, catalog/slice identity, and committed provenance artifacts | project-status WP-D1 through WP-D4A entries; data docs; data-slice artifacts | No live API, data download, vendor acquisition, or broader data family acquisition is authorized |
| Operator surfaces | Read-only operator surface and alert/briefing channel are designed; F5 static dashboard is implemented as local display-only surface | E2/E3 docs; F5B/F5C docs | Alert implementation and any paper-risk snapshot source remain future-gated |
| Paper-risk sandbox design | Two-lane sandbox wall and E4 paper-bot scaffolding design exist | E1/E4 architecture docs | Paper-bot implementation remains separately Main/Karl-gated |
| Simulator realism | Bar-based offline runner assumptions and D6 descriptive checkpoint exist; paper-bot simulation is design-only | `RP-4492`; WP-D6; E4 design | Realistic simulator implementation, intrabar fill model, L2/trade data, and exchange constraint expansion are not authorized |
| Data acquisition / OI / L2 / trades | No committed OI/L2/trade data acquisition track was verified in this package | artifact inventory and targeted search | Karl-gated / not started |
| Paper/live/protected runtime | Protected runtime boundaries remain intact; no package in this map authorizes paper/live/protected-path implementation | `AGENTS.md`; startup docs; E1/E4 docs | Forbidden now unless later explicit Main/Karl package authorizes exact protected scope |

## Main 4 Adopted Track Disposition

| Track | Main 4 posture | Current repo-truth status | Remaining gap | Next WP shape | Gate |
|---|---|---|---|---|---|
| STRAT-BRIEF | Design-roadmap track | Partially built / absorbed by lab design consolidation and D6 descriptive checkpoint | No fresh Main 5 brief selects next strategy-lab decision | T1 decision brief or activation packet | Main decision required |
| STRAT-CAP | First post-F5 lane | This package creates the capability map | Merge/review this map | T1 docs-only closeout | Main review |
| INDICATOR/CATALOG | Design-roadmap track | Partially built: catalog schema/instance exist; compiler supports basic builtins; lookback binding merged | Additional indicators/operators remain unimplemented | Narrow compiler/catalog design or implementation package | Main decision; implementation packages require scoped validation |
| PERP-FEATURES | Design-roadmap track | Partially represented through 15m OHLCV, funding-era docs, backtest assumptions, and D4A provenance; not a dedicated feature expansion track | Mark/index/premium/funding feature integration and perp-specific feature families are not currently sequenced | T1 feasibility/design before data/tooling | Main decision; data acquisition Karl-gated if external/new |
| CALENDAR | Design-roadmap track | Design-authorized, not started as a dedicated implementation surface | UTC/session/time filters deferred in compiler plan | T1 closed calendar/session filter design | Main decision |
| WFO | Design-roadmap track | Design concern appears in lab roadmap and validity notes; no WFO implementation verified here | Exact walk-forward protocol and result-population storage needs undecided | T1 methodology design before implementation | Main/Karl decision |
| DASHBOARD-REVIEW | Design-roadmap track | Partially built / F5 complete for display-only Results; E2 read-only surface design exists | No review-workflow controls or authority-bearing dashboard behavior, by design | T1 review-surface constraints or narrow display-only implementation | Main decision; no authority |
| FLOW-FEAS | Design-roadmap track | Design-authorized, not started in this package; no committed flow-data feasibility artifact verified | Source, cost, provenance, and utility unknown | T1 feasibility only | Karl-gated for acquisition/vendor spend |
| OI-DATA | Design-roadmap track | Design-authorized, not started; no OI artifact verified | Source, cost, coverage, validation, and storage unknown | T1 feasibility/data contract only | Karl-gated for acquisition/vendor spend |
| TRADE/L2-DATA | Design-roadmap track | Design-authorized, not started; no trade/L2 artifact verified | Source, storage, cost, privacy, and simulator use unknown | T1 feasibility/data contract only | Karl-gated for acquisition/vendor spend |
| SIMULATOR | Design-roadmap track | Design-only scaffolding exists through E4; implementation not started | Exact simulator model, state, tests, and protected separation undecided | T1/T3 only after Main/Karl boundary authorization | Karl-gated |
| PROTECTED-PAPER/LIVE | Hard-gated surface | Protected and not authorized; E1/E4 preserve sandbox-only boundary | Exact paper-runtime implementation remains gated; live remains forbidden now | No WP unless Main/Karl explicitly authorizes exact scope | Karl-gated / forbidden now |

## Strategy-Research Input Status

External or side strategy research remains planning input only. It does not
create official candidates, Strategy Specs, result populations, evidence,
promotion, readiness, ranking, recommendation, paper/live, or execution
authority.

`STRAT-SPEC-0001`, `VM-0001`, `SWEEP-PLAN-0001`, and `RP-4492` are current repo
artifacts, but this map does not mutate them, interpret them as selection
authority, or authorize any new run.

## True Next-Decision Menu

Option A: accept this capability map and choose the next design track. Candidate
decisions include compiler-extension ordering, strategy-lab validity floor,
FLOW/OI/trade/L2 feasibility, WFO methodology, or dashboard-review constraints.

Option B: authorize a specific next implementation block only if it is already
repo-compatible and not Karl-gated. The existing compiler-extension path is the
most repo-described implementation candidate, but this document does not
authorize it.

Option C: pause further work pending Main/Karl decision, especially if Main 5
wants to reset priorities before using Main 4's design runway.

Option D: request a narrower follow-up inventory if this map surfaces a status
ambiguity that needs a small fact-finding package before implementation order is
chosen.

Existing decision candidates include accepting or revising the compiler-extension
ordering, deciding whether a lab validity floor is required before more lab
implementation, and deciding whether data feasibility tracks should precede
compiler or dashboard-review work.

## Main 5 Activation Note

What Main 5 needs to know:

- Repo truth now includes merged F5B/F5C Results dashboard work and PR #426
  guidance alignment on top of the earlier strategy-lab, data, compiler, and
  engineering design tranches.
- Main 4 authorized the post-F5 design roadmap and made STRAT-CAP the first
  sequencing lane.
- F5B, F5C, GUIDE-EFF-05, and GUIDE-CLAUDE-ALIGN-01 are complete; F5D is
  classified conditional-not-needed by current repo truth.
- Current built capability includes Strategy Spec/indicator/variant/sweep/result
  population surfaces, D4A/D5 real-data provenance, lookback binding, static
  display-only Results dashboard, and sandbox/operator/alert designs.
- Open gaps remain around next implementation ordering, expanded compiler
  operators/indicators, WFO/robustness protocol, FLOW/OI/trade/L2 feasibility,
  simulator realism, and any protected paper/live work.
- Data acquisition, vendor spend, simulator implementation, and paper/live or
  protected-path work remain Karl-gated.
- Main 5's next decision is to accept/revise this map and choose the next narrow
  design or implementation package; this map itself chooses none.
