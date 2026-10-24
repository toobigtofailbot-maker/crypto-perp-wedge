# WP-EXTREME-HERMES-02B-DISCOVERY-TO-NATIVE-INTENT-01

- Branch: `claude/wp-extreme-hermes-02b-discovery-to-native-intent-01-cc`
- Exact base: `aee8e71f969297ffe29c1c1a1e97a600444bcecf` (origin/main; contains PR #748
  merge `6c5df27e2a563de8cecabaca96f41fb9886f6ba1`)
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/751
- Implementation head: `599cb948`; this PR-URL-only commit follows it (a commit cannot contain its own SHA)
- Lane A, T2, default OFF, non-capital, no scientific execution; self-merge: no

## Delivered (exact four-file allowlist)

- `tools/hermes/discovery_intent_consumer.py`: manual `inspect` / `materialize` /
  `verify` CLI. It consumes one verified 02A `*.discovery-intent` packet and
  processes every idea in source order, with no ranking or strategy selection.
  Source integrity reuses `discovery_intent.verify_directory` and the 02A cycle
  gate. It also checks model-turn receipts, the critic receipt, the exact
  retained-input inventory, the exact packet and idea field sets, the authority
  flags, unaltered Hermes-authored fields, native re-validation of
  `validated_draft_input`, and fingerprints. The source `repo_sha` must equal the
  current HEAD; it is never rebound.
  For each `TYPED_VALID` idea, anchors are re-resolved against current committed
  bytes and verbatim HEAD quotes, and must be backed by repo sources (public
  sources can never be anchors). Then the unmodified `BoundedResearchIntentBuilder`
  binds the idea through `EvidenceResourceCatalog`, `RepoIdentity` and the
  read-only reader. The native intent must pass contract round-trip,
  `semantic_content_sha256`, fingerprint, anchor/repo identity and non-authority
  checks.
- `tests/test_hermes_discovery_intent_consumer.py`: 29 offline tests.
- `tools/hermes/README.md`: a concise manual operator/verify section.
- This status fragment. `docs/project_status.md` is untouched.

## Output contract

The output is a new external directory with `summary.json`,
`intents/NN.native_intent.json` (only for successful native builds) and
`SHA256SUMS`. It is closed, content-hashed and deterministic. Per-idea statuses
are `NATIVE_INTENT_BUILT_REVIEW_REQUIRED`, `NOT_READY_LEAD`,
`BLOCKED_MEMORY_UNAVAILABLE`, `BLOCKED_EVIDENCE_UNVERIFIED` and
`BLOCKED_NATIVE_BUILD_FAILED`. The summary keeps critic assessments, gaps,
citations and next investigations. It also records the original 02A memory state
next to the separate refreshed read-only lookup; no match is never novelty, and
similarity is never equivalence. Anchor relevance, data coverage and mechanism
remain explicit reviewer requirements. `not_authority=true` is set and there is
no automatic consumer. Any global integrity failure, stale SHA, link or junction,
collision or secret means nothing is written.

## Evidence state

- Focused (WP command): 92 passed. Adjacent `test_hermes_domain_tools.py` +
  `test_project_evidence_mcp.py` (includes the native write-capable-role
  rejection test): 64 passed. `test_research_memory_postgres.py`: 3 skipped,
  because `RESEARCH_MEMORY_TEST_DSN` is not configured (environment skip, not a
  pass). Ruff is clean on the new files.
- Physical 02A packet `C:\HermesReports\02a-intent-03.discovery-intent`
  (content `ca3de60e...`, bound to `023d51c31b0589b54085ef82abcfa0878e47dc28`).
  `inspect` passed full strict source verification and reports
  `HISTORICAL_SOURCE_SHA_NOT_CURRENT_HEAD_MATERIALIZATION_REFUSED`.
  `materialize` exits 1 as stale and writes no output. The packet bytes are
  unchanged (`packet.json` `b5254dec...`).
- Research Memory DSN: `RESEARCH_MEMORY_READONLY_DSN` is not configured here, so
  there is no live PostgreSQL positive. Native binding is proven only with a
  frozen read-only fixture. Without the DSN, typed ideas fail closed as
  `BLOCKED_MEMORY_UNAVAILABLE` and leads are retained. No role, credential or
  database change was made.

## Authority

No new Hermes model turn, backtest, experiment, admission, Prefect, Optuna,
Runner, Governor, Stage 5B, canonical write, database administration, Lane B,
paper/live or capital action occurred. The batch output authorizes no research
even when native intents exist. Held for Side 23 exact-head review and Karl's
merge decision.
