"""Manually build and validate candidate overlay shadow logs."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.registry.validate_overlay_shadow_logs import validate_overlay_shadow_logs
from tools.shadow.overlay_shadow_hook import (
    PERMISSION_TO_MULTIPLIER,
    REPO_ROOT,
    load_json,
    observe_external_overlay_bucket,
)


OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
CANONICAL_SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "context_snapshot_sample.json"
CANONICAL_CONFIG_PATH = REPO_ROOT / "configs" / "fmp_macro_flags.json"

ADVISORY_SOURCE_PATTERNS = {
    "BMAP": re.compile(r"^BMAP-[0-9]{4}$"),
    "PGAS": re.compile(r"^PGAS-[0-9]{4}$"),
}
OVERLAY_SHADOW_LOG_NAME_PATTERN = re.compile(r"^(OSH-[0-9]{4})\.overlay_shadow_log\.json$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--advisory-source", choices=sorted(ADVISORY_SOURCE_PATTERNS), required=True)
    parser.add_argument("--advisory-artifact-id", required=True)
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--context-snapshot-path", type=Path, default=None)
    parser.add_argument("--macro-flags-path", type=Path, default=None)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    return parser


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return _repo_relative(resolved)
    except ValueError:
        return resolved.as_posix()


def _require_exact_path(path: Path, expected: Path, label: str) -> Path:
    resolved = path.resolve()
    expected_resolved = expected.resolve()
    if resolved != expected_resolved:
        raise ValueError(
            f"{label} must resolve to {_repo_relative(expected_resolved)}, got {resolved.as_posix()}"
        )
    return resolved


def parse_timestamp_utc(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"timestamp must be ISO-8601 UTC: {value}") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a UTC offset: {value}")

    utc_parsed = parsed.astimezone(timezone.utc)
    if utc_parsed.utcoffset() != timezone.utc.utcoffset(utc_parsed):
        raise ValueError(f"timestamp must be UTC: {value}")

    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"timestamp must be UTC: {value}")

    return utc_parsed.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_advisory_artifact_id(advisory_source: str, advisory_artifact_id: str) -> str:
    pattern = ADVISORY_SOURCE_PATTERNS[advisory_source]
    if not pattern.fullmatch(advisory_artifact_id):
        raise ValueError(
            f"advisory artifact id for {advisory_source} must match {pattern.pattern}: {advisory_artifact_id}"
        )
    return advisory_artifact_id


def next_overlay_shadow_log_id(overlay_shadow_logs_dir: Path | None = None) -> str:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or OVERLAY_SHADOW_LOGS_DIR
    highest = 0
    for path in sorted(overlay_shadow_logs_dir.glob("*.overlay_shadow_log.json")):
        match = OVERLAY_SHADOW_LOG_NAME_PATTERN.fullmatch(path.name)
        if match is None:
            continue
        highest = max(highest, int(match.group(1).split("-")[1]))
    return f"OSH-{highest + 1:04d}"


def default_output_path(overlay_shadow_logs_dir: Path | None = None) -> Path:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or OVERLAY_SHADOW_LOGS_DIR
    return overlay_shadow_logs_dir / f"{next_overlay_shadow_log_id(overlay_shadow_logs_dir)}.overlay_shadow_log.json"


def resolve_output_path(path: Path | None, overlay_shadow_logs_dir: Path | None = None) -> Path:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or OVERLAY_SHADOW_LOGS_DIR
    if path is None:
        return default_output_path(overlay_shadow_logs_dir)

    candidate = path if path.is_absolute() else REPO_ROOT / path
    resolved = candidate.resolve()
    logs_dir_resolved = overlay_shadow_logs_dir.resolve()

    if resolved.parent != logs_dir_resolved:
        raise ValueError(f"out must be a file directly under {_repo_relative(logs_dir_resolved)}")

    match = OVERLAY_SHADOW_LOG_NAME_PATTERN.fullmatch(resolved.name)
    if match is None:
        raise ValueError(f"out filename must match OSH-NNNN.overlay_shadow_log.json: {resolved.name}")

    return resolved


def overlay_shadow_log_id_from_path(path: Path) -> str:
    match = OVERLAY_SHADOW_LOG_NAME_PATTERN.fullmatch(path.name)
    if match is None:
        raise ValueError(f"invalid overlay shadow log filename: {path.name}")
    return match.group(1)


def _load_json_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.exists():
        raise ValueError(f"{label} does not exist: {_display_path(resolved)}")
    if not resolved.is_file():
        raise ValueError(f"{label} is not a file: {_display_path(resolved)}")
    try:
        load_json(resolved)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} contains invalid JSON: {_display_path(resolved)}: {exc}") from exc
    return resolved


def resolve_overlay_input_paths(args: argparse.Namespace) -> tuple[str, Path, Path]:
    explicit_snapshot = args.context_snapshot_path
    explicit_config = args.macro_flags_path
    legacy_snapshot = args.snapshot
    legacy_config = args.config

    if (explicit_snapshot is None) != (explicit_config is None):
        raise ValueError(
            "--context-snapshot-path and --macro-flags-path must be supplied together or omitted together"
        )

    if explicit_snapshot is not None and (legacy_snapshot is not None or legacy_config is not None):
        raise ValueError(
            "legacy --snapshot/--config cannot be combined with --context-snapshot-path/--macro-flags-path"
        )

    if explicit_snapshot is not None:
        snapshot_path = _load_json_path(explicit_snapshot, "context snapshot path")
        config_path = _load_json_path(explicit_config, "macro flags path")
        return "explicit", snapshot_path, config_path

    snapshot_path = _require_exact_path(legacy_snapshot or CANONICAL_SNAPSHOT_PATH, CANONICAL_SNAPSHOT_PATH, "snapshot")
    config_path = _require_exact_path(legacy_config or CANONICAL_CONFIG_PATH, CANONICAL_CONFIG_PATH, "config")
    return "canonical", snapshot_path, config_path


def render_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2) + "\n"


def _notes_for_source(advisory_source: str) -> str:
    if advisory_source == "PGAS":
        return (
            "WP-7k manual shadow-run helper. The PGAS combined advisory bucket is advisory-only, "
            "validation-gated, manual/on-demand only, and records comparison evidence only; no scheduler, "
            "trigger, runtime influence, OMS authority, or risk authority are created by this helper."
        )
    return (
        "WP-7k manual shadow-run helper. The bucket-mapping advisory output is advisory-only, "
        "validation-gated, manual/on-demand only, and records comparison evidence only; no scheduler, "
        "trigger, runtime influence, OMS authority, or risk authority are created by this helper."
    )


def _load_bmap_chain(advisory_artifact_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    bucket_mapping_path = BUCKET_MAPPINGS_DIR / f"{advisory_artifact_id}.bucket_mapping.json"
    bucket_mapping = load_json(bucket_mapping_path)
    agent_output = load_json(AGENT_OUTPUTS_DIR / f"{bucket_mapping['source_agent_output_id']}.agent_output.json")
    return bucket_mapping, agent_output


def _load_pgas_chain(advisory_artifact_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pre_gate_path = PRE_GATE_ADVISORY_SNAPSHOTS_DIR / f"{advisory_artifact_id}.pre_gate_advisory_snapshot.json"
    pre_gate_advisory_snapshot = load_json(pre_gate_path)
    bucket_mapping = load_json(
        BUCKET_MAPPINGS_DIR / f"{pre_gate_advisory_snapshot['source_bucket_mapping_id']}.bucket_mapping.json"
    )
    agent_output = load_json(
        AGENT_OUTPUTS_DIR / f"{pre_gate_advisory_snapshot['source_agent_output_id']}.agent_output.json"
    )
    return pre_gate_advisory_snapshot, bucket_mapping, agent_output


def build_candidate_payload(
    *,
    advisory_source: str,
    advisory_artifact_id: str,
    timestamp_utc: str,
    snapshot_path: Path,
    config_path: Path,
    overlay_shadow_log_id: str,
) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    config = load_json(config_path)
    observation = observe_external_overlay_bucket(snapshot=snapshot, config=config, evaluation_time_utc=timestamp_utc)

    if advisory_source == "PGAS":
        pre_gate_advisory_snapshot, bucket_mapping, agent_output = _load_pgas_chain(advisory_artifact_id)
        combined_bucket = pre_gate_advisory_snapshot.get("combined_bucket")
        if combined_bucket not in PERMISSION_TO_MULTIPLIER:
            raise ValueError(f"PGAS combined_bucket must be in the locked bucket domain: {combined_bucket}")
        source_bucket_mapping_id = str(pre_gate_advisory_snapshot["source_bucket_mapping_id"])
        source_agent_output_id = str(pre_gate_advisory_snapshot["source_agent_output_id"])
        mapped_bucket = str(combined_bucket)
        size_multiplier = PERMISSION_TO_MULTIPLIER[mapped_bucket]
        payload = {
            "overlay_shadow_log_id": overlay_shadow_log_id,
            "source_bucket_mapping_id": source_bucket_mapping_id,
            "source_agent_output_id": source_agent_output_id,
            "observed_overlay_bucket": str(observation["observed_overlay_bucket"]),
            "observed_overlay_size_multiplier": observation["observed_overlay_size_multiplier"],
            "mapped_bucket": mapped_bucket,
            "size_multiplier": size_multiplier,
            "comparison_result": (
                "MATCH" if observation["observed_overlay_bucket"] == mapped_bucket else "MISMATCH"
            ),
            "override_applied": False,
            "fail_open_preserved": True,
            "advisory_only": True,
            "observed_at": timestamp_utc,
            "observation_source": {
                "source_type": "committed_macro_context_fixture",
                "snapshot_path": _repo_relative(snapshot_path),
                "config_path": _repo_relative(config_path),
                "evaluation_time_utc": timestamp_utc,
                "decision_id": observation["decision_id"],
                "context_missing": observation["context_missing"],
                "reason_code": observation["reason_code"],
            },
            "notes": _notes_for_source(advisory_source),
            "advisory_source": "PGAS",
            "source_pre_gate_advisory_snapshot_id": str(
                pre_gate_advisory_snapshot["pre_gate_advisory_snapshot_id"]
            ),
        }
        if source_bucket_mapping_id != bucket_mapping.get("bucket_mapping_id"):
            raise ValueError("PGAS source_bucket_mapping_id must match the referenced bucket mapping")
        if source_agent_output_id != agent_output.get("agent_output_id"):
            raise ValueError("PGAS source_agent_output_id must match the referenced agent output")
        return payload

    bucket_mapping, agent_output = _load_bmap_chain(advisory_artifact_id)
    mapped_bucket = str(bucket_mapping["mapped_bucket"])
    payload = {
        "overlay_shadow_log_id": overlay_shadow_log_id,
        "source_bucket_mapping_id": str(bucket_mapping["bucket_mapping_id"]),
        "source_agent_output_id": str(agent_output["agent_output_id"]),
        "observed_overlay_bucket": str(observation["observed_overlay_bucket"]),
        "observed_overlay_size_multiplier": observation["observed_overlay_size_multiplier"],
        "mapped_bucket": mapped_bucket,
        "size_multiplier": bucket_mapping["size_multiplier"],
        "comparison_result": "MATCH" if observation["observed_overlay_bucket"] == mapped_bucket else "MISMATCH",
        "override_applied": False,
        "fail_open_preserved": True,
        "advisory_only": True,
        "observed_at": timestamp_utc,
        "observation_source": {
            "source_type": "committed_macro_context_fixture",
            "snapshot_path": _repo_relative(snapshot_path),
            "config_path": _repo_relative(config_path),
            "evaluation_time_utc": timestamp_utc,
            "decision_id": observation["decision_id"],
            "context_missing": observation["context_missing"],
            "reason_code": observation["reason_code"],
        },
        "notes": _notes_for_source(advisory_source),
    }
    if payload["source_bucket_mapping_id"] != advisory_artifact_id:
        raise ValueError("BMAP advisory_artifact_id must match the referenced bucket mapping")
    if payload["source_agent_output_id"] != bucket_mapping.get("source_agent_output_id"):
        raise ValueError("BMAP source_agent_output_id must match the referenced bucket mapping")
    return payload


def validate_candidate_against_corpus(
    payload: Mapping[str, Any],
    destination_path: Path,
    *,
    overlay_shadow_logs_dir: Path | None = None,
) -> list[str]:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or OVERLAY_SHADOW_LOGS_DIR
    with tempfile.TemporaryDirectory(prefix="shadow-run-helper-") as temp_dir_name:
        temp_overlay_shadow_logs_dir = Path(temp_dir_name) / "overlay_shadow_logs"
        temp_overlay_shadow_logs_dir.mkdir(parents=True, exist_ok=True)

        for existing_path in sorted(overlay_shadow_logs_dir.glob("*.overlay_shadow_log.json")):
            shutil.copyfile(existing_path, temp_overlay_shadow_logs_dir / existing_path.name)

        candidate_path = temp_overlay_shadow_logs_dir / destination_path.name
        candidate_path.write_text(render_payload(payload), encoding="utf-8")
        return validate_overlay_shadow_logs(
            overlay_shadow_logs_dir=temp_overlay_shadow_logs_dir,
            bucket_mappings_dir=BUCKET_MAPPINGS_DIR,
            agent_outputs_dir=AGENT_OUTPUTS_DIR,
            pre_gate_advisory_snapshots_dir=PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
        )


def _write_payload(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_payload(payload), encoding="utf-8")


def _print_validation_errors(errors: Sequence[str]) -> None:
    for error in errors:
        print(f"VALIDATION ERROR: {error}", file=sys.stderr)


def _is_noncanonical_explicit_mode(overlay_input_mode: str, snapshot_path: Path, config_path: Path) -> bool:
    return (
        overlay_input_mode == "explicit"
        and (
            snapshot_path.resolve() != CANONICAL_SNAPSHOT_PATH.resolve()
            or config_path.resolve() != CANONICAL_CONFIG_PATH.resolve()
        )
    )


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        advisory_artifact_id = validate_advisory_artifact_id(args.advisory_source, args.advisory_artifact_id)
        overlay_input_mode, snapshot_path, config_path = resolve_overlay_input_paths(args)
        timestamp_utc = parse_timestamp_utc(args.timestamp)
        destination_path = resolve_output_path(args.out)
        overlay_shadow_log_id = overlay_shadow_log_id_from_path(destination_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.write and destination_path.exists():
        print(f"ERROR: refusing to overwrite existing file: {destination_path}", file=sys.stderr)
        return 1

    noncanonical_explicit_mode = _is_noncanonical_explicit_mode(overlay_input_mode, snapshot_path, config_path)

    if args.write and noncanonical_explicit_mode:
        print(
            "ERROR: noncanonical explicit overlay-input paths cannot be written because the current "
            "overlay_shadow_log schema and validator still lock observation_source.snapshot_path and "
            "observation_source.config_path to the canonical fixture paths",
            file=sys.stderr,
        )
        return 1

    try:
        payload = build_candidate_payload(
            advisory_source=args.advisory_source,
            advisory_artifact_id=advisory_artifact_id,
            timestamp_utc=timestamp_utc,
            snapshot_path=snapshot_path,
            config_path=config_path,
            overlay_shadow_log_id=overlay_shadow_log_id,
        )
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    validation_note: str | None = None
    if noncanonical_explicit_mode:
        validation_note = (
            "Corpus validation skipped because the current overlay_shadow_log schema and validator still "
            "lock observation_source.snapshot_path and observation_source.config_path to the canonical fixtures"
        )
    else:
        errors = validate_candidate_against_corpus(payload, destination_path)

    if not args.write:
        print(render_payload(payload), end="")
        print(f"Proposed output path: {_repo_relative(destination_path)}", file=sys.stderr)
        print(f"Proposed output id: {overlay_shadow_log_id}", file=sys.stderr)
        print(f"Overlay input mode: {overlay_input_mode}", file=sys.stderr)
        print(f"Context snapshot path: {_display_path(snapshot_path)}", file=sys.stderr)
        print(f"Macro flags path: {_display_path(config_path)}", file=sys.stderr)
        if errors:
            print("Validation: FAIL", file=sys.stderr)
            _print_validation_errors(errors)
            return 1
        print("Validation: PASS", file=sys.stderr)
        if validation_note is not None:
            print(f"Validation note: {validation_note}", file=sys.stderr)
        return 0

    if errors:
        print("Validation: FAIL", file=sys.stderr)
        _print_validation_errors(errors)
        return 1

    _write_payload(destination_path, payload)
    print(f"Wrote validated overlay shadow log: {_repo_relative(destination_path)}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
