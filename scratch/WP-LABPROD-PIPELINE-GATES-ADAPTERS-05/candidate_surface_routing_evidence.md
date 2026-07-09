# Candidate-Surface Routing Evidence

## Scaffold

- Existing scaffold: `tools.lab_pipeline.gate_actions.record_candidate_surface_decision`.
- Allowed statuses:
  - `hold_for_review`;
  - `needs_more_evidence`;
  - `do_not_escalate`.

## Current Route

The current product runner fixture route is:

```text
needs_more_evidence
```

Reason: product runner output has aggregate Result Population rows but lacks committed WFO/OOS gate evidence and fold/OOS inputs. Robustness and candidate-review payloads preserve missing OOS/per-trade caveats.

## GO Safety

The adapter uses the scaffold even for routing and copies the scaffold payload into the product adapter output. The scaffold payload asserts:

- `writes_candidate_lifecycle = false`;
- `writes_crossing = false`;
- `writes_promotion_or_readiness = false`;
- no paper/live/runtime authority.

Focused tests verify:

- current route is `needs_more_evidence`;
- GO-like status selection resolves to `hold_for_review`, not admission/crossing/promotion;
- no candidate lifecycle, crossing, or promotion/readiness write is created.
