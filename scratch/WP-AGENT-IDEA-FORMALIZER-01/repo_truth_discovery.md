# WP-AGENT-IDEA-FORMALIZER-01 Repo-Truth Discovery

## Facts

- Base: refreshed `origin/main` at `ba116f6` after PR #543 merged.
- ToolContext lives in `tools/agent_sandbox/tool_context.py`; permissions live in
  `tools/agent_sandbox/permissions.py`; audit sinks live in
  `tools/agent_sandbox/audit.py`.
- `ToolContext.run_allowed()` audits an action before invoking its operation.
  `BlockedActionError` preserves the blocked audit record. The merged role
  taxonomy already includes `idea_formalizer` with safe repo reads and scoped
  scratch writes.
- The existing deterministic intake path is
  `tools/research_workflow/formalize_research_idea.py`, backed by
  `tools/research_workflow/validate_research_idea.py`. It accepts structured
  JSON or conservative plain text and emits scratch-only research-idea and
  workflow-input artifacts.
- The merged idea formalizer has no provider seam and explicitly records that
  no live LLM/API abstraction exists.
- Data availability truth is the catalog at
  `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`,
  validated by `tools/registry/validate_data_feature_availability.py`.
- Taker flow has a conditional `FULL_HISTORY_PUBLIC_ARCHIVE` trade/archive
  derivation. Open interest is snapshot/recent-only and requires vendor or
  captured history. Long/short ratios are recent-only public REST.
  Liquidation volume is not compiler-visible and is vendor-only for history.
- Compiler indicator capability is declared in
  `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`.
- Strategy Spec validation is provided by
  `tools/registry/validate_strategy_specs.py`; the schema is
  `research/schemas/strategy_spec.schema.json`.
- The SMA/stddev mean-reversion family in
  `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json` is a valid
  merged template for a narrowly matching scratch draft.
- `pyproject.toml`, `requirements.txt`, and `requirements.lock.txt` contain no
  OpenAI, Anthropic, Claude, or general LLM SDK dependency. No dependency
  addition is required or safe for this package.

## Decision

- Add only active-WP scratch reads and read-only Strategy Spec validation to
  the existing `idea_formalizer` role.
- Keep all provider behavior offline. `fake_offline` is deterministic;
  `chatgpt_account_packet` only writes an operator packet and imports a local
  response after schema validation.
- Read capability and availability catalogs through ToolContext. Write only
  beneath `scratch/WP-AGENT-IDEA-FORMALIZER-01/`.
- Produce a Strategy Spec draft only for the merged SMA/stddev mean-reversion
  family; other accepted ideas remain structured advisory objects with an
  explicit draft blocker.

## Non-Authority

This note and every output from this package are scratch-only, non-canonical,
advisory, and grant no candidate, evidence, promotion, paper/live, runtime, or
execution authority.
