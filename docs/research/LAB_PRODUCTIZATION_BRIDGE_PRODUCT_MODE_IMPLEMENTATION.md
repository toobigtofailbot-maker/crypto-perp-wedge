# Lab Productization Bridge Product Mode Implementation

## Summary

This package adds an explicit, opt-in `product_bridge_prepare_only` mode to `tools/research_agents/formalizer_runner_bridge.py`. Legacy bridge behavior remains the default `legacy_bridge_run` path.

Product mode validates a Karl bridge-specific exact-content approval marker, product-local source paths, product-local output root, source/product/formalizer hashes, run and stage identity, and required authority flags. It derives and validates scratch-only Strategy Spec, Variant Manifest, Sweep Plan, denominator ledger, and human review packet artifacts through the existing bridge-owned validators, then stops before runner execution.

## Karl Stale-Approval Decision

For this package, stale approval rejection is content-bound rather than wall-clock-bound. A timestamp is required for audit, but expiry is determined by exact hash/path/run/stage/authority-field binding, not elapsed time.

No 24-hour, same-day, execution-start, git-time, or environment-clock freshness rule is implemented.

## Product Approval Contract

Product bridge preparation requires:

- `schema_version = product_bridge_preparation_approval_v1`
- `approved_by = Karl`
- `approval_scope = noncanonical_product_bridge_preparation_only`
- exact approval statement
- parseable UTC-like `approval_timestamp_utc`
- source product packet path and SHA256
- source formalizer output path and SHA256
- reproducible approval marker content hash
- source formalizer run id
- product pipeline run id
- bridge stage identity `bridge_spec_variant_sweep_preparation`
- product-mode output root
- `authorizes_bridge_preparation = true`
- false runner, canonical, candidate, paper/live/runtime, scheduler/autonomy, notification, provider/API/credential, dependency/config/data, and protected-path authority flags

Broad lab prereg approval and legacy operator approval are rejected in product mode.

## Prepare-Only Boundary

Product mode does not call `_invoke_runner`, does not call `run_offline_sweep`, and does not request `RUN_NONCANONICAL_OFFLINE_SWEEP`. Review packets explicitly record `runner_invoked = false` and `runner_boundary = not_requested`.

## Legacy Preservation

The legacy bridge path remains the constructor default and keeps the existing ToolContext WP allowlist, approval parser, source-prefix validation, output-root derivation, validator calls, runner invocation behavior, denominator schema, and review packet schema.

The legacy config dataclass was not extended, preserving `config.__dict__` in the legacy run identity hash. A focused byte-regression test pins the pre-change deterministic legacy run id, artifact paths, artifact hashes, trial counts, and runner audit count.

## Non-Authority

This implementation adds no runner adapter, WFO/OOS execution, robustness execution, candidate-review execution, canonical evidence write, candidate lifecycle write, crossing, promotion/readiness, paper/live/runtime contact, scheduler/autonomy, notification firing, provider/API/credential use, dependency/config/data acquisition, or protected-path authority.
