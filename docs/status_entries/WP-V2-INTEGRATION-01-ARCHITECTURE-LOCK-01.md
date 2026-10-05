# WP-V2-INTEGRATION-01-ARCHITECTURE-LOCK-01

- Package: `WP-V2-INTEGRATION-01-ARCHITECTURE-LOCK-01`
- Branch: `codex/wp-v2-integration-01-architecture-lock-01`
- Execution base: `a295299cb18ca247c14114cd9f06f7b4e29c90c5`
- Decision: `D2-022`
- Package class: T0 documentation/process-policy architecture lock
- Pull request: [#728](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/728),
  open and non-draft
- Substantive head: `10e09a1db3f810defddf149bc7569067080ec22d`
- Merge posture: held for Side exact-head review; no self-merge

## Exact changed-file set

1. `docs/architecture/2026-10-hermes_research_integration_handoff_lock.md`
2. `docs/decisions.md`
3. `docs/project_status.md`
4. `docs/status_entries/WP-V2-INTEGRATION-01-ARCHITECTURE-LOCK-01.md`

## Delivered boundary

D2-022 locks the first HERMES-02 proof to a CPW-owned fixed-command host-side
adapter under Prefect operational control. `BoundedResearchIntent v1` is the
strict non-authoritative handoff; Project-Evidence / CPW owns evidence
re-resolution, validation, and exact read-only `hypothesis-v1` deduplication.
A later CPW-only deterministic builder owns intent-to-`SearchContract`
conversion. Search Governor retains scientific/search-legality authority,
Optuna remains proposer-only, Prefect remains operational-only, and H2/H2.5
remain inert.

01A and 01B remain separately authorized future implementation packages. The
lock activates no Stage 5B, autonomous research, runner, runtime, paper/live,
or capital path.

## Validation

- `git diff --check`: passed.
- `tools/dev/verify.py --validation-preset docs-only --json`: passed with
  `overall_status=pass` and no forbidden-path matches.
- Exact four-file changed-scope check: passed.
- Semantic and forbidden-scope inspection: passed; only the four authorized
  Markdown files changed.

## Zero-code / zero-runtime statement

This package changes exactly four Markdown files. It changes no code,
dependency, config, schema, validator, query layer, Research Memory, Hermes,
Prefect, Search Governor/Optuna, H2/H2.5, research artifact, runtime, protected
execution surface, paper/live behavior, or capital authority.
