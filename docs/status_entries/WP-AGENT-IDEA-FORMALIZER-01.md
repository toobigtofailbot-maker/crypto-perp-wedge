# WP-AGENT-IDEA-FORMALIZER-01 Branch State

## Scope Summary

Adds the first bounded idea-formalization research agent. It converts a human
idea into a structured scratch-only research object, assesses merged compiler
and data-availability truth, optionally creates a validator-clean scratch
Strategy Spec draft for the exact merged SMA/stddev mean-reversion family, and
produces a human-review packet. It has no execution or canonical authority.

Branch: `agent/idea-formalizer-01-provider-flex`.
Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\agent-idea-formalizer-01-provider-flex`.
Base: refreshed `origin/main` at `ba116f6` after PR #543 merged.

## Main Authorization

Main authorized `WP-AGENT-IDEA-FORMALIZER-01` as the first real bounded
research agent. The active provider-flexible execution package authorizes the
repo-native ToolContext integration, offline fake provider, operator-mediated
ChatGPT packet flow, scratch outputs, focused cage extension, tests, and this
status entry. It does not authorize canonical, execution, or protected-path
work.

## Provider Flexibility Posture

`ReasoningProvider` defines the provider seam. Selection is configuration
driven through `provider_mode` and `provider_id`; agent semantics do not depend
on a specific vendor. `fake_offline` and `chatgpt_account_packet` are active.
`openai_api_disabled`, `anthropic_api_disabled`, and `local_model_disabled`
are explicit fail-closed future placeholders.

No OpenAI, Anthropic, Claude, LangChain, or other provider SDK was added. No
API key, credential, live model call, or network call is required.

## Initial ChatGPT Account-Mediated Mode

`chatgpt_account_packet` writes a compact Markdown packet beneath the active
WP scratch prefix. Karl can use that packet in account-authenticated
ChatGPT/Codex manually. A response may be imported only from the active scratch
prefix. The importer requires the exact inline JSON schema, matching request
ID, matching bounded symbol/timeframe, and features already detected from the
operator idea. No OpenAI API call occurs.

## ToolContext Integration

Every agent repo read, output write, provider-response import, and Strategy
Spec validation is routed through `ToolContext`. The existing
`idea_formalizer` role gains only:

- reads beneath its own active-WP scratch prefix;
- the existing read-only registry-validator action.

Writes remain limited to `scratch/WP-AGENT-IDEA-FORMALIZER-01/`. Canonical,
dependency, project-status, network, credentials, private endpoints,
candidate lifecycle, backtest/sweep, evidence suppression/deletion, provider
memory, and protected trading actions remain hard blocked and audited.

## Reasoning Provider Interface

The provider contract contains `build_request`, `complete`, and
`parse_response`. Provider responses are advisory data. They must pass the
closed inline JSON schema and bounded-context checks before the agent uses
them. `fake_offline` is deterministic and rule based. The ChatGPT adapter is a
packet/import mechanism only.

## Input / Output Contract

Input includes plain-English idea, symbol, locked timeframe, optional operator
constraints, and selected provider configuration. Output includes provider
metadata, structured research object or rejection reasons, capability and
historical-testability assessment, draft status/blockers, human-review packet,
and explicit non-authority flags.

Run IDs are stable hashes of bounded input and provider configuration. Outputs
are placed only under the package scratch directory.

## Data Availability Checks

The agent reads the merged indicator and data-feature availability catalogs
through ToolContext. It distinguishes compiler visibility from historical
testability and handles the required classes:

- taker flow: conditional full-history public trade/archive derivation;
- open interest: snapshot/recent-only and vendor/capture constrained, never
  reconstructed from trades;
- long/short ratio: recent-only public REST and vendor/capture constrained;
- liquidation volume: not compiler visible and vendor-only for history;
- OHLCV indicators: available when source bars and merged indicator entries
  exist.

Ideas blocked on data return `needs_data` with explicit feature blockers.

## Draft Strategy Spec Behavior

The only implemented draft adapter is the exact merged SMA/stddev
mean-reversion family represented by `STRAT-SPEC-0003`. The agent copies that
merged capability shape into active-WP scratch, resets status/review/hash and
pre-registration fields to draft/non-authoritative values, records provider
metadata in provenance constraints, and runs the existing Strategy Spec
validator through ToolContext.

No adapter is invented for other primitive families. Those ideas receive a
structured adapter blocker rather than an invalid canonical-looking draft.

## Rejection Behavior

The deterministic provider rejects non-causal or primitive-free ideas. The
orchestrator rejects malformed, mismatched, or unsupported provider responses.
Requests for canonical writes, candidate lifecycle actions, execution,
protected paths, credentials, private endpoints, evidence hiding/deletion,
ToolContext bypass, provider memory as repo truth, or live APIs are rejected
with the blocked ToolContext audit record preserved in the review packet.

## Adversarial Boundary Tests

Tests cover canonical Strategy Spec and Result Population writes, promotion,
freeze, registration, backtest, sweep, global funding-mode mutation, private
endpoints, credentials, live provider APIs, runtime/live, OMS/risk, failed
variant suppression, evidence deletion, ToolContext bypass, and provider
memory. They assert blocked audit decisions, no canonical mutation, and no
allowed network action.

## Validation Status

- Ruff format/check for changed Python: PASS.
- Provider-flex and ToolContext tests: PASS, 99 tests.
- Strategy Spec and data-availability regression tests: PASS, 110 tests.
- Strategy Spec validator: PASS.
- Data feature availability validator: PASS.
- Result Population validator: PASS.
- Query view discovery: PASS; all views listed.
- Ambient Python 3.14 full pytest: collection blocked by 24 missing-dependency
  errors for `binance`, `pandas`, and `numpy`; not passing evidence.
- Repo-venv Python 3.11 full pytest: baseline-limited, 2,000 passed, 1 skipped,
  1 failed, and 6 warnings in 1,422.24 seconds. The sole failure is
  `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage`
  because the known gitignored isolated-worktree D4A normalized-data fixture
  is absent (`normalized_data_local_exists` is false). This is unrelated to
  the package diff.
- Diff-scope summary: PASS; eight intended files and no forbidden-path match.
- `git diff --check`: PASS.

## Boundary Summary

Changed implementation is limited to `tools/research_agents/`, the narrow
ToolContext policy extension, tests, package scratch discovery note, and this
status entry. No schema, validator behavior, query layer, dependency file,
canonical artifact, config, compiler, runner, backtester, runtime, paper/live,
OMS, risk, reconciliation, capital, broker/exchange, credential, or
`docs/project_status.md` file changed.

## Non-Authority Statement

This agent and all outputs are scratch-only, draft-only, advisory, and
non-canonical. They provide no evidence, preregistration, candidate,
registration, freeze, approval, promotion, ranking, recommendation, readiness,
paper/live, runtime, risk, capital, or execution authority. Validator success
does not change that posture. Human review and separately authorized future
packages remain required.
