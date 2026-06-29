# Baseline Payload Catalog

This package defines non-promotable construction payloads only. The payloads are reference signals for future research-lab infrastructure validation, not strategy candidates and not evidence of edge.

## Global Provenance

- `construction_payload`: true
- `non_promotable`: true
- `candidate_eligible`: false
- `promotion_eligible`: false
- `paper_live_eligible`: false
- `edge_claim_allowed`: false
- `canonical_crossing_allowed`: false

Because current Strategy Spec / Variant Manifest / Sweep Plan schemas use `additionalProperties: false`, these exact fields are not embedded in schema-validated artifacts in this package.

## Baselines

| Baseline | Family | Known Property | Later Use | Crossing |
| --- | --- | --- | --- | --- |
| `known_losing_baseline` | SMA crossover price-only | Deliberately cost-sensitive/churn-prone losing behavior once later executed | OOS, robustness, and gate-failure plumbing | Reject by construction |
| `known_neutral_or_no_trade_baseline` | SMA / StdDev z-score price-only | No-trade or near-neutral behavior once later executed | Empty-result, denominator, dashboard no-candidate rendering | Reject by construction |
| `known_degenerate_or_invalid_baseline` | SMA parameter constraint fixture | Invalid/blocked accounting without execution | Denominator preservation and failed/invalid row retention | Reject by construction |

## Primitive Constraint

All baseline definitions stay within current price-only SMA / StdDev vocabulary already present in repo Strategy Specs and compiler-facing artifact examples. No funding, OI, taker-flow, liquidation, L2, CME, private provider, new adapter, new indicator, new strategy-family implementation, or compiler change is introduced.

## Contract-Only Route

No scratch Strategy Spec, Variant Manifest, or Sweep Plan drafts are created here. A future package may add schema-compatible drafts only after schema-level construction-payload provenance support is explicitly authorized, or after a separately approved fixture-artifact schema exists.
