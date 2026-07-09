# Repo Truth Discovery

Package: `WP-LABPROD-BOUNDED-SWEEP-SCALE-06`

## Facts

- Base branch: refreshed `main`.
- Base commit: `129bb28424c825a2d0bb1607366dc09bd9ef01c1`.
- `origin/main` equals local `main` at `129bb28424c825a2d0bb1607366dc09bd9ef01c1`.
- PR #624 is merged in the base commit: `Merge pull request #624 from toobigtofailbot-maker/codex/wp-labprod-pipeline-gates-adapters-05`.
- `gh pr list --state open --json number,title,headRefName,baseRefName,files --limit 100` returned `[]`.
- PR #588 is merged. `gh pr view 588` reports title `WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01`, merge commit `3060ad49a8cef605eeeb5fd058e1c3bee4a998c1`, and scratch artifacts including `synthetic_population_manifest.json`, `denominator_accounting.json`, and `validation_summary.txt`.
- Product runner adapter exists at `tools/lab_pipeline/runner_adapter.py`.
- Product gates adapter exists at `tools/lab_pipeline/gates_adapter.py`.
- Current runner outcome vocabulary includes `successful`, `failed`, `invalid`, `excluded`, `errored`, `aborted`, `filtered`, `data_unavailable`, and `not_attempted`.

## Inferences

- The PR #624 hard gate is satisfied by current merged repo truth.
- The no-open-PR hard gate is satisfied for runner adapter, gates adapter, result-population schema, and denominator handling.
- The product pipeline can be scaled safely at the runner-adapter approval boundary without changing runner or backtester semantics.

## Decisions

- Implement scale support as approval/budget plumbing in the product runner adapter.
- Preserve all existing runner semantics and only validate prepared denominator scope before and after runner invocation.
- Surface the scale budget in the product gates advisory packet.

## Open Questions

- Repo truth does not expose a native product runner `no_trade` outcome category; future support should map it explicitly if the runner vocabulary adds it.

## Future Options

- A future package may add a dedicated large real product run fixture once a real edge-search flow authorizes one.
- A future package may add UI/cockpit display of `approved_sweep_budget` if product cockpit scope authorizes it.
