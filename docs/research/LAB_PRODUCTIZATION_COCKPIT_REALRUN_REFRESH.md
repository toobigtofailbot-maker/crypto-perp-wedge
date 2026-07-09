# Lab Productization Cockpit — Real-Run Refresh

_Package: WP-LABPROD-COCKPIT-REALRUN-REFRESH-08 (read-only cockpit refresh)_

## Purpose

The static lab product cockpit (`tools/lab_cockpit`) previously surfaced the
concluded real-traffic hypothesis batch and the legacy **spine-only** pipeline
run-state panel (`runner_invoked = false`). With the product runner adapter
(PR #623) and product gates adapters (PR #624) now merged, the product pipeline
can produce a real advisory review packet. This refresh adds a read-only panel
that displays those **real** product runs — the actual run chain, runner output,
withheld WFO/OOS + robustness posture, the advisory review packet, and an honest
candidate/no-candidate funnel.

The cockpit remains visualization only: it runs nothing, approves nothing,
executes no transition, and renders no control.

## Real product chain surfaced

```
product bridge prepare  ->  product runner adapter  ->  product gates adapters
(Strategy Spec /            (offline runner;            (WFO/OOS + robustness +
 Variant Manifest /          Result Population;          candidate-review agents;
 Sweep Plan +                denominator counts;         advisory_review_packet.json)
 denominator ledger)         direct reconciliation)
```

Because the adapters write to gitignored package `outputs/` roots, no product run
is committed on `origin/main`. A reproducible generator
(`scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/generate_product_run_fixtures.py`)
drives the **real** chain once into a throwaway temp repo and copies the honest
terminal artifacts into
`scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/product_runs/<gates_run_id>/`,
together with a deterministic `run_index.json` the cockpit reads as its single
entry point. Absolute machine paths are sanitized; the fixture is byte-identical
across runs.

## Panels

### Product pipeline · real runs

- **State vocabulary** (all six distinguished): no run, awaiting execute
  approval, prepared (bridge prepare-only), executed (runner Result Population),
  advisory packet ready, blocked / failed.
- **Per-run card**: provenance ids (pipeline / bridge / runner / gates); stage
  ladder with reached markers; a "real runner executed" callout stating
  `runner_invoked = true` and the preserved denominator; a **withheld / missing
  statistics** table (WFO/OOS gate blocked/withheld, per-trade, oos-walkforward,
  funding-stress — each with `fabricated = false`); robustness diagnostics
  (completed + skipped-with-reason); advisory candidate-review (status, evidence
  gaps, no promotion recommendation); an advisory **surface-routing** callout;
  and a present/missing + sha256 artifact drilldown.

### Product candidate funnel

Narrows the preserved runner denominator through advisory review to an explicit
`Candidates admitted = 0`. Advisory `surface_status` is review-routing only.

## Honesty guarantees

- **Missing ≠ zero.** Withheld statistics are shown with explicit status strings
  and `fabricated = false`; the WFO/OOS gate is shown as blocked/withheld, never a
  zero pass.
- **No admission.** `candidate_lifecycle_written`, `go_auto_admission`,
  `go_auto_crossing`, `go_auto_promotion` all surface as `false`; the
  non-promotion posture is displayed. Any GO-like signal is review-needed only.
- **Spine-only supersession.** The legacy spine-only pipeline panel keeps its
  honest per-run labels but now notes that the real runner + gates adapter flow is
  complete — correcting the obsolete "flow not yet complete" framing only because
  committed real-run evidence exists.
- **Fail closed.** Missing/empty product-run directory → no-run panel; malformed
  `run_index.json` → blocked/failed card. Nothing is fabricated.

## Non-authority

Inherits every dashboard/cockpit guarantee and adds:
`reads_product_run_state_only = true`; `invokes_product_runner_adapter`,
`invokes_product_gates_adapter`, `writes_advisory_review_packet`,
`records_candidate_surface_decision`, `admits_candidate` all `false`.
