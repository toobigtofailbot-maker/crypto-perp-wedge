import copy
import json
from pathlib import Path

from jsonschema import Draft7Validator

import pytest

from tests.test_validate_result_populations import _write_valid_fixture
from tools.research_replay.normalization import (
    CONTRACT_VERSION,
    ReplayNormalizationError,
    build_contract_summary,
    compare_result_populations,
    normalized_stable_hash,
)


def _fixture_payload(tmp_path: Path) -> dict:
    *_, result_population, _, _, _, _ = _write_valid_fixture(tmp_path)
    return result_population


def test_identical_replay_inputs_produce_identical_normalized_hash(tmp_path):
    payload = _fixture_payload(tmp_path)
    replay = copy.deepcopy(payload)
    replay["audit_envelope"]["created_at"] = "2030-01-01T00:00:00Z"
    replay["validation_summary"]["validation_timestamp"] = "2030-01-01T00:00:00Z"
    replay["append_only_ledger"]["events"][0]["event_timestamp"] = "2030-01-01T00:00:00Z"

    assert normalized_stable_hash(payload, repo_root=tmp_path) == normalized_stable_hash(
        replay,
        repo_root=tmp_path,
    )


def test_changed_metric_changes_normalized_hash(tmp_path):
    payload = _fixture_payload(tmp_path)
    changed = copy.deepcopy(payload)
    changed["variant_result_rows"][0]["metrics"]["pnl"] += 1.0

    assert normalized_stable_hash(payload, repo_root=tmp_path) != normalized_stable_hash(
        changed,
        repo_root=tmp_path,
    )


def test_changed_denominator_changes_normalized_hash(tmp_path):
    payload = _fixture_payload(tmp_path)
    changed = copy.deepcopy(payload)
    changed["committed_denominator_snapshot"]["committed_denominator"] += 1

    assert normalized_stable_hash(payload, repo_root=tmp_path) != normalized_stable_hash(
        changed,
        repo_root=tmp_path,
    )


def test_changed_parent_identity_hashes_change_normalized_hash(tmp_path):
    payload = _fixture_payload(tmp_path)

    for object_name, field_name in (
        ("parent_strategy_spec", "strategy_spec_hash"),
        ("parent_variant_manifest", "manifest_hash"),
        ("parent_sweep_plan", "sweep_plan_identity_hash"),
    ):
        changed = copy.deepcopy(payload)
        changed[object_name][field_name] = "sha256:" + "9" * 64

        assert normalized_stable_hash(payload, repo_root=tmp_path) != normalized_stable_hash(
            changed,
            repo_root=tmp_path,
        )


def test_path_portable_normalization_does_not_hide_semantic_path_difference(tmp_path):
    payload = _fixture_payload(tmp_path)
    absolute = copy.deepcopy(payload)
    relative = copy.deepcopy(payload)
    different = copy.deepcopy(payload)

    rel_ref = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    absolute["parent_strategy_spec"]["strategy_spec_ref"] = str(tmp_path / rel_ref)
    relative["parent_strategy_spec"]["strategy_spec_ref"] = rel_ref
    different["parent_strategy_spec"]["strategy_spec_ref"] = (
        "research/strategy_specs/STRAT-SPEC-9999.strategy_spec.json"
    )

    assert normalized_stable_hash(absolute, repo_root=tmp_path) == normalized_stable_hash(
        relative,
        repo_root=tmp_path,
    )
    assert normalized_stable_hash(relative, repo_root=tmp_path) != normalized_stable_hash(
        different,
        repo_root=tmp_path,
    )


def test_repo_root_absolute_path_matches_relative_path(tmp_path):
    payload = _fixture_payload(tmp_path)
    absolute = copy.deepcopy(payload)
    relative = copy.deepcopy(payload)

    rel_ref = "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    absolute["parent_strategy_spec"]["strategy_spec_ref"] = str(tmp_path / rel_ref)
    relative["parent_strategy_spec"]["strategy_spec_ref"] = rel_ref

    assert normalized_stable_hash(absolute, repo_root=tmp_path) == normalized_stable_hash(
        relative,
        repo_root=tmp_path,
    )


def test_external_absolute_paths_fail_closed(tmp_path):
    payload = _fixture_payload(tmp_path)
    changed = copy.deepcopy(payload)
    changed["parent_strategy_spec"]["strategy_spec_ref"] = (
        "C:\\outside-repo\\strategy_spec.json"
    )

    with pytest.raises(ReplayNormalizationError):
        normalized_stable_hash(changed, repo_root=tmp_path)


def test_non_object_variant_result_row_fails_closed(tmp_path):
    payload = _fixture_payload(tmp_path)
    payload["variant_result_rows"].append("malformed-row")

    with pytest.raises(ReplayNormalizationError):
        normalized_stable_hash(payload, repo_root=tmp_path)


def test_contract_summary_validates_against_owned_schema(tmp_path):
    payload = _fixture_payload(tmp_path)
    summary = build_contract_summary(payload, repo_root=tmp_path)
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "tools"
        / "research_replay"
        / "replay_normalization_contract.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    errors = sorted(Draft7Validator(schema).iter_errors(summary), key=lambda err: list(err.path))

    assert errors == []
    assert summary["contract_version"] == CONTRACT_VERSION
    assert summary["normalized_payload"]["trial_count"] == 2
    assert summary["normalized_payload"]["variant_ids"] == ["VAR-000001", "VAR-000002"]


def test_compare_result_populations_reports_replay_invariant_fields(tmp_path):
    payload = _fixture_payload(tmp_path)
    replay = copy.deepcopy(payload)

    comparison = compare_result_populations(payload, replay, repo_root=tmp_path)

    assert comparison["normalized_stable_hash_match"] is True
    assert all(comparison["matched_fields"].values())


def test_pr563_scratch_populations_are_normalizable():
    root = Path(__file__).resolve().parents[1]
    fixed_path = (
        root
        / "scratch"
        / "WP-RESEARCH-FUNDING-CARRY-02"
        / "outputs"
        / "813c51adc1879144"
        / "fixed_max_hold_only"
        / "runner_artifacts"
        / "RP-2009.result_population.json"
    )
    midline_path = (
        root
        / "scratch"
        / "WP-RESEARCH-FUNDING-CARRY-02"
        / "outputs"
        / "813c51adc1879144"
        / "midline_reversion_or_max_hold"
        / "runner_artifacts"
        / "RP-7592.result_population.json"
    )

    fixed = build_contract_summary(fixed_path, repo_root=root)
    midline = build_contract_summary(midline_path, repo_root=root)

    assert fixed["source"]["result_population_id"] == "RP-2009"
    assert midline["source"]["result_population_id"] == "RP-7592"
    assert fixed["normalized_payload"]["trial_count"] == 18
    assert midline["normalized_payload"]["trial_count"] == 18
    assert fixed["normalized_stable_hash"] != midline["normalized_stable_hash"]
