# Direct Runner Reconciliation Evidence

## Verdict

Adapter-vs-direct runner reconciliation is implemented and covered by focused tests.

## Mechanism

The adapter invokes `tools.research_runner.run_offline_sweep.run_offline_sweep` twice over the same bridge-prepared Strategy Spec / Variant Manifest / Sweep Plan:

- adapter invocation output: `runner_artifacts/adapter/<RP>.result_population.json`
- direct invocation output: `runner_artifacts/direct/<RP>.result_population.json`

Both invocations use the same deterministic seed and no adapter-side mutation of runner inputs or runner output semantics.

## Comparison

The adapter first compares raw Result Population file hashes. If raw bytes differ, it falls back only to the repo-defined read-only replay normalization contract in `tools/research_replay/normalization.py`.

If neither raw byte hashes nor normalized stable hashes match, the adapter fails closed.

## Focused Evidence

Command:

```text
.\.venv\Scripts\python.exe -m pytest tests/test_lab_pipeline_runner_adapter.py -q
```

Result:

```text
29 passed
```

Coverage includes:

- bridge prepare-only artifacts consumed as runner inputs;
- real existing runner invoked and written to product scratch;
- adapter and direct Result Population hashes match byte-wise in the positive path;
- direct reconciliation verdict recorded as `passed`;
- no canonical Result Population directory is written.

## Boundary

This evidence is non-authoritative package evidence only. It is not canonical evidence, not a candidate lifecycle record, not a gate result, not readiness, and not paper/live/runtime authority.
