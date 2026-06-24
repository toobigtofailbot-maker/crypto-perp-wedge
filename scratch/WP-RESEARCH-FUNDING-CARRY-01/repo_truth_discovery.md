# WP-RESEARCH-FUNDING-CARRY-01 Repo-Truth Discovery

## Funding feature and runner path

- PR #560 is merged at `8384a66`.
- The ignored 15m funding feature CSV is locally available and was copied byte-for-byte from the prior materialization worktree into this fresh worktree.
- Its SHA256 is `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`, matching the PR #560 manifest.
- `tools/research_runner/run_offline_sweep.py` collects declared non-OHLCV `data_ref` and `host_data_refs` fields, retains `funding_rate`, and emits the full-history availability claim.
- `tools/research_runner/spec_signal_compiler.py` accepts `funding_rate` as a direct `data_ref`.

## Exact hypothesis expressiveness

- The Strategy Spec grammar and compiler have no rolling empirical-percentile transform over a `data_ref`.
- `data_ref.lookback` rejects `bars_parameter_ref`; lookback binding is limited to approved `indicator_ref` entries.
- The approved indicator catalog has no funding-rate percentile indicator.
- `max_holding_period` executes in the compiler, but `max_holding_period.bars` must be a literal integer and cannot bind a Variant Manifest parameter.
- Therefore the pre-registered 3 lookbacks x 2 entry percentiles x 2 exit modes x 3 max holds (36 rows) cannot be represented honestly by the current Strategy Spec / compiler / runner contract.

Substituting absolute funding-rate thresholds, whole-sample percentiles, price-derived proxies, a trend-following direction, or a narrowed grid would change the pre-registered hypothesis or denominator. No such substitution was made.

## Formalizer and bridge

- The idea formalizer detects SMA/stddev and Donchian draft families; it has no funding-percentile family adapter.
- The bridge resolves only SMA/stddev and Donchian families and templates their VM/Sweep artifacts.
- Adding a funding adapter alone would still produce an unexecutable draft because the percentile and variant-bound max-hold semantics are absent.

## Downstream reach

- The robustness diagnostician is aggregate-row oriented and is not itself prefix-hard-coded to SMA/stddev, but it requires completed bridge rows; none can be produced here.
- The candidate-review packet hard-codes its strategy summary to the STRAT-SPEC-0003 SMA/stddev family. Genericization would be required only after runnable evidence exists and is not reached in this blocked package.

## Funding P&L

- Funding-rate data would be a signal feature only.
- Funding payments are separately controlled by `funding_cost_mode`, which remains default-off and unchanged.
- Any future run under this hypothesis must be labeled a price-P&L funding-rate signal test.

## Replay / determinism

- No committed repo-native command reconstructs RP-2592, RP-3731, or RP-7134 from pinned artifacts and compares byte or normalized hashes.
- Historical docs contain package-specific replay evidence, but not a reusable committed harness/command.
- A funding scratch population cannot be replayed because no honest funding population can be compiled.

## Exact change and forbidden scope

This branch adds blocked scratch/status documentation only. It changes no compiler, schema, validator, runner, formalizer, bridge, robustness, candidate-review, canonical artifact, trial log, lifecycle, runtime, OMS, risk, reconciliation, capital, funding accounting, fill, position, provider, API, or network path.

Repo-truth adjustment: the package expected minimal adapter work might suffice, but current merged grammar requires new rolling-percentile computation semantics and variant-bound max-hold semantics first. That is a separate design/implementation decision surface, so this execution stops fail-closed.
