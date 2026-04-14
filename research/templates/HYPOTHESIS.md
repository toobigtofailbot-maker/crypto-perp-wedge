# Hypothesis Template

<!-- This file is a template. Copy it into a new hypothesis directory before testing.
     Fill all fields before the first backtest.
     Once trials begin, do not modify the hypothesis in place; create a new
     hypothesis instead. -->

## Hypothesis ID

<!-- Format: H-NNN -->

## Metadata

<!-- Created: YYYY-MM-DD -->

<!-- Status: DRAFT | TESTING | CONCLUDED -->

<!-- Owner: optional -->

## Economic Rationale

<!-- Why does this edge exist? What market inefficiency, behavioral pattern,
     or structural feature does this strategy exploit? This section must
     stand alone before any testable prediction. -->

## Testable Prediction

<!-- Specific, falsifiable prediction. Name the signal family, instrument,
     timeframe, and expected performance direction. -->

## Primary Timeframe

<!-- Exactly one of: 15m, 30m, 1h, 4h, 1d -->

<!-- Justification for this choice (required): -->

## Confirmation Timeframes

<!-- Optional. Must be coarser than primary. List or "None". -->

## Required Data

<!-- Instrument -->

<!-- Required streams -->

<!-- Optional evaluation range -->

## Success Criteria

<!-- Numeric thresholds aligned with D2-006 gates -->

## Kill Criteria

<!-- Conditions that would end this hypothesis without further tuning -->

## Free Parameters

<!-- List all tunable parameters. Maximum 5. -->

## Expected Trial Count

<!-- Estimated number of trials before evaluation. Include rationale
     (e.g., grid size × folds). -->

## Artefacts

<!-- Notebook / report / output path if applicable -->

<!-- Keep optional and lightweight -->

## Decision Record

<!-- Outcome: GO | NO-GO | REVISE -->

<!-- Fill only after evaluation -->

## Notes

<!-- Optional additional context -->
