"""Pure classification + summary for the coverage audit.

Reading is separated from classifying: :func:`classify_artifact` is a pure
function over a repo-relative path plus a :class:`CoverageContext`, so it is
trivially testable, while :func:`build_audit` does the aggregation. File I/O and
git enumeration live in ``run.py``.

Design intent
-------------
The lab coordinator state model (``tools/lab_state``) and every operator surface
read exactly the subjects bound in ``tools.lab_state.run.SUBJECTS``. So an
artifact is *operator-visible* only if it is one of those subjects' referenced
paths. Everything else is classified by descriptive type and a coverage status,
without ever pretending an uncovered artifact is covered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Vocabulary.
# ---------------------------------------------------------------------------
# The classification categories required by the package. Each discovered
# artifact resolves to exactly one (first matching rule wins).
CATEGORIES: tuple[str, ...] = (
    "coordinator_subject_covered",
    "surface_visible",
    "known_supporting_artifact",
    "known_fixture",
    "status_entry_only",
    "synthesis_or_report",
    "blocked_or_no_go_evidence",
    "candidate_or_crossing_evidence",
    "orphan_research_artifact",
    "requires_followup_mapping",
    "intentionally_out_of_scope",
)

# Coverage status is an orthogonal axis describing operator visibility, not the
# artifact's descriptive type.
COVERAGE_STATUSES: tuple[str, ...] = (
    "covered",          # resolves to a coordinator subject and is operator-visible
    "out_of_scope",     # edge-search-era / process evidence the coordinator omits by design
    "unmapped_gap",     # an operator-relevant conclusion not represented anywhere
    "malformed",        # exists but unreadable / malformed metadata (fail closed)
)


class AuditError(ValueError):
    """Raised when a classification violates the audit's own invariants."""


# ---------------------------------------------------------------------------
# Rule data. Kept as module constants so tests can assert against them.
# ---------------------------------------------------------------------------
# Roles in tools.lab_state.run.SUBJECTS whose artifact is *rendered* (shown as
# content) by a surface, vs merely *consulted* for a stage state.
_SURFACE_RENDERED_ROLES: frozenset[str] = frozenset(
    {"experiment_run", "candidate_review_reach", "reporting"}
)
_CONSULTED_ROLES: frozenset[str] = frozenset(
    {"formalization", "replay_normalization", "walkforward_oos_gate"}
)
_SUPPLEMENTAL_RENDERED_ROLE_PREFIXES: tuple[str, ...] = (
    "supplemental_",
    "legacy_",
    "canonical_",
    "bundle_",
)
_SUPPLEMENTAL_RENDERED_ROLES: frozenset[str] = frozenset(
    {"riskmanaged_conclusion_evidence"}
)

# Operator-relevant conclusions that are NOT bound to any coordinator subject.
# These are the silent-evidence gap set: committed conclusions an operator would
# expect to see but the coordinator does not represent. Directory prefixes.
_UNMAPPED_CONCLUSION_DIRS: tuple[str, ...] = (
    "scratch/WP-RESEARCH-FUNDING-CARRY-01/",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02/",
    "scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/",
    "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/",
    "scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/",
    "scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/",
)
# Canonical registries that are operator-relevant but unbound.
_UNMAPPED_CANONICAL_PREFIXES: tuple[str, ...] = (
    "research/result_populations/",
)
_UNMAPPED_CANONICAL_FILES: frozenset[str] = frozenset(
    {"research/candidate_registry.jsonl"}
)
# Unbound synthesis docs (a bound one is a coordinator path and handled first).
_UNMAPPED_SYNTHESIS_FILES: frozenset[str] = frozenset(
    {"docs/research/PRICEONLY_SYNTHESIS_2026-06.md"}
)

# Lab tooling / integration scratch + contract docs: supporting, not research
# conclusions, and intentionally not coordinator subjects.
_SUPPORTING_SCRATCH_PREFIXES: tuple[str, ...] = (
    "scratch/WP-LAB-",
    "scratch/WP-AGENT-",
    "scratch/WP-CHASSIS-",
    "scratch/WP-COMPILER-",
    "scratch/WP-DATA-",
    "scratch/WP-INFRA-",
    "scratch/WP-PILOT-",
    "scratch/WP-RUNNER-",
    "scratch/EXT-",
)
_SUPPORTING_DOC_PREFIXES: tuple[str, ...] = (
    "docs/research/LAB_",
)

# Filename markers used to subclassify unbound research conclusion scratch.
_NO_GO_MARKERS: tuple[str, ...] = (
    "blocked_",
    "no_candidate_review_packet_reason",
    "missing_diagnostics",
)
_CANDIDATE_MARKERS: tuple[str, ...] = (
    "result_packet",
    "human_review_packet",
    "candidate",
    "crossing",
    ".result_population.json",
)


@dataclass
class CoverageContext:
    """Immutable inputs needed to classify an artifact.

    ``surface_paths`` and ``consulted_paths`` are derived from the live
    ``SUBJECTS`` binding so the audit stays in sync if a subject is added.
    """

    surface_paths: frozenset[str]
    consulted_paths: frozenset[str]
    fixture_paths: frozenset[str] = field(default_factory=frozenset)

    @property
    def coordinator_paths(self) -> frozenset[str]:
        return self.surface_paths | self.consulted_paths


@dataclass
class ArtifactClassification:
    """One artifact's classification result."""

    path: str
    category: str
    coverage_status: str
    surface_visible: bool
    requires_followup: bool
    malformed: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "category": self.category,
            "coverage_status": self.coverage_status,
            "surface_visible": self.surface_visible,
            "requires_followup": self.requires_followup,
            "malformed": self.malformed,
            "rationale": self.rationale,
        }


def coordinator_paths_from_subjects(
    subjects: dict[str, dict[str, Any]],
) -> tuple[frozenset[str], frozenset[str]]:
    """Split coordinator-referenced paths into (surface-rendered, consulted).

    Pure over the ``SUBJECTS`` shape so the resolver binding is the single source
    of truth for what counts as operator-visible.
    """
    surface: set[str] = set()
    consulted: set[str] = set()
    for subject in subjects.values():
        for role, rel in subject.get("artifacts", {}).items():
            if not rel:
                continue
            if role in _SURFACE_RENDERED_ROLES:
                surface.add(rel)
            elif role in _CONSULTED_ROLES:
                consulted.add(rel)
            else:  # pragma: no cover - guards against an unmodelled role
                raise AuditError(f"unknown subject artifact role: {role}")
        for item in subject.get("supplemental_artifacts", []):
            rel = item.get("path")
            role = str(item.get("role", "supplemental_evidence"))
            if not rel:
                continue
            if (
                role not in _SUPPLEMENTAL_RENDERED_ROLES
                and not role.startswith(_SUPPLEMENTAL_RENDERED_ROLE_PREFIXES)
            ):
                raise AuditError(f"unknown supplemental artifact role: {role}")
            surface.add(str(rel))
    # A path that is rendered for one subject dominates a consulted-only use.
    consulted -= surface
    return frozenset(surface), frozenset(consulted)


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def classify_artifact(
    path: str, ctx: CoverageContext, *, malformed: bool = False
) -> ArtifactClassification:
    """Classify one repo-relative artifact path. Pure; first matching rule wins.

    ``malformed`` is set by the caller when a JSON artifact it tried to read for
    metadata could not be parsed — the audit then fails closed (it never treats a
    malformed artifact as covered or out-of-scope).
    """
    name = _basename(path)

    # 0. Fail closed: malformed metadata never masquerades as coverage.
    if malformed:
        return ArtifactClassification(
            path=path,
            category="requires_followup_mapping",
            coverage_status="malformed",
            surface_visible=False,
            requires_followup=True,
            malformed=True,
            rationale="Artifact exists but its metadata could not be parsed; "
            "fail closed rather than infer coverage.",
        )

    # 1. Surface-rendered coordinator path.
    if path in ctx.surface_paths:
        return ArtifactClassification(
            path, "surface_visible", "covered", True, False, False,
            "Rendered as content by a coordinator operator surface.",
        )

    # 2. Consulted coordinator path (drives a stage state, not rendered).
    if path in ctx.consulted_paths:
        return ArtifactClassification(
            path, "coordinator_subject_covered", "covered", False, False, False,
            "Consulted by the coordinator to resolve a stage state.",
        )

    # 3. Declared test fixture.
    if path in ctx.fixture_paths:
        return ArtifactClassification(
            path, "known_fixture", "out_of_scope", False, False, False,
            "Test fixture exercised by lab tooling tests.",
        )

    # 4. Unbound operator-relevant conclusions → coverage gaps.
    if (
        path in _UNMAPPED_CANONICAL_FILES
        or path in _UNMAPPED_SYNTHESIS_FILES
        or path.startswith(_UNMAPPED_CANONICAL_PREFIXES)
        or path.startswith(_UNMAPPED_CONCLUSION_DIRS)
    ):
        category = _conclusion_subcategory(path, name)
        return ArtifactClassification(
            path, category, "unmapped_gap", False, True, False,
            "Committed conclusion not bound to any coordinator subject; "
            "operator view does not represent it.",
        )

    # 5. Lab tooling / integration supporting scratch + contract docs.
    if path.startswith(_SUPPORTING_SCRATCH_PREFIXES) or path.startswith(
        _SUPPORTING_DOC_PREFIXES
    ):
        return ArtifactClassification(
            path, "known_supporting_artifact", "out_of_scope", False, False, False,
            "Lab tooling / integration supporting artifact (not a research "
            "conclusion the coordinator tracks).",
        )

    # 6. Status entries (other than the two bound formalization entries).
    if path.startswith("docs/status_entries/"):
        return ArtifactClassification(
            path, "status_entry_only", "out_of_scope", False, False, False,
            "Repo status entry; not bound as a coordinator formalization subject.",
        )

    # 7. Other docs/research synthesis / contract docs.
    if path.startswith("docs/research/"):
        return ArtifactClassification(
            path, "synthesis_or_report", "out_of_scope", False, False, False,
            "Research synthesis / contract doc not bound to a coordinator subject.",
        )

    # 8. Everything else under research/ is edge-search-era process evidence the
    #    coordinator omits by design (edge-search held).
    if path.startswith("research/"):
        return ArtifactClassification(
            path, "intentionally_out_of_scope", "out_of_scope", False, False, False,
            "Edge-search-era research/process evidence; coordinator deliberately "
            "does not surface it while edge-search is held.",
        )

    # 9. Remaining scratch (research process scratch not otherwise classified).
    if path.startswith("scratch/"):
        return ArtifactClassification(
            path, "orphan_research_artifact", "out_of_scope", False, False, False,
            "Research process scratch not bound to a coordinator subject.",
        )

    # 10. Default fallthrough.
    return ArtifactClassification(
        path, "intentionally_out_of_scope", "out_of_scope", False, False, False,
        "Outside audited research roots.",
    )


def _conclusion_subcategory(path: str, name: str) -> str:
    """Descriptive type for an unbound committed conclusion."""
    lower = name.lower()
    if lower.endswith(".md") and "synthesis" in lower:
        return "synthesis_or_report"
    # NO-GO / blocked markers win first: a "no_candidate_review_packet_reason"
    # is a NO-GO record, not candidate evidence, despite containing "candidate".
    if any(marker in lower for marker in _NO_GO_MARKERS):
        return "blocked_or_no_go_evidence"
    if any(marker in lower for marker in _CANDIDATE_MARKERS):
        return "candidate_or_crossing_evidence"
    if path in _UNMAPPED_SYNTHESIS_FILES:
        return "synthesis_or_report"
    # Supporting files inside an unbound conclusion dir still require mapping.
    return "requires_followup_mapping"


# ---------------------------------------------------------------------------
# Aggregation.
# ---------------------------------------------------------------------------
def build_audit(
    classifications: Iterable[ArtifactClassification],
    *,
    subjects: dict[str, dict[str, Any]],
    schema_version: str = "lab_state_coverage_audit/v1",
) -> dict[str, Any]:
    """Aggregate per-artifact classifications into the audit summary payload."""
    items = list(classifications)
    by_category: dict[str, int] = {c: 0 for c in CATEGORIES}
    by_status: dict[str, int] = {s: 0 for s in COVERAGE_STATUSES}
    for item in items:
        if item.category not in by_category:
            raise AuditError(f"unknown category: {item.category}")
        if item.coverage_status not in by_status:
            raise AuditError(f"unknown coverage_status: {item.coverage_status}")
        by_category[item.category] += 1
        by_status[item.coverage_status] += 1

    gaps = [i for i in items if i.coverage_status == "unmapped_gap"]
    malformed = [i for i in items if i.malformed]
    covered = [i for i in items if i.coverage_status == "covered"]
    surface_visible = [i for i in items if i.surface_visible]

    findings = _build_findings(gaps)
    follow_ups = _recommended_follow_ups(gaps, malformed)

    return {
        "schema_version": schema_version,
        "non_authority_declaration": (
            "Read-only coverage audit. Mutates no artifact, runs no strategy, "
            "fetches no data, changes no coordinator/candidate bindings, and "
            "resumes no edge-search. Gaps are reported, never fixed here."
        ),
        "coordinator_subjects": sorted(subjects),
        "totals": {
            "total_discovered_artifacts": len(items),
            "covered_coordinator_artifacts": len(covered),
            "surface_visible_artifacts": len(surface_visible),
            "unmapped_gap_artifacts": len(gaps),
            "malformed_or_unreadable_artifacts": len(malformed),
        },
        "by_category": by_category,
        "by_coverage_status": by_status,
        "findings": findings,
        "recommended_follow_up_packages": follow_ups,
        "gaps_found": bool(gaps) or bool(malformed),
    }


def _gap_group(path: str) -> str:
    """Group a gap path to a recommended-mapping bucket."""
    for prefix in _UNMAPPED_CONCLUSION_DIRS:
        if path.startswith(prefix):
            return prefix.rstrip("/")
    if path.startswith("research/result_populations/"):
        return "research/result_populations"
    if path in _UNMAPPED_CANONICAL_FILES:
        return path
    if path in _UNMAPPED_SYNTHESIS_FILES:
        return path
    return "other_unmapped"


def _build_findings(
    gaps: list[ArtifactClassification],
) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for item in gaps:
        groups.setdefault(_gap_group(item.path), []).append(item.path)
    findings: list[dict[str, Any]] = []
    for group in sorted(groups):
        paths = sorted(groups[group])
        findings.append(
            {
                "subject_group": group,
                "kind": "unmapped_committed_conclusion",
                "artifact_count": len(paths),
                "example_paths": paths[:5],
                "detail": (
                    "Committed research conclusion not bound to any coordinator "
                    "subject; not represented in dashboard/report/approval/scheduler."
                ),
            }
        )
    return findings


def _recommended_follow_ups(
    gaps: list[ArtifactClassification],
    malformed: list[ArtifactClassification],
) -> list[dict[str, Any]]:
    follow_ups: list[dict[str, Any]] = []
    if gaps:
        groups = sorted({_gap_group(i.path) for i in gaps})
        follow_ups.append(
            {
                "package": "WP-LAB-COORDINATOR-SUBJECT-COVERAGE-EXTENSION-01",
                "intent": (
                    "Bind the unmapped committed research conclusions as "
                    "additional read-only coordinator subjects so the operator "
                    "view stops omitting them. No new research; mapping only."
                ),
                "subject_groups": groups,
                "authority_note": (
                    "Requires editing tools/lab_state/run.py SUBJECTS — out of "
                    "scope for this audit-only package."
                ),
            }
        )
    if malformed:
        follow_ups.append(
            {
                "package": "WP-LAB-COVERAGE-MALFORMED-ARTIFACT-TRIAGE-01",
                "intent": (
                    "Triage artifacts whose metadata could not be parsed during "
                    "the coverage audit (fail-closed)."
                ),
                "artifact_count": len(malformed),
            }
        )
    return follow_ups
