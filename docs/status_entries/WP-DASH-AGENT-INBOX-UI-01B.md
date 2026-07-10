# WP-DASH-AGENT-INBOX-UI-01B Status

Branch: `claude/wp-dash-agent-inbox-ui-01b`

Base: `main` at `071a6afe801ef431ac26e1df0df3867591cb83b8`

Built the `/agent-inbox` route out from a read-only schema placeholder into a
bounded intake UI over the isolated scratch-write service delivered by
`WP-DASH-AGENT-INBOX-WRITE-01A`. An operator can submit a title, hypothesis,
market hint, timeframe hint, constraints, and submitter label, and review the
noncanonical draft packet the service returns: draft id, formalizer status and
draft content, open questions, blockers, warnings, availability primitive check,
provenance, tool-context audit, and all 21 non-authority flags rendered verbatim.

This is the one form and the one submit button in the dashboard.
`src/components/agent-inbox/IntakeForm.tsx` is the only file in
`operator_dashboard_frontend/src/` containing any interactive element. The submit
control reads "Create scratch draft". There is no run, approve, promote, execute,
cross, trade, create-candidate, send-to-pipeline, paper/live, scheduler, or
notification control. Draft output is never presented as executable:
`draft_strategy_spec.produced` is surfaced explicitly (always `false`), and the
formalizer's draft language and parameter bounds are captioned as neither a
Strategy Spec, a Variant Manifest, nor a Sweep Plan.

The write path is kept separate from the read path. `src/lib/agentInboxClient.ts`
is POST-only against one endpoint with no generic `request(method, …)` escape
hatch; `src/lib/apiClient.ts` remains GET-only, unchanged, and imported by no
page. Nothing in this package reads, writes, or mutates the read-only dashboard
API, which still exposes zero write endpoints — the page renders that API's own
`agent_inbox_write: unavailable` projection rather than contradicting it.

One design point worth recording. The isolated service ships no CORS middleware:
a preflight `OPTIONS /api/agent/intake-draft` answers `405` with no
`Access-Control-*` headers, so a direct cross-origin JSON POST from the browser
is blocked. This package may not modify that service, so the browser posts to a
same-origin passthrough at `POST /agent-inbox/intake-draft`
(`src/app/agent-inbox/intake-draft/route.ts`), which forwards one body to one
hardcoded upstream path and returns the service's status and body verbatim. The
handler validates, normalizes, retries, caches, and persists nothing; every
intake rule stays inside 01A. The package sanctions this under its "documented
local path" option. The service origin comes from the server-only
`AGENT_INBOX_SERVICE_ORIGIN` env var, with no default and no fallback to the
dashboard API origin; `/agent-inbox` is rendered per request so an operator can
start the service and reload without rebuilding.

Failure states are honest. Unconfigured returns `503` and the page renders
"Intake service not configured" with the form disabled; an unreachable service
returns `502`; a service rejection surfaces the service's own message verbatim
(for example `market_hint must remain bounded to BTCUSDT`). No draft packet is
ever fabricated to stand in for a real response. No draft data is persisted
client-side: no `localStorage`, `sessionStorage`, cookie, or `indexedDB`.

Validation: `npm run typecheck`, `npm run lint`, and `npm run build` pass with no
dependency change. `tests/test_operator_dashboard_api.py` (11 passed) and
`tests/test_agent_inbox_intake.py` (8 passed) confirm the unmodified backends
still pass. Repo validators and `diff_scope_summary.py` are clean. The full HTTP
exchange was driven end to end against the real `tools.agent_inbox_intake` app,
returning a real packet written to
`scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`; those verification packets were
removed afterwards and 01A's tree is clean. Live in-browser React interaction was
not exercised — the browser extension was unavailable — so the server-rendered
DOM and the real HTTP exchange stand in its place; the untested gap is
client-side React rendering only.

Boundary: `tools/operator_dashboard_api/**` and `tools/agent_inbox_intake/**`
were not modified. No canonical Strategy Spec, Variant Manifest, Sweep Plan,
Result Population, candidate registry/lifecycle record, approval marker, runner
job, pipeline run, scheduler, notification, provider/API contact, runtime,
paper/live, OMS/risk/reconciliation/safe-mode, config, dependency, schema,
validator, query-layer, `src/`, `lib/`, or `data/` path was changed.

The draft packet is review-only and creates no downstream authority.
