"""Validate JSON shadow_signal_summary artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR = REPO_ROOT / "research" / "shadow_signal_summaries"
DEFAULT_OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
SHADOW_SIGNAL_SUMMARY_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "shadow_signal_summary.schema.json"
)
DERIVATION_METHOD = "shadow_signal_summary_option_a_floor_10_v1"
SEGMENTATION_AXES = [
    "advisory_source",
    "source_bucket_mapping_id",
    "source_pre_gate_advisory_snapshot_id",
    "fixture_identity",
]
DERIVATION_INPUTS = {
    "source_relation": "overlay_shadow_logs",
    "source_artifact_family": "overlay_shadow_logs",
    "fixture_identity_rule": "committed_overlay_input_pair_v1",
    "rate_denominator_rule": "match_plus_mismatch",
}
OBSERVATION_FLOOR = 10
CANONICAL_SNAPSHOT_PATH = "tests/fixtures/context_snapshot_sample.json"
CANONICAL_CONFIG_PATH = "configs/fmp_macro_flags.json"
FIXTURE_02_SNAPSHOT_PATH = "tests/fixtures/context_snapshot_sample_02.json"
FIXTURE_02_CONFIG_PATH = "configs/fmp_macro_flags_02.json"


@dataclass(frozen=True)
class SegmentKey:
    advisory_source: str
    source_bucket_mapping_id: str
    source_pre_gate_advisory_snapshot_id: str | None
    fixture_identity: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(
    path: Path,
    validator: Draft7Validator,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path)):
        errors.append(f"{path}: {_format_schema_error(schema_error)}")
    return payload, errors


def normalize_fixture_identity(snapshot_path: str, config_path: str) -> str:
    if snapshot_path == CANONICAL_SNAPSHOT_PATH and config_path == CANONICAL_CONFIG_PATH:
        return "canonical"
    if snapshot_path == FIXTURE_02_SNAPSHOT_PATH and config_path == FIXTURE_02_CONFIG_PATH:
        return "_02"
    raise ValueError(
        "unknown fixture identity pair: "
        f"snapshot_path={snapshot_path!r}, config_path={config_path!r}"
    )


def _format_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _signal_state(
    match_count: int,
    mismatch_count: int,
    observation_count: int,
) -> tuple[bool, str, float | None, float | None]:
    denominator = match_count + mismatch_count
    if observation_count < OBSERVATION_FLOOR:
        return True, "INSUFFICIENT_EVIDENCE", None, None
    if match_count > mismatch_count:
        outcome = "AGREEMENT_SIGNAL"
    elif mismatch_count > match_count:
        outcome = "DISAGREEMENT_SIGNAL"
    else:
        outcome = "MIXED_SIGNAL"
    return (
        False,
        outcome,
        _format_rate(match_count, denominator),
        _format_rate(mismatch_count, denominator),
    )


def derive_shadow_signal_summary_payload(
    *,
    shadow_signal_summary_id: str,
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
) -> dict[str, Any]:
    shadow_log_files = sorted(overlay_shadow_logs_dir.glob("*.overlay_shadow_log.json"))
    if not shadow_log_files:
        raise ValueError(f"no overlay shadow logs found under {overlay_shadow_logs_dir}")

    shadow_logs: list[dict[str, Any]] = []
    for path in shadow_log_files:
        payload = load_json(path)
        payload["_path"] = path
        shadow_logs.append(payload)

    shadow_logs.sort(
        key=lambda payload: (
            payload["observed_at"],
            payload["overlay_shadow_log_id"],
        )
    )

    segments: dict[SegmentKey, dict[str, Any]] = {}
    for payload in shadow_logs:
        observation_source = payload.get("observation_source", {})
        fixture_identity = normalize_fixture_identity(
            observation_source.get("snapshot_path", ""),
            observation_source.get("config_path", ""),
        )
        key = SegmentKey(
            advisory_source=payload.get("advisory_source") or "BMAP",
            source_bucket_mapping_id=payload["source_bucket_mapping_id"],
            source_pre_gate_advisory_snapshot_id=payload.get("source_pre_gate_advisory_snapshot_id"),
            fixture_identity=fixture_identity,
        )
        segment = segments.setdefault(
            key,
            {
                "advisory_source": key.advisory_source,
                "source_bucket_mapping_id": key.source_bucket_mapping_id,
                "source_pre_gate_advisory_snapshot_id": key.source_pre_gate_advisory_snapshot_id,
                "fixture_identity": key.fixture_identity,
                "match_count": 0,
                "mismatch_count": 0,
                "abstention_count": 0,
                "observation_count": 0,
                "rate_denominator": 0,
                "agreement_rate": None,
                "disagreement_rate": None,
                "insufficient_evidence": True,
                "signal_outcome": "INSUFFICIENT_EVIDENCE",
                "first_observed_at": payload["observed_at"],
                "last_observed_at": payload["observed_at"],
            },
        )
        if payload.get("comparison_result") == "MATCH":
            segment["match_count"] += 1
        elif payload.get("comparison_result") == "MISMATCH":
            segment["mismatch_count"] += 1
        else:
            segment["abstention_count"] += 1
        segment["observation_count"] += 1
        segment["rate_denominator"] = segment["match_count"] + segment["mismatch_count"]
        segment["last_observed_at"] = payload["observed_at"]

    sorted_segments = [
        segments[key]
        for key in sorted(
            segments,
            key=lambda item: (
                item.advisory_source,
                item.source_bucket_mapping_id,
                item.source_pre_gate_advisory_snapshot_id or "",
                item.fixture_identity,
            ),
        )
    ]
    for segment in sorted_segments:
        (
            segment["insufficient_evidence"],
            segment["signal_outcome"],
            segment["agreement_rate"],
            segment["disagreement_rate"],
        ) = _signal_state(
            match_count=segment["match_count"],
            mismatch_count=segment["mismatch_count"],
            observation_count=segment["observation_count"],
        )

    first_payload = shadow_logs[0]
    last_payload = shadow_logs[-1]
    return {
        "shadow_signal_summary_id": shadow_signal_summary_id,
        "generated_at": last_payload["observed_at"],
        "corpus_window": {
            "first_overlay_shadow_log_id": first_payload["overlay_shadow_log_id"],
            "last_overlay_shadow_log_id": last_payload["overlay_shadow_log_id"],
            "first_observed_at": first_payload["observed_at"],
            "last_observed_at": last_payload["observed_at"],
            "total_source_observation_count": len(shadow_logs),
        },
        "derivation_method": DERIVATION_METHOD,
        "segmentation_axes": SEGMENTATION_AXES,
        "derivation_inputs": DERIVATION_INPUTS,
        "segments": sorted_segments,
        "deterministic": True,
        "advisory_only": True,
        "notes": (
            "WP-7t descriptive-only shadow-signal summary over committed overlay shadow logs. "
            "It locks Option A with a static floor of 10 observations per segment, encodes "
            "insufficiency machine-readably, and grants no runtime, overlay, OMS, risk, or "
            "policy authority."
        ),
    }


def validate_shadow_signal_summaries(
    shadow_signal_summaries_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    schema_path: Path = SHADOW_SIGNAL_SUMMARY_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for shadow_signal_summary artifacts, or [] when valid."""

    if not shadow_signal_summaries_dir.exists():
        return []

    summary_files = sorted(shadow_signal_summaries_dir.rglob("*.shadow_signal_summary.json"))
    if not summary_files:
        return []

    errors: list[str] = []
    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    known_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in summary_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue

        summary_id = payload.get("shadow_signal_summary_id")
        if isinstance(summary_id, str):
            expected_name = f"{summary_id}.shadow_signal_summary.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if summary_id in known_ids:
                errors.append(
                    f"{path}: duplicate shadow_signal_summary_id {summary_id}; "
                    f"first seen at {id_paths[summary_id]}"
                )
            known_ids.add(summary_id)
            id_paths.setdefault(summary_id, path)
        else:
            errors.append(f"{path}: missing valid shadow_signal_summary_id")
            continue

        try:
            expected_payload = derive_shadow_signal_summary_payload(
                shadow_signal_summary_id=summary_id,
                overlay_shadow_logs_dir=overlay_shadow_logs_dir,
            )
        except (ValueError, KeyError) as exc:
            errors.append(f"{path}: cannot derive expected summary: {exc}")
            continue

        for index, segment in enumerate(payload.get("segments", [])):
            match_count = segment.get("match_count")
            mismatch_count = segment.get("mismatch_count")
            abstention_count = segment.get("abstention_count")
            observation_count = segment.get("observation_count")
            rate_denominator = segment.get("rate_denominator")
            if isinstance(match_count, int) and isinstance(mismatch_count, int):
                expected_denominator = match_count + mismatch_count
                if rate_denominator != expected_denominator:
                    errors.append(
                        f"{path}: segments[{index}].rate_denominator should be "
                        f"{expected_denominator}, got {rate_denominator}"
                    )
            if (
                isinstance(match_count, int)
                and isinstance(mismatch_count, int)
                and isinstance(abstention_count, int)
                and isinstance(observation_count, int)
            ):
                expected_observation_count = match_count + mismatch_count + abstention_count
                if observation_count != expected_observation_count:
                    errors.append(
                        f"{path}: segments[{index}].observation_count should be "
                        f"{expected_observation_count}, got {observation_count}"
                    )
            if isinstance(observation_count, int):
                insufficient_evidence = segment.get("insufficient_evidence")
                signal_outcome = segment.get("signal_outcome")
                agreement_rate = segment.get("agreement_rate")
                disagreement_rate = segment.get("disagreement_rate")
                expected_insufficient, expected_outcome, expected_agreement_rate, expected_disagreement_rate = _signal_state(
                    match_count=int(match_count or 0),
                    mismatch_count=int(mismatch_count or 0),
                    observation_count=observation_count,
                )
                if insufficient_evidence != expected_insufficient:
                    errors.append(
                        f"{path}: segments[{index}].insufficient_evidence should be "
                        f"{expected_insufficient}, got {insufficient_evidence}"
                    )
                if signal_outcome != expected_outcome:
                    errors.append(
                        f"{path}: segments[{index}].signal_outcome should be "
                        f"{expected_outcome}, got {signal_outcome}"
                    )
                if agreement_rate != expected_agreement_rate:
                    errors.append(
                        f"{path}: segments[{index}].agreement_rate should be "
                        f"{expected_agreement_rate}, got {agreement_rate}"
                    )
                if disagreement_rate != expected_disagreement_rate:
                    errors.append(
                        f"{path}: segments[{index}].disagreement_rate should be "
                        f"{expected_disagreement_rate}, got {disagreement_rate}"
                    )

        if payload != expected_payload:
            errors.append(f"{path}: payload does not match deterministic derivation from overlay shadow logs")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--shadow-signal-summaries-dir",
        type=Path,
        default=DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    )
    parser.add_argument(
        "--overlay-shadow-logs-dir",
        type=Path,
        default=DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    )
    parser.add_argument("--schema", type=Path, default=SHADOW_SIGNAL_SUMMARY_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_shadow_signal_summaries(
        shadow_signal_summaries_dir=args.shadow_signal_summaries_dir,
        overlay_shadow_logs_dir=args.overlay_shadow_logs_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.shadow_signal_summaries_dir.exists():
        print(f"OK: {args.shadow_signal_summaries_dir} does not exist; nothing to validate")
    else:
        print(
            "OK: shadow_signal_summary artifacts under "
            f"{args.shadow_signal_summaries_dir} validate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
