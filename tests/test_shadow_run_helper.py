import shutil
from pathlib import Path

import pytest

from tools.shadow import shadow_run_helper as helper


def _canonical_args(*, advisory_source: str, advisory_artifact_id: str, timestamp: str) -> list[str]:
    return [
        "--advisory-source",
        advisory_source,
        "--advisory-artifact-id",
        advisory_artifact_id,
        "--snapshot",
        str(helper.CANONICAL_SNAPSHOT_PATH),
        "--config",
        str(helper.CANONICAL_CONFIG_PATH),
        "--timestamp",
        timestamp,
    ]


def _copy_committed_overlay_shadow_logs(destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(helper.OVERLAY_SHADOW_LOGS_DIR.glob("*.overlay_shadow_log.json")):
        shutil.copyfile(path, destination_dir / path.name)


def _patched_repo_relative(path: Path) -> str:
    resolved = path.resolve()
    if resolved == helper.CANONICAL_SNAPSHOT_PATH.resolve():
        return "tests/fixtures/context_snapshot_sample.json"
    if resolved == helper.CANONICAL_CONFIG_PATH.resolve():
        return "configs/fmp_macro_flags.json"
    return resolved.as_posix()


def _overlay_shadow_log_path(overlay_shadow_logs_dir: Path, overlay_shadow_log_id: str) -> Path:
    return overlay_shadow_logs_dir / f"{overlay_shadow_log_id}.overlay_shadow_log.json"


def _next_output_path(overlay_shadow_logs_dir: Path | None = None) -> Path:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or helper.OVERLAY_SHADOW_LOGS_DIR
    overlay_shadow_log_id = helper.next_overlay_shadow_log_id(overlay_shadow_logs_dir)
    return _overlay_shadow_log_path(overlay_shadow_logs_dir, overlay_shadow_log_id)


def test_cli_rejects_unsupported_advisory_source():
    with pytest.raises(SystemExit):
        helper.run(
            [
                "--advisory-source",
                "NOPE",
                "--advisory-artifact-id",
                "BMAP-0001",
                "--snapshot",
                str(helper.CANONICAL_SNAPSHOT_PATH),
                "--config",
                str(helper.CANONICAL_CONFIG_PATH),
                "--timestamp",
                "2026-04-22T00:00:00Z",
            ]
        )


def test_cli_rejects_missing_required_args():
    with pytest.raises(SystemExit):
        helper.run(["--advisory-source", "BMAP"])


@pytest.mark.parametrize(
    ("advisory_source", "advisory_artifact_id"),
    [("BMAP", "PGAS-0002"), ("PGAS", "BMAP-0001"), ("BMAP", "BMAP-12")],
)
def test_validate_advisory_artifact_id_rejects_malformed_values(advisory_source: str, advisory_artifact_id: str):
    with pytest.raises(ValueError):
        helper.validate_advisory_artifact_id(advisory_source, advisory_artifact_id)


@pytest.mark.parametrize(
    "timestamp",
    ["not-a-timestamp", "2026-04-22T00:00:00", "2026-04-22T00:00:00-05:00"],
)
def test_parse_timestamp_utc_rejects_invalid_values(timestamp: str):
    with pytest.raises(ValueError):
        helper.parse_timestamp_utc(timestamp)


def test_run_rejects_noncanonical_snapshot_and_config(tmp_path, capsys):
    snapshot_path = tmp_path / "snapshot.json"
    config_path = tmp_path / "config.json"
    snapshot_path.write_text("{}", encoding="utf-8")
    config_path.write_text("{}", encoding="utf-8")

    exit_code = helper.run(
        [
            "--advisory-source",
            "BMAP",
            "--advisory-artifact-id",
            "BMAP-0001",
            "--snapshot",
            str(snapshot_path),
            "--config",
            str(config_path),
            "--timestamp",
            "2026-04-22T00:00:00Z",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "snapshot must resolve to" in captured.err


def test_resolve_output_path_rejects_invalid_filename():
    with pytest.raises(ValueError):
        helper.resolve_output_path(helper.OVERLAY_SHADOW_LOGS_DIR / "invalid.json")


def test_resolve_output_path_rejects_path_outside_committed_dir(tmp_path):
    with pytest.raises(ValueError):
        helper.resolve_output_path(tmp_path / "OSH-0003.overlay_shadow_log.json")


def test_next_overlay_shadow_log_id_advances_past_current_committed_corpus():
    committed_ids = [
        int(path.stem.split(".")[0].split("-")[1])
        for path in helper.OVERLAY_SHADOW_LOGS_DIR.glob("OSH-*.overlay_shadow_log.json")
    ]

    expected = f"OSH-{max(committed_ids) + 1:04d}"

    assert helper.next_overlay_shadow_log_id() == expected


def test_bmap_payload_generation_is_byte_identical_for_identical_inputs():
    payload_a = helper.build_candidate_payload(
        advisory_source="BMAP",
        advisory_artifact_id="BMAP-0001",
        timestamp_utc="2026-04-22T00:00:00Z",
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id="OSH-9999",
    )
    payload_b = helper.build_candidate_payload(
        advisory_source="BMAP",
        advisory_artifact_id="BMAP-0001",
        timestamp_utc="2026-04-22T00:00:00Z",
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id="OSH-9999",
    )

    assert helper.render_payload(payload_a) == helper.render_payload(payload_b)


def test_bmap_payload_uses_explicit_timestamp_and_omits_advisory_source():
    payload = helper.build_candidate_payload(
        advisory_source="BMAP",
        advisory_artifact_id="BMAP-0001",
        timestamp_utc="2026-04-22T00:00:00Z",
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id="OSH-9999",
    )

    assert payload["observed_at"] == "2026-04-22T00:00:00Z"
    assert payload["observation_source"]["evaluation_time_utc"] == "2026-04-22T00:00:00Z"
    assert "advisory_source" not in payload
    assert "source_pre_gate_advisory_snapshot_id" not in payload


def test_pgas_payload_uses_committed_combined_bucket_without_recomputation():
    payload = helper.build_candidate_payload(
        advisory_source="PGAS",
        advisory_artifact_id="PGAS-0002",
        timestamp_utc="2026-04-22T00:00:00Z",
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id="OSH-9999",
    )

    assert payload["advisory_source"] == "PGAS"
    assert payload["source_pre_gate_advisory_snapshot_id"] == "PGAS-0002"
    assert payload["mapped_bucket"] == "ALLOW_REDUCED"
    assert payload["size_multiplier"] == 0.5
    assert payload["observed_at"] == "2026-04-22T00:00:00Z"
    assert payload["observation_source"]["evaluation_time_utc"] == "2026-04-22T00:00:00Z"


def test_dry_run_prints_candidate_and_writes_nothing(capsys):
    expected_path = _next_output_path()
    expected_id = expected_path.stem.split(".")[0]
    assert not expected_path.exists()

    exit_code = helper.run(
        _canonical_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
        )
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f'"overlay_shadow_log_id": "{expected_id}"' in captured.out
    assert f"Proposed output path: research/overlay_shadow_logs/{expected_id}.overlay_shadow_log.json" in captured.err
    assert f"Proposed output id: {expected_id}" in captured.err
    assert "Validation: PASS" in captured.err
    assert not expected_path.exists()


def test_validation_against_corpus_catches_duplicate_overlay_shadow_log_id():
    payload = helper.build_candidate_payload(
        advisory_source="BMAP",
        advisory_artifact_id="BMAP-0001",
        timestamp_utc="2026-04-22T00:00:00Z",
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id="OSH-0001",
    )

    errors = helper.validate_candidate_against_corpus(
        payload,
        helper.OVERLAY_SHADOW_LOGS_DIR / "OSH-9999.overlay_shadow_log.json",
    )

    assert any("duplicate overlay_shadow_log_id OSH-0001" in error for error in errors)


def test_write_mode_refuses_overwrite_existing_file(tmp_path, capsys, monkeypatch):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    _copy_committed_overlay_shadow_logs(overlay_shadow_logs_dir)
    existing_path = _next_output_path(overlay_shadow_logs_dir)
    existing_path.write_text("already here\n", encoding="utf-8")
    monkeypatch.setattr(helper, "OVERLAY_SHADOW_LOGS_DIR", overlay_shadow_logs_dir)

    exit_code = helper.run(
        _canonical_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
        )
        + ["--out", str(existing_path), "--write"]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "refusing to overwrite existing file" in captured.err
    assert existing_path.read_text(encoding="utf-8") == "already here\n"


def test_write_mode_fails_without_writing_when_validation_fails(tmp_path, capsys, monkeypatch):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    _copy_committed_overlay_shadow_logs(overlay_shadow_logs_dir)
    target_path = _next_output_path(overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "OVERLAY_SHADOW_LOGS_DIR", overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "_repo_relative", _patched_repo_relative)
    monkeypatch.setattr(helper, "validate_candidate_against_corpus", lambda payload, destination_path: ["boom"])

    exit_code = helper.run(
        _canonical_args(
            advisory_source="PGAS",
            advisory_artifact_id="PGAS-0002",
            timestamp="2026-04-22T00:00:00Z",
        )
        + ["--out", str(target_path), "--write"]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Validation: FAIL" in captured.err
    assert not target_path.exists()


def test_write_mode_writes_only_after_successful_validation(tmp_path, capsys, monkeypatch):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    _copy_committed_overlay_shadow_logs(overlay_shadow_logs_dir)
    target_path = _next_output_path(overlay_shadow_logs_dir)
    target_id = target_path.stem.split(".")[0]
    monkeypatch.setattr(helper, "OVERLAY_SHADOW_LOGS_DIR", overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "_repo_relative", _patched_repo_relative)

    exit_code = helper.run(
        _canonical_args(
            advisory_source="PGAS",
            advisory_artifact_id="PGAS-0002",
            timestamp="2026-04-22T00:00:00Z",
        )
        + ["--out", str(target_path), "--write"]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert target_path.exists()
    assert f'"overlay_shadow_log_id": "{target_id}"' in target_path.read_text(encoding="utf-8")
    assert "Wrote validated overlay shadow log:" in captured.out
