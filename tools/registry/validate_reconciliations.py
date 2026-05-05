"""Validate JSON reconciliation artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.registry.validate_registry import (
    DEFAULT_REGISTRY_PATH,
    load_registry_rows,
)


DEFAULT_RECONCILIATIONS_DIR = REPO_ROOT / "research" / "reconciliations"
DEFAULT_OUTCOME_LEDGERS_DIR = REPO_ROOT / "research" / "outcome_ledgers"
DEFAULT_EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DEFAULT_LIFECYCLE_CHANGES_DIR = REPO_ROOT / "research" / "lifecycle_changes"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
DEFAULT_OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR = REPO_ROOT / "research" / "shadow_signal_summaries"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR = REPO_ROOT / "research" / "shadow_signal_summaries_v2"
RECONCILIATION_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "reconciliation.schema.json"
D2_006_ARTIFACT_ID = "D2-006"
D2_006_ARTIFACT_PATH = "docs/onboarding/PHASE2_BASELINE.md"

KNOWN_REF_PATTERNS = {
    "AOUT": re.compile(r"^AOUT-[0-9]{4}$"),
    "MOUT": re.compile(r"^MOUT-[0-9]{4}$"),
    "BMAP": re.compile(r"^BMAP-[0-9]{4}$"),
    "PGAS": re.compile(r"^PGAS-[0-9]{4}$"),
    "OSH": re.compile(r"^OSH-[0-9]{4}$"),
    "SSS": re.compile(r"^SSS-[0-9]{4}$"),
    "LCH": re.compile(r"^LCH-[0-9]{4}$"),
}
ADVISORY_REF_FAMILIES = {"AOUT", "MOUT", "BMAP", "PGAS", "OSH", "SSS"}
LIFECYCLE_REF_FAMILIES = {"LCH"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_ids(registry_path: Path = DEFAULT_REGISTRY_PATH) -> set[str]:
    return {
        row["candidate_id"]
        for _, row in load_registry_rows(registry_path)
        if isinstance(row.get("candidate_id"), str)
    }


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _resolve_repo_path(repo_root: Path, ref_value: Any) -> Path | None:
    if not isinstance(ref_value, str):
        return None
    candidate = Path(ref_value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None
    return resolved


def _load_ids(directory: Path, glob_pattern: str, id_field: str) -> set[str]:
    ids: set[str] = set()
    if not directory.exists():
        return ids
    for path in sorted(directory.rglob(glob_pattern)):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        artifact_id = payload.get(id_field)
        if isinstance(artifact_id, str):
            ids.add(artifact_id)
    return ids


def _load_outcomes(outcome_ledgers_dir: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    outcomes: dict[str, tuple[Path, dict[str, Any]]] = {}
    if not outcome_ledgers_dir.exists():
        return outcomes
    for path in sorted(outcome_ledgers_dir.rglob("*.outcome_ledger.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        outcome_id = payload.get("outcome_id")
        if isinstance(outcome_id, str):
            outcomes[outcome_id] = (path, payload)
    return outcomes


def _load_experiment_plans(experiments_dir: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    plans: dict[str, tuple[Path, dict[str, Any]]] = {}
    if not experiments_dir.exists():
        return plans
    for path in sorted(experiments_dir.rglob("EXP-*.plan.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        plan_id = payload.get("plan_id")
        if isinstance(plan_id, str):
            plans[plan_id] = (path, payload)
    return plans


def _known_ref_family(ref_value: str) -> str | None:
    for family, pattern in KNOWN_REF_PATTERNS.items():
        if pattern.match(ref_value):
            return family
    return None


def _known_ref_ids(
    *,
    lifecycle_changes_dir: Path,
    agent_outputs_dir: Path,
    macro_window_agent_outputs_dir: Path,
    bucket_mappings_dir: Path,
    pre_gate_advisory_snapshots_dir: Path,
    overlay_shadow_logs_dir: Path,
    shadow_signal_summaries_dir: Path,
    shadow_signal_summaries_v2_dir: Path,
) -> dict[str, set[str]]:
    return {
        "AOUT": _load_ids(agent_outputs_dir, "*.agent_output.json", "agent_output_id"),
        "MOUT": _load_ids(
            macro_window_agent_outputs_dir,
            "*.macro_window_agent_output.json",
            "macro_window_agent_output_id",
        ),
        "BMAP": _load_ids(bucket_mappings_dir, "*.bucket_mapping.json", "bucket_mapping_id"),
        "PGAS": _load_ids(
            pre_gate_advisory_snapshots_dir,
            "*.pre_gate_advisory_snapshot.json",
            "pre_gate_advisory_snapshot_id",
        ),
        "OSH": _load_ids(overlay_shadow_logs_dir, "*.overlay_shadow_log.json", "overlay_shadow_log_id"),
        "SSS": _load_ids(
            shadow_signal_summaries_dir,
            "*.shadow_signal_summary.json",
            "shadow_signal_summary_id",
        )
        | _load_ids(
            shadow_signal_summaries_v2_dir,
            "*.shadow_signal_summary.json",
            "shadow_signal_summary_id",
        ),
        "LCH": _load_ids(lifecycle_changes_dir, "*.lifecycle_change.json", "lifecycle_change_id"),
    }


def _validate_refs(
    *,
    path: Path,
    field_name: str,
    values: Any,
    known_ids: dict[str, set[str]],
    repo_root: Path,
    allowed_families: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(values, list):
        return errors
    for ref_value in values:
        if not isinstance(ref_value, str):
            continue
        family = _known_ref_family(ref_value)
        if family is not None:
            if family not in allowed_families:
                errors.append(f"{path}: {field_name} unsupported {family} reference: {ref_value}")
            elif ref_value not in known_ids.get(family, set()):
                errors.append(f"{path}: {field_name} unresolved {family} reference: {ref_value}")
            continue

        ref_path = _resolve_repo_path(repo_root, ref_value)
        if ref_path is None:
            errors.append(f"{path}: {field_name} invalid repo-relative path reference: {ref_value}")
        elif not ref_path.exists():
            errors.append(f"{path}: {field_name} repo-relative path does not exist: {ref_value}")
    return errors


def _validate_expectation_source(
    *,
    path: Path,
    payload: dict[str, Any],
    experiment_plans: dict[str, tuple[Path, dict[str, Any]]],
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    source_type = payload.get("expectation_source_type")
    source_id = payload.get("expectation_source_artifact_id")
    source_path = payload.get("expectation_source_artifact_path")
    extracted = payload.get("expectation_extracted")

    if isinstance(extracted, dict):
        if extracted.get("source_type") != source_type:
            errors.append(
                f"{path}: expectation_extracted.source_type does not match expectation_source_type"
            )
        if extracted.get("source_artifact_id") != source_id:
            errors.append(
                f"{path}: expectation_extracted.source_artifact_id does not match expectation_source_artifact_id"
            )
        if extracted.get("source_artifact_path") != source_path:
            errors.append(
                f"{path}: expectation_extracted.source_artifact_path does not match "
                "expectation_source_artifact_path"
            )

    resolved_source_path = _resolve_repo_path(repo_root, source_path)
    if source_type == "exp_success_criteria":
        plan_entry = experiment_plans.get(source_id)
        if plan_entry is None:
            errors.append(f"{path}: expectation_source_artifact_id not found in discovered EXP plans: {source_id}")
            return errors

        plan_path, plan_payload = plan_entry
        if resolved_source_path is None:
            errors.append(f"{path}: expectation_source_artifact_path invalid repo-relative path: {source_path}")
        elif not resolved_source_path.exists():
            errors.append(f"{path}: expectation_source_artifact_path does not exist: {source_path}")
        elif resolved_source_path != plan_path.resolve():
            errors.append(
                f"{path}: expectation_source_artifact_path {source_path} does not match "
                f"expectation_source_artifact_id {source_id}"
            )
        if plan_payload.get("candidate_id") != payload.get("candidate_id"):
            errors.append(
                f"{path}: EXP candidate_id {plan_payload.get('candidate_id')} does not match REC "
                f"candidate_id {payload.get('candidate_id')}"
            )
        if "success_criteria" not in plan_payload:
            errors.append(f"{path}: EXP plan lacks success_criteria: {source_id}")
    elif source_type == "d2_006_gates":
        if source_id != D2_006_ARTIFACT_ID:
            errors.append(f"{path}: d2_006_gates requires expectation_source_artifact_id {D2_006_ARTIFACT_ID}")
        if source_path != D2_006_ARTIFACT_PATH:
            errors.append(f"{path}: d2_006_gates requires expectation_source_artifact_path {D2_006_ARTIFACT_PATH}")
        if resolved_source_path is None:
            errors.append(f"{path}: expectation_source_artifact_path invalid repo-relative path: {source_path}")
        elif not resolved_source_path.exists():
            errors.append(f"{path}: expectation_source_artifact_path does not exist: {source_path}")
    elif source_type is not None:
        errors.append(f"{path}: unsupported expectation_source_type: {source_type}")

    return errors


def _validate_outcome_reference(
    *,
    path: Path,
    payload: dict[str, Any],
    outcomes: dict[str, tuple[Path, dict[str, Any]]],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    outcome_id = payload.get("outcome_id")
    outcome_entry = outcomes.get(outcome_id)
    if outcome_entry is None:
        return None, [f"{path}: outcome_id not found in discovered outcome ledgers: {outcome_id}"]

    _, outcome = outcome_entry
    for field_name in ("candidate_id", "outcome_kind", "pipeline_version"):
        if payload.get(field_name) != outcome.get(field_name):
            errors.append(
                f"{path}: {field_name} {payload.get(field_name)} does not match referenced "
                f"OL {outcome_id} value {outcome.get(field_name)}"
            )
    if outcome.get("outcome_kind") != "research_oos":
        errors.append(f"{path}: referenced OL outcome_kind must be research_oos: {outcome.get('outcome_kind')}")
    return outcome, errors


def _validate_derivation_record(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    derivation_record = payload.get("derivation_record")
    if not isinstance(derivation_record, dict):
        return errors
    source_outcome_id = derivation_record.get("source_outcome_id")
    if source_outcome_id is not None and source_outcome_id != payload.get("outcome_id"):
        errors.append(
            f"{path}: derivation_record.source_outcome_id does not match outcome_id: {source_outcome_id}"
        )
    expectation_source_type = derivation_record.get("expectation_source_type")
    if expectation_source_type is not None and expectation_source_type != payload.get("expectation_source_type"):
        errors.append(
            f"{path}: derivation_record.expectation_source_type does not match expectation_source_type: "
            f"{expectation_source_type}"
        )
    return errors


def _validate_realized_metrics(path: Path, payload: dict[str, Any], outcome: dict[str, Any] | None) -> list[str]:
    if outcome is None:
        return []
    realized_metrics = payload.get("realized_metrics")
    outcome_metrics = outcome.get("metrics")
    if not isinstance(realized_metrics, dict) or not isinstance(outcome_metrics, dict):
        return []

    errors: list[str] = []
    for metric_name, realized_value in sorted(realized_metrics.items()):
        if metric_name not in outcome_metrics:
            continue
        if realized_value != outcome_metrics.get(metric_name):
            errors.append(
                f"{path}: realized_metrics.{metric_name} {realized_value!r} does not match "
                f"referenced OL {payload.get('outcome_id')} metrics.{metric_name} "
                f"{outcome_metrics.get(metric_name)!r}"
            )
    return errors


def _validate_overall_verdict(path: Path, payload: dict[str, Any]) -> list[str]:
    comparison = payload.get("comparison")
    if not isinstance(comparison, dict):
        return []
    metric_comparisons = comparison.get("metric_comparisons")
    if not isinstance(metric_comparisons, list):
        return []
    verdicts = [
        metric.get("comparison_verdict")
        for metric in metric_comparisons
        if isinstance(metric, dict) and isinstance(metric.get("comparison_verdict"), str)
    ]
    if not verdicts:
        return []

    verdict_set = set(verdicts)
    expected: str | None = None
    if verdict_set == {"met"}:
        expected = "all_met"
    elif verdict_set == {"not_met"}:
        expected = "none_met"
    elif verdict_set == {"insufficient_evidence"}:
        expected = "insufficient_evidence"
    elif verdict_set <= {"met", "not_met"} and {"met", "not_met"} <= verdict_set:
        expected = "partially_met"

    if expected is not None and payload.get("overall_verdict") != expected:
        return [
            f"{path}: overall_verdict {payload.get('overall_verdict')} does not match clear "
            f"metric_comparisons derivation {expected}"
        ]
    return []


def validate_reconciliations(
    reconciliations_dir: Path = DEFAULT_RECONCILIATIONS_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    outcome_ledgers_dir: Path = DEFAULT_OUTCOME_LEDGERS_DIR,
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
    lifecycle_changes_dir: Path = DEFAULT_LIFECYCLE_CHANGES_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    macro_window_agent_outputs_dir: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    pre_gate_advisory_snapshots_dir: Path = DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    shadow_signal_summaries_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    shadow_signal_summaries_v2_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    schema_path: Path = RECONCILIATION_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for reconciliation artifacts, or [] when valid."""

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    if not reconciliations_dir.exists():
        return []

    reconciliation_files = sorted(reconciliations_dir.rglob("*.reconciliation.json"))
    stray_rec_files = [
        path
        for path in sorted(reconciliations_dir.rglob("REC-*"))
        if path.is_file() and not path.name.endswith(".reconciliation.json")
    ]
    if not reconciliation_files and not stray_rec_files:
        return []

    errors = [
        f"{path}: REC artifact filename must use REC-NNNN.reconciliation.json suffix"
        for path in stray_rec_files
    ]
    candidate_ids = load_candidate_ids(registry_path)
    outcomes = _load_outcomes(outcome_ledgers_dir)
    experiment_plans = _load_experiment_plans(experiments_dir)
    payloads: list[tuple[Path, dict[str, Any]]] = []
    known_reconciliation_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in reconciliation_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        payloads.append((path, payload))

        reconciliation_id = payload.get("reconciliation_id")
        if isinstance(reconciliation_id, str):
            expected_name = f"{reconciliation_id}.reconciliation.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if reconciliation_id in known_reconciliation_ids:
                errors.append(
                    f"{path}: duplicate reconciliation_id {reconciliation_id}; "
                    f"first seen at {id_paths[reconciliation_id]}"
                )
            known_reconciliation_ids.add(reconciliation_id)
            id_paths.setdefault(reconciliation_id, path)
        else:
            errors.append(f"{path}: missing valid reconciliation_id")

    known_ids = _known_ref_ids(
        lifecycle_changes_dir=lifecycle_changes_dir,
        agent_outputs_dir=agent_outputs_dir,
        macro_window_agent_outputs_dir=macro_window_agent_outputs_dir,
        bucket_mappings_dir=bucket_mappings_dir,
        pre_gate_advisory_snapshots_dir=pre_gate_advisory_snapshots_dir,
        overlay_shadow_logs_dir=overlay_shadow_logs_dir,
        shadow_signal_summaries_dir=shadow_signal_summaries_dir,
        shadow_signal_summaries_v2_dir=shadow_signal_summaries_v2_dir,
    )

    for path, payload in payloads:
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")

        outcome, outcome_errors = _validate_outcome_reference(path=path, payload=payload, outcomes=outcomes)
        errors.extend(outcome_errors)
        errors.extend(
            _validate_expectation_source(
                path=path,
                payload=payload,
                experiment_plans=experiment_plans,
                repo_root=repo_root,
            )
        )
        errors.extend(_validate_derivation_record(path, payload))
        errors.extend(_validate_realized_metrics(path, payload, outcome))
        errors.extend(_validate_overall_verdict(path, payload))
        errors.extend(
            _validate_refs(
                path=path,
                field_name="linked_advisory_artifacts",
                values=payload.get("linked_advisory_artifacts"),
                known_ids=known_ids,
                repo_root=repo_root,
                allowed_families=ADVISORY_REF_FAMILIES,
            )
        )
        errors.extend(
            _validate_refs(
                path=path,
                field_name="linked_lifecycle_artifacts",
                values=payload.get("linked_lifecycle_artifacts"),
                known_ids=known_ids,
                repo_root=repo_root,
                allowed_families=LIFECYCLE_REF_FAMILIES,
            )
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconciliations-dir", type=Path, default=DEFAULT_RECONCILIATIONS_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=RECONCILIATION_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_reconciliations(
        reconciliations_dir=args.reconciliations_dir,
        registry_path=args.registry,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.reconciliations_dir.exists():
        print(f"OK: {args.reconciliations_dir} does not exist; nothing to validate")
    else:
        print(f"OK: reconciliation artifacts under {args.reconciliations_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
