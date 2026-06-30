from __future__ import annotations

from pathlib import Path

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
