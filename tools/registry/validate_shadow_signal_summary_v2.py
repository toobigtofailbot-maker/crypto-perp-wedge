"""Validate JSON shadow_signal_summary v2 artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR = REPO_ROOT / "research" / "shadow_signal_summaries_v2"
SHADOW_SIGNAL_SUMMARY_V2_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "shadow_signal_summary_v2.schema.json"
)
DERIVATION_METHOD = "shadow_signal_summary_option_a_floor_10_v1"
DERIVATION_INPUTS = {
    "source_relation": "overlay_shadow_logs",
    "source_artifact_family": "overlay_shadow_logs",
    "fixture_identity_rule": "committed_overlay_input_pair_v1",
    "rate_denominator_rule": "match_plus_mismatch",
}
OBSERVATION_FLOOR = 10
ALLOWED_SEGMENTATION_AXES = {
    (
        "advisory_source",
        "source_bucket_mapping_id",
        "source_pre_gate_advisory_snapshot_id",
        "fixture_identity",
    ),
    ("advisory_source",),
    ("fixture_identity",),
    ("advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id"),
}


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


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _segment_key(segment: dict[str, Any], axes: tuple[str, ...]) -> tuple[Any, ...]:
    return tuple(segment.get(axis) for axis in axes)


def _segment_sort_key(segment: dict[str, Any], axes: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for axis in axes:
        value = segment.get(axis)
        normalized.append("" if value is None else str(value))
    return tuple(normalized)


def validate_shadow_signal_summary_v2(
    shadow_signal_summaries_v2_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    schema_path: Path = SHADOW_SIGNAL_SUMMARY_V2_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for shadow_signal_summary v2 artifacts, or [] when valid."""

    if not shadow_signal_summaries_v2_dir.exists():
        return []

    summary_files = sorted(shadow_signal_summaries_v2_dir.rglob("*.shadow_signal_summary.json"))
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

        schema_version = payload.get("schema_version")
        if schema_version != "v2":
            errors.append(f"{path}: schema_version must be 'v2', got {schema_version!r}")

        axes_value = payload.get("segmentation_axes")
        axes = tuple(axes_value) if isinstance(axes_value, list) else ()
        if axes not in ALLOWED_SEGMENTATION_AXES:
            errors.append(f"{path}: unsupported segmentation_axes {axes_value!r}")
            continue

        generated_at = payload.get("generated_at")
        corpus_window = payload.get("corpus_window")
        if not isinstance(corpus_window, dict):
            errors.append(f"{path}: missing valid corpus_window")
            continue

        if payload.get("derivation_method") != DERIVATION_METHOD:
            errors.append(
                f"{path}: derivation_method must be {DERIVATION_METHOD!r}, "
                f"got {payload.get('derivation_method')!r}"
            )
        if payload.get("derivation_inputs") != DERIVATION_INPUTS:
            errors.append(f"{path}: derivation_inputs must match the locked v1 derivation inputs")

        corpus_first = _parse_timestamp(corpus_window.get("first_observed_at"))
        corpus_last = _parse_timestamp(corpus_window.get("last_observed_at"))
        generated_dt = _parse_timestamp(generated_at)
        if generated_at != corpus_window.get("last_observed_at"):
            errors.append(
                f"{path}: generated_at must equal corpus_window.last_observed_at, "
                f"got {generated_at!r} vs {corpus_window.get('last_observed_at')!r}"
            )
        if (
            corpus_first is not None
            and corpus_last is not None
            and corpus_first > corpus_last
        ):
            errors.append(
                f"{path}: corpus_window.first_observed_at must be <= last_observed_at"
            )
        if generated_dt is None:
            errors.append(f"{path}: generated_at is not a valid timestamp")

        segments = payload.get("segments")
        if not isinstance(segments, list):
            errors.append(f"{path}: segments must be a list")
            continue

        seen_keys: dict[tuple[Any, ...], int] = {}
        observed_sort_keys: list[tuple[str, ...]] = []
        total_observation_count = 0

        for index, segment in enumerate(segments):
            if not isinstance(segment, dict):
                errors.append(f"{path}: segments[{index}] must be an object")
                continue

            key = _segment_key(segment, axes)
            if key in seen_keys:
                errors.append(
                    f"{path}: duplicate segment key at segments[{index}] and "
                    f"segments[{seen_keys[key]}] for axes {list(axes)}"
                )
            else:
                seen_keys[key] = index

            observed_sort_keys.append(_segment_sort_key(segment, axes))

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
                total_observation_count += observation_count

            if isinstance(observation_count, int):
                insufficient_evidence = segment.get("insufficient_evidence")
                signal_outcome = segment.get("signal_outcome")
                agreement_rate = segment.get("agreement_rate")
                disagreement_rate = segment.get("disagreement_rate")
                (
                    expected_insufficient,
                    expected_outcome,
                    expected_agreement_rate,
                    expected_disagreement_rate,
                ) = _signal_state(
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

            segment_first = _parse_timestamp(segment.get("first_observed_at"))
            segment_last = _parse_timestamp(segment.get("last_observed_at"))
            if segment_first is None or segment_last is None:
                errors.append(
                    f"{path}: segments[{index}] has invalid first_observed_at/last_observed_at"
                )
            else:
                if segment_first > segment_last:
                    errors.append(
                        f"{path}: segments[{index}].first_observed_at must be <= last_observed_at"
                    )
                if corpus_first is not None and segment_first < corpus_first:
                    errors.append(
                        f"{path}: segments[{index}].first_observed_at is before corpus window"
                    )
                if corpus_last is not None and segment_last > corpus_last:
                    errors.append(
                        f"{path}: segments[{index}].last_observed_at is after corpus window"
                    )

        expected_total = corpus_window.get("total_source_observation_count")
        if total_observation_count != expected_total:
            errors.append(
                f"{path}: total segment observation_count should equal "
                f"corpus_window.total_source_observation_count ({expected_total}), "
                f"got {total_observation_count}"
            )

        if observed_sort_keys != sorted(observed_sort_keys):
            errors.append(
                f"{path}: segments are not in deterministic order for axes {list(axes)}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--shadow-signal-summaries-v2-dir",
        type=Path,
        default=DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    )
    parser.add_argument("--schema", type=Path, default=SHADOW_SIGNAL_SUMMARY_V2_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_shadow_signal_summary_v2(
        shadow_signal_summaries_v2_dir=args.shadow_signal_summaries_v2_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.shadow_signal_summaries_v2_dir.exists():
        print(f"OK: {args.shadow_signal_summaries_v2_dir} does not exist; nothing to validate")
    else:
        print(
            "OK: shadow_signal_summary v2 artifacts under "
            f"{args.shadow_signal_summaries_v2_dir} validate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
