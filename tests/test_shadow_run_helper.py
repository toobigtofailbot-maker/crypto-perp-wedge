import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pytest

from tools.shadow import shadow_run_helper as helper


def _base_args(*, advisory_source: str, advisory_artifact_id: str, timestamp: str) -> list[str]:
    return [
        "--advisory-source",
        advisory_source,
        "--advisory-artifact-id",
        advisory_artifact_id,
        "--timestamp",
        timestamp,
    ]


def _legacy_canonical_args(*, advisory_source: str, advisory_artifact_id: str, timestamp: str) -> list[str]:
    return _base_args(
        advisory_source=advisory_source,
        advisory_artifact_id=advisory_artifact_id,
        timestamp=timestamp,
    ) + [
        "--snapshot",
        str(helper.CANONICAL_SNAPSHOT_PATH),
        "--config",
        str(helper.CANONICAL_CONFIG_PATH),
    ]


def _explicit_args(
    *,
    advisory_source: str,
    advisory_artifact_id: str,
    timestamp: str,
    snapshot_path: Path,
    config_path: Path,
) -> list[str]:
    return _base_args(
        advisory_source=advisory_source,
        advisory_artifact_id=advisory_artifact_id,
        timestamp=timestamp,
    ) + [
        "--context-snapshot-path",
        str(snapshot_path),
        "--macro-flags-path",
        str(config_path),
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
    try:
        return resolved.relative_to(helper.REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _overlay_shadow_log_path(overlay_shadow_logs_dir: Path, overlay_shadow_log_id: str) -> Path:
    return overlay_shadow_logs_dir / f"{overlay_shadow_log_id}.overlay_shadow_log.json"


def _next_output_path(overlay_shadow_logs_dir: Path | None = None) -> Path:
    overlay_shadow_logs_dir = overlay_shadow_logs_dir or helper.OVERLAY_SHADOW_LOGS_DIR
    overlay_shadow_log_id = helper.next_overlay_shadow_log_id(overlay_shadow_logs_dir)
    return _overlay_shadow_log_path(overlay_shadow_logs_dir, overlay_shadow_log_id)


@contextmanager
def _repo_temp_overlay_inputs(snapshot_text: str = "{}", config_text: str = "{}"):
    with tempfile.TemporaryDirectory(dir=helper.REPO_ROOT, prefix="tmp-shadow-helper-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        snapshot_path = temp_dir / "context_snapshot.json"
        config_path = temp_dir / "macro_flags.json"
        snapshot_path.write_text(snapshot_text, encoding="utf-8")
        config_path.write_text(config_text, encoding="utf-8")
        yield snapshot_path, config_path


def test_cli_rejects_unsupported_advisory_source():
    with pytest.raises(SystemExit):
        helper.run(
            [
                "--advisory-source",
                "NOPE",
                "--advisory-artifact-id",
                "BMAP-0001",
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


def test_run_rejects_noncanonical_legacy_snapshot_and_config(tmp_path, capsys):
    snapshot_path = tmp_path / "snapshot.json"
    config_path = tmp_path / "config.json"
    snapshot_path.write_text("{}", encoding="utf-8")
    config_path.write_text("{}", encoding="utf-8")

    exit_code = helper.run(
        _base_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
        )
        + [
            "--snapshot",
            str(snapshot_path),
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "snapshot must resolve to" in captured.err


def test_run_rejects_partial_explicit_context_snapshot_path(capsys):
    with _repo_temp_overlay_inputs() as (snapshot_path, _):
        exit_code = helper.run(
            _base_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
            )
            + ["--context-snapshot-path", str(snapshot_path)]
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "must be supplied together or omitted together" in captured.err


def test_run_rejects_partial_explicit_macro_flags_path(capsys):
    with _repo_temp_overlay_inputs() as (_, config_path):
        exit_code = helper.run(
            _base_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
            )
            + ["--macro-flags-path", str(config_path)]
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "must be supplied together or omitted together" in captured.err


def test_run_rejects_mixed_legacy_and_explicit_overlay_input_paths(capsys):
    with _repo_temp_overlay_inputs() as (snapshot_path, config_path):
        exit_code = helper.run(
            _legacy_canonical_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
            )
            + [
                "--context-snapshot-path",
                str(snapshot_path),
                "--macro-flags-path",
                str(config_path),
            ]
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "cannot be combined" in captured.err


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


def test_default_mode_dry_run_prints_candidate_and_overlay_input_paths(capsys):
    expected_path = _next_output_path()
    expected_id = expected_path.stem.split(".")[0]
    assert not expected_path.exists()

    exit_code = helper.run(
        _base_args(
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
    assert "Overlay input mode: canonical" in captured.err
    assert "Context snapshot path: tests/fixtures/context_snapshot_sample.json" in captured.err
    assert "Macro flags path: configs/fmp_macro_flags.json" in captured.err
    assert "Validation: PASS" in captured.err
    assert not expected_path.exists()


def test_legacy_canonical_args_match_default_mode_payload(capsys):
    exit_code_default = helper.run(
        _base_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
        )
    )
    captured_default = capsys.readouterr()

    exit_code_legacy = helper.run(
        _legacy_canonical_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
        )
    )
    captured_legacy = capsys.readouterr()

    assert exit_code_default == 0
    assert exit_code_legacy == 0
    assert captured_default.out == captured_legacy.out


@pytest.mark.parametrize(
    ("advisory_source", "advisory_artifact_id", "timestamp", "overlay_shadow_log_id", "committed_path"),
    [
        (
            "BMAP",
            "BMAP-0001",
            "2026-04-22T00:00:00Z",
            "OSH-0003",
            helper.OVERLAY_SHADOW_LOGS_DIR / "OSH-0003.overlay_shadow_log.json",
        ),
        (
            "PGAS",
            "PGAS-0003",
            "2026-04-22T04:00:00Z",
            "OSH-0006",
            helper.OVERLAY_SHADOW_LOGS_DIR / "OSH-0006.overlay_shadow_log.json",
        ),
    ],
)
def test_default_mode_payload_matches_committed_helper_rows(
    advisory_source: str,
    advisory_artifact_id: str,
    timestamp: str,
    overlay_shadow_log_id: str,
    committed_path: Path,
):
    payload = helper.build_candidate_payload(
        advisory_source=advisory_source,
        advisory_artifact_id=advisory_artifact_id,
        timestamp_utc=timestamp,
        snapshot_path=helper.CANONICAL_SNAPSHOT_PATH,
        config_path=helper.CANONICAL_CONFIG_PATH,
        overlay_shadow_log_id=overlay_shadow_log_id,
    )

    assert helper.render_payload(payload) == committed_path.read_text(encoding="utf-8")


def test_explicit_mode_dry_run_accepts_valid_overlay_inputs_and_reports_paths(capsys):
    with _repo_temp_overlay_inputs() as (snapshot_path, config_path):
        exit_code = helper.run(
            _explicit_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
                snapshot_path=snapshot_path,
                config_path=config_path,
            )
        )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Overlay input mode: explicit" in captured.err
    assert f"Context snapshot path: {helper._display_path(snapshot_path)}" in captured.err
    assert f"Macro flags path: {helper._display_path(config_path)}" in captured.err
    assert "Validation: PASS" in captured.err
    assert "Validation note:" not in captured.err


def test_explicit_mode_rejects_nonexistent_context_snapshot_path(capsys):
    missing_snapshot = helper.REPO_ROOT / "tests" / "fixtures" / "context_snapshot_missing.json"

    with _repo_temp_overlay_inputs() as (_, config_path):
        exit_code = helper.run(
            _explicit_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
                snapshot_path=missing_snapshot,
                config_path=config_path,
            )
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "context snapshot path does not exist" in captured.err


def test_explicit_mode_rejects_nonexistent_macro_flags_path(capsys):
    missing_config = helper.REPO_ROOT / "configs" / "fmp_macro_flags_missing.json"

    with _repo_temp_overlay_inputs() as (snapshot_path, _):
        exit_code = helper.run(
            _explicit_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
                snapshot_path=snapshot_path,
                config_path=missing_config,
            )
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "macro flags path does not exist" in captured.err


def test_explicit_mode_rejects_invalid_json_overlay_input(capsys):
    with _repo_temp_overlay_inputs(snapshot_text="{", config_text="{}") as (snapshot_path, config_path):
        exit_code = helper.run(
            _explicit_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
                snapshot_path=snapshot_path,
                config_path=config_path,
            )
        )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "context snapshot path contains invalid JSON" in captured.err


def test_explicit_mode_dry_run_is_byte_identical_for_repeated_inputs(capsys):
    with _repo_temp_overlay_inputs() as (snapshot_path, config_path):
        explicit_args = _explicit_args(
            advisory_source="BMAP",
            advisory_artifact_id="BMAP-0001",
            timestamp="2026-04-22T00:00:00Z",
            snapshot_path=snapshot_path,
            config_path=config_path,
        )
        exit_code_a = helper.run(explicit_args)
        captured_a = capsys.readouterr()
        exit_code_b = helper.run(explicit_args)
        captured_b = capsys.readouterr()

    assert exit_code_a == 0
    assert exit_code_b == 0
    assert captured_a.out == captured_b.out


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
        _base_args(
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


def test_write_mode_accepts_noncanonical_explicit_paths_after_validation(tmp_path, capsys, monkeypatch):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    _copy_committed_overlay_shadow_logs(overlay_shadow_logs_dir)
    target_path = _next_output_path(overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "OVERLAY_SHADOW_LOGS_DIR", overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "_repo_relative", _patched_repo_relative)

    with _repo_temp_overlay_inputs() as (snapshot_path, config_path):
        exit_code = helper.run(
            _explicit_args(
                advisory_source="BMAP",
                advisory_artifact_id="BMAP-0001",
                timestamp="2026-04-22T00:00:00Z",
                snapshot_path=snapshot_path,
                config_path=config_path,
            )
            + ["--out", str(target_path), "--write"]
        )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"Wrote validated overlay shadow log: {_patched_repo_relative(target_path)}" in captured.out
    assert target_path.exists()
    payload = helper.load_json(target_path)
    assert payload["overlay_shadow_log_id"] == "OSH-0007"
    assert payload["observation_source"]["snapshot_path"] == _patched_repo_relative(snapshot_path)
    assert payload["observation_source"]["config_path"] == _patched_repo_relative(config_path)


def test_write_mode_fails_without_writing_when_validation_fails(tmp_path, capsys, monkeypatch):
    overlay_shadow_logs_dir = tmp_path / "research" / "overlay_shadow_logs"
    _copy_committed_overlay_shadow_logs(overlay_shadow_logs_dir)
    target_path = _next_output_path(overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "OVERLAY_SHADOW_LOGS_DIR", overlay_shadow_logs_dir)
    monkeypatch.setattr(helper, "_repo_relative", _patched_repo_relative)
    monkeypatch.setattr(helper, "validate_candidate_against_corpus", lambda payload, destination_path: ["boom"])

    exit_code = helper.run(
        _base_args(
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
        _base_args(
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
