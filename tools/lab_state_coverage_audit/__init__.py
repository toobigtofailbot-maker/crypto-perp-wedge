"""Read-only coverage audit of the lab coordinator state model and surfaces.

This package enumerates committed research artifacts and classifies each by how
it is (or is not) represented in the operator view that the coordinator state
model (`tools/lab_state`) and its surfaces (dashboard / report / approval /
scheduler) project. It mutates nothing, runs no strategy, fetches no data, and
never changes coordinator or candidate-lifecycle bindings. Coverage gaps are
reported as findings plus recommended follow-up packages — never fixed here.
"""

from tools.lab_state_coverage_audit.audit import (
    CATEGORIES,
    ArtifactClassification,
    AuditError,
    build_audit,
    classify_artifact,
    coordinator_paths_from_subjects,
)

__all__ = [
    "CATEGORIES",
    "ArtifactClassification",
    "AuditError",
    "build_audit",
    "classify_artifact",
    "coordinator_paths_from_subjects",
]
