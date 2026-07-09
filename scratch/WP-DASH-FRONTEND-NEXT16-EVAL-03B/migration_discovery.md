# WP-DASH-FRONTEND-NEXT16-EVAL-03B Migration Discovery

## Preflight

- Base branch: `main`
- Base SHA: `d276d90e885ccdfdf1249d2bee45c47d6c187dec`
- Package branch: `claude/wp-dash-frontend-next16-eval-03b`
- PR #632 / `WP-DASH-FRONTEND-DEPS-03A`: merged at `2026-07-09T22:17:29Z`, merge commit `d276d90e885ccdfdf1249d2bee45c47d6c187dec`
- Open competing PR search for Next 16 / this package: none found
- Frontend package files present: `operator_dashboard_frontend/package.json`, `operator_dashboard_frontend/package-lock.json`
- Node/npm used: Node `v24.18.0`, npm `11.16.0` from `C:\Program Files\nodejs`

## Current Versions

From `operator_dashboard_frontend/package.json` on refreshed `main`:

- `next`: `14.2.35`
- `eslint-config-next`: `14.2.35`
- `react`: `18.3.1`
- `react-dom`: `18.3.1`
- `typescript`: `5.5.3`
- `eslint`: `8.57.0`

## Baseline Audit

Command:

```powershell
npm audit --omit=dev
```

Result:

- Exit code: `1`
- Findings: `2 vulnerabilities (1 moderate, 1 high)`
- Affected production packages: `next`, nested `next/node_modules/postcss`
- npm remediation text: `npm audit fix --force` would install `next@16.2.10`, a breaking change

## Baseline Build Behavior

Commands after `npm ci`:

```powershell
npm run typecheck
npm run lint
npm run build
```

Results:

- `npm run typecheck`: pass
- `npm run lint`: pass, no ESLint warnings or errors
- `npm run build`: pass under Next `14.2.35`
- Route behavior: 25 app routes generated; all static except dynamic `/strategies/[strategy_id]`

## Target Metadata

Command:

```powershell
npm view next@16.2.10 version peerDependencies engines
```

Result:

- Version exists: `16.2.10`
- Node engine: `>=20.9.0`
- React peer range: `^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0`
- React DOM peer range: `^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0`

Inference:

- Current `react@18.3.1` and `react-dom@18.3.1` satisfy the target peer range.
- No React major migration is required by target metadata.
- Current Node `v24.18.0` satisfies the target engine.

Command:

```powershell
npm view eslint-config-next@16.2.10 version peerDependencies
```

Result:

- Version exists: `16.2.10`
- Peer dependency: `eslint >=9.0.0`
- Current frontend uses `eslint@8.57.0`

Inference:

- Updating `eslint-config-next` to `16.2.10` requires an ESLint 9 migration.

## Config / Router Discovery

Relevant files:

- `operator_dashboard_frontend/next.config.mjs`
- `operator_dashboard_frontend/.eslintrc.json`
- `operator_dashboard_frontend/tsconfig.json`
- `operator_dashboard_frontend/tailwind.config.ts`
- `operator_dashboard_frontend/postcss.config.mjs`

Observed:

- `next.config.mjs` is minimal and local-first: `reactStrictMode: true`; no rewrites, proxies, image domains, auth, telemetry, or deployment target.
- App Router is already used under `src/app`.
- `.eslintrc.json` extends `next/core-web-vitals`.
- No broad route/layout rewrite was discovered before the trial.

## Trial Install Results

Direct target install:

```powershell
npm install next@16.2.10 eslint-config-next@16.2.10
```

Result:

- Exit code: `1`
- Failure: `ERESOLVE unable to resolve dependency tree`
- Cause: `eslint-config-next@16.2.10` requires `eslint >=9.0.0`; installed `eslint@8.57.0`

Minimal peer-satisfying trial:

```powershell
npm install next@16.2.10 eslint-config-next@16.2.10 eslint@9.39.4
```

Result:

- Exit code: `0`
- Dependency changes were trial-only and reverted before final evidence.

Trial validation:

- `npm run typecheck`: pass
- `npm run build`: pass under Next `16.2.10`
- `npm run lint`: fail; existing `next lint` script is interpreted as an invalid project directory by Next `16.2.10`
- `npm audit --omit=dev`: fail; still reports `2 moderate severity vulnerabilities`

Post-trial audit details:

- `postcss <8.5.10` remains reported under `node_modules/next/node_modules/postcss`
- `next 9.3.4-canary.0 - 16.3.0-canary.5` remains reported by npm audit
- `npm view next version` returned `16.2.10`, so no newer stable Next release was available through npm at evaluation time

Inference:

- The npm-recommended/latest stable target `next@16.2.10` does not currently clear `npm audit --omit=dev`.
- Making lint pass would require replacing `next lint` with an ESLint 9-compatible lint path and likely migrating from `.eslintrc.json` to current ESLint flat-config conventions.
- Because audit still fails at the target version, applying the migration now would not satisfy this package objective.
