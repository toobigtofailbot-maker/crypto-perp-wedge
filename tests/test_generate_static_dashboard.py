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
    assert html.count('class="page-section"') == 3
    assert 'href="#overview"' in html
    assert 'href="#data-provenance"' in html
    assert 'href="#gates"' in html
    assert "No D5 result population yet." in html
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


def test_results_renderer_unchanged_no_results_page_in_html(tmp_path):
    _, index_path = generate_dashboard(Path("."), tmp_path / "data", tmp_path / "build")
    html = index_path.read_text(encoding="utf-8")
    assert html.count('class="page-section"') == 3


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
