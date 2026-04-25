import json
from pathlib import Path

from jsonschema import Draft7Validator

from tools.registry.validate_shadow_signal_summaries import validate_shadow_signal_summaries
from tools.registry.validate_shadow_signal_summary_v2 import (
    DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    SHADOW_SIGNAL_SUMMARY_V2_SCHEMA_PATH,
    validate_shadow_signal_summary_v2,
)


def _load_schema(path: Path = SHADOW_SIGNAL_SUMMARY_V2_SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema_payload(payload: dict) -> list[str]:
    schema = _load_schema()
    Draft7Validator.check_schema(schema)
    return [error.message for error in Draft7Validator(schema).iter_errors(payload)]


def _base_payload(segmentation_axes: list[str], segments: list[dict]) -> dict:
    total_observation_count = sum(segment["observation_count"] for segment in segments)
    return {
        "shadow_signal_summary_id": "SSS-9000",
        "schema_version": "v2",
        "generated_at": "2026-04-22T08:00:00Z",
        "corpus_window": {
            "first_overlay_shadow_log_id": "OSH-0001",
            "last_overlay_shadow_log_id": "OSH-0010",
            "first_observed_at": "2026-04-19T17:00:00Z",
            "last_observed_at": "2026-04-22T08:00:00Z",
            "total_source_observation_count": total_observation_count,
        },
        "derivation_method": "shadow_signal_summary_option_a_floor_10_v1",
        "segmentation_axes": segmentation_axes,
        "derivation_inputs": {
            "source_relation": "overlay_shadow_logs",
            "source_artifact_family": "overlay_shadow_logs",
            "fixture_identity_rule": "committed_overlay_input_pair_v1",
            "rate_denominator_rule": "match_plus_mismatch",
        },
        "segments": segments,
        "deterministic": True,
        "advisory_only": True,
        "notes": (
            "WP-7z additive SSS v2 schema family for four-axis compatibility and "
            "coherent single-axis segmentation forms only."
        ),
    }


def _source_only_segment(
    *,
    advisory_source: str,
    match_count: int,
    mismatch_count: int,
    abstention_count: int,
    first_observed_at: str = "2026-04-19T17:00:00Z",
    last_observed_at: str = "2026-04-22T08:00:00Z",
) -> dict:
    observation_count = match_count + mismatch_count + abstention_count
    rate_denominator = match_count + mismatch_count
    insufficient = observation_count < 10
    if insufficient:
        signal_outcome = "INSUFFICIENT_EVIDENCE"
        agreement_rate = None
        disagreement_rate = None
    elif match_count > mismatch_count:
        signal_outcome = "AGREEMENT_SIGNAL"
        agreement_rate = match_count / rate_denominator
        disagreement_rate = mismatch_count / rate_denominator
    elif mismatch_count > match_count:
        signal_outcome = "DISAGREEMENT_SIGNAL"
        agreement_rate = match_count / rate_denominator
        disagreement_rate = mismatch_count / rate_denominator
    else:
        signal_outcome = "MIXED_SIGNAL"
        agreement_rate = match_count / rate_denominator
        disagreement_rate = mismatch_count / rate_denominator
    return {
        "advisory_source": advisory_source,
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "abstention_count": abstention_count,
        "observation_count": observation_count,
        "rate_denominator": rate_denominator,
        "agreement_rate": agreement_rate,
        "disagreement_rate": disagreement_rate,
        "insufficient_evidence": insufficient,
        "signal_outcome": signal_outcome,
        "first_observed_at": first_observed_at,
        "last_observed_at": last_observed_at,
    }


def _fixture_only_segment(
    *,
    fixture_identity: str,
    match_count: int,
    mismatch_count: int,
    abstention_count: int,
) -> dict:
    segment = _source_only_segment(
        advisory_source="BMAP",
        match_count=match_count,
        mismatch_count=mismatch_count,
        abstention_count=abstention_count,
    )
    segment.pop("advisory_source")
    segment["fixture_identity"] = fixture_identity
    return segment


def _lineage_segment(
    *,
    advisory_source: str,
    source_bucket_mapping_id: str,
    source_pre_gate_advisory_snapshot_id,
    match_count: int,
    mismatch_count: int,
    abstention_count: int,
) -> dict:
    segment = _source_only_segment(
        advisory_source=advisory_source,
        match_count=match_count,
        mismatch_count=mismatch_count,
        abstention_count=abstention_count,
    )
    segment["source_bucket_mapping_id"] = source_bucket_mapping_id
    segment["source_pre_gate_advisory_snapshot_id"] = source_pre_gate_advisory_snapshot_id
    return segment


def _four_axis_segment(
    *,
    advisory_source: str,
    source_bucket_mapping_id: str,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity: str,
    match_count: int,
    mismatch_count: int,
    abstention_count: int,
) -> dict:
    segment = _lineage_segment(
        advisory_source=advisory_source,
        source_bucket_mapping_id=source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id=source_pre_gate_advisory_snapshot_id,
        match_count=match_count,
        mismatch_count=mismatch_count,
        abstention_count=abstention_count,
    )
    segment["fixture_identity"] = fixture_identity
    return segment


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_shadow_signal_summary_v2_schema_meta_valid():
    Draft7Validator.check_schema(_load_schema())


def test_valid_minimal_advisory_source_only_v2_payload_passes_schema():
    payload = _base_payload(
        ["advisory_source"],
        [_source_only_segment(advisory_source="BMAP", match_count=6, mismatch_count=4, abstention_count=0)],
    )

    errors = _validate_schema_payload(payload)

    assert errors == []


def test_valid_four_axis_v2_payload_passes_validator(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        [
            "advisory_source",
            "source_bucket_mapping_id",
            "source_pre_gate_advisory_snapshot_id",
            "fixture_identity",
        ],
        [
            _four_axis_segment(
                advisory_source="BMAP",
                source_bucket_mapping_id="BMAP-0001",
                source_pre_gate_advisory_snapshot_id=None,
                fixture_identity="_02",
                match_count=0,
                mismatch_count=4,
                abstention_count=0,
            ),
            _four_axis_segment(
                advisory_source="PGAS",
                source_bucket_mapping_id="BMAP-0001",
                source_pre_gate_advisory_snapshot_id="PGAS-0002",
                fixture_identity="canonical",
                match_count=3,
                mismatch_count=3,
                abstention_count=0,
            ),
        ],
    )
    payload["shadow_signal_summary_id"] = "SSS-9001"
    _write_json(summaries_dir / "SSS-9001.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert errors == []


def test_valid_fixture_only_v2_payload_passes_validator(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        ["fixture_identity"],
        [_fixture_only_segment(fixture_identity="canonical", match_count=5, mismatch_count=5, abstention_count=0)],
    )
    payload["shadow_signal_summary_id"] = "SSS-9002"
    _write_json(summaries_dir / "SSS-9002.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert errors == []


def test_valid_advisory_lineage_v2_payload_passes_validator(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        ["advisory_source", "source_bucket_mapping_id", "source_pre_gate_advisory_snapshot_id"],
        [
            _lineage_segment(
                advisory_source="BMAP",
                source_bucket_mapping_id="BMAP-0001",
                source_pre_gate_advisory_snapshot_id=None,
                match_count=4,
                mismatch_count=4,
                abstention_count=1,
            ),
            _lineage_segment(
                advisory_source="PGAS",
                source_bucket_mapping_id="BMAP-0002",
                source_pre_gate_advisory_snapshot_id="PGAS-0003",
                match_count=1,
                mismatch_count=1,
                abstention_count=1,
            ),
        ],
    )
    payload["shadow_signal_summary_id"] = "SSS-9003"
    payload["corpus_window"]["total_source_observation_count"] = 12
    _write_json(summaries_dir / "SSS-9003.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert errors == []


def test_shadow_signal_summary_v2_validator_noops_when_directory_missing(tmp_path):
    missing_dir = tmp_path / "missing_shadow_signal_summaries_v2"

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=missing_dir)

    assert errors == []


def test_validator_rejects_missing_or_wrong_schema_version(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    base = _base_payload(
        ["advisory_source"],
        [_source_only_segment(advisory_source="BMAP", match_count=6, mismatch_count=4, abstention_count=0)],
    )

    missing = dict(base)
    missing["shadow_signal_summary_id"] = "SSS-9010"
    missing.pop("schema_version")
    _write_json(summaries_dir / "SSS-9010.shadow_signal_summary.json", missing)

    wrong = dict(base)
    wrong["shadow_signal_summary_id"] = "SSS-9011"
    wrong["schema_version"] = "v1"
    _write_json(summaries_dir / "SSS-9011.shadow_signal_summary.json", wrong)

    other = dict(base)
    other["shadow_signal_summary_id"] = "SSS-9012"
    other["schema_version"] = "v3"
    _write_json(summaries_dir / "SSS-9012.shadow_signal_summary.json", other)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert any("schema_version must be 'v2'" in error for error in errors)
    assert any("SSS-9011.shadow_signal_summary.json" in error for error in errors)
    assert any("SSS-9012.shadow_signal_summary.json" in error for error in errors)


def test_validator_rejects_mismatched_segmentation_axes_vs_segment_shape(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        ["advisory_source"],
        [
            {
                **_source_only_segment(
                    advisory_source="BMAP",
                    match_count=6,
                    mismatch_count=4,
                    abstention_count=0,
                ),
                "fixture_identity": "canonical",
            }
        ],
    )
    payload["shadow_signal_summary_id"] = "SSS-9020"
    _write_json(summaries_dir / "SSS-9020.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert any("is not valid under any of the given schemas" in error for error in errors)


def test_validator_rejects_duplicate_segment_keys(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    segment = _source_only_segment(advisory_source="BMAP", match_count=5, mismatch_count=4, abstention_count=0)
    payload = _base_payload(["advisory_source"], [segment, dict(segment)])
    payload["shadow_signal_summary_id"] = "SSS-9030"
    payload["corpus_window"]["total_source_observation_count"] = 18
    _write_json(summaries_dir / "SSS-9030.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert any("duplicate segment key" in error for error in errors)


def test_validator_rejects_count_rate_floor_timestamp_and_corpus_window_drift(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        ["advisory_source"],
        [_source_only_segment(advisory_source="BMAP", match_count=6, mismatch_count=4, abstention_count=0)],
    )
    payload["shadow_signal_summary_id"] = "SSS-9040"
    payload["generated_at"] = "2026-04-22T07:00:00Z"
    payload["segments"][0]["observation_count"] = 99
    payload["segments"][0]["agreement_rate"] = 0.5
    payload["segments"][0]["first_observed_at"] = "2026-04-18T17:00:00Z"
    payload["corpus_window"]["total_source_observation_count"] = 5
    _write_json(summaries_dir / "SSS-9040.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert any("generated_at must equal corpus_window.last_observed_at" in error for error in errors)
    assert any("observation_count should be" in error for error in errors)
    assert any("agreement_rate should be" in error for error in errors)
    assert any("is before corpus window" in error for error in errors)
    assert any("total segment observation_count should equal" in error for error in errors)


def test_validator_rejects_unsorted_segments(tmp_path):
    summaries_dir = tmp_path / "research" / "shadow_signal_summaries_v2"
    payload = _base_payload(
        ["advisory_source"],
        [
            _source_only_segment(advisory_source="PGAS", match_count=6, mismatch_count=4, abstention_count=0),
            _source_only_segment(advisory_source="BMAP", match_count=6, mismatch_count=4, abstention_count=0),
        ],
    )
    payload["shadow_signal_summary_id"] = "SSS-9050"
    payload["corpus_window"]["total_source_observation_count"] = 20
    _write_json(summaries_dir / "SSS-9050.shadow_signal_summary.json", payload)

    errors = validate_shadow_signal_summary_v2(shadow_signal_summaries_v2_dir=summaries_dir)

    assert any("segments are not in deterministic order" in error for error in errors)


def test_v1_validator_still_accepts_committed_sss_v1_instance():
    errors = validate_shadow_signal_summaries()

    assert errors == []


def test_v1_behavior_remains_unchanged_after_v2_addition():
    errors = validate_shadow_signal_summaries()

    assert errors == []
