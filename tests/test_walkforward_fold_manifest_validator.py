import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_walkforward_fold_manifest import (
    DEFAULT_SCHEMA_PATH,
    main,
    validate_walkforward_fold_manifests,
)


FIXTURES = Path(__file__).parent / "fixtures" / "walkforward"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_valid_fixture_matches_schema_and_semantic_validator():
    payload = _load_json(FIXTURES / "valid_walkforward_fold_manifest.json")
    schema = _load_json(DEFAULT_SCHEMA_PATH)
    schema_errors = list(Draft7Validator(schema).iter_errors(payload))

    assert schema_errors == []
    assert validate_walkforward_fold_manifests(
        explicit_paths=[FIXTURES / "valid_walkforward_fold_manifest.json"]
    ) == []


def test_validator_rejects_selection_evaluation_overlap():
    errors = validate_walkforward_fold_manifests(
        explicit_paths=[FIXTURES / "invalid_walkforward_fold_manifest_overlap.json"]
    )

    assert any("evaluation must not overlap selection" in error for error in errors)


def test_validator_rejects_known_count_denominator_shrinkage():
    errors = validate_walkforward_fold_manifests(
        explicit_paths=[FIXTURES / "invalid_walkforward_fold_manifest_counts.json"]
    )

    assert any("known outcome counts must sum to declared_variant_count" in error for error in errors)


def test_validator_rejects_authority_like_keys(tmp_path):
    payload = _load_json(FIXTURES / "valid_walkforward_fold_manifest.json")
    payload["folds"][0]["lineage_refs"][0]["promotion"] = "forbidden"
    path = tmp_path / "bad.walkforward_fold_manifest.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    errors = validate_walkforward_fold_manifests(explicit_paths=[path])

    assert any("Additional properties are not allowed" in error for error in errors)


def test_cli_accepts_explicit_valid_fixture(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate_walkforward_fold_manifest",
            str(FIXTURES / "valid_walkforward_fold_manifest.json"),
        ],
    )

    assert main() == 0
    assert "OK: walk-forward fold manifests validate" in capsys.readouterr().out
