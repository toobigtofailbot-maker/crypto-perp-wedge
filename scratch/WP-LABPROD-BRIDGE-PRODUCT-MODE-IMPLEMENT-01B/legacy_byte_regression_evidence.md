# Legacy Byte Regression Evidence

## Verdict

`legacy_behavior_changed`: false

## Pre-Implementation Baseline

Captured before code changes on package branch after repo-truth discovery, using `tests.test_agent_formalizer_runner_bridge._run(tmp_path)` with deterministic fixtures.

- run_id: `c81e86a223723b97`
- status: `completed`
- trial counts: completed 8, failed 0, invalid 0, pruned 0, blocked 0
- `RUN_NONCANONICAL_OFFLINE_SWEEP` allowed audit records: 2

Key artifact hashes:

- Strategy Spec: `sha256:2152be54645c20bc0a320142002abfb3a223f28f7ca7c1f9cbbd638d9e03caae`
- Variant Manifest: `sha256:ad0ec366a903bbd12f8a06d50d6a61cdff452d4bdeab6d859ce29f2bd13f947c`
- Sweep Plan: `sha256:9dce4b61acfad4b04f1e38836b3fb8297122a6a6b0e82e6c35c2ab1a591c2254`
- Denominator ledger: `sha256:bca1017aa5771bc6949a7cd61d9883994d45786e7fda2a937bcc7eab41aebf31`
- Human review packet: `sha256:650a3559582c12ad7f7150279b76a0a779db498f3ed8c85d740e723fb2959c2f`
- Runner result: `sha256:e391705cd21b8cdabddb092b4a55907f0855077716194ae064326c2ad521a645`

## Post-Implementation Evidence

`tests/test_agent_formalizer_runner_bridge.py::test_legacy_bridge_byte_regression_fixture_remains_stable` pins the exact pre-change run id, key artifact paths, key artifact hashes, trial counts, and runner audit count.

Focused command result:

- `.venv\Scripts\python.exe -m pytest tests/test_agent_formalizer_runner_bridge.py -q`
- Result: `65 passed`

## Scope Check

The legacy config dataclass was not extended, so legacy `config.__dict__` remains unchanged in the legacy run identity hash. The legacy constructor path, approval parser, source prefixes, output root derivation, runner invocation branch, denominator schema, and review packet schema remain default behavior.
