# WP-INBOX-DRAFT-HISTORY-02B — UI Contract

Read-only draft history over the 02A history endpoints. UI/presentation only.

## Same-origin passthroughs (Next route handlers)

The isolated intake service ships no CORS, so the browser reads it through
same-origin passthroughs. Each forwards one method to one hardcoded upstream.

| Browser path | Method | Upstream (hardcoded) | Notes |
| --- | --- | --- | --- |
| `/agent-inbox/drafts` | `GET` only | `GET /api/agent/drafts` | list envelope, verbatim |
| `/agent-inbox/drafts/[draft_id]` | `GET` only | `GET /api/agent/drafts/{draft_id}` | `draft_id` validated `AIDRAFT-<16 hex>` before any fetch |

- No POST/PUT/PATCH/DELETE handler is defined on either route. `POST
  /agent-inbox/drafts` → `405`.
- Passthrough failures: unset origin → `503 {agent_inbox_unconfigured:true}`;
  unreachable service → `502 {agent_inbox_unreachable:true}`. Otherwise the
  service's status and body are returned unchanged (incl. its own 400/404/503).

## Client (`agentInboxClient.ts`)

- `getIntakeDrafts(): Promise<AgentInboxDraftListEnvelope>` — GET the list.
- `getIntakeDraft(draftId): Promise<AgentInboxDraftPacket>` — GET one packet.
- Unconfigured/unreachable → `AgentInboxUnavailableError`.
- Service rejection (400/404/503) → `AgentInboxRejectedError` (carries status).
- No packet is ever synthesized to stand in for a real response.

### List row fields (from `list_intake_drafts`)

`draft_id`, `created_at`, `schema_version`, `title`, `submitter_label`,
`market_hint`, `timeframe_hint`, `hypothesis_preview`, `blocker_count`,
`warning_count`, `open_question_count`, `fabricated`, `non_authority` (compact
posture), `source_packet_path`.

## Component (`DraftHistory.tsx`)

- Fetches the list on mount when `serviceConfigured` (server-resolved from
  `AGENT_INBOX_SERVICE_ORIGIN`).
- **Refresh history (read-only)** button re-reads the list. GET only.
- Each list row is a button that opens the stored packet via `getIntakeDraft`,
  rendered by the existing `DraftPacketView`. **Close detail** clears in-memory
  UI state only (no network).
- States: loading, loaded (rows), empty (honest), unavailable (unconfigured or
  service-down), error (service rejection). None fabricates drafts.
- No client-side persistence (no localStorage/sessionStorage/cookie).

## Detail view (reuses `DraftPacketView`)

Renders the stored packet honestly: source request, formalizer status, draft
language (research object + proposed bounds), blockers/warnings/open questions,
availability primitive check, provenance, tool-context audit, non-authority
flags, `fabricated`, source hashes. Nothing scored, ranked, or made executable.

## Posture

Scratch-only / noncanonical. The list and detail are review material only — not
evidence, approval, ranking, readiness, recommendation, or execution input.
