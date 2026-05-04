"""Build a candidate outcome-ledger artifact from committed REP/EXP truth."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from tools.registry.validate_outcome_ledger import (
    DEFAULT_EXPERIMENTS_DIR,
    DEFAULT_OUTCOME_LEDGERS_DIR,
    OUTCOME_LEDGER_SCHEMA_PATH,
    REPO_ROOT,
    validate_outcome_ledgers,
)
from tools.registry.validate_registry import DEFAULT_REGISTRY_PATH, load_registry_rows


OUTCOME_ID_PATTERN = re.compile(r"^OL-[0-9]{4}$")
CANDIDATE_ID_PATTERN = re.compile(r"^H-[0-9]{3}$")
REP_ID_PATTERN = re.compile(r"^REP-[0-9]{4}$")
EXP_ID_PATTERN = re.compile(r"^EXP-[0-9]{4}$")
PIPELINE_VERSIONS = {"pre_wp_5b", "post_wp_5b"}
DERIVATION_TOOL_VERSION = "wp-9o"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcome-id", required=True)
    parser.add_argument("--rep-id", required=True)
    parser.add_argument("--rep-path", required=True)
    parser.add_argument("--exp-id", required=True)
    parser.add_argument("--exp-path", required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--pipeline-version", required=True, choices=sorted(PIPELINE_VERSIONS))
    parser.add_argument("--derivation-timestamp", required=True)
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("--output", type=Path)
    output_group.add_argument("--stdout", action="store_true")
    return parser


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2) + "\n"


def _repo_relative(path: Path, repo_root: Path = REPO_ROOT) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _display_path(path: Path, repo_root: Path = REPO_ROOT) -> str:
    resolved = path.resolve()
    try:
        return _repo_relative(resolved, repo_root)
    except ValueError:
        return resolved.as_posix()


def _resolve_repo_relative_path(path_value: str, *, repo_root: Path = REPO_ROOT) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"path must be repo-relative and stay under repo root: {path_value}")
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path must stay under repo root: {path_value}") from exc
    if not resolved.exists():
        raise ValueError(f"path does not exist: {path_value}")
    if not resolved.is_file():
        raise ValueError(f"path is not a file: {path_value}")
    return resolved


def _parse_derivation_timestamp(value: str) -> str:
    if not re.fullmatch(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})$", value):
        raise ValueError(f"derivation timestamp must be timezone-qualified ISO-8601 with seconds: {value}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"derivation timestamp is not parseable: {value}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"derivation timestamp must include a timezone offset: {value}")
    return value


def _load_candidate_ids(registry_path: Path = DEFAULT_REGISTRY_PATH) -> set[str]:
    return {
        row["candidate_id"]
        for _, row in load_registry_rows(registry_path)
        if isinstance(row.get("candidate_id"), str)
    }


def _load_schema(schema_path: Path = OUTCOME_LEDGER_SCHEMA_PATH) -> dict[str, Any]:
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    return schema


def _metric_fields(schema: Mapping[str, Any]) -> tuple[list[str], set[str]]:
    metrics_schema = schema["definitions"]["research_oos_metrics"]
    required = list(metrics_schema["required"])
    allowed = set(metrics_schema["properties"])
    return required, allowed


def _validate_identity_args(
    *,
    outcome_id: str,
    rep_id: str,
    exp_id: str,
    candidate_id: str,
    pipeline_version: str,
) -> None:
    if not OUTCOME_ID_PATTERN.fullmatch(outcome_id):
        raise ValueError(f"outcome_id must match OL-NNNN: {outcome_id}")
    if not REP_ID_PATTERN.fullmatch(rep_id):
        raise ValueError(f"rep_id must match REP-NNNN: {rep_id}")
    if not EXP_ID_PATTERN.fullmatch(exp_id):
        raise ValueError(f"exp_id must match EXP-NNNN: {exp_id}")
    if not CANDIDATE_ID_PATTERN.fullmatch(candidate_id):
        raise ValueError(f"candidate_id must match H-NNN: {candidate_id}")
    if pipeline_version not in PIPELINE_VERSIONS:
        raise ValueError(
            f"pipeline_version must be one of {sorted(PIPELINE_VERSIONS)}: {pipeline_version}"
        )


def _source_data_refs(exp_payload: Mapping[str, Any]) -> list[str]:
    refs = exp_payload.get("data_requirements")
    if not isinstance(refs, list) or not refs:
        raise ValueError("EXP data_requirements must be a non-empty list")
    if not all(isinstance(item, str) and item for item in refs):
        raise ValueError("EXP data_requirements must contain only non-empty strings")
    return list(refs)


def _copy_oos_metrics(rep_payload: Mapping[str, Any], schema: Mapping[str, Any]) -> dict[str, Any]:
    metrics = rep_payload.get("metrics")
    if not isinstance(metrics, dict) or not isinstance(metrics.get("out_of_sample"), dict):
        raise ValueError("REP metrics.out_of_sample is required")

    out_of_sample = metrics["out_of_sample"]
    required_fields, allowed_fields = _metric_fields(schema)
    missing = [field for field in required_fields if field not in out_of_sample]
    if missing:
        raise ValueError(f"REP metrics.out_of_sample missing required fields: {', '.join(missing)}")

    return {
        field: out_of_sample[field]
        for field in out_of_sample
        if field in allowed_fields
    }


def _validate_source_pair(
    *,
    rep_payload: Mapping[str, Any],
    exp_payload: Mapping[str, Any],
    rep_id: str,
    exp_id: str,
    candidate_id: str,
    rep_path: str,
    exp_path: str,
) -> None:
    if rep_payload.get("report_id") != rep_id:
        raise ValueError(f"REP path {rep_path} does not contain report_id {rep_id}")
    if exp_payload.get("plan_id") != exp_id:
        raise ValueError(f"EXP path {exp_path} does not contain plan_id {exp_id}")
    if rep_payload.get("candidate_id") != candidate_id:
        raise ValueError(f"REP candidate_id does not match supplied candidate_id: {rep_payload.get('candidate_id')}")
    if exp_payload.get("candidate_id") != candidate_id:
        raise ValueError(f"EXP candidate_id does not match supplied candidate_id: {exp_payload.get('candidate_id')}")
    if rep_payload.get("plan_id") != exp_id:
        raise ValueError(f"REP plan_id does not match supplied exp_id: {rep_payload.get('plan_id')}")


def _notes(candidate_id: str, rep_id: str, exp_id: str, pipeline_version: str) -> str:
    note = (
        f"WP-9o helper maps {candidate_id} / {rep_id} / {exp_id} as {pipeline_version}; "
        "source EXP/REP truth preserves the no-formal-split window convention."
    )
    if candidate_id == "H-004":
        note += " H-004 split handling remains explicit when separate REP sources are used."
    return note


def _retrospective_disclosure(rep_id: str) -> str:
    return (
        f"WP-9o derives this candidate outcome-ledger artifact after the fact from the already "
        f"committed {rep_id} report. REP remains the authoritative research record. This artifact "
        "carries no promotion, demotion, policy, REC/reconciliation, paper/live, runtime, deployment, "
        "strategy adjustment, or protected-path authority."
    )


def build_outcome_payload(
    *,
    outcome_id: str,
    rep_id: str,
    rep_path: str,
    exp_id: str,
    exp_path: str,
    candidate_id: str,
    pipeline_version: str,
    derivation_timestamp: str,
    repo_root: Path = REPO_ROOT,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    schema_path: Path = OUTCOME_LEDGER_SCHEMA_PATH,
) -> dict[str, Any]:
    _validate_identity_args(
        outcome_id=outcome_id,
        rep_id=rep_id,
        exp_id=exp_id,
        candidate_id=candidate_id,
        pipeline_version=pipeline_version,
    )
    derivation_timestamp = _parse_derivation_timestamp(derivation_timestamp)

    if candidate_id not in _load_candidate_ids(registry_path):
        raise ValueError(f"candidate_id not found in registry: {candidate_id}")

    resolved_rep_path = _resolve_repo_relative_path(rep_path, repo_root=repo_root)
    resolved_exp_path = _resolve_repo_relative_path(exp_path, repo_root=repo_root)
    rep_payload = load_json(resolved_rep_path)
    exp_payload = load_json(resolved_exp_path)
    _validate_source_pair(
        rep_payload=rep_payload,
        exp_payload=exp_payload,
        rep_id=rep_id,
        exp_id=exp_id,
        candidate_id=candidate_id,
        rep_path=rep_path,
        exp_path=exp_path,
    )

    schema = _load_schema(schema_path)
    payload = {
        "schema_version": "v1",
        "outcome_id": outcome_id,
        "candidate_id": candidate_id,
        "lifecycle_state_during_window": "in_research",
        "evaluation_window_start": None,
        "evaluation_window_end": None,
        "outcome_kind": "research_oos",
        "metrics": _copy_oos_metrics(rep_payload, schema),
        "data_provenance": {
            "source_data_refs": _source_data_refs(exp_payload),
            "source_data_window_start": None,
            "source_data_window_end": None,
            "source_data_notes": f"Copied from {exp_id} data_requirements; no formal source-data window endpoints are committed for this baseline.",
        },
        "derivation_record": {
            "derivation_method": "from_rep_artifact",
            "source_artifact_id": rep_id,
            "source_artifact_path": _repo_relative(resolved_rep_path, repo_root),
            "derivation_timestamp": derivation_timestamp,
            "derivation_tool_version": DERIVATION_TOOL_VERSION,
        },
        "pipeline_version": pipeline_version,
        "linked_artifacts": [exp_id, rep_id],
        "retrospective_flag": True,
        "linked_advisory_artifacts": [],
        "notes": _notes(candidate_id, rep_id, exp_id, pipeline_version),
        "retrospective_disclosure": _retrospective_disclosure(rep_id),
    }

    validator = Draft7Validator(schema)
    schema_errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    if schema_errors:
        first_error = schema_errors[0]
        location = ".".join(str(part) for part in first_error.absolute_path)
        prefix = f"{location}: " if location else ""
        raise ValueError(f"generated outcome ledger failed schema validation: {prefix}{first_error.message}")

    return payload


def validate_candidate_against_corpus(
    payload: Mapping[str, Any],
    *,
    outcome_ledgers_dir: Path = DEFAULT_OUTCOME_LEDGERS_DIR,
    repo_root: Path = REPO_ROOT,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
) -> list[str]:
    outcome_id = payload.get("outcome_id")
    if not isinstance(outcome_id, str):
        return ["candidate payload missing outcome_id"]

    with tempfile.TemporaryDirectory(prefix="outcome-ledger-helper-") as temp_dir_name:
        temp_outcome_ledgers_dir = Path(temp_dir_name) / "outcome_ledgers"
        temp_outcome_ledgers_dir.mkdir(parents=True, exist_ok=True)

        if outcome_ledgers_dir.exists():
            for existing_path in sorted(outcome_ledgers_dir.glob("*.outcome_ledger.json")):
                existing_payload = load_json(existing_path)
                if existing_payload.get("outcome_id") == outcome_id:
                    continue
                shutil.copyfile(existing_path, temp_outcome_ledgers_dir / existing_path.name)

        candidate_path = temp_outcome_ledgers_dir / f"{outcome_id}.outcome_ledger.json"
        candidate_path.write_text(render_payload(payload), encoding="utf-8")
        return validate_outcome_ledgers(
            outcome_ledgers_dir=temp_outcome_ledgers_dir,
            registry_path=registry_path,
            experiments_dir=experiments_dir,
            repo_root=repo_root,
        )


def _write_payload(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_payload(payload), encoding="utf-8")


def _print_validation_errors(errors: Sequence[str]) -> None:
    for error in errors:
        print(f"VALIDATION ERROR: {error}", file=sys.stderr)


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        payload = build_outcome_payload(
            outcome_id=args.outcome_id,
            rep_id=args.rep_id,
            rep_path=args.rep_path,
            exp_id=args.exp_id,
            exp_path=args.exp_path,
            candidate_id=args.candidate_id,
            pipeline_version=args.pipeline_version,
            derivation_timestamp=args.derivation_timestamp,
        )
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_candidate_against_corpus(payload)
    if errors:
        print("Validation: FAIL", file=sys.stderr)
        _print_validation_errors(errors)
        return 1

    if args.stdout:
        print(render_payload(payload), end="")
        print("Validation: PASS", file=sys.stderr)
        return 0

    output_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    if output_path.exists():
        print(f"ERROR: refusing to overwrite existing file: {_display_path(output_path)}", file=sys.stderr)
        return 1

    try:
        _write_payload(output_path, payload)
    except OSError as exc:
        print(f"ERROR: failed to write output file: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote validated outcome ledger candidate: {_display_path(output_path)}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())

