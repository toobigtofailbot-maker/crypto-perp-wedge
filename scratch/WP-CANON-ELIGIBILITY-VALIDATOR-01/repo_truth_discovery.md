# Repo-truth discovery

- Base: `origin/main` at `86b6cd7`; Lane 1 review-state work is merged.
- Scratch input: `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/*.draft_packet.json`.
- Review trail: append-only `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/*.review_events.jsonl`, as implemented by `tools/agent_inbox_intake/service.py`.
- Draft packets expose source request, formalized research object, parameter bounds, explicit capability assessment, provenance, source hashes, blockers, and non-authority flags.
- Data/feature availability truth is represented in the draft capability assessment and backed by `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`. The validator does not claim that a concrete dataset slice exists.
- Concluded-family truth is available in `research/candidate_registry.jsonl` (`status=CONCLUDED`). Canonical family grammar is available in `research/strategy_specs/*.strategy_spec.json`; completed population lineage is available in `research/result_populations/*.result_population.json`.
- The canonical intake control-plane design is `docs/architecture/scratch_to_canonical_intake_control_plane.md`. It requires a later Karl-gated Gate C and does not let this package authorize canonical writes.

Decision: implement the narrowest deterministic lexical/family scan over the committed registry and Strategy Specs, then link matched specs to committed Result Populations. No concluded artifacts are changed.
