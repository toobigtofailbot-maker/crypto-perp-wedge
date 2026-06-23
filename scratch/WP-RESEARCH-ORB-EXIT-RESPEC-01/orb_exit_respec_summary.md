# WP-RESEARCH-ORB-EXIT-RESPEC-01 Summary

## Fact

The package reached the bounded idea formalizer and stopped before bridge execution. The formalizer accepted the ORB exit re-spec idea as scratch-only, detected `atr` and `ohlcv`, and reported full-history public testability for those inputs, but it produced no draft Strategy Spec because no validated adapter exists for this primitive family.

Committed repo truth does contain ORB-related design and scratch dry-run records. The prior ORB 15m preregistration surface used a UTC 00:00 opening range, break-and-retest entry, one trade per session, and exits via `time_exit.session_end`, `opening_range_opposite_side`, and `fixed_R_target`. That prior scratch dry-run was non-canonical, wrote no Result Population, preserved denominator 8/8, and reported all rows net-negative with high drawdowns.

## Inference

The lower-level grammar/compiler can express ORB, but the completed agent machine path cannot yet generate or bridge ORB artifacts. Running a manual ORB re-spec here would bypass the selected formalizer/bridge path and would not answer the requested MFE/exit-reason question because current outputs lack MFE, MAE, exit reason, and real per-trade rows.

## Decision

Outcome: `BLOCKED`.

Earliest honest boundary: no bridge-compatible ORB draft Strategy Spec exists.

## Follow-Up Needed

- Add a narrow ORB adapter to the formalizer and bridge, or explicitly authorize a manual scratch ORB artifact path.
- Add MFE/MAE/exit-reason/per-trade instrumentation before claiming an ORB exit-retention result.

## Boundary

No canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, candidate lifecycle entry, trial log, canonical crossing, paper/live/runtime path, OMS/risk/reconciliation/capital path, credential, private endpoint, provider/API call, or network code was created or touched.
