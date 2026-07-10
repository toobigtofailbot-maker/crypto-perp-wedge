# WP-INBOX-DRAFT-HISTORY-02B — Agent Inbox Draft History UI

Status: ready for review

## Summary

Adds a read-only draft history view to the `/agent-inbox` page. It lists and
opens previously submitted scratch draft packets from the isolated Agent Inbox
intake service (`tools.agent_inbox_intake`), over the read-only history
endpoints delivered by WP-INBOX-DRAFT-HISTORY-02A. UI/presentation only; no
service or `tools/**` change.

## Scope (frontend only)

- `operator_dashboard_frontend/src/lib/agentInboxClient.ts` — added GET-only
  history client: list/detail path constants, `AgentInboxDraftSummary` +
  `AgentInboxDraftListEnvelope` types, `getIntakeDrafts()`, `getIntakeDraft()`.
  Reuses the existing `AgentInboxUnavailableError` / `AgentInboxRejectedError`.
- `operator_dashboard_frontend/src/app/agent-inbox/drafts/route.ts` — same-origin
  read-only `GET` passthrough to `GET /api/agent/drafts` (hardcoded upstream).
- `operator_dashboard_frontend/src/app/agent-inbox/drafts/[draft_id]/route.ts` —
  same-origin read-only `GET` passthrough to `GET /api/agent/drafts/{draft_id}`
  (hardcoded upstream base; `draft_id` validated against `AIDRAFT-<16 hex>`
  before any request).
- `operator_dashboard_frontend/src/components/agent-inbox/DraftHistory.tsx` — the
  history UI: list + detail, read-only refresh, honest empty / unconfigured /
  service-down states. Detail reuses the existing `DraftPacketView`.
- `operator_dashboard_frontend/src/app/agent-inbox/page.tsx` — renders
  `<DraftHistory>` below the intake form.

## Read-only endpoint usage

- `GET /agent-inbox/drafts` → `GET /api/agent/drafts`
- `GET /agent-inbox/drafts/[draft_id]` → `GET /api/agent/drafts/{draft_id}`

Both passthroughs forward one method to one hardcoded upstream path and return
the service's answer verbatim with its own status code. Neither is a general
forwarder. No POST/PUT/PATCH/DELETE handler is defined on either route; the list
route answers `POST` with `405`.

## Controls

Two network controls exist and both are GET-only reads:
1. **Refresh history (read-only)** — re-reads `GET /agent-inbox/drafts`.
2. **Opening a draft** — reads `GET /agent-inbox/drafts/{id}`.

Plus a local **Close detail** button that only clears in-memory UI state (no
network). No run / approve / promote / execute / candidate / pipeline / paper /
live / scheduler / notification / review-state control exists.

## Configured / unconfigured / service-down handling

- **Configured** (`AGENT_INBOX_SERVICE_ORIGIN` set, service up): the list renders
  from the service; drafts open into the stored packet view.
- **Unconfigured** (`AGENT_INBOX_SERVICE_ORIGIN` unset): the page passes
  `serviceConfigured=false`; history renders "Draft history not configured" and
  never fetches or simulates drafts.
- **Service-down** (origin set, service unreachable): the passthrough returns
  `502 agent_inbox_unreachable`; history renders "Draft history unavailable"
  with the service's own words. No simulated drafts.
- **Empty history**: honest empty state, not simulated drafts.

## Posture

Draft history is scratch-only / noncanonical. The list and detail are review
material only — not evidence, approval, ranking, readiness, recommendation, or
execution input. Nothing is persisted client-side (no localStorage,
sessionStorage, or cookie), so a reload re-reads the service.

## Validation

Frontend (`operator_dashboard_frontend/`):
- `npm run typecheck` — pass
- `npm run lint` — pass (no warnings or errors)
- `npm run build` — pass; `/agent-inbox/drafts` and
  `/agent-inbox/drafts/[draft_id]` registered as dynamic routes.

Backend regression:
- `pytest tests/test_agent_inbox_intake.py tests/test_operator_dashboard_api.py`
  — 28 passed.

Repo:
- `python tools/dev/diff_scope_summary.py` — only the 5 allowed frontend files;
  no forbidden-path matches.
- `git diff --check` / `git diff --cached --check` — clean.

Browser/manual (isolated service on `:8100`, dashboard on `:3210` with
`AGENT_INBOX_SERVICE_ORIGIN`):
- Submitted a bounded idea through the form; the returned packet rendered.
- After reload, the submitted draft appeared at the top of history.
- Opened a draft from history; the full stored packet rendered.
- Reloaded; history remained, read from the service.
- Unconfigured (`:3211`, no env): "Draft history not configured".
- Service-down (service stopped, Refresh): "Draft history unavailable".
- Storage check: `localStorage` / `sessionStorage` / `document.cookie` all empty.
- Network check: history requests were GET only; `POST /agent-inbox/drafts` → 405.

## Next dependent package

WP-INBOX-DRAFT-REVIEW-STATE-03A / 03B.
