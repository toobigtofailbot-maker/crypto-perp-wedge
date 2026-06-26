"""Tests for the read-only lab state-model coverage audit.

The pure classifier is exercised directly with synthetic paths; the full audit
build is exercised against the live repo to confirm the coordinator-bound paths
resolve to ``covered`` and that the audit never mutates anything.
"""

from __future__ import annotations

import pytest

from tools.lab_state.run import SUBJECTS
from tools.lab_state_coverage_audit import audit, run
from tools.lab_state_coverage_audit.audit import (
    CATEGORIES,
    COVERAGE_STATUSES,
    AuditError,
    CoverageContext,
    build_audit,
    classify_artifact,
    coordinator_paths_from_subjects,
)


@pytest.fixture
def ctx() -> CoverageContext:
    surface, consulted = coordinator_paths_from_subjects(SUBJECTS)
    return CoverageContext(surface_paths=surface, consulted_paths=consulted)


# ---------------------------------------------------------------------------
# coordinator_paths_from_subjects
# ---------------------------------------------------------------------------
def test_coordinator_paths_split_surface_vs_consulted() -> None:
    surface, consulted = coordinator_paths_from_subjects(SUBJECTS)
    # Reporting + conclusion + review records are surface-rendered.
    assert (
        "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md" in surface
    )
    assert (
        "scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json"
        in surface
    )
    # Formalization status entries are consulted for state only.
    assert (
        "docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md" in consulted
    )
    # The two sets are disjoint.
    assert not (surface & consulted)


def test_coordinator_paths_rejects_unknown_role() -> None:
    bad = {"x": {"artifacts": {"made_up_role": "scratch/x.json"}}}
    with pytest.raises(AuditError):
        coordinator_paths_from_subjects(bad)


# ---------------------------------------------------------------------------
# classify_artifact — coverage-bearing paths.
# ---------------------------------------------------------------------------
def test_surface_path_is_surface_visible_and_covered(ctx: CoverageContext) -> None:
    path = "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md"
    result = classify_artifact(path, ctx)
    assert result.category == "surface_visible"
    assert result.coverage_status == "covered"
    assert result.surface_visible is True
    assert result.requires_followup is False


def test_consulted_path_is_coordinator_covered_not_rendered(
    ctx: CoverageContext,
) -> None:
    path = "docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md"
    result = classify_artifact(path, ctx)
    assert result.category == "coordinator_subject_covered"
    assert result.coverage_status == "covered"
    assert result.surface_visible is False


# ---------------------------------------------------------------------------
# classify_artifact — gap / fail-closed paths.
# ---------------------------------------------------------------------------
def test_malformed_fails_closed(ctx: CoverageContext) -> None:
    # Even a coordinator surface path, if malformed, must not read as covered.
    path = "scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json"
    result = classify_artifact(path, ctx, malformed=True)
    assert result.malformed is True
    assert result.coverage_status == "malformed"
    assert result.category == "requires_followup_mapping"
    assert result.requires_followup is True


def test_former_no_go_conclusion_is_now_covered(ctx: CoverageContext) -> None:
    path = "scratch/WP-RESEARCH-FUNDING-CARRY-01/no_candidate_review_packet_reason.json"
    result = classify_artifact(path, ctx)
    assert result.coverage_status == "covered"
    assert result.category == "surface_visible"
    assert result.requires_followup is False


def test_former_result_packet_gap_is_now_covered(ctx: CoverageContext) -> None:
    path = "scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_result_packet.json"
    result = classify_artifact(path, ctx)
    assert result.coverage_status == "covered"
    assert result.category == "surface_visible"


def test_former_canonical_result_population_gap_is_now_covered(
    ctx: CoverageContext,
) -> None:
    path = "research/result_populations/RP-2592.result_population.json"
    result = classify_artifact(path, ctx)
    assert result.coverage_status == "covered"
    assert result.category == "surface_visible"


def test_former_synthesis_doc_gap_is_now_covered(ctx: CoverageContext) -> None:
    path = "docs/research/PRICEONLY_SYNTHESIS_2026-06.md"
    result = classify_artifact(path, ctx)
    assert result.coverage_status == "covered"
    assert result.category == "surface_visible"


# ---------------------------------------------------------------------------
# classify_artifact — out-of-scope buckets.
# ---------------------------------------------------------------------------
def test_lab_tooling_scratch_is_supporting(ctx: CoverageContext) -> None:
    result = classify_artifact(
        "scratch/WP-LAB-RESULTS-DASHBOARD-01/some_note.json", ctx
    )
    assert result.category == "known_supporting_artifact"
    assert result.coverage_status == "out_of_scope"


def test_other_status_entry_is_status_entry_only(ctx: CoverageContext) -> None:
    result = classify_artifact("docs/status_entries/WP-D3.md", ctx)
    assert result.category == "status_entry_only"


def test_edge_search_research_is_intentionally_out_of_scope(
    ctx: CoverageContext,
) -> None:
    result = classify_artifact("research/briefs/2026-04-foo/outputs/Q01.json", ctx)
    assert result.category == "intentionally_out_of_scope"
    assert result.coverage_status == "out_of_scope"


# ---------------------------------------------------------------------------
# build_audit aggregation.
# ---------------------------------------------------------------------------
def test_build_audit_counts_and_findings(ctx: CoverageContext) -> None:
    paths = [
        "docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md",  # covered/surface
        "docs/status_entries/WP-LAB-IDEA-INTAKE-FORMALIZATION-01.md",  # covered/consulted
        "scratch/WP-RESEARCH-FUNDING-CARRY-01/no_candidate_review_packet_reason.json",  # former gap, covered
        "research/briefs/2026-04-foo/outputs/Q01.json",  # oos
    ]
    classifications = [classify_artifact(p, ctx) for p in paths]
    summary = build_audit(classifications, subjects=SUBJECTS)
    assert summary["totals"]["total_discovered_artifacts"] == 4
    assert summary["totals"]["covered_coordinator_artifacts"] == 3
    assert summary["totals"]["surface_visible_artifacts"] == 2
    assert summary["totals"]["unmapped_gap_artifacts"] == 0
    assert summary["gaps_found"] is False
    assert summary["findings"] == []
    assert summary["recommended_follow_up_packages"] == []


def test_build_audit_rejects_unknown_category(ctx: CoverageContext) -> None:
    good = classify_artifact("research/x.json", ctx)
    good.category = "totally_invalid"
    with pytest.raises(AuditError):
        build_audit([good], subjects=SUBJECTS)


def test_every_category_and_status_is_in_vocabulary() -> None:
    # Guards against drift between the declared vocabulary and what the classifier
    # can emit.
    assert len(set(CATEGORIES)) == len(CATEGORIES)
    assert "requires_followup_mapping" in CATEGORIES
    assert set(COVERAGE_STATUSES) == {
        "covered",
        "out_of_scope",
        "unmapped_gap",
        "malformed",
    }


# ---------------------------------------------------------------------------
# Full audit against the live repo (read-only).
# ---------------------------------------------------------------------------
def test_build_coverage_audit_over_repo_covers_bound_paths() -> None:
    payload = run.build_coverage_audit()
    summary = payload["summary"]
    # All coordinator-referenced and supplemental historical paths resolve to covered.
    assert summary["totals"]["covered_coordinator_artifacts"] == 107
    assert summary["totals"]["surface_visible_artifacts"] == 103
    assert summary["totals"]["unmapped_gap_artifacts"] == 0
    # The repo is large; the audit must enumerate a substantial universe.
    assert summary["totals"]["total_discovered_artifacts"] > 1000
    # No category count is negative and they sum to the total.
    total = summary["totals"]["total_discovered_artifacts"]
    assert sum(summary["by_category"].values()) == total
    assert sum(summary["by_coverage_status"].values()) == total
    # Every inventory item uses a valid category/status.
    for item in payload["inventory"]:
        assert item["category"] in CATEGORIES
        assert item["coverage_status"] in COVERAGE_STATUSES


def test_build_coverage_audit_covers_former_known_gaps() -> None:
    payload = run.build_coverage_audit()
    inv = {i["path"]: i for i in payload["inventory"]}
    former_gap = "docs/research/PRICEONLY_SYNTHESIS_2026-06.md"
    assert inv[former_gap]["coverage_status"] == "covered"
    # The bound funding-fade conclusion is covered, not a gap.
    bound = "scratch/WP-RESEARCH-FUNDING-FADE-CONCLUDE-01/conclusion_traceability.json"
    assert inv[bound]["coverage_status"] == "covered"
