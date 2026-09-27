# CPW-CANON-01 — Engine-Neutral Execution/Evidence Contract

- Branch: `codex/cpw-canon-01-engine-neutral-execution-evidence-contract`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/716
- Base SHA: `e2948465f36f9b45dfc0a97382b57fa374f956ab`
- Implementation/final semantic HEAD: `27d7bd3d2dd2c3bab135bd7e6c1ea6bd0cf391ba`
- Package class: T2 — narrow production contract
- Merge status: open, non-draft, not merged; Side exact-head review required

## Changed files

1. `tools/execution_evidence_contract.py`
2. `tools/execution_evidence_legacy_rp.py`
3. `tests/test_execution_evidence_contract.py`
4. `docs/architecture/2026-09-engine_neutral_execution_evidence_contract.md`
5. `docs/status_entries/CPW-CANON-01.md`

## Outcome and validation

The package adds the engine-neutral RunRequest and ResultEnvelope content
contracts, deterministic CANON-01 JSON hashes, and a read-only RP v1 adapter
that retains provenance and exact legacy hashes outside the new scientific
identities.

Required T2 validation passed after the final `origin/main` rebase check:

- `python -m pytest tests/test_execution_evidence_contract.py -q`: 19 passed.
- `python -m pytest tests/test_research_domain.py -q`: 19 passed.
- `python -m pytest tests/test_research_replay_normalization.py -q`: 11 passed.
- `python -m pytest tests/test_validate_result_populations.py -q`: 61 passed.
- `python -m tools.registry.validate_result_populations`: all committed artifacts valid.
- `tools/dev/diff_scope_summary.py` in committed base-to-head mode: exactly five
  allowed files, no forbidden-path matches, and no untracked or staged files.
- `git diff --check`: passed.

Full pytest: NOT RUN — narrow T2 contract package; no existing schema,
validator, runner, dependency, query layer, protected writer, or runtime
surface changed; not used as merge evidence.

## Boundary

No historical RP or legacy hash meaning changes. No existing schema, validator,
runner, replay production module, canonical writer/crossing, framework
implementation, runtime, paper/live/protected path, or dependency changes.

After merge, CPW-NAUTILUS-N1-01 is next in Karl's serialized plan.
This package does not authorize N1-01 or any later package.
