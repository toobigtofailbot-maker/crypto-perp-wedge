import json
import re
from pathlib import Path

import pytest

from tools.research_workflow import draft_grid_generator as generator


def _write_parameter_space(path: Path, payload: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload or generator.default_parameter_space(), indent=2),
        encoding="utf-8",
    )
    return path


def test_draft_labels_match_package_contract():
    assert generator.DRAFT_LABELS == [
        "DRAFT WORKFLOW OUTPUT",
        "NOT CANONICAL PREREGISTRATION",
        "NOT CANDIDATE EVIDENCE",
        "NOT SCREEN-GATE OR PROMOTION AUTHORITY",
        "VALIDATED ONLY AGAINST STRUCTURAL REPO VALIDATORS",
        "NOT PAPER / LIVE / RUNTIME AUTHORITY",
    ]


def test_default_parameter_space_expands_to_stable_draft_variants(tmp_path):
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json")

    first = generator.build_artifacts(parameter_space)
    second = generator.build_artifacts(parameter_space)

    assert first == second
    _, parent_spec, manifest, sweep = first
    assert parent_spec["strategy_spec_id"] == "STRAT-SPEC-9101"
    assert manifest["variant_manifest_id"] == "VM-9101"
    assert sweep["sweep_plan_id"] == "SWEEP-PLAN-9101"
    assert len(manifest["variant_assignments"]) == 150
    assert manifest["variant_assignments"][0]["variant_id"] == "VAR-000001"
    assert manifest["variant_assignments"][0]["parameter_values"] == {
        "center_lookback_bars": 50,
        "vol_lookback_bars": 30,
        "trend_lookback_bars": 100,
    }
    assert manifest["variant_assignments"][-1]["variant_id"] == "VAR-000150"
    assert manifest["variant_assignments"][-1]["parameter_values"] == {
        "center_lookback_bars": 100,
        "vol_lookback_bars": 50,
        "trend_lookback_bars": 200,
    }
    assert sweep["trial_accounting"]["not_attempted_variant_count"] == 150
    assert sweep["trial_accounting"]["multiple_testing_denominator"] == 150


def test_run_generator_writes_validator_backed_draft_outputs(tmp_path):
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json")
    output_dir = tmp_path / "scratch"

    report = generator.run_generator(parameter_space_path=parameter_space, output_dir=output_dir)

    assert report["labels"] == generator.DRAFT_LABELS
    assert report["generated_variant_count"] == 150
    assert report["validator_authority"]["strategy_spec_validator"]["passed"] is True
    assert report["validator_authority"]["variant_sweep_validator"]["passed"] is True
    assert report["decision_recommendation"] == "ADOPT_AS_WORKFLOW_ACCELERATOR"
    assert "external_source_posture" not in report
    assert report["generation_posture"]["repo_owned_generator"] is True
    assert report["seed_used"] is None
    assert {path.name for path in output_dir.iterdir()} == {
        "draft_grid_generation_report.json",
        "draft_grid_generation_report.md",
        "generated_artifacts.sha256",
        "generated_strategy_specs",
        "generated_sweep_plans",
        "generated_variant_manifests",
    }

    report_on_disk = json.loads(
        (output_dir / "draft_grid_generation_report.json").read_text(encoding="utf-8")
    )
    assert report_on_disk["output_checksum"] == report["output_checksum"]
    manifest = json.loads(
        (
            output_dir
            / "generated_variant_manifests"
            / "VM-9101.variant_manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["manifest_hash_pinning"]["manifest_hash"].startswith("sha256:")
    report_md = (output_dir / "draft_grid_generation_report.md").read_text(encoding="utf-8")
    assert "DRAFT WORKFLOW OUTPUT" in report_md
    assert "NOT CANONICAL PREREGISTRATION" in report_md
    assert "Hyperopt" not in report_md


def test_same_input_same_output_checksum(tmp_path):
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json")

    first = generator.run_generator(parameter_space_path=parameter_space, output_dir=tmp_path / "one")
    second = generator.run_generator(parameter_space_path=parameter_space, output_dir=tmp_path / "two")

    assert first["generated_variant_count"] == second["generated_variant_count"]
    assert first["deterministic_artifact_checksum"] == second["deterministic_artifact_checksum"]


def test_axis_order_controls_stable_cartesian_order(tmp_path):
    payload = generator.default_parameter_space()
    payload["axis_order"] = [
        "trend_lookback_bars",
        "vol_lookback_bars",
        "center_lookback_bars",
    ]
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json", payload)

    _, _, manifest, _ = generator.build_artifacts(parameter_space)

    assert manifest["variant_assignments"][0]["parameter_values"] == {
        "trend_lookback_bars": 100,
        "vol_lookback_bars": 30,
        "center_lookback_bars": 50,
    }
    assert manifest["parameter_axes"][0]["parameter_name"] == "trend_lookback_bars"


def test_duplicate_parameter_value_fails_before_writes(tmp_path):
    payload = generator.default_parameter_space()
    payload["parameters"][0]["values"] = [50, 50]
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json", payload)

    with pytest.raises(generator.pilot.WorkflowHyperoptPilotError, match="duplicate values"):
        generator.build_artifacts(parameter_space)


def test_grid_above_bound_fails_before_writes(tmp_path):
    payload = generator.default_parameter_space()
    payload["parameters"][0]["values"] = [50, 60, 70, 80, 90, 100, 110]
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json", payload)

    with pytest.raises(generator.pilot.WorkflowHyperoptPilotError, match="above max"):
        generator.build_artifacts(parameter_space)


def test_too_many_variants_fails_before_writes(tmp_path):
    payload = generator.default_parameter_space()
    payload["parameters"][0]["values"] = list(range(50, 101))
    payload["parameters"][0]["bounds"]["max"] = 100
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json", payload)

    with pytest.raises(generator.pilot.WorkflowHyperoptPilotError, match="exceeds max variant count"):
        generator.build_artifacts(parameter_space)


def test_committed_report_does_not_embed_machine_local_paths(tmp_path):
    parameter_space = _write_parameter_space(tmp_path / "parameter_space.json")
    output_dir = tmp_path / "generated"

    report = generator.run_generator(parameter_space_path=parameter_space, output_dir=output_dir)

    assert report["generated_artifacts"]["strategy_spec"]["path"] == (
        "external:STRAT-SPEC-9101.strategy_spec.json"
    )
    root = generator.REPO_ROOT.resolve()
    bad_tokens = {str(root), str(root).replace("\\", "/"), "C:/", "C:\\"}
    for path in (
        output_dir / "draft_grid_generation_report.json",
        output_dir / "draft_grid_generation_report.md",
        output_dir / "generated_artifacts.sha256",
    ):
        text = path.read_text(encoding="utf-8")
        assert not any(token and token in text for token in bad_tokens)
        assert not re.search(r"\b[A-Za-z]:[\\/]", text)
        assert f"/{root.name}/" not in text


def test_committed_report_checksums_match_status_entry():
    report_path = generator.DEFAULT_OUTPUT_DIR / "draft_grid_generation_report.json"
    status_entry = generator.REPO_ROOT / "docs" / "status_entries" / f"{generator.PACKAGE_ID}.md"

    if not report_path.exists() or not status_entry.exists():
        pytest.skip("committed generated report/status entry not present yet")

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    status_text = status_entry.read_text(encoding="utf-8")

    assert payload["deterministic_artifact_checksum"] in status_text
    assert payload["output_checksum"] in status_text


def test_source_does_not_use_network_dependencies_or_canonical_writes():
    source = (generator.REPO_ROOT / "tools/research_workflow/draft_grid_generator.py").read_text(
        encoding="utf-8"
    )

    forbidden_terms = [
        "requests",
        "urllib",
        "http://",
        "https://",
        "socket",
        "append_trial",
        "write_result_population",
        "run_offline_sweep",
        "spec_signal_compiler",
    ]
    assert not any(term in source for term in forbidden_terms)
    assert generator.DEFAULT_OUTPUT_DIR.parts[-2:] == ("scratch", generator.PACKAGE_ID)
