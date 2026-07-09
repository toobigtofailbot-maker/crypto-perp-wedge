# WP-DASH-FRONTEND-SHELL-03 — No-Control Evidence

Static verification that the frontend shell contains no write/control surface.
Commands run from `operator_dashboard_frontend/`.

## Mutation methods (POST/PUT/PATCH/DELETE)

```
grep -rniE "method:\s*['\"](POST|PUT|PATCH|DELETE)" src
=> NONE
```

No mutation HTTP method is issued anywhere in the shell.

## Network `fetch`

```
grep -rnE "fetch\(" src
=> src/lib/apiClient.ts:23:  const res = await fetch(`${baseUrl}${path}`, {
```

The single `fetch` is in `src/lib/apiClient.ts`, hard-coded to `method: "GET"`
with no generic method escape hatch. It is **not imported by any page** — the
shell renders committed fixtures by default, so the default runtime makes no
network contact at all.

## Forms / submit / inputs

```
grep -rniE "<form" src                 => NONE
grep -rniE "onSubmit|onClick" src      => NONE
grep -rniE "<button" src               => NONE
grep -rniE "<input|<textarea|<select" src => NONE
```

There are no forms, no submit handlers, no click handlers, no buttons, and no
input controls anywhere in the shell. The Agent Inbox page deliberately renders
the intake schema as a static preview list with **no form and no submit target**.

## Control verbs

```
grep -rniE "\b(run|approve|execute|promote|cross|trade|notify|schedule)\b" src/app src/components
```

All matches are descriptive text or data-field names, not control actions:

- `research/jobs`: "run status", `run.pipeline_run_id`, `run.status` — these read
  committed queue data; "Notification fields are dry-run preview metadata only".
- `research/families`: "cross-family comparison panels are built by a later …"
  — descriptive copy.
- `research` / `research/result-populations`: route notes / descriptions.

No match is a button, handler, or endpoint call.

## Interactivity inventory

- **Navigation only:** Next.js `<Link>` elements in the sidebar, section index
  cards, strategy list rows, and strategy detail back-link. These change the
  route and nothing else.
- **Client component:** `Sidebar.tsx` (`"use client"`) uses `usePathname()` to
  highlight the active route — read-only, no side effects.
- All other components and pages are server components rendering fixtures.

## Conclusion

The shell contains **no** run, approve, execute, promote, cross, trade,
paper/live start, notification-send, scheduler, mutation-fetch, POST, or
form-submit-that-writes surface. Buttons/links present are navigation-only.
