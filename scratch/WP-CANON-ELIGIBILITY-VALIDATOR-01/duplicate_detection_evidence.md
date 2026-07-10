# Duplicate and freshness evidence

The scan normalizes meaningful tokens from the draft title, hypothesis, formalized summary, and features. It compares them with:

1. concluded candidate name, strategy family, differentiation summary, and timeframe;
2. Strategy Spec title, short name, entry logic, exit logic, and primary timeframe;
3. Result Population lineage descending from a matched Strategy Spec.

Every match includes source path, source SHA-256, normalized-overlap explanation, and similarity where applicable. The focused test proves detection of a known SMA-distance/mean-reversion family across a concluded candidate, `STRAT-SPEC-0001`, and `RP-2134` lineage.

Limitations: this is deterministic lexical/family proximity, not semantic embedding search. It can miss differently worded equivalents and can conservatively flag shared vocabulary. Therefore any match makes the advisory intake ineligible pending human clarification; absence of a match is not proof of novelty.
