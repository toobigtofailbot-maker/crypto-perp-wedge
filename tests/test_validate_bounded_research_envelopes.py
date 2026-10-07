import json
from pathlib import Path

import pytest

from tools.registry.validate_bounded_research_envelopes import main, validate_files

ROOT = Path(__file__).resolve().parents[1]
BASE = "9d9f8a94405ded76bbef0163488b9a8e0596371a"


def test_default_absence_and_exact_fixture_files():
    assert main([]) == 0
    paths = list((ROOT / "tests/fixtures/research_autonomy").glob("*.json"))
    before = {p: p.read_bytes() for p in paths}
    assert validate_files(paths, repo_sha=BASE) == 2
    assert before == {p: p.read_bytes() for p in paths}


def test_malformed_file_and_orphan_control_fail(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"schema_version":"wrong"}')
    assert main([str(p), "--repo-sha", BASE]) == 1
    control = ROOT / "tests/fixtures/research_autonomy/bounded_research_envelope_control.fixture.json"
    with pytest.raises(ValueError, match="target envelope"):
        validate_files([control], repo_sha=BASE)
