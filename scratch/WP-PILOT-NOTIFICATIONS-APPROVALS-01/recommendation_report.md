# WP-PILOT-NOTIFICATIONS-APPROVALS-01 Recommendation Report

## Decision

- Recommendation: `ADOPT_CANDIDATE_CONDITIONAL` for notification transport and IssueOps-shaped approval queues.
- Scope: scratch-only, advisory, dry-run.

## Required Questions

- Can Apprise be adopted as notification transport? Conditional yes, subject to a later dependency decision. Apprise is not importable here, so behavior was not exercised.
- Can GitHub IssueOps serve as approval queue? Conditional yes for human-readable queue shape, audit labels, comments, and manual status transitions; no GitHub write was performed here.
- What exact repo-owned adapter would be needed? A repo-owned dry-run-first notification adapter, an allowlisted Apprise URL loader, a local audit log writer, and a GitHub IssueOps payload builder with write calls disabled by default and separately authorized.
- What remains mocked? Apprise delivery, GitHub issue creation, label/comment ingestion, human identity verification, and any transition from pending to approved/rejected.
- What future agent-phase pieces would consume this? Bounded research agents, lab monitors, blocked-action reporters, manual gate queues, and future research-to-shadow handoff packets.
- What are the stop conditions? Real credentials, non-local URLs, GitHub write APIs, automatic approval, execution hooks, canonical writes, candidate promotion, paper/live activation, runtime/OMS/risk/reconciliation contact, or dependency-file mutation.

## Boundary

- One-way notification only.
- Human approval remains pending.
- This pilot grants no approval, execution, promotion, paper/live, runtime, or canonical-write authority.
