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

## Authority boundary

These tools are compute-only CPW domain semantics. They cannot invoke Prefect,
Search Governor, a runner or backtester; create canonical evidence; promote a
candidate; approve; dispatch; trade; change dependencies; or enable tools.
They grant no execution, scheduler, canonical, approval, promotion, runtime,
risk, paper/live, or capital authority. They cannot self-enable or widen
MCP/tool scope. Existing H2 proposals and H2.5 prepared payloads remain separate
inert workflows. HERMES-02 and HERMES-03 are future work.
