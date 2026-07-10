# Scratch Draft Review State Contract

## Endpoints

- `GET /api/agent/drafts/{draft_id}/review-events` returns an honest empty or populated append-only trail for an existing scratch draft.
- `POST /api/agent/drafts/{draft_id}/review-events` appends exactly one event and returns the event plus current trail metadata.

Both endpoints validate `draft_id` as `AIDRAFT-<16 uppercase hex characters>` before constructing a path. Missing valid drafts return not-found. Malformed requests and state IDs fail closed. Storage read/append failures return service-unavailable.

## Event schema

Each JSONL row contains `schema_version`, `event_id`, `append_index`, `draft_id`, `review_state`, `reviewer_label`, `timestamp_utc`, `rationale`, optional `clarification_request`, and explicit non-authority flags.

Allowed states and semantics:

- `reviewed`: a human reviewed the draft.
- `rejected`: a human rejected it as not worth further intake work.
- `needs_clarification`: a human requests clarification before further consideration.
- `flagged_for_canonicalization`: a human thinks it may merit a later Karl-gated canonicalization review.

The last state is annotation only, not approval or promotion.

## Storage and append-only behavior

The deterministic path is `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews/{draft_id}.review_events.jsonl`. Existing rows are validated and retained byte-for-byte; a POST opens the trail in append mode and adds one canonical JSON line. No edit, update, or delete endpoint exists.
