# WP-HERMES-H0-H1-READONLY-OPERATOR-01

## Package State

- Branch: `codex/wp-hermes-h0-h1-readonly-operator-01`
- Refreshed base: `b6331a973fbe7a2e7568913dedbde6b457cc8eb4`
- Physical-acceptance implementation head: `8b582225cc831a3d595fe5476154af89504b36d8`
- PR: <https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/706>
- Package class: T2 bounded read-only research operator
- Result: physical H0/H1 acceptance and final status-only delta validation PASS

## Delivered Surface

The package adds a pinned Hermes v2026.8.13 deployment and a repo-owned
Project-Evidence MCP boundary. Hermes can read only allowlisted project
evidence, run predeclared read-only queries, look up the PostgreSQL Research
Memory index through a dedicated read-only role, check a dependency-watch
manifest, and submit non-authoritative proposal files to one external outbox.

The final dependency state preserves both direct pins:

- `optuna==4.9.0`
- `mcp==1.28.1`

## ChatGPT/Codex OAuth Acceptance

- Provider: `openai-codex` through ChatGPT/Codex OAuth.
- Selected supported model: `gpt-5.6-luna`.
- Account pool: exactly one credential, safely labeled `second-account`.
- The previously quota-blocked credential was removed from the Hermes pool;
  there is no multi-account fallback, rotation, or load balancing.
- Authenticated live catalog access returned nine models and included the
  selected model.
- The one bounded smoke inference returned exactly
  `SECOND_ACCOUNT_SMOKE_OK`.
- Credential material remains in the external Hermes/Codex auth store only.
  No auth store is tracked by the repository.
- `OPENAI_API_KEY` is absent from the external Hermes `.env`, both deployment
  containers, and the repository auth/config surface; it was not required or
  used for acceptance. The surrounding Codex host process environment is not
  mounted into either container.

## Physical H0/H1 Evidence

- A bounded live Hermes interaction used Project-Evidence MCP, reported exact
  repo SHA `8b582225cc831a3d595fe5476154af89504b36d8`, separated FACT from
  INFERENCE and OPEN QUESTION, and marked unsupported artifact hashes UNKNOWN.
- A real model-backed `daily-research-brief` run cited exact resource/query
  references, repo paths, repo SHA, and available artifact SHA-256 values. It
  separated FACT, INFERENCE, BLOCKER/FAILURE, and OPEN QUESTION and marked
  unresolved evidence UNKNOWN.
- Before and after both model runs, the repository remained clean and the two
  pre-existing proposal-outbox files retained their exact SHA-256 values. No
  unexpected project write or proposal occurred.
- PostgreSQL connected as `hermes_research_memory_reader` with
  `default_transaction_read_only=on`, zero mutation privileges, and live counts
  of 12 hypothesis items, 12 memory records, 24 aliases, and 78 evidence
  references. INSERT, UPDATE, DELETE, and DDL probes each failed with SQLSTATE
  `25006`.
- Hermes runs as `10000:10000`; Project-Evidence runs as `65532:65532`. Both
  use read-only root filesystems, drop all capabilities, have no host-published
  ports, and share only the private evidence network. The external proposal
  outbox is the sole project-facing read/write mount.
- Daily research brief, weekly science review, and dependency/security watch
  schedules remain enabled with the repo-defined skills.

## Authority Boundary

Hermes has no arbitrary shell, filesystem, SQL, browser, provider-rotation,
exchange, order, credential, capital, OMS, risk, reconciliation, safe-mode,
dispatch, or KDAUTH capability. It cannot mutate canonical evidence, Result
Populations, Strategy Specs, promotion/GO state, runtime, paper/live state, or
Search Governor scientific semantics. Research Memory remains an index, not
truth. Proposal files are non-authoritative and require a separately approved
human/repo workflow before any use.

H2/H3/H4 are not started or authorized by this package.

## Validation

- Fresh final-lock installation and `pip check`: PASS at the physical-
  acceptance implementation head; dependency files did not change during the
  account switch or status-only tail.
- `python -m pytest tests/test_hermes_deployment_contract.py
  tests/test_project_evidence_mcp.py -q`: PASS, 39 passed and 2 skipped.
- `tools/dev/diff_scope_summary.py --check-forbidden` with the two final status
  files allowlisted: PASS, no forbidden-path match.
- `git diff --check`: PASS.
