# WP-DATA-AVAILABILITY-LABELS-01 Branch State

## Scope Summary

- Adds a versioned evidence-integrity catalog for perp-derived compiler features.
- Adds an optional, identity-bearing Result Population `data_availability_claim`; existing artifacts may omit it and remain valid.
- Blocks declared full-history evidence when a parent Strategy Spec uses a recent-only, snapshot-only, vendor-only, streaming-only, or unknown data field without an explicit aligned historical dataset override and provenance.
- Adds the read-only `v_data_feature_availability` query/report surface.

## Coverage Classes

- `FULL_HISTORY_PUBLIC_ARCHIVE`
- `RECENT_ONLY_PUBLIC_REST`
- `STREAMING_ONLY_PUBLIC_WS`
- `VENDOR_ONLY_FOR_HISTORY`
- `PUBLIC_SNAPSHOT_ONLY`
- `UNKNOWN_OR_BLOCKED`

## Feature Label Summary

- All 16 current compiler-visible non-OHLCV fields have at least one availability label.
- Funding, funding mark price, mark price, index price, and premium index are conditional public-archive history: the aligned dataset must cover the claimed window and existing gap policy still applies.
- Open interest is public-snapshot-only; open-interest value and long/short ratios are recent-only public REST.
- Taker flow has source-specific labels: Binance ratio REST remains recent-only, while deterministic trade/aggregate-trade archive derivation is conditional full-history public archive.
- UTC hour/day/weekend fields are bar-timestamp-derived and conditional on source-bar history.
- A non-compiler-visible liquidation-volume row exercises the vendor-history fail-closed class without enabling compiler support.
- Trade and aggregate-trade archives are explicitly not treated as a reconstruction path for true open interest.

## Enforcement Summary

- The availability validator schema-checks the catalog, reads current compiler allowlists from source, requires complete compiler-field labeling, rejects unknown compiler-visible labels, enforces timestamp/taker/OI invariants, and rejects duplicate feature/source keys.
- The Result Population validator binds every non-OHLCV `data_ref` in the parent Strategy Spec to a catalog `(feature_name, source_class)` row when `data_availability_claim` is present.
- Full-history claims fail on missing or unknown bindings, recent/snapshot/vendor classes without explicit historical dataset provenance, conditional archive sources without condition assertions, and claim metadata omitted from either identity-hash scope.
- Vendor/capture-dependent rows require a `VENDOR_HISTORICAL_DATASET` or `CAPTURED_HISTORICAL_DATASET` override with dataset/provenance refs and alignment/full-history assertions.

## Compatibility with Existing Artifacts

- Existing committed Strategy Specs and Result Populations are unchanged.
- `data_availability_claim` is optional, so Result Populations without an explicit full-history availability claim preserve their existing schema and hash posture.
- Existing committed Result Populations validate successfully.

## Boundary Summary

- Ingestion, archive download, taker-flow reconstruction, vendor integration, live capture: not touched.
- Compiler semantics, runner, backtester, funding PnL/cost, canonical artifacts, trial log: not touched.
- Runtime, paper/live, OMS, reconciliation, risk, overlay, safe mode, configs, broker/exchange paths: not touched.
- No candidate promotion, readiness, ranking, recommendation, or downstream authority is created.

## Validation Status

- `python -m tools.registry.validate_data_feature_availability`: PASS.
- Focused availability/Result Population tests: PASS, 69 passed.
- Required Strategy Spec/Result Population/compiler regression tests: PASS, 397 passed.
- Strategy Spec validator: PASS.
- Result Population validator, including existing committed artifacts: PASS.
- Query view discovery/projection: PASS; `v_data_feature_availability` listed and returned labeled rows.
- Broader `tests/test_research_query.py` plus availability-query test: timed out after 304 seconds without failure output; the package-specific availability-query test already passed.
- Diff scope summary: PASS; expected package-authorized research/schema paths only, no runtime/canonical-artifact write.
- `git diff --check`: PASS.
- Full pytest: completed with 1,880 passed, 1 skipped, 6 warnings, and 1 known isolated-worktree local-data failure. `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` expected the gitignored local D4A normalized CSV. After copying that file from the root checkout into this worktree for validation only, the failing test passed (1 passed). The copied file remains gitignored and is not a package change.
