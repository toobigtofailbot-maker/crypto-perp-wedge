# Repo Truth Discovery

Package: WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01

Base commit: `ca3916a5b5d68e8239ec5753d2a27bd4bcea3632`

Merged prerequisite PRs observed: #577, #578, #579, #580 artifacts present on refreshed main.

Frozen hypothesis id: H-FUNDING-FADE-RISKMANAGED-01

Frozen window: 2024-01-01T00:00:00Z inclusive through 2025-01-01T00:00:00Z exclusive; warmup no later than 2023-07-05T00:00:00Z.

Frozen risk-control states: no_atr, atr_20, atr_30.

Frozen denominator count: 108 unique rows, 36 per risk state.

Data-prep readiness state: ready; funding-feature CSV present locally, ignored, checksum `70cbe2040c8fb5987b2971a13c8bd4f66e91152331d5b641d684673364be3931`.

Karl sign-off authorization source: operator authorization in attached execution package for this WP, after frozen content sign-off packet was surfaced.

Execution route selected: six exit-mode-decomposed runner invocations using runner-compatible scratch copies, then selected-row denominator reconstruction.

Repo-truth adjustments made: runner-compatible scratch copies stripped planning wrapper fields, mapped descriptive frozen variant IDs to schema-valid runner IDs, normalized metadata enum values, and kept 36-row sub-run committed denominators so runner validation preserved excluded rows. No signal/risk/window/sizing/data parameters changed.
