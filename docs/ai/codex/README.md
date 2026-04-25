# Codex Operating Model

This directory defines the repo-side Codex operating layer for `crypto-perp-wedge`.

## Precedence

1. Current merged repo truth, including live merged state and actual changed files.
2. Active work package or task-specific scope and constraints.
3. Root `AGENTS.md`.
4. Supporting Codex workflow docs under `docs/ai/codex/`.
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
- Codex Ask Mode investigates repo truth before proposing action.
- Codex Code Mode executes one locked work package on one branch.
- Codex Review focuses on changed files, validation evidence, and forbidden-scope drift.

## Source Of Truth

- Git history plus the current repository contents are authoritative.
- `docs/project_status.md` is the current-state anchor.
- Memory, chat summaries, handoffs, and generic best practice are advisory only and must be re-verified.

## Boundaries

- Protected runtime and live-trading-adjacent paths stay protected unless a package explicitly opens them.
- Research, advisory, and shadow artifacts do not grant execution authority.
- Codex should stop instead of improvising around missing decisions or protected boundaries.

## Use

- Start with `AGENTS.md`.
- Use the documents in this folder for setup, memory policy, protected-path handling, validation expectations, report-back format, and review discipline.
- Treat the existing `.claude/` guidance as related repo workflow context, not as permission to broaden Codex scope.
