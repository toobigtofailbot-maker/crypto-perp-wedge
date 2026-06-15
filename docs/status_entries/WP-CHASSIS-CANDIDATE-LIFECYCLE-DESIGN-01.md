# WP-CHASSIS-CANDIDATE-LIFECYCLE-DESIGN-01 - Candidate lifecycle design

- Package class: T1 docs/schema-design only.
- Branch: `design/chassis-candidate-lifecycle-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-CHASSIS-CANDIDATE-LIFECYCLE-DESIGN-01`.
- Base: `origin/main` at `c3c9e63`.
- Scope summary: Adds a docs-only architecture design for a future candidate lifecycle chassis before any strategy can become a candidate.
- Changed files:
  - `docs/architecture/candidate_lifecycle_design.md`
  - `docs/status_entries/WP-CHASSIS-CANDIDATE-LIFECYCLE-DESIGN-01.md`
- Repo-truth inputs inspected: startup anchors, candidate registry design, Strategy DSL locking decision, Strategy Research Lab target operating model, lab consolidation roadmap, walk-forward/OOS windowing design, and recent docs-only status-entry conventions.
- Design summary: Defines a future candidate record concept with identity, source lineage, evidence refs, validation refs, paper/shadow refs, status, review metadata, and append-only event history. Defines conceptual states `proposed`, `validated_research`, `paper_candidate`, `paper_running`, `promoted_live`, `rejected`, `demoted`, and `retired`; transition rules; canonical trial, walk-forward/OOS, robustness, Monte Carlo/bootstrap, paper/shadow, and live gates; evidence-link requirements; demotion/rejection/halt/retirement logic; and append-only lifecycle audit events.
- Monte Carlo/bootstrap placement: Not required before candidate registration unless Main/Karl later decide otherwise; recommended after initial GO plus walk-forward/OOS plus DSR/PSR/MinTRL posture and before paper promotion or before live promotion, depending on future gate lock.
- Boundary summary: No candidate registry artifact is created or changed; no candidate IDs are created; no candidate is registered, approved, promoted, demoted, rejected, or retired; no Strategy Spec, Variant Manifest, Sweep Plan, result population, schema, validator, compiler, catalog, query, runner, `lib/`, data, dashboard, runtime, paper/live, OMS/risk/reconciliation, broker/exchange, capital, collateral, or protected path is changed or authorized.
- Authority summary: The design is non-authoritative architecture text only. Evidence links are review pointers, not execution authority. All lifecycle transitions are stop-and-report by default, and the live gate can never auto-progress.
- Next authority: Future implementation would require separately scoped Main/Karl authorization, exact artifact/schema decisions, validation design, and protected-boundary review where applicable.
