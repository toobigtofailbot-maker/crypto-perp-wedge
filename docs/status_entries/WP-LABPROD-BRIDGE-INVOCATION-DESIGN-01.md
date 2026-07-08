# WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01

## Status

Docs/design-only architecture decision complete. The package resolves the WP03
Outcome B collision on paper and recommends a deliberate additive bridge
product-mode contract plus an explicit bridge-preparation / runner-execution
split before any further product bridge adapter implementation.

## Changed Files

- `docs/research/LAB_PRODUCTIZATION_BRIDGE_INVOCATION_DESIGN.md`
- `docs/status_entries/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01.md`
- `scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/`

## Repo-Truth Discovery

The existing bridge accepts only its current ToolContext WP allowlist, validates
legacy formalizer scratch prefixes, writes under `scratch/<tool_context.wp_id>/outputs`,
requires legacy operator bridge approval, and invokes the offline runner on its
unblocked path. The lab product flow requires package-local scratch output,
Karl exact-content approval, and no runner execution for bridge preparation.

## Decision

Do not adapt the product flow by faking legacy bridge approval, legacy scratch
paths, or bridge-owned output roots. Do not reimplement bridge behavior inside
the product pipeline. A future implementation must be authorized as a
bridge-contract change that preserves legacy behavior unchanged by default,
adds a strict product-mode contract, and exposes preparation-only behavior with
runner execution separated.

## Boundary

No bridge code, adapter code, runner code, WFO/OOS code, robustness code,
candidate-review code, gate actions, dashboard/cockpit, schema, validator,
query layer, data, config, dependency, `src/`, `lib/`, `.claude/`, canonical
Result Population, candidate lifecycle, crossing, promotion/readiness,
paper/live/runtime, scheduler/autonomy, notification, provider/API/credential,
or protected path was changed.

## Validation

Validation results are recorded in
`scratch/WP-LABPROD-BRIDGE-INVOCATION-DESIGN-01/validation_summary.txt`.

## Next Authorization

Main/Karl decision is required before any implementation. The design asks for
the next authorized capsules rather than naming or drafting the implementation
work.
