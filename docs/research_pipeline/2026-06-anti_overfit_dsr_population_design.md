# Anti-Overfit / DSR Population Design

## 1. Scope

WP-S2c-159 / WP-12gf is a Tier 1 documentation-only substantive design
package.

It defines anti-overfit / DSR population logic design for the future Strategy
Research Lab.

It creates only this design document and one `docs/project_status.md`
branch-state entry.

It creates no formula implementation, DSR calculation, anti-overfit
implementation, ranking artifact, ranking score, schema, validator, query view,
parser/compiler, code, test, fixture, artifact, storage path, sweep, backtest,
result aggregation, strategy execution, or authority.

## 2. Authorization and repo-truth basis

WP-S2c-158 locked variant/storage discipline and complete result-population
preservation.

WP-S2c-157 consolidated variant/storage design.

WP-S2c-156 defined result-population / storage design.

WP-S2c-155 defined sweep-orchestration design.

WP-S2c-154 opened variant generation design.

WP-S2c-151 locked the Strategy Spec / Strategy DSL direction.

WP-S2c-147 defines the Strategy Research Lab lifecycle from idea intake to
advisory ranked output.

Track 3 remains paused and WP-S2c-140 onward remains deferred, not rescinded.

Implementation remains unauthorized until later explicit Karl authorization.

## 3. Design objective

The objective is to define how the future lab should detect and surface
overfit risk at population level.

DSR / multiple-testing-aware interpretation should depend on the complete
variant population, not surviving winners or a best-looking subset.

The future triage layer is diagnostic and advisory only.

This design preserves D2-006, D2-007, REC-5, Phase 9 / D2-011, Scope 6,
canonical evidence routing, and permanent human gates.

This package does not create calculations or executable rules.

## 4. Lifecycle placement

Anti-overfit / DSR review belongs after future result-population creation and
before advisory ranking.

It consumes future complete result populations and canonical evidence
references.

It should feed WP-S2c-160 advisory ranking design.

It does not replace EXP / REP, trial-log, OL / REC / DEC.

It does not bypass D2-006 promotion gates or Scope 6 R2S discipline.

## 5. Anti-overfit triage posture

Triage is an upstream diagnostic filter / warning layer.

Future triage may mark variants or families as fragile, blocked, suspicious, or
unsuitable for advisory ranking consideration.

Triage does not approve candidates.

Triage does not promote anything.

Triage does not override D2-006.

Triage does not create evidence by itself.

Triage must be mechanical and pre-defined before result review where possible.

Triage should not be adjusted post-result to rescue desired variants.

## 6. DSR population posture

DSR / multiple-testing-aware interpretation must operate at the population
level.

The tested population includes attempted and relevant non-success outcomes
preserved by WP-S2c-158.

DSR cannot be computed only on the winning variant or a hand-picked subset.

The population denominator must reflect variants, trials, retries, seeds,
folds, walk-forward windows, and amendments as later design defines.

This package does not implement DSR formulas or choose exact computation
mechanics.

DSR is referenced as Bailey and Lopez de Prado 2014 conceptual discipline only;
no formula implementation is created.

## 7. Full-population input requirement

Future anti-overfit review requires the complete result-population surface
locked by WP-S2c-158.

Missing failed, invalid, errored, aborted, or filtered variants should block or
qualify anti-overfit review.

Winner-only data is insufficient.

Population completeness defects should be surfaced explicitly before advisory
ranking.

No result population is created here.

## 8. Mechanical triage criteria

Future mechanical criteria families should include:

- liquidation or ruin events;
- negative or materially weak risk-adjusted performance;
- single-event or single-trade dependency;
- parameter-cliff sensitivity;
- walk-forward divergence;
- regime instability;
- cost, slippage, and funding fragility;
- drawdown or tail-risk concentration;
- insufficient trade count or sample size;
- data/timeframe unsupported cases;
- mismatch against pre-registered variant universe;
- trial-budget or amendment irregularities.

Exact thresholds remain deferred.

## 9. Liquidation and ruin-event handling

Future variants with liquidation, near-ruin, hard risk-cap breach analogs, or
unacceptable loss concentration should be triaged as blocked or high-risk
unless later policy says otherwise.

This handling must not change D-0001 hard risk caps or runtime risk settings.

No runtime risk logic is modified.

## 10. Negative risk-adjusted outcome handling

Future variants with negative Sharpe or materially negative risk-adjusted
metrics should not survive solely because raw return is positive.

This package does not lock exact metrics or thresholds.

Risk-adjusted weakness is advisory diagnostic only until later ranking design.

## 11. Single-event and single-trade dependency handling

A future variant whose result depends on one trade, one event, one date window,
or one extreme outlier should be flagged as fragile.

Single-trade win-rate or single-event concentration should be visible before
advisory ranking.

Exact concentration metrics remain deferred.

## 12. Parameter-cliff sensitivity handling

A future variant family should be flagged if small parameter changes produce
large performance collapse.

Future design should consider parameter sensitivity around tested values,
including plus/minus 20 percent style stress where meaningful and allowed by
parameter domains.

This package does not lock exact parameter-stress math or thresholds.

## 13. Walk-forward divergence handling

Future anti-overfit review should compare in-sample, out-of-sample, and
walk-forward segments where applicable.

Large walk-forward divergence or poor walk-forward efficiency should flag
fragility.

Exact walk-forward metrics and thresholds remain deferred.

## 14. Regime-stability handling

Future review should assess whether apparent performance concentrates in one
regime only.

Regime instability should be visible across market conditions, volatility
buckets, trend/range contexts, or other later-authorized regimes.

This package does not create regime taxonomy or data changes.

## 15. Cost, slippage, and funding fragility handling

Future variants should be checked for fragility under costs, slippage,
turnover, and funding assumptions.

A variant that only works under unrealistic costs should be flagged.

No cost model or funding model is implemented here.

## 16. Drawdown and tail-risk concentration handling

Future review should flag variants whose returns are dominated by unacceptable
drawdown, tail loss, or recovery profile.

Tail-risk concentration should not be hidden by average metrics.

No drawdown threshold is modified here.

## 17. Sample-size and trade-count posture

Future variants with too few trades or weak sample support should be flagged or
blocked from advisory ranking consideration.

The design should distinguish insufficient sample from poor performance.

Exact minimum trade counts and sample thresholds remain deferred unless already
locked elsewhere.

## 18. Robustness checks

Future robustness-check families should include:

- parameter sensitivity;
- walk-forward efficiency;
- regime stability;
- segment consistency;
- OOS / holdout behavior where applicable;
- cost, slippage, and funding stress;
- drawdown and tail-risk profile;
- turnover and liquidity plausibility;
- trial-budget / multiple-testing exposure;
- pre-registration consistency.

These checks are design concepts only, not calculations.

## 19. D2-006 promotion-gate composition

Lab anti-overfit triage is upstream of D2-006.

D2-006 remains the promotion gate.

Lab triage cannot relax D2-006 thresholds.

Passing lab triage does not mean passing D2-006.

Failing lab triage may stop a variant from advisory ranking or require explicit
warning, but exact downstream handling is for WP-S2c-160.

This package modifies no D2-006 rule.

## 20. REC-5 floor preservation at variant scale

REC-5 floor discipline remains absolute.

Sweep volume must not dilute exact-segment REC-5 evidence requirements.

A variant cannot use population size or near-neighbor variants to satisfy
exact-segment evidence.

Cross-segment inference remains forbidden unless already authorized by locked
discipline.

No REC-5 rule is modified.

## 21. Relationship to WP-S2c-158 storage lock

WP-S2c-159 depends on the WP-S2c-158 complete result-population preservation
lock.

Anti-overfit review must use full population retention and canonical evidence
authority.

Intermediate result-population surfaces, if later created, remain evidence
input / index only.

No storage path, schema, query view, result surface, or artifact is created
here.

## 22. Relationship to EXP / REP, trial-log, OL / REC / DEC

EXP / REP, trial-log, OL, REC, and DEC remain canonical evidence and decision
surfaces.

Anti-overfit design may later consume references to those surfaces.

It does not create or modify any canonical artifact.

It does not create a parallel decision store.

## 23. Relationship to WP-S2c-160 advisory ranking artifact

WP-S2c-160 should design how anti-overfit / DSR outputs are represented in an
advisory ranking artifact.

WP-S2c-160 must preserve non-authority framing.

WP-S2c-159 does not create an advisory ranking artifact.

WP-S2c-159 does not rank variants.

## 24. Deferred implementation details

The following details are explicitly deferred:

- DSR formula implementation;
- exact multiple-testing denominator;
- exact triage thresholds;
- exact robustness metrics;
- exact ranking inputs;
- exact score definitions;
- schema fields;
- validators;
- query views;
- storage paths;
- artifacts;
- examples / fixtures;
- code / tests / tools;
- parser / compiler;
- implementation.

## 25. Rejected and out-of-scope alternatives

DSR on only the best variant is rejected because it hides multiple-testing
exposure.

Winner-only result review is rejected because it creates survivorship bias and
weakens source-of-truth discipline.

Post-hoc threshold changes are rejected because they weaken anti-overfit
control.

Lab triage replacing D2-006 is rejected because D2-006 remains the promotion
gate.

REC-5 dilution by sweep volume is rejected because exact-segment evidence
discipline must hold.

Ranking-as-authority is rejected because advisory ordering cannot execute
human gates.

Automatic promotion is rejected because permanent human gates and protected
boundaries remain in force.

Implementation before WP-S2c-164 authorization is rejected because the lab
design tranche has not authorized implementation.

Track 3 / AUTO reactivation is rejected because those paths remain paused or
frozen.

Paper/live bridge or runtime contact is rejected because protected runtime
boundaries remain strict.

## 26. Protected boundaries

This design explicitly preserves:

- permanent human gates;
- WP-S2c-100 locked criteria;
- D2-006;
- D2-007;
- REC-5 floor discipline;
- Phase 9 / D2-011 pre-registration discipline;
- Scope 6 discipline;
- WP-S2c-113 Scope 6 lock;
- WP-S2c-114 schemas;
- WP-S2c-115 validators;
- WP-S2c-117 query views;
- WP-S2c-151 Strategy DSL / Strategy Spec lock;
- WP-S2c-158 variant/storage lock;
- Phase 1 paper runtime;
- D-0001 hard risk caps;
- D2-008 overlay semantics and output set;
- OMS / reconciliation / kill-switch / safe-mode;
- SignalProvider Protocol;
- Tier 4 boundaries;
- `lib/`, `src/`, `configs/`, `.claude/`, and `data` protected paths;
- AUTO frozen status;
- A2C-003 unauthorized status;
- C/F deferred and A/D/E rejected;
- Track 3 paused;
- WP-S2c-140 onward deferred, not rescinded.

## 27. Stop conditions

Stop if any content creates formula implementation, DSR calculation code,
ranking/scoring code, schema, validator, query view, parser/compiler, fixture,
storage path, artifact instance, variant manifest, sweep plan, run manifest,
result population, metrics table, EXP, REP, trial-log row, OL, REC, DEC, or
implementation.

Stop if any content runs backtests, sweeps, optimizations, parameter searches,
result aggregation, DSR/statistical calculations, runner commands,
local-run-registry writes, local-sweep-result writes, or query-output packages.

Stop if any content modifies or weakens D2-006, D2-007, REC-5, Phase 9 /
D2-011, Scope 6, WP-S2c-151, WP-S2c-158, or permanent human gates.

Stop if any content treats anti-overfit triage or DSR as candidate approval,
ranking authority, recommendation authority, promotion authority, readiness
authority, transition authority, paper/live authority, runtime authority, or
automatic gate satisfaction.

Stop if any content permits runtime contact, broker/exchange/order contact,
network contact, file-writing commands, protected-path contact, Track 3
reactivation, AUTO bridge reactivation, paper bridge work,
monitoring/dashboard work, A2C-003, C/F, or A/D/E.

Stop if validation fails.

## 28. Validation posture

Validation profile is CS12 T1-doc-narrow.

Validation requires exact changed-file scope.

Integrity views and validators should run per doc-narrow convention.

No full pytest is required unless repo-local convention or validation issues
require it.

## 29. Non-authority boundary

This design creates no strategy authority, recommendation authority, approval
authority, runtime authority, paper/live authority, ranking/scoring authority,
promotion authority, transition authority, readiness authority, implementation
authority, or human-gate execution authority.

It is diagnostic design only.

## 30. Next-package posture

After merge, the default next sequential package is WP-S2c-160 advisory ranking
artifact design, unless Main/Karl directs otherwise.

WP-S2c-160 is not Karl-gated.

Do not draft implementation packages.

Do not draft Track 3 continuation packages.

Do not draft schema/validator/parser/compiler/query-view packages.
