# WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01 Branch State

## Scope Summary

Adds one deterministic Donchian/channel-breakout formalizer and bridge adapter. It produces validator-clean scratch Strategy Spec, Variant Manifest, and Sweep Plan artifacts, then exercises the existing real offline runner with full denominator retention. It creates no canonical or execution authority.

Branch: `agent/adapter-donchian-family-01`.
Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\agent-adapter-donchian-family-01`.
Base: refreshed `origin/main` at `fa1994d` after PR #555 merged.

## Main Authorization

Main authorized one structurally distinct family adapter after the existing machine proved limited to STRAT-SPEC-0003 SMA/stddev semantics. The package permits scratch-only formalization, VM/Sweep derivation, real offline runner smoke, tests, proof artifacts, and this status entry. Canonical crossing, lifecycle, promotion/readiness, protected trading paths, provider/API/network calls, and compiler/runner semantic changes remain forbidden.

## Repo-Truth Discovery

Merged repo truth contains the required Donchian primitive and grammar. It also corrects the package premise: Donchian is not an unconcluded archetype. H-002/REP-0003 is a concluded Donchian `NO-GO`, and H-012/REP-0032 includes a funded Donchian test and pure comparator. No Donchian canonical Result Population exists under `research/result_populations/`. This package therefore claims adapter breadth only, not family novelty or fresh research evidence.

## Donchian Compiler / Grammar Support

The active indicator catalog binds `donchian` to `donchian_v1`, accepts integer `lookback_bars >= 1`, and exposes `upper`, `lower`, `mid`, `width`, and causal lagged equivalents. The adapter uses `upper_lag1` and `lower_lag1` with existing `gt`/`lt`, parameter-bound lookbacks, explicit long/short groups, and side-specific exits. No schema, validator, compiler primitive, operator, runner, or backtester semantics changed.

## Formalizer Adapter

The formalizer recognizes the unambiguous `donchian_channel_breakout_v1` family, emits a both-direction completed-bar breakout draft with opposite-channel exits, records source idea/data/non-authority/freshness metadata, and validates the scratch draft. Mixed Donchian plus SMA/stddev declarations do not resolve to either adapter.

## Bridge Adapter

The bridge dispatches only validated Donchian drafts for this active WP, verifies Donchian-only indicator references, derives family-specific scratch VM/Sweep inputs, invokes the real offline runner, and reconciles the written run with a direct manual-equivalent run. Existing SMA/stddev behavior remains covered by regression tests.

## Bounded Grid / Sweep Contract

The only free parameter is `channel_lookback_bars` with the fixed manual grid `[20, 55]`. The committed/selected/multiple-testing denominator is 2. Adaptive search and post-hoc narrowing are false. Funding cost mode is explicit and defaults to off.

## Freshness / Distinctness Checks

The generated Strategy Spec differs from STRAT-SPEC-0003 and contains no SMA/stddev indicator refs. `VM-9771` and `SWEEP-PLAN-9771` differ from VM-0003/SWEEP-PLAN-0003 in IDs, search family, axis, assignments, and denominator. Tests reject SMA-only use of the Donchian WP, ambiguous family declarations, and mutated SMA refs in a Donchian draft.

## Smoke Runner Result

Formalizer run `cb9be3bae086` and bridge run `7f62785b9cd2a5d2` completed against a deterministic scratch 15m OHLCV fixture. Both variants completed, all direct-reconciliation comparisons matched, and the scratch runner wrote `RP-3248` beneath the active WP prefix. Any metrics are fixture-specific adapter-smoke output and carry no GO/NO-GO meaning.

## Denominator Preservation

The ledger declares and retains exactly two rows: 2 completed, 0 failed, 0 invalid, 0 pruned, and 0 blocked. The bridge mapping retains every native runner outcome class and the ToolContext suppression path remains hard blocked.

## Missing Capabilities

The adapter intentionally omits intrabar breakout, ATR stop/target, time/session exit, funding signals, multi-timeframe confirmation, and any new compiler semantics. The downstream robustness diagnostician and candidate-review packet preparer remain bound to the original bridge prefix/SMA family and were not expanded because this package ends at runner-smoke proof.

## ToolContext Boundary

The existing role permissions are reused with active-WP path scoping; no permission table change was needed. Donchian formalizer and bridge reads/writes remain under `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/`. Tests cover canonical artifacts, trial log, crossing, lifecycle/readiness, runtime/paper/live, OMS/risk/reconciliation/capital, private/credential, provider/API/network, and evidence-suppression prohibitions.

## Validation Status

- Formalizer/bridge/ToolContext regressions: 141 passed.
- Donchian adapter tests: 29 passed.
- Result Population/data-feature/candidate-registry validator tests: 88 passed.
- Candidate registry, Result Population, and data-feature registry validators: passed.
- Query view discovery: 124 views listed.
- Full pytest initially exposed only the known absent gitignored D4A normalized fixture. After a hash-verified validation-only copy from the root checkout, full pytest passed: 2215 passed, 1 skipped, 6 warnings. The copy was removed afterward. The final provider-scope cleanup restored the provider file and moved identical Donchian-bound normalization into the formalizer; afterward the exact focused suites passed (141 and 29) and scratch hashes remained stable.
- Diff-scope summary: intended code, test, status, and active-WP scratch files only; no forbidden-path match.
- `git diff --check`: passed.

## Boundary Summary

No canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial log, registry, or crossing output was written. No candidate registration/promotion/freeze/readiness action is possible. No paper/live/runtime, OMS/risk/reconciliation/capital, broker/exchange/order, config, dependency, canonical/cataloged data, private endpoint, credential, provider/API/network, compiler, schema, validator, query, runner, or backtester semantic surface changed.

## Non-Authority Statement

All outputs are scratch-only, non-canonical, non-evidence, not candidate authority, not promotion/readiness authority, not paper/live/runtime authority, and human-review-required. The smoke does not reopen or reinterpret earlier Donchian conclusions.

## Follow-On Research WP

`WP-RESEARCH-EDGE-DONCHIAN-01` remains separate and is not authorized or executed here. Because prior Donchian evidence exists, any follow-on must define a genuinely distinct preregistered hypothesis and address that repo truth explicitly.
