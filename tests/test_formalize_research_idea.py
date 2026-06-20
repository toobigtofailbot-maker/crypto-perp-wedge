import json
from pathlib import Path

from tools.research_workflow import formalize_research_idea as formalizer
from tools.research_workflow.validate_research_idea import validate_path


FIXTURES = Path(__file__).parent / "fixtures" / "research_ideas"


def test_json_idea_formalizes_to_valid_scratch_artifacts(tmp_path):
    report = formalizer.formalize(
        input_path=FIXTURES / "valid_research_idea_current_lab.json",
        output_dir=tmp_path,
    )

    assert report["status"] == "formalized"
    assert report["classification"] == "current_lab_testable"
    assert report["capability_mapping"]["lab_testable"] is True
    assert report["llm_assist"]["used"] is False
    assert validate_path(tmp_path / "example_research_idea.json") == []
    assert (tmp_path / "draft_workflow_parameter_space.json").exists()
    assert report["workflow_generator"]["eligible"] is True
    assert report["workflow_generator"]["invoked"] is False


def test_upgrade_dependent_idea_is_tagged_and_not_sent_to_generator(tmp_path):
    report = formalizer.formalize(
        input_path=FIXTURES / "valid_research_idea_upgrade_dependent.json",
        output_dir=tmp_path,
    )

    assert report["status"] == "formalized"
    assert report["classification"] == "upgrade_dependent_data"
    assert report["capability_mapping"]["lab_testable"] is False
    assert report["workflow_generator"]["eligible"] is False
    assert not (tmp_path / "draft_workflow_parameter_space.json").exists()


def test_invalid_idea_writes_rejection_report_but_no_research_object(tmp_path):
    report = formalizer.formalize(
        input_path=FIXTURES / "invalid_research_idea_non_causal.json",
        output_dir=tmp_path,
    )

    assert report["status"] == "rejected"
    assert report["rejection_reasons"]
    assert not (tmp_path / "example_research_idea.json").exists()
    on_disk = json.loads((tmp_path / "example_formalization_report.json").read_text(encoding="utf-8"))
    assert on_disk["status"] == "rejected"


def test_ambiguous_plain_text_is_rejected_without_search_expansion(tmp_path):
    source = tmp_path / "idea.txt"
    source.write_text("Find a profitable BTC strategy.", encoding="utf-8")

    report = formalizer.formalize(input_path=source, output_dir=tmp_path / "out")

    assert report["status"] == "rejected"
    assert any("bounded parameter" in reason for reason in report["rejection_reasons"])
    assert not (tmp_path / "out" / "example_research_idea.json").exists()


def test_sufficiently_explicit_plain_text_is_formalized_locally(tmp_path):
    source = tmp_path / "idea.txt"
    source.write_text(
        "Test BTCUSDT on 4h because temporary price pressure mean reverts. "
        "Enter long after completed-bar close crosses above SMA. "
        "Exit after price returns below SMA. "
        "SMA lookback from 20 to 40 bars. "
        "Stop if walk-forward expectancy is non-positive.",
        encoding="utf-8",
    )

    report = formalizer.formalize(
        input_path=source,
        output_dir=tmp_path / "out",
        created_at_utc="2026-06-20T00:00:00Z",
    )

    assert report["status"] == "formalized"
    payload = json.loads((tmp_path / "out" / "example_research_idea.json").read_text(encoding="utf-8"))
    assert payload["instrument_universe"]["symbols"] == ["BTCUSDT"]
    assert payload["timeframe"]["primary"] == "4h"
    assert validate_path(tmp_path / "out" / "example_research_idea.json") == []


def test_optional_workflow_generator_writes_only_under_requested_output(tmp_path):
    report = formalizer.formalize(
        input_path=FIXTURES / "valid_research_idea_current_lab.json",
        output_dir=tmp_path,
        generate_workflow_drafts=True,
    )

    assert report["workflow_generator"]["invoked"] is True
    assert report["workflow_generator"]["generated_variant_count"] == 27
    assert (tmp_path / "workflow_gen" / "draft_grid_generation_report.json").exists()


def test_formalizer_source_has_no_network_or_canonical_write_path():
    source = (formalizer.REPO_ROOT / "tools" / "research_workflow" / "formalize_research_idea.py").read_text(encoding="utf-8")
    forbidden = ["import requests", "import urllib", "import socket", "research/strategy_specs", "research/variant_manifests", "research/sweep_plans"]
    assert not any(term in source for term in forbidden)
    assert formalizer.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", formalizer.PACKAGE_ID)
