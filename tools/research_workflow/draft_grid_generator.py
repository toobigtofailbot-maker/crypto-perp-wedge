"""Generate validator-backed draft Strategy Spec / VM / Sweep artifacts.

This module productionizes the merged workflow-hyperopt pilot as a repo-owned
draft generator while preserving the pilot's existing validator-compatible
artifact materialization. Outputs are scratch-only and non-authoritative.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from tools.external_pilots import workflow_hyperopt_pilot as pilot


REPO_ROOT = Path(__file__).resolve().parents[2]
_PILOT_DEFAULT_PARAMETER_SPACE = pilot.default_parameter_space
PACKAGE_ID = "EXT-INTEG-WORKFLOW-GEN-01"
GENERATION_TIMESTAMP = "2026-06-19T00:00:00Z"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_PARAMETER_SPACE_PATH = DEFAULT_OUTPUT_DIR / "parameter_space.json"

DRAFT_LABELS = [
    "DRAFT WORKFLOW OUTPUT",
    "NOT CANONICAL PREREGISTRATION",
    "NOT CANDIDATE EVIDENCE",
    "NOT SCREEN-GATE OR PROMOTION AUTHORITY",
    "VALIDATED ONLY AGAINST STRUCTURAL REPO VALIDATORS",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
]


class DraftGridGeneratorError(RuntimeError):
    """Raised when draft grid generation cannot proceed safely."""


def default_parameter_space() -> dict[str, Any]:
    """Return the deterministic demo parameter-space spec for this package."""

    payload = copy.deepcopy(_PILOT_DEFAULT_PARAMETER_SPACE())
    payload.update(
        {
            "package_id": PACKAGE_ID,
            "generated_strategy_spec_id": "STRAT-SPEC-9101",
            "generated_variant_manifest_id": "VM-9101",
            "generated_sweep_plan_id": "SWEEP-PLAN-9101",
            "search_family_id": "SF-EXT-INTEG-WORKFLOW-GEN-9101",
            "created_at": GENERATION_TIMESTAMP,
        }
    )
    payload["authority"] = {
        "scratch_only": True,
        "canonical_preregistration": False,
        "canonical_strategy_spec_mutation": False,
        "canonical_variant_manifest_mutation": False,
        "canonical_sweep_plan_mutation": False,
        "candidate_evidence_authority": False,
        "screen_gate_authority": False,
        "promotion_readiness_authority": False,
        "runtime_authority": False,
    }
    return payload


def _artifact_paths(output_dir: Path, parameter_space: dict[str, Any]) -> dict[str, Path]:
    return {
        "strategy_spec": output_dir
        / "generated_strategy_specs"
        / f"{parameter_space['generated_strategy_spec_id']}.strategy_spec.json",
        "variant_manifest": output_dir
        / "generated_variant_manifests"
        / f"{parameter_space['generated_variant_manifest_id']}.variant_manifest.json",
        "sweep_plan": output_dir
        / "generated_sweep_plans"
        / f"{parameter_space['generated_sweep_plan_id']}.sweep_plan.json",
        "report_json": output_dir / "draft_grid_generation_report.json",
        "report_md": output_dir / "draft_grid_generation_report.md",
        "checksums": output_dir / "generated_artifacts.sha256",
    }


def _rewrite_draft_text(value: Any) -> Any:
    if isinstance(value, str):
        replacements = {
            "Scratch Workflow Pilot Parent Strategy Spec Snapshot": (
                "Draft Workflow Generator Parent Strategy Spec Snapshot"
            ),
            "scratch-workflow-hyperopt-pilot-parent": (
                "scratch-draft-grid-generator-parent"
            ),
            "repo-native-workflow-pilot-manual-grid": (
                "repo-native-draft-grid-generator-manual-grid"
            ),
            "workflow authoring pilot": "draft grid generator",
            "Workflow authoring pilot": "Draft grid generator",
            "Scratch workflow pilot artifact": "Draft workflow generator artifact",
            "Scratch workflow pilot": "Draft workflow generator",
            "workflow pilot": "draft generator",
            "Workflow pilot": "Draft generator",
            "hyperopt": "grid",
            "Hyperopt": "Grid",
            "pilot": "generator",
            "Pilot": "Generator",
        }
        rewritten = value
        for old, new in replacements.items():
            rewritten = rewritten.replace(old, new)
        return rewritten
    if isinstance(value, list):
        return [_rewrite_draft_text(item) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite_draft_text(child) for key, child in value.items()}
    return value


def _sync_hashes(parent_spec: dict[str, Any], manifest: dict[str, Any], sweep: dict[str, Any]) -> None:
    strategy_hash = pilot.sha256_prefixed(parent_spec)
    manifest["parent_strategy_spec"]["strategy_spec_hash"] = strategy_hash
    for ref in manifest.get("lineage", {}).get("parent_refs", []):
        if isinstance(ref, dict) and ref.get("ref_type") == "prior_strategy_spec":
            ref["ref_hash"] = strategy_hash

    hash_pinning = manifest.get("manifest_hash_pinning", {})
    scope = hash_pinning.get("hash_scope", [])
    scoped_payload = pilot._hash_scope_payload(manifest, scope)
    if scoped_payload is None:
        raise DraftGridGeneratorError("manifest hash scope contains missing fields")
    manifest_hash = pilot.sha256_prefixed(scoped_payload)
    hash_pinning["manifest_hash"] = manifest_hash

    sweep["parent_variant_manifest"]["manifest_hash"] = manifest_hash
    lineage = sweep.get("lineage", {})
    parent_manifest_ref = lineage.get("parent_manifest_ref")
    if isinstance(parent_manifest_ref, dict):
        parent_manifest_ref["ref_hash"] = manifest_hash
    parent_strategy_ref = lineage.get("parent_strategy_spec_ref")
    if isinstance(parent_strategy_ref, dict):
        parent_strategy_ref["ref_hash"] = strategy_hash


def _productionize_artifacts(
    parent_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    parent_spec = _rewrite_draft_text(parent_spec)
    manifest = _rewrite_draft_text(manifest)
    sweep = _rewrite_draft_text(sweep)
    _sync_hashes(parent_spec, manifest, sweep)
    return parent_spec, manifest, sweep


def _report(
    parameter_space_path: Path,
    paths: dict[str, Path],
    parameter_space: dict[str, Any],
    parent_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    artifact_payload = {
        "parameter_space": parameter_space,
        "strategy_spec": parent_spec,
        "variant_manifest": manifest,
        "sweep_plan": sweep,
    }
    generated_artifacts = {
        "parameter_space": {
            "path": pilot._portable_report_path(parameter_space_path),
            "checksum": pilot._sha256_file(parameter_space_path),
        },
        "strategy_spec": {
            "path": pilot._portable_report_path(paths["strategy_spec"]),
            "checksum": pilot._sha256_file(paths["strategy_spec"]),
        },
        "variant_manifest": {
            "path": pilot._portable_report_path(paths["variant_manifest"]),
            "checksum": pilot._sha256_file(paths["variant_manifest"]),
        },
        "sweep_plan": {
            "path": pilot._portable_report_path(paths["sweep_plan"]),
            "checksum": pilot._sha256_file(paths["sweep_plan"]),
        },
    }
    report: dict[str, Any] = {
        "labels": DRAFT_LABELS,
        "package_id": PACKAGE_ID,
        "tool_identity": "tools.research_workflow.draft_grid_generator",
        "materialization_kind": parameter_space["materialization_kind"],
        "source_strategy_spec_ref": parameter_space["source_strategy_spec_ref"],
        "generated_strategy_spec_id": parent_spec["strategy_spec_id"],
        "generated_variant_manifest_id": manifest["variant_manifest_id"],
        "generated_sweep_plan_id": sweep["sweep_plan_id"],
        "generated_variant_count": len(manifest["variant_assignments"]),
        "axis_order": parameter_space["axis_order"],
        "axis_count": len(parameter_space["parameters"]),
        "deterministic_ordering": "axis_order_then_itertools_product_left_to_right",
        "seed_used": None,
        "generated_artifacts": generated_artifacts,
        "deterministic_artifact_checksum": pilot._sha256_payload(artifact_payload),
        "validator_authority": validation,
        "generation_posture": {
            "repo_owned_generator": True,
            "scratch_only": True,
            "existing_structural_validators_only": True,
            "external_dependency_added": False,
            "external_runtime_tool_invoked": False,
            "optimizer_or_ranking_authority": False,
        },
        "boundary_statement": {
            "canonical_result_population_write": False,
            "canonical_preregistration_created": False,
            "canonical_strategy_spec_mutation": False,
            "canonical_variant_manifest_mutation": False,
            "canonical_sweep_plan_mutation": False,
            "screen_gate_authority_created": False,
            "promotion_readiness_authority_created": False,
            "candidate_evidence_authority_created": False,
            "runner_backtester_changed": False,
            "runtime_paper_live_touched": False,
            "oms_risk_reconciliation_credentials_order_paths_touched": False,
        },
        "decision_recommendation": "ADOPT_AS_WORKFLOW_ACCELERATOR",
        "next_gated_wp_suggestion": (
            "Future draft-to-canonical promotion requires a separate human-gated package; "
            "this generator creates no promotion authority."
        ),
    }
    report["output_checksum"] = pilot._sha256_payload(report)
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Draft Grid Generation Report",
        "",
        *[f"- {label}" for label in DRAFT_LABELS],
        "",
        f"Recommendation: `{report['decision_recommendation']}`",
        f"Generated variants: `{report['generated_variant_count']}`",
        f"Deterministic checksum: `{report['deterministic_artifact_checksum']}`",
        f"Output checksum: `{report['output_checksum']}`",
        "",
        "## Generated Artifacts",
        "",
    ]
    for name, artifact in report["generated_artifacts"].items():
        lines.append(f"- {name}: `{artifact['path']}` / `{artifact['checksum']}`")
    lines.extend(["", "## Validator Authority", ""])
    for name, validator in report["validator_authority"].items():
        lines.append(f"- {name}: `{'PASS' if validator['passed'] else 'FAIL'}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Scratch-only Strategy Spec snapshot, Variant Manifest, and Sweep Plan artifacts.",
            "- No canonical preregistration, Result Population, trial log, runner, backtester, runtime, paper, or live path is changed.",
            "- No optimizer, ranking, screen-gate, promotion, readiness, or candidate-evidence authority is created.",
            "",
        ]
    )
    return "\n".join(lines)


@contextlib.contextmanager
def _pilot_context() -> Iterator[None]:
    """Bind pilot materialization helpers to this production package identity."""

    saved = {
        "PACKAGE_ID": pilot.PACKAGE_ID,
        "DEFAULT_OUTPUT_DIR": pilot.DEFAULT_OUTPUT_DIR,
        "DEFAULT_PARAMETER_SPACE_PATH": pilot.DEFAULT_PARAMETER_SPACE_PATH,
        "GENERATION_TIMESTAMP": pilot.GENERATION_TIMESTAMP,
        "NON_CANONICAL_LABELS": pilot.NON_CANONICAL_LABELS,
        "default_parameter_space": pilot.default_parameter_space,
        "_artifact_paths": pilot._artifact_paths,
    }
    try:
        pilot.PACKAGE_ID = PACKAGE_ID
        pilot.DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
        pilot.DEFAULT_PARAMETER_SPACE_PATH = DEFAULT_PARAMETER_SPACE_PATH
        pilot.GENERATION_TIMESTAMP = GENERATION_TIMESTAMP
        pilot.NON_CANONICAL_LABELS = DRAFT_LABELS
        pilot.default_parameter_space = default_parameter_space
        pilot._artifact_paths = _artifact_paths
        yield
    finally:
        pilot.PACKAGE_ID = saved["PACKAGE_ID"]
        pilot.DEFAULT_OUTPUT_DIR = saved["DEFAULT_OUTPUT_DIR"]
        pilot.DEFAULT_PARAMETER_SPACE_PATH = saved["DEFAULT_PARAMETER_SPACE_PATH"]
        pilot.GENERATION_TIMESTAMP = saved["GENERATION_TIMESTAMP"]
        pilot.NON_CANONICAL_LABELS = saved["NON_CANONICAL_LABELS"]
        pilot.default_parameter_space = saved["default_parameter_space"]
        pilot._artifact_paths = saved["_artifact_paths"]


def build_artifacts(
    parameter_space_path: Path = DEFAULT_PARAMETER_SPACE_PATH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build draft artifacts in memory without writing them."""

    with _pilot_context():
        parameter_space, parent_spec, manifest, sweep = pilot.build_artifacts(parameter_space_path)
        parent_spec, manifest, sweep = _productionize_artifacts(parent_spec, manifest, sweep)
        return parameter_space, parent_spec, manifest, sweep


def run_generator(
    *,
    parameter_space_path: Path = DEFAULT_PARAMETER_SPACE_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Write draft artifacts and return the deterministic generation report."""

    with _pilot_context():
        pilot._ensure_default_parameter_space(parameter_space_path)
        parameter_space, parent_spec, manifest, sweep = pilot.build_artifacts(parameter_space_path)
        parent_spec, manifest, sweep = _productionize_artifacts(parent_spec, manifest, sweep)
        paths = _artifact_paths(output_dir, parameter_space)
        paths["strategy_spec"].parent.mkdir(parents=True, exist_ok=True)
        paths["variant_manifest"].parent.mkdir(parents=True, exist_ok=True)
        paths["sweep_plan"].parent.mkdir(parents=True, exist_ok=True)
        pilot._write_json(paths["strategy_spec"], parent_spec)
        pilot._write_json(paths["variant_manifest"], manifest)
        pilot._write_json(paths["sweep_plan"], sweep)
        validation = pilot._validation_summary(paths)
        report = _report(
            parameter_space_path,
            paths,
            parameter_space,
            parent_spec,
            manifest,
            sweep,
            validation,
        )
        pilot._write_json(paths["report_json"], report)
        paths["report_md"].write_text(_markdown_report(report), encoding="utf-8")
        paths["checksums"].write_text(
            "\n".join(
                f"{artifact['checksum']}  {artifact['path']}"
                for artifact in report["generated_artifacts"].values()
            )
            + "\n",
            encoding="utf-8",
        )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter-space", type=Path, default=DEFAULT_PARAMETER_SPACE_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_generator(
            parameter_space_path=args.parameter_space,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "generated_variant_count": report["generated_variant_count"],
                "generated_variant_manifest_id": report["generated_variant_manifest_id"],
                "generated_sweep_plan_id": report["generated_sweep_plan_id"],
                "deterministic_artifact_checksum": report["deterministic_artifact_checksum"],
                "strategy_spec_validator_passed": report["validator_authority"][
                    "strategy_spec_validator"
                ]["passed"],
                "variant_sweep_validator_passed": report["validator_authority"][
                    "variant_sweep_validator"
                ]["passed"],
                "decision_label": report["decision_recommendation"],
                "output_checksum": report["output_checksum"],
                "output_dir": pilot._portable_report_path(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
