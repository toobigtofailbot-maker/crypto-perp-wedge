# WP-DASH-AGENT-INBOX-UI-01B UI Contract

## Endpoint used

| Hop | Method | Path | Served by |
| --- | --- | --- | --- |
| Browser → dashboard origin | `POST` | `/agent-inbox/intake-draft` | `src/app/agent-inbox/intake-draft/route.ts` (passthrough) |
| Dashboard server → intake service | `POST` | `${AGENT_INBOX_SERVICE_ORIGIN}/api/agent/intake-draft` | `tools.agent_inbox_intake` (01A, isolated) |

No other endpoint is contacted. The upstream path is a module constant, so the
passthrough cannot be steered at a different target by a caller.

### Why a passthrough instead of a direct browser POST

`tools/agent_inbox_intake/app.py` installs no CORS middleware. Measured against
the real service:

- `OPTIONS /api/agent/intake-draft` with `Origin` + `Access-Control-Request-Method: POST` → **HTTP 405**
- `POST` with `Origin` → response carries **no `Access-Control-*` header**

A JSON body sets `Content-Type: application/json`, which forces a CORS
preflight, so a direct cross-origin POST is blocked by every browser. This
package may not modify the 01A service, so the request is made same-origin
instead. §10.2 of the package sanctions exactly this: "explicit endpoint base
variable **or documented local path**".

The passthrough contains no logic: no validation, normalization, enrichment,
retry, caching, persistence, or interpretation. It forwards one body and returns
the service's status and body verbatim. Every intake rule stays inside 01A.

## Client module used

`src/lib/agentInboxClient.ts` — POST-only, one endpoint, no generic
`request(method, …)` escape hatch.

Kept strictly separate from `src/lib/apiClient.ts` (the GET-only read-only
dashboard API client). `apiClient.ts` is unchanged and is still imported by no
page. Nothing in the Agent Inbox path reads, writes, or mutates the dashboard
API.

Configuration: `AGENT_INBOX_SERVICE_ORIGIN` (server-only; deliberately **not**
`NEXT_PUBLIC_*`, so the browser never receives an origin to fetch directly).
There is no default and no fallback to the dashboard API origin. The
`/agent-inbox` page is `dynamic = "force-dynamic"` so the origin is read at
request time, letting an operator start the service and reload without a rebuild.

## Request fields

Mirrors `IntakeDraftRequest` (`extra="forbid"` — unknown keys are rejected 422).

| Form control | Request field | Required | UI bound | Source of bound |
| --- | --- | --- | --- | --- |
| Idea title | `title` | yes | `maxLength=120`, non-empty | pydantic `max_length=120` |
| Hypothesis / idea | `hypothesis_text` | yes | `maxLength=4000`, non-empty | pydantic `max_length=4000` |
| Market / instrument hint | `market_hint` | no | `maxLength=80`, default `BTCUSDT` | pydantic + service BTCUSDT rule |
| Timeframe hint | `timeframe_hint` | no | `<select>` over `{15m,30m,1h,4h,1d}` | `LOCKED_TIMEFRAMES` |
| Constraints / notes | `constraints_notes` | no | `maxLength=1200` | pydantic `max_length=1200` |
| Submitter label | `submitter_label` | no | `maxLength=80` | pydantic `max_length=80` |

`client_draft_id` is intentionally **not** exposed. Omitting it makes `draft_id`
a deterministic hash of the normalised request, which is the desired behavior
for an operator-facing form.

Empty optional fields are omitted from the JSON body rather than sent as `""`.

### Where the UI mirrors vs. defers

- **Mirrors** (enumerated set, safe to constrain): `timeframe_hint` is a
  `<select>` restricted to the locked timeframes.
- **Mirrors** (cheap, prevents a guaranteed 400): the combined
  `title + hypothesis_text + constraints_notes` length is shown against the
  5200-character service cap and blocks submit when exceeded.
- **Defers** (service stays authoritative): the `market_hint` BTCUSDT rule is
  surfaced as an inline warning but does **not** block submit. If the operator
  proceeds, the service's own HTTP 400 text is displayed verbatim. The UI never
  substitutes its own judgement for the service's.

## Response fields displayed

From `agent_inbox_intake_draft_packet_v1`:

- `draft_id`, `created_at`, `schema_version`
- `formalizer_result.status`
- `formalizer_result.draft_strategy_spec.produced` (always `false`)
- `provenance.output_path` (where the packet was written)
- `warnings[]`, `open_questions[]`, `blockers[]`,
  `formalizer_result.rejection_reasons[]`
- `formalizer_result.research_object` — `summary`, `causal_rationale`,
  `falsifiable_prediction`, `entry_concept`, `exit_concept`, `symbols`,
  `timeframe`, `features`, `parameter_bounds[]`, `stop_conditions[]`
- `availability_primitive_check` — `historically_testable_now`,
  `blocking_features`, `distinction`, `feature_assessments[]`
- `non_authority_flags` (all 21 booleans, rendered verbatim via `FlagGrid`)
- `provenance.*`, `formalizer_result.provider_metadata.api_call_made`,
  `fabricated`, `source_hashes.source_request_sha256`
- `tool_context_audit[]` — `action_type`, `decision`, `target_path`

Nothing is scored, ranked, summarized into a verdict, or presented as runnable.
`research_object` is captioned "Proposed draft language, not a Strategy Spec and
not a Variant Manifest"; `parameter_bounds` is captioned "Not a Variant
Manifest, not a Sweep Plan, and not a sweep grid".

## Boundary language

Rendered by `src/components/agent-inbox/IntakeBoundaryPanel.tsx`, above the form:

- Draft only.
- Scratch only.
- Does not create Strategy Spec / Variant Manifest / Sweep Plan.
- Does not run backtests.
- Does not create candidates.
- Does not approve, promote, cross, or trade.
- Does not touch paper/live/runtime.
- Requires human review before any repo action.

Plus 01A's own wording, verbatim: "The draft packet is review material only. It
is not evidence, authority, approval, recommendation, ranking, readiness,
promotion, or execution input."

The page additionally carries a "Two services, one boundary" card explaining
that the read-only dashboard API still exposes zero write endpoints, and renders
that API's own `unavailable.agent_inbox_write` note through `BoundaryNotes`.

## Allowed form behavior

- Collect the six bounded fields above.
- POST once, on explicit operator submit, to the single scratch intake endpoint.
- Render the returned draft packet read-only.
- Show an honest unavailable state when unconfigured or unreachable.
- Show the service's own rejection text when the service says no.
- Reset local form state with "Clear form" (in-memory `useState` only).

## Explicitly forbidden UI controls (none present)

No control labelled or behaving as: Run, Approve, Promote, Execute,
Create Candidate, Send to Pipeline, Cross, Trade, Deploy, Launch, Schedule, or
Notify. No paper/live control. No runner/pipeline/gates trigger. No candidate
registry or lifecycle action. No approval marker. No dashboard API mutation.

The submit button reads **"Create scratch draft"**. The only other control is a
**"Clear form"** button of `type="button"` that resets local state.

## Persistence

None. No `localStorage`, `sessionStorage`, `cookie`, or `indexedDB` anywhere in
`operator_dashboard_frontend/src/`. Form contents and the returned packet live in
React state and are discarded on reload. The service holds the packet on disk;
the browser does not.
