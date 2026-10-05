# Hermes H0/H1, H2/H2.5, and Typed CPW Domain Tools

This directory is the repo-owned deployment/configuration surface for pinned
Hermes Agent `v2026.8.13` (v0.20.1). The image is pinned by both tag and
multi-architecture digest:

```text
nousresearch/hermes-agent:v2026.8.13@sha256:68e15ae2a6d894d0ccbd9f8aacbbe13d4d28fa5dc9b6a303970b67bb2499b1a6
```

The Project-Evidence sidecar is built from a digest-pinned Python 3.11 image
and the repo lock file. Hermes gets no repository mount. The sidecar receives
only explicit read-only evidence mounts; it does not receive `src/`, `lib/`,
`configs/`, `secrets/`, `research/queue/`, dispatch/KDAUTH, OMS, risk,
reconciliation, paper/live, exchange, order, capital, or credential paths.

## Boundary

Project-Evidence is default-deny and exposes:

- explicit evidence URIs, never caller paths;
- four predeclared in-memory DuckDB queries, never caller SQL;
- parameterized Research Memory alias lookup through a DB-enforced read-only
  role whose mutation privileges are checked at connection time;
- a normalized allowlisted release/security watch with free-form upstream text
  discarded;
- exactly one project write surface: `scratch/hermes_proposal_outbox/`.

The outbox is proposal/prepared-record-only, gitignored, exclusive-create,
symlink/traversal
resistant, source/repo-SHA linked, and marked `not_authority=true`. Nothing in
runner, dispatch, KDAUTH, promotion, readiness, runtime, or protected code reads
the outbox. Hermes state under its separate `HERMES_HOME` is not project state.

H2 evolves the existing `submit_proposal` input into a strict seven-type
contract. Every proposal binds exact resource/query evidence identities, separates
FACT/INFERENCE/OPEN QUESTION, declares an A0/A1/A2 class from closed affected
domains, and requests only human review for a separate future work package.
Project-Evidence re-resolves every declared path/hash before persistence. A0 is
mandatory for protected or ambiguous scope; A2 is limited to explicitly low-risk
proposal domains and grants no standing authority. The outer outbox record and
the typed proposal both require human review and have no automatic consumer.

H2.5 adds exactly one tool, `submit_prepared_payload`, for seven closed inert
plan types. It independently finds a compatible H2 parent by proposal ID in
this fixed outbox, validates the nested H2 object, recomputes the parent content
hash over Hermes canonical UTF-8 JSON bytes with sorted keys and exactly one
trailing LF, re-resolves current evidence, preserves the parent's A0/A1/A2
class, and writes a distinct `HERMES-PREP-*.prepared.json` record. The prepared
payload hash covers only the nested validated payload, never its own hash or
outer metadata. A0 also requires `permanent_non_executable=true` and
`protected_human_gate_only=true`.

PREPARE is still inert human-review content. There is no executable payload,
approval token, broker, dispatcher, automatic consumer, Governor/Prefect/Codex
invocation, project or canonical mutation, dependency update, network hydration,
diagnostic execution, or runtime/trading action. H3 and H4 remain unstarted.

HERMES-01 adds five strict compute-only Project-Evidence tools for capability
assessment, reasoned-draft formalization, preregistration packet construction,
approval-requirement description, and trial-denominator validation. Hermes
provides generic reasoning; framework-neutral CPW domain functions remain the
single owner of research/scientific semantics. Project-Evidence re-resolves
repo inputs and binds every result to the exact repo SHA, repo path, and
artifact hash. Model content is untrusted reasoning input, not evidence. The
tools write no artifact and grant no canonical, approval, execution,
candidate/promotion, scheduler/Prefect, runtime/risk, paper/live, or capital
authority. H2/H2.5 behavior is unchanged. HERMES-02 01A adds one manually
triggered, fixed-command, non-authoritative bounded research-intent handoff.
Project-Evidence resolves exact evidence and performs exact read-only Research
Memory dedup before emitting a strict intent; the handoff stops before Governor,
Optuna, runner, canonical, promotion, runtime, paper/live, or capital authority.
HERMES-03 canary/runtime consolidation remains future work.

## One-time PostgreSQL role setup

Run `research_memory_readonly_role.sql` as the Research Memory database owner,
then set authentication for the fixed `hermes_research_memory_reader` role by
your normal secret-management process. Do not place its DSN in the repository
or the Hermes model-credential file. Pass only that role's DSN to `start.ps1`.

The sidecar sets `default_transaction_read_only=on`, issues `SET TRANSACTION
READ ONLY`, and refuses service if the role has any mutation privilege on the
four Research Memory tables. An absent DSN leaves the rest of MCP available and
causes Research Memory lookups to fail as UNKNOWN; it never falls back to a
write-capable DSN.

## Start

Use a project-specific home outside the repository. Authenticate that home with
the pinned Hermes native `openai-codex` device flow (`hermes auth add
openai-codex`), which stores its ChatGPT/Codex OAuth state only under the
external Hermes home. The deployment does not require or read
`OPENAI_API_KEY`.

```powershell
.\tools\hermes\start.ps1 `
  -HermesProjectHome C:\Hermes\crypto-perp-wedge `
  -HermesModel '<Codex model available to the authenticated plan>' `
  -ResearchMemoryReadOnlyDsn $env:RESEARCH_MEMORY_READONLY_DSN `
  -InstallSchedules
```

The script resolves the exact Git SHA/branch, rejects a repo-contained or linked
Hermes home, validates Compose, starts the pinned services, and idempotently
adds the three repo-owned schedule-plan jobs by name. It prints no DSN or model
credential. Compose runs the pinned Hermes CLI directly as its built-in
`hermes` user (UID/GID 10000) with Docker as the external supervisor; this
avoids granting the image's optional `s6` bootstrap any extra capabilities.

## Physical acceptance (required on the deployment host)

This repo cannot prove that a host has Docker, model credentials, or Research
PostgreSQL connectivity. On the intended Docker-capable host, run the command
above, then verify:

```powershell
docker compose -f tools\hermes\compose.yaml ps
docker compose -f tools\hermes\compose.yaml exec -T hermes hermes cron list
```

Exercise `project_evidence_manifest`, one allowed resource, one denied resource,
one allowed query, one denied query, one Research Memory lookup, one mutation
attempt (which must be rejected by the DB role), and one proposal. Restart both
containers and repeat the manifest/mount inspection. Do not report physical H0
acceptance until those checks pass.

## Reporting samples

`samples/daily-research-brief.md` and `samples/weekly-science-review.md` are
deterministic repo-only acceptance outputs anchored to base SHA
`12ea35c8a6cfc60fc439527104ad9a67a162e4fb`. They intentionally mark physical
deployment state UNKNOWN rather than fabricating it.
