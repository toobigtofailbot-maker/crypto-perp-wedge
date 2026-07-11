# Canonical Queue Control Plane

Status: locked design/contract for `WP-CANON-QUEUE-CONTROL-PLANE-DESIGN-LOCK-03A`. This package creates no writer, approval, production queue item, dispatch, or execution surface.

## Boundary and layout

Gate Q is Karl's exact-content authority for exactly one append-only admission. Gate C, eligibility, review state, canonical artifact existence, UI state, and model advice cannot substitute for Gate Q. Admission means an exclusive file creation only; it never calls a runner, scheduler, dispatcher, notification system, candidate lifecycle, paper/live/runtime, broker, exchange, OMS, risk, or reconciliation surface.

The canonical directory is `research/queue/admissions/`. It is new, is not referenced by any current watcher or runner, is separate from scratch, run outputs, and Result Populations, and contains one immutable item per file. The deterministic identity is `QI-YYYYMMDD-XXXXXXXX`; its only target is `research/queue/admissions/<queue_item_id>.queue_item.json`. The suffix is eight uppercase alphanumeric characters. IDs and paths are permanently single-use. Existing targets, audit evidence of an ID/path/approval, ambiguity, or collision must fail closed; a future writer must use atomic exclusive create and must never overwrite, repair in place, or silently reuse.

The `YYYYMMDD` component must equal the UTC calendar date of `admitted_at`; mismatch fails closed. Gate-Q approvals use one file per approval at `research/queue/gate_q_approvals/<approval_id>.gate_q_approval.json`. The ID must exactly bind the filename and the queue item's `gate_q.path`. Approval IDs and paths are permanently single-use, existing targets reject, and a hash-valid copy elsewhere is not authoritative. Neither directory is watched by current runner or scheduler code.

## Bounded vocabulary

`queue_target` has one value: `offline_research`. `priority` is `normal` (default ordinary ordering) or `expedited` (human-selected earlier attention). Neither priority changes validation, denominator, dataset, budget, Gate-Q, or later execution requirements, and neither implies dispatch authority.

## Exact admission bundle

Gate Q binds the Strategy Spec, one Gate-C crossing audit record, Variant Manifest, Sweep Plan, source draft, review trail, eligibility report, and Gate-C approval. The Gate-C record reference fixes audit path `research/canonical_crossing_audit/strategy_spec_writes.jsonl`, 1-based line number, Gate-C approval ID, Strategy Spec ID, canonical target path, and SHA-256 of the exact raw JSONL record bytes including its line terminator. Validation locates that line, recomputes its raw hash, parses its IDs/target, and requires exactly one matching record; unrelated later appends do not change the reference. Gate Q also binds the dataset, denominator, budget, priority, target, queue item ID, exact target path, and SHA-256 of the exact UTF-8 queue-item file bytes. Any missing path, unreadable content, schema failure, hash mismatch, symlink escape, lineage mismatch, or post-approval byte change rejects admission.

The queue item carries the Gate-Q ID/path and `approval_core_sha256`. `gate_q_approval_core_v1` hashes every Gate-Q field except `proposed_queue_item` and `approval_core_sha256` using `repo_canonical_json_v1`: recursively reject every floating-point value; serialize UTF-8 with object keys lexicographically sorted by Python/Unicode code-point order, compact `,` and `:` separators, `ensure_ascii=false`, JSON's deterministic string escaping, and no leading/trailing or insignificant whitespace. Integers, strings, booleans, null, arrays, and objects are permitted. This is a repo-local algorithm, not RFC 8785/JCS. This scoped hash avoids an impossible circular full-file hash: Gate Q hashes the exact queue bytes while the queue item binds the immutable approval core. A future writer must recompute both. The full Gate-Q file is still validated and its exact proposed-item binding is mandatory.

## Admission audit

The sole append-only audit is `research/queue/admission_audit/queue_admissions.jsonl`, with each line validated by `research/schemas/queue_admission_audit_record.schema.json`. Stable record ID is `QAUDIT-<queue_item_id>`. Each complete record binds queue item ID/path/hash; Gate-Q ID/path/full-file hash/core hash; Strategy Spec ID/path/hash; VM and Sweep paths/hashes; admitted timestamp; writer version; passed validation; and explicit no-dispatch/no-execution truth. Permanent reuse scans reject any prior Gate-Q approval ID, queue item ID, or queue target path, even if an artifact was later removed.

A future writer must serialize admissions under one exclusive crossing lock, validate before mutation, exclusive-create the queue item, append exactly one complete JSONL record, flush both, and never dispatch. On item or audit failure it must truncate any partial audit append to its prior byte length and remove the newly created item. Failed rollback is integrity-critical, forbids automatic retry, and requires operator inspection. Gate-Q approval artifacts are pre-existing human approvals and are never created or modified by the admission writer.

## Denominator, dataset, and budget

The denominator is `committed_pre_registered_population_count` and must be the same positive integer in the Variant Manifest declared population, its trial-budget denominator, and the Sweep Plan committed/multiple-testing denominator. Mismatch rejects.

Dataset identity requires a nonempty ID and snapshot/version, repo-approved immutable path plus raw-file SHA-256, market `BTCUSDT_BINANCE_USDTM_PERPETUAL`, and a timeframe in `15m|30m|1h|4h|1d`. It must satisfy the Spec/Plan stream and timeframe requirements. Missing, mutable, unresolved, or incompatible data rejects.

Budget uses the sole metric `variant_attempts`, unit `attempts`, an exact positive integer upper bound, and `actual <= upper_bound`. All retries count as attempts. For v1 the bound must equal the committed denominator: no retry allowance or expansion is admitted. Exceedance or mismatch rejects; vague budgets are invalid.

## Later writer requirements

A later separately authorized writer must independently parse and validate all referenced artifacts; recompute raw-file hashes, `repo_canonical_json_v1` approval-core hash, and exact queue bytes hash; validate cross-artifact IDs, dataset compatibility, denominator equality, budget, priority, target, Gate-Q derived path, Gate-C record, and queue-ID UTC date; check the append-only admission audit for reuse; reject used approval IDs, item IDs, or paths; confine paths to repo roots; use atomic exclusive create and the locked rollback semantics; and fail closed. It must create no dispatch request, run output, Result Population, candidate, or notification.

## Traceability

`scratch draft -> review trail -> advisory eligibility -> Gate-C approval -> Gate-C crossing audit -> canonical Strategy Spec -> Variant Manifest -> Sweep Plan -> Gate-Q approval -> admitted/non-dispatched queue item`. Later execution and Result Population steps remain separate and unauthorized here.
