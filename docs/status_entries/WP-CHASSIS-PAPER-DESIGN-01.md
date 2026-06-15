# WP-CHASSIS-PAPER-DESIGN-01 - Disconnected paper/shadow chassis design

- Package class: docs/architecture design only.
- Branch: `design/chassis-paper-01`.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-CHASSIS-PAPER-DESIGN-01`.
- Base: `origin/main` at `c3c9e63`.
- Scope summary: Adds a non-authoritative architecture design for a
  disconnected paper/shadow chassis and live-readiness decomposition that can
  be built separately from the research engine.
- Created design file:
  `docs/architecture/paper_shadow_chassis_design.md`.
- Architecture coverage: paper/shadow engine, OMS abstraction, reconciliation,
  risk caps, safe mode, kill switch, operator controls, monitoring, dashboard
  surface, data feed architecture, order model and exchange constraints,
  position/account state model, backtest-to-paper signal equivalence, paper
  fill/simulation model, secrets/key management, release/deployment,
  runbooks/incident response, observability, and live-readiness
  classification.
- Boundary summary: Docs/status only. No paper runtime, shadow runtime, OMS,
  reconciliation, exchange connector, broker connector, live data feed,
  credentials, deployment service, dashboard, alert, schema, validator,
  compiler, runner, query-layer, `lib`, Strategy Spec, Variant Manifest, Sweep
  Plan, result population, candidate lifecycle, runtime, paper/live path,
  broker/exchange, capital, or autonomous behavior is changed or authorized.
- Live-readiness summary: Before paper/shadow, the design requires manual
  candidate/spec selection, signal-equivalence proof, replay path, paper/shadow
  evidence state, explicit fill assumptions, feed freshness gates, operator
  approval, halt control, read-only status surface, and heartbeat/freshness
  observability. Before live, the design requires OMS intent routing, exchange
  constraints, venue reconciliation, hard risk caps, safe-mode/kill-switch
  implementation, secrets, release controls, incident runbooks, alert routing,
  partial fills, quote-aware fill realism, and account/margin/liquidation
  modeling.
- Explicitly blocked: cross-venue support, multi-instrument scaling, capital
  scaling, any autonomy over capital, self-modifying risk parameters, and
  unsupervised live promotion.
- Next authority: This package authorizes no implementation. Future paper,
  shadow, OMS, reconciliation, risk, feed, dashboard, deployment, secrets, or
  live-readiness work requires separately scoped authorization.

## Validation

- `git status --short`: PASS; only the two expected docs/status files were
  untracked before staging.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no forbidden-path matches.

## PR status

- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/479
- Draft state: ready for review.
