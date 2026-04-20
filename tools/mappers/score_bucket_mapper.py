"""Deterministic advisory score bucket mapper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_OUTPUT_PATH = REPO_ROOT / "research" / "agent_outputs" / "AOUT-0001.agent_output.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "research" / "bucket_mappings" / "BMAP-0001.bucket_mapping.json"
BUCKET_MAPPING_ID = "BMAP-0001"
MAPPING_METHOD = "score_thresholds_with_confidence_floor_v1"
CONFIDENCE_FLOOR = 0.60


def load_agent_output(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def map_score_to_bucket(setup_score: float, confidence: float) -> dict[str, Any]:
    """Map bounded advisory score and confidence into the locked bucket domain."""

    if confidence < CONFIDENCE_FLOOR:
        return {
            "mapped_bucket": "BLOCK",
            "size_multiplier": 0.0,
            "confidence_floor_triggered": True,
        }
    if setup_score >= 80.0:
        return {
            "mapped_bucket": "ALLOW",
            "size_multiplier": 1.0,
            "confidence_floor_triggered": False,
        }
    if setup_score >= 60.0:
        return {
            "mapped_bucket": "ALLOW_REDUCED",
            "size_multiplier": 0.5,
            "confidence_floor_triggered": False,
        }
    return {
        "mapped_bucket": "BLOCK",
        "size_multiplier": 0.0,
        "confidence_floor_triggered": False,
    }


def build_bucket_mapping(
    agent_output: dict[str, Any],
    bucket_mapping_id: str = BUCKET_MAPPING_ID,
) -> dict[str, Any]:
    setup_score = float(agent_output["setup_score"])
    confidence = float(agent_output["confidence"])
    mapping = map_score_to_bucket(setup_score=setup_score, confidence=confidence)

    return {
        "bucket_mapping_id": bucket_mapping_id,
        "source_agent_output_id": agent_output["agent_output_id"],
        "agent_type": agent_output["agent_type"],
        "generated_at": agent_output["generated_at"],
        "as_of_timestamp": agent_output["as_of_timestamp"],
        "source_setup_score": agent_output["setup_score"],
        "source_confidence": agent_output["confidence"],
        "mapping_method": MAPPING_METHOD,
        "confidence_floor": CONFIDENCE_FLOOR,
        "confidence_floor_triggered": mapping["confidence_floor_triggered"],
        "mapped_bucket": mapping["mapped_bucket"],
        "size_multiplier": mapping["size_multiplier"],
        "deterministic": True,
        "advisory_only": True,
        "notes": (
            "WP-6j advisory-only bucket mapping generated from committed Regime/Scoring "
            "agent output. It has no overlay contact, no execution influence, no OMS or "
            "risk authority, and no bucket override semantics."
        ),
    }


def write_bucket_mapping(
    source_path: Path = DEFAULT_AGENT_OUTPUT_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    bucket_mapping_id: str = BUCKET_MAPPING_ID,
) -> None:
    payload = build_bucket_mapping(
        agent_output=load_agent_output(source_path),
        bucket_mapping_id=bucket_mapping_id,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_AGENT_OUTPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--bucket-mapping-id", default=BUCKET_MAPPING_ID)
    args = parser.parse_args()

    write_bucket_mapping(
        source_path=args.source,
        output_path=args.output,
        bucket_mapping_id=args.bucket_mapping_id,
    )
    print(f"OK: wrote deterministic bucket mapping to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
