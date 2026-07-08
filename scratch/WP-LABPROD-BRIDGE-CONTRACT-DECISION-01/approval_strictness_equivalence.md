# Approval Strictness Equivalence

## Question

Can the additive Karl exact-content product-mode approval path be shown at least as strict as the existing legacy operator bridge approval path?

## Verdict

`strictness_verdict`: `as_strict_or_stricter_if_implemented_as_specified`

## Comparison

| Dimension | Legacy bridge approval | Proposed product bridge-preparation approval | Strictness result |
|---|---|---|---|
| Actor identity / signer | `approved_by = operator` | `approved_by = Karl` | stricter |
| Approval scope | `noncanonical_scratch_runner_bridge_only` | bridge-specific product preparation-only scope | at least as strict if distinct |
| Exact statement requirement | none beyond scope fields | exact approval statement required | stricter |
| Source artifact binding | colocated prefix and source formalizer run id | source product packet path/hash and formalizer output path/hash | stricter |
| Source artifact hash binding | not required | required | stricter |
| Approval artifact hash binding | not required | required | stricter |
| Timestamp requirement | nonempty timestamp | timestamp plus stale approval rejection | stricter |
| Source run / pipeline run identity | source formalizer run id | source formalizer run id plus product/pipeline run id | stricter |
| Bridge stage identity | implicit bridge scope | explicit bridge preparation stage identity | stricter |
| Non-inferability from broad prereg approval | not applicable | broad prereg approval rejected unless bridge-specific marker exists | stricter |
| Explicit false authority flags | limited non-authority flags downstream | explicit false runner/canonical/candidate/runtime/scheduler/provider/dependency/protected flags | stricter |
| Rejection of broad approvals | legacy rejects wrong scope | product mode rejects wrong scope and broad false-flag drift | stricter |
| Rejection of legacy approval in product mode | not applicable | required | stricter |
| Rejection of product approval in legacy mode | current legacy rejects Karl shape | must remain unchanged unless separately authorized | unchanged/strict |
| Stale approval rejection | not present | required | stricter |
| Path-prefix binding | formalizer prefix and approval colocated | product scratch source/output prefix binding | at least as strict |
| Output-root binding | active WP output root | product package-local output root | at least as strict |
| Runner authority flag | runner allowed by legacy bridge path when unblocked | runner authority explicitly false | stricter for product preparation |
| Canonical/candidate/paper-live/runtime/scheduler/notification/provider/dependency flags | indirectly prohibited by ToolContext/non-authority | explicit false flags required | stricter |
| Audit evidence | ToolContext audit on allowed/blocked actions | ToolContext audit plus approval/path/hash validation evidence | stricter |

## Weaknesses Found

- No product-mode approval implementation exists today.
- Exact stale-approval window is an open Karl decision.
- Exact product-mode approval schema name and statement text are open Karl decisions.
- Exact product-mode WP allowlist is open Karl decision.

These are not weaknesses in the proposed strictness if implemented as specified. They are future implementation blockers if left undefined.

## Required Future Tests

- Product mode accepts only Karl approval.
- Product mode rejects legacy operator approval.
- Product mode rejects broad pipeline prereg approval without bridge-specific marker.
- Product mode rejects wrong scope.
- Product mode rejects wrong exact statement.
- Product mode rejects missing or stale timestamp.
- Product mode rejects source product packet hash mismatch.
- Product mode rejects source formalizer output hash mismatch.
- Product mode rejects approval artifact hash mismatch.
- Product mode rejects source run / pipeline run / bridge stage mismatch.
- Product mode rejects path-prefix and output-root mismatch.
- Product mode rejects `authorizes_runner_execution = true`.
- Product mode rejects canonical/candidate/paper-live/runtime/scheduler/notification/provider/dependency/protected authority.
- Legacy mode continues to reject product approval unless explicitly authorized by a separate decision.
- Audit records prove rejected approvals fail closed.

## Required Future Blockers

- Block implementation if stale approval semantics are not specified.
- Block implementation if product mode can infer bridge approval from broad prereg approval.
- Block implementation if product mode accepts legacy approval.
- Block implementation if legacy mode starts accepting product approval without explicit authorization.
- Block implementation if hash binding cannot be validated.
- Block implementation if runner or protected authority flags are not explicit false values.

## Result Fields

```json
{
  "strictness_verdict": "as_strict_or_stricter_if_implemented_as_specified",
  "weaknesses_found": [
    "No product-mode implementation exists today.",
    "Exact stale-approval window remains a Karl decision.",
    "Exact approval schema name, statement text, and product WP allowlist remain Karl decisions."
  ],
  "required_future_tests": [
    "reject legacy approval in product mode",
    "reject broad prereg approval in product mode",
    "reject stale approval",
    "reject source or approval hash mismatch",
    "reject runner/canonical/candidate/runtime/scheduler/provider/dependency authority",
    "preserve legacy approval behavior unchanged"
  ],
  "required_future_blockers": [
    "missing stale-window decision",
    "approval inferable from broad prereg",
    "legacy approval accepted in product mode",
    "hash binding absent",
    "runner authority not explicit false"
  ]
}
```
