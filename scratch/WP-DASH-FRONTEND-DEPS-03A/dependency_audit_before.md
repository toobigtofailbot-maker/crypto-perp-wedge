# WP-DASH-FRONTEND-DEPS-03A — Dependency audit (BEFORE)

Scope: `operator_dashboard_frontend/` (isolated, local-first, read-only Next.js shell)

## Environment
- node: v24.18.0
- npm: 11.16.0

## Installed versions (before patch)
- next: `14.2.5`
- react: `18.3.1`
- react-dom: `18.3.1`
- eslint-config-next: `14.2.5`

## `npm audit --omit=dev` (before)
- Result: **2 vulnerabilities (1 moderate, 1 critical)**
- `next` `0.9.9 - 16.3.0-canary.5` — Severity: **critical** (26 advisories aggregated), incl.:
  - Next.js authorization bypass vulnerability — GHSA-7gfc-8cq8-jh5f (critical class)
  - Authorization Bypass in Next.js Middleware — GHSA-f82v-jwr5-mffw
  - Next.js Cache Poisoning — GHSA-gp8f-8m3g-qvj9
  - Multiple DoS / SSRF / cache-poisoning / XSS advisories
  - Depends on vulnerable versions of postcss
  - "fix available via `npm audit fix --force` — Will install next@14.2.35, which is outside the stated dependency range"
- `postcss <8.5.10` (bundled under `node_modules/next/node_modules/postcss`) — Severity: moderate — GHSA-qx2v-qp2m-jg93 (resolved by upgrading next)

## `npm outdated next` (before)
- No output row emitted (lockfile-resolved 14.2.5 vs declared range).

## Notes
- npm's own recommended remediation for the critical set is `next@14.2.35` (latest of the `14.2.x` line) — a within-major/minor patch.
