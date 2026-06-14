# Realism Runway Conclusion

## Status / authority boundary

This note records the realism-runway measurement conclusion for the `RP-6688` / `RP-7520` cross-read. It is evidence-level research-pipeline memory only.

This note does not register a candidate, rank variants, mark readiness, promote a strategy, authorize paper/live execution, authorize runtime behavior, or create trading authority.

## Runway summary

`RP-6688` is the prior fixed-order-size population and is retained as append-only evidence.

`RP-7520` is the canonical dynamic-equity-target-leverage population for `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002`.

The sizing-realism runway moved the measurement surface from fixed order size toward dynamic equity target leverage for future comparable realism runs. That measurement conclusion does not create candidate lifecycle action or downstream execution authority.

## Canonical evidence

- `RP-6688`: prior fixed-order-size result population for the first both-direction SMA-band population.
- `RP-7520`: canonical dynamic-equity-target-leverage result population.
- `docs/research_pipeline/2026-06-canonical_dynamic_sizing_result_population.md`: detailed `RP-7520` evidence note.
- `docs/status_entries/WP-REALISM-SIZING-03a.md`: package status, validation, and boundary record for the canonical dynamic-sizing write.

`RP-7520` preserves denominator 10, uses `dynamic_equity_target_leverage` at `target_leverage=1.0`, includes `sizing_metadata` in both identity scopes, and preserves lineage over the cleaned D4 slice.

## RP-6688 / RP-7520 cross-read

`RP-6688`'s uniform liquidation result is classified as a sizing-artifact under the old measurement model.

`RP-7520` does not reproduce the uniform liquidation artifact. It records non-degenerate dynamic 1x results for the same frozen Strategy Spec, variant manifest, sweep plan, and cleaned BTCUSDT 15m D4 lineage.

The cross-read preserves both artifacts: `RP-6688` remains append-only prior evidence under its recorded fixed-size assumptions, and `RP-7520` is the comparable dynamic-sizing evidence surface for future realism work unless Main authorizes otherwise.

## Measurement model conclusion

Dynamic equity target leverage is the canonical measurement model for future comparable realism runs unless Main authorizes otherwise.

This conclusion is about measurement comparability and realism, not strategy approval, candidate lifecycle, ranking, readiness, promotion, paper/live execution, runtime behavior, or trading authority.

## Strategy interpretation boundary

`STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` shows no evidence-level edge under the `RP-7520` measurement.

This is evidence-level interpretation only and creates no candidate lifecycle verdict.

The result should not be generalized to mean-reversion broadly, all both-direction strategies, all 15m strategies, or any paper/live setting.

## What remains not authorized

This note authorizes no result-population mutation, data acquisition, schema or validator change, query-layer behavior change, candidate registration, ranking, readiness marking, strategy promotion, dashboard implementation, paper/live execution, runtime behavior, OMS/risk/reconciliation change, broker/exchange connectivity, collateral movement, or autonomous behavior.

No follow-on implementation package is automatically authorized by this conclusion.

## Next possible architecture directions

Future scoped packages may choose to preserve this conclusion in downstream planning surfaces, compare later result populations against `RP-7520`, or design additional realism criteria. Those packages require explicit authorization, exact scope, and their own validation plan.

The BTC perp capability backlog records non-authoritative future capability inventory in `docs/architecture/BTC_PERP_FUTURE_CAPABILITY_BACKLOG.md`.
