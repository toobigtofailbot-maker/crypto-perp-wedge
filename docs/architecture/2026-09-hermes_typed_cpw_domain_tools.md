# Hermes Typed CPW Domain Tools

## Purpose

CPW-HERMES-01 exposes five bounded CPW research-domain transformations through
the existing Project-Evidence MCP. Hermes remains the generic reasoning and
tool-invocation runtime. It does not become the owner of CPW research meaning.
This package depends on the framework-neutral domain seams established by
CPW-MIG-01 and adds no dependency.

## Exact tool surface

The five added tools are:

1. `cpw_assess_research_capabilities`
2. `cpw_formalize_strategy_draft`
3. `cpw_build_preregistration_packet`
4. `cpw_build_approval_requirement`
5. `cpw_validate_trial_denominator`

Together with the existing manifest, resource, query, Research Memory,
dependency-watch, H2 proposal, and H2.5 prepared-payload tools, the deployed
Project-Evidence inventory is exactly 13 tools. There is no generic invocation,
path, SQL, shell, network-target, credential, output-path, or plugin surface.

## Ownership and authority

Hermes owns generic reasoning, session behavior, skill execution, and typed
tool invocation. CPW owns capability meaning, reasoned-draft constraints,
Strategy-Spec construction, preregistration meaning, approval-requirement
meaning, and full-denominator scientific accounting. Project-Evidence owns the
closed transport schemas, exact resource resolution, repo identity, artifact
hashing, and deterministic result envelope.

The returned domain transformations are authoritative as the defined CPW
semantics they compute. They are not canonical evidence and grant no canonical
write, approval, candidate/promotion, execution, scheduler/Prefect,
runtime/risk, paper/live, or capital authority. Every result declares those
non-action boundaries and has no automatic consumer.

## Evidence and determinism

Project-Evidence exposes four additional exact resources:

- `project://indicator-catalog` →
  `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `project://feature-availability` →
  `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`
- `project://strategy-spec-template` →
  `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `project://strategy-spec-schema` →
  `research/schemas/strategy_spec.schema.json`

The sidecar receives these files through exact read-only mounts. Hermes still
receives no repository mount. Each tool re-resolves every repo resource and
returns its exact resource URI, repo path, artifact SHA-256, and repo SHA.
Caller-supplied hashes and paths are unavailable. Identical strict input,
resolved evidence, and repo identity produce identical input hashes and domain
semantics; no time, randomness, process, or session value participates.

Hermes/model draft content is untrusted reasoning input, never repo evidence.
Produced Strategy-Spec drafts are validated in memory against the committed
schema and are never written by the tool.

## Single semantic owner

`formalize_reasoned_strategy_draft` in `tools.research_domain.formalization`
owns the remaining shared reasoned-draft semantics: feature-subset enforcement,
bounded symbol/timeframe checks, capability and family gating, historical-data
blockers, Donchian normalization, and funding-family dual-spec construction.
The legacy IdeaFormalizer continues to own provider calls, ToolContext,
scratch I/O, validation, CLI behavior, and its outward result envelope, but now
delegates that semantic transformation to the same pure function used by the
MCP adapter. Caller-specific provenance is explicit input to the domain owner;
the MCP does not fabricate legacy provider metadata or rewrite completed specs.

## Deployment and adjacent contracts

The Hermes control remains `v2026.8.13` / `v0.20.1` at the existing exact image
digest. `_config_version` remains 12. The sidecar copies only the
framework-neutral `tools/research_domain` package in addition to its existing
code. The ninth repo-owned skill documents the bounded workflow and cannot
self-enable tools.

H2 typed proposals and H2.5 prepared payloads retain their existing models,
serialization, outbox, and inert non-authority meaning. The merged Prefect
integration remains separate and consumes no H2.5 prepared payload. This
package invokes no Prefect flow, Search Governor, runner/backtester, CANON
writer/crossing, broker, dispatch, runtime, OMS, reconciliation, risk, or
trading surface.

HERMES-02 remains the future operational Hermes-to-typed-CPW-to-Prefect research
handoff boundary. HERMES-03 remains the future canary/version-acceptance and
generic runtime/provider-consolidation boundary. This document does not design
or authorize either package. After CPW-HERMES-01 merges, the current top-level
serialized plan returns to Side/Main and points to RESEARCH-02 next unless Karl
changes it.
