"""Deterministic advisory eligibility validator for reviewed Agent Inbox drafts.

This module has no canonical, Gate C, queue, candidate, or execution authority.
Its only write surface is the package-owned scratch reports directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


PACKAGE_ID = "WP-CANON-ELIGIBILITY-VALIDATOR-01"
SCHEMA_VERSION = "canon_intake_eligibility_report_v1"
DEFAULT_DRAFT_ROOT = Path("scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts")
DEFAULT_REVIEW_ROOT = Path("scratch/WP-DASH-AGENT-INBOX-WRITE-01A/reviews")
DEFAULT_REPORT_ROOT = Path(f"scratch/{PACKAGE_ID}/reports")
LOCKED_TIMEFRAMES = frozenset({"15m", "30m", "1h", "4h", "1d"})
TOKEN_RE = re.compile(r"[a-z0-9]+")
DRAFT_ID_RE = re.compile(r"^AIDRAFT-[A-F0-9]{16}$")
PASS = "pass"
FAIL = "fail"
UNKNOWN = "unknown"


class EligibilityValidationError(ValueError):
    """Raised when input is malformed or a source cannot be read honestly."""


def _hash_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EligibilityValidationError(f"unreadable JSON artifact: {path.as_posix()}") from exc
    if not isinstance(value, dict):
        raise EligibilityValidationError(f"JSON artifact must be an object: {path.as_posix()}")
    return value, _hash_bytes(raw)


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise EligibilityValidationError(f"source escapes repository: {path}") from exc


def _artifact(path: Path, repo_root: Path, digest: str) -> dict[str, str]:
    return {"path": _relative(path, repo_root), "sha256": digest}


def _check(status: str, explanation: str, evidence: Iterable[str] = ()) -> dict[str, Any]:
    return {"status": status, "explanation": explanation, "evidence": sorted(set(evidence))}


def _tokens(*values: Any) -> set[str]:
    text = " ".join(str(v) for v in values if v is not None).lower()
    ignored = {"the", "and", "with", "for", "from", "into", "when", "after", "bars", "btcusdt"}
    return {token for token in TOKEN_RE.findall(text) if len(token) > 2 and token not in ignored}


def _similarity(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left and right else 0.0


def _load_reviews(path: Path, draft_id: str) -> tuple[list[dict[str, Any]], str | None]:
    if not path.exists():
        return [], None
    try:
        raw = path.read_bytes()
        lines = raw.decode("utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EligibilityValidationError(f"unreadable review trail: {path.as_posix()}") from exc
    events: list[dict[str, Any]] = []
    for index, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EligibilityValidationError(f"malformed review event at line {index}") from exc
        if not isinstance(event, dict) or event.get("draft_id") != draft_id:
            raise EligibilityValidationError(f"invalid review event at line {index}")
        if event.get("append_index") != index or not isinstance(event.get("review_state"), str):
            raise EligibilityValidationError(f"invalid review event ordering at line {index}")
        events.append(event)
    return events, _hash_bytes(raw)


def _draft_fields(packet: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    request = packet.get("source_request")
    formalizer = packet.get("formalizer_result")
    if not isinstance(request, dict) or not isinstance(formalizer, dict):
        raise EligibilityValidationError("draft packet lacks source_request or formalizer_result")
    research_object = formalizer.get("research_object")
    if not isinstance(research_object, dict):
        research_object = {}
    for field in ("title", "hypothesis_text"):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise EligibilityValidationError(f"draft packet has invalid source_request.{field}")
    return request, research_object


def _scan_sources(repo_root: Path, draft_tokens: set[str], timeframe: str | None) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    matches: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    registry = repo_root / "research/candidate_registry.jsonl"
    try:
        raw = registry.read_bytes()
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EligibilityValidationError("candidate registry is unreadable") from exc
    sources.append(_artifact(registry, repo_root, _hash_bytes(raw)))
    for row in rows:
        if not isinstance(row, dict) or row.get("status") != "CONCLUDED":
            continue
        candidate_tokens = _tokens(row.get("name"), row.get("strategy_family"), row.get("differentiation_summary"))
        score = _similarity(draft_tokens, candidate_tokens)
        overlap = sorted(draft_tokens & candidate_tokens)
        family_hit = bool(set(overlap) & {"momentum", "trend", "following", "reversion", "funding", "bollinger", "macd", "donchian", "moving", "average"})
        if score >= 0.20 or (family_hit and timeframe == row.get("timeframe") and len(overlap) >= 2):
            matches.append({
                "match_type": "concluded_candidate_near_duplicate",
                "source_id": row.get("candidate_id"),
                "source_path": "research/candidate_registry.jsonl",
                "source_hash": _hash_bytes(raw),
                "similarity": round(score, 6),
                "explanation": f"normalized overlap={overlap}; concluded family={row.get('strategy_family')}; timeframe={row.get('timeframe')}",
            })
    matched_spec_ids: set[str] = set()
    for spec_path in sorted((repo_root / "research/strategy_specs").glob("*.strategy_spec.json")):
        spec, digest = _read_json(spec_path)
        sources.append(_artifact(spec_path, repo_root, digest))
        body = spec.get("timeframe_and_data") if isinstance(spec.get("timeframe_and_data"), dict) else {}
        spec_tokens = _tokens(spec.get("title"), spec.get("short_name"), json.dumps(spec.get("entry_logic", {})), json.dumps(spec.get("exit_logic", {})))
        score = _similarity(draft_tokens, spec_tokens)
        overlap = sorted(draft_tokens & spec_tokens)
        if score >= 0.16 and len(overlap) >= 2:
            matched_spec_ids.add(str(spec.get("strategy_spec_id")))
            matches.append({
                "match_type": "canonical_family_near_duplicate",
                "source_id": spec.get("strategy_spec_id"),
                "source_path": _relative(spec_path, repo_root),
                "source_hash": digest,
                "similarity": round(score, 6),
                "explanation": f"normalized overlap={overlap}; primary_timeframe={body.get('primary_timeframe')}",
            })
    for population_path in sorted((repo_root / "research/result_populations").glob("*.result_population.json")):
        population, digest = _read_json(population_path)
        sources.append(_artifact(population_path, repo_root, digest))
        lineage = population.get("lineage") if isinstance(population.get("lineage"), dict) else {}
        parent_spec_id = lineage.get("strategy_spec_id")
        if parent_spec_id in matched_spec_ids:
            matches.append({
                "match_type": "result_population_lineage_match",
                "source_id": population.get("result_population_id"),
                "source_path": _relative(population_path, repo_root),
                "source_hash": digest,
                "similarity": None,
                "explanation": f"committed result population descends from matched {parent_spec_id}",
            })
    return sorted(matches, key=lambda item: (item["source_path"], str(item["source_id"]))), sources


def validate_draft_eligibility(
    draft_id: str,
    *,
    repo_root: Path,
    draft_root: Path = DEFAULT_DRAFT_ROOT,
    review_root: Path = DEFAULT_REVIEW_ROOT,
    report_root: Path = DEFAULT_REPORT_ROOT,
    write_report: bool = True,
) -> dict[str, Any]:
    """Build one deterministic advisory report; optionally write it to scratch."""
    repo_root = repo_root.resolve()
    if not DRAFT_ID_RE.fullmatch(draft_id):
        raise EligibilityValidationError("draft_id must match AIDRAFT-<16 uppercase hex>")
    draft_path = repo_root / draft_root / f"{draft_id}.draft_packet.json"
    if not draft_path.is_file():
        raise EligibilityValidationError(f"draft not found: {draft_id}")
    packet, draft_hash = _read_json(draft_path)
    if packet.get("draft_id") != draft_id or packet.get("schema_version") != "agent_inbox_intake_draft_packet_v1":
        raise EligibilityValidationError("draft identity or schema_version is invalid")
    request, obj = _draft_fields(packet)
    review_path = repo_root / review_root / f"{draft_id}.review_events.jsonl"
    reviews, review_hash = _load_reviews(review_path, draft_id)
    latest_review = reviews[-1]["review_state"] if reviews else None
    source_artifacts = [_artifact(draft_path, repo_root, draft_hash)]
    if review_hash:
        source_artifacts.append(_artifact(review_path, repo_root, review_hash))

    market = request.get("market_hint")
    symbols = obj.get("symbols") if isinstance(obj.get("symbols"), list) else []
    timeframe = request.get("timeframe_hint") or obj.get("timeframe")
    hypothesis = obj.get("falsifiable_prediction")
    bounds = obj.get("parameter_bounds")
    provenance = packet.get("provenance")
    source_hashes = packet.get("source_hashes")
    availability = packet.get("availability_primitive_check")
    if not isinstance(availability, dict):
        availability = packet.get("formalizer_result", {}).get("capability_assessment", {})

    checks: dict[str, Any] = {}
    checks["falsifiable_hypothesis"] = _check(PASS if isinstance(hypothesis, str) and hypothesis.strip() else UNKNOWN, "A falsifiable prediction is present." if hypothesis else "No formalized falsifiable prediction is present.")
    bounded_market = market == "BTCUSDT" and (not symbols or symbols == ["BTCUSDT"])
    checks["bounded_market"] = _check(PASS if bounded_market else FAIL, f"market_hint={market!r}; formalized symbols={symbols!r}")
    checks["bounded_timeframe"] = _check(PASS if timeframe in LOCKED_TIMEFRAMES else FAIL, f"timeframe={timeframe!r}; allowed={sorted(LOCKED_TIMEFRAMES)}")
    feature_assessments = availability.get("feature_assessments") if isinstance(availability, dict) else None
    blocking = availability.get("blocking_features") if isinstance(availability, dict) else None
    if isinstance(feature_assessments, list):
        feature_status = FAIL if blocking else PASS
    else:
        feature_status = UNKNOWN
    checks["feature_availability"] = _check(feature_status, f"blocking_features={blocking!r}; assessment_count={len(feature_assessments) if isinstance(feature_assessments, list) else 0}")
    historical = availability.get("historically_testable_now") if isinstance(availability, dict) else None
    history_status = PASS if historical is True else FAIL if historical is False else UNKNOWN
    checks["data_availability"] = _check(history_status, f"historically_testable_now={historical!r}")
    checks["historical_testability"] = _check(history_status, "Uses the packet's explicit capability assessment; this does not prove a dataset slice exists.")
    if isinstance(bounds, list) and bounds:
        sane = all(isinstance(item, dict) and isinstance(item.get("minimum"), (int, float)) and isinstance(item.get("maximum"), (int, float)) and item["minimum"] <= item["maximum"] for item in bounds)
        parameter_status = PASS if sane and len(bounds) <= 5 else FAIL
    else:
        parameter_status = UNKNOWN
    checks["parameter_bounds"] = _check(parameter_status, f"declared_bound_count={len(bounds) if isinstance(bounds, list) else 0}; maximum supported free-parameter count=5")
    provenance_ok = isinstance(provenance, dict) and bool(provenance) and isinstance(source_hashes, dict) and bool(source_hashes)
    checks["provenance_completeness"] = _check(PASS if provenance_ok else FAIL, "Draft provenance and source hashes are present." if provenance_ok else "Draft provenance or source hashes are missing.")

    draft_tokens = _tokens(request.get("title"), request.get("hypothesis_text"), obj.get("summary"), obj.get("features"))
    matches, scan_sources = _scan_sources(repo_root, draft_tokens, timeframe if isinstance(timeframe, str) else None)
    source_artifacts.extend(scan_sources)
    duplicate_status = FAIL if matches else PASS
    checks["duplicate_near_duplicate_scan"] = _check(duplicate_status, f"detected {len(matches)} normalized near-duplicate match(es).", [item["source_path"] for item in matches])
    concluded_matches = [item for item in matches if item["match_type"] == "concluded_candidate_near_duplicate"]
    checks["concluded_family_freshness_scan"] = _check(FAIL if concluded_matches else PASS, f"detected {len(concluded_matches)} concluded-family match(es).")

    rejection_reasons: list[str] = []
    warnings = ["Advisory evidence only; this report is not Gate C and grants no write or queue authority."]
    open_questions: list[str] = []
    if latest_review not in {"reviewed", "flagged_for_canonicalization"}:
        open_questions.append("A reviewed or flagged_for_canonicalization review state is required before Gate C review consideration.")
    for name, check in checks.items():
        if check["status"] == FAIL:
            rejection_reasons.append(f"{name}: {check['explanation']}")
        elif check["status"] == UNKNOWN:
            open_questions.append(f"{name}: {check['explanation']}")
    blockers = packet.get("blockers")
    if isinstance(blockers, list) and blockers:
        warnings.extend(f"draft blocker: {item}" for item in blockers)

    if rejection_reasons:
        status = "ineligible"
    elif open_questions:
        status = "needs_clarification"
    elif latest_review in {"reviewed", "flagged_for_canonicalization"}:
        status = "eligible_for_gate_c_review"
    else:
        status = "insufficient_evidence"
    report = {
        "schema_version": SCHEMA_VERSION,
        "draft_id": draft_id,
        "source_draft_path": _relative(draft_path, repo_root),
        "source_draft_hash": draft_hash,
        "review_trail_path": _relative(review_path, repo_root) if review_hash else None,
        "review_trail_hash": review_hash,
        "reviewed_state_summary": {"event_count": len(reviews), "latest_state": latest_review, "flagged_for_canonicalization": latest_review == "flagged_for_canonicalization"},
        "eligibility_status": status,
        "advisory_only": True,
        "canonical_authority": False,
        "gate_c_authority": False,
        "queue_authority": False,
        "checks": checks,
        "rejection_reasons": sorted(rejection_reasons),
        "warnings": sorted(set(warnings)),
        "open_questions": sorted(set(open_questions)),
        "duplicate_near_duplicate_candidates": matches,
        "source_artifacts_read": sorted({(item["path"], item["sha256"]) for item in source_artifacts}),
        "non_authority_flags": {"not_approval": True, "not_canonical_write": True, "not_gate_c": True, "not_queue_admission": True, "not_candidate_creation": True, "not_research_execution": True, "not_runtime_action": True},
    }
    report["source_artifacts_read"] = [{"path": path, "sha256": digest} for path, digest in report["source_artifacts_read"]]
    if write_report:
        output_root = (repo_root / report_root).resolve()
        allowed = (repo_root / "scratch" / PACKAGE_ID).resolve()
        if output_root != allowed and allowed not in output_root.parents:
            raise EligibilityValidationError("report output must remain under package scratch root")
        output_root.mkdir(parents=True, exist_ok=True)
        (output_root / f"{draft_id}.eligibility_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft_id")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        report = validate_draft_eligibility(args.draft_id, repo_root=args.repo_root, write_report=not args.no_write)
    except EligibilityValidationError as exc:
        parser.exit(2, f"eligibility validation failed closed: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
