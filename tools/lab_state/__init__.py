"""Read-only research-lab coordinator state model.

This package defines one canonical status vocabulary (``model``) and one
read-only resolver (``resolver``) over existing repo/scratch/research artifacts.
It never executes a lifecycle transition, runs a strategy, resumes edge-search,
writes canonical or candidate evidence, or touches runtime/paper/live paths.
"""

from tools.lab_state import model, resolver

__all__ = ["model", "resolver"]
