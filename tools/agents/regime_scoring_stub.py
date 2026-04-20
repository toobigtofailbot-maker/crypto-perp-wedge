"""Deterministic fixture-backed Regime/Scoring advisory agent stub."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "regime_scoring_market_fixture.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "research" / "agent_outputs" / "AOUT-0001.agent_output.json"
AGENT_OUTPUT_ID = "AOUT-0001"
AGENT_TYPE = "REGIME_SCORING"
METHOD_ID = "fixture_regime_scoring_v1"


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_regime_score(fixture: dict[str, Any]) -> dict[str, Any]:
    """Compute the bounded advisory score from a committed market fixture."""

    observations = sorted(fixture["observations"], key=lambda row: row["timestamp"])
    if len(observations) < 2:
        raise ValueError("at least two observations are required")

    closes = [float(row["close"]) for row in observations]
    funding_rates = [float(row["funding_rate"]) for row in observations]
    spreads_bps = [float(row["spread_bps"]) for row in observations]
    returns = [
        (close / prior_close) - 1.0
        for prior_close, close in zip(closes[:-1], closes[1:], strict=True)
    ]

    realized_volatility = pstdev(returns)
    vol_component = _clamp(realized_volatility / 0.005)
    funding_component = _clamp(mean(abs(rate) for rate in funding_rates) / 0.0005)
    spread_component = _clamp(mean(spreads_bps) / 5.0)
    stress_score = (0.60 * vol_component) + (0.25 * funding_component) + (0.15 * spread_component)

    setup_score = round(100.0 * (1.0 - stress_score), 2)
    confidence = round(
        _clamp(
            0.50
            + (0.20 * (1.0 - vol_component))
            + (0.15 * (1.0 - funding_component))
            + (0.10 * (1.0 - spread_component))
            + (0.05 * (min(len(observations), 8) / 8.0))
        ),
        3,
    )

    return {
        "setup_score": setup_score,
        "confidence": confidence,
        "scoring_method": {
            "method_id": METHOD_ID,
            "realized_volatility": realized_volatility,
            "vol_component": vol_component,
            "funding_component": funding_component,
            "spread_component": spread_component,
            "stress_score": stress_score,
        },
    }


def build_agent_output(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> dict[str, Any]:
    fixture = load_fixture(fixture_path)
    score = compute_regime_score(fixture)
    input_ref = {
        "path": _repo_relative(fixture_path),
        "sha256": _sha256_file(fixture_path),
        "role": "fixture_market_snapshot",
    }

    return {
        "agent_output_id": AGENT_OUTPUT_ID,
        "agent_type": AGENT_TYPE,
        "generated_at": fixture["generated_at"],
        "input_data_refs": [input_ref],
        "as_of_timestamp": fixture["as_of_timestamp"],
        "setup_score": score["setup_score"],
        "confidence": score["confidence"],
        "scoring_method": score["scoring_method"],
        "rationale_summary": (
            "Fixture-backed deterministic Regime/Scoring stub: low normalized realized "
            "volatility, funding, and spread stress produce a bounded advisory setup score."
        ),
        "deterministic": True,
        "notes": (
            "WP-7a advisory-only output generated from a tiny committed fixture. It uses no "
            "ignored local processed market data, live external input, network call, LLM call, "
            "candidate recommendation, overlay signal, OMS instruction, risk change, sizing "
            "instruction, or execution authority."
        ),
    }


def write_agent_output(output_path: Path = DEFAULT_OUTPUT_PATH, fixture_path: Path = DEFAULT_FIXTURE_PATH) -> None:
    payload = build_agent_output(fixture_path=fixture_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    write_agent_output(output_path=args.output, fixture_path=args.fixture)
    print(f"OK: wrote deterministic agent output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
