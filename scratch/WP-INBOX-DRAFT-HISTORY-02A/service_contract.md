# WP-INBOX-DRAFT-HISTORY-02A Service Contract

The isolated intake service reads only `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`.

## `GET /api/agent/drafts`

Returns a compact envelope. Drafts are sorted by `created_at` descending, then `draft_id` ascending for deterministic ties.

Example non-empty response:

```json
{
  "status": "available",
  "count": 1,
  "drafts": [
    {
      "draft_id": "AIDRAFT-8DEEE634E62CD560",
      "created_at": "2026-07-09T23:42:19Z",
      "schema_version": "agent_inbox_intake_draft_packet_v1",
      "title": "EMA momentum continuation",
      "submitter_label": "codex-sample",
      "market_hint": "BTCUSDT",
      "timeframe_hint": "15m",
      "hypothesis_preview": "BTCUSDT 15m EMA momentum persists because slow information diffusion keeps pressure moving in the same direction after completed bars.",
      "blocker_count": 1,
      "warning_count": 1,
      "open_question_count": 1,
      "fabricated": false,
      "non_authority": {
        "scratch_only": true,
        "noncanonical": true,
        "draft_only": true,
        "review_only": true,
        "not_approval": true,
        "not_promotion": true,
        "not_execution": true
      },
      "source_packet_path": "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-8DEEE634E62CD560.draft_packet.json"
    }
  ],
  "storage_source": "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts",
  "scratch_only": true
}
```

If the directory is missing or contains no packet files, HTTP 200 returns:

```json
{
  "status": "empty",
  "count": 0,
  "drafts": [],
  "storage_source": "scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts",
  "scratch_only": true
}
```

A matching but malformed packet fails the list closed with HTTP 503 and an honest `detail` message naming the invalid packet property.

## `GET /api/agent/drafts/{draft_id}`

Accepts only `AIDRAFT-<16 uppercase hex characters>`. A valid identifier returns the parsed stored JSON object exactly as persisted; no field is canonicalized, renamed, omitted, or written back.

- malformed or unsafe identifier: HTTP 400;
- well-formed identifier with no packet: HTTP 404;
- stored packet malformed or inconsistent with its filename: HTTP 503.

## Non-authority boundary

Both endpoints are read-only scratch views. They add no edit, delete, approve, review, canonicalize, register, queue, schedule, notify, execute, paper, or live operation.
