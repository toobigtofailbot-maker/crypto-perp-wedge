from __future__ import annotations

import json
from pathlib import Path

from tools.lab_state.resolver import REPO_ROOT
from tools.lab_visual_cockpit.run import build, scan_read_only_controls


def test_lab_visual_cockpit_builds_static_artifacts(tmp_path: Path) -> None:
    result = build(tmp_path, write_repo_evidence=False)
    data = result["data"]

    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "cockpit_data.json").exists()
    assert (tmp_path / "cockpit.md").exists()
    assert data["surface_kind"] == "read_only_static_visual_cockpit"
    assert data["authority"]["read_only"] is True
    assert data["authority"]["network_fetch_added"] is False
    assert data["candidate_review_funnel"]["winner_only_view"] is False
    assert data["candidate_review_funnel"]["candidate_ready"] == 0


def test_generated_html_has_no_forbidden_control_behavior(tmp_path: Path) -> None:
    result = build(tmp_path, write_repo_evidence=False)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    scan = scan_read_only_controls(html)

    assert scan["overall_pass"] is True
    assert "<form" not in html.lower()
    assert "fetch(" not in html
    assert "XMLHttpRequest" not in html
    assert "WebSocket" not in html
    assert "EventSource" not in html
    assert "navigator.sendBeacon" not in html
    assert "src=\"http://" not in html
    assert "src=\"https://" not in html
    assert "<button" not in html.lower()


def test_missing_metrics_are_explicit_not_fabricated(tmp_path: Path) -> None:
    result = build(tmp_path, write_repo_evidence=False)
    policy = result["data"]["missing_metric_policy"]
    html = (tmp_path / "index.html").read_text(encoding="utf-8").lower()

    assert policy["missing_equity_curve"] == "rendered_unavailable_not_present"
    assert policy["missing_drawdown_curve"] == "rendered_unavailable_not_present"
    assert policy["missing_returns_distribution"] == "rendered_unavailable_not_present"
    assert policy["missing_mc_robustness_data"] == "rendered_withheld_unavailable"
    assert policy["no_fabricated_metrics"] is True
    assert policy["placeholder_fake_performance_numbers"] is False
    assert "unavailable / not present" in html
    assert "withheld/unavailable" in html


def test_capability_completion_uses_side12_capability_rows(tmp_path: Path) -> None:
    result = build(tmp_path, write_repo_evidence=False)
    cards = result["data"]["capability_completion"]["cards"]
    groups = result["data"]["capability_completion"]["groups"]
    source_map = json.loads(
        (REPO_ROOT / "scratch/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01/side12_operating_readiness_map.json").read_text(
            encoding="utf-8"
        )
    )

    card_ids = [card["capability_id"] for card in cards]
    by_id = {card["capability_id"]: card for card in cards}

    assert len(cards) == 23
    assert card_ids == list(range(1, 24))
    assert not {"base_commit", "capabilities", "package", "status_counts"}.intersection({str(card_id) for card_id in card_ids})

    assert by_id[14]["capability_name"] == "Dashboard coverage"
    assert by_id[14]["source_status"] == "acceptance_tested_by_event_tape"
    assert by_id[14]["status_bucket"] == "acceptance_tested_by_event_tape"
    assert by_id[14]["operating_readiness_acceptance_tested"] is True

    assert by_id[21]["source_status"] == "needs_real_GO_candidate"
    assert by_id[21]["requires_real_GO_candidate"] is True

    assert by_id[23]["source_status"] == "GO_gated_protected"
    assert by_id[23]["paper_live_GO_gated"] is True
    assert by_id[23]["authority_created_here"] is False

    assert groups == source_map["status_counts"]
