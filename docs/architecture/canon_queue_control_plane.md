# Canonical Queue Control Plane

Status: locked design/contract for `WP-CANON-QUEUE-CONTROL-PLANE-DESIGN-LOCK-03A`. This package creates no writer, approval, production queue item, dispatch, or execution surface.

## Boundary and layout

Gate Q is Karl's exact-content authority for exactly one append-only admission. Gate C, eligibility, review state, canonical artifact existence, UI state, and model advice cannot substitute for Gate Q. Admission means an exclusive file creation only; it never calls a runner, scheduler, dispatcher, notification system, candidate lifecycle, paper/live/runtime, broker, exchange, OMS, risk, or reconciliation surface.

The canonical directory is `research/queue/admissions/`. It is new, is not referenced by any current watcher or runner, is separate from scratch, run outputs, and Result Populations, and contains one immutable item per file. The deterministic identity is `QI-YYYYMMDD-XXXXXXXX`; its only target is `research/queue/admissions/<queue_item_id>.queue_item.json`. The suffix is eight uppercase alphanumeric characters. IDs and paths are permanently single-use. Existing targets, audit evidence of an ID/path/approval, ambiguity, or collision must fail closed; a future writer must use atomic exclusive create and must never overwrite, repair in place, or silently reuse.

## Bounded vocabulary

`queue_target` has one value: `offline_research`. `priority` is `normal` (default ordinary ordering) or `expedited` (human-selected earlier attention). Neither priority changes validation, denominator, dataset, budget, Gate-Q, or later execution requirements, and neither implies dispatch authority.

## Exact admission bundle

Gate Q binds the Strategy Spec, Gate-C crossing audit, Variant Manifest, Sweep Plan, source draft, review trail, eligibility report, and Gate-C approval by repo-relative path and raw-file SHA-256. It also binds the dataset, denominator, budget, priority, target, queue item ID, exact target path, and SHA-256 of the exact UTF-8 queue-item file bytes. Any missing path, unreadable content, schema failure, hash mismatch, symlink escape, lineage mismatch, or post-approval byte change rejects admission.

The queue item carries the Gate-Q ID/path and `approval_core_sha256`. `gate_q_approval_core_v1` is canonical JSON (RFC 8785/JCS semantics) of every Gate-Q field except `proposed_queue_item` and `approval_core_sha256`. This scoped hash avoids an impossible circular full-file hash: Gate Q hashes the exact queue bytes while the queue item binds the immutable approval core. A future writer must recompute both. The full Gate-Q file is still validated and its exact proposed-item binding is mandatory.

## Denominator, dataset, and budget

The denominator is `committed_pre_registered_population_count` and must be the same positive integer in the Variant Manifest declared population, its trial-budget denominator, and the Sweep Plan committed/multiple-testing denominator. Mismatch rejects.

Dataset identity requires a nonempty ID and snapshot/version, repo-approved immutable path plus raw-file SHA-256, market `BTCUSDT_BINANCE_USDTM_PERPETUAL`, and a timeframe in `15m|30m|1h|4h|1d`. It must satisfy the Spec/Plan stream and timeframe requirements. Missing, mutable, unresolved, or incompatible data rejects.

Budget uses the sole metric `variant_attempts`, unit `attempts`, an exact positive integer upper bound, and `actual <= upper_bound`. All retries count as attempts. For v1 the bound must equal the committed denominator: no retry allowance or expansion is admitted. Exceedance or mismatch rejects; vague budgets are invalid.

## Later writer requirements

A later separately authorized writer must independently parse and validate all referenced artifacts; recompute raw-file hashes, JCS approval-core hash, and exact queue bytes hash; validate cross-artifact IDs, dataset compatibility, denominator equality, budget, priority, and target; check an append-only admission audit for reuse; reject used approval IDs, item IDs, or paths; confine paths to repo roots; use an atomic exclusive create; append an audit record without losing failure evidence; and fail closed. It must create no dispatch request, run output, Result Population, candidate, or notification. Recovery and audit atomicity require explicit implementation review in `WP-CANON-QUEUE-ADMISSION-GATED-03B`.

## Traceability

`scratch draft -> review trail -> advisory eligibility -> Gate-C approval -> Gate-C crossing audit -> canonical Strategy Spec -> Variant Manifest -> Sweep Plan -> Gate-Q approval -> admitted/non-dispatched queue item`. Later execution and Result Population steps remain separate and unauthorized here.
