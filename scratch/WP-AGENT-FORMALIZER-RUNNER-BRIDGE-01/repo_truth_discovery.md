# WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01 Repo-Truth Discovery

## Base and dependencies

- Refreshed base: `origin/main` at `ad0b399`, the merge commit for PR #545.
- PR #544 formalizer contract: `agent_formalized_idea_v1` under
  `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/<run_id>/formalized_idea.json`.
  The only merged draft adapter copies the `STRAT-SPEC-0003` SMA/stddev
  mean-reversion capability family to a validator-clean scratch draft.
- PR #545 approval contract is a colocated operator JSON marker. Its runner is
  fixture-only and explicitly records that real `run_offline_sweep` integration
  remained blocked pending VM/Sweep inputs.

## ToolContext

- Gate: `tools/agent_sandbox/tool_context.py`.
- Closed policy: `tools/agent_sandbox/permissions.py`.
- Existing scratch reads/writes, validator actions, hard canonical/protected
  blocks, audit-before-execute behavior, and `noncanonical_experiment_run` are
  reusable. The bridge needs a separate narrow role and
  `noncanonical_offline_sweep_run` action because generic sweep/backtest actions
  remain hard blocked.

## Runner and parent contracts

- Entry point: `tools.research_runner.run_offline_sweep.run_offline_sweep`.
- Required inputs: schema- and validator-clean Strategy Spec, Variant Manifest,
  and Sweep Plan. The runner additionally requires the manifest
  `pre_registration_status` to be `frozen_for_sweep_planning`.
- Existing schemas:
  `research/schemas/strategy_spec.schema.json`,
  `research/schemas/variant_manifest.schema.json`, and
  `research/schemas/sweep_plan.schema.json`.
- VM/Sweep validator:
  `tools.registry.validate_variant_sweep_artifacts`; it accepts caller-supplied
  scratch directories and validates parent hashes, population accounting,
  frozen compatibility status, assignments, and sweep linkage.
- The exact supported family has merged templates
  `VM-0003.variant_manifest.json` and `SWEEP-PLAN-0003.sweep_plan.json`.
  Reusing their bounded eight-row grid avoids inventing strategy or search
  semantics.

## Scratch runner support

- The runner accepts caller-supplied input paths and output directories.
- `--write-result-population` rejects the canonical
  `research/result_populations/` tree but permits a scratch output directory.
- The produced scratch Result Population-shaped artifact is validated with the
  existing Result Population validator and contains explicit non-authority
  declarations.
- `canonical_15m=True` plus a local CSV fixture compiles the supplied Strategy
  Spec/variant through the real signal compiler and backtester. It is offline,
  deterministic, and uses zero funding for the fixture.
- No runner or backtester change is required for this package.

## Trial accounting

- Native runner outcomes are `successful`, `failed`, `invalid`, `excluded`,
  `errored`, `aborted`, `filtered`, `data_unavailable`, and `not_attempted`.
- The bridge ledger maps them without dropping rows:
  successful -> completed; failed -> failed; invalid -> invalid;
  excluded/filtered -> pruned; and errored/aborted/data_unavailable/not_attempted
  -> blocked. The original runner outcome is retained on every ledger row.

## Funding and data availability

- Merged backtest truth defaults `funding_cost_mode` to `off`.
- The offline runner does not expose a funding mode argument and its 15m fixture
  creates zero funding. Therefore default-off is supportable, while a requested
  funding-on run must block even after explicit operator approval; labeling a
  zero-funding run as funding-on would be false.
- Availability facts come from the formalizer assessment and merged availability
  labels. Recent/snapshot/streaming/vendor constrained features block a
  full-history public run. Open interest is never reconstructed from trades.
  Liquidation history requires vendor/captured data. Public archive taker flow
  requires a referenced present local source.

## Local data requirement

- The first bridge requires a repo-local 15m OHLCV CSV under the active bridge
  scratch prefix (or an already allowlisted test fixture path). It is hashed and
  read through ToolContext before runner invocation. No network, credentials,
  private endpoint, or live data fetch is used.

## Repo-truth adjustments to the brief

- Runner-compatible VM/Sweep copies must carry schema-required planning/frozen
  fields. In scratch these are technical compatibility metadata only and are
  explicitly labeled as granting no canonical approval or freeze authority.
- Explicit funding-on execution is not currently supported by the real runner;
  the bridge fails closed and makes the reason visible rather than changing the
  runner or funding model inside this package.
