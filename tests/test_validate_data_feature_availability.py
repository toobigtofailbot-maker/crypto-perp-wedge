import copy
import json
import sys

from jsonschema import Draft7Validator

from tools.registry.validate_data_feature_availability import (
    CURRENT_COMPILER_FEATURES,
    DEFAULT_CATALOG_PATH,
    DEFAULT_SCHEMA_PATH,
    TIMESTAMP_DERIVED_FEATURES,
    load_json,
    main,
    validate_catalog_payload,
    validate_data_feature_availability,
)
from tools.research_query.query_layer import init_duckdb, list_views, run_named_view


def test_availability_schema_and_mapping_validate():
    Draft7Validator.check_schema(load_json(DEFAULT_SCHEMA_PATH))
    assert validate_data_feature_availability() == []


def test_all_current_compiler_data_derived_refs_have_labels():
    catalog = load_json(DEFAULT_CATALOG_PATH)
    labeled = {
        entry["feature_name"]
        for entry in catalog["entries"]
        if entry["compiler_visible"]
    }
    assert labeled == CURRENT_COMPILER_FEATURES


def test_timestamp_fields_are_bar_derived_and_full_history_if_bars_exist():
    catalog = load_json(DEFAULT_CATALOG_PATH)
    timestamp_entries = {
        entry["feature_name"]: entry
        for entry in catalog["entries"]
        if entry["feature_name"] in TIMESTAMP_DERIVED_FEATURES
    }
    assert set(timestamp_entries) == TIMESTAMP_DERIVED_FEATURES
    assert all(
        entry["source_class"] == "DERIVED_FROM_BAR_TIMESTAMP"
        and entry["coverage_class"] == "FULL_HISTORY_PUBLIC_ARCHIVE"
        and entry["canonical_full_history_allowed"] == "conditional"
        and "bars exist" in entry["history_limitation"].lower()
        for entry in timestamp_entries.values()
    )


def test_open_interest_never_uses_trade_archives_or_full_history_public_archive():
    catalog = load_json(DEFAULT_CATALOG_PATH)
    oi_entries = [
        entry
        for entry in catalog["entries"]
        if entry["feature_name"] in {"open_interest", "open_interest_value"}
    ]
    assert oi_entries
    assert all(entry["coverage_class"] != "FULL_HISTORY_PUBLIC_ARCHIVE" for entry in oi_entries)
    assert all(entry["source_class"] != "PUBLIC_TRADE_ARCHIVE_DERIVATION" for entry in oi_entries)


def test_taker_rest_is_recent_only_and_archive_derivation_is_conditional_full_history():
    catalog = load_json(DEFAULT_CATALOG_PATH)
    entries = catalog["entries"]
    for feature in {"taker_buy_sell_ratio", "taker_buy_volume", "taker_sell_volume"}:
        feature_entries = [entry for entry in entries if entry["feature_name"] == feature]
        assert any(
            entry["source_class"] == "PUBLIC_REST_TAKER_RATIO"
            and entry["coverage_class"] == "RECENT_ONLY_PUBLIC_REST"
            and entry["canonical_full_history_allowed"] == "no"
            for entry in feature_entries
        )
        assert any(
            entry["source_class"] == "PUBLIC_TRADE_ARCHIVE_DERIVATION"
            and entry["coverage_class"] == "FULL_HISTORY_PUBLIC_ARCHIVE"
            and entry["canonical_full_history_allowed"] == "conditional"
            for entry in feature_entries
        )


def test_unknown_compiler_visible_feature_label_fails_closed():
    catalog = copy.deepcopy(load_json(DEFAULT_CATALOG_PATH))
    catalog["entries"].append(
        {
            "feature_name": "unknown_feature",
            "compiler_visible": True,
            "coverage_class": "UNKNOWN_OR_BLOCKED",
            "source_class": "UNKNOWN_SOURCE",
            "history_limitation": "Unknown.",
            "canonical_full_history_allowed": "no",
            "requires_vendor_or_captured_data": True,
            "conditions": [],
            "notes": "Blocked.",
        }
    )
    assert any("unknown features marked compiler_visible" in error for error in validate_catalog_payload(catalog))


def test_query_view_lists_availability_labels():
    connection = init_duckdb()
    assert "v_data_feature_availability" in list_views(connection)
    rows = run_named_view(connection, "v_data_feature_availability")
    assert rows
    assert {row["feature_name"] for row in rows} >= CURRENT_COMPILER_FEATURES
    open_interest = next(row for row in rows if row["feature_name"] == "open_interest")
    assert open_interest["coverage_class"] == "PUBLIC_SNAPSHOT_ONLY"
    assert open_interest["canonical_full_history_allowed"] == "no"


def test_cli_passes_for_committed_catalog(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_data_feature_availability"])
    assert main() == 0
    assert "OK:" in capsys.readouterr().out
