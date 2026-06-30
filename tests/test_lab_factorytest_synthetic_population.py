from __future__ import annotations

import json
from pathlib import Path

from tools.lab_factorytest.generate_synthetic_population import (
    BASELINE_ID,
    DEFAULT_ROWS,
    build_rows,
    generate,
)


def _baseline() -> dict:
    return {
        "baseline_id": BASELINE_ID,
        "expected_gate_result": "fail",
    }


def _gates() -> dict:
    return {
        "wfo_oos_gate_expected": "fail_or_insufficient",
        "robustness_mc_gate_expected": "fail_or_insufficient_or_withheld",
        "statistical_diagnostics_gate_expected": "insufficient_or_withheld_unless_real_inputs_exist",
        "candidate_eligibility_expected": "reject_by_construction",
    }


def test_rows_preserve_full_denominator_and_status_mix() -> None:
    rows = build_rows(DEFAULT_ROWS, _baseline(), _gates())

    assert len(rows) == DEFAULT_ROWS
    statuses = {row["status"] for row in rows}
    assert {"completed", "failed", "invalid", "blocked", "insufficient", "withheld"} <= statuses
    assert all(row["denominator_accounting_status"] == "retained" for row in rows)


def test_non_promotable_dominates_favorable_numeric_rows() -> None:
    rows = build_rows(DEFAULT_ROWS, _baseline(), _gates())
    favorable = [row for row in rows if row["numerically_favorable"]]

    assert favorable
    assert all(row["synthetic_metrics"]["synthetic_score"] > 0 for row in favorable)
    assert all(row["construction_payload"] is True for row in rows)
    assert all(row["non_promotable"] is True for row in rows)
    assert not any(row["candidate_eligible"] for row in rows)
    assert not any(row["promotion_eligible"] for row in rows)
    assert not any(row["paper_live_eligible"] for row in rows)
    assert not any(row["canonical_crossing_allowed"] for row in rows)
    assert not any(row["edge_claim_allowed"] for row in rows)
    assert all(row["candidate_review_expected"] == "no_candidate" for row in rows)
    assert all(row["crossing_expected"] == "reject_by_construction" for row in rows)


def test_generate_materializes_expected_scratch_outputs(tmp_path: Path) -> None:
    repo_root = Path.cwd()
    scratch_dir = tmp_path / "scratch"

    result = generate(repo_root=repo_root, scratch_dir=scratch_dir, row_count=500)

    assert result["row_count_planned"] == 500
    assert result["row_count_materialized"] == 500
    assert result["all_rows_accounted"] is True
    assert result["canonical_result_population_written"] is False
    assert result["candidate_registry_written"] is False
    assert result["real_strategy_execution"] is False

    manifest = json.loads((scratch_dir / "synthetic_population_manifest.json").read_text())
    assert manifest["strategy_family_count"] == 1
    assert manifest["baseline"]["baseline_id"] == BASELINE_ID
    assert len(manifest["rows"]) == 500

    expected_outputs = {
        "repo_truth_discovery.md",
        "synthetic_population_manifest.json",
        "synthetic_population_manifest.md",
        "denominator_accounting.json",
        "gate_outcome_summary.json",
        "non_promotable_assertions.json",
        "factorytest_result.json",
        "external_runway_usage.md",
        "validation_summary.txt",
    }
    assert expected_outputs == {path.name for path in scratch_dir.iterdir()}
