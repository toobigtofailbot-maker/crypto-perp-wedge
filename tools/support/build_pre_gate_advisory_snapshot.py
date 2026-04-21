"""Build deterministic bundle-only pre-gate advisory snapshot artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_OUTPUT_PATH = REPO_ROOT / "research" / "agent_outputs" / "AOUT-0001.agent_output.json"
DEFAULT_BUCKET_MAPPING_PATH = REPO_ROOT / "research" / "bucket_mappings" / "BMAP-0001.bucket_mapping.json"
DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH = (
    REPO_ROOT
    / "research"
    / "macro_window_agent_outputs"
    / "MOUT-0001.macro_window_agent_output.json"
)
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "research"
    / "pre_gate_advisory_snapshots"
    / "PGAS-0001.pre_gate_advisory_snapshot.json"
)
PRE_GATE_ADVISORY_SNAPSHOT_ID = "PGAS-0001"
COMBINATION_RULE = "NONE_BUNDLE_ONLY"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _latest_timestamp(*values: str) -> str:
    latest = max((_parse_timestamp(value) for value in values), key=lambda item: item.timestamp())
    return latest.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_pre_gate_advisory_snapshot(
    agent_output: dict[str, Any],
    bucket_mapping: dict[str, Any],
    macro_window_agent_output: dict[str, Any],
    pre_gate_advisory_snapshot_id: str = PRE_GATE_ADVISORY_SNAPSHOT_ID,
) -> dict[str, Any]:
    return {
        "pre_gate_advisory_snapshot_id": pre_gate_advisory_snapshot_id,
        "generated_at": _latest_timestamp(
            agent_output["generated_at"],
            bucket_mapping["generated_at"],
            macro_window_agent_output["generated_at"],
        ),
        "as_of_timestamp": _latest_timestamp(
            agent_output["as_of_timestamp"],
            bucket_mapping["as_of_timestamp"],
            macro_window_agent_output["as_of_timestamp"],
        ),
        "source_agent_output_id": agent_output["agent_output_id"],
        "source_bucket_mapping_id": bucket_mapping["bucket_mapping_id"],
        "source_macro_window_agent_output_id": macro_window_agent_output["macro_window_agent_output_id"],
        "setup_score": agent_output["setup_score"],
        "confidence": agent_output["confidence"],
        "mapped_bucket": bucket_mapping["mapped_bucket"],
        "size_multiplier": bucket_mapping["size_multiplier"],
        "macro_window_flag": macro_window_agent_output["macro_window_flag"],
        "deterministic": True,
        "advisory_only": True,
        "combination_rule_applied": COMBINATION_RULE,
        "notes": (
            "WP-7g bundle-only pre-gate advisory snapshot over committed advisory artifacts. "
            "It encodes no final gate decision, no runtime influence, no execution authority, "
            "and no overlay, OMS, risk, or policy authority."
        ),
    }


def write_pre_gate_advisory_snapshot(
    source_agent_output_path: Path = DEFAULT_AGENT_OUTPUT_PATH,
    source_bucket_mapping_path: Path = DEFAULT_BUCKET_MAPPING_PATH,
    source_macro_window_agent_output_path: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    pre_gate_advisory_snapshot_id: str = PRE_GATE_ADVISORY_SNAPSHOT_ID,
) -> None:
    payload = build_pre_gate_advisory_snapshot(
        agent_output=load_json(source_agent_output_path),
        bucket_mapping=load_json(source_bucket_mapping_path),
        macro_window_agent_output=load_json(source_macro_window_agent_output_path),
        pre_gate_advisory_snapshot_id=pre_gate_advisory_snapshot_id,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-output", type=Path, default=DEFAULT_AGENT_OUTPUT_PATH)
    parser.add_argument("--bucket-mapping", type=Path, default=DEFAULT_BUCKET_MAPPING_PATH)
    parser.add_argument("--macro-window-agent-output", type=Path, default=DEFAULT_MACRO_WINDOW_AGENT_OUTPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--pre-gate-advisory-snapshot-id", default=PRE_GATE_ADVISORY_SNAPSHOT_ID)
    args = parser.parse_args()

    write_pre_gate_advisory_snapshot(
        source_agent_output_path=args.agent_output,
        source_bucket_mapping_path=args.bucket_mapping,
        source_macro_window_agent_output_path=args.macro_window_agent_output,
        output_path=args.output,
        pre_gate_advisory_snapshot_id=args.pre_gate_advisory_snapshot_id,
    )
    print(f"OK: wrote deterministic pre-gate advisory snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
