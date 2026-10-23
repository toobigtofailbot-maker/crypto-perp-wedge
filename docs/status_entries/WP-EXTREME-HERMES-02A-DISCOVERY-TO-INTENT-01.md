# WP-EXTREME-HERMES-02A-DISCOVERY-TO-INTENT-01

- Branch: `claude/wp-extreme-hermes-02a-discovery-to-intent-01`
- Exact base: `a1d83b9157ee9e9892cd7fc92fe6471b5d8349c2` (#733/#735/#737/#740 merged ancestors)
- Implementation head: `d6b4c49b943d6dec208aadd7d0c4215d85f2fa4d`
- Side 23 narrow correction reviewed at `684011621d9368b6903c5291b680e3eebbdccf5b`;
  the correction head is recorded in the PR body (a commit cannot contain its own SHA).
- Lane A, non-capital, non-scientific-execution; self-merge: no

## Delivered

- `tools/hermes/research_turn.ps1`: default-OFF `-StructuredIntentHandoff`. The
  four existing turns, prompts and files are unchanged. The switch adds one
  `director-intent` turn (memory/session_search only). Only that turn's boundary
  permits non-authoritative typed research-intent drafts; admitted/executable
  intents, proposals and dispatch stay forbidden. The adapter then writes a new
  sibling `<OutputRoot>.discovery-intent` directory.
- `tools/hermes/discovery_intent.py`: deterministic fail-closed adapter over
  native `BoundedResearchRequestV1`/`BoundedResearchIntentDraftInput`, the
  `EvidenceResourceCatalog`, HEAD-blob identity, verbatim HEAD-content quote
  provenance for repo sources and anchors, and the native `hypothesis-v1`
  fingerprint. Per idea: `TYPED_VALID` or a retained `NOT_READY` lead with exact
  failed fields. Repo anchors carry a data-availability, prior-investigation or
  constraint role, never mechanism support. Their semantic relevance remains a
  visible `REVIEWER_CHECK_REQUIRED`. Memory state is reported separately.
  `NEW_UNMATCHED` requires both the repo index and the read-only Postgres lookup
  to succeed; otherwise the state is `UNKNOWN_MEMORY_STATE`.

## Evidence state

- Corrected viability gate: native strict dry-validation of one taker-flow 1h
  draft anchored only to `project://feature-availability` as DATA-AVAILABILITY
  evidence. Its verbatim quote shows taker buy/sell volume is a conditional
  `CANONICAL_KLINE_TAKERFLOW_DERIVATION` limited to canonical 30m/1h/4h/1d bases.
  It establishes neither actual 1h coverage (that needs a D2-021 parent lineage
  check) nor any edge. Mechanism support must come from public research. The
  earlier H-005 (MACD) anchor was not relevant to this mechanism and was removed.
  Semantic relevance remains a reviewer check.
- Research Memory Postgres: the local database has no
  `hermes_research_memory_reader` role and no read-only DSN is configured, so
  Postgres lookups report `UNKNOWN_MEMORY_STATE`; no role was created.
- Physical F1/F2 cycle: `PHYSICAL_BLOCKED` at the fresh-home
  `hermes auth add openai-codex` device-login gate, which needs the owner.
  The end-to-end model-authored packet is unproven.

## Authority

The packet is a draft with zero admission, experiment, approval, scheduler,
runner, candidate, paper/live or capital authority and no consumer. No research
admission, proposal, compiler, Runner, Governor, Prefect, broker, backtest,
canonical or protected write was invoked.
