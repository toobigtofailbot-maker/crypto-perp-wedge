---
name: result-population-critic
description: Critique Result Populations without decision authority.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [research, critique, result-population]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# Result Population Critic

## When to use

Use for descriptive criticism of an existing canonical Result Population.

## Procedure

1. Resolve the exact `evidence://result-population/RP-NNNN` resource.
2. Run only `result-population-overview` and
   `result-population-denominator` when aggregate context is needed.
3. Check denominator preservation, outcome counts, parent lineage, offline and
   non-authority flags, data coverage, and explicit error rows.
4. Separate observed FACT from INFERENCE and OPEN QUESTION.
5. Withhold any metric, per-trade claim, robustness claim, or causal claim not
   present in the exact evidence.

## Forbidden conclusions

Do not emit approval, recommendation, promotion, readiness, freeze, dispatch,
execution, or trading-language authority. Do not edit or recreate a Result
Population. Do not treat a positive metric as sufficient scientific evidence.
This skill cannot self-enable any broader capability.

## Verification

The critique cites exact artifact and query evidence at one repo SHA and labels
all unsupported claims UNKNOWN.
