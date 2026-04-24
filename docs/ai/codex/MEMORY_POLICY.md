# Memory Policy

Codex memory is for stable preferences, not repo state.

Allowed memory content:

- stable communication preferences
- durable workflow preferences
- long-lived repo interaction preferences that do not claim current branch or state

Disallowed memory content:

- current branch, PR, diff, merge, artifact, or test-status claims
- repo state summaries that can go stale after the next merge
- claims about what files currently exist, what package is active, or what validation already passed

Rules:

- Never trust memory for branch, PR, artifact, test, or current-state claims.
- `docs/project_status.md` and current repo contents override memory.
- If memory conflicts with repo truth, report the mismatch and follow repo truth.
- Tool-assisted chats should not generate memories for this repo because they often contain transient repo facts.
