# Hermes H0/H1 Read-Only Research Operator

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

The outbox is proposal-only, gitignored, exclusive-create, symlink/traversal
resistant, source/repo-SHA linked, and marked `not_authority=true`. Nothing in
runner, dispatch, KDAUTH, promotion, readiness, runtime, or protected code reads
the outbox. Hermes state under its separate `HERMES_HOME` is not project state.

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

Use a project-specific home outside the repository. Store Hermes model
credentials only in that home according to upstream Hermes setup guidance.

```powershell
.\tools\hermes\start.ps1 `
  -HermesProjectHome C:\Hermes\crypto-perp-wedge `
  -HermesModel '<configured-provider/model>' `
  -ResearchMemoryReadOnlyDsn $env:RESEARCH_MEMORY_READONLY_DSN `
  -InstallSchedules
```

The script resolves the exact Git SHA/branch, rejects a repo-contained or linked
Hermes home, validates Compose, starts the pinned services, and idempotently
adds the three repo-owned schedule-plan jobs by name. It prints no DSN or model
credential.

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
