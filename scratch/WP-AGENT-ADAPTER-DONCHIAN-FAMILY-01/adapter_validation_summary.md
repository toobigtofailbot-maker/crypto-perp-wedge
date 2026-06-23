# Donchian Adapter Validation Summary

## Outcome

The bounded `donchian_channel_breakout_v1` formalizer and bridge path completed end to end through the real offline runner. This is adapter-validation evidence only, not a Donchian research result.

## Proven Path

1. Deterministic fixture idea `cb9be3bae086` was accepted with detected features `donchian` and `ohlcv`.
2. Scratch draft `STRAT-SPEC-9226` validated and contains Donchian references only.
3. Scratch `VM-9771` and `SWEEP-PLAN-9771` validated with the fixed two-row lookback grid `[20, 55]`.
4. Bridge run `7f62785b9cd2a5d2` invoked `tools.research_runner.run_offline_sweep` and its direct manual-equivalent reconciliation path.
5. Both variants completed; the reconciliation comparisons all matched; the full two-row denominator was retained.

## Freshness

- Strategy semantics differ from STRAT-SPEC-0003 and contain no SMA/stddev indicator references.
- VM/Sweep IDs and parameter axes differ from VM-0003/SWEEP-PLAN-0003.
- The adapter rejects SMA-only and ambiguous Donchian-plus-SMA/stddev family declarations.
- No novelty claim is made: prior Donchian evidence exists in H-002/REP-0003 and H-012/REP-0032. No canonical Donchian Result Population was found.

## Validation

- Formalizer/bridge/ToolContext regressions: 141 passed.
- Donchian adapter tests: 29 passed.
- Result Population/data-feature/candidate-registry validator tests: 88 passed.
- Candidate registry, Result Population, and data-feature registry validators: passed.
- Query view discovery: 124 views listed.
- Full pytest: the first isolated-worktree run had only the known missing gitignored D4A fixture failure. After copying the existing root-checkout fixture with expected SHA256 `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab` for validation only, full pytest passed: `2215 passed, 1 skipped, 6 warnings`. The validation-only copy was then removed. After the final provider-scope cleanup, the exact focused suites passed (141 and 29) and scratch hashes remained stable.
- Diff-scope summary found only intended package files and no forbidden-path match; `git diff --check` passed.

## Boundary

All generated Strategy Spec, Variant Manifest, Sweep Plan, ledger, and Result Population-shaped runner outputs are beneath the active package scratch prefix. No canonical crossing, lifecycle action, runtime/protected-path action, credential/private endpoint, provider/API, or network action occurred. Funding remained explicit and off.
