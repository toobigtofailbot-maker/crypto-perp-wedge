# Codex Operating Model

This directory defines the repo-side Codex operating layer for `crypto-perp-wedge`.

## Model

- Architecture and workflow docs decide sequencing and allowed scope.
- Codex Ask Mode investigates repo truth before proposing action.
- Codex Code Mode executes one locked work package on one branch.
- Codex Review focuses on changed files, validation evidence, and forbidden-scope drift.

## Source Of Truth

- Git history plus the current repository contents are authoritative.
- `docs/project_status.md` is the current-state anchor.
- Memory, chat summaries, and handoffs are advisory only and must be re-verified.

## Boundaries

- Protected runtime and live-trading-adjacent paths stay protected unless a package explicitly opens them.
- Research, advisory, and shadow artifacts do not grant execution authority.
- Codex should stop instead of improvising around missing decisions or protected boundaries.

## Use

- Start with `AGENTS.md`.
- Use the documents in this folder for setup, memory policy, protected-path handling, validation expectations, report-back format, and review discipline.
- Treat the existing `.claude/` guidance as related repo workflow context, not as permission to broaden Codex scope.
