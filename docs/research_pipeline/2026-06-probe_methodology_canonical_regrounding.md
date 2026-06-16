# Premise Probe Canonical Regrounding

This document is a methodology guardrail. It does not mutate prior evidence, does not rerun any strategy, does not change runner/compiler behavior, does not create strategy authority, and does not authorize candidate, walk-forward, paper/live, runtime, OMS/risk, broker/exchange, or capital actions.

## Background

The 4h premise probe and canonical RP-6236 diverged because they did not test the same population. The probe used 0005 bar-count horizons directly on 4h bars, while canonical RP-6236 used the frozen 0006 horizon-rescaled grid. The canonical runner was diagnosed as sound for that diagnostic, the trend gate was applied as intended, and RP-6236 remains interpretable as valid canonical evidence for the exact frozen 0006 population.

This document locks the future methodology consequence: a premise probe may set canonical expectations only when it is canonical-equivalent. A related, useful, or promising probe that changes the population, route, data, or assumptions remains exploratory and non-gating.

## Probe Classes

| Probe class | Meaning | Can gate canonical expectations? |
|---|---|---|
| `canonical-equivalent probe` | Uses exact Strategy Spec, exact grid/VM, exact Sweep Plan, canonical runner path, exact data lineage, equivalent sizing/cost/funding assumptions | Yes, if validation passes |
| `premise-only exploratory probe` | Tests a related idea but not exact canonical population/path | No |
| `scratch feasibility check` | Verifies local feasibility, data availability, or implementation mechanics | No |
| `regression probe` | Confirms known prior behavior on exact inputs | Yes, only for that regression claim |
| `noncanonical research probe` | Any direct/custom route, altered grid, altered logic, or altered data assumptions | No |

## Canonical Expectation Requirements

Any probe used to set canonical expectations must record and match:

- Strategy Spec ID and SHA/content identity;
- Variant Manifest ID and exact selected denominator;
- Sweep Plan ID and exact selected trial set;
- data slice identity and parent lineage;
- runner path;
- signal compiler path;
- entry/exit/filter semantics;
- cost/funding/slippage/sizing assumptions;
- timeframe and annualization basis;
- full variant denominator;
- no hidden failed/no-trade/errored rows;
- command and reproducibility notes.

If any of these differ, the probe is not allowed to gate canonical expectations.

## Required Wording For Exploratory Probes

Exploratory probes must say:

```text
This probe is exploratory and non-gating. It does not establish canonical expectations and cannot justify a canonical trial, candidate route, walk-forward route, paper/live route, or strategy promotion without a canonical-equivalent probe or separately authorized canonical trial.
```

## Stop Rules

Future WPs must stop and escalate if:

- probe and canonical grid differ;
- probe and canonical runner path differ;
- probe and canonical data lineage differ;
- probe and canonical cost/funding/sizing assumptions differ;
- probe uses direct/custom code and is then treated as canonical expectation;
- aggregate metrics differ materially without explanation;
- trade counts differ materially without explanation;
- a probe is used to justify a canonical package but lacks full denominator evidence.

## Report-Back Requirement

Future premise-probe report-backs must include:

```text
Probe class:
Canonical-equivalent: YES/NO
Exact spec/grid/sweep match: YES/NO
Canonical runner path: YES/NO
Exact data lineage: YES/NO
Cost/funding/sizing match: YES/NO
Full denominator retained: YES/NO
Can gate canonical expectations: YES/NO
Reason:
```

## RP-6236 Note

This document does not annotate, correct, replace, or rerun RP-6236. The diagnostic classified RP-6236 as interpretable canonical evidence for the exact frozen 0006 population. Any future append-only annotation or replacement route would require a separate explicit package.

## Future Online Strategy Implication

The online OHLCV parameter-lock ideas remain preserved as hypotheses only. Any future ORB/no-wick/deterministic-ORB probe must use this methodology if it is expected to set canonical expectations.
