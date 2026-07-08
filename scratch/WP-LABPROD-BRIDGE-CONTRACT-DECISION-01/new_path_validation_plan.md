# New-Path Validation Plan

## Purpose

This plan defines how a future implementation would validate product-mode bridge preparation.

## Required Tests

1. Product mode requires a product-specific ToolContext/WP allowlist.
2. Product mode rejects unsupported WP IDs.
3. Product mode requires Karl exact-content bridge-preparation marker.
4. Product mode rejects legacy operator approval.
5. Product mode rejects broad lab pipeline prereg approval when bridge-specific marker is absent.
6. Product mode rejects stale approval.
7. Product mode rejects source formalizer hash mismatch.
8. Product mode rejects approval artifact hash mismatch.
9. Product mode rejects source product packet hash mismatch.
10. Product mode rejects wrong bridge stage identity.
11. Product mode rejects broad or true runner authorization.
12. Product mode rejects canonical/candidate/paper-live/runtime/scheduler/notification/provider/dependency/protected authority.
13. Product mode validates source formalizer output through bridge-owned contract checks.
14. Product mode validates generated Strategy Spec through bridge-owned validator calls.
15. Product mode validates generated Variant Manifest and Sweep Plan through bridge-owned validator calls.
16. Product mode writes only product package-local scratch outputs.
17. Product mode never invokes runner.
18. Product mode cannot access `RUN_NONCANONICAL_OFFLINE_SWEEP` unless separately authorized by a future runner package.
19. Product mode records denominator ledger fields.
20. Product mode records human review packet fields.
21. Product mode records explicit non-authority fields.
22. Product mode records audit trail for approval/path/hash validation.
23. Product mode failure leaves no partial authoritative artifacts.
24. Product mode failure leaves no canonical artifacts.
25. Product mode failure leaves no runner artifacts.

## Required Artifact Checks

- Source product packet path is product-local.
- Source product packet hash matches approval marker.
- Source formalizer output path is product-local.
- Source formalizer output hash matches approval marker.
- Product approval marker path is product-local.
- Product approval marker hash is recorded.
- Output root is product-local.
- Denominator ledger preserves all generated rows.
- Review packet states runner was not invoked.
- Non-authority assertions are explicit false for protected authority.

## Required Negative Tests

- wrong actor;
- wrong scope;
- wrong statement;
- missing timestamp;
- stale timestamp;
- mismatched source run id;
- mismatched pipeline/product run id;
- mismatched source hash;
- mismatched approval hash;
- approval authorizes runner;
- approval authorizes canonical write;
- approval authorizes candidate lifecycle;
- approval authorizes paper/live/runtime;
- approval authorizes scheduler/autonomy;
- approval authorizes notifications;
- approval authorizes provider/API/credentials;
- approval authorizes dependency/config/data acquisition;
- approval authorizes protected-path touch;
- source path outside product scratch;
- output root outside product scratch.

## Validation Status

`new_path_validation_plan_status`: `specified_for_future_implementation_not_executed_here`
