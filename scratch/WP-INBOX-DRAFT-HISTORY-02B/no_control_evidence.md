# WP-INBOX-DRAFT-HISTORY-02B — No-Control / No-Mutation Evidence

Goal: show the history view reads only, mutates nothing, and adds no lifecycle
control. Verified by source scan and by live browser/network checks.

## HTTP verbs

The two new route handlers export **only** `GET`. There is no POST/PUT/PATCH/
DELETE handler in either file, so neither can submit or mutate.

- `app/agent-inbox/drafts/route.ts` → `export async function GET()`
- `app/agent-inbox/drafts/[draft_id]/route.ts` → `export async function GET(...)`

Live check (dashboard on `:3210`, service on `:8100`):

```
GET  /agent-inbox/drafts                          -> 200
GET  /agent-inbox/drafts/AIDRAFT-B681B1CA1D84647D -> 200
GET  /agent-inbox/drafts/bogus                    -> 400 (rejected at proxy, no upstream call)
POST /agent-inbox/drafts                          -> 405 (no POST handler)
```

Recorded browser network requests for the history feature were GET-only:

```
GET /agent-inbox/drafts                          -> 200 OK   (list, on mount / refresh)
GET /agent-inbox/drafts/AIDRAFT-B681B1CA1D84647D -> 200 OK   (open detail)
```

No POST to `/agent-inbox/drafts*` was ever issued by the history UI. The only
POST surface on the page remains the pre-existing intake submit
(`POST /agent-inbox/intake-draft`), unchanged by this package.

## Controls present (and what they do)

1. **Refresh history (read-only)** — re-reads `GET /agent-inbox/drafts`.
2. **Draft row** (per draft) — reads `GET /agent-inbox/drafts/{id}` and shows it.
3. **Close detail** — clears in-memory UI state only; no network.

No run / approve / promote / execute / crossing / candidate / registry /
runner / pipeline / bridge / gate / scheduler / notification / paper / live /
review-state control exists in the added code.

## No general forwarder

- List upstream is the constant `AGENT_INBOX_DRAFTS_UPSTREAM_PATH`
  (`/api/agent/drafts`).
- Detail upstream is that constant plus a `draft_id` first validated against
  `^AIDRAFT-[A-F0-9]{16}$`. An invalid id is rejected before any fetch, so no
  arbitrary path segment can be smuggled through.
- Neither route contacts the read-only dashboard API.

## No client-side persistence

Browser check after loading and opening a draft:

```
localStorage   = {}
sessionStorage = {}
document.cookie = ""
```

A page reload re-reads the service; the browser holds no draft state.

## Honest absence states

- Unconfigured (`AGENT_INBOX_SERVICE_ORIGIN` unset): "Draft history not
  configured … none is simulated." No fetch.
- Service-down: "Draft history unavailable … No draft history was read." No
  simulated drafts.
- Empty history: honest empty state.

## Posture

Draft history is scratch-only / noncanonical and is review material only — not
evidence, approval, ranking, readiness, recommendation, or execution input.
