# WP-INBOX-DRAFT-HISTORY-02A Repo Truth Discovery

## Preflight

- Refreshed `main` at `1969251e96c5e923d4857a4c36294286b47503c2`, the merge commit for PR #639.
- PR #635's isolated write service is present under `tools/agent_inbox_intake`.
- PR #639's Agent Inbox UI is present, but no history API or history UI exists.
- The requested local branch already existed as a clean pointer to current `main`; it contained no commits or diff and was safely reused.

## Stored packet contract

Inspected:

- `tools/agent_inbox_intake/models.py`
- `tools/agent_inbox_intake/service.py`
- `tools/agent_inbox_intake/app.py`
- `tests/test_agent_inbox_intake.py`
- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/AIDRAFT-8DEEE634E62CD560.draft_packet.json`
- `docs/status_entries/WP-DASH-AGENT-INBOX-WRITE-01A.md`
- `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/isolation_contract.md`

Repo truth:

- Scratch packets live only under `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`.
- Filenames use `<draft_id>.draft_packet.json`.
- Service-generated identifiers use `AIDRAFT-` plus 16 uppercase hexadecimal characters.
- The committed packet uses `agent_inbox_intake_draft_packet_v1` and contains stable source request, timestamps, blockers, warnings, open questions, non-authority flags, provenance, hashes, and `fabricated` fields.
- The existing POST path writes exactly one packet and does not write canonical research artifacts.

Decision: the current packet contract is stable enough for a bounded reader without migration or schema changes. The reader validates the existing identity and metadata contract but returns packet detail without normalization or rewriting.

## Boundary discovery

- History can be implemented entirely inside `tools.agent_inbox_intake` and its focused tests.
- No dashboard UI or `tools/operator_dashboard_api` change is required.
- No storage move, review-state decision, approval semantic, canonicalization, or queue path is required.
- A missing storage directory can truthfully be represented as an empty scratch history.
