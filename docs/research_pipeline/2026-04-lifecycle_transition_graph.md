# Lifecycle Transition Graph v1

## Purpose

This document defines the permitted Phase 9 lifecycle transition graph for
Lifecycle Change artifacts.

All unlisted edges are forbidden. `archived` is terminal.

## Permitted Edges

```text
proposed -> in_research
in_research -> research_concluded
research_concluded -> paper_eligible
research_concluded -> archived
paper_eligible -> paper_active
paper_eligible -> archived
paper_active -> paper_concluded
paper_active -> halted
paper_active -> archived
paper_concluded -> live_eligible
paper_concluded -> archived
live_eligible -> live_active
live_eligible -> archived
live_active -> paper_concluded
live_active -> halted
live_active -> archived
halted -> previous_non_halted_state
halted -> archived
any non-archived state -> halted
archived -> no outbound transition
```

The schema represents `any non-archived state -> halted` as explicit edge
strings for each non-archived source state.

The schema represents halted recovery with
`halted->previous_non_halted_state`, `from_state = halted`, and `to_state` set
to the recovered lifecycle state. JSON Schema cannot prove that the target is
the immediately preceding non-halted state without instance history. That check
belongs to WP-9b validator/integrity logic or later.

## Forbidden Examples

```text
proposed -> paper_active
proposed -> live_active
in_research -> paper_active
research_concluded -> live_active
paper_eligible -> live_active
archived -> any state
live_active -> in_research
```

## Evolution

Graph evolution requires explicit later versioned schema work. Future packages
must not silently add edges through validators, query views, helpers, or
artifact instances.

## Non-Claims

This graph does not execute lifecycle changes by itself and does not authorize
runtime deployment, paper execution, live execution, OMS changes, risk changes,
overlay changes, or protected-path behavior changes.
