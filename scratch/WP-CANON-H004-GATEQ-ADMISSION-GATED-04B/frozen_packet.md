# H-004-R2 exact Gate-Q packet — frozen Stage A

## Verdict

`KARL EXACT-CONTENT GATE-Q APPROVAL REQUIRED`

This packet authorizes nothing by itself. Stage B must not begin unless Karl approves every exact byte-bound fact below. General package approval is insufficient.

## Repository and reconciliation

| Fact | Frozen value |
|---|---|
| Base | `e4cc369610d8582f279cddb5df973a58b2345aaa` |
| Branch | `codex/wp-canon-h004-gateq-admission-gated-04b` |
| Worktree | `C:/GitHub/crypto-perp-wedge-wp-canon-h004-gateq-admission-gated-04b` |
| Reconciliation merge | `e4cc369610d8582f279cddb5df973a58b2345aaa` / PR #663 |
| Reconciliation package head | `eacc975`, ancestor of refreshed `origin/main` |
| Open PRs at freeze | none |
| Authoritative queue state at freeze | absent |

## Frozen approval and queue item

| Fact | Frozen value |
|---|---|
| Gate-Q proposal file | `scratch/WP-CANON-H004-GATEQ-ADMISSION-GATED-04B/proposed_gate_q_approval.json` |
| Gate-Q ID | `GATE-Q-H004-R2-04B-0001` |
| Gate-Q authoritative target | `research/queue/gate_q_approvals/GATE-Q-H004-R2-04B-0001.gate_q_approval.json` |
| Gate-Q full-file SHA-256 | `sha256:8645018c04a565761d72047b5225fbfd5694e342f5180407f0c8b111ba310fed` |
| Gate-Q approval-core SHA-256 | `sha256:08e78c274cbade0fb6622596d0b9d36c94cccfea0a29488d7e447f591509e88c` |
| Gate-Q `approved_at` | `2026-07-17T22:23:24Z` |
| Queue proposal file | `scratch/WP-CANON-H004-GATEQ-ADMISSION-GATED-04B/proposed_queue_item.json` |
| Queue-item ID | `QI-20260717-H004R2B1` |
| Queue-item authoritative target | `research/queue/admissions/QI-20260717-H004R2B1.queue_item.json` |
| Queue-item full-file SHA-256 | `sha256:47ba045b4ac89588e1865c280b080f0922cef6bb1e7d4e7880090ba07a44d967` |
| Queue-item `admitted_at` | `2026-07-17T22:23:24Z` |
| Terminal status | `admitted_non_dispatched` |

## Strategy Spec and Gate-C lineage

| Artifact | ID/path | Exact SHA-256 |
|---|---|---|
| Strategy Spec | `STRAT-SPEC-0007` / `research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json` | `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c` |
| Gate-C approval | `GATE-C-H004-R2-0001` / `scratch/WP-CANON-FIRST-GATE-C-CROSSING-GATED-02C/approvals/GATE-C-H004-R2-0001.gate_c_approval.json` | `sha256:b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd` |
| Gate-C raw audit record | `research/canonical_crossing_audit/strategy_spec_writes.jsonl`, line 1 | `sha256:ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2` |
| Source draft | `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-2B5725C1A8349863.draft_packet.json` | `sha256:7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a` |
| Review trail | `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/AIDRAFT-2B5725C1A8349863.review_events.jsonl` | `sha256:a0e3174758316a18ff0f4f207886d2cb1704eaad609e397fd1aee1e0f4339230` |

Exact eligibility object on Gate-C, Gate-Q, queue item, and derived audit:

```json
{
  "advisory_only": true,
  "path": "scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/AIDRAFT-2B5725C1A8349863.eligibility_report.json",
  "sha256": "sha256:76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9"
}
```

## Gate C-VP, VM, and Sweep

| Artifact | Exact identity | Exact hashes / facts |
|---|---|---|
| Gate C-VP | `VPAPP-20260715-H004R201`; `research/strategy_spec_variant_planning_approvals/VPAPP-20260715-H004R201.variant_planning_approval.json` | file `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a`; core `sha256:4b8e126870c918e88ac42336427c3ba495bcacb6433bd3741b0a01c712bf99f0` |
| Variant Manifest | `VM-0007`; `research/variant_manifests/VM-0007.variant_manifest.json` | file `sha256:822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d`; manifest `sha256:168fe6deefc761bc9bf9f603f37d199c5f3ef28a83aff5ee0a6a6596729fc667`; committed/cap 81; adaptive false; post-hoc mutation forbidden |
| Sweep Plan | `SWEEP-PLAN-0007`; `research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json` | file `sha256:66d48ec6d57048012dcd243ca7dda25dcf59241b1a3733dc05796eb46d7af2f0`; selected 81; executed 0; not attempted 81; denominator 81 |

Search family: `SF-H004-R2-EMA-PULLBACK-CONTINUATION-1D-0001`.

## Dataset

| Fact | Frozen value |
|---|---|
| Dataset ID | `binance_usdtm_btcusdt_ohlcv_1d` |
| Snapshot version | `2026-04-12T1655Z` |
| Logical path | `data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` |
| Parquet SHA-256 | `sha256:c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802` |
| Catalog path | `research/data_slices/binance_usdtm_btcusdt_1d/binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json` |
| Catalog SHA-256 | `sha256:51fc09918841cd3ac353efe375af91a4732080571f9b1af634f5d1a426217adb` |
| Market / timeframe | `BTCUSDT_BINANCE_USDTM_PERPETUAL` / `1d` |
| Completed bars / gaps / duplicates | 2,293 / 0 / 0 |
| Unresolved policy | `reject` |

## Denominator, budget, priority, and target

- Committed population: 81.
- Selected population: 81.
- Multiple-testing denominator: 81.
- Denominator basis: `committed_pre_registered_population_count`.
- Priority: `normal`.
- Queue target: `offline_research`.

```json
{
  "metric": "variant_attempts",
  "upper_bound": 81,
  "unit": "attempts",
  "comparison": "actual_lte_upper_bound",
  "retries_included": true,
  "mismatch_or_exceed_policy": "reject"
}
```

## Exact traceability-hash set

The queue item contains exactly these 12 unique hashes:

1. `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`
2. `sha256:ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2`
3. `sha256:7c4e53c5cceefc23dc2c242102c0a5c744355d7fafff4ebd892944cf13c5193a`
4. `sha256:a0e3174758316a18ff0f4f207886d2cb1704eaad609e397fd1aee1e0f4339230`
5. `sha256:76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9`
6. `sha256:b05753fe01cc99aa2c4f0e419fca88f4f843154f12843f01aae775eb1e4e68cd`
7. `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a`
8. `sha256:4b8e126870c918e88ac42336427c3ba495bcacb6433bd3741b0a01c712bf99f0`
9. `sha256:822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d`
10. `sha256:168fe6deefc761bc9bf9f603f37d199c5f3ef28a83aff5ee0a6a6596729fc667`
11. `sha256:66d48ec6d57048012dcd243ca7dda25dcf59241b1a3733dc05796eb46d7af2f0`
12. `sha256:c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802`

## Authority and state

Every authority flag is false: dispatch, execution, scheduler autonomy, candidate lifecycle, promotion/readiness, paper/live/runtime, and notifications. The posture is append-only, exact-content, single-use, non-dispatch, and non-execution.

Stage-A proof: no authoritative Gate-Q file, queue item, or admission audit exists; no dispatch, scheduler, runner, execution, Result Population, candidate, readiness, promotion, runtime, paper/live, OMS, risk, or reconciliation output was created.

## Exact Karl authorization text

Karl may authorize Stage B only by approving the complete statement below without changing any fact:

> I, Karl, approve the exact H-004-R2 Gate-Q packet `GATE-Q-H004-R2-04B-0001` for authoritative path `research/queue/gate_q_approvals/GATE-Q-H004-R2-04B-0001.gate_q_approval.json`, full-file SHA-256 `sha256:8645018c04a565761d72047b5225fbfd5694e342f5180407f0c8b111ba310fed`, and approval-core SHA-256 `sha256:08e78c274cbade0fb6622596d0b9d36c94cccfea0a29488d7e447f591509e88c`; and queue item `QI-20260717-H004R2B1` for authoritative path `research/queue/admissions/QI-20260717-H004R2B1.queue_item.json`, full-file SHA-256 `sha256:47ba045b4ac89588e1865c280b080f0922cef6bb1e7d4e7880090ba07a44d967`. I approve Strategy Spec SHA `sha256:b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c`; Gate-C approval `GATE-C-H004-R2-0001`; Gate-C audit `research/canonical_crossing_audit/strategy_spec_writes.jsonl` line 1 SHA `sha256:ef5a452a4aff61a35fdbdfcf16162362400345f28af67b7bb41aa4ae36024be2`; exact eligibility object `{\"advisory_only\":true,\"path\":\"scratch/WP-CANON-ELIGIBILITY-VALIDATOR-01/reports/AIDRAFT-2B5725C1A8349863.eligibility_report.json\",\"sha256\":\"sha256:76a0654144d215d62932568b5627d6838f3613e36238bebccaac25d55b873dd9\"}`; Gate C-VP file/core hashes `sha256:13b40df10af9290d65c971e1e57397e5193cc76fa5852a04b6084ec41c8a275a` / `sha256:4b8e126870c918e88ac42336427c3ba495bcacb6433bd3741b0a01c712bf99f0`; VM file/manifest hashes `sha256:822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d` / `sha256:168fe6deefc761bc9bf9f603f37d199c5f3ef28a83aff5ee0a6a6596729fc667`; Sweep file hash `sha256:66d48ec6d57048012dcd243ca7dda25dcf59241b1a3733dc05796eb46d7af2f0`; dataset `binance_usdtm_btcusdt_ohlcv_1d`, snapshot `2026-04-12T1655Z`, path `data/processed/binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, SHA `sha256:c6e2e7ce030db6a710d95e48325fc77b27efbbdd441199b3d7458d4394795802`; denominator 81 with basis `committed_pre_registered_population_count`; exact budget `{\"metric\":\"variant_attempts\",\"upper_bound\":81,\"unit\":\"attempts\",\"comparison\":\"actual_lte_upper_bound\",\"retries_included\":true,\"mismatch_or_exceed_policy\":\"reject\"}`; priority `normal`; queue target `offline_research`; and the append-only, exact-content, single-use, non-dispatch, non-execution posture with every downstream authority flag false. I authorize exactly one inert queue admission and no dispatch, scheduling, runner invocation, execution, Result Population, candidate action, or runtime transition.

Any changed byte, ID, path, hash, timestamp, denominator, budget, priority, queue target, eligibility field, or authority fact requires a new Stage-A packet and a new exact authorization.
