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

## Project Status Posture

`docs/project_status.md` remains the current-state anchor, milestone summary, major accepted-decision ledger, current runway pointer, and startup entrypoint.

After WP-G2, `docs/project_status.md` should not be the default place for every branch-state detail from parallel WPs. Update it when a package creates a milestone, changes the runway, changes major accepted decisions, or is explicitly scoped to update it. Otherwise, link or summarize the relevant status fragment.

## Conflict Reduction

Fragment files reduce merge conflicts because unrelated parallel WPs can write separate status files. If a WP still edits `docs/project_status.md`, the final rebase and GitHub mergeability gate remains mandatory.

## Forbidden Scope

Status fragments must not:

- authorize runtime, paper, live, OMS, reconciliation, risk, safe-mode, kill-switch, broker, exchange, or order-path changes;
- promote research, advisory, shadow, or report artifacts into execution authority;
- change schemas, validators, query-layer behavior, tools, tests, data artifacts, dependencies, or CI unless the active WP explicitly authorizes those changes;
- rewrite historical project status entries broadly;
- remove or reinterpret another merged WP's status.

## Review Checklist

Reviewers should confirm:

- the fragment filename matches the WP id;
- all required fields are present;
- changed-file lists match the actual diff;
- validation evidence matches the package class;
- boundary language does not create authority outside the active package;
- `docs/project_status.md` changes, if any, are compact milestone or runway updates;
- no protected runtime or research-artifact authority is introduced through process text.
