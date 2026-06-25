"""Read-only operator daily brief and weekly research-lab report surface.

This package shapes the deterministic read-only lab dashboard projection
(``tools/lab_dashboard``, itself a projection of the merged coordinator state
model ``tools/lab_state``) into operator-readable **daily brief** and **weekly
report** artifacts. It re-derives no state, introduces no new state vocabulary,
and is descriptive only: it emits no recommendation, ranking-as-authority,
promotion label, or auto-send.
"""
