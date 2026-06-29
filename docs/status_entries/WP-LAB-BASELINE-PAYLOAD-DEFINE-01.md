# WP-LAB-BASELINE-PAYLOAD-DEFINE-01 Status

## Decision

Complete. This package defines non-promotable baseline construction payloads for later research-lab validation. It uses a contract-only route and creates no executable strategy artifacts.

## Repo Truth

- Branch: `lab/baseline-payload-define-01`.
- Base commit: `b060059fcd09de790344e8c3336ef27711527162`.
- Required PR #582 artifacts are present on refreshed `main`.
- Existing supported primitive family selected: SMA / StdDev price-only closed-condition vocabulary.
- Existing construction/non-promotable exact-field idiom: not found in Strategy Spec / Variant Manifest / Sweep Plan schemas.
- Current schemas use `additionalProperties: false`, so exact required provenance fields cannot be inserted without schema changes.

## Delivered Artifacts

- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/repo_truth_discovery.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_ground_truth_contract.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/non_promotable_provenance_contract.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/later_consumer_map.md`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/blocked_or_deferred_requirements.json`
- `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/validation_summary.txt`

## Baselines Defined

- `known_losing_baseline`: deliberately non-edge, high-cost/gate-failing reference signal using existing SMA crossover vocabulary.
- `known_neutral_or_no_trade_baseline`: no-trade or near-neutral reference signal using existing SMA / StdDev vocabulary.
- `known_degenerate_or_invalid_baseline`: invalid/blocked denominator-preservation reference payload using existing SMA parameter-constraint semantics.

## Provenance And Guardrails

Each baseline is permanently construction-only and non-promotable:

- `construction_payload`: true
- `non_promotable`: true
- `candidate_eligible`: false
- `promotion_eligible`: false
- `paper_live_eligible`: false
- `edge_claim_allowed`: false
- `canonical_crossing_allowed`: false

Later gates, crossing/candidate machinery, dashboards, reports, and agent loops must reject these payloads by construction. Any attempt to promote, cross, register, rank as edge, paper-trade, live-trade, or remove these flags is a lab defect.

## Schema Artifact Decision

No scratch Strategy Spec, Variant Manifest, or Sweep Plan drafts were created. Current schemas cannot carry the exact permanent construction-only fields without schema changes, and schema changes are forbidden in this package.

## Remaining Side 12 Lab Capabilities Not Completed By This Package

This package defines construction payloads only and does not complete:

- idea intake
- automatic strategy formalization from arbitrary ideas
- variant generation at scale
- data-availability classifier
- strategy-family routing
- large-scale batch sweeps
- mature WFO/OOS implementation
- mature Monte Carlo/robustness implementation
- anti-overfit review across full populations
- run registry / result-store maturity
- daily/weekly operator briefs
- rich dashboards across strategy details, sweeps, MC, WFO, blockers, and agents
- bounded research-agent scheduling/prioritization
- notifications
- candidate lifecycle gate maturity
- real candidate crossing
- paper/live path

Lab declared finished: false.

## Validation

Validation commands were run after artifact creation and recorded in `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/validation_summary.txt`.

Full pytest was not run because this is a definition-only package and no code changes are authorized.

## Boundary Check

- No strategy run executed.
- No backtest run executed.
- No canonical Result Population written.
- No candidate lifecycle write.
- No candidate-review packet created.
- No crossing or promotion.
- No paper/live/runtime work.
- No OMS/risk/reconciliation/order/exchange path touched.
- No private provider/API access.
- No data committed.
- No code, schema, validator, runner, query-layer, dashboard, or lab-state behavior changed.
