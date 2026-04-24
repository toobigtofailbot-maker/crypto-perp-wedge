# Protected Paths And Boundaries

Stop and escalate before touching these areas unless the active package explicitly authorizes them:

- Runtime execution paths and execution-connected code.
- OMS truth and reconciliation truth.
- Hard risk caps and related risk enforcement.
- Bounded overlay semantics, including the locked output set and fail-open behavior.
- Safe-mode behavior and other protective runtime controls.
- Live-trading or brokerage-connected paths, credentials, or integrations.
- `lib/` research/runtime-support code.
- `src/` runtime code.
- `configs/` live or testable runtime configuration.

Why these are protected:

- They control determinism, auditability, and safety.
- They can change execution behavior, risk posture, or evidence integrity.
- A docs, artifact, or workflow package must not implicitly modify execution semantics.

Working rule:

- If safe implementation appears to require more than documentation or an `AGENTS.override.md` in a protected area, stop and escalate rather than improvising.
