# Repo-truth discovery

- Refreshed `origin/main` was `8f4c8b6`, the merge commit for PR #651.
- The locked architecture and all three queue schemas are present on that base.
- `research/queue/admissions/` is documented as inert and is not a runner or scheduler input.
- Existing canonical validators are `tools.registry.validate_strategy_specs` and `tools.registry.validate_variant_sweep_artifacts`; the writer consumes them without changing them.
- Work occurs only in the new sibling worktree and branch required by the package. The stopped `...-03` branch was not reused or modified.
- Final follow-up started from reviewed PR #652 head `9711774392a49680ddb9f164b10b50313867e118`; the PR was open, targeted `main`, and contained only its expected eight-file scope. The locked audit schema contains paths and hashes sufficient to reconstruct the stored queue item, Gate-Q approval, Strategy Spec, Variant Manifest, and Sweep Plan; their nested Gate-Q/item contracts locate the dataset and complete Gate-C/source lineage.
