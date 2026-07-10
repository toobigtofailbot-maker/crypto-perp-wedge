# WP-DASH-AGENT-INBOX-UI-01B No-Control Evidence

This package intentionally introduces **one** form. The evidence below separates
that allowed intake-form behavior from the forbidden control surface.

## 1. Allowed: the intake form

One `<form>` exists in the entire frontend, on `/agent-inbox`.

Rendered DOM of `GET /agent-inbox` (dashboard on `:3100`, service origin set):

```text
<form >
<input    id="intake-title"
<textarea id="intake-hypothesis"
<input    id="intake-market"
<select   id="intake-timeframe"
<option value="15m"  <option value="30m"  <option value="1h"
<option value="4h"   <option value="1d"
<textarea id="intake-constraints"
<input    id="intake-submitter"
<button type="submit" disabled="">Create scratch draft
<button type="button">Clear form
```

The submit button is disabled until `title` and `hypothesis_text` are non-empty.
The only other control is `type="button"` and resets local React state.

## 2. The form submits only to the isolated scratch intake endpoint

Every `fetch` call in `operator_dashboard_frontend/src/`:

```text
src/app/agent-inbox/intake-draft/route.ts:51   fetch(upstream, { method: "POST" })
src/lib/agentInboxClient.ts:228                fetch(AGENT_INBOX_PROXY_PATH, { method: "POST" })
src/lib/apiClient.ts:23                        fetch(`${baseUrl}${path}`, { method: "GET" })
```

- The browser POST goes to the same-origin constant `AGENT_INBOX_PROXY_PATH`.
- The server POST goes to `${origin}${AGENT_INBOX_UPSTREAM_PATH}`, where
  `AGENT_INBOX_UPSTREAM_PATH` is a module constant (`/api/agent/intake-draft`).
  A caller cannot redirect it, so the passthrough is not a general forwarder.
- `apiClient.ts` remains GET-only and unchanged.

The passthrough answers non-POST verbs with 405:

```text
GET    /agent-inbox/intake-draft -> 405
DELETE /agent-inbox/intake-draft -> 405
```

## 3. Interactive elements exist in exactly one file

```text
$ grep -rlE "<form|<button|<input|<textarea|<select|onClick|onSubmit" src/
src/components/agent-inbox/IntakeForm.tsx
```

Every other route in the dashboard remains pure read-only presentation with no
control of any kind.

## 4. No run / approve / execute / promote / cross / trade controls

```text
$ grep -rniE "(Run|Approve|Promote|Execute|Create Candidate|Send to Pipeline|Cross|Trade|Deploy|Launch)" \
    src/ --include=*.tsx --include=*.ts | grep -iE "<button|onClick|type=\"submit\""
NONE: no forbidden verb on any control
```

The submit control reads "Create scratch draft". These verbs appear in the UI
only inside boundary prose that **denies** them ("Does not approve, promote,
cross, or trade").

## 5. No candidate creation controls

No control writes, proposes, or references a candidate registry or candidate
lifecycle record. The returned packet's own `non_authority_flags` are rendered
verbatim, including `not_candidate_registry: true` and
`not_candidate_lifecycle: true`.

## 6. No paper/live controls

No paper or live route, control, or call is added or touched. The `/paper` and
`/live` routes are untouched placeholder pages. The packet declares
`not_paper_live: true`, `not_runtime: true`.

## 7. No scheduler / notification controls

No scheduler, cron, timer, retry loop, polling, or notification call exists. The
single POST fires only on explicit operator submit. Packet flags
`not_scheduler: true`, `not_notification: true` are rendered.

## 8. No dashboard read-only API mutation

- `tools/operator_dashboard_api/**` not modified (see changed-file list).
- `tests/test_operator_dashboard_api.py` → **11 passed**.
- The dashboard API still declares zero write endpoints; the page renders that
  projection (`allowed_methods: GET`, `draft_endpoint_available: false`) rather
  than contradicting it.
- `src/lib/apiClient.ts` unchanged; still imported by no page.

## 9. No backend implementation changes

`tools/agent_inbox_intake/**` is unmodified. `tests/test_agent_inbox_intake.py`
→ **8 passed**. The service contract, request schema, and packet schema are
consumed exactly as 01A shipped them.

The one server-side file this package adds — the Next route handler — is
frontend transport glue, not backend logic. It validates nothing, decides
nothing, and persists nothing. Removing the isolated service makes it useless;
it cannot produce a draft on its own. Its necessity is forced by the service
having no CORS middleware (measured: preflight → 405, no `Access-Control-*`
headers), and by this package being forbidden from adding CORS to that service.

## 10. No local persistence

```text
$ grep -rniE "localStorage|sessionStorage|document\.cookie|indexedDB" src/
(only the IntakeForm doc comment stating that none are used)
```

Form input and the returned packet live in React state and vanish on reload.

## 11. Draft output is never presented as executable

- `draft_strategy_spec.produced` is surfaced explicitly (always `false`).
- `research_object` is captioned "Proposed draft language, not a Strategy Spec
  and not a Variant Manifest. Nothing below is compiled, validated, or runnable."
- `parameter_bounds` is captioned "Not a Variant Manifest, not a Sweep Plan, and
  not a sweep grid."
- The packet header carries `scratch only`, `not executable`, and
  `human review required` badges.
- All 21 `non_authority_flags` are rendered verbatim rather than summarized.

## 12. Failure never fabricates a packet

Measured against the running stack:

| Condition | Result | UI |
| --- | --- | --- |
| `AGENT_INBOX_SERVICE_ORIGIN` unset | `503 {"agent_inbox_unconfigured": true}` | "Intake service not configured", form disabled |
| Service down (dead port) | `502 {"agent_inbox_unreachable": true}` | "Intake service unreachable" |
| Bad timeframe | `400 "timeframe_hint must be one of ['15m','1d','1h','30m','4h']"` | "Draft not created" + service text verbatim |
| `market_hint: ETHUSDT` | `400 "market_hint must remain bounded to BTCUSDT"` | "Draft not created" + service text verbatim |
| Missing `title` | `422` pydantic list detail | "Draft not created" + flattened field errors |
| Extra key `run_backtest` | `422 "Extra inputs are not permitted"` | "Draft not created" |

In every failure path the UI states that no draft packet was created and renders
nothing in its place.

## 13. Protected paths untouched

No change to `src/**`, `lib/**`, `configs/**`, `data/**`, `.claude/**`,
`tools/operator_dashboard_api/**`, `tools/agent_inbox_intake/**`, runtime, OMS,
risk, reconciliation, safe-mode, paper/live, provider/broker/exchange/credential,
scheduler, notification, bridge/runner/gates, canonical evidence artifacts,
candidate registry/lifecycle artifacts, schemas/validators/query-layer, or
deployment/hosting/auth files. No Python or root dependency file changed. No
frontend dependency added (`package.json` and lockfile unchanged).

Three draft packets written into `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`
by the real service during verification were removed with `git clean`; 01A's
committed sample packet is preserved and its tree is clean.
