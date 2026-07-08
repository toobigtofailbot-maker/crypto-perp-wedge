# WP-LABPROD-INPRODUCT-GATE-ACTIONS-01 Branch State

## Scope Summary

Adds local, non-canonical in-product gate-action scaffolding for the merged lab
pipeline preregistration approval contract and a future advisory
candidate-surface decision.

This package creates no cockpit button and no canonical or lifecycle write path.

## Repo-Truth Discovery

Fact: `tools/lab_pipeline` already creates a frozen
`preregistration_packet.json`, an `approval_requirement.json`, and a file-based
approval contract consumed by `tools.lab_pipeline.run --approval`.

Fact: `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md` and
`docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md` are read-only surfaces and do not
execute gates.

Fact: candidate lifecycle design and implementation paths remain separate and
human-gated. This package did not modify candidate lifecycle files.

Inference: the safe product-action layer should produce only local packets that
the existing pipeline can already validate.

Decision: add `tools/lab_pipeline/gate_actions.py` plus additive CLI handling in
`tools/lab_pipeline/run.py`.

Open question: exact UI placement remains deferred to a later cockpit/UI package.

Future option: a later package may bind these CLI/action contracts to a UI
control if it preserves the same non-authority boundary.

## Implementation

Changed files:

- `tools/lab_pipeline/gate_actions.py`
- `tools/lab_pipeline/run.py`
- `tests/test_lab_pipeline_gate_actions.py`
- `docs/research/LAB_PRODUCTIZATION_GATE_ACTIONS.md`
- `docs/status_entries/WP-LABPROD-INPRODUCT-GATE-ACTIONS-01.md`
- package scratch evidence under
  `scratch/WP-LABPROD-INPRODUCT-GATE-ACTIONS-01/`

Implemented actions:

- prereg approval preview with no marker creation;
- exact explicit prereg approval marker generation;
- candidate-surface advisory decisions limited to `hold_for_review`,
  `needs_more_evidence`, and `do_not_escalate`;
- repo-local output path safety checks;
- non-authority assertions on every action output.

Forbidden actions:

- candidate admission;
- candidate lifecycle write;
- canonical crossing;
- promotion/readiness;
- paper/live/runtime start or contact;
- scheduler/autonomy;
- notification sending;
- provider/API/credential use;
- dependency/config/data acquisition;
- protected-path touch.

## Validation Status

Focused validation and required validators are recorded in
`scratch/WP-LABPROD-INPRODUCT-GATE-ACTIONS-01/validation_summary.txt`.

## Boundary Summary

No `src/`, `lib/`, `configs/`, `.claude/`, `data/`, cockpit UI,
candidate lifecycle, canonical Result Population, Strategy Spec, Variant
Manifest, Sweep Plan, trial-log, dependency, provider/API, credential,
paper/live/runtime, OMS/risk/reconciliation, scheduler, notification, or
protected path was changed.

Outputs are package-local or temporary-validation-local only.
