# Repo-truth discovery

Package: `WP-CANON-DISPATCH-CONTROL-PLANE-DESIGN-LOCK-01`
Base: refreshed `origin/main` at `1c22edf602f748ed03d9304c66b4b40cd6f0d601`

## Preflight facts

- The drafting anchor equals refreshed `origin/main` and is an ancestor.
- The root checkout was clean but occupied by the explicitly parallel `codex/wp-runner-1d-real-data-capability-01` branch. It was left untouched. This package uses the isolated worktree `C:/GitHub/crypto-perp-wedge-wp-canon-dispatch-control-plane-design-lock-01` created directly from `origin/main`.
- The requested branch did not exist locally or remotely before creation.
- `gh pr list --state open` returned zero open PRs, so no overlapping dispatch/execution contract or `docs/project_status.md` edit was open.
- PR #664 is merged in the base. `QI-20260717-H004R2B1` exists with `status="admitted_non_dispatched"`; its Gate-Q approval and admission audit exist; no production dispatch, execution stream, or `RP-0007` exists.
- The blocked H-004 worktree has exactly twelve untracked Stage-A files. Their preflight SHA-256 values were captured before this worktree was created; no file in that worktree was edited.
- `STRAT-SPEC-0007` hash readiness and the 1d runner gap remain external parallel tracks.

## Existing idioms

### Identity and immutable naming

- Canonical queue IDs use date plus uppercase fixed-width suffix: `QI-YYYYMMDD-XXXXXXXX`.
- One immutable JSON object per ID is stored at an ID-derived path.
- Approval, queue-item, and target paths are permanently single-use; historical audit evidence prevents reuse after improper removal.
- This package follows those idioms with `DSP-YYYYMMDD-XXXXXXXX`, `RUN-YYYYMMDD-XXXXXXXX`, and derived filenames.

### Schema and JSONL

- Research schemas use JSON Schema Draft 7, closed objects, explicit required fields, const/enums, tagged lowercase hashes matching `sha256:<64 lowercase hex>`, and explicit non-authority declarations.
- `queue_admissions.jsonl` and other event/audit surfaces treat each LF-terminated line as one independently parseable record.
- Event idioms use stable event IDs, timestamp, actor, type, and monotonic sequence.
- The Result Population outcome vocabulary is `successful|failed|invalid|excluded|errored|aborted|filtered|data_unavailable|not_attempted`; this package reuses it unchanged.

### Canonical JSON and raw hashes

- `repo_canonical_json_v1` rejects floats, sorts object keys by Python/Unicode code point, uses compact separators and UTF-8 with `ensure_ascii=false`, and adds no incidental whitespace.
- Gate-C audit references hash exact raw JSONL record bytes including LF.
- Artifact references use exact raw-file SHA-256 rather than parsed-object equivalence.

### Crossing, lock, rollback, and reuse

- `tools/canon_intake/queue_admission.py` rejects symlink components and path traversal, resolves paths under repo root, takes an exclusive `O_CREAT|O_EXCL` lock, revalidates inside the lock, exclusive-creates targets, flushes/fsyncs, and scans historical records for ID/path reuse.
- Queue admission rolls back its two-surface transaction. Option C differs intentionally after the dispatch crossing: the immutable dispatch and append-only event history must be preserved, so post-crossing failures cannot delete or truncate history.
- A partial execution append remains crash-visible rather than being silently repaired.

### Denominator, budget, and authority

- Queue/Gate-Q fix denominator basis `committed_pre_registered_population_count` and budget metric `variant_attempts` with retries counted, `actual <= upper_bound`, mismatch/exceed rejection, and v1 upper bound equal to denominator.
- Admission has no dispatch or execution authority. Result Population is canonical scientific evidence only through its separate schema/validator and has no ranking/recommendation/readiness/runtime authority.
- Dispatch/execution records therefore own control-plane history only and cannot replace RP, EXP/REP/OL/REC/DEC, candidate, ranking, recommendation, promotion, paper/live, or runtime artifacts.

## Preserved Stage-A evidence

The twelve uncommitted files under `C:/GitHub/crypto-perp-wedge-wp-canon-h004-dispatch-gated-01/scratch/WP-CANON-H004-DISPATCH-GATED-01/` were inspected read-only. They prove:

- no merged dispatch/execution contract existed at the base;
- queue/admission were inert and unchanged;
- no production dispatch/execution/RP existed for H-004-R2;
- the runner was `wp-s2c-190-build-test-v1`, SHA-256 `sha256:bbd34bf955292bfe7bd00949f0cc5cab3687007476819ff65613db5c7da91c0e`;
- the public validated 1d real-data runner path was independently absent;
- no run or canonical write occurred.

## Pre-change preservation hashes

| Path | SHA-256 |
| --- | --- |
| `research/queue/admissions/QI-20260717-H004R2B1.queue_item.json` | `47ba045b4ac89588e1865c280b080f0922cef6bb1e7d4e7880090ba07a44d967` |
| `research/queue/gate_q_approvals/GATE-Q-H004-R2-04B-0001.gate_q_approval.json` | `8645018c04a565761d72047b5225fbfd5694e342f5180407f0c8b111ba310fed` |
| `research/queue/admission_audit/queue_admissions.jsonl` | `e668475f7d9f0d3d3c425a173aa1eb593814d824d4590c794887bde21368d3e2` |
| `research/strategy_specs/STRAT-SPEC-0007.strategy_spec.json` | `b23ebc1093df51b7fab5e39c46fd2b96b5e71d35300134eb319a5cbc32d0857c` |
| `research/variant_manifests/VM-0007.variant_manifest.json` | `822da9ca46eca4f3a9d4d86936fdd3447004ef77806fc3ce60ab0cf979ea171d` |
| `research/sweep_plans/SWEEP-PLAN-0007.sweep_plan.json` | `66d48ec6d57048012dcd243ca7dda25dcf59241b1a3733dc05796eb46d7af2f0` |
| `tools/research_runner/run_offline_sweep.py` | `bbd34bf955292bfe7bd00949f0cc5cab3687007476819ff65613db5c7da91c0e` |
| `research/schemas/result_population.schema.json` | `128c744cec03a360977d330b6ddd5b436fcbad5b023aa43744dc5e3da47ccdec` |
| `tools/registry/validate_result_populations.py` | `7268065e205419db49e9065264743b6c168714d14bac9e54638680c53eb9a615` |

## Integrity baseline

All 58 discovered `v_integrity_*` views were run from one read-only in-memory query connection. Exactly one view was nonempty:

`v_integrity_strategy_spec_hash_readiness` -> `strategy_spec_hash_readiness_violation`, `STRAT-SPEC-0007`, `hash_pinning.hash_status`, expected `computed when intended_for_variant_manifest=true`, actual `not_computed`.

Canonical sorted JSON SHA-256 over the complete view-name-to-row map: `sha256:b5037fc44bb0ef659dc5b178dee29d0b2632c8d59ebd33fa71df9e1990df6e38`.

## Decision

No repo idiom conflicts with Main's Option-C semantics. Additive contract work may proceed. No writer, runner invocation, production instance, query view, or protected boundary is required.
