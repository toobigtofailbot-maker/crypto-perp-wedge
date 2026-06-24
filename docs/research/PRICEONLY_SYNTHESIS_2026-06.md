# BTC 15m Price-Only Research Synthesis and Data-Derived Frontier Status

## Scope

This document synthesizes current repo evidence for the BTCUSDT 15m price-only research lane, recent blocked research-machine reach attempts, data-derived family reach, canonical crossing status, and remaining Side 12 / operator research-lab target-state gaps.

The discovery source is `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/repo_truth_discovery.md`. The structured evidence index is `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json`.

This package did not run a strategy, run a backtest, create or modify a canonical Result Population, execute canonical crossing, promote/register/freeze a candidate, or touch runtime, paper/live, OMS, risk, reconciliation, capital, broker/exchange, provider/API, network, compiler, runner, backtester, data ingestion, schemas, validators, or query behavior.

## Non-Authority Statement

This synthesis is evidence organization only. It is not a strategy recommendation, not a ranking surface, not a candidate-review packet, not a candidate lifecycle action, not a paper/live readiness marker, not runtime authority, and not trading authority.

Research/workbench artifacts and scratch artifacts remain non-authoritative unless a later approved path promotes them through repo-defined gates.

## Evidence Classification Method

Each item is classified with the package vocabulary:

| Dimension | Values used |
|---|---|
| Research evidence state | `canonical_result_population`, `canonical_report`, `scratch_result`, `blocked_attempt`, `adapter_smoke`, `docs_only_design`, `fixture_only_mechanism`, `infrastructure_only` |
| Outcome state | `GO`, `NO-GO`, `BLOCKED`, `ADAPTER_ONLY`, `SMOKE_ONLY`, `NOT_TESTED`, `UNKNOWN` |
| Family class | `price_only`, `data_derived`, `hybrid`, `infrastructure`, `unknown` |
| Authority status | `canonical_evidence`, `non_canonical_evidence`, `not_evidence`, `human_review_required` |

Canonical Result Populations and their paired repo reports are evidence. Scratch blocked attempts and adapter smokes are not canonical strategy evidence. Infrastructure and docs-only designs describe capability or intent, not edge.

## Price-Only Lane: Committed Findings

Repo truth contains several BTCUSDT 15m price-only canonical populations:

- `RP-4492` / `STRAT-SPEC-0001`: SMA-distance real-data population with descriptive non-authority checkpoint.
- `RP-6688` / `STRAT-SPEC-0002`: both-direction SMA-band fixed-size population; all rows record terminal loss/full drawdown under that measurement.
- `RP-7520` / `STRAT-SPEC-0002`: dynamic 1x rerun for the same SMA-band lineage; no uniform liquidation artifact, but no evidence-level edge.
- `RP-7134` / `STRAT-SPEC-0003`: z-score trend-gated mean reversion; frozen screen verdict `NO-GO`.
- `RP-2592` / `STRAT-SPEC-0004`: SMA crossover momentum; frozen screen verdict `NO-GO`.
- `RP-3731` / `STRAT-SPEC-0005`: momentum v2 with ATR-stop; frozen screen verdict `NO-GO`.

The committed price-only BTCUSDT 15m families tested or recorded so far have not produced a candidate worth crossing. This is a current-evidence statement only. It does not state that price-only can never work or that BTC 15m is impossible.

Related Donchian repo truth:

- H-002 / `REP-0003` records a 4h Donchian `NO-GO`.
- H-012 / `REP-0032` records a 15m Donchian breakout with funding filter `NO-GO`; its pure Donchian comparator also liquidated later.

## Price-Only Lane: Blocked / Non-Canonical Attempts

Recent research-machine use attempts produced blocked or adapter-only outcomes rather than fresh price-only edge evidence:

- ORB exit re-spec (`WP-RESEARCH-ORB-EXIT-RESPEC-01`): formalizer accepted the idea, but no validated ORB draft adapter or bridge support exists. No Strategy Spec, VM, Sweep Plan, runner result, robustness packet, or candidate-review packet was produced. MFE, MAE, exit reason, per-trade rows, and ORB gross PnL/cost-gross diagnostics are missing.
- SMA/stddev fresh edge attempt (`WP-RESEARCH-EDGE-SMA-FAMILY-01`): formalizer output duplicated the already-concluded `STRAT-SPEC-0003` / `VM-0003` / `SWEEP-PLAN-0003` / `RP-7134` family. VM/Sweep/bridge were blocked to avoid relabeling duplicate evidence as fresh.
- Donchian adapter (`WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`): formalizer and bridge adapter smoke completed on deterministic scratch fixture data and wrote scratch `RP-3248` under the WP prefix. This is `ADAPTER_ONLY` / `SMOKE_ONLY`, not a canonical Donchian research conclusion.

## Data-Derived Frontier: Current Status

Data-derived infrastructure exists in parts:

- Compiler-visible data refs exist for funding, mark/index/premium, open interest, long/short ratios, and taker fields as direct input values.
- Data feature availability labels distinguish conditional full-history public archive support from recent-only, snapshot-only, vendor-only, streaming-only, or blocked classes.
- Taker-flow archive reconstruction exists as a deterministic offline local-public-archive tool.
- Funding cost mode exists as an explicit default-off backtester setting.

The recent taker-flow adapter/downstream package stopped before implementation. Current repo truth records that the offline runner input path narrows input to OHLCV columns before compilation, and the worktree has no runner-consumable full-history taker-flow dataset. A taker-flow bridge pretending to run through the current runner would either substitute price-only proxy data or require runner/data-source changes.

No committed equivalent taker-flow canonical RP/REP or GO/NO-GO strategy conclusion was found. Taker-flow remains `BLOCKED` / `NOT_TESTED` as a strategy family in the current adapter/downstream frontier. Historical funding-containing candidates exist and have `NO-GO` conclusions, but those do not test the blocked taker-flow adapter path.

## Research-Lab Reach: Current Limits

The research lab has real partial surfaces: idea intake/formalization, bounded research agents, scratch candidate-review packet preparation, fixture-only crossing builder, walk-forward contracts, scratch walk-forward run capability, advisory robustness, dashboard operator review, and notification/approval pilot plumbing.

Current limits remain:

- family adapters are incomplete;
- downstream robustness/candidate-review reach is not generic across supported families;
- non-OHLCV data-derived runner input is blocked;
- per-trade / MFE / MAE / exit_reason diagnostics are not available across the relevant result paths;
- walk-forward/OOS and Monte Carlo robustness are not standard candidate gates across the research machine;
- dashboard/reporting/operator surfaces are partial;
- no paper/live/runtime execution-machine phase is authorized or built for this research state.

## Canonical Crossing Status

Canonical crossing support is fixture-only. `WP-AGENT-CANONICAL-CROSSING-BUILD-01` proves a crossing mechanism against fake/test registry copies and scratch outputs only.

No real canonical crossing has been executed. The first real canonical crossing remains unavailable because no real candidate-review packet worth crossing exists in current repo truth. Recent ORB, SMA/stddev, and taker-flow attempts did not produce the required valid bridge, robustness, and candidate-review source chain.

## Side 12 / Operator Research-Lab Target-State Gaps

| Target item | Status | Evidence basis |
|---|---|---|
| always-on research queue / scheduler | not built | No always-on scheduler or queue authority found. |
| autonomous research scout | not built | Bounded agents exist, but no autonomous scout authority or implementation. |
| Karl-requested idea intake path | partial | Idea intake/formalization surfaces exist, bounded and non-authoritative. |
| broader family adapter coverage | partial | SMA/stddev and Donchian paths exist; ORB and taker-flow are blocked. |
| generic downstream robustness/candidate-review reach across supported families | built for one path only | Current downstream contracts remain narrow and prefix/family constrained. |
| full data-derived family support | blocked by current infrastructure | Taker-flow adapter reach is blocked by runner/data support. |
| runner/data path for non-OHLCV data-derived columns | blocked by current infrastructure | Offline runner input currently strips non-OHLCV fields. |
| per-trade / MFE / MAE / exit_reason diagnostics | partial | Missing for the recent ORB/SMA/taker-flow reach attempts and committed RP aggregate paths. |
| walk-forward/OOS integration as a standard candidate gate | partial | Contracts and scratch run capability exist; first canonical run remains separately gated. |
| Monte Carlo / robustness as a standard candidate gate | partial | Advisory robustness exists; standard gate integration remains incomplete. |
| candidate lifecycle from real agent-produced packet | not built | Scratch-only packet/lifecycle surfaces exist; no real crossed packet. |
| first real canonical crossing | not built | Fixture-only crossing exists; no real crossing. |
| dashboard pages for jobs, strategies, sweeps, walk-forward, robustness, candidates, data provenance, and agent activity | partial | Operator Review dashboard exists; full page breadth remains incomplete. |
| daily brief | not built | No implementation found. |
| weekly report | not built | No implementation found. |
| operator notifications / approval queue | partial | Notification/approval pilot exists, not integrated as target-state queue. |
| regime / parameter advisor | partial | Advisory regime/scoring surfaces exist, not full integrated advisor reach. |
| live/paper performance monitor | not built | Paper/live monitoring remains outside current research state. |
| paper/live/runtime execution-machine phase | not built | Protected runtime/paper/live phase remains out of scope. |

The Side 12 / operator research-lab target state is not complete.

## Open Decision Surfaces

Main may choose whether to commit to runner/data-path work for data-derived families.

Main may choose whether to resume taker-flow/funding adapter work after runner/data-path support exists.

Main may choose whether to add more price-only adapters despite the current synthesis.

Main may choose whether to expand dashboards/reporting/operator surfaces before additional research execution.

Main may choose whether to hold canonical crossing until a real candidate-review packet exists.

## Evidence Index

| Artifact/path | Family/archetype | Evidence classification | Outcome state | Authority status | Short finding |
|---|---|---|---|---|---|
| `research/result_populations/RP-4492.result_population.json` | BTCUSDT 15m SMA-distance | `canonical_result_population` | `UNKNOWN` | `canonical_evidence` | Complete 7/7 real-data population with descriptive checkpoint only. |
| `research/result_populations/RP-6688.result_population.json` | BTCUSDT 15m both-direction SMA-band fixed-size | `canonical_result_population` | `NO-GO` | `canonical_evidence` | Complete 10/10 population; all rows terminal-loss/full-drawdown under fixed-size measurement. |
| `research/result_populations/RP-7520.result_population.json` | BTCUSDT 15m both-direction SMA-band dynamic 1x | `canonical_result_population` | `NO-GO` | `canonical_evidence` | No uniform liquidation artifact, but no evidence-level edge. |
| `research/result_populations/RP-7134.result_population.json` | BTCUSDT 15m z-score trend-gated mean reversion | `canonical_result_population` | `NO-GO` | `canonical_evidence` | Frozen screen records `NO-GO`; no walk-forward/readiness authority. |
| `research/result_populations/RP-2592.result_population.json` | BTCUSDT 15m SMA crossover momentum | `canonical_result_population` | `NO-GO` | `canonical_evidence` | Frozen screen records `NO-GO` due to cost burden and drawdown. |
| `research/result_populations/RP-3731.result_population.json` | BTCUSDT 15m momentum v2 ATR-stop | `canonical_result_population` | `NO-GO` | `canonical_evidence` | Frozen screen records `NO-GO` due to drawdown and cost. |
| `research/experiments/REP-0003.report.json` | 4h Donchian trend following | `canonical_report` | `NO-GO` | `canonical_evidence` | H-002 concluded `NO-GO`; corrects stale Donchian novelty premise. |
| `research/experiments/REP-0032.report.json` | 15m Donchian funding-filter plus pure comparator | `canonical_report` | `NO-GO` | `canonical_evidence` | H-012 concluded `NO-GO`; pure comparator also liquidated later. |
| `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/repo_truth_discovery.md` | ORB / opening range exit re-spec | `blocked_attempt` | `BLOCKED` | `non_canonical_evidence` | No validated ORB adapter or bridge support; diagnostics missing. |
| `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/repo_truth_discovery.md` | SMA/stddev fresh edge attempt | `blocked_attempt` | `BLOCKED` | `non_canonical_evidence` | Blocked because machine path duplicated concluded `RP-7134`. |
| `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/donchian_bridge_smoke_reference.json` | Donchian adapter | `adapter_smoke` | `ADAPTER_ONLY` | `non_canonical_evidence` | Fixture-backed real-runner smoke only; no strategy conclusion. |
| `scratch/WP-AGENT-ADAPTER-TAKERFLOW-FAMILY-01/repo_truth_discovery.md` | Taker-flow adapter/downstream reach | `blocked_attempt` | `BLOCKED` | `non_canonical_evidence` | Runner/data support cannot consume archive-derived taker-flow columns. |
| `docs/status_entries/WP-AGENT-CANONICAL-CROSSING-BUILD-01.md` | Canonical crossing mechanism | `fixture_only_mechanism` | `NOT_TESTED` | `not_evidence` | Fixture-only builder exists; no real crossing executed. |
| `docs/status_entries/WP-COMPILER-FEATURES-DATA-DERIVED-01.md` | Data-derived feature refs | `infrastructure_only` | `NOT_TESTED` | `not_evidence` | Direct input refs only; no runner/data ingestion conclusion. |
| `docs/status_entries/WP-DATA-AVAILABILITY-LABELS-01.md` | Data-derived availability labels | `infrastructure_only` | `NOT_TESTED` | `not_evidence` | Labels full-history/recent/snapshot/vendor classes. |
| `docs/status_entries/WP-DATA-TAKERFLOW-ARCHIVE-RECON-01.md` | Taker-flow archive reconstruction | `infrastructure_only` | `NOT_TESTED` | `not_evidence` | Offline reconstruction tool exists; no strategy or runner integration conclusion. |

The complete structured evidence index lives at `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json`.
