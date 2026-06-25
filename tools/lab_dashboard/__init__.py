"""Read-only research results dashboard surface over the lab coordinator state.

This package projects ``tools/lab_state`` coordinator-state snapshots into a
deterministic, read-only operator visibility model and renders it as a static
HTML / markdown artifact. It contains no executable controls: it never runs a
strategy, resumes edge-search, executes a transition, writes canonical or
candidate-lifecycle evidence, or fetches data. See
``docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md``.
"""
