# Repo Truth Discovery

## Fact

- Root checkout was refreshed from `origin/main` before the package worktree was
  created.
- Open PR collision check returned no open PRs.
- `tools/lab_pipeline` contains the merged pipeline preregistration approval
  contract from PR #612.
- The existing pipeline approval contract requires `approved_by = Karl`,
  `approval_scope = noncanonical_offline_research_execution_only`, the exact
  approval statement, exact packet hash binding, noncanonical execution true,
  and broader authority flags false.
- `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md` and
  `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md` explicitly describe read-only
  surfaces with no gate execution controls.
- Candidate lifecycle docs and code remain separate from this package and are
  not write targets.

## Inference

- The package should produce local action artifacts that the existing pipeline
  can consume, rather than changing the pipeline approval validator.
- Candidate-surface decisions should remain advisory records only and should not
  share the candidate lifecycle registry or crossing write paths.

## Decision

- Implement the action layer in `tools/lab_pipeline/gate_actions.py`.
- Add only additive CLI routing in `tools/lab_pipeline/run.py`.
- Keep all gate-action outputs package-local or temporary-validation-local.

## Open Question

- Where a later UI/cockpit package should place a control is deferred.

## Future Option

- A later UI package can call the CLI/API contract created here if it preserves
  the exact same approval and non-authority checks.
