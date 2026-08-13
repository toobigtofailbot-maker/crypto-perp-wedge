# Coding-Agent Operating Model

This directory is the current shared coding-agent guidance path for `crypto-perp-wedge`. The directory name `docs/ai/codex/` is historical; contents apply to Claude Code and Codex by default unless a specific file is explicitly marked as tool-specific. No directory rename is authorized in this note; path migration requires a separate work package.

## Precedence

1. Current merged repo truth, including live merged state and actual changed files.
2. Active work package or task-specific scope and constraints.
3. Root `AGENTS.md`.
4. Supporting coding-agent workflow docs under `docs/ai/codex/`.
5. Chat memory, prior summaries, and generic best practice.

- Anchor on current merged repo truth before applying guidance.
- If repo guidance appears to conflict with active package constraints, the package constraints and repo truth win.
- Package-specific forbidden scope and constraints still win.
- Inspect actual changed files and live merged state rather than relying on summaries.
- Actual changed files and live merged state outrank guidance summaries.
- Repo-side guidance is default operating discipline, not permission to broaden scope.
- Nested `AGENTS.override.md` files constrain local work only; they do not authorize work outside the active package.

## Model

- Architecture and workflow docs decide sequencing and allowed scope.
- A coding agent investigates repo truth before proposing action (Ask / research mode).
- A coding agent executes one locked work package on one branch (Code / execution mode).
- Coding-agent review focuses on changed files, validation evidence, and forbidden-scope drift.

## Source Of Truth

- Git history plus the current repository contents are authoritative.
- `docs/project_status.md` is the current-state anchor.
- Memory, chat summaries, handoffs, and generic best practice are advisory only and must be re-verified.

## Package-Class Read-Path Router

### Shared vs tool-specific startup anchors

Shared startup anchors are defined by `AGENTS.md`: `docs/project_status.md`, `CLAUDE_START_HERE.md`, and `docs/runbook.md`. Despite its historical filename, `CLAUDE_START_HERE.md` is the shared coding-agent startup anchor referenced by `AGENTS.md`.

`.claude/README.md` is a Claude-specific local entrypoint / asset index. It is not a universal Codex startup requirement unless the active WP, a Claude-specific execution brief, or the relevant task scope explicitly requires it.

This clarification does not change startup order, make any startup anchor optional, or rename `CLAUDE_START_HERE.md` or `docs/ai/codex/`.

This router applies **after** required shared startup anchors (`AGENTS.md`, `CLAUDE_START_HERE.md`, `docs/runbook.md`, `docs/project_status.md`) and after the active WP instructions. It does not change those startup anchors, make any of them optional, or reduce repo-truth obligations, validation, changed-file inspection, or stop-condition investigation. It reduces wrong-file reading only.

**T0 docs / status / comments only:**
- Startup anchors.
- Active WP.
- Target docs and status files.
- Relevant shared guidance.
- Avoid code, artifacts, runtime, data, tests unless conflict/stop investigation requires it.

**T1 tests / read-only query additions / exact persistence / non-canonical research automation:**
- Startup anchors.
- Active WP.
- Directly affected tests, read-only query surfaces, exact artifacts, or bounded
  non-canonical automation.
- Relevant adjacent tests, validators, and integrity views required by the
  package.
- For exact persistence, verify bytes, hashes, lineage, and non-authority.

**T2 schema / validator / contract / query-SQL / broadly used production code:**
- Startup anchors.
- Active WP.
- Changed production, contract, schema, validator, and query modules.
- Direct consumers and adjacent subsystem tests.
- Relevant validators and integrity views.
- Focused and adjacent validation before any broad suite required by blast
  radius or an active gate.
- No helper output replaces direct inspection.

**T3 canonical crossing / execution writer / dispatch authorization / protected writers:**
- Startup anchors and active WP.
- Protected canonical, writer, and dispatch surfaces.
- Exact protected identities, contracts, append-only/full-denominator posture,
  and full protected validation evidence.
- Exact-head review and the applicable human gate.

**T4 runtime / paper/live / OMS / reconciliation / risk / capital:**
- Stop unless the active WP explicitly authorizes the boundary.
- Inspect only the explicitly authorized runtime/protected surfaces.
- Follow maximum safety validation and the explicit Karl/protected gate.

**Context Budget field model for future WPs:**

```text
P0 — Read first:
P0 — Read for this package:
P1 — Read only if blocked:
P2 — Do not read / do not touch:
P1 — Search terms if paths changed:
```

See `docs/ai/codex/COMPACT_WP_TEMPLATE.md` for the full Context Budget requirements.

## Boundaries

- Protected runtime and live-trading-adjacent paths stay protected unless a package explicitly opens them.
- Research, advisory, and shadow artifacts do not grant execution authority.
- A coding agent should stop instead of improvising around missing decisions or protected boundaries.

## Use

- Start with `AGENTS.md`.
- Use the documents in this folder for setup, memory policy, protected-path handling, validation expectations, report-back format, and review discipline.
- Treat the existing `.claude/` folder as a thin Claude-specific entrypoint, not as a duplicate workflow standard and not as permission to broaden coding-agent scope.
