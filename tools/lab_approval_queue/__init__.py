"""Read-only research-lab approval / gate queue surface.

This package projects the merged coordinator state model
(``tools/lab_state``) into an operator-facing queue of *pending human gates*,
*blocked validation states*, and *candidate-review readiness when evidence
exists*. It displays gates; it never executes them. It writes nothing, runs no
strategy, fetches no data, and renders no executable control.
"""
