# PR Review Checklist

Review the changed files directly and check:

- The changed-file set matches the package objective.
- Forbidden paths stayed untouched unless explicitly authorized.
- The diff does not smuggle in architecture redesign or scope broadening.
- Required artifacts, docs, or paired evidence are present.
- Current-state tests or status references are not stale.
- Schema, validator, and query-layer changes remain aligned when those areas are in scope.
- Runtime boundaries, risk boundaries, and advisory-only boundaries remain intact.
- Validation evidence is strong enough for the package class.
- `docs/project_status.md` wording is accurate and uses branch-state phrasing when the work is not yet merged.
