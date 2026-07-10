# Artifact inventory

Inventory scope: committed repo artifacts only. Scratch artifacts are eligible only as
read-only, noncanonical diagnostics; they gain no evidence or execution authority.

| Target class | State | Projected source / field | Linkage and notes |
|---|---|---|---|
| Equity curves | unavailable | none | No committed equity point array was found. Aggregate return/PnL is not expanded into a curve. |
| Drawdown time series | unavailable | none | Result populations and WFO reports contain aggregate drawdown scalars only. |
| WFO folds | exists / projected for `RP-2592` | `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json` → `fold_results`; `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_walkforward_run_report.json` → `fold_results` | Each source has 2 folds. Both match `RP-2592` on strategy-spec, variant-manifest, and sweep-plan lineage. Both remain scratch-only and noncanonical. |
| Monte Carlo robustness summary | exists / projected for `RP-2592` | `scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.json` → `bootstrap_ci` | Ten metric confidence summaries, each based on 1,000 seeded samples. The report directly names `RP-2592`. |
| Raw Monte Carlo sample distribution | withheld / not projected | none | Only confidence summaries and `bootstrap_samples_checksum` are committed; the 1,000 raw samples are not. |
| Per-trade return distributions | unavailable | none | Committed Result Population rows explicitly expose aggregate per-variant metrics only. |
| Trade lists | unavailable | none | Aggregate `trade_count` values are not expanded or inferred into trades. |
| Summarized trade diagnostics | exists / projected | each committed Result Population → `variant_result_rows` | Direct result-population linkage; 66 rows across 8 artifacts. Rows are returned verbatim. |

## Projected-source hashes

| Source | Rows/folds/metrics | File SHA-256 |
|---|---:|---|
| `scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json` | 2 folds | `sha256:72add2f6c6c9c62232d1da99b61d2f04642f6d5d3cb4c670a7504d229f26a0e6` |
| `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_walkforward_run_report.json` | 2 folds | `sha256:a574dbff580995df7ea19be6d6b8732240501dd718c6a9d5c1d2c34bfcd79be9` |
| `scratch/EXT-INTEG-ROBUSTNESS-MC-01/seeded_advisory_mc_report.json` | 10 metric summaries | `sha256:5a02ca2c8265b9caf13ffa02dc4297b13e900208dad5e57984f0f360f5b91fd1` |

The Monte Carlo report additionally records raw-sample checksum
`sha256:6c7434602cc8235fadec0b75f13548e77cb7f7684e40e8884f52eef286a52121`.
That checksum is provenance only; it is not a substitute for absent raw samples.

## Result Population diagnostic hashes

| Result Population | Source | Rows | File SHA-256 |
|---|---|---:|---|
| `RP-2134` | `research/result_populations/RP-2134.result_population.json` | 7 | `sha256:b80b882e1b7866d761906c7502cf180acca0eeff0e7f3d022c15a1ff05ec3df9` |
| `RP-2592` | `research/result_populations/RP-2592.result_population.json` | 8 | `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8` |
| `RP-3731` | `research/result_populations/RP-3731.result_population.json` | 8 | `sha256:e8d6bc5c48a80c32f9495a0d63d05be0cf8513b8f3912d6b81c6dbca715672c2` |
| `RP-4492` | `research/result_populations/RP-4492.result_population.json` | 7 | `sha256:943833067d2bef2fc7a2d38c3502d7c115fef01b275dad5152c55f4cb51910aa` |
| `RP-6236` | `research/result_populations/RP-6236.result_population.json` | 8 | `sha256:1b8f4ed5199067629e55fea3fcaf5d544168b03fa99af824d98b22582b1772b9` |
| `RP-6688` | `research/result_populations/RP-6688.result_population.json` | 10 | `sha256:dd7a329fdf7649ce9d926a56b7fd3f262db46e2ecd9a490a34f3ec05dcf02e23` |
| `RP-7134` | `research/result_populations/RP-7134.result_population.json` | 8 | `sha256:9813afd65c946ceaac23804fd485b4452d2451bec31a726eb86667926741e524` |
| `RP-7520` | `research/result_populations/RP-7520.result_population.json` | 10 | `sha256:1df066eeb15957bb0a0825b180bcded8ee971a6e9834a30fe93ac7b70810bd36` |
