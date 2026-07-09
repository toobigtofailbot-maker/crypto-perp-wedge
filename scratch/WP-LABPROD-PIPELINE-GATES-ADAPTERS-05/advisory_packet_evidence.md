# Advisory Packet Evidence

## Implementation

- Entry point: `tools.lab_pipeline.gates_adapter.run_product_gates_adapters`.
- Packet schema: `product_pipeline_advisory_review_packet_v1`.
- Output root: `scratch/WP-LABPROD-PIPELINE-GATES-ADAPTERS-05/outputs`.
- Focused test: `tests/test_lab_pipeline_gates_adapter.py::test_product_gates_adapter_invokes_existing_agents_and_writes_advisory_packet`.

## Contents Verified

The focused test verifies that the advisory packet includes:

- runner adapter reference and Result Population reference;
- product bridge reference;
- denominator counts for `completed`, `failed`, `invalid`, `blocked`, `pruned`;
- WFO/OOS result with withheld statistics;
- robustness wrapper with raw existing-agent review and diagnostics payloads;
- candidate-review wrapper with raw existing-agent JSON and Markdown payloads;
- withheld-statistics section;
- candidate-surface routing;
- non-promotion posture;
- non-authority assertions.

## Current Fixture Evidence

The current product runner fixture preserves denominator counts:

```json
{
  "completed": 8,
  "failed": 0,
  "invalid": 0,
  "blocked": 0,
  "pruned": 0
}
```

The focused test verifies no canonical `research/result_populations` directory and no `research/candidate_registry.jsonl` are created in the temp repo.
