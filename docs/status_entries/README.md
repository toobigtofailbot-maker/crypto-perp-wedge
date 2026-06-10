# Status Entries

## Purpose

`docs/status_entries/` stores per-WP status fragments so parallel work packages do not all need to edit `docs/project_status.md` for high-churn branch-state detail.

The fragments are process records. They do not create execution authority, research authority, promotion authority, policy authority, or runtime authority.

## File Naming

Use one Markdown file per work package:

```text
docs/status_entries/<WP_ID>.md
```

Examples:

```text
docs/status_entries/WP-D3.md
docs/status_entries/WP-R3.md
docs/status_entries/WP-E4.md
```

Use the package id as written in the active WP. If the package has both a local id and a roadmap id, put the local id first in the filename and include both in the fragment title.

## Required Fields

Each fragment must include:

- WP id / title
- branch / PR
- package class
- scope summary
- changed files
- validation summary
- boundary summary
- merge status
- next dependency / runway note

Keep entries factual. Separate current facts from future options when both are present.

## Future WP Updates

For future parallel WPs, prefer creating or updating the WP-specific fragment instead of adding full branch-state detail to `docs/project_status.md`.

Fragments may be drafted while a PR is open. After merge, update the fragment's merge status if the package owns that update. Do not edit another WP's fragment unless the active package explicitly scopes that maintenance.

## Status Fragments Are Preferred for Per-WP Detail

Status fragments under `docs/status_entries/<WP_ID>.md` are the preferred surface for per-WP branch-state detail. Write or update the WP-specific fragment rather than adding full branch-state detail to `docs/project_status.md`.

## Project Status Posture

`docs/project_status.md` remains the current-state anchor, milestone summary, major accepted-decision ledger, current runway pointer, and startup entrypoint. It is read at the start of every session and must not be demoted or bypassed.

`docs/project_status.md` should receive compact updates only when a package:

- creates a milestone;
- changes the runway or current runway pointer;
- records a major accepted decision; or
- is explicitly scoped to update it.

If a WP modifies `docs/project_status.md`, it must complete the final rebase and GitHub mergeability checks before the PR is called merge-ready.

For per-WP branch-state detail, link or summarize the relevant status fragment rather than expanding `docs/project_status.md`.

## Parallel-PR Collision Safeguard

Parallel open PRs should avoid overlapping `docs/project_status.md` edits when possible. If two PRs both need `docs/project_status.md`, the later PR must refresh and rebase onto the current `origin/main` after the earlier PR merges before it is called merge-ready. Do not call a PR merge-ready if GitHub reports `docs/project_status.md` conflicts or `mergeable=false`.

## Conflict Reduction

Fragment files reduce merge conflicts because unrelated parallel WPs can write separate status files. If a WP still edits `docs/project_status.md`, the final rebase and GitHub mergeability gate remains mandatory.

## Forbidden Scope

Status fragments must not:

- authorize runtime, paper, live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, or order-path changes;
- promote research, advisory, shadow, or report artifacts into execution authority;
- change schemas, validators, query-layer behavior, tools, tests, data artifacts, dependencies, or CI unless the active WP explicitly authorizes those changes;
- rewrite historical project status entries broadly;
- remove or reinterpret another merged WP's status;
- serve as a replacement for repo truth, `docs/project_status.md`, or the startup read order;
- create execution, research, promotion, policy, runtime, paper/live, or artifact authority.

## Review Checklist

Reviewers should confirm:

- the fragment filename matches the WP id;
- all required fields are present;
- changed-file lists match the actual diff;
- validation evidence matches the package class;
- boundary language does not create authority outside the active package;
- `docs/project_status.md` changes, if any, are compact milestone or runway updates;
- no protected runtime or research-artifact authority is introduced through process text.
