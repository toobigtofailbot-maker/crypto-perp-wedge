# WP-DASH-FRONTEND-NEXT16-EVAL-03B Migration Decision

## Decision

Deferred.

## Reason

The target migration was not applied because the current npm advisory database still reports production audit findings against `next@16.2.10`, which is both the npm-remediation target from the baseline audit and the latest stable `next` version visible through `npm view next version` during evaluation.

## Facts

- Baseline `npm audit --omit=dev` on `next@14.2.35` reports `2 vulnerabilities (1 moderate, 1 high)`.
- Baseline npm remediation says `npm audit fix --force` will install `next@16.2.10`.
- `next@16.2.10` exists.
- `next@16.2.10` supports current `react@18.3.1` and `react-dom@18.3.1`; no React major migration is required.
- `eslint-config-next@16.2.10` requires `eslint >=9.0.0`.
- Direct install of `next@16.2.10 eslint-config-next@16.2.10` fails with an ESLint 8 versus ESLint 9 peer conflict.
- Trial install with `eslint@9.39.4` succeeds.
- Trial `npm run typecheck` and `npm run build` pass.
- Trial `npm run lint` fails because the existing `next lint` script is no longer compatible as written under Next `16.2.10`.
- Trial `npm audit --omit=dev` still fails with `2 moderate severity vulnerabilities` against `next` and nested `postcss`.
- Trial dependency/config edits were reverted; no frontend migration is retained in this branch.

## Inference

Next 16 migration is technically close for this isolated shell, but it is not sufficient to clear the production audit at the currently available target. The remaining lint work is also a toolchain migration, not a feature change, but doing it now would still leave audit failing.

## Decision

Do not apply the Next 16 migration in this package.

## Future Option

Re-evaluate when npm publishes a stable Next version outside the currently reported vulnerable range, or when the advisory/remediation metadata changes. A future package can combine:

- Next stable version that clears `npm audit --omit=dev`;
- matching `eslint-config-next`;
- ESLint 9-compatible lint command/config migration;
- no React major change unless separately authorized.
