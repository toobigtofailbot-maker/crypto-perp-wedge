# WP-EXTREME-HERMES-02C-INTENT-TO-STRATEGY-SPEC-DRAFT-01

- Branch: `claude/wp-extreme-hermes-02c-intent-to-strategy-spec-draft-01`
- Exact base: `e6074075017f23d9e960ed0a44d606beb0d2aaec` (origin/main; contains PR #751 / 02B head
  `6c2933eb981c9af36efd9e61a78027ee2f391d63`)
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/752
- Implementation head: `ccedfa4cf362d9d45ea08cac6f06ee3c99d65d44`; this PR-URL-only commit follows it (a commit cannot contain its own SHA)
- Lane A, T2, default OFF, noncanonical, non-capital, no scientific execution; self-merge: no

## Delivered (exact four-file allowlist)

- `tools/hermes/intent_strategy_spec_handoff.py`: a manual `prepare` / `build` / `verify` CLI.
  - `prepare` re-verifies one 02B batch: `verify_batch`, the closed summary and idea field sets,
    every `BoundedResearchIntentV1` (`semantic_content_sha256`, fingerprint, request id, repo SHA,
    instrument scope), and that the batch is bound to the current HEAD.
  - It writes one strategy-developer request + prompt per built intent. All bound data comes from
    the intent and the 02B context, as data. Every lead and blocked idea is retained in source order.
  - `build` re-renders the prepared directory byte-for-byte from its own source copy, then imports
    captured replies offline. A typed-safe `ReasonedDraft` goes unchanged to
    `CpwDomainTools.formalize_strategy_draft`, and drafts are emitted only through the existing
    `validate_strategy_specs`.
  - `verify` rechecks bytes and links and re-validates the drafts. With
    `--prepared-dir/--responses-dir` it replays the build byte-for-byte.
- `tests/test_hermes_intent_strategy_spec_handoff.py`: 35 offline tests. They reuse the merged 02B
  fixtures (`make_packet`, `FrozenMemory`) to build real current-HEAD 02B batches.
- `tools/hermes/README.md`: a concise opt-in operator section (input/output, manual model step,
  non-authority).
- This status fragment. `docs/project_status.md` is untouched.

No native component was modified: 02A/02B, Project-Evidence domain tools, formalization,
validator, schema, compiler, Research Memory, `research_turn.ps1`, Prefect, Governor and Optuna
are all unchanged.

## Requirement -> evidence

| Requirement | Evidence |
|---|---|
| Verify all 02B inputs; whole-batch tamper/stale fails closed | `test_stale_head_and_tampered_prepared_or_source_fail_closed`, CLI stale refusal in `test_cli_prepare_build_verify_replay_and_stale_refusal` |
| Preserve all ideas, order, leads | `test_prepare_keeps_every_idea_in_order_and_binds_each_request` (DON, FLOW, LOB) |
| Strict `ReasonedDraft` reply with exact id/hash echo | `test_invalid_model_responses_stay_not_ready_with_cause` (14 cases), `test_replay_substitution_and_inventory_tampering_fail_globally` (8 cases) |
| Supported native family -> schema-valid noncanonical draft | `test_supported_family_drafts_unsupported_stays_not_ready_and_replay_is_exact` (donchian 4h; `validate_strategy_specs == []`; draft/none/no-reviewer flags) |
| Unsupported order-flow / volatility -> `NOT_READY_UNSUPPORTED_FAMILY` / `NEEDS_CAPABILITY` | same test (FLOW) + `test_needs_data_family_mismatch_and_second_unsupported_family` (VOL) |
| Compiler-visible but no history -> no testability claim | same test (OI: `NOT_READY_NEEDS_DATA`, `historically_testable_now is False`) |
| No relabeling of families | same test (MIS: `NOT_READY_FAMILY_MISMATCH`) |
| Missing / declined / invalid replies | `test_missing_and_declined_responses_stay_not_ready`, invalid-response matrix |
| Negative memory and critic agreement retained | `test_prior_negative_memory_and_critic_stance_are_preserved` |
| Fake anchors / URLs / tool requests rejected | invalid matrix: `draft_evidence_anchor`, `url_in_text`, `tool_request` |
| Evidence drift vs HEAD | `test_evidence_drift_from_head_blocks_that_idea` |
| Links, collision, external-only, race after preflight | `test_links_output_collision_and_race_after_preflight` (Windows run; Linux uses the unchanged 02B `renameat2(RENAME_NOREPLACE)` primitive) |
| Deterministic replay | byte-identical rebuild + CLI `verify` replay; a changed reply fails replay |
| Zero scientific/trading consumers, no subprocess | `test_native_family_ids_match_formalizer_and_no_subprocess_or_consumer_is_reached` |
| Model authorship never claimed from text | `test_operator_capture_is_recorded_but_not_claimed_authentic` |

## Output contract

- **Prepared** (`AWAITING_MODEL_REASONING`): `manifest.json`, `requests/NN.request.json`,
  `requests/NN.prompt.md`, `source/` (byte copy of the 02B batch) and `SHA256SUMS`.
- **Built**: `summary.json`, `ideas/NN.receipt.json` for every idea,
  `drafts/NN/<STRAT-SPEC-id>.strategy_spec.json` (only for
  `DRAFT_SPEC_SCHEMA_VALID_REVIEW_REQUIRED`) and `SHA256SUMS`.
- **Every receipt keeps**:
  - critic, sources and both memory states;
  - the native formalization envelope (input hash, anchors, capability assessment, adapter
    metadata, the native adapter's own parameter bounds);
  - the model's uncertainty and contradictions;
  - the dispositions `COMPILER_CHECK_NOT_PROVEN`, `DATA_COVERAGE_UNVERIFIED` and
    `NOT_ADMITTED_NO_PREREGISTRATION_NO_EXECUTION`.
- **Provenance**: the native `source_type: manual_idea` is labeled as native-internal only. The
  summary records the true 02A -> 02B -> 02C chain.
- **Hashes and publication**: no wall-clock time enters any hash. Output is external only,
  published exclusive-create with atomic no-replace.

## Evidence state

- Physical model proof: `PHYSICAL_BLOCKED_NO_CURRENT_HEAD_NATIVE_BATCH`. No 02B batch exists on
  this host; `C:\HermesReports` holds only 02A cycles and packets.
  - `discovery_intent_consumer.py inspect` on `C:\HermesReports\02a-intent-03.discovery-intent`
    reports `HISTORICAL_SOURCE_SHA_NOT_CURRENT_HEAD_MATERIALIZATION_REFUSED`. The packet is bound
    to `023d51c3...` and its content is `ca3de60e...`.
  - Pointing 02C `prepare` at that 02A packet exits 1 and writes nothing.
  - A fresh 02A -> 02B physical source is not authorized by this WP, so no Hermes request was sent.
  - All positive evidence is current-HEAD labeled fixtures (`LABELED_FIXTURE_NOT_MODEL_OUTPUT`),
    not model output or physical research.
- Research Memory: no DSN here. The 02B fixtures use the frozen read-only memory fixture.
- Science: no scientific, backtest, holdout, Stage 5B, Prefect, trading or capital action and no
  claim. A schema-valid draft is not a compiled, data-covered or profitable strategy.

## Limitations

- Only the four native family adapters can yield a draft. Arbitrary families stay `NOT_READY` until
  a separately authorized adapter/compiler WP.
- The URL and tool-request screens on reply text are deliberately conservative regexes and can
  produce false positives (fail-closed). Edge claims in prose are not machine-detected. Every
  receipt carries `MODEL_PROSE_IS_NOT_EVIDENCE`.
- The static compiler check (`spec_signal_compiler`) is not run. The disposition is honestly
  `COMPILER_CHECK_NOT_PROVEN`.

Next (not authorized here): 02D candidate-agnostic admission / pre-registration / SearchContract
bridge.
