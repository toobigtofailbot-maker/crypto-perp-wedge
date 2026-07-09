# Direct-Agent Reconciliation Evidence

## Scope

This evidence covers `tools.lab_pipeline.gates_adapter.run_product_gates_adapters`.

## WFO/OOS

- Adapter entry point: `tools.oos_gate.evaluate.evaluate_candidate_review_gate`.
- Direct comparison: the adapter repeats the existing function call with the same candidate payload and missing gate artifact.
- Comparison rule: Python payload equality.
- Normalization: none.
- Current verdict: passed in `tests/test_lab_pipeline_gates_adapter.py`.

## Robustness

- Adapter entry point: `tools.research_agents.robustness_diagnostician_agent.RobustnessDiagnosticianAgent.run`.
- Direct comparison: the adapter runs the existing agent twice over the same temporary compatibility inputs.
- Compared outputs:
  - returned result object;
  - `robustness_review_packet.json` payload;
  - `robustness_diagnostics.json` payload.
- Comparison rule: payload equality.
- Normalization: none.
- Current verdict: passed in `tests/test_lab_pipeline_gates_adapter.py`.

## Candidate Review

- Adapter entry point: `tools.research_agents.candidate_review_packet_agent.CandidateReviewPacketAgent.run`.
- Direct comparison: the adapter runs the existing agent twice over the same temporary compatibility inputs.
- Compared outputs:
  - returned result object;
  - `candidate_review_packet.json` payload;
  - `candidate_review_packet.md` text.
- Comparison rule: payload/text equality.
- Normalization: none.
- Current verdict: passed in `tests/test_lab_pipeline_gates_adapter.py`.

## Stop Condition Check

No new normalization was created. If any direct repeat comparison fails, `GatesAdapterError` is raised and no successful advisory result is returned.
