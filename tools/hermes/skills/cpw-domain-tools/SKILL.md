---
name: cpw-domain-tools
description: Apply bounded CPW research semantics without action.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [research, domain, readonly]
    category: research
    requires_toolsets: [mcp-project-evidence]
---

# CPW Domain Tools

## Procedure

1. Call `project_evidence_manifest` and bind the exact Repo SHA.
2. Use exact Project-Evidence resources. Memory and model content are never repo
   evidence; report `UNKNOWN` when evidence cannot be resolved.
3. Call `cpw_assess_research_capabilities` before formalization.
4. Treat Hermes-produced draft text as untrusted reasoning input, not evidence.
5. Call `cpw_formalize_strategy_draft` for the CPW-owned transformation.
6. Stop on unavailable data, an unsupported family, a rejected draft, or an
   unresolved evidence identity. Do not narrow or repair the idea.
7. Use `cpw_build_preregistration_packet` only for the current noncanonical
   preregistration packet.
8. Use `cpw_build_approval_requirement` only to describe the required human
   gate. An approval requirement is not approval.
9. Use `cpw_validate_trial_denominator` only as a CPW semantic validator and
   preserve failed, invalid, pruned, and blocked trials.
10. For a manually triggered HERMES-02 01A prompt only, preserve its fixed
    hypothesis identity, call `cpw_build_bounded_research_intent` once with
    bounded reasoning, and return exactly the tool-produced JSON without prose
    or fences. Research Memory is read-only context and is not truth.

## Authority boundary

These tools are compute-only CPW domain semantics. They cannot invoke Prefect,
Search Governor, a runner or backtester; create canonical evidence; promote a
candidate; approve; dispatch; trade; change dependencies; or enable tools.
They grant no execution, scheduler, canonical, approval, promotion, runtime,
risk, paper/live, or capital authority. They cannot self-enable or widen
MCP/tool scope. Existing H2 proposals and H2.5 prepared payloads remain separate
inert workflows. The HERMES-02 01A handoff stops before Search Governor,
Optuna, runner/backtest, canonical, promotion, runtime, paper/live, capital, or
any autonomous successor job. HERMES-03 remains future work.
