import json
from pathlib import Path

import pytest

from tools.dashboard.collector import collect_dashboard_data
from tools.dashboard.generate_static_dashboard import generate_dashboard, main
from tools.dashboard.renderer import render_dashboard
from tools.dashboard.validate_dashboard_data import validate_dashboard_data_file


FORBIDDEN_CONTROL_SNIPPETS = [
    "<button",
    "approved strategy",
    "recommended variant",
    "best variant",
    "ready for live",
    "ready for paper",
    "place order",
    "cancel order",
    "start paper run",
    "start live run",
    "approval button",
    "leaderboard",
    "winner",
    "promote",
]

NETWORK_OR_BUILD_SNIPPETS = [
    "https://",
    "http://",
    "cdn.",
    "unpkg",
    "vite",
    "react",
    "type=\"module\"",
]


def test_generator_creates_valid_dashboard_data_and_index(tmp_path):
    data_dir = tmp_path / "dashboard_data"
    output_dir = tmp_path / "dashboard_build"

    dashboard_data_path, index_path = generate_dashboard(Path("."), data_dir, output_dir)

    assert dashboard_data_path == data_dir / "dashboard_data.json"
    assert index_path == output_dir / "index.html"
    assert dashboard_data_path.exists()
    assert index_path.exists()
    assert validate_dashboard_data_file(dashboard_data_path) == []


def test_generated_dashboard_data_contains_current_d4a_facts(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    d4 = payload["pages"]["data_provenance"]["d4_slice"]

    assert d4["catalog_ref"].startswith("binance_usdtm_btcusdt_ohlcv_15m.")
    assert d4["data_slice_identity"].startswith("binance_usdtm_btcusdt_ohlcv_15m:sha256:")
    assert d4["row_count"] == 220128
    assert d4["expected_row_count"] == 220128
    assert d4["gap_facts"]["gap_count"] == 0
    assert d4["duplicate_facts"]["duplicate_group_count"] == 0


def test_index_contains_required_pages_empty_states_and_gate_phrase(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    assert "Overview" in html
    assert "Data / Provenance" in html
    assert "Gates" in html
    assert "Operator Review" in html
    assert "Results" in html
    assert html.count('class="page-section"') == 5
    assert 'href="#overview"' in html
    assert 'href="#data-provenance"' in html
    assert 'href="#gates"' in html
    assert 'href="#operator-review"' in html
    assert 'href="#results"' in html
    assert 'id="results"' in html
    assert "D5 result population RP-4492 is available for display-only Results data." in html
    assert "No paper runtime yet." in html
    assert "No live mode." in html
    assert "Dashboard displays gates; dashboard does not satisfy gates." in html


def test_index_contains_d4a_catalog_ref_and_slice_identity(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    assert "binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m" in html
    assert "binance_usdtm_btcusdt_ohlcv_15m:sha256:" in html


def test_renderer_consumes_dashboard_data_without_source_artifact_paths(tmp_path):
    payload = collect_dashboard_data(Path("."))
    output_dir = tmp_path / "build"

    index_path = render_dashboard(payload, output_dir)

    assert index_path.exists()
    assert (output_dir / "assets" / "dashboard.css").exists()
    assert (output_dir / "assets" / "dashboard.js").exists()


def test_invalid_dashboard_data_blocks_rendering(monkeypatch, tmp_path):
    payload = collect_dashboard_data(Path("."))
    payload["pages"]["overview"]["status"] = "OK"
    called = False

    def fake_collect(_repo_root):
        return payload

    def fake_render(_data, _output_dir):
        nonlocal called
        called = True
        return tmp_path / "build" / "index.html"

    monkeypatch.setattr("tools.dashboard.generate_static_dashboard.collect_dashboard_data", fake_collect)
    monkeypatch.setattr("tools.dashboard.generate_static_dashboard.render_dashboard", fake_render)

    with pytest.raises(SystemExit) as exc:
        generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")

    assert exc.value.code == 1
    assert called is False
    assert not (tmp_path / "build" / "index.html").exists()


def test_generated_output_paths_are_local_and_gitignored(tmp_path):
    dashboard_data_path, index_path = generate_dashboard(
        Path("."),
        tmp_path / "dashboard_data",
        tmp_path / "dashboard_build",
    )

    assert "dashboard_data" in dashboard_data_path.parts
    assert "dashboard_build" in index_path.parts
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "/dashboard_build/" in gitignore
    assert "/dashboard_data/" in gitignore


def test_no_forbidden_authority_controls_are_rendered(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8").lower()

    for snippet in FORBIDDEN_CONTROL_SNIPPETS:
        assert snippet not in html


def test_static_assets_are_local_only_without_network_or_build_references(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8").lower()
    css = (index_path.parent / "assets" / "dashboard.css").read_text(encoding="utf-8").lower()
    js = (index_path.parent / "assets" / "dashboard.js").read_text(encoding="utf-8").lower()

    assert 'href="assets/dashboard.css"' in html
    assert 'src="assets/dashboard.js"' in html
    for snippet in NETWORK_OR_BUILD_SNIPPETS:
        assert snippet not in html
        assert snippet not in css
        assert snippet not in js


def test_polish_structure_and_inert_filters_render(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")
    js = (index_path.parent / "assets" / "dashboard.js").read_text(encoding="utf-8")

    assert 'class="status-summary"' in html
    assert 'class="slice-grid"' in html
    assert 'class="table-wrap"' in html
    assert 'data-filter-target="artifact-table"' in html
    assert 'data-filter-target="gate-table"' in html
    assert 'class="filter-row"' in html
    assert "query !== \"\"" in js


def test_cli_prints_generated_paths(tmp_path, capsys):
    rc = main(
        [
            "--repo-root",
            ".",
            "--data-dir",
            str(tmp_path / "dashboard_data"),
            "--output-dir",
            str(tmp_path / "dashboard_build"),
        ]
    )

    assert rc == 0
    out = capsys.readouterr().out
    assert "dashboard_data:" in out
    assert "dashboard_html:" in out


# ---------------------------------------------------------------------------
# WP-F5B: Results collector tests
# ---------------------------------------------------------------------------

def test_collect_includes_results_page_when_rp4492_present():
    from tools.dashboard.collector import collect_dashboard_data
    payload = collect_dashboard_data(Path("."))
    assert "results" in payload["pages"]
    results = payload["pages"]["results"]
    assert results is not None
    assert results["status"] == "PASS"


def test_generated_dashboard_data_includes_valid_results_page(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    errors = validate_dashboard_data_file(dashboard_data_path)
    assert errors == []

    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    results = payload["pages"]["results"]

    assert results["result_population"]["result_population_id"] == "RP-4492"
    assert results["complete_population"]["committed_denominator"] == 7
    assert results["complete_population"]["result_row_count"] == 7
    assert results["complete_population"]["outcome_counts_sum"] == 7
    assert len(results["variant_table"]["rows"]) == 7
    assert [r["variant_id"] for r in results["variant_table"]["rows"]] == [
        "VAR-000001", "VAR-000002", "VAR-000003",
        "VAR-000004", "VAR-000005", "VAR-000006", "VAR-000007",
    ]
    assert results["variant_table"]["variant_order_policy"] == "variant_id_ascending_only_not_quality_order"
    assert results["descriptive_summary"]["variant_order_policy"] == "variant_id_ascending_only_not_quality_order"

    nan = results["non_authority_notes"]
    assert nan["no_ranking_as_authority"] is True
    assert nan["no_recommendation"] is True
    assert nan["no_readiness"] is True
    assert nan["no_promotion"] is True
    assert nan["no_execution"] is True


def test_results_page_has_no_forbidden_authority_keys_or_values(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    results = payload["pages"]["results"]
    results_text = json.dumps(results).lower()

    # Exact authority/action terms that must not appear as standalone values or key names
    # (not substring checks — checked as distinct tokens to avoid false positives from
    #  negation fields like "no_readiness" or descriptive caveats).
    forbidden_substrings = [
        "best_variant", "recommended_variant", "approved_strategy",
        "ready_for_live", "ready_for_paper", "leaderboard",
        "promote_to_paper", "live_enabled",
    ]
    for term in forbidden_substrings:
        assert term not in results_text, f"Forbidden term {term!r} found in results page"

    # Validator already catches FORBIDDEN_AUTHORITY_KEYS; confirm no validator errors
    from tools.dashboard.validate_dashboard_data import validate_dashboard_data_file
    assert validate_dashboard_data_file(dashboard_data_path) == []


def test_results_overview_no_stale_empty_state_warning_when_rp4492_present(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    overview = payload["pages"]["overview"]

    warning_ids = [w["warning_id"] for w in overview["warnings"]]
    assert "no-d5-results" not in warning_ids

    rp_state = overview["latest_result_population_empty_state"]
    assert rp_state["status"] == "PASS"
    expected_msg = "D5 result population RP-4492 is available for display-only Results data."
    assert rp_state["message"] == expected_msg
    raw = json.dumps(payload)
    assert "No D5 result population yet." not in raw


def test_results_page_now_renders_in_html(tmp_path):
    # F5C: renderer now includes Results page (replaces F5B's renderer-unchanged assertion)
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")
    assert html.count('class="page-section"') == 5
    assert 'id="results"' in html
    assert 'href="#results"' in html


def test_generator_validates_before_rendering_still_passes(tmp_path):
    dashboard_data_path, index_path = generate_dashboard(
        Path("."), tmp_path / "data", tmp_path / "build"
    )
    assert validate_dashboard_data_file(dashboard_data_path) == []
    assert index_path.exists()


def test_generated_output_gitignore_patterns_cover_dashboard_dirs():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "/dashboard_build/" in gitignore
    assert "/dashboard_data/" in gitignore


# ---------------------------------------------------------------------------
# WP-F5C: Results renderer tests
# ---------------------------------------------------------------------------

def test_results_page_renders_rp4492_and_variant_table(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    assert "RP-4492" in html
    assert "variant_id_ascending_only_not_quality_order" in html
    for var_id in ["VAR-000001", "VAR-000002", "VAR-000003",
                   "VAR-000004", "VAR-000005", "VAR-000006", "VAR-000007"]:
        assert var_id in html

    # Variant IDs must appear in ascending order
    positions = [html.index(v) for v in
                 ["VAR-000001", "VAR-000002", "VAR-000003",
                  "VAR-000004", "VAR-000005", "VAR-000006", "VAR-000007"]]
    assert positions == sorted(positions)

    assert "Rows are displayed in variant ID order only" in html


def test_results_page_no_authority_banner(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html_lower = index_path.read_text(encoding="utf-8").lower()

    # Required non-authority declarations
    assert "no ranking authority" in html_lower
    assert "no recommendation" in html_lower
    assert "no readiness authority" in html_lower
    assert "no promotion authority" in html_lower
    assert "no execution authority" in html_lower


def test_results_page_no_extended_forbidden_snippets(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html_lower = index_path.read_text(encoding="utf-8").lower()

    # All FORBIDDEN_CONTROL_SNIPPETS including F5C additions
    for snippet in FORBIDDEN_CONTROL_SNIPPETS:
        assert snippet not in html_lower, f"Forbidden snippet found in HTML: {snippet!r}"


def test_results_page_variant_ids_in_ascending_order(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    ids = ["VAR-000001", "VAR-000002", "VAR-000003",
           "VAR-000004", "VAR-000005", "VAR-000006", "VAR-000007"]
    positions = [html.index(var_id) for var_id in ids]
    assert positions == sorted(positions), "Variant IDs are not in ascending order in HTML"


def test_results_absent_renders_gracefully(tmp_path):
    # renderer must not crash if pages.results is absent
    payload = collect_dashboard_data(Path("."))
    payload["pages"].pop("results", None)

    index_path = render_dashboard(payload, tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    assert index_path.exists()
    assert 'id="results"' in html
    assert "Results data is not available" in html
    # Absent state must not imply failure, readiness, or approval
    assert "does not imply failure, readiness, or approval" in html


def test_results_renderer_uses_supplied_payload_only(tmp_path):
    # Renderer takes the data dict directly and must not re-read source artifacts
    payload = collect_dashboard_data(Path("."))
    index_path = render_dashboard(payload, tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")

    assert index_path.exists()
    assert "RP-4492" in html
    assert 'id="results"' in html


# ---------------------------------------------------------------------------
# WP-LAB-RESULTS-SURFACE-01: lab registry dashboard surface
# ---------------------------------------------------------------------------

def test_generated_dashboard_data_includes_lab_registry(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    registry = payload["pages"]["results"]["lab_registry"]

    assert registry["schema_version"] == "lab_run_registry.v1"
    assert registry["record_count"] == 8
    assert registry["run_order_policy"] == "run_id_ascending_only_not_quality_order"
    assert [record["run_id"] for record in registry["records"]] == sorted(
        record["run_id"] for record in registry["records"]
    )
    assert registry["non_authority_notes"]["no_ranking_as_authority"] is True
    assert registry["non_authority_notes"]["no_execution"] is True


def test_lab_registry_renders_without_quality_order_or_authority(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")
    html_lower = html.lower()

    assert "Lab Run / Result Registry" in html
    assert "Runs are displayed in run ID order only" in html
    assert "RP-7520" in html
    assert "advisory_analytics_report.json" in html
    assert "seeded_advisory_mc_report.json" in html
    assert "vectorbt_triage_report.json" in html
    assert "quality ranking" in html_lower
    assert "leaderboard" not in html_lower


# ---------------------------------------------------------------------------
# WP-LAB-DASHBOARD-EXPANSION-01: operator review surface
# ---------------------------------------------------------------------------

def test_generated_dashboard_data_includes_operator_review_summary(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    payload = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
    review = payload["pages"]["operator_review"]

    assert review["status"] == "BLOCKED"
    assert review["active_and_recent_jobs"]["status"] == "NOT_AVAILABLE"
    assert review["active_and_recent_jobs"]["active_count"] is None
    assert review["active_and_recent_jobs"]["recent_job_count"] == 8
    assert review["population_summary"]["population_count"] == 8
    assert review["population_summary"]["complete_population_count"] == 8
    assert review["population_summary"]["committed_denominator"] == 66
    assert review["population_summary"]["result_row_count"] == 66
    assert review["population_summary"]["outcome_counts"] == {
        "successful": 66,
        "failed": 0,
        "invalid": 0,
        "excluded": 0,
        "errored": 0,
        "aborted": 0,
        "data_unavailable": 0,
        "unknown": 0,
    }


def test_operator_review_exposes_uncertainty_and_manual_posture(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    review = json.loads(dashboard_data_path.read_text(encoding="utf-8"))["pages"]["operator_review"]

    assert review["evidence_summary"]["walkforward_oos"]["available_count"] == 0
    assert review["evidence_summary"]["walkforward_oos"]["unavailable_count"] == 8
    assert review["evidence_summary"]["robustness"]["available_count"] == 1
    assert review["evidence_summary"]["robustness"]["unavailable_count"] == 7
    assert review["lifecycle_summary"]["state"] == "not_available"
    assert review["approval_summary"]["state"] == "manual_approval_required"
    assert review["approval_summary"]["pending_count"] is None
    assert review["non_authority_notes"]["not_ranking_authority"] is True
    assert review["non_authority_notes"]["not_approval"] is True
    assert review["non_authority_notes"]["not_execution"] is True


def test_operator_candidate_reviews_are_stable_and_include_caveats(tmp_path):
    dashboard_data_path, _ = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    candidates = json.loads(dashboard_data_path.read_text(encoding="utf-8"))["pages"]["operator_review"]["candidate_reviews"]

    assert len(candidates) == 8
    assert [item["review_id"] for item in candidates] == sorted(item["review_id"] for item in candidates)
    assert all(item["caveats"] for item in candidates)
    assert all(item["candidate_lifecycle_state"] == "not_available" for item in candidates)
    assert all(item["approval_state"] == "manual_approval_required" for item in candidates)
    assert all(item["evidence_links"] for item in candidates)


def test_operator_review_renders_blockers_without_controls(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")
    html_lower = html.lower()

    assert 'id="operator-review"' in html
    assert "Candidates with Caveats" in html
    assert "Blockers and Missing Prerequisites" in html
    assert "Blocked by OOS / walk-forward not run" in html
    assert "Blocked by robustness not run" in html
    assert "Blocked by funding realism" in html
    assert "Manual approval required" in html
    assert "not a ranking" in html_lower
    assert "<button" not in html_lower
    assert "deploy now" not in html_lower
    assert "safe to trade" not in html_lower
    assert "recommended variant" not in html_lower
    assert "best strategy" not in html_lower
