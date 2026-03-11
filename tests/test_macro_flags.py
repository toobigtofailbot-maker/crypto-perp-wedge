import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

from src.context.macro_flags import FAIL_OPEN_WINDOW, generate_macro_flags


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def test_determinism_same_snapshot_same_hash():
    snapshot = _load_json(ROOT / "tests/fixtures/context_snapshot_sample.json")
    config = _load_json(ROOT / "configs/fmp_macro_flags.json")

    out_1 = generate_macro_flags(snapshot=snapshot, config=config)
    out_2 = generate_macro_flags(snapshot=snapshot, config=config)

    assert _hash(out_1) == _hash(out_2)


def test_fail_open_for_missing_snapshot_and_empty_events():
    config = _load_json(ROOT / "configs/fmp_macro_flags.json")

    out_missing = generate_macro_flags(snapshot=None, config=config)
    assert out_missing["context_missing"] is True
    assert out_missing["windows"] == [FAIL_OPEN_WINDOW]

    out_empty = generate_macro_flags(
        snapshot={"asof_timestamp_utc": "2025-01-01T00:00:00Z", "snapshot_hash": "x", "events": []},
        config=config,
    )
    assert out_empty["context_missing"] is True
    assert out_empty["windows"] == [FAIL_OPEN_WINDOW]


def test_allowed_set_enforcement():
    snapshot = _load_json(ROOT / "tests/fixtures/context_snapshot_sample.json")
    config = _load_json(ROOT / "configs/fmp_macro_flags.json")
    config["per_event_permission"]["CPI"] = "SOMETHING_ELSE"

    out = generate_macro_flags(snapshot=snapshot, config=config)
    for window in out["windows"]:
        assert window["permission"] in {"ALLOW", "ALLOW_REDUCED", "BLOCK"}
        assert window["size_multiplier"] in {1.0, 0.5, 0.0}


def test_windows_sorted_deterministically():
    snapshot = _load_json(ROOT / "tests/fixtures/context_snapshot_sample.json")
    config = _load_json(ROOT / "configs/fmp_macro_flags.json")

    out = generate_macro_flags(snapshot=snapshot, config=config)
    keys = [(w["start_utc"], w["end_utc"], w["permission"], w["size_multiplier"]) for w in out["windows"]]
    assert keys == sorted(keys)
