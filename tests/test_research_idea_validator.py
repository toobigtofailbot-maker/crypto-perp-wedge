import copy
import json
from pathlib import Path

from tools.research_workflow.validate_research_idea import validate_path, validate_payload


FIXTURES = Path(__file__).parent / "fixtures" / "research_ideas"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_current_lab_fixture_is_valid():
    assert validate_path(FIXTURES / "valid_research_idea_current_lab.json") == []


def test_upgrade_dependent_fixture_is_valid():
    assert validate_path(FIXTURES / "valid_research_idea_upgrade_dependent.json") == []


def test_unbounded_search_is_rejected_early():
    errors = validate_path(FIXTURES / "invalid_research_idea_unbounded_search.json")
    assert any("unbounded_search" in error for error in errors)
    assert any("magic_optimizer" in error for error in errors)
    assert any("early-rejection outcome" in error for error in errors)


def test_non_causal_and_same_bar_language_is_rejected():
    errors = validate_path(FIXTURES / "invalid_research_idea_non_causal.json")
    assert any("future_lookahead" in error for error in errors)
    assert any("same_bar_leakage" in error for error in errors)


def test_parameter_values_must_stay_inside_bounds():
    payload = _load("valid_research_idea_current_lab.json")
    payload["parameter_ranges"][0]["values"].append(101)
    errors = validate_payload(payload)
    assert any("outside declared bounds" in error for error in errors)


def test_parameter_grid_has_hard_expansion_bound():
    payload = _load("valid_research_idea_current_lab.json")
    payload["parameter_ranges"] = []
    for index in range(5):
        parameter = copy.deepcopy(_load("valid_research_idea_current_lab.json")["parameter_ranges"][0])
        parameter["name"] = f"parameter_{index}"
        parameter["minimum"] = 1
        parameter["maximum"] = 4
        parameter["values"] = [1, 2, 3, 4]
        payload["parameter_ranges"].append(parameter)
    errors = validate_payload(payload)
    assert any("1024 variants" in error for error in errors)


def test_non_authority_flags_are_fail_closed():
    payload = _load("valid_research_idea_current_lab.json")
    payload["non_authority_flags"]["not_canonical"] = False
    errors = validate_payload(payload)
    assert any("not_canonical" in error for error in errors)


def test_free_form_executable_code_is_rejected():
    payload = _load("valid_research_idea_current_lab.json")
    payload["entry_exit_concept"]["entry"] = "```python\ndef signal(frame): return frame.close > 0\n```"
    errors = validate_payload(payload)
    assert any("executable_code" in error for error in errors)
