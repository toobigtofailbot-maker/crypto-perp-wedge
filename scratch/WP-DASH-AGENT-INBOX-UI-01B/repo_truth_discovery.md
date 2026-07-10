# WP-DASH-AGENT-INBOX-UI-01B Repo Truth Discovery

Base: `main` at `071a6afe801ef431ac26e1df0df3867591cb83b8`.

## Hard dependency check

| Requirement | Status | Evidence |
| --- | --- | --- |
| `WP-DASH-AGENT-INBOX-WRITE-01A` merged | PASS | `e1e0618` on `main`, merge `74e6464` (PR #635) |
| Isolated intake service exists | PASS | `tools/agent_inbox_intake/{__init__,app,models,service}.py` |
| Service contract documented | PASS | `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/isolation_contract.md` |
| Read-only dashboard API is GET-only | PASS | no `.post`/`.put`/`.patch`/`.delete` in `tools/operator_dashboard_api/` |
| `operator_dashboard_frontend/` exists and validates | PASS | baseline typecheck + lint + build clean |
| Node/npm available | PASS | `npm ci` clean |
| No open PR implementing Agent Inbox UI | PASS | no remote branch matches `*inbox*`/`*intake*` |

## Current Agent Inbox placeholder route

`operator_dashboard_frontend/src/app/agent-inbox/page.tsx` renders the committed
fixture `src/lib/fixtures/agent_intake_schema.json` (a projection of the
read-only dashboard API `GET /api/agent/intake-schema`). It states there is
intentionally no form and no submit target, and lists
`future_intake_fields_preview` as dashed non-input chips.

That page is the placeholder this package replaces.

## Isolated write service endpoint / contract

The intake service is a **separate FastAPI app**, not a route on the dashboard
API. `tools/agent_inbox_intake/app.py` calls `FastAPI(...)` itself and mounts
exactly one route:

- `POST /api/agent/intake-draft`

It is not mounted into `tools.operator_dashboard_api`, so the two services run
on different origins. `tools/operator_dashboard_api/readers.py:471`
(`read_agent_intake_schema`) still projects
`unavailable.agent_inbox_write = "POST /api/agent/intake-draft is intentionally
not implemented."` — this remains **true of the dashboard API** and is not a
contradiction. The UI must therefore target a separately configured base URL and
must not treat the dashboard API as the write target.

## Request schema

From `tools/agent_inbox_intake/models.py` (`IntakeDraftRequest`,
`model_config = ConfigDict(extra="forbid")` — unknown keys are rejected):

| Field | Required | Type | Bound |
| --- | --- | --- | --- |
| `title` | yes | str | 1–120 chars |
| `hypothesis_text` | yes | str | 1–4000 chars |
| `market_hint` | no | str \| null | ≤80 chars, default `BTCUSDT` |
| `timeframe_hint` | no | str \| null | ≤10 chars, default `15m` |
| `constraints_notes` | no | str \| null | ≤1200 chars |
| `submitter_label` | no | str \| null | ≤80 chars |
| `client_draft_id` | no | str \| null | ≤80 chars, `^[A-Za-z0-9_.:-]{1,80}$` |

Additional **fail-closed** rules enforced in `service.py::_normalise_request`,
which are not visible in the pydantic model and which the UI must respect:

- `market_hint` must contain `BTCUSDT` after upper-casing and stripping `-`/`_`,
  else `IntakeDraftError: market_hint must remain bounded to BTCUSDT`.
- `timeframe_hint` must be in `LOCKED_TIMEFRAMES` =
  `{"15m", "30m", "1h", "4h", "1d"}`
  (`tools/research_agents/idea_formalizer_agent.py:52`).
- `len(title) + len(hypothesis_text) + len(constraints_notes)` must be
  ≤ `MAX_COMBINED_TEXT_LENGTH` (5200).
- Empty-after-strip `title` or `hypothesis_text` is rejected.

`IntakeDraftError` is surfaced by `app.py` as **HTTP 400** with the message in
`detail`. Pydantic validation failures surface as **HTTP 422** with `detail` as
a list of error objects. The UI error state must handle both shapes.

## Response draft packet schema

`service.py::create_intake_draft` returns the persisted packet
(`SCHEMA_VERSION = "agent_inbox_intake_draft_packet_v1"`). Confirmed against the
committed sample `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/sample_draft_packet.json`:

- `schema_version`, `draft_id` (`AIDRAFT-<16 hex upper>`), `created_at` (UTC `Z`)
- `source_request` — the normalised echo of what was submitted
- `formalizer_result` — `status`, `run_id`, `rejection_reasons[]`,
  `research_object{summary, causal_rationale, falsifiable_prediction,
  entry_concept, exit_concept, features[], symbols[], timeframe,
  parameter_bounds[], stop_conditions[]}`,
  `draft_strategy_spec{produced, path, blockers[]}`,
  `capability_assessment`, `provider_metadata`, `non_authority`,
  `adapter_metadata`, `blocked_action`
- `availability_primitive_check` — same object as
  `formalizer_result.capability_assessment`
- `open_questions[]`, `blockers[]`, `warnings[]`
- `non_authority_flags` — 21 booleans (`scratch_only`, `not_strategy_spec`,
  `not_execution`, `not_paper_live`, …; `fabricated` is `false`)
- `provenance` — `service_namespace`, `package_id`, `formalizer_module`,
  `formalizer_mode`, `provider_mode`, `provider_id`, `tool_context_role`,
  `tool_context_wp_id`, `output_path`, `captured_formalizer_write_paths[]`,
  `formalizer_writes_captured_in_memory`
- `source_hashes` — `source_request_sha256`, `formalizer_result_sha256`
- `tool_context_audit[]` — `action_type`, `decision`, `target_path`, `role`,
  `policy_id`, `reason`, `timestamp_utc`, `wp_id`, `non_authority`
- `fabricated: false`

Note: `draft_strategy_spec.produced` is **always `false`** — 01A's
`PacketOnlyIdeaFormalizer._draft_family_supported` returns `False`
unconditionally, so a Strategy Spec is never emitted and
`blockers` reliably carries `"no validated draft adapter exists for this exact
primitive family"`. The UI must not present the packet as a spec.

## Current frontend API/client helpers

`src/lib/apiClient.ts` — `readOnlyApiClient`, GET-only, explicitly documents
that it defines no POST/PUT/PATCH/DELETE helper and no generic
`request(method, …)` escape hatch. It is not imported by any page; pages read
committed fixtures via `src/lib/fixtures.ts`.

## Is a separate client needed?

**Yes.** Reasons:

1. Different origin — the intake service is its own FastAPI app, so it cannot
   share `apiClient`'s `DEFAULT_BASE_URL` (`http://127.0.0.1:8000`).
2. Adding a POST helper to `readOnlyApiClient` would break that module's stated
   GET-only contract, which other packages rely on as a boundary assertion.

The UI therefore adds `src/lib/agentInboxClient.ts`, POST-only, one endpoint,
its own base URL read from `NEXT_PUBLIC_AGENT_INBOX_BASE_URL`. When that
variable is unset the UI renders an unavailable state; it never falls back to
the dashboard API origin.

## Exact no-authority wording from 01A

From `isolation_contract.md`:

> The draft packet is review material only. It is not evidence, authority,
> approval, recommendation, ranking, readiness, promotion, or execution input.

From the packet `warnings[]` emitted by `service.py`:

> Scratch-only Agent Inbox draft packet; no canonical artifact, candidate,
> runner, pipeline, paper/live, scheduler, or notification authority.

From the packet `open_questions[]`:

> Human review must decide whether this scratch draft should be revised,
> discarded, or promoted through a later authorized package.

## No-control constraints

The service exposes exactly one POST and no other verb. The UI adds exactly one
form whose only submit target is that endpoint. No run, approve, execute,
promote, cross, trade, candidate-creation, paper/live, scheduler, or
notification control is introduced. The dashboard API stays untouched and
GET-only. No draft data is persisted client-side.
