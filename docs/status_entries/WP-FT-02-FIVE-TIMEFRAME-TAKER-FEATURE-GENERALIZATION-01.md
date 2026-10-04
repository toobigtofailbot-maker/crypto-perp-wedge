# WP-FT-02 Five-Timeframe Taker-Feature Generalization

- Package: `WP-FT-02-FIVE-TIMEFRAME-TAKER-FEATURE-GENERALIZATION-01`
- Branch: `codex/wp-ft-02-five-timeframe-taker-feature-generalization-01`
- Exact base: `a9ce8963569581476d6039fa978f55161db946b1`
- Validated semantic implementation head: `81660eb34b276c02723d4fea17d81ddba7426828`
- Pull request: [#726](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/726)
- Package class: shared scientific contract and offline research-runner semantics;
  full-release validation required
- Merge status: open, non-draft, not merged
- Self-merge: no
- Next dependency: Prefect real-consumer orchestration after merge

## Exact final scope

1. `research/schemas/research_feature_table_manifest.schema.json`
2. `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`
3. `tools/research_domain/feature_data.py`
4. `tools/data/materialize_takerflow_features.py`
5. `tools/data/research_feature_table.py`
6. `tools/registry/validate_data_feature_availability.py`
7. `tools/research_runner/run_offline_sweep.py`
8. `tools/lab_readiness/readiness.py`
9. `docs/architecture/2026-09-research_data_feature_expansion.md`
10. `docs/project_status.md`
11. `tests/test_takerflow_feature_materialization.py`
12. `tests/test_research_feature_table.py`
13. `tests/test_validate_data_feature_availability.py`
14. `tests/test_offline_research_runner.py`
15. `tests/test_research_domain.py`
16. `tests/test_validate_result_populations.py`
17. `tests/test_lab_readiness.py`
18. `docs/status_entries/WP-FT-02-FIVE-TIMEFRAME-TAKER-FEATURE-GENERALIZATION-01.md`

## Scientific semantics

D2-021 remains the canonical-base and feature-parent identity authority. The
legacy 15-minute `CANONICAL_D4_KLINE_DERIVATION` contract remains the sole 15m
authority. The new `CANONICAL_KLINE_TAKERFLOW_DERIVATION` contract is closed to
30m, 1h, 4h, and 1d and requires feature parent identity to equal the exact
canonical execution-base identity.

All five routes use the unchanged row-local formulas: buy volume is
`taker_buy_base_vol`, sell volume is `volume - taker_buy_base_vol`, and the
ratio is null exactly when sell volume is zero. Features become available only
at the exclusive completed-bar close. Resolution requires an exact one-to-one
timestamp join with no fill, forward fill, backfill, interpolation, tolerance,
repair, splice, or as-of behavior. Composite identities use the truthful
`cpw_research_composite_<timeframe>` family.

## Real-byte materialization evidence

The exact local canonical inputs were materialized twice under ignored scratch
paths with `network_used=false`. Every output row count equalled its parent row
count, timestamp grids and exclusive-close availability were exact, non-null
ratios were finite, zero-sell and null-ratio counts matched, and repeated CSV
bytes and feature-table identities were equal.

| Timeframe | Parent physical SHA-256 | Parent execution-base identity | Rows | Feature CSV SHA-256 | Source-set identity | Feature-table identity | Projection SHA-256 | Zero/null rows |
|---|---|---|---:|---|---|---|---|---:|
| 15m | `c30fd7f07fdf513cdaf234b1bee4eff03b430a479cc572a2cc8b57394f22e0ab` | `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664` | 220128 | `c726d5a73a2d2168404c2a3599c477f9bea7ab5066d59c3f090a456b8efeffba` | `sha256:a706affa0f3b3be362ffeb523d8dcd6805235127618760e13a16b7d6969f411e` | `sha256:0ab8af18c78d274d7ac4e3b11a9701d7e604e5c9a8e746b6000e1cca4f79403c` | `35b29807d6347cb46c552f8b2a1f0f409221d601f9c6a8b503d3d48890de5aba` | 15 / 15 |
| 30m | `05c5857d668d2d12bcc743a13ad92a34590bc1c37ff8ea1f5f54d5d1fbf379ba` | `binance_usdtm_btcusdt_ohlcv_30m:sha256:090f4fac75bedf64fd19dbbeec141169bd7eaeaaaef187038878a6242022b94e` | 110064 | `9e9ceb2395a38b5c610b620ee2c9f3fcea0a2c30d74708fd002ffa1d9b10ea8b` | `sha256:f42323b54a8dae3bb5433b29c65b9fd3bde72a1156d95adf6cb39be90c6dd28b` | `sha256:89c08f51f3097e30d2517131bdaacbc6f49602f8710bbdf745ac84e0d7ed2cf1` | `ce2355ab622f72a670127903c80a9102d73ed19488729bdf287ce72dac257e24` | 5 / 5 |
| 1h | `28b750e90ee9957e6fc22811c4ae632355a239f2b958ed65c9b3c56cb2d9e79e` | `binance_usdtm_btcusdt_ohlcv_1h:sha256:9e0faa68eb84b1aa176a5857432840b71a6049765963637236241b91ae807877` | 55032 | `760901c14d3703f5a577e44f4c9bdeb023932b8f754cbaea3aa6752615c12c09` | `sha256:650898572620ce72af6dce1eb6bd81b91e33a206301d12810c34e382abedc5a5` | `sha256:9ff0b6368a60eb36ba1c79f925a2d87fe430c82c6b6a170be9a2222c498dad7a` | `b1cb32bc16ad2d9d66758a7b44caebb8c524792d08e7be88efb4b4cbb7e04e23` | 1 / 1 |
| 4h | `828ad4a975c157c7ac4d3c873a39a8b6bbfec3cb306e25eb74209c8a01da6ca1` | `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30` | 13758 | `bc2ee14b95696cf3c0af83b58d4d56963ffe20219033eebd16f75d413f421575` | `sha256:a2445bc149bd5aa7e3c1b9e3788df72c351f70416e4621dea38d0ebda3aa3175` | `sha256:09c200decd6bc324b41353f1727b6571fc80a72b5df567ece2886e1dbbe6e7cd` | `fcc87e59c87aa3aec003c8f5cb6a9ecdda9f73f2114319309163496008f5821b` | 0 / 0 |
| 1d | `c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802` | `binance_usdtm_btcusdt_ohlcv_1d:identity_sha256:05ce3d5fdb5186ae36f612e2c51393eaecb110a66b0c3506e5583f3acedd443f` | 2293 | `b6394cc2b47aba3fb437c04efd5cfd1b0f15ed96f2064bddbaea08ee96efc034` | `sha256:dc543eab709dd45f471cab03cbb4514d2997c3a580d1194c552b0865a8891688` | `sha256:843668b0490d0725efab615eb6195282070d12f891acb2f414f67e329cb3af3f` | `1161d4eed00362702a43f0ccabc51eed537ee7bd9020eb5803f7ebf0e277283b` | 0 / 0 |

The 15m feature CSV, source-set, feature-table, and projection identities above
exactly reproduce the locked RESEARCH-02 identities.

## Validation

- Exact-base baseline after permitted ignored-corpus provisioning: `382 passed,
  3 skipped`.
- Focused seven-file package suite: `306 passed, 3 skipped`.
- Five read-only adjacent regression files: `141 passed`.
- Combined focused and adjacent run: `447 passed, 3 skipped`.
- Explicit full-history legacy identity plus generic materializer checks:
  `9 passed`.
- Data-feature availability validator: pass.
- Current committed Result Population validator: pass.
- `git diff --check` and production-module byte compilation: pass.
- Semantic-head exact scope: 17 changed files, both research paths authorized,
  zero rejected authorized paths, zero forbidden matches, and zero allowlist
  violations.
- Full-release profile `full-release-balanced-v1`: all 187 tracked test files
  uniquely assigned once across 48 completed shards; failed shards `0`;
  timed-out shards `0`; slowest shard 41 at 1500.594 seconds.
- Integrity views reproduced only the two repo-documented FT-01 baseline
  disclosures: `v_integrity_execution_streams` reports the intentionally absent
  H-004 local stream, and
  `v_integrity_strategy_spec_legacy_hash_scope_reproducibility` reports the
  preserved `STRAT-SPEC-0007` unresolved legacy hash scope. The semantic diff
  changes neither surface. These two known rows make the generic verifier's
  aggregate status nonzero; all required commands, shards, and all other
  integrity views passed.

## Boundary summary

This package changes no runtime execution, OMS, reconciliation, risk cap,
overlay, safe-mode, config, paper/live, capital, scheduler, autonomous agent,
promotion, candidate, canonical Result Population, or trial-log authority. The
materialized feature artifacts are local ignored research inputs and carry no
execution or promotion authority. Per-hypothesis/default-off restrictions
remain until later Stage 5B implementation, validation, explicit activation,
and a valid Karl-approved envelope.
