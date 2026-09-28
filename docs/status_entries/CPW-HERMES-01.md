# CPW-HERMES-01 — Typed CPW Domain Tools

## Package and finality

- Work package: `CPW-HERMES-01`
- Package class: MIGRATION; validation tier T2
- Branch: `codex/cpw-hermes-01-typed-cpw-domain-tools`
- Base SHA: `283969cc8b981e61fa0e8a28f620ad9a9f7b522d`
- Original implementation and physical-acceptance head:
  `c2efd0d4ad1dc96eef753d9fc29fe46efa928c44`
- Side Follow-up 02 reviewed head: `cb67772813b98ac8b1f24b39f2c524d3ce4ee524`
- Follow-up 02 implementation and physical-acceptance head:
  `42cf701dd86d5655510f2b90fbae7457e4d62112`
- PR: [#718 — CPW-HERMES-01: Add typed CPW domain tools](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/718)
- Final head: the commit containing this status-only factual tail; its immutable
  SHA is recorded in the PR body and exact-head handoff because a commit cannot
  contain its own object ID.
- Merge state: open, non-draft, not merged; Side exact-head review remains
  required.

## Delivered contract

Project-Evidence manifest `project_evidence_mcp_v3` exposes exactly 13 tools:
the existing eight bounded tools plus
`cpw_assess_research_capabilities`, `cpw_formalize_strategy_draft`,
`cpw_build_preregistration_packet`, `cpw_build_approval_requirement`, and
`cpw_validate_trial_denominator`. Four exact static resources bind the indicator
catalog, feature-availability catalog, Strategy-Spec template, and
Strategy-Spec schema to repo paths, artifact hashes, and the exact repo SHA.

The public pure `formalize_reasoned_strategy_draft` function is the shared CPW
owner of current reasoned-draft semantics. The legacy IdeaFormalizer delegates
to it with compatibility provenance, while the MCP passes truthful
caller-neutral provenance. All new outputs are deterministic, in-memory,
noncanonical domain results. They create no approval, execution, scheduler,
canonical, candidate, promotion, runtime, risk, paper/live, or capital
authority.

Hermes remains pinned to Agent `v2026.8.13` / control `v0.20.1`, image digest
`sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6`.
The repo-owned Hermes skill count is exactly nine. Hermes has no repo mount. The
Project-Evidence image contains `tools/research_domain` and excludes research
agents, runners, and protected runtime code.

## Side exact-head Follow-up 02

Side review of `cb67772813b98ac8b1f24b39f2c524d3ce4ee524` identified and
authorized two narrow semantic corrections. Hermes-created Strategy-Spec
parents no longer claim the indicator catalog as the persisted path of the
in-memory IDEA concept. Generic source context now accepts a real lineage path,
a deterministic lineage hash, or both, and requires at least one. The Hermes
adapter supplies `lineage_ref_path=null` and `lineage_ref_hash=input_sha256`;
fixed and caller evidence remain in `provenance.source_refs`. The legacy
IdeaFormalizer continues to use its real scratch path with `ref_hash=null`, and
its fixed-input oracle remains unchanged.

The approval-requirement adapter now extracts the packet's pipeline id and
three frozen input objects, reconstructs the packet through the existing CPW
`build_preregistration_packet` domain owner, and requires deep equality before
calling `build_approval_requirement`. Rehashed packets with an altered
canonical-write flag, execution scope, non-authority flags, approval binding,
or an extra top-level field fail closed. Exact valid packet and approval-output
bytes remain unchanged. The tool inventory, schema, dependencies, Hermes
configuration, image, and authority boundary are unchanged.

## Validation

- Pre-mutation immutable legacy oracle: `146 passed`.
- Original focused domain/new-tool validation: `39 passed`.
- Follow-up 02 focused domain/new-tool validation: `44 passed`.
- Post-change legacy semantic oracles: `146 passed`.
- MCP/deployment/H2/H2.5 adjacency: `130 passed`.
- Corrected H2.5 exact oracle: `1 passed`.
- Ruff check: passed; Ruff format check: 12 files already formatted.
- Compileall: passed.
- Docker Compose configuration: passed.
- Base-to-head scope check: `allowed_file_violations=[]` and
  `forbidden_matches=[]`.
- `git diff --check`: passed.
- Final rebase: branch was already current with `origin/main` at the base SHA;
  no rewrite and no content change.
- full pytest: NOT RUN — bounded T2 Hermes/domain migration; focused, directly
  affected legacy-consumer, MCP/deployment, H2/H2.5, and physical acceptance
  evidence are the merge evidence; no dependency, canonical writer, execution,
  runtime, OMS, reconciliation, risk, paper/live, or capital surface changed.

## Physical Hermes acceptance

Docker's Linux engine was reachable. Project-Evidence and Hermes were rebuilt
or restarted and inspected at the implementation head. The live manifest bound
repo SHA `c2efd0d4ad1dc96eef753d9fc29fe46efa928c44`; live discovery returned exactly
the required 13 tools; and each of the five new tools succeeded through the
deployed MCP.

An authenticated `openai-codex` / `gpt-5.6-luna` Hermes interaction bound the
manifest, read the four minimum exact resources, assessed a supported BTCUSDT
Donchian idea, produced and formalized a strict draft, built the noncanonical
preregistration packet and approval requirement, and validated a two-of-two
synthetic denominator containing completed and blocked trials. It explicitly
reported that the approval requirement was not approval and stopped without
research execution or writes. Before/after checks found a clean Git state, no
research-path mutation, and zero proposal/prepared outbox files. After both
services restarted, the manifest, exact 13-tool inventory, and one bounded
capability call succeeded again. No secret was printed or recorded.

Follow-up 02 physical acceptance repeated this proof at
`42cf701dd86d5655510f2b90fbae7457e4d62112`. Live formalization returned one
accepted draft whose parent had `ref_path=null` and
`ref_hash=sha256:1f2d2ebf1c0cd68c7d3f7449e38706e267e78d1d54979d461cec3807da48a9b9`,
exactly matching that response's `input_sha256`; all four evidence URIs
remained in both anchors and provenance source refs. A packet built by the live
preregistration tool was accepted by the live approval-requirement tool with
`approval_authority=false`, while a rehashed packet with
`canonical_write_allowed=true` was rejected as not the exact locked CPW
packet. The authenticated bounded model chain passed again. Git and research
paths remained clean, the outbox stayed empty, and the restart proof again
returned manifest v3, exactly 13 tools, and a successful bounded capability
call.

## H2/H2.5 oracle correction

On the base SHA,
`test_actual_surfaces_have_no_prepared_consumer_or_dispatch` contained a stale
pre-existing global assertion forbidding the string `prefect`, although merged
CPW-PREFECT-01 already contained `tools/prefect_integration/__init__.py` and
`tools/prefect_integration/acceptance.py`. Read-only inspection confirmed that
surface contains none of `.prepared.json`, `PreparedPayload`,
`submit_prepared_payload`, or `HERMES-PREP`.

The authorized correction adds `tools/prefect_integration` to the explicit
prepared-payload marker scan, removes only the obsolete global name assertion,
and preserves the Codex prepared-payload consumer protection. The exact
corrected test passed, and the full 130-test H2/H2.5 adjacency set passed.
`tools/prefect_integration/**` remained unchanged. The invariant remains: no
H2.5 prepared-payload consumer or dispatch path.

## Scope and boundary

The final base-to-head diff contains exactly the 20 authorized files; the
single scope expansion is `tests/test_hermes_prepare.py`, and this status entry
is the final authorized path. Follow-up 02 changed only
`tools/research_domain/formalization.py`,
`tools/mcp/project_evidence/domain_tools.py`, `tests/test_research_domain.py`,
`tests/test_hermes_domain_tools.py`, and this existing status entry; it created
no file. `docs/project_status.md`, dependency files,
Prefect production code, Search Governor, runners/backtesters, CANON, BROKER,
runtime, paper/live, OMS, reconciliation, risk, overlay, safe mode,
kill-switch, exchange/order, credentials, collateral, and capital surfaces are
unchanged. H2 proposals and H2.5 prepared payloads retain their existing inert,
non-authoritative semantics.

## Runway

After CPW-HERMES-01 merges, return to Side/Main. Karl's current top-level
serialized plan points to RESEARCH-02 next. HERMES-02 and HERMES-03 remain
future packages and are not authorized by this package. This entry grants no
merge authority; the PR is held for Side exact-head review.
