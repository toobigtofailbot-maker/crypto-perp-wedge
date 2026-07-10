# WP-INBOX-DRAFT-HISTORY-02A Status

Branch: `codex/wp-inbox-draft-history-02a`

Base: refreshed `main` at `1969251e96c5e923d4857a4c36294286b47503c2`

Added read-only scratch draft history to the isolated `tools.agent_inbox_intake` service:

- `GET /api/agent/drafts` returns deterministic newest-first compact metadata.
- `GET /api/agent/drafts/{draft_id}` returns the exact stored JSON packet.
- A missing scratch draft directory returns an empty history response.
- Invalid identifiers, path traversal attempts, malformed filenames, and malformed packets fail closed with honest HTTP responses.

Storage remains `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`. The package adds no UI, review state, canonicalization, candidate lifecycle, research queue, scheduler, notification, runtime, paper/live, OMS, risk, reconciliation, provider, broker, or exchange behavior. `tools/operator_dashboard_api` is unchanged.

The dependent UI package remains `WP-INBOX-DRAFT-HISTORY-02B` and has no implementation authority from this package.
