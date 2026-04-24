# Codex Desktop Setup

Recommended Desktop posture for this repo:

- Personality: precise, professional, direct.
- Custom instructions: include the repo operating block from `AGENTS.md` and point to `docs/ai/codex/`.
- Memory: allow only stable user preferences and durable workflow preferences.
- Skip tool-assisted chats for memory generation: enabled.
- Network: off by default for implementation work unless the package explicitly needs external lookup.
- Approvals and sandbox: conservative by default; prefer read-only or tightly scoped write access.
- Subagents: off by default; reserve for later large audits or review-only fan-out work.
- MCP/connectors: repo and GitHub only for now.
- Never connect Codex Desktop directly to brokerage, exchange, live-trading, or secrets systems.

Use stronger permissions only when the active package requires them and the boundary is explicitly authorized in repo truth.
