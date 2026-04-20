"""Deterministic fixture-backed Macro/Narrative advisory agent stub."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "macro_narrative_input_fixture.json"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "research"
    / "macro_window_agent_outputs"
    / "MOUT-0001.macro_window_agent_output.json"
)
MACRO_WINDOW_AGENT_OUTPUT_ID = "MOUT-0001"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_macro_window_flag(fixture: dict[str, Any]) -> bool:
    """Derive the advisory macro-window flag from the committed fixture."""

    return bool(fixture["macro_event_window_active"])


def build_macro_window_agent_output(
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    output_id: str = MACRO_WINDOW_AGENT_OUTPUT_ID,
) -> dict[str, Any]:
    fixture = load_fixture(fixture_path)

    return {
        "macro_window_agent_output_id": output_id,
        "generated_at": fixture["generated_at"],
        "as_of_timestamp": fixture["as_of_timestamp"],
        "source_fixture_path": _repo_relative(fixture_path),
        "source_fixture_sha256": _sha256_file(fixture_path),
        "macro_window_flag": derive_macro_window_flag(fixture),
        "event_class": fixture["event_class"],
        "event_name": fixture["event_name"],
        "deterministic": True,
        "advisory_only": True,
        "notes": (
            "WP-7f fixture-backed macro-window advisory output. It is advisory-only, has no "
            "runtime influence, no execution authority, no live news ingestion, no LLM call, "
            "no candidate-specific logic, and no overlay, OMS, risk, sizing, or policy authority."
        ),
    }


def write_macro_window_agent_output(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
    output_id: str = MACRO_WINDOW_AGENT_OUTPUT_ID,
) -> None:
    payload = build_macro_window_agent_output(fixture_path=fixture_path, output_id=output_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--macro-window-agent-output-id", default=MACRO_WINDOW_AGENT_OUTPUT_ID)
    args = parser.parse_args()

    write_macro_window_agent_output(
        output_path=args.output,
        fixture_path=args.fixture,
        output_id=args.macro_window_agent_output_id,
    )
    print(f"OK: wrote deterministic macro-window agent output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
