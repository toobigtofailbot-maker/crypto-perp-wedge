# WP-INBOX-LOCAL-RUNBOOK-01 Status

Branch: `codex/wp-inbox-local-runbook-01`

PR: [#646](https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/646)

Package class: Tier 1 documentation / local operator runbook.

## Scope summary

Added a runbook-only local startup and verification path for the isolated Agent
Inbox intake service and operator dashboard. The intake service runs on
`127.0.0.1:8765`; the dashboard runs on `127.0.0.1:3000` with
`AGENT_INBOX_SERVICE_ORIGIN=http://127.0.0.1:8765` in its server process.

Repo truth did not show a service-process launcher convention, so this package
keeps process ownership explicit in two operator terminals and adds no launcher
or background supervisor.

## Changed files

- `docs/runbooks/agent_inbox_local_runtime.md`
- `docs/status_entries/WP-INBOX-LOCAL-RUNBOOK-01.md`
- `scratch/WP-INBOX-LOCAL-RUNBOOK-01/runtime_discovery.md`
- `scratch/WP-INBOX-LOCAL-RUNBOOK-01/validation_summary.txt`
- `scratch/WP-INBOX-LOCAL-RUNBOOK-01/operator_sanity_check.md`

## Validation summary

- Intake OpenAPI and docs endpoints returned HTTP 200.
- Unconfigured, configured, and unreachable dashboard states were exercised;
  unreachable submit returned HTTP 502 without creating a packet.
- Browser submission returned `AIDRAFT-7B2F4F814C1401E7`; scratch existence,
  non-authority flags, history list/detail, exact cleanup, and service shutdown
  were verified.
- `tests/test_agent_inbox_intake.py`: 14 passed, 1 dependency deprecation warning.
- `tests/test_operator_dashboard_api.py`: 14 passed, 1 dependency deprecation warning.
- `python tools/dev/diff_scope_summary.py`: clean; no forbidden-path matches.
- `git diff --check` and `git diff --cached --check`: passed.
- Frontend sources/package scripts were not touched, so their conditional
  typecheck/lint/build gate was not required. Live `next dev` and browser
  interaction passed.
- Full repository pytest was not run; the active package does not require it and
  it is not used as merge evidence.

## Boundary summary

Documentation and scratch evidence only. No generated validation packet is
retained. No canonical artifact, candidate, queue, research execution, runner,
bridge, gate, pipeline, scheduler, notification, hosted deployment, auth, CORS,
dashboard API write, frontend UI, intake behavior, dependency, config, provider,
broker, exchange, runtime, paper/live, OMS, risk, reconciliation, or safe-mode
path was added or modified.

## Merge status

Draft PR #646 is open against `main` with the package commits pushed.

## Next dependency / runway note

No downstream authority is created. Starting both services, entering an idea,
reviewing the scratch packet, and deleting any validation packet remain explicit
manual operator actions.
