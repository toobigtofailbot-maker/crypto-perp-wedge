# WP-INBOX-DRAFT-REVIEW-STATE-03B UI contract

## Surface

The review-state UI mounts inside the opened scratch-draft detail on `/agent-inbox`,
beneath the read-only `DraftPacketView`. It is the `ReviewTrail` component
(`src/components/agent-inbox/ReviewTrail.tsx`), given the opened draft's
`draft_id`.

## Read: review trail

On mount (and on the "Refresh (read-only)" control) the component GETs the
append-only trail via the same-origin passthrough and renders, per event:

- append index (`#N`) and `review_state` badge;
- a non-authoritative plain-language gloss of the state;
- `reviewer_label`, `timestamp_utc` (UTC);
- `rationale`;
- optional `clarification_request`;
- the event's `non_authority_flags` (collapsible);
- for `flagged_for_canonicalization` events, the annotation-only notice.

States rendered honestly:

- loading — "Reading the review trail from the isolated service…";
- empty — "No review events yet…" (an honest empty trail, not a simulated one);
- loaded — the events in `append_index` order plus a footer with `storage_source`
  and `canonical_authority = false`;
- unavailable — service unconfigured (503 `agent_inbox_unconfigured`) or unreachable
  (502 `agent_inbox_unreachable`), shown as "Review trail unavailable";
- error — the service's own 400/404/503 words (e.g. malformed trail).

## Write: append one review event

A single bounded form appends exactly one event:

- `review_state` — select limited to the four allowed states;
- `reviewer_label` — text, ≤ 80 chars;
- `rationale` — textarea, ≤ 1200 chars;
- `clarification_request` — optional textarea, ≤ 1200 chars (omitted, not sent
  empty, when blank).

Submit button copy: **"Append scratch review event"**. Beneath it: "Appends one
annotation. Approves, promotes, canonicalizes, queues, and runs nothing." The
button is disabled until `reviewer_label` and `rationale` are non-empty and while a
submit is in flight.

On success the component replaces its trail state with the `review_trail` the
service returns (append order preserved) and clears the text inputs, keeping the
selected state for a quick follow-up. On failure it shows the service's rejection
or an unavailable message inline and preserves the typed input.

## Same-origin route contract

`src/app/agent-inbox/drafts/[draft_id]/review-events/route.ts` exposes exactly two
verbs:

- `GET`  → upstream `GET /api/agent/drafts/{draft_id}/review-events`
- `POST` → upstream `POST /api/agent/drafts/{draft_id}/review-events`

No PUT/PATCH/DELETE (they resolve to 405). Behavior:

- `draft_id` is validated against `AIDRAFT-<16 uppercase hex>` before any upstream
  request; a malformed id returns 400 and makes no upstream call;
- the upstream host is `AGENT_INBOX_SERVICE_ORIGIN`; unset returns 503
  `agent_inbox_unconfigured` with no upstream call;
- the upstream path is a constant with a constant `/review-events` suffix — not a
  general forwarder;
- it never contacts `tools.operator_dashboard_api`;
- the isolated service's response and status are returned verbatim; a fetch failure
  returns 502 `agent_inbox_unreachable`.

## flagged_for_canonicalization copy (verbatim in UI)

> Flagged for canonicalization is only a review annotation. It does not create or
> approve a Strategy Spec, does not queue research, and does not authorize
> execution. Canonicalization remains Karl-gated and separate.

Shown both in the append form (when that state is selected) and on each stored
`flagged_for_canonicalization` event row.
