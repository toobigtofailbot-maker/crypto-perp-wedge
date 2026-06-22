# WP-COMPILER-FEATURES-REGIME-SESSION-01 Branch State

## Authorization

- Main-authorized under the lab-capability completion path.
- Does not authorize runtime scheduling, paper/live, funding/cost, or agent behavior.

## Scope Summary

- Adds deterministic UTC/session/time filters as closed timestamp-derived `data_ref` fields.
- Preserves regime capability through the existing `trend` and `regime` group roles and ordinary closed indicator/feature conditions; no new regime classifier is added.

## Semantic Summary

- `hour_of_day_utc` is the current completed bar timestamp hour, integer `0` through `23`.
- `day_of_week_utc` is the current completed bar weekday, integer Monday `0` through Sunday `6`.
- `is_weekend_utc` is boolean true only for Saturday and Sunday.
- Session gates compose existing comparisons, for example `hour_of_day_utc >= 8` and `hour_of_day_utc < 20`, giving an inclusive start and exclusive end.
- Timestamp-derived fields require a timezone-aware UTC `DatetimeIndex`; non-datetime, timezone-naive, non-UTC, and missing timestamps fail closed with a compiler error.
- Values derive only from each current row's index timestamp. No future row is read, and no fill, backfill, interpolation, calendar, DST, or local-time conversion is performed.

## Boundary Summary

- No MTF implementation.
- No data ingestion.
- No runner/backtester changes.
- No runtime/paper/live.
- No canonical artifacts.
- No promotion/readiness authority.

## Validation Status

- Focused tests: PASS, 360 tests across Strategy Spec validation, Indicator Catalog validation, and signal compiler coverage.
- Strategy Spec validator: PASS.
- Indicator Catalog validator: PASS.
- Result Population validator: PASS.
- Query-view discovery: PASS.
- Diff scope: PASS; no forbidden-path matches.
- `git diff --check`: PASS.
- Full pytest: 1 unrelated environment failure, 1,865 passed, 1 skipped, 6 warnings. `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` requires the gitignored D4A normalized-data fixture, which is absent in this isolated worktree. The package-focused suite passes independently.
