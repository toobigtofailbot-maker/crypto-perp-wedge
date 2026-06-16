# Future Strategy Capability Matrix

This document is non-authoritative architecture memory. It preserves future strategy, data, indicator, simulator, and automation capability lanes so they are not forgotten while the project pursues the fastest safe path for one promising candidate family. It does not authorize implementation, sequencing, data acquisition, candidate registration, promotion, paper/live execution, runtime behavior, OMS/risk changes, broker/exchange connectivity, collateral movement, autonomy, or strategy deployment. Each item still requires a scoped future package, validation plan, changed-file boundary, and explicit authorization before implementation or evidence production.

## Purpose

This matrix preserves future strategy, data, indicator, simulator, and automation families as repo memory. It prevents broad lab-roadmap items from being forgotten while the repo focuses on one candidate path, distinguishes first-live prerequisites from future lab expansion, and keeps all future items human-gated and repo-governed.

The matrix is a preservation surface only. It does not approve, rank, sequence, register, freeze, test, promote, or deploy any strategy family.

## Current fast-path stance

The current operating preference is to push one promising candidate family through the minimum safe evidence path first. Future lab expansion may continue later, or in safe parallel, only when it does not block that first candidate path.

The first-live path should not wait for every family in this matrix. The project may pursue one promising candidate family through canonical evidence, walk-forward/OOS, robustness, candidate review, paper/shadow, and a tightly capped live gate while the broader lab is expanded separately. This document preserves the broader lab scope; it does not make it a prerequisite for first live.

If a future item becomes necessary for the selected candidate, it must be promoted into a separately scoped package with explicit authorization, validation, and changed-file boundaries.

## Capability classes

| Class | Meaning |
|---|---|
| `current_or_near_current` | Mostly compatible with current/near-current OHLCV/crossover/ATR-style lab surfaces. |
| `compiler_indicator_upgrade` | Needs new indicator catalog, Strategy Spec grammar, compiler support, or closed-form expression support. |
| `data_package_required` | Needs new historical data, data-slice metadata, provenance, validation, or causal alignment rules. |
| `simulator_upgrade_required` | Needs intrabar/path/fill/queue/order-book/inventory realism before honest testing. |
| `paper_live_guardrail_required` | Relevant only after paper/shadow/live architecture; not a research prerequisite. |
| `deferred_or_rejected_for_now` | Not suitable for near path due to lookahead, folklore, unavailable data, or excessive scope. |

## Strategy / indicator matrix

| Family / capability | Class | Preserved for later? | Current status | Required upgrades | Not-before condition | First-live prerequisite? | Authority boundary |
|---|---|---:|---|---|---|---:|---|
| SMA/EMA crossover | `current_or_near_current` | Yes | Current path already uses SMA crossover variants | Runner/timeframe support as needed | Candidate-specific package | Possible if selected | No live/runtime authority |
| SMA distance / trend-following | `current_or_near_current` | Yes | Current/near-current OHLCV-compatible family | Strategy Spec / runner path as needed | Candidate-specific prereg | Possible if selected | No candidate authority |
| ATR-stop variants | `current_or_near_current` | Yes | ATR stop exists in current momentum path | Variant-specific prereg/trial | After baseline evidence requires stop isolation | Possible if selected | No auto-promotion |
| OHLCV-only momentum / mean reversion | `current_or_near_current` | Yes | Near-current family | Candidate-specific prereg, runner, result population | Human-gated trial package | Possible if selected | No live authority |
| Breakout / channel | `compiler_indicator_upgrade` | Yes | Future strategy family | Donchian/channel indicator + compiler/spec support | Indicator/compiler package | No unless selected | No implementation authority |
| RSI | `compiler_indicator_upgrade` | Yes | Future strategy family | RSI catalog/compiler support | Indicator/compiler package | No | No implementation authority |
| RVOL | `compiler_indicator_upgrade` | Yes | Future filter/confirmation family | RVOL feature definition, volume alignment, compiler/spec support | Feature-definition package | No unless selected | No ranking authority |
| Z-score / volatility-normalized bands | `compiler_indicator_upgrade` | Yes | Future mean-reversion/normalization family | z-score/stddev composition or closed feature support | Expressiveness package | No unless selected | No result authority |
| Session / day-of-week filters | `compiler_indicator_upgrade` | Yes | Future deterministic filter family | UTC/session calendar, causal labels, spec/compiler support | Calendar/filter package | No | No live authority |
| Multi-condition composed strategies | `compiler_indicator_upgrade` | Yes | Future expressiveness family | Closed grammar/composition support; no eval/free-form formulas | Grammar package | No | No DSL free-form authority |

## Crypto/perp data matrix

| Data / strategy lane | Class | Preserved for later? | Current status | Required upgrades | Not-before condition | First-live prerequisite? | Authority boundary |
|---|---|---:|---|---|---|---:|---|
| Funding-rate strategies | `data_package_required` | Yes | Funding realism is known future dependency; funding-based strategies separate | Funding alignment, lag rules, result identity | Data/feature package | Funding realism may be prerequisite; funding strategy is not | No live viability claim |
| Basis / premium / mark-index divergence | `data_package_required` | Yes | Broadly preserved in future backlog | Data alignment, feature definitions, validation | Data/feature package | No unless selected | No strategy approval |
| Open interest | `data_package_required` | Yes | Not current-ready unless repo truth later proves data availability | Historical OI source, licensing, catalog, validation | Data-source decision | No | No data acquisition authority |
| Liquidation flush / liquidation events | `data_package_required` and `simulator_upgrade_required` | Yes | Future-heavy lane | Liquidation event data, causal labels, path realism | Data + simulator design | No | No live alert/trading authority |
| Long/short ratio | `data_package_required` | Yes | Future data lane | Source, history, definitions, validation | Data-source package | No | No promotion authority |
| Taker-flow imbalance | `data_package_required` | Yes | Partly related to kline taker fields but not fully locked | All-interval schema verification, feature definitions, causal lag | Feature/data feasibility package | No unless selected | No ranking authority |
| Macro / Nasdaq / DXY | `data_package_required` | Yes | Future external-data/regime lane | External data, timestamp alignment, provenance | Data-source package | No | No macro-as-authority |
| On-chain flows | `data_package_required` | Yes | Future external-data lane | Vendor/source decision, schema, provenance | Data-source package | No | No implementation authority |

## Simulator / execution-realism matrix

| Simulator / realism lane | Class | Preserved for later? | Current status | Required upgrades | Not-before condition | First-live prerequisite? | Authority boundary |
|---|---|---:|---|---|---|---:|---|
| Intrabar stops / targets | `simulator_upgrade_required` | Yes | Known realism issue, especially for 4h bar-close stops | Conservative intrabar/path modeling or explicit limitation policy | If selected candidate depends on stop/path realism | Possibly, if selected candidate's live-readiness depends on it | No backtest semantic change here |
| Limit orders | `simulator_upgrade_required` | Yes | Future execution-realism family | Limit-fill assumptions, partial fills, price path | Strategy/simulator package | No unless selected | No order authority |
| Partial fills | `simulator_upgrade_required` | Yes | Future simulator realism | Fill model design, validation, evidence | Simulator design package | No | No broker/exchange authority |
| Queue modeling | `simulator_upgrade_required` | Yes | Future microstructure realism | L2 data, queue assumptions, replay engine | L2/simulator package | No | No live execution authority |
| Market-making / grid / inventory | `simulator_upgrade_required` | Yes | Future heavy strategy family | Limit-order, queue, inventory, risk simulator | Simulator stack exists | No | No autonomous strategy authority |
| L2 / depth replay | `simulator_upgrade_required` and `data_package_required` | Yes | Future-heavy data/sim lane | Historical L2 source, reconstruction, replay validation | Data/vendor decision and simulator design | No | No venue/runtime authority |

## Agent / automation matrix

| Automation lane | Class | Preserved for later? | Current status | Required upgrades | Not-before condition | First-live prerequisite? | Authority boundary |
|---|---|---:|---|---|---|---:|---|
| Strategy idea intake | `current_or_near_current` / future automation | Yes | Future lab capability | Intake contract and classifier | Lab automation package | No | Human-gated |
| Strategy Spec generator / DSL assist | `compiler_indicator_upgrade` / automation | Yes | Future assistant capability | Bounded generator, validation, human review | Spec grammar stable | No | Not execution authority |
| Parameter sweep engine | `current_or_near_current` / automation | Yes | Needed for scale | Bounded sweep orchestration and result registry | Runner stable | Possibly helpful, not mandatory for first candidate | No hidden denominator |
| Result store / run registry | `current_or_near_current` / automation | Yes | Needed for scale | Run registry schema/artifacts | Runner/canonical result path stable | Helpful, not necessarily first-live prerequisite | No parallel truth store |
| Anti-overfit gates | `current_or_near_current` / robustness | Yes | Future robustness layer | DSR/PSR/MinTRL, sensitivity, full-population review | Canonical results exist | Likely before candidate promotion | No auto-approval |
| Walk-forward / regime validation | `current_or_near_current` / robustness | Yes | Future evidence gate | Fold schema/results, chronology checks | Canonical result exists | Likely before candidate promotion | No auto-promotion |
| Monte Carlo / robustness engine | `current_or_near_current` / robustness | Yes | Future robustness layer | Trade/equity series, seed protocol, report | Candidate has enough evidence | Likely before paper/live | No readiness authority |
| Read-only dashboard expansion | `paper_live_guardrail_required` / review | Yes | Future operator/review surface | Dashboard data contracts, non-authority UI | Evidence artifacts exist | Helpful, not authority | Dashboard not truth |
| Agent-assisted strategy drafting | future automation | Yes | Future bounded research assistant | Idea intake, generation constraints, validation | Lab contracts stable | No | Agent cannot approve |
| Large-scale batch sweeps | future automation | Yes | Future scale layer | Batch runner, resource controls, denominator policy | Runner/result registry stable | No | No autonomous promotion |
| 24/7 research monitor / self-improvement | future automation | Yes | Long-term | Scheduler, proposal queue, human gates | Lab mature and protected boundaries locked | No | No live strategy changes |

## Deferred / rejected examples

The following examples remain deferred or rejected for now:

- same-bar lookahead entries;
- heatmap/screenshot-only liquidation claims;
- order-book wall folklore without reproducible L2 rules;
- market making/grid without fill/inventory simulator;
- live liquidation alerts as trading signals;
- autonomous strategy promotion;
- autonomous live parameter changes.

## Sequencing principles

1. First live pilot should not wait for all future families.
2. Any selected candidate gets only the upgrades needed for that candidate.
3. Future families remain preserved but not authorized.
4. Data packages require provenance, retention, licensing/source decision, validation, and causal alignment.
5. Simulator packages require design before implementation.
6. Agents can propose/research, but cannot approve, promote, or trade.
7. Dashboard surfaces are presentation only; repo artifacts remain truth.
8. Paper/live/runtime/OMS/risk/exchange/capital work remains protected and separate.
9. Failed or deferred strategy families must remain visible, not silently deleted.
10. Future work must not create a second truth store outside committed repo artifacts.

## Remaining-WP estimate note

This matrix does not change the current working estimate for the first-candidate path. Broad lab completion would require many additional packages beyond the first-live path, but this document is not a roadmap commitment or implementation queue.
