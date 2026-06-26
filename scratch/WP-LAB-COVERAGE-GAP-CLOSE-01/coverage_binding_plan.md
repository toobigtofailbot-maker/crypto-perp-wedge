# Coverage Binding Plan

## Decision

- Add read-only supplemental artifact references to the coordinator snapshot shape.
- Bind the 99 pre-binding gap artifacts through six historical coordinator subjects, leaving the original two subjects intact.
- Keep existing state vocabulary; do not create readiness, approval, promotion, or operator-gate state.

## Subject Bindings

- `historical_canonical_evidence_bundle`: binds `9` former gap artifact(s); overall state `experiment_complete`; operator gate remains `not_started`.
- `edge_sma_family_blocked`: binds `13` former gap artifact(s); overall state `blocked`; operator gate remains `not_started`.
- `funding_carry_01_blocked_no_go`: binds `14` former gap artifact(s); overall state `no_go`; operator gate remains `not_started`.
- `funding_carry_02_no_go`: binds `45` former gap artifact(s); overall state `no_go`; operator gate remains `not_started`.
- `orb_exit_respec_blocked`: binds `10` former gap artifact(s); overall state `blocked`; operator gate remains `not_started`.
- `priceonly_synthesis_reported`: binds `8` former gap artifact(s); overall state `reported`; operator gate remains `not_started`.

## Non-Bindable

- None. All 99 former gaps are committed, readable, and safe to expose as read-only references.
