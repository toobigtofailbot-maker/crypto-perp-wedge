# WP-RESEARCH-FUNDING-CARRY-01 Branch State

## Scope Summary

Attempt the first non-canonical full-denominator funding-rate positioning-fade research loop. The attempt stopped fail-closed before implementation or execution because current validated strategy semantics cannot represent the pre-registered family.

## Main / Operator Direction

The package authorized a funding-rate signal test after PR #560, with no canonical writes, crossing, candidate action, funding-P&L change, or runtime contact.

## Repo-Truth Discovery

PR #560 is present at base commit `8384a66`. The exact ignored 15m funding-feature CSV is locally available with manifest-matching SHA256 `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`. The runner preserves declared `funding_rate`, and the compiler accepts it as a direct `data_ref`.

Current grammar has no rolling empirical-percentile transform over a data-derived field. `data_ref.lookback` cannot bind a lookback parameter, and `max_holding_period.bars` cannot bind a Variant Manifest parameter. The exact 36-row pre-registered family is therefore not runnable without new grammar/compiler semantics.

## Pre-Registered Hypothesis

`H-FUNDING-RATE-POSITIONING-FADE-01`: extreme positive funding implies long crowding and a short signal; extreme negative funding implies short crowding and a long signal. Allowed variants remain 30d/90d/180d rolling percentiles, 0.90/0.95 entry thresholds, percentile-normalization or fixed-hold exits, and 16/32/96-bar maximum holds. No post-result variant was added; no results were observed.

## Funding P&L Boundary

The intended use is signal generation only. Funding payments remain separate, `funding_cost_mode` remains default-off, and no funding/cost/accounting semantics changed. Any future result is a price-P&L funding-rate signal test, not a complete carry-P&L strategy.

## Formalizer / Bridge Implementation

Blocked before implementation. A funding adapter alone cannot create an executable validated artifact while rolling-percentile and variant-bound max-hold semantics are absent. No substitute threshold, proxy, denominator narrowing, or architecture redesign was introduced.

## Runner Result

No runner invocation occurred. All 36 planned rows are recorded as blocked before VM/Sweep materialization. No Result Population was written.

## Full Denominator

The scratch denominator manifest records 36 planned, 0 complete, 0 failed, 0 invalid, 36 blocked, and 0 pruned rows. No row was hidden or narrowed.

## Robustness Diagnostics

Blocked because there are no completed result rows. No robustness conclusion was fabricated.

## Candidate-Review Packet Status

Not generated. Review-trigger conditions cannot be satisfied or evaluated without result and robustness evidence.

## RP Replay / Determinism Harness

No reusable committed repo-native replay command was found for RP-2592, RP-3731, or RP-7134. A funding replay cannot be produced without a runnable funding population. The scratch blocked report pins the funding input hash and runner commit.

## Validation Status

Documentation/JSON parse checks, required-output presence, targeted existing runner/compiler/validator tests, registry validators, research-query view listing, diff-scope summary, full pytest, and `git diff --check` are recorded in the scratch validation summary.

## Boundary Summary

No canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial log, lifecycle registry, or crossing artifact was written. No compiler, schema, validator, query, runner, backtester, funding accounting, fill, position, runtime, paper/live, OMS, risk, reconciliation, capital, credential, provider/API, network, adoption-PoC, dashboard, scheduler, or large-data tracked file changed.

## Non-Authority Statement

These scratch artifacts are `non_canonical_research_evidence`, `scratch_result_population`, `not_crossed`, `not_paper_ready`, and `not_live_ready`. They provide no execution, evidence-promotion, candidate, ranking, readiness, or trading authority.

## Research-Lab Completion Note

The Side 12 / operator research-lab target state remains incomplete. This branch adds a pre-registration, exact denominator block record, data/semantic lineage, and funding/replay boundary records; it does not add runnable funding-family semantics, a completed research population, downstream robustness evidence, a real candidate-review packet, canonical crossing, scheduler/reporting surfaces, or paper/live/runtime authority. The external-adoption track is deferred in this WP.

## Open Decision Surfaces

- Whether a separate bounded design package defines rolling empirical-percentile Strategy Spec semantics over declared data-derived fields.
- Whether maximum-hold bars become variant-bindable or the family is represented through another explicitly reviewed artifact shape.
- Whether a later implementation package adds the corresponding compiler, validator, formalizer, bridge, and replay contracts.
- Whether candidate-review family metadata is genericized after completed funding evidence exists.
