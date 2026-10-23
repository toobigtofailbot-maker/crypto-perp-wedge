# WP-EXTREME-HERMES-02A-DISCOVERY-TO-INTENT-01

- Branch: `claude/wp-extreme-hermes-02a-discovery-to-intent-01`
- Exact base: `a1d83b9157ee9e9892cd7fc92fe6471b5d8349c2` (#733/#735/#737/#740 merged ancestors)
- Implementation head: `d6b4c49b943d6dec208aadd7d0c4215d85f2fa4d`
- Lane A, non-capital, non-scientific-execution; self-merge: no

## Delivered

- `tools/hermes/research_turn.ps1`: default-OFF `-StructuredIntentHandoff`. The
  four existing turns, prompts and files are unchanged; the switch adds one
  `director-intent` turn (memory/session_search only) and runs the adapter into
  a new sibling `<OutputRoot>.discovery-intent` directory.
- `tools/hermes/discovery_intent.py`: deterministic fail-closed adapter over
  native `BoundedResearchRequestV1`/`BoundedResearchIntentDraftInput`, the
  `EvidenceResourceCatalog`, HEAD-blob identity, and the native `hypothesis-v1`
  fingerprint. Per idea: `TYPED_VALID` or retained `NOT_READY` lead with exact
  failed fields. Memory state is reported separately as `EXACT_DUPLICATE`,
  `PRIOR_FAILED_INVESTIGATION`, `POSSIBLE_SEMANTIC_SIMILARITY`, `NEW_UNMATCHED`
  (only after a successful read-only Postgres lookup) or `UNKNOWN_MEMORY_STATE`.

## Evidence state

- Viability gate: PASS. A relevant taker-flow 1h draft natively validates and
  binds to `project://feature-availability` and `evidence://hypothesis/H-005`
  with matching HEAD-blob SHA-256; no exact repo-index fingerprint match.
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
