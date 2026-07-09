# Lab Productization Pipeline Gates Adapters

## Summary

`WP-LABPROD-PIPELINE-GATES-ADAPTERS-05` adds a narrow advisory evaluation adapter layer over product runner adapter output. It consumes `product_runner_adapter_result_v1`, invokes existing WFO/OOS, robustness, and candidate-review components, and writes a noncanonical product-scratch advisory packet when called.

The adapter does not create canonical evidence, register candidates, cross evidence, promote, mark readiness, contact paper/live/runtime, use scheduler/autonomy, fire notifications, call providers/APIs, mutate dependencies/configs/data, or touch protected runtime paths.

## Inputs

The entry point is:

```text
tools.lab_pipeline.gates_adapter.run_product_gates_adapters
```

It requires a `runner_adapter_result.json` produced by `tools.lab_pipeline.runner_adapter.run_product_runner_adapter`.

Required runner facts:

- runner adapter run id;
- adapter Result Population path/hash;
- direct Result Population path/hash;
- direct runner reconciliation verdict;
- bridge preparation run id;
- product pipeline run id;
- execute approval path/hash;
- denominator counts in `completed`, `failed`, `invalid`, `blocked`, `pruned`;
- `noncanonical_product_scratch_only` status.

## Existing-Agent Invocation

The adapter invokes existing components rather than reimplementing logic:

- WFO/OOS: `tools.oos_gate.evaluate.evaluate_candidate_review_gate`;
- robustness: `tools.research_agents.robustness_diagnostician_agent.RobustnessDiagnosticianAgent.run`;
- candidate review: `tools.research_agents.candidate_review_packet_agent.CandidateReviewPacketAgent.run`;
- GO routing scaffold: `tools.lab_pipeline.gate_actions.record_candidate_surface_decision`.

Current robustness and candidate-review agents accept legacy bridge-shaped scratch paths, not direct product runner scratch paths. The product adapter therefore builds a temporary repo-shaped compatibility sandbox, runs the existing agents there, embeds their raw output payloads in product adapter wrappers, and writes only package-local product scratch outputs.

## WFO/OOS Posture

Current product runner output contains aggregate Result Population rows. It does not contain committed walk-forward/OOS windows, purge/embargo periods, or fold-level OOS metrics.

The WFO/OOS adapter therefore invokes the existing gate evaluator with missing gate evidence and records:

- `adapter_status = blocked`;
- `withheld_missing_walkforward_oos_inputs`;
- no fabricated WFO/OOS metrics;
- no zero-filled OOS metrics;
- no pass/fail authority.

## Advisory Packet

The advisory packet schema is `product_pipeline_advisory_review_packet_v1`. It includes:

- runner result reference;
- product bridge reference;
- full denominator counts;
- WFO/OOS result;
- robustness result wrapper with raw existing-agent payload;
- candidate-review result wrapper with raw existing-agent payload;
- withheld-statistics section;
- direct-agent reconciliation;
- candidate-surface routing;
- non-promotion posture;
- non-authority assertions.

## Candidate Surface Routing

Allowed surface statuses remain exactly:

- `hold_for_review`;
- `needs_more_evidence`;
- `do_not_escalate`.

The current product runner fixture path routes to `needs_more_evidence` because WFO/OOS evidence is missing and robustness/candidate-review packets preserve missing fold/OOS and per-trade caveats.

No GO-like path can auto-admit, auto-cross, auto-promote, write candidate lifecycle, write candidate registry, or write canonical evidence.

## Reconciliation

The adapter performs direct-agent reconciliation:

- WFO/OOS output is compared against a direct repeat of the existing gate evaluator.
- Robustness output is compared against a direct repeat of the existing robustness agent on the same compatibility inputs.
- Candidate-review JSON and Markdown are compared against a direct repeat of the existing candidate-review agent on the same compatibility inputs.

No normalization is introduced. A mismatch fails closed.
