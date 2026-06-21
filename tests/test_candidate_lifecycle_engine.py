from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.candidate_lifecycle.lifecycle_engine import (
    FORBIDDEN_PACKET_PHRASES,
    REQUIRED_NON_AUTHORITY_FLAGS,
    build_lifecycle_report,
    build_outputs,
)


FIXTURES = Path(__file__).parent / "fixtures" / "candidate_lifecycle_engine"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_candidate_input_emits_human_gated_packet_state() -> None:
    report = build_lifecycle_report(_load_fixture("valid_candidate_inputs.json"))

    candidate = report["candidate_reports"][0]
    assert report["scratch_only"] is True
    assert report["canonical_authority"] is False
    assert report["aggregate"]["canonical_evidence_mutations"] == 0
    assert report["aggregate"]["paper_live_actions"] == 0
    assert report["aggregate"]["auto_promotions"] == 0
    assert candidate["pending_state"] == "human_approval_required"
    assert candidate["requested_transition"]["transition_edge"] == "research_concluded->paper_eligible"
    assert candidate["blockers"] == []
    assert "robustness_report_ref" not in candidate["missing_evidence"]
    assert candidate["non_authority_flags"] == REQUIRED_NON_AUTHORITY_FLAGS


def test_auto_promotion_input_is_blocked_without_authority() -> None:
    report = build_lifecycle_report(_load_fixture("invalid_auto_promotion.json"))

    candidate = report["candidate_reports"][0]
    assert candidate["pending_state"] == "blocked"
    assert any("auto_promote=true" in blocker for blocker in candidate["blockers"])
    assert any("mark_ready_for_live=true" in blocker for blocker in candidate["blockers"])
    assert any("forbidden lifecycle target" in blocker for blocker in candidate["blockers"])
    assert report["aggregate"]["auto_promotions"] == 0
    assert report["aggregate"]["paper_live_actions"] == 0


def test_missing_evidence_becomes_blocker() -> None:
    report = build_lifecycle_report(_load_fixture("missing_evidence_blockers.json"))

    candidate = report["candidate_reports"][0]
    assert candidate["pending_state"] == "blocked"
    assert "result_population_ref" in candidate["missing_evidence"]
    assert "walkforward_run_ref" in candidate["missing_evidence"]
    assert "dashboard_review_ref" in candidate["missing_evidence"]
    assert any("missing required evidence: result_population_ref" in blocker for blocker in candidate["blockers"])


def test_review_packet_avoids_forbidden_authority_phrases() -> None:
    outputs = build_outputs(FIXTURES / "valid_candidate_inputs.json")

    lowered = outputs.packet_markdown.lower()
    for phrase in FORBIDDEN_PACKET_PHRASES:
        assert phrase not in lowered
    assert "human_gated" in outputs.packet_markdown
    assert "not_execution_authority" in outputs.packet_markdown


def test_cli_writes_report_packet_and_provenance(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.candidate_lifecycle.lifecycle_engine",
            "--input",
            str(FIXTURES / "valid_candidate_inputs.json"),
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "candidate_lifecycle_report.json").exists()
    assert (tmp_path / "candidate_review_packet.md").exists()
    assert (tmp_path / "provenance.json").exists()
    report = json.loads((tmp_path / "candidate_lifecycle_report.json").read_text(encoding="utf-8"))
    provenance = json.loads((tmp_path / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["report_identity_hash"] == report["report_identity_hash"]
