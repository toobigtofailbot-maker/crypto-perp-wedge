# WP-LAB-IDEA-INTAKE-FORMALIZATION-01

This directory contains a deterministic, scratch-only idea-formalization
example. Nothing here is canonical preregistration, candidate evidence,
promotion, paper/live authority, or runtime authority.

## Example flow

```powershell
python -m tools.research_workflow.validate_research_idea tests/fixtures/research_ideas/valid_research_idea_current_lab.json
python -m tools.research_workflow.formalize_research_idea `
  --input tests/fixtures/research_ideas/valid_research_idea_current_lab.json `
  --output-dir scratch/WP-LAB-IDEA-INTAKE-FORMALIZATION-01
```

The formalizer writes:

- `example_research_idea.json`: validated structured idea copy;
- `example_formalization_report.json`: classification, capability mapping,
  rejection state, non-authority declarations, and workflow eligibility;
- `draft_workflow_parameter_space.json`: workflow-gen input only when the idea
  exactly matches the merged generator's bounded source family.

Pass `--generate-workflow-drafts` only to materialize the eligible generator
outputs under this scratch directory. The generator remains draft-only and
does not create a canonical Strategy Spec, Variant Manifest, or Sweep Plan.

## Plain-text intake

The local parser accepts plain text only when the text explicitly contains a
bounded instrument, locked timeframe, causal rationale, entry, exit, known
feature, bounded parameter range, and stop condition. Ambiguous ideas are
rejected for clarification. The parser does not invent or expand search space.

No repo-owned live LLM/API abstraction exists on this branch. No LLM, network,
credentials, or secrets are used. A future LLM adapter requires a separate
approved package and deterministic validation after model output.

Draft-to-preregistration remains a human-gated future action.
