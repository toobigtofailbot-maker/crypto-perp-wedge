"""Formalize a research idea into validated, scratch-only draft artifacts.

JSON inputs use the research-idea contract directly. Plain-text inputs are
handled by a deliberately conservative local parser; ambiguous text is rejected
for clarification rather than expanded into an unbounded search. No network,
credentials, model API, strategy execution, or canonical write is performed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.research_workflow import draft_grid_generator
from tools.research_workflow.validate_research_idea import validate_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "WP-LAB-IDEA-INTAKE-FORMALIZATION-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
KNOWN_DATA_STREAMS = {"ohlcv", "funding", "mark", "index", "premium"}
KNOWN_FEATURES = {"sma", "ema", "atr", "stddev"}
WORKFLOW_PARAMETER_NAMES = {
    "center_lookback_bars",
    "vol_lookback_bars",
    "trend_lookback_bars",
}
NON_AUTHORITY_FLAGS = {
    "draft_only": True,
    "not_canonical": True,
    "not_preregistered": True,
    "not_candidate_evidence": True,
    "not_promotion": True,
    "not_paper_live": True,
    "human_gate_required_for_draft_to_prereg": True,
}


class FormalizationError(RuntimeError):
    """Raised for unsafe or malformed formalization requests."""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _stable_suffix(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8].upper()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized[:64]


def _split_clauses(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"[.;\n]+", text) if item.strip()]


def _plain_text_to_payload(text: str, *, created_at_utc: str | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Conservatively extract only explicit, locally testable text features."""

    reasons: list[str] = []
    symbols = sorted(set(re.findall(r"\b[A-Z0-9]{2,20}USDT\b", text.upper())))
    timeframe_matches = re.findall(r"(?<![A-Za-z0-9])(15m|30m|1h|4h|1d)(?![A-Za-z0-9])", text, re.I)
    timeframes = list(dict.fromkeys(item.lower() for item in timeframe_matches))
    clauses = _split_clauses(text)
    entry_clauses = [item for item in clauses if re.search(r"\b(enter|entry)\b", item, re.I)]
    exit_clauses = [item for item in clauses if re.search(r"\b(exit|close position)\b", item, re.I)]
    stop_clauses = [item for item in clauses if re.search(r"\bstop (testing )?if\b", item, re.I)]
    causal_match = re.search(r"\b(?:because|due to)\s+(.+?)(?:[.;]|$)", text, re.I)

    parameter_ranges: list[dict[str, Any]] = []
    range_pattern = re.compile(
        r"\b([A-Za-z][A-Za-z0-9 _-]{1,40}?)\s+(?:from|between)\s+"
        r"(-?\d+(?:\.\d+)?)\s+(?:to|and)\s+(-?\d+(?:\.\d+)?)"
        r"(?:\s+(bars?|percent|bps|hours?|days?))?\b",
        re.I,
    )
    for match in range_pattern.finditer(text):
        minimum = float(match.group(2))
        maximum = float(match.group(3))
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        integer = minimum.is_integer() and maximum.is_integer()
        minimum_value: int | float = int(minimum) if integer else minimum
        maximum_value: int | float = int(maximum) if integer else maximum
        parameter_ranges.append(
            {
                "name": _normalize_name(match.group(1)),
                "value_type": "integer" if integer else "number",
                "units": match.group(4) or "unitless",
                "minimum": minimum_value,
                "maximum": maximum_value,
                "values": [minimum_value] if minimum_value == maximum_value else [minimum_value, maximum_value],
                "rationale": "Explicit bounds extracted from the source idea; intermediate expansion is not authorized.",
            }
        )

    features = sorted(feature for feature in KNOWN_FEATURES if re.search(rf"\b{feature}\b", text, re.I))
    if not symbols:
        reasons.append("plain text must explicitly name a bounded instrument such as BTCUSDT")
    if not timeframes:
        reasons.append("plain text must explicitly name one locked timeframe")
    if not causal_match:
        reasons.append("plain text must include an explicit causal rationale using 'because' or 'due to'")
    if not entry_clauses or not exit_clauses:
        reasons.append("plain text must explicitly describe both entry and exit concepts")
    if not parameter_ranges:
        reasons.append("plain text must include at least one bounded parameter using 'from X to Y' or 'between X and Y'")
    if not features:
        reasons.append("plain text must name at least one known feature: sma, ema, atr, or stddev")
    if not stop_clauses:
        reasons.append("plain text must state an explicit 'stop if' condition")
    if reasons:
        return None, reasons

    payload: dict[str, Any] = {
        "idea_id": f"IDEA-{_stable_suffix(text)}",
        "schema_version": "v1",
        "created_at_utc": created_at_utc or _utc_now(),
        "source_type": "human",
        "plain_language_idea": text.strip(),
        "market_hypothesis": {
            "claim": clauses[0],
            "causal_rationale": causal_match.group(1).strip(),
            "observable_prediction": entry_clauses[0],
        },
        "instrument_universe": {"symbols": symbols, "market_type": "perpetual", "venue": "Binance USDT-M"},
        "timeframe": {
            "primary": timeframes[0],
            "confirmations": timeframes[1:],
            "decision_timing": "completed_bar_close",
            "entry_timing": "next_bar_open",
        },
        "required_data": [{"stream": "ohlcv", "fields": ["open", "high", "low", "close", "volume"], "availability": "current_lab"}],
        "required_indicators_features": [
            {"feature_id": feature, "description": f"Source idea explicitly references {feature}.", "availability": "current_lab"}
            for feature in features
        ],
        "entry_exit_concept": {
            "entry": entry_clauses[0],
            "exit": exit_clauses[0],
            "position_directions": ["long", "short"] if re.search(r"\blong\b", text, re.I) and re.search(r"\bshort\b", text, re.I) else (["short"] if re.search(r"\bshort\b", text, re.I) else ["long"]),
        },
        "risk_logic_concept": {"exit_risk_logic": exit_clauses[0], "sizing_posture": "research_assumption_only"},
        "parameter_ranges": parameter_ranges,
        "expected_edge_mechanism": causal_match.group(1).strip(),
        "failure_modes": ["The asserted causal mechanism may not persist out of sample."],
        "overfit_risks": ["Sparse source detail and endpoint-only parameter extraction require human review."],
        "validation_requirements": ["Use preregistered walk-forward evaluation before treating results as evidence."],
        "stop_conditions": stop_clauses,
        "current_lab_compatibility": {
            "is_testable": True,
            "known_capabilities": ["ohlcv", *features],
            "missing_capabilities": [],
        },
        "upgrade_dependencies": [],
        "classification": "current_lab_testable",
        "rejection_reasons": [],
        "non_authority_flags": copy.deepcopy(NON_AUTHORITY_FLAGS),
    }
    return payload, []


def load_input(path: Path, *, created_at_utc: str | None = None) -> tuple[dict[str, Any] | None, list[str], str]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None, ["input is empty"], "plain_text"
    if path.suffix.lower() == ".json" or text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, [f"invalid JSON: {exc}"], "json"
        if not isinstance(payload, dict):
            return None, ["JSON root must be an object"], "json"
        return payload, [], "json"
    payload, reasons = _plain_text_to_payload(text, created_at_utc=created_at_utc)
    return payload, reasons, "plain_text"


def classify_capabilities(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("required_data", [])
    features = payload.get("required_indicators_features", [])
    known_data = sorted({item.get("stream") for item in data if isinstance(item, dict) and item.get("stream") in KNOWN_DATA_STREAMS})
    missing_data = sorted({item.get("stream") for item in data if isinstance(item, dict) and item.get("stream") not in KNOWN_DATA_STREAMS})
    known_features = sorted({item.get("feature_id") for item in features if isinstance(item, dict) and item.get("feature_id") in KNOWN_FEATURES})
    missing_features = sorted({item.get("feature_id") for item in features if isinstance(item, dict) and item.get("feature_id") not in KNOWN_FEATURES})
    return {
        "known_data_streams": known_data,
        "missing_data_streams": missing_data,
        "known_features": known_features,
        "missing_features": missing_features,
        "lab_testable": payload.get("classification") == "current_lab_testable" and not missing_data and not missing_features,
    }


def build_workflow_input(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Build an input only for the generator's exact merged source family."""

    reasons: list[str] = []
    params = payload.get("parameter_ranges", [])
    names = {item.get("name") for item in params if isinstance(item, dict)}
    if payload.get("classification") != "current_lab_testable":
        reasons.append("idea is not current-lab testable")
    if names != WORKFLOW_PARAMETER_NAMES:
        reasons.append("parameter names do not exactly match the merged workflow generator source family")
    if reasons:
        return None, reasons

    parameter_by_name = {item["name"]: item for item in params}
    result = draft_grid_generator.default_parameter_space()
    suffix = 9200 + (int(_stable_suffix(payload["idea_id"]), 16) % 100)
    result.update(
        {
            # The merged generator validates its own package identity. This
            # adapter preserves that contract and records this WP in the
            # scratch-only search-family identifier instead.
            "package_id": draft_grid_generator.PACKAGE_ID,
            "generated_strategy_spec_id": f"STRAT-SPEC-{suffix:04d}",
            "generated_variant_manifest_id": f"VM-{suffix:04d}",
            "generated_sweep_plan_id": f"SWEEP-PLAN-{suffix:04d}",
            "search_family_id": f"SF-{PACKAGE_ID}-{suffix:04d}",
            "created_at": payload["created_at_utc"],
        }
    )
    result["parameters"] = []
    for name in result["axis_order"]:
        source = parameter_by_name[name]
        result["parameters"].append(
            {
                "name": name,
                "type": source["value_type"],
                "units": source["units"],
                "values": source["values"],
                "description": f"Draft grid axis formalized from {payload['idea_id']}.",
                "rationale": source["rationale"],
                "bounds": {"min": source["minimum"], "max": source["maximum"], "inclusive_min": True, "inclusive_max": True},
            }
        )
    return result, []


def formalize(
    *, input_path: Path, output_dir: Path, generate_workflow_drafts: bool = False,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    payload, intake_reasons, input_kind = load_input(input_path, created_at_utc=created_at_utc)
    report: dict[str, Any] = {
        "package_id": PACKAGE_ID,
        "input_kind": input_kind,
        "status": "rejected" if intake_reasons else "pending_validation",
        "rejection_reasons": intake_reasons,
        "non_authority_flags": copy.deepcopy(NON_AUTHORITY_FLAGS),
        "llm_assist": {"available": False, "used": False, "reason": "no repo-owned live LLM/API abstraction exists; future adapter requires separate approval"},
        "research_idea_path": None,
        "workflow_generator": {"eligible": False, "invoked": False, "input_path": None, "output_dir": None, "ineligibility_reasons": []},
    }
    output_dir.mkdir(parents=True, exist_ok=True)

    if payload is not None and not intake_reasons:
        errors = validate_payload(payload)
        if errors:
            report["status"] = "rejected"
            report["rejection_reasons"] = errors
        else:
            idea_path = output_dir / "example_research_idea.json"
            _write_json(idea_path, payload)
            report["status"] = "formalized"
            report["classification"] = payload["classification"]
            report["capability_mapping"] = classify_capabilities(payload)
            report["research_idea_path"] = _portable_path(idea_path)
            workflow_input, workflow_reasons = build_workflow_input(payload)
            workflow_report = report["workflow_generator"]
            workflow_report["eligible"] = workflow_input is not None
            workflow_report["ineligibility_reasons"] = workflow_reasons
            if workflow_input is not None:
                parameter_path = output_dir / "draft_workflow_parameter_space.json"
                _write_json(parameter_path, workflow_input)
                workflow_report["input_path"] = _portable_path(parameter_path)
                if generate_workflow_drafts:
                    workflow_output = output_dir / "workflow_gen"
                    generator_report = draft_grid_generator.run_generator(parameter_space_path=parameter_path, output_dir=workflow_output)
                    workflow_report["invoked"] = True
                    workflow_report["output_dir"] = _portable_path(workflow_output)
                    workflow_report["generated_variant_count"] = generator_report["generated_variant_count"]

    report_path = output_dir / "example_formalization_report.json"
    _write_json(report_path, report)
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generate-workflow-drafts", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = formalize(input_path=args.input, output_dir=args.output_dir, generate_workflow_drafts=args.generate_workflow_drafts)
    except (OSError, FormalizationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "formalized" else 2


if __name__ == "__main__":
    raise SystemExit(main())
