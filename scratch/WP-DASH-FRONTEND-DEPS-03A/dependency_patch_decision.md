# WP-DASH-FRONTEND-DEPS-03A — Dependency patch decision

## Decision
Apply the narrowest safe update within the `14.2.x` line:

- `next`: `14.2.5` → `14.2.35`
- `eslint-config-next`: `14.2.5` → `14.2.35` (kept in lockstep with `next`; toolchain alignment)
- `react` / `react-dom`: **unchanged** (`18.3.1`) — npm resolution did not require a change.

`14.2.35` is the latest available release on the `14.2.x` line (the line is maxed), and it is npm's own recommended remediation target for the surfaced advisories.

## Patch Selection Rules applied
1. **Rule 1 (narrowest safe update first):** Tried the latest patched `14.2.x` = `14.2.35`. It resolves the **critical**-severity advisory set (authorization-bypass class GHSA-7gfc-8cq8-jh5f / GHSA-f82v-jwr5-mffw and the bundled-postcss moderate). Applied.
2. **Rule 2 / Rule 3 (no unjustified major jump):** After patching to `14.2.35`, `npm audit --omit=dev` still reports a **high**-severity residual set whose only remediation is `next@16.2.10` — a **breaking major jump**. Per Rule 3 and the stop condition "npm audit requires a major/minor jump that is not clearly safe", the Next 16 upgrade is **NOT applied** here. It is reported for a separate, explicitly-justified follow-up package.
4. **Rule 4:** React/React-DOM unchanged.

## Residual after `14.2.35` (reported, not fixed)
- `npm audit --omit=dev` → **2 vulnerabilities (1 moderate, 1 high)**.
- Advisory range now `9.3.4-canary.0 - 16.3.0-canary.5`; severity dropped **critical → high**; aggregated advisory count dropped **26 → 14**.
- Remaining items are predominantly DoS / SSRF / cache-poisoning / image-optimizer classes that require `next@16.2.10` (breaking).
- Real-world exposure for this shell is low: it is a **local-first, read-only, non-hosted** dev shell with no image-optimizer usage in production, no hosted deployment, and no untrusted internet ingress. This does not lower the audit number but bounds the operational risk while the Next 16 evaluation is scheduled separately.

## Net posture change
- **Before:** critical (26 advisories), including auth-bypass.
- **After:** high (14 advisories), auth-bypass class resolved, bundled-postcss moderate resolved.
- Direction: strict improvement via a within-line, non-breaking patch.

## Follow-up recommended (out of scope here)
- Separate package to evaluate `next@15`/`next@16` migration (App Router compatibility, breaking changes, React version implications) to fully clear the audit.
